READY

# parcel-w6metrics report - final metrics refresh through Wave 6 close

Branch `wave6-metrics` (worktree `worktrees/w6-metrics`, base
`cdc40ae`), never pushed/merged. Owned files only:
`docs/metrics/{usage,passes,escalations,briefs}.jsonl`, append-only
(`git diff --stat` at the fold: 3 files changed, 77 insertions,
0 deletions; escalations byte-unchanged). Ledger:
`ledger/parcel-w6metrics.md`. All runs are script files in
`scratch/parcel-w6metrics/` under Git Bash with `MSF_PYTHON` pinned
to the workspace `.venv`, TMP in scratch, `ulimit -v` ceiling in
the runner. Session logs were read for counting and role labels
only; nothing with `cft` in its name was opened, searched, or
listed; `docs/metrics/plants.jsonl` was not opened (kit runs were
made on scratch combined copies holding only the four owned
files, so no plants/corrections input was read at all).

## Rows before/after and spans

| file | before | appended | after | span after |
|---|---|---|---|---|
| usage.jsonl | 93 | 35 | 128 | passes 2026-10-26T09:24:41-07:00 .. 2026-10-30T15:43:55-07:00 (was ..2026-10-29T11:36:52-07:00) |
| passes.jsonl | 94 | 37 | 131 | same |
| escalations.jsonl | 20 | 0 | 20 | sent ..2026-10-28T07:51:02-07:00 (unchanged; none sourceable, below) |
| briefs.jsonl | 39 | 5 | 44 | wave1..wave6 (own row last) |

Frozen-prefix proof (`append_rows.py`, one append-mode handle per
file): prefixes byte-identical after appending (prefix sha256
usage `8041187465af8a18`, passes `bafaf2d41f280bcc`, escalations
`9213f63174d82613`, briefs `7ff1f2919a48a02e`); final files equal
the pre-validated combined copies byte for byte (file sha256
usage `0c544361055cb4a3`, passes `2c4b39eb301a339a`, briefs
`d8ea1cf9c37da2e0`, escalations unchanged).

45 previously unrowed work sessions fold to 35 agents (35 usage
rows, 37 passes): appended in=220,313,353, out=1,623,075,
cached=213,503,365, messages=2,344.

## Expected vs found coverage (list built first)

Expected agents were enumerated from `ledger/briefs/` + git log
(2026-10-29T11:39:55..2026-10-30T16:08:00, all branches) +
per-agent ledger files BEFORE the extractor ran; `fold.py`
asserts every expected agent has exactly its expected session
count and every new extractor session maps exactly once
(45 sessions, 35 agents, 0 unmapped, 0 missing).

| expected (records) | sessions found | rowed as |
|---|---|---|
| parcel-w5metrics, verifier-w5metrics, parcel-w5readme3, verifier-w5readme3, auditor-adherence-final | 5 | wave5, 5 usage + 5 passes |
| study-video-intro-outro, -gitvisual, -intro-polish, -gitvisual-polish, -why, -gitvisual-v3, -why-v2, -gitvisual-v4 | 8 | polish, surveyors |
| study-video-textpacing (brief: two parallel agents) | 2 | polish, one folded pass |
| Spark stale-info audit (lead.md: 5 slices + critic + synthesis; no agent name in records) | 7 | polish, `auditor-staleinfo-spark`, one folded pass |
| verifier-polish1 | 1 | polish verifier |
| lead-polish1 (parcel-polish1) | 0 child sessions | not rowed: lead-authored in the main session (frozen lead idiom); quantified in lead continuation below |
| parcel-w6augint, verifier-w6augint, study-w6sanitize | 3 | wave6 |
| parcel-w6ci (tip + lead send-back revision) | 2 | wave6 author passes 1+2 |
| verifier-w6ci | 1 | wave6 verifier, sent_back (caf00b0) |
| parcel-w6examples, verifier-w6examples | 2 | wave6 |
| parcel-w6sanitize (tip + lead send-back revision) | 2 | wave6 author passes 1+2 |
| verifier-w6sanitize | 1 | wave6 verifier |
| parcel-w6judgemap, verifier-w6judgemap | 2 | wave6 |
| study-video-gitvisual-v6 (draft + r2 revision, same scratch) | 2 | wave6, one folded pass |
| study-video-gitvisual-v7 | 1 | wave6 surveyor |
| parcel-w6filmretime, verifier-w6filmretime | 2 | wave6 |
| surveyor-epidemiclicense | 1 | wave6 surveyor |
| parcel-w6popups, fixer-w6popups, verifier-w6popups | 3 | wave6 author + fixer + verifier |
| parcel-w6captions, parcel-w6metrics (own) | sessions start after the cutoff | excluded mechanically by `--until`; not reconstructed |

