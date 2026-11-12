# Kaggle Writeup submission mechanics (researched 2026-11-11; READ-ONLY)

PAPER = https://www.kaggle.com/competitions/gemma-4-developer-agent-paper . Anything not tied to a source below is NOT VERIFIED. I could not open the logged-in Writeup editor, so UI details are second-hand.

## 1. Creating and submitting
Verified (PAPER/Submission Requirements page, via Kaggle MCP list_competition_pages):
- "To create a new Writeup, click on the 'New Writeup' button here. After you have saved your Writeup, you should see a 'Submit' button in the top right corner."
- Paper must contain: title and subtitle, abstract, introduction, research description (methods, experiments), related works and citations.
- "Any un-submitted or draft Writeups by the competition deadline will not be considered." Deadline 2026-11-12 23:59 UTC (Timeline page).
- A private Kaggle Notebook/Resource attached becomes public after the deadline.
- Must "join this competition" (Evaluation page); entry = accepting rules ("Entry is required to make a Submission", foundational rules 3.18.b). Rules say no multiple accounts. Each team member must register individually and confirm team membership.

Second-hand (a different Kaggle hackathon, same Writeup product): to submit, the Writeup needs a selected track, a title, a subtitle and a thumbnail image. Source: https://gist.github.com/bigsnarfdude/19be893b58c844cb43b2d30d07f31af0 (third party, NOT VERIFIED for this competition). Thumbnail size/aspect ratio: not specified anywhere I found -> NOT VERIFIED. Media gallery, attachments, exact mandatory-field list for this competition: NOT VERIFIED.

