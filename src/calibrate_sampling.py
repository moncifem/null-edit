"""E3: check the first-deviation identity against REAL generation.

Identity: if p_t = P(original token t | prompt, original tokens < t), then under ancestral sampling
(temperature 1, no top-k/top-p) the first position where a sampled rewrite differs from the
original is distributed as P(tau = t) = (1 - p_t) * prod_{s<t} p_s, and P(no deviation) = prod p_t.

We actually generate K rewrites per file with mlx-lm's ordinary generation loop (same prompt as
frame R, temperature 1), stop each sample at its first deviation from the original, and compare the
empirical first-deviation lines with the single-pass teacher-forced prediction.
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np

from common import RESULTS, file_at, gold_edits, is_test_path, load_instances
from run_conflict import PROMPTS, trunc_issue
from scorer import Scorer, line_scores


def seed_everything(seed: int):
    try:
        import mlx.core as mx

        mx.random.seed(seed)
    except Exception:
        pass
    try:
        import torch

        torch.manual_seed(seed)
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--instances", required=True)
    ap.add_argument("--k", type=int, default=30)
    ap.add_argument("--max-file-tokens", type=int, default=1200)
    ap.add_argument("--max-files", type=int, default=6)
    args = ap.parse_args()
    insts = {i["instance_id"]: i for i in load_instances()}
    ids = [l.strip() for l in open(args.instances) if l.strip()]
    sc = Scorer(args.model)
    out = open(RESULTS / f"calib_{args.tag}.jsonl", "a")
    seed_everything(0)
    n_files = 0
    for iid in ids:
        inst = insts[iid]
        for path in [p for p in gold_edits(inst["patch"]) if p.endswith(".py") and not is_test_path(p)]:
            if n_files >= args.max_files:
                return
            src = file_at(inst["repo"], inst["base_commit"], path)
            target = src if src.endswith("\n") else src + "\n"
            t_ids = sc.encode(target)
            if len(t_ids) > args.max_file_tokens or len(t_ids) < 100:
                continue
            n_files += 1
            user = PROMPTS["R"].format(path=path, repo=inst["repo"], issue=trunc_issue(inst["problem_statement"]), file=target)
            prefix = sc.chat_prefix(user, "```python\n")
            s = sc.score(prefix, target)  # single teacher-forced pass
            p_ids = sc.encode(prefix)
            first_dev, gen_tokens = [], 0
            t0 = time.time()
            for k in range(args.k):
                g = sc.generate(p_ids, len(t_ids), temp=1.0,
                                stop_fn=lambda toks: toks[-1] != t_ids[len(toks) - 1])
                toks = g["tokens"]
                gen_tokens += len(toks)
                # first deviation: last generated token differs, or generation ended early (EOS = deviation)
                if toks and toks[-1] != t_ids[len(toks) - 1]:
                    dev = len(toks) - 1
                elif len(toks) < len(t_ids):
                    dev = len(toks)
                else:
                    dev = -1
                first_dev.append(dev)
            secs = time.time() - t0
            buckets = line_scores(target, s)
            tok2line = np.zeros(len(t_ids), int)
            for li, b in enumerate(buckets):
                tok2line[b] = li
            S = np.array([-s.logp[b].sum() if b else 0.0 for b in buckets])
            before = np.concatenate([[0.0], np.cumsum(S)[:-1]])
            pred_first = (1 - np.exp(-S)) * np.exp(-before)
            rec = {"iid": iid, "path": path, "n_tok": len(t_ids), "k": args.k,
                   "pred_no_edit": float(np.exp(s.logp.astype(np.float64).sum())),
                   "emp_no_edit": float(np.mean(np.array(first_dev) < 0)),
                   "first_dev_tokens": first_dev,
                   "first_dev_lines": [int(tok2line[t]) + 1 if t >= 0 else -1 for t in first_dev],
                   "pred_first_line": pred_first.tolist(), "score_secs": round(s.seconds, 2),
                   "gen_secs": round(secs, 1), "gen_tokens": gen_tokens}
            out.write(json.dumps(rec) + "\n")
            out.flush()
            print(iid, path, len(t_ids), "pred P(no edit)", round(rec["pred_no_edit"], 3), "emp", rec["emp_no_edit"],
                  "score", rec["score_secs"], "s vs gen", rec["gen_secs"], "s", flush=True)


if __name__ == "__main__":
    main()
