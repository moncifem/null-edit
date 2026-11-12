"""Figures for the paper (matplotlib, CPU only).

fig1_example.png   hazard map of one held-out file (right vs wrong issue), gold line marked
fig2_hitk.png      line-level hit@k curves, TEST and LIVE
fig3_scaling.png   model-size scaling of line-level hit@10 (scoring vs generated answer)
fig4_fixedpoint.png residual hazard of original / gold-patched / resolved / unresolved files

Usage: python src/figures.py [fig1 iid path]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import os

RES, FIG = Path(os.environ.get("NULLEDIT_RESULTS", ROOT / "results")).resolve(), ROOT / "figures"
FIG.mkdir(exist_ok=True)

# colour-blind-safe palette (Okabe-Ito)
C = {"H": "#0072B2", "S": "#56B4E9", "gen": "#D55E00", "quote": "#E69F00", "bm25": "#009E73",
     "wrong": "#999999", "rand": "#CCCCCC", "len": "#CC79A7"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 160, "savefig.bbox": "tight"})

CURVES = [
    ("lrank_drop_R-RX_pos", "Null-edit hazard H (2 passes)", C["H"], "-"),
    ("lrank_surp_R_sum", "Null-edit hazard S (1 pass)", C["S"], "-"),
    ("lrank_gen2", "Generated answer: quoted lines", C["quote"], "--"),
    ("lrank_gen", "Generated answer: line ranges", C["gen"], "--"),
    ("lrank_bm25", "BM25", C["bm25"], ":"),
    ("lrank_surp_RX_sum", "Hazard under a wrong issue", C["wrong"], ":"),
    ("lrank_random", "Random", C["rand"], ":"),
]


def rows(name):
    p = RES / name
    return json.load(open(p))["rows"] if p.exists() else None


def fig2():
    sets = [("an_e4b_test.json", "SWE-bench Verified (held-out)"), ("an_e4b_live.json", "SWE-bench-Live (post-cutoff)")]
    sets = [(rows(f), t) for f, t in sets if rows(f)]
    if not sets:
        return
    fig, axes = plt.subplots(1, len(sets), figsize=(5.2 * len(sets), 3.6), sharey=True, squeeze=False)
    ks = np.arange(1, 21)
    for ax, (rs, title) in zip(axes[0], sets):
        for key, label, col, ls in CURVES:
            if key not in rs[0]:
                continue
            r = np.array([x[key] for x in rs])
            ax.plot(ks, [100 * (r <= k).mean() for k in ks], ls, color=col, label=label, lw=2)
        ax.set_title(f"{title}\n{len(rs)} files, Gemma 4 E4B", fontsize=10)
        ax.set_xlabel("k (lines inspected)")
        ax.set_xticks([1, 5, 10, 15, 20])
        ax.grid(alpha=0.25)
    axes[0][0].set_ylabel("files with a gold-edited line in top k (%)")
    hl = {}
    for ax in axes[0]:
        for h, l in zip(*ax.get_legend_handles_labels()):
            hl.setdefault(l, h)
    order = [c[1] for c in CURVES if c[1] in hl]
    axes[0][-1].legend([hl[l] for l in order], order, frameon=False, fontsize=8, loc="center left", bbox_to_anchor=(1.0, 0.5))
    fig.savefig(FIG / "fig2_hitk.png")
    plt.close(fig)


def fig3():
    """Top-10 hit rate of the one-pass hazard S per Gemma 4 size, by file length. Left: all lines ranked.
    Right: code lines only (comment and docstring lines not ranked). Needs codeonly_sizes.json (analyze_codeonly.py)."""
    p = RES / "codeonly_sizes.json"
    if not p.exists():
        return
    rows = json.load(open(p))
    p31 = RES / "codeonly_31b.json"   # 31B was scored on files up to 11,000 tokens only (memory)
    if p31.exists():
        rows["31B"] = json.load(open(p31))["31B"]
    order = [n for n in ("E2B", "E4B", "12B", "26B-A4B", "31B") if n in rows]
    cols = dict(zip(("E2B", "E4B", "12B", "26B-A4B", "31B"), ("#9ecae1", C["S"], "#e6550d", "#756bb1", "#31a354")))
    bands = ["under 5,000", "5,000-11,000", "over 11,000"]
    xl = ["< 5k", "5k to 11k", "> 11k"]
    fig, axes = plt.subplots(1, 2, figsize=(7.8, 3.3), sharey=True)
    for ax, key, title in zip(axes, ("all", "code"), ("All lines ranked", "Code lines only (comments, docstrings not ranked)")):
        for n in order:
            xs, v = [], []
            for i, b in enumerate(bands):
                r = [x[key] for x in rows[n] if x["band"] == b]
                if len(r) >= 5:
                    xs.append(i)
                    v.append(100 * np.mean(r))
            ax.plot(xs, v, "o-", color=cols[n], lw=2.4 if n == "E4B" else 1.6, label=n)
        ax.set_ylim(0, 100)
        ax.set_title(title, fontsize=9.5)
        ax.set_xticks(range(3))
        nb = [sum(x["band"] == b for x in rows[order[0]]) for b in bands]
        ax.set_xticklabels([f"{a}\n(n = {n})" for a, n in zip(xl, nb)], fontsize=8.5)
        ax.set_xlim(-0.25, 2.25)
        ax.set_xlabel("file length (tokens)")
        ax.grid(alpha=0.25)
    sj = RES / "scaling.json"
    if sj.exists():
        sc = json.load(open(sj))
        first = next(iter(sc["runs"].values()))
        bm = [first[f"lrank_bm25@10|{st}"][0] for st in sc["strata"] if f"lrank_bm25@10|{st}" in first]
        if len(bm) == 3:
            for ax in axes:
                ax.plot(range(3), bm, "k:", lw=1.6, label="BM25")
    axes[0].set_ylabel("fix line in the top 10 (% of files)")
    axes[0].legend(frameon=False, fontsize=7.5, ncol=2, loc="lower left")
    fig.tight_layout()
    fig.savefig(FIG / "fig3_scaling.png")
    plt.close(fig)


def fig1(iid, path, tag="e4b_test"):
    sys.path.insert(0, str(ROOT / "src"))
    from analyze_conflict import fix_anchors, line_features
    from common import file_at, gold_edits, load_instances
    from run_conflict import key

    inst = {i["instance_id"]: i for i in load_instances()}[iid]
    src = file_at(inst["repo"], inst["base_commit"], path)
    z = np.load(RES / f"conflict_{tag}" / (key(iid, path) + ".npz"))
    f = line_features(src, z)
    g = gold_edits(inst["patch"])[path]
    gold = sorted(fix_anchors(g, f["ntok"] > 0, len(f["ntok"]), "all"))
    S, SX = f["surp_R_sum"], f["surp_RX_sum"]
    lines = src.splitlines()
    x = np.arange(1, len(S) + 1)
    fig, ax = plt.subplots(figsize=(8.5, 3.0))
    ax.bar(x, SX, width=1.0, color=C["wrong"], alpha=0.8, label="wrong issue")
    ax.bar(x, S, width=1.0, color=C["H"], alpha=0.75, label="correct issue")
    for gl in gold:
        ax.axvline(gl, color=C["gen"], lw=1, ls="--")
    ax.plot([], [], color=C["gen"], ls="--", label="line edited by the human fix")
    top = int(np.argmax(S))
    left = top + 1 > 0.6 * len(S)
    ax.annotate(lines[top].strip()[:40] + "…", (top + 1, S[top]), xytext=(-8 if left else 8, -2), textcoords="offset points",
                ha="right" if left else "left", fontsize=7, family="monospace")
    ax.set_xlabel(f"line of {path}")
    ax.set_ylabel("edit hazard $S_i$ (nats)")
    ax.set_title(f"{iid}: where Gemma 4 E4B would depart from the unchanged file", fontsize=10)
    ax.legend(frameon=False, fontsize=8)
    fig.savefig(FIG / "fig1_example.png")
    plt.close(fig)
    print("gold lines", gold, "top line", top + 1, repr(lines[top]))


def thumbnail(iid, path, tag="e4b_test"):
    """1280x720 cover image: the hazard map of one held-out file under the title."""
    sys.path.insert(0, str(ROOT / "src"))
    from analyze_conflict import fix_anchors, line_features
    from common import file_at, gold_edits, load_instances
    from run_conflict import key

    inst = {i["instance_id"]: i for i in load_instances()}[iid]
    src = file_at(inst["repo"], inst["base_commit"], path)
    f = line_features(src, np.load(RES / f"conflict_{tag}" / (key(iid, path) + ".npz")))
    gold = sorted(fix_anchors(gold_edits(inst["patch"])[path], f["ntok"] > 0, len(f["ntok"]), "all"))
    S, SX = f["surp_R_sum"], f["surp_RX_sum"]
    x = np.arange(1, len(S) + 1)
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor("white")
    fig.text(0.06, 0.86, "The Null Edit", fontsize=54, fontweight="bold", color="#111111")
    fig.text(0.06, 0.775, "Reading where a small model wants to change code,", fontsize=22, color="#444444")
    fig.text(0.06, 0.72, "without letting it write", fontsize=22, color="#444444")
    ax = fig.add_axes([0.07, 0.13, 0.87, 0.5])
    ax.bar(x, SX, width=1.6, color=C["wrong"], alpha=0.9, label="edit hazard under a wrong issue")
    ax.bar(x, S, width=1.6, color=C["H"], alpha=0.9, label="edit hazard under the right issue")
    for gl in gold:
        ax.axvline(gl, color=C["gen"], lw=2, ls="--")
    ax.plot([], [], color=C["gen"], ls="--", lw=2, label="line the human fix edits")
    ax.set_xlabel(f"line of {path}  (Gemma 4 E4B, one forward pass, nothing generated)", fontsize=14)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.tick_params(labelsize=12)
    ax.legend(frameon=False, fontsize=14, loc="upper left")
    with plt.rc_context({"savefig.bbox": "standard"}):
        fig.savefig(FIG / "thumbnail.png")
    plt.close(fig)


def fig4(tag="e4b"):
    p = RES / f"fixedpoint_{tag}" / "scores.jsonl"
    if not p.exists():
        return
    rs = [json.loads(l) for l in open(p)]
    groups = {"original\n(unfixed)": [], "human fix\napplied": [], "resolving\nagent patch": [], "non-resolving\nagent patch": []}
    for r in rs:
        o = next(c for c in r["cands"] if c["h"] == "orig")
        g = next(c for c in r["cands"] if c["h"] == "gold")
        pos = [c["S_total"] for c in r["cands"] if c["resolved"] is True]
        neg = [c["S_total"] for c in r["cands"] if c["resolved"] is False]
        if not pos or not neg:
            continue
        groups["original\n(unfixed)"].append(o["S_total"])
        groups["human fix\napplied"].append(g["S_total"])
        groups["resolving\nagent patch"].append(np.mean(pos))
        groups["non-resolving\nagent patch"].append(np.mean(neg))
    fig, ax = plt.subplots(figsize=(4.8, 3.3))
    data = [np.array(v) for v in groups.values()]
    ax.boxplot(data, showfliers=False, widths=0.55, medianprops=dict(color=C["gen"], lw=2))
    ax.set_xticklabels(list(groups), fontsize=8)
    ax.set_ylabel("residual hazard $S$ = $-\\log P$(no edit)  (nats)")
    ax.set_title(f"What the model still wants to change ({len(data[0])} tasks)", fontsize=10)
    ax.grid(alpha=0.25, axis="y")
    fig.savefig(FIG / "fig4_fixedpoint.png")
    plt.close(fig)


if __name__ == "__main__":
    fig2()
    fig3()
    fig4()
    if len(sys.argv) >= 3:
        fig1(sys.argv[1], sys.argv[2], *(sys.argv[3:4]))
        thumbnail(sys.argv[1], sys.argv[2], *(sys.argv[3:4]))
