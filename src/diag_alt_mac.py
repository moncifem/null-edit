"""What does 12B write instead? (MAC arm, MLX 4-bit; qualitative.)

For long files of the length check, take the tokens that are very surprising (p < 0.1) under the WRONG issue in BOTH
the laptop's 4-bit run and the DGX arm's bf16 run, and let the 4-bit model continue greedily from just before each one.
Usage: python diag_alt_mac.py [--model ../data/models/gemma-4-12B-it-4bit] [--per-file 3]
"""
import argparse, json, os, time
import numpy as np
from common import file_at, load_instances
from run_conflict import PROMPTS, key, trunc_issue
from scorer import Scorer

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="../data/models/gemma-4-12B-it-4bit")
ap.add_argument("--per-file", type=int, default=3)
ap.add_argument("--frame", default="R")
a = ap.parse_args()
M, D = "../results/conflict_g12b_lencheck", "../results_dgx/conflict_g12b_test"
insts = {i["instance_id"]: i for i in load_instances()}
sc = Scorer(a.model)
thr = float(os.environ.get("THROTTLE", "0"))
for l in open(M + "/log.jsonl"):
    r = json.loads(l)
    if "secs" not in r or r["n_tok"] < 5000:
        continue
    k = key(r["iid"], r["path"])
    zm, zd = np.load(f"{M}/{k}.npz"), np.load(f"{D}/{k}.npz")
    f = "lp_" + a.frame
    both = np.where((zm[f] < np.log(0.1)) & (zd[f] < np.log(0.1)))[0]
    if not len(both):
        continue
    both = both[np.argsort(zd[f][both])][: a.per_file]
    inst = insts[r["iid"]]
    src = file_at(inst["repo"], inst["base_commit"], r["path"])
    target = src if src.endswith("\n") else src + "\n"
    iss = insts[r["x_issue"]] if a.frame == "RX" else inst   # RX: the wrong issue the stored run used
    user = PROMPTS["R"].format(path=r["path"], repo=inst["repo"], issue=trunc_issue(iss["problem_statement"]), file=target)
    prefix = sc.chat_prefix(user, "```python\n")
    print(f"\n{r['iid']} {r['path']} ({r['n_tok']} tokens)", flush=True)
    for t in both:
        t0 = time.time()
        s0 = int(zm["offsets"][t][0])
        g = sc.generate(sc.encode(prefix + target[:s0]), 24, temp=0.0)
        print(f"  token {t}: p(bf16) = {np.exp(zd[f][t]):.4f}, p(4-bit) = {np.exp(zm[f][t]):.4f}\n"
              f"    before   {target[max(0, s0 - 70):s0]!r}\n    original {target[s0:s0 + 70]!r}\n    model    {g['text'][:90]!r}", flush=True)
        if thr:
            time.sleep(thr * (time.time() - t0))
