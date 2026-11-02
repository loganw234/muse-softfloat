**Role:** parcel-w6ci (Wave 6 queue item 2: library CI on Linux)

**Base:** `50aac59f6035d56c37340ff07c59252cfd22d5d4`, branch
`wave6-ci`, worktree `worktrees/w6-ci`. Work only there.

**Job:** add GitHub Actions CI that runs the library gate on
Ubuntu, proving the results are not specific to the owner's
Windows host. Minimum: a `smoke` job on push/pull_request/
workflow_dispatch (checkout, install host gcc + python3 +
gcc-arm-none-eabi, `MSF_PYTHON=python3 bash tools/run.sh smoke`,
upload the build/smoke logs as an artefact). Add a `standard`
job the same way (it is the merge gate; allow a generous
timeout). Make only the portability edits to `tools/run.sh`
that Linux actually requires - inventory every Windows/MYS2
assumption you find (PATH, cygpath, .exe names, `python` vs
`python3`, dumpmachine pattern, the x87 control, any exec
tricks) in your report with its Linux disposition; do not
change what the gate checks or weaken any refusal. The gate
must still print its full inventory before any verdict, and a
green run that cannot name its vectors has failed (AGENTS.md).

**Owned files:** .github/workflows/ci.yml (new), tools/run.sh
(portability only), docs/HARNESS.md or AGENTS.md only for a
one-paragraph CI pointer if truly needed, docs/metrics/
briefs.jsonl (own row, wave "wave6", base above). No library
src/include, no RECORD/README edits.

**Acceptance:** (a) `tools/run.sh standard` still PASSes on this
Windows host in the worktree after your edits (byte-for-byte
same verdicts); (b) workflow YAML parses (state your checker)
and every command in it is one you have run locally in
equivalent form, or flagged as CI-only; (c) the lead will push
branch `wave6-ci` to trigger the real run before merge - your
report must state exactly what a green run will show and what
could still differ on Ubuntu (package names/versions are the
risk to name). Do not push anything yourself.

**Outputs:** tip commit(s) on `wave6-ci` with detailed body +
`Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>`;
`scratch/parcel-w6ci/report.md` + `ledger/parcel-w6ci.md`.
Structured complete/evidence/unresolved mandatory. Script files,
Git Bash, MSF_PYTHON pinned, scratch under `scratch/parcel-w6ci/`.
Nothing with `cft` in its name. ~360 min.
