300 files, window +-5 lines around each of the top-k lines

| Ranking | all gold in view, k=1 | all gold in view, k=3 | all gold in view, k=5 | all gold in view, k=10 | any gold in view, k=5 | share of file shown, k=5 |
|---|---|---|---|---|---|---|
| ask, then H | 28 [23, 33] | 42 [35, 48] | 45 [39, 51] | 50 [44, 56] | 72 | 7.7% |
| H | 23 [18, 29] | 38 [32, 43] | 45 [39, 52] | 55 [49, 61] | 73 | 9.3% |
| S | 20 [16, 25] | 37 [31, 42] | 44 [38, 50] | 53 [46, 59] | 70 | 9.6% |
| generated answer (ranges) | 24 [19, 29] | 29 [24, 35] | 34 [28, 39] | 38 [31, 44] | 60 | 4.6% |
| generated answer | 14 [10, 18] | 19 [14, 24] | 22 [17, 27] | 31 [25, 37] | 47 | 4.1% |
| BM25 | 10 [5, 17] | 21 [14, 29] | 26 [19, 35] | 35 [27, 45] | 49 | 10.8% |
| wrong issue | 3 [1, 5] | 6 [4, 9] | 8 [5, 11] | 15 [11, 19] | 25 | 11.2% |
| random | 2 [0, 3] | 3 [1, 6] | 7 [4, 10] | 14 [10, 18] | 22 | 12.7% |

Budget-matched: windows opened in ranking order until at most the given share of the file is shown (at least one window)

| Ranking | all gold in view, 5% of file | all gold in view, 10% of file | all gold in view, 20% of file | any gold, 5% | any gold, 10% | any gold, 20% |
|---|---|---|---|---|---|---|
| ask, then H | 44 [38, 49] | 56 [50, 62] | 67 [60, 73] | 71 [66, 77] | 79 [74, 84] | 88 [83, 92] |
| H | 40 [34, 46] | 53 [47, 60] | 67 [60, 73] | 66 [60, 72] | 80 [75, 86] | 90 [87, 94] |
| S | 36 [31, 42] | 48 [42, 54] | 61 [55, 67] | 60 [54, 66] | 76 [71, 81] | 87 [83, 91] |
| generated answer (ranges) | 38 [33, 44] | 44 [38, 50] | 46 [40, 52] | 64 [58, 69] | 70 [64, 75] | 72 [67, 78] |
| generated answer | 29 [23, 34] | 32 [26, 38] | 34 [28, 40] | 52 [46, 58] | 54 [48, 60] | 57 [50, 63] |
| BM25 | 23 [15, 33] | 30 [22, 39] | 37 [29, 45] | 40 [32, 49] | 53 [46, 61] | 64 [58, 71] |
| wrong issue | 5 [3, 7] | 7 [5, 10] | 14 [10, 18] | 14 [11, 18] | 24 [20, 29] | 40 [35, 46] |
| random | 3 [1, 5] | 4 [2, 7] | 11 [7, 14] | 10 [7, 14] | 17 [13, 21] | 34 [29, 40] |

Paired differences, any gold line in view (percentage points, instance-clustered bootstrap):

- 5% of file: ask, then H − H: +5.3 [+1.0, +9.8], p = 0.0230
- 10% of file: ask, then H − H: -1.0 [-4.9, +2.9], p = 0.6612
- 20% of file: ask, then H − H: -2.7 [-5.8, +0.3], p = 0.0972
- 5% of file: ask, then H − generated answer (ranges): +7.7 [+3.6, +11.7], p = 0.0002
- 10% of file: ask, then H − generated answer (ranges): +9.7 [+6.0, +13.5], p = 0.0000
- 20% of file: ask, then H − generated answer (ranges): +15.3 [+11.4, +19.4], p = 0.0000
- 5% of file: H − generated answer (ranges): +2.3 [-3.4, +7.8], p = 0.4512
- 10% of file: H − generated answer (ranges): +10.7 [+5.9, +15.8], p = 0.0000
- 20% of file: H − generated answer (ranges): +18.0 [+13.4, +22.8], p = 0.0000
- 5% of file: H − BM25: +25.7 [+17.5, +34.3], p = 0.0000
- 10% of file: H − BM25: +27.3 [+20.1, +35.1], p = 0.0000
- 20% of file: H − BM25: +26.0 [+20.1, +32.4], p = 0.0000

median file: 686 lines; 10% = 69 lines
