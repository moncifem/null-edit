"""Two further figures for the paper (matplotlib, CPU only).

fig0_method.png   how null-edit teacher forcing works, on the held-out example of fig1 (real code, real hazards)
fig4_asked.png    asking the model against its own map at every Gemma 4 size (from asked_sizes.json)

Usage (from src/): NULLEDIT_RESULTS=../results_dgx python figures_extra.py [iid path]
"""
from __future__ import annotations

import json
import sys
import textwrap

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from figures import C, FIG, RES, ROOT

INK, MUTED, PANEL = "#1a1a1a", "#666666", "#F5F7FA"


def fig_method(iid="pydata__xarray-4075", path="xarray/core/weighted.py", tag="e4b_test"):
    sys.path.insert(0, str(ROOT / "src"))
    from analyze_conflict import fix_anchors, line_features
    from common import file_at, gold_edits, load_instances
    from run_conflict import key

    inst = {i["instance_id"]: i for i in load_instances()}[iid]
    src = file_at(inst["repo"], inst["base_commit"], path)
    f = line_features(src, np.load(RES / f"conflict_{tag}" / (key(iid, path) + ".npz")))
    gold = set(fix_anchors(gold_edits(inst["patch"])[path], f["ntok"] > 0, len(f["ntok"]), "all"))
    S, lines = f["surp_R_sum"], src.splitlines()
    top = int(np.argmax(S)) + 1                      # 1-based line with the highest hazard
    nb = [n for n in range(1, len(lines) + 1) if lines[n - 1].strip()]      # non-blank lines
    k0 = nb.index(top)
    show = nb[max(0, k0 - 3):k0 + 4]
    title = inst["problem_statement"].strip().splitlines()[0].lstrip("# ").strip()

    fig = plt.figure(figsize=(11.5, 3.1))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 115); ax.set_ylim(3.5, 34.5); ax.axis("off")

    def box(x, y, w, h, fc=PANEL, ec="#C9D1DB"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=1.2", fc=fc, ec=ec, lw=1.0))

    def arrow(x0, x1, y):
        ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="-|>", mutation_scale=16, lw=1.6, color=INK))

    # 1. the prompt
    box(1, 5, 30, 28)
    ax.text(2.5, 31.2, "1  Prompt", fontsize=11, weight="bold", color=INK, va="top")
    ax.text(2.5, 27.6, "Issue", fontsize=8.5, color=MUTED, va="top")
    ax.text(2.5, 25.4, textwrap.fill("“" + title + "”", 38), fontsize=8.5, color=INK, va="top", style="italic")
    ax.text(2.5, 19.4, "File", fontsize=8.5, color=MUTED, va="top")
    ax.text(2.5, 17.2, path, fontsize=8.5, color=INK, va="top", family="monospace")
    ax.text(2.5, 13.6, "Instruction", fontsize=8.5, color=MUTED, va="top")
    ax.text(2.5, 11.4, textwrap.fill("“Rewrite <path> so that the issue is fixed. Output the complete file, changing only what is necessary.”", 40),
            fontsize=8.5, color=INK, va="top")
    arrow(32, 37.5, 19)

    # 2. one forward pass over the unchanged file
    box(38.5, 5, 25, 28, fc="#EAF3FB", ec=C["S"])
    ax.text(40, 31.2, "2  One forward pass", fontsize=11, weight="bold", color=INK, va="top")
    ax.text(40, 27.2, textwrap.fill("Gemma 4 is given the unchanged file back as its own answer.", 31), fontsize=9, color=INK, va="top")
    ax.text(40, 20.0, textwrap.fill("At every token we record the probability p of writing what is already there.", 31),
            fontsize=9, color=INK, va="top")
    ax.text(40, 11.2, "Nothing is generated.\nNo fine-tuning, tests or tools.", fontsize=9, color=C["H"], va="top", weight="bold")
    arrow(64.5, 70, 19)

    # 3. the map: real lines of the file with their hazards
    box(71, 5, 43, 28)
    ax.text(72.5, 31.2, "3  Edit hazard per line", fontsize=11, weight="bold", color=INK, va="top")
    ax.text(113, 31.0, "S = −Σ log p", fontsize=8.5, color=MUTED, va="top", ha="right", family="monospace")
    smax = max(S[n - 1] for n in show)
    for k, n in enumerate(show):
        y = 26.3 - 2.75 * k
        hot = n in gold
        code = lines[n - 1].strip()
        code = code if len(code) <= 30 else code[:29] + "…"
        ax.text(72.5, y, f"{n}", fontsize=7.5, color=MUTED, va="center", family="monospace")
        ax.text(75.5, y, code, fontsize=7.5, color=INK, va="center", family="monospace", weight="bold" if hot else "normal")
        w = 13.5 * S[n - 1] / smax
        ax.barh(y, max(w, 0.15), left=98.5, height=1.5, color=C["gen"] if hot else C["H"])
    ax.text(72.5, 6.6, "orange: the line the human fix edits (never shown to the model)", fontsize=7.8, color=C["gen"], va="center")
    fig.savefig(FIG / "fig0_method.png", dpi=200)
    plt.close(fig)
    print("method figure: lines", show, "gold", sorted(gold), "top", top)


