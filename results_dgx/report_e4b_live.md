## Gemma 4 E4B, SWE-bench-Live post-cutoff (DGX arm)  (../results_dgx/an_e4b_live.json)
median lines/file 324, median functions/file 26

**Line level: rank of the best-ranked gold line within the file** (n = 278 files, 145 instances; 95% instance-clustered bootstrap CI)

| Method | hit@1 | hit@5 | hit@10 | median rank | MRR |
|---|---|---|---|---|---|
| Null-edit hazard, issue-specific H (2 passes) | 30.9 [24, 38] | 59.0 [53, 66] | 68.3 [62, 75] | 4 | 0.432 [0.37, 0.50] |
| Null-edit hazard S (1 pass) | 29.5 [23, 37] | 56.5 [50, 63] | 66.9 [61, 73] | 4 | 0.420 [0.36, 0.49] |
| BM25 (issue vs line) | 12.6 [8, 17] | 29.9 [23, 37] | 42.8 [36, 49] | 14 | 0.219 [0.17, 0.26] |
| Wrong-issue hazard S (control) | 9.4 [6, 13] | 25.5 [19, 32] | 33.8 [26, 41] | 22 | 0.182 [0.14, 0.22] |
| Mirror control: lines the wrong issue makes harder | 9.7 [6, 13] | 18.7 [13, 24] | 27.0 [20, 33] | 53 | 0.153 [0.11, 0.19] |
| Line length in tokens | 4.7 [3, 7] | 18.7 [14, 23] | 32.4 [26, 39] | 22 | 0.134 [0.11, 0.16] |
| Position (top of file first) | 4.7 [2, 9] | 13.3 [8, 19] | 16.5 [11, 22] | 64 | 0.095 [0.06, 0.14] |
| Random | 3.6 [1, 6] | 17.3 [13, 22] | 27.0 [21, 32] | 44 | 0.113 [0.09, 0.14] |

**Function level: rank of the best-ranked gold function within the file** (n = 278 files, 145 instances; 95% instance-clustered bootstrap CI)

| Method | hit@1 | hit@3 | hit@5 | median rank | MRR |
|---|---|---|---|---|---|
| Null-edit hazard, issue-specific H (2 passes) | 62.6 [57, 69] | 86.0 [81, 91] | 89.9 [86, 93] | 1 | 0.750 [0.71, 0.79] |
| Null-edit hazard S (1 pass) | 57.6 [52, 64] | 83.1 [78, 88] | 89.2 [85, 93] | 1 | 0.714 [0.67, 0.76] |
| H, function of the top-ranked line (post hoc) | 60.4 [54, 67] | 83.1 [78, 88] | 89.2 [85, 93] | 1 | 0.730 [0.69, 0.78] |
| BM25 (issue vs function) | 47.5 [40, 55] | 75.9 [70, 81] | 84.9 [80, 89] | 2 | 0.634 [0.58, 0.69] |
| Wrong-issue hazard S (control) | 36.3 [29, 44] | 55.8 [48, 63] | 70.5 [63, 77] | 3 | 0.511 [0.45, 0.57] |
| H per token, summed (length-normalised, post hoc) | 63.7 [57, 70] | 84.9 [80, 89] | 90.3 [86, 94] | 1 | 0.750 [0.71, 0.80] |
| Function length in tokens | 41.4 [35, 48] | 67.6 [61, 74] | 77.0 [70, 83] | 2 | 0.570 [0.51, 0.62] |
| Function length in lines | 41.0 [34, 47] | 67.3 [61, 73] | 78.1 [72, 84] | 2 | 0.570 [0.51, 0.62] |
| Random line scores, summed (pure length prior) | 42.4 [36, 49] | 67.6 [60, 74] | 77.0 [70, 83] | 2 | 0.575 [0.52, 0.62] |

**Concentration of edit mass** (lines within ±2 of a gold line are 9.7% of lines on average)

- S, correct issue: 32.5% [28, 38] of the file's total mass  (enrichment ×3.4)
- S, wrong issue: 13.5% [10, 17] of the file's total mass  (enrichment ×1.4)
- H: 34.9% [30, 40] of the file's total mass  (enrichment ×3.6)
- median total S: correct issue 4.7 nats, wrong issue 1.7 nats

**Issue-weighted estimates** (each issue counts once; guards against multi-file issues dominating)

| Method | line hit@1 | line hit@10 | function hit@1 |
|---|---|---|---|
| H | 32.4 [26, 39] | 71.9 [65, 78] | 63.2 [56, 70] |
| S | 30.4 [24, 37] | 70.0 [63, 76] | 57.8 [51, 65] |
| BM25 | 10.9 [6, 16] | 42.4 [35, 49] | 45.2 [38, 52] |

**Files the model would leave unchanged** (76 of 278 files: every original token has probability >= 0.5 under the fix-it prompt, so the greedy rewrite reproduces the file verbatim)

- H: line hit@10 52.6% [43, 64]; function hit@1 57.9% [45, 69]
- S: line hit@10 50.0% [40, 61]; function hit@1 53.9% [42, 65]
- BM25: line hit@10 39.5% [26, 52]; function hit@1 52.6% [37, 66]

**Issues that do not quote a gold line verbatim** (251 of 278 files)

- H: line hit@10 67.3%; function hit@1 62.2%
- S: line hit@10 66.5%; function hit@1 57.8%
- BM25: line hit@10 41.0%; function hit@1 46.2%

**Paired differences (percentage points, bootstrap 95% CI, two-sided p; Holm = Holm-adjusted over the tests listed)**

- line hit@10: H − BM25: +25.5 [+17.6, +34.0], p < 0.0001, Holm < 0.01
- line hit@10: S − BM25: +24.1 [+16.3, +32.2], p < 0.0001, Holm < 0.01
- line hit@10: S − wrong-issue S: +33.1 [+24.8, +41.2], p < 0.0001, Holm < 0.01
- function hit@1: H − BM25: +15.1 [+7.3, +23.1], p = 0.0004, Holm < 0.01
- function hit@3: H − BM25: +10.1 [+3.9, +16.1], p = 0.0020, Holm < 0.01
