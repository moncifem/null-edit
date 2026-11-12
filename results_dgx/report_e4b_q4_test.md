## E4B, MLX 4-bit weights in PyTorch (DGX arm)  (../results_dgx/an_e4b_q4_test.json)
median lines/file 500, median functions/file 62

**Line level: rank of the best-ranked gold line within the file** (n = 98 files, 83 instances; 95% instance-clustered bootstrap CI)

| Method | hit@1 | hit@5 | hit@10 | median rank | MRR |
|---|---|---|---|---|---|
| Null-edit hazard, issue-specific H (2 passes) | 20.4 [12, 29] | 49.0 [38, 60] | 63.3 [54, 73] | 6 | 0.340 [0.27, 0.42] |
| Null-edit hazard S (1 pass) | 17.3 [10, 26] | 37.8 [27, 48] | 58.2 [48, 68] | 7 | 0.293 [0.22, 0.37] |
| BM25 (issue vs line) | 8.2 [3, 15] | 28.6 [20, 38] | 37.8 [28, 47] | 23 | 0.167 [0.11, 0.23] |
| Wrong-issue hazard S (control) | 3.1 [0, 7] | 7.1 [2, 13] | 11.2 [5, 18] | 64 | 0.064 [0.03, 0.10] |
| Mirror control: lines the wrong issue makes harder | 3.1 [0, 7] | 5.1 [1, 10] | 8.2 [3, 14] | 130 | 0.048 [0.02, 0.09] |
| Line length in tokens | 0.0 [0, 0] | 12.2 [6, 19] | 18.4 [11, 26] | 60 | 0.062 [0.04, 0.08] |
| Position (top of file first) | 1.0 [0, 3] | 4.1 [1, 8] | 7.1 [2, 12] | 172 | 0.034 [0.02, 0.06] |
| Random | 1.0 [0, 3] | 6.1 [2, 11] | 11.2 [4, 18] | 76 | 0.043 [0.02, 0.07] |

**Function level: rank of the best-ranked gold function within the file** (n = 98 files, 83 instances; 95% instance-clustered bootstrap CI)

| Method | hit@1 | hit@3 | hit@5 | median rank | MRR |
|---|---|---|---|---|---|
| Null-edit hazard, issue-specific H (2 passes) | 41.8 [32, 53] | 67.3 [58, 76] | 79.6 [71, 87] | 2 | 0.577 [0.50, 0.66] |
| Null-edit hazard S (1 pass) | 38.8 [30, 48] | 58.2 [48, 67] | 73.5 [64, 82] | 3 | 0.531 [0.45, 0.61] |
| H, function of the top-ranked line (post hoc) | 35.7 [26, 46] | 64.3 [55, 74] | 76.5 [68, 84] | 2 | 0.537 [0.46, 0.62] |
| BM25 (issue vs function) | 42.9 [32, 54] | 66.3 [56, 76] | 76.5 [68, 85] | 2 | 0.580 [0.50, 0.66] |
| Wrong-issue hazard S (control) | 13.3 [7, 21] | 36.7 [27, 47] | 50.0 [39, 61] | 6 | 0.292 [0.23, 0.36] |
| H per token, summed (length-normalised, post hoc) | 44.9 [34, 56] | 69.4 [60, 78] | 81.6 [74, 89] | 2 | 0.603 [0.52, 0.68] |
| Function length in tokens | 39.8 [30, 50] | 53.1 [42, 63] | 60.2 [50, 70] | 3 | 0.496 [0.41, 0.58] |
| Function length in lines | 36.7 [27, 46] | 51.0 [40, 62] | 60.2 [50, 70] | 3 | 0.476 [0.39, 0.56] |
| Random line scores, summed (pure length prior) | 38.8 [29, 49] | 51.0 [40, 62] | 62.2 [52, 72] | 3 | 0.479 [0.39, 0.57] |

**Concentration of edit mass** (lines within ±2 of a gold line are 4.2% of lines on average)

- S, correct issue: 23.7% [17, 31] of the file's total mass  (enrichment ×5.6)
- S, wrong issue: 3.7% [1, 6] of the file's total mass  (enrichment ×0.9)
- H: 27.8% [21, 36] of the file's total mass  (enrichment ×6.6)
- median total S: correct issue 10.4 nats, wrong issue 5.7 nats

**Issue-weighted estimates** (each issue counts once; guards against multi-file issues dominating)

| Method | line hit@1 | line hit@10 | function hit@1 |
|---|---|---|---|
| H | 22.1 [14, 31] | 63.1 [53, 73] | 43.8 [33, 54] |
| S | 18.5 [11, 27] | 57.0 [47, 67] | 39.9 [30, 50] |
| BM25 | 7.6 [2, 14] | 36.6 [27, 47] | 43.9 [33, 55] |

**Issues that do not quote a gold line verbatim** (89 of 98 files)

- H: line hit@10 61.8%; function hit@1 40.4%
- S: line hit@10 57.3%; function hit@1 38.2%
- BM25: line hit@10 32.6%; function hit@1 41.6%

**Paired differences (percentage points, bootstrap 95% CI, two-sided p; Holm = Holm-adjusted over the tests listed)**

- line hit@10: H − BM25: +25.5 [+14.1, +36.4], p < 0.0001, Holm < 0.01
- line hit@10: S − BM25: +20.4 [+8.6, +31.5], p = 0.0004, Holm < 0.01
- line hit@10: S − wrong-issue S: +46.9 [+35.3, +58.1], p < 0.0001, Holm < 0.01
- function hit@1: H − BM25: -1.0 [-13.4, +11.6], p = 0.9230, Holm 1.000
- function hit@3: H − BM25: +1.0 [-10.7, +12.5], p = 0.9618, Holm 1.000
