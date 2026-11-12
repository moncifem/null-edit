## Gemma 4 31B, held-out (DGX arm)  (../results_dgx/an_g31b_test.json)
median lines/file 324, median functions/file 36

**Line level: rank of the best-ranked gold line within the file** (n = 74 files, 61 instances; 95% instance-clustered bootstrap CI)

| Method | hit@1 | hit@5 | hit@10 | median rank | MRR |
|---|---|---|---|---|---|
| Null-edit hazard S (1 pass) | 45.9 [35, 58] | 73.0 [62, 84] | 79.7 [70, 89] | 2 | 0.593 [0.50, 0.69] |
| BM25 (issue vs line) | 9.5 [3, 18] | 25.7 [15, 37] | 36.5 [25, 48] | 20 | 0.182 [0.11, 0.26] |
| Line length in tokens | 0.0 [0, 0] | 17.6 [10, 26] | 23.0 [14, 33] | 33 | 0.086 [0.06, 0.12] |
| Position (top of file first) | 1.4 [0, 4] | 4.1 [0, 9] | 10.8 [4, 18] | 84 | 0.045 [0.02, 0.08] |
| Random | 1.4 [0, 4] | 10.8 [4, 18] | 17.6 [9, 27] | 46 | 0.066 [0.04, 0.10] |

**Function level: rank of the best-ranked gold function within the file** (n = 74 files, 61 instances; 95% instance-clustered bootstrap CI)

| Method | hit@1 | hit@3 | hit@5 | median rank | MRR |
|---|---|---|---|---|---|
| Null-edit hazard S (1 pass) | 59.5 [48, 71] | 82.4 [74, 91] | 90.5 [83, 97] | 1 | 0.723 [0.64, 0.81] |
| BM25 (issue vs function) | 50.0 [38, 62] | 74.3 [63, 85] | 82.4 [73, 91] | 2 | 0.650 [0.56, 0.74] |
| Function length in tokens | 45.9 [34, 59] | 68.9 [58, 79] | 75.7 [65, 85] | 2 | 0.592 [0.50, 0.69] |
| Function length in lines | 43.2 [32, 55] | 64.9 [53, 76] | 77.0 [67, 86] | 2 | 0.570 [0.48, 0.66] |
| Random line scores, summed (pure length prior) | 44.6 [33, 57] | 66.2 [54, 77] | 77.0 [67, 86] | 2 | 0.572 [0.48, 0.67] |

**Concentration of edit mass** (lines within ±2 of a gold line are 5.7% of lines on average)

- S, correct issue: 45.9% [37, 55] of the file's total mass  (enrichment ×8.0)

**Issue-weighted estimates** (each issue counts once; guards against multi-file issues dominating)

| Method | line hit@1 | line hit@10 | function hit@1 |
|---|---|---|---|
| S | 50.5 [38, 63] | 83.7 [74, 92] | 63.0 [51, 74] |
| BM25 | 8.7 [3, 16] | 34.6 [23, 46] | 50.7 [39, 63] |

**Issues that do not quote a gold line verbatim** (70 of 74 files)

- S: line hit@10 80.0%; function hit@1 58.6%
- BM25: line hit@10 32.9%; function hit@1 47.1%

**Paired differences (percentage points, bootstrap 95% CI, two-sided p; Holm = Holm-adjusted over the tests listed)**

- line hit@10: S − BM25: +43.2 [+28.4, +58.0], p < 0.0001, Holm < 0.01
