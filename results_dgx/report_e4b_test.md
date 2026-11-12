## Gemma 4 E4B, SWE-bench Verified held-out (DGX arm)  (../results_dgx/an_e4b_test.json)
median lines/file 587, median functions/file 72

**Line level: rank of the best-ranked gold line within the file** (n = 300 files, 240 instances; 95% instance-clustered bootstrap CI)

| Method | hit@1 | hit@5 | hit@10 | median rank | MRR |
|---|---|---|---|---|---|
| Null-edit hazard, issue-specific H (2 passes) | 27.0 [21, 33] | 55.0 [49, 61] | 69.0 [64, 74] | 4 | 0.401 [0.35, 0.46] |
| Null-edit hazard S (1 pass) | 23.3 [18, 29] | 51.3 [45, 58] | 63.7 [58, 70] | 5 | 0.361 [0.31, 0.41] |
| Generated answer: line ranges (same model) | 23.0 [18, 29] | 43.0 [36, 50] | 51.0 [44, 58] | 10 | 0.317 [0.26, 0.38] |
| Generated answer: quoted lines (same model) | 11.7 [8, 16] | 30.7 [25, 37] | 44.7 [38, 51] | 60 | 0.211 [0.17, 0.25] |
| Exploratory hybrid: H inside generated functions first | 33.0 [27, 40] | 58.0 [52, 65] | 67.3 [62, 73] | 3 | 0.453 [0.40, 0.51] |
| BM25 (issue vs line) | 12.0 [5, 21] | 30.3 [22, 40] | 38.0 [29, 47] | 23 | 0.203 [0.14, 0.29] |
| Wrong-issue hazard S (control) | 3.0 [1, 5] | 9.7 [6, 14] | 15.7 [11, 21] | 71 | 0.079 [0.06, 0.10] |
| Mirror control: lines the wrong issue makes harder | 1.7 [0, 3] | 6.3 [4, 10] | 8.3 [5, 12] | 256 | 0.045 [0.03, 0.07] |
| Line length in tokens | 2.3 [1, 4] | 11.0 [7, 15] | 17.3 [13, 22] | 78 | 0.075 [0.05, 0.10] |
| Position (top of file first) | 0.7 [0, 2] | 3.3 [1, 6] | 7.3 [4, 10] | 180 | 0.033 [0.02, 0.05] |
| Random | 1.7 [0, 3] | 7.7 [5, 11] | 11.7 [8, 16] | 85 | 0.054 [0.04, 0.07] |

**Function level: rank of the best-ranked gold function within the file** (n = 300 files, 240 instances; 95% instance-clustered bootstrap CI)

| Method | hit@1 | hit@3 | hit@5 | median rank | MRR |
|---|---|---|---|---|---|
| Null-edit hazard, issue-specific H (2 passes) | 50.3 [43, 58] | 74.7 [68, 81] | 84.0 [78, 89] | 1 | 0.646 [0.59, 0.70] |
| Null-edit hazard S (1 pass) | 44.3 [38, 51] | 71.7 [64, 79] | 81.0 [76, 86] | 2 | 0.598 [0.54, 0.66] |
| Generated answer: line ranges (same model) | 59.7 [51, 68] | 73.7 [68, 80] | 74.7 [69, 81] | 1 | 0.673 [0.61, 0.74] |
| Generated answer: quoted lines (same model) | 51.3 [44, 59] | 61.7 [56, 67] | 62.0 [56, 68] | 1 | 0.571 [0.52, 0.63] |
| H, function of the top-ranked line (post hoc) | 48.0 [41, 56] | 71.3 [65, 78] | 82.7 [77, 88] | 2 | 0.624 [0.57, 0.68] |
| BM25 (issue vs function) | 38.3 [32, 44] | 62.3 [56, 68] | 71.3 [66, 77] | 2 | 0.535 [0.48, 0.58] |
| Wrong-issue hazard S (control) | 19.3 [14, 25] | 35.3 [29, 42] | 43.7 [37, 51] | 7 | 0.319 [0.27, 0.37] |
| H per token, summed (length-normalised, post hoc) | 49.0 [42, 56] | 72.3 [66, 79] | 84.0 [78, 89] | 2 | 0.635 [0.58, 0.69] |
| Function length in tokens | 29.7 [24, 36] | 44.0 [37, 51] | 53.0 [45, 61] | 5 | 0.408 [0.35, 0.47] |
| Function length in lines | 28.0 [22, 34] | 41.7 [34, 49] | 51.7 [43, 60] | 5 | 0.392 [0.33, 0.45] |
| Random line scores, summed (pure length prior) | 28.7 [23, 35] | 41.3 [34, 49] | 52.3 [44, 60] | 5 | 0.393 [0.33, 0.45] |

**Concentration of edit mass** (lines within ±2 of a gold line are 3.8% of lines on average)

- S, correct issue: 28.5% [24, 33] of the file's total mass  (enrichment ×7.4)
- S, wrong issue: 3.9% [3, 5] of the file's total mass  (enrichment ×1.0)
- H: 32.6% [28, 38] of the file's total mass  (enrichment ×8.5)
- median total S: correct issue 5.0 nats, wrong issue 1.4 nats

