"""Where does the model's own edit land, and does the null-edit map help it land on the fix?

Reads results/edit_<tag>/gen.jsonl (run_edit.py). Nothing is executed. Outcomes per file and arm:
  valid        the SEARCH block is found verbatim (whitespace-normalised, contiguous) EXACTLY ONCE in the file
  ambiguous    the SEARCH block occurs more than once (counted as not valid, as an apply tool would)
  truncated    the reply hit the token cap before the closing marker
  noop         SEARCH and REPLACE are identical
  on_gold      a line the edit changes (or an insertion anchor) is a gold-edited line     <- PRIMARY (pre-declared)
  near_gold    ... within +-3 lines of a gold-edited line
  gold_unit    the edit changes a line inside a gold function/unit
  adds_gold    the edit INTRODUCES a line that the human fix adds: the line is new in REPLACE (not copied from
               SEARCH), does not occur anywhere in the original file, and has >= 12 characters
  on_hint      a line the edit changes is one of the hinted lines (how far the model defers to the hint)
An invalid edit scores 0 on every outcome. Paired differences use the instance-clustered bootstrap of
report.py; p-values are Holm-adjusted over the secondary tests, the primary contrasts are reported unadjusted.

Usage: python analyze_edit.py --tag e4b_test [--conflict-tag e4b_test] [--hints ../results_dgx/hints_e4b_test.json]
"""
from __future__ import annotations

import argparse
import difflib
import json
from collections import defaultdict

import numpy as np
from unidiff import PatchSet

from analyze_conflict import fix_anchors, line_features, units_with_module
from common import RESULTS, file_at, gold_edits, load_instances
from report import boot
from run_conflict import key

ORDER = ["none", "H", "WRONG", "BM25", "GOLD"]
LAB = {"none": "no hint", "H": "hint: top-5 null-edit lines", "WRONG": "hint: top-5 wrong-issue lines (placebo)",
       "BM25": "hint: top-5 BM25 lines", "GOLD": "hint: gold lines (ceiling)"}
OUTS = ["valid", "ambiguous", "truncated", "noop", "on_gold", "near_gold", "gold_unit", "adds_gold", "on_hint"]


def norm(l: str) -> str:
    return " ".join(l.split())


def parse(resp: str):
    if "<<<<<<< SEARCH" not in resp or "=======" not in resp:
        return None
    body = resp.split("<<<<<<< SEARCH", 1)[1]
    search, rest = body.split("=======", 1)
    repl = rest.split(">>>>>>> REPLACE", 1)[0]
    return search.strip("\n").split("\n"), repl.strip("\n").split("\n")


def locate(search: list[str], lines: list[str]):
    """(start index or None, number of occurrences, trimmed search) of the contiguous block `search` in `lines`."""
    q = [norm(x) for x in search]
    while q and not q[0]:
        search, q = search[1:], q[1:]
    while q and not q[-1]:
        search, q = search[:-1], q[:-1]
    if not q:
        return None, 0, search
    L = [norm(x) for x in lines]
    hits = [i for i in range(len(L) - len(q) + 1) if L[i : i + len(q)] == q]
    return (hits[0] if hits else None), len(hits), search


def diff_edit(start: int, search: list[str], repl: list[str]):
    """(1-based original lines the edit modifies; an insertion marks its two neighbours,
        normalised lines that REPLACE introduces)."""
    changed, new = set(), set()
    a, b = [norm(x) for x in search], [norm(x) for x in repl]
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op in ("replace", "delete"):
            changed.update(range(start + i1 + 1, start + i2 + 1))
        elif op == "insert":
            changed.update({start + i1, start + i1 + 1})
        if op in ("replace", "insert"):
            new.update(b[j1:j2])
    return {l for l in changed if l >= 1}, new


def gold_added(patch: str, path: str) -> set[str]:
    out = set()
    for pf in PatchSet(patch):
        if pf.path == path:
            for h in pf:
                out.update(norm(l.value) for l in h if l.is_added)
    return out


