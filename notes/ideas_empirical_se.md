# Hypotheses from the empirical SE / program comprehension lens

Author role: independent scientist (empirical SE, program comprehension, cognitive science lens)
Date: 2026-11-11. Constraint: decisive experiment in ~8 h on one M5 Max (64 GB), local Gemma 4 inference only, no Docker test execution.

Conventions: "[verified]" = I opened the source in this session. "[not opened]" = classic reference cited from memory; check before citing. "SPECULATION" marks claims I have not checked.

Shared data assets (all public, no execution needed):
- SWE-bench Verified (500 instances: issue text, base commit, gold patch, test patch).
- SWE-bench `experiments` repo: per-submission `results/` (resolved instance IDs) and pointers to `all_preds.jsonl` (patches) and `trajs/` (trajectories). [verified] https://github.com/SWE-bench/experiments. Note the repo now says it "holds entries, not artifacts", so patches/trajectories must be fetched from submitter-hosted locations via `python -m analysis.download_logs`. **Budget 1-2 h for the download; some links may be dead.**
- Git histories of the 12 Verified repositories (clone once, a few GB in total).
- Local Gemma 4 E4B / 26B-MoE / 31B with teacher-forced log-probs.

---

## Ranking

1. **H1: Co-change blindness.** Agents' missed edit sites can be predicted from version-history change coupling, and the effect is stronger for small models. Best mix of novelty, generality and verifiability, and it leads directly to a fix.
2. **H2: The scent gradient.** Small-model agents forage by lexical scent, so their gap to frontier models grows as the issue's information scent falls. Very cheap to run and likely to show an effect, but it is less novel and has a memorization confound.
3. **H3: The naturalness inversion.** Wrong agent patches are *more* natural than correct ones under a small LM. This is the most surprising of the three if it holds and it uses log-probs, but it is the most likely to come out null.

---

## H1: Co-change blindness (an "omission law" for agent patches)

**(1) Phenomenon.** Two decades of mining-software-repositories work show that changes propagate along *evolutionary* coupling. Files and functions that changed together in the past tend to change together again. ROSE (Zimmermann et al., ICSE 2004 / TSE 2005) warns a developer who "missed a related change". [verified abstract page] https://www.st.cs.uni-saarland.de/softevo/changes.php?lang=fr. LLM agents never look at this signal. They localize from the issue text, the code and sometimes the static call graph. Studies of agent failures repeatedly name *incomplete repair* (the agent fixes the primary site and misses a dependent one) as a major failure class, especially on multi-file tasks. See "An Empirical Study on Failures in Automated Issue Solving" [verified search summary] https://arxiv.org/html/2509.13941v1. None of these studies asks whether the *specific* missed site was predictable from history.

**(2) Hypothesis (quantitative).** Take SWE-bench Verified instances whose gold patch touches ≥2 files or ≥2 top-level functions/methods. For each agent patch, let E be the edited entities and G the gold entities.
- (a) Among unresolved patches, "strict-omission" patches (E ∩ G ≠ ∅ and G \ E ≠ ∅) make up ≥30% of unresolved patches in this multi-site subset.
- (b) Mine change coupling only from commits *before* the base commit and seed it with E ∩ G. A ROSE-style confidence ranking then places a missing gold entity in its top-3 for ≥40% of omissions. This beats each of three baselines (same-directory/same-class, static import/call neighbours, BM25 against the issue text) by ≥10 percentage points of top-3 recall.
- (c) The omission share of failures is higher for small open-weight agents (≤32B: e.g. SWE-smith/SWE-Gym-style 7-32B submissions, and Gemma itself) than for frontier agents, by ≥1.5x.
- (d) A local localization-only experiment gives Gemma 4 the issue plus the first correctly edited file and asks which other entities must change. Adding a "historically co-changed with" list of 5 entries raises recall of the missing gold site by ≥10 points for E4B, with a smaller gain for 31B.

