"""Exploratory (post hoc): does the map of the larger models recover in long files if lines that are comments or
docstrings are not ranked?  CPU only, saved DGX scores. Gold lines that are themselves comment/docstring lines stay
in the gold set (the file then counts as a miss unless another gold line is ranked), so the restriction cannot help
by construction.
Usage: NULLEDIT_RESULTS=../results_dgx python explore_codeonly.py
"""
import io, json, tokenize
import numpy as np
from analyze_conflict import fix_anchors, line_features
from common import RESULTS, file_at, gold_edits, load_instances
from run_conflict import key

insts = {i["instance_id"]: i for i in load_instances()}


def prose_lines(src: str) -> set[int]:
    """1-based lines that are comment-only or inside a string statement (docstring)."""
    out = set()
    try:
        prev = None
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT and not tok.line[: tok.start[1]].strip():
                out.add(tok.start[0])
            if tok.type == tokenize.STRING and (prev is None or prev in (tokenize.INDENT, tokenize.NEWLINE, tokenize.NL, tokenize.DEDENT)) \
                    and tok.line[: tok.start[1]].strip() == "":
                out.update(range(tok.start[0], tok.end[0] + 1))
            if tok.type not in (tokenize.COMMENT,):
                prev = tok.type
    except Exception:
        pass
    return out


tags = [("E2B", "e2b_test"), ("E4B", "e4b_test"), ("12B", "g12b_test"), ("26B-A4B", "g26b_test")]
logs = {n: {(r["iid"], r["path"]): r for r in map(json.loads, open(RESULTS / f"conflict_{t}" / "log.jsonl")) if "secs" in r} for n, t in tags}
ids = [l.strip() for l in open("../results/test_ids.txt")][:100]
common = sorted(k for k in set.intersection(*[set(v) for v in logs.values()]) if k[0] in ids)
bands = [("under 5,000", 0, 5000), ("5,000-11,000", 5000, 11000), ("over 11,000", 11000, 10**9)]
res = {n: {b[0]: [] for b in bands} for n, _ in tags}
share = {n: [] for n, _ in tags}
for iid, path in common:
    inst = insts[iid]
    src = file_at(inst["repo"], inst["base_commit"], path)
    prose = prose_lines(src)
    for n, t in tags:
        z = np.load(RESULTS / f"conflict_{t}" / (key(iid, path) + ".npz"))
        f = line_features(src, z)
        valid = f["ntok"] > 0
        gold = fix_anchors(gold_edits(inst["patch"])[path], valid, len(valid), "all")
        if not gold:
            continue
        S = f["surp_R_sum"]
        code = np.array([valid[i] and (i + 1) not in prose for i in range(len(valid))])
        r_all = list(np.argsort(-np.where(valid, S, -1e9), kind="stable") + 1)
        r_code = list(np.argsort(-np.where(code, S, -1e9), kind="stable")[: int(code.sum())] + 1)
        hit_all = bool(set(r_all[:10]) & gold)
        hit_code = bool(set(r_code[:10]) & gold)
        ntok = logs[n][(iid, path)]["n_tok"]
        b = next(b[0] for b in bands if b[1] <= ntok < b[2])
        res[n][b].append((hit_all, hit_code, iid))
        tot = S[valid].sum()
        share[n].append((b, S[[i for i in range(len(valid)) if valid[i] and (i + 1) in prose]].sum() / tot if tot > 0 else np.nan,
                         np.mean([(i + 1) in prose for i in range(len(valid)) if valid[i]])))
print("S line@10: all lines -> code lines only (comment and docstring lines not ranked)\n")
print("| Model | " + " | ".join(f"{b[0]} tokens" for b in bands) + " | all files |\n|---|---|---|---|---|")
for n, _ in tags:
    cells = []
    allr = []
    for b in bands:
        r = res[n][b[0]]; allr += r
        cells.append(f"{100*np.mean([x[0] for x in r]):.0f} -> {100*np.mean([x[1] for x in r]):.0f} (n={len(r)})")
    cells.append(f"{100*np.mean([x[0] for x in allr]):.0f} -> {100*np.mean([x[1] for x in allr]):.0f}")
    print(f"| {n} | " + " | ".join(cells) + " |")
print("\nShare of the file's total hazard that sits on comment/docstring lines (median over files), and share of such lines:\n")
for n, _ in tags:
    print(n, {b[0]: (round(float(np.nanmedian([s for bb, s, _ in share[n] if bb == b[0]])), 2), round(float(np.median([q for bb, _, q in share[n] if bb == b[0]])), 2)) for b in bands})
