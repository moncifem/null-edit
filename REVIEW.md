# Adversarial review and responses

Reviews were commissioned from independent subagents that did not share the PI's context.
Full texts: `notes/review_design.md`, `notes/prior_art_surprisal.md`, `notes/prior_art_nulledit.md`,
`replication/REPORT.md`.

## Round 1 — design review before the main run (Opus critic, 2026-11-11 ~18:40 UTC)

Reviewed the first formulation ("blind" likelihood shift) and the analysis code.

| # | Finding | Severity | Response |
|---|---------|----------|----------|
| B1 | Line length (tokens) alone reached AUROC 0.69 — higher than several drop features; it was not a baseline. | Blocker | Added `line_ntok` and function-length baselines to every table; added per-token-normalised scores (`Hnorm`, `Snorm`) as a length control. The first formulation was dropped anyway (see RESEARCH_LOG 18:45). |
| B2 | ~140 feature × aggregation choices tuned on 25 instances, no CIs. | Blocker | One primary feature (H), one secondary (S), one aggregation (sum) pre-registered in `HYPOTHESES.md` Revision 1 *before* any held-out scoring; instance-clustered bootstrap CIs and paired tests in `src/report.py`. Anything else is labelled post hoc. |
| B3 | Memorization not ruled out; SWE-bench-Live control confounds "unseen" with a different repo population. | Blocker | LIVE control kept (issues ≥ 2025-03, cutoff Jan 2025); wrong-issue control run on LIVE too; reported with its own baselines so the comparison is within-set. Residual limitation stated in the paper. |
| B4 | Patch experiment leaked gold into the context and scored raw sums over diff tokens. | Blocker | That experiment was replaced by fixed-point verification (`src/run_fixedpoint.py`): the context is only the patched file itself; baselines for diff size, consensus and similarity-to-gold are reported. |
| M1 | 32% of gold lines are insertion anchors; blank anchors silently dropped. | Major | `fix_anchors` moves blank anchors to the nearest tokenised line; "modified-lines-only" labelling reported as robustness. |
| M2 | Copying from the issue makes quoted lines *more* likely; unsigned features pick up lexical overlap. | Major | Only signed features are used (H keeps the positive part of log p_wrong − log p_right). |
| M4 | Generative baseline handicapped by a strict parser. | Major | Lenient parser; parse failures count as misses and are reported; a second generative baseline that *quotes* lines instead of giving numbers was added (no line-number arithmetic needed). |
| M5 | Only gold files are scored (oracle file). | Major | Claims restricted to within-file localization; separate file-level experiment with BM25 hard negatives (E4). |
| M6 | Per-file averaging over-weights multi-file instances; blank lines could win a unit `max`. | Major | Bootstrap is clustered by instance; token-less lines are excluded from unit aggregation. |
| M7 | Wrong-issue control could share files with the true issue and differ in length; seeding not restart-safe. | Major | Control issue now drawn per instance (seeded by instance id) from same-repo issues with disjoint gold files and closest length. |

## Round 2 — prior-art attacks (Sonnet examiners)

* No same-idea work found for (a) issue-conditioned likelihood maps of existing code or
  (b) null-edit teacher forcing as a localizer / verifier. Nearest ancestors: speculative-edit
  decoding (EfficientEdit; Predicted Outputs; Cursor) — same forward pass, used for speed, positions
  not exposed or evaluated; naturalness / entropy line of work (Ray 2016; Yang 2024; LLMAO; Campos
  2024) — unconditional or trained; concurrent: Hennara et al. 2026 (patch likelihood as a training
  signal). **Consequences for the paper:** the identity is presented as elementary; the speed
  argument is not claimed as a contribution; EfficientEdit is cited as the mechanical ancestor.

## Round 3 — independent replication of the analysis (Sonnet replicator, 19:30 UTC)

