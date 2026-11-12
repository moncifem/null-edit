S line@10; issues from ../results/test_ids.txt; files common to all runs

| Model | files (issues) | all lines @10 | code lines only @10 | difference (points), p | all lines @1 | code only @1 | hazard on comment/docstring lines (median share) | median total hazard (nats) |
|---|---|---|---|---|---|---|---|---|
| 31B | 74 (61) | 80 [70, 89] | 81 [72, 90] | +1.4 [-7.4, +10.4], p = 0.8846 | 46 [35, 58] | 54 [42, 66] | 0.31 | 36.1 |
| E2B | 74 (61) | 69 [57, 80] | 66 [54, 78] | -2.7 [-9.1, +3.8], p = 0.5256 | 23 [13, 35] | 24 [15, 35] | 0.02 | 4.1 |
| 12B | 74 (61) | 73 [63, 83] | 78 [68, 88] | +5.4 [-4.1, +15.6], p = 0.3410 | 31 [21, 42] | 39 [28, 51] | 0.49 | 21.2 |
| 26B-A4B | 74 (61) | 76 [65, 86] | 77 [67, 87] | +1.4 [-6.5, +9.3], p = 0.8666 | 34 [24, 45] | 47 [36, 59] | 0.47 | 32.7 |
| E4B | 74 (61) | 80 [70, 89] | 74 [64, 85] | -5.4 [-12.0, +0.0], p = 0.1254 | 39 [26, 53] | 38 [25, 51] | 0.02 | 5.0 |

Comment/docstring lines are 28% of non-blank lines (mean over files); every gold line is such a line in 3% of files.

**By file length** (all lines -> code lines only; n files)

| Model | under 5,000 tokens | 5,000-11,000 tokens | over 11,000 tokens |
|---|---|---|---|
| 31B | 90 -> 84 (n = 51; share 0.01) | 57 -> 74 (n = 23; share 0.62) | – |
| E2B | 76 -> 73 (n = 51; share 0.01) | 52 -> 52 (n = 23; share 0.03) | – |
| 12B | 86 -> 84 (n = 51; share 0.46) | 43 -> 65 (n = 23; share 0.56) | – |
| 26B-A4B | 84 -> 80 (n = 51; share 0.30) | 57 -> 70 (n = 23; share 0.76) | – |
| E4B | 84 -> 78 (n = 51; share 0.01) | 70 -> 65 (n = 23; share 0.04) | – |

**Against E4B ranked over all lines, same files** (secondary)

- 31B code lines only − E4B: +1.4 [-8.1, +11.1], p = 0.8760 (74 files); 31B all lines − E4B: +0.0 [-11.1, +11.3], p = 1.0000
- E2B code lines only − E4B: -13.5 [-23.9, -2.7], p = 0.0180 (74 files); E2B all lines − E4B: -10.8 [-20.6, -1.4], p = 0.0296
- 12B code lines only − E4B: -1.4 [-10.7, +8.6], p = 0.8912 (74 files); 12B all lines − E4B: -6.8 [-17.4, +3.8], p = 0.2624
- 26B-A4B code lines only − E4B: -2.7 [-12.7, +7.5], p = 0.6826 (74 files); 26B-A4B all lines − E4B: -4.1 [-14.8, +6.5], p = 0.5524
