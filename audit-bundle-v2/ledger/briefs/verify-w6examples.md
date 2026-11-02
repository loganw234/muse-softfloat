**Role:** verifier-w6examples (ParcelRound verifier, examples on-ramp)

**Stance:** disconfirm only. Findings: an expectation the
mathematics contradicts, a check that cannot fail, a README
command that does not work from a fresh clone.

**Copy:** `worktrees/verify6-examples` (detached HEAD, parent
`537b08e`). Never consult the parcel branch/worktree, other
worktrees, keys, `scratch/lead/`, `scratch/parcel-w6examples/`,
`ledger/lead.md`, or GitHub run history. Authorities: this
brief, `ledger/parcel-w6examples.md`, the copy's tree.
**Fence by name: `docs/metrics/plants.jsonl` must not be
opened, read, grepped, or cited anywhere.** Nothing with
`cft` in its name. Never modify the copy; work in a duplicate.
Do not flash any board.

**Required probes:**
1. Derive every number in the host example independently
   (exact rational/integer arithmetic of your own, plus the
   committed vectors where they cover the same cells):
   pinned bit patterns, flag words, decimal strings, the
   augmented-pair identity. Any mismatch between main.c,
   expected.txt, and your derivation is a finding - name
   which artefact is wrong.
2. Failure paths: corrupt one expectation in your duplicate
   and confirm the one-command build actually fails (both a
   program self-check and the stdout diff); read build.sh
   for any path where a mismatch still exits 0, including
   the regen mode's reachability from CI.
3. CI job: the example-host job must enforce, not
   regenerate; existing jobs byte-unchanged vs parent.
4. Pico example: UF2 builds; call/constant sequences mirror
   the host program exactly (diff the two sources' demo
   sequences); run_example.sh follows the board pattern
   (lock, serial-targeted, compares output) by reading.
5. Fresh-clone rehearsal: .git-free copy of the tree,
   follow examples/README.md literally from its root.
6. Gate: `tools/run.sh standard` in the duplicate PASSes
   unchanged; only owned files differ from the parent.

**Outputs:** `scratch/verifier-w6examples/report.md` +
`ledger/verifier-w6examples.md`. Structured
complete/evidence/unresolved mandatory. Script files, Git
Bash, MSF_PYTHON pinned to workspace .venv. ~300 min.