A replicator re-implemented label construction, token-to-line assignment, S, H and the ranking from
a written spec, without access to the analysis code. **All DEV numbers reproduced exactly** (S:
13.3/43.3/66.7, median rank 7; H: 16.7/56.7/70.0, median rank 5). Noted: scores are driven by very
few tokens (≥95% of tokens have log p > −0.001), as expected for a copy task.

_Further rounds are appended below._

## Round 4 — adversarial review of the first full draft (Opus critic, 2026-11-12 ~00:05 UTC)

Full text: `notes/review_draft1.md`. The reviewer re-derived numbers from the saved per-token logs
(CPU only) and audited every number in the draft against the reports (all matched to rounding).
Scores given to the draft as it stood: Novelty 3, Quality 3, Relevance 2, Verifiability 4, Clarity 3.

| # | Finding | Severity | Response |
|---|---------|----------|----------|
| F1 | Claims ahead of evidence: "controls show both conditions necessary" (RB/R0 only piloted); 4-bit loss stated as causal; quote baseline + `align_quotes` are post hoc; "leaf-most def" is wrong (outermost defs, gap units ranked); "far better than asking" contradicted at function top-1. | Blocker | Abstract, contributions, §3, §5 rewritten. Post hoc mapping and the strict-mapping number (36%) disclosed in §3. Unit definition corrected in paper and docstring. RB/R0 run kept in the queue (100 issues); the 4-bit claim now waits for the de-confounding run (MLX 4-bit weights de-quantized into the PyTorch model, `src/make_q4_model.py`). |
| F2 | hit@10 vs generated answer not budget-matched (answer lists a median of 11 lines; ceiling 49%). | Blocker | Budget-matched comparison added to `report.py` (H 66.7 vs 49.3, +17.3 [11.8, 23.1]). Added the reviewer's "greedy no-op" analysis after re-deriving it independently: 84/300 files have every token p ≥ 0.5; H line hit@10 64% there (BM25 38%, quoted 39%). New "let it write" baseline (`src/run_edit.py`, search/replace edit) queued. |
| F3 | "Complementary, 64%" is uninformative (any two rankers look complementary). | Major | Sentence deleted. |
| F4 | Memorization: wrong-issue control cannot rule out memorised issue→fix pairs; LIVE wrong issues often cross-repo / length-mismatched; fix N; add a generated baseline on LIVE. | Major | Wording changed (limitations + §4.4). LIVE N fixed at the first 150 ids of `results/live_ids.txt` (decided before the partial look, see queue file `todo_v4`). On LIVE, S (one pass, independent of the wrong issue) is reported as the robust score; H is reported with the share of same-repo wrong issues. `genq_e4b_live` queued. |
| F5 | Function-level length confound; function-length row missing from the table (bug: computed, never written). | Major | Bug fixed; token- and line-length rows reported (29.7% / 28.3% top-1). Length-normalised H reported (49.0% top-1). |
| F6 | File-weighted estimates; one issue contributes 19 files. | Major | Issue-weighted estimates added (H@10 70.4 vs BM25 33.4). |
| F7 | MRR pre-registered but missing; no multiplicity correction; "p = 0.0000". | Major | MRR column added; Holm-adjusted p-values; p < 1e-4 notation. Function hit@1 H−BM25 survived Holm at 0.044 over the 8 tests then listed; with the tests added later the family grew and it no longer does (Holm 0.11) — the paper now gives the unadjusted p = 0.02 and says so (Round 6). Sentence on the MAC→DGX switch added to §3. |
| F8 | No evidence that an agent benefits. | Major | (i) Context-budget analysis (`src/context_budget.py`, written independently before the review returned; the reviewer had not seen it). (ii) Map-guided edit experiment queued: same model writes one search/replace edit with no hint / top-5 H lines / top-5 BM25 lines (placebo). |
| F9 | Fixed-point design confounded by similarity to the public gold fix; analysis script crashed on its arguments. | Major | Argument bug fixed; candidates identical to the gold fix excluded by default; within-instance logistic regression with `sim_gold` and diff size as covariates added; "hazard removed by the patch" score added. Result will be reported as exploratory whatever it shows. |
| F10 | File-level: ties favoured gold; no path baseline; argument bug. | Major | Random tie-breaking; "path named in issue" baseline; argument bug fixed. Gold-always-a-candidate is stated as a design limitation. |
| F11 | Sanity checks to report (ties, first token of line, position, mirror control, first-edit probability ranking). | Minor | Position and mirror-control rows added to the report (7% and 8% hit@10); first-edit-probability ranking (60%) stated in Limitations. |
| F12 | Novelty objection: "speculative-edit verification + surprisal localization". | Minor | Positioning rewritten around the sub-threshold finding (§4.3): a speculative editor only sees realised divergences. |
| F13 | Title opaque; abstract half placeholders. | Minor | Subtitle to be revised at freeze; abstract restructured. |

