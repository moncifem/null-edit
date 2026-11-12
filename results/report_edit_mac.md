98 files, 83 issues; one greedy search/replace edit per file and arm; oracle file; nothing executed; a reply that hit the token cap is invalid (declared rule)

| Arm | valid | ambiguous | truncated | noop | on_gold | near_gold | gold_unit | adds_gold | on_hint | on_gold if valid | median tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|
| no hint | 64 [54, 74] | 2 [0, 5] | 29 [19, 39] | 11 [5, 18] | 28 [18, 38] | 33 [22, 43] | 37 [26, 48] | 5 [1, 11] | 0 [0, 0] | 43 [29, 56] | 336 |
| hint: top-5 null-edit lines | 65 [56, 74] | 1 [0, 3] | 27 [18, 35] | 8 [3, 14] | 27 [18, 36] | 35 [26, 44] | 40 [30, 49] | 6 [1, 12] | 45 [35, 55] | 41 [28, 54] | 305 |
| hint: top-5 wrong-issue lines (placebo) | 54 [43, 65] | 0 [0, 0] | 33 [23, 42] | 16 [9, 24] | 11 [5, 19] | 14 [7, 22] | 19 [11, 28] | 2 [0, 6] | 9 [3, 16] | 21 [10, 34] | 352 |
| hint: gold lines (ceiling) | 76 [67, 84] | 1 [0, 3] | 18 [11, 27] | 13 [7, 20] | 40 [29, 50] | 51 [41, 61] | 54 [44, 64] | 6 [1, 12] | 37 [26, 48] | 53 [41, 65] | 262 |

**Primary contrasts** (on_gold, percentage points, instance-clustered bootstrap, unadjusted p):

- hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +15.3 [+6.3, +24.7], p = 0.0010
- hint: top-5 null-edit lines − no hint: -1.0 [-9.1, +7.4], p = 0.9242

**Secondary contrasts** (Holm-adjusted over this list):

- near_gold: hint: top-5 null-edit lines − no hint: +2.0 [-5.8, +10.4], p = 0.7030, Holm 1.000
- gold_unit: hint: top-5 null-edit lines − no hint: +3.1 [-5.4, +12.1], p = 0.5654, Holm 1.000
- adds_gold: hint: top-5 null-edit lines − no hint: +1.0 [-2.1, +4.8], p = 0.7864, Holm 1.000
- valid: hint: top-5 null-edit lines − no hint: +1.0 [-9.1, +11.5], p = 0.9238, Holm 1.000
- near_gold: hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +20.4 [+11.0, +30.0], p = 0.0000, Holm 0.000
- gold_unit: hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +20.4 [+10.1, +30.9], p = 0.0004, Holm 0.009
- adds_gold: hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +4.1 [+1.0, +8.5], p = 0.0348, Holm 0.452
- valid: hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +11.2 [-2.2, +24.7], p = 0.1186, Holm 0.949
- on_gold: hint: top-5 wrong-issue lines (placebo) − no hint: -16.3 [-26.8, -6.2], p = 0.0018, Holm 0.032
- near_gold: hint: top-5 wrong-issue lines (placebo) − no hint: -18.4 [-29.3, -7.8], p = 0.0014, Holm 0.027
- gold_unit: hint: top-5 wrong-issue lines (placebo) − no hint: -17.3 [-28.4, -6.4], p = 0.0018, Holm 0.032
- adds_gold: hint: top-5 wrong-issue lines (placebo) − no hint: -3.1 [-6.6, +0.0], p = 0.0986, Holm 0.887
- valid: hint: top-5 wrong-issue lines (placebo) − no hint: -10.2 [-24.0, +3.1], p = 0.1586, Holm 1.000
- on_gold: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +13.3 [+3.1, +23.7], p = 0.0128, Holm 0.179
- near_gold: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +16.3 [+7.6, +25.3], p = 0.0004, Holm 0.009
- gold_unit: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +14.3 [+4.2, +24.0], p = 0.0046, Holm 0.074
- adds_gold: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +0.0 [-3.1, +3.0], p = 1.0000, Holm 1.000
- valid: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +10.2 [+1.0, +19.4], p = 0.0434, Holm 0.477
- on_gold: hint: gold lines (ceiling) − no hint: +12.2 [+1.1, +23.8], p = 0.0348, Holm 0.452
- near_gold: hint: gold lines (ceiling) − no hint: +18.4 [+7.4, +30.1], p = 0.0012, Holm 0.024
- gold_unit: hint: gold lines (ceiling) − no hint: +17.3 [+4.8, +30.2], p = 0.0076, Holm 0.114
- adds_gold: hint: gold lines (ceiling) − no hint: +1.0 [-2.1, +4.9], p = 0.7808, Holm 1.000
- valid: hint: gold lines (ceiling) − no hint: +11.2 [+0.0, +23.6], p = 0.0700, Holm 0.700

**Does the model follow the hint, or use it?** (H arm)

- hint contains a gold line (47 files): on_gold with hint 53 [38, 68], without hint 49 [33, 64]; edit touches a hinted line 60 [46, 74]
- hint contains no gold line (51 files): on_gold with hint 2 [0, 6], without hint 8 [2, 16]; edit touches a hinted line 31 [19, 46]
- hint: top-5 null-edit lines: hint contains a gold line in 48% of files; edit touches a hinted line in 45%
- hint: top-5 wrong-issue lines (placebo): hint contains a gold line in 7% of files; edit touches a hinted line in 9%
- hint: gold lines (ceiling): hint contains a gold line in 100% of files; edit touches a hinted line in 37%

On the same files the map alone: top-1 line is gold 21%, a gold line in the top 5 48%.

**Files the greedy rewrite would leave unchanged** (8 files): on_gold no hint 12 [0, 43]; hint: top-5 null-edit lines 0 [0, 0]; hint: top-5 wrong-issue lines (placebo) 0 [0, 0]; hint: gold lines (ceiling) 38 [10, 75]