Edit / unsubmit:
- A submitted writeup can be edited via Edit -> "Update Submission" (user report, https://www.kaggle.com/competitions/gemma-4-developer-agent-paper/discussion/743094). On 2026-09-24 that failed with toast "Failed to check for writeup conflict" (CheckHackathonWriteupConflict returned 404); host asked on Sep 29 whether it was still affecting anyone, no confirmed fix statement. Treat as possible regression: test the save/submit flow EARLY.
- Form shows "You've already submitted to this competition. To submit this writeup, you'll first need to unsubmit your previous writeup." when submitting a second writeup (reported in https://www.kaggle.com/competitions/gemma-4-developer-agent-paper/discussion/753195). Host (Nov 9): "This should be fixed. I see multiple submissions from the same team"; a participant confirmed two writeups both "Submitted" on Nov 9. So unsubmit/resubmit exists; two writeups per team OK.
- Whether edit-without-unsubmit works, and whether resubmit resets the tie-break timestamp: NOT VERIFIED (unanswered in 753195).

## 2. Editor formatting
- Kaggle content is Markdown (source: same gist, "All Kaggle content is written in Markdown", third party). Tables, LaTeX ($...$), code blocks, image upload method (drag/drop vs URL), image size limits, editor length limits: NOT VERIFIED. Kaggle has no public docs page I could fetch (https://www.kaggle.com/docs/writeups returned 404).
- Staff on formatting (references style/appendix, topic 756499): no answer. Competition-level limit: 3,000 words (see competition.md).
- Safe approach: assume GitHub-flavored Markdown with tables may render poorly and LaTeX may not render; preview after save; use images (PNG) for key equations/tables as fallback; keep tables simple.

## 3. Project Links / PDF alternative
- Public Notebook goes in the Project Links field; must be public, no login/paywall (Submission Requirements).
- Public Project Link: "instead of writing your paper in the Kaggle Writeup, you can also upload an arXiv-ready (LaTeX/Word) PDF ... publicly accessible and not require a login or paywall." Staff (743255, per competition.md): same 3,000-word limit, PDF is judged as the writeup; write a short abstract in the Kaggle body. Host also said an arXiv link is OK as a submission (745872). GitHub links accepted for code (751804). Whether Project Links accept arbitrary URLs (GitHub/PDF) is implied but NOT VERIFIED in the UI. Title+subtitle still required by the form regardless.

## 4. API / CLI / MCP
- Kaggle MCP tools present: get_hackathon_overview, list_hackathon_tracks, list_competition_pages, list_competition_topics, get_forum_topic, list_topic_messages, get_hackathon_write_up, list_hackathon_write_ups, download_hackathon_write_ups, get_writeup, get_writeup_by_slug, get_writeup_by_topic, get_resolved_writeup_links. NO create/update/submit writeup tool exists (names list has none).
- Unauthenticated read worked for: pages, tracks, forum topics. get_writeup_by_slug returned "Permission 'writeUps.get' was denied". list_hackathon_write_ups was Unauthenticated earlier (competition.md).
- kaggle CLI 2.1.2 (latest 2.2.5): `kaggle competitions` = list, files, download, submit, submissions, leaderboard, episodes, replay, logs, pages, topics; `forums`, `kernels`, `datasets`, `models`, `benchmarks`. No writeup command. `competitions submit` is for prediction/code submissions, not writeups. Conclusion: writeup creation/submission is browser-only. (Token not loaded or used.)

## 5. Tracks/awards
- list_hackathon_tracks returns a single track "Total Prizes Available" (id 7317) with three prizes: Overall Best Paper $15k (highest average of five criteria), Best New Resource $10k (new dataset/tool/software vs empirical paper), Best New Application $10k (new use-case, e.g. code graphs for TPU kernels; new eval datasets for novel tasks; existing benchmarks not previously used with graphs/embeddings). Source: Kaggle MCP list_hackathon_tracks.
- So there is one track; no evidence of a per-prize selector at submission. Whether the form shows a track dropdown (single option) is NOT VERIFIED. Prize category is determined by judges (see competition.md: one writeup can be considered for several awards, wins only one).
- Judging: 5 criteria (Novelty, Quality, Relevance, Verifiability, Clarity) 0-5 averaged; top 3 papers by points (Evaluation page). Rubric not shared. Tie: entered first wins.
- Topics 743310 (host Sep 29): non-archival, parallel submission to arXiv/other venues allowed, only prize winners promised to be highlighted. 743094: see section 1. 749546 Word Count: see competition.md.

## 6. Checklist for the human (browser, ~60-90 min plus buffer)
1. (2 min) Logged in with the right account; confirm you have joined the PAPER competition (rules accepted); teammates registered and team confirmed.
2. (5 min) Prepare assets: title, subtitle, abstract, body Markdown (<= ~2,800 words incl. title, abstract, captions, tables; excl. references and figures), cover/thumbnail image (size not specified -> use 16:9, ~1280x720 PNG/JPG under a few MB; NOT VERIFIED), figures as PNG, GitHub/notebook URLs (public, no login).
3. (3 min) Open PAPER Overview page, click "New Writeup"; paste title, subtitle, body, pick the track/prize category if offered.
4. (10 min) Add thumbnail/card image, figures, Project Links (public notebook / GitHub; or PDF link if using PDF route), attach any Kaggle resource (becomes public after deadline).
5. (5 min) Save, preview rendering of tables, math, code, images; fix quirks.
6. (2 min) Click "Submit" (top right). Confirm status shows "Submitted" (not Draft) on the writeup page and in the competition's writeups list.
7. (5 min) Re-open in a private/incognito window or logged-out to confirm the public notebook/PDF/GitHub links load without login.
8. (optional) Edit via Update Submission; re-verify state is "Submitted" afterwards.
9. Do all of this well before 2026-11-12 23:59 UTC; aim for Nov 12 morning UTC at the latest, ideally today (Nov 11).

## Biggest risks
- Save/submit regression ("Failed to check for writeup conflict") reported Sep 24; no confirmed fix. Submit an early version now, then update.
- Unsubmit/resubmit may reset the timestamp (tie-break) and a draft at deadline is not judged; ensure "Submitted" state after the last edit.
- Markdown/LaTeX/table rendering and thumbnail size unknown; word-count enforcement unclear (no counter).
- Deadline confusion (one post says Nov 13; page says Nov 12 23:59 UTC).
