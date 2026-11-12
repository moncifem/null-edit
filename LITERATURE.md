# LITERATURE.md (compiled 2026-11-11)

Verification convention. VERIFIED = the arXiv abstract page or official page was opened on 2026-11-11 and title, authors, date and venue were read from it. The fetch tool returns summaries from a small model, so "what it shows" statements are abstract-level, not full-text. Venue is given only when the page states it; otherwise "none stated on page". NOT VERIFIED = not opened from a primary source in this pass. Nothing here is from memory.

## 1. Core references (verified)

### 1a. SWE-bench family, agents, localization

| Work | Authors, year, venue | URL | What it shows (abstract-level) | Relation to our work |
|---|---|---|---|---|
| SWE-bench: Can Language Models Resolve Real-World GitHub Issues? | Jimenez, Yang, Wettig, Yao, Pei, Press, Narasimhan; Oct 2023; ICLR 2024 (stated in page comments) | https://arxiv.org/abs/2310.06770 | 2,294 real GitHub issues; best model tested (Claude 2) resolved about 1.96%. | Source benchmark; our evaluation data (Verified subset). VERIFIED |
| SWE-bench Verified (OpenAI blog, "Introducing SWE-bench Verified") | OpenAI with the SWE-bench authors, 13 Aug 2024 per search snippet; the notes/brief name Chowdhury et al. | https://openai.com/index/introducing-swe-bench-verified/ | 500 human-validated instances (confirmed on https://www.swebench.com/verified.html: "A human-validated subset of 500 SWE-bench instances", "created in collaboration with OpenAI"). | Primary eval set. **NOT VERIFIED (primary)**: the OpenAI page returned HTTP 403 twice. Date, byline (Chowdhury et al.), 93 annotators / 1,699 samples seen only in a search snippet. Do not cite author names or numbers until the page is opened. |
| SWE-bench Goes Live! (SWE-bench-Live) | Linghao Zhang, Shilin He, Chaoyun Zhang et al. (15 authors); v1 29 May 2025; no venue stated | https://arxiv.org/abs/2505.23419 | Continuously updatable benchmark, 1,319 tasks from issues created since 2024; agents do noticeably worse than on static SWE-bench. | Post-cutoff evaluation set. Title differs from the brief's "SWE-bench-Live": paper title is "SWE-bench Goes Live!". VERIFIED |
| SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering | John Yang, Jimenez, Wettig, Lieret, Yao, Narasimhan, Press; May 2024; NeurIPS 2024 (venue per mini-SWE-agent README, not on arXiv page) | https://arxiv.org/abs/2405.15793 | A custom agent-computer interface gave 12.5% pass@1 on SWE-bench (then state of the art). | Agent baseline we contrast with (we use no agent loop). VERIFIED |
| mini-SWE-agent | SWE-agent team (GitHub repo; no paper of its own) | https://github.com/SWE-agent/mini-swe-agent | README: "100 lines of python for the agent class"; "Scores >74% on the SWE-bench verified benchmark". README asks users to cite the SWE-agent paper. | Minimal harness baseline. Score is a README claim with strong models; not peer reviewed. VERIFIED (README only) |
| Agentless: Demystifying LLM-based Software Engineering Agents | Chunqiu Steven Xia, Deng, Dunn, Lingming Zhang; Jul 2024; no venue stated | https://arxiv.org/abs/2407.01489 | Fixed three-phase pipeline (localize, repair, validate) with no agent loop; best open-source result and lowest cost on SWE-bench Lite at the time. | Closest pipeline-style comparator; its localization stage is the baseline we compete with. VERIFIED |
| LocAgent: Graph-Guided LLM Agents for Code Localization | Zhaoling Chen, Tang, Deng, Wu, Wu, Jiang, Prasanna, Cohan, Xingyao Wang; Mar 2025; no venue stated | https://arxiv.org/abs/2503.09089 | Codebase as directed heterogeneous graph so agents localize by multi-hop search; reports improved localization accuracy (the 92.7% file-level and LocBench figures in the notes were not on the abstract summary I read). | Agentic localization baseline. VERIFIED (headline number NOT re-checked) |
| SWE-Fixer: Training Open-Source LLMs for Effective and Efficient GitHub Issue Resolution | Chengxing Xie, Li, Gao, Du, Lam, Zou, Chen; Jan 2025; no venue stated | https://arxiv.org/abs/2501.05040 | Retrieval model plus editing model, two model calls per instance; competitive among open-source models. | Retrieve-then-edit baseline, trained. VERIFIED |
| SweRank: Software Issue Localization with Code Ranking | Revanth Gangi Reddy, Suresh, Doo, Liu, Nguyen, Zhou, Yavuz, Xiong, Ji, Joty; May 2025; "ICLR 2026 Camera Ready Version" | https://arxiv.org/abs/2505.07849 | Retrieve-and-rerank framework reaching state of the art on SWE-Bench-Lite and LocBench issue localization. It exists. | Trained ranker baseline for file/function localization. VERIFIED |
| The SWE-Bench Illusion: When State-of-the-Art LLMs Remember Instead of Reason | Shanchao Liang, Garg, Zilouchian Moghaddam; Jun 2025 (v4 Dec 2025); no venue stated | https://arxiv.org/abs/2506.12286 | Models do better on SWE-Bench repos than on other repos, suggesting memorization contributes to scores (the 76% / 5-gram numbers in the notes are from other pages of the paper and were not re-checked). | Motivates the post-cutoff SWE-bench-Live arm: copy/likelihood methods are contamination-sensitive. VERIFIED |
| SWE-Bench+: Enhanced Coding Benchmark for LLMs | Reem Aleithan, Xue, Mohajer, Nnorom, Uddin, Song Wang; Oct 2024; no venue stated | https://arxiv.org/abs/2410.06992 | Audits SWE-bench: solution leakage in issue text and weak tests; SWE-Agent+GPT-4 falls from 12.47% to 3.97% after filtering. | Warns that issue text can leak the fix, which directly affects an issue-conditioned method. VERIFIED |
| Majgaonkar et al., Understanding Code Agent Behaviour: An Empirical Study of Success and Failure Trajectories | Oorja Majgaonkar, Fei, Li, Sarro, He Ye; 31 Oct 2025; no venue stated | https://arxiv.org/abs/2511.00197 | Across OpenHands, SWE-agent and Prometheus, agents often locate the right files even when they fail; success depends more on roughly correct changes. | Supports "localization is not the main bottleneck for strong agents", which limits the headline value of localization gains; notes had it right. VERIFIED |
| CodeMonkeys: Scaling Test-Time Compute for Software Engineering | Ryan Ehrlich, Brown, Juravsky, Clark, Re, Mirhoseini; Jan 2025; no venue stated | https://arxiv.org/abs/2501.14723 | Samples many multi-turn editing attempts per issue and selects among them: 57.4% Verified for about $2,300. | Selection/verification baseline for the patch-verification extension. VERIFIED |
| R2E-Gym: Procedural Environments and Hybrid Verifiers for Scaling Open-Weights SWE Agents | Naman Jain, Singh, Shetty, Zheng, Sen, Stoica; Apr 2025; no venue stated | https://arxiv.org/abs/2504.07164 | 8.7K+ executable environments; combining execution-based and execution-free verifiers reaches 51% on Verified. | Evidence that execution-free verifiers help; baseline for our verification extension. VERIFIED |
| R4P: Scalable Supervision for Software Agents via Patch Reasoning | Junjielong Xu, Tan, Liu, Peng, Gao, Pinjia He; v1 26 Oct 2025, v2 26 Aug 2026; "EMNLP'26 Findings" | https://arxiv.org/abs/2510.22775 | Reasoning-based reward for agent patches without running tests; 72.2% accuracy verifying SWE-bench patches. | Closest execution-free patch verifier (trained/reasoning, not likelihood). VERIFIED (abstract) |

