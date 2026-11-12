## Gemma 4 26B-A4B, held-out (DGX arm)  (../results_dgx/an_g26b_test.json)
median lines/file 493, median functions/file 60

**Line level: rank of the best-ranked gold line within the file** (n = 111 files, 95 instances; 95% instance-clustered bootstrap CI)

| Method | hit@1 | hit@5 | hit@10 | median rank | MRR |
|---|---|---|---|---|---|
| Null-edit hazard S (1 pass) | 23.4 [16, 31] | 51.4 [42, 61] | 58.6 [50, 68] | 5 | 0.367 [0.30, 0.44] |
| Generated answer: line ranges (same model) | 27.0 [19, 36] | 63.1 [53, 73] | 73.9 [65, 82] | 4 | 0.423 [0.35, 0.50] |
| BM25 (issue vs line) | 7.2 [3, 13] | 29.7 [21, 39] | 37.8 [29, 47] | 23 | 0.168 [0.12, 0.22] |
| Line length in tokens | 0.0 [0, 0] | 13.5 [8, 20] | 18.9 [12, 26] | 51 | 0.068 [0.05, 0.09] |
| Position (top of file first) | 0.9 [0, 3] | 3.6 [1, 7] | 8.1 [4, 13] | 172 | 0.034 [0.02, 0.06] |
| Random | 0.9 [0, 3] | 7.2 [3, 12] | 11.7 [6, 18] | 76 | 0.047 [0.03, 0.07] |

**Function level: rank of the best-ranked gold function within the file** (n = 111 files, 95 instances; 95% instance-clustered bootstrap CI)

| Method | hit@1 | hit@3 | hit@5 | median rank | MRR |
|---|---|---|---|---|---|
| Null-edit hazard S (1 pass) | 36.9 [28, 46] | 59.5 [50, 68] | 68.5 [59, 77] | 2 | 0.518 [0.44, 0.59] |
| Generated answer: line ranges (same model) | 79.3 [70, 88] | 86.5 [79, 93] | 88.3 [81, 95] | 1 | 0.832 [0.76, 0.90] |
| BM25 (issue vs function) | 43.2 [34, 53] | 64.9 [55, 74] | 75.7 [67, 84] | 2 | 0.578 [0.50, 0.65] |
| Function length in tokens | 36.9 [28, 46] | 53.2 [43, 63] | 60.4 [51, 69] | 3 | 0.482 [0.40, 0.56] |
| Function length in lines | 35.1 [27, 44] | 51.4 [41, 61] | 60.4 [51, 69] | 3 | 0.469 [0.39, 0.54] |
| Random line scores, summed (pure length prior) | 36.0 [27, 45] | 51.4 [41, 61] | 62.2 [53, 71] | 3 | 0.468 [0.39, 0.55] |

**Concentration of edit mass** (lines within ±2 of a gold line are 4.2% of lines on average)

- S, correct issue: 22.6% [17, 29] of the file's total mass  (enrichment ×5.4)

**Issue-weighted estimates** (each issue counts once; guards against multi-file issues dominating)

| Method | line hit@1 | line hit@10 | function hit@1 |
|---|---|---|---|
| S | 24.1 [16, 33] | 58.3 [49, 68] | 37.9 [29, 47] |
| generated answer (line ranges) | 28.0 [19, 37] | 75.8 [67, 84] | 82.7 [75, 90] |
| BM25 | 6.7 [2, 12] | 36.8 [28, 46] | 44.1 [34, 54] |

**Issues that do not quote a gold line verbatim** (101 of 111 files)

- S: line hit@10 58.4%; function hit@1 38.6%
- generated answer (line ranges): line hit@10 71.3%; function hit@1 77.2%
- BM25: line hit@10 32.7%; function hit@1 41.6%

**Paired differences (percentage points, bootstrap 95% CI, two-sided p; Holm = Holm-adjusted over the tests listed)**

- line hit@10: S − BM25: +20.7 [+7.9, +33.3], p = 0.0012, Holm < 0.01
- line hit@10: S − generative: -15.3 [-25.9, -5.2], p = 0.0026, Holm < 0.01
- function hit@1: S − generative: -42.3 [-53.0, -31.5], p < 0.0001, Holm < 0.01
