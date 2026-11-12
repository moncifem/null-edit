# Review of draft 2 — "The Null Edit" (hostile but fair; Opus critic, 2026-11-12)

Scope: PAPER.md as it stands, checked against `results_dgx/report_e4b_test.md`, `report_e4b_live.md`,
`report_e4b_q4_test.md`, `report_context_budget.md`, `extra_e4b_test.md`, EXPERIMENTS.md, HYPOTHESES.md and
`src/`. I recomputed the no-op subset numbers on the CPU from `results_dgx/an_e4b_test.json` and `an_e4b_live.json`.
I don't repeat Round-4 points that were fixed. Where a Round-4 fix did not fully land I say so (§7).

---

## 0. Blocking issues, in order

1. **§4.3 headline overclaims, and its title is contradicted by the paper's own data.** On the 84 "greedy no-op" files the
   *asked* model (line ranges) names the gold function first in **54.8%** of files, while H does so in 48.8% (report_e4b_test.md,
   "Files the model would leave unchanged"). On these files the model *does* say where when someone asks it. Only the
   rewrite channel stays silent. Second, the number used is H, which needs a second prompt (the wrong issue), so it is not a property
   of the rewrite policy. The rewrite policy's own quantity is S: 53.6% [42, 65]. Third, "would change nothing" holds only
   for greedy decoding with an assistant turn prefilled with ```` ```python\n ````. The paper never mentions that prefill. Under
   the model's own sampling distribution, the median P(no edit) on these files is **0.32**, so a sampled rewrite edits about 2
   times in 3. Details and replacement text are in §2.2.
2. **The abstract and contribution 2 still say "better than asking" with no qualifier.** At line top-1 the map and the
   pre-registered answer are tied (27 vs 23, Holm 0.70). At function top-1 asking wins (−9.3). At function top-3 they are tied.
   With a 5% reading budget they are tied. The map wins at line top-5 and top-10, at function top-5, and with ≥10% reading
   budgets. The abstract puts the reversal last, after quantization, and words it as "Asking *remains* better", although this
   is the first time the abstract mentions it. See §2.1.
3. **§4.7 says "the gap is weight precision, not software", but it leaves out a significant software effect.** At function top-1
   the same 4-bit weights score 39.6% (DGX) and 44.0% (MAC), −4.4 [−8.6, −1.1] (EXPERIMENTS.md, quantization table). The
   CI excludes zero. The abstract's "on either software stack" also implies a bf16 run on the MAC that does not exist. See §2.3.
4. **Two cells in Table 1 are stale or wrong** (§1). Small, but this paper sells itself on verifiability.
5. **There is a scoring bug in the queued edit experiment:** `adds_gold` credits replacement lines that were simply copied from SEARCH. The "BM25 placebo" is
   also not a placebo. See §3. Fix both before the run lands, not after.

---

## 1. Numeric audit (abstract, Table 1, §4.1–4.5, 4.7, 4.8)

Everything else I checked matches the reports to rounding: abstract numbers; §4.1; §4.2; §4.3; §4.4; §4.5, including
"89 of 91 repositories absent from Verified", which I verified from the rows (only matplotlib and pylint overlap); §4.7;
and §4.8.

| Where | Paper | Report | File |
|---|---|---|---|
| Table 1, BM25 line@5 | 30 | **31.0** | report_e4b_test.md (30.3 is the stale EXPERIMENTS.md E1b value) |
| Table 1, Length line@5 | 10 | **11.3** | report_e4b_test.md |
| Table 1, Length line@10 | 18 [14, 23] | **17.3 [13, 22]** | report_e4b_test.md (no file has 18) |
| §4.7 "first 88 issues, 98 files" | 88 issues | 98 files come from **83** instances | report_e4b_q4_test.md. Say "first 88 issues (83 with a scorable file, 98 files)" |
| §4.2 hybrid "inside the functions the answer named first" | unspecified | code uses the answer's **first three** units (`ranked_units[:3]`) | analyze_conflict.py:318 |
| §4.7 "reproduces the MAC numbers" | line-level only | function@1 differs: −4.4 [−8.6, −1.1] | EXPERIMENTS.md |
| §4.1 budget-matched "H 67% against 49%" | vs quoted | correct, but the budget is the *quoted* answer's line count. The pre-registered line-range answer at that budget is 50.3%, not reported | report.py:107–115 |

These are not errors, but they belong in the text:
- Issue-weighted function@1: line-range answer **64.7** vs H 54.7. With issue weighting, asking's lead grows to about 10 points. §4.1 reports
  only the issue-weighted line number (70 vs 33), which is the one favourable to the map. Report both, or neither.
- LIVE no-op subset: H 52.6 [43, 64], S 50.0, BM25 39.5, random 30.3. §4.3 should cite this replication, which is weaker but still
  above both baselines.

---

## 2. Claims that outrun the evidence

### 2.1 The line-range baseline (most scrutiny)

Quoted: *"puts a line of the human fix in its top ten for 69% of files, against 38% for BM25 and 51% when the same model is
asked to name the lines."* … *"Asking remains better at naming the single most likely function (60% vs 50%)."*

- The comparison is correct, but the order is not. The reversal is now a main result and should sit next to the headline,
  not after quantization. "Remains" is wrong: this is its first mention.
- The line@10 number for the answer depends on a reading convention: lines inside a range are inspected top to bottom
  (analyze_conflict.py:296–313). The answer contains a gold line *somewhere* in **62%** of files (rank ≤ n_lines; recomputed), but
  scores 51% at top-10. So about 11 points of the gap come from ranges being wide and read from the top. A sceptic will say the
  map wins at line@10 partly because a ten-line cut-off penalises a range answer. You already have the fair metric: the
  **reading-budget** table, where the answer gets windows of the same size. There the result is tied at 5% (64 vs 66), the map
  leads at 10% (80 vs 70), and the map leads widely at 20% (90 vs 72). Lead with that for the asking comparison, and keep line@10 for BM25.
- Contribution 2 (*"ranks human-edited lines better than BM25 and than the same model's generated answers"*) is false at
  line@1 against line ranges (n.s.).

**Is "the map finds the edit better than asking" still fair?** Only in this form: *after the first guess*. Replacement for
the abstract, sentences 4–5 plus the last sentence:

> On 300 held-out files of SWE-bench Verified, Gemma 4 E4B's per-line *edit hazard* — no fine-tuning, generation, tests or
> tools — puts a line of the human fix in its top ten for 69% of files, against 38% for BM25 and 51% when the same model is
> asked for line ranges. Asking is better at the first guess: it names the right function first in 60% of files, the map in
> 50%. The map is better at every guess after that, and an agent that reads 10% of a file in map order sees the fix in 80% of
> files (asking: 70%).

Replacement for contribution 2:

> 2. *A pre-registered evaluation* on 300 held-out SWE-bench Verified files with Gemma 4 E4B. The map beats BM25 at every
>    cut-off. Against the same model's generated answer it loses at the first function, ties at the first line, and wins from
>    the fifth line and the third function on.

### 2.2 §4.3 "The model knows where before it says so"

**Is the p ≥ 0.5 argument sound?** As arithmetic, yes. If every forced token has p ≥ 0.5, no other token can be the argmax, so
greedy decoding *from the same prefix* reproduces the file token for token. It has four holes a judge will find:

1. **Prefix.** `run_conflict.py:144` prefills the assistant turn with ```` ```python\n ````. The paper does not say this, in §2 or in §4.3.
   The model's free greedy reply might start with prose, a diff or a snippet, so "its greedy rewrite *is* the unchanged
   file" is shown only conditional on the prefill. Disclose it in §2. Better still, generate the first ~16 tokens with no prefill
   on the 84 files: seconds per file. That check would turn the claim from "conditional" into "observed".