### 1b. Speculative decoding and edit speed-ups

| Work | Authors, year, venue | URL | What it shows | Relation |
|---|---|---|---|---|
| Fast Inference from Transformers via Speculative Decoding | Yaniv Leviathan, Kalman, Matias; Nov 2022 (rev. May 2023); ICML 2023 Oral | https://arxiv.org/abs/2211.17192 | Parallel verification of draft tokens speeds sampling 2-3x on T5-XXL with identical output distribution. | Theory behind "verify a copied draft in one pass"; the first-deviation distribution is a chain-rule consequence of this verification. VERIFIED |
| Accelerating Large Language Model Decoding with Speculative Sampling | Charlie Chen, Borgeaud, Irving, Lespiau, Sifre, Jumper; Feb 2023; no venue stated (arXiv preprint) | https://arxiv.org/abs/2302.01318 | A draft model proposes tokens that the target checks in parallel; 2-2.5x speed-up on 70B Chinchilla without changing the model. | Same as above. VERIFIED |
| EfficientEdit: Accelerating Code Editing via Edit-Oriented Speculative Decoding | Peiding Wang, Zhang, Liu, Zhu, Xu, Shi, Lian, Li, Shen, Fu; Jun 2025 (v2 Sep 2025); "Accepted by ASE 2025" | https://arxiv.org/abs/2506.02780 | Reuses unchanged original code as draft with specialized draft models and dynamic verification; up to 10.38x on CanItEdit. **Title differs from the brief:** the arXiv title is "EfficientEdit: Accelerating Code Editing via Edit-Oriented Speculative Decoding"; "Reuse or Generate?" is not the title on the abstract page I opened (the notes saw it on the HTML version; the title may have changed between versions, NOT checked). | Closest mechanical ancestor (teacher-force the original, rejection marks where edits start). It targets speed; the abstract mentions no localization evaluation. VERIFIED (title caveat) |
| OpenAI Predicted Outputs docs | OpenAI documentation, undated | https://developers.openai.com/api/docs/guides/predicted-outputs | `prediction` parameter speeds up regeneration of a file with small edits; supported on gpt-4o/4o-mini/4.1 family; `logprobs` not supported; only aggregate `rejected_prediction_tokens` in usage, no per-position information. | Same mechanism exposed commercially; shows the per-token signal we use is not exposed there. VERIFIED |
| Cursor, "Editing Files at 1000 Tokens per Second" (instant apply) | Cursor blog, 14 May 2024 | https://cursor.com/blog/instant-apply | Describes "speculative edits": a custom speculative-decoding algorithm for full-file rewrites, "up to 9x faster". The page does not explicitly say the draft tokens come from the original file (implied only). Hosted by Fireworks per search snippet (not opened). | The only primary source for Cursor fast apply; vendor blog, not peer reviewed. VERIFIED |