**(3) Mechanism.** Co-change captures *latent, non-syntactic* dependencies: parallel implementations (backend A/B), docs and changelog paired with code, serializer/deserializer pairs, `__init__` exports, sibling subclasses that must stay consistent. These are invisible to call graphs and only weakly cued by issue text. Small models have less capacity to infer them from code reading within a limited context, so they stop at the first site that has scent. In foraging terms, they leave the "patch" too early because they have no scent leading to the next one.

**(4) Prior art and difference.**
- Wang et al., "Improving Code Localization with Repository Memory" (ICLR 2026) gives LocAgent tools that retrieve recent commits, linked issues and summaries of actively changing code. [verified abstract] https://arxiv.org/abs/2510.01003. As far as the abstract says, this is commit/issue *retrieval* and hot-spot summaries. It does not test an explicit file-pair or function-pair co-change model, and it does not study *omissions* in published agent patches. **This is the closest prior art and a reviewer will raise it.** Our contribution is different in kind: an offline *diagnostic law* over thousands of published patches from many agents, the test of whether *specific omitted sites* can be predicted from history, and a model-size interaction.
- Failure taxonomies (arXiv 2509.13941 above; CHAINSWE's "undershoot", SWE-Bench ProMax's "incomplete refactoring", seen in search results) describe omission qualitatively. None tie it to evolutionary coupling.
- TRAJEVAL (arXiv 2603.24631) [verified abstract] reports that 60-69% of failures of capable models reach and edit the correct functions but produce wrong patches. That is consistent with this hypothesis: some of these "edit-quality" failures could be omissions of a *second* site.
- Honest assessment: the ingredients are old (ROSE). The new parts are measuring agents with them, the size interaction, and turning it into a cheap tool for local agents.

**(5) Falsification.**
- Strict omissions are <15% of multi-site failures.
- OR co-change top-3 recall on omitted entities does not beat the static-neighbour and same-directory baselines (difference <5 points, CI including 0).
- OR there is no size gradient in omission share.

**(6) Smallest convincing experiment.**
- *Step A (0 LLM compute, ~3 h including downloads):*
  - Parse gold patches and `all_preds.jsonl` for ~20-40 Verified submissions covering a range of model sizes. Map hunks to files and enclosing functions (Python `ast` at the base commit).
  - Compute strict-omission rates by submission.
  - Mine co-change with `git log --name-only` (file level) and diff-hunk→function mapping (function level) on commits strictly before each base commit. Cap at 5k commits and drop commits touching >30 files (standard MSR noise filter).
  - Report top-k recall of the omitted entities against the baselines, with a bootstrap over instances (instances are the unit, not patches).
- *Step B (Gemma, ~2-3 h):*
  - Run localization-only prompts on the ~60-150 multi-site instances × {E4B, 31B} × {no hint, co-change hint, placebo hint = same-directory list of the same length}.
  - Score recall of missing gold entities.
  - Rough cost (SPECULATION, measure first): ~4k-token prompts and short outputs. On MLX 4-bit, expect E4B at ~1 s and 31B at ~5-10 s per prompt, so ~300 prompts per config is well under 1 h each.
- Controls:
  - Placebo hint of equal length.
  - Instance fixed effects (conditional logit) so that "harder instances are multi-file" does not drive the result.
  - Exclude test, docs and changelog files from G in the main analysis and report them separately.
- Caveat: SWE-bench Verified is mostly single-file gold patches (check the exact share). Function-level multi-site inflates N; it may still be only ~100-200 instances. Report CIs honestly.

**(7) Implications if validated.** This would give a concrete, nearly free tool for local agents: a `git log`-derived "you edited X; historically X co-changes with Y (conf 0.7)" check at submit time, which is ROSE revived as an agent guardrail. It also makes a general point. Repository *history* is a source of knowledge that is orthogonal to model scale, so it should help small models most. That supports building local agents around "MSR priors" rather than around larger context windows.

**Probability** the effect is real and visible in one day: **0.55**. Probability it beats static-dependency baselines by the stated margin: **0.35**.

