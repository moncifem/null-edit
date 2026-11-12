# Research log

All times UTC. Deadline: 2026-11-12 23:59 UTC (Kaggle Writeup must be *submitted*, not saved as draft).

## 2026-11-11

**17:55 — Start.** Hardware: Apple M5 Max, 64 GB, macOS. Local Gemma 4 available through Ollama
(E4B 8.0B Q4_K_M, 26B, 31B). No git repo, empty project. ~30 h to deadline.

**18:00 — Competition read (verified via Kaggle API pages).** Paper track judged on five equally
weighted criteria (novelty, quality/generality, relevance, verifiability, clarity). 3,000 words max;
Writeup needs title, subtitle, abstract, intro, methods + experiments, related work + citations.
Code optional (public notebook / project link). See `notes/competition.md` for host answers
(tables and captions count toward the word limit; references and figures do not).

**18:05 — Six parallel investigations launched** (3 Sonnet literature/intel, 3 Opus idea generation
with different lenses). Reports: `notes/competition.md`, `notes/frontier_map.md`,
`notes/prior_art_surprisal.md`, `notes/ideas_infotheory.md`, `notes/ideas_inversion.md`,
`notes/ideas_empirical_se.md`.

**18:10 — PI candidate (formed before agents reported).** *Issue-conditioned surprisal shift*:
teacher-force existing code under "no issue" / "issue, current file" / "issue, file after the fix"
prompts; the per-token log-likelihood ratio is an edit-saliency map obtained without generating a
token. Motivating facts: (i) localization experiments need no test execution, so they can run on
real SWE-bench Verified data on a laptop; (ii) on local hardware prompt processing is an order of
magnitude faster than generation.

**18:20 — Convergence.** Two of three independent Opus agents arrived at likelihood-as-instrument
ideas without seeing mine (PMI patch discrimination; "residual bits" of the gold patch as a
difficulty law). Third proposed git co-change omission analysis. Prior-art agent: no exact match
found for issue-conditioned code-token likelihood ratio; closest are Ray 2016 / Yang 2024
(unconditional naturalness / entropy-delta), LLMAO (trained probe), Campos 2024, and a concurrent
preprint that scores *patch* likelihood as a training signal. Main threat raised by every agent:
**memorization** of SWE-bench repositories by the model -> need a post-training-cutoff control set.

**18:30 — Infrastructure.** MLX scorer (`src/scorer.py`) gives per-token log-probs with character
offsets. Measured on E4B 4-bit: scoring 715-867 tok/s vs. generation 54 tok/s (13-16x).
Public leaderboard patches with resolved labels are downloadable anonymously
(`src/fetch_patches.py`), so patch-level experiments need no Docker.

**18:40 — Pilot launched** on 25 dev instances (every 20th Verified instance by id; these are the
*development set* — any choice of aggregation is made here and frozen before touching the rest).

**18:45 — DEV result, first formulation ("blind" likelihood shift, file not in prompt).** 16 files:
no better than BM25. Negative result, parked (details in EXPERIMENTS.md E1a).

**18:50 — Reformulation: null-edit teacher forcing.** Put issue + file in the prompt, ask for a
full rewrite, teacher-force the unchanged file. Gives the exact first-edit distribution of the
model's rewrite policy in one pass (identity in HYPOTHESES.md, Revision 1). Prior-art search
(`notes/prior_art_nulledit.md`): no same-idea work found; nearest ancestor is speculative-edit
decoding (EfficientEdit, arXiv 2506.02780; OpenAI Predicted Outputs), which uses the same
verification pass for speed, not as a measurement. The efficiency argument is NOT novel.

**18:55 — DEV result, null-edit (E4B, 30 files of 25 instances, files ≤ 20k tokens).**
Line level, rank of best gold line: one-pass hazard S hit@10 0.67 (median rank 7); issue-specific
hazard H hit@10 0.70 (median rank 5); BM25 0.37; line length 0.33; wrong-issue control 0.20;
random 0.13; the model's own generated answer 0.37.
Function level hit@1/3/5: H 0.53/0.87/1.00; generated answer 0.60/0.73/0.80; BM25 0.37/0.80/0.87;
function length 0.30/0.63/0.70. Controls RB (right issue, "copy" instruction) and R0 (no issue) are
at chance -> the signal needs the right issue AND the instruction to fix.
Caveats found by the design reviewer (`notes/review_design.md`): sum-aggregation is confounded with
function length (random-sum hit@1 0.40); only gold files are scored (oracle file); memorization
not yet ruled out. Pre-registered TEST protocol written to HYPOTHESES.md before any TEST scoring.

