"""Analyse E1 token maps: line-level and function-level localization inside files.

Usage: python src/analyze_conflict.py --tag e4b [--ids file] [--exclude file] [--json out]
"""
from __future__ import annotations

import argparse
import zlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.metrics import roc_auc_score

from common import RESULTS, Unit, file_at, function_units, gold_edits, load_instances
from run_conflict import key
from scorer import Scored, line_scores

TOK = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def bm25_tokens(s: str) -> list[str]:
    out = []
    for w in TOK.findall(s):
        out.append(w.lower())
        parts = re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])", w)
        if len(parts) > 1 or "_" in w:
            out.extend(p.lower() for p in re.split(r"_+", w) if p)
            out.extend(p.lower() for p in parts)
    return out


def units_with_module(src: str) -> list[Unit]:
    """Function units plus residual 'gap' units (class headers / module code between defs)."""
    n = len(src.splitlines())
    fu = function_units(src)
    units, cur = [], 1
    for u in fu:
        if u.start > cur:
            units.append(Unit(f"<gap@{cur}>", cur, u.start - 1, "gap"))
        units.append(u)
        cur = max(cur, u.end + 1)
    if cur <= n:
        units.append(Unit(f"<gap@{cur}>", cur, n, "gap"))
    return units


def line_features(src: str, z) -> dict[str, np.ndarray]:
    target = src if src.endswith("\n") else src + "\n"
    n = len(target.splitlines())
    lp = {k[3:]: z[k] for k in z.files if k.startswith("lp_") and k[3:] not in ("D", "DX")}
    feats: dict[str, np.ndarray] = {}
    if lp:
        any_lp = next(iter(lp.values()))
        buckets = line_scores(target, Scored(any_lp, z["offsets"], 0, 0.0))[:n]
        feats["ntok"] = np.array([len(b) for b in buckets])

        def agg(arr, fn, empty=0.0):
            return np.array([fn(arr[b]) if b else empty for b in buckets], dtype=np.float64)

        for a in lp:
            feats[f"surp_{a}_sum"] = agg(-lp[a], np.sum)
            feats[f"surp_{a}_max"] = agg(-lp[a], np.max)
            # exact probability that the model's FIRST deviation from the original falls in line i
            S = feats[f"surp_{a}_sum"]
            before = np.concatenate([[0.0], np.cumsum(S)[:-1]])
            feats[f"first_{a}"] = (1 - np.exp(-S)) * np.exp(-before)
        if "U" in lp:
            feats["surp_U_mean"] = agg(-lp["U"], np.mean)
        pairs = [("F", "U"), ("F", "B"), ("B", "U"), ("X", "U"), ("F", "X"),
                 ("R", "RX"), ("R", "RB"), ("R", "R0"), ("RB", "R0"), ("RX", "R0")]
        for a, b in pairs:
            if a in lp and b in lp:
                d = lp[a] - lp[b]  # negative = token became LESS likely under `a`
                feats[f"drop_{a}-{b}_sum"] = agg(-d, np.sum)  # higher = more conflict
                feats[f"drop_{a}-{b}_max"] = agg(-d, np.max)
                feats[f"drop_{a}-{b}_pos"] = agg(np.maximum(-d, 0), np.sum)
                feats[f"gain_{a}-{b}_pos"] = agg(np.maximum(d, 0), np.sum)
    # diff-marker frames: probability of starting an edit ('-' or '+') at each line start
    for fr in ("D", "DX"):
        if f"lp_{fr}" not in z.files:
            continue
        dtarget = "".join(" " + l + "\n" for l in target.splitlines())
        offs = z[f"offsets_{fr}"]
        db = line_scores(dtarget, Scored(z[f"lp_{fr}"], offs, 0, 0.0))[:n]
        pm, pp = np.exp(z[f"minus_{fr}"].astype(np.float64)), np.exp(z[f"plus_{fr}"].astype(np.float64))
        first = [b[0] if b else None for b in db]
        feats[f"pminus_{fr}"] = np.array([pm[i] if i is not None else 0.0 for i in first])
        feats[f"pplus_{fr}"] = np.array([pp[i] if i is not None else 0.0 for i in first])
        feats[f"pedit_{fr}"] = feats[f"pminus_{fr}"] + feats[f"pplus_{fr}"]
        # '+' at the start of line i+1 means "insert after line i": also credit the previous line
        nxt = np.concatenate([feats[f"pplus_{fr}"][1:], [0.0]])
        feats[f"pedit2_{fr}"] = feats[f"pminus_{fr}"] + np.maximum(feats[f"pplus_{fr}"], nxt)
        feats[f"surp_{fr}_sum"] = np.array([-z[f"lp_{fr}"][b].sum() if b else 0.0 for b in db])
        if "ntok" not in feats:
            feats["ntok"] = np.array([len(b) for b in db])
    if "pedit_D" in feats and "pedit_DX" in feats:
        feats["pedit_D-DX"] = np.log(feats["pedit_D"] + 1e-9) - np.log(feats["pedit_DX"] + 1e-9)
    return feats


