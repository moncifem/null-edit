# Hypotheses

Status legend: OPEN (untested) · PILOT (dev-set evidence only) · SUPPORTED / REFUTED (held-out evidence).

Notation. For a token x_t of existing source code, three teacher-forced prompts:
U = no issue; B = issue + "current file"; F = issue + "file after the fix".
`drop_FB(t) = log P_B(x_t) - log P_F(x_t)` (positive = the token became *less* likely once the model
is told the issue has been fixed).

| ID | Hypothesis | Falsifier | Status |
|----|-----------|-----------|--------|
| H1 | Lines that the gold patch edits are enriched among lines with high `drop_F*` (the model "expects something else there"). | Line-level AUROC of drop features ≈ 0.5, or no better than unconditional surprisal. | OPEN |
| H2 | The useful signal is *fix intent*, not topical association: `drop_FB` (issue held constant) localizes better than `B-U` (issue present vs absent) and better than lexical overlap (BM25). | `B-U` or BM25 ≥ `drop_FB` at line/function level. | OPEN |
| H3 | The signal is issue-specific: conditioning on a *different* issue of the same repo (X) removes it. | `drop_XU` ≈ `drop_FU`. | OPEN |
| H4 | Scoring extracts at least as much localization knowledge from a small model as asking it to generate the location from the same input. | Generative baseline (same model, same file) clearly better at function level. | OPEN |
| H5 | The effect is not memorization: it holds on issues created after Gemma 4's release. | Signal vanishes on post-release tasks. | OPEN |
| H6 | The same likelihood ratio, applied to candidate patches, separates resolved from unresolved leaderboard patches within a task. | Within-task AUROC ≈ 0.5 or explained by similarity to gold. | OPEN |
| H7 | "Residual bits" of the gold patch given issue + context predict the fraction of public agents that solve a task beyond patch-size features. | Partial correlation ≈ 0 after size controls. | OPEN |

Rejected / parked candidates (see `notes/ideas_*.md`): Luby-restart heavy-tail analysis (needs
many executed trajectories; infeasible in the time), co-change omission (needs heterogeneous
trajectory parsing), open-loop agents (QA/vision prior art; weaker tie to a design principle).

---

## Revision 1 (2026-11-11 18:55 UTC) — after DEV, before any TEST evaluation

**Outcome of the first formulation on DEV (16 files):** the "blind" likelihood shift (file not in
the prompt; H1–H3 above) is real but no better than BM25 (line AUROC 0.75 vs 0.72; function hit@1
0.44 vs 0.56). H2 as stated is **refuted on DEV**: "fix" wording vs "current file" wording (F−B)
carries little signal when the model has not read the file. Parked as a negative result.

**New formulation — null-edit teacher forcing.** Put the issue *and the file* in the prompt, ask
for a full rewrite that fixes the issue, and teacher-force the **unchanged file** as the answer.
With p_t = P(original token t | prompt, original tokens < t):

* Identity: under ancestral sampling the first position where the model's rewrite would deviate
  from the original is distributed as P(τ=t) = (1−p_t)·∏_{s<t} p_s, and P(no edit) = ∏ p_t.
  One forward pass therefore yields the exact first-edit distribution of the model's rewrite policy.
* Line "edit hazard" (single pass): S_i = −Σ_{t∈line i} log p_t^R.
* Issue-specific hazard (two passes): H_i = Σ_{t∈line i} max(0, log p_t^RX − log p_t^R), where RX
  is the identical prompt with a *wrong* issue (same repo, disjoint gold files, similar length).

### Pre-registered TEST analysis (frozen now)

* **Primary feature:** H_i (two-pass). **Secondary:** S_i (one-pass). Function score = sum over the
  function's lines. No other feature/aggregation will be reported as a headline.
* **Primary metrics:** line-level hit@1/5/10 and median rank of the best-ranked gold line within the
  file; function-level hit@1/3/5 and MRR. Gold lines = modified lines + insertion anchors (blank
  anchors moved to the nearest tokenised line); a "modified-lines-only" labelling is reported as a
  robustness check.
