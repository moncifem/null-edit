"""Is the issue-independent surprisal of a model on long files a property of the model or of our scoring loop?
Scores the R frame of a few long held-out files three ways: chunk 1024 with KV cache (what every run uses),
chunk 4096, and one single pass without cache. Prints per-file totals, the largest per-token difference and
the text around the most surprising tokens.

Usage: python diag_long.py --model ../data/models/gemma-4-12B-it --ref-tag g12b_test [--n 4] [--min-tok 8000] [--max-tok 14000]
"""
import argparse, json
import numpy as np
from common import RESULTS, file_at, load_instances
from run_conflict import PROMPTS, key, trunc_issue
from scorer import Scorer

ap = argparse.ArgumentParser()
ap.add_argument("--model", required=True)
ap.add_argument("--ref-tag", required=True)
ap.add_argument("--n", type=int, default=4)
ap.add_argument("--min-tok", type=int, default=8000)
ap.add_argument("--max-tok", type=int, default=14000)
a = ap.parse_args()
sc = Scorer(a.model)
insts = {i["instance_id"]: i for i in load_instances()}
rows = [json.loads(l) for l in open(RESULTS / f"conflict_{a.ref_tag}" / "log.jsonl")]
rows = [r for r in rows if "skip" not in r and a.min_tok <= r["n_tok"] <= a.max_tok][: a.n]
for r in rows:
    inst = insts[r["iid"]]
    src = file_at(inst["repo"], inst["base_commit"], r["path"])
    target = src if src.endswith("\n") else src + "\n"
    user = PROMPTS["R"].format(path=r["path"], repo=inst["repo"], issue=trunc_issue(inst["problem_statement"]), file=target)
    prefix = sc.chat_prefix(user, "```python\n")
    res = {}
    for c in (1024, 512, 4096):
        sc.chunk = c
        res[c] = sc.score(prefix, target)
    ref = np.load(RESULTS / f"conflict_{a.ref_tag}" / (key(r["iid"], r["path"]) + ".npz"))["lp_R"]
    b = res[1024].logp.astype(np.float64)
    print(f'\n{r["iid"]} {r["path"]} tok {len(b)}')
    for c, s in res.items():
        lp = s.logp.astype(np.float64)
        print(f"  chunk {c if c < 10**9 else 'single pass'}: total nats {-lp.sum():.2f}, tokens p<0.1: {(lp < np.log(0.1)).sum()}, "
              f"max|d| vs chunk 1024: {np.abs(lp - b).max():.3f}, corr {np.corrcoef(lp, b)[0, 1]:.4f}")
    print(f"  stored run: total nats {-ref.astype(np.float64).sum():.2f}, max|d| vs now {np.abs(ref - res[1024].logp).max():.3f}")
    offs = res[1024].offsets
    for t in np.argsort(b)[:4]:
        s0, e0 = int(offs[t][0]), int(offs[t][1])
        print(f"    p={np.exp(b[t]):.4f} at char {s0}: ...{target[max(0, s0 - 60):s0]!r} >>{target[s0:e0]!r}<< {target[e0:e0 + 30]!r}")
    # what would the model write instead? greedy continuation from just before the three most surprising tokens
    for t in np.argsort(b)[:3]:
        s0 = int(offs[t][0])
        g = sc.generate(sc.encode(prefix + target[:s0]), 24, temp=0.0)
        print(f"    at char {s0} (token {t} of {len(b)}): original continues {target[s0:s0 + 70]!r}\n      model writes {g['text'][:90]!r}", flush=True)
