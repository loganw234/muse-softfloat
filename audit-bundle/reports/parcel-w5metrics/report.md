READY

# parcel-w5metrics report - metrics refresh through SF-2 close

Branch `wave5-metrics` (worktree `worktrees/w5-metrics`, base
`5142594`), one commit, never pushed/merged. `git diff --stat`:
4 files changed, 119 insertions, 0 deletions (owned files only).
Ledger: `ledger/parcel-w5metrics.md` (design entry first, results
entry last). All runs are script files in `scratch/parcel-w5metrics/`
under Git Bash with `MSF_PYTHON` pinned to the workspace `.venv`,
TMP in scratch, `ulimit -v` ceiling in the runner. Session logs were
read for counting and role labels only; nothing with `cft` in its
name was opened, searched, or listed.

## Rows before/after and spans

| file | before | appended | after | span after |
|---|---|---|---|---|
| usage.jsonl | 39 | 54 | 93 | passes 2026-10-26T09:24:41-07:00 .. 2026-10-29T11:36:52-07:00 (was ..2026-10-27T11:16:42-07:00) |
| passes.jsonl | 39 | 55 | 94 | same |
| escalations.jsonl | 13 | 7 | 20 | sent ..2026-10-28T07:51:02-07:00 (was ..2026-10-27T08:45:48-07:00) |
| briefs.jsonl | 27 | 3 | 30 | wave1..wave5 (own row last) |

Append-only proof (`append_rows.py`): frozen prefixes byte-identical
after appending (prefix sha256 usage `11463ad2…`, passes `d96ea499…`,
escalations `baed1144…`, briefs `6854b096…`); final file sha256 match
the pre-validated combined copies byte for byte.

New usage rows cover 62 previously unrowed work sessions folded to
54 agents: in=711,281,962, out=3,574,759, cached=697,108,722,
messages=4,866. Combined usage.jsonl totals: in=1,190,490,305,
out=5,638,465, msgs=7,756 (lead rowed once, frozen wave0 cut - see
"Not rowed, by design").

## Method (usage/passes)

One run of the sanctioned `tools/extract_session_metrics.py`
(selftest 8 checks, 0 failed) over the single lead session dir
`…/sessions/2026/10/26/01a17907-…` with
`--until 2026-10-29T11:39:55-07:00` (committer time of base
5142594; latest in-scope child ends 11:36:52, so only the live lead
file is truncated and this parcel's own session, starting 11:51:01,
is excluded mechanically). Its refusals were satisfied from records
only: `--author-commit lead=dfc7a02…` and seven `--verdict` values
copied from the frozen passes rows for the natively labelled frozen
verifiers in the same subtree. Output 101 work sessions (146 internal
reminder sessions excluded by the tool). The lead rows were then
dropped in the fold (frozen wave0 lead row already rows the lead;
re-rowing to the later cutoff would double count).

Recount check (`check_recount.py`): 37 of 38 frozen child sessions
recount exactly (tokens/messages/tool uses/start/end); the lead row
differs by its earlier cutoff as constructed; recount-probe differs
(see frozen-row errors). No frozen session is pruned: all 39 session
files are on disk, including the three the tokens study called
missing.

The fold (`fold.py`, asserts every new session maps exactly once)
restates extractor session-id labels to agent names from dispatched
role labels + brief/ledger attribution (the frozen lead-fold idiom;
one extractor foible handled: its deep search labels the
verifier-extractor session `verifier-wave0` because its brief quotes
Wave 0 - restated from `ledger/verifier-extractor.md`). Wave labels
follow the wave of the work in RECORD (tier2 studies wave4, SF-1
verification wave4, sf2 studies wave5, SF-0/P0 checks wave0,
Wave-1-prep checks wave1 - the last ten are pre-Wave-4 sessions the
earlier folds never rowed; they are included, labelled into their
own waves, so no extractor-visible work session is left unrowed).

Multi-session dispatches: usage sums per agent+model (the kit sums
per agent); passes fold to the reporting pass where a sibling
produced no verdict/commit - verifier-w5exp2 (first child died
mid-probes, RECORD Step 3a), verifier-sf1 (5 lens/synthesis
sessions, attempt-1 pair stopped by the owner parity rule),
parcel-w5aug (3 attempts, one branch tip). parcel-w5twiddledoc
keeps two passes: author (0cad043) and an unnamed Spark fixer pass
(a41f026, identified by that commit's body + session span; the
agent itself was a Spark dispatch, so both passes sum into one
Spark usage row).

## Annotation sources (never invented)

- Author commits (13 parcels): merge-commit second parent ==
  branch tip == the commit RECORD names (verified in git for each:
  minmax 128e577, interval 1d55a8a, trig 81b7635, kissfft d322d07,
  attr 8bfc877, alg1 b886e03, alg2 e858498, exp2 2618b34, site
  cd09700, demo 3feebb9, twiddledoc 0cad043 + fix a41f026, log2
  826f836, aug 3741453).
