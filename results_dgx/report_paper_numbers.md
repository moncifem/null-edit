## Held-out Verified, E4B (DGX arm)

- gold source files of the first 250 held-out issues: 317; scored: 300; analysed: 300
- ranking lines by first-edit probability P(tau in line): line hit@10 60.3
- files where every token has p >= 0.5: 84 files, 73 issues; median P(no edit) 0.32; files with min p in [0.5, 0.6): 18
- line-range answer lists a gold line anywhere: 62.0% of 300 files
- quoted answer, line hit@10: strict all-occurrences mapping 36.0, aligned mapping 44.7

## 4-bit weights (MLX checkpoint de-quantized into the DGX code)

- lrank_drop_R-RX_pos@10: bf16 75.5 vs 4-bit on DGX 63.3; difference +12.2 [+5.0, +20.2] (98 files, 83 issues)
- urank_drop_R-RX_pos|sum@1: bf16 63.3 vs 4-bit on DGX 41.8; difference +21.4 [+13.7, +29.7] (98 files, 83 issues)
- 4-bit on DGX, H − BM25 line@10: +25.5 [+14.1, +36.4]; function@1 H 41.8 vs BM25 42.9
- lrank_drop_R-RX_pos@10: 4-bit on DGX 63.7 vs 4-bit on MAC 64.8; difference -1.1 [-3.5, +0.0] (91 files, 76 issues)
- urank_drop_R-RX_pos|sum@1: 4-bit on DGX 39.6 vs 4-bit on MAC 44.0; difference -4.4 [-8.6, -1.1] (91 files, 76 issues)

## SWE-bench-Live, post-cutoff

- 278 files, 145 issues, 91 repositories, 89 of them not in SWE-bench Verified (shared: matplotlib/matplotlib, pylint-dev/pylint)
- files where every token has p >= 0.5: 76; line hit@10 S 50.0, H 52.6, BM25 39.5

## Label-free check: S line hit@10 by the file's total hazard (threshold 50 nats, post hoc)

111 common files (31B: the 74 of them it could score)

| Model | total hazard ≤ 50 nats | > 50 nats |
|---|---|---|
| E2B | 60% (57/95) | 12% (2/16) |
| E4B | 74% (82/111) | – (0 files) |
| 12B | 77% (54/70) | 29% (12/41) |
| 26B-A4B | 82% (37/45) | 42% (28/66) |
| 31B | 92% (45/49) | 56% (14/25) |
