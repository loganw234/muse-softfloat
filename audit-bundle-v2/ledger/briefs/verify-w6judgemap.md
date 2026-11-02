**Role:** verifier-w6judgemap (ParcelRound verifier, judge's map)

**Stance:** disconfirm only. You are the judge with five
minutes and no patience: every number, link, and command in
the map must survive being used exactly as written.

**Copy:** `worktrees/verify6-judgemap` (detached HEAD, parent
`af36464`). Never consult the parcel branch/worktree, other
worktrees, keys, `scratch/lead/`, `scratch/parcel-w6judgemap/`,
`ledger/lead.md`, or GitHub run history. Authorities: this
brief, `ledger/parcel-w6judgemap.md`, the copy's tree.
**Fence by name: `docs/metrics/plants.jsonl` must not be
opened, read, grepped, or cited - with ONE exception: the
map invites a recount of its rows, so you may count its
lines and `grade` values mechanically (e.g. `wc -l`, a JSON
parse that prints only the two totals) and cite only those
totals, never row contents.** Nothing with `cft` in its
name. Never modify the copy; work in a duplicate. No board.

**Required probes:**
1. Walk the map as a judge: follow steps 1-5 in order from
   a .git-free copy of the tree. Step 1: probe the named
   film file (duration/resolution/audio) against the map's
   numbers. Steps 3-4: run every command exactly as
   printed, from the stated directory (the demo host run
   included, fetches allowed); each must do what the text
   around it claims, on a machine with no board attached
   unless the step says otherwise.
2. Every number in the changed README text re-derived by
   your own commands (instantiations, vectors, plants per
   the fence exception, manifest entries, hashes quoted -
   including truncated ones, which must prefix-match a
   full hash you compute or find recorded in the copy).
3. Every relative link in README resolves on disk;
   the demo expectation files match what the demo programs
   actually print in your run.
4. Claim discipline sweep of the diff: timings as records
   only, KissFFT never "unmodified", silent film stated,
   augmented consumption matches the code, no step
   promises hardware the judge does not have.
5. Gate: `tools/run.sh standard` PASS unchanged in the
   duplicate; diff vs parent limited to owned files.

**Outputs:** `scratch/verifier-w6judgemap/report.md` +
`ledger/verifier-w6judgemap.md`. Structured
complete/evidence/unresolved mandatory. Script files, Git
Bash, MSF_PYTHON pinned to workspace .venv. ~300 min.