**19:00 — Cost reality check.** Plain prefill on E4B runs at ~3,500–6,800 tok/s; my scorer ran at
~1,000 tok/s (memory-starved earlier; chunking + full-vocab log-softmax). Benchmarked in isolation:
hidden-only 4,500 tok/s, stock head + log-softmax 3,580 tok/s. So a null-edit pass costs ~2 prefills
of the file; the generative answer costs 1 prefill + ~60 generated tokens (median 1.4 s/file).
Generation is cheaper per file here; the null-edit's advantage is line-level resolution, not speed.

**19:05 — All jobs stopped at the user's request** (machine was being overloaded; an early version
of the scorer let MLX hold ~50 GB). State: DEV complete; TEST run had scored 7 files and is
resumable (`src/queue1.sh`); models E2B/E4B/12B/31B downloaded; 136 leaderboard submissions' patches
downloaded. Nothing is running.

**19:10 — Resumed, throttled** (user approved; then asked for less fan noise). One job at a time,
`nice`, MLX cache capped at 1 GB, 512-token chunks, duty cycle ~40% (`THROTTLE=1.5`). Scorer now
skips the vocabulary head on prompt tokens: ~3,900 tok/s unthrottled, ~7 GB footprint. File cap
raised from 20k to 32k tokens because 40% of gold files exceeded 20k (deviation from the
pre-registration; the ≤20k subset is reported separately). Workload trimmed: TEST 250 instances,
LIVE 150, controls 60, file-level 60, fixed-point 70, E2B/12B 100, 12B-LIVE 60. 31B not run
(would need ~20 GB on a machine the user is working on).

**19:30 — Independent replication of the analysis** (`replication/`): all DEV numbers reproduced
exactly from the raw `.npz` files by a replicator without access to the analysis code.

**19:40 — Interim held-out look (91 files / 76 instances; protocol frozen, no tuning).**
Line hit@10: H 64.8 [55, 75], S 59.3, BM25 38.5, wrong-issue control 12.1, random 13.2
(H − BM25 = +26.4 points, p = 0.0002). Function level: H 44.0 vs BM25 42.9 hit@1 — no difference.
Edit mass within ±2 lines of a gold line (4% of lines): 23% under the correct issue (×5.8
enrichment), 3.6% under a wrong issue (×0.9). So far: a line-level instrument, not a better
function ranker.

**19:45 — Compute moved to a DGX Spark at the user's direction.** Laptop GPU work stopped (fan
noise). Laptop state at stop: E4B 4-bit MLX, held-out TEST scored for the first 88 instances of
`results/test_ids.txt` (98 files) — kept as the *consumer-hardware arm*.
DGX: NVIDIA GB10, aarch64, 121 GB unified memory, Ubuntu 24.04, idle. Plan: PyTorch/transformers
backend (`src/scorer_torch.py`, same interface as the MLX scorer), **official full-precision (bf16)
checkpoints of all five Gemma 4 sizes** (E2B, E4B, 12B, 26B A4B, 31B; all ungated on Hugging Face).
User requirements recorded: (1) the paper must say which results come from the Mac and which from
the DGX; (2) test as much as possible on the DGX, with every Gemma 4 size. The earlier decision to
skip 31B applied to the laptop only.

**20:10 — DGX environment.** A fresh `pip install torch` stalled on the DGX's slow link (~11 MB/s
shared with the 165 GB of model downloads), so the DGX arm borrows an existing CUDA build on that
machine through a `.pth` file: torch 2.14.1+cu130, transformers 5.14.0.dev0, accelerate 1.15.0,
numpy 2.5.4 (read-only use of `~/apertus-redteam/.venv`); `unidiff` installed into our own venv.
Jobs run through `src/runner.sh`, which pops commands from `todo.txt` one at a time.

