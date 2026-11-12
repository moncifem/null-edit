# Frontier map: agentic SWE with small local models (compiled 2026-11-11)

Convention: every entry below was opened this session (arXiv abstract page or README/site) unless marked NOT VERIFIED. Findings are from abstracts/pages only, not full-text reading; per-entry limitations marked "(mine)" are my inference, not the authors' claim. Gaps in coverage are listed at the end.

## A. SWE agents and benchmarks

- A1. Jimenez et al., Oct 2023. SWE-bench: 2,294 real issues from 12 Python repos; Claude 2 solved 1.96%. https://arxiv.org/abs/2310.06770 . Limitation: Python-only, 12 repos; test-based grading (see C).
- A2. Yang et al., May 2024. SWE-agent: custom agent-computer interface; 12.5% pass@1 on SWE-bench (then SOTA). https://arxiv.org/abs/2405.15793 . Limitation (mine): tuned for frontier models' tool formats.
- A3. Xia et al., Jul 2024. Agentless: fixed 3-phase pipeline (localize, repair, validate) solved 32.0% of SWE-bench Lite at ~$0.70/issue, no agent loop. https://arxiv.org/abs/2407.01489 . Limitation: Lite only in abstract.
- A4. Wang et al., Jul 2024. OpenHands platform (sandbox, browsing, multi-agent), 15 benchmarks. https://arxiv.org/abs/2407.16741 . Limitation: a platform paper; abstract gives no isolated small-model numbers.
- A5. Zhang et al., Apr 2024. AutoCodeRover: AST-aware code search, 19% on Lite, ~$0.43/issue. https://arxiv.org/abs/2404.05427 . Limitation: early, low absolute numbers.
- A6. Moatless Tools (aorwall), GitHub README. Argues for good context-insertion tools over agent reasoning. Lists "Verified Mini" (50 instances) scores incl. qwen-2.5-coder-32b-instruct 32%, gpt-4o-mini 16%, llama-3.1-405b 28%. https://github.com/aorwall/moatless-tools . Limitation: n=50, README, not peer reviewed.
- A7. mini-SWE-agent (SWE-agent team), README: ~100-line bash-only agent, claims >74% SWE-bench Verified (with strong models); no local-model numbers on the page. https://github.com/SWE-agent/mini-swe-agent
- A8. SWE-bench Multilingual site: 300 tasks, 42 repos, 9 languages; Claude 3.7 + SWE-agent got ~43% vs 63% on Verified. https://www.swebench.com/multilingual.html . Limitation: single model evaluated on that page.
- A9. Zan et al., Apr 2025. Multi-SWE-bench: 1,632 expert-annotated instances in 7 languages, plus 4,723 RL instances. https://arxiv.org/abs/2504.02605
- A10. Deng et al., Sep 2025. SWE-Bench Pro: 1,865 problems, 41 maintained repos, long-horizon. https://arxiv.org/abs/2509.16941 . Fetched page gave no solve rates.
- A11. Pan et al., Dec 2024. SWE-Gym: trained agents gain up to 19 points absolute; with verifier 32.0% Verified / 26.0% Lite. https://arxiv.org/abs/2412.21139
- A12. Yang et al., Apr 2025. SWE-smith: 50k instances from 128 repos; SWE-agent-LM-32B 40.2% pass@1 Verified. https://arxiv.org/abs/2504.21798
- A13. Jain et al., Apr 2025. R2E-Gym: procedural environments; hybrid verifiers reach 51% Verified (open weights). https://arxiv.org/abs/2504.07164
- A14. Wei et al., Feb 2025. SWE-RL: Llama3-SWE-RL-70B 41.0% Verified with rule-based similarity reward; RL generalized better than SFT. https://arxiv.org/abs/2502.18449
- A15. Together AI, Jul 2025 (blog). DeepSWE: Qwen3-32B trained by RL only on 4,500 R2E-Gym tasks; 42.2% pass@1, 59% with Best@16 hybrid test-time scaling. https://www.together.ai/blog/deepswe . Limitation: blog, not peer reviewed.
- A16. Kon et al., Feb 2026. SWE-Protege: Qwen2.5-Coder-7B post-trained reaches 42.4% Pass@1 Verified using ~4 expert calls/task; states small models show "pervasive action looping". https://arxiv.org/abs/2602.22124 . Limitation: depends on an expert model; needs training.

