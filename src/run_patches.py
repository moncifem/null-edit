"""Experiment E2: does the issue make a candidate patch more likely? (execution-free patch scoring)

Candidates: public SWE-bench Verified leaderboard patches (data/patches/*.jsonl) with their
official resolved/unresolved labels, deduplicated per instance, plus the gold patch (kept separate).

For each instance the context is the pre-fix source of every unit (function / gap) touched by ANY
candidate (so the context does not reveal which candidate is right). Each candidate is rendered as
a normalized diff (source files only, test files dropped) and its tokens are scored under
  C  context only                (no issue)
  I  issue + context
  X  another issue + context     (control)
Score = sum_t [log P_I - log P_C] over diff tokens ("issue information", nats).

Output: results/patches_<tag>/scores.jsonl
"""
from __future__ import annotations

import argparse
import copy
import glob
import hashlib
import json
import random
import time
from collections import defaultdict
from pathlib import Path

import mlx.core as mx
import numpy as np
from mlx_lm.models.cache import make_prompt_cache
from unidiff import PatchSet

from analyze_conflict import units_with_module
from common import DATA, RESULTS, file_at, is_test_path, load_instances
from run_conflict import trunc_issue
from scorer import Scorer

MAX_CTX_LINES = 400


def normalize_patch(patch: str) -> tuple[str, dict[str, set[int]]] | None:
    """Drop test/non-python/new files; return canonical diff text and touched source lines."""
    try:
        ps = PatchSet(patch)
    except Exception:
        return None
    parts, touched = [], {}
    for pf in ps:
        if pf.is_added_file or pf.is_removed_file or not pf.path.endswith(".py") or is_test_path(pf.path):
            continue
        lines = set()
        body = [f"--- a/{pf.path}\n+++ b/{pf.path}\n"]
        for h in pf:
            body.append(f"@@ -{h.source_start},{h.source_length} +{h.target_start},{h.target_length} @@\n")
            for ln in h:
                body.append(str(ln) if str(ln).endswith("\n") else str(ln) + "\n")
                if ln.is_removed:
                    lines.add(ln.source_line_no)
            lines.update(range(h.source_start, h.source_start + max(h.source_length, 1)))
        parts.append("".join(body))
        touched[pf.path] = lines
    if not parts:
        return None
    return "".join(parts), touched


def changed_only(diff: str) -> str:
    return "".join(l for l in diff.splitlines(keepends=True) if l[:1] in "+-" and not l.startswith(("+++", "---")))


def score_with_cache(sc: Scorer, cache, last_logits_ids: list[int], target: str):
    """Score `target` continuing from a prefilled cache. `last_logits_ids` = final prefix token (re-fed)."""
    t_ids, offs = sc.encode(target, offsets=True)
    c = copy.deepcopy(cache)
    x = mx.array(last_logits_ids + t_ids[:-1])[None]
    logits = sc.model(x, cache=c)[0].astype(mx.float32)
    lp = logits - mx.logsumexp(logits, axis=-1, keepdims=True)
    sel = mx.take_along_axis(lp, mx.array(t_ids)[:, None], axis=-1)[:, 0]
    mx.eval(sel)
    return np.array(sel), offs


