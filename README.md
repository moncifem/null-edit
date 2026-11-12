# The Null Edit

Reading where a small model wants to change code, without letting it write.

Code, protocol and raw results for a submission to the Kaggle *Gemma 4 Developer Agent — Paper
Track*. No fine-tuning, no test execution, no network access at inference time.

## Two hardware arms

The work was done on two machines and the paper keeps them apart.

| Arm | Machine | Software | Weights | What was run there |
|-----|---------|----------|---------|--------------------|
| **MAC** | Apple M5 Max laptop, 64 GB | MLX 0.32.4, mlx-lm 0.32.2 | `mlx-community/gemma-4-*-it-4bit` | Development set (25 issues), every design choice, the failed "blind" formulation, an interim look at the first 88 held-out issues |
| **DGX** | NVIDIA DGX Spark (GB10, 121 GB) | PyTorch 2.14.1, transformers 5.14.0.dev0 | official `google/gemma-4-{E2B,E4B,12B,26B-A4B,31B}-it`, bf16 | Every held-out number of the paper: 250 SWE-bench Verified issues, 150 post-cutoff SWE-bench-Live issues, controls, all five model sizes, generated-answer baselines, the edit experiment |

`SCORER_BACKEND=torch` selects the PyTorch scorer (`src/scorer_torch.py`); otherwise the MLX scorer
(`src/scorer_mlx.py`) is used. `results/` holds the MAC arm's outputs, `results_dgx/` the DGX arm's.
The MAC arm's 4-bit checkpoint was also de-quantized into the PyTorch model (`src/make_q4_model.py`)
to separate the effect of quantization from the effect of the software stack.

## What is here

| Path | Content |
|------|---------|
| `PAPER.md` | The paper |
| `HYPOTHESES.md` | Hypotheses, the pre-registered held-out analysis, and their status |
| `EXPERIMENTS.md` | Protocols, configurations and result tables |
| `REVIEW.md` | Adversarial reviews and how each point was handled |
| `RESEARCH_LOG.md` | Chronological log, including the failed first formulation |
| `LITERATURE.md` | Verified references and novelty comparison |
| `src/` | All code (see below) |
| `results/`, `results_dgx/` | Per-token log-probabilities (`conflict_*/*.npz`), generated answers, analysis JSON and reports |
| `replication/` | Independent re-derivation of the dev-set numbers from the raw data |
| `notes/` | Reports of the exploratory, prior-art and review subagents |

## Reproduce the tables from the saved logs (CPU, minutes)

```bash
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install -r requirements.txt
# data: SWE-bench Verified / SWE-bench-Live metadata and a clone of each repository under data/repos/<owner>_<name>
cd src && NULLEDIT_RESULTS=../results_dgx zsh analyze_all.sh
```

## Re-run the scoring (GPU)

```bash
cd src
export SCORER_BACKEND=torch           # leave unset on Apple silicon (MLX)
M=../data/models/gemma-4-E4B-it       # hf download google/gemma-4-E4B-it --local-dir $M
# null-edit teacher forcing: R = correct issue, RX = wrong issue
python run_conflict.py --model $M --tag e4b_test --instances ../results/test_ids.txt --limit 250 \
    --frames R,RX --max-file-tokens 32000 --sleep 0
# the same model asked to name the location (line ranges; quoted lines)
python run_generative.py --model $M --tag e4b_test --instances ../results/test_ids.txt --limit 250 --sleep 0
python run_generative.py --mode quote --model $M --tag e4b_test_quote --instances ../results/test_ids.txt --limit 250 --sleep 0
# tables with instance-clustered bootstrap CIs
python analyze_conflict.py --tag e4b_test --ids ../results/test_ids.txt --gen e4b_test --gen2 e4b_test_quote --json ../results/an_e4b_test.json
python report.py ../results/an_e4b_test.json
```

`src/queue_dgx.txt` lists every DGX run of the paper as `name | command`, in the order executed
(`src/runner.sh` executes such a list one job at a time). `src/queue_b.sh` is the MAC arm's list;
there `THROTTLE=1.5` kept the laptop GPU ~40% busy — it changes wall-clock time only.

## Code map

| File | Role |
|------|------|
| `scorer.py`, `scorer_mlx.py`, `scorer_torch.py` | Teacher-forced per-token log-probabilities with character offsets |
| `run_conflict.py` | Prompt frames and scoring loop (R, RX, RB, R0; earlier "blind" frames U, B, F, X) |
| `run_generative.py` | Generated-answer baselines (same model, same input): line ranges, quoted lines |
| `analyze_conflict.py`, `report.py`, `extra_stats.py` | Labels, ranking, baselines, bootstrap tables, subsets |
| `merge_frames.py`, `scaling.py` | Controls on common files; model-size table |
| `make_q4_model.py` | MLX 4-bit checkpoint → de-quantized PyTorch checkpoint |
| `context_budget.py` | How much of a file must be shown for the edit to be in view |
| `make_hints.py`, `run_edit.py`, `analyze_edit.py` | The model writes one edit, with and without the map as a hint |
| `build_file_cands.py`, `analyze_filelevel.py` | File-level experiment with BM25 hard negatives |
| `fetch_patches.py`, `run_fixedpoint.py`, `analyze_fixedpoint.py` | Patch checking on public leaderboard patches |
| `calibrate_sampling.py` | First-edit identity checked against real sampling |
| `figures.py`, `analyze_all.sh` | Figures; one script that regenerates every report |

## Data sources and licences

SWE-bench Verified (princeton-nlp/SWE-bench_Verified), SWE-bench-Live (SWE-bench-Live/SWE-bench-Live),
public leaderboard predictions listed in github.com/SWE-bench/experiments, Gemma 4 (Apache 2.0).
Code in this repository: Apache 2.0.
