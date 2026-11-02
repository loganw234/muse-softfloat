**Role:** verifier-w5alg1 (ParcelRound verifier, SF-2 Step 2a)

**Stance:** disconfirm only. Findings (a) regression,
(b) wrong answer.

**Copy:** `worktrees/verify5-alg1` (detached HEAD, parent
`7c3819c`). Never consult the parcel branch/worktree,
other worktrees, keys, `scratch/lead/`,
`scratch/parcel-w5alg1/`, or `ledger/lead.md`. Governing:
this brief, the copy's `docs/studies/SF-2.md`, the parcel
ledger, `scratch/sf2-algebraic/report.md` (read in full).
Clean room: nothing with `cft` in its name, ever; MPFR/
CORE-MATH executed oracles only. Never modify the
copy/commit. No board flashing.

**Required probes (counts each; skips named):**
1. Kernel exactness, independently: your own exact
   decider (integer arithmetic, from the study's
   definition - not the copy's generator) vs the copy's
   `msf_alg.c` through the runner: binary16 exhaustive
   (65,536 x 5 modes, count printed), binary32/64
   directed + seeded volume with counts. The decision
   compare (`alg_cmp_sq`) and the bit-search bounds
   re-derived on paper against the study, not just
   replayed.
2. Specials: whole Clause 9.2.1 rSqrt table executed
   incl. both signed zeros (pole signs), -inf, negative
   finite, sNaN/qNaN payloads, flags exact. The -0 cell
   decided from the clause extracts, not MPFR.
3. Seam: operations/implemented/COVERAGE counts
   (Tier 2 45 registered / 42 implemented / hypot
   planned-only - a hypot row claiming implemented is a
   finding), claim tokens inside the closed set,
   `math_bin` dispatch traced, regeneration byte-stable,
   seam controls watched.
4. Generator integrity: regenerate committed alg sets
   twice (byte-identical + match committed); the exact
   decider's subnormal/smallest-normal boundary probed
   against your own arithmetic; cross-decide a sample
   with MPFR (Step 0b recipes).
5. Gates: `smoke` + `standard` PASS in the copy (script
   files, Git Bash, MSF_PYTHON pinned); target-compile
   of `msf_alg.c` clean; type scan clean; claim surface
   vs parent exactly the brief-owned files (the board
   wiring escalation is lead work, not a parcel defect).

**Outputs:** `scratch/verifier-w5alg1/report.md` (first
line READY/NOT READY; per-format counts incl. your
exhaustive total; findings with smallest repro; not-done
list) and `ledger/verifier-w5alg1.md`. Structured
complete/evidence/unresolved. Times are records only.
Explicit memory ceilings on any long sweep.
