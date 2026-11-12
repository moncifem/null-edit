# Prior-art examination: null-edit teacher forcing (edit-location / GEC / QE neighbours)

Date of search: 2026-11-12. Method: web search plus fetch of arXiv abstract / ACL Anthology / repo pages. Fetches were summarised by a small model, so quoted details are from those summaries; no full-text PDFs were read. Anything not opened is marked NOT VERIFIED.

## Bottom line
No SAME IDEA found. No paper found that teacher-forces the unchanged input as the answer to an edit/fix instruction and reads copy probabilities as a localizer or as a first-edit distribution. The closest neighbours are GEC / GED token-probability detectors (an ancestor of the mechanism, with no instruction and no source-as-target forcing) and generation-free line-level bug localizers (a different mechanism). Search coverage is limited (about 12 queries); absence is not proof.

## Hits (all opened unless stated)

### 1. Wooding, Caines, Rei, "Minimally Supervised Multilingual Grammatical Error Detection" (repo token-probability-ged)
- Page: https://github.com/brandonwooding/token-probability-ged (repo page opened; the paper itself NOT VERIFIED; the citation block says "Under review"; date not stated; Imperial College MSc AI thesis project).
- Scores each token by its next-token probability from a pretrained or instruction-tuned decoder (few-shot prompt with correction examples) and flags tokens below a threshold as errors. Reports macro F0.5 of 68.2 on MultiGED-2023 without human-annotated GED training data. An instruction-based detection variant also exists (section 3.1).
- Verdict: PARTIAL OVERLAP / strong ANCESTOR. Same mechanism (per-token probability of the given text as a detector, no decoding) in text. Differences: the few-shot prompt does not ask for a rewrite with the input then forced as the answer, there is no first-edit distribution, and the task is not issue-conditioned localization.

