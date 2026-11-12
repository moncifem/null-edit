"""Robustness and breakdown tables from analyze_conflict.py --json rows.
Usage: python extra_stats.py <rows.json> [<other_arm_rows.json>]"""
import json, sys
from collections import defaultdict
import numpy as np
from report import boot

H, S, B = "lrank_drop_R-RX_pos", "lrank_surp_R_sum", "lrank_bm25"
UH, UB = "urank_drop_R-RX_pos|sum", "urank_bm25_unit"
rows = json.load(open(sys.argv[1]))["rows"]

def line(name, rs):
    if len(rs) < 5:
        return
    f = lambda k, t: 100 * np.mean([r[k] <= t for r in rs])
    print(f"| {name} | {len(rs)} | {f(H,10):.0f} | {f(S,10):.0f} | {f(B,10):.0f} | {f(UH,1):.0f} | {f(UB,1):.0f} |")

print("| Subset | files | H line@10 | S line@10 | BM25 line@10 | H func@1 | BM25 func@1 |\n|---|---|---|---|---|---|---|")
line("all", rows)
line("file ≤ 20k tokens (pre-registered cap)", [r for r in rows if r["n_tok"] <= 20000])
line("file > 20k tokens", [r for r in rows if r["n_tok"] > 20000])
line("single-file instances", [r for r in rows if sum(1 for x in rows if x["iid"] == r["iid"]) == 1])
line("patch only adds lines (pure insertion)", [r for r in rows if r["n_removed"] == 0])
line("patch modifies/removes lines", [r for r in rows if r["n_removed"] > 0])
line("1–2 gold lines", [r for r in rows if r["n_gold_lines"] <= 2])
line("≥ 6 gold lines", [r for r in rows if r["n_gold_lines"] >= 6])
by = defaultdict(list)
for r in rows:
    by[r["repo"]].append(r)
for repo, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
    line(repo, rs)
# repo-macro average (each repo equal weight)
mac = lambda k, t: 100 * np.mean([np.mean([r[k] <= t for r in rs]) for rs in by.values() if len(rs) >= 5])
print(f"| repo macro-average (repos with ≥5 files) | – | {mac(H,10):.0f} | {mac(S,10):.0f} | {mac(B,10):.0f} | {mac(UH,1):.0f} | {mac(UB,1):.0f} |")

if len(sys.argv) > 2:
    other = {(r["iid"], r["path"]): r for r in json.load(open(sys.argv[2]))["rows"]}
    common = [(r, other[(r["iid"], r["path"])]) for r in rows if (r["iid"], r["path"]) in other]
    print(f"\nPaired comparison on {len(common)} common files ({len({a['iid'] for a,_ in common})} instances): this arm vs other arm")
    for k, t, lab in ((H, 10, "H line hit@10"), (S, 10, "S line hit@10"), (H, 1, "H line hit@1"), (UH, 1, "H function hit@1")):
        a = np.mean([x[k] <= t for x, _ in common]); b = np.mean([y[k] <= t for _, y in common])
        pr = [dict(iid=x["iid"], d=float(x[k] <= t) - float(y[k] <= t)) for x, y in common]
        p, lo, hi, bs = boot(pr, lambda r: r["d"])
        print(f"- {lab}: {100*a:.1f} vs {100*b:.1f}  (diff {100*p:+.1f} [{100*lo:+.1f}, {100*hi:+.1f}], p = {2*min((bs<=0).mean(), (bs>=0).mean()):.3f})")
