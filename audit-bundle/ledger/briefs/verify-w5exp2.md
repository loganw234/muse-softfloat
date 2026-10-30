**Role:** verifier-w5exp2 (ParcelRound verifier, SF-2 Step 3a)

**Stance:** disconfirm only. Findings (a) regression,
(b) wrong answer. Claim language: correct rounding or
it does not ship.

**Copy:** `worktrees/verify5-exp2` (detached HEAD, parent
`a0acf2a`). Never consult the parcel branch/worktree,
other worktrees, keys, `scratch/lead/`,
`scratch/parcel-w5exp2/`, or `ledger/lead.md`. Governing:
this brief, the copy's `docs/studies/SF-2.md`, the parcel
ledger, `scratch/sf2-explog/report.md` (read in full).
Clean room: nothing with `cft` in its name, ever; MPFR
is your decider; worst-case input files may be fetched
to your scratch (record hashes) or reused from the
spike's pinned tree under `scratch/oracles` by execution
only. Never modify the copy. No board flashing (the
genuine board is busy with a demo run; board.lock is not
yours). Moderate load: your own decider legs sequential,
memory ceilings.

**Required probes (counts each; skips named):**
1. Correctness, independently decided: binary16
   exhaustive vs your MPFR decider (both functions, 5
   modes); binary32 sampled shards (state coverage
   fraction honestly - full exhaustion is the parcel's
   claim, your job is sampled falsification + the shard
   arithmetic in its logs re-added by you from the
   report); binary64 100% of the published worst-case
   inputs for both functions if fetchable, else the
   largest named fraction + seeded volume. Any
   final-undecided anywhere is a (b).
2. Ek re-derivation: rerun the table generator in
   scratch and byte-compare `src/msf_explog_tables.h`;
   the Ek integers re-derived from the generator's own
   output (a narrowed bound that only regeneration
   catches is still a finding); stage reach vs the
   spike-measured margins restated from the study.
3. Cuts and ties: every exact exponent cut probed at
   boundary-1/boundary/boundary+1 per format incl. the
   -1075 tie and exp2m1(-54); saturation cell; specials
   table (inf not invalid, exp2m1(-inf) = -1, signed
   zeros) flags-exact.
4. Seam census (57 registered / 51 implemented / log2
   pair planned; closed claim set; flags column true),
   regeneration byte-stable, `smoke` + `standard` PASS,
   target-compile at -Os AND -O3, claim surface vs
   parent.

**Outputs:** `scratch/verifier-w5exp2/report.md` (first
line READY/NOT READY; per-leg counts incl. your shard
fraction; findings with smallest repro; not-done) and
`ledger/verifier-w5exp2.md`. Structured
complete/evidence/unresolved. Times are records only.
