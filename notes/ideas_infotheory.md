# Hypotheses from information theory, statistical physics, and optimal search

Written 2026-11-11 by an independent "scientist" subagent. Budget: about 25 minutes, with a few web searches for prior art.
Speculation is labeled as such. No experimental results here are real. All numbers below are **predictions** or **rough estimates**.
Throughput figures for Gemma 4 on an M5 Max are my guesses, not measurements. Benchmark them in the first 10 minutes.

## Ranking

| Rank | Hypothesis | P(effect real and visible in 1 day) | Cost |
|---|---|---|---|
| 1 | **H1: Residual-bits law.** Task difficulty is the number of bits about the fix that the issue does *not* supply, measured as a teacher-forced code length. The logit slope against those bits measures how many bits an agent gets from its environment instead of guessing. | 0.55 for the basic effect; 0.30 for the strong slope interpretation | about 2-4 h of local scoring, plus labels from public sources |
| 2 | **H2: Decreasing-hazard / restart law for small agents.** The chance of first success per step falls inside a trajectory. Short restarts beat long runs at the same token budget, and the gain grows as the model gets smaller. | 0.50 | about 6-8 h of agent runs; the restart analysis is offline and nearly free |
| 3 | **H3: Information-acquisition curves.** A Bayesian observer can split agent failures into *acquisition* failures (the needed bits never entered the context) and *exploitation* failures (the bits were in context but unused). After the first edit, steps often *lose* bits ("entropy production"). | 0.35 | about 2-3 h of local scoring on public trajectories |

---

## H1. The residual-bits law of issue resolution (rank 1)

**(1) Phenomenon or limitation.** SWE-style difficulty is described today with structural proxies or human labels:
- patch size, files touched, and repository scale;
- annotator time-to-fix;
- hand-annotated "localization cue" and "suggested fix" spans.

No one measures the quantity that coding theory says should matter: how many bits of the fix the issue report carries, and how many it leaves for the agent to find. An issue report is a noisy channel from the maintainer's head (the fix) to the agent. Its information content about the fix can be measured directly with teacher-forced log-probabilities.

**(2) Hypothesis.** Fix a scorer LM (Gemma 4 26B or 31B). Let `C` be oracle code context: the pre-patch text of the gold-edited files, windowed around the hunks so that localization is held out. Let `P` be the gold patch, written as a canonical diff. Let `X` be the issue text. Define:
- `L0 = -log2 p(P | C)`: the fix's code length with no issue.
- `L1 = -log2 p(P | X, C)`: the **residual bits** R the agent must still produce.
- `I = L0 - L1`: the pointwise mutual information the issue supplies.
- `ρ = I / L0`: the "channel coverage."

Quantitative predictions on SWE-bench Verified (500 instances), using cross-agent solve fraction from the public SWE-bench experiments leaderboard results:

- (a) Spearman(R, solve fraction) ≤ -0.35.
- (b) After controlling for gold-patch lines, hunks, files, issue length, and repository, the partial correlation of R (or ρ) stays ≤ -0.15. Adding R to a structural-feature logistic model raises AUC for "solved by a majority of agents" by ≥ 0.03.
- (c) **Derivation (speculative but checkable).** Model a pure guessing agent as a sampler whose distribution matches the scorer. It hits the fix with probability about 2^-R, so logit(solve) ≈ const - (ln 2)·R, a slope of -0.69 per bit. Now take an agent that gets bits from the environment (reading code, running tests, seeing tracebacks) at no cost. Its slope should be flatter. Fit, for each agent, `logit P(solve_i) = a_agent - b_agent·R_i`. The ratio `b_agent / ln2` is then an **effective fraction of bits the agent must guess rather than acquire**. Prediction: `b_agent` falls as the agent gets stronger, so the curves are not just shifted but also flattened. A pure capability-shift model (IRT with a common slope) should fit worse than per-agent slopes.

