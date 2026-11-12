# Experiments

Everything here runs on one Apple M5 Max (64 GB) with MLX (`mlx-lm 0.32.2`), 4-bit Gemma 4
checkpoints from `mlx-community` (`gemma-4-e4b-it-4bit`, `gemma-4-12B-it-4bit`,
`gemma-4-31b-it-4bit`). No fine-tuning, no test execution, no network at inference time.
Thinking mode is disabled in every prompt. Scoring is deterministic (no sampling).

## Hardware provenance (every result table names its arm)

| Arm | Machine | Backend | Weights | Used for |
|-----|---------|---------|---------|----------|
| **MAC** | Apple M5 Max laptop, 64 GB | MLX 0.32.4 / mlx-lm 0.32.2 | `mlx-community/gemma-4-*-it-4bit` (4-bit) | Development set (all design choices), throughput on consumer hardware, held-out replication subset (first 88 TEST instances, E4B) |
| **DGX** | NVIDIA DGX Spark (GB10, aarch64, 121 GB unified memory) | PyTorch (cu130) / transformers | official `google/gemma-4-{E2B,E4B,12B,26B-A4B,31B}-it`, bf16 | All headline held-out results, all model sizes, controls, file-level, fixed-point |

## Data and splits (fixed before any held-out evaluation)

| Set | Source | Use |
|-----|--------|-----|
| DEV (25 instances) | SWE-bench Verified, every 20th instance by sorted id (`results/pilot_ids.txt`) | All design choices: prompt frame, line feature, aggregation |
| TEST (475 instances) | remaining SWE-bench Verified, shuffled with seed 20261111 (`results/test_ids.txt`), evaluated in that order (prefix subsets when compute-limited) | Held-out evaluation |
| LIVE (post-cutoff) | SWE-bench-Live `full`, `created_at >= 2025-03-01`, Python source gold files, ≤3 instances per repo, shuffled seed 0 (`results/live_ids.txt`) | Memorization control: issues created after Gemma 4's reported knowledge cutoff (Jan 2025) |

Gold labels (`src/common.py: gold_edits`): original-file line numbers removed/modified by the gold
patch; a pure insertion is represented by its two neighbouring original lines. Function units:
outermost `def` spans from `ast` (nested defs merged into their parent; an earlier version of this line said "leaf-most", which was wrong); residual module/class-header lines form "gap" units. Test files
and newly created files are excluded.

## E0 — Throughput (measured)

E4B 4-bit, MLX: teacher-forced scoring incl. full-vocabulary log-softmax 715–1,100 tok/s
(2.8k–43k-token inputs); greedy generation 54 tok/s. Ratio 13–20×.

## E1a — "Blind" conflict map (file NOT in the prompt) — DEV only

Frames U (no issue), B (issue + "print current file"), F (issue + "print file after fix"),
X (wrong issue + F wording); target = original file. Result on 16 DEV files (partial run, stopped
when the read-then-rewrite variant took priority): best drop feature line-AUROC 0.75 vs BM25 0.72;
function-level hit@1 0.44 vs BM25 0.56. **Conclusion: without the file in context the likelihood
shift is no better than lexical matching.** (Raw: `results/conflict_e4b_pilot/`.)

## E1b — Null-edit teacher forcing (file in the prompt)

Frames (`src/run_conflict.py`): R (issue + file + "rewrite so the issue is fixed"), RX (wrong
issue), RB (issue + file + "print unchanged"), R0 (file + "print unchanged"), D/DX (full-context
unified diff with edit-marker read-out). Target = the unchanged original file.

_Protocol and results are appended below as they are produced._

## E1b results — held-out TEST, Gemma 4 E4B, DGX arm (bf16, PyTorch)

First 250 TEST instances; 300 of 317 gold source files scored (17 exceed 32k tokens). Generated 2026-11-11 22:20 UTC by `src/report.py`.

median lines/file 587, median functions/file 72

**Line level: rank of the best-ranked gold line within the file** (n = 300 files, 240 instances; 95% instance-clustered bootstrap CI)

| Method | hit@1 | hit@5 | hit@10 | median rank |
|---|---|---|---|---|
| Null-edit hazard, issue-specific H (2 passes) | 27.0 [21, 33] | 55.0 [49, 61] | 69.0 [64, 74] | 4 |
| Null-edit hazard S (1 pass) | 23.3 [18, 29] | 51.3 [45, 58] | 63.7 [58, 70] | 5 |
| BM25 (issue vs line) | 12.0 [5, 21] | 30.3 [22, 40] | 38.0 [29, 47] | 23 |
| Wrong-issue hazard S (control) | 3.0 [1, 5] | 9.7 [6, 14] | 15.7 [11, 21] | 71 |
| Line length in tokens | 2.3 [1, 4] | 11.0 [7, 15] | 17.3 [13, 22] | 77 |
| Random | 2.3 [1, 4] | 6.7 [4, 10] | 12.0 [8, 16] | 99 |

**Function level: rank of the best-ranked gold function within the file** (n = 300 files, 240 instances; 95% instance-clustered bootstrap CI)

| Method | hit@1 | hit@3 | hit@5 | median rank |
|---|---|---|---|---|
| Null-edit hazard, issue-specific H (2 passes) | 50.3 [43, 58] | 74.7 [68, 81] | 84.0 [78, 89] | 1 |
| Null-edit hazard S (1 pass) | 44.3 [38, 51] | 71.7 [64, 79] | 81.0 [76, 86] | 2 |
| H, function of the top-ranked line (post hoc) | 48.0 [41, 56] | 71.3 [65, 78] | 82.7 [77, 88] | 2 |
| BM25 (issue vs function) | 38.3 [32, 44] | 62.3 [56, 68] | 71.3 [66, 77] | 2 |
| Wrong-issue hazard S (control) | 19.3 [14, 25] | 35.3 [29, 42] | 43.7 [37, 51] | 7 |
| Random line scores, summed (pure length prior) | 27.3 [22, 34] | 42.7 [36, 50] | 51.7 [44, 59] | 5 |