* **Baselines on the same files:** BM25 (line and function), line length in tokens, function length,
  random, wrong-issue hazard (S under RX), and the *generative* answer of the same model given the
  same issue + numbered file (greedy, thinking off, lenient parser, parse failures count as misses).
* **Sets:** TEST = first N instances of `results/test_ids.txt` (N fixed by compute, reported), files
  ≤ 20k tokens (coverage reported); LIVE = first N of `results/live_ids.txt`.
* **Statistics:** instance-clustered bootstrap 95% CIs (10,000 resamples); paired bootstrap for the
  difference to BM25 and to the generative baseline.

| ID | Hypothesis | Falsifier | Status |
|----|-----------|-----------|--------|
| N1 | H_i / S_i localize gold-edited lines far better than lexical matching and line length. | hit@10 CI overlaps BM25's. | PILOT (DEV, 22 files: hit@10 0.82/0.77 vs 0.36) |
| N2 | The signal needs both the right issue and the instruction to fix: wrong issue (RX), copy instruction with the right issue (RB) and plain copy (R0) are near chance. | Controls within CI of R. | PILOT (DEV: hit@10 0.18–0.27) |
| N3 | Scoring recovers at least as much as asking: H_i ≥ generative answer of the same model at function level, and better at line level. | Generative clearly better. | OPEN |
| N4 | Not memorization: holds on issues created after the model's knowledge cutoff (LIVE). | LIVE hit@k drops to baseline level. | OPEN |
| N5 | Sharper with model size (E2B < E4B < 12B < 31B). | No monotone trend. | OPEN |
| N6 | Fixed-point verification: after applying a *resolving* patch, the residual hazard of the patched file is lower than after an *unresolving* patch (public leaderboard patches). | Within-task AUROC ≈ 0.5, or explained by diff size / consensus / similarity to gold. | OPEN |
| N7 | File level: the gold file has higher hazard mass than BM25-retrieved distractor files. | AUROC ≈ 0.5. | OPEN |

---

## Revision 2 (2026-11-12 02:02 UTC) — map-guided edit, declared before the run starts

Written while `edit_e4b` is still queued on the DGX (no edit has been generated with these arms).

**Design.** First 100 held-out issues (111 gold files with saved scores), Gemma 4 E4B bf16, one greedy
search/replace edit per file and arm, answer prefilled with the opening marker, oracle file, nothing
executed. Arms: `none` (no hint); `H` (text of the five highest null-edit-hazard lines); `WRONG` (text of
the five highest-hazard lines under the wrong issue — same kind of lines, no issue information: the
placebo); `GOLD` (text of up to five gold lines padded with random lines, shuffled: the ceiling). Hints
quote line text without numbers.

**Primary outcome:** `on_gold` — the edit's SEARCH block is found exactly once in the file and the edit
changes (or inserts next to) a gold-edited line. **Primary contrasts:** H − WRONG and H − none, paired,
instance-clustered bootstrap, reported unadjusted. Everything else (near_gold, gold_unit, adds_gold,
valid, GOLD contrasts, hint-quality splits, the greedy-no-op subset) is secondary and Holm-adjusted or
descriptive.

| ID | Hypothesis | Falsifier |
|----|-----------|-----------|
| N8 | With the map's top-5 lines as a hint, the model's own edit lands on a gold line more often than with a placebo hint and than with no hint. | CI of H − WRONG or of H − none includes 0. |
| N9 | The gain is not pure deference: the H arm's on_gold exceeds the map's own top-1 hit rate on the same files, and the hint does not reduce on_gold where it contains no gold line. | H arm on_gold ≤ map top-1; or on_gold falls below the no-hint arm where the hint is wrong. |