- Verdicts/a/b (26 verifier passes): the report's own counts per
  the kit chain rule ("each as its report counts them"). Explicit
  in ledger/report for the SF-0 chain, extractor, approval, p0,
  w1prep, nanfix (all READY 0,0 except sf0 0,6 / rechecker-sf0 0,2),
  w4seam (3,2), w4minmax (0,5), w4interval (2,3), w4trig (3,3),
  w4kissfft (4,1), w5attr (3,2), w5alg1 (1,3), w5alg2 (2,3),
  w5log2 (1,4), w5aug (5,1). Classed by the brief's own (a)/(b)
  definitions applied to the enumerated findings, (c) folded into
  a, dual tags at their first letter: readme (5,1), readme2 (5,0),
  sf2 (4,1), site (4,1), demo (1,4), twiddledoc (7,0 - seven ledger
  bullets), exp2 (3,2; F1 tagged (b) in the report, the rest by the
  frozen w3str/w4trig artefact precedents). Verdict vocabulary
  mapped where the kit enum requires: verifier-sf1 PASS -> READY
  (0,0, "no (a)/(b)"), verifier-sf2 FAIL -> NOT READY. Per-agent
  source strings are printed by `fold.py` (fold.log).
- sent_back: true only where git shows the work revised after the
  verdict - SF-0 chain (revisions + rechecks), verifier-readme
  (fix d87c87c), verifier-sf2 (fold f3eea91), verifier-w5twiddledoc
  (fix a41f026). Every planted-copy parcel pass merged at its
  pre-verifier tip (branch tip predates the verifier session in
  all 13 cases), so those NOT READYs carry sent_back=false.
- Escalations: sent stamps from the urgent files' `Written:` lines
  (video-final + four tier2 tests) and ledger results-entry stamps
  (alg1 2026-10-28 06:36:21, alg2 07:51:02); answered stamps are
  the answering lead commits (109b814, 53d2265). The five test
  rows omit `answered`: the lead ledger stamps no receipt for
  them, and none was estimated.
- Briefs: bases/time boxes from the briefs themselves
  (trigspike b704b4c/300 in brief + its ledger; exp2 "base = the
  hypot merge commit" = 4a80126, 900 in brief; metrics 5142594,
  ~480 in brief footer).

## Reconciliation vs scratch/study-tokens-visual/data/tokens.json

(`reconcile.py`, streamed recount with the shared counting rules.)
Their tree span ends 2026-10-28T20:07:54-07:00; this refresh runs
to 2026-10-29T11:39:55-07:00.

- Method agreement is exact: my streamed recount of the whole lead
  subtree truncated at their tmax reproduces their tree to the
  token - in=1,469,302,586, out=6,444,124, cached=1,424,594,514,
  msgs=8,709 (diff 0 everywhere). Their "242 files" vs 248 present
  now: the 6 later files contribute zero records at or before tmax.
- Tree composition at their tmax (measured here): lead main
  in=389,458,215 / out=1,037,570 / msgs=1,534; internal reminder
  sessions in=13,560,774 / out=235,121 / msgs=145; frozen-row child
  sessions in=450,114,977 / out=1,948,637 / msgs=2,759;
  then-unrowed child sessions in=616,168,620 / out=3,222,796 /
  msgs=4,271.
- Span bridge, their tmax -> SF-2 close, unrowed-children bucket
  +95,113,342 in / +351,963 out / +595 msgs, itemised: parcel-
  w5log2 tail (11,289,699 in), verifier-w5log2 (24,033,925),
  parcel-w5aug attempts 1-3 (1,164,023 + 20,137,930 + 902,128),
  verifier-w5aug (33,338,485), study-tokens-visual's own tail
  past its scan instant (4,247,152). Lead main adds a further
  11,265,354 in over the same span (unrowed, below).
- Their `grand` double-counts, beyond span: the three
  "missing_sessions" (verifier-w2xf, auditor-wave2, auditor-final)
  are inside the tree (files present in the subtree; the study's
  printed ids differ from the frozen notes by one hex digit each,
  e.g. `…84ff-c65e…` vs frozen `…84ff-2653…`), so adding their
  frozen rows on top counts in=38,594,472 / out=158,002 /
  msgs=242 twice. Corrected project billed at their span is
  tree-only 1,475,746,710, not 1,514,499,184 (+2.6% overclaim;
  their 1:785,427 headline becomes ~1:765,429 on the corrected
  denominator - their band still covers it).
- Fold tie-out: appended usage rows equal the streamed
  new-children bucket at the SF-2-close cutoff exactly (same four
  totals as "Rows before/after"); the extractor's own totals
  agree (101 work sessions, out=6,589,920, in=1,562,120,508
  including lead-to-cutoff and frozen sessions).