**Concentration of edit mass** (lines within ±2 of a gold line are 3.8% of lines on average)

- S, correct issue: 28.5% [24, 33] of the file's total mass  (enrichment ×7.4)
- S, wrong issue: 3.9% [3, 5] of the file's total mass  (enrichment ×1.0)
- H: 32.6% [28, 38] of the file's total mass  (enrichment ×8.5)
- median total S: correct issue 5.0 nats, wrong issue 1.4 nats

**Paired differences (percentage points, bootstrap 95% CI, two-sided p)**

- line hit@10: H − BM25: +31.0 [+21.3, +40.2], p = 0.0000
- line hit@10: S − BM25: +25.7 [+14.1, +36.2], p = 0.0000
- line hit@10: S − wrong-issue S: +48.0 [+41.5, +54.5], p = 0.0000
- function hit@1: H − BM25: +12.0 [+1.7, +22.0], p = 0.0222
- function hit@3: H − BM25: +12.3 [+3.3, +20.7], p = 0.0074

### Robustness and breakdowns (`src/extra_stats.py`; hit rates in %)

| Subset | files | H line@10 | S line@10 | BM25 line@10 | H func@1 | BM25 func@1 |
|---|---|---|---|---|---|---|
| all | 300 | 69 | 64 | 38 | 50 | 38 |
| file ≤ 20k tokens (pre-registered cap) | 246 | 71 | 66 | 39 | 54 | 40 |
| file > 20k tokens | 54 | 59 | 54 | 33 | 35 | 31 |
| single-file instances | 209 | 71 | 67 | 32 | 56 | 37 |
| patch only adds lines (pure insertion) | 66 | 55 | 47 | 18 | 47 | 26 |
| patch modifies/removes lines | 234 | 73 | 68 | 44 | 51 | 42 |
| 1–2 gold lines | 156 | 64 | 57 | 34 | 47 | 32 |
| ≥ 6 gold lines | 65 | 77 | 77 | 49 | 55 | 51 |
| django/django | 130 | 72 | 68 | 42 | 56 | 41 |
| sympy/sympy | 63 | 65 | 56 | 44 | 40 | 40 |
| sphinx-doc/sphinx | 27 | 63 | 59 | 26 | 44 | 33 |
| pylint-dev/pylint | 15 | 67 | 60 | 33 | 47 | 33 |
| matplotlib/matplotlib | 13 | 46 | 31 | 23 | 23 | 23 |
| astropy/astropy | 13 | 77 | 77 | 54 | 54 | 46 |
| scikit-learn/scikit-learn | 12 | 75 | 67 | 33 | 75 | 50 |
| pytest-dev/pytest | 10 | 80 | 80 | 30 | 60 | 50 |
| pydata/xarray | 9 | 78 | 67 | 22 | 44 | 22 |
| repo macro-average (repos with ≥5 files) | – | 69 | 63 | 34 | 49 | 38 |

Paired comparison on 91 common files (76 instances): this arm vs other arm
- H line hit@10: 75.8 vs 64.8  (diff +11.0 [+3.5, +19.1], p = 0.007)
- S line hit@10: 74.7 vs 59.3  (diff +15.4 [+6.9, +24.7], p = 0.001)
- H line hit@1: 39.6 vs 23.1  (diff +16.5 [+6.4, +27.1], p = 0.000)
- H function hit@1: 62.6 vs 44.0  (diff +18.7 [+10.4, +28.0], p = 0.000)

"This arm" = DGX bf16; "other arm" = MAC 4-bit MLX, same files. Backend and quantization are confounded in this comparison.

Modified-lines-only labelling (233 files): H line hit@1/5/10 = 27.5/54.9/65.7 vs BM25 14.6/31.8/39.5; function hit@1 48.5 vs 39.1.

### Asking the model instead (generated answer, same model, same files) — DGX arm, added 2026-11-11 23:45 UTC

