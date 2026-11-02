# Ledger: parcel-w6metrics (Wave 6 close: final metrics refresh)

## 2026-10-30 design entry (before any metrics edit): expected list + annotation plan

**parcel-w6metrics** (brief ledger/briefs/w6-metrics.md). Base
cdc40ae, worktree worktrees/w6-metrics, branch wave6-metrics
(clean at entry). Owned files only:
docs/metrics/{usage,passes,escalations,briefs}.jsonl,
append-only. Nothing with `cft` in its name opened/searched/
listed; docs/metrics/plants.jsonl not opened. Session logs read
for counting and role labels only. All runs are script files in
scratch/parcel-w6metrics/ under Git Bash, MSF_PYTHON pinned to
the workspace .venv, TMP in scratch, ulimit ceiling in the
runner.

Expected-agent list built FIRST from ledger/briefs/ + git log
(2026-10-29T11:39:55..2026-10-30T16:08:00, all branches) +
per-agent ledger files, before the extractor ran: 5 Wave-5-close
agents (w5metrics, w5readme3 + their verifiers,
auditor-adherence-final); the 2026-10-29 polish round (8 film
studies, study-video-textpacing x2 sessions, the Spark
stale-info audit of 7 sessions per lead.md, verifier-polish1;
lead-polish1 itself lead-authored with no child session); 19
Wave 6 agents (7 parcels, fixer-w6popups, 7 verifiers,
study-w6sanitize, film v6/v7 studies, surveyor-epidemiclicense;
parcel-w6ci and parcel-w6sanitize two sessions each after lead
send-backs). Annotations (--author-commit/--verdict and all fold
restatements) from ledger/RECORD/git log only. Cutoff: committer
time of base cdc40ae, 2026-10-30T16:08:00-07:00, so the two seal
parcels dispatched at the base (this one, parcel-w6captions) are
excluded mechanically.

## 2026-10-30 results entry: READY; rows appended through Wave 6 close

Full record: scratch/parcel-w6metrics/report.md (first line
READY). One commit on wave6-metrics, never pushed/merged.
git diff vs base: 3 owned files changed, 77 insertions,
0 deletions; escalations byte-unchanged.

- Rows: usage 93->128 (+35), passes 94->131 (+37),
  escalations 20->20 (+0, none sourceable - searched
  ledger/urgent, all span ledgers, all Wave 6 briefs),
  briefs 39->44 (+5, own row last). Spans now end
  2026-10-30T15:43:55-07:00 (verifier-w6popups).
- Coverage: 45 new work sessions -> 35 agents; fold.py asserts
  the expected list exactly (0 unmapped, 0 missing; every
  author commit an ancestor of cdc40ae; every briefs base
  resolvable). No session pruned: all 101 w5-era extractor
  sessions still on disk and recount exact.
- Totals: frozen billed 1,196,128,770 re-derived as the frozen
  usage.jsonl in+out (the film outro figure, unchanged there).
  Appended billed +221,936,428 (in 220,313,353 / out 1,623,075,
  msgs 2,344). Refreshed at cutoff: billed 1,418,065,198
  (in 1,410,803,658, out 7,261,540, cached 1,379,156,504,
  msgs 10,100). Difference is span only; recount cross-checks
  (w5 extract-out and an independent streaming inventory) agree
  to the token.
- Not rowed, quantified in the report: lead continuation after
  the frozen wave0 cut (in 495,572,730, incl. lead-polish1's
  author work), 146 internal reminder sessions (in 13,560,774),
  the two post-cutoff seal-parcel sessions.
- Append-only proof: frozen prefixes byte-identical (prefix
  sha256 usage 8041187465af8a18, passes bafaf2d41f280bcc,
  escalations 9213f63174d82613, briefs 7ff1f2919a48a02e);
  appended files equal the pre-validated combined copies.
- Gates: extractor selftest 8/0; kit round_metrics selftest
  43/0 and tables (all/wave5/polish/wave6) exit 0 on combined
  copies of the four owned files only; tools/run.sh standard
  PASS in the worktree (exit 0, totals 411,213 + 1,117,504;
  scratch/parcel-w6metrics/standard.log).
- Frozen-row findings (reported, not edited): briefs row 32
  lead-polish1 time_box_min 240 has no source in its brief or
  ledger; three w5-reported items re-confirmed verbatim.
  verifier-w5metrics F1-F4 confirmed to describe its planted
  copy only, not the frozen rows.
- Not reconstructed (named in the report): briefs rows for the
  nine 10/29 film studies, gitvisual-v7, epidemic licence study
  and the Spark audit (no sourceable base+time box);
  parcel-w6captions briefs row left to that parcel's own tip;
  lead-polish1 pass row (lead main session, frozen idiom);
  this parcel's own usage/pass rows (post-cutoff, live).

For: lead.
