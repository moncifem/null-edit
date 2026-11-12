"""Code-lines-only map (HYPOTHESES.md Revision 3). CPU only, saved scores.

The one-pass hazard S is ranked (a) over all non-blank lines and (b) over code lines only: comment-only lines and
string-statement (docstring) lines are not ranked. Gold lines are unchanged in both, so a gold line that is itself a
comment or docstring line counts against (b). `prose_lines` is copied verbatim from explore_codeonly.py (frozen there).

Usage: NULLEDIT_RESULTS=../results_dgx python analyze_codeonly.py --ids ../results/conf_ids.txt \
          --runs 12B=g12b_conf 26B-A4B=g26b_conf --ref E4B=e4b_test
"""
import argparse, io, json, tokenize
import numpy as np
from analyze_conflict import fix_anchors, line_features
from common import RESULTS, file_at, gold_edits, load_instances
from report import boot
from run_conflict import key


def prose_lines(src: str) -> set[int]:
    """1-based lines that are comment-only or inside a string statement (docstring)."""
    out = set()
    try:
        prev = None
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT and not tok.line[: tok.start[1]].strip():
                out.add(tok.start[0])
            if tok.type == tokenize.STRING and (prev is None or prev in (tokenize.INDENT, tokenize.NEWLINE, tokenize.NL, tokenize.DEDENT)) \
                    and tok.line[: tok.start[1]].strip() == "":
                out.update(range(tok.start[0], tok.end[0] + 1))
            if tok.type not in (tokenize.COMMENT,):
                prev = tok.type
    except Exception:
        pass
    return out


BANDS = [("under 5,000", 0, 5000), ("5,000-11,000", 5000, 11000), ("over 11,000", 11000, 10**9)]