def fix_anchors(g, valid: np.ndarray, nl: int, mode: str = "all") -> set[int]:
    """Gold line set. Insertion anchors that fall on token-less (blank) lines are moved to the
    nearest line that has tokens, in the direction away from the insertion point.
    mode: 'all' (modified + insertion anchors) | 'modified' (removed/modified lines only)."""
    out = {l for l in g.removed if 1 <= l <= nl and valid[l - 1]}
    if mode == "modified":
        return out
    anchors = sorted(l for l in g.lines if l not in g.removed)
    for a in anchors:
        if not (1 <= a <= nl):
            continue
        if valid[a - 1]:
            out.add(a)
            continue
        # direction: an anchor whose successor is also an anchor/gold is the "before" side
        step = -1 if (a + 1) in g.lines else 1
        b = a
        while 1 <= b <= nl and not valid[b - 1]:
            b += step
        if 1 <= b <= nl:
            out.add(b)
    return out


def unit_scores(units: list[Unit], line_feat: np.ndarray, how: str, valid: np.ndarray | None = None) -> np.ndarray:
    out = []
    for u in units:
        seg = line_feat[u.start - 1 : u.end]
        if valid is not None:
            seg = seg[valid[u.start - 1 : u.end]]
        if len(seg) == 0:
            out.append(-1e18)
        elif how == "max":
            out.append(seg.max())
        elif how == "sum":
            out.append(seg.sum())
        elif how == "mean":
            out.append(seg.mean())
        elif how == "top3":
            out.append(np.sort(seg)[-3:].mean())
    return np.array(out)


def frng(fkey: str, name: str):
    """Seeded per (file, feature): adding a feature never shifts another feature's tie-breaking or the random baseline."""
    return np.random.default_rng(zlib.crc32(f"{fkey}|{name}".encode()))