def pval(bs):
    return min(1.0, 2 * min((bs <= 0).mean(), (bs >= 0).mean()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--conflict-tag", default=None, help="to report the map's own hit rates and the no-op subset")
    ap.add_argument("--hints", default=None, help="hints json used by run_edit.py (for on_hint and hint-quality splits)")
    ap.add_argument("--lenient-truncation", action="store_true",
                    help="score a reply that hit the token cap if its SEARCH block is complete (sensitivity analysis). "
                         "Default: such a reply is invalid, as declared in HYPOTHESES.md Revision 2c.")
    args = ap.parse_args()
    insts = {i["instance_id"]: i for i in load_instances()}
    recs = [json.loads(l) for l in open(RESULTS / f"edit_{args.tag}" / "gen.jsonl")]
    arms = sorted({r["arm"] for r in recs}, key=ORDER.index)
    hints = json.load(open(args.hints)) if args.hints else {}
    by = defaultdict(dict)
    for r in recs:
        by[(r["iid"], r["path"])][r["arm"]] = r
    rows = []
    for (iid, path), d in by.items():
        if set(d) != set(arms):
            continue
        inst = insts[iid]
        src = file_at(inst["repo"], inst["base_commit"], path)
        lines = src.splitlines()
        nl = len(lines)
        orig = {norm(l) for l in lines}
        valid_lines = np.array([bool(l.strip()) for l in lines])
        gold = fix_anchors(gold_edits(inst["patch"])[path], valid_lines, nl, "all")
        if not gold:
            continue
        units = units_with_module(src)
        gold_units = {i for i, u in enumerate(units) if any(u.start <= l <= u.end for l in gold)}
        added = {x for x in gold_added(inst["patch"], path) if len(x) >= 12 and x not in orig}
        h = hints.get(key(iid, path), {})
        row = {"iid": iid, "path": path}
        for arm in arms:
            o = dict.fromkeys(OUTS, 0.0)
            o["truncated"] = float(d[arm].get("truncated", ">>>>>>> REPLACE" not in d[arm]["response"]))
            hl = {l for l, _ in h.get(arm, [])}
            if hl:
                row[f"{arm}|hint_has_gold"] = float(bool(hl & gold))
            pr = parse(d[arm]["response"])
            if o["truncated"] and not args.lenient_truncation:
                pr = None
            if pr:
                start, nhits, search = locate(pr[0], lines)
                o["ambiguous"] = float(nhits > 1)
                if nhits == 1:
                    o["valid"] = 1.0
                    ch, new = diff_edit(start, search, pr[1])
                    o["noop"] = float(not ch)
                    o["on_gold"] = float(bool(ch & gold))
                    o["near_gold"] = float(any(abs(c - g) <= 3 for c in ch for g in gold))
                    o["gold_unit"] = float(any(u.start <= c <= u.end for c in ch for i, u in enumerate(units) if i in gold_units))
                    o["adds_gold"] = float(bool(added & new))
                    o["on_hint"] = float(bool(ch & hl))
            for k, v in o.items():
                row[f"{arm}|{k}"] = v
            row[f"{arm}|tokens"] = d[arm]["gen_tokens"]
        rows.append(row)
    if args.conflict_tag:
        dd = RESULTS / f"conflict_{args.conflict_tag}"
        for r in rows:
            inst = insts[r["iid"]]
            src = file_at(inst["repo"], inst["base_commit"], r["path"])
            z = np.load(dd / (key(r["iid"], r["path"]) + ".npz"))
            f = line_features(src, z)
            valid = f["ntok"] > 0
            gold = fix_anchors(gold_edits(inst["patch"])[r["path"]], valid, len(valid), "all")
            order = list(np.argsort(-np.where(valid, f["drop_R-RX_pos"], -1e9)) + 1)
            r["map_top1"] = float(order[0] in gold)
            r["map_top5"] = float(bool(set(order[:5]) & gold))
            r["greedy_noop"] = float(np.exp(z["lp_R"].astype(np.float64).min()) >= 0.5)

    def cell(sub, fn):
        p, lo, hi, _ = boot(sub, fn)
        return f"{100*p:.0f} [{100*lo:.0f}, {100*hi:.0f}]"

    print(f"{len(rows)} files, {len({r['iid'] for r in rows})} issues; one greedy search/replace edit per file and arm; "
          f"oracle file; nothing executed; a reply that hit the token cap is "
          + ("scored if its SEARCH block is complete (sensitivity analysis)\n" if args.lenient_truncation else "invalid (declared rule)\n"))
    print("| Arm | " + " | ".join(OUTS) + " | on_gold if valid | median tokens |\n|---|" + "---|" * (len(OUTS) + 2))
    for arm in arms:
        v = [r for r in rows if r[f"{arm}|valid"]]
        print(f"| {LAB[arm]} | " + " | ".join(cell(rows, lambda r, k=k: r[f"{arm}|{k}"]) for k in OUTS)
              + f" | {cell(v, lambda r: r[f'{arm}|on_gold']) if len(v) >= 5 else '–'} | {np.median([r[f'{arm}|tokens'] for r in rows]):.0f} |")

    print("\n**Primary contrasts** (on_gold, percentage points, instance-clustered bootstrap, unadjusted p):\n")
    prim = [(a, b) for a, b in (("H", "WRONG"), ("H", "none")) if a in arms and b in arms]
    for a, b in prim:
        p, lo, hi, bs = boot(rows, lambda r: r[f"{a}|on_gold"] - r[f"{b}|on_gold"])
        print(f"- {LAB[a]} − {LAB[b]}: {100*p:+.1f} [{100*lo:+.1f}, {100*hi:+.1f}], p = {pval(bs):.4f}")
    print("\n**Secondary contrasts** (Holm-adjusted over this list):\n")
    sec = []
    for a, b in (("H", "none"), ("H", "WRONG"), ("WRONG", "none"), ("GOLD", "H"), ("GOLD", "none"), ("H", "BM25"), ("BM25", "none")):
        if a in arms and b in arms:
            for k in ("on_gold", "near_gold", "gold_unit", "adds_gold", "valid"):
                if (a, b) in prim and k == "on_gold":
                    continue
                p, lo, hi, bs = boot(rows, lambda r: r[f"{a}|{k}"] - r[f"{b}|{k}"])
                sec.append((f"{k}: {LAB[a]} − {LAB[b]}", p, lo, hi, pval(bs)))
    m = len(sec)
    run, adj = 0.0, {}
    for rank, i in enumerate(sorted(range(m), key=lambda i: sec[i][4])):
        run = max(run, min(1.0, (m - rank) * sec[i][4]))
        adj[i] = run
    for i, (lab, p, lo, hi, pv) in enumerate(sec):
        print(f"- {lab}: {100*p:+.1f} [{100*lo:+.1f}, {100*hi:+.1f}], p = {pv:.4f}, Holm {adj[i]:.3f}")

    if "H|hint_has_gold" in rows[0]:
        print("\n**Does the model follow the hint, or use it?** (H arm)\n")
        for flag, name in ((1.0, "hint contains a gold line"), (0.0, "hint contains no gold line")):
            sub = [r for r in rows if r["H|hint_has_gold"] == flag]
            if len(sub) >= 5:
                print(f"- {name} ({len(sub)} files): on_gold with hint {cell(sub, lambda r: r['H|on_gold'])}, "
                      f"without hint {cell(sub, lambda r: r['none|on_gold'])}; edit touches a hinted line {cell(sub, lambda r: r['H|on_hint'])}")
        for arm in arms:
            if f"{arm}|hint_has_gold" in rows[0]:
                print(f"- {LAB[arm]}: hint contains a gold line in {100*np.mean([r[f'{arm}|hint_has_gold'] for r in rows]):.0f}% of files; "
                      f"edit touches a hinted line in {100*np.mean([r[f'{arm}|on_hint'] for r in rows]):.0f}%")
    if args.conflict_tag:
        print(f"\nOn the same files the map alone: top-1 line is gold {100*np.mean([r['map_top1'] for r in rows]):.0f}%, "
              f"a gold line in the top 5 {100*np.mean([r['map_top5'] for r in rows]):.0f}%.")
        sub = [r for r in rows if r["greedy_noop"]]
        if len(sub) >= 5:
            print(f"\n**Files the greedy rewrite would leave unchanged** ({len(sub)} files): on_gold "
                  + "; ".join(f"{LAB[a]} {cell(sub, lambda r, a=a: r[f'{a}|on_gold'])}" for a in arms))
    json.dump({"rows": rows}, open(RESULTS / f"an_edit_{args.tag}{'_lenient' if args.lenient_truncation else ''}.json", "w"))


if __name__ == "__main__":
    main()