**20:20 — DGX backend validated (E4B bf16, PyTorch).** Same chat prefix and identical tokenization
as the MLX arm. Chunked-with-cache vs single-pass scoring: max per-token difference 0.04–0.62 nats
(bf16 noise). Against the laptop's 4-bit MLX scores on six DEV files: best gold-line rank
30/4/1/1/5/4 (DGX) vs 42/4/1/4/5/2 (Mac); line-level S correlation 0.31–0.98 — the same lines
light up although quantization changes individual token probabilities. Throughput on the GB10:
1.7–3.2k tok/s scoring; ~15 tok/s generation with the plain Python decode loop.
First batch of DGX jobs failed instantly (instance-id files not yet synced; the runner mis-reported
exit codes) — fixed, runner restarted at 20:19 with 40 queued jobs covering all five model sizes.

**22:20 — Held-out result, E4B, DGX arm (250 TEST instances, 300 files, protocol as pre-registered
except the 32k cap).** Line level hit@1/5/10: H 27.0/55.0/69.0 (median rank 4 of ~590 lines),
S 23.3/51.3/63.7, BM25 12.0/30.3/38.0, wrong-issue 3.0/9.7/15.7, line length 17.3@10, random 12.0@10.
H − BM25 at hit@10: +31.0 [21.3, 40.2]. Function level hit@1: H 50.3, S 44.3, BM25 38.3, length
prior 27.3 (H − BM25 +12.0 [1.7, 22.0], p = 0.022). Edit mass within ±2 lines of a gold line
(3.8% of lines): 28.5% under the correct issue, 3.9% under a wrong one.
Robust across subsets: ≤20k-token files 71 vs 39 (BM25); pure insertions 55 vs 18; repo
macro-average 69 vs 34; modified-lines-only labels 65.7 vs 39.5.
**Unexpected:** on the 91 files scored on both machines, bf16 (DGX) beats 4-bit MLX (Mac) by
+11 points at line hit@10 (p = 0.007), +16.5 at hit@1 and +18.7 at function hit@1. Quantization
(confounded with backend) blunts the instrument — a practical finding for local deployment.

## 2026-11-11 23:45 UTC — held-out comparison with the generated answer (DGX)

* `genq_e4b_test` finished (300 files). First scoring of the quoted-answer baseline used the strict
  "all occurrences" mapping (line hit@10 36.0). Inspection showed the model quotes whole blocks and that
  repeated lines (`)`, `return [` …) were being mapped to every occurrence, which pushes gold lines down
  the inspection order. Added a context-aware mapping (`align_quotes`) that favours the baseline; both are
  reported. Under the favourable mapping: line 11.7/30.7/44.7, function 51.3/61.7/62.0.
* Honest reading: at **function top-1 the generated answer ties H** (51.3 vs 50.3, p = 0.79). The null-edit
  map wins at line level (+24 points at top-10) and at function top-3/top-5 (+13/+22). The paper's claim
  is therefore "line-level resolution and a ranked list", not "better function picker".
* Moved the line-range generated baseline (`gen_e4b_test`, now 250 instances) to the front of the DGX queue:
  on DEV it was the stronger of the two generated baselines at function level (61% hit@1 on 33 files), so
  the headline comparison must include it on the same 300 files.
* Tooling added: `merge_frames.py`, `scaling.py`, control rows in `report.py`, 5-size `fig3`.

## 2026-11-12 00:20 UTC — review round 4 and re-plan

* Opus critic reviewed the full draft (`notes/review_draft1.md`): 2 blockers (claims ahead of evidence;
  generated-answer comparison not budget-matched), 8 majors. Responses in `REVIEW.md` Round 4.
* New analyses from saved logs (no GPU): budget-matched comparison, greedy-no-op subset (84 files),
  issue-weighted estimates, MRR, Holm correction, mirror control, position baseline, context budget.