**Also declared now (no-prefill check, `noprefill_e4b`).** On the 84 files where every token has
p ≥ 0.5 under the fix-it prompt, the model answers the same prompt freely (greedy, 40 tokens, no
prefilled fence). Reported: share of replies that open with a ```` ```python ```` fence and the file's
first lines. If this share is low, the "greedy rewrite reproduces the file" statement holds only
conditional on the prefill and the paper must say so.

**Revision 2b (2026-11-12 03:55 UTC) — MAC-arm replication of the map-guided edit, declared before it starts.**
The DGX is unreachable (out of memory since ~03:42 UTC) and `edit_e4b` has not started there. Same design,
arms, prompt, outcomes and primary contrasts as above, run entirely on the laptop: Gemma 4 E4B 4-bit (MLX),
hints from the MAC arm's own 4-bit map (`results/hints_e4b_test_mac.json`, 98 files of the first 88 held-out
issues), tag `e4b_test_mac`. If the DGX run also completes, the DGX (bf16) run is the primary result and this
one is reported as the on-device replication; if it does not, this run is the only one and is reported as such.

**Revision 2c (2026-11-12 03:58 UTC) — token cap raised before any outcome was scored.** The first replies of
the laptop run (≤ 12 of them, kept in `results/edit_e4b_test_mac_cap256_pilot/`) were read for format only:
the model copies long SEARCH blocks and most replies hit the 256-token cap before the `=======` separator,
which would make them invalid by construction. The cap is raised to 640 tokens for every arm and the run
restarted from scratch. No outcome (`on_gold` or any other) had been computed. Nothing else changes. A reply
that still hits the cap counts as invalid, as declared.

**Revision 2d (2026-11-12 05:55 UTC) — no-prefill check moved to the laptop, declared before it starts.** The
DGX is still unreachable. The check declared in Revision 2 is run on the MAC arm instead: Gemma 4 E4B 4-bit
(MLX) answers the fix-it prompt freely (greedy, 40 tokens, no prefilled fence) on the same 84 files (those
where every token has p ≥ 0.5 under the DGX arm's bf16 scores; `results/noprefill_files_dgx84.json`). Under
the 4-bit weights only 8 of the laptop's 98 scored files meet that criterion, so the file list is the bf16
one and the model is the 4-bit one; the paper must state both. Reported as declared: share of replies opening
with a python fence, and share that then copy the file's first lines. If the DGX returns, the bf16 run
replaces this one as the primary.

---

## Revision 3 (2026-11-12 07:20 UTC) — code-lines-only map for the larger models, declared before the confirmation set is scored

**What was seen (exploratory, on the 111 files of held-out issues 1–100; `src/explore_codeonly.py`, sha256 prefix
`b5d620859dd9edd1`).** For 12B and 26B A4B most of a long file's hazard sits on comment and docstring lines (median
share over 11,000 tokens: 0.90 and 0.91; such lines are 31% of lines; E4B 0.11). Ranking only code lines (comment-only
lines and string-statement lines are not ranked; gold lines among them stay gold, so they count against the method)
changes S line@10 from 59% to 79% (12B) and from 59% to 75% (26B A4B); over 11,000 tokens from 32% to 81% and from 24%
to 70%. E4B: 74% → 70%. A laptop check (12B 4-bit, MLX) shows the model rewording docstrings and comments at tokens
that are also very surprising in the bf16 run. This was found after looking at these files, so it is a hypothesis.

**Confirmation set.** Held-out issues 101–200 of `results/test_ids.txt` (`results/conf_ids.txt`). 12B and 26B A4B have
scored none of them (E4B scored them in the main experiment). One pass (frame R), same prompt, same code, DGX arm, tags
`g12b_conf` and `g26b_conf`. Files of at most 32k tokens.

**Frozen analysis.** `prose_lines()` of `explore_codeonly.py` as it is now. Metric: S line@10, gold lines unchanged.

| ID | Hypothesis | Falsifier |
|----|-----------|-----------|
| N10 | For 12B and for 26B A4B, S restricted to code lines beats S over all lines at line@10 on the confirmation files (primary, one test per model, paired instance-clustered bootstrap). | CI of the paired difference includes 0 for either model. |
| N11 | With code lines only, 12B and 26B A4B are not worse than E4B's S over all lines on the same files (secondary; difference and CI reported, no threshold). | — (descriptive) |

Also reported, descriptive: the three length bands, the share of hazard on comment/docstring lines, E4B and E2B under
the same restriction, function level. If 31B can be scored (files ≤ 11,000 tokens), it is analysed the same way and
labelled as outside this confirmation.

**Revision 3b (2026-11-12 07:23 UTC) — laptop replication of the confirmation, declared before it starts.** The DGX
is still unreachable. As insurance, the same confirmation issues are scored on the MAC arm: Gemma 4 12B 4-bit (MLX),
one pass, files of at most 12,000 tokens (laptop memory), tag `g12b_conf_mac`, same frozen analysis. It is secondary:
the DGX runs `g12b_conf` / `g26b_conf` decide N10 if they complete; if they do not, this run is reported as the only
confirmation, with its arm, its quantization and its file-length limit stated.


## Status at freeze (2026-11-12) — every hypothesis, with the evidence that decides it

The tables above are left as they were written. Arms: DGX = bf16, PyTorch; MAC = 4-bit, MLX. Numbers are hit rates in %
with 95% instance-clustered bootstrap intervals; sources are the sections of `EXPERIMENTS.md` named in brackets.

| ID | Status | Evidence |
|----|--------|----------|
| N1 | **SUPPORTED** | Held-out Verified, E4B, 300 files: H line@10 69 [64, 74], S 64 [58, 70], BM25 38 [29, 47], length 17. H − BM25 +31.0 [21, 40]. [E1b results] |
| N2 | **PARTLY REFUTED** | The comparative claim holds: wrong issue 16 [11, 21] at line@10; on 111 files the probe reaches 74 against 35 (right issue, copy instruction) and 23 (no issue), +38.7 [29, 48]. The prediction "near chance" is refuted: both instruction controls are above random (12). [Instruction controls] |
| N3 | **REFUTED at function@1, SUPPORTED at line level** | Function@1: asked 60, H 50 (−9.3 [−15, −4]). Line@10: H 69, asked 51 (+18.0 [12, 24]). Line@1: tied. [Asking the model instead] |
| N4 | **SUPPORTED** (within-set) | SWE-bench-Live after the cutoff, 278 files: H 68 [62, 75], BM25 43, wrong issue 34. Not a proof of no leakage. [Post-cutoff control] |
| N5 | **REFUTED** | S line@10 on 111 files: E2B 53, E4B 74, 12B 59, 26B A4B 59; 31B 80 = E4B 80 on the 74 files it could score. No monotone trend. [Model sizes, parts 1–3] |
| N6 | **NOT RUN** | The fixed-point experiment was dropped for time; its scripts are in `src/` and were not used for the paper. |
| N7 | **NOT RUN** | The file-level experiment was dropped for time; same remark. |
| N8 | **NOT SUPPORTED** (MAC arm) | on_gold: map hint 27, no hint 28, placebo 11, gold lines 40. H − WRONG +15.3 [+6.3, +24.7]; H − none −1.0 [−9.1, +7.4]. N8 required both. [Map-guided edit, MAC arm; scoring corrected 10:35 UTC] |
| N9 | **NOT SUPPORTED** (MAC arm) | H arm (27) exceeds the map's top-1 (21), but where the hint has no gold line on_gold is 2 against 8 without a hint. |
| N10 | **SUPPORTED** | Confirmation issues 101–200, 113 files, DGX: 12B 42 → 69 (+27.4 [+19.4, +36.3]); 26B A4B 39 → 66 (+27.4 [+20.0, +35.5]). MAC replication (12B 4-bit, 69 files): 41 → 57 (+15.9 [+7.0, +25.4]). [Code-lines-only map: pre-registered confirmation] |
| N11 | descriptive | With code lines only, against E4B over all lines on the same files: 12B +4.4 [−3.6, +12.9]; 26B A4B +1.8 [−7.1, +10.7]. |

No-prefill check (declared with N8/N9): on the MAC arm, 4-bit E4B opened with prose in all 84 files; the statement
"greedy rewriting reproduces the file" therefore holds only from the prefilled fence, and the paper says so.
