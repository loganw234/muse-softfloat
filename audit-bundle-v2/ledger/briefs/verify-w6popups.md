**Role:** verifier-w6popups (ParcelRound verifier, generalised popup cards)

**Stance:** disconfirm only. Seven cards now make seven counted
claims under a frozen timeline. Recount every number from its
source and re-derive the timing freeze; anything you cannot
re-derive is a finding.

**Copy:** `worktrees/verify6-popups` (detached HEAD `8507695`,
parent `f01dc96`). Never consult the parcel branch/worktree
(`wave6-popups`, `worktrees/w6-popups`), other worktrees, keys
(`scratch/lead/keys/`), `scratch/lead/`,
`scratch/parcel-w6popups/`, `ledger/lead.md`, or GitHub.
Authorities: this brief, `ledger/parcel-w6popups.md`, the
copy's tree. **Fence by name: `docs/metrics/plants.jsonl` row
contents must not be opened, read, or cited — with ONE
exception: you may count its lines and `grade` values
mechanically and cite only those totals.** Nothing with `cft`
in its name. Never modify the copy; work in a duplicate. No
board.

**Required probes:**
1. Recount every card number from source data in the copy
   with your own scripts: role/episode counts from
   `video/segments/process_graph.json` (distinguish drawn
   lane roles from passes roles, and account for the spine
   episode), merges from `video/segments/history.json`,
   escalation filings vs fixer lanes from
   `docs/metrics/escalations.jsonl` + the graph, plants
   totals from the graph's accounting vs the fenced file's
   mechanical totals, gate test volumes from `tools/run.sh`
   composition (what smoke verifies; what standard adds:
   derive the extras from their generator parts) and RECORD.
   Each card's stated count must equal the count its own
   description describes, from the source the parcel ledger
   names; a count that matches a *different* source than its
   description (e.g. HEAD vs frozen, lanes vs passes) is a
   finding.
2. Timing freeze. Import the copy's `gitvisual.py` and the
   parent's (from the copy's own git history): `POPUP_WORDS`
   per card, `POPUP_DWELL`, `ARRIVALS`, `T_BRIDGE`,
   `T_REPLAY`, `SHIFT`, `GATES`, `LEGS`, `TOTAL` must be
   identical card-by-card and constant-by-constant. Cursor
   exactly on each gate rank at its t0; monotonic.
3. Render truth: probe the copy's `gitvisual7.mp4`
   (duration/resolution/fps/audio) and grab one still per
   card at mid-dwell; the rendered text must match `POPUP5`
   exactly, sit inside its card, and be legible. Titles must
   match the on-screen legend's system names.
4. Copy discipline: descriptions are general (no incident
   specifics, hashes, or file names), titles/lines within
   the pacing limits (headline <=6 words, lines <=10), and
   no card claims anything the following replay does not
   show.
5. Gate and scope: `tools/run.sh standard` PASS unchanged
   in the duplicate; diff vs parent limited to
   `video/segments/gitvisual.py` (POPUP5 strings/comment),
   the regenerated `gitvisual7.mp4`, and the briefs own
   row; the briefs row's numbers match your recounts.

**Outputs:** `scratch/verifier-w6popups/report.md` +
`ledger/verifier-w6popups.md`, verdict READY or NOT READY
with numbered findings (blocker = wrong answer/regression
vs the parcel brief, or note). Structured
complete/evidence/unresolved mandatory. Script files, Git
Bash, MSF_PYTHON pinned to workspace .venv. Stop and report
if a frame pipeline would exceed ~6 GB. ~240 min.
