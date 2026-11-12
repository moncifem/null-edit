111 files, 95 issues; one greedy search/replace edit per file and arm; oracle file; nothing executed; a reply that hit the token cap is scored if its SEARCH block is complete (sensitivity analysis)

| Arm | valid | ambiguous | truncated | noop | on_gold | near_gold | gold_unit | adds_gold | on_hint | on_gold if valid | median tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|
| no hint | 94 [89, 98] | 1 [0, 3] | 8 [4, 14] | 10 [5, 16] | 41 [31, 52] | 50 [40, 61] | 59 [48, 69] | 11 [5, 17] | 0 [0, 0] | 44 [34, 55] | 189 |
| hint: top-5 null-edit lines | 95 [91, 99] | 0 [0, 0] | 5 [2, 10] | 7 [3, 12] | 44 [34, 54] | 54 [44, 64] | 60 [50, 70] | 11 [5, 17] | 80 [72, 88] | 46 [36, 56] | 186 |
| hint: top-5 wrong-issue lines (placebo) | 91 [85, 96] | 0 [0, 0] | 14 [8, 21] | 8 [4, 13] | 37 [28, 47] | 41 [32, 51] | 46 [36, 56] | 11 [5, 18] | 35 [26, 44] | 41 [31, 51] | 224 |
| hint: gold lines (ceiling) | 95 [91, 99] | 1 [0, 3] | 7 [3, 12] | 9 [4, 15] | 68 [60, 77] | 77 [69, 84] | 78 [71, 86] | 12 [6, 19] | 68 [59, 76] | 72 [63, 80] | 175 |

**Primary contrasts** (on_gold, percentage points, instance-clustered bootstrap, unadjusted p):

- hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +7.2 [-1.8, +16.2], p = 0.1326
- hint: top-5 null-edit lines − no hint: +2.7 [-5.1, +10.2], p = 0.5562

**Secondary contrasts** (Holm-adjusted over this list):

- near_gold: hint: top-5 null-edit lines − no hint: +3.6 [-5.4, +12.7], p = 0.4884, Holm 1.000
- gold_unit: hint: top-5 null-edit lines − no hint: +1.8 [-6.3, +9.7], p = 0.7286, Holm 1.000
- adds_gold: hint: top-5 null-edit lines − no hint: +0.0 [-4.8, +5.0], p = 1.0000, Holm 1.000
- valid: hint: top-5 null-edit lines − no hint: +1.8 [-3.7, +7.5], p = 0.6412, Holm 1.000
- near_gold: hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +12.6 [+3.4, +22.4], p = 0.0088, Holm 0.141
- gold_unit: hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +14.4 [+4.5, +24.6], p = 0.0064, Holm 0.109
- adds_gold: hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +0.0 [-5.0, +5.2], p = 1.0000, Holm 1.000
- valid: hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +4.5 [-1.9, +11.5], p = 0.2418, Holm 1.000
- on_gold: hint: top-5 wrong-issue lines (placebo) − no hint: -4.5 [-13.2, +3.8], p = 0.3480, Holm 1.000
- near_gold: hint: top-5 wrong-issue lines (placebo) − no hint: -9.0 [-18.9, +0.0], p = 0.0752, Holm 1.000
- gold_unit: hint: top-5 wrong-issue lines (placebo) − no hint: -12.6 [-22.2, -3.5], p = 0.0104, Holm 0.156
- adds_gold: hint: top-5 wrong-issue lines (placebo) − no hint: +0.0 [-4.5, +4.4], p = 1.0000, Holm 1.000
- valid: hint: top-5 wrong-issue lines (placebo) − no hint: -2.7 [-9.6, +3.9], p = 0.5128, Holm 1.000
- on_gold: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +24.3 [+14.3, +34.5], p = 0.0000, Holm 0.000
- near_gold: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +22.5 [+12.0, +33.3], p = 0.0002, Holm 0.004
- gold_unit: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +18.0 [+8.2, +28.0], p = 0.0006, Holm 0.011
- adds_gold: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +0.9 [-2.9, +4.9], p = 0.8206, Holm 1.000
- valid: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +0.0 [-5.0, +5.2], p = 1.0000, Holm 1.000
- on_gold: hint: gold lines (ceiling) − no hint: +27.0 [+16.7, +37.2], p = 0.0000, Holm 0.000
- near_gold: hint: gold lines (ceiling) − no hint: +26.1 [+16.1, +36.4], p = 0.0000, Holm 0.000
- gold_unit: hint: gold lines (ceiling) − no hint: +19.8 [+9.9, +29.9], p = 0.0006, Holm 0.011
- adds_gold: hint: gold lines (ceiling) − no hint: +0.9 [-3.6, +5.7], p = 0.8280, Holm 1.000
- valid: hint: gold lines (ceiling) − no hint: +1.8 [-3.7, +7.4], p = 0.6430, Holm 1.000

**Does the model follow the hint, or use it?** (H arm)

- hint contains a gold line (67 files): on_gold with hint 67 [55, 78], without hint 58 [45, 71]; edit touches a hinted line 90 [82, 96]
- hint contains no gold line (44 files): on_gold with hint 9 [2, 19], without hint 16 [6, 28]; edit touches a hinted line 66 [51, 80]
- hint: top-5 null-edit lines: hint contains a gold line in 60% of files; edit touches a hinted line in 80%
- hint: top-5 wrong-issue lines (placebo): hint contains a gold line in 10% of files; edit touches a hinted line in 35%
- hint: gold lines (ceiling): hint contains a gold line in 100% of files; edit touches a hinted line in 68%

On the same files the map alone: top-1 line is gold 36%, a gold line in the top 5 60%.

**Files the greedy rewrite would leave unchanged** (29 files): on_gold no hint 17 [4, 32]; hint: top-5 null-edit lines 24 [10, 40]; hint: top-5 wrong-issue lines (placebo) 24 [10, 40]; hint: gold lines (ceiling) 52 [34, 69]