No session in the span is pruned or invisible: every frozen
session file (101 extractor sessions at the w5 run) is still on
disk, and every ledger/brief-named child agent above has session
files.

## Method (usage/passes)

One run of the sanctioned `tools/extract_session_metrics.py`
(selftest 8 checks, 0 failed) over the single lead session dir
`…/sessions/2026/10/26/01a17907-…` with
`--until 2026-10-30T16:08:00-07:00` (committer time of base
cdc40ae; latest in-scope child ends 15:43:55, so only the live
lead file is truncated and the two seal-parcel sessions starting
after the base are excluded mechanically). Output 146 work
sessions (146 internal reminder sessions excluded by the tool).
Its refusals were satisfied from records only, with the same
annotation set as the w5 run: `--author-commit lead=dfc7a02…`
and seven `--verdict` values copied from the frozen passes rows
for the natively labelled frozen verifiers. The lead row was
then dropped in the fold (frozen wave0 lead row already rows
the lead; re-rowing would double count).

Recount checks (`check_recount.py`): the new extractor output
agrees with the w5 run's `extract-out` on all 100 frozen child
sessions to the token/message/tool-use/start/end (only the lead
differs, by its later cutoff, as constructed); an independent
streaming inventory (`inventory.py`, same counting rules) agrees
with the extractor on all 45 new sessions (0 diffs). Fold
tie-out: appended usage rows equal the inventory's new-session
bucket exactly (220,313,353 in / 1,623,075 out / 2,344 msgs).

The fold (`fold.py`) restates session-id labels to agent names
from dispatched role labels ("You are X") + brief/scratch/worktree
path labels in early records + ledger attribution (the frozen
fold idiom). Wave labels follow the wave of the work in the
records: Wave 5 close agents `wave5`; the post-close film-study
and cleanup round of 2026-10-29 (before the Wave 6 queue opened
that evening) `polish` - the label the frozen briefs row for
lead-polish1 already carries; everything dispatched under the
Wave 6 queue and item-5 sealing `wave6`, including the 10/30
film v6/v7 studies that fed the wave6 film parcels.