`src/run_generative.py --mode quote`: the same E4B bf16 model reads the same issue and file and is asked to
quote up to five lines that must change (greedy, 160-token cap). Quotes are mapped back to line numbers.
Two mappings are reported: *aligned* (a line that occurs several times in the file is assigned to the
occurrence that continues the quoted block or lies nearest to a uniquely matched quote — the reading most
favourable to the baseline; `analyze_conflict.py: align_quotes`, written after seeing the first numbers, so
post hoc but in the baseline's favour) and *all occurrences* (the original, stricter mapping).

| E4B, 300 held-out files | line hit@1 | hit@5 | hit@10 | function hit@1 | hit@3 | hit@5 |
|---|---|---|---|---|---|---|
| Null-edit H (2 passes) | 27.0 | 55.0 | 69.0 | 50.3 | 74.7 | 84.0 |
| Null-edit S (1 pass) | 23.3 | 51.3 | 63.7 | 44.3 | 71.7 | 81.0 |
| Generated answer, quoted lines — aligned | 11.7 | 30.7 | 44.7 | 51.3 | 61.7 | 62.0 |
| Generated answer, quoted lines — all occurrences | 11.7 | 26.3 | 36.0 | 47.0 | 60.0 | 62.7 |

Paired (aligned mapping): line hit@10 H − generated +24.3 [+18.9, +30.2]; line hit@1 +15.3 [+9.9, +21.0];
function hit@1 −1.0 [−6.7, +4.8] (p = 0.79, **a tie**); function hit@3 +13.0 [+5.5, +20.2]; function hit@5
+22.0 [+14.5, +29.5]. The generated answer is empty or unmatched for 5 files; it never lists more than a few
functions, so its curve saturates near 62%. Either method ranks the gold function first on 63.7% of files
(both: 38.0%), i.e. the two signals are complementary. (Superseded: any two rankers look complementary by this count; the claim was removed from the paper in review round 4.)

Cost on the DGX (median per file, 6.7k-token median file): one null-edit pass 4.7 s (two passes ≈ 9.5 s);
generated answer 13.5 s (prompt read at ~3.2k tok/s, then ~12 tok/s generation in our plain PyTorch loop).
On the Mac (MLX, 4-bit) generation runs at ~115 tok/s, so the generated answer is the cheaper of the two
there. **Speed is implementation-dependent and is not claimed as a contribution.**

### Context budget for an agent (post hoc, analysis only; `src/context_budget.py`) — DGX arm, E4B, 300 held-out files

Not pre-registered. Windows of ±5 lines are opened around lines in ranking order until at most the given
share of the file's lines is shown. "All gold in view" = every gold-edited line of that file is inside a
shown window. The generated (quoted) answer is taken in answer order and cannot use more budget than it names.

| Ranking | all gold in view, 5% of file | 10% | 20% | any gold in view, 5% | 10% | 20% |
|---|---|---|---|---|---|---|
| Null-edit H | 40 [34, 46] | 53 [47, 60] | 67 [60, 73] | 66 [60, 72] | 80 [75, 86] | 90 [87, 94] |
| Null-edit S | 36 [31, 42] | 48 [42, 54] | 61 [55, 67] | 60 [54, 66] | 76 [71, 81] | 87 [83, 91] |
| Generated answer (quoted) | 29 [23, 34] | 32 [26, 38] | 34 [28, 40] | 52 [46, 58] | 54 [48, 60] | 57 [50, 63] |
| BM25 | 24 [16, 34] | 30 [22, 39] | 37 [29, 46] | 42 [34, 50] | 53 [46, 61] | 65 [58, 71] |
| Wrong issue | 5 | 7 | 14 | 14 | 24 | 40 |
| Random | 4 | 6 | 10 | 12 | 18 | 32 |

Full output: `results_dgx/report_context_budget.md`.

## Post-cutoff control — SWE-bench-Live, Gemma 4 E4B, DGX arm (2026-11-12 00:30 UTC)

First 150 ids of `results/live_ids.txt` (N fixed before any LIVE number was seen); issues created
2025-03-01 … 2025-08-29, i.e. after the model card's stated training-data cutoff (January 2025); 91
repositories, at most three issues each. 278 of 297 gold source files scored (18 over the 32k cap, 1
without usable labels), 145 issues. Files are smaller than in Verified (median 324 lines; ±2-line
neighbourhoods of gold lines cover 9.7% of a file vs 3.8%), so every method — including random — scores
higher in absolute terms; comparisons are within-set. Full report: `results_dgx/report_e4b_live.md`.

| Method | line hit@1 | hit@5 | hit@10 | function hit@1 | hit@3 | hit@5 |
|---|---|---|---|---|---|---|
| Null-edit H (2 passes) | 30.9 [24, 38] | 59.0 [53, 66] | 68.3 [62, 75] | 62.6 [57, 69] | 86.0 | 89.9 |
| Null-edit S (1 pass) | 29.5 [23, 37] | 56.5 [50, 63] | 66.9 [61, 73] | 57.6 [52, 64] | 83.1 | 89.2 |
| BM25 | 12.6 [8, 18] | 29.5 [23, 36] | 43.2 [37, 49] | 47.5 [40, 55] | 75.9 | 85.3 |
| Wrong-issue S (control) | 9.4 | 25.5 | 33.8 [26, 41] | 36.3 | 55.8 | 70.5 |
| Length in tokens | 5.4 | 19.8 | 30.9 | 41.4 | 67.6 | 77.0 |
| Random | 5.0 | 16.2 | 25.9 | 41.0 | 68.7 | 78.4 |

Paired: line hit@10 H − BM25 +25.2 [+17.2, +33.6]; S − BM25 +23.7 [+15.9, +31.8]; S − wrong-issue
+33.1 [+24.8, +41.2]; function hit@1 H − BM25 +15.1 [+7.3, +23.1] (all Holm < 0.01). Issue-weighted:
H@10 71.9 vs BM25 42.5.

Caveat on the wrong-issue control in this set: with ≤3 issues per repository, only 74% of issues get a
same-repository wrong issue; the rest use another repository's. On the same-repository subset (182
files): H 70.9, S 68.7, BM25 42.3, wrong issue 34.6. S does not depend on the wrong issue at all.

Greedy-no-op subset (76 files where every token has p ≥ 0.5): H line hit@10 52.6 [43, 64], BM25 39.5.

## Pre-registered generated-answer baseline: line ranges — E4B, DGX arm (2026-11-12 01:20 UTC)

Same model, same 300 held-out files; the model reads the issue and the numbered file and answers with
line ranges (the baseline named in the pre-registration). Lines of the answer are inspected in answer
order. Report: `results_dgx/report_e4b_test.md`.

