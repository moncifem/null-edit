# Hostile review of PAPER.md (draft 1), 2026-11-12

Reviewer stance: senior ML/SE reviewer plus a Kaggle judge (Novelty, Quality, Relevance, Verifiability,
Clarity, 0-5 each). Points already fixed in REVIEW.md rounds 1-3 are not repeated unless the fix falls short.
All new numbers below were computed CPU-only from `results_dgx/an_e4b_test.json`,
`results_dgx/conflict_e4b_test/*.npz` and `results_dgx/gen_e4b_test_quote/gen.jsonl`, using the
project's own `line_features`, `fix_anchors`, `rank_of_best_gold`, `align_quotes` and `units_with_module`.
The scripts are in the session scratchpad (a1-a6.py) and are easy to fold into `extra_stats.py`.

Severity: **BLOCKER** = a judge or reviewer would reject or seriously discount the paper on this point;
**MAJOR** = a visible weakness that costs points; **MINOR** = polish.

---

## 0. Number audit (PAPER.md against the report files)

Every concrete number in the Abstract, §4.1, §4.2, §4.3 and §4.6 matches `report_e4b_test.md` /
`extra_e4b_test.md` / `EXPERIMENTS.md` up to rounding (69/38/45, 27%, median rank 4, 64% S, 55 vs 18
pure-insertion, 69 vs 34 macro, 51 vs 50 with −1.0 [−7,+5], 62/84, 63.7→"64%", 3.9/3.8/28.5/×7.4,
1.4→5.0 nats, 75.8 vs 64.8 [3.5,19.1], 18.7). §3 "300 of 317" checks out (the largest scored file has
31,702 tokens; the smallest skipped one has 32,310). Problems:

| Where | Problem |
|---|---|
| Table 1, "Length only", function columns (27/43/52) | This is `urank_random|sum` (random line scores summed). The pre-registered *function length* baseline (`unit_length`) is computed in `analyze_conflict.py:317-318` but **never written to `row`**, so `report.py` silently drops it. Recomputed: function length in lines gives 28.0/41.7/52.0; function length in tokens (`urank_line_ntok|sum`, already in the JSON) gives **29.7/44.0/53.0**. Report the token-length row as the length baseline, since it is the strongest. |
| §3 "first 250" vs Table 1 "240 issues" | 10 of the first 250 instances have no scorable file (17 files skipped for size). Say so in §3. |
| §4.8 "44% vs 56%" | n = 16 DEV files (±25 pp). It is also the DEV set that was used to *choose* the new formulation, so it is a design-stage observation, not a held-out negative result. Say "on 16 development files". |
| §4.3 "1.4 to 5.0 nats" | These are medians. Say "median". |
| §5 "a short generated answer costs about as much as two scoring passes" | DGX: 13.5 s vs 9.5 s (1.4×); Mac: generation is cheaper. Give both numbers in one clause. |
| Abstract "vanishes under a wrong issue (16%)" | 16% is above random (12%) and equal to line length (17%). "Falls to the line-length baseline (16% vs 17%)" is accurate; "vanishes" is a stretch. |
| Contribution 2 "far better ... than asking the same model" | Contradicted at function top-1 (a tie). Write "at line level". |
| Contribution 3 and §5 "our controls show both conditions are necessary" | RB/R0 have **no held-out result** (DEV pilot only; HYPOTHESES N2 is PILOT). As written this is an unsupported claim; it also appears outside a placeholder in §5. |
| Abstract "fragile to 4-bit quantization (−11 points)" | Backend, kernels, community quantization and chunked-cache numerics are all confounded (EXPERIMENTS.md says so). It is stated as causal in the abstract before the de-confounding run exists. |
| §3 "Functions are leaf-most `def` spans" | `common.py:154-163` does the opposite: nested defs are merged into the **outermost** def under a class/module (no recursion into FunctionDef). Plus "gap" units (imports, class headers, module code) are ranked too: 70/300 files have a gold line in a gap unit. Say "outermost function or method, plus residual module/class blocks". |

---

## Ranked findings