## Round 5 — second prior-art attack: edit-location prediction, error detection in NLP (Sonnet examiner, 2026-11-12 ~00:40 UTC)

Full text: `notes/prior_art_editlocation.md` (12 searches, 13 primary pages opened). **No same-idea work
found.** Narrowing accepted: "token probability as an error/edit-location signal" and "generation-free
localization" are *not* claimed as new — they are established in grammatical error correction (Cao et al.,
Findings of ACL 2023), glass-box translation quality estimation (Fomicheva et al., TACL 2020) and trained
code localizers/probes (Coeditor; Stein et al. 2025; Rozanov 2026). What the paper claims: the
instruction-conditioned null-edit forcing, the exact first-edit distribution, training-free line
localization of human fix edits, and the sub-threshold finding. Related work updated with refs [19]–[22];
an unverified "under review" thesis found by the examiner is not cited.


## Round 6 — Opus critic on draft 2 (2026-11-12 02:00 UTC)

Full report: `notes/review_draft2.md`. Scores as the draft stood: Novelty 3, Quality 3, Relevance 2,
Verifiability 4, Clarity 3. The review targeted the passages edited around two fresh results (line-range
baseline, 4-bit check).

| # | Finding | Severity | Response |
|---|---------|----------|----------|
| G1 | §4.3 "the model knows where before it says so" is contradicted by the paper's own row: on the 84 greedy-no-op files the *asked* model names the gold function first in 55% (map 49%). Headline used H (needs a second prompt), not S; the greedy claim depends on an undisclosed ```` ```python ```` prefill; under sampling the median P(no edit) is 0.32; 18 files have min p in [0.5, 0.6). | Blocker | Section retitled "Below the decoding threshold (post hoc)" and rewritten: leads with S (54%), keeps H in brackets, states the asking number, the sampling number, the prefill (now also in §2) and the Live replication (50% vs 39%). Contribution 3 reworded. A no-prefill check on the 84 files (`run_noprefill.py`) is queued and pre-declared in `HYPOTHESES.md`. |
| G2 | Abstract and contribution 2 say the map beats asking without qualification; "remains better" on first mention; the answer's line top-ten is depressed by reading ranges top-down (it contains a gold line somewhere in 62% of files). | Blocker | Abstract and contribution 2 rewritten: asking wins the first guess (60% vs 50%), ties the first line, the map wins after. §4.2 retitled "Where asking wins", gives the 62% and points to the equal-budget comparison in §4.8. |
| G3 | §4.7 "weight precision, not software" omits a significant stack difference at function top-1 (−4.4 [−8.6, −1.1]); "on either software stack" implies a bf16 MLX run that does not exist; 98 files come from 83 issues. | Blocker | §4.7 rewritten with the reviewer's structure; abstract sentence replaced by "Community 4-bit weights lose 12 points to bf16"; practical advice added (at 4 bits use the map for lines, not functions). |
| G4 | Table 1 stale cells (BM25 line@5, length rows). Cause: one shared random stream, so adding a feature shifted tie-breaks. | Major | `analyze_conflict.py` now seeds per (file, feature) (`frng`); all reports regenerated; H and S rows unchanged, baseline rows now stable (BM25 12/30/38, length 2/11/17, random 2/8/12); Table 1 and §4.4/§4.5 updated. |
| G5 | Edit experiment: `adds_gold` credited lines copied from SEARCH; BM25 is not a placebo; no ceiling; deference confound; ambiguous SEARCH accepted; truncation and validity not reported; no primary outcome; hint shows line numbers the model cannot use. | Blocker (fixed before the run) | `analyze_edit.py` rewritten (introduced lines only, ≥12 chars, not present in the original; ambiguous = invalid; truncation; on_hint; splits by hint quality; no-op subset; Holm over secondaries). Arms changed to none / H / wrong-issue hazard (placebo) / gold (ceiling); hint text without numbers. Primary outcome and contrasts declared in `HYPOTHESES.md` Revision 2 at 02:02 UTC, before the job started. |
| G6 | Relevance: make §4.8 a measured recipe. | Major | Added the "ask, then read by hazard" ordering to `context_budget.py`: at a 5% reading budget 71% (map 66%, asking 64%; +5.3 [1, 10] and +7.7 [4, 12]); no gain at 10% (79% vs 80%). §4.8 rewritten around where to read / where to edit; intro reframed as a tool call. |
| G7 | Issue-weighted function top-1 (asking 65% vs 55%) omitted while the favourable issue-weighted line number is reported. | Major | Added to §4.2. |
| G8 | Size table needs the asking baseline at every size; cut patch check first, file ranking to a sentence. | Major | Line-range generation is queued for all four other sizes (26B and 31B on 60 issues). Patch check dropped from the paper plan; file ranking reduced to one sentence if it lands. |
| G9 | Clarity: "the map" undefined, nats, mirror-control sentence, three file sets in §4.7. | Minor | Fixed as proposed. Subtitle decision deferred to freeze. |
| G10 | Asking baseline missing on Live. | Major | `gen_e4b_live` (line ranges, 150 issues) is queued; placeholder in §4.5. |

