**Role:** verifier-w6sanitize (ParcelRound verifier, sanitize budget)

**Stance:** disconfirm only. Findings: a sanitize run that
can pass without instrumenting, a canary that cannot trap,
a skip that claims findings, a flavour leak into other
budgets.

**Copy:** `worktrees/verify6-sanitize` (detached HEAD, parent
`537b08e`). Never consult the parcel branch/worktree, other
worktrees, keys, `scratch/lead/`, `scratch/parcel-w6sanitize/`,
`scratch/study-w6sanitize/`, `ledger/lead.md`, or GitHub run
history. Authorities: this brief, `ledger/parcel-w6sanitize.md`,
the copy's tree. **Fence by name: `docs/metrics/plants.jsonl`
must not be opened, read, grepped, or cited anywhere.**
Nothing with `cft` in its name. Never modify the copy; run
gates in a duplicate under your own scratch.

**Required probes:**
1. `bash tools/run.sh sanitize` (trap) in the duplicate:
   verdict line, per-set totals, and each canary's measured
   exit behaviour. Then prove liveness yourself: build each
   canary with and without the flags the file spells and
   confirm the deliberate UB is really UB (traps/reports
   only when instrumented; the stated trap boundary canary
   behaves as documented).
2. Flavour machinery by reading + probes: SANFLAGS per
   flavour are what the inventory prints; `MSF_SANITIZE`
   with a non-sanitize budget is refused (run it);
   a bogus flavour is refused; `MSF_SANITIZE=full` on this
   host SKIPs-BY-NAME with no PASS and no findings claimed
   (run it, quote the lines); explicit `MSF_SANITIZE=trap`
   with the sanitize budget works (run it).
3. Non-perturbation: `standard` PASS in the duplicate with
   totals 411,213 + 1,117,504 and every control refused;
   the sanitized builds never touch the compiler probe or
   ARM objects (read the build seams).
4. CI sanitize job by reading: runs the flavour it claims
   on the OS it claims; a SKIP there cannot look like the
   PASS line the job exists to produce.
5. AGENTS.md / usage text name the budget and its cost
   truthfully against your measured run.

**Outputs:** `scratch/verifier-w6sanitize/report.md` +
`ledger/verifier-w6sanitize.md`. Structured
complete/evidence/unresolved mandatory. Script files, Git
Bash, MSF_PYTHON pinned to workspace .venv, memory modest.
~360 min.