### F1 — BLOCKER: Claims in the contributions, related work and abstract run ahead of the evidence
*Evidence.* Contribution 3 and §5 ("our controls show both conditions are necessary") rest on RB/R0,
which have only a DEV pilot (HYPOTHESES.md:63, status PILOT). The abstract states quantization as a
cause (see table above). The pre-registered generated baseline (N3: "numbered file", line ranges) is
the one marked `[[..]]`; the reported quote baseline was added later, with a mapping (`align_quotes`)
written *after seeing the first numbers* (EXPERIMENTS.md:131). The paper discloses none of this.
*Fix.* (a) Until `report_e4b_ctrl.md` exists, cut "and the instruction" from contribution 3, §4.3's
title and §5. (b) Abstract: "the 4-bit MLX arm scores 11 points lower on the same files; [[the cause is /
is not weight precision]]". (c) §3: one sentence saying the quote baseline and its aligned mapping are
post hoc, that the pre-registered line-range baseline is reported in row 4, and that the strict mapping
gives 36.0 at line hit@10.
*Cost.* Text only. The controls themselves take ≈45 min of GPU (300 files × 2 passes × ~4.7 s) and are
already queued; make sure they cover the same 300 files, not `--limit 60/100`, or report their n.

### F2 — BLOCKER (for the line-level headline): hit@10 against a generated answer is not budget-matched; fix it and add the free "greedy rewrite" result
*Evidence.* The quote prompt says "up to 5 lines", but the model ignores this. After `align_quotes`, an
answer lists a **median of 11 lines** (IQR 8-14, max 24). **60% of answers hit the 160-token cap**
(`gen_tokens` = 160), and many dump whole blocks starting from the top of the file (e.g.
sympy-16886, django-15277 in `gen.jsonl`). The line rank of the generated answer
(`analyze_conflict.py:287-302`) is "lines read in answer order, else nl+1". So hit@10 compares a full
ranking with a list whose ceiling is its any-hit rate: **49.3%**. Only 7% of quoted lines fail to match
(247/3,563), so fuzzy matching would not help. The handicap is format plus cap, not matching.
A skeptic will say: "you asked a 4B model for a format it cannot follow, cut it off at 160 tokens, and
scored it on a list it never produced."
*What closes most of the hole, at zero cost (computed):*
- **Budget-matched comparison.** For each file, let k_i = the number of distinct lines the answer named
  (mean 10.8). Then the generated answer hits 49.3%, H@k_i 66.7%, S@k_i 64.0%, BM25@k_i 37.3%. The gap
  survives at 17 points. Report this row; it removes the "unfair k" objection.
- **The greedy rewrite is free from the same pass, and it is the paper's best argument.** If every
  original token has p_t ≥ 0.5, it is the argmax, so a greedy "rewrite so the issue is fixed" by the same
  model reproduces the file unchanged. This holds **exactly**, under the same numerics. That is the case
  for **84/300 files (28%)**. On those 84 files, where letting the model write yields *no edit at all*,
  H still puts a gold line in its top 10 for **64%** (BM25 38%, quoted answer 39%). This is the cleanest
  evidence for the title's "without letting it write": the knowledge sits in sub-argmax probability mass
  that generation throws away. Put it in §4.1 and the abstract. (Caveat to state: bf16 chunked scoring
  noise of 0.04-0.62 nats per token (RESEARCH_LOG 20:20) can flip tokens near p = 0.5, so report the
  count with p ∈ [0.45, 0.55].)
*Single cheapest extra baseline that closes the rest:* **"Let it write the fix":** greedy generation of
an edit (SEARCH/REPLACE block or unified diff with ≥3 context lines, 384-token cap, thinking off),
locations read from the SEARCH/removed lines. This is what an agent actually does. It removes the
"wrong output format" objection because the location falls out of an edit. Cost ≈ 300 × 25-30 s ≈
2.5 GPU-h with the current 12 tok/s Python loop. Switching `scorer_torch.generate` to HF `generate`
with a KV cache / static cache should at least double that speed; check this first. A thinking-on
variant on 100 files (≈2 h) answers "you disabled reasoning" and can be a subset.

