# Design review of E1/E2 before the main run (hostile reviewer)

Scope: HYPOTHESES.md, RESEARCH_LOG.md, src/common.py, src/scorer.py, src/run_conflict.py,
src/analyze_conflict.py, src/run_generative.py, src/run_patches.py. No code was modified and no model was loaded.
Everything below was checked with CPU-only snippets: the tokenizer.json, unidiff on data/swebench_verified.jsonl,
and numpy on the 16 pilot `.npz` files already written to results/conflict_e4b_pilot/. All of them are dev-set files, so looking at them is allowed.
**The pilot numbers below come from 16 files and are noisy. Use them as warning signs, not as results.**

Facts established along the way:

| Check | Result |
|---|---|
| gold_edits on synthetic diffs (modify, delete, insertion at top of file, mixed hunk) | correct, no off-by-one; Verified has 0 zero-length source hunks (the case where `source_start-1` would be wrong) |
| Gold lines in Verified (621 non-test .py gold files) | 3214 lines: 2194 removed/modified + 1028 insertion anchors (32%) |
| Blank gold lines | 363 (11%); 255 of these are insertion anchors |
| Gemma 4 newline tokens | `\n`, `\n\n`, `\n\n\n` are pure-newline tokens. No vocab token mixes a newline with content. Indentation is a separate token. So **blank lines never receive tokens** (ntok=0, i.e. `valid=False`), and the token for "k blank lines follow" is attributed to the preceding line |
| Line splitting | `str.splitlines()` and `split('\n')` agree on all 621 Verified files. The Live files have not been checked |
| AST parse failures | 0 / 621 |
| Files > 40k tokens (skipped) | 20 / 621 (3.2%) |
| Mean non-blank line length | gold 37.8 chars vs all lines 32.8 |
| Gold lines quoted verbatim in issue (non-blank, ≥12 chars) | 110 / 2490 lines; 65 instances |
| Live set | 374 rows, 2025-03-01 .. 2025-09-01, 193 repos; 33 of 200 live_ids have **no other same-repo issue**, so they get no X frame |
| Prompt cache | `mx.array` implements `__deepcopy__`. RotatingKVCache multi-token updates use the concat path (no in-place writes). E2's prefill/score_with_cache index arithmetic is correct |

Pilot AUROC at line level (mean over 16 files, labels = `GoldFile.lines`):

| feature | AUROC |
|---|---|
| **ntok (line length in tokens, trivial)** | **0.692** |
| surp_U_sum / surp_U_max | 0.624 / 0.645 |
| drop_FU_sum / drop_FB_sum / drop_FX_sum | 0.548 / 0.578 / 0.550 |
| abs_FU_sum / abs_XU_sum (wrong issue!) | 0.723 / 0.619 |
| drop_FU_max | 0.751 |
| drop_FU_max, token-permutation null (deltas shuffled within file, buckets kept) | 0.591 |
| drop_XU_max | 0.578 |
| drop_FU_max residualised on surp_U_max + log ntok | 0.668 |
| position (line index) | 0.518 |

Token-level corr(surprisal_U, |logP_U - logP_F|) = 0.49. On lines quoted in the issue, mean drop_FU = **−16.2 nats**, against −0.43 on other lines (2 files only).

---

## BLOCKERS

### B1. Line-length confound, and the length baselines are missing (analyze_conflict.py:60-79, 163-170)
`*_sum`, `*_pos` and `abs_*` add up over a line's tokens, and even `*_max` is a maximum over more draws on longer lines. Gold lines are 15% longer than average.
In the pilot, **raw token count (AUROC 0.69) beats drop_FU_sum (0.55), drop_FB_sum (0.58) and drop_FX_sum (0.55)**. abs_XU_sum, computed with the *wrong* issue, scores 0.62. `ntok` is computed but explicitly skipped (`if name == "ntok": continue`, line 169), so the table never shows the line-length baseline. Random (0.5) is the wrong chance level for every feature in the table.

**Fix (analysis only, no GPU):**
(a) Add `ntok`, character length and `surp_U_*` as line baselines.
(b) Add a **token-permutation null** for each drop feature: permute the per-token delta vector within the file, re-aggregate with the same buckets, and average over 20 permutations. For max this was 0.59 in the pilot. Report the gain over this null, not over 0.5.
(c) Report residualised AUROC: regress the feature on log ntok and surp_U within each file, then take the AUROC of the residual. In the pilot this gave 0.668.
(d) At unit level, add `sum of ntok` as a baseline next to `unit_length`. The current `u.end-u.start` (line 184) counts lines, but the `sum` aggregation scales with tokens.

