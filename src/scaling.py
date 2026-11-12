"""Model-size scaling table on the files common to all runs.

Usage: python scaling.py NAME=an_file.json [NAME=an_file.json ...]
Prints hit rates (%) with instance-clustered bootstrap CIs for the null-edit scores and the
generated-answer baseline of every model on the same files.
"""
from __future__ import annotations

import json
import sys

from common import RESULTS
from report import boot

COLS = [("S line@1", "lrank_surp_R_sum", 1), ("S line@10", "lrank_surp_R_sum", 10), ("H line@10", "lrank_drop_R-RX_pos", 10),
        ("wrong-issue line@10", "lrank_surp_RX_sum", 10), ("asked (ranges) line@10", "lrank_gen", 10),
        ("quoted answer line@10", "lrank_gen2", 10), ("BM25 line@10", "lrank_bm25", 10),
        ("S func@1", "urank_surp_R_sum|sum", 1), ("H func@1", "urank_drop_R-RX_pos|sum", 1), ("asked (ranges) func@1", "urank_gen", 1),
        ("quoted answer func@1", "urank_gen2", 1), ("S func@5", "urank_surp_R_sum|sum", 5), ("H func@5", "urank_drop_R-RX_pos|sum", 5),
        ("asked (ranges) func@5", "urank_gen", 5), ("no-op files (%)", "min_p_R", None)]


CUTS = (5000, 11000)   # chosen post hoc: 5,000 after seeing the first three sizes; 11,000 is 31B's memory limit
STRATA = [("under 5,000 tokens", 0, CUTS[0]), ("5,000 to 11,000 tokens", CUTS[0], CUTS[1]), ("over 11,000 tokens", CUTS[1], 10**9)]


def main():
    """Arguments NAME=an_file.json; a name ending in '*' marks a run that covers only part of the files
    (31B: files up to 11,000 tokens) — it does not restrict the common set and is reported where it has files."""
    import numpy as np
    runs = []
    for a in sys.argv[1:]:
        name, f = a.split("=")
        rows = {(r["iid"], r["path"]): r for r in json.load(open(RESULTS / f))["rows"]}
        runs.append((name.rstrip("*"), rows, name.endswith("*")))
    common = set.intersection(*[set(r) for _, r, part in runs if not part])
    print(f"{len(common)} common files, {len({k[0] for k in common})} instances\n")
    print("| Model | files | " + " | ".join(c[0] for c in COLS) + " |\n|---|---|" + "---|" * len(COLS))
    out = {}
    for name, rows, part in runs:
        rs = [rows[k] for k in sorted(common) if k in rows]
        cells = []
        for lab, key, k in COLS:
            if any(key not in r for r in rs):
                cells.append("–")
                continue
            p, lo, hi, _ = boot(rs, (lambda r: r[key] >= 0.5) if k is None else (lambda r: r[key] <= k))
            cells.append(f"{100*p:.0f} [{100*lo:.0f}, {100*hi:.0f}]")
            out.setdefault(name, {})[lab] = [100 * p, 100 * lo, 100 * hi]
        print(f"| {name}{' (partial coverage)' if part else ''} | {len(rs)} | " + " | ".join(cells) + " |")
    # --- by file length: copy fidelity. total_surp_RX_sum is what copying costs with the WRONG issue (nats). ---
    ref = runs[0][1]
    print(f"\n**By file length** (same files; bands chosen post hoc)\n")
    print("| Model | files | S line@10 | H line@10 | S func@1 | BM25 line@10 | median copy cost, right issue (nats) | median copy cost, wrong issue (nats) |\n|---|---|---|---|---|---|---|---|")
    for sname, lo_t, hi_t in STRATA:
        ks = [k for k in sorted(common) if lo_t <= ref[k]["n_tok"] < hi_t]
        for name, rows, part in runs:
            rs = [rows[k] for k in ks if k in rows]
            if len(rs) < 5:
                continue
            cells = []
            for key, k in (("lrank_surp_R_sum", 10), ("lrank_drop_R-RX_pos", 10), ("urank_surp_R_sum|sum", 1), ("lrank_bm25", 10)):
                if any(key not in r for r in rs):
                    cells.append("–")
                    continue
                p, lo, hi, _ = boot(rs, lambda r: r[key] <= k)
                cells.append(f"{100*p:.0f} [{100*lo:.0f}, {100*hi:.0f}]")
                out.setdefault(name, {})[f"{key}@{k}|{sname}"] = [100 * p, 100 * lo, 100 * hi]
            rx = f"{np.median([r['total_surp_RX_sum'] for r in rs]):.1f}" if all("total_surp_RX_sum" in r for r in rs) else "–"
            print(f"| {name}, {sname} | {len(rs)} of {len(ks)} | " + " | ".join(cells) + f" | {np.median([r['total_surp_R_sum'] for r in rs]):.1f} | {rx} |")
            out[name][f"copy_cost_R|{sname}"] = float(np.median([r["total_surp_R_sum"] for r in rs]))
            if rx != "–":
                out[name][f"copy_cost_RX|{sname}"] = float(rx)
            out[name][f"n|{sname}"] = len(rs)
    # --- does the cost of copying grow with file length? ---
    from scipy.stats import spearmanr
    print("\n**Copy cost against file length** (Spearman, right issue; and the label-free check: files whose total hazard exceeds 50 nats)\n")
    print("| Model | Spearman(file tokens, total hazard) | files over 50 nats | S line@10 over 50 nats | S line@10 at or under 50 nats |\n|---|---|---|---|---|")
    for name, rows, part in runs:
        rs = [rows[k] for k in sorted(common) if k in rows]
        rho = spearmanr([r["n_tok"] for r in rs], [r["total_surp_R_sum"] for r in rs])[0]
        hi_ = [r for r in rs if r["total_surp_R_sum"] > 50]
        lo_ = [r for r in rs if r["total_surp_R_sum"] <= 50]
        f = lambda g: f"{100*np.mean([r['lrank_surp_R_sum'] <= 10 for r in g]):.0f}" if len(g) >= 5 else "–"
        print(f"| {name} | {rho:.2f} | {len(hi_)} of {len(rs)} | {f(hi_)} | {f(lo_)} |")
        out[name]["spearman_len_cost"] = float(rho)
        out[name]["over50"] = [len(hi_), len(rs), f(hi_), f(lo_)]
    json.dump({"n_files": len(common), "strata": [s[0] for s in STRATA], "runs": out}, open(RESULTS / "scaling.json", "w"), indent=1)


if __name__ == "__main__":
    main()