| Method | line hit@1 | hit@5 | hit@10 | function hit@1 | hit@3 | hit@5 |
|---|---|---|---|---|---|---|
| Null-edit H | 27.0 | 55.0 | 69.0 [64, 74] | 50.3 | 74.7 | 84.0 |
| Generated answer: line ranges | 23.0 [18, 29] | 43.0 [36, 50] | 51.0 [44, 58] | 59.7 [51, 68] | 73.7 | 74.7 |
| Generated answer: quoted lines | 11.7 | 30.7 | 44.7 | 51.3 | 61.7 | 62.0 |
| Exploratory hybrid: H inside the answer's first three functions, then the rest | 33.0 | 58.0 | 67.3 | – | – | – |

Paired, H − line-range answer: line hit@10 **+18.0** [+11.6, +24.3]; hit@5 +12.0 [+6.3, +17.5]; hit@1
+4.0 [−1.6, +9.7] (n.s.); function hit@1 **−9.3** [−15.3, −3.7] (the answer wins); hit@3 +1.0
[−3.6, +5.9]; hit@5 +9.3 [+4.6, +14.1]. Hybrid − H at line hit@1: +6.0 [+3.1, +9.2]; at hit@10 −1.7 (n.s.).

**Reading.** Asking the model for line ranges is the stronger generated baseline and it *beats* the map
at naming one function. The map wins on lines beyond the first and on functions beyond the third, and
on the greedy-no-op subset (84 files): line hit@10 H 64.3 vs 39.3; function hit@1 48.8 vs 54.8.
Context budget (any gold line in view at 5/10/20% of the file): H 66/80/90, line-range answer 64/70/72.

## Is the MAC–DGX gap quantization or software? (2026-11-12 01:45 UTC)

`e4b_q4_test`: the MAC arm's exact MLX 4-bit checkpoint, de-quantized (`src/make_q4_model.py`) and run
through the DGX PyTorch code on the first 88 held-out issues (98 files scored).

| Comparison (common files) | H line hit@10 | S line hit@10 | H line hit@1 | H function hit@1 |
|---|---|---|---|---|
| bf16 (DGX) vs 4-bit weights (DGX), 98 files | 75.5 vs 63.3, +12.2 [+5.0, +20.2] | 74.5 vs 58.2, +16.3 | 37.8 vs 20.4, +17.3 | 63.3 vs 41.8, +21.4 [+13.7, +29.7] |
| 4-bit weights (DGX) vs 4-bit (MAC, MLX), 91 files | 63.7 vs 64.8, −1.1 [−3.5, 0.0] | 58.2 vs 59.3, −1.1 | 22.0 vs 23.1, −1.1 | 39.6 vs 44.0, −4.4 [−8.6, −1.1] |

**Reading.** The same 4-bit weights give the same line-level numbers on both software stacks; the
12-point gap to bf16 is weight precision. A small residual difference between stacks remains at function
top-1 (−4.4). With 4-bit weights H no longer beats BM25 at function top-1 (41.8 vs 42.9) but still does
on lines (+25.5 [+14.1, +36.4] at hit@10). Report: `results_dgx/report_e4b_q4_test.md`.

## Reading recipe "ask, then read by hazard" and the no-op subset, re-examined (2026-11-12 02:10 UTC, post hoc, CPU)

Any gold line in view after opening ±5-line windows in ranking order (300 held-out files; `report_context_budget.md`):

| Ordering | 5% of file | 10% | 20% |
|---|---|---|---|
| Ask for line ranges, then H inside the answer's first three functions, then H elsewhere | 71 [66, 77] | 79 [74, 84] | 88 [83, 92] |
| H | 66 [60, 72] | 80 [75, 86] | 90 [87, 94] |
| Generated answer: line ranges | 64 [58, 69] | 70 [64, 75] | 72 [67, 78] |
| BM25 | 40 [32, 49] | 53 [46, 61] | 64 [58, 71] |

Paired: recipe − H at 5%: +5.3 [+1.0, +9.8] (p = 0.02); at 10%: −1.0 (n.s.); recipe − answer at 5%:
+7.7 [+3.6, +11.7]; H − answer at 5%: +2.3 (n.s.), at 10%: +10.7 [+5.9, +15.8].

Greedy-no-op subset (84 files, 73 issues; every token p ≥ 0.5 from the prefilled fence): median
P(no edit) = e^{−S} = 0.32, so a temperature-1 rewrite edits about two files in three; 18 files have
their lowest token probability in [0.5, 0.6). Line hit@10: S 53.6 [42, 65], H 64.3 [53, 75], BM25 38.1,
line-range answer 39.3; function hit@1: line-range answer 54.8, H 48.8, S 47.6. Live (76 files): S 50.0,
H 52.6, BM25 39.5. The line-range answer contains a gold line somewhere in 62% of all 300 files (51% within
its first ten lines read top-down).

Random baseline and tie-breaking are now seeded per (file, feature); baseline rows moved by ≤ 1 point
(BM25 line 12.0/30.3/38.0; length 2.3/11.0/17.3; random 1.7/7.7/11.7); H and S rows are unchanged.

## Instruction controls RB / R0 — E4B, DGX arm (2026-11-12 02:15 UTC)

First 100 held-out issues, 111 files (95 issues), merged with R/RX of the main run on the same files
(`merge_frames.py`; `report_e4b_ctrl.md`). RB = right issue + "print the file again, exactly as it is";
R0 = no issue + the same copy instruction.

| Prompt | line hit@1 | hit@5 | hit@10 | function hit@1 |
|---|---|---|---|---|
| R: right issue, "rewrite so that the issue is fixed" (S) | 31.5 | 58.6 | 73.9 [65, 82] | 54.1 |
| RB: right issue, copy instruction | 8.1 | 23.4 | 35.1 [26, 45] | 26.1 |
| R0: no issue, copy instruction | 2.7 | 13.5 | 22.5 [15, 30] | 23.4 |
| RX: wrong issue, fix instruction | 2.7 | 9.9 | 13.5 [7, 21] | 19.8 |
| BM25 | 7.2 | 29.7 | 37.8 | 43.2 |
| Random | 0.9 | 7.2 | 11.7 | 36.0 (length prior) |