**Hostile reviewer's simpler explanation:** "Co-change is just a noisy proxy for module structure or imports, and omitted files are simply the ones in the same package." This is addressed by the same-directory and static-neighbour baselines plus a partial-effect regression. Second objection: "omission is just difficulty". This is addressed with instance fixed effects and within-instance comparison across agents.

---

## H2: The scent gradient (small models forage by lexical scent)

**(1) Phenomenon.** Information foraging theory (Pirolli & Card; applied to debugging by Lawrance, Burnett et al.) [not opened] says programmers navigate by *scent*: lexical cues linking the goal (the bug report) to code. Experts can also navigate by structural and semantic knowledge when scent is weak; novices cannot. The analogous claim for LLM agents is untested: **small-model agents are "novices" whose localization collapses when scent is low, while frontier agents degrade much less.** Aggregate resolve rates hide this.

**(2) Hypothesis.** Define per-instance scent S as the rank of the gold file under BM25 with issue text as query over all repository `.py` files. Secondary S': the fraction of identifiers in gold hunks (function/class names) that appear in the issue text.
- (a) Fit a mixed logistic model, resolved ~ log-rank(S) × model-size class + (1|instance-difficulty proxies), over all Verified submissions. The scent slope (log-odds per unit log-rank) is ≥1.5x steeper for ≤32B open-weight agents than for frontier agents.
- (b) For Gemma 4 E4B localization-only (issue + repository file list → top-5 files), BM25 rank explains most of the variance. After controlling for log BM25 rank, the partial association between Gemma's correctness and the "semantic-only" instance features is ~0, whereas Gemma 31B retains a positive residual. Prediction: E4B top-1 accuracy on the lowest-scent quartile is ≤ BM25's own top-1 accuracy in that quartile + 5 points.

**(3) Mechanism.** Small models have weaker world-models of the repository's architecture, both from fewer parameters and from weaker memorization of these repos. Their tool calls (grep/find) are seeded by surface tokens from the issue, so localization reduces to lexical retrieval. Frontier models can make multi-hop inferences ("this error message is raised in the validator, so the root cause is in the field class"), which is the expert's structural navigation.

