"""Does the model, left to itself, open its rewrite the way the probe assumes?

The probe prefills the answer with "```python\n" and teacher-forces the file. Here the same fix-it prompt
is answered freely (greedy, no prefill) for a short opening, on a given list of files, to check that the
free reply starts with a fenced copy of the file rather than prose or a diff.

Output: results/noprefill_<tag>/gen.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import time

from common import RESULTS, file_at, load_instances
from run_conflict import PROMPTS, trunc_issue
from scorer import Scorer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--files", required=True, help="json list of [iid, path]")
    ap.add_argument("--max-tokens", type=int, default=40)
    args = ap.parse_args()
    insts = {i["instance_id"]: i for i in load_instances()}
    outdir = RESULTS / f"noprefill_{args.tag}"
    outdir.mkdir(parents=True, exist_ok=True)
    done = set()
    if (outdir / "gen.jsonl").exists():
        done = {(r["iid"], r["path"]) for r in map(json.loads, open(outdir / "gen.jsonl"))}
    sc = Scorer(args.model)
    out = open(outdir / "gen.jsonl", "a")
    throttle = float(os.environ.get("THROTTLE", "0"))
    for iid, path in json.load(open(args.files)):
        if (iid, path) in done:
            continue
        t0 = time.time()
        inst = insts[iid]
        src = file_at(inst["repo"], inst["base_commit"], path)
        target = src if src.endswith("\n") else src + "\n"
        user = PROMPTS["R"].format(path=path, repo=inst["repo"], issue=trunc_issue(inst["problem_statement"]), file=target)
        g = sc.generate(sc.encode(sc.chat_prefix(user)), args.max_tokens, temp=0.0)
        fence = "```python\n"
        body = g["text"][len(fence):] if g["text"].startswith(fence) else None
        rec = {"iid": iid, "path": path, "response": g["text"], "starts_with_fence": body is not None,
               "copies_file_opening": bool(body is not None and len(body) >= 20 and target.startswith(body[: max(20, len(body) - 12)]))}
        out.write(json.dumps(rec) + "\n")
        out.flush()
        print(iid, path, rec["starts_with_fence"], rec["copies_file_opening"], flush=True)
        if throttle:
            time.sleep(throttle * (time.time() - t0))


if __name__ == "__main__":
    main()
