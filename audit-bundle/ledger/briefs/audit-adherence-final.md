**Role:** auditor-adherence-final (read-only methods audit, Wave 5 close)

**Task:** Grade how well the project adhered to the
bootstrap kit methods (HonestFramework + ParcelRound)
across the whole run, with emphasis on whether the
conceded slips in `scratch/audit-adherence-2/report.md`
were actually repaired, and enumerate the remaining
close-out debts. READ-ONLY: no repo modification.

**Authorities:** the bootstrap kit docs (workspace
root `softfloat-bootstrap-kit/` - methods text only;
its tools are frozen, reading docs is fine), git
history of `muse-softfloat/`, `docs/RECORD.md`,
`docs/metrics/*.jsonl` as refreshed at `bc807e6`,
ledger files EXCEPT `ledger/lead.md` (off-limits:
grade from artefacts, not the lead's self-account),
prior audits (`scratch/audit-adherence-2/report.md`
and any earlier). Nothing with `cft` in its name.

**Required:**
1. Re-grade each audit-adherence-2 slip: repaired /
   partially / still open, with commit-level evidence
   (Wave 1 merges before verdicts; ~30/44 lead FP
   commits unverified; key hashes never pre-committed;
   passes/usage frozen; escalations frozen;
   checked_by=integration). For key hashes: assess the
   proposed going-forward shape (key sha256 written
   into the verifier brief before dispatch, briefs in
   ledger) - is it sufficient, and is there a cheaper
   stronger one within the frozen kit tools?
2. Wave 4-5 adherence fresh-eyed: planted verification
   coverage (every merge planted? every plant key
   hashed?), append-only discipline (metrics prefixes,
   RECORD restate-vs-append handling), briefs-before-
   dispatch, timeboxes/seam-stops honored, board lock
   discipline, clean-room (no third-party source in
   repo - check, do not assume), licence/attribution
   (Co-Authored-By trailers), public-claim discipline
   in README/site/RECORD vs evidence.
3. Enumerate candidate `corrections.jsonl` rows for
   Waves 4-5 (parcel/verifier corrections to lead
   briefs or lead claims): per candidate give wave,
   brief, by, at (sourced timestamp), one-line text,
   accepted, and the exact source (file:line or
   commit). Only rows you can source; name the
   unsourceable suspicion list separately.
4. Remaining-debt list for submission (frozen files,
   stale numbers anywhere public, unverified claims),
   each with the cheapest honest disposition.

**Outputs:** `scratch/audit-adherence-final/report.md`
(first line: ADHERENT / ADHERENT WITH SLIPS / NOT
ADHERENT; per-slip re-grades with evidence; fresh
findings; corrections candidates table; debt list) +
`ledger/auditor-adherence-final.md`. Structured
complete/evidence/unresolved - mandatory. Script files
(Git Bash, MSF_PYTHON pinned). ~360 min. No board use.
