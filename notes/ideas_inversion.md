# Assumption inversion of the agent paradigm: three candidate hypotheses (Gemma 4, local)

Lens: what cloud-era coding agents take for granted, and which of those assumptions may be false for small local models.
Date: 2026-11-11. Status: these are proposals, nothing has been run. Any number below that is not cited is a **prediction or a guess** and is labeled that way.

---

## 0. Inherited assumptions and how much evidence backs them for small models

| # | Inherited assumption | Evidence for SMALL local models? | What follows if it is false |
|---|---|---|---|
| A1 | The model must **generate** its actions and patches as text | Weak. Generation is the only interface most scaffolds use, so it is rarely compared against scoring. | The model can be used as a *scorer* (recognizer) over candidates it did not write, which is cheap locally (see A9). -> **H1** |
| A2 | The agent's next action is **conditioned on the latest observation** (observe-think-act is closed-loop) | Assumed by design. Recent work shows agents often call tools and then disregard the result (QA and vision settings, not coding). | The loop is mostly open-loop: tool outputs are spent tokens that change little. -> **H2** |
| A3 | **Exploration helps localization** (more steps = better grounding) | Mixed. Agentless-style pipelines with no free exploration were competitive at the frontier; there is little direct evidence for 4-8B models. | A model's zero-shot prior over file paths may beat its own exploration, and the agent may *abandon* a correct prior. -> **H3** |
| A4 | More context and more steps help | Weak for small models (long-context degradation is well known in general, but rarely measured inside SWE trajectories). | Shorter transcripts, re-anchoring to the issue. (Folded into H2's issue-influence measure.) |
| A5 | The issue text is the right query | Untested for small models. | (Not pursued.) |
| A6 | One trajectory per attempt; append-only transcript | Convention. | (Not pursued.) |
| A7 | Tests are the verifier | Execution-free verifiers exist, but they are trained or rubric-based (R4P, Agentic Rubrics, DeepSWE-Verifier). | A zero-training likelihood verifier. -> H1 |
| A8 | The model that navigates is the model that edits | Convention. | Split roles across E4B, 26B and 31B. (Not pursued.) |
| A9 | Input and output tokens cost about the same (or input is cheaper only because of API pricing) | False on local hardware: prefill is compute-bound and batched, decode is memory-bandwidth-bound. *Speculation:* on an M5 Max, prefill is probably 10-50x faster per token than decode. **Measure this; do not assert it.** | Under a fixed time budget, "score K candidates" is much cheaper than "generate K candidates". This is the economic rationale for H1 and H3. |

---

## H1 (rank 1). "The small model recognizes far more than it generates": an execution-free likelihood verifier for repository patches

**(1) Phenomenon.** Agent design assumes the model's value lies in what it can *generate*. For small models, generation of a correct multi-hunk repository patch is rare, yet the model may still *assign* systematically higher issue-conditional likelihood to correct patches than to incorrect ones. If so, a small model's "verification competence" is much larger than its "generation competence". That is a generator-verifier gap measured with no training at all. Raw log-likelihood is a known poor ranker for code (see prior art), so the specific claim is that a **PMI-style normalisation** recovers the signal.

**(2) Hypothesis (quantitative, these are predictions).**
For SWE-bench Verified instances that have at least one resolved and one unresolved public agent patch, define the score
`S(patch) = [log p(patch | file context, issue) - log p(patch | file context, neutral/empty issue)] / n_tokens`
(domain-conditional PMI, Holtzman et al. 2021). Predictions:
- (a) Pairwise AUROC of S for resolved vs unresolved patches *within the same instance* is >= 0.65 for E4B and >= 0.70 for 31B dense.
- (b) Raw mean log-likelihood (no PMI) is within +/-0.05 of 0.5 AUROC, or below it.
- (c) Picking the top-S patch among the candidates for an instance resolves more instances than (i) a random candidate and (ii) the shortest candidate, by >= 10 points. Bonus comparison: the E4B-selected rate exceeds E4B's own generation resolve rate by a large factor. (Generation baseline is optional and can come from the literature or a tiny native run.)

**(3) Mechanism (why it might be true).** Scoring only needs the model to notice inconsistencies: a patch that touches the wrong symbol, contradicts the issue, or breaks local idioms. Generating needs a long, exact, error-free sequence to be produced. Errors compound in generation but not in scoring. PMI removes the "this diff looks like common code" fluency term, which otherwise rewards short, generic, wrong patches. That fluency term is the documented failure of raw likelihood ranking.

**(4) Prior art (all opened).**
- Holtzman et al., *Surface Form Competition* (domain-conditional PMI), https://arxiv.org/abs/2104.08315. This is the scoring trick. It was tested on multiple-choice NLP, not on code patches.
- *On LLMs' Internal Representation of Code Correctness*, https://arxiv.org/html/2512.07404v3. It uses 7-8B models on HumanEval and BigCodeBench, and finds that "intrinsic" likelihood ranking is inconsistent and sometimes below random. It does **not** study SWE-bench or repository patches, and it does not test PMI. This is the closest prior work. It is also a warning: raw likelihood fails, so the novelty depends on PMI with the issue as the conditioning variable.
- Execution-free SWE verifiers exist but are **trained or agentic**: R4P (https://arxiv.org/html/2510.22775v1) and Agentic Rubrics (https://arxiv.org/html/2601.04171v1). Neither is a zero-training likelihood scorer on a small local model.
- I found no paper that ranks SWE-bench agent patches by issue-conditional PMI. That is one search session, so this is honest uncertainty, not a guarantee.

**(5) Falsification.** The hypothesis is falsified if PMI AUROC is <= 0.58 for both E4B and 31B (with 95% CI including 0.5), or if PMI adds nothing over trivial features (patch length, number of hunks, which agent produced it) in a logistic regression.

**(6) Smallest convincing experiment.**
- *Data:* SWE-bench Verified issues and base-commit files from the public dataset, plus the GitHub repo checkouts needed only to read files (no Docker, no test runs). Candidate patches and resolved labels come from the SWE-bench `experiments` repo, https://github.com/SWE-bench/experiments.
  - **Risk to check first:** the page says per-instance `all_preds.jsonl` and logs live in the submitters' repos or in `s3://swe-bench-submissions/`, while only `results/` (the resolved IDs) is in-repo.
  - Choose about 8-12 diverse submissions with downloadable predictions.
  - Keep instances that have at least 2 distinct resolved and at least 2 distinct unresolved patches. Dedupe identical diffs.
  - Target 100-150 instances, about 6-8 patches each.
- *Context:* the issue text plus the pre-patch content of the files the patch touches (truncated windows around the hunks, so that every candidate in an instance shares a comparable context). Use the union of touched files per instance so that context does not leak which patch is right.
- *Scoring:* teacher-forced log-probs on the diff tokens under two prefixes, with and without the issue. Shared-prefix KV caching makes the per-candidate cost small.
  - Compute estimate (*speculative*): about 1,000 candidates x 2 conditions x about 5k prefix tokens (cached per instance) plus about 400 diff tokens. That is roughly 1-2M effective prefill tokens: under 1 hour for E4B, a few hours for 31B dense, and the 26B MoE in between.
- *Baselines:* random candidate, shortest patch, raw mean log-likelihood, raw sum log-likelihood, and an "agent-reputation" prior (the overall resolve rate of the submitting system).
- *Controls:*
  - **Memorization.** Gold patches for SWE-bench Verified are very likely in pretraining. Exclude the gold patch from candidates. Compute each candidate's similarity to gold (normalised edit distance) and report the PMI effect *partialled on gold-similarity*. If possible, replicate on 30-50 post-cutoff instances (SWE-bench-Live or SWE-rebench style) that use the same candidate-generation logic.
  - **Agent-style confound.** Run the analysis within agent family, or include agent identity as a covariate.
  - **Permutation test.** Shuffle issues across instances; AUROC should collapse to about 0.5.
- *Analysis:* within-instance pairwise AUROC with bootstrap CIs over instances; top-1 selection rate vs baselines; scale trend across E4B, 26B and 31B.

**(7) Implications if validated.**
- Small local models are better used as **judges/rankers in a generate-elsewhere-or-cheaply, verify-locally** loop. That loop is execution-free and needs no Docker, so it is practical exactly where SWE-bench execution is unreliable.
- It turns A9 (cheap prefill) into a design rule: spend local compute on scoring, not on decoding.
- It also gives a one-line, training-free reranker that any agent framework can adopt.

**Honest probability** that the effect is real and visible in one day: **about 45%** that PMI AUROC is at least 0.65 with a CI excluding 0.5 on one model; **about 25%** that it survives the gold-similarity partialling convincingly.
**Most likely hostile explanation:** "The model has memorised the gold patches. Resolved agent patches look like gold, so it is recall, not recognition." Second explanation: "It is patch length or style." The controls above target both. The partialled result is the one that matters.

---

## H2 (rank 2). "Small coding agents are open-loop": actions are nearly insensitive to the tool observations that are supposed to drive them

**(1) Phenomenon.** The observe-think-act loop assumes each action is a function of the latest observation. For small models, the next action may be mostly determined by the issue plus the model's habitual action sequence (ls, grep, open, edit). The observation would then contribute little beyond copying a token or two, such as a path or a line number. If so, the transcript is mostly paid-for but causally inert context, and failures come from the loop *not closing*, not from bad tools.

**(2) Hypothesis (predictions).** On Gemma's own SWE trajectories, define per-step **observation influence**
`I_obs(t) = log p(a_t | h_<t, o_t) - log p(a_t | h_<t, o'_t)`
where `a_t` is the action actually taken (tool name plus arguments), `o_t` is the real observation, and `o'_t` is a type-matched counterfactual observation (the same tool's output from a different instance in the same repo, or a "no matches" output).
- (a) For E4B, the median I_obs over the *action-type tokens* is < 0.5 nats. More than 50% of all steps have total |I_obs| < 1 nat.
- (b) Influence concentrates in argument tokens that are copy-able from the observation (paths, line numbers). The decision of *what kind* of action to take is barely influenced.
- (c) The 31B dense model shows at least 2x higher median I_obs than E4B, which gives a scale signature.
- (d) *Secondary:* issue influence `I_issue(t)` (issue text vs a shuffled issue) decays with step index t. Prediction: it falls by more than 50% from steps 1-3 to steps 10+ for E4B.

**(3) Mechanism.** Small models have strong action-format priors from instruction tuning and agent-trace data. Long verbatim tool outputs dilute attention. Copying is easier than conditioning a decision on content. Without RL on environment feedback, nothing forces the decision to depend on the observation.

**(4) Prior art (opened or seen).**
- *Spurious Tool Use* (Qwen2.5-7B, QA and math), https://www.alphaxiv.org/abs/2609.16268. It studies whether agents *call* tools for spurious cues, not whether their actions depend on tool *outputs*. Its authors note an agent may search and then ignore the result. It does not cover coding or step-level teacher-forced attribution.
- Search results (snippets only, not fully read): a 2026 EMNLP Findings paper corrupts observations in visual tool use and reports a policy/observation decoupling, https://aclanthology.org/2026.findings-emnlp.728.pdf. An ICML 2026 paper perturbs a tool output in HotpotQA ReAct, https://icml.cc/virtual/2026/77959.
- So the *general idea* that agents may ignore observations is in the air. My contribution would be (i) the coding/SWE domain, (ii) a **cheap teacher-forced causal measurement** that needs no reruns and no execution, and (iii) a scale curve on one model family. Novelty is moderate, not radical. Be upfront about this.

**(5) Falsification.** The hypothesis is falsified if the median I_obs on action-type tokens is at least 2 nats for E4B, and comparable to 31B. It is also falsified if counterfactual observations in "informative" steps (see control) change the action-type distribution substantially (for example, total-variation distance over the top-5 next action types > 0.3).

**(6) Smallest convincing experiment.**
- Generate about 40 trajectories per model (E4B and 31B; 26B optional) on SWE-bench Verified issues using **read-only native tools only**: ls, grep, open-file-window and a final edit proposal. No test execution is needed, because we measure the loop, not resolution. Cap trajectories at 15 steps.
  - *Speculative cost:* E4B at about 1-3 minutes per trajectory, so 1-2 hours; 31B is slower, so run 20-30 trajectories.
- Teacher-force each step under three conditions: real observation, type-matched counterfactual observation, and an empty observation. Reuse the cached prefix `h_<t`, so each condition costs one observation plus one action of prefill.
  - About 600 steps x 3 conditions: well under an hour per model (*speculative*).
- *Control for "the observation was uninformative anyway":* label "informative" steps automatically, for example a grep that returned 0 vs more than 0 hits, or an opened file that does or does not contain an identifier from the issue. Show that I_obs is low *even on informative steps*.
- *Control:* also score Gemma on public trajectories from strong agents (where SWE-bench experiments provide `trajs/`). This distinguishes "Gemma as a reader ignores observations" from "Gemma's own actions are uninformative".
- *Baseline for scale of effect:* I_issue at step 1 serves as an upper reference for how much a context segment can matter.

**(7) Implications.** If small agents are open-loop, then:
- Verbatim tool output is waste on local hardware.
- Better scaffolds should *force* the closure, for example by making the observation the immediate question ("Given this grep result, which file?") or by using structured or compressed observations.
- Pure "more steps" scaling is futile for small models.

The measurement itself, observation influence per step, is a general diagnostic for any agent.

**Honest probability:** **about 55%** that E4B shows clearly low observation influence on action types. **About 40%** that the scale contrast with 31B is clean within the day.
**Most likely hostile explanation:** "The action was already determined by sensible strategy. Low influence is correct behaviour, not a defect." The informative-step control is the answer, and it must be done well. Another hostile point: "the counterfactual observations are out-of-distribution." Use type-matched, same-repo outputs.

---

## H3 (rank 3). "Exploration destroys a correct prior": zero-shot file localization by scoring beats, or is abandoned by, the agent's own exploration

**(1) Phenomenon.** We assume exploration improves localization. A small model may already know, *as a prior*, which file is implicated (partly from memorisation, partly from naming conventions). Agentic exploration may then lead it *away* from that prior through distracting grep hits, long outputs, and premature commitment.

**(2) Hypothesis (predictions).**
- (a) For E4B, file-level acc@1 from **PMI scoring of every repo file path** given the issue (no code read, only the path list at the base commit) is at least as high as the acc@1 of the file the E4B agent finally edits or names.
- (b) A **prior-abandonment rate**: among instances where the zero-shot top-1 file is correct, the agent ends on a wrong file in at least 25% of cases. Abandonment exceeds rescue (zero-shot wrong, agent right).
- (c) A crossover with scale: for 31B, the agent beats zero-shot.

**(3) Mechanism.** The parametric prior is compact and undistracted. Exploration adds noisy evidence the small model weighs poorly (see H2), and grep hits on generic identifiers pull it toward test files or utility modules.

**(4) Prior art (opened).**
- *The SWE-Bench Illusion*, https://arxiv.org/html/2506.12286v4. Ten closed frontier models identify buggy file paths from issue text alone at up to 76% on Verified. That is framed as **memorisation**. It includes no small open models and no comparison against agentic localization.
- Agentless (localize without free exploration; I saw it in search results, did not reopen): https://arxiv.org/abs/2407.01489.
- Retrieval-based localizers (SWERank) are strong at small scale.
- **What is new here:** the *within-model* comparison of the prior against exploration, the abandonment/rescue decomposition, and the scale crossover. The prior itself is not new.
- Because of the SWE-Bench Illusion, a reviewer will say the "prior" is memorisation. Report that openly. The claim is about the *agent's failure to use what the model already knows*, whatever the source.

**(5) Falsification.** The hypothesis is falsified if E4B agent acc@1 exceeds zero-shot acc@1 by more than 10 points (CI excluding 0) and abandonment is < 10%.

**(6) Smallest experiment.**
- Zero-shot step: use 150 Verified instances. Take the base-commit file lists (git ls-tree, Python files only). Score each path under issue vs no-issue using a shared-prefix cache. With about 1,000 paths of about 15 tokens each, that is about 15k tokens per instance (cheap, under 30 minutes for E4B; *speculative*).
- Agent step: the same read-only E4B agent as in H2 on 60-100 instances. This can be **shared with H2**.
- Gold file: files touched by the gold patch.
- Post-cutoff replication on a small fresh set, if one can be obtained, to separate memorisation from inference.
- Baselines: BM25 over file contents, and path-string overlap with the issue.

**(7) Implications.** "Ask the prior first, explore only to verify" would be the right policy for small models. It is cheap, it composes with H1, and it argues against copying cloud-agent exploration budgets onto local models.

**Honest probability:** **about 40%** that zero-shot is at least as good as the agent for E4B. **About 60%** that the abandonment rate is notable (at least 20%). The headline might be "abandonment" rather than "zero-shot wins".
**Most likely hostile explanation:** "Zero-shot wins only because of SWE-bench memorisation. On fresh repos, exploration would win." Without a post-cutoff set this cannot be fully rebutted, which is why H3 ranks third.

---

## Ranking rationale

1. **H1** is the most general and practical ("small models recognize more than they generate"). It runs entirely on public artifacts, with no execution, and is fastest to compute. Its main risk is memorisation, which can be partly controlled.
2. **H2** is the purest inversion of the loop assumption and is cheap via teacher forcing. The novelty is moderate because "agents ignore observations" is being studied in non-coding settings.
3. **H3** is cheap and intuitive, but the closest prior art (SWE-Bench Illusion) already covers the zero-shot half, and the memorisation confound is hardest to rule out.

**Combined plan (if one wants a single paper):** H1 as the headline. The H3 zero-shot path scoring and the measured prefill/decode speed ratio (A9) are supporting evidence for a "score, don't generate" thesis. H2 is a stretch goal if the trajectories exist.

**First-hour de-risking checklist:**
- (i) Verify that candidate patches are actually downloadable for at least 8 Verified submissions.
- (ii) Measure Gemma prefill vs decode tokens/s on the M5 Max.
- (iii) Pilot H1 on 15 instances. Stop or switch to H2 if PMI AUROC is under 0.55.
