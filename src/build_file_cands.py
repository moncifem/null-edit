"""File-level candidates for experiment E4: gold file(s) + top-K BM25 non-gold source files.

For each instance: BM25(issue, file content) over every non-test .py file at the base commit.
Output: results/file_cands.json {iid: {"paths": [...], "bm25_rank": {path: rank}, "gold": [...]}}
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from rank_bm25 import BM25Okapi
from analyze_conflict import bm25_tokens
from common import RESULTS, gold_edits, is_test_path, list_py_files, load_instances, repo_dir

K = int(sys.argv[2]) if len(sys.argv) > 2 else 3
N = int(sys.argv[1]) if len(sys.argv) > 1 else 120
MAX_CHARS = 60000  # ~ <= 18k tokens

def read_all(repo, commit, paths):
    p = subprocess.Popen(["git", "-C", str(repo_dir(repo)), "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, _ = p.communicate("".join(f"{commit}:{x}\n" for x in paths).encode())
    res, i = {}, 0
    for x in paths:
        j = out.index(b"\n", i); head = out[i:j].split(); i = j + 1
        if len(head) < 3: continue
        size = int(head[2]); res[x] = out[i:i+size].decode("utf-8", "replace"); i += size + 1
    return res

insts = {i["instance_id"]: i for i in load_instances()}
ids = open(RESULTS / "test_ids.txt").read().split()
out = {}
for iid in ids:
    if len(out) >= N: break
    inst = insts[iid]
    gold = [p for p in gold_edits(inst["patch"]) if p.endswith(".py") and not is_test_path(p)]
    if len(gold) != 1 or len(gold_edits(inst["patch"])) != 1: continue
    paths = [p for p in list_py_files(inst["repo"], inst["base_commit"]) if not is_test_path(p)]
    files = read_all(inst["repo"], inst["base_commit"], paths)
    if gold[0] not in files or len(files[gold[0]]) > MAX_CHARS: continue
    keep = [p for p in paths if p in files and 200 < len(files[p])]
    bm = BM25Okapi([bm25_tokens(files[p]) or ["_"] for p in keep])
    sc = bm.get_scores(bm25_tokens(inst["problem_statement"]))
    order = [keep[i] for i in np.argsort(-sc)]
    rank = {p: r for r, p in enumerate(order, 1)}
    distract = [p for p in order if p != gold[0] and len(files[p]) <= MAX_CHARS][:K]
    out[iid] = {"paths": [gold[0]] + distract, "gold": gold, "bm25_rank": {p: rank[p] for p in [gold[0]] + distract}, "n_files": len(keep)}
    print(len(out), iid, "gold bm25 rank", rank[gold[0]], "of", len(keep), flush=True)
json.dump(out, open(RESULTS / "file_cands.json", "w"), indent=0)
json.dump({k: v["paths"] for k, v in out.items()}, open(RESULTS / "file_cands_paths.json", "w"))
open(RESULTS / "file_ids.txt", "w").write("\n".join(out) + "\n")
r = np.array([v["bm25_rank"][v["gold"][0]] for v in out.values()])
print("instances", len(out), "BM25 gold file hit@1", (r <= 1).mean(), "hit@5", (r <= 5).mean(), "hit@10", (r <= 10).mean(), "median", np.median(r))
