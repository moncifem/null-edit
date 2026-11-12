"""Numbers quoted in the paper that no other report prints. CPU only, from saved analysis rows.
Usage (from src/): NULLEDIT_RESULTS=../results_dgx python paper_numbers.py > ../results_dgx/report_paper_numbers.md
"""
import json
from pathlib import Path

import numpy as np

from common import RESULTS, load_instances
from report import boot

ROOT = Path(__file__).resolve().parent.parent
H, S, B, UH = "lrank_drop_R-RX_pos", "lrank_surp_R_sum", "lrank_bm25", "urank_drop_R-RX_pos|sum"


def rows(f, base=RESULTS):
    p = Path(base) / f
    return {(r["iid"], r["path"]): r for r in json.load(open(p))["rows"]} if p.exists() else None


def diff(a, b, keys, key, k, la, lb):
    fa, fb = 100 * np.mean([a[x][key] <= k for x in keys]), 100 * np.mean([b[x][key] <= k for x in keys])
    p, lo, hi, _ = boot([{"iid": x[0], "d": float(a[x][key] <= k) - float(b[x][key] <= k)} for x in keys], lambda r: r["d"])
    print(f"- {key}@{k}: {la} {fa:.1f} vs {lb} {fb:.1f}; difference {100*p:+.1f} [{100*lo:+.1f}, {100*hi:+.1f}] ({len(keys)} files, {len({x[0] for x in keys})} issues)")


E = rows("an_e4b_test.json")
print("## Held-out Verified, E4B (DGX arm)\n")
log = [json.loads(l) for l in open(RESULTS / "conflict_e4b_test" / "log.jsonl")]
ids = set(open(ROOT / "results" / "test_ids.txt").read().split()[:250])
log = [r for r in log if r["iid"] in ids]
print(f"- gold source files of the first 250 held-out issues: {len(log)}; scored: {sum('skip' not in r for r in log)}; analysed: {len(E)}")
print(f"- ranking lines by first-edit probability P(tau in line): line hit@10 {100*np.mean([r['lrank_first_R'] <= 10 for r in E.values()]):.1f}")
noop = [r for r in E.values() if r["min_p_R"] >= 0.5]
pn = np.exp(-np.array([r["total_surp_R_sum"] for r in noop]))
print(f"- files where every token has p >= 0.5: {len(noop)} files, {len({r['iid'] for r in noop})} issues; median P(no edit) {np.median(pn):.2f}; "
      f"files with min p in [0.5, 0.6): {sum(r['min_p_R'] < 0.6 for r in noop)}")
cb = RESULTS / "context_budget_e4b_test.json"
if cb.exists() and "lrank_gen" in next(iter(E.values())):
    nl = {(r["iid"], r["path"]): r["n_lines"] for r in json.load(open(cb))["rows"]}
    print(f"- line-range answer lists a gold line anywhere: {100*np.mean([E[k]['lrank_gen'] <= nl[k] for k in E if k in nl]):.1f}% of {sum(k in nl for k in E)} files")
qa = rows("an_e4b_test_quoteall.json")
if qa:
    print(f"- quoted answer, line hit@10: strict all-occurrences mapping {100*np.mean([r['lrank_gen2'] <= 10 for r in qa.values()]):.1f}, aligned mapping {100*np.mean([r['lrank_gen2'] <= 10 for r in E.values()]):.1f}")

Q = rows("an_e4b_q4_test.json")
M = rows("an_e4b_test.json", ROOT / "results")
if Q:
    print("\n## 4-bit weights (MLX checkpoint de-quantized into the DGX code)\n")
    ks = sorted(set(Q) & set(E))
    diff(E, Q, ks, H, 10, "bf16", "4-bit on DGX")
    diff(E, Q, ks, UH, 1, "bf16", "4-bit on DGX")
    p, lo, hi, _ = boot([{"iid": x[0], "d": float(Q[x][H] <= 10) - float(Q[x][B] <= 10)} for x in ks], lambda r: r["d"])
    print(f"- 4-bit on DGX, H − BM25 line@10: {100*p:+.1f} [{100*lo:+.1f}, {100*hi:+.1f}]; function@1 H {100*np.mean([Q[x][UH] <= 1 for x in ks]):.1f} vs BM25 {100*np.mean([Q[x]['urank_bm25_unit'] <= 1 for x in ks]):.1f}")
    if M:
        ks = sorted(set(Q) & set(M))
        diff(Q, M, ks, H, 10, "4-bit on DGX", "4-bit on MAC")
        diff(Q, M, ks, UH, 1, "4-bit on DGX", "4-bit on MAC")

L = rows("an_e4b_live.json")
if L:
    print("\n## SWE-bench-Live, post-cutoff\n")
    live_repos = {r["repo"] for r in L.values()}
    ver_repos = {i["repo"] for i in load_instances()}
    print(f"- {len(L)} files, {len({k[0] for k in L})} issues, {len(live_repos)} repositories, {len(live_repos - ver_repos)} of them not in SWE-bench Verified "
          f"(shared: {', '.join(sorted(live_repos & ver_repos)) or 'none'})")
    noop = [r for r in L.values() if r["min_p_R"] >= 0.5]
    print(f"- files where every token has p >= 0.5: {len(noop)}; line hit@10 S {100*np.mean([r[S] <= 10 for r in noop]):.1f}, H {100*np.mean([r[H] <= 10 for r in noop]):.1f}, BM25 {100*np.mean([r[B] <= 10 for r in noop]):.1f}")

print("\n## Label-free check: S line hit@10 by the file's total hazard (threshold 50 nats, post hoc)\n")
runs = [(n, rows(f)) for n, f in (("E2B", "an_e2b_test.json"), ("E4B", "an_e4b_test.json"), ("12B", "an_g12b_test.json"),
                                  ("26B-A4B", "an_g26b_test.json"), ("26B-A4B", "an_g26b_test_h.json"), ("31B", "an_g31b_test.json"), ("31B", "an_g31b_test_h.json"))]
runs = [(n, a) for n, a in runs if a]
common = sorted(set.intersection(*[set(a) for _, a in runs]))
print(f"{len(common)} common files\n\n| Model | total hazard ≤ 50 nats | > 50 nats |\n|---|---|---|")
for n, a in runs:
    tot = np.array([a[k]["total_surp_R_sum"] for k in common]); hit = np.array([a[k][S] <= 10 for k in common]); m = tot <= 50
    f = lambda x: f"{100*hit[x].mean():.0f}% ({hit[x].sum()}/{x.sum()})" if x.sum() else "– (0 files)"
    print(f"| {n} | {f(m)} | {f(~m)} |")