Not rowed, by design (quantified so the gap is visible): lead main
after the frozen wave0 cut (in=371,587,130, out=950,418,
msgs=1,452 to the SF-2-close cutoff - the brief lists no lead
continuation and the frozen idiom rows the lead once); 146
internal reminder-observer sessions (in=13,560,774, extractor-
excluded harness sessions); 3 pre-project stub sessions (zero
provider usage); 27 top-level snapshot files that duplicate
subagent sessions under the same ids (early partial copies; never
in the extractor's tree); this parcel's own session (live at the
cutoff; only its briefs row lands).

## Not reconstructed (no source, never guessed)

- briefs.jsonl rows for study-sf2-algebraic, study-sf2-attribute,
  study-sf2-augmented, study-sf2-explog, study-kissfft-visual,
  study-tokens-visual, auditor-adherence-2: none of these briefs
  (nor their ledgers) states a time box, and `time_box_min` is a
  required field - a row would invent it. (The adherence audit's
  fix list asked for the sf2 rows; the constraint above is why
  they cannot be sourced honestly. Their usage/passes rows DID
  land, with work strings from the briefs; only the briefs rows
  are missing.) Verifier briefs have never carried briefs rows
  (frozen idiom, waves 1-3 likewise) and get none.
- `answered` stamps for the five test escalations (above).
- No Wave 4-5 session is pruned or invisible: every
  ledger/scratch-named agent in the brief's list (trig, kissfft,
  interval, seam, oracle0b, trigspike, attr, alg1/2, exp2 incl.
  dead first verifier, log2, aug x3, site, demo, twiddledoc + fix,
  both visual studies, audits, SF-1/SF-2/readme verifications) has
  session files and is rowed. The wave0 escalation channel test
  stays unrowed per the metrics README idiom (rows begin Wave 1);
  its stamps exist (sent 2026-10-26 10:12:05, received 10:13:40
  in ledger/lead.md) if the lead wants the idiom changed.

## Frozen-row errors found (reported, not edited)

1. passes.jsonl `sent_back: true` on the five planted-copy parcel
   verifiers verifier-w1f32, verifier-w1f64, verifier-w2f16,
   verifier-w2xf, verifier-w3str: nothing was sent back (parcels
   merged at pre-verifier tips; findings were the plants), so the
   kit chain table overstates send-backs for waves 1-3
   (auditor-adherence-2 mechanism 1, re-verified mechanically
   here). The three lead-work trues (phase0 x2, wave0) are
   correct - restatements followed those verdicts.
2. recount-probe's frozen usage/passes rows undercount the very
   transcript they cite: the note's sha256 matches the current
   file, yet out 7,610 vs recount 8,647; in 624,495 vs 667,568;
   messages 18 vs 19; tools 19 vs 20; end …11:31:29 vs …11:31:34.
   Consistent with an `--until` cut taken while the probe was
   still finishing; the row does not reproduce from its source.
3. briefs.jsonl rows 1-2 `ceiling_text` cites "brief
   w1-ff64.md:29" / "w1-ff32.md:29"; the files are
   `ledger/briefs/w1-f64.md` / `w1-f32.md`.
4. Observation (plants.jsonl, not owned here): side-parcel plant
   rows carry topic wave labels (`readme`, `site` - the demo
   verifier's plants also sit under `site`) and short
   work strings, so per-wave kit plants tables silently omit
   verifier-readme/readme2/w5site/w5demo from wave5 (8 of 12
   groups shown). All-wave totals are unaffected.

## Gates run (observed output)

- `extract_session_metrics.py --selftest`: 8 checks, 0 failed.
- Extractor full run: 101 work sessions, exit 0 (extract.log).
- Kit `round_metrics.py --selftest`: 43 checks, 0 failed.
- Kit tables on the appended worktree files: all waves and each
  of wave0-wave5, `--repo muse-softfloat`, all exit 0
  (tables-final-*.md; wave4/wave5 chains, boxes with git-measured
  changed lines, and escalation medians render as expected).
- `tools/run.sh smoke` in the worktree: `budget smoke: PASS in
  23s`, exit 0 (tier1 783/783, tier2 66/66 - the metrics appends
  touch nothing the gate reads, run as a branch-health check).
- Load: everything above is single-job streaming or one gate run;
  nothing heavy was run beside anything else.

Not done, named: the not-reconstructed briefs rows and unanswered
test stamps above; corrections.jsonl remains frozen at Wave 3
(outside this parcel's owned files - the audit also names it);
RECORD.md gets no backfilled token figures from this parcel
(RECORD is the lead's fold; the kit tables under scratch are the
evidence); round_metrics per-wave plants coverage keeps the
topic-label gap in item 4 until the lead rules on those rows.
