# Audit Wave 1 — method adherence (disconfirm-only)

Auditor: auditor-wave1. Kit: softfloat-bootstrap-kit v1 (frozen; not modified).
Method read in full: WORKFLOW.md, ROLES.md, METRICS.md, PROJECT.md, OWNER.md,
CLEAN-ROOM.md, AGENTS.md, GLOSSARY.md, MANIFEST.txt.
Project record read: ledger/lead.md, ledger/parcel-f32.md, ledger/parcel-f64.md,
ledger/verifier-w1f32.md, ledger/verifier-w1f64.md, ledger/briefs/w1-f32.md,
ledger/briefs/w1-f64.md, ledger/briefs/w1-f32-regate.md,
ledger/briefs/w1-f64-regate.md, scratch/parcel-f32/report.md,
scratch/parcel-f64/report.md, scratch/verifier-w1f32/report.md,
scratch/verifier-w1f64/report.md, muse-softfloat/docs/RECORD.md,
muse-softfloat/docs/metrics/*.jsonl, git log/status/show in muse-softfloat.
Keys: sha256 only (scratch/lead/keys/*.json); contents never opened.

## Verdicts per method area

1. ParcelRound briefs / time boxes / scope ceilings / off-limits — ADHERED
with one brief fault (lead-confirmed, counted in corrections.jsonl).
- Briefs carry owned/forbidden files, negative controls, time box (300 min),
  ceiling (3,000 lines), READY def, and the what-this-brief-got-wrong line:
  ledger/briefs/w1-f32.md:25-31,89-101; w1-f64.md:25-31,89-101.
- F32 brief line 89 says totalOrder keys are "within binary64" for a
  binary32 parcel — wrong, CONFIRMED by lead (ledger/lead.md 2026-10-26
  21:55:48) and counted (corrections.jsonl row 1). F32 brief pack sentence
  vs msf32_log_b dest f64 — CONFIRMED same entry, counted (row 2).
- Ceilings held: f32 1,814/3,000 lines, vectors 930,433/1MB bytes
  (scratch/parcel-f32/report.md:18-23); f64 1,788/3,000, 998,736 bytes
  (scratch/parcel-f64/report.md:44-46).
- Active work inside boxes: f32 design 21:53:20 to checkpoint 22:19
  (~26 min) + regate 05:04-05:14 (~10 min, within regate 120-min box);
  f64 design 21:55:22 to checkpoint 22:28 + regate ~11 min. No 240-min
  checkpoint was owed (work closed same evening). Off-limits held:
  parcels escalated kernel/ingest defects instead of editing
  (ledger/parcel-f32.md 2026-10-26 22:11:37).
2. Escalation discipline (incl. first-minutes test) — ADHERED with weak trail.
- Wave 1 test escalations filed at start per briefs and answered in ~20 s,
  recorded in docs/metrics/escalations.jsonl rows 1-2
  (21:44:19→21:44:38, 21:45:08→21:45:28). Load-bearing escalation
  (tininess + eq ingest) ledger-first then urgent, ruled within ~3 min
  (ledger/lead.md 2026-10-26 22:14:34; escalations.jsonl rows 3-4).
- Trail weakness: ledger/urgent/ holds only test-escalation-channel-test.md;
  the Wave 1 parcel test files were cleared, so file evidence is gone and
  the claim rests on escalations.jsonl + parcel reports. Clearing is normal
  practice but the method's cross-check (ledger stamps vs files) cannot run.
3. Verifier independence and verdict discipline — ADHERED on independence,
  DIVERGED on sequencing.
- Both verifiers built fresh independent references (no generator imports),
  state nothing was fixed, list named gaps, never touch cft/board/lead
  (scratch/verifier-w1f32/report.md §9; scratch/verifier-w1f64/report.md
  "Not done"). Classes used correctly: (a)/(b) only send-backs carry the
  verdicts; notes N1-N6 separated.
- SEQUENCING DIVERGENCE: local merges 2843792 (f32, 05:17:07) and 06fdec8
  (f64, 05:18:44) moved the parcels onto main BEFORE the planted verifiers
  reported (ledger/verifier-w1f64.md 05:44:40, ledger/verifier-w1f32.md
  05:49:50). WORKFLOW.md Phase 4 demands verify-then-merge with the gate
  after each merge and ROLES.md forbids merging on a report's strength.
  Push was held (remote still pre-wave at audit time for these commits…
  actually 8d8219c/704cf0c wiring commits exist locally; `git status` shows
  only metrics files modified, merges committed locally). Lead self-reports
  this as "deviation to be named in the Wave 1 RECORD entry"
  (ledger/lead.md 2026-10-27 05:58:36). Consequence is live: both verifiers
  returned NOT READY on the planted copies (correctly — the copies carry
  5 plants each), and the send-back loop now has to operate on already-merged
  trees. The verifiers' (a)-class findings on shared-file diffs vs base
  are copy artifacts of exactly this ordering (f32 report §6 probes the
  lead-fix files; lead entry 05:58:36 confirms).
- No verifier brief files exist in ledger/briefs/ (only parcel + regate
  briefs). Verifier tasking lives in Workflow prompts/scratch scripts, not
  in the method's templates/verifier.md shape. Falsifiable: `ls
  ledger/briefs` shows 4 files, none naming a verifier.
4. Ledger practice (append-only, per-agent, Measured/Believed/For, at-event)
   — PARTIAL, with an honestly self-reported gap.
- Shape held everywhere sampled: every entry carries Measured/Believed/For
  lines. Per-agent files held. No edits of others' files seen.
- GAP CONFIRMED: lead.md jumps 22:14:34 → 05:23:02 with zero entries for
  checkpoints 6c1bc01/5153324, fixes 53acb1a/b37fb12, merges 9bb8723/
  80cbc97, regates cb10ee2/26c76aa, serial merges 2843792/06fdec8.
  The 2026-10-27 06:27:24 BACKFILL entry admits exactly this ("that gap is
  the fault being recorded") at the owner's prompt. Backfill is honest but
  after-the-fact: entries-belong-at-the-event is the violated half.
- Verifier ledger bodies were staged by children and appended by the lead
  (sandbox could not spawn ledger.sh); disclosed in ledger/verifier-p0.md
  precedent and rechecker-tininess.md. Acceptable with disclosure, but the
  f32/f64 verifier ledger entries should state the same staging explicitly —
  verifier-w1f32.md/ledger-body.md exists in scratch; check the ledger entry
  notes it.
5. Metrics inputs (usage/passes/briefs/plants/corrections/escalations/
   fetches) — PARTIAL; rows exist but uncommitted, Wave 1 passes/usage owed.
- CONFIRMED PRESENT (working tree): plants.jsonl 10 rows, 9 caught / 1
  missed (f32 generator-pool INT32_MAX plant, note names the benign-filed
  drift); corrections.jsonl 7 rows; escalations.jsonl 5 rows with
  test flags and answer stamps; briefs.jsonl 2 rows; fetches.jsonl 2 rows
  with archive + licence hashes. Key hashes in plants.jsonl match
  `sha256sum scratch/lead/keys/key-*.json`
  (71ef8ff1…f32, e6bbc65c…f64). Grading 9/10 CONFIRMED against verifier
  reports (f32 report §7 classes map to 4 caught + 1 missed; f64 report
  5/5 caught).
- GAPS: (a) all three Wave 1 rows files show `M` in `git status` —
  written but UNCOMMITTED, so the record (RECORD.md has no Wave 1 entry
  yet) carries no Wave 1 metrics; (b) passes.jsonl/usage.jsonl end at
  Wave 0 — no rows for parcel-f32/f64, regaters, rechecker-tininess, or
  the two planted verifiers; (c) briefs.jsonl omits the two regate briefs
  (only the 300-min parcel briefs; regates add 120-min boxes each).
6. Clean-room rules — ADHERED on evidence available.
- No cft open/search/list in any read ledger, report, or commit body;
  both Wave 1 verifiers explicitly record cft untouched
  (f32 report §9, f64 report "Not done"). Key contents never opened by
  this audit (hashes only). No mechanical fence exists (known limit,
  RECORD.md Wave 0 entry) — owner's audit is the control.
7. Record / commit practice (detailed bodies, ledger stamps,
   Co-Authored-By) — ADHERED on bodies/trailers, PARTIAL on stamp timing.
- Sampled commits carry detailed bodies + `Co-Authored-By: Muse Code
  (muse-wonder-full-1.0) <noreply@meta.ai>`: 2843792, 06fdec8, 8d8219c,
  52a6715, 53acb1a all confirm. Merge bodies name evidence paths
  (scratch/*/report.md, ledger files). Lead fix 53acb1a was Spark-rechecked
  READY before push (ledger/rechecker-tininess.md 2026-10-27 05:00:39,
  (a)0 (b)0, oracle differential 2400/2400).
