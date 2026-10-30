**Role:** verifier-w5metrics (ParcelRound verifier, metrics refresh)

**Stance:** disconfirm only. Findings: a number that
does not re-derive from a transcript, an annotation
without a record source, an edited frozen row.

**Copy:** `worktrees/verify5-metrics` (detached HEAD,
parent `5142594`). Never consult the parcel
branch/worktree, other worktrees, keys, `scratch/lead/`,
`scratch/parcel-w5metrics/`, or `ledger/lead.md`.
Authorities: this brief, `ledger/parcel-w5metrics.md`,
`tools/extract_session_metrics.py` (in the copy), the
session stores under
`C:\Users\logan\.local\share\muse\sessions\`, the copy's
git history, `docs/RECORD.md`, scratch study data
(`scratch/study-tokens-visual/data/tokens.json`) for
the reconciliation. Nothing with `cft` in its name.
Never modify the copy. Session logs for counting only
(role labels; no owner prose quoted).

**Required probes:**
1. Append-only: prefix of each metrics file byte-
   identical to the parent's (hash the parent blob
   against the file head; row counts before/after).
2. Re-run the sanctioned extractor yourself (selftest
   first) on a sample of appended sessions spanning
   waves 0/4/5 + one verifier + one study; every token/
   message/tool-use number must match its row exactly.
   Model attribution per row vs the transcripts.
3. Annotations: every author-commit and verdict in
   appended passes rows traced to git/RECORD/ledger;
   sent_back semantics (true only on a proven revision
   round; a planted-copy NOT READY is not a send-back).
4. Escalations: each appended row's sent/answered
   stamps sourced; an answered stamp with no source
   is a fabrication finding.
5. Briefs: restored rows' base commits exist and are
   the parcels' real bases (git cat-file + branch
   archaeology from the copy's history/RECORD);
   time boxes from briefs/ledger, never invented.
6. Reconciliation re-derived: fold totals vs your
   streamed recount; the tokens-study span bridge and
   the claimed 38.6M double-count checked in numbers.
7. Kit `round_metrics.py` tables exit 0 on the copy's
   files; `tools/run.sh smoke` PASS outside the copy.

**Outputs:** `scratch/verifier-w5metrics/report.md`
(READY/NOT READY; per-probe evidence; findings;
not-done) + `ledger/verifier-w5metrics.md`. Structured
complete/evidence/unresolved - mandatory. Script files
(Git Bash, MSF_PYTHON pinned), ulimit ceilings, stream
large logs. ~360 min.