**(4) Prior art and difference.**
- "The SWE-Bench Illusion" (Liang et al., NeurIPS 2025) shows models can name the gold file from issue text alone at ~76% on Verified versus ~53% on outside repos, attributing the gap to memorization. [verified] https://arxiv.org/html/2506.12286v1
- "Does SWE-Bench-Verified Test Agent Ability or Model Memory?" (arXiv 2512.10218) reports similar results. [seen in search results, not opened]
- ContextBench (arXiv 2602.05892) annotates gold context and retrieval recall. [seen in search results]
- Agentless and many others use BM25-style retrieval as a stage. None of these reports a **model-size × scent interaction** or frames small-model failure as scent dependence. The foraging framing exists for web QA (InForage, NeurIPS 2025; https://arxiv.org/html/2505.09316v2, seen) but not, as far as my searches found, for code agents.
- Honest assessment: lexical-overlap stratification is an obvious analysis, and someone may have done it inside a larger paper. Novelty is moderate.

**(5) Falsification.**
- Equal scent slopes across size classes (interaction CI includes 0).
- OR E4B beats BM25 by >15 points in the low-scent quartile.

**(6) Experiment.**
- *Step A (0 LLM compute, ~1.5 h):*
  - BM25 over each base-commit snapshot. Use `git archive` per base commit: 500 snapshots is heavy, so cache by (repo, nearest release tag) as an approximation and check it on a sample.
  - Join with `results/` resolved lists for all Verified submissions. This needs only resolved IDs, not patches, so it avoids the artifact download problem entirely.
  - Fit the interaction model.
- *Step B (~2 h):* Gemma E4B / 26B-MoE / 31B localization-only on all 500 instances with the file list. File lists for django and sympy are long, so truncate to the top-200 by BM25 plus 50 random files. This keeps prompts ~6-8k tokens. Compare with the BM25 baseline by quartile.
- Memorization control (important): run a "repo-name + issue only, no file list" probe à la SWE-Bench Illusion. Report the scent slope separately for instances where Gemma can and cannot name the file without context. Optionally add 30-50 post-cutoff issues from the same repos' recent history (gold = merged PR files) as an uncontaminated slice.

**(7) Implications.** Local agents should *route by scent*. When the issue has strong scent, a cheap E4B loop suffices. When scent is weak, spend compute on non-lexical localization (pre-LLM SBFL from a reproduction test, co-change from H1, call-graph expansion) or escalate to the 31B. This gives a principled, measurable "when is a small model enough?" criterion, computable *before* running the agent.

**Probability** real and visible: **0.65**. Probability it is seen as novel enough: **0.4**.

**Hostile simpler explanation:** "Low scent just means hard instance. Every model degrades, and differences in slope are a ceiling/floor artifact of the logit scale." Mitigate with log-odds and ratio-scale reporting plus instance random effects. The second objection, "this is memorization, not foraging", needs the contamination probe above.

---

## H3: The naturalness inversion (wrong agent patches are too natural)

**(1) Phenomenon.** Ray, Hellendoorn et al. ("On the 'Naturalness' of Buggy Code", ICSE 2016) found that buggy lines are more entropic and that fixes reduce entropy. [verified] https://arxiv.org/pdf/1506.01159. Yang et al. turned this into *entropy-delta* for ranking template-based APR patches, with large gains. [verified] https://arxiv.org/abs/2404.15236. Both assume that natural means correct. For LLM-generated patches this assumption may *invert*. LLM agents produce the *modal* fix, while real fixes on mature repositories often need project-specific, low-probability tokens (an internal helper, an unusual flag, a precise edge-case condition). If so, low surprisal under a small LM marks a *plausible-but-wrong* patch. That would be a "plausibility trap" that explains why self-consistency and likelihood reranking plateau for small models.

**(2) Hypothesis.** Score added/changed lines under Gemma 4 E4B with teacher forcing, conditioned on the issue text and ±60 lines of surrounding base-file context. Take the mean NLL per token over added tokens and the entropy-delta.
- (a) Within instance, gold patches have higher mean added-token NLL than unresolved agent patches in ≥60% of instances.
- (b) Within-instance AUC for resolved vs unresolved agent patches is <0.45 (i.e., *lower* NLL predicts *failure*), after residualizing on added-token count and edit size.
- (c) The inversion is stronger when the scorer is the same family/size as the generator (self-naturalness). Testable only if we generate Gemma patches; optional.
- Direction is pre-registered as the inversion. The opposite result, natural = correct (AUC >0.55), would replicate Yang et al. on agentic patches. That result is useful as a free verifier for local agents, but it is not the claimed phenomenon.

**(3) Mechanism (SPECULATION).** Agents generate by sampling near the mode of p(code | context). Correct fixes encode information *missing* from the local context (the issue's hidden constraint, which is why the bug exists). Mutual-information arguments then suggest the correct fix has higher conditional surprisal than a "generic" fix. Pre-LLM n-gram findings were about *bugs* being unnatural relative to the corpus, not about *competing fixes*. The two can coexist.

**(4) Prior art and difference.**
- Entropy-delta (Yang et al., ICSE 2025, above) and Ray et al. (above).
- Test-free verifiers on SWE-bench Verified such as R4P (arXiv 2510.22775) report ~72% accuracy using a trained reasoning verifier. [seen in search results, not opened in full]
- "Are 'Solved Issues' in SWE-bench Really Solved Correctly?" (arXiv 2503.15223) shows ~7.8% of "resolved" patches fail the developer tests. [seen in search results]
- I found no study scoring *agent* patches on SWE-bench by LM surprisal and asking about direction or inversion. Novelty is moderate to high *if* the inversion holds. If the result is just "natural = correct", it is incremental over entropy-delta.

**(5) Falsification.** Within-instance AUC between 0.45 and 0.55 with a tight CI (no signal), or >0.55 (no inversion). Either way, report it. A null result is a useful negative for "likelihood reranking in local agents".

**(6) Experiment.**
- Data: ~150 Verified instances that have ≥2 resolved and ≥2 unresolved agent patches across submissions. Up to 8 patches per instance plus gold, giving ~1,300 scorings.
- Scoring: each scoring is ~2.5-3.5k tokens (issue + local context + hunk), ~4M tokens in total. E4B prefill on MLX (SPECULATION: 1-3k tok/s) takes ~0.5-1.2 h. Rerun with 31B on a 40-instance subset (~1-2 h) to check the scale-dependence of the inversion.
- Controls:
  - Length residualization.
  - Exclude whitespace/comment-only changes.
  - Compare patches *within instance* (conditional logistic or paired AUC).
  - Shuffle control: score each patch against the wrong instance's issue, which should remove the issue-conditioning component.
  - Label noise: drop instances with known weak tests (per 2503.15223) if the list is available.
- No execution needed.

**(7) Implications.** If inverted, likelihood-based self-selection (best-of-n by log-prob, "pick the most confident patch") is *harmful* for local agents. Selection should instead favour patches that add the *information* the issue demands. The paper's line would be "surprise is a feature, not a bug". If not inverted, entropy-delta becomes a free, offline patch reranker for local agents, and Gemma E4B becomes a verifier for 31B.

**Probability** of the inversion being real and visible: **0.25**. Probability of *some* significant signal in either direction: **0.5**.

**Hostile simpler explanation:** "Unresolved patches are longer/boilerplate-heavy, and boilerplate is low-NLL." This is the reason for length and token-type controls. A second objection, "gold patches look unnatural because the model memorized the *post-fix* code", actually predicts the opposite direction, which helps interpretation.

---

## Also considered (not ranked)
- **First-scent anchoring / marginal value theorem in trajectories.** Agents over-stay in the first file they open. The fraction of trajectory steps spent in the first non-gold file before leaving would predict failure, and small models would leave patches later than MVT predicts. Trajectory formats in `experiments` are heterogeneous (no fixed format required), which makes parsing too slow for one day. It partially overlaps TRAJEVAL's search/read/edit decomposition.
- **FixCache for agents.** The prior bug-fix density of a file predicts agent localization success beyond lexical scent. It is cheap, but probably dominated by H2's memorization confound (frequently fixed files are well represented in pretraining).

## Recommended plan for the 8-hour budget
Run H1-A and H2-A first (pure data, no LLM, ~4 h including downloads; H2-A needs only resolved-ID lists, so start it immediately). Then spend the Gemma budget on H1-B (the co-change hint ablation). Run H3 with E4B only if time remains, since it is a single 1-h scoring job. H1 gives the paper its "law + tool" contribution, H2 gives the generality and model-size story, and H3 is a high-variance bonus.

## Sources opened or seen in this session
- https://github.com/SWE-bench/experiments (opened)
- https://arxiv.org/abs/2510.01003 (opened abstract: Repository Memory, ICLR 2026)
- https://arxiv.org/abs/2603.24631 (opened abstract: TRAJEVAL / Coherence Collapse)
- https://arxiv.org/html/2509.13941v1 (search summary: failures in automated issue solving)
- https://arxiv.org/html/2506.12286v1 (search summary: SWE-Bench Illusion)
- https://arxiv.org/abs/2404.15236 (search summary: entropy-delta)
- https://arxiv.org/pdf/1506.01159 (search summary: naturalness of buggy code)
- https://www.st.cs.uni-saarland.de/softevo/changes.php?lang=fr (search summary: ROSE)
- https://arxiv.org/html/2505.09316v2 (search result: InForage)
- https://arxiv.org/html/2510.22775v1, https://arxiv.org/abs/2503.15223, https://arxiv.org/html/2602.05892, https://arxiv.org/html/2512.10218v1 (search results only; verify before citing)