def fig_asked():
    d = json.load(open(RES / "asked_sizes.json"))
    names = list(d)
    lab = [n.replace("-", " ") for n in names]
    x = np.arange(len(names))
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.6), sharey=True, gridspec_kw={"width_ratios": [3, 2]})

    def bars(ax, series, w):
        off = (np.arange(len(series)) - (len(series) - 1) / 2) * w
        for o, (key, label, col, hatch) in zip(off, series):
            v = np.array([d[n][key] for n in names])
            ax.bar(x + o, v[:, 0], w * 0.92, color=col, label=label, hatch=hatch, edgecolor="white", linewidth=0.6,
                   yerr=[v[:, 0] - v[:, 1], v[:, 2] - v[:, 0]], error_kw={"lw": 0.9, "capsize": 2, "ecolor": "#333333"})
            for xi, vi in zip(x + o, v):
                ax.text(xi, vi[2] + 1.5, f"{vi[0]:.0f}", ha="center", va="bottom", fontsize=8)
        ax.set_xticks(x); ax.set_xticklabels(lab); ax.set_ylim(0, 108); ax.set_yticks(range(0, 101, 20)); ax.grid(axis="y", alpha=0.25); ax.set_axisbelow(True)

    bars(axes[0], [("asked_line10", "asked for line ranges", C["gen"], None), ("map_line10", "null-edit map, all lines", C["S"], None),
                   ("code_line10", "null-edit map, code lines only", C["H"], None)], 0.27)
    axes[0].set_title("A line of the fix among the top ten lines", fontsize=10)
    axes[0].set_ylabel("files (%)")
    bars(axes[1], [("asked_func1", "asked", C["gen"], None), ("map_func1", "null-edit map", C["S"], None)], 0.36)
    axes[1].set_title("The right function ranked first", fontsize=10)
    for ax in axes:
        ax.axvspan(-0.5, 1.5, color="#000000", alpha=0.035, lw=0)
        ax.set_xlim(-0.5, len(names) - 0.5)
    axes[0].text(0.5, 106, "small models: the map leads", ha="center", va="top", fontsize=8.5, color=MUTED)
    axes[0].text(2.5, 106, "larger models: asking catches up", ha="center", va="top", fontsize=8.5, color=MUTED)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, fontsize=9, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.08))
    fig.suptitle("Gemma 4, same 111 held-out files per model (bf16 weights, 95% intervals)", fontsize=10, y=1.03)
    fig.savefig(FIG / "fig4_asked.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    fig_method(*sys.argv[1:3])
    fig_asked()


def card(iid="pydata__xarray-4075", path="xarray/core/weighted.py", tag="e4b_test"):
    """1120x560 card for the Kaggle writeup. Title and peak sit inside the central square, which is the thumbnail crop."""
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
    fig = plt.figure(figsize=(11.2, 5.6), dpi=100)
    fig.patch.set_facecolor("white")
    fig.text(0.5, 0.80, "The Null Edit", fontsize=46, fontweight="bold", color="#111111", ha="center")
    fig.text(0.5, 0.705, "Reading where a small model wants", fontsize=17, color="#444444", ha="center")
    fig.text(0.5, 0.645, "to change code, without letting it write", fontsize=17, color="#444444", ha="center")
    ax = fig.add_axes([0.05, 0.15, 0.90, 0.42])
    c = gold[0]
    ax.set_xlim(c - 140, c + 140)                      # the human-edited line sits in the middle of the card
    ax.bar(x, SX, width=1.6, color=C["wrong"], alpha=0.9)
    ax.bar(x, S, width=1.6, color=C["H"], alpha=0.95)
    for gl in gold:
        ax.axvline(gl, color=C["gen"], lw=2, ls="--")
    ax.set_yticks([]); ax.set_xticks([])
    for sp in ("left", "top", "right"):
        ax.spines[sp].set_visible(False)
    fig.text(0.5, 0.075, "Gemma 4 · one forward pass · nothing generated", fontsize=13, color="#444444", ha="center")
    with plt.rc_context({"savefig.bbox": "standard"}):
        fig.savefig(FIG / "card_1120x560.png", dpi=100)
    plt.close(fig)


if __name__ == "__main__":
    card(*sys.argv[1:3])