### 1c. Naturalness, token likelihood and localization

| Work | Authors, year, venue | URL | What it shows | Relation |
|---|---|---|---|---|
| On the "Naturalness" of Buggy Code | Baishakhi Ray, Hellendoorn, Godhane, Tu, Bacchelli, Devanbu; Jun 2015; arXiv page states no venue (ICSE 2016 is from the notes, NOT checked on the page) | https://arxiv.org/abs/1506.01159 | Buggy code is more surprising to language models than the fixed code; entropy ranking of lines is about as good as PMD/FindBugs. | Origin of the surprisal-localization lineage; unconditional baseline. VERIFIED |
| Revisiting Unnaturalness for Automated Program Repair in the Era of Large Language Models | Aidan Z.H. Yang, Kolak, Hellendoorn, Martins, Le Goues; Apr 2024; no venue on page (ICSE 2025 is from the notes, NOT checked) | https://arxiv.org/abs/2404.15236 | LLM entropy of code improves several APR stages (re-ranking lines, ranking patches) and reduces overfitting and leakage. | Nearest prior art for patch ranking (entropy-delta) and unconditional per-line surprisal; Defects4J, no issue conditioning (per notes). VERIFIED |
| Large Language Models for Test-Free Fault Localization (LLMAO) | Aidan Z.H. Yang, Martins, Le Goues, Hellendoorn; Oct 2023; no venue on page | https://arxiv.org/abs/2310.01726 | Adds fine-tuned bidirectional adapter layers on an LLM to find buggy lines without test coverage. **Title differs from the brief** (the paper's title is not "LLMAO"; LLMAO is the method name). | Trained single-pass line scorer; contrast with our zero-shot, issue-conditioned map. VERIFIED |
| Bug Detection and Localization using Pre-trained Code Language Models | Viola Campos; INFORMATIK 2024, Lecture Notes in Informatics (GI); DOI 10.18420/inf2024_124 | https://dl.gi.de/server/api/core/bitstreams/1b3e1225-28f4-4696-9245-4c6a57b95702/content | Likelihood-based suspiciousness scores detect buggy methods with up to 78% accuracy on a common benchmark; leakage inflates results (large gap vs a non-public student dataset). PDF text read via pdftotext. | Teacher-forced likelihood localization without issue conditioning; supports using post-cutoff data. VERIFIED |
| FLARE: Fine-Grained Diagnostic Feedback for LLM Code Refinement | Yinsheng Yao, Zhang, Tong, Tianyi Zhang; 2 Jun 2026 (v2 16 Sep 2026); no venue stated | https://arxiv.org/abs/2606.03852 | Iterative refinement built around "a lightweight diagnostic model that predicts line-level suspiciousness signals"; gains on LiveCodeBench and BigCodeBench. **Differs from the notes:** the abstract describes a learned diagnostic model; the notes' claim that it uses the generator's own token probabilities is NOT confirmed. | Related only as line-level suspiciousness to guide refinement; do not describe it as a token-probability method. VERIFIED (abstract); mechanism NOT VERIFIED |
| Let the Fixer Decide: Training a Code Localizer from the Fixer's Likelihood | Khalil Hennara, Hreden, Aldallal, Chrouf, AlModhayan; 9 Nov 2026; no venue stated | https://arxiv.org/abs/2611.12164 | Trains a localizer from a frozen fixer's likelihood scores, no tests or RL; the fixer finds bugs about as often as the teacher's while using 27.5% less code. | Concurrent work (2 days old) on issue-conditioned likelihood; trains a localizer rather than reading a zero-shot map. VERIFIED (abstract; notes also skimmed the PDF) |
| Surface Form Competition: Why the Highest Probability Answer Isn't Always Right | Ari Holtzman, West, Shwartz, Choi, Zettlemoyer; Apr 2021 (v9 Nov 2022); no venue on page | https://arxiv.org/abs/2104.08315 | Raw string probability underrates correct answers because mass is split across wordings; Domain Conditional PMI reweights by the prior. | Theoretical lineage for dividing by an unconditional prior (our with/without-issue contrast). VERIFIED |
| Self-Refine: Iterative Refinement with Self-Feedback | Aman Madaan et al. (16 authors); Mar 2023; no venue on page | https://arxiv.org/abs/2303.17651 | One LLM improves its own outputs via self-feedback loops, about 20% absolute average gain over one-step generation across seven tasks. | Fixed-point / "no further edits" stopping idea for the verification extension; stability is not shown to imply correctness. VERIFIED |

