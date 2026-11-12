S line@10; issues from ../results/conf_ids.txt

| Model | files (issues) | all lines @10 | code lines only @10 | difference (points), p | all lines @1 | code only @1 | hazard on comment/docstring lines (median share) | median total hazard (nats) |
|---|---|---|---|---|---|---|---|---|
| 12B-4bit | 69 (58) | 41 [29, 52] | 57 [45, 68] | +15.9 [+7.0, +25.4], p = 0.0008 | 6 [1, 12] | 13 [6, 21] | 0.74 | 64.8 |

Comment/docstring lines are 30% of non-blank lines (mean over files); every gold line is such a line in 1% of files.

**By file length** (all lines -> code lines only; n files)

| Model | under 5,000 tokens | 5,000-11,000 tokens | over 11,000 tokens |
|---|---|---|---|
| 12B-4bit | 62 -> 75 (n = 40; share 0.70) | 11 -> 33 (n = 27; share 0.77) | 0 -> 0 (n = 2; share 0.83) |
