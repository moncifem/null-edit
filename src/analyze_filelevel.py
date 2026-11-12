"""E4: file-level ranking. Candidates = gold file + top-3 BM25 non-gold files (hard negatives).
File scores from null-edit maps; metric = rank of the gold file among the 4 candidates."""
import json, sys
from collections import defaultdict
import numpy as np
from analyze_conflict import line_features
from common import RESULTS, file_at, load_instances
from run_conflict import key

import argparse, re
ap = argparse.ArgumentParser(); ap.add_argument("--tag", required=True); tag = ap.parse_args().tag
tie = np.random.default_rng(0)
insts = {i["instance_id"]: i for i in load_instances()}
cands = json.load(open(RESULTS / "file_cands.json"))
d = RESULTS / f"conflict_{tag}"
have = {(r["iid"], r["path"]): r for r in map(json.loads, open(d / "log.jsonl")) if "skip" not in r}
rows = []
for iid, c in cands.items():
    if not all((iid, p) in have for p in c["paths"]):
        continue
    inst = insts[iid]
    sc = defaultdict(dict)
    for p in c["paths"]:
        z = np.load(d / (key(iid, p) + ".npz"))
        f = line_features(file_at(inst["repo"], inst["base_commit"], p), z)
        H, S, SX = f["drop_R-RX_pos"], f["surp_R_sum"], f["surp_RX_sum"]
        nt = f["ntok"].sum()
        sc["H_total"][p] = H.sum()
        sc["H_max_line"][p] = H.max()
        sc["H_top5"][p] = np.sort(H)[-5:].sum()
        sc["H_per_ktok"][p] = H.sum() / nt
        sc["S_total"][p] = S.sum()
        sc["S_max_line"][p] = S.max()
        sc["S_top5"][p] = np.sort(S)[-5:].sum()
        sc["dS_total (S - S_wrong)"][p] = S.sum() - SX.sum()
        sc["P(edit) = 1-exp(-S)"][p] = 1 - np.exp(-S.sum())
        sc["wrong-issue S_top5"][p] = np.sort(SX)[-5:].sum()
        sc["file length (tokens)"][p] = nt
        sc["BM25 (whole repo rank)"][p] = -c["bm25_rank"][p]
        # path baseline: does the issue name the file or its module? (the path is visible in the prompt)
        stem = p.rsplit("/", 1)[-1][:-3]
        issue = inst["problem_statement"]
        sc["path named in issue"][p] = 2.0 * (p in issue) + 1.0 * bool(re.search(r"(?<![A-Za-z0-9_])" + re.escape(stem) + r"(?![A-Za-z0-9_])", issue))
        sc["random"][p] = tie.random()
    g = c["gold"][0]
    row = {"iid": iid}
    for name, m in sc.items():
        order = sorted(m, key=lambda p: (-m[p], tie.random()))  # random tie-breaking (never favours the gold file)
        row[name] = order.index(g) + 1
    rows.append(row)
print(f"instances: {len(rows)} (4 candidates each; chance hit@1 = 25%)")
rng = np.random.default_rng(0)
print(f"{'file score':28s} {'hit@1':>18s} {'MRR':>6s}")
for name in [k for k in rows[0] if k != "iid"]:
    r = np.array([x[name] for x in rows])
    bs = [(r[rng.integers(0, len(r), len(r))] <= 1).mean() for _ in range(5000)]
    print(f"{name:28s} {100*(r<=1).mean():5.1f} [{100*np.percentile(bs,2.5):.0f}, {100*np.percentile(bs,97.5):.0f}] {np.mean(1/r):6.3f}")
json.dump(rows, open(RESULTS / f"an_filelevel_{tag}.json", "w"))