**Issue-weighted estimates** (each issue counts once; guards against multi-file issues dominating)

| Method | line hit@1 | line hit@10 | function hit@1 |
|---|---|---|---|
| H | 28.7 [23, 34] | 70.4 [65, 76] | 54.7 [49, 61] |
| S | 24.6 [19, 30] | 66.0 [60, 72] | 47.4 [41, 53] |
| generated answer (line ranges) | 24.3 [19, 30] | 53.7 [48, 60] | 64.7 [59, 70] |
| generated answer (quoted) | 13.0 [9, 17] | 43.9 [38, 50] | 54.2 [48, 60] |
| BM25 | 7.6 [4, 11] | 33.4 [28, 39] | 37.0 [31, 43] |

**Budget-matched comparison with the generated answer** (every method is given exactly as many lines as the answer listed for that file; median 11 lines)

- H: 66.7% [61, 72]
- S: 64.0% [59, 70]
- generated answer (line ranges): 50.3% [44, 57]
- generated answer (quoted): 49.3% [43, 56]
- BM25: 37.0% [29, 46]
- H − generated answer at matched budget: +17.3 [+11.8, +23.1], p < 0.0001

**Files the model would leave unchanged** (84 of 300 files: every original token has probability >= 0.5 under the fix-it prompt, so the greedy rewrite reproduces the file verbatim)

- H: line hit@10 64.3% [53, 75]; function hit@1 48.8% [38, 60]
- S: line hit@10 53.6% [42, 65]; function hit@1 47.6% [37, 59]
- generated answer (line ranges): line hit@10 39.3% [29, 51]; function hit@1 54.8% [44, 67]
- generated answer (quoted): line hit@10 39.3% [28, 50]; function hit@1 46.4% [35, 58]
- BM25: line hit@10 38.1% [25, 51]; function hit@1 36.9% [26, 48]

**Issues that do not quote a gold line verbatim** (272 of 300 files)

- H: line hit@10 67.3%; function hit@1 48.5%
- S: line hit@10 62.5%; function hit@1 42.3%
- generated answer (line ranges): line hit@10 47.8%; function hit@1 56.6%
- generated answer (quoted): line hit@10 42.6%; function hit@1 49.6%
- BM25: line hit@10 34.6%; function hit@1 35.7%

**Paired differences (percentage points, bootstrap 95% CI, two-sided p; Holm = Holm-adjusted over the tests listed)**

- line hit@10: H − BM25: +31.0 [+21.3, +40.2], p < 0.0001, Holm < 0.01
- line hit@10: S − BM25: +25.7 [+14.1, +36.2], p < 0.0001, Holm < 0.01
- line hit@10: H − generative: +18.0 [+11.6, +24.3], p < 0.0001, Holm < 0.01
- line hit@10: S − generative: +12.7 [+7.0, +18.1], p = 0.0002, Holm < 0.01
- line hit@10: S − wrong-issue S: +48.0 [+41.5, +54.5], p < 0.0001, Holm < 0.01
- line hit@10: H − generative (quoted): +24.3 [+18.9, +30.2], p < 0.0001, Holm < 0.01
- line hit@5: H − generative (quoted): +24.3 [+18.5, +30.1], p < 0.0001, Holm < 0.01
- line hit@1: H − generative (quoted): +15.3 [+9.9, +21.0], p < 0.0001, Holm < 0.01
- function hit@1: H − BM25: +12.0 [+1.7, +22.0], p = 0.0222, Holm 0.111
- function hit@1: H − generative: -9.3 [-15.3, -3.7], p = 0.0014, Holm < 0.01
- function hit@3: H − BM25: +12.3 [+3.3, +20.7], p = 0.0074, Holm 0.044
- function hit@3: H − generative: +1.0 [-3.6, +5.9], p = 0.7436, Holm 1.000
- function hit@1: S − generative: -15.3 [-21.8, -9.3], p < 0.0001, Holm < 0.01
- function hit@5: H − generative: +9.3 [+4.6, +14.1], p < 0.0001, Holm < 0.01
- line hit@1: H − generative: +4.0 [-1.6, +9.7], p = 0.1756, Holm 0.702
- line hit@5: H − generative: +12.0 [+6.3, +17.5], p < 0.0001, Holm < 0.01
- line hit@1: hybrid − generative: +10.0 [+4.5, +15.8], p = 0.0006, Holm < 0.01
- line hit@10: hybrid − H: -1.7 [-6.2, +3.2], p = 0.5300, Holm 1.000
- line hit@1: hybrid − H: +6.0 [+3.1, +9.2], p < 0.0001, Holm < 0.01
- function hit@1: H − generative (quoted): -1.0 [-6.7, +4.8], p = 0.7932, Holm 1.000
- function hit@3: H − generative (quoted): +13.0 [+5.5, +20.2], p = 0.0008, Holm < 0.01
- function hit@5: H − generative (quoted): +22.0 [+14.5, +29.5], p < 0.0001, Holm < 0.01