def prefill(sc: Scorer, prefix: str):
    ids = sc.encode(prefix)
    cache = make_prompt_cache(sc.model)
    body = ids[:-1]
    for i in range(0, len(body), 2048):
        out = sc.model(mx.array(body[i : i + 2048])[None], cache=cache)
        mx.eval(out[0, -1, :1])
    return cache, [ids[-1]], len(ids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--instances", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--max-cands", type=int, default=12)
    args = ap.parse_args()
    insts = {i["instance_id"]: i for i in load_instances()}
    all_insts = list(insts.values())
    ids = [l.strip() for l in open(args.instances) if l.strip()][: args.limit]
    want = set(ids)
    # load candidates
    cands = defaultdict(dict)  # iid -> diff_hash -> record
    for fp in sorted(glob.glob(str(DATA / "patches/*.jsonl"))):
        sub = Path(fp).stem
        for l in open(fp):
            r = json.loads(l)
            if r["instance_id"] not in want or not r["patch"]:
                continue
            norm = normalize_patch(r["patch"])
            if norm is None:
                continue
            diff, touched = norm
            h = hashlib.md5(changed_only(diff).encode()).hexdigest()[:12]
            rec = cands[r["instance_id"]].setdefault(h, {"diff": diff, "touched": touched, "subs": [], "labels": []})
            rec["subs"].append(sub)
            rec["labels"].append(bool(r["resolved"]))
    outdir = RESULTS / f"patches_{args.tag}"
    outdir.mkdir(parents=True, exist_ok=True)
    done = {json.loads(l)["iid"] for l in open(outdir / "scores.jsonl")} if (outdir / "scores.jsonl").exists() else set()
    sc = Scorer(args.model)
    rng = random.Random(0)
    fout = open(outdir / "scores.jsonl", "a")
    for n, iid in enumerate(ids):
        if iid in done:
            continue
        inst = insts[iid]
        pool = cands.get(iid, {})
        # label consistency: drop diffs with conflicting labels across submissions
        items = [(h, r) for h, r in pool.items() if len(set(r["labels"])) == 1]
        pos = [x for x in items if x[1]["labels"][0]]
        neg = [x for x in items if not x[1]["labels"][0]]
        if len(pos) < 1 or len(neg) < 1:
            continue
        rng.shuffle(pos)
        rng.shuffle(neg)
        k = args.max_cands // 2
        chosen = pos[:k] + neg[:k]
        gold = normalize_patch(inst["patch"])
        if gold is None:
            continue
        # shared context: union of units touched by any chosen candidate or gold
        touched = defaultdict(set)
        for _, r in chosen:
            for p, ls in r["touched"].items():
                touched[p] |= ls
        for p, ls in gold[1].items():
            touched[p] |= ls
        ctx_parts, n_ctx_lines = [], 0
        for p in sorted(touched):
            try:
                src = file_at(inst["repo"], inst["base_commit"], p)
            except Exception:
                continue
            lines = src.splitlines()
            units = units_with_module(src)
            keep = [u for u in units if any(u.start <= l <= u.end for l in touched[p])]
            for u in keep:
                seg = lines[u.start - 1 : u.end]
                if len(seg) > 150:  # very long unit: keep only +-40 lines around touched lines
                    idx = sorted({j for l in touched[p] if u.start <= l <= u.end
                                  for j in range(max(u.start, l - 40), min(u.end, l + 40) + 1)})
                    seg = [lines[j - 1] for j in idx]
                n_ctx_lines += len(seg)
                ctx_parts.append(f"# {p} (lines {u.start}-{u.end})\n" + "\n".join(seg) + "\n")
        if not ctx_parts or n_ctx_lines > MAX_CTX_LINES * 3:
            continue
        ctx = "\n".join(ctx_parts)
        others = [i for i in all_insts if i["repo"] == inst["repo"] and i["instance_id"] != iid]
        other = rng.choice(others) if others else None
        tail = ("Relevant source code from the repository {repo}:\n\n```python\n{ctx}```\n\n"
                "Write a patch in unified diff format.")
        frames = {
            "C": tail,
            "I": "The following GitHub issue was filed against the repository {repo}:\n\n<issue>\n{issue}\n</issue>\n\n"
                 + tail.replace("Write a patch in unified diff format.", "Write a patch in unified diff format that fixes the issue."),
        }
        frames["X"] = frames["I"]
        t0 = time.time()
        res = {"iid": iid, "n_ctx_lines": n_ctx_lines, "cands": []}
        targets = [("gold", gold[0], None, None)] + [(h, r["diff"], r["labels"][0], r["subs"]) for h, r in chosen]
        scores = defaultdict(dict)
        for fr, tmpl in frames.items():
            if fr == "X" and other is None:
                continue
            issue = trunc_issue(inst["problem_statement"] if fr != "X" else other["problem_statement"])
            prefix = sc.chat_prefix(tmpl.format(repo=inst["repo"], issue=issue, ctx=ctx), "```diff\n")
            cache, last, n_pre = prefill(sc, prefix)
            for h, diff, lab, subs in targets:
                lp, offs = score_with_cache(sc, cache, last, diff)
                # split into changed-line tokens vs all tokens
                starts = [0]
                for i, ch in enumerate(diff):
                    if ch == "\n":
                        starts.append(i + 1)
                starts = np.array(starts)
                dl = diff.splitlines()
                chg = np.zeros(len(lp), bool)
                for ti, (a, b) in enumerate(offs):
                    li = int(np.searchsorted(starts, a, side="right") - 1)
                    if li < len(dl) and dl[li][:1] in "+-" and not dl[li].startswith(("+++", "---")):
                        chg[ti] = True
                scores[h][fr] = {"sum": float(lp.sum()), "n": int(len(lp)), "sum_chg": float(lp[chg].sum()), "n_chg": int(chg.sum())}
            del cache
            mx.clear_cache()
        for h, diff, lab, subs in targets:
            res["cands"].append({"h": h, "resolved": lab, "n_subs": len(subs) if subs else 0, "subs": subs,
                                 "diff": diff, **{f"{fr}_{k}": v for fr, d in scores[h].items() for k, v in d.items()}})
        res["secs"] = round(time.time() - t0, 1)
        fout.write(json.dumps(res) + "\n")
        fout.flush()
        print(n, iid, len(targets), "cands", n_ctx_lines, "ctx lines", res["secs"], "s", flush=True)


if __name__ == "__main__":
    main()
