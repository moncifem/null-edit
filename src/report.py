"""Final tables with instance-clustered bootstrap CIs from analyze_conflict.py --json outputs.

Usage: python src/report.py results/an_e4b_test.json [--name "E4B / Verified TEST"]
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict

import numpy as np

LINE = [
    ("Null-edit hazard, issue-specific H (2 passes)", "lrank_drop_R-RX_pos"),
    ("Null-edit hazard S (1 pass)", "lrank_surp_R_sum"),
    ("Generated answer: line ranges (same model)", "lrank_gen"),
    ("Generated answer: quoted lines (same model)", "lrank_gen2"),
    ("Exploratory hybrid: H inside generated functions first", "lrank_hybrid"),
    ("BM25 (issue vs line)", "lrank_bm25"),
    ("Wrong-issue hazard S (control)", "lrank_surp_RX_sum"),
    ("Correct issue, instruction 'print unchanged' (control)", "lrank_surp_RB_sum"),
    ("No issue, instruction 'print unchanged' (control)", "lrank_surp_R0_sum"),
    ("Mirror control: lines the wrong issue makes harder", "lrank_gain_R-RX_pos"),
    ("Line length in tokens", "lrank_line_ntok"),
    ("Position (top of file first)", "lrank_position"),
    ("Random", "lrank_random"),
]
UNIT = [
    ("Null-edit hazard, issue-specific H (2 passes)", "urank_drop_R-RX_pos|sum"),
    ("Null-edit hazard S (1 pass)", "urank_surp_R_sum|sum"),
    ("Generated answer: line ranges (same model)", "urank_gen"),
    ("Generated answer: quoted lines (same model)", "urank_gen2"),
    ("H, function of the top-ranked line (post hoc)", "urank_drop_R-RX_pos|max"),
    ("BM25 (issue vs function)", "urank_bm25_unit"),
    ("Wrong-issue hazard S (control)", "urank_surp_RX_sum|sum"),
    ("Correct issue, instruction 'print unchanged' (control)", "urank_surp_RB_sum|sum"),
    ("No issue, instruction 'print unchanged' (control)", "urank_surp_R0_sum|sum"),
    ("H per token, summed (length-normalised, post hoc)", "urank_Hnorm|sum"),
    ("Function length in tokens", "urank_line_ntok|sum"),
    ("Function length in lines", "urank_unit_length"),
    ("Random line scores, summed (pure length prior)", "urank_random|sum"),
]


def boot(rows, fn, B=10000, seed=0):
    by = defaultdict(list)
    for r in rows:
        by[r["iid"]].append(r)
    ids = sorted(by)
    rng = np.random.default_rng(seed)
    # per-instance sufficient stats: list of per-file values
    vals = [np.array([fn(r) for r in by[i]], float) for i in ids]
    sums = np.array([v.sum() for v in vals])
    cnts = np.array([len(v) for v in vals])
    point = sums.sum() / cnts.sum()
    idx = rng.integers(0, len(ids), size=(B, len(ids)))
    bs = sums[idx].sum(1) / cnts[idx].sum(1)
    return point, np.percentile(bs, 2.5), np.percentile(bs, 97.5), bs


def table(rows, spec, ks, title):
    out = [f"\n**{title}** (n = {len(rows)} files, {len({r['iid'] for r in rows})} instances; 95% instance-clustered bootstrap CI)\n",
           "| Method | " + " | ".join(f"hit@{k}" for k in ks) + " | median rank | MRR |", "|---|" + "---|" * (len(ks) + 2)]
    for name, key in spec:
        if key not in rows[0]:
            continue
        cells = []
        for k in ks:
            p, lo, hi, _ = boot(rows, lambda r: r[key] <= k)
            cells.append(f"{100*p:.1f} [{100*lo:.0f}, {100*hi:.0f}]")
        med = np.median([r[key] for r in rows])
        m, mlo, mhi, _ = boot(rows, lambda r: 1.0 / r[key])
        out.append(f"| {name} | " + " | ".join(cells) + f" | {med:.0f} | {m:.3f} [{mlo:.2f}, {mhi:.2f}] |")
    return "\n".join(out)


def paired(rows, a, b, k):
    if a not in rows[0] or b not in rows[0]:
        return None
    p, lo, hi, bs = boot(rows, lambda r: float(r[a] <= k) - float(r[b] <= k))
    pval = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
    return p, lo, hi, pval


def inst_weighted(rows, key, k):
    """Each issue counts once (mean over its files), instead of each file."""
    by = defaultdict(list)
    for r in rows:
        by[r["iid"]].append(float(r[key] <= k))
    v = np.array([np.mean(x) for x in by.values()])
    rng = np.random.default_rng(0)
    bs = v[rng.integers(0, len(v), size=(10000, len(v)))].mean(1)
    return v.mean(), np.percentile(bs, 2.5), np.percentile(bs, 97.5)


def extras(rows):
    H, S, B, G = "lrank_drop_R-RX_pos", "lrank_surp_R_sum", "lrank_bm25", "lrank_gen2"
    UH, UB, UG = "urank_drop_R-RX_pos|sum", "urank_bm25_unit", "urank_gen2"
    names = [("H", H, UH), ("S", S, "urank_surp_R_sum|sum"), ("generated answer (line ranges)", "lrank_gen", "urank_gen"),
             ("generated answer (quoted)", G, UG), ("BM25", B, UB)]
    names = [n for n in names if n[1] in rows[0]]
    print("\n**Issue-weighted estimates** (each issue counts once; guards against multi-file issues dominating)\n")
    print("| Method | line hit@1 | line hit@10 | function hit@1 |\n|---|---|---|---|")
    for lab, lk, uk in names:
        c = [inst_weighted(rows, lk, 1), inst_weighted(rows, lk, 10), inst_weighted(rows, uk, 1)]
        print(f"| {lab} | " + " | ".join(f"{100*p:.1f} [{100*lo:.0f}, {100*hi:.0f}]" for p, lo, hi in c) + " |")
    if G in rows[0] and "gen2_nranges" in rows[0]:
        n = np.array([max(r["gen2_nranges"], 1) for r in rows])
        print(f"\n**Budget-matched comparison with the generated answer** (every method is given exactly as many lines as the "
              f"answer listed for that file; median {np.median(n):.0f} lines)\n")
        for lab, lk, _ in names:
            p, lo, hi, _ = boot(rows, lambda r: float(r[lk] <= max(r["gen2_nranges"], 1)))
            print(f"- {lab}: {100*p:.1f}% [{100*lo:.0f}, {100*hi:.0f}]")
        pr = paired_fn(rows, lambda r: float(r[H] <= max(r["gen2_nranges"], 1)) - float(r[G] <= max(r["gen2_nranges"], 1)))
        print(f"- H − generated answer at matched budget: {100*pr[0]:+.1f} [{100*pr[1]:+.1f}, {100*pr[2]:+.1f}], p {'< 0.0001' if pr[3] < 1e-4 else f'= {pr[3]:.4f}'}")
    if "min_p_R" in rows[0]:
        sub = [r for r in rows if r["min_p_R"] >= 0.5]
        if len(sub) >= 10:
            print(f"\n**Files the model would leave unchanged** ({len(sub)} of {len(rows)} files: every original token has "
                  f"probability >= 0.5 under the fix-it prompt, so the greedy rewrite reproduces the file verbatim)\n")
            for lab, lk, uk in names:
                p, lo, hi, _ = boot(sub, lambda r: r[lk] <= 10)
                p1, lo1, hi1, _ = boot(sub, lambda r: r[uk] <= 1)
                print(f"- {lab}: line hit@10 {100*p:.1f}% [{100*lo:.0f}, {100*hi:.0f}]; function hit@1 {100*p1:.1f}% [{100*lo1:.0f}, {100*hi1:.0f}]")
    if "issue_quotes_gold" in rows[0]:
        sub = [r for r in rows if not r["issue_quotes_gold"]]
        print(f"\n**Issues that do not quote a gold line verbatim** ({len(sub)} of {len(rows)} files)\n")
        for lab, lk, uk in names:
            print(f"- {lab}: line hit@10 {100*np.mean([r[lk] <= 10 for r in sub]):.1f}%; function hit@1 {100*np.mean([r[uk] <= 1 for r in sub]):.1f}%")


def paired_fn(rows, fn):
    p, lo, hi, bs = boot(rows, fn)
    return p, lo, hi, 2 * min((bs <= 0).mean(), (bs >= 0).mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--name", default="")
    args = ap.parse_args()
    rows = json.load(open(args.json))["rows"]
    print(f"## {args.name}  ({args.json})")
    print(f"median lines/file {np.median([r['n_lines'] for r in rows]):.0f}, median functions/file {np.median([r['n_units'] for r in rows]):.0f}")
    print(table(rows, LINE, (1, 5, 10), "Line level: rank of the best-ranked gold line within the file"))
    print(table(rows, UNIT, (1, 3, 5), "Function level: rank of the best-ranked gold function within the file"))
    if "mass_near_surp_R_sum" in rows[0]:
        fl = np.mean([r["frac_lines_near_gold"] for r in rows])
        print(f"\n**Concentration of edit mass** (lines within ±2 of a gold line are {100*fl:.1f}% of lines on average)\n")
        for nm, lab in (("surp_R_sum", "S, correct issue"), ("surp_RX_sum", "S, wrong issue"), ("drop_R-RX_pos", "H")):
            k = f"mass_near_{nm}"
            if k in rows[0]:
                p_, lo, hi, _ = boot(rows, lambda r: r[k])
                print(f"- {lab}: {100*p_:.1f}% [{100*lo:.0f}, {100*hi:.0f}] of the file's total mass  (enrichment ×{p_/fl:.1f})")
        if "total_surp_RX_sum" in rows[0]:
            print(f"- median total S: correct issue {np.median([r['total_surp_R_sum'] for r in rows]):.1f} nats, wrong issue {np.median([r['total_surp_RX_sum'] for r in rows]):.1f} nats")
    extras(rows)
    print("\n**Paired differences (percentage points, bootstrap 95% CI, two-sided p; Holm = Holm-adjusted over the tests listed)**\n")
    H, S = "lrank_drop_R-RX_pos", "lrank_surp_R_sum"
    UH, US = "urank_drop_R-RX_pos|sum", "urank_surp_R_sum|sum"
    res = []
    for label, a, b, k in [
        ("line hit@10: H − BM25", H, "lrank_bm25", 10), ("line hit@10: S − BM25", S, "lrank_bm25", 10),
        ("line hit@10: H − generative", H, "lrank_gen", 10), ("line hit@10: S − generative", S, "lrank_gen", 10),
        ("line hit@10: S − wrong-issue S", S, "lrank_surp_RX_sum", 10),
        ("line hit@10: H − generative (quoted)", H, "lrank_gen2", 10), ("line hit@5: H − generative (quoted)", H, "lrank_gen2", 5),
        ("line hit@1: H − generative (quoted)", H, "lrank_gen2", 1),
        ("function hit@1: H − BM25", UH, "urank_bm25_unit", 1), ("function hit@1: H − generative", UH, "urank_gen", 1),
        ("function hit@3: H − BM25", UH, "urank_bm25_unit", 3), ("function hit@3: H − generative", UH, "urank_gen", 3),
        ("function hit@1: S − generative", US, "urank_gen", 1), ("function hit@5: H − generative", UH, "urank_gen", 5),
        ("line hit@1: H − generative", H, "lrank_gen", 1), ("line hit@5: H − generative", H, "lrank_gen", 5),
        ("line hit@1: hybrid − generative", "lrank_hybrid", "lrank_gen", 1), ("line hit@10: hybrid − H", "lrank_hybrid", H, 10), ("line hit@1: hybrid − H", "lrank_hybrid", H, 1),
        ("function hit@1: H − generative (quoted)", UH, "urank_gen2", 1), ("function hit@3: H − generative (quoted)", UH, "urank_gen2", 3),
        ("function hit@5: H − generative (quoted)", UH, "urank_gen2", 5),
        ("line hit@10: S − 'print unchanged' control", S, "lrank_surp_RB_sum", 10),
    ]:
        r = paired(rows, a, b, k)
        if r:
            res.append((label, r))
    order = sorted(range(len(res)), key=lambda i: res[i][1][3])
    holm, run = {}, 0.0
    for j, i in enumerate(order):
        run = max(run, min(1.0, (len(res) - j) * max(res[i][1][3], 1e-4)))
        holm[i] = run
    for i, (label, r) in enumerate(res):
        ps = "p < 0.0001" if r[3] < 1e-4 else f"p = {r[3]:.4f}"
        print(f"- {label}: {100*r[0]:+.1f} [{100*r[1]:+.1f}, {100*r[2]:+.1f}], {ps}, Holm {'< 0.01' if holm[i] < 0.01 else f'{holm[i]:.3f}'}")


if __name__ == "__main__":
    main()
