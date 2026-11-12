## Controls, E4B (DGX arm)  (../results_dgx/an_e4b_ctrl.json)
median lines/file 493, median functions/file 60

**Line level: rank of the best-ranked gold line within the file** (n = 111 files, 95 instances; 95% instance-clustered bootstrap CI)

| Method | hit@1 | hit@5 | hit@10 | median rank | MRR |
|---|---|---|---|---|---|
| Null-edit hazard, issue-specific H (2 passes) | 36.0 [26, 46] | 60.4 [51, 69] | 75.7 [68, 83] | 3 | 0.486 [0.40, 0.57] |
| Null-edit hazard S (1 pass) | 31.5 [22, 41] | 58.6 [49, 68] | 73.9 [65, 82] | 4 | 0.447 [0.36, 0.53] |
| BM25 (issue vs line) | 7.2 [3, 13] | 29.7 [21, 39] | 37.8 [29, 47] | 23 | 0.168 [0.12, 0.22] |
| Wrong-issue hazard S (control) | 2.7 [0, 6] | 9.9 [4, 16] | 13.5 [7, 21] | 41 | 0.081 [0.05, 0.12] |
| Correct issue, instruction 'print unchanged' (control) | 8.1 [3, 14] | 23.4 [16, 32] | 35.1 [26, 45] | 25 | 0.160 [0.11, 0.22] |
| No issue, instruction 'print unchanged' (control) | 2.7 [0, 6] | 13.5 [7, 20] | 22.5 [15, 30] | 54 | 0.091 [0.06, 0.13] |
| Mirror control: lines the wrong issue makes harder | 2.7 [0, 6] | 4.5 [1, 9] | 6.3 [2, 12] | 186 | 0.046 [0.02, 0.09] |
| Line length in tokens | 0.0 [0, 0] | 13.5 [8, 20] | 18.9 [12, 26] | 51 | 0.068 [0.05, 0.09] |
| Position (top of file first) | 0.9 [0, 3] | 3.6 [1, 7] | 8.1 [4, 13] | 172 | 0.034 [0.02, 0.06] |
| Random | 0.9 [0, 3] | 7.2 [3, 12] | 11.7 [6, 18] | 76 | 0.047 [0.03, 0.07] |

**Function level: rank of the best-ranked gold function within the file** (n = 111 files, 95 instances; 95% instance-clustered bootstrap CI)

| Method | hit@1 | hit@3 | hit@5 | median rank | MRR |
|---|---|---|---|---|---|
| Null-edit hazard, issue-specific H (2 passes) | 59.5 [50, 69] | 82.0 [74, 90] | 91.9 [87, 96] | 1 | 0.726 [0.66, 0.80] |
| Null-edit hazard S (1 pass) | 54.1 [45, 64] | 78.4 [71, 86] | 88.3 [82, 94] | 1 | 0.684 [0.61, 0.76] |
| H, function of the top-ranked line (post hoc) | 59.5 [50, 70] | 77.5 [69, 85] | 91.9 [87, 96] | 1 | 0.715 [0.64, 0.79] |
| BM25 (issue vs function) | 43.2 [34, 53] | 64.9 [55, 74] | 75.7 [67, 84] | 2 | 0.578 [0.50, 0.65] |
| Wrong-issue hazard S (control) | 19.8 [12, 28] | 38.7 [29, 49] | 48.6 [39, 59] | 6 | 0.340 [0.27, 0.42] |
| Correct issue, instruction 'print unchanged' (control) | 26.1 [18, 35] | 48.6 [39, 58] | 60.4 [51, 69] | 4 | 0.419 [0.35, 0.49] |
| No issue, instruction 'print unchanged' (control) | 23.4 [15, 32] | 42.3 [32, 52] | 51.4 [41, 61] | 5 | 0.373 [0.30, 0.45] |
| H per token, summed (length-normalised, post hoc) | 56.8 [47, 66] | 80.2 [72, 88] | 91.0 [86, 96] | 1 | 0.710 [0.64, 0.78] |
| Function length in tokens | 36.9 [28, 46] | 53.2 [43, 63] | 60.4 [51, 69] | 3 | 0.482 [0.40, 0.56] |
| Function length in lines | 35.1 [27, 44] | 51.4 [41, 61] | 60.4 [51, 69] | 3 | 0.469 [0.39, 0.54] |
| Random line scores, summed (pure length prior) | 36.0 [27, 45] | 51.4 [41, 61] | 62.2 [53, 71] | 3 | 0.468 [0.39, 0.55] |

**Concentration of edit mass** (lines within ±2 of a gold line are 4.2% of lines on average)

- S, correct issue: 37.3% [30, 45] of the file's total mass  (enrichment ×8.9)
- S, wrong issue: 3.4% [2, 6] of the file's total mass  (enrichment ×0.8)
- H: 41.4% [34, 49] of the file's total mass  (enrichment ×9.9)
- median total S: correct issue 5.6 nats, wrong issue 1.3 nats

**Issue-weighted estimates** (each issue counts once; guards against multi-file issues dominating)

| Method | line hit@1 | line hit@10 | function hit@1 |
|---|---|---|---|
| H | 35.6 [26, 45] | 76.0 [68, 84] | 61.5 [52, 71] |
| S | 30.4 [21, 39] | 74.6 [66, 83] | 55.2 [46, 65] |
| BM25 | 6.7 [2, 12] | 36.8 [28, 46] | 44.1 [34, 54] |

**Files the model would leave unchanged** (29 of 111 files: every original token has probability >= 0.5 under the fix-it prompt, so the greedy rewrite reproduces the file verbatim)

- H: line hit@10 69.0% [53, 84]; function hit@1 55.2% [38, 72]
- S: line hit@10 69.0% [52, 86]; function hit@1 48.3% [31, 66]
- BM25: line hit@10 34.5% [17, 54]; function hit@1 34.5% [17, 53]

**Issues that do not quote a gold line verbatim** (101 of 111 files)

- H: line hit@10 75.2%; function hit@1 58.4%
- S: line hit@10 73.3%; function hit@1 52.5%
- BM25: line hit@10 32.7%; function hit@1 41.6%

**Paired differences (percentage points, bootstrap 95% CI, two-sided p; Holm = Holm-adjusted over the tests listed)**

- line hit@10: H − BM25: +37.8 [+28.1, +47.7], p < 0.0001, Holm < 0.01
- line hit@10: S − BM25: +36.0 [+26.2, +46.2], p < 0.0001, Holm < 0.01
- line hit@10: S − wrong-issue S: +60.4 [+50.0, +70.6], p < 0.0001, Holm < 0.01
- function hit@1: H − BM25: +16.2 [+4.5, +28.0], p = 0.0070, Holm < 0.01
- function hit@3: H − BM25: +17.1 [+8.3, +26.7], p < 0.0001, Holm < 0.01
- line hit@10: S − 'print unchanged' control: +38.7 [+29.3, +48.2], p < 0.0001, Holm < 0.01