Multi-session dispatches: usage sums per agent+model (the kit
sums per agent). Sessions that produced no separate tip/report
fold to one reporting pass: study-video-textpacing (two parallel
agents under one brief), auditor-staleinfo-spark (5 slices +
critic + synthesis under one lead dispatch; the name is this
fold's restatement from the lead.md heading "Spark stale-info
polish audit" - no record carries an agent name for it),
study-video-gitvisual-v6 (draft + r2 revision, same agent/scratch
per lead.md). parcel-w6ci and parcel-w6sanitize keep two author
passes: each session reported its own tip and the second is a
lead send-back revision after a red CI run (lead.md), so pass 1 /
pass 2 carry their own commits (cf. twiddledoc's two passes in
the w5 fold; parcel-w5aug's attempts produced one tip and folded
to one pass).

## Totals reconciliation (brief item 2)

Billed = input + output over `usage.jsonl`.

- Prior authority: 1,196,128,770 billed. This is exactly the
  frozen `usage.jsonl` total re-derived here (in 1,190,490,305 +
  out 5,638,465), i.e. the figure the film's outro card carries
  as of its freeze. It is NOT re-derived from the tokens study's
  span (that study counted the whole tree including lead main;
  the w5 report's bridge stands).
- Appended span (45 sessions, 2026-10-29T11:51:01..
  2026-10-30T15:43:55, cutoff 16:08:00): in +220,313,353,
  out +1,623,075, billed +221,936,428, cached +213,503,365,
  messages +2,344.
- Refreshed totals at the Wave 6 close cutoff: **in
  1,410,803,658, out 7,261,540, billed 1,418,065,198, cached
  1,379,156,504, messages 10,100.**

The whole difference against the prior authority is span: the
frozen rows end 2026-10-29T11:36:52 and every appended session
starts after that; per-agent amounts are in
`tables-{wave5,polish,wave6}.md` and `new-usage.jsonl`. Nothing
else differs - the recount checks above reproduce the frozen
sessions exactly under the same counting contract. The film is
not changed (its outro figure remains the frozen authority, per
the brief); these docs supersede it.

Not rowed, by design (quantified so the gap is visible): lead
main after the frozen wave0 cut (in=495,572,730, out=1,287,904,
msgs=1,960 to the cutoff - includes the lead-polish1 author
work, lead gate fixes and film integrations; the frozen idiom
rows the lead once); 146 internal reminder-observer sessions
(in=13,560,774, out=235,121, msgs=145, unchanged since the w5
cut); the two seal-parcel sessions that start after the cutoff
(this parcel's and parcel-w6captions', 0 records at the cutoff).

## Annotation sources (never invented)

- Author/fixer commits (11 passes): the tip each parcel
  reported in its ledger/report, verified in git and asserted
  ancestors of cdc40ae by `fold.py`: w5metrics 3f29682 (merge
  a1a888f 2nd parent), w5readme3 498a916 (merge 5a387e5 2nd),
  w6augint 5ce5ac5 (branch tip 93886a8 is a later lead gate fix),
  w6ci eda5812 + revision 5b53bf3 (branch tip caf00b0 is a later
  lead fix), w6examples b6e08fd (merge b85e037 2nd), w6sanitize
  1bc0979 + revision 77e6e64 (merge 4486cb5 2nd), w6judgemap
  245a4f5 (branch tip e1b0b46 is a later lead fix), w6filmretime
  1cfed36 (merge 3dfa3d8 2nd), w6popups 0708e2e, fixer-w6popups
  ef0215b (merge f36e171 2nd).
- Verdicts/a/b (10 verifier passes): every report is NOT READY
  on its planted copy as constructed. a/b follow the kit
  untagged rule stated by verifier-w5metrics ((a) = regression
  vs the in-copy record, (b) = wrong answer), applied per
  finding with the w5 fold's precedents (wrong vector/constant
  = (b); build break and gate-hole = (a); link = (c->a)):
  w5metrics (7,1) [F2 token count the (b); F1,F3-F8 vs record],
  w5readme3 (7,1) [F5 sample vector the (b)], polish1 (4,0),
  w6augint (4,1) [F1 426 decided-wrong the (b)], w6ci (4,3)
  [(b)=F2 smoke-for-standard behaviour swap, F6/F7 wrong
  tag/control output], w6examples (2,2) [(b)=F1/F2 wrong
  constants], w6sanitize (5,0) [report verdict REJECT mapped to
  kit NOT READY], w6judgemap (4,1) [(b)=wrong expected-interval
  nibble], w6filmretime (4,1) [(b)=blocker 3 wrong gate rank;
  3 blockers + 2 notes counted as the report enumerates them],
  w6popups (6,0) [code vs in-copy mp4/ledger/row record].
  Verdict vocabulary mapped where the kit enum requires:
  REJECT -> NOT READY, "NOT merge-ready" -> NOT READY (cf.
  PASS->READY / FAIL->NOT READY in the w5 fold). Per-agent
  source strings are printed by `fold.py` (`fold.log`).
- sent_back: true only where git shows the work revised after
  the verdict on the branch that merged - verifier-polish1
  (8751b11 verifier-observation fix + 227f69f byte restore after
  the 20:30 verdict, merged f7660f6) and verifier-w6ci
  (caf00b0 "verifier F3" lead fix at 05:41 after the 05:38
  session end, merged 6675fec). Every other verifier's parcel
  tip predates its session and merged at that tip; lead gate
  fixes that landed BEFORE verifier dispatch (93886a8, e1b0b46)
  do not count.

## Escalations: none appended (searched, none sourceable)

Searched: `ledger/urgent/` (no file written after 2026-10-27;
the alg1/alg2 wave5 rows came from ledger stamps, already
rowed); `escalat|urgent` across all Wave 6 and Wave-5-close
parcel/verifier/study ledgers (hits are only metrics-file
references and the popups escalation-count derivation); the
Wave 6 briefs themselves (none carries a test-escalation-at
-dispatch requirement, unlike Waves 1-4). The span's three
lead->parcel send-backs (w6ci, w6sanitize revisions; w6popups
fixer) are not parcel->lead escalations in the
`escalations.jsonl` sense and carry no sent/answered stamp pair
for that direction; they are rowed where the records support
them - author pass 2 / fixer pass in `passes.jsonl`. Inventing
stamps for them would violate the brief, so escalations stays
at 20 rows, byte-unchanged.

## Briefs: appended 5, named gaps below

Appended (base + time box both in the brief/ledger; every base
asserted resolvable in git): auditor-adherence-final (wave5,
bc807e6 freeze in its ledger, 360), study-w6sanitize (50aac59
named in its brief, 240), study-video-gitvisual-v6 (main
97e10a4 named in its brief, 480), fixer-w6popups (parcel tip
0708e2e named in its brief, 120), parcel-w6metrics last
(cdc40ae, 480, own brief footer). All seven Wave 6 parcel rows
and the polish row were already appended by their own parcels
and check out (bases resolve; no `fatal` echoes in kit tables).

## Not reconstructed (no source, never guessed)

- briefs.jsonl rows for study-video-intro-outro,
  study-video-gitvisual, study-video-intro-polish,
  study-video-gitvisual-polish, study-video-why,
  study-video-gitvisual-v3, study-video-why-v2,
  study-video-gitvisual-v4, study-video-textpacing: none of
  these briefs states a time box or a base commit (`base` and
  `time_box_min` are required fields). study-video-gitvisual-v7:
  brief base is its own scratch renderer, no commit.
  surveyor-epidemiclicense: web study, no base commit anywhere
  in brief/ledger. auditor-staleinfo-spark: no brief file, no
  time box (lead dispatch recorded only in lead.md). Their
  usage/passes rows DID land; only the briefs rows are missing
  (same constraint as the w5 sf2 studies, which remain missing
  for the same reason).
- briefs row for parcel-w6captions: its brief is fully
  sourceable (cdc40ae, 300) but the parcel was dispatched in
  parallel at this same base and appends its own row at its tip
  per the standing idiom; adding it here would double the row.
  Its session is likewise after this cutoff and unrowed.
- A passes row for lead-polish1: lead-authored inside the main
  lead session; there is no child transcript to count and the
  frozen idiom rows the lead once (wave0). Its tokens sit in
  the quantified lead continuation above.
- This parcel's own usage/pass rows: live after the cutoff;
  only its briefs row lands (w5 precedent).

## Frozen-row errors found (reported, not edited)

1. briefs.jsonl row 32 (`lead-polish1`) carries
   `time_box_min: 240`, but no time box appears in its brief
   (`ledger/briefs/polish-stale1.md`, 31 lines, read in full)
   or in `ledger/parcel-polish1.md` (searched for `240` and
   any minutes figure: none). The row was appended by the
   polish parcel itself; the freeze stands.
2. Carry-overs from the w5 report, re-confirmed verbatim on
   the frozen files: passes `sent_back: true` on the five
   waves 1-3 planted-copy parcel verifiers; recount-probe's
   rows undercount their own cited transcript; briefs rows 1-2
   `ceiling_text` cite `w1-ff64.md:29` / `w1-ff32.md:29` for
   files named `w1-f64.md` / `w1-f32.md`.
3. Explicitly NOT frozen-row errors: verifier-w5metrics
   findings F1-F4 describe its planted copy `091c890` only.
   On the frozen files re-checked here, verifier-w5exp2's
   usage row carries model `muse-spark-1.3`,
   verifier-extractor's carries `output_tokens` 34,350, the
   exp2 briefs base is `4a80126…`, and verifier-w5aug
   `sent_back` is false - all as the transcripts/records say.

## Gates run (observed output)

- `extract_session_metrics.py --selftest`: 8 checks, 0 failed.
- Extractor full run: 146 work sessions, exit 0
  (`extract.log`).
- Recount checks: frozen child sessions exact vs the w5
  extractor output; inventory vs extractor on the 45 new
  sessions: 0 diffs (`recount.txt`).
- Fold asserts: 45 sessions / 35 agents, every author commit
  an ancestor of cdc40ae, every new+frozen briefs base
  resolvable (`fold.log`).
- Kit `round_metrics.py --selftest`: 43 checks, 0 failed.
  Tables on the combined copies (all waves, wave5, polish,
  wave6, `--repo` the worktree): all exit 0, no `fatal`
  echoes (`kit.log`, `tables-*.md`).
- Append: frozen prefixes byte-identical; worktree files equal
  the pre-validated combined copies (`append.log`).
- `tools/run.sh standard` in the worktree: `budget standard:
  PASS in 945s`, exit 0 (`standard.log`; slow wall time is this
  sandbox shell's, totals 411,213 + 1,117,504, all controls
  refused).
- Diff vs base limited to owned files: 3 files, +77/-0
  (escalations untouched).
- Load: single-job streaming inventories/extractor (201 MB lead
  log read by the extractor under the runner's ulimit ceiling)
  and one gate run at a time; nothing heavy beside anything
  else.

Not done, named: the not-reconstructed briefs rows and
lead-polish1 pass above; `corrections.jsonl` remains frozen
(outside this parcel's owned files); RECORD.md gets no token
backfill from this parcel (the lead's fold); the film keeps its
frozen 1,196,128,770 outro figure per the brief.