Not adopted: generating 16 tokens "at the argmax margin" for the 18 borderline files (no GPU time); the
borderline count is reported in the experiment log instead.

## Round 7 — number audit of draft 3 (Sonnet subagent, 2026-11-12 03:50 UTC)

~150 numeric claims checked against `results_dgx/report_*.md`, `EXPERIMENTS.md`, `HYPOTHESES.md`;
~142 matched. Findings and responses:

| # | Finding | Response |
|---|---|---|
| A1 | §4.8 "10% ≈ 59 lines" used the median of non-blank lines (587); the budget is counted in all lines (median 686 → 69). | Fixed: "about 69 lines"; §4.1 now says "587 non-blank lines". |
| A2 | §3 said the quoted-lines baseline was "added before the held-out run". Its code ran on DEV at 22:19 UTC while held-out scoring finished at 22:14; it was run on held-out files after the map's numbers were known. | Fixed: "not pre-registered"; added "All three [asking baselines] were run after the map's held-out scores were known." |
| A3 | Contribution 2 "beats BM25 at every cut-off": function hit@1 is not significant after Holm. | Fixed: "on lines at every cut-off" (line hit@1 +15.0 [2.4, 25.2], @5 +24.7 [13.2, 35.0], @10 +31.0 [21.3, 40.2]). |
| A4 | §3 "All five … checkpoints" while only three sizes are scored. | Pending 26B A4B and 31B; wording will follow what is actually run. |
| A5 | Several numbers exist only in hand-written logs (4-bit paired differences, P(no edit) median, 62% "somewhere", 89 of 91 repositories, 60% first-edit ranking). | To do at freeze: a script that regenerates them (`extra_stats.py`), or drop the number. |
