**Role:** verifier-w4trig (ParcelRound verifier, SF-1 Step 2c kernel)

**Stance:** disconfirm only. This is the project's strongest
claim so far (correct rounding); verify it like one. Findings
one per line, (a) regression / claim-surface deviation or
(b) wrong answer. The parcel's decider, generator, and error
budget are suspects, not oracles: a wrong decider that agrees
with a wrong kernel is the failure this brief is priced to catch.

**Copy:** `worktrees/verify4-trig` (detached HEAD, parent
`a4f6fb9`). Never consult the parcel branch/worktree, other
worktrees, keys, `scratch/lead/`, `scratch/parcel-w4trig/`,
`scratch/tier2-trig-spike/` outputs as authority (the spike
*report* may be read as a governing text), or `ledger/lead.md`.
Clean room: nothing with `cft` in its name, ever; no IEEE PDF;
CORE-MATH per Step 0b fences (executables + mechanical `.wc`
input parsing from the pinned scratch tree only; MPFR
re-decides; `cr_cospif` directed modes decide nothing; no
implementation/constants read). Never modify the copy/commit.
No board flashing (compile checks only).

**Subject:** six rows `msf{16,32,64}_sin_pi/_cos_pi`, C-754,
all modes. Governing: brief `ledger/briefs/w4-trigkernel.md`,
design/checkpoints `ledger/parcel-w4trig.md`, SF-1 Sections
6/8/14, spike Sections 2-6. Lead-settled leg-(c) authority
(published worst-case completeness + measured 58.58) is not
yours to relitigate - but whether the *implementation's*
stages actually decide every gate input inside that argument
absolutely is.

**Required probes (counts each; skips named):**
1. Source audit, line by line: reduction exactness (all
   magnitudes incl. subnormals and huge integers), settled
   zero-sign cells, quadrant/sign algebra, delta branch,
   interval-pack agreement rule incl. flags, stage-final
   fallback, NaN matrix reuse, inexact/underflow judgement.
   Re-derive the Ek claim independently far enough to judge
   it (your own script over the evaluation order; compare
   exponents against the generated header; a too-narrow Ek is
   a (b) even if every replay passes).
2. Constants: parse `src/msf_trig_tables.h` and verify every
   entry is the exact 384-bit floor of its named constant by
   your own exact-rational computation; regenerate via
   `tools/gen_trig_tables.py` to temp and byte-compare.
3. Independent decider: fresh code (MPFR by the proven recipe
   and/or mpmath >=200-bit, your own narrowing) - never the
   parcel's harness logic. Cross-decide: all committed
   specials in all modes; seeded samples per format/function
   incl. near-integer/half/quarter and saturation strata;
   the hardest published inputs you parse. Only after the
   parcel harness's decider agrees with yours on stated
   samples may you use it as an execution vehicle below.
4. Gate reruns on the copy: binary16 exhaustive (own or
   audited decider, all finite/modes); binary64 100% of
   published worst-case inputs; binary64 seeded >= 2^20 per
   function; binary32 at least two full exhaustive shards
   (one low-magnitude, one high-magnitude; state which) plus
   seeded strata - a full 32-shard rerun is not required, its
   absence must be named; forced-stage samples at stages 2/3;
   escalation counters read (final-undecided must be 0).
5. Regeneration byte-identity: table generator (4 table
   outputs), trig table header, committed trig vectors;
   committed vectors replayed in smoke; `smoke` + `standard`
   PASS in the copy (script files, Git Bash, MSF_PYTHON
   pinned); firmware targets compile (no flash).
6. Negative controls of your own: dropped table limb /
   narrowed Ek must fail a hardest gate; one sign/quadrant
   corruption; one directed-neighbour corruption - each
   watched failing with an unmutated pass beside it.
7. Claim surface vs parent: brief-owned files only; 6 rows
   wave 4, none partial; run.sh/CMake touches limited to the
   brief's lines; ceiling; no KissFFT/compat/board-program
   changes smuggled in.

**Outputs:** `scratch/verifier-w4trig/report.md` (first line
`READY` or `NOT READY`; findings with smallest failing
input/mode; every count; decider-independence route stated;
not-done list incl. any f32 shards not rerun) and
`ledger/verifier-w4trig.md`. Structured
complete/evidence/unresolved. Times are records only.