- TIMING GAP: merge bodies claim "standard re-run at this merge," but no
  merge-time log path is cited in either merge message, and the lead ledger
  had no entry at 05:17-05:18 (see finding 4). The backfill entry
  (06:27:24) asserts `tools/run.sh standard` PASS after each merge (final
  smoke 52,168 vectors, 9/9 controls, +1,117,504 standard) plus board
  replay (2,767 vectors, host==board SHA-256
  4d7c2a28…b329). Believed-until-logged: ask for the two merge-time logs
  by path in the Wave 1 RECORD entry.
8. Budget gates (smoke / standard / board) — ADHERED as run, with scoping
   note.
- Smoke + standard PASS re-run in worktrees at regate (f32 report §5,
  f64 report test group 1: smoke 29,982 + standard +1,117,504, 9/9
  controls). Board replay measured with whole-run hash agreement
  (backfill entry). Scoping note both verifiers state and the method
  requires: run.sh budgets do NOT replay parcel *-f32.vec/*-f64.vec
  (f32 report §2: VECS lists P0 vectors only); the budgets pass while
  parcel vectors fail. The lead closed this at merge with wiring commits
  704cf0c/8d8219c. Verdict on gate adequacy is the integration
  verifier's, still owed.
9. Owner-intervention handling — ADHERED.
- Standing push/merge permission, Co-Authored-By rule, commit-body rule,
  SF-0 approval + MIT/Logan W. all recorded verbatim with dates
  (ledger/lead.md 2026-10-26 10:48:17, 10:49:40, 11:38:59; 13:57:41).
  Remaining kickoff items conversationally deferred per the owner's own
  word — within OWNER.md "What the lead asks first."

## Severity-ordered findings (one per line, falsifiable)

1. SEV-1: Merges 2843792/06fdec8 moved Wave 1 parcels onto main before
   planted verifiers reported (05:17-05:18 vs 05:44/05:49) — verify-then-
   merge violated; send-back loop now operates on merged trees.
2. SEV-1: Lead ledger silent 22:14→05:23 across 2 checkpoints, 2 fixes,
   2 branch merges, 2 regates, 2 serial merges, 2 wiring commits —
   self-admitted in 06:27:24 BACKFILL; entries belong at the event.
3. SEV-2: Wave 1 metrics rows (plants/corrections/escalations) modified
   but uncommitted (`git status M`); passes/usage have zero Wave 1 rows —
   RECORD carries no Wave 1 figures yet.
4. SEV-2: No verifier brief files in ledger/briefs/ (4 files: 2 parcel,
   2 regate); verifier tasking not in templates/verifier.md shape.
5. SEV-2: briefs.jsonl omits both 120-min regate briefs; time-box table
   will undercount Wave 1 boxes 2/4.
6. SEV-2: Wave 1 urgent test files absent from ledger/urgent/ (only the
   Phase 0 test file remains); test-escalation evidence rests on
   escalations.jsonl alone.
7. SEV-3: Merge messages claim merge-time standard re-runs without citing
   log paths; only source is the next-day backfill entry — demand log
   paths in the Wave 1 RECORD entry.
8. SEV-3: run.sh smoke/standard do not replay parcel vector files
   (verifier-proved); budgets alone cannot gate Wave 1 — closed only by
   post-merge wiring commits 704cf0c/8d8219c, integration check owed.
9. SEV-3: Grading (plants.jsonl, 05:56) precedes the round-end reveal the
   method schedules "near the end" (WORKFLOW.md); keys still confined to
   scratch/lead/keys/ (hashes match ledger) — early but contained.
10. SEV-3: f32 generator-pool plant (INT32_MAX weakened) missed exactly as
    graded: 16-line regen drift observed but filed benign
    (plants.jsonl row 5 note; verifier-w1f32 report §2 conv-int drift) —
    detection without the byte-identity norm; process fix owed, not a
    grading dispute.
11. SEV-4: Verifier ledger-append provenance (child-staged, lead-appended)
    disclosed for P0 precedent but not stated in the w1f32/w1f64 ledger
    entries — one line owed in each.
12. SEV-4: Parcel-f32 report notes CRLF parcel rows vs AGENTS.md LF rule in
    implemented.tsv (report.md:47-52); lead LF-normalised at b37fb12 —
    closed, record as brief-fault-class example.

## What a final-wave audit must re-check

- That a Wave 1 RECORD entry exists with chain table (a)/(b) per pass,
  send-backs, time-box/ceiling actuals incl. regate boxes, plants table
  via round_metrics.py at reveal, corrections accepted, escalations with
  latencies, and the deviation note for pre-verification merges.
- That passes.jsonl/usage.jsonl gain one row per Wave 1 agent
  (parcel-f32/f64, both regaters, rechecker-tininess, verifier-w1f32/
  verifier-w1f64) with transcript/model stamps, and briefs.jsonl gains
  the two regate rows; re-run `round_metrics.py --wave wave1`.
- That the integration verifier re-made each merge with `git merge-tree`
  and checked plant grading via `plant.py check` (WORKFLOW.md steps 7-8),
  with the reveal reading keys from the ledger/record, not scratch.
- That merge-time standard/board logs are cited by path and replayed,
  and that wiring commits 704cf0c/8d8219c regenerated tables byte-clean.
- That verifier briefs exist as files for Wave 2+ (or a recorded owner
  decision that Workflow prompts replace them), and urgent test files are
  retained until the wave closes.
- That no Wave 1 commit message claim ("READY", counts) outlives its
  verifier: parcel re-gate READY claims (26c76aa, cb10ee2) vs planted
  NOT READY verdicts must be reconciled line-by-line (plants vs genuine
  defects) in the RECORD entry.
- Clean-room: owner's fingerprint audit at wave close, result in record.
