**Role:** verifier-w5alg2 (ParcelRound verifier, SF-2 Step 2b)

**Stance:** disconfirm only. Findings (a) regression,
(b) wrong answer.

**Copy:** `worktrees/verify5-alg2` (detached HEAD, parent
`0f08aa3`). Never consult the parcel branch/worktree,
other worktrees, keys, `scratch/lead/`,
`scratch/parcel-w5alg2/`, or `ledger/lead.md`. Governing:
this brief, the copy's `docs/studies/SF-2.md`, the parcel
ledger (incl. its jam-equivalence addendum - adjudicate
it, do not take it on trust), `scratch/sf2-algebraic/
report.md` Secs. 3.2/5.2/6. Clean room: nothing with `cft`
in its name, ever; MPFR/CORE-MATH executed oracles only.
Never modify the copy. No board flashing.

**Required probes (counts each; skips named):**
1. Own exact decider (independent integer arithmetic) vs
   the kernel: binary16 pool sweep + sampled volume,
   f32/f64 directed+seeded, counts printed. The
   floor-sum lemma and anchored-window bounds re-derived
   on paper; the sticky assembly (tail, parity, remainder)
   audited arm by arm - a dropped component is a (b) even
   if your sample happens to pass.
2. The jam question adjudicated independently: decide
   for yourself whether the shipped floor form and the
   `MSF_ALG_TEST_JAM` form can ever diverge (construct
   or exhaust the search you need at binary16; reasons,
   not vibes). The parcel shipped floor; your job is
   whether floor is *right*, tie families included.
3. Specials in evaluation order, whole table, both
   operand orders: sNaN first, inf-over-qNaN, (±0,±0)
   sign, payloads. Flags exact.
4. Ties: the committed tie families replayed; te vs ta
   must differ exactly on true ties (count them);
   subnormal-output cases with counts.
5. Seam census (Tier 2 45/45, parity across formats -
   a format missing implemented status is a finding),
   regeneration byte-stable, `smoke` + `standard` PASS,
   target-compile, claim surface vs parent.

**Outputs:** `scratch/verifier-w5alg2/report.md` (first
line READY/NOT READY; counts; findings with smallest
repro; your jam adjudication; not-done) and
`ledger/verifier-w5alg2.md`. Structured
complete/evidence/unresolved. Script files (Git Bash,
MSF_PYTHON pinned, memory ceilings). Times are records.
