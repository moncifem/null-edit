# Replication report

Script: replication/replicate_lines.py (run as `python replicate_lines.py <run_dir>`; seed 0 for tie-breaks).

## Dev run (conflict_e4b_devR, 30 files) vs claimed
| metric | mine S | claimed S | mine H | claimed H | mine len | claimed len | mine random |
|---|---|---|---|---|---|---|---|
| hit@1 | 0.133 | 0.133 | 0.167 | 0.167 | 0.033 | - | 0.000 |
| hit@5 | 0.433 | 0.433 | 0.567 | 0.567 | 0.200 | - | 0.067 |
| hit@10 | 0.667 | 0.667 | 0.700 | 0.700 | 0.333 | 0.333 | 0.100 (claimed ~0.13; within noise at n=30) |
| median rank | 7 | 7 | 5 | 5 | 24 | - | 51.5 |

Verdict: S, H and line-length numbers match EXACTLY. Random baseline differs only by seed noise (3/30 vs ~4/30).

## Spec ambiguities / resolutions
- Pure-insertion block = maximal run of consecutive +/- lines with no "-" line; before = ptr-1, after = ptr (ptr = next original line). Insertion at hunk end uses ptr as well. Anchors beyond file end dropped.
- Anchor relocation only applied when token-less; removed lines that are token-less are dropped (no relocation per spec).
- Test-file filter: any dir component test/tests/testing, basename test_*, *_test.py, conftest.py, tests*. All 30+61 rows passed it.
- Ties broken by a random permutation key (np lexsort). Hits near ties (e.g. many equal scores) could shift by noise; none observed to matter for dev.
- Trailing "" line after final "\n" is token-less and excluded automatically.

## Anomalies
- django__django-13128 expressions.py: offsets are not contiguous (first token [0,6], last ends at len(text) but some gap/overlap exists between tokens). Does not change the result (gold ranks 8/4).
- n_tok matches len(offsets), lp_R, lp_RX in all rows; no NaN/inf; no positive lp_R; no missing files/gold-less files.
- lp_R is near zero (> -1e-3) for 95-100% of tokens in every file: expected for a copy task, so S/H are driven by the few non-copied tokens. (Not a bug, but the signal is sparse.)
- test run: 61 rows existed at run time (log had 73 lines incl. skips/at moment of read); all 61 evaluated.

## Held-out test run (61 files, still growing)
| score | hit@1 | hit@5 | hit@10 | median rank |
|---|---|---|---|---|
| S | 0.197 | 0.443 | 0.623 | 7 |
| H | 0.246 | 0.508 | 0.689 | 5 |
| length | 0.000 | 0.131 | 0.230 | 59 |
| random | 0.033 | 0.066 | 0.131 | 114 |

## Per-file ranks (dev run)
| iid | path | n_lines | n_gold | rank_S | rank_H | rank_len |
|---|---|---|---|---|---|---|
| astropy__astropy-12907 | astropy/modeling/separable.py | 255 | 1 | 42 | 229 | 12 |
| astropy__astropy-8707 | astropy/io/fits/card.py | 1078 | 2 | 3 | 3 | 515 |
| astropy__astropy-8707 | astropy/io/fits/header.py | 1786 | 11 | 4 | 3 | 22 |
| django__django-11790 | django/contrib/auth/forms.py | 374 | 1 | 4 | 4 | 1 |
| django__django-12308 | django/contrib/admin/utils.py | 469 | 2 | 1 | 1 | 26 |
| django__django-13128 | django/db/models/expressions.py | 1100 | 23 | 8 | 4 | 7 |
| django__django-13568 | django/contrib/auth/checks.py | 193 | 1 | 4 | 4 | 10 |
| django__django-14034 | django/forms/boundfield.py | 247 | 2 | 5 | 5 | 106 |
| django__django-15572 | django/template/autoreload.py | 43 | 2 | 2 | 2 | 2 |
| django__django-16145 | django/core/management/commands/runserver.py | 166 | 3 | 4 | 4 | 5 |
| django__django-16667 | django/forms/widgets.py | 980 | 2 | 6 | 5 | 2 |
| matplotlib__matplotlib-22719 | lib/matplotlib/category.py | 205 | 2 | 7 | 6 | 116 |
| matplotlib__matplotlib-25775 | lib/matplotlib/backends/backend_agg.py | 461 | 1 | 9 | 5 | 132 |
| matplotlib__matplotlib-25775 | lib/matplotlib/backends/backend_cairo.py | 419 | 6 | 3 | 2 | 44 |
| matplotlib__matplotlib-25775 | lib/matplotlib/text.py | 1656 | 16 | 69 | 33 | 83 |
| pydata__xarray-3151 | xarray/core/combine.py | 592 | 8 | 10 | 7 | 279 |
| pylint-dev__pylint-4551 | pylint/pyreverse/diagrams.py | 218 | 1 | 182 | 110 | 63 |
| pylint-dev__pylint-4551 | pylint/pyreverse/inspector.py | 301 | 22 | 2 | 1 | 16 |
| pylint-dev__pylint-4551 | pylint/pyreverse/utils.py | 172 | 3 | 1 | 1 | 83 |
| pylint-dev__pylint-4551 | pylint/pyreverse/writer.py | 188 | 5 | 13 | 12 | 12 |
| pytest-dev__pytest-7205 | src/_pytest/setuponly.py | 65 | 3 | 1 | 1 | 6 |
| scikit-learn__scikit-learn-13328 | sklearn/linear_model/huber.py | 250 | 1 | 11 | 10 | 27 |
| scikit-learn__scikit-learn-9288 | sklearn/cluster/k_means_.py | 1394 | 5 | 27 | 19 | 3 |
| sphinx-doc__sphinx-8120 | sphinx/application.py | 970 | 2 | 13 | 12 | 13 |
| sphinx-doc__sphinx-8120 | sphinx/locale/__init__.py | 203 | 1 | 40 | 39 | 46 |
| sphinx-doc__sphinx-9602 | sphinx/domains/python.py | 1197 | 4 | 7 | 5 | 260 |
| sympy__sympy-13877 | sympy/utilities/randtest.py | 151 | 4 | 1 | 1 | 4 |
| sympy__sympy-17318 | sympy/simplify/radsimp.py | 911 | 3 | 119 | 151 | 265 |
| sympy__sympy-17318 | sympy/simplify/sqrtdenest.py | 561 | 1 | 92 | 274 | 132 |
| sympy__sympy-21379 | sympy/core/mod.py | 204 | 6 | 10 | 9 | 7 |