### B2. Garden of forking paths on 25 instances, no uncertainty, no paired tests (analyze_conflict.py:168-186, 194-207)
The grid is about 36 line features × (1 line metric + 3 unit aggregations) ≈ 140 configurations. It includes sign-agnostic features (`abs_`, `gain_`, `surp_*`) and is ranked by its own dev mean. With about 30 dev files, the winner's curse alone is several AUROC points. The test-set sample size and seed are also not fixed ("subsampled").

**Fix:**
- Before the test run, write the following into HYPOTHESES.md with a timestamp:
  - ONE primary feature with its sign and aggregation (for example `drop_FU_max` for line and `drop_FU_max|max` for unit).
  - ONE primary metric.
  - The comparison it must beat: the permutation null, surp_U, ntok, BM25 and generation.
  - The test N and seed.
- Use instance-clustered bootstrap CIs (resample instances, not files) and paired bootstrap (or Wilcoxon) differences against each baseline.
- Apply Holm correction over the pre-registered secondary set: FB vs BU (H2), FU vs XU (H3), Live (H5).
- Put the full grid in an appendix, labelled exploratory.
- Run the analysis script with `--exclude results/pilot_ids.txt` for every number in the paper.

### B3. Memorisation is not ruled out by the planned control (H5; run_conflict.py; data/swebench_live_post.jsonl)
Verified fixes date from 2013 to 2023. The post-fix version of every gold file sits on GitHub and is almost certainly in pretraining. Under F, "print the file after the fix" can be answered by **recalling the fixed version**, which produces a drop exactly at the gold lines. That is the trivial explanation for H1.

SWE-bench-Live does not cleanly separate memorisation from other causes:
(i) It covers 193 mostly less-popular repos, so file familiarity, style and length all shift together with "not memorised". If the signal disappears there, nobody can say why.
(ii) The margin between the reported cutoff (Jan 2025) and the earliest task (Mar 2025) is two months, and model cutoffs are soft.
(iii) 33/200 Live ids have no X control.

**Fix, cheapest first:**
(a) On saved data, at no cost: regress per-file AUROC on the file's mean U surprisal (a familiarity proxy) and on `created_at`, within Verified. If the signal lives only in low-perplexity (memorised) files, say so.
(b) Compare Verified and Live **within matched U-perplexity bins and file-length bins**, not as raw means.
(c) Direct memorisation probe, one cheap U pass per file: teacher-force the **post-fix** file under U and compare logP_U(post-fix hunk) with logP_U(pre-fix hunk). Being more likely post-fix without the issue is memorisation of the fix. Report H1 for instances with and without this signature.
(d) If time allows: mine post-2025-03 fixes from the **same 12 repos**. The clones are local, and Django commits are formatted "Fixed #NNNNN --". This gives a same-distribution post-cutoff set.
(e) For Live, draw the X issue from another repo when the same repo has no other issue, and say so in the paper.

### B4. E2: gold leaks into the shared context, and the score is length-confounded (run_patches.py:145-151, 160-168, 206)
The docstring claims the context does not reveal which candidate is right. It does: the units touched by the gold patch are always added to the context (lines 150-151), even when no chosen candidate touches them. Long units are cut to ±40-line windows centred partly on gold lines (164-165). Under I, a patch that edits the region the context is "about" becomes more likely, and resolved patches are the ones that edit that region.

Separately, the score is `sum` over all diff tokens (line 206). Longer diffs get larger |score|, and resolved and unresolved diffs differ systematically in length.