### F3 — MAJOR: The "complementary" sentence (§4.2) is vacuous
*Evidence.* "One of them is right at top-1 on 64%" (H ∪ generated, 63.7%). But H ∪ BM25 = **64.7%**,
H ∪ function length = 60.0%, generated ∪ BM25 = 62.7%. Any two weakly correlated rankers give this.
*Fix.* Delete it, or replace it with a deployable combination. "Generated lines first, then H" is
computed below (F8): it beats both components in the read-budget analysis (81% within 1k tokens).
*Cost.* Analysis only.

### F4 — MAJOR: Memorization. Say exactly what the wrong-issue control rules out, and fix the LIVE control before it runs at scale
*What the wrong-issue control rules out:* that the hazard is a property of the file (hard-to-copy
lines, unusual tokens) or of the prompt frame. *What it does NOT rule out:* that the model memorized the
issue→fix association, or the **post-fix version of the file** (the fixed repository state has been
public on GitHub since 2023; [17] shows models recall SWE-bench file paths from the issue alone). A
memorized fix lowers p_t at exactly the gold lines under the right issue, and only under the right
issue, so it passes the wrong-issue control by construction. The DEV "blind" negative (no file in
context ≈ BM25) is weak evidence against verbatim recall of the whole fixed file, but not against
localized recall.
*LIVE design problems (checked in `results_dgx/conflict_e4b_live/log.jsonl`):*
- With ≤3 instances per repository, the same-repo/disjoint-files pool is tiny. **5/38 wrong issues
  come from another repository**, and the wrong/right issue length ratio has a 10-90% range of
  **0.33-27×** (Verified: 0.74-1.20). On LIVE, H is computed against a badly mismatched control, and
  the wrong-issue row is an easier control than on Verified. Fix: draw the LIVE wrong issue from LIVE
  ∪ the remaining post-cutoff pool of the same repo, and if that fails, match on length across repos
  (or truncate to matched length). Report the same-repo fraction.
- A partial LIVE result already exists (`report_e4b_live.md`: 38 files, H 65.8 vs BM25 47.4, CI
  [51,80]). Fix N now (all 200 `live_ids`) and say so, or a judge will suspect optional stopping.
- LIVE has no generated-answer baseline (`gen_e4b_live_quote` is missing). Without it, LIVE cannot
  support "beats asking the model" after the cutoff. It costs about 200 files × 10 s ≈ 35 min.
*Wording.* "Issues created ≥ 2025-03-01, at least five weeks after the knowledge cutoff stated in the
Gemma 4 model card (January 2025) [16]. We cannot inspect the training corpus. The LIVE repositories
also differ from Verified's, so a drop on LIVE could reflect either memorization or a population shift;
we therefore compare methods within LIVE." Quote the card's exact phrase (knowledge vs training-data
cutoff). If the card gives a release date, also report the subset of issues created after the
release.
*Cost.* Text, plus about 1-1.5 GPU-h for LIVE R/RX/gen on 200 instances (median file 328 lines, so
cheaper per file than Verified).

### F5 — MAJOR: Function level. The sum aggregation is length-driven, and the paper's length baseline is the weaker one
*Evidence.* The top-H function is a median **7.1×** longer than the file's median unit. Function length
in tokens gives 29.7% hit@1, not 27% (see table above). The length-free variants are about as good:
`Hnorm|sum` 49.0/72.3/84.0, `H|max` 48.0/71.3/82.7, `H|top3` 49.7/72.7/82.7. So the function result does
not depend on the length prior, and the paper should show that.
*Fix.* Report the token-length baseline, and show `H|max` (already a post-hoc row) next to `H|sum`
with one sentence: "a length-free aggregation gives the same result". Rename the units to "function or
module block".
*Cost.* Analysis only.