### Gemma-specific / small-local numbers (published)
- Google Gemma 4 model card (https://ai.google.dev/gemma/docs/core/model_card_4): E2B 2.3B effective, E4B 4.5B effective (8B with embeddings), 26B A4B (25.2B total, 3.8B active), 31B dense; ctx 128K (E2B/E4B), 256K (26B/31B). LiveCodeBench v6: 31B 80.0, 26B 77.1, E4B 52.0, E2B 44.0. Codeforces ELO 2150/1718/940/633. **No SWE-bench number on the card.**
- A web search surfaced an uncorroborated blog claim (contracollective.com) of "61.2% SWE-bench Verified" for a "Gemma 4 27B" (no such size on the model card). NOT VERIFIED; treat as unreliable. Another blog says Google omits SWE-bench rows for 12B/26B/31B (not opened).
- Practitioner feasibility test (ai-muninn.com, 2026-04-13, 1 task per pair, n=1, not a SWE-bench task): Gemma 4 26B on OpenHands (function calling) never finished, 40+ "missing required parameters" tool-call errors with the gemma4 parser/official template; on SWE-agent (plain-text actions) it submitted a patch in 9 steps. https://ai-muninn.com/en/blog/swe-bench-local-models-framework-matters . Anecdotal.
- Other <=32B numbers above: SWE-agent-LM-32B 40.2 (A12), DeepSWE-32B 42.2 (A15), SWE-Protege-7B 42.4 (A16), SWE-Fixer (Qwen-based) 30.2 Verified (B3), Qwen2.5-Coder-32B CoSIL localization 44.6% top-1 Verified (B5). All involve fine-tuning; **I found no published zero-shot, no-fine-tune Gemma 3/4 SWE-bench result.**

## B. Localization

- B1. Chen et al., Mar 2025. LocAgent: graph-guided agent; fine-tuned Qwen2.5-Coder-32B reaches 92.7% file-level accuracy, ~86% cheaper than proprietary. https://arxiv.org/abs/2503.09089 . (LocBench not mentioned on the abstract page; not verified.)
- B2. Ouyang et al., Oct 2024. RepoGraph: repo-level code graph plugin improves 4 methods on SWE-bench. https://arxiv.org/abs/2410.14684
- B3. Xie et al., Jan 2025. SWE-Fixer: separate retrieval and edit models; 22.0% Lite / 30.2% Verified (32.8% with PASS_TO_PASS filter); two model calls per issue. https://arxiv.org/abs/2501.05040
- B4. Yu et al., Feb 2025. OrcaLoca: 65.33% function match on Lite; +6.33 pts resolve rate. https://arxiv.org/abs/2502.00350
- B5. Jiang et al., Mar 2025. CoSIL: training-free iterative code-graph search; 43.3% Top-1 (Lite) / 44.6% (Verified) function-level with Qwen2.5-Coder-32B. https://arxiv.org/abs/2503.22424
- B6. Majgaonkar et al., Oct 2025. Success/failure trajectories of OpenHands, SWE-agent, Prometheus: problematic files found in 72-81% of trajectories even among failures, so repair, not navigation, dominates for those agents. https://arxiv.org/abs/2511.00197 . Limitation: strong models; file-level granularity.
- B7. SWE-smith (A12), per search snippet of its paper (not read in full): ~53% of SWE-agent-LM-32B failures linked to localization/looping; >25% trajectories have a repeated sequence of length >=10 vs <4% for Claude 3.7. Unverified detail from search snippet; abstract page confirms only the headline score.
- Not covered: SWE-bench BM25 RAG baselines (in A1, numbers not extracted), LocBench dataset. Mark NOT VERIFIED.

## C. Failures, long-horizon, contamination

- C1. Aleithan et al., Oct 2024. SWE-Bench+: 32.67% of successful patches had solution leakage, 31.08% passed via weak tests; SWE-agent+GPT-4 fell 12.47% to 3.97% after filtering. https://arxiv.org/abs/2410.06992
- C2. Yu et al., Jun 2025. UTBoost: insufficient tests in 36 instances, 345 wrongly-passing patches; affects 40.9% of Lite and 24.4% of Verified leaderboard entries. https://arxiv.org/abs/2506.09289
- C3. Liang et al., Jun 2025. SWE-Bench Illusion: models identify buggy file paths from issue text alone up to 76% (53% on non-SWE-bench repos); 5-gram match up to 35% vs 18% elsewhere. https://arxiv.org/abs/2506.12286 . Limitation: suggestive of memorization, not proof.
- C4. Kwa et al. (METR), Mar 2025. 50% time horizon; doubling ~7 months. https://arxiv.org/abs/2503.14499
- C5. Ord, May 2025. Constant per-minute failure rate -> exponential decay, "half-life" per agent. https://arxiv.org/abs/2505.05115 . Limitation: one task suite.
- C6. Liu et al., Jul 2023. Lost in the Middle: accuracy highest when evidence is at start/end of context. https://arxiv.org/abs/2307.03172 . Pre-dates agentic long contexts.
- C7. Hong, Troynikov, Huber (Chroma), Jul 2025. Context Rot: across 18 LLMs reliability degrades with input length even on simple tasks; distractors compound it. https://www.trychroma.com/research/context-rot . Technical report, not peer reviewed; not coding-specific.
- C8. Liu et al., Sep 2025. Failures in automated issue solving: 150 failed Verified attempts; most agentic failures from flawed reasoning and "cognitive deadlocks"; supervisory Expert-Executor solves 22.2% of previously unsolved. https://arxiv.org/abs/2509.13941
- C9. Mehtiyev & Assuncao, Apr 2026. 9,374 trajectories, 19 agents: trajectory length-failure correlation reverses once difficulty controlled; gather-context-then-validate behaviors predict success; LLM, not framework, is primary driver. https://arxiv.org/abs/2604.02547
- C10. Jain, Oct 2026. "Beyond Benchmarks": small quantized open workers passed 0/45 (Qwen3-Coder 30B-A3B) and 12/45 (Nemotron Cascade 2) on a 15-task suite; endpoints differ in tool-call formatting, caching, reliability. https://arxiv.org/abs/2610.34241 . Limitation: small custom suite, studies not pooled.
- C11. Karmakar & Chatterjee, May 2026. AgentFloor: 16 open models (0.27-32B) vs GPT-5 over 16,542 runs; best open model matches GPT-5 in aggregate, gap is long-horizon planning. https://arxiv.org/abs/2605.00334 . Not coding-specific.
- NeurIPS 2026 listing "The Parser Is Part of the Agent" (silent tool-call repair): seen only in a search result, NOT VERIFIED.

## D. Verification / selection

- D1. Ehrlich et al., Jan 2025. CodeMonkeys: 57.4% Verified for ~$2,300; selecting among existing top submissions 66.2%. https://arxiv.org/abs/2501.14723
- D2. Mundler et al., Jun 2024. SWT-Bench: generated reproduction tests double SWE-agent precision as a patch filter. https://arxiv.org/abs/2406.12952
- D3. Ahmed et al., Feb 2025. Otter: issue-to-test generation with rule checks and self-reflective planning. https://arxiv.org/abs/2502.05368
- D4. R2E-Gym hybrid verifier (A13): execution-based and execution-free each plateau ~42-43%, combined 51%.
- D5. SWE-Gym verifiers (A11) and DeepSWE Best@16 (A15) show large gains from selection.
- D6. Agentless (A3) uses regression + reproduction tests with majority voting/reranking.
- NOT VERIFIED / not opened: OpenHands critic model; LLM-as-judge for patches papers.

## E. Local inference economics

- E1. Shkolnikov, Feb 2026. Persistent Q4 KV cache for multi-agent edge inference (Apple M4 Pro): cache restore cuts TTFT 22-136x (Gemma) at 4-32K; re-prefill 15.7 s/agent at 4K; Q4 fits 4x more contexts. https://arxiv.org/abs/2603.04428 . Limitation: multi-agent switching, not a single coding agent loop.
- E2. Rajesh, Oct 2025. MLX vs MLC-LLM vs Ollama vs llama.cpp vs PyTorch MPS on M2 Ultra (Qwen2.5, prompts up to 100K): MLX best sustained decode, MLC lower TTFT at moderate prompts; abstract lacks numbers. https://arxiv.org/abs/2511.05502
- E3. Search-snippet-only (not opened, NOT VERIFIED): vLLM-metal blog, oMLX SSD-cache test, BaseRT paper.
- Gap: I found no paper arguing agent design should explicitly change for local models because prefill dominates; E1 and C10 are closest.

## Anomalies and open questions

1. No published zero-shot Gemma 4 SWE-bench number; the model card reports LiveCodeBench but not SWE-bench, and the only figure seen is an unreliable blog (A, Gemma section). A one-day mini-SWE-agent run of E4B/26B/31B on a Verified subset is itself a novel data point.
2. Competence on competitive coding does not transfer to repo agents: Gemma 4 31B LiveCodeBench 80 vs E4B 52 (model card), yet small workers get 0/45 in C10. How steep is the capability cliff by size in an identical harness?
3. Harness matters more than may be assumed: same Gemma 4 26B failed in OpenHands (function calling) but succeeded in SWE-agent (text actions) (ai-muninn post, n=1) and C10 says endpoints differ in tool-call formatting. Probe: text-action vs native tool-call on identical tasks. Contrast with C9 that the LLM dominates over framework for strong models; maybe reverses for small ones.
4. Localization vs repair is contradictory: B6 (72-81% file localization even in failures, repair dominates) vs B7/A12 (localization/looping dominates for a 32B small model). Not measured in a single controlled comparison across sizes. Probe: score file/function localization separately from patch correctness for E4B/26B/31B.
5. Looping/repetition in small models (A16, B7) is asserted but rarely quantified against context length; C9 shows length-failure correlation is confounded by difficulty. Probe: loop rate vs step count and context fill, controlling for task.
6. Context rot (C7) and lost-in-the-middle (C6) are measured on synthetic retrieval, not agent trajectories; whether small Gemma 4 context degradation (128K E4B) causes agent failure at 20-60K tokens is unmeasured.
7. Constant-hazard model (C5) is fit to frontier models; does a per-step hazard fit small models, and does a verifier/reset change it? Cheap to test via survival curves over steps.
8. Test insufficiency inflates scores (C1, C2) and memorization inflates them (C3); small-model numbers are therefore hard to compare across papers. Probe: report with a stronger-test or post-cutoff subset, noting Gemma 4's data cutoff.
9. Verifier/selection gains are large (A13, D1, A15) but mostly use big or fine-tuned models; whether a small Gemma judge/self-consistency without training adds value is untested here. Probe: best-of-n with test-based vs LLM-judge selection on E4B.
10. Agentless-style fixed pipelines (A3, B3) outperformed agents early on; whether a scaffolded pipeline beats a free agent for small models, given tool-call failures, is an open comparison (confounded across papers by model).
11. Local economics: prefill dominates agent loops and prefix caching gives 22-136x TTFT (E1) but nobody reports resolve-rate per wall-clock hour for local SWE agents; benchmarks report dollars, which are meaningless locally. Probe: tokens/s prefill vs decode on M5 Max, cache hit rate in an agent loop.
12. Reported local-runtime comparisons (E2) use Qwen on M2 Ultra; none I verified uses Gemma 4 on M5-class chips, and quantization effect on tool-call validity is unmeasured.
