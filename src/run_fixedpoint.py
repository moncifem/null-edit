"""Experiment E2: fixed-point patch verification without running tests.

Idea: a patch that resolves the issue should leave the model with little remaining desire to edit.
For each candidate patch we apply it, then run null-edit teacher forcing on the PATCHED file
(prompt = issue + patched file + "rewrite so that the issue is fixed"; forced answer = patched file)
and record the residual hazard. Candidates are public SWE-bench Verified leaderboard patches with
their official resolved/unresolved labels (data/patches/*.jsonl).

Selection (label-blind except for balancing, seeded per instance):
  * instance's gold patch touches exactly one non-test .py file F, and F has <= --max-file-tokens;
  * candidate's source-file changes touch only F and apply cleanly;
  * distinct patched contents only; contents with conflicting labels across submissions dropped;
  * up to K resolved + K unresolved candidates.
The gold patch is scored too but reported separately (never used as a candidate).

Output: results/fixedpoint_<tag>/scores.jsonl
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import random
import subprocess
import tempfile
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from unidiff import PatchSet

from common import DATA, RESULTS, file_at, gold_edits, is_test_path, load_instances
from run_conflict import PROMPTS, trunc_issue
from scorer import Scorer, line_scores


def source_part(patch: str) -> tuple[str, list[str]] | None:
    """Keep only hunks for existing non-test .py files; return (diff text, paths)."""
    try:
        ps = PatchSet(patch)
    except Exception:
        return None
    parts, paths = [], []
    for pf in ps:
        if pf.is_added_file or pf.is_removed_file or pf.is_rename:
            if not is_test_path(pf.path) and pf.path.endswith(".py"):
                return None  # creates/removes source files: out of scope for single-file scoring
            continue
        if not pf.path.endswith(".py") or is_test_path(pf.path):
            continue
        parts.append(str(pf))
        paths.append(pf.path)
    if not parts:
        return None
    return "".join(parts), paths


def apply_patch(src: str, path: str, diff: str) -> str | None:
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(src, encoding="utf-8")
        (Path(td) / "p.diff").write_text(diff, encoding="utf-8")
        r = subprocess.run(["patch", "-p1", "--no-backup-if-mismatch", "-s", "-f", "-i", "p.diff"], cwd=td,
                           capture_output=True)
        if r.returncode != 0:
            return None
        return f.read_text(encoding="utf-8")


def changed_line_set(old: str, new: str) -> set[int]:
    """1-based line numbers in `new` that are added/changed relative to `old` (plus deletion anchors)."""
    import difflib

    a, b = old.splitlines(), new.splitlines()
    out = set()
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag in ("replace", "insert"):
            out.update(range(j1 + 1, j2 + 1))
        elif tag == "delete":
            out.update({max(j1, 1), min(j1 + 1, len(b))})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--instances", required=True)
    ap.add_argument("--limit", type=int, default=None, help="number of ELIGIBLE instances to score")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--max-file-tokens", type=int, default=5000)
    ap.add_argument("--frames", default="R,RX")
    args = ap.parse_args()
    insts = {i["instance_id"]: i for i in load_instances()}
    all_insts = list(insts.values())
    ids = [l.strip() for l in open(args.instances) if l.strip()]
    want = set(ids)
    raw = defaultdict(list)
    for fp in sorted(glob.glob(str(DATA / "patches/*.jsonl"))):
        sub = Path(fp).stem
        rows = [json.loads(l) for l in open(fp)]
        if sum(r["resolved"] for r in rows) == 0:
            continue  # label file unusable
        for r in rows:
            if r["instance_id"] in want and r["patch"]:
                raw[r["instance_id"]].append((sub, r["patch"], bool(r["resolved"])))
    outdir = RESULTS / f"fixedpoint_{args.tag}"
    outdir.mkdir(parents=True, exist_ok=True)
    done = {json.loads(l)["iid"] for l in open(outdir / "scores.jsonl")} if (outdir / "scores.jsonl").exists() else set()
    sc = Scorer(args.model)
    fout = open(outdir / "scores.jsonl", "a")
    frames = args.frames.split(",")
    n_done = len(done)
    for iid in ids:
        if args.limit and n_done >= args.limit:
            break
        if iid in done:
            continue
        inst = insts[iid]
        gold = gold_edits(inst["patch"])
        gpaths = [p for p in gold if p.endswith(".py") and not is_test_path(p)]
        if len(gold) != 1 or len(gpaths) != 1:
            continue
        path = gpaths[0]
        src = file_at(inst["repo"], inst["base_commit"], path)
        if not src.endswith("\n"):
            src += "\n"
        if len(sc.encode(src)) > args.max_file_tokens:
            continue
        # candidates
        pool = {}
        for sub, patch, lab in raw.get(iid, []):
            sp = source_part(patch)
            if sp is None or sp[1] != [path]:
                continue
            new = apply_patch(src, path, sp[0])
            if new is None or new == src:
                continue
            if not new.endswith("\n"):
                new += "\n"
            h = hashlib.md5(new.encode()).hexdigest()[:12]
            rec = pool.setdefault(h, {"new": new, "subs": [], "labels": []})
            rec["subs"].append(sub)
            rec["labels"].append(lab)
        gold_new = apply_patch(src, path, source_part(inst["patch"])[0])
        if gold_new is None:
            continue
        gold_h = hashlib.md5((gold_new if gold_new.endswith("\n") else gold_new + "\n").encode()).hexdigest()[:12]
        items = [(h, r) for h, r in pool.items() if len(set(r["labels"])) == 1]
        pos = sorted([x for x in items if x[1]["labels"][0]], key=lambda x: x[0])
        neg = sorted([x for x in items if not x[1]["labels"][0]], key=lambda x: x[0])
        if not pos or not neg:
            continue
        rng = random.Random(iid)
        rng.shuffle(pos)
        rng.shuffle(neg)
        chosen = pos[: args.k] + neg[: args.k]
        # wrong issue: same repo, disjoint gold files, similar length (same rule as run_conflict.py)
        gset = set(gold)
        others = [i for i in all_insts if i["repo"] == inst["repo"] and i["instance_id"] != iid
                  and not (set(gold_edits(i["patch"])) & gset)]
        pool_x = sorted(others, key=lambda i: abs(len(i["problem_statement"]) - len(inst["problem_statement"])))[:8]
        other = random.Random(iid).choice(pool_x) if pool_x else None
        t0 = time.time()
        res = {"iid": iid, "path": path, "n_pos_pool": len(pos), "n_neg_pool": len(neg), "cands": []}
        targets = [("orig", src, None, [], False), ("gold", gold_new if gold_new.endswith("\n") else gold_new + "\n", None, [], True)]
        targets += [(h, r["new"], r["labels"][0], r["subs"], h == gold_h) for h, r in chosen]
        for h, text, lab, subs, is_gold in targets:
            rec = {"h": h, "resolved": lab, "n_subs": len(subs), "equals_gold": is_gold, "n_tok": 0}
            lps = {}
            for fr in frames:
                if fr == "RX" and other is None:
                    continue
                iss = trunc_issue(inst["problem_statement"] if fr != "RX" else other["problem_statement"])
                user = PROMPTS[fr].format(path=path, repo=inst["repo"], issue=iss, file=text)
                s = sc.score(sc.chat_prefix(user, "```python\n"), text)
                lps[fr] = s
            sR = lps["R"]
            rec["n_tok"] = int(len(sR.logp))
            rec["S_total"] = float(-sR.logp.sum())
            rec["S_max_tok"] = float(-sR.logp.min())
            buckets = line_scores(text, sR)
            S_line = np.array([-sR.logp[b].sum() if b else 0.0 for b in buckets])
            rec["S_line_max"] = float(S_line.max())
            rec["S_top5"] = float(np.sort(S_line)[-5:].sum())
            chg = changed_line_set(src, text) if h != "orig" else set()
            rec["n_changed_lines"] = len(chg)
            idx = [l - 1 for l in chg if 1 <= l <= len(S_line)]
            rec["S_changed"] = float(S_line[idx].sum()) if idx else 0.0
            rec["S_unchanged"] = rec["S_total"] - rec["S_changed"]
            if "RX" in lps:
                d = lps["RX"].logp - sR.logp
                rec["H_total"] = float(np.maximum(d, 0).sum())
                rec["SX_total"] = float(-lps["RX"].logp.sum())
                H_line = np.array([np.maximum(d[b], 0).sum() if b else 0.0 for b in buckets])
                rec["H_line_max"] = float(H_line.max())
                rec["H_changed"] = float(H_line[idx].sum()) if idx else 0.0
            import difflib
            rec["sim_gold"] = float(difflib.SequenceMatcher(None, text, targets[1][1], autojunk=False).quick_ratio())
            res["cands"].append(rec)
        res["secs"] = round(time.time() - t0, 1)
        fout.write(json.dumps(res) + "\n")
        fout.flush()
        n_done += 1
        print(n_done, iid, path, len(targets), "targets", res["secs"], "s", flush=True)


if __name__ == "__main__":
    main()