### F6 — MAJOR: Multi-file instances and point-estimate weighting (round-1 M6 fix is incomplete)
*Evidence.* The cluster bootstrap fixes the CI but not the point estimate, which is file-weighted.
`sympy__sympy-13091` contributes **19 of 300 files** (6.3%). BM25 ranks the gold line first in 15 of
those 19, which explains BM25's odd hit@1 CI [5, 21]. Instance-macro estimates: H@10 70.4, BM25@10
33.4, quoted answer 43.9; line hit@1 H 28.7 vs BM25 7.6; function hit@1 H 54.7 vs generated 54.2 vs
BM25 37.0. The current weighting favours the baselines, so this *strengthens* the paper, but the
reviewer will ask.
*Fix.* Report instance-macro point estimates next to the file-weighted ones, or as the primary
estimate (one footnote plus one column).
*Cost.* Analysis only.

### F7 — MAJOR: Statistics: multiplicity, an incompletely reported pre-registration, and the arm switch
- Roughly 17 paired tests are reported. Pre-registered primary metrics are line hit@1/5/10 + median and
  function hit@1/3/5 + **MRR**. MRR is **not reported anywhere** (it is a pre-registered primary
  metric), and neither is the pre-registered function-length baseline (F0). Declare one confirmatory
  contrast (N1: H vs BM25, line hit@10, p < 1e-4) and Holm-correct the family of primary metrics.
  Function hit@1 H−BM25 (p = 0.022) does not survive Holm over 8 tests; say so.
- "p = 0.0000" from 10,000 resamples means p < 1e-4. Print it that way.
- The pre-registration was written for the 4-bit MAC pipeline. The interim look at 91 MAC files (log
  19:40) showed "function H 44 vs BM25 43", then the headline moved to the bf16 DGX arm, which scores
  11 points higher on the same files. The switch was operational (fan noise, user direction, 19:45),
  but nothing in the paper says it happened before any DGX number existed. Add that sentence to the
  pre-registration paragraph, and report the MAC 98-file numbers in an appendix table so nobody can say
  "you switched to the arm that won".
- The 20k→32k deviation is handled well: the ≤20k subset is 71 vs 39. Keep it.
*Cost.* Analysis plus text.

### F8 — MAJOR (Relevance): No evidence that an agent benefits. A free analysis closes most of this
*Computed (analysis only).* An agent that opens ±10-line windows around lines in score order, counting
the tokens it reads until a gold line is visible (median file 6.7k tokens):

| reading order | median tokens read | ≤ 1k tokens | ≤ 2k tokens |
|---|---|---|---|
| H | 344 | 79% | 88% |
| S (1 pass) | 416 | 75% | 85% |
| generated answer's lines, then H | 274 | **81%** | **90%** |
| generated answer's lines, then top-down | 273 | 67% | 72% |
| BM25 | 636 | 59% | 73% |
| top-down | 1,996 | 33% | 51% |

So "a hazard-guided agent sees the edit site within 1k tokens (15% of the file) in 79% of files, vs 59%
for BM25". It is also the first deployable combination with the generated answer. A
`context_budget.py` step is referenced in `analyze_all.sh` but the file does not exist in `src/`:
write it with this definition. State that this counts the *reader's context* tokens, not the
prefill compute (H costs two file prefills).
*Cheap GPU step (< 1 h, one GPU, E4B, no tests):* **map-guided edit.** The same SEARCH/REPLACE
generation as F2, with and without the top-5 H lines listed in the prompt ("lines the model flagged as
likely to change: …"). Measure whether the edit touches a gold line, and whether its SEARCH block lies
within ±2 of a gold line. On 100 files × 2 arms ≈ 1 h at 12 tok/s, less with a KV cache. It turns "a
map" into "an agent tool that improves the agent's own edit" with the same model, which this track
needs.

### F9 — MAJOR: The fixed-point verification design has a memorization leak and lacks the baselines it needs
*Evidence (`run_fixedpoint.py`, `analyze_fixedpoint.py`):*
- **Memorization of the post-fix file.** Verified gold fixes are public. A gold-like candidate gets low
  residual hazard *because the model has seen that code*, not because it is correct. Resolved
  leaderboard patches resemble gold more, so this inflates the resolved-vs-unresolved AUROC. `sim_gold`
  is shown only as a competing ranker, not partialled out. The docstring promises "a logistic regression
  with instance fixed effects removed (within-instance centring)", and **it is not implemented**.
  Candidates with `equals_gold=True` stay in the candidate set.
- §4.7's "residual hazard falls from xx to xx after the human fix" has the same confound (gold is the
  memorized endpoint) and should not be framed as validation.