2. **Greedy only.** Median P(no edit) = e^{−S} on the 84 files is **0.32** (LIVE: 0.38). A temperature-1 rewrite edits ~2/3
   of these files. The phrase "would not act on it" is about greedy decoding, not about the model.
3. **Margin.** 18 of the 84 files have min p in [0.5, 0.6), and 32 have it in [0.5, 0.7). With bf16 and KV-cached incremental decoding,
   some of these may flip. "In exactly these files" sounds sharper than the evidence is. Report the min-p distribution, or
   run the 16-token check above at the argmax margin.
4. **Two different prompts.** The generated answers come from different prompts (a numbered file and "which locations…"), not
   from the rewrite prompt. On the no-op files the asking prompt names the gold function first **54.8%** of the time, against the
   map's 48.8% (H − ask: −6.0 [−17.7, +4.8], recomputed). So the model *does* say where when asked. What the subset shows is
   narrower: **the rewrite channel would emit nothing, and its own probabilities still point at the fix.** That is still interesting,
   and it is exactly the speculative-editing point. But the title "knows where before it says so" is contradicted at
   function level by the paper's own row.

Also: H uses a second prompt with the wrong issue, so it is not a quantity of the rewrite policy. The clean statistic is S:
53.6% [42, 65]. Paired S − BM25 = +15.5 [+2.2, +29.4], p = 0.03. Paired S − line-range answer = +14.3 [+2.4, +25.6],
p = 0.03 (recomputed, post hoc subset, unadjusted). Also state that the subset was defined after the reviewer's suggestion,
so it is post hoc, and that it has 73 issues.

