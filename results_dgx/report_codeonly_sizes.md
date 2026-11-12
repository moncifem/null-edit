S line@10; issues from ../results/test_ids.txt; files common to all runs

| Model | files (issues) | all lines @10 | code lines only @10 | difference (points), p | all lines @1 | code only @1 | hazard on comment/docstring lines (median share) | median total hazard (nats) |
|---|---|---|---|---|---|---|---|---|
| E2B | 111 (95) | 53 [43, 63] | 56 [46, 66] | +2.7 [-3.6, +9.3], p = 0.4814 | 15 [8, 23] | 16 [9, 24] | 0.13 | 13.4 |
| 12B | 111 (95) | 59 [50, 69] | 79 [71, 87] | +19.8 [+10.2, +29.9], p = 0.0000 | 21 [14, 28] | 32 [24, 41] | 0.68 | 29.1 |
| 26B-A4B | 111 (95) | 59 [50, 68] | 75 [66, 83] | +16.2 [+7.4, +25.9], p = 0.0002 | 23 [16, 31] | 38 [29, 47] | 0.65 | 73.8 |
| E4B | 111 (95) | 74 [65, 82] | 70 [61, 79] | -3.6 [-8.6, +0.9], p = 0.2052 | 32 [22, 41] | 34 [25, 44] | 0.04 | 5.6 |

Comment/docstring lines are 31% of non-blank lines (mean over files); every gold line is such a line in 3% of files.

**By file length** (all lines -> code lines only; n files)

| Model | under 5,000 tokens | 5,000-11,000 tokens | over 11,000 tokens |
|---|---|---|---|
| E2B | 76 -> 73 (n = 51; share 0.01) | 52 -> 52 (n = 23; share 0.03) | 22 -> 35 (n = 37; share 0.47) |
| 12B | 86 -> 84 (n = 51; share 0.46) | 43 -> 65 (n = 23; share 0.56) | 32 -> 81 (n = 37; share 0.90) |
| 26B-A4B | 84 -> 80 (n = 51; share 0.30) | 57 -> 70 (n = 23; share 0.76) | 24 -> 70 (n = 37; share 0.91) |
| E4B | 84 -> 78 (n = 51; share 0.01) | 70 -> 65 (n = 23; share 0.04) | 62 -> 62 (n = 37; share 0.11) |

**Against E4B ranked over all lines, same files** (secondary)

- E2B code lines only − E4B: -18.0 [-26.7, -9.4], p = 0.0000 (111 files); E2B all lines − E4B: -20.7 [-30.0, -12.1], p = 0.0000
- 12B code lines only − E4B: +5.4 [-2.8, +13.9], p = 0.2402 (111 files); 12B all lines − E4B: -14.4 [-24.5, -4.6], p = 0.0064
- 26B-A4B code lines only − E4B: +0.9 [-7.5, +9.4], p = 0.9302 (111 files); 26B-A4B all lines − E4B: -15.3 [-25.4, -5.8], p = 0.0020
