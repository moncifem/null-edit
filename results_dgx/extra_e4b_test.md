| Subset | files | H line@10 | S line@10 | BM25 line@10 | H func@1 | BM25 func@1 |
|---|---|---|---|---|---|---|
| all | 300 | 69 | 64 | 38 | 50 | 38 |
| file ≤ 20k tokens (pre-registered cap) | 246 | 71 | 66 | 39 | 54 | 40 |
| file > 20k tokens | 54 | 59 | 54 | 33 | 35 | 31 |
| single-file instances | 209 | 71 | 67 | 32 | 56 | 37 |
| patch only adds lines (pure insertion) | 66 | 55 | 47 | 18 | 47 | 26 |
| patch modifies/removes lines | 234 | 73 | 68 | 44 | 51 | 42 |
| 1–2 gold lines | 156 | 64 | 57 | 34 | 47 | 32 |
| ≥ 6 gold lines | 65 | 77 | 77 | 49 | 55 | 51 |
| django/django | 130 | 72 | 68 | 42 | 56 | 41 |
| sympy/sympy | 63 | 65 | 56 | 44 | 40 | 40 |
| sphinx-doc/sphinx | 27 | 63 | 59 | 26 | 44 | 33 |
| pylint-dev/pylint | 15 | 67 | 60 | 33 | 47 | 33 |
| matplotlib/matplotlib | 13 | 46 | 31 | 23 | 23 | 23 |
| astropy/astropy | 13 | 77 | 77 | 54 | 54 | 46 |
| scikit-learn/scikit-learn | 12 | 75 | 67 | 33 | 75 | 50 |
| pytest-dev/pytest | 10 | 80 | 80 | 30 | 60 | 50 |
| pydata/xarray | 9 | 78 | 67 | 22 | 44 | 22 |
| repo macro-average (repos with ≥5 files) | – | 69 | 63 | 34 | 49 | 38 |

Paired comparison on 91 common files (76 instances): this arm vs other arm
- H line hit@10: 75.8 vs 64.8  (diff +11.0 [+3.5, +19.1], p = 0.007)
- S line hit@10: 74.7 vs 59.3  (diff +15.4 [+6.9, +24.7], p = 0.001)
- H line hit@1: 39.6 vs 23.1  (diff +16.5 [+6.4, +27.1], p = 0.000)
- H function hit@1: 62.6 vs 44.0  (diff +18.7 [+10.4, +28.0], p = 0.000)