Paired at line hit@10: R − RB +38.7 [+29.3, +48.2]; RB − R0 +12.6 [+4.6, +20.8]; RB − RX +21.6
[+12.7, +31.2]; RB − BM25 −2.7 [−14.0, +9.2]; R0 − random +10.8 [+2.6, +19.6] (p = 0.016).

**Reading.** Pre-registered N2 predicted that both copy controls would be near chance. They are not:
with no issue at all the copy hazard is already above random (fixed lines are slightly less predictable
code — the "naturalness" effect), and the right issue adds 13 points even under a copy instruction. But
the copy controls stay at or below BM25, and the instruction to fix adds 39 points on top. N2 is
therefore supported in its comparative form (controls far below R) and refuted in its "near chance" form.
Under a wrong issue the fix instruction scores *below* the no-issue copy control (13.5 vs 22.5): a wrong
issue pulls the model's edits elsewhere.

## Model sizes, part 1: E2B, E4B, 12B (DGX arm, 03:45 UTC)

`e2b_test`, `g12b_test`: first 100 held-out issues, frames R and RX, bf16, same code as E4B.
111 files / 95 issues are common to the three runs. Source: `results_dgx/scaling.md`.

111 common files, 95 instances

| Model | S line@1 | S line@10 | H line@10 | wrong-issue line@10 | asked (ranges) line@10 | quoted answer line@10 | BM25 line@10 | S func@1 | H func@1 | asked (ranges) func@1 | quoted answer func@1 | S func@5 | H func@5 | asked (ranges) func@5 | no-op files (%) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E2B | 15 [8, 23] | 53 [43, 63] | 57 [47, 66] | 17 [10, 25] | – | – | 38 [29, 47] | 38 [28, 48] | 41 [32, 51] | – | – | 71 [62, 80] | 76 [67, 83] | – | 9 [4, 14] |
| E4B | 32 [22, 41] | 74 [65, 82] | 76 [68, 83] | 14 [7, 21] | 61 [52, 71] | 51 [41, 61] | 38 [29, 47] | 54 [45, 64] | 59 [50, 69] | 69 [60, 79] | 64 [54, 74] | 88 [82, 94] | 92 [87, 96] | 84 [76, 91] | 26 [18, 34] |
| 12B | 21 [14, 28] | 59 [50, 69] | 62 [53, 72] | 16 [9, 23] | – | – | 38 [29, 47] | 34 [25, 43] | 39 [30, 48] | – | – | 70 [61, 79] | 74 [64, 82] | – | 5 [1, 9] |

**By file length** (same files; cut at 5000 tokens, chosen after seeing the first three sizes)

| Model | files | S line@10 | H line@10 | S func@1 | BM25 line@10 | median copy cost, right issue (nats) | median copy cost, wrong issue (nats) |
|---|---|---|---|---|---|---|---|
| E2B, under 5,000 tokens | 51 | 76 [65, 88] | 76 [65, 88] | 59 [44, 74] | 35 [23, 48] | 4.3 | 0.8 |
| E4B, under 5,000 tokens | 51 | 84 [74, 94] | 84 [74, 94] | 73 [58, 87] | 35 [23, 48] | 5.7 | 0.7 |
| 12B, under 5,000 tokens | 51 | 86 [75, 96] | 86 [75, 96] | 59 [45, 74] | 35 [23, 48] | 16.9 | 1.4 |
| E2B, 5,000 tokens or more | 60 | 33 [21, 46] | 40 [28, 52] | 20 [10, 31] | 40 [28, 52] | 22.1 | 18.3 |
| E4B, 5,000 tokens or more | 60 | 65 [52, 77] | 68 [56, 80] | 38 [27, 50] | 40 [28, 52] | 5.1 | 2.0 |
| 12B, 5,000 tokens or more | 60 | 37 [24, 50] | 42 [28, 55] | 13 [5, 23] | 40 [28, 52] | 68.8 | 47.9 |

Reading. Not monotonic in size (pre-registered N5 predicted E2B < E4B < 12B < 31B: refuted for
E4B vs 12B). The split by file length is post hoc (cut at 5,000 tokens chosen after seeing these
runs). "Copy cost" is the file total −Σ log p_t; under the wrong issue it measures how hard the model
finds it to reproduce the file at all. On long files 12B has ~24 tokens per file with p < 0.5 in each
frame (about half shared between frames); E4B is confident (p ≥ 0.9) on nearly all of them.

Label-free check (post hoc, threshold 50 nats chosen after seeing the data), S line hit@10 by the
file's total hazard under the right issue, 111 files:

| Model | ≤ 50 nats | > 50 nats |
|---|---|---|
| E2B | 60% (57/95) | 12% (2/16) |
| E4B | 74% (82/111) | – (0 files) |
| 12B | 77% (54/70) | 29% (12/41) |

Not yet verified: that the long-file copy cost of 12B/E2B is a property of the models and not of the
chunked KV-cache scoring loop (`src/diag_long.py`, pending).

## Map-guided edit, MAC arm (Revision 2b/2c) — finished 06:30 UTC, 2026-11-12; scoring corrected 10:35 UTC

Gemma 4 E4B 4-bit (MLX), 98 files / 83 issues, hints from the laptop's own 4-bit map, one greedy
search/replace edit per file and arm, 640-token cap, oracle file, nothing executed. Report:
`results/report_edit_mac.md`; replies: `results/edit_e4b_test_mac/gen.jsonl`.

