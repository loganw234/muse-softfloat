NOT READY

# verifier-w4trig report — Wave 4 Step 2c sinPi/cosPi (6 rows)

Copy: `worktrees/verify4-trig` @ `0bfd726` (detached HEAD, parent
`a4f6fb9`), verified clean at open and close (no writes to the copy;
all probe outputs under `scratch/verifier-w4trig/`).

Decider-independence route: fresh two-precision mpmath decider of my
own (`scratch/verifier-w4trig/mydecider.py`: exact Fraction decode,
own settled-specials restatement, exact nearest-integer reduction,
mpmath 130/170-digit pairs with escalation to 350/400 and 800/900,
first-principles 4-mode rounding, per-mode tiny-after-rounding
underflow, strict-interiority clearance, refusal on any doubt) vs the
parcel harness MPFR decider (`tests/trig_exhaustive.c`, audited line
by line, used afterwards only as an execution vehicle). Cross-decision
set (`tmp/xdec.in`, 19,297 inputs, own RNG seed 999): all committed
specials (zeros/infs/NaN payloads, small+large integers/half-integers
per format), 3,000 seeded inputs per format/function with
near-integer/half/quarter bounce and tiny strata, my own mechanical
`.wc` parse + margin rank (top-50 + 500 random per function).
Result: 18,494/18,494 agree, 0 disagreements; my 803 undecided are all
f64 cosPi deep-saturation (delta below my route's reach), the parcel
harness decides all 19,297 (1 banner line, 0 undecided). Saturation
path validated separately: 5 hand-derived exact-inequality cases
(f64 cos 2^-1074, 2^-1022, 2^-28; f32 cos 2^-149; f16 cos 2^-24)
match the harness decide output bit-for-bit.

## Findings (one per line)

(a) BUILD: the copy does not compile under its own flags. `tools/run.sh`
`CFLAGS=-std=c11 -O2 -Wall -Wextra -Werror` (host) and the board
`target_compile_options(... -Wall -Wextra -Werror)` both fail on
`src/msf_math.c:589`: `r_neg` set but never used
(`-Werror=unused-but-set-variable`). Evidenced with the exact run.sh
host command line (log `log_werror_build.txt`) and the board
CMake+Ninja build (`log_fwbuild.txt`; keep-going `-k 0` shows this is
the SOLE failure, `probe_fwk0.sh`). Consequence: `tools/run.sh smoke`
and `standard` cannot pass in the copy; all 5 firmware targets are
unlinked (all other TUs compile; type scan clean; ARM symbol scan of
available objects shows no refused helpers). The variable is the
smoking gun for finding (b1): the author computed `r_neg` and forgot
to apply it. The sign-fixed diagnostic build (scratch only) compiles
clean under `-Werror` host AND `-mcpu=cortex-m0plus` ARM, proving the
fix direction.

(b1) WRONG SIGN, sinPi, all formats, all modes, every kernel-path input
with negative reduction remainder. `trig_core` uses
`result_sign = d.sign ^ parity` for sin, missing `^ r_neg`
(`r_neg` = remainder `r<0`, i.e. `frac(|x|)` in (1/2,1) mod 1):
`sinPi(x)=sgn(x)*(-1)^n*sin(pi*r)` with `sin(pi*r)=-M` for `r<0`
(`M>0` the folded kernel value), so the delivered sign is exactly
negated. Smallest failing input: f16 `0x3801` (+0.50048828125), any
mode, e.g. te: kernel `-1` (`0xbc00`) vs correct `+1` (`0x3c00`).
Scope (all mechanically classified, 100% attributed): f16 exhaustive
40,960/507,904 checks (10,240 inputs x4); f64 worst-case sinPi set
34,104 lines over 8,525 unique inputs (all class rneg, all exact
negation pattern `got[rm]==flip(want[mirror(rm)])`, 0 non-conforming);
f64 seeded 2^20/function 53,676 lines (~13.4k inputs, pattern as
printed; full-set proof pending signfix-seed rerun); committed vectors
5,120 lines. No other defect fires anywhere in these gates: every
non-sign check passes (f16: 462,848/462,848; signfix f16: 507,904/507,904
PASS; signfix trig vectors: 43,491/43,492, the 1 line being (b3)).

(b2) WRONG ZERO SIGN, cosPi at negative half-integers, all modes.
`trig_core` half-integer branch passes `d.sign` for cosPi, delivering
`-0`; the settled cell B (design entry, corroborated by MPFR and the
Step 0b executable, and by the copy's own committed vectors which
expect `+0`) requires `+0` in every mode. The code contradicts its own
comment (`cosPi = +0 in every mode`). Smallest failing input: f16
`0xb800` (-0.5), any mode: kernel `0x8000` vs correct `0x0000`
(directly probed, all 3 formats x4 modes). Scope: f16 4,096 checks
(1,024 inputs x4); f64 worst-case cosPi set 4 lines (1 input,
`0xc320000000000001` = -2251799813685248.5, x4); committed vectors 516
lines. With (b1), this fully explains all 45,056 f16 mismatches
(predicted 45,056 = observed 45,056, exact) and all 34,108 worst-case
mismatches.

(b3) TOO-NARROW STAGE-1 Ek. Committed header
`MSF_TRIG_EK_EXP = {200, 242, 370}` claims stage-1 relative error
`<= 2^-200`. My independent re-derivation of the scalar recurrence
(`check_ek.py`, own code over the evaluation order: table quantum,
u/u^2 rounding, Horner with rho_k amplification, Taylor tails,
delta branch) gives proven bounds 2^-155/2^-251/2^-379 (bound bits
155/251/379; code needs exponent <= bound-9). Stages 2-3 (242/370)
are exactly at the margin and sound; stage 1 needs `<= 146` (the
committed generator itself prints 146). A 54-bit-too-narrow stage-1
interval is unsound (endpoints can agree while the true value rounds
otherwise): a (b) even though no replay misfires on it (all gates'
non-sign checks pass, including 3 full f32 shards + f64seed on the
signfix build). The design entry and parcel checkpoint both state the
code uses 146/242/370; the header does not match its own design.

(a) REGENERATION: `tools/gen_trig_tables.py` does NOT reproduce
`src/msf_trig_tables.h` (two regions + comment skew):
line 21 EK (`200` vs regenerated `146`), and all 39 `MSF_TRIG_SIN_C`
entries shifted one factorial: the generator emits
`floor(1/(2k+3)!)` (its own `[0]` = 0xAAAA... = 1/6) while labeling
it `1/1!`; the header correctly holds `1/(2k+1)!`. Running the
committed generator would silently corrupt the sin kernel (Horner
constant 1/6 instead of 1). COS table, pi, NTERMS (21/29/39) and tails
regenerate identically; the mismatch is exactly EK line + 39 sin rows.
Separately verified by own exact computation: all 80 header entries
are the exact 384-bit floors of the correct constants
(`check_floors.py`: exact `Fraction(1,k!)` + pi at dps 300/240 with
+-2^-590 bracket stability; 80/80 exact, all normalized).

(a) STALE COMMITTED VECTOR: `tests/vectors/trig-f64.vec:3`
`msf64_sin_pi te 0 -> 0 10` expects inexact for `sinPi(+0)`; correct
is `00` (exact). Regeneration produces `00` (and the generator's
SPECIAL-DISAGREE cross-check passes), so the committed line cannot
have come from the committed generator+decider. Kernel is correct
here (returns +0/00). This plus (b1)/(b2) fully explains the smoke
vector replay: 140,805/146,442 pass, 5,637 fail = 5,120 (b1) + 516
(b2) + 1 (this line), 0 unattributed (every FAIL line classified).

(a) BUILD (consequence): `tools/run.sh smoke`/`standard` and all 5
firmware targets FAIL at compile (same `r_neg` root cause); unit
tests PASS when built without `-Werror` (vehicle); full committed
vector replay FAILs exactly per the cells above. The copy's gate
claims (f16 0 mismatches, worst-case 0 mismatches, smoke/standard
PASS, firmware 447/447) are disconfirmed as stated for this copy.

## Gate counts (copy; audited MPFR vehicle unless noted)

- f16 exhaustive (own-classifier + harness): 507,904 checked,
  45,056 mismatches (all sign cells, exact prediction), 0 undecided,
  0 audits failing, stage hits 376,832/0/0, final_undecided=0 -> FAIL.
- Signfix diagnostic f16: 507,904 checked, 0 mismatches -> PASS
  (bounds the defect set to the two sign cells).
- f64 worst-case 100%: sinPi 297,084 checks (74,271 tokens x4;
  dump set == my mechanical parse set, symdiff 0), 34,104 mismatch
  lines (8,525 unique, all rneg negation pattern), specials 533,
  escalations 0, final_undecided=0 -> FAIL.
  cosPi 206,232 checks (51,558 x4), 4 mismatches (1 neg-half input
  x4), specials 1,030, escalations 24, final_undecided=0 -> FAIL.
- f64 seeded 2^20/function (seed 777): 8,388,608 checked, 53,676
  mismatch lines, 0 undecided, 998,882 specials, final_undecided=0
  -> FAIL. Full-set attribution complete: signfix rerun of the same
  seed (below) gives 0 mismatches, so every one of the 53,676 lines
  is the sin r_neg sign defect (spot pattern confirmed on printed
  lines; the only code delta is the two sign lines).
- f32 shards on copy: shard 0 (low, [0,67108864), subnormal/zero
  region): 1,073,741,824 checked (2^30, full), 0 mismatches,
  67,108,863 decider escalations (saturation caution, all resolved),
  134 audits 0 fail, final_undecided=0 -> PASS (50m47s).
  Shard 31 (high, [2080374784,2147483648)): 939,524,096 checked
  (full finite range), 0 mismatches, 234,881,024 specials
  (all-huge-integer region) -> PASS.
- f32 shards on signfix (diagnostic): 0, 16 ([1073741824,1140850688),
  middle kernel-heavy), 31: running. f64seed signfix: running.
- Forced stages (copy, wc sin): FORCE_START=1 hits 0/294952/0,
  FORCE_START=2 hits 0/0/294952, same 34,104 sign mismatches,
  final_undecided=0 both -> escalation mechanics work; Ziv path
  stage-independent of the sign defect.
- Table/header/vector regen: gen_tables 4/4 byte-identical;
  trig vectors f16/f32 identical, f64 1-line drift (b3-vector above);
  trig header NOT byte-identical (EK + 39 sin rows, above).
- smoke components (scratch replication): unit PASS; full VECS
  140,805/146,442 (fails per cells above); type scan clean; ARM
  symbol scan clean for built objects (msf_math.o unbuildable);
  copied P0 controls c1/c3/c7 all refused (vehicle validated).
- Firmware: configure ok; build FAILs solely on `r_neg`
  (keep-going: exactly 1 failing TU); signfix msf_math.c compiles
  clean under board ARM flags.

## Claim surface vs parent a4f6fb9

16 files, +45,768/-21. run.sh: SRC+VECS lines only. board/CMakeLists:
+1 core source line. implemented.tsv +6 rows wave 4; COVERAGE 6 rows
planned->implemented; header/dispatch generated updates consistent
(+metrics briefs.jsonl row). New: msf_math.c (702), trig tables (114),
gen_trig_tables.py (235), gen_vectors_trig.py (351),
trig_exhaustive.c (827) = 2,115 hand-written <= 4,500 ceiling
(generated tables/vectors excluded per brief). 6 rows wave 4, none
partial. No KissFFT/compat/board-program changes. No board flashing.

## Diagnostic signfix reruns (scratch sources only, two sign lines)

- f64 worst-case sinPi: 297,084 checked, 0 mismatches -> PASS.
- f64 worst-case cosPi: 206,232 checked, 0 mismatches -> PASS.
  (Proves the defect set on the hardest gates is exactly the two
  sign cells; magnitudes/intervals/pack/flags otherwise bit-exact.)
- f32 full shard 0: 1,073,741,824 checked, 0 mismatches -> PASS.
- f32 full shard 16 (middle kernel-heavy [1073741824,1140850688),
  |x| in [2,4)): 1,073,741,824 checked, 0 mismatches, 4,080
  specials, 134 audits 0 fail, final_undecided=0 -> PASS.
- f32 full shard 31: 939,524,096 checked, 0 mismatches -> PASS.
- f64seed 2^20 seed 777 rerun: 8,388,608 checked, 0 mismatches,
  0 undecided -> PASS.
  (Two full f32 shards low+high on the signfix build plus a middle
  kernel-heavy shard, and the seed rerun, all clean: no Ek-200
  misfire observed anywhere; the (b3) finding stands on the
  derivation, not on a replay.)

## Not done

- Full f32 exhaustive beyond shards 0/31 on the copy: 30 shards
  outstanding by design (brief requires two; ~50 min/shard).
- Board sampled replay: not run (no board lock; compile only per brief).
- run.sh smoke/standard as literally prescribed: blocked at
  build_host by finding (a); components replicated from scratch instead.
- `standard` pack-sweep generation: not run (same blocker; the f16
  exhaustive gate supersedes it for this parcel).
- Full f32 exhaustive beyond shards 0/31 (copy) not rerun: 30 shards
  outstanding by design (brief requires two; wall ~50 min/shard).
- Board sampled replay: not run (no board lock; compile only per brief).
- run.sh smoke/standard as literally prescribed: blocked at
  build_host by finding (a); components replicated from scratch instead.
- `standard` pack-sweep generation: not run (same blocker; trig-exhaustive
  f16 gate supersedes it for this parcel).
- Matters explicitly not relitigated: lead-settled leg-(c) authority
  (published completeness + 58.58); IEEE text (fences held: no cft
  names opened/searched/listed, no PDF, CORE-MATH contact =
  executables + mechanical .wc parse only, MPFR re-decided
  everything, directed cr_cospif never consulted).

Times are records only (host under load).
