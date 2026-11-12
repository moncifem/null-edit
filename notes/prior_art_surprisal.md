# Prior-art check: issue-conditioned surprisal shift (2026-11-11)

Method: ~14 web searches plus fetches. Several fetches returned only summaries from a small model, so details marked "abstract-level" were not checked against the full text. No exact match found. This is an absence-of-evidence result from a limited-budget search, not proof of novelty.

## Works characterized

### 1. Ray et al. 2015, "On the Naturalness of Buggy Code" (Ray, Hellendoorn, Godhane, Tu, Bacchelli, Devanbu; arXiv 1506.01159; ICSE 2016)
URL opened: https://arxiv.org/abs/1506.01159
- Computes: language-model entropy (n-gram, per the well-known paper; the abstract page I opened did not state n-gram, NOT VERIFIED here) on lines of ~8,296 bug-fix commits from 10 Java projects. Buggy lines are more entropic and become less so after the fix. Ranking high-entropy lines is about as cost-effective as PMD/FindBugs.
- No bug report conditioning. Scoring only. Unconditional.
- Verdict: BACKGROUND ONLY for claims 1-3. It is the origin of claim (4)'s baseline ("naturalness") and supports it as a known, modest signal.

### 2. Yang et al. 2024, "Revisiting Unnaturalness for APR in the Era of LLMs" (Aidan Z.H. Yang + coauthors; arXiv 2404.15236; ICSE 2025)
URLs opened: https://arxiv.org/abs/2404.15236 and https://arxiv.org/html/2404.15236v1
- Computes: (a) per-line entropy by masking each line in turn and querying the LLM (InCoder, StarCoder, CodeLlama; 2048-token window; infill-style, with prefix and suffix context). Used to RE-RANK top-N lines from SBFL, TransferFL, LLMAO. (b) "Entropy-delta": entropy change of a line before vs after replacement by a patch, used to rank/classify plausible patches. Positive = patch more natural.
- Data: Defects4J v1.2/2.0 (single-line bugs, TBar/Shibboleth/Panther patches). Not SWE-bench. Input is code only; no bug report, issue or test message conditioning.
- Reported: InCoder entropy re-ranking of SBFL moved Top-1 from 24 to 50; entropy-delta patch ranking Top-1 127 vs 85 for Shibboleth; classification F1 0.824 vs 0.750. Entropy alone is weaker than combined (matches claim 4's direction); TransferFL Top-1 dropped with entropy re-ranking.
- Verdict: PARTIAL OVERLAP with claims (3) and (4). Same patch-ranking principle (a correct patch reduces surprisal), already published. Differs: unconditional (no issue), infilling mask-per-line (many forward passes), Defects4J single-line, no issue-conditioned contrast. Claim (4) is largely pre-empted as a qualitative result.

### 3. LLMAO (Yang, Martins, Le Goues, Hellendoorn; arXiv 2310.01726; ICSE 2024)
URL opened: search result only (https://arxiv.org/pdf/2310.01726); I did not open the paper body. Treat details as abstract-level.
- Computes: frozen causal LLM per-line representations in ONE pass, small trained bidirectional adapter predicts line bugginess. Test-free. Trained supervised, no issue text.
- Verdict: PARTIAL OVERLAP with claim (2) in spirit (single forward pass, no tests, no generation), but it is a trained classifier on hidden states, not a zero-shot likelihood contrast, and it does not use issue text.

### 4. FLAG (Ahmad, Tan, Karri, Pearce; arXiv 2306.12643, 2023)
URL opened: https://arxiv.org/abs/2306.12643
- Computes: LLM regenerates each line and differences, plus confidence and comment distance, flag anomalies. 121 benchmarks in C/Python/Verilog. Generation-based, not teacher-forced, no issue conditioning (decoding details NOT VERIFIED).
- Verdict: BACKGROUND ONLY (anomaly detection by regeneration).

### 5. Campos 2024, "Bug Detection and Localization using Pre-trained Code Language Models" (Viola Campos; INFORMATIK 2024, LNI)
URL opened (PDF, read via pdftotext): https://dl.gi.de/server/api/core/bitstreams/1b3e1225-28f4-4696-9245-4c6a57b95702/content
- Computes: CodeLlama-Python teacher-forced token likelihood and a "likelihood ratio" (log p of the ground-truth token over log p of the model's top token, after Villmow et al.), aggregated at token/line/method level. Not a with-vs-without-context ratio. Datasets: HumanEvalFix plus a small student-submission set. Up to 78% method-level detection accuracy. Notes training-data leakage.
- No bug report conditioning.
- Verdict: PARTIAL OVERLAP with claim (4) (scoring-only, teacher-forced, likelihood for localization), but its "ratio" is a different quantity. Does not do the issue-conditioned contrast.

### 6. ANVIL (Wang, Liu, Guo, Hu, Grishchenko, Lie; arXiv 2408.16028; DIMVA 2026 per a PDF filename in search results, NOT VERIFIED)
URL opened: https://arxiv.org/abs/2408.16028
- Computes: LLM reconstructs a masked line; hybrid anomaly score (exact match, cross-entropy, confidence, structural complexity). Line-level vulnerability detection on PrimeVul. No NL conditioning; tests context size.
- Verdict: BACKGROUND ONLY (line-level surprisal anomaly detection).

### 7. Fixer-Guided Localization, "Let the Fixer Decide" (Hennara et al.; arXiv 2611.12164, 9 Nov 2026)
URL opened: https://arxiv.org/pdf/2611.12164 (read via pdftotext)
- Computes: a frozen fixer scores each candidate localization z by log p(verified patch y* | issue x, code at z). Scores weight SFT of a localizer (EM-style). Uses only a forward pass of the fixer as the "environment". Tokens scored are PATCH tokens given issue plus candidate context, used as a TRAINING signal, not inference-time scoring of existing repo lines. Inspired by Sachan et al. retrieval-from-reader training.
- Verdict: PARTIAL OVERLAP. Closest in being "likelihood-with-issue, no tests, forward pass". Differs: needs the gold/verified patch (training only), scores patch not source lines, no with-vs-without-issue contrast, no per-token map, no patch ranking. Very recent (2 days old), so cite as concurrent work. Method details beyond abstract and intro were skimmed only.

### 8. Context-aware decoding / PMI contrast (Shi et al. 2023, arXiv 2305.14739; also P-CXMI, Fernandes et al. arXiv 2109.07446)
URLs: seen in search results only (not opened).
- Computes: log p(y|c,x) - log p(y|x) (PMI) as a decoding adjustment, and P-CXMI as a with/without-context measure on translation. Same mathematical quantity as the candidate idea, never applied to code edit localization in anything found.
- Verdict: BACKGROUND ONLY, but it is the theoretical lineage and must be cited. The quantity is not new; its application is.

### 9. Query-likelihood rerankers (Sachan et al. 2022 UPR; Zhuang et al. LLM query likelihood models)
URL: seen in search snippets only, NOT opened.
- Computes: average log P(query | prompt, doc). No code-specific zero-shot application to issues found in my searches. SweRank (arXiv 2505.07849) trains a listwise reranker and a contrastive embedder for issue localization; BRaIn (arXiv 2501.10542) uses LLM relevance judgments; LLM-BL (ICPC 2025) uses listwise ranking. All seen via snippets only.
- Verdict: BACKGROUND ONLY (P(issue|code) as baseline is plausible to implement but I found no paper doing so zero-shot on SWE-bench).

### 10. Test-free patch selection on SWE-bench
Seen via search snippets, none uses patch or code logprob as main signal:
- PatchFusion / PatchFuseBench (arXiv 2607.01597, Yang et al.), opened abstract: cross-candidate edit-atom agreement; no logprobs. BACKGROUND ONLY.
- R4P (reasoning verifier, arXiv 2510.22775 "Scalable Supervision for Software Agents via Patch Reasoning", Xu et al.), PDF unreadable to the fetcher; abstract-level claims only. Generative reasoning verifier. BACKGROUND ONLY.
- EGSS (arXiv 2602.05242), opened abstract: entropy-guided stepwise scaling for agents; the abstract does not say what entropy is measured on (likely generation uncertainty). PARTIAL at most; NOT VERIFIED.
- "Dissecting the SWE-Bench Leaderboards" (arXiv 2506.17208): lists selectors (voting, embeddings, reward models, LLM adjudicators). No logprob selector seen in snippets.
- Agentless (arXiv 2407.01489), CORTEXA, Co-PatcheR: test-based or LLM selection. CodeMonkeys and SWE-Fixer details NOT VERIFIED (not found).
- Pragmatic Reasoning (arXiv 2502.15835): ranks code candidates by log-prob under induced instructions. Generation benchmark, not SWE-bench. Snippet only.

### 11. Other
- Dinh et al., NeurIPS 2023, "LLMs of Code Fail at Completing Code with Potential Bugs" (arXiv 2306.03438): shows bugs in context hurt completion; not localization. BACKGROUND ONLY.
- Local-hardware argument ("prompt eval 10-50x faster than generation, so score instead of generate"): searched; found only blog posts about local agents being slow on prompt processing and verifier loops. No paper arguing the scoring-vs-generating asymmetry for agent design. NOT FOUND (does not prove absence).
- IRBL (BugLocator etc.), SweRank, LocAgent-type work: background only.

## Not found (searched, nothing)
- Any work computing log P(token | code, issue) - log P(token | code) over existing source lines for localization.
- Any work using that quantity to rank SWE-bench leaderboard patches.
- Any per-token logprob-based SWE-bench localization with no generation.

## Verdict per claim

(1) Conflict (likelihood DROP under issue conditioning) enriches edit lines: LIKELY NEW as an empirical claim. The quantity is old (PMI/CAD, P-CXMI) and the "unconditional surprisal marks bugs" premise is old (Ray, Yang). Closest: Yang 2024 (unconditional, per-line entropy), Fixer-Guided Localization (issue-conditioned patch likelihood, training only). Caveat: the sign is theoretically odd. Lines to be edited are buggy, so a model told "this is the file after the fix" should find old buggy tokens LESS likely, but that same conditioning also depresses many unrelated tokens. The result is untested; it may fail. The claim that BM25/embeddings/P(issue|code) capture only positive association is a hypothesis, not prior art.

(2) Single parallel forward pass, no agent loop: PARTIAL OVERLAP in form. LLMAO (single pass, test-free, trained, no issue); Yang 2024 (many masked passes). Novel part is zero-shot plus issue-conditioned plus SWE-bench. The local-hardware throughput argument I could not find stated in the literature, but it is an engineering framing, not a scientific contribution.

(3) Patch ranking via surprisal removal: PARTIAL OVERLAP, substantially pre-empted in the unconditional form by Yang 2024 entropy-delta (Defects4J). The issue-conditioned version evaluated on SWE-bench leaderboard patches appears new. Must beat or be compared against entropy-delta and a plain log P(patch | issue, context) baseline.

(4) Unconditional surprisal much weaker than conditional contrast: Mostly PRE-EMPTED as a premise (Ray, Yang report modest standalone signal; Campos notes leakage and model-complexity confounds). The head-to-head against the conditional contrast is new, but it is a control experiment, not a standalone contribution.

## Positioning suggestions
- Frame the novelty as "issue-conditioned pointwise information over EXISTING code, a zero-shot token-level map", citing CAD/P-CXMI as the quantity and Ray/Yang/LLMAO/Campos as the naturalness lineage, and FGL as concurrent issue-conditioned likelihood work.
- Baselines required: unconditional entropy (Yang), masked-line entropy, P(issue|code) query likelihood, BM25/embedding, SweRank, plus raw log P(patch | issue) and Yang's entropy-delta for patch ranking.
- Control for leakage and memorization (SWE-bench is widely trained on; Campos shows leakage inflates likelihood methods). Use SWE-bench Live or post-cutoff issues.
- Test both signs (drops and rises) and the "after the fix" framing; report line-level enrichment against gold hunks with length and token-frequency matching.
- Likely strongest, defensible contribution: patch ranking and verification on public leaderboard patches (cheap, no tests), and a negative/positive result on whether a contrast beats unconditional entropy. Do not lean on the local-hardware argument as a scientific claim; report measured throughput.
- Before submission, rerun targeted searches for Villmow et al. 2023 (cited in Campos for the likelihood ratio, NOT VERIFIED), CodeMonkeys, and any 2026 arXiv papers on "surprisal" plus issue conditioning, since the field moves fast.