**Correction (10:35 UTC).** Revision 2c declares that a reply which hits the token cap is invalid. The
analysis script did not apply that rule: it scored a truncated reply whenever its SEARCH block was complete
(18–21 such replies per arm). The table first written here (on_gold 32 / 31 / 21 / 47; H − WRONG +9.2
[−1.0, +19.1]) was therefore the *lenient* scoring, wrongly described as "counted as invalid, as declared".
Found while applying a review, before submission. `analyze_edit.py` now applies the declared rule by default;
`--lenient-truncation` reproduces the earlier table exactly (`results/report_edit_mac_lenient.md`).

Declared rule (primary):

| Arm | valid | truncated | on_gold (primary) | near_gold | gold_unit | edit touches a hinted line |
|---|---|---|---|---|---|---|
| no hint | 64 | 29 | 28 [18, 38] | 33 | 37 | – |
| top-5 null-edit lines | 65 | 27 | 27 [18, 36] | 35 | 40 | 45 |
| top-5 wrong-issue lines (placebo) | 54 | 33 | 11 [5, 19] | 14 | 19 | 9 |
| gold lines (ceiling) | 76 | 18 | 40 [29, 50] | 51 | 54 | 37 |

* **Primary contrasts (on_gold):** H − WRONG = +15.3 [+6.3, +24.7], p = 0.001; H − none = −1.0 [−9.1, +7.4], p = 0.92.
  **N8 is not supported on this arm**: it requires both, and H − none includes 0. The map's lines are a far better
  hint than the placebo's, and no better than no hint.
* Secondary (Holm): H − WRONG on near_gold +20.4 (Holm < 0.001) and gold_unit +20.4 (Holm 0.009). The placebo hurts
  relative to no hint: on_gold −16.3 [−26.8, −6.2] (Holm 0.032). GOLD − none: near_gold +18.4 (Holm 0.024); on_gold
  +12.2 [+1.1, +23.8] (Holm 0.45, not significant).
* Hint quality split (descriptive): where the hint contains a gold line (47 files) on_gold is 53% with the hint and 49%
  without; where it does not (51 files), 2% with and 8% without. **N9**: the H arm (27%) exceeds the map's own top-1
  on these files (21%), but on_gold falls below the no-hint arm where the hint is wrong — the second falsifier is met
  in point estimate. Not supported.
* Greedy-no-op files under 4-bit weights: only 8, no conclusion.
* Sensitivity (lenient scoring of truncated replies): on_gold 32 [22, 42] / 31 [20, 42] / 21 [13, 31] / 47 [36, 58];
  H − WRONG +9.2 [−1.0, +19.1], p = 0.08; H − none −1.0 [−9.6, +7.7]; split 60 vs 53 and 4 vs 12. Same conclusion for
  N8 and N9; the H − WRONG contrast is significant only under the declared rule.
* Reading: the model follows hints in both directions. An untested interpretation: the map is the model's own
  inclination and adds nothing when fed back. Truncation at the cap (18–33% of replies) is high.

## No-prefill check, MAC arm (Revision 2d) — 06:31–06:44 UTC, 2026-11-12

Gemma 4 E4B 4-bit (MLX) answers the fix-it prompt freely (greedy, 40 tokens, no prefilled fence) on the 84 files
that are greedy no-ops under the DGX arm's bf16 scores. Replies: `results/noprefill_e4b_test_mac/gen.jsonl`.