**Fix:**
- Build the context only from the chosen candidates (drop lines 150-151). Score gold only when its units are already covered, or give it its own run.
- Use the per-token mean of `sum_chg` (changed lines only) as the primary score.
- Report these as baselines in the same within-task AUROC table:
  - diff length (n_chg)
  - **n_subs**: a consensus or majority baseline, which is execution-free and probably strong
  - raw logP_C (naturalness)
  - lexical overlap between the added lines and the issue
  - similarity to gold, as an *explanatory* covariate (H6's falsifier): partial out normalised edit distance to gold, and "touches the gold function".
- E2 has no memorisation control, because Verified gold patches are public. State this as a limitation.

---

## MAJORS

### M1. Insertion anchors, blank lines, and unit-level inflation (common.py:120-124; analyze_conflict.py:144-152)
The parser is correct, but the labelling has three problems:
- **32% of gold lines are anchors, not edits.** A feature that peaks at structural boundaries (the `def` line after a block, the last line of a function) hits anchors without localising anything.
- **255 anchors are blank lines.** Gemma attaches `\n\n` to the previous line, so a blank line has ntok=0 and its label disappears silently (`gold_lines` keeps it, `valid` drops it). 4 files have *only* blank gold lines and are skipped by `y[valid].sum()==0` (line 149) without a log entry.
- **At function level, the two anchors of one insertion can sit in two units.** 73 anchor pairs straddle a unit boundary. 88 files gain an extra gold unit through anchors alone, usually the next, unrelated function. This inflates unit hit@k for every method, the baselines included.

**Fix:**
- Report three labelings: removed/modified only (`g.removed`, primary), insertion-only files (anchors), and the union.
- Move a blank anchor to the nearest non-blank line in the same direction.
- At unit level, assign an insertion to the unit containing `prev_src` (or to the enclosing scope of the inserted lines in the post-fix file), never to both neighbours.
- Log files dropped for having no valid gold lines.

**Token-boundary note (feature, not bug, but describe it):**
- The newline run that ends line i belongs to line i, and the indentation or first token of line i+1 belongs to line i+1.
- Uncertainty about "what comes next", which is where an insertion appears, is therefore split across the last token of the line above and the first token of the line below.
- That split is what justifies labelling both anchors.
- The paper should state that a line score includes its trailing-newline decision.
- Add a cheap ablation on saved data: recompute with the newline token and the first token of each line excluded. If the signal survives only on boundary tokens, the method finds insertion points rather than "conflicting code".

### M2. Copying and lexical overlap contaminate sign-agnostic features (analyze_conflict.py:67-74)
When the issue quotes a line or a traceback, B and F **raise** the likelihood of that line by copying, so drop_FU and drop_BU become strongly *negative* there (pilot: −16 nats on quoted lines). `abs_*` and `gain_*` therefore detect lexical copying, which is BM25 by another route. The X control does not cancel this, because X has different identifiers.

**Fix:**
- Keep signed drop features as the primary set. Mark `abs_`/`gain_` as lexical diagnostics.
- Report the primary AUROC stratified by BM25 tertile (or residualised on line BM25) and separately for gold lines quoted or not quoted in the issue.
- Make drop_FB (issue held constant, copying cancels) the H2 headline.
- Add the trivial baseline that a lexical reviewer will ask for: "line appears verbatim in the issue, or traceback cites `path:line`". It is free.

### M3. Entropy confound (analyze_conflict.py:67-72)
|Δ| grows with surprisal (token corr 0.49). High-entropy lines get large deltas of both signs under any prompt change. In the pilot, residualising cut drop_FU_max from 0.751 to 0.668.

**Fix:** Report the residualised version (B1c) as the claimed effect. Compare against `surp_F` and `surp_B` (issue-conditioned surprisal), which are already computed: if surp_B ≈ drop_FB, the "fix intent" story is unneeded.

### M4. The generative baseline is handicapped and has no evaluation code (run_generative.py:31-46, 55)
`parse` returns [] for common outputs: `1. 120-130: foo`, `1) 45-50`, `Lines 120-130`, `L120-L130`, `` `120`-`130` `` (all checked). Ranges are never turned into a ranking, and no script scores G, so the denominator and the parse-failure handling are undefined. Greedy decoding, thinking off and 160 tokens on a 4B model will be read as a strawman.

**Fix:**
- Make the parser accept an optional list marker and the `Lines`/`L` prefixes. Log the parse-failure rate.
- Count failures as misses over the same file set as E1, which needs the same >40k skip.
- Define the ranking: expand ranges in answer order, and within a range in line order. For unit level, map ranges to units in order, then dedupe. Also report the "any-hit within the top-5 ranges" metric, but penalise width: report mean range width, or line-level precision.
- Run thinking-on with about 1024 tokens on a 50-file subset, or state the restriction in the abstract.
- Report wall-clock for both methods: scoring runs 3-4 passes over the file, generation runs 1 prefill plus decode.

### M5. Oracle-file setting (analyze_conflict.py:119; run_conflict.py:81-82)
Only gold files are scored. Every number is "localisation within the file you already know was edited". A judge will ask whether drops also occur in files that need no edit.

**Fix:**
- Claim only within-file localisation, and frame it explicitly.
- If GPU time allows: run `--files cands` with U and F on the top-1 BM25 non-gold file for about 50 test instances. Report file-level AUROC of max(drop) and the distribution of top-line drop magnitudes, gold versus distractor files.

### M6. Aggregation and weighting (analyze_conflict.py:171-186, 194-199)
- AUROC and ranks are averaged **per file**, so 70/500 multi-file instances count 2 or more times.
- Django is 231/500 and dominates. Report per-instance (mean over files) and per-repo macro averages.
- Line 177 replaces invalid (blank) lines with **0.0** before the unit `max`/`top3`. For features that are mostly negative (any drop where F is generally *more* confident than U), blank lines win and create ties. Use `-np.inf` for max/top3 and 0 only for sum.
- The `random` baseline uses one draw per file. Report analytic chance: the hypergeometric hit@k given n_valid and n_gold, and AUROC 0.5.

### M7. E2 is not reproducible across resumes; the X issue in E1/E2 is not controlled (run_patches.py:123-140, 172-173; run_conflict.py:87-88)
In E2, ids already in `done` `continue` before the shared `rng` is consumed. After a crash and restart, every later instance gets a different candidate subsample and X issue. Seed per instance instead: `random.Random(int(md5(iid),16))`.

In E1 and E2, X is any same-repo issue. Its own gold patch may touch the same file, which is common in Django (one ticket per area) and contaminates the control. Its length also differs from F's issue, so prefix length differs.

**Fix:** Draw X from issues whose gold files are disjoint from the scored file, and closest in issue token length. For the already-running pilot, log the overlap and exclude affected files from the H3 analysis.

---

## MINORS

- **bf16 logits** (config: dtype bfloat16, final_logit_softcapping 30). The logit step is 0.125 for |logit| in [16, 30], which puts a per-token noise floor of about 0.1 nats on mid-probability tokens. It is unbiased for signed sums, but it adds length-proportional mass to `abs_`/`_pos` features (part of B1). A fp32 lm_head would remove it; otherwise mention it.
- **splitlines vs '\n'** (analyze_conflict.py:158, run_generative.py:82, common.py BM25 lines, against scorer.py:96-99). The two agree on Verified, but Live files containing `\f`, lone `\r` or ` ` would misalign BM25 and G line numbers. Use `target.split('\n')` everywhere, or assert equal lengths.
- **bm25_tokens** (analyze_conflict.py:25-33). Both the `_`-split and the camel-split add the same subtokens, so snake_case parts are counted twice. This is harmless but undocumented. Line-level BM25 computes IDF over the lines of one file; state it.
- **Skips** (run_conflict.py:100). The >40k-token skip (3.2%) and fetch failures must be reported, and all baselines evaluated on exactly the surviving set (true for analyze_conflict; ensure it for G).
- **Position** shows no material effect (AUROC 0.52; per-decile mean token drop between −0.065 and +0.025). Keep the position baseline anyway; it is free.
- **Forced assistant prefix** "```python\n" with thinking off. The off-distribution start is identical across frames, so it cancels in the deltas. Mention it.
- **E2 `chg` mask** (run_patches.py:202-205) assigns tokens by start offset. Fine, given Gemma's pure-newline tokens. Use `sum_chg`, not `sum`, because hunk-header line numbers and context copies add noise.
- **E2 selection**: requiring ≥1 resolved and ≥1 unresolved candidate, plus a context of ≤1200 lines, selects mid-difficulty, localised tasks. Report how many are excluded at each step.
- **E1 X on Verified**: in the pilot, both astropy instances drew the same X (astropy-14539). This is fine, but report the X ids.

## The 3 most damaging objections and the cheapest answer to each

1. **"Your localisation is line length plus surprisal."** (Pilot: ntok 0.69 beats every drop_*_sum.)
   Answer on saved data: run the permutation null, residualised AUROC and the ntok/surp baselines, with paired instance-bootstrap CIs (B1, M3). No GPU.
2. **"F just recalls the memorised fixed file; Live differs for unrelated reasons."**
   Answer on saved data: the familiarity regression and Live versus Verified within matched U-perplexity bins.
   Small GPU run: the post-fix-file U probe (B3c), which costs one pass over the edited hunks only.
3. **"It is BM25 or copying in disguise, and you picked the best of 140 features on 25 instances."**
   Answer: pre-register one signed feature now, report BM25-stratified and quoted/unquoted AUROC plus drop_FB, and apply Holm over the pre-registered set (B2, M2). No GPU.