### 1d. Gemma 4 and MLX

**Gemma 4 official sources (opened 2026-11-11):**
- Model card: https://ai.google.dev/gemma/docs/core/model_card_4
  - Sizes, verbatim: "The models are available in five distinct sizes: E2B, E4B, 12B, 26B A4B, and 31B."
  - License, verbatim: "License: Apache 2.0".
  - Training data cutoff, verbatim (Training Dataset section): "with a cutoff date of January 2025". The same wording appears on the Hugging Face card https://huggingface.co/google/Gemma-4-E2B ("a cutoff date of January 2025").
  - Release date: not stated on the model card.
- Launch post: https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/ titled "Gemma 4: Byte for byte, the most capable open models", dated Apr 02, 2026. Sizes there: "Effective 2B (E2B), Effective 4B (E4B), a 26B Mixture of Experts (MoE) model, and a 31B Dense model" (four sizes, no 12B; the 12B appears only on the model card and later). License: "commercially permissive Apache 2.0 license". Knowledge cutoff: not stated in the launch post.
- Technical report: https://arxiv.org/abs/2607.02770 "Gemma 4 Technical Report", Gemma Team, submitted 2 Jul 2026 (v2 24 Jul 2026); the abstract page states no knowledge cutoff.
- Model-card parameter/benchmark details (from notes, opened earlier): E2B 2.3B effective, E4B 4.5B effective, 26B A4B 25.2B total / 3.8B active; no SWE-bench number on the card.
- The cutoff is therefore stated by the official model card and Hugging Face card (first-party), not only by third parties. Release date "2 April 2026" comes from the official launch post.
- Practical caveat: a January 2025 cutoff precedes the SWE-bench Verified issues' later period but SWE-bench itself (2023) and Verified (Aug 2024) are well within the pre-training window, so contamination is expected on Verified; SWE-bench-Live issues created after Jan 2025 are the clean arm. Check the exact creation-date range of the Live tasks used.

