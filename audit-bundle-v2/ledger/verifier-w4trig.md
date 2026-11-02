# verifier-w4trig record (ParcelRound verifier, SF-1 Step 2c kernel)

Role: verifier-w4trig. Stance: disconfirm. Copy: `worktrees/verify4-trig`
@ `0bfd726` (detached HEAD, parent `a4f6fb9`), clean at open and close;
never modified (all probe outputs under `scratch/verifier-w4trig/`).
Governing texts read: `ledger/briefs/verify-w4trig.md` (obeyed exactly),
`ledger/briefs/w4-trigkernel.md`, `ledger/parcel-w4trig.md` design +
checkpoints, spike `scratch/tier2-trig-spike/report.md` Sections 2-6,
SF-1 Sections 6/8/14. Fences held: nothing with `cft` in its name
opened/searched/listed; IEEE PDF not opened; CORE-MATH contact =
executables + mechanical `.wc` parse from the pinned
`scratch/oracles` tree only; MPFR re-decided everything; directed
`cr_cospif` never consulted; no implementation/constants read; no board
flashing (compile checks only). Full evidence: `scratch/verifier-w4trig/report.md`
(first line NOT READY) with per-probe scripts and logs.

Verdict: NOT READY. Six findings, each evidenced with the smallest
failing input and mode:

- (a) BUILD: copy fails its own `-Wall -Wextra -Werror` host and board
  builds: `src/msf_math.c:589` `r_neg` set but never used. Exact run.sh
  host command fails; board CMake+Ninja fails with this as the SOLE
  error (keep-going `-k 0`); `run.sh smoke`/`standard` and all 5
  firmware targets therefore cannot pass.
- (b1) sinPi sign negated for every kernel-path input with negative
  reduction remainder (`frac(|x|)` in (1/2,1) mod 1), all formats and
  modes: `result_sign = d.sign ^ parity` misses `^ r_neg` (the computed
  variable is the smoking gun). Smallest: f16 `0x3801` any mode
  (te: `-1` vs `+1`). f16: 40,960 checks; f64 worst-case: 34,104 lines
  / 8,525 unique inputs, all exact-negation pattern, 0 non-conforming;
  f64 seed 2^20: 53,676 lines; committed vectors: 5,120 lines.
- (b2) cosPi at negative half-integers gives `-0`, settled cell B
  requires `+0` all modes (code contradicts its own comment and its
  own committed vectors). Smallest: f16 `0xb800` any mode. f16: 4,096
  checks; f64 worst-case: 4 lines (input `0xc320000000000001`); vectors:
  516 lines. (b1)+(b2) explain 100% of mismatches (f16 predicted
  45,056 = observed 45,056).
- (b3) Stage-1 Ek too narrow: header claims 2^-200; own re-derivation
  (scalar recurrence over the evaluation order) proves 2^-155, so code
  needs exponent <=146 (generator and design entry agree: 146/242/370).
  Unsound interval even though no replay misfires on it.
- (a) `tools/gen_trig_tables.py` does not regenerate the header: EK
  line plus all 39 sin rows shifted one factorial (emits
  `floor(1/(2k+3)!)` labeled `1/1!`; header correctly holds
  `1/(2k+1)!`). Running it would corrupt the sin kernel. Header
  constants themselves verified exact 384-bit floors (80/80, own exact
  computation).
- (a) One stale committed vector: `trig-f64.vec:3` expects inexact for
  `sinPi(+0)` (correct: exact). Vector replay: 140,805/146,442 pass,
  5,637 fail = 5,120 + 516 + 1, zero unattributed.

Decider independence: own two-precision mpmath decider (own code,
own RNG seed 999, own `.wc` parse+rank) vs audited parcel MPFR
decider: 18,494/18,494 agree, 0 disagreements, across specials,
seeded strata, and hardest published inputs; saturation path
hand-verified on 5 exact-inequality cases. Parcel harness used as a
vehicle only after this agreement. Diagnostic: two-line signfix in
scratch sources clears everything (f16 507,904 PASS, worst-case
100% PASS both functions, 3 full f32 shards + f64seed PASS,
43,491/43,492 committed vectors), bounding the defect set.

Gate counts (copy): f16 exhaustive FAIL (45,056 sign); f64 worst-case
100% FAIL both functions (34,104 + 4, sign only; sets verified equal
to mechanical parse, symdiff 0); f64 seeded 2^20 FAIL (53,676, sign);
f32 shard 0 (low, full 2^30) PASS; shard 31 (high, full finite range)
PASS; forced stages hit 0/N/0 with final_undecided=0; escalation
counters clean; unit PASS (vehicle); type scan clean; symbol scan
clean for built objects; P0 controls c1/c3/c7 refused (vehicle
validated); table/vector regen as above; claim surface: 16 files,
run.sh 2 lines + CMake 1 line only, +6 rows wave 4, 2,115 <= 4,500
lines, no KissFFT/compat/board changes.

Not done: 30 remaining f32 shards (brief requires two: 0 low + 31
high, stated); board sampled replay (no lock); literal run.sh
budgets (blocked by the build finding; replicated from scratch);
pack-sweep generation (same blocker). Lead leg-(c) authority not
relitigated. Times are records only.
