"""Baseline G: the SAME model localizes by GENERATING an answer (greedy), given the same
issue and the same file (with line numbers) that the scoring method sees.

Output: results/gen_<tag>/gen.jsonl with the raw response, parsed ranked line ranges, timing.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path

from common import RESULTS, file_at, gold_edits, is_test_path, load_instances
from run_conflict import MAX_FILE_TOKENS, trunc_issue
from scorer import Scorer

PROMPT = (
    "The following GitHub issue was filed against the repository {repo}:\n\n<issue>\n{issue}\n</issue>\n\n"
    "Below is the current content of `{path}`, with line numbers.\n\n```python\n{numbered}```\n\n"
    "Which locations in this file must be edited to fix the issue? "
    "Answer with up to 5 locations, most likely first, one per line, in exactly this format:\n"
    "<start_line>-<end_line>: <function or class name>\n"
    "Each range should be as narrow as possible (the specific lines to change). Output only the list."
)

PROMPT_QUOTE = (
    "The following GitHub issue was filed against the repository {repo}:\n\n<issue>\n{issue}\n</issue>\n\n"
    "Below is the current content of `{path}`.\n\n```python\n{file}```\n\n"
    "Which lines of this file must be changed to fix the issue? Quote up to 5 existing lines, most likely first, "
    "each on its own line, copied exactly from the file (one physical line each, no line numbers, no explanations). "
    "If code must be inserted, quote the existing line right before the insertion point. Output only the quoted lines."
)


def match_quotes(resp: str, file_lines: list[str]) -> list[tuple[int, int]]:
    """Map quoted lines back to 1-based line numbers (whitespace-insensitive exact match; all occurrences)."""
    norm = {}
    for i, l in enumerate(file_lines, 1):
        k = " ".join(l.split())
        if k:
            norm.setdefault(k, []).append(i)
    out = []
    for q in resp.splitlines():
        q = q.strip().strip("`")
        q = re.sub(r"^\d+\s*[|:]\s?", "", q)
        k = " ".join(q.split())
        if not k or k.startswith("```"):
            continue
        for i in norm.get(k, []):
            if (i, i) not in out:
                out.append((i, i))
    return out


RANGE = re.compile(r"(?<![\w.])(\d+)\s*(?:-|–|—|to|\.\.)\s*(\d+)(?!\w)")
SINGLE = re.compile(r"(?:^|[Ll]ines?\s+)\W*(\d+)\s*[:|]")
ENUM = re.compile(r"^\s*(?:\d+[.)]|[-*•])\s+")


def parse(resp: str) -> list[tuple[int, int]]:
    """Lenient parser: accepts '120-130: f', '1. 120-130', 'Lines 120 to 130', '- 120: f', etc."""
    out = []
    for line in resp.splitlines():
        line = ENUM.sub("", line.strip().strip("`*"))
        m = RANGE.search(line)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            out.append((min(a, b), max(a, b)))
            continue
        m = SINGLE.search(line) or re.match(r"^(\d+)\b", line)
        if m:
            out.append((int(m.group(1)), int(m.group(1))))
    return out[:5]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--instances", required=True)
    ap.add_argument("--dataset", default=None)
    ap.add_argument("--max-tokens", type=int, default=160)
    ap.add_argument("--mode", default="range", choices=["range", "quote"])
    ap.add_argument("--max-file-tokens", type=int, default=MAX_FILE_TOKENS)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--sleep", type=float, default=0.3, help="pause between files (keeps the machine responsive)")
    args = ap.parse_args()
    insts = {i["instance_id"]: i for i in load_instances(Path(args.dataset) if args.dataset else None)}
    ids = [l.strip() for l in open(args.instances) if l.strip()][: args.limit]
    outdir = RESULTS / f"gen_{args.tag}"
    outdir.mkdir(parents=True, exist_ok=True)
    done = set()
    if (outdir / "gen.jsonl").exists():
        done = {(json.loads(l)["iid"], json.loads(l)["path"]) for l in open(outdir / "gen.jsonl")}
    sc = Scorer(args.model)
    f = open(outdir / "gen.jsonl", "a")
    for n, iid in enumerate(ids):
        inst = insts[iid]
        gold = gold_edits(inst["patch"])
        for path in [p for p in gold if p.endswith(".py") and not is_test_path(p)]:
            if (iid, path) in done:
                continue
            try:
                src = file_at(inst["repo"], inst["base_commit"], path)
            except Exception:
                continue
            target = src if src.endswith("\n") else src + "\n"
            if len(sc.encode(target)) > args.max_file_tokens:
                continue
            numbered = "".join(f"{i}| {l}\n" for i, l in enumerate(target.splitlines(), 1))
            if args.mode == "quote":
                user = PROMPT_QUOTE.format(repo=inst["repo"], issue=trunc_issue(inst["problem_statement"]), path=path,
                                           file=target)
            else:
                user = PROMPT.format(repo=inst["repo"], issue=trunc_issue(inst["problem_statement"]), path=path,
                                     numbered=numbered)
            ids_ = sc.encode(sc.chat_prefix(user))
            g = sc.generate(ids_, args.max_tokens, temp=0.0)
            text = g["text"]
            ranges = match_quotes(text, target.splitlines()) if args.mode == "quote" else parse(text)
            rec = {"iid": iid, "path": path, "response": text, "ranges": ranges, "mode": args.mode,
                   "secs": round(g["secs"], 2), "prompt_tokens": g["prompt_tokens"], "gen_tokens": g["gen_tokens"],
                   "prompt_tps": g["prompt_tps"], "gen_tps": g["gen_tps"]}
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print(n, iid, path, rec["ranges"], rec["secs"], flush=True)
            time.sleep(args.sleep + rec["secs"] * float(os.environ.get("THROTTLE", "0")))


if __name__ == "__main__":
    main()