- Selection: single-file gold, file ≤ 6k tokens, tasks with both a resolved and an unresolved
  candidate. That is a middle-difficulty, small-file subset. Report the subset size and its gold-line
  stats.
- Engineering: `analyze_fixedpoint.py:11` hardcodes `../results/` (ignores `NULLEDIT_RESULTS`), and
  `analyze_all.sh:61` calls it with `--tag e4b`, so it parses `tag = "--tag"`. It will crash.
*Baselines that must appear in the same table:* random (0.5 / pool share); diff size (present);
consensus (present); similarity to gold (present, as an oracle); **within-instance partial AUROC of −H
after regressing out sim_gold and n_changed_lines**; **excluding equals_gold candidates**;
**unconditional entropy-delta** (Yang et al. 2024 [11] already rank patches by entropy delta: S of the
patched file under R0/no-issue minus S of the original), since otherwise the novelty claim over [11]
is open; **same-model LLM-as-judge** (one forward pass: log P("Yes") for "Does this patch fix the
issue?"; costs about one null-edit pass); and **map consistency** (does the patch touch the original
file's top-k H lines? This needs the original's line map, which `run_fixedpoint.py` does not save. Save
per-line arrays, or reuse `conflict_e4b_test` npz for overlapping instances).
*Cost.* Analysis fixes are CPU. The judge baseline is ≈ 1 pass per candidate (~same as the existing
run, ≈ 30-45 min).

### F10 — MAJOR: The file-level design has a tie bug, a path confound and oracle inclusion
*Evidence (`build_file_cands.py`, `analyze_filelevel.py`):*
- **Ties favour the gold file.** `order = sorted(m, key=lambda p: -m[p])` over a dict whose first key is
  the gold file (`paths = [gold] + distract`). Python's sort is stable, so every tie ranks gold first.
  `P(edit) = 1-exp(-S)` saturates to exactly 1.0 for S ≳ 37 nats, so ties are real for that row.
  Fix: random tie-breaking, or shuffle the paths.
- **The path is in the prompt.** "Rewrite `{path}` so that the issue is fixed" shows the file path, and
  issues often name the module or file. Total hazard can then reflect path-issue match rather than
  content. Required baseline: a path/module-name match score (BM25 of the issue vs the path tokens,
  plus "issue mentions the basename"). Required ablation: replace the path with a neutral name for a
  subset (this needs GPU).
- **Oracle inclusion.** The gold file is always a candidate, whatever its BM25 rank. Report the
  distribution of the gold file's repo-wide BM25 rank, and an end-to-end variant: re-rank BM25's top-4,
  counting a miss when gold is not retrieved.
- File length (present) and BM25 (present) stay. Add "H per kilo-token" as the length-free row
  (present) in the same table.
- Engineering: `analyze_all.sh:60` passes `--tag e4b_test`, but the script reads `sys.argv[1]`, so it
  crashed (`report_filelevel.md` currently contains that traceback). The distractor npz files share the
  `conflict_e4b_test` directory with the main run. `analyze_conflict` filters on `gold` correctly, but
  `merge_frames.py` and any future reruns should be checked for that.
*Cost.* CPU, plus ≈ 15-20 min of GPU for a renamed-path ablation on 60 instances.

### F11 — MINOR: Labels and metric. Mostly sound; report the robustness that already exists
Checked and **not** a problem:
- Ties: 94% of lines have H < 1e-3, but the best gold line has H exactly 0 in only 1/300 files.
  `rank_of_best_gold` breaks ties at random, so the near-zero tail only affects deep ranks.
- First-token-of-line tokenization: the first token of a line carries a median 0.4% of S. The
  hazard is not an artefact of indentation tokens.
