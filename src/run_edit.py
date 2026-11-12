"""Let the model write the fix — with and without the null-edit map as a hint.

For every gold file the same model reads the issue and the file and writes ONE search/replace edit
(greedy). Three arms, same files, same wording otherwise:
  none   no hint (this is also the "let it write" localization baseline: where does it edit?)
  H      the five highest null-edit-hazard lines of the file are listed as a hint
  WRONG  the five highest-hazard lines under a wrong issue, same format (placebo hint)
  GOLD   lines the human fix edits, padded to five, same format (ceiling)
The hint quotes the lines' text without line numbers, since the file in the prompt is not numbered.
Hints come from `make_hints.py` (computed from saved scores; no generation involved).
Nothing is executed; `analyze_edit.py` scores where the edit lands and how it compares to the gold patch.

Output: results/edit_<tag>/gen.jsonl  (one record per file and arm)
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from common import RESULTS, file_at, gold_edits, is_test_path, load_instances
from run_conflict import MAX_FILE_TOKENS, key, trunc_issue
from scorer import Scorer

THROTTLE = float(os.environ.get("THROTTLE", "0"))

HEAD = ("The following GitHub issue was filed against the repository {repo}:\n\n<issue>\n{issue}\n</issue>\n\n"
        "Here is the current content of `{path}`:\n\n```python\n{file}```\n\n")
HINT = ("A diagnostic probe marked these lines of the file as the most likely to need a change "
        "(the probe can be wrong):\n{lines}\n\n")
TAIL = ("Fix the issue with one edit to `{path}`. Reply with exactly one block in this format and nothing else:\n\n"
        "<<<<<<< SEARCH\n(a few consecutive lines copied exactly from the file)\n=======\n(the lines that replace them)\n>>>>>>> REPLACE")
END = ">>>>>>> REPLACE"
START = "<<<<<<< SEARCH\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--instances", required=True)
    ap.add_argument("--hints", required=True)
    ap.add_argument("--arms", default="none,H,WRONG,GOLD")
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--max-file-tokens", type=int, default=MAX_FILE_TOKENS)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    insts = {i["instance_id"]: i for i in load_instances()}
    ids = [l.strip() for l in open(args.instances) if l.strip()][: args.limit]
    hints = json.load(open(args.hints))
    arms = args.arms.split(",")
    outdir = RESULTS / f"edit_{args.tag}"
    outdir.mkdir(parents=True, exist_ok=True)
    done = set()
    if (outdir / "gen.jsonl").exists():
        done = {(r["iid"], r["path"], r["arm"]) for r in map(json.loads, open(outdir / "gen.jsonl"))}
    sc = Scorer(args.model)
    out = open(outdir / "gen.jsonl", "a")

    def stop(toks):
        return len(toks) % 6 == 0 and END in sc.hf.decode(toks[-48:], skip_special_tokens=True)

    for n, iid in enumerate(ids):
        inst = insts[iid]
        for path in [p for p in gold_edits(inst["patch"]) if p.endswith(".py") and not is_test_path(p)]:
            h = hints.get(key(iid, path))
            if h is None:
                continue
            try:
                src = file_at(inst["repo"], inst["base_commit"], path)
            except Exception:
                continue
            target = src if src.endswith("\n") else src + "\n"
            if len(sc.encode(target)) > args.max_file_tokens:
                continue
            head = HEAD.format(repo=inst["repo"], issue=trunc_issue(inst["problem_statement"]), path=path, file=target)
            for arm in arms:
                if (iid, path, arm) in done:
                    continue
                mid = "" if arm == "none" else HINT.format(lines="\n".join(f"- {t}" for _, t in h[arm]))
                t0 = time.time()
                # the answer is prefilled with the opening marker in every arm, so all arms answer in the same format
                g = sc.generate(sc.encode(sc.chat_prefix(head + mid + TAIL.format(path=path), START)), args.max_tokens, temp=0.0, stop_fn=stop)
                rec = {"iid": iid, "path": path, "arm": arm, "response": START + g["text"], "gen_tokens": g["gen_tokens"],
                       "prompt_tokens": g["prompt_tokens"], "secs": round(time.time() - t0, 2), "truncated": END not in g["text"]}
                out.write(json.dumps(rec) + "\n")
                out.flush()
                print(n, iid, path, arm, g["gen_tokens"], rec["secs"], flush=True)
                if THROTTLE:  # duty-cycle the GPU on a shared laptop: sleep THROTTLE x compute time
                    time.sleep(THROTTLE * rec["secs"])


if __name__ == "__main__":
    main()
