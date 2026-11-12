"""Agent-facing read-out: how much of a file must be shown for the edit to be in view?

For each scored file we open a window of +-W lines around each of the top-k lines of a ranking and
ask (a) whether every gold-edited line falls inside the shown windows ("all gold in view"),
(b) whether at least one does, and (c) what share of the file's lines is shown.
Rankings: null-edit H and S, BM25, wrong-issue hazard, random, and the generated (quoted) answer
taken in answer order. CPU only; reads the saved per-token log-probabilities.

Usage: python context_budget.py --tag e4b_test --ids ../results/test_ids.txt [--gen2 e4b_test_quote]
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi

from analyze_conflict import align_quotes, bm25_tokens, fix_anchors, line_features, units_with_module
from common import RESULTS, file_at, gold_edits, load_instances
from report import boot
from run_conflict import key


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--ids", default=None)
    ap.add_argument("--dataset", default=None)
    ap.add_argument("--gen2", default=None)
    ap.add_argument("--gen", default=None, help="line-range answers (run_generative.py, range mode)")
    ap.add_argument("--window", type=int, default=5)
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    insts = {i["instance_id"]: i for i in load_instances(Path(args.dataset) if args.dataset else None)}
    d = RESULTS / f"conflict_{args.tag}"
    recs = [json.loads(l) for l in open(d / "log.jsonl")]
    recs = [r for r in recs if "skip" not in r and r.get("gold")]
    if args.ids:
        keep = {l.strip() for l in open(args.ids)}
        recs = [r for r in recs if r["iid"] in keep]
    gen = {}
    if args.gen2:
        for l in open(RESULTS / f"gen_{args.gen2}" / "gen.jsonl"):
            g_ = json.loads(l)
            gen[(g_["iid"], g_["path"])] = g_
    genr = {}
    if args.gen:
        for l in open(RESULTS / f"gen_{args.gen}" / "gen.jsonl"):
            g_ = json.loads(l)
            genr[(g_["iid"], g_["path"])] = g_
    rng = np.random.default_rng(0)
    KS = (1, 3, 5, 10)
    BUDGETS = (0.05, 0.10, 0.20)
    rows, seen = [], set()
    for r in recs:
        k = key(r["iid"], r["path"])
        if k in seen or not (d / (k + ".npz")).exists():
            continue
        seen.add(k)
        inst = insts[r["iid"]]
        src = file_at(inst["repo"], inst["base_commit"], r["path"])
        f = line_features(src, np.load(d / (k + ".npz")))
        nl = len(f["ntok"])
        valid = f["ntok"] > 0
        gold = fix_anchors(gold_edits(inst["patch"])[r["path"]], valid, nl, "all")
        if not gold:
            continue
        lines = src.splitlines()
        bm = np.array(BM25Okapi([bm25_tokens(l) or ["_"] for l in lines]).get_scores(bm25_tokens(inst["problem_statement"])))
        orders = {}
        for name, sc in (("H", f.get("drop_R-RX_pos")), ("S", f.get("surp_R_sum")), ("BM25", bm),
                         ("wrong issue", f.get("surp_RX_sum")), ("random", rng.random(nl))):
            if sc is None:
                continue
            s = np.where(valid, sc + 1e-9 * rng.random(nl), -1e9)
            orders[name] = list(np.argsort(-s) + 1)
        if gen:
            g_ = gen.get((r["iid"], r["path"]))
            orders["generated answer"] = [a for a, _ in align_quotes(g_["response"], lines)] if g_ else []
        if genr:
            g_ = genr.get((r["iid"], r["path"]))
            o = []
            for a, b in (g_["ranges"] if g_ else []):
                o += [l for l in range(max(a, 1), min(b, nl) + 1) if l not in o]
            orders["generated answer (ranges)"] = o
            if g_ and "drop_R-RX_pos" in f:
                # recipe "ask, then read by hazard": lines of the answer's first three functions in H order, then the rest in H order
                units = units_with_module(src)
                named = []
                for a, b in g_["ranges"]:
                    for i, u in enumerate(units):
                        if u.start <= b and a <= u.end and i not in named:
                            named.append(i)
                inside = np.zeros(nl, bool)
                for i in named[:3]:
                    inside[units[i].start - 1 : units[i].end] = True
                hs = np.where(valid, f["drop_R-RX_pos"] + 1e6 * inside + 1e-9 * rng.random(nl), -1e9)
                orders["ask, then H"] = list(np.argsort(-hs) + 1)
        row = {"iid": r["iid"], "path": r["path"], "n_lines": nl}
        for name, order in orders.items():
            for kk in KS:
                shown = np.zeros(nl + 2, bool)
                for l in order[:kk]:
                    shown[max(l - args.window, 1) : min(l + args.window, nl) + 1] = True
                row[f"{name}|all|{kk}"] = float(all(shown[g] for g in gold))
                row[f"{name}|any|{kk}"] = float(any(shown[g] for g in gold))
                row[f"{name}|frac|{kk}"] = float(shown.sum() / nl)
            for B in BUDGETS:  # budget-matched: open windows in ranking order until B of the file is shown
                shown = np.zeros(nl + 2, bool)
                for l in order:
                    nxt = shown.copy()
                    nxt[max(l - args.window, 1) : min(l + args.window, nl) + 1] = True
                    if nxt.sum() > max(B * nl, 2 * args.window + 1):
                        break
                    shown = nxt
                row[f"{name}|allB|{B}"] = float(all(shown[g] for g in gold))
                row[f"{name}|anyB|{B}"] = float(any(shown[g] for g in gold))
        rows.append(row)
    names = [n for n in ("ask, then H", "H", "S", "generated answer (ranges)", "generated answer", "BM25", "wrong issue", "random") if f"{n}|all|1" in rows[0]]
    print(f"{len(rows)} files, window +-{args.window} lines around each of the top-k lines\n")
    print("| Ranking | " + " | ".join(f"all gold in view, k={k}" for k in KS) + " | any gold in view, k=5 | share of file shown, k=5 |")
    print("|---|" + "---|" * (len(KS) + 2))
    for n in names:
        cells = []
        for kk in KS:
            p, lo, hi, _ = boot(rows, lambda r: r[f"{n}|all|{kk}"])
            cells.append(f"{100*p:.0f} [{100*lo:.0f}, {100*hi:.0f}]")
        a5 = 100 * np.mean([r[f"{n}|any|5"] for r in rows])
        f5 = 100 * np.mean([r[f"{n}|frac|5"] for r in rows])
        print(f"| {n} | " + " | ".join(cells) + f" | {a5:.0f} | {f5:.1f}% |")
    print(f"\nBudget-matched: windows opened in ranking order until at most the given share of the file is shown (at least one window)\n")
    print("| Ranking | " + " | ".join(f"all gold in view, {int(100*B)}% of file" for B in BUDGETS) + " | " + " | ".join(f"any gold, {int(100*B)}%" for B in BUDGETS) + " |")
    print("|---|" + "---|" * (2 * len(BUDGETS)))
    for n in names:
        cells = []
        for kind in ("allB", "anyB"):
            for B in BUDGETS:
                p, lo, hi, _ = boot(rows, lambda r: r[f"{n}|{kind}|{B}"])
                cells.append(f"{100*p:.0f} [{100*lo:.0f}, {100*hi:.0f}]")
        print(f"| {n} | " + " | ".join(cells) + " |")
    print("\nPaired differences, any gold line in view (percentage points, instance-clustered bootstrap):\n")
    for a_, b_ in (("ask, then H", "H"), ("ask, then H", "generated answer (ranges)"), ("H", "generated answer (ranges)"), ("H", "BM25")):
        if a_ in names and b_ in names:
            for B in BUDGETS:
                p, lo, hi, bs = boot(rows, lambda r: r[f"{a_}|anyB|{B}"] - r[f"{b_}|anyB|{B}"])
                pv = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
                print(f"- {int(100*B)}% of file: {a_} − {b_}: {100*p:+.1f} [{100*lo:+.1f}, {100*hi:+.1f}], p = {pv:.4f}")
    print(f"\nmedian file: {np.median([r['n_lines'] for r in rows]):.0f} lines; 10% = {np.median([0.1 * r['n_lines'] for r in rows]):.0f} lines")
    if args.json:
        json.dump({"rows": rows}, open(args.json, "w"))


if __name__ == "__main__":
    main()