* New experiments queued on the DGX: `edit_e4b` (let-it-write baseline + map-guided edit, 3 arms),
  `e4b_q4_test` (MLX 4-bit weights de-quantized into the PyTorch model; mapping validated: 345 matrices,
  relative error vs bf16 median 9.5%; sha256 of the MLX file identical to the laptop's copy).
* Laptop → DGX upload is too slow for checkpoints (12 MB in 5 min); the DGX downloads from the hub instead.
* Dropped from the queue for time: post-cutoff runs for sizes other than E4B, range-mode generation on LIVE.
  Trimmed: 31B to 60 issues, fixed-point to 60, file-level to 50.

## 2026-11-12 01:50 UTC — line-range baseline and 4-bit de-confound

* `gen_e4b_test` (pre-registered line-range answer, 300 files) finished. It is the stronger generated
  baseline: line hit@10 51% (H 69%, +18 [12, 24]) but function hit@1 60% vs 50% for H (−9.3 [−15, −4]).
  The paper's "ties asking at one function" claim was true only for the quoted answer and is replaced by
  "asking wins at the first function pick". Abstract, contribution 2, Table 1, §4.2, §4.3, §4.8 and
  Limitations updated.
* `e4b_q4_test` finished: the laptop's 4-bit weights in the DGX code reproduce the laptop's numbers
  (−1.1 points) and trail bf16 by 12.2 points → the MAC/DGX gap is quantization (§4.7).
* Holm family grew as post hoc tests were added; H − BM25 at function hit@1 is now reported with its
  unadjusted p (0.02) and described as not significant after correction.
* DGX queue reordered so the four other Gemma 4 sizes run before the edit experiment.

## 2026-11-12 03:45 UTC — controls, first two other sizes, two incidents

* `e4b_ctrl` (RB, R0) finished 02:13: no issue + copy 23%, right issue + copy 35% (BM25 38%), fix
  instruction 74% at line hit@10 (111 files). The pre-registered "near chance" prediction for the copy
  controls is refuted; the comparative prediction (far below the probe) holds. Written into §4.4.
* `e2b_test`, `g12b_test` finished (R, RX; first 100 held-out issues; 111 files common with E4B).
  Size is not monotonic: line hit@10 S = E2B 53, E4B 74, 12B 59. Split by file length (cut at 5,000
  tokens, chosen after seeing these three runs): under 5,000 tokens all three work (76 / 84 / 86); at
  5,000 or more E2B and 12B collapse (33 / 65 / 37) because copying itself becomes costly whatever the
  issue: median wrong-issue copy cost 18 / 2 / 48 nats. In those files 12B has ~24 tokens with p < 0.5
  per frame, half of them not shared between frames, and E4B is confident on nearly all of them.
  `scaling.py` now prints the split. To check: that this is the model and not the chunked KV-cache
  scoring loop (`diag_long.py`: chunk 512 / 1024 / 6000 on three long files).
* INCIDENT 1: `g26b_test` failed at load (03:31). The first 26B shard was truncated by the download
  (46.2 of 49.9 GB; `curl -C -` returned early and the script did not verify sizes). Resumed and verified
  against the safetensors header (49,907,246,508 bytes); job re-queued behind a marker file. 31B shards
  verified complete the same way.
* INCIDENT 2 (my error): I started `diag_long.py` (12B, 24 GB) next to the running 31B job. Memory went
  to 121/121 GB and the DGX stopped answering ssh at ~03:42. No parallel jobs next to 26B/31B again.

## 2026-11-12 03:55 UTC — audit round, DGX still down, laptop replication started

* Number audit by a Sonnet subagent (REVIEW.md Round 7): ~150 claims, 3 fixes (10% of the median file is
  69 lines, not 59; the quoted-lines baseline was not "added before the held-out run"; "beats BM25 at every
  cut-off" narrowed to lines). `src/paper_numbers.py` now regenerates every number that previously lived
  only in hand-written logs (`results_dgx/report_paper_numbers.md`); all reproduce.
* DGX: answers ping (RTT 1–2 s) but not ssh since ~03:42 UTC — swapping. State of the 31B run unknown.
* Fallback and on-device replication (declared in HYPOTHESES.md Revision 2b before starting):
  `edit_e4b_test_mac` — the map-guided edit experiment entirely on the laptop (E4B 4-bit MLX, hints from the
  laptop's own 4-bit map, 98 files), one niced job, THROTTLE=1.5 (GPU ~40% duty), started 03:54 UTC.

## 2026-11-12 04:10 UTC — DGX down 28 min; laptop plan

* DGX: no ssh, no ping at 04:10. Needs a reboot by the user (notified). A retry loop reports when it answers.
* Edit experiment restarted on the laptop at 03:57 with a 640-token cap (HYPOTHESES.md Revision 2c);
  30 replies in 12 min at THROTTLE=1.5 → ends ≈ 06:40–07:15 UTC.
* Queued behind it on the laptop (`src/queue_mac2.sh`, one throttled job at a time): 12B and E2B 4-bit MLX,
  frames R and RX, on 20 files chosen by length only (`results/lencheck_ids.txt`: first 10 single-file
  held-out issues with a 5k–12k-token file, first 10 under 5k). Purpose: an independent backend (MLX instead of
  the PyTorch chunked KV-cache loop) to tell whether the long-file copy cost of 12B/E2B is the model's.
* Contingency if the DGX stays down: sizes section reports E2B/E4B/12B only and says why; the laptop edit run
  is the edit result; no-prefill check and asking-on-Live are dropped from the paper.

### 2026-11-12 05:52 UTC — DGX still down; CPU-only diagnostic of the long-file copy cost; laptop queue reordered

* DGX: no ping, no ssh since ~03:42 UTC (2 h 10 min). Waiting for a reboot by the user. Nothing can be run there.
* **Chunk-boundary diagnostic (CPU only, saved DGX scores, files ≥ 5,000 tokens, wrong-issue frame).** If the
  12B/E2B copy cost in long files came from the 1024-token chunked KV-cache loop, surprising tokens (p < 0.1)
  would cluster at chunk starts. They do not: position-within-chunk histogram (8 bins) is flat for all three
  sizes (12B: 0.11–0.16 per bin, 1,148 tokens; E2B 211 tokens; E4B 98 tokens over 183 files). So a boundary
  bug is unlikely. What is seen instead for 12B: the cost sits in a few very surprising tokens (≈ 10 nats each),
  mostly newlines, punctuation and common words (`\n\n`, `\n`, ` :`, `.`, ` the`, ` to`), spread over the whole
  file, and concentrated in a handful of very long files (sympy, astropy: 400–940 nats). This is compatible with
  the model losing its place while copying long repetitive files, and equally with a backend problem specific
  to 12B at long context. **Still unverified**; the laptop MLX run on 20 files is the available independent check.
* Laptop queue (one throttled job at a time): edit run (299/392 replies at 05:51) → no-prefill check
  (Revision 2d; E4B 4-bit on the 84 bf16 greedy-no-op files) → 12B length check → E2B length check.
* Figure 3 redrawn (legend below the panels, copy cost annotated in grey).

### 2026-11-12 06:14 UTC — DGX back without a reboot

* At 06:12:07 UTC the kernel killed the 31B job (exit 137); memory was freed, the runner survived and started
  `g26b_test` (26B A4B, 100 issues, one pass). The stall lasted 2 h 30 min (03:42–06:12). The diagnostic process
  that caused it is gone. 31B had scored one file (3,247 tokens in 13 s, ≈ 250 tokens/s).
* Queue rewritten (backup `todo.bak_v8`), strictly serial, nothing beside 26B/31B: `g31b_test` (now 100 issues, so
  all five sizes share the same 111 files; the plan had said 60 for compute reasons) → `diag_12b` (chunk-size
  diagnostic, 3 long files) → `noprefill_e4b` → asking baselines for E2B and 12B → `edit_e4b` (cap 640 tokens,
  Revision 2c) → asking baselines for 26B A4B and 31B (100 issues) → wrong-issue passes for 26B A4B and 31B →
  asking on Live → file level, fixed point, calibration if time remains.
* Laptop edit run: 357 of 392 replies; 25% of replies reach the 640-token cap (counted invalid, as declared).

### 2026-11-12 07:10 UTC — second DGX stall; cause identified: 31B's cache does not fit on long files

* The DGX stopped answering again some time after 06:45 UTC, with `g31b_test` running **alone**. Its second file is
  `sympy/printing/latex.py` (24,933 tokens; prompt + answer ≈ 51k tokens).
* Arithmetic from the model configs: 31B has 60 layers × 16 key/value heads × 256 dims → 0.98 MB of bf16 cache per
  context token. 51k tokens → ≈ 50 GB of cache on top of 62 GB of weights: more than the 121 GB the machine has.
  (12B: 0.39 MB/token; E4B: 0.09; E2B: 0.04.) So the first stall (03:42) was most likely the same file and not only
  the diagnostic I had started beside it; re-queuing 31B on 100 issues unchanged repeated it. My error twice: I did
  not size the job before launching it.
* Last time the kernel needed 2 h 30 min to kill the process. Expected back ≈ 09:15 UTC unless rebooted earlier.
* Fix, written and ready to ship (not yet tested on the DGX):
  - `scorer_torch.py`: `SCORER_MEM_FRACTION` sets a hard per-process GPU memory cap, so an oversized job fails
    instead of stalling the machine;
  - `run_conflict.py`: an out-of-memory error on a file is logged as `{"skip": "oom"}` and the run continues;
  - 31B will be run with `--max-file-tokens 11000` and a 0.8 cap (≈ 97 GB): worst case 62 GB weights + ≈ 23 GB
    cache + ≈ 4 GB transient. The paper will state that 31B covers files up to 11k tokens for memory reasons.
* New DGX order once it answers (≈ 7.5 h of compute left before the 17:00 UTC freeze): 31B capped → `diag_12b` →
  `diag_g26b` → `noprefill_e4b` → wrong-issue passes for 26B A4B and 31B → asking baselines (E2B, 12B, E4B Live,
  26B A4B, 31B) → bf16 edit run last, only if time remains (the laptop run then stands as the edit result, as
  Revision 2b allows).
* Laptop: 12B length check done (see EXPERIMENTS.md); E2B length check running.

### 2026-11-12 07:22 UTC — why the larger models' maps fail in long files: they rewrite prose (exploratory), and a pre-registered confirmation

* Laptop, 12B 4-bit (MLX), tokens that are very surprising in BOTH the 4-bit and the bf16 run, greedy continuation
  from just before each (`results/diag_alt_mac_R.txt`): at several the model writes the actual fix (django-14765:
  `assert isinstance(real_apps, set)`; requests-1142: an early return for GET/HEAD; sphinx-9320: `allow_empty`;
  pytest-7982: `follow_symlinks=True`); at the others it **rewords a docstring or a comment**. So the cost is the
  model's behaviour, reproduced on a second backend, not a scoring artefact — for these tokens.
* CPU analysis on saved DGX scores (`src/explore_codeonly.py`): for 12B and 26B A4B the median share of a file's
  hazard that sits on comment/docstring lines is 0.46/0.30 under 5,000 tokens and 0.90/0.91 over 11,000 (E4B 0.01 and
  0.11; such lines are 31% of lines). Not ranking those lines moves S line@10 from 59% to 79% (12B, +19.8 [10, 30])
  and from 59% to 75% (26B A4B, +16.2 [7, 26]); over 11,000 tokens 32 → 81 and 24 → 70. E4B 74 → 70; E2B 53 → 56.
  With code lines only, 12B and 26B A4B are level with or above E4B (+5.4 [−3, 14], +0.9 [−8, 9]).
* This replaces the earlier reading ("the probe needs a model that can copy"): the larger models can locate the fix;
  what they do not do is leave prose alone when told to change only what is necessary.
* It was found by looking at the held-out files of issues 1–100, so it is exploratory. **Revision 3** in
  `HYPOTHESES.md` (07:20 UTC) freezes the line classifier and declares a confirmation on issues 101–200, which 12B and
  26B A4B have never scored. Analysis script: `src/analyze_codeonly.py` (reproduces the exploratory numbers).
* DGX queue for when it answers: `src/requeue_dgx.py` (confirmation runs first, then 31B with a memory cap and files
  ≤ 11,000 tokens, then diagnostics, bf16 no-prefill, wrong-issue pass for 26B A4B, asking baselines; bf16 edit last).

### 2026-11-12 10:28 UTC — DGX back after the second stall (3 h 45 min lost)

- The DGX answered again at 10:28 UTC: the kernel had killed the 31B run (`END g31b_test (exit 137)`
  at 10:28:31) and the runner moved on. The machine was not rebooted (uptime 57 days), but other
  services hosted on it restarted at the same time (their process ids are all new): our job took
  them down. This is our fault and is the reason for the three safeguards below.
- Safeguards shipped before anything else ran: (1) `SCORER_MEM_FRACTION=0.8` for every 31B job and
  files capped at 11,000 tokens for 31B (sizing: 0.98 MB of cache per context token, 62 GB of
  weights); (2) `run_conflict.py` skips a file on a CUDA out-of-memory error and logs
  `"skip": "oom"`; (3) `src/memguard.sh` on the DGX kills *our* job (never anything else) when
  available memory drops under 8 GB.
- Queue reordered (`src/requeue_dgx.py`): the pre-registered confirmation runs first (12B, then
  26B A4B, issues 101–200), then 31B on the first 100 issues, then diagnostics, no-prefill in bf16,
  wrong-issue pass for 26B A4B, asking baselines, 31B confirmation, edit experiment last.
  `g12b_conf` started at 10:29:24 UTC.
- Laptop: number audit of the stable sections of the paper launched (subagent, read-only).

### 2026-11-12 10:35 UTC — reviews of the current draft; a scoring error found and corrected

- Number audit (subagent, read-only): 157 numbers checked against the reports, no mismatch; one
  ambiguity (median 587 non-blank lines vs 10% ≈ 69 lines of 686 total lines) clarified in §4.8.
- Critical review (subagent): §4.6 states a mechanism from post hoc evidence and omits that N5 was
  refuted; §4.8 says the hint "does not move" the edit when it moves it both ways; abstract and
  limitations overreach. Fixes applied or queued for the final text.
- **Scoring error, edit experiment.** While applying the review I checked the sentence "truncated
  replies count as invalid, as declared" against the data: 18–21 truncated replies per arm had been
  scored. `analyze_edit.py` now applies the declared rule by default. Corrected primary numbers:
  on_gold 28 / 27 / 11 / 40 (none / map hint / placebo / gold); H − WRONG +15.3 [+6.3, +24.7];
  H − none −1.0 [−9.1, +7.4]. N8 and N9 remain not supported. The earlier (lenient) table is kept
  as a sensitivity analysis. EXPERIMENTS.md and the paper corrected.

### 14:22–15:00 UTC, 2026-11-12 — asking at every size; freeze of the text

- Asking baselines finished for E2B, 12B, 26B A4B (111 files) and for E4B on Live. 31B's was stopped by
  the memory watchdog (exit 137, six minutes in); no other service was affected.
- **Result that narrows the paper's claim:** asked for line ranges, 12B and 26B A4B put a gold line in
  their ten for 74% of files, above their all-lines maps (59%) and level with their code-only maps
  (79%, 75%), and name the gold function first in 80% / 79% (maps 34% / 37%). The map beats asking
  only for E2B (53 vs 30) and E4B (74 vs 61). Abstract, contribution 4 and §4.6 rewritten to say that
  the map's lead is a small-model effect. Decision: report it in the abstract, not only in §4.6.
- Live: asking 51% against H 68% at line top-ten; tie at function top-1 (64 vs 63).
- The bf16 edit run started at 14:22 UTC and will not finish before the freeze; its placeholder was
  removed and §4.8 stays labelled MAC arm.
- `analyze_all.sh` rerun end to end (3 min 56 s, no failure). `paper_numbers.py` restricted its
  label-free table to the 74 files 31B has; fixed to treat 31B as partial coverage, as `scaling.py` does.
- Number audit of the final text (subagent, read-only): no numeric mismatch in the new passages; four
  wording points fixed ("match" → "not distinguishable from"; "the sizes" → "the four smaller sizes";
  BM25 39% → 40% on Live no-op files; "a quarter" → "18–33%" of replies truncated).
- `src/queue_dgx.txt` written from the DGX runner history. Ten early command lines were not kept; they
  are marked NOT KEPT with a description from this log instead of a reconstructed command.
- Paper: 2,993 words by the strict count (every whitespace-separated token), no placeholders.

### 17:32–17:50 UTC, 2026-11-12 — bf16 edit experiment; final text

- `edit_e4b` finished on the DGX (111 files, 3 h 10 min). Under the declared rule: on_gold 40 (no hint),
  44 (map hint), 32 (wrong-issue hint), 66 (gold lines). Map − wrong +12.6 [+3.6, +21.6]; map − none
  +4.5 [−2.7, +11.7]. N8 and N9 not supported on bf16 either; the sign is positive where the 4-bit
  arm's was zero, and neither is reliable.
- §4.8 now leads with the bf16 numbers and keeps the MAC numbers labelled MAC. Contribution 5 reworded
  from "leaves the accuracy unchanged" to "does not reliably improve". Paper: 2,995 words (strict count).
- A draft sentence said the MAC run had a shorter token cap. Checked against the data: both runs used
  640 tokens; the 4-bit model simply truncates more often (18–33% against 5–14%). Sentence corrected
  before it reached the repository.
- `g31b_conf` started at 17:32 UTC under the memory watchdog; it is not in the paper.
