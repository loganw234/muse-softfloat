# Verifier-w6metrics: NOT READY (3 blockers, 4 notes)

Verified parcel commit `fe04000` (parent `cdc40ae`) from detached duplicate;
copy never modified. Full evidence: `scratch/verifier-w6metrics/report.md`
(scripts `scratch/verifier-w6metrics/bin/`, logs `scratch/verifier-w6metrics/out/`).
Cutoff `2026-10-30T16:08:00-07:00`. All fences held.

## Findings

**B1 (blocker).** `usage.jsonl` is not append-only: frozen row 1 (wave0 lead)
`output_tokens` 116106 -> 1161060. Parent bytes are not a prefix of the tip;
actual diff is 78+/1-, not the claimed 77+/0. Parcel brief item 5 forbids
editing existing rows. Parent value corroborated by the recomputed frozen
billed 1,196,128,770 (exact) and the carried `RECORD.md` wave0 table.
Effect: +1,044,954 phantom output tokens in tip totals.

**B2 (blocker).** Appended `verifier-w6popups` usage out=336,920 vs transcript
recount 33,692 (same trailing-zero signature; all other fields exact to the
unit). Appended out sums to 1,926,303, not 1,623,075; tip billed recomputes to
1,419,413,380, not 1,418,065,198 (gap = B1 + B2 to the token).

**B3 (blocker).** `fixer-w6popups` passes row cites commit `...b053`, which does
not exist; actual `wave6-popups` tip is `...b052` (one hex digit). All other 11
author/fixer commits exist and are ancestors of base.

**N1 (note).** Own `briefs` row base `f01dc96` (real, ancestor of base) is not
the brief-named base `cdc40ae`; the other 4 appended briefs rows match their
briefs exactly.

**N2 (note).** Ledger diff summary "77+/0" understates measured 78+/1-.

**N3 (note).** `parcel-w6ci`/`parcel-w6sanitize` double passes rows are distinct
send-back sessions (no exact dups); per-session vs summed tool counts are
numerically exact everywhere (e.g. auditor 289 over 7 sessions).

**N4 (note).** Coverage clean: 35 appended agents = expected 5+11+19; no
in-span briefed agent lacks a row; 5 post-cutoff sessions (one mine) all start
after the cutoff and are mechanically excluded.

## Passing
Row counts as claimed; parent prefix hashes match the ledger's for all four
files; frozen billed exact; appended in/msgs/cached exact; shapes/annotations
complete; 10-agent extractor recount exact except B2 (selftest 8/0);
`tools/run.sh standard` PASS exit 0 in the duplicate; diff limited to the three
owned files; escalations byte-identical.

For: lead.
