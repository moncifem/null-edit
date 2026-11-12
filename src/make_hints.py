"""Hints for run_edit.py: five lines per file and arm. CPU only, from saved scores.

  H      the five highest null-edit-hazard lines (most likely first)
  WRONG  the five highest-hazard lines under the WRONG issue: same kind of lines (hard to copy), no information
         about this issue -> the placebo
  GOLD   lines the human fix edits (up to five, padded with random lines, shuffled) -> the ceiling
  BM25   the five highest-BM25 lines (a lexical hint; not run by default)

Usage: python make_hints.py --tag e4b_test --ids ../results/test_ids.txt --limit 100 --out ../results_dgx/hints_e4b_test.json
"""
from __future__ import annotations

import argparse
import json

import numpy as np
from rank_bm25 import BM25Okapi

from analyze_conflict import bm25_tokens, fix_anchors, frng, line_features
from common import RESULTS, file_at, gold_edits, load_instances
from run_conflict import key

ap = argparse.ArgumentParser()
ap.add_argument("--tag", required=True)
ap.add_argument("--ids", required=True)
ap.add_argument("--limit", type=int, default=None)
ap.add_argument("--k", type=int, default=5)
ap.add_argument("--out", required=True)
args = ap.parse_args()
insts = {i["instance_id"]: i for i in load_instances()}
keep = set([l.strip() for l in open(args.ids) if l.strip()][: args.limit])
d = RESULTS / f"conflict_{args.tag}"
rng = np.random.default_rng(0)
out = {}
for r in map(json.loads, open(d / "log.jsonl")):
    if "skip" in r or not r.get("gold") or r["iid"] not in keep:
        continue
    k = key(r["iid"], r["path"])
    if k in out or not (d / (k + ".npz")).exists():
        continue
    inst = insts[r["iid"]]
    src = file_at(inst["repo"], inst["base_commit"], r["path"])
    f = line_features(src, np.load(d / (k + ".npz")))
    lines = src.splitlines()
    valid = f["ntok"] > 0
    bm = np.array(BM25Okapi([bm25_tokens(l) or ["_"] for l in lines]).get_scores(bm25_tokens(inst["problem_statement"])))
    rec = {}
    for name, sc in (("H", f["drop_R-RX_pos"]), ("WRONG", f["surp_RX_sum"]), ("BM25", bm)):
        s = np.where(valid, sc + 1e-9 * rng.random(len(lines)), -1e9)
        rec[name] = [[int(i) + 1, lines[i].strip()[:160]] for i in np.argsort(-s)[: args.k]]
    g = frng(k, "goldhint")
    gold = sorted(fix_anchors(gold_edits(inst["patch"])[r["path"]], valid, len(lines), "all"))
    pick = [int(x) for x in g.permutation(gold)[: args.k]]
    rest = [i + 1 for i in np.flatnonzero(valid) if i + 1 not in gold]
    pick += [int(x) for x in g.permutation(rest)[: args.k - len(pick)]]
    rec["GOLD"] = [[int(l), lines[int(l) - 1].strip()[:160]] for l in g.permutation(pick)]
    out[k] = rec
open(args.out, "w").write(json.dumps(out))
print(len(out), "files")
