**Role:** auditor-adherence-2 (owner-requested methods audit)

**Question:** how well has this project actually followed
the two working methods - HonestFramework and ParcelRound
as carried in the bootstrap kit - across the whole run so
far (Phase 0 through Wave 5 SF-2 Step 1)? Grade adherence
mechanism by mechanism from executed evidence, not from
what the documents claim. Read-only: modify nothing,
commit nothing, flash nothing.

**Sources (read as governing):** the bootstrap kit
(`softfloat-bootstrap-kit/` - read its method documents
and tool contracts in full), `muse-softfloat/AGENTS.md`,
`muse-softfloat/docs/HARNESS.md` and `KICKOFF.md`,
`ledger/` (lead + parcel/verifier/study files),
`muse-softfloat/docs/metrics/*.jsonl`, the git history
of `muse-softfloat` (commit bodies, merges, authorship
trailers), `scratch/` report trees, brief files. Never
open/search/list anything with `cft` in its name. You may
read `ledger/lead.md` (it is evidence for you, unlike for
verifiers). The earlier mid-project adherence report
(scratch, Wave 1 era) may be read for continuity - grade
independently; say where you disagree with it.

**Mechanisms to grade (each: held / held-with-named-slips
/ broken, with the smallest concrete evidence - commit
hash, ledger line, file:line, or a counted sample):**
1. Verifier before main moves (planted copies, disconfirm-
   only, verdicts honoured; count parcels/lead commits
   that reached main without one, if any).
2. Planted-copy hygiene (keys outside the repo, copies
   detached/no refs, grades recorded in metrics, misses
   graded honestly rather than edited away).
3. Parcels: brief-before-work, owned-file discipline,
   design entries before code, READY/NOT READY honoured,
   no parcel merging its own work.
4. Records: in-place restatement only pre-push, append-
   only after; RECORD/metrics same-step with the work;
   ledger outside the worktree; slips attributed.
5. Honest claims: SF-0/SF-1/SF-2 claim surface vs what
   shipped (claim tokens closed set, deferred by name,
   qualified sentences - sample RECORD/README/BOARD
   sentences against the artefacts); timings recorded,
   never claimed as performance.
6. Clean room: oracle fetch records (hashes, licences),
   no vendored third-party source in the repo (sample the
   tree), executed-only oracle discipline, the fenced
   defective-oracle handling.
7. Commit discipline: detailed bodies, verification +
   ledger references, Co-Authored-By trailers (count
   coverage over history), merge shapes.
8. Automation honesty: script files not inline one-offs
   for gates, negative controls permanent and run,
   runner inventory checks, board lock + serial targeting
   under multi-board bus (evidence in scripts/logs).
9. Owner gates: decisions asked where the methods
   require them (studies approved before waves, scope
   changes recorded), standing permissions used within
   their text.
10. Incident handling: the recorded failures (tininess,
    env-drop flash trap, oracle defects, runaway script)
    - were they recorded same-step with corrective rules?

**Outputs:** `scratch/audit-adherence-2/report.md`:
- line 1: overall grade (ADHERENT / ADHERENT WITH SLIPS /
  NON-ADHERENT) + one-sentence justification;
- per-mechanism grades with evidence pointers and counts;
- the five sharpest slips, each with its cost;
- five concrete fixes worth adopting before Wave 5 ends;
- not-audited list (sampling boundaries named).
And `ledger/auditor-adherence-2.md` (Measured/Believed/For).
Structured complete/evidence/unresolved. Script files for
any counting (Git Bash, MSF_PYTHON pinned, TMP in your
scratch). Where the kit text and the project's practice
diverge by a recorded owner decision, that is adherence,
not a slip - say so explicitly.
