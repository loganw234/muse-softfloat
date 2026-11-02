**Role:** verifier-w6metrics (ParcelRound verifier, final metrics refresh)

**Stance:** disconfirm only. The refresh claims append-only
fidelity and extractor-derived totals. Recompute both; trust
no sum you did not add up yourself.

**Copy:** `worktrees/verify6-metrics` (detached HEAD `fe04000`,
parent `cdc40ae`). Never consult the parcel branch/worktree
(`wave6-metrics`, `worktrees/w6-metrics`), other worktrees,
keys (`scratch/lead/keys/`), `scratch/lead/`,
`scratch/parcel-w6metrics/`, `ledger/lead.md`, or GitHub.
Authorities: this brief, `ledger/parcel-w6metrics.md`, the
copy's tree (its git history gives you the parent files).
Session stores may be read for extractor recounts (counting
only; no owner-text quoting beyond role labels). **Fence by
name: `docs/metrics/plants.jsonl` must not be opened, read,
grepped, or cited — no exception.** Nothing with `cft` in
its name. Never modify the copy; work in a duplicate. No
board.

**Required probes:**
1. Append-only: for each of usage/passes/escalations/briefs,
   the parent's file bytes (from the copy's git history) are
   an exact byte prefix of the copy's; escalations unchanged
   or prefix-clean. Row counts before/after per file stated.
2. Shape and references: every appended row parses with the
   frozen rows' field shape; every commit named in appended
   passes/briefs rows exists in the copy's history and is an
   ancestor of the base (or is otherwise exactly as its brief
   file states); every appended briefs row's base equals the
   base named in its `ledger/briefs/` file; no agent row
   duplicated within the appended span.
3. Totals: sum usage input/output over frozen span, appended
   span, and total yourself; compare against the parcel
   ledger's reconciliation (frozen billed, appended,
   refreshed). Per-wave row tables (usage + passes) recomputed
   and compared with the report's claims where the copy
   carries them.
4. Extractor recount: re-run `tools/extract_session_metrics.py`
   (per its header contract) far enough to independently
   recount at least 6 appended agents spanning wave6 + polish
   (tokens and tool_uses to the unit), including at least one
   verifier and one fixer; disagreements beyond the extractor's
   documented labelling gaps are findings. State your cutoff.
5. Coverage: the expected agent list from `ledger/briefs/` +
   git log vs appended agents — name any briefed agent with
   no row that the parcel report (in the ledger) does not
   already name as not-reconstructed.
6. Gate and scope: `tools/run.sh standard` PASS unchanged in
   the duplicate; diff vs parent limited to
   `docs/metrics/{usage,passes,briefs}.jsonl` (+escalations
   only if prefix-clean appends exist).

**Outputs:** `scratch/verifier-w6metrics/report.md` +
`ledger/verifier-w6metrics.md`, verdict READY or NOT READY
with numbered findings (blocker = wrong answer/regression vs
the parcel brief, or note). Structured
complete/evidence/unresolved mandatory. Script files, Git
Bash, MSF_PYTHON pinned to workspace .venv; stream large logs
with explicit memory ceilings. ~300 min.