- Position: the top-H line sits at a median relative position of 0.50 (10-90%: 0.12-0.92). Ranking by
  position gives 7% hit@10. No early-line bias.
- Imports: only 1 file has gold lines that are all imports. Excluding import gold lines gives H@10 68.6%.
- Issue hints: in 24 files the issue contains a gold added line verbatim (H 100%, BM25 75%, gen 58%).
  Without hints *or* quoted gold lines (261 files): H 66 / S 61 / BM25 33 / quoted answer 43. The
  method does not get its credit from issues that spell out the fix. **Put this stratum in the
  extra table**, because a judge will ask.
- Mirror control for H: `gain_R-RX_pos` (lines the *wrong* issue makes harder relative to the right
  one) gets 8.3% hit@10 (random 12%). This shows that the positive-part construction does not
  manufacture signal. It is free; report it as the H-specific control.
- The identity's own quantity, P(τ ∈ line i) (`first_R`), gets 60.3% hit@10 (S 63.7%). Report it once.
  The ranker S is a *conditional hazard*, not the first-edit probability, and the abstract's "exactly"
  is about P(τ), which is not the ranked quantity.

Remaining minor points:
- The "best-ranked gold line" metric rewards hitting any one of many gold lines (≥6 gold lines: 77%
  vs 1-2: 64%), and an agent needs *every* hunk. Add hunk-level recall@k (the share of hunks with a line
  in the top-k), analysis only.
- Insertions are double-anchored (both neighbours count as gold). The quote prompt asks for the line
  *before*, which is consistent. Cite the modified-only labelling (H 65.7 vs BM25 39.5, n = 233) in the
  main text, not just in EXPERIMENTS.
- The wrong-issue selection uses the *gold file set* (`run_conflict.py:105`) for disjointness. That is
  label information, though harmless here. A deployable rule is "disjoint from the file being scored";
  state that this is equivalent for scored gold files.
- "Exactly" in §2/abstract holds for temperature-1 ancestral sampling, under this chat template and
  the forced "```python\n" opening, over **token** sequences: a non-canonical tokenization of identical
  text counts as a "departure". Add one clause.

### F12 — MINOR: Novelty and positioning
*Strongest "trivial / known" objection:* "This is the verification pass of speculative editing
(EfficientEdit, Cursor, Predicted Outputs), where rejected positions *are* the edit positions, combined
with 2015-2024 surprisal fault localization. Of course the tokens the model would rewrite have low
probability under an edit prompt: that is the definition of its edit distribution. The gain over
'asking' is an instruction-following artefact of a 4B model." Also expect "next-edit-location
prediction" work (e.g. Coeditor-style edit models) to be raised. LITERATURE.md does not cover it.
Check it and add one sentence.
*Best honest answer (all supportable after F2/F8):* (1) the mechanism is known and the identity is
elementary, and we say so; (2) nobody had measured whether these discarded probabilities localize
issue-driven edits, and with the conditioning (issue *and* fix instruction, with the file in context)
they do, while unconditional or wrong-issue variants fall to the length baseline; (3) the signal is
**sub-argmax**: in 28% of files the same model's greedy rewrite changes nothing, yet the map localizes
the fix there 64% of the time. A speed-oriented speculative editor never surfaces this, because it only
sees where greedy/sampled decoding actually diverges. (3) is the sentence that makes "we claim no
speed advantage" a strength rather than a concession.
Defensibility of "no speed advantage": fine, and honest. Do not bury it: one clause in §5 is enough,
with both machines' numbers.

### F13 — MINOR: Clarity in the first 60 seconds
- Title: "The Null Edit" means nothing to a judge before they read §2. Suggestion: **"The Null Edit:
  Gemma 4 Shows Where It Would Fix Your Code in One Forward Pass, Even When It Would Not Write the Fix"**.
  Shorter: "Where Would Gemma Edit? Reading Bug Locations from a Rewrite It Never Writes".
