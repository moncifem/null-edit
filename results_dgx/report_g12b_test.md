## Gemma 4 12B, held-out (DGX arm)  (../results_dgx/an_g12b_test.json)
median lines/file 493, median functions/file 60

**Line level: rank of the best-ranked gold line within the file** (n = 111 files, 95 instances; 95% instance-clustered bootstrap CI)

| Method | hit@1 | hit@5 | hit@10 | median rank | MRR |
|---|---|---|---|---|---|
| Null-edit hazard, issue-specific H (2 passes) | 23.4 [16, 31] | 49.5 [40, 59] | 62.2 [53, 72] | 6 | 0.364 [0.29, 0.44] |
| Null-edit hazard S (1 pass) | 20.7 [14, 28] | 45.9 [36, 55] | 59.5 [50, 69] | 6 | 0.331 [0.26, 0.40] |
| Generated answer: line ranges (same model) | 34.2 [25, 44] | 64.0 [54, 75] | 73.9 [65, 82] | 3 | 0.471 [0.39, 0.56] |
| Exploratory hybrid: H inside generated functions first | 50.5 [41, 60] | 73.0 [64, 82] | 81.1 [73, 89] | 1 | 0.608 [0.53, 0.69] |
| BM25 (issue vs line) | 7.2 [3, 13] | 29.7 [21, 39] | 37.8 [29, 47] | 23 | 0.168 [0.12, 0.22] |
| Wrong-issue hazard S (control) | 1.8 [0, 5] | 8.1 [3, 13] | 16.2 [9, 23] | 80 | 0.064 [0.04, 0.09] |
| Mirror control: lines the wrong issue makes harder | 1.8 [0, 5] | 6.3 [2, 11] | 12.6 [7, 19] | 139 | 0.055 [0.03, 0.08] |
| Line length in tokens | 0.0 [0, 0] | 13.5 [8, 20] | 18.9 [12, 26] | 51 | 0.068 [0.05, 0.09] |
| Position (top of file first) | 0.9 [0, 3] | 3.6 [1, 7] | 8.1 [4, 13] | 172 | 0.034 [0.02, 0.06] |
| Random | 0.9 [0, 3] | 7.2 [3, 12] | 11.7 [6, 18] | 76 | 0.047 [0.03, 0.07] |

**Function level: rank of the best-ranked gold function within the file** (n = 111 files, 95 instances; 95% instance-clustered bootstrap CI)

| Method | hit@1 | hit@3 | hit@5 | median rank | MRR |
|---|---|---|---|---|---|
| Null-edit hazard, issue-specific H (2 passes) | 38.7 [30, 48] | 58.6 [49, 68] | 73.9 [64, 82] | 2 | 0.537 [0.46, 0.61] |
| Null-edit hazard S (1 pass) | 34.2 [25, 43] | 53.2 [44, 63] | 70.3 [61, 79] | 3 | 0.495 [0.42, 0.57] |
| Generated answer: line ranges (same model) | 80.2 [72, 88] | 83.8 [76, 91] | 84.7 [77, 92] | 1 | 0.826 [0.75, 0.90] |
| H, function of the top-ranked line (post hoc) | 36.0 [27, 45] | 60.4 [51, 70] | 73.9 [64, 83] | 2 | 0.524 [0.45, 0.60] |
| BM25 (issue vs function) | 43.2 [34, 53] | 64.9 [55, 74] | 75.7 [67, 84] | 2 | 0.578 [0.50, 0.65] |
| Wrong-issue hazard S (control) | 19.8 [13, 27] | 37.8 [28, 48] | 48.6 [38, 59] | 6 | 0.334 [0.27, 0.41] |
| H per token, summed (length-normalised, post hoc) | 38.7 [30, 48] | 60.4 [50, 70] | 70.3 [60, 79] | 2 | 0.537 [0.46, 0.61] |
| Function length in tokens | 36.9 [28, 46] | 53.2 [43, 63] | 60.4 [51, 69] | 3 | 0.482 [0.40, 0.56] |
| Function length in lines | 35.1 [27, 44] | 51.4 [41, 61] | 60.4 [51, 69] | 3 | 0.469 [0.39, 0.54] |
| Random line scores, summed (pure length prior) | 36.0 [27, 45] | 51.4 [41, 61] | 62.2 [53, 71] | 3 | 0.468 [0.39, 0.55] |

**Concentration of edit mass** (lines within ±2 of a gold line are 4.2% of lines on average)

- S, correct issue: 23.8% [18, 30] of the file's total mass  (enrichment ×5.7)
- S, wrong issue: 3.5% [1, 7] of the file's total mass  (enrichment ×0.8)
- H: 25.9% [20, 32] of the file's total mass  (enrichment ×6.2)
- median total S: correct issue 29.1 nats, wrong issue 30.7 nats

**Issue-weighted estimates** (each issue counts once; guards against multi-file issues dominating)

| Method | line hit@1 | line hit@10 | function hit@1 |
|---|---|---|---|
| H | 24.6 [16, 33] | 63.2 [54, 73] | 41.1 [31, 51] |
| S | 22.2 [14, 31] | 60.1 [50, 70] | 35.8 [26, 45] |
| generated answer (line ranges) | 35.7 [26, 45] | 75.8 [67, 84] | 83.6 [76, 90] |
| BM25 | 6.7 [2, 12] | 36.8 [28, 46] | 44.1 [34, 54] |

**Issues that do not quote a gold line verbatim** (101 of 111 files)

- H: line hit@10 61.4%; function hit@1 39.6%
- S: line hit@10 58.4%; function hit@1 34.7%
- generated answer (line ranges): line hit@10 71.3%; function hit@1 78.2%
- BM25: line hit@10 32.7%; function hit@1 41.6%

**Paired differences (percentage points, bootstrap 95% CI, two-sided p; Holm = Holm-adjusted over the tests listed)**

- line hit@10: H − BM25: +24.3 [+11.2, +37.6], p = 0.0004, Holm < 0.01
- line hit@10: S − BM25: +21.6 [+8.4, +34.9], p = 0.0012, Holm 0.011
- line hit@10: H − generative: -11.7 [-21.5, -1.8], p = 0.0286, Holm 0.143
- line hit@10: S − generative: -14.4 [-24.8, -4.3], p = 0.0080, Holm 0.056
- line hit@10: S − wrong-issue S: +43.2 [+32.8, +54.1], p < 0.0001, Holm < 0.01
- function hit@1: H − BM25: -4.5 [-15.1, +6.0], p = 0.4506, Holm 0.562
- function hit@1: H − generative: -41.4 [-52.3, -30.8], p < 0.0001, Holm < 0.01
- function hit@3: H − BM25: -6.3 [-17.0, +4.0], p = 0.2808, Holm 0.562
- function hit@3: H − generative: -25.2 [-36.1, -14.4], p < 0.0001, Holm < 0.01
- function hit@1: S − generative: -45.9 [-56.5, -35.5], p < 0.0001, Holm < 0.01
- function hit@5: H − generative: -10.8 [-22.1, +0.8], p = 0.0730, Holm 0.219
- line hit@1: H − generative: -10.8 [-20.7, -0.9], p = 0.0388, Holm 0.155
- line hit@5: H − generative: -14.4 [-26.7, -2.7], p = 0.0188, Holm 0.113
- line hit@1: hybrid − generative: +16.2 [+5.6, +26.9], p = 0.0034, Holm 0.027
- line hit@10: hybrid − H: +18.9 [+9.7, +28.4], p = 0.0002, Holm < 0.01
- line hit@1: hybrid − H: +27.0 [+18.7, +35.9], p < 0.0001, Holm < 0.01
