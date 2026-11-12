---
license: apache-2.0
language:
- en
pretty_name: "The Null Edit: per-token edit hazards of Gemma 4 on SWE-bench files"
size_categories:
- 1K<n<10K
task_categories:
- text-generation
tags:
- code
- gemma
- gemma-4
- swe-bench
- swe-bench-verified
- swe-bench-live
- fault-localization
- issue-localization
- teacher-forcing
- log-probabilities
- coding-agents
configs:
- config_name: per_file
  default: true
  data_files:
  - split: train
    path: data/per_file_metrics.parquet
---

# The Null Edit — data

**Reading where a small model wants to change code, without letting it write.**

This dataset holds everything measured for the paper *The Null Edit*: the per-token log-probabilities of
**Gemma 4** (E2B, E4B, 12B, 26B A4B, 31B) teacher-forced on unchanged source files of SWE-bench issues, the
model's generated answers used as baselines, and the per-file metrics behind every table and figure.

- **Code, pre-registration, research log, reviews:** https://github.com/moncifem/null-edit
- **Paper:** Kaggle writeup, *Google – The Gemma 4 Developer Agent Paper Track* (text in the repository: `PAPER.md`)

![Null-edit teacher forcing](https://huggingface.co/datasets/moncefem/null-edit/resolve/main/figures/fig0_method.png)

## The idea in three lines

1. Give the model an issue and a source file and ask it to *rewrite the file so that the issue is fixed*.
2. Do not let it write. Feed the **unchanged file** back as its own answer and record, at every token, the
   probability `p_t` of writing what is already there. One forward pass, nothing generated.
3. Per line, `S_i = −Σ log p_t` is the **edit hazard**: how strongly the model wants to depart from that line.
   The product form gives the exact distribution of where a sampled rewrite would first differ from the file.

Running the same prompt with a *wrong* issue and keeping the excess gives the issue-specific hazard `H_i`.

## What we found

| | Line of the human fix in the top 10 lines | Right function ranked first |
|---|---|---|
| **Null-edit map, H (2 passes)** | **69%** | 50% |
| Null-edit map, S (1 pass) | 64% | 44% |
| Same model asked for line ranges | 51% | **60%** |
| BM25 | 38% | 38% |
| Map under a wrong issue (control) | 16% | 19% |

Gemma 4 E4B, bf16, 300 held-out files (240 issues) of SWE-bench Verified; no fine-tuning, tests or tools.

![Hit rate by number of lines inspected](https://huggingface.co/datasets/moncefem/null-edit/resolve/main/figures/fig2_hitk.png)

- On issues created **after the model's training cutoff** (SWE-bench-Live, 278 files) the map reaches 68% against 43% for BM25.
- The map still localizes the fix in files that greedy rewriting would leave unchanged.
- **Larger models are not better out of the box:** 12B and 26B A4B spend their hazard on comments and docstrings.
  Ranking code lines only repairs this (+27 points on fresh issues, pre-registered).
- **The map's lead over asking is a small-model effect.** At 12B and 26B A4B, asking is about as good as the
  repaired map and names the right function first far more often.
- Community 4-bit weights score 12 points below bf16 on the same files.
- Two negative results are included: feeding the map back as a hint does not reliably improve the model's own edit,
  and without the file in context, likelihood shifts are no better than BM25.

![Asking against the map, by model size](https://huggingface.co/datasets/moncefem/null-edit/resolve/main/figures/fig4_asked.png)

## Quick start

```python
from datasets import load_dataset

rows = load_dataset("moncefem/null-edit", "per_file", split="train").to_pandas()
e4b = rows[(rows.arm == "dgx_bf16") & (rows.run == "e4b_test")]
print((e4b.lrank_drop_R_RX_pos <= 10).mean())   # 0.69: H puts a gold line in its top ten
print((e4b.lrank_gen <= 10).mean())             # 0.51: the model asked for line ranges
```

Per-token log-probabilities of one file:

```python
import numpy as np
from huggingface_hub import hf_hub_download

f = hf_hub_download("moncefem/null-edit", "dgx_bf16/conflict_e4b_test/astropy__astropy-13398__303601b1.npz",
                    repo_type="dataset")
z = np.load(f)
z["offsets"]   # (n_tokens, 2) character span of each token in the source file
z["lp_R"]      # log p_t under the right issue
z["lp_RX"]     # log p_t under a wrong issue (same repository, disjoint files)
```

The source files themselves are not redistributed: each is the file at the instance's `base_commit` in its
upstream repository. `src/common.py` in the GitHub repository fetches it, and `src/analyze_conflict.py` turns
offsets and log-probabilities into per-line hazards, ranks and the metrics below.

## Contents

| Path | What it is |
|---|---|
| `data/per_file_metrics.parquet` | One row per (arm, run, file): 2,299 rows. Ranks of the best gold line / function under every score and baseline, token counts, total hazard. Loaded by the `per_file` config. |
| `dgx_bf16/` | **DGX arm**: NVIDIA DGX Spark, PyTorch/transformers, official bf16 weights. Every held-out number of the paper unless marked MAC. |
| `mac_4bit/` | **MAC arm**: Apple M5 Max laptop, MLX, community 4-bit weights. Development set, design choices, and results marked MAC. |
| `*/conflict_<run>/*.npz` | Per-token log-probabilities of one scored file (`offsets`, `lp_R`, and where run `lp_RX`, `lp_RB`, `lp_R0`). |
| `*/conflict_<run>/log.jsonl` | Index of the run: instance id, file path, token count, the wrong issue used, timings. |
| `*/gen_<run>/gen.jsonl` | The model's generated answers (line ranges; `_quote`: quoted lines) used as the asking baseline. |
| `*/edit_<run>/gen.jsonl` | Search/replace edits written with no hint, the map's top-5 lines, wrong-issue lines, or the gold lines. |
| `*/noprefill_*/gen.jsonl` | Replies without the prefilled code fence, on the files greedy rewriting leaves unchanged. |
| `*/an_<run>.json` | Per-file analysis rows and summary for one run (source of the parquet table). |
| `*/report_*.md`, `scaling.md` | The generated reports every number in the paper is taken from. |
| `*/test_ids.txt`, `conf_ids.txt`, `live_ids.txt` | Instance lists: held-out order, pre-registered confirmation set, post-cutoff set. |
| `dgx_bf16/runner.progress` | Start, end and exit status of every DGX run. |
| `figures/` | The paper's figures. |

### Runs

| Run | Model | Data | Files |
|---|---|---|---|
| `e4b_test` | E4B | SWE-bench Verified, held-out | 300 |
| `e4b_live` | E4B | SWE-bench-Live, issues created on or after 2025-03-01 | 278 |
| `e4b_ctrl` | E4B | controls: copy instruction (`RB`), no issue (`R0`) | 111 |
| `e4b_q4_test` | E4B, community 4-bit weights run through the DGX code | held-out | 98 |
| `e2b_test`, `g12b_test`, `g26b_test` | E2B, 12B, 26B A4B | held-out issues 1–100 | 111 each |
| `g31b_test` | 31B (files up to 11,000 tokens: memory limit) | held-out issues 1–100 | 74 |
| `g12b_conf`, `g26b_conf` | 12B, 26B A4B | pre-registered confirmation, issues 101–200 | 113 each |
| `e4b_dev` | E4B | development set (every 20th instance) | 33 |

Frames: `R` right issue + fix instruction (the probe); `RX` wrong issue; `RB` right issue + "print the file
unchanged"; `R0` no issue.

### Main columns of `per_file`

| Column | Meaning |
|---|---|
| `arm`, `run`, `iid`, `path`, `repo` | Which machine/weights, which run, SWE-bench instance, file, repository |
| `n_tok`, `n_lines`, `n_units` | File size in tokens, lines, and functions |
| `lrank_surp_R_sum` | Rank of the best-ranked gold line under the one-pass map **S** (1 = top) |
| `lrank_drop_R_RX_pos` | Same under the issue-specific map **H** |
| `lrank_surp_RX_sum` | Same under the wrong-issue control |
| `lrank_gen`, `lrank_gen2` | Same for the generated answers (line ranges; quoted lines) |
| `lrank_bm25` | Same for BM25 between issue and line |
| `urank_*` | The same ranks at function level |
| `total_surp_R_sum` | File total `S = −log P(no edit)` in nats |
| `min_p_R` | Smallest token probability in the file; ≥ 0.5 means greedy rewriting reproduces the file |

`hit@k` in the paper is the share of files with rank ≤ k; intervals use 10,000 instance-clustered bootstrap resamples.

## Limits you should know

- **Oracle file.** Scored files are the ones the human patch touches; this is line and function localization inside
  a known file, not repository-level retrieval, and no test is executed.
- **Memorization.** SWE-bench Verified predates the model. The post-cutoff set supports a within-set comparison,
  not a proof of no leakage.
- **Labels.** A human patch is one valid fix among several.
- **Python only**, files up to 32k tokens (31B: 11,000). One prompt, designed on E4B, with a prefilled code fence.
- **Two arms are not interchangeable:** 4-bit and bf16 weights differ by 12 points on the same files.
- The 31B asking baseline and the 31B confirmation run did not complete (memory); they are absent, not zero.
- Ten early DGX command lines were not saved; the repository's run list marks them rather than reconstructing them.

## Provenance and licence

Derived from [SWE-bench Verified](https://www.swebench.com/verified.html) (Jimenez et al., 2024) and
[SWE-bench-Live](https://arxiv.org/abs/2505.23419) (Zhang et al., 2025); instance ids and file paths refer to those
benchmarks, and generated answers may quote short fragments of the upstream source files, which remain under their
own licences. Models: Google Gemma 4, used under the Gemma terms. The measurements, tables and figures in this
dataset are released under Apache 2.0.

## Citation

```bibtex
@misc{nulledit2026,
  title  = {The Null Edit: Reading where a small model wants to change code, without letting it write},
  year   = {2026},
  note   = {Kaggle writeup, Google -- The Gemma 4 Developer Agent Paper Track},
  howpublished = {\url{https://github.com/moncifem/null-edit}}
}
```