**MLX / mlx-lm:** https://github.com/ml-explore/mlx-lm. Repo "About": "Run LLMs with MLX"; README: "a Python package for generating text and fine-tuning large language models on Apple silicon with MLX"; MIT license. VERIFIED (repo page).

## 2. Background and landscape

Status labels are those assigned in the notes (frontier_map.md and the ideas_*.md / prior_art_*.md files) unless I re-opened the source above. "Notes-VERIFIED" means the notes' author opened the page; I did not repeat it.

**SWE agents, benchmarks and small-model training (Notes-VERIFIED, abstract-level)**
- OpenHands (Wang et al., 2024) https://arxiv.org/abs/2407.16741 ; AutoCodeRover https://arxiv.org/abs/2404.05427 ; Moatless Tools https://github.com/aorwall/moatless-tools (README, n=50 mini subset).
- Multilingual / harder benchmarks: https://www.swebench.com/multilingual.html ; Multi-SWE-bench https://arxiv.org/abs/2504.02605 ; SWE-Bench Pro https://arxiv.org/abs/2509.16941 .
- Training small/open agents: SWE-Gym https://arxiv.org/abs/2412.21139 ; SWE-smith https://arxiv.org/abs/2504.21798 ; SWE-RL https://arxiv.org/abs/2502.18449 ; DeepSWE (Together AI blog, not peer reviewed) https://www.together.ai/blog/deepswe ; SWE-Protege https://arxiv.org/abs/2602.22124 .
- No published zero-shot Gemma 4 SWE-bench result was found; a blog claim of "61.2% SWE-bench Verified" for a "Gemma 4 27B" is NOT VERIFIED and refers to a size that does not exist on the model card. Practitioner anecdote (n=1) on harness effects: https://ai-muninn.com/en/blog/swe-bench-local-models-framework-matters .

**Localization (Notes-VERIFIED unless stated)**
- RepoGraph https://arxiv.org/abs/2410.14684 ; OrcaLoca https://arxiv.org/abs/2502.00350 ; CoSIL https://arxiv.org/abs/2503.22424 ; Repository Memory for localization (ICLR 2026) https://arxiv.org/abs/2510.01003 (abstract).
- SWE-smith failure breakdown (localization/looping about 53% of failures) is from a search snippet only: NOT VERIFIED.
- Bug-report information and repair success, https://www.alphaxiv.org/abs/2607.09553 (notes opened; I did not).

**Benchmark validity and failures (Notes-VERIFIED)**
- UTBoost https://arxiv.org/abs/2506.09289 ; Failures in automated issue solving https://arxiv.org/abs/2509.13941 ; trajectory study with 9,374 trajectories https://arxiv.org/abs/2604.02547 ; TRAJEVAL / Coherence Collapse https://arxiv.org/abs/2603.24631 (abstract; 60-69% of failures edit the right functions yet produce wrong patches).
- Seen in search results only (NOT VERIFIED): "Are 'Solved Issues' in SWE-bench Really Solved Correctly?" https://arxiv.org/abs/2503.15223 ; 2512.10218 (memory vs ability); ContextBench 2602.05892 ; CodeTracer https://www.alphaxiv.org/abs/2604.11641 ; "Dissecting the SWE-Bench Leaderboards" 2506.17208.
- Long-context behaviour: Lost in the Middle https://arxiv.org/abs/2307.03172 ; Context Rot (technical report) https://www.trychroma.com/research/context-rot . METR horizon https://arxiv.org/abs/2503.14499 ; Ord https://arxiv.org/abs/2505.05115 ; AgentFloor https://arxiv.org/abs/2605.00334 ; "Beyond Benchmarks" https://arxiv.org/abs/2610.34241 (small custom suite).