Replacement §4.3 (title and text):

> **4.3 Below the decoding threshold (*post hoc*).** With the response opened by ```` ```python ````, 84 of the 300 files have
> every original token at probability ≥ 0.5, so greedy decoding reproduces them verbatim. A whole-file rewriter, or a
> speculative editor that only sees where greedy decoding diverges, would change nothing. The one-pass map of the same
> forward pass still puts a gold line in its top ten for 54% of these files [42, 65] (H 64%), against 38% for BM25 and 39%
> for either generated answer. On LIVE the figure is 50% (BM25 39%). The location is present below the argmax. The model is
> not silent about it, though. Asked directly, it names the gold function first in 55% of these files. And under
> sampling it would edit two files in three (median P(no edit) = 0.32). What greedy rewriting discards, the probabilities keep.

Contribution 3 then becomes: *"A below-threshold finding: in files where greedy rewriting makes no change, the same forward
pass still localizes the fix."*

### 2.3 §4.7 quantization

- *"the gap is weight precision, not software"* → "at line level the gap is weight precision. At function top-1 a smaller
  software difference remains (−4.4 [−8.6, −1.1])."
- *"Four-bit weights cost the probe 12 points, on either software stack."* (abstract) → "The same 4-bit weights score 11–12
  points below bf16, whether run in MLX or in PyTorch." Strictly, there is no bf16 run in MLX, so write "4-bit weights score 12 points below
  bf16 in PyTorch, and MLX reproduces the 4-bit numbers."
- The comparison file set is easier than the full set: bf16 scores 75.5% on these 98 files and 69% overall. Say "on the first 98 files".
- Agent-relevant and missing: at 4 bits the map *loses its function-level advantage over BM25* (41.8 vs 42.9) but keeps the
  line-level advantage (+25.5). This is the practical message for laptop agents. It deserves a sentence in §6 or §4.8:
  "run the probe at bf16, or use it only for line ranking".
- A consequence the paper does not state: every design choice was made on an arm that is 12 points weaker. That is
  conservative and should be said, because it pre-empts the "tuned on test" objection.

### 2.4 Smaller over-statements

- §4.4 *"It is the issue, and the instruction."* The instruction half is the placeholder (RB/R0). Until it lands, the
  title claims more than the text shows. Retitle "It is the issue" or wait.
- §1, contribution 4 lists "all five Gemma 4 sizes" as done. It is a placeholder.
- Abstract *"It disappears under a wrong issue (16%)"*: random is 13%, so write "falls to near chance (16%; random 13%)".
- §4.5: the asking baseline was not run on LIVE (`genq_e4b_live` queued per REVIEW F4, absent from the report). The abstract's "(68% vs
  43%)" should name BM25 explicitly, and §4.5 should say asking was not run on LIVE. Without it, the post-cutoff check does not
  test whether the *asking* gap is a memorization effect.
- §4.1 *"with every issue weighted equally (70% vs 33%)"*: give the function@1 counterpart too (H 54.7, ask 64.7). See §1.
- §2 *"the exact distribution of where its rewrite would first depart"*: exact for ancestral sampling at temperature 1
  with no top-p or top-k, *given the prefilled fence*. Add those six words.

---

## 3. The queued map-guided edit experiment (run_edit.py, make_hints.py, analyze_edit.py)

**What it must show to earn its ~120 words.** The H-hint arm must beat both the no-hint arm and a *properly matched* placebo arm on
a pre-declared primary outcome. The gain must also exceed what pure deference to the hint would produce.

Holes, most serious first:

1. **`adds_gold` bug (leakage-like false positives).** `analyze_edit.py:117` intersects the gold *added* lines with
   *all* REPLACE lines, including lines copied unchanged from SEARCH. Any gold patch that re-indents code, for example by wrapping
   a block in an `if`, has added lines equal to original lines after `norm()`. An edit whose SEARCH merely contains those lines
   then scores adds_gold = 1 without changing anything relevant. Lines of ≥ 4 characters such as `else:`, `pass`, `return`
   and `return None` also match by accident. Fix: use only lines REPLACE introduces (difflib opcodes `insert`/`replace`, j-side).
   Exclude lines already present anywhere in the original file. Require ≥ 1 non-trivial token, for example ≥ 12 characters or an identifier.
2. **Deference confound.** The hint lists line *text*, and SEARCH must be copied from the file. A model that copies the first
   hinted line into SEARCH lands `on_gold` with probability equal to the hint's own top-1 or top-5 rate (H: 27% / 55%). Then
   "H > none on on_gold" only shows that the model follows instructions. The script already prints the map's own top-1 and top-5 on
   the same files. Make the comparison explicit and add (a) **share of edits that touch a hinted line**, per arm, and (b)
   on_gold **conditional on the hint containing / not containing a gold line**. The interesting results are: the H arm beats "the
   hint's top-1" (the model *selects* among hints), and the H arm does no harm when the hint is wrong.
3. **BM25 is not a placebo.** It carries real signal (38% at top-10) and different-looking lines (issue-word lines, often
   docstrings and comments). H − BM25 then confounds hint quality with hint style. Add **wrong-issue H top-5** (the RX pass
   already exists, so the cost is zero). Those lines look like hazard lines, hard to copy and same format, but carry no issue information. That is a true
   placebo. If one more arm is affordable, add an **oracle hint** (gold lines, padded to 5) as a ceiling. Without a ceiling, the reader
   cannot tell whether a small gain means a weak map or a model that ignores hints.
4. **Validity is mixed into the outcome.** An invalid SEARCH (not found) scores 0 on every outcome. Hints probably raise validity, because the
   model copies hint text verbatim. Report `valid` per arm, and report on_gold both unconditionally and conditional on valid.
5. **Ambiguous SEARCH.** `locate` takes the first occurrence (`hits[0]`). Real apply tools reject ambiguous blocks. Count
   multi-occurrence SEARCH as invalid, or report the rate. Otherwise a short SEARCH like `return x` can land anywhere.
6. **Truncation.** 256 tokens with a stop on `>>>>>>> REPLACE`. A truncated reply with no `=======` is a parse failure, and one
   with `=======` but no end marker is a truncated REPLACE. Report the truncation rate per arm, since hint arms have longer prompts but
   the same cap.
7. **Multiplicity and primary outcome.** The analysis prints 6 outcomes × 3 contrasts, uncorrected. Declare one primary
   (I suggest `on_gold`, H − wrong-issue-H) in HYPOTHESES.md **before** the run finishes, and Holm-correct the rest.
8. **Scope statements needed in the text:** oracle file, one greedy sample, one edit for multi-hunk patches (on_gold needs only one
   gold line), and no execution. "Touches a gold line" ≠ "fixes the bug".
9. **Subset choice.** `make_hints.py --limit 100` takes the first 100 test ids. Those overlap the 88 issues of the MAC interim look.
   That is harmless for this experiment, but say which issues were used.
10. Minor: the hint shows `line N:` numbers but the file in the prompt is not numbered, so numbers can't be used. Either number
    the file in all arms or drop the numbers. As it is, the hint format contains a cue the model cannot act on.

The most interesting secondary analysis, and cheap: the **84 greedy-no-op files**. Does the hint turn a no-op into an
on-gold edit? That ties §4.3 to the agent story in one sentence.

### Placeholders: what each must show, and what to cut

The body is ~2,500 words without tables (≈ 2,740 with tables). The placeholders will add 300–450, so there is no room for all of them.

| Placeholder | Worth its words only if it shows… | Keep / cut |
|---|---|---|
| §4.6 five sizes | H/S **and the asking baseline** at each size on common files. The question that matters is whether asking catches up with size. `scaling.py` prints "–" when a size has no `gen` run, and I see generation queued for E2B/12B only. If 26B/31B lack the asking column, the table cannot answer the obvious question. | **Keep** (table + 2 sentences) |
| RB / R0 | That RB (right issue, copy instruction) is near the wrong-issue level. If RB ≈ R, the "conditioned on an instruction to fix it" distinction in §5 collapses, and the novelty claim has to shrink. Report the paired S − S_RB. | **Keep**, one sentence (it is pre-registered N2) |
| Map-guided edit | See above: beats a matched placebo, beyond deference. | **Keep**. The best relevance lever |
| File ranking | Beats BM25 and "path named in issue" with hard negatives. It mainly answers the oracle-file limitation. | Cut to one sentence, or move to the appendix/repository |
| Fixed-point patch check | Exploratory and confounded with similarity to gold (Round 4 F9). | **Cut first** |
| §4.9 negative result | It is a dev-set result on 16 files from the MAC arm. | Fold into one clause of §2 or §6 if space is short |

---

## 4. Relevance to developer agents

As it stands, relevance is carried by one post hoc paragraph (§4.8), and two of its three parts are placeholders. A judge
scoring "developer agents built on Gemma 4" will see a localization metric paper.

**The single change that raises it most:** make §4.8 the agent recipe and quantify it, using only CPU work on saved data. You
already have every ingredient:

- *Recipe:* ask the model for functions (one short generation), then read map-ranked ±5-line windows inside them, then map
  order elsewhere. This is the exploratory hybrid (line top-1 33%, the best number in the paper) put into the reading-budget
  table. `context_budget.py` needs a "hybrid" ordering of about 10 lines. Report "fix in view at 5% / 10% of the file". If the hybrid wins at 5%,
  where asking and the map currently tie, you have a concrete recommendation: "ask, then read by hazard".
- *Cost line:* two forward passes ≈ 9.5 s per 6.7k-token file on the DGX. One short answer ≈ 13.5 s in your loop and is cheaper in MLX.
  Tokens read by the agent at a 10% budget: about 650 lines → about 60 lines.
- *Laptop advice from §4.7:* at 4 bits, use the map for line ranking, not function picking.

If the map-guided edit lands with the fixes in §3, it becomes the headline of §4.8. "With the map as a hint, the same model's
single edit lands on a gold line in X% of files vs Y% without, Z% with a placebo" is the closest thing to an agent outcome
available today. Also reframe §1's first paragraph from "what can a model tell us if it never writes" to "a free tool call
for small-model agents: where to read, and where to edit". That framing makes the title earn its keep.

---

## 5. Clarity

**Jargon before definition**
- "the map" is used as a noun from the abstract on and never defined. Abstract: "the resulting per-line *edit hazard* (the
  'map')".
- "teacher forcing" is not explained for non-ML readers. In §1 add: "(score a given answer instead of sampling one)".
- "greedy rewrite", "argmax", "nats", "Holm", "hit@k". hit@k is defined in §3, but "top ten" is used before that, which is fine. "Nats"
  in §4.4 needs "(natural-log units)" or should go.
- "sub-threshold" (contribution 3) is undefined. Replace it with the wording in §2.2.
- "MAC/DGX arm" is used in §4.9 before it is clear that the arms differ in more than the machine.
- "RB/R0" only appears in placeholders, but §3 "Controls" gives no symbols, so the placeholder text will need to define them.

**Sentences a first-time reader will not parse**
- *"the total appetite for editing rises from 1.4 to 5.0 nats"* → "the file's total hazard S (−log P(no edit)) rises from 1.4
  to 5.0 nats: the probability of copying the file unchanged falls from 25% to under 1%." The median-file arithmetic is
  e^{−1.4} = 0.25 and e^{−5.0} = 0.007.
- *"Lines that the wrong issue makes harder (the mirror image of H) score below random (8%)."* → "Ranking lines by the
  opposite difference, the lines the *wrong* issue makes harder to copy, finds the fix in 8% of files, below random (13%)."
- *"(paired differences to H: +31.0 …)"* → "H leads by 31.0 [21, 40], 18.0 [12, 24] and 24.3 [19, 30] points".
- Abstract *"Four-bit weights cost the probe 12 points, on either software stack."* See §2.3.
- §4.7 uses three file sets (91, 98 and "the common files") in five sentences.

**Weakest paragraph: §4.7.** Replacement (≈ 95 words):

> **4.7 Quantization blunts the probe.** The laptop arm's community 4-bit weights, de-quantized into the DGX code, reproduce
> the laptop's line-level numbers (H top-ten 63.7% vs 64.8% on 91 shared files; −1.1 [−3.5, 0.0]) and score 12.2 points
> [5.0, 20.2] below bf16 on the same 98 files (63.3% vs 75.5%). The loss is in the weights, not the software, except for a
> smaller stack difference at function top-1 (−4.4 [−8.6, −1.1]). At 4 bits the map still beats BM25 on lines (+25.5 [14, 36])
> but not on functions (42% vs 43%). On a laptop, use it to rank lines. Every design choice was made on this weaker arm.

**Subtitle.** The current "Reading where a small model wants to change code, without letting it write" is decent but passive,
and it hides Gemma 4. Options:
- *"Gemma 4 shows where it would edit a file in one forward pass — even when it would not edit it"*
- *"Where a small model would edit, read from one forward pass"*
- *"A free localization signal for Gemma 4 coding agents"* (best for the Relevance score)

---

## 6. Scores as the draft stands (0–5)

| Criterion | Score | Why |
|---|---|---|
| Novelty | 3 | The identity is elementary and the pass is speculative decoding's. The new parts are the use and the below-argmax observation, which is currently over-framed. RB/R0 decides whether "instruction-conditioned" is real. |
| Quality | 3 | Pre-registration, clustered CIs, Holm, wrong-issue/mirror/length controls, LIVE and the de-quantization check are strong. Docked for the edits made in the last hour (§4.3, §4.7, abstract), stale table cells, and an asking comparison partly driven by a reading convention. |
| Relevance | 2 | No agent outcome yet, and §4.8 is post hoc and two-thirds placeholder. |
| Verifiability | 4 | Per-token logs, scripts and reports make everything recomputable. I recomputed several numbers. Docked for stale cells and REVIEW.md inconsistencies (§7). |
| Clarity | 3 | Dense, with jargon before definition. §4.7 and §4.4 are hard to read. Section titles claim more than their text shows. |

Average 3.0.

**Three changes that would raise the average most**
1. **Rewrite §4.3, the abstract and contribution 2/3 as in §2.1–2.2.** Lead with S, say greedy and prefill, keep the function-level
   asking number, and put the first-guess reversal next to the headline. Run the 16-token no-prefill check on the 84 files if any GPU
   minute is free. (Quality +1, Clarity +0.5. It also removes the most likely judge objection.)
2. **Give §4.8 a measured agent recipe:** hybrid reading budget (CPU only), cost line and 4-bit advice. Then the map-guided edit with the
   §3 fixes: diff-only `adds_gold`, a wrong-issue-H placebo, deference metrics and a pre-declared primary outcome. (Relevance +1 to +2.)
3. **Make the size table include the asking baseline at every size, and cut the patch check and file ranking to make room.** Whether
   asking catches up with size is the question a judge will ask after reading §4.2. (Novelty/Quality +0.5. Word budget stays under 3,000.)

---

## 7. Round-4 fixes that did not fully land

- **REVIEW.md F7** says "Function hit@1 H−BM25 survives Holm at 0.044". The current report gives Holm **0.111** for that test,
  and 0.044 now belongs to function hit@3. The paper is right and REVIEW.md is stale. Since REVIEW.md ships, fix it.
- **REVIEW.md F1** says the unit definition was corrected "in paper and docstring". EXPERIMENTS.md line 25 still says
  "leaf-most `def` spans".
- **REVIEW.md F11** says the position and mirror rows were added. They are in the report, but Table 1 shows neither. The mirror number is
  cited in §4.4, which is fine.
- **F13** "Subtitle to be revised at freeze": not yet done.
- EXPERIMENTS.md still says the quoted and H answers are "complementary" (F3 deleted this from the paper only). That is acceptable in a log,
  but mark it as superseded.
- Minor reproducibility point: `analyze_conflict.py` uses one shared `rng` for random tie-breaking and for the random baseline. Adding
  features shifts the random stream, which is why the random row differs between EXPERIMENTS.md (12.0) and the report (12.7). Use
  per-feature seeds so released numbers are stable.
