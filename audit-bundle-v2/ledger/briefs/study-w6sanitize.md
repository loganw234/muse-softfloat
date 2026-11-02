**Role:** study-w6sanitize (surveyor, Wave 6 queue item 3 feasibility)

**Job:** determine how an ASan/UBSan pass over the host runners
can actually run, and run as much of it as this host allows in
scratch. Read-only on the repo (`muse-softfloat/` at `50aac59`);
all builds under `scratch/study-w6sanitize/` in a copied tree,
never in the repo.

Probes: (1) which compilers here support
`-fsanitize=address,undefined` end-to-end (compile AND run a
canary with a deliberate heap overflow and a deliberate UB,
both must be caught): mingw64 gcc, clang if present, others on
PATH - version strings recorded; (2) how tools/run.sh builds
its runners - the exact flag injection point for a sanitizer
variant that does not weaken the gate (env override shape);
(3) if a compiler passes the canaries, build the library +
vector runner sanitized and run the committed vector set (or
the largest stated subset that finishes in your box), report
every sanitizer finding verbatim or the clean total; any real
finding gets a minimal repro input. (4) Recommend the parcel
shape: host script, CI job (needs parcel-w6ci), or both, with
costs measured.

**Outputs:** `scratch/study-w6sanitize/report.md` +
`ledger/study-w6sanitize.md`. Structured
complete/evidence/unresolved mandatory. Script files, Git Bash,
MSF_PYTHON pinned to workspace .venv, explicit memory ceiling
(sanitizer builds are hungry - stay under ~4 GB or stop and
report). Nothing with `cft` in its name. ~240 min.
