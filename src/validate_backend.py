"""Sanity checks for a scorer backend (run on the DGX):
 1. chat template string, 2. chunked-with-cache scoring == single-pass scoring,
 3. agreement with the laptop (MLX 4-bit) per-token log-probs on DEV files, 4. throughput."""
import json, sys, time
import numpy as np
from common import RESULTS, file_at, gold_edits, load_instances
from run_conflict import PROMPTS, key, trunc_issue
from scorer import BACKEND, Scorer, line_scores

model = sys.argv[1]
ref_dir = RESULTS / "conflict_e4b_devR"  # laptop results, rsynced
sc = Scorer(model)
print("backend", BACKEND, "| prefix:", repr(sc.chat_prefix("hi", "```python\n")))
insts = {i["instance_id"]: i for i in load_instances()}
rows = [json.loads(l) for l in open(ref_dir / "log.jsonl")]
rows = [r for r in rows if "skip" not in r and r["n_tok"] < 6000][:6]
for r in rows:
    inst = insts[r["iid"]]
    src = file_at(inst["repo"], inst["base_commit"], r["path"])
    target = src if src.endswith("\n") else src + "\n"
    user = PROMPTS["R"].format(path=r["path"], repo=inst["repo"], issue=trunc_issue(inst["problem_statement"]), file=target)
    prefix = sc.chat_prefix(user, "```python\n")
    s1 = sc.score(prefix, target)
    old = sc.chunk
    sc.chunk = 10**9
    s2 = sc.score(prefix, target)
    sc.chunk = old
    z = np.load(ref_dir / (key(r["iid"], r["path"]) + ".npz"))
    ref = z["lp_R"]
    same_tok = len(ref) == len(s1.logp) and np.array_equal(z["offsets"], s1.offsets)
    buckets = line_scores(target, s1)
    S = np.array([-s1.logp[b].sum() if b else 0 for b in buckets])
    Sref = np.array([-ref[b].sum() if b else 0 for b in buckets]) if same_tok else None
    gold = sorted(gold_edits(inst["patch"])[r["path"]].lines)
    order = np.argsort(-S)
    grank = min(int(np.where(order == g - 1)[0][0]) + 1 for g in gold if g <= len(S))
    print(f'{r["iid"]} {r["path"]} tok {len(s1.logp)} | chunked-vs-single max|d| {np.abs(s1.logp - s2.logp).max():.4f} '
          f'| same tokenization as laptop: {same_tok} | corr(logp) vs laptop 4-bit: {np.corrcoef(ref, s1.logp)[0,1] if same_tok else float("nan"):.3f} '
          f'| corr(line S): {np.corrcoef(S, Sref)[0,1] if same_tok else float("nan"):.3f} | best gold rank {grank} | {round((s1.n_prefix + len(s1.logp)) / s1.seconds)} tok/s')
g = sc.generate(sc.encode(sc.chat_prefix("Write a Python function that reverses a linked list.")), 120)
print("generation:", round(g["gen_tps"]), "tok/s; prefill", round(g["prompt_tps"]), "tok/s;", repr(g["text"][:80]))
