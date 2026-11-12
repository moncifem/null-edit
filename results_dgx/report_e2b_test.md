## Gemma 4 E2B, held-out (DGX arm)  (../results_dgx/an_e2b_test.json)
median lines/file 493, median functions/file 60

**Line level: rank of the best-ranked gold line within the file** (n = 111 files, 95 instances; 95% instance-clustered bootstrap CI)

| Method | hit@1 | hit@5 | hit@10 | median rank | MRR |
|---|---|---|---|---|---|
| Null-edit hazard, issue-specific H (2 passes) | 18.0 [10, 26] | 42.3 [33, 52] | 56.8 [47, 66] | 7 | 0.306 [0.23, 0.38] |
| Null-edit hazard S (1 pass) | 15.3 [8, 23] | 40.5 [31, 50] | 53.2 [43, 63] | 9 | 0.274 [0.20, 0.35] |
| BM25 (issue vs line) | 7.2 [3, 13] | 29.7 [21, 39] | 37.8 [29, 47] | 23 | 0.168 [0.12, 0.22] |
| Wrong-issue hazard S (control) | 2.7 [0, 6] | 8.1 [3, 14] | 17.1 [10, 25] | 53 | 0.072 [0.04, 0.11] |
| Mirror control: lines the wrong issue makes harder | 1.8 [0, 5] | 8.1 [3, 13] | 15.3 [9, 22] | 111 | 0.056 [0.03, 0.09] |
| Line length in tokens | 0.0 [0, 0] | 13.5 [8, 20] | 18.9 [12, 26] | 51 | 0.068 [0.05, 0.09] |
| Position (top of file first) | 0.9 [0, 3] | 3.6 [1, 7] | 8.1 [4, 13] | 172 | 0.034 [0.02, 0.06] |
| Random | 0.9 [0, 3] | 7.2 [3, 12] | 11.7 [6, 18] | 76 | 0.047 [0.03, 0.07] |

**Function level: rank of the best-ranked gold function within the file** (n = 111 files, 95 instances; 95% instance-clustered bootstrap CI)

| Method | hit@1 | hit@3 | hit@5 | median rank | MRR |
|---|---|---|---|---|---|
| Null-edit hazard, issue-specific H (2 passes) | 41.4 [32, 51] | 65.8 [56, 75] | 75.7 [67, 83] | 2 | 0.567 [0.49, 0.64] |
| Null-edit hazard S (1 pass) | 37.8 [28, 48] | 58.6 [49, 68] | 71.2 [62, 80] | 2 | 0.521 [0.44, 0.60] |
| H, function of the top-ranked line (post hoc) | 41.4 [32, 51] | 64.0 [54, 73] | 74.8 [66, 83] | 2 | 0.558 [0.48, 0.64] |
| BM25 (issue vs function) | 43.2 [34, 53] | 64.9 [55, 74] | 75.7 [67, 84] | 2 | 0.578 [0.50, 0.65] |
| Wrong-issue hazard S (control) | 18.0 [11, 25] | 35.1 [26, 44] | 51.4 [41, 62] | 5 | 0.325 [0.26, 0.39] |
| H per token, summed (length-normalised, post hoc) | 40.5 [31, 50] | 63.1 [53, 73] | 76.6 [68, 84] | 2 | 0.555 [0.48, 0.63] |
| Function length in tokens | 36.9 [28, 46] | 53.2 [43, 63] | 60.4 [51, 69] | 3 | 0.482 [0.40, 0.56] |
| Function length in lines | 35.1 [27, 44] | 51.4 [41, 61] | 60.4 [51, 69] | 3 | 0.469 [0.39, 0.54] |
| Random line scores, summed (pure length prior) | 36.0 [27, 45] | 51.4 [41, 61] | 62.2 [53, 71] | 3 | 0.468 [0.39, 0.55] |

**Concentration of edit mass** (lines within ±2 of a gold line are 4.2% of lines on average)

- S, correct issue: 22.4% [16, 29] of the file's total mass  (enrichment ×5.3)
- S, wrong issue: 5.1% [1, 10] of the file's total mass  (enrichment ×1.2)
- H: 25.0% [18, 32] of the file's total mass  (enrichment ×6.0)
- median total S: correct issue 13.4 nats, wrong issue 6.4 nats

**Issue-weighted estimates** (each issue counts once; guards against multi-file issues dominating)

| Method | line hit@1 | line hit@10 | function hit@1 |
|---|---|---|---|
| H | 18.1 [11, 26] | 55.0 [45, 65] | 42.2 [33, 52] |
| S | 14.9 [8, 22] | 51.3 [42, 61] | 38.8 [29, 48] |
| BM25 | 6.7 [2, 12] | 36.8 [28, 46] | 44.1 [34, 54] |

**Files the model would leave unchanged** (10 of 111 files: every original token has probability >= 0.5 under the fix-it prompt, so the greedy rewrite reproduces the file verbatim)

- H: line hit@10 60.0% [30, 90]; function hit@1 60.0% [30, 90]
- S: line hit@10 60.0% [30, 90]; function hit@1 50.0% [20, 80]
- BM25: line hit@10 30.0% [0, 60]; function hit@1 60.0% [30, 90]

**Issues that do not quote a gold line verbatim** (101 of 111 files)

- H: line hit@10 55.4%; function hit@1 41.6%
- S: line hit@10 50.5%; function hit@1 37.6%
- BM25: line hit@10 32.7%; function hit@1 41.6%

**Paired differences (percentage points, bootstrap 95% CI, two-sided p; Holm = Holm-adjusted over the tests listed)**

- line hit@10: H − BM25: +18.9 [+7.6, +29.8], p = 0.0010, Holm < 0.01
- line hit@10: S − BM25: +15.3 [+3.6, +26.8], p = 0.0144, Holm 0.043
- line hit@10: S − wrong-issue S: +36.0 [+27.0, +45.3], p < 0.0001, Holm < 0.01
- function hit@1: H − BM25: -1.8 [-11.9, +8.1], p = 0.8022, Holm 1.000
- function hit@3: H − BM25: +0.9 [-9.5, +11.1], p = 0.9350, Holm 1.000