- Abstract: lead with the result and the sub-argmax finding, and put caveats after the numbers. Too
  many placeholders currently sit in the abstract. Final abstract: at most one sentence each for LIVE
  and scaling. Suggested opening: "Asked to rewrite a file so that an issue is fixed, Gemma 4 E4B
  would, under greedy decoding, change nothing in 28% of files, yet its token probabilities over the
  unchanged file point to the human fix's line in the top ten in 64% of those files, and in 69%
  overall (BM25 38%, the model's own answer 45%; 67% vs 49% at an equal number of lines)."
- Add a 6-line worked example (Figure 1 exists as `figures/fig1_example.png`; reference it in §2): issue
  excerpt, three file lines, the hazard per line, gold marked.
- Define hit@k and "best-ranked gold line" in one plain sentence near Table 1 ("a reader who checks
  the top 10 lines finds an edited line").
- Table 1: rename "Length only" to "Length (tokens)"; add a "lines listed" column for the generated
  answer (median 11) and the budget-matched row; add n per row where it differs.
- §2: "H_i = Σ max(0, log p^wrong − log p)" — say in words: "how much harder the right issue makes
  copying this line than a wrong issue does".
- Figure 3 is referenced but does not exist yet (`figures/` has fig1 and fig2 only).

---

## Highest-value use of ~12 GPU-hours on one DGX Spark (in order)

1. **Make the held-out claims unconditional (≈ 3 h):** RB/R0 controls on the same 300 files (≈ 45 min);
   the pre-registered line-range generated baseline (queued; ≈ 1 h); the 4-bit-weights-in-PyTorch
   run on the 91 common files (≈ 15 min), or drop the causal wording; LIVE with all 200 instances,
   fixed length-matched wrong issues, and the quoted-answer baseline (≈ 1-1.5 h). Without these,
   contributions 3-4 are placeholders.
2. **"Let it write" baseline plus map-guided edit (≈ 3-4 h; first switch generation to HF `generate`
   with a KV cache):** greedy SEARCH/REPLACE edit on the 300 files (no hint), the same with the top-5 H
   lines listed (100-300 files), and a thinking-on variant on 100 files. Together with the free
   greedy-no-op and read-budget analyses, this answers both "you handicapped the baseline" and "where
   is the agent?".
3. **Model sizes, trimmed (remaining ≈ 4-5 h):** E2B and 12B on 100 issues (R+RX), 26B-A4B on 100, 31B
   on ≥ 50 issues or S-only (one pass) on 100. Drop 31B-LIVE and 12B-LIVE before dropping 31B on
   Verified. If the fixed-point run is kept, add the LLM-as-judge pass (≈ 30-45 min) and the sim_gold
   partial analysis. Otherwise move fixed-point to "future work". As designed it is the most
   attackable section, and a weak §4.7 hurts more than a missing one.

Analysis-only items to do regardless (≈ 2 h of CPU): F2 budget-matched row and greedy-no-op result;
F3 deletion; F5 length baseline and `H|max`; F6 instance-macro; F7 MRR, Holm, arm-switch sentence; F8
read-budget table; F9/F10 script bugs and tie-breaking; F11 hint stratum, mirror control, hunk recall.

## Scores as the draft stands (0-5)

| Criterion | Score | Why |
|---|---|---|
| Novelty | 3 | Known mechanism, new measurement. Rises to 4 if the sub-argmax / greedy-no-op finding is made central. |
| Quality | 3 | Pre-registration, clustered bootstrap, replication and honest ties are strong. Pending controls stated as results, a non-budget-matched generated baseline, missing pre-registered metrics (MRR, function length), and quantization stated as causal pull it down. |
| Relevance | 2 | Agent track, but no agent and no downstream effect. The read-budget table plus a map-guided edit run would make it 4. |
| Verifiability | 4 | Per-token npz files, scripts, log, an independent replication. Docked for the broken file-level/fixed-point analysis invocations and the post hoc `align_quotes` not being flagged in the paper. |
| Clarity | 3 | The method is crisp and the writing tight, but the title is opaque, the abstract is half placeholders, the unit definition is wrong, and the "complementary" sentence misleads. |