**Verification and selection**
- Notes-VERIFIED: SWT-Bench https://arxiv.org/abs/2406.12952 ; Otter https://arxiv.org/abs/2502.05368 ; PatchFusion 2607.01597 (abstract); EGSS https://arxiv.org/abs/2602.05242 (abstract does not say what entropy is measured; NOT VERIFIED mechanism).
- Search-snippet only (NOT VERIFIED): Agentic Rubrics https://arxiv.org/html/2601.04171v1 ; Yadavally et al. 2501.16655 (LLM critics) ; Pragmatic Reasoning 2502.15835 ; On LLMs' Internal Representation of Code Correctness https://arxiv.org/html/2512.07404v3 (reported: raw likelihood ranking inconsistent, sometimes below random on HumanEval/BigCodeBench; important caution for our verification extension).

**Likelihood lineage and contrast quantities**
- FLAG https://arxiv.org/abs/2306.12643 and ANVIL https://arxiv.org/abs/2408.16028 (Notes-VERIFIED abstracts): regeneration/anomaly scoring of lines.
- Context-aware decoding / PMI (Shi et al. 2023, 2305.14739) and P-CXMI (Fernandes et al., 2109.07446): search results only, NOT VERIFIED; same quantity as a with/without-context contrast.
- UPR / query-likelihood rerankers (Sachan et al.), BRaIn 2501.10542, LLM-BL: snippets only, NOT VERIFIED. Dinh et al. 2306.03438 (bugs in context hurt completion): snippet only.
- Villmow et al. 2023 (source of Campos's likelihood ratio): NOT VERIFIED.

**Next-edit and copy-bias literature (all NOT VERIFIED, snippets)**
- NES 2508.02473 ; Next Edit Prediction 2508.10074 ; neural-symbolic edit grammar 2204.06643 ; GEC over-correction EMNLP 2023 main.619, 2605.13624, GECScore 2405.04286 ; Fireworks/Morph/Trelis posts about Cursor Fast Apply (secondary).

**Local inference (Notes-VERIFIED abstracts)**
- Persistent Q4 KV cache https://arxiv.org/abs/2603.04428 ; MLX vs other runtimes https://arxiv.org/abs/2511.05502 . Not checked: vLLM-metal, oMLX, BaseRT.

**Other items cited by ideas_*.md (not central to this paper)**: difficulty prediction from static features 2608.18280 (opened per notes); ReD restarts https://arxiv.org/html/2601.21522v2 (opened per notes); ROSE co-change https://www.st.cs.uni-saarland.de/softevo/changes.php?lang=fr (search summary); InForage https://arxiv.org/html/2505.09316v2 (search result); Spurious Tool Use alphaxiv 2609.16268, EMNLP-Findings 2026.findings-emnlp.728 and ICML 2026/77959 (snippets). SWE-bench experiments repo https://github.com/SWE-bench/experiments (opened per notes; holds entries, not artifacts).

## 3. Novelty comparison

Verdicts follow prior_art_surprisal.md and prior_art_nulledit.md. These are absence-of-evidence results from limited searches, not proof of novelty.

| Closest prior work | What it does | What we do differently | Strength of overlap |
|---|---|---|---|
| Ray et al. 2015 | N-gram/LM entropy of lines; buggy lines more surprising, entropy ranking about as good as static analyzers | Token-level, issue-conditioned, a rewrite-task probability rather than unconditional naturalness | Background; unconditional baseline |
| Yang et al. 2024 (2404.15236) | LLM per-line entropy (masked, infill) to re-rank SBFL lines; entropy-delta to rank patches; Defects4J, no issue text | One teacher-forced pass over the whole file, conditioned on the issue; SWE-bench Verified and Live; patch verification would need comparison to entropy-delta | Partial; patch-ranking idea pre-empted in unconditional form |
| LLMAO (2310.01726) | Trained adapter on hidden states, one pass, test-free, no issue | Zero-shot, no training, issue-conditioned | Partial in form |
| Campos 2024 | Teacher-forced likelihood and likelihood ratio, HumanEvalFix, no bug report | Issue-conditioned, SWE-bench scale, repo files | Partial; scoring-only teacher forcing is shared |
| EfficientEdit (2506.02780) / Cursor speculative edits / Predicted Outputs | Original file as draft verified in one pass, for speed; rejection marks edit start as a by-product | Read the per-token deviation probability as a localization signal and evaluate it as such; no draft model | Partial; same mechanical object, different purpose |
| Speculative decoding (Leviathan, Chen) | Verification of drafts preserves the target distribution | We use the chain-rule consequence (first-deviation distribution) as a measurement, which is not a contribution by itself | Theory background |
| Fixer-Guided Localization (2611.12164) | Frozen fixer's log p(verified patch given issue and code at z) trains a localizer | Inference-time zero-shot map over existing file tokens; no gold patch, no training | Partial; concurrent work |
| FLARE (2606.03852) | Learned line-level suspiciousness to guide code refinement (LiveCodeBench, BigCodeBench) | Existing repo file plus issue; no trained diagnostic model | Weak; mechanism per notes unconfirmed |
| Agentic/trained localizers (LocAgent, SweRank, SWE-Fixer, Agentless) | Search agents, rerankers or retrieval models | Single forward pass, no tools; we should report them as baselines, not claim to beat them without numbers | Different regime |
| R4P, R2E-Gym verifiers | Trained or reasoning-based execution-free patch verification | Extension only: fixed-point test (residual edit hazard after patching); highest risk, since low edit probability is not correctness (copy bias; Self-Refine-style stability) | Adjacent; verification claim is speculative |

Do not claim: speed novelty, the first-deviation identity as a contribution, or novelty of the PMI-style contrast quantity itself (CAD / P-CXMI / Holtzman).

## 4. Open verification gaps

1. SWE-bench Verified OpenAI post: HTTP 403 on both attempts. Authors (Chowdhury et al.), date (13 Aug 2024) and annotation numbers are NOT VERIFIED from the primary page; only the 500-instance fact is confirmed via swebench.com. Cite by URL and verify the byline manually first.
2. EfficientEdit title: arXiv page title is "EfficientEdit: Accelerating Code Editing via Edit-Oriented Speculative Decoding"; the brief's "Reuse or Generate?" title was not found there. Check v1 vs v2 titles on arXiv before citing.
3. FLARE: the mechanism in prior_art_nulledit.md (generator token probabilities) is contradicted by the abstract (learned diagnostic model). Read the full text before characterizing it.
4. LocAgent headline numbers (92.7% file-level), SWE-Bench Illusion numbers (76%, 35% 5-gram), and venue claims from the notes (Yang 2024 = ICSE 2025, Ray = ICSE 2016, LLMAO = ICSE 2024) were not on the abstract pages I read. Confirm in DBLP/proceedings or leave the venue out.
5. mini-SWE-agent ">74%" is a README claim with strong models and is not peer reviewed; say so.
6. Cursor fast apply: only the vendor blog (May 2024) was opened; whether draft tokens come from the original file is implied, not stated.
7. Gemma 4: no release date on the model card (use the launch post, 2 Apr 2026). Launch post lists four sizes, model card five (adds 12B); the cutoff "January 2025" is stated on the model card and HF card, not in the launch post or the tech report abstract. No official SWE-bench number exists; do not cite the blog's 61.2%.
8. Never opened (cite only after opening): CAD (2305.14739), P-CXMI (2109.07446), Villmow et al., Sachan UPR, "Internal Representation of Code Correctness" (2512.07404), Agentic Rubrics, Yadavally et al., NES / Next Edit Prediction, GEC copy-bias papers, "Are Solved Issues Really Solved Correctly" (2503.15223).
9. All "what it shows" lines are abstract-level via a summarizing fetch tool, not full-text reads; any number quoted in the paper should be re-read in the source.
10. Contamination: Verified predates Gemma 4's stated January 2025 cutoff, so a high copy probability can reflect memorization; this must be controlled with SWE-bench-Live tasks created after that date.

## Addendum 2026-11-12 — error detection from token probabilities, edit-location prediction

See `notes/prior_art_editlocation.md` for the full, verified list. Cited in the paper: Cao et al.,
Findings of ACL 2023 (aclanthology.org/2023.findings-acl.760; autoregressive GEC models assign low
probability to tokens needing correction); Fomicheva et al., TACL 2020, arXiv:2005.10608 (glass-box QE);
Wei, Durrett, Dillig, Coeditor, ICLR 2024, arXiv:2305.18584 (trained edit prediction); Stein et al.,
arXiv:2502.13966 (attention probing for fault localization). Not cited because not verified from a
primary source: Wooding, Caines, Rei (GED from token probabilities; repository page only).
