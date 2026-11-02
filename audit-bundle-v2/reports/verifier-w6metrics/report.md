# Verifier-w6metrics report: NOT READY

Parcel commit `fe04000` ("Bring docs/metrics current through Wave 6 close"),
parent `cdc40ae`. Copy `worktrees/verify6-metrics` never modified; all work in
detached duplicate `scratch/verifier-w6metrics/dup` (registered worktree at
`fe04000`) via scripts in `scratch/verifier-w6metrics/bin/` (Git Bash,
`MSF_PYTHON` = workspace `.venv` python 3.12.15, `ulimit -v 4194304`, TMP in
verifier scratch). Cutoff `2026-10-30T16:08:00-07:00` (base committer time).
Fences held: `docs/metrics/plants.jsonl` never opened/grepped/cited, nothing
with `cft` in its name, no parcel branch/worktree, no `scratch/lead/`,
`scratch/parcel-w6metrics/`, `ledger/lead.md`, GitHub, or other worktrees.
Session-store reads counting-only via the extractor (role labels only).

## Verdict: NOT READY — 3 blockers, 4 notes

Blocker = wrong answer vs the parcel brief (`ledger/briefs/w6-metrics.md`) or
its ledger reconciliation (`ledger/parcel-w6metrics.md`).

### B1 (blocker): `usage.jsonl` is not append-only — frozen row 1 edited
- Parent bytes (from copy history) are NOT a byte prefix of the tip
  (`cmp` fails). `passes`/`escalations`/`briefs` are prefix-clean.
- Row 1 (wave0 `lead`, muse-wonder-full-1.0): `output_tokens` 116106 (parent)
  -> 1161060 (tip). Every other byte of the 93 frozen rows is identical.
- The parcel brief item 5 orders: expose wrong existing rows in the report,
  do not edit. The parcel ledger claims "frozen prefixes byte-identical" and
  "77 insertions, 0 deletions". Actual diff parent..tip: 78 insertions,
  1 deletion (`usage` 36+/1-, `passes` 37+/0, `briefs` 5+/0).
- Corroboration the parent value is the standing figure: recomputed frozen
  billed from parent bytes = 1,196,128,770 exactly (ledger's frozen figure),
  and the copy-carried `docs/RECORD.md` wave0 table lists lead out 116,106.
- Effect: +1,044,954 phantom output tokens in every tip total.

### B2 (blocker): appended `verifier-w6popups` usage row overstates output 10x
- Committed: out=336,920. Independent extractor recount of session
  `10cd2f59-...` (cutoff applied): out=33,692; in/cached/msgs/tool_uses match
  to the unit (in 3,212,583 / cached 3,095,743 / msgs 48 / tools 56).
- Same trailing-zero signature as B1 (33692 -> 336920, delta +303,228).
- Effect: appended out sums to 1,926,303, not the ledger's 1,623,075
  (in 220,313,353, msgs 2,344 verified exact). Tip billed recomputes to
  1,419,413,380, not the claimed refreshed 1,418,065,198; the gap 1,348,182
  = 1,044,954 (B1) + 303,228 (B2) exactly. Cached 1,379,156,504 and in
  1,410,803,658 verified exact.

### B3 (blocker): `fixer-w6popups` passes row names a nonexistent commit
- Row cites `ef0215b140a...b053`. No such object (`cat-file` fails; "not a
  valid commit name"; not an ancestor of base). Actual `wave6-popups` tip is
  `ef0215b140a...b052` (last hex digit 2), subject "Fix two popup-card counts
  on w6-popups (lead send-back)", parent `0708e2e` (= fixer-brief base and the
  parcel-w6popups commit). One wrong hex digit.
- The other 11 appended author/fixer commits all exist and are ancestors of
  `cdc40ae`. All 10 appended verifier rows carry a/b/verdict/sent_back; all
  12 author/fixer rows carry commit.

### N1 (note): own `briefs` row base is not the brief-named base
- `parcel-w6metrics` row base `f01dc96...` vs brief base `cdc40ae`. `f01dc96`
  ("Music decided...") is real and an ancestor of base. The other 4 appended
  briefs rows match their brief files exactly (auditor `bc807e6`, sanitize
  `50aac59`, v6 `97e10a4`, fixer `0708e2e`). The parcel brief does not dictate
  the own-row base, so note only.

### N2 (note): ledger diff summary understates the change
- "3 owned files, 77 insertions, 0 deletions" vs measured 78+/1- across the
  same 3 files (`escalations` byte-identical, sha256 full match). Subsumed by
  B1 numerically; listed because the acceptance item (e) demands exact proof.

### N3 (note): `passes` repeats two agents by design; tool-count conventions differ
- `parcel-w6ci` x2 and `parcel-w6sanitize` x2 rows are distinct sessions
  (different commits/ends), matching the ledger's send-back account; no
  exact-duplicate row anywhere. `parcel-w6ci` usage is session-summed while
  passes are per-session (47+43=90 verified per session in order);
  `auditor-staleinfo-spark` carries one passes row with tools=289 = sum over
  its 7 sessions. Numerically exact everywhere; convention mix only.

### N4 (note): coverage has no in-span gap
- Appended agents = 35 = 5 (w5-close) + 11 (polish) + 19 (wave6), matching the
  ledger's expected list; every appended session found in the lead store.
- Briefed-but-unrowed: `lead-polish1`, `parcel-w6captions`, own rows — all
  named in the parcel ledger. Five lead-store transcripts modified after the
  cutoff all start after it (16:10/17:12/17:44; one is this verifier's own),
  so all are mechanically excluded, consistent with the ledger's seal-parcel
  account. `verifier-w6captions`/`video-final` have no in-span work sessions.

## Passing probes (detail)
1. Append-only: row counts usage 93->128, passes 94->131, escalations 20->20,
   briefs 39->44 (as claimed). Parent prefix sha256-first16 match the ledger's
   quoted hashes for all four files (8041187465af8a18, bafaf2d41f280bcc,
   9213f63174d82613, 7ff1f2919a48a02e; full hashes in `out/` logs).
2. Shape/refs: all appended rows parse; frozen/appended key-shape sets equal
   for all three files; briefs bases per above; no exact-dup rows.
3. Totals: frozen billed 1,196,128,770 exact from parent bytes; appended in +
   msgs exact; out/cached/tip per B1+B2. Carried `RECORD.md` wave0 table:
   19/19 carried rows match parent bytes exactly (out/in/tools); the other 8
   wave0 agents are not carried as tables (prose only); tip lead row
   contradicts the carried 116,106.
4. Extractor recount: selftest 8/0; 10 agents (8 wave6 incl. 3 verifiers +
   fixer, 2 polish) recounted to the unit for tokens and tool_uses at the
   stated cutoff; session-id fallback labels are the extractor's documented
   gap and match the rows' own notes. Logs: `out/recount.log`.
5. Coverage: per N4. Log: `out/fresh.log`, `out/labels.log` (labels only).
6. Gate/scope: `tools/run.sh standard` PASS exit 0 in the duplicate
   (61 s; totals 411,213 + 1,117,504; log `out/standard.log`); diff vs parent
   limited to `docs/metrics/{usage,passes,briefs}.jsonl`; escalations
   byte-unchanged. Duplicate and copy both clean of tracked modifications.

## Remedy (for the lead; not applied — verifier never edits)
Restore `116106` (usage line 1), `33692` (verifier-w6popups out), `...b052`
(fixer commit); re-issue reconciliation (refreshed billed 1,418,065,198 then
recomputes exactly); optionally restate the own-briefs-row base rule.
