S line@10; issues from ../results/conf_ids.txt

| Model | files (issues) | all lines @10 | code lines only @10 | difference (points), p | all lines @1 | code only @1 | hazard on comment/docstring lines (median share) | median total hazard (nats) |
|---|---|---|---|---|---|---|---|---|
| 12B | 113 (96) | 42 [32, 52] | 69 [60, 78] | +27.4 [+19.4, +36.3], p = 0.0000 | 12 [6, 18] | 25 [17, 32] | 0.79 | 53.2 |
| 26B-A4B | 113 (96) | 39 [30, 48] | 66 [57, 75] | +27.4 [+20.0, +35.5], p = 0.0000 | 7 [3, 12] | 23 [16, 31] | 0.79 | 123.7 |
| E4B | 113 (96) | 65 [54, 75] | 66 [56, 76] | +1.8 [-2.6, +6.3], p = 0.5398 | 19 [13, 27] | 25 [17, 33] | 0.05 | 5.3 |

Comment/docstring lines are 32% of non-blank lines (mean over files); every gold line is such a line in 1% of files.

**By file length** (all lines -> code lines only; n files)

| Model | under 5,000 tokens | 5,000-11,000 tokens | over 11,000 tokens |
|---|---|---|---|
| 12B | 80 -> 85 (n = 40; share 0.12) | 44 -> 74 (n = 27; share 0.85) | 7 -> 52 (n = 46; share 0.93) |
| 26B-A4B | 75 -> 82 (n = 40; share 0.42) | 44 -> 67 (n = 27; share 0.73) | 4 -> 52 (n = 46; share 0.93) |
| E4B | 82 -> 82 (n = 40; share 0.02) | 59 -> 67 (n = 27; share 0.05) | 52 -> 52 (n = 46; share 0.24) |

**Against E4B ranked over all lines, same files** (secondary)

- 12B code lines only − E4B: +4.4 [-3.6, +12.9], p = 0.3262 (113 files); 12B all lines − E4B: -23.0 [-33.3, -12.7], p = 0.0000
- 26B-A4B code lines only − E4B: +1.8 [-7.1, +10.7], p = 0.7508 (113 files); 26B-A4B all lines − E4B: -25.7 [-35.5, -15.8], p = 0.0000