## Per-file ranks (test run)
| iid | path | n_lines | n_gold | rank_S | rank_H | rank_len |
|---|---|---|---|---|---|---|
| django__django-13810 | django/core/handlers/base.py | 310 | 4 | 13 | 8 | 136 |
| django__django-10097 | django/core/validators.py | 446 | 1 | 4 | 4 | 32 |
| pytest-dev__pytest-7982 | src/_pytest/pathlib.py | 493 | 1 | 5 | 3 | 35 |
| django__django-13195 | django/contrib/messages/storage/cookie.py | 161 | 1 | 1 | 1 | 4 |
| django__django-13195 | django/contrib/sessions/middleware.py | 73 | 2 | 1 | 1 | 35 |
| django__django-13195 | django/http/response.py | 450 | 5 | 5 | 4 | 10 |
| sympy__sympy-14531 | sympy/printing/str.py | 661 | 17 | 10 | 10 | 8 |
| django__django-15957 | django/db/models/fields/related_descriptors.py | 1214 | 8 | 28 | 22 | 97 |
| pylint-dev__pylint-4661 | pylint/config/__init__.py | 103 | 3 | 3 | 3 | 23 |
| sphinx-doc__sphinx-9367 | sphinx/pycode/ast.py | 189 | 5 | 1 | 1 | 13 |
| django__django-16819 | django/db/migrations/operations/models.py | 964 | 2 | 7 | 7 | 36 |
| sympy__sympy-24661 | sympy/parsing/sympy_parser.py | 1017 | 2 | 112 | 67 | 440 |
| django__django-14765 | django/db/migrations/state.py | 737 | 3 | 1 | 1 | 15 |
| sphinx-doc__sphinx-7985 | sphinx/builders/linkcheck.py | 320 | 4 | 1 | 1 | 13 |
| scikit-learn__scikit-learn-25973 | sklearn/feature_selection/_sequential.py | 270 | 7 | 19 | 17 | 4 |
| sympy__sympy-15017 | sympy/tensor/array/dense_ndim_array.py | 155 | 1 | 1 | 1 | 5 |
| django__django-13363 | django/db/models/functions/datetime.py | 252 | 2 | 3 | 3 | 25 |
| django__django-14053 | django/contrib/staticfiles/storage.py | 374 | 6 | 8 | 7 | 29 |
| sphinx-doc__sphinx-7590 | sphinx/util/cfamily.py | 357 | 5 | 36 | 23 | 8 |
| django__django-11119 | django/template/engine.py | 159 | 1 | 1 | 1 | 67 |
| sphinx-doc__sphinx-11510 | sphinx/directives/other.py | 348 | 6 | 3 | 1 | 39 |
| django__django-15569 | django/db/models/query_utils.py | 290 | 2 | 1 | 1 | 9 |
| sphinx-doc__sphinx-9320 | sphinx/cmd/quickstart.py | 506 | 3 | 1 | 1 | 228 |
| pytest-dev__pytest-7571 | src/_pytest/logging.py | 671 | 6 | 43 | 32 | 49 |
| django__django-16527 | django/contrib/admin/templatetags/admin_modify.py | 133 | 1 | 2 | 2 | 77 |
| sympy__sympy-13798 | sympy/printing/latex.py | 1793 | 4 | 4 | 3 | 351 |
| sympy__sympy-16886 | sympy/crypto/crypto.py | 1931 | 1 | 413 | 128 | 693 |
| django__django-15277 | django/db/models/fields/__init__.py | 2188 | 1 | 2 | 2 | 175 |
| sympy__sympy-13878 | sympy/stats/crv_types.py | 1940 | 76 | 6 | 2 | 5 |
| django__django-13417 | django/db/models/query.py | 1757 | 1 | 11 | 10 | 138 |
| django__django-13023 | django/db/models/fields/__init__.py | 2113 | 1 | 45 | 26 | 1362 |
| django__django-11095 | django/contrib/admin/options.py | 1902 | 3 | 8 | 6 | 226 |
| django__django-11265 | django/db/models/sql/query.py | 2085 | 5 | 151 | 70 | 29 |
| django__django-16100 | django/contrib/admin/options.py | 2227 | 8 | 8 | 5 | 200 |
| sympy__sympy-12489 | sympy/combinatorics/permutations.py | 2294 | 43 | 6 | 1 | 15 |
| sympy__sympy-21930 | sympy/physics/secondquant.py | 2472 | 3 | 39 | 18 | 286 |
| matplotlib__matplotlib-24970 | lib/matplotlib/colors.py | 2243 | 10 | 146 | 49 | 291 |
| sphinx-doc__sphinx-8269 | sphinx/builders/linkcheck.py | 332 | 2 | 11 | 9 | 83 |
| django__django-14771 | django/utils/autoreload.py | 555 | 2 | 24 | 16 | 9 |
| django__django-12143 | django/contrib/admin/options.py | 1904 | 1 | 4 | 1 | 5 |
| django__django-13512 | django/contrib/admin/utils.py | 474 | 3 | 2 | 2 | 168 |
| django__django-13512 | django/forms/fields.py | 1086 | 1 | 4 | 4 | 237 |
| django__django-16938 | django/core/serializers/python.py | 159 | 1 | 2 | 2 | 28 |
| django__django-16938 | django/core/serializers/xml_serializer.py | 424 | 1 | 8 | 6 | 67 |
| pydata__xarray-4356 | xarray/core/nanops.py | 146 | 5 | 2 | 2 | 8 |
| sympy__sympy-13480 | sympy/functions/elementary/hyperbolic.py | 1126 | 1 | 17 | 10 | 464 |
| psf__requests-1142 | requests/models.py | 513 | 3 | 1 | 1 | 59 |
| django__django-16429 | django/utils/timesince.py | 114 | 2 | 16 | 14 | 95 |
| pytest-dev__pytest-5809 | src/_pytest/pastebin.py | 95 | 5 | 1 | 1 | 2 |
| django__django-13279 | django/contrib/sessions/backends/base.py | 315 | 4 | 3 | 3 | 68 |
| django__django-15161 | django/db/models/expressions.py | 1212 | 12 | 50 | 55 | 124 |
| django__django-15930 | django/db/models/expressions.py | 1511 | 2 | 425 | 225 | 159 |
| django__django-11276 | django/utils/html.py | 324 | 21 | 1 | 1 | 2 |
| sphinx-doc__sphinx-10323 | sphinx/directives/code.py | 391 | 4 | 66 | 52 | 265 |
| django__django-15098 | django/utils/translation/trans_real.py | 482 | 1 | 24 | 22 | 4 |
| pylint-dev__pylint-6386 | pylint/config/argument.py | 382 | 3 | 48 | 142 | 102 |
| pylint-dev__pylint-6386 | pylint/config/arguments_manager.py | 678 | 2 | 309 | 507 | 437 |
| pylint-dev__pylint-6386 | pylint/config/utils.py | 213 | 5 | 7 | 6 | 17 |
| pylint-dev__pylint-6386 | pylint/lint/base_options.py | 560 | 4 | 10 | 7 | 115 |
| pydata__xarray-4687 | xarray/core/computation.py | 1681 | 7 | 9 | 5 | 393 |
| sympy__sympy-12481 | sympy/combinatorics/permutations.py | 2298 | 6 | 15 | 26 | 88 |


(rank_len column = line-token-length baseline.)