* Replies opening with a ```` ```python ```` fence: **0 of 84**. Replies that then copy the file's first lines: 0 of 84.
* Every reply opens with prose ("The issue is that …", "This is a complex request …").
* Consequence, as declared in Revision 2: the statement "greedy decoding reproduces the file" holds **only
  conditional on the prefilled fence**. The paper's §4.3 now says so. The identity of §2 is about the policy
  conditioned on the prefill; that is unchanged.
* Not measured: whether the prose is followed by a full rewrite, and what the bf16 model does (queued on the DGX).

## Model sizes, part 2: 26B A4B (DGX, bf16) — 06:12–06:44 UTC

111 files / 95 issues common to four sizes, one pass (S). Full table: `results_dgx/scaling.md`.

| | E2B | E4B | 12B | 26B A4B |
|---|---|---|---|---|
| S line@10, all 111 files | 53 [43, 63] | 74 [65, 82] | 59 [50, 69] | 59 [50, 68] |
| S line@10, 51 files under 5,000 tokens | 76 | 84 | 86 | 84 |
| S line@10, 60 files of 5,000 tokens or more | 33 | 65 | 37 | 37 |
| median copy cost, right issue, long files (nats) | 22.1 | 5.1 | 68.8 | 201.5 |
| S function@1, all files | 38 | 54 | 34 | 37 |
| greedy no-op files | 9% | 26% | 5% | 1% |

26B A4B repeats the 12B pattern: as good as E4B on short files, at BM25's level on long ones, with a very high
cost of copying. E4B is the outlier among four sizes. Two caveats to carry into the paper: the prompt was designed
on E4B (development set), and the long-file cost is not yet shown to be the models' behaviour rather than the
backend's (diagnostics `diag_12b`, `diag_g26b` queued; laptop MLX check running).

## Cross-backend length check, 12B (MAC arm, MLX 4-bit) — 06:44–07:03 UTC, 2026-11-12

20 files chosen by length only (`results/lencheck_ids.txt`: 10 under 5,000 tokens, 10 of 5,000–12,000), frames R and
RX, Gemma 4 12B 4-bit on MLX; compared token by token with the DGX arm's bf16 run on the same files.

| Median cost of copying the file (nats) | MLX 4-bit, right issue | MLX 4-bit, wrong issue | DGX bf16, right issue | DGX bf16, wrong issue |
|---|---|---|---|---|
| 10 files under 5,000 tokens | 35.9 | 35.9 | 16.3 | 0.6 |
| 10 files of 5,000–12,000 tokens | 110.6 | 106.5 | 28.6 | 5.9 |

* On an independent backend (different framework, different attention and cache code) 12B also pays more to copy
  long files than short ones, under a wrong issue as well. The direction of the DGX finding is reproduced.
* It is **not a clean replication**: the weights differ (4-bit vs bf16) and the 4-bit model is a far less confident
  copier at every length (36 nats on short files where bf16 pays 0.6). Token-level agreement is weak (correlation of
  per-token log-probabilities under the wrong issue 0.0–0.8 per file). Of the bf16 run's very surprising tokens
  (p < 0.1) in the long files, 16 of 32 are also very surprising in the 4-bit run (e.g. sympy-24661: 8 of 14).
* These ten long files stop at 12k tokens; the DGX collapse is strongest above that (files of 20k+ tokens cost
  400–940 nats). The DGX diagnostics (`diag_12b`, `diag_g26b`: chunk sizes 1024/512/4096 and what the model writes
  instead) remain the decisive check.

## Cross-backend length check, E2B (MAC arm, MLX 4-bit) — 07:03–07:07 UTC, 2026-11-12

Same 20 files. Median cost of copying (nats): MLX 4-bit short 14.1 (right issue) / 18.1 (wrong), long 18.0 / 22.8;
DGX bf16 on the same files short 7.6 / 7.5, long 3.9 / 3.0. No length effect for E2B in the 5,000–12,000-token range on
either backend; the DGX arm's E2B collapse sits in files over 11,000 tokens (next table), which this check does not
reach. 5 of the bf16 run's 10 very surprising tokens (p < 0.1) in the long files are also very surprising on MLX.

## Model sizes by file length, three bands (DGX, bf16; *post hoc*) — 07:10 UTC

`results_dgx/scaling.md` (regenerated by `scaling.py`; bands under 5,000 / 5,000–11,000 / over 11,000 tokens: 5,000 was
chosen after seeing the first three sizes, 11,000 is the largest file 31B can score in 121 GB).

| S line@10 (%) | E2B | E4B | 12B | 26B A4B | BM25 |
|---|---|---|---|---|---|
| under 5,000 tokens (51 files) | 76 | 84 | 86 | 84 | 35 |
| 5,000–11,000 tokens (23 files) | 52 | 70 | 43 | 57 | 39 |
| over 11,000 tokens (37 files) | 22 | 62 | 32 | 24 | 41 |

| Median total hazard, right issue (nats) | E2B | E4B | 12B | 26B A4B |
|---|---|---|---|---|
| under 5,000 tokens | 4.3 | 5.7 | 16.9 | 25.7 |
| 5,000–11,000 tokens | 3.4 | 3.7 | 29.1 | 87.1 |
| over 11,000 tokens | 42.9 | 6.5 | 173.8 | 341.2 |

Spearman(file tokens, total hazard): E2B 0.47, E4B −0.03, 12B 0.67, 26B A4B 0.73. Label-free check (total hazard over
50 nats → S line@10): E2B 16 files, 12% vs 60% below; 12B 41 files, 29% vs 77%; 26B A4B 66 files, 42% vs 82%; E4B
0 files. The 50-nat threshold was chosen on E2B/12B before 26B A4B was scored and was not changed.
The refactored scoring loop (out-of-memory skip) reproduces the previous per-token scores exactly on two files (E2B,
MLX; max difference 0.0).

## What 12B writes instead (MAC arm, MLX 4-bit; qualitative) — 07:11–07:26 UTC, 2026-11-12

`src/diag_alt_mac.py`; outputs `results/diag_alt_mac_R.txt` (right issue) and `results/diag_alt_mac_RX.txt` (wrong
issue). Long files of the length check; tokens with p < 0.1 in BOTH the 4-bit run and the DGX bf16 run; greedy
continuation (24 tokens) of the 4-bit model from just before the token. Up to three tokens per file.

* **Right issue (16 tokens, 8 files).** About half are edits toward the fix (django-14765 `assert
  isinstance(real_apps, set)`; requests-1142 early return for GET/HEAD; sphinx-9320 `allow_empty`; pytest-7982
  `follow_symlinks=True`; sympy-24661 a changed signature). The rest reword a docstring or comment.
* **Wrong issue (10 tokens, 4 files).** All ten are in docstrings, comments or user-facing string literals: the model
  re-wraps or rewords prose, removes a blank line, drops a duplicated word (`this could / could fall back` → one
  `could`), removes a double space, or alters a doctest example. None is in executable code.
* Reading: with no reason to edit, 12B still proofreads prose while "changing only what is necessary". This is
  qualitative (few tokens, one model, 4-bit continuation), but it matches the quantitative share of hazard on
  comment/docstring lines in the bf16 scores.
* Note for the frozen classifier of Revision 3: it treats comments and docstrings as prose, not ordinary string
  literals (e.g. sphinx's help texts), so it under-covers what the model rewords. It stays frozen.

## Code-lines-only map: laptop replication of the confirmation (Revision 3b) — 07:27–07:57 UTC, 2026-11-12

Gemma 4 12B 4-bit (MLX), confirmation issues 101–200, one pass, files ≤ 12,000 tokens: 69 files / 58 issues scored,
50 files skipped for length. Report: `results/report_codeonly_conf_mac.md`.

| | all lines | code lines only | paired difference |
|---|---|---|---|
| S line@10 | 41 [29, 52] | 57 [45, 68] | **+15.9 [+7.0, +25.4], p = 0.0008** |
| S line@1 | 6 | 13 | |
| under 5,000 tokens (40 files) | 62 | 75 | |
| 5,000–11,000 tokens (27 files) | 11 | 33 | |

Median share of hazard on comment/docstring lines 0.74 (they are 30% of lines); median total hazard 64.8 nats.
N10 holds on this arm for 12B (secondary by declaration: 4-bit weights, short and medium files only, one model).
The DGX runs that decide N10 have not started: the DGX has not answered since about 06:45 UTC.

## Code-lines-only map: pre-registered confirmation on the DGX (Revision 3, N10/N11) — 2026-11-12

DGX arm, bf16, one pass (frame R), confirmation issues 101–200 (`results/conf_ids.txt`), files ≤ 32k tokens, frozen
analysis (`src/analyze_codeonly.py`). Report: `results_dgx/report_codeonly_conf.md`.

**12B (`g12b_conf`, 10:29–11:04 UTC).** 113 files / 96 issues scored; 6 files skipped for size (> 32k tokens); no
out-of-memory skip.

| | all lines | code lines only | paired difference |
|---|---|---|---|
| 12B, S line@10 | 42 [32, 52] | 69 [60, 78] | **+27.4 [+19.4, +36.3], p < 0.0001** |
| 12B, S line@1 | 12 [6, 18] | 25 [17, 32] | |
| 12B, under 5,000 tokens (40 files) | 80 | 85 | |
| 12B, 5,000–11,000 tokens (27 files) | 44 | 74 | |
| 12B, over 11,000 tokens (46 files) | 7 | 52 | |
| E4B on the same files (reference) | 65 [54, 75] | 66 [56, 76] | +1.8 [−2.6, +6.3] |

Median share of 12B's hazard on comment/docstring lines: 0.79 overall (0.12 / 0.85 / 0.93 by length band); such lines are
32% of non-blank lines. E4B: 0.05 (0.24 over 11,000 tokens). **N10 holds for 12B.** N11 (descriptive): 12B with code
lines only against E4B over all lines, same files: +4.4 [−3.6, +12.9]; 12B over all lines against E4B: −23.0 [−33.3, −12.7].

**26B A4B (`g26b_conf`, 11:04–11:40 UTC).** 113 files / 96 issues (the same files); 6 skipped for size; no
out-of-memory skip; the memory watchdog never fired.

| | all lines | code lines only | paired difference |
|---|---|---|---|
| 26B A4B, S line@10 | 39 [30, 48] | 66 [57, 75] | **+27.4 [+20.0, +35.5], p < 0.0001** |
| 26B A4B, S line@1 | 7 [3, 12] | 23 [16, 31] | |
| 26B A4B, under 5,000 tokens (40 files) | 75 | 82 | |
| 26B A4B, 5,000–11,000 tokens (27 files) | 44 | 67 | |
| 26B A4B, over 11,000 tokens (46 files) | 4 | 52 | |

Median share of hazard on comment/docstring lines 0.79 (0.42 / 0.73 / 0.93 by band); median total hazard 123.7 nats
(12B 53.2; E4B 5.3). **N10 is supported: the interval excludes 0 for both models.** N11 (descriptive): 26B A4B with code
lines only against E4B over all lines +1.8 [−7.1, +10.7]; over all lines −25.7 [−35.5, −15.8]. Over 11,000 tokens all
three models reach 52% (E4B is unchanged by the rule: 52% → 52%); this set has more long files than issues 1–100
(46 of 113 against 37 of 111), which is why every model's overall number is lower here.

## Model sizes, part 3: 31B (DGX, bf16) — 11:40–12:04 UTC, 2026-11-12

`g31b_test`: first 100 held-out issues, one pass (frame R), files ≤ 11,000 tokens only (31B needs about 1 MB of cache
per context token on top of 62 GB of weights; two earlier attempts on longer files exhausted the machine's memory).
`SCORER_MEM_FRACTION=0.8`. 74 of the 111 files scored (61 issues); 37 skipped for length; no out-of-memory skip; lowest
available memory seen during the run 11 GB. Report: `results_dgx/report_codeonly_31b.md` (all five sizes on these 74 files).

| Model (74 files) | S line@10, all lines | code lines only | S line@1 | under 5,000 tokens (51) | 5,000–11,000 tokens (23) | prose share of hazard |
|---|---|---|---|---|---|---|
| E2B | 69 [57, 80] | 66 | 23 | 76 → 73 | 52 → 52 | 0.02 |
| E4B | 80 [70, 89] | 74 | 39 | 84 → 78 | 70 → 65 | 0.02 |
| 12B | 73 [63, 83] | 78 | 31 | 86 → 84 | 43 → 65 | 0.49 |
| 26B A4B | 76 [65, 86] | 77 | 34 | 84 → 80 | 57 → 70 | 0.47 |
| 31B | 80 [70, 89] | 81 | 46 | 90 → 84 | 57 → 74 | 0.31 |

31B against E4B on the same files: 0.0 [−11.1, +11.3] over all lines; +1.4 [−8.1, +11.1] with code lines only. 31B is
not covered by the pre-registered confirmation (N10 names 12B and 26B A4B) and has no file over 11,000 tokens, where
the other large models lose most. What can be said: on short and medium files the largest model is level with E4B, and
in the 5,000–11,000 band it shows the same drift to prose (share 0.62) and the same repair (57% → 74%) as 12B and 26B A4B.
