"""Experiment E1: issue-conditioned surprisal maps over source files.

For each (instance, file) we teacher-force the ORIGINAL (pre-fix) file under prompts:
  U  no issue                      "print the file"
  B  issue + "current contents"    (topical conditioning, no fix intent)
  F  issue + "after the fix"       (fix intent)
  X  (control) a DIFFERENT instance's issue from the same repo + "after the fix"
and store per-token log-probs. Nothing is generated.

Usage: python src/run_conflict.py --model data/models/gemma-4-e4b-it-4bit --tag e4b \
          --instances results/pilot_ids.txt [--files gold|cands] [--frames U,B,F,X]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from pathlib import Path

import numpy as np

from common import RESULTS, file_at, gold_edits, is_test_path, load_instances
from scorer import Scorer

MAX_ISSUE_CHARS = 6000
MAX_FILE_TOKENS = 40000

PROMPTS = {
    "U": "Print the complete contents of the file `{path}` from the repository {repo}.",
    "B": (
        "The following GitHub issue was filed against the repository {repo}:\n\n<issue>\n{issue}\n</issue>\n\n"
        "Print the complete current contents of the file `{path}`, exactly as it is now, before the issue is fixed."
    ),
    "F": (
        "The following GitHub issue was filed against the repository {repo}:\n\n<issue>\n{issue}\n</issue>\n\n"
        "Print the complete contents of the file `{path}` after the issue has been fixed."
    ),
}
PROMPTS["X"] = PROMPTS["F"]

# --- "read-then-rewrite" frames: the file is IN the prompt, then teacher-forced as the answer -----
_ISSUE = "The following GitHub issue was filed against the repository {repo}:\n\n<issue>\n{issue}\n</issue>\n\n"
_FILE = "Here is the current content of `{path}`:\n\n```python\n{file}```\n\n"
PROMPTS["R"] = _ISSUE + _FILE + (
    "Rewrite `{path}` so that the issue is fixed. Output the complete file, changing only what is necessary.")
PROMPTS["RX"] = PROMPTS["R"]  # same wording, different (wrong) issue
PROMPTS["RB"] = _ISSUE + _FILE + "Print the complete content of `{path}` again, exactly as it is, without any change."
PROMPTS["R0"] = _FILE + "Print the complete content of `{path}` again, exactly as it is, without any change."
PROMPTS["D"] = _ISSUE + _FILE + (
    "Fix the issue by editing `{path}`. Output the complete file as a unified diff with full context: prefix every "
    "unchanged line with a single space, every removed line with `-`, and every added line with `+`. Do not omit any line.")
PROMPTS["DX"] = PROMPTS["D"]
DIFF_FRAMES = ("D", "DX")


def trunc_issue(s: str) -> str:
    s = s.strip()
    return s if len(s) <= MAX_ISSUE_CHARS else s[:MAX_ISSUE_CHARS] + "\n[...truncated]"


def key(iid: str, path: str) -> str:
    return iid + "__" + hashlib.md5(path.encode()).hexdigest()[:8]


def score_frames(sc, frames, issue, other, path, repo, target, edit_masks):
    arrs, secs, offsets = {}, {}, None
    for fr in frames:
        iss = issue
        if fr.endswith("X"):
            if other is None:
                continue
            iss = trunc_issue(other["problem_statement"])
        user = PROMPTS[fr].format(path=path, repo=repo, issue=iss, file=target)
        if fr in DIFF_FRAMES:
            dtarget = "".join(" " + l + "\n" for l in target.splitlines())
            prefix = sc.chat_prefix(user, f"```diff\n--- a/{path}\n+++ b/{path}\n@@ ... @@\n")
            s = sc.score(prefix, dtarget, masks=edit_masks)
            arrs["lp_" + fr] = s.logp
            arrs["offsets_" + fr] = s.offsets
            for k, v in s.extra.items():
                arrs[f"{k}_{fr}"] = v
        else:
            prefix = sc.chat_prefix(user, "```python\n")
            s = sc.score(prefix, target)
            arrs["lp_" + fr] = s.logp
            offsets = s.offsets
        secs[fr] = round(s.seconds, 2)
    return arrs, secs, offsets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--instances", required=True)
    ap.add_argument("--files", default="gold")
    ap.add_argument("--frames", default="U,B,F")
    ap.add_argument("--cands", default=None, help="json {iid: [paths]} for --files cands")
    ap.add_argument("--dataset", default=None)
    ap.add_argument("--max-file-tokens", type=int, default=MAX_FILE_TOKENS)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--sleep", type=float, default=0.3, help="pause between files (keeps the machine responsive)")
    args = ap.parse_args()

    insts = load_instances(Path(args.dataset) if args.dataset else None)
    by_id = {i["instance_id"]: i for i in insts}
    ids = [l.strip() for l in open(args.instances) if l.strip()][: args.limit]
    frames = args.frames.split(",")
    cands = json.load(open(args.cands)) if args.cands else {}
    outdir = RESULTS / f"conflict_{args.tag}"
    outdir.mkdir(parents=True, exist_ok=True)
    sc = Scorer(args.model)
    edit_masks = {"minus": sc.vocab_ids_startswith("-"), "plus": sc.vocab_ids_startswith("+")}
    rng = random.Random(0)
    log = open(outdir / "log.jsonl", "a")

    for n, iid in enumerate(ids):
        inst = by_id[iid]
        repo, commit = inst["repo"], inst["base_commit"]
        gold = gold_edits(inst["patch"])
        if args.files == "gold":
            paths = [p for p in gold if p.endswith(".py") and not is_test_path(p)]
        else:
            paths = cands.get(iid, [])
        issue = trunc_issue(inst["problem_statement"])
        # control issue: another instance of the same repo (deterministic)
        # wrong-issue control: same repo, disjoint gold files, closest issue length; per-instance seed
        gset = set(gold)
        others = [i for i in insts if i["repo"] == repo and i["instance_id"] != iid
                  and not (set(gold_edits(i["patch"])) & gset)]
        if not others:
            others = [i for i in insts if i["instance_id"] != iid and not (set(gold_edits(i["patch"])) & gset)]
        r_i = random.Random(iid)
        pool = sorted(others, key=lambda i: abs(len(i["problem_statement"]) - len(inst["problem_statement"])))[:8]
        other = r_i.choice(pool) if pool else None
        for path in paths:
            out = outdir / (key(iid, path) + ".npz")
            if out.exists():
                continue
            try:
                src = file_at(repo, commit, path)
            except Exception as e:
                log.write(json.dumps({"iid": iid, "path": path, "skip": "fetch", "err": repr(e)[:100]}) + "\n")
                continue
            target = src if src.endswith("\n") else src + "\n"
            n_tok = len(sc.encode(target))
            if n_tok > args.max_file_tokens or n_tok < 5:
                log.write(json.dumps({"iid": iid, "path": path, "skip": "size", "n_tok": n_tok}) + "\n")
                continue
            arrs, secs = {}, {}
            offsets = None
            try:
                arrs, secs, offsets = score_frames(sc, frames, issue, other, path, repo, target, edit_masks)
            except Exception as e:  # out of memory on a long file: skip it, keep the run alive
                if "out of memory" not in str(e).lower():
                    raise
                del e
                import gc, torch
                gc.collect(); torch.cuda.empty_cache()
                log.write(json.dumps({"iid": iid, "path": path, "skip": "oom", "n_tok": n_tok}) + "\n")
                log.flush()
                print(n, iid, path, n_tok, "SKIP out of memory", flush=True)
                continue
            if offsets is None:
                offsets = np.zeros((0, 2), dtype=np.int64)
            np.savez_compressed(out, offsets=offsets, **arrs)
            rec = {"iid": iid, "path": path, "n_tok": n_tok, "secs": secs, "gold": path in gold,
                   "x_issue": other["instance_id"] if other else None}
            log.write(json.dumps(rec) + "\n")
            log.flush()
            print(n, iid, path, n_tok, secs, flush=True)
            time.sleep(args.sleep)


if __name__ == "__main__":
    main()