def rank_of_best_gold(scores: np.ndarray, gold: set[int], rng) -> int:
    """1-based rank of the best-ranked gold item, random tie-breaking."""
    order = np.lexsort((rng.random(len(scores)), -scores))
    for r, i in enumerate(order, 1):
        if int(i) in gold:
            return r
    return len(scores) + 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--ids", default=None)
    ap.add_argument("--exclude", default=None)
    ap.add_argument("--json", default=None)
    ap.add_argument("--dataset", default=None)
    ap.add_argument("--gen", default=None, help="tag of a run_generative.py run to compare on the same files")
    ap.add_argument("--gen2", default=None, help="second generative run (e.g. quote mode)")
    ap.add_argument("--labels", default="all", choices=["all", "modified"])
    ap.add_argument("--quote-match", default="aligned", choices=["aligned", "all"],
                    help="how repeated quoted lines are mapped to file lines (aligned = most favourable)")
    ap.add_argument("--feats", default=None, help="comma-separated feature substrings to print")
    args = ap.parse_args()
    gen = {}
    if args.gen:
        for l in open(RESULTS / f"gen_{args.gen}" / "gen.jsonl"):
            g_ = json.loads(l)
            gen[(g_["iid"], g_["path"])] = g_
    gen2 = {}
    if args.gen2:
        for l in open(RESULTS / f"gen_{args.gen2}" / "gen.jsonl"):
            g_ = json.loads(l)
            gen2[(g_["iid"], g_["path"])] = g_
    insts = {i["instance_id"]: i for i in load_instances(Path(args.dataset) if args.dataset else None)}
    d = RESULTS / f"conflict_{args.tag}"
    recs = [json.loads(l) for l in open(d / "log.jsonl")]
    recs = [r for r in recs if "skip" not in r and r.get("gold")]
    if args.ids:
        keep = {l.strip() for l in open(args.ids)}
        recs = [r for r in recs if r["iid"] in keep]
    if args.exclude:
        ex = {l.strip() for l in open(args.exclude)}
        recs = [r for r in recs if r["iid"] not in ex]
    seen = set()
    rng = np.random.default_rng(0)
    line_auc = defaultdict(list)
    line_rank = defaultdict(list)
    unit_rank = defaultdict(list)
    n_lines, n_units, n_gold_units = [], [], []
    rows = []
    for r in recs:
        k = key(r["iid"], r["path"])
        if k in seen or not (d / (k + ".npz")).exists():
            continue
        if args.gen and (r["iid"], r["path"]) not in gen:
            continue
        seen.add(k)
        inst = insts[r["iid"]]
        src = file_at(inst["repo"], inst["base_commit"], r["path"])
        z = np.load(d / (k + ".npz"))
        feats = line_features(src, z)
        nl = len(feats["ntok"])
        g = gold_edits(inst["patch"])[r["path"]]
        valid = feats["ntok"] > 0
        gold_lines = fix_anchors(g, valid, nl, args.labels)
        if not gold_lines:
            continue
        y = np.zeros(nl, dtype=int)
        for l in gold_lines:
            y[l - 1] = 1
        if y[valid].sum() == 0 or y[valid].sum() == valid.sum():
            continue
        units = units_with_module(src)
        gold_units = {i for i, u in enumerate(units) if any(u.start <= l <= u.end for l in gold_lines)}
        n_lines.append(int(valid.sum()))
        n_units.append(len(units))
        n_gold_units.append(len(gold_units))
        # baselines
        issue = inst["problem_statement"]
        lines = src.splitlines()
        q = bm25_tokens(issue)
        docs_u = [bm25_tokens("\n".join(lines[u.start - 1 : u.end])) or ["_"] for u in units]
        bm_u = BM25Okapi(docs_u).get_scores(q)
        docs_l = [bm25_tokens(l) or ["_"] for l in lines]
        bm_l = np.array(BM25Okapi(docs_l).get_scores(q))
        feats = dict(feats)
        feats["bm25"] = bm_l
        feats["random"] = frng(k, "random").random(nl)
        feats["line_ntok"] = feats["ntok"].astype(float)
        nt = np.maximum(feats["ntok"], 1)
        if "drop_R-RX_pos" in feats:
            feats["Hnorm"] = feats["drop_R-RX_pos"] / nt  # per-token normalised (length control)
        if "surp_R_sum" in feats:
            feats["Snorm"] = feats["surp_R_sum"] / nt
        row = {"iid": r["iid"], "path": r["path"], "n_lines": int(valid.sum()), "n_units": len(units),
               "n_tok": r.get("n_tok"), "n_gold_lines": len(gold_lines), "n_gold_units": len(gold_units),
               "n_removed": g.n_removed, "n_added": g.n_added, "repo": inst["repo"]}
        if "lp_R" in z.files:
            lpR = z["lp_R"].astype(np.float64)
            row["min_p_R"] = float(np.exp(lpR.min()))  # >= 0.5 for every token => the greedy rewrite is a no-op
            row["n_tok_p_below_half"] = int((lpR < np.log(0.5)).sum())
        gl_txt = [" ".join(lines[l - 1].split()) for l in gold_lines if l - 1 < len(lines)]
        issue_norm = " ".join(issue.split())
        row["issue_quotes_gold"] = bool(any(len(t) >= 12 and t in issue_norm for t in gl_txt))
        feats["position"] = -np.arange(nl, dtype=float)  # top-of-file first
        # concentration of edit mass within +-2 lines of a gold line
        near = np.zeros(nl, bool)
        for l in gold_lines:
            near[max(l - 3, 0) : min(l + 2, nl)] = True
        row["frac_lines_near_gold"] = float((near & valid).sum() / max(valid.sum(), 1))
        for nm in ("surp_R_sum", "surp_RX_sum", "drop_R-RX_pos"):
            if nm in feats:
                tot = feats[nm][valid].sum()
                row[f"mass_near_{nm}"] = float(feats[nm][near & valid].sum() / tot) if tot > 0 else 0.0
                row[f"total_{nm}"] = float(tot)
        for name, f in feats.items():
            if name == "ntok":
                continue
            s = np.where(valid, f, -1e9)
            line_auc[name].append(roc_auc_score(y[valid], f[valid]))
            lr = rank_of_best_gold(s, {l - 1 for l in gold_lines}, frng(k, name))
            line_rank[name].append(lr)
            row[f"lrank_{name}"] = lr
            for how in ("max", "sum", "top3"):
                us = unit_scores(units, f, how, valid)
                ur = rank_of_best_gold(us, gold_units, frng(k, f"{name}|{how}"))
                unit_rank[f"{name}|{how}"].append(ur)
                row[f"urank_{name}|{how}"] = ur
        for gname, gdict in (("gen", gen), ("gen2", gen2)):
            if not gdict:
                continue
            if (r["iid"], r["path"]) not in gdict:
                ranges = []
            else:
                g_rec = gdict[(r["iid"], r["path"])]
                ranges = [tuple(x) for x in g_rec["ranges"]]
                if g_rec.get("mode") == "quote" and args.quote_match == "aligned":
                    ranges = align_quotes(g_rec["response"], src.splitlines())
            ranked_units = []
            for a, b in ranges:
                for i, u in enumerate(units):
                    if u.start <= b and a <= u.end and i not in ranked_units:
                        ranked_units.append(i)
            ur = next((j for j, i in enumerate(ranked_units, 1) if i in gold_units), len(units) + 1)
            label = "GENERATIVE" if gname == "gen" else "GENERATIVE-quote"
            unit_rank[label + "|-"].append(ur)
            row[f"urank_{gname}"] = ur
            # line level: number of lines a reader inspects, in answer order, until a gold line is hit
            cnt, lr = 0, nl + 1
            seen_l = set()
            for a, b in ranges:
                hit = False
                for l in range(max(a, 1), min(b, nl) + 1):
                    if l in seen_l:
                        continue
                    seen_l.add(l)
                    cnt += 1
                    if l in gold_lines:
                        hit = True
                        break
                if hit:
                    lr = cnt
                    break
            line_rank[label].append(lr)
            line_auc[label].append(float("nan"))
            row[f"lrank_{gname}"] = lr
            row[f"{gname}_nranges"] = len(ranges)
            # exploratory hybrid: lines inside the generated functions first (by H), then the rest (by H)
            if gname == "gen" and "drop_R-RX_pos" in feats:
                inside = np.zeros(nl, bool)
                for i in ranked_units[:3]:
                    inside[units[i].start - 1 : units[i].end] = True
                hy = np.where(valid, feats["drop_R-RX_pos"] + 1e6 * inside, -1e9)
                row["lrank_hybrid"] = rank_of_best_gold(hy, {l - 1 for l in gold_lines}, frng(k, "hybrid"))
        ur = rank_of_best_gold(np.array(bm_u), gold_units, frng(k, "bm25_unit"))
        unit_rank["bm25_unit|-"].append(ur)
        row["urank_bm25_unit"] = ur
        ur = rank_of_best_gold(np.array([u.end - u.start for u in units], float), gold_units, frng(k, "unit_length"))
        unit_rank["unit_length|-"].append(ur)
        row["urank_unit_length"] = ur
        rows.append(row)

    N = len(n_lines)
    print(f"files analysed: {N}; median lines {np.median(n_lines):.0f}; median units {np.median(n_units):.0f}; "
          f"chance unit hit@1 {np.mean(np.array(n_gold_units)/np.array(n_units)):.3f}")
    print("\nLINE level (rank of best gold line among all lines of the file)")
    print(f"{'feature':22s} {'AUROC':>6s} {'hit@1':>6s} {'hit@5':>6s} {'hit@10':>6s} {'medRank':>7s}")
    summ = {"N": N, "line": {}, "unit": {}}
    def show(name):
        return not args.feats or any(f in name for f in args.feats.split(",")) or "GENERATIVE" in name

    for name in sorted(line_auc, key=lambda k: -np.nan_to_num(np.mean(line_auc[k]), nan=2)):
        if not show(name):
            continue
        rk = np.array(line_rank[name])
        s = dict(auroc=float(np.mean(line_auc[name])), hit1=float((rk <= 1).mean()), hit5=float((rk <= 5).mean()),
                 hit10=float((rk <= 10).mean()), med=float(np.median(rk)))
        summ["line"][name] = s
        print(f"{name:22s} {s['auroc']:6.3f} {s['hit1']:6.3f} {s['hit5']:6.3f} {s['hit10']:6.3f} {s['med']:7.0f}")
    print("\nUNIT (function) level")
    print(f"{'feature|agg':28s} {'hit@1':>6s} {'hit@3':>6s} {'hit@5':>6s} {'MRR':>6s}")
    for name in sorted(unit_rank, key=lambda k: -np.mean(1 / np.array(unit_rank[k]))):
        if not show(name):
            continue
        rk = np.array(unit_rank[name])
        s = dict(hit1=float((rk <= 1).mean()), hit3=float((rk <= 3).mean()), hit5=float((rk <= 5).mean()),
                 mrr=float((1 / rk).mean()))
        summ["unit"][name] = s
        print(f"{name:28s} {s['hit1']:6.3f} {s['hit3']:6.3f} {s['hit5']:6.3f} {s['mrr']:6.3f}")
    if args.json:
        json.dump({"summary": summ, "rows": rows}, open(args.json, "w"))


