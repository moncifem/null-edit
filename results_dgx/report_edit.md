111 files, 95 issues; one greedy search/replace edit per file and arm; oracle file; nothing executed; a reply that hit the token cap is invalid (declared rule)

| Arm | valid | ambiguous | truncated | noop | on_gold | near_gold | gold_unit | adds_gold | on_hint | on_gold if valid | median tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|
| no hint | 89 [83, 94] | 1 [0, 3] | 8 [4, 14] | 10 [5, 16] | 40 [29, 50] | 48 [37, 58] | 56 [46, 66] | 11 [5, 17] | 0 [0, 0] | 44 [34, 56] | 189 |
| hint: top-5 null-edit lines | 90 [84, 95] | 0 [0, 0] | 5 [2, 10] | 7 [3, 12] | 44 [34, 54] | 53 [43, 63] | 59 [49, 68] | 10 [4, 16] | 75 [65, 83] | 49 [39, 59] | 186 |
| hint: top-5 wrong-issue lines (placebo) | 81 [74, 88] | 0 [0, 0] | 14 [8, 21] | 8 [4, 13] | 32 [22, 41] | 36 [27, 46] | 40 [30, 50] | 11 [5, 18] | 31 [22, 40] | 39 [28, 49] | 224 |
| hint: gold lines (ceiling) | 90 [84, 95] | 1 [0, 3] | 7 [3, 12] | 9 [4, 15] | 66 [57, 74] | 73 [65, 81] | 75 [67, 82] | 12 [6, 19] | 65 [56, 73] | 73 [64, 82] | 175 |

**Primary contrasts** (on_gold, percentage points, instance-clustered bootstrap, unadjusted p):

- hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +12.6 [+3.6, +21.6], p = 0.0070
- hint: top-5 null-edit lines − no hint: +4.5 [-2.7, +11.7], p = 0.2638

**Secondary contrasts** (Holm-adjusted over this list):

- near_gold: hint: top-5 null-edit lines − no hint: +5.4 [-2.9, +14.0], p = 0.2508, Holm 1.000
- gold_unit: hint: top-5 null-edit lines − no hint: +2.7 [-5.6, +10.8], p = 0.5744, Holm 1.000
- adds_gold: hint: top-5 null-edit lines − no hint: -0.9 [-5.6, +3.7], p = 0.8686, Holm 1.000
- valid: hint: top-5 null-edit lines − no hint: +0.9 [-5.9, +7.9], p = 0.9168, Holm 1.000
- near_gold: hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +17.1 [+7.9, +26.8], p = 0.0000, Holm 0.000
- gold_unit: hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +18.9 [+9.0, +29.1], p = 0.0004, Holm 0.008
- adds_gold: hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): -0.9 [-5.6, +3.8], p = 0.8490, Holm 1.000
- valid: hint: top-5 null-edit lines − hint: top-5 wrong-issue lines (placebo): +9.0 [+0.8, +17.6], p = 0.0482, Holm 0.627
- on_gold: hint: top-5 wrong-issue lines (placebo) − no hint: -8.1 [-16.2, +0.0], p = 0.0608, Holm 0.730
- near_gold: hint: top-5 wrong-issue lines (placebo) − no hint: -11.7 [-20.9, -2.8], p = 0.0094, Holm 0.132
- gold_unit: hint: top-5 wrong-issue lines (placebo) − no hint: -16.2 [-25.7, -6.8], p = 0.0022, Holm 0.035
- adds_gold: hint: top-5 wrong-issue lines (placebo) − no hint: +0.0 [-4.5, +4.4], p = 1.0000, Holm 1.000
- valid: hint: top-5 wrong-issue lines (placebo) − no hint: -8.1 [-16.7, +0.8], p = 0.0772, Holm 0.849
- on_gold: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +21.6 [+11.2, +32.2], p = 0.0000, Holm 0.000
- near_gold: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +19.8 [+9.0, +30.9], p = 0.0010, Holm 0.017
- gold_unit: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +16.2 [+5.9, +26.5], p = 0.0026, Holm 0.039
- adds_gold: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +1.8 [-2.6, +6.5], p = 0.5276, Holm 1.000
- valid: hint: gold lines (ceiling) − hint: top-5 null-edit lines: +0.0 [-7.9, +7.6], p = 1.0000, Holm 1.000
- on_gold: hint: gold lines (ceiling) − no hint: +26.1 [+15.7, +36.4], p = 0.0000, Holm 0.000
- near_gold: hint: gold lines (ceiling) − no hint: +25.2 [+15.1, +35.8], p = 0.0000, Holm 0.000
- gold_unit: hint: gold lines (ceiling) − no hint: +18.9 [+8.5, +29.6], p = 0.0008, Holm 0.014
- adds_gold: hint: gold lines (ceiling) − no hint: +0.9 [-3.6, +5.7], p = 0.8280, Holm 1.000
- valid: hint: gold lines (ceiling) − no hint: +0.9 [-6.4, +8.0], p = 0.9064, Holm 1.000

**Does the model follow the hint, or use it?** (H arm)

- hint contains a gold line (67 files): on_gold with hint 67 [55, 78], without hint 57 [44, 69]; edit touches a hinted line 87 [78, 94]
- hint contains no gold line (44 files): on_gold with hint 9 [2, 19], without hint 14 [4, 25]; edit touches a hinted line 57 [41, 72]
- hint: top-5 null-edit lines: hint contains a gold line in 60% of files; edit touches a hinted line in 75%
- hint: top-5 wrong-issue lines (placebo): hint contains a gold line in 10% of files; edit touches a hinted line in 31%
- hint: gold lines (ceiling): hint contains a gold line in 100% of files; edit touches a hinted line in 65%

On the same files the map alone: top-1 line is gold 36%, a gold line in the top 5 60%.

**Files the greedy rewrite would leave unchanged** (29 files): on_gold no hint 14 [3, 28]; hint: top-5 null-edit lines 24 [10, 40]; hint: top-5 wrong-issue lines (placebo) 24 [10, 40]; hint: gold lines (ceiling) 52 [34, 69]
