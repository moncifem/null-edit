"""Asking the model against its own null-edit map, at every Gemma 4 size (section 4.6).

Reads the per-size analysis files (an_<tag>.json, which hold the generated-answer ranks) and the
code-lines-only ranks written by analyze_codeonly.py (codeonly_sizes.json), on the same files.
Prints hit rates and paired differences with instance-clustered bootstrap intervals.

Usage (from src/): NULLEDIT_RESULTS=../results_dgx python asked_vs_map.py
Not pre-registered: the asking baseline was pre-registered for E4B only.
"""
from __future__ import annotations

import json

import numpy as np

from common import RESULTS

SIZES = [("E2B", "an_e2b_test.json"), ("E4B", "an_e4b_test.json"), ("12B", "an_g12b_test.json"), ("26B-A4B", "an_g26b_test.json")]
B = 10000


def boot(keys, vals, rng):
    """Mean and 95% interval of vals (one per file), resampling instances."""
    by = {}
    for (iid, _), v in zip(keys, vals):
        by.setdefault(iid, []).append(v)
    groups = [np.array(g, float) for g in by.values()]
    sums = np.array([g.sum() for g in groups]); ns = np.array([len(g) for g in groups])
    idx = rng.integers(0, len(groups), (B, len(groups)))
    bs = sums[idx].sum(1) / ns[idx].sum(1)
    return 100 * float(np.mean(vals)), 100 * float(np.percentile(bs, 2.5)), 100 * float(np.percentile(bs, 97.5))


def main():
    rng = np.random.default_rng(0)
    code = json.load(open(RESULTS / "codeonly_sizes.json"))
    f = lambda t: f"{t[0]:.0f} [{t[1]:.0f}, {t[2]:.0f}]"
    g = lambda t: f"{t[0]:+.1f} [{t[1]:+.1f}, {t[2]:+.1f}]"
    print("**Asked for line ranges against the model's own map, same files** (hit %, instance-clustered bootstrap)\n")
    print("| Model | files | asked line@10 | map line@10 | map, code lines only, line@10 | asked − map | asked − code-only map | asked func@1 | map func@1 | asked − map, func@1 | asked func@5 | map func@5 |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    out = {}
    for name, fn in SIZES:
        rows = {(r["iid"], r["path"]): r for r in json.load(open(RESULTS / fn))["rows"]}
        co = {(r["iid"], r["path"]): r for r in code[name]}
        keys = sorted(k for k in co if k in rows and "lrank_gen" in rows[k])
        if not keys:
            continue
        a = np.array([rows[k]["lrank_gen"] <= 10 for k in keys], float)
        m = np.array([rows[k]["lrank_surp_R_sum"] <= 10 for k in keys], float)
        c = np.array([co[k]["code"] for k in keys], float)
        af = np.array([rows[k]["urank_gen"] <= 1 for k in keys], float)
        mf = np.array([rows[k]["urank_surp_R_sum|sum"] <= 1 for k in keys], float)
        af5 = np.array([rows[k]["urank_gen"] <= 5 for k in keys], float)
        mf5 = np.array([rows[k]["urank_surp_R_sum|sum"] <= 5 for k in keys], float)
        b = [boot(keys, v, rng) for v in (a, m, c, a - m, a - c, af, mf, af - mf, af5, mf5)]   # same order as the columns
        cells = [(g if i in (3, 4, 7) else f)(t) for i, t in enumerate(b)]
        print(f"| {name} | {len(keys)} | " + " | ".join(cells) + " |")
        out[name] = {"n": len(keys), "asked_line10": b[0], "map_line10": b[1], "code_line10": b[2],
                     "asked_func1": b[5], "map_func1": b[6]}   # each: [estimate, low, high] in percent
    json.dump(out, open(RESULTS / "asked_sizes.json", "w"), indent=1)


if __name__ == "__main__":
    main()