def align_quotes(resp: str, file_lines: list[str]) -> list[tuple[int, int]]:
    """Map lines quoted by the model back to file lines, resolving repeated lines by context.

    A quoted line that occurs several times in the file is assigned to the occurrence that continues the
    previous quoted line (contiguous block), else to the occurrence nearest to the closest uniquely
    matched quote; if the answer contains no unique quote, all occurrences are kept (answer order).
    This is the reading most favourable to the generated answer.
    """
    norm: dict[str, list[int]] = {}
    for i, l in enumerate(file_lines, 1):
        k = " ".join(l.split())
        if k:
            norm.setdefault(k, []).append(i)
    qs = []
    for q in resp.splitlines():
        q = q.strip().strip("`")
        q = re.sub(r"^\d+\s*[|:]\s?", "", q)
        k = " ".join(q.split())
        if k and not k.startswith("```") and k in norm:
            qs.append(norm[k])
    uniq = [(j, occ[0]) for j, occ in enumerate(qs) if len(occ) == 1]
    out: list[tuple[int, int]] = []
    prev = None
    for j, occ in enumerate(qs):
        if len(occ) == 1:
            pick = [occ[0]]
        elif prev is not None and any(prev < o <= prev + 3 for o in occ):
            pick = [min(o for o in occ if prev < o <= prev + 3)]
        elif uniq:
            anchor = min(uniq, key=lambda u: abs(u[0] - j))[1]
            pick = [min(occ, key=lambda o: abs(o - anchor))]
        else:
            pick = list(occ)
        prev = pick[0] if len(pick) == 1 else None
        for o in pick:
            if (o, o) not in out:
                out.append((o, o))
    return out


if __name__ == "__main__":
    main()
