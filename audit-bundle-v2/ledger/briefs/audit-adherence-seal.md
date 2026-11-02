**Role:** auditor-adherence-seal (read-only methods audit, submission seal)

**Task:** Grade how well the project adhered to the bootstrap kit
methods (HonestFramework + ParcelRound) from the SF-2 close
through the Wave 6 queue and the seal parcels (HEAD = the tree
you are given; state its hash), and enumerate what submission
debts remain. READ-ONLY: no repo modification.

**Authorities:** bootstrap kit docs (workspace root
`softfloat-bootstrap-kit/` — methods text only), git history of
`muse-softfloat/`, `docs/RECORD.md`, `docs/metrics/*.jsonl`
(current tree), `docs/metrics/plant_keys.sha256`, ledger files
EXCEPT `ledger/lead.md` (off-limits: grade from artefacts, not
the lead's self-account), the committed `audit-bundle/`
(including `plant-keys/`), prior audits
(`scratch/audit-adherence-2/report.md`,
`scratch/audit-adherence-final/report.md`). Fence:
`scratch/lead/` is off-limits except files already copied into
the committed bundle. Nothing with `cft` in its name. Never
consider or mention any `Muse`-audit branches if you encounter
branch names — out of scope entirely.

**Required:**
1. Re-grade the remaining-debt / slip list of
   audit-adherence-final at current HEAD: each item
   repaired / partially / still open, with commit-level
   evidence.
2. Wave 6 + seal adherence fresh-eyed:
   - planted-verification coverage: every parcel merge in the
     span verified on a planted copy before merge? Every
     verifier key's sha256 committed to
     `docs/metrics/plant_keys.sha256` BEFORE its dispatch
     (git-log timing vs verifier ledger stamps)?
   - append-only discipline: metric-file prefixes across the
     span's merges (including the briefs union merge and any
     pre-push in-place restatements — disclosed or silent?),
     RECORD append-vs-restate handling after push.
   - briefs-before-dispatch, ownership fences, send-back
     handling (only regression/wrong-answer?), board lock
     discipline, Co-Authored-By trailers on AI commits.
   - clean-room: no third-party softfloat/math/workload source
     and no raw music track in the repo — check, do not assume.
   - public-claim discipline: README/site/film-caption numbers
     vs evidence at HEAD (plant tallies, token figures and
     their freeze disclosures, board claims, silent-vs-music
     posture and its licensing record).
3. Candidate `docs/metrics/corrections.jsonl` rows for the
   span (parcel/verifier corrections to lead briefs or lead
   claims): wave, brief, by, at (sourced), one-line text,
   accepted, exact source. Only sourceable rows; name the
   unsourceable suspicion list separately. State the file's
   current row count first.
4. Remaining-debt list for submission (stale public numbers,
   unverified claims, frozen-file hazards, anything a judge
   re-running the map would trip on), each with the cheapest
   honest disposition.

**Outputs:** `scratch/audit-adherence-seal/report.md` (first
line: ADHERENT / ADHERENT WITH SLIPS / NOT ADHERENT;
per-item re-grades with evidence; fresh findings; corrections
candidates table; debt list) + `ledger/auditor-adherence-seal.md`.
Structured complete/evidence/unresolved mandatory. Script
files (Git Bash, MSF_PYTHON pinned). ~360 min. No board use.