def pval(bs):
    return min(1.0, 2 * min((bs <= 0).mean(), (bs >= 0).mean()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True, help="NAME=tag")
    ap.add_argument("--ref", default=None, help="NAME=tag of the reference run (ranked over all lines)")
    ap.add_argument("--ids", required=True)
    ap.add_argument("--limit", type=int, default=10**9)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--out", default=None, help="name of the json written to the results directory")
    ap.add_argument("--common", action="store_true", help="restrict to files every run (and the reference) has")
    a = ap.parse_args()
    insts = {i["instance_id"]: i for i in load_instances()}
    ids = set([l.strip() for l in open(a.ids) if l.strip()][: a.limit])
    runs = [r.split("=") for r in a.runs] + ([a.ref.split("=")] if a.ref else [])
    logs = {n: {(r["iid"], r["path"]): r for r in map(json.loads, open(RESULTS / f"conflict_{t}" / "log.jsonl"))
                if "secs" in r and r["iid"] in ids and r.get("gold", True)} for n, t in runs}
    keys = {n: set(v) for n, v in logs.items()}
    if a.common:
        c = set.intersection(*keys.values())
        keys = {n: c for n in keys}
    rows = {n: [] for n, _ in runs}
    cache = {}
    for n, t in runs:
        for iid, path in sorted(keys[n]):
            inst = insts[iid]
            if (iid, path) not in cache:
                src = file_at(inst["repo"], inst["base_commit"], path)
                cache[(iid, path)] = (src, prose_lines(src))
            src, prose = cache[(iid, path)]
            z = np.load(RESULTS / f"conflict_{t}" / (key(iid, path) + ".npz"))
            f = line_features(src, z)
            valid = f["ntok"] > 0
            gold = fix_anchors(gold_edits(inst["patch"])[path], valid, len(valid), "all")
            if not gold:
                continue
            S = f["surp_R_sum"]
            is_prose = np.array([(i + 1) in prose for i in range(len(valid))])
            code = valid & ~is_prose
            order_all = np.argsort(-np.where(valid, S, -1e9), kind="stable") + 1
            order_code = (np.argsort(-np.where(code, S, -1e9), kind="stable") + 1)[: int(code.sum())]
            tot = float(S[valid].sum())
            ntok = logs[n][(iid, path)]["n_tok"]
            rows[n].append({"iid": iid, "path": path, "n_tok": ntok, "band": next(b[0] for b in BANDS if b[1] <= ntok < b[2]),
                            "all": float(bool(set(order_all[: a.k]) & gold)), "code": float(bool(set(order_code[: a.k]) & gold)),
                            "all1": float(order_all[0] in gold), "code1": float(len(order_code) > 0 and order_code[0] in gold),
                            "prose_share": float(S[valid & is_prose].sum() / tot) if tot > 0 else np.nan,
                            "prose_lines": float(is_prose[valid].mean()), "gold_all_prose": float(all(is_prose[g - 1] for g in gold)),
                            "total": tot})

    def cell(rs, fn):
        if len(rs) < 5:
            return "–"
        p, lo, hi, _ = boot(rs, fn)
        return f"{100*p:.0f} [{100*lo:.0f}, {100*hi:.0f}]"

    print(f"S line@{a.k}; issues from {a.ids}" + ("; files common to all runs" if a.common else "") + "\n")
    print(f"| Model | files (issues) | all lines @{a.k} | code lines only @{a.k} | difference (points), p | all lines @1 | code only @1 | hazard on comment/docstring lines (median share) | median total hazard (nats) |\n|---|---|---|---|---|---|---|---|---|")
    for n, _ in runs:
        rs = rows[n]
        p, lo, hi, bs = boot(rs, lambda r: r["code"] - r["all"])
        print(f"| {n} | {len(rs)} ({len({r['iid'] for r in rs})}) | {cell(rs, lambda r: r['all'])} | {cell(rs, lambda r: r['code'])} | "
              f"{100*p:+.1f} [{100*lo:+.1f}, {100*hi:+.1f}], p = {pval(bs):.4f} | {cell(rs, lambda r: r['all1'])} | {cell(rs, lambda r: r['code1'])} | "
              f"{np.nanmedian([r['prose_share'] for r in rs]):.2f} | {np.median([r['total'] for r in rs]):.1f} |")
    print(f"\nComment/docstring lines are {100*np.mean([r['prose_lines'] for r in rows[runs[0][0]]]):.0f}% of non-blank lines (mean over files); "
          f"every gold line is such a line in {100*np.mean([r['gold_all_prose'] for r in rows[runs[0][0]]]):.0f}% of files.")
    print("\n**By file length** (all lines -> code lines only; n files)\n")
    print("| Model | " + " | ".join(b[0] + " tokens" for b in BANDS) + " |\n|---|---|---|---|")
    for n, _ in runs:
        cells = []
        for b in BANDS:
            rs = [r for r in rows[n] if r["band"] == b[0]]
            cells.append(f"{100*np.mean([r['all'] for r in rs]):.0f} -> {100*np.mean([r['code'] for r in rs]):.0f} (n = {len(rs)}; share {np.nanmedian([r['prose_share'] for r in rs]):.2f})" if rs else "–")
        print(f"| {n} | " + " | ".join(cells) + " |")
    if a.ref:
        rn = a.ref.split("=")[0]
        ref = {(r["iid"], r["path"]): r for r in rows[rn]}
        print(f"\n**Against {rn} ranked over all lines, same files** (secondary)\n")
        for n, _ in runs[:-1]:
            rs = [dict(r, ref=ref[(r["iid"], r["path"])]["all"]) for r in rows[n] if (r["iid"], r["path"]) in ref]
            p, lo, hi, bs = boot(rs, lambda r: r["code"] - r["ref"])
            p2, lo2, hi2, bs2 = boot(rs, lambda r: r["all"] - r["ref"])
            print(f"- {n} code lines only − {rn}: {100*p:+.1f} [{100*lo:+.1f}, {100*hi:+.1f}], p = {pval(bs):.4f} ({len(rs)} files); "
                  f"{n} all lines − {rn}: {100*p2:+.1f} [{100*lo2:+.1f}, {100*hi2:+.1f}], p = {pval(bs2):.4f}")
    json.dump(rows, open(RESULTS / (a.out or ("codeonly_" + "_".join(t for _, t in runs) + ".json")), "w"))


if __name__ == "__main__":
    main()
