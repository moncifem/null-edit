98 files, 83 issues; one greedy search/replace edit per file and arm; oracle file; nothing executed; a reply that hit the token cap is scored if its SEARCH block is complete (sensitivity analysis)

| Arm | valid | ambiguous | truncated | noop | on_gold | near_gold | gold_unit | adds_gold | on_hint | on_gold if valid | median tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|
| no hint | 83 [75, 90] | 2 [0, 5] | 29 [19, 39] | 11 [5, 18] | 32 [22, 42] | 40 [29, 50] | 47 [36, 57] | 5 [1, 11] | 0 [0, 0] | 38 [27, 49] | 336 |
| hint: top-5 null-edit lines | 84 [76, 91] | 1 [0, 3] | 27 [18, 35] | 8 [3, 14] | 31 [20, 42] | 43 [32, 54] | 49 [38, 60] | 6 [1, 12] | 58 [48, 69] | 37 [25, 48] | 305 |
| hint: top-5 wrong-issue lines (placebo) | 76 [67, 84] | 0 [0, 0] | 33 [23, 42] | 16 [9, 24] | 21 [13, 31] | 24 [16, 34] | 32 [22, 42] | 3 [0, 8] | 18 [11, 26] | 28 [18, 40] | 352 |
| hint: gold lines (ceiling) | 91 [85, 96] | 1 [0, 3] | 18 [11, 27] | 13 [7, 20] | 47 [36, 58] | 62 [52, 72] | 66 [56, 76] | 6 [1, 12] | 44 [33, 55] | 52 [40, 62] | 262 |

**Primary contrasts** (on_gold, percentage points, instance-clustered bootstrap, unadjusted p):

- hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +9.2 [-1.0, +19.1], p = 0.0836
- hint: top-5 null-edit lines − no hint: -1.0 [-9.6, +7.7], p = 0.9160

**Secondary contrasts** (Holm-adjusted over this list):

- near_gold: hint: top-5 null-edit lines − no hint: +3.1 [-5.4, +12.1], p = 0.5564, Holm 1.000
- gold_unit: hint: top-5 null-edit lines − no hint: +2.0 [-7.4, +12.1], p = 0.7564, Holm 1.000
- adds_gold: hint: top-5 null-edit lines − no hint: +1.0 [-2.1, +4.8], p = 0.7864, Holm 1.000
- valid: hint: top-5 null-edit lines − no hint: +1.0 [-8.1, +10.4], p = 0.9184, Holm 1.000
- near_gold: hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +18.4 [+8.4, +28.6], p = 0.0010, Holm 0.021
- gold_unit: hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +17.3 [+7.2, +27.5], p = 0.0012, Holm 0.024
- adds_gold: hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +3.1 [+0.0, +6.9], p = 0.0980, Holm 1.000
- valid: hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +8.2 [-3.1, +19.8], p = 0.1878, Holm 1.000
- on_gold: hint: top-5 wrong-issue lines (placebo) − no hint: -10.2 [-19.8, +0.0], p = 0.0654, Holm 0.850
- near_gold: hint: top-5 wrong-issue lines (placebo) − no hint: -15.3 [-25.2, -5.2], p = 0.0068, Holm 0.095
- gold_unit: hint: top-5 wrong-issue lines (placebo) − no hint: -15.3 [-25.0, -5.1], p = 0.0050, Holm 0.085
- adds_gold: hint: top-5 wrong-issue lines (placebo) − no hint: -2.0 [-5.1, +0.0], p = 0.2682, Holm 1.000
- valid: hint: top-5 wrong-issue lines (placebo) − no hint: -7.1 [-17.7, +2.8], p = 0.1920, Holm 1.000
- on_gold: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +16.3 [+5.2, +27.6], p = 0.0054, Holm 0.086
- near_gold: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +19.4 [+8.8, +29.9], p = 0.0004, Holm 0.009
- gold_unit: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +17.3 [+5.5, +28.7], p = 0.0040, Holm 0.072
- adds_gold: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +0.0 [-3.1, +3.0], p = 1.0000, Holm 1.000
- valid: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +7.1 [-1.1, +15.1], p = 0.1106, Holm 1.000
- on_gold: hint: gold lines (ceiling) − no hint: +15.3 [+4.7, +26.5], p = 0.0056, Holm 0.086
- near_gold: hint: gold lines (ceiling) − no hint: +22.4 [+11.6, +34.0], p = 0.0000, Holm 0.000
- gold_unit: hint: gold lines (ceiling) − no hint: +19.4 [+7.3, +31.9], p = 0.0014, Holm 0.027
- adds_gold: hint: gold lines (ceiling) − no hint: +1.0 [-2.1, +4.9], p = 0.7808, Holm 1.000
- valid: hint: gold lines (ceiling) − no hint: +8.2 [+0.0, +17.0], p = 0.0824, Holm 0.989

**Does the model follow the hint, or use it?** (H arm)

- hint contains a gold line (47 files): on_gold with hint 60 [44, 75], without hint 53 [37, 68]; edit touches a hinted line 72 [58, 85]
- hint contains no gold line (51 files): on_gold with hint 4 [0, 10], without hint 12 [4, 20]; edit touches a hinted line 45 [31, 60]
- hint: top-5 null-edit lines: hint contains a gold line in 48% of files; edit touches a hinted line in 58%
- hint: top-5 wrong-issue lines (placebo): hint contains a gold line in 7% of files; edit touches a hinted line in 18%
- hint: gold lines (ceiling): hint contains a gold line in 100% of files; edit touches a hinted line in 44%

On the same files the map alone: top-1 line is gold 21%, a gold line in the top 5 48%.

**Files the greedy rewrite would leave unchanged** (8 files): on_gold no hint 38 [12, 71]; hint: top-5 null-edit lines 0 [0, 0]; hint: top-5 wrong-issue lines (placebo) 12 [0, 43]; hint: gold lines (ceiling) 50 [22, 86]