### 2. Cao, Cao, Hu, Hou, Xiao, Zhu, "Improving Autoregressive Grammatical Error Correction with Non-autoregressive Models"
- Findings of ACL 2023, pp. 12014-12027, https://aclanthology.org/2023.findings-acl.760/
- Observes that "autoregressive models tend to assign low probabilities to tokens that need corrections" and uses this to motivate a regularizer. Not a detector evaluation.
- Verdict: ANCESTOR. It is the empirical observation behind the idea (a GEC seq2seq model's token probability dips where an edit is needed), but it is used for training, not zero-shot localization.

### 3. Graliński, Staruch, Jurkiewicz, "Oddballness: universal anomaly detection with language models"
- arXiv:2409.03046, 4 Sep 2024, cs.CL, no venue listed. https://arxiv.org/abs/2409.03046
- Unsupervised token anomaly score from LM probabilities, evaluated on GED. Per the search snippet (not re-checked), it is not better than the plain probability baseline in every language.
- Verdict: ANCESTOR (LM-probability error detection; no edit instruction, no copying).

### 4. Fomicheva et al., "Unsupervised Quality Estimation for Neural Machine Translation"
- Fomicheva, Sun, Yankovskaya, Blain, Guzmán, Fishel, Aletras, Chaudhary, Specia. arXiv:2005.10608, 21 May 2020, accepted to TACL (TACL vol. 8, pp. 539-555 per search result). https://arxiv.org/abs/2005.10608
- Glass-box QE: decoder confidence (token probabilities, uncertainty) as a proxy for translation quality, with no extra training data. Fomicheva forced-decodes the MT system's own output (full-text claim NOT VERIFIED beyond the abstract and search snippets).
- Verdict: ANCESTOR (conceptual: read forced-decoding probabilities as a quality or error signal). Not code, no edit instruction.

### 5. Wei, Durrett, Dillig, "Coeditor: Leveraging Contextual Changes for Multi-round Code Auto-editing"
- ICLR 2024; arXiv:2305.18584, submitted 29 May 2023 (v2 28 Apr 2024). https://arxiv.org/abs/2305.18584
- Fine-tuned model that generates line-diff edits for a code region from recent changes. Location comes from the model's generated diff output, not from copy probabilities.
- Verdict: NOT RELATED for mechanism (supervised generation); ANCESTOR for the task (edit prediction).

### 6. Gupta et al., "GrACE: Generation using Associated Code Edits"
- Gupta, Khare, Bajpai, Chakraborty, Gulwani, Kanade, Radhakrishna, Soares, Tiwari. arXiv:2305.14129, 23 May 2023 (v3 20 Sep 2023), no venue listed. https://arxiv.org/abs/2305.14129
- Conditions code LMs (Codex zero-shot, CodeT5 fine-tuned) on prior edits to predict the next edit. A search snippet mentions an "edit likelihood" framing that includes finding the locations to edit. I did not read the body.
- Verdict: ANCESTOR (edit-likelihood framing of location, learned from edit history; no null-edit forcing).

### 7. Lu, Huo, Zhang, Li, Lyu, "Next Edit Prediction: Learning to Predict Code Edits from Context and Interaction History"
- arXiv:2508.10074, 13 Aug 2025 (v2 14 Sep 2025), cs.SE, no venue listed. https://arxiv.org/abs/2508.10074
- Supervised task and benchmark: predict where and what the next edit is from history. Fine-tuned models.
- Verdict: ANCESTOR / NOT RELATED mechanism.

### 8. Chen et al., "NES: An Instruction-Free, Low-Latency Next Edit Suggestion Framework Powered by Learned Historical Editing Trajectories"
- Chen, Xiao, Zhu, Xie, Liang, Chen, Jiang, Li, Di. arXiv:2508.02473, 4 Aug 2025 (v3 1 Apr 2026), FSE'26 Industry Track. https://arxiv.org/abs/2508.02473
- Two learned models: one predicts edit location, one generates the edit. Instruction-free. Reports 75.6% location accuracy. Location model internals NOT VERIFIED.
- Verdict: ANCESTOR (trained location predictor; not copy-probability based).

### 9. Rozanov, "Multi-task LLMs for Bug Classification: Efficient Inference with Auxiliary Decoding Heads"
- arXiv:2606.09956, 8 Jun 2026, cs.SE, no venue listed. https://arxiv.org/abs/2606.09956
- Trained line-level bug localization in one forward pass (per search snippet, per-line classification heads; the abstract says one generated token per file). Input is the file; no issue conditioning evidenced.
- Verdict: PARTIAL OVERLAP on "no generation, single pass, line level" goal; different mechanism (supervised heads, not teacher-forced copy probability). It is a likely reviewer comparison point.

### 10. Stein, Wayne, Naik, Naik, Wong, "Where's the Bug? Attention Probing for Scalable Fault Localization"
- arXiv:2502.13966, 19 Feb 2025, cs.SE, no venue listed. https://arxiv.org/abs/2502.13966
- Bug Attention Probe: probe over LLM internal attention, trained without line-level labels, for line-level localization.
- Verdict: ANCESTOR (reading localization out of a frozen LM's internals without generation; trained probe).

### 11. Wang-Lin, Isopoussu, Mahon, "If It's Not Buggy, Don't Fix It: On the Dynamics of Iterative Bug-fixing with LLMs"
- arXiv:2609.10123, 9 Sep 2026, cs.SE/cs.CL, no venue listed. https://arxiv.org/abs/2609.10123
- Finds that models over-edit correct programs, and finds a steering vector controlling edit eagerness (an internal "buggy code" representation).
- Verdict: ANCESTOR for the "latent edit propensity" idea (interpretability side); not a localizer.

### 12. Yang, Cai, Jin, Tian, "PAFT: Preservation Aware Fine-Tuning for Minimal-Edit Program Repair"
- arXiv:2604.03113, 3 Apr 2026, cs.SE, no venue listed. https://arxiv.org/abs/2604.03113
- Trains models to preserve unchanged tokens (token-level preservation signals from aligning buggy and fixed code). Related to the "copy vs edit" token distinction, but it is a training method.
- Verdict: ANCESTOR (the same copy-vs-edit token labelling, used for fine-tuning).

### 13. Liu, "Copy-as-Decode: Grammar-Constrained Parallel Prefill for LLM Editing"
- arXiv:2604.18170, v1 20 Apr 2026; v2 withdrawn 24 May 2026 (withdrawal note cites authorship review). https://arxiv.org/abs/2604.18170
- Serving-layer primitive: copy spans specified by line ranges and prefilled in parallel. The abstract contrasts itself with probabilistic verification.
- Verdict: NOT RELATED for localization (efficiency paper); topically adjacent to the copy-versus-edit view. Cite cautiously because it is withdrawn.

## Searched, nothing found
- Overwatch (arXiv 2207.12456): appeared only as a "similar papers" title; not opened. NOT VERIFIED.
- CoEdPilot (arXiv 2408.01733), CodeEditor, Copilot NES / Zed / Cursor tab: not opened (CoEdPilot only appeared in search listings). NOT VERIFIED. All are trained edit-location predictors, so by design they are not the same mechanism.
- GECToR keep-tag probability as a detector: no paper found; the search did not surface GECToR's own paper. NOT VERIFIED.
- Forced decoding of the source as the target under a correction instruction (GEC or code): none found.
- SWE-bench line-level localization via likelihood/perplexity/surprisal given the issue: none found. Retrieval and RL localizers only (SweRank, CodeScout 2603.17829 and SWE-Explore 2606.07297 were seen in snippets only, not opened).
- Titles with "null edit", "identity rewrite", "edit hazard", "first-edit distribution", "rewrite likelihood", "forced copy" (through the search date): none found.
- "Knows but does not say" / logit-lens for bug localization: only probing papers (items 10, 11).

## Suggested related-work text
"Using token probabilities of text under a language model to flag errors is established in grammatical error detection (Wooding, Caines and Rei, under review; Cao et al., Findings of ACL 2023, observe that autoregressive correctors assign low probability to tokens needing correction) and glass-box quality estimation (Fomicheva et al., TACL 2020). Learned edit-location predictors (Coeditor, Wei et al., ICLR 2024; NES, Chen et al., FSE 2026 Industry) and generation-free supervised line localizers (Rozanov, arXiv 2606.09956; Stein et al., arXiv 2502.13966) are trained. To our knowledge, no prior work teacher-forces the unchanged file as the answer to an issue-conditioned rewrite instruction, and none uses the resulting copy probabilities as a zero-shot, training-free localizer or as an exact first-deviation distribution."

## Does the claim survive?
Yes, in a narrowed form. Safe: (a) issue-conditioned, instruction-conditioned null-edit forcing; (b) the closed-form first-edit distribution; (c) training-free line-level localization of human fix edits, plus the sub-threshold finding. Not safe: broad claims that token probability as an error or edit-location signal is new (GEC, GED, QE precedent), or that generation-free localization is new (item 9). Recommend framing as "transferring the GED/QE probability-as-detector idea to instruction-conditioned code rewriting, with the edit instruction and the source-as-target forcing as the novelty."