**(3) Mechanism.** By the coding theorem, an agent that cannot gather information must find the fix by search. The expected search effort scales like 2^(bits missing). Every useful action (reading a file, running a test) is a channel use that delivers some bits. A strong agent has more capacity per action and a better prior, so it gets more of R from the environment and its difficulty curve flattens.

**(4) Prior art I checked. Honest assessment: the measured quantity looks new, but its ingredients are not.**
- *What Makes Software Issue Resolution Tasks Difficult for Agents?* ([arXiv 2608.18280](https://arxiv.org/abs/2608.18280)) predicts difficulty from static patch, repository, and prompt features. It reaches AUC 0.863, driven by patch fragmentation and repository scale. As summarized in the search results, it deliberately avoids LLM-based encodings and has no log-probability features. It is the right **baseline** to beat.
- Bug-report information annotation ([alphaxiv 2607.09553](https://www.alphaxiv.org/abs/2607.09553.md)) hand-labels localization cues and suggested fixes in the 441 Verified reports. Suggested fixes were the strongest predictor (code OR 3.97, natural language OR 3.16). Localization alone was not significant in the pooled model. H1 is a continuous, annotation-free generalization of that discrete finding, and it adds the slope interpretation.
- SWE-bench Live ([arXiv 2505.23419](https://arxiv.org/pdf/2505.23419)) and SWE-smith ([arXiv 2504.21798](https://arxiv.org/pdf/2504.21798)) use patch size or a learned predictor of time-to-fix labels.
- Coder-Reviewer reranking (Zhang et al., 2022) uses p(instruction | code), a PMI-like signal, to *rank candidate programs*, not to measure task difficulty. I cite it from memory and did not open it in this session.
- My searches found no paper that uses gold-patch code length conditioned on the issue, or issue-patch PMI, to explain agent difficulty. That is weak evidence of absence (two searches only).

**(5) Falsification.** The hypothesis fails if any of these holds:
- |partial ρ| < 0.1 after the structural controls;
- the AUC gain is < 0.01;
- per-agent slopes `b_agent` do not differ, or do not decrease with leaderboard rank (no flattening);
- R predicts no better than raw gold-patch token count.

**(6) Smallest convincing experiment.**
- *Data:* SWE-bench Verified instances (HF `princeton-nlp/SWE-bench_Verified`) and the per-agent resolved ID lists from `github.com/SWE-bench/experiments` (`evaluation/verified/*/results/`). Per the repo README, per-instance artifacts now live in submitter repositories or S3, but resolved lists are in-repo. Take about 50-100 agents and compute each instance's cross-agent solve fraction, plus per-agent binary labels for the slope analysis.
- *Context:* Clone the about 12 repositories once. `git show base_commit:path` gives the pre-patch files, so no Docker and no checkout is needed.
- *Scoring:* For each instance, score the diff tokens only under `[C]` and under `[X, C]`. Keep a fixed template and truncate C to ±80 lines around each hunk (about 3-6k tokens). That is 500 × 2 × about 6k ≈ 6M prefill tokens. Guess: about 1-2 h on 26B MoE with MLX or llama.cpp; also run E4B (cheaper) to check that the scorer does not matter.
- *Secondary measure:* localization bits `-log2 p(path | X, repo file list)` to separate "where" bits from "what" bits. Prediction: "what" bits dominate, in line with 2607.09553.
- *Controls:*
  - Patch length (tokens, lines, hunks): report per-token R as well as total R.
  - Issue length.
  - Repository fixed effects.
  - A **shuffled-issue control**: score with an issue from another instance in the same repository. This should give I ≈ 0, which checks that the prompt format is not leaking.
  - The scorer swap (E4B vs 26B vs 31B).
  - **Contamination:** Gold patches are probably in pretraining data, and memorization lowers L1 and L0 together. Check that the PMI `I` still predicts. Also score *agent-produced correct non-gold patches* (available from submitter artifacts where reachable): their R should track the gold R if R measures task information rather than memorization.
- *Statistics:* Spearman with bootstrap CIs; nested logistic and GLMM models with agent random effects; likelihood-ratio test of common-slope vs per-agent-slope models.

**(7) Implications if validated.**
- A cheap, annotation-free, model-based difficulty meter for benchmarks: build difficulty-controlled splits and detect "giveaway" issues.
- A principled per-agent number, "bits acquired from the environment," that ranks agents by **information efficiency** rather than raw solve rate.
- Practical tooling: an agent can estimate R before starting. Low-R tasks call for one-shot patching; high-R tasks call for exploration and test-writing. This is budget allocation by bits.

**Hostile reviewer's simpler explanation.** "R is just patch length times average surprise, so you rediscovered patch size. And PMI is just 'the issue contains the fix', which 2607.09553 already showed." Answer: the partial correlations against length and fragmentation, the per-token R, and the slope-flattening claim cannot be reduced to patch size. The second objection is partly right. H1 generalizes that finding, and the paper should say so.

---

## H2. Decreasing hazard: small-model agents should be built as restart machines (rank 2)

**(1) Phenomenon.** Agent frameworks give a small model one long trajectory with a step budget (30-250 steps), assuming more steps means more chances. Restart theory for Las Vegas algorithms (Luby, Sinclair, Zuckerman 1993) says restarts help exactly when the **hazard rate** of success decreases with elapsed time. That is the signature of heavy-tailed run-length distributions, as in SAT. No one has measured the **within-trajectory** hazard of first success for LLM coding agents. If it decreases, long-horizon budgets are wasted on small models.

**(2) Hypothesis.** Let T be the step at which the working tree first passes the hidden tests, with T = ∞ if it never does. Measure the per-instance distribution of T across seeds.
- (a) For Gemma 4 E4B and 26B, the empirical hazard h(t) = P(T = t | T ≥ t), pooled over seeds *within* an instance, decreases after an early peak. Prediction: h(2·median) < 0.5·h(median) on the majority of instances that are solved at least once.
- (b) The fixed-cutoff restart cost is E(t) = ∫₀ᵗ (1 − F(s)) ds / F(t) (Luby et al.). Its minimizer t* lies at about 1-2× the median success step, well below standard budgets. At equal total steps B = 40, restarting at t* solves ≥ 1.3× as many instance-seeds as one 40-step run.
- (c) **Size dependence:** the tail is heavier (gain from restarts larger) for E4B than for 26B or 31B.
- (d) Luby's universal sequence, which needs no knowledge of the distribution, gets within about 1.5× of the oracle t*.

**(3) Mechanism.** This is statistical physics of search: trapping in a glassy state.
- Each failed edit, long traceback, and wrong hypothesis stays in context and conditions later actions toward it (self-conditioning, or "context poisoning").
- Small models have weaker long-context retrieval, so the effective temperature drops as context fills. The trajectory freezes into a basin.
- A restart is a quench back to the high-entropy initial state.
- *Speculative:* the trap depth grows with how much a model relies on recent context, which would explain prediction (c).

**(4) Prior art.**
- *Reset-and-Discard (ReD)* ([arXiv 2601.21522](https://arxiv.org/html/2601.21522v2)) is the closest. It brings Luby-style reasoning to LLMs, proves that τ = 1 (reset after each attempt) is optimal across *questions*, and models power-law pass@k (α ≈ 0.34 for Llama-3.1-8B on HumanEval). But it treats **independent single-sample attempts**, not multi-step agents. Its heavy tail is across-question difficulty, not within-trajectory hazard.
- Classic restart theory: *Runtime Distributions and Criteria for Restarts* ([arXiv 1709.10405](https://arxiv.org/pdf/1709.10405)) and van Beek's group on universal restart strategies ([cp07.pdf](https://cs.uwaterloo.ca/~vanbeek/Publications/cp07.pdf)).
- Repeated sampling ("Large Language Monkeys", Brown et al. 2024; cited from memory) shows coverage grows with samples but does not ask how long each sample should be.
- **What is new:** the within-trajectory hazard of multi-step agents, the size dependence, and the design consequence that the budget should be split into many short runs rather than spent on one long one.

**(5) Falsification.** The hypothesis fails if any of these holds:
- within-instance hazard is flat or increasing (geometric or "warming-up" T), so t* ≈ B;
- restart gain at t* is < 10% at equal steps;
- the gain is not larger for E4B than for 26B.

**(6) Smallest convincing experiment.**
- *Tasks:* 25-30 bugs in small pure-Python projects whose tests run natively in seconds. Two options:
  - Inject SWE-smith-style mutations (operator swaps, off-by-one, wrong branch) into 2-3 small dependency-free libraries. Keep only mutations that make at least one test fail.
  - Or use QuixBugs Python, but it may be too easy for 26B.
- *Agent:* a minimal bash-plus-edit loop (mini-swe-agent style) with max 40 steps, temperature 0.7. After **every** step, the harness silently runs the hidden tests to record T. The agent cannot see this.
- *Runs:* 30 bugs × 6 seeds × E4B (180 trajectories), plus 30 × 4 × 26B (120). Guess: 2-4 s per step with 4 parallel llama.cpp or MLX slots, which comes to about 6-8 h total. Cut seeds if throughput is lower.
- *Analysis is offline and free:* a restart with cutoff t equals the first t steps of an independent seed, so bootstrap over seeds to get coverage at equal step budgets for every t, for Luby, and for no-restart.
- *Controls:* report per-instance hazards (see the confound below); count tokens as well as steps; add a "continue with context wiped but files kept" arm on a subset to separate context poisoning from bad file states.

**(7) Implications.** A concrete design principle for local agents: **budget = many short episodes**, with t* estimated online from a few runs. Longer context windows and horizons may *hurt* small models. This also gives an operational test of "trap" dynamics in agent trajectories.

**Hostile reviewer's simpler explanation.** "Heterogeneity across instances. A mixture of constant hazards always gives a decreasing *pooled* hazard (the classic survival-analysis artefact), and moving on from hard instances is just ReD." The main defense is the per-instance, multi-seed hazard estimate. With 6 seeds the per-instance power is limited, so prediction (a) must be tested with a mixed-effects discrete-time hazard model (logit h ~ log t + instance random effect).

---

## H3. Information-acquisition curves: acquisition vs. exploitation failures, and negative bits after edits (rank 3)

**(1) Phenomenon.** Trajectory studies measure discrete milestones: was the right file viewed or edited? Recent work shows that localization is *not* the main failure mode for capable agents. Many failing trajectories reach the right code and still fail. There is no continuous measure of **how many bits about the fix each action delivered**. So we cannot tell an agent that never got the needed information from one that had it in context and did not use it.

**(2) Hypothesis.** Use a fixed observer LM (Gemma 4 26B) as an approximate Bayesian observer. For a trajectory prefix τ≤k (with observations truncated), let `L_k = -log2 p(P_gold | X, τ≤k)`. Bits acquired at step k: `ΔI_k = L_{k-1} − L_k`. Predictions:
- (a) **Bursty acquisition:** ΔI is heavy-tailed. The top 2 steps carry ≥ 60% of the net bits, mostly from reproduction or traceback outputs and reading the edited function.
- (b) **Entropy production:** after the agent's first edit, failing trajectories have net-negative Σ ΔI more often than resolved ones (OR ≥ 2). Self-generated wrong code and logs reduce the observer's belief in the true fix.
- (c) **Failure decomposition:** among failed trajectories, a large fraction (prediction ≥ 30%) end with `L_final` below the median `L_final` of *resolved* trajectories. These are exploitation failures: the information was there and went unused.
- (d) `L_k` at a fixed early step predicts final resolution beyond "gold file viewed by step k."

**(3) Mechanism.** Environment observations are a channel to the fix. Agent-written content (wrong edits, misleading test scaffolds) is noise injected into the same context. Exploitation failures match the "coherence collapse" pattern reported in recent trajectory analyses.

**(4) Prior art.**
- Cross-agent fault-localization study ([arXiv 2511.00197](https://arxiv.org/abs/2511.00197)): 72-81% of even *failed* trajectories identify the problematic files. The metrics are discrete (file, function, hunk).
- TRAJEVAL / "Coherence Collapse" ([arXiv 2603.24631](https://arxiv.org/abs/2603.24631)): 60-69% of failures reach and edit the correct functions yet produce incorrect patches. The stage decomposition is search, read, edit.
- CodeTracer ([alphaxiv 2604.11641](https://www.alphaxiv.org/abs/2604.11641)): step-level backward tracing of failure origin.
- None measure bits per action. H3 turns their qualitative finding into a quantitative, model-scored information curve. Novelty is moderate: it is a new instrument more than a new law. The negative-bits claim (b) is the most original part.

**(5) Falsification.** The hypothesis fails if any of these holds:
- ΔI is roughly uniform over steps;
- post-edit Σ ΔI does not differ between resolved and unresolved trajectories;
- `L_k` adds nothing beyond discrete localization features;
- the observer's curves are dominated by memorization: flat-low `L` from step 0 regardless of trajectory. Test this with the shuffled-issue and no-issue controls.

**(6) Smallest convincing experiment.**
- *Data:* 2 public agents with downloadable Verified trajectories (find via `metadata.yaml` assets in the experiments repo). Sample 60 instances where one agent succeeded and the other failed, which pairs the instances and controls difficulty: 120 trajectories.
- *Scoring:* truncate each observation to 1.5k tokens and cap context at about 32k. Use prefix KV caching: extend by one step, score the gold diff, roll back. Estimate: about 50k prefill tokens per trajectory, about 6M total, about 1.5-3 h on 26B MoE (speculative throughput).
- *Controls:* score a **decoy patch** (the gold patch of another same-repo instance) at every k. Real acquisition should lower `L_k` for gold but not for the decoy, so use a gold-minus-decoy contrast. Also run E4B as observer to show the result does not depend on the observer.

**(7) Implications.**
- A diagnostic that tells agent builders whether to invest in **search tools** (acquisition failures) or **context hygiene and summarization** (exploitation failures, entropy production).
- A principled trigger for H2-style restarts: restart when cumulative ΔI turns negative.

**Hostile reviewer's simpler explanation.** "The observer is just reacting to the gold function's text appearing in context (copying), and to trajectory length." The decoy contrast and the length-matched comparison handle this partly. Observer-agent mismatch is a real limitation: the observer's beliefs are not the agent's.

---

## Recommendation for a 30-hour deadline

**H1** is the strongest paper bet:
- It uses public labels across about 100 agents, so it generalizes across agents.
- Its compute fits easily.
- It has a clean derivation, slope ln 2 per bit for a pure guesser, that judges can verify.

If time remains, a reduced **H2** (E4B only, 20 bugs × 6 seeds) is the most *actionable* companion result. The two connect: H1 says difficulty is bits to be acquired; H2 says how small agents should spend their budget acquiring them.

## Sources opened or retrieved in this session
- https://arxiv.org/html/2601.21522v2 (ReD; opened)
- https://arxiv.org/abs/2608.18280 (difficulty from static features; opened)
- https://www.alphaxiv.org/abs/2607.09553.md (bug-report information for repair agents; opened)
- https://github.com/SWE-bench/experiments (repo structure; opened)
- https://arxiv.org/pdf/1709.10405, https://cs.uwaterloo.ca/~vanbeek/Publications/cp07.pdf, https://arxiv.org/abs/2511.00197, https://arxiv.org/abs/2603.24631, https://www.alphaxiv.org/abs/2604.11641, https://arxiv.org/pdf/2505.23419, https://arxiv.org/pdf/2504.21798 (seen through search-result summaries only; check before citing in the paper)
- Cited from memory, not opened: Luby, Sinclair & Zuckerman 1993; Coder-Reviewer reranking (Zhang et al. 2022); Large Language Monkeys (Brown et al. 2024).
