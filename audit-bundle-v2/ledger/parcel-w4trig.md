
## 2026-10-27 19:08:05 -07:00 - Design entry: correctly rounded sinPi/cosPi, binary16/32/64 (6 rows, one bundle), written before any kernel code

Measured: brief ledger/briefs/w4-trigkernel.md read first and
obeyed; spike scratch/tier2-trig-spike/report.md Sections 2-6
read in full as a proposal to re-derive (done below, with one
width change); worktrees/w4-trig verified on branch wave4-trig
at base a4f6fb9, clean. Declarations verified:
msf{16,32,64}_sin_pi / _cos_pi, signature (a, msf_rounding_t,
msf_flags_t *), sig class math_un, tier 2, wave 4, C-754,
planned in docs/COVERAGE.tsv. Shared helpers read and judged
sufficient (no lead-owned file needs an edit): msf_decode /
msf_nan_delivery (src/msf_decode.h), msf_pack_generic +
per-format packs (src/msf_roundpack.c, interface in
src/msf_internal.h: magnitude (sig+f)*2^exp2 over a 128-bit
sig plus sticky, tininess after rounding judged inside the
pack), msf_u128 helpers (src/msf_wide.c). Fences held: nothing
with cft in its name opened/searched/listed; IEEE PDF not
opened (S1 paraphrase scratch/S1/report.md, SF-0/SF-1, and the
Clause 9 survey scratch/tier2-clause9/report.md Section 4.6
only); CORE-MATH contact limited to executing the Step 0b
binary64 objects (one settlement measurement below) and,
later, mechanical .wc input parsing with MPFR re-deciding
every value; cr_cospif directed modes decide nothing here.
No code written yet; this entry is the design gate.

### 1. Specials second-read (Clause 9.2.1 for sinPi/cosPi, my own words)

Homogeneous formats, canonical results, rounding attribute
applies. NaN delivery is the SF-0 2.5 matrix unchanged via
msf_nan_delivery(dfmt=fmt, ops=[decoded], n=1,
invalid_without_nan = is_infinity): a signaling NaN input
signals invalid and delivers that operand quieted; a quiet
NaN input delivers itself, no flag; an infinite input is the
only invalid-without-NaN case and delivers the default quiet
NaN plus invalid. sinPi/cosPi are not among the 9.2.1
NaN-exception families (hypot/pow class, survey 4.6.1), so
wholesale matrix reuse is legitimate; infinity never results.
Finite table (n an integer value representable in the format;
all sufficiently large finite inputs are integers):

| input x            | sinPi(x)              | cosPi(x) | flags |
|---|---|---|---|
| +-0                | +-0, sign of x        | 1        | none (exact) |
| integer n          | +-0, SIGN OF X [cell A] | (-1)^n | none (exact) |
| half-integer n+1/2 | +/-1 by reduction signs: sinPi sign = sgn(x)*(-1)^n*sgn(r), r = x - n nearest-integer remainder | +0 IN ALL MODES [cell B] | none (exact) |
| other finite       | correctly rounded kernel value | same | inexact always; underflow iff the pack judges the rounded result tiny (after rounding) and inexact; never overflow, never divideByZero |

|result| <= 1 always, so overflow is impossible. Underflow
is judged by the shared pack on the wide value only (exact
tiny test inside msf_pack_generic per Clause 7.5 as shipped);
inexact is signalled exactly when the delivered value differs
from the exact result, which outside the exact branches is
always (Niven argument in Section 5 of the spike, re-carried:
a dyadic non-{integer,half-integer} input has irrational
sinPi/cosPi, since rational values of sin/cos at rational
multiples of pi lie in {0,+-1/2,+-1} and +-1/2 needs
non-dyadic |r| = 1/6-class arguments).

The two flagged cells, settled and how: the S1 paraphrase and
SF-0 do not pin these two cells textually (S1 Section on
Clause 6.3 gives only the general exact-zero-sum rule:
positive except under roundTowardNegative; survey 4.6.1 says
9.2.1 tabulates zeros with signs per function). Settlement
therefore used three agreeing routes, all measured today:
(i) mathematical symmetry as the 9.2.1 table is structured by
it - sinPi is odd and its integer zeros are the +-0 row
continued, giving sign-of-x; cosPi is even and its
half-integer zeros take the unsigned (+0) entry; (ii) MPFR
4.2.2 measured behaviour (scratch/parcel-w4trig/
zero_sign_probe.c, out/zero_sign.log): mpfr_sinpi(-1) =
mpfr_sinpi(-3) = -0 in RNDN/RNDZ/RNDU/RNDD all, and
mpfr_cospi(+-0.5, +-1.5, +-2.5) = +0 in all four modes
including RNDD - i.e. both cells deviate from the 6.3 default
in exactly the believed direction, which is only possible if
9.2.1 specifies them per function; (iii) executable-only
execution of the pinned Step 0b binary64 objects under
fesetround (cm_zero_probe.c, out/cm_zero.log): identical bits
in all four modes (sinpi(-3) = 8000000000000000, cospi(2.5) =
0000000000000000 under FE_DOWNWARD and FE_UPWARD alike; the
run also cross-confirms the sinPi half-integer +-1 signs my
reduction formula gives, e.g. sinPi(-1.5) = +1). Cell A =
sinPi at a negative integer delivers -0 (sign of x) in every
mode. Cell B = cosPi at any half-integer delivers +0 in every
mode. Both cells are pinned as explicit special-case code in
the kernel, as explicit expected values in the vector
generator (not inherited from any oracle), and as directed
vectors in all four modes; MPFR agreeing is recorded as
corroboration, never as the decider for these cells.

### 2. Error budget re-derived (script-computed)

Reduction (re-derived, integer-exact): decode a = |x| =
sig*2^exp (sig < 2^53). Split a = I + f by shifts; nearest-
integer form n, r with |r| <= 1/2; sinPi(x) = sgn(x)*(-1)^n *
sinPi(r), cosPi(x) = (-1)^n * cosPi(r). Fold t = |r| to
[0, 1/4] by t' = 1/2 - t with sin/cos swapped. Exact branches
r = 0 and t = 1/2 leave before any approximation. The kernel
sees only t in [0, 1/4] (exact dyadic, <= 54 significant
bits), u = pi*t in [0, pi/4], z = u^2.

Kernel arithmetic (my choice, one change from the spike):
positive wide floats only (every kernel quantity is >= 0 on
this range), W-bit normalized significands over 32-bit limbs,
and rigorous INTERVALS [lo, hi] with outward rounding at
every operation, instead of a scalar approximation plus an
Ek fudge. Containment is therefore per-operation (mul:
[down(lo*lo), up(hi*hi)]; sub a-b: [down(a_lo-b_hi),
up(a_hi-b_lo)]); the realised interval half-width in code is
>= the true error by construction at every width. The
derived Ek(W) below is the proven upper bound on that
half-width, which is what termination needs. Table entries
(pi and Taylor coefficients 1/(2k+1)!, 1/(2k)!) are stored
floored at the top width; at stage width W the coefficient
interval is [trunc_W(c), trunc_W(c) + 1 ulp_W], which
contains the true coefficient (table quantum accounted).
Horner runs from the smallest term: acc <- c_k - z*acc with
z*acc <= rho_k * c_k, rho_k <= z_max/((2k+2)(2k+3)) (sin),
so subtraction never cancels catastrophically. Cos-shaped
results are always evaluated as delta = 1 - cos(u) =
(z/2)*D(z), D from the shifted cos coefficients (d_k =
2/(2k+2)!), and 1 - delta is formed exactly at pack scale
(288-bit fixed-point integer subtraction, sticky preserved),
so directed decisions near +-1 rest on delta's relative
interval. Taylor tails are added as absolute widenings by a
power-of-two bound per stage/series.

Script: scratch/parcel-w4trig/error_budget.py (exact
Fractions, pi bounded by a rational ceiling, every stage of
the evaluation order: table quantum, pi interval, u
multiply, u^2 rounding, Horner accumulation with the rho_k
amplification, Taylor tails by first-neglected-term /
(1-ratio), delta-branch terms). Result: three stages
W in {160, 256, 384} (5/8/12 limbs; spike proposed 160/224 -
I take limb multiples with more slack, price named below),
term counts 21/29/39 per series for tails <= 2^-(W+24), and
relative full-width bounds Ek(160) <= 2^-155.2, Ek(256) <=
2^-251.2, Ek(384) <= 2^-379.2 (half-widths one bit smaller).
Stage 1 therefore decides any input whose genuine distance
to a rounding boundary exceeds 2^-154 relative, against the
measured complete-set f64 need of 2^-111.6 (spike Section 2,
58.58 extra bits by MPFR re-decision, leg-(c) authority per
lead decision 2026-10-27 18:53). Price of W=384 top width:
table is 80 entries x (12 limbs + exponent) ~= 4 KB rodata
(spike estimated ~1.3 KB at 224 bits); flash is measured from
the firmware build before close and reported, not assumed.

Interval pack: endpoints convert to the pack's (sig128,
exp2, sticky) grid exactly (top 128 bits + OR of the rest;
the destination round bit always lies inside those 128 bits
for these magnitudes, including subnormal results, since
the smallest nonzero |y| here is ~pi*2^-1074). Pack both
endpoints under the caller's attribute into scratch flags;
accept iff bits AND flags agree (monotonicity squeeze;
inexact asserted on kernel branches per the Niven argument,
underflow taken from the agreed pack judgement - endpoint
tininess disagreement is simply undecided and escalates).

### 3. Stage-final behaviour

Stages run 160 -> 256 -> 384. If the 384-bit interval still
straddles a boundary, the shipped code packs the lo endpoint
(defined, deterministic) and, in test builds, increments a
final-undecided counter. That path is unreachable under the
leg-(c) argument: it needs a genuine boundary distance under
2^-379 relative (~326 extra bits at f64) against the
published-completeness measurement of 58.58. Test-only
instrumentation (-DMSF_TRIG_TEST_COUNTERS, counters exported
from the TU only under that macro, plus -DMSF_TRIG_FORCE_START
to exercise later stages deliberately) must show ZERO
final-undecided hits across every gate set; any hit stops
the bundle as REFUSED, never a shrug.

### 4. Table generation

tools/gen_trig_tables.py generates src/msf_trig_tables.h
from first principles: pi and factorial reciprocals computed
with mpmath at 700-bit working precision, converted to exact
Fractions, floored to 384-bit limbs by exact rational floor
(no floating rounding anywhere in the pipeline), each entry
self-checked by exact interval containment (stored <= true <
stored + 1 ulp) at generation time; the generator also emits
the per-stage term-count and tail-bound constants from the
same bounds the budget script derives, and refuses if its
own containment checks fail. Regeneration must be
byte-identical (drift-checked like other generated files by
cmp in my gate scripts; run.sh drift list is lead-owned and
gets the addition at merge if the lead wants it there - my
scripts check it regardless). Dropped-low-limb truncation is
gate-visible: a mutant build with the low limb of every
table entry dropped (MSF_TRIG_DROP_LIMB test macro) must
fail the worst-case gate, watched.

### 5. Implementation shape and gates (plan)

New src/msf_math.c (one TU, all three formats, pure C11, no
allocation/recursion, fixed stack: a handful of 12-limb
values) + src/msf_trig_tables.h. Wiring I may touch:
tools/run.sh (SRC line + VECS line only), board/CMakeLists.txt
(core source line only). Owned: tools/gen_trig_tables.py,
tests/gen_vectors_trig.py, tests/vectors/trig-*.vec,
tests/trig_exhaustive.c (MPFR-decided differential harness,
shardable, test-counter readout), tables/implemented.tsv
(6 rows at wave 4 or none), regenerated outputs of
tools/gen_tables.py, tests/VECTORS.md tag rows.
Committed vectors: provenance family mpfr640-trig:* -
expected values decided by MPFR at 640-bit precision through
a C decider the generator drives (narrowing by the proven
Step 0b/spike recipe: check_range + subnormalize + zero
guard, flags computed from first principles in the
generator, never transcribed from MPFR flags; specials from
the table in Section 1 above, cross-checked against MPFR).
Gates, all counts printed, script files under Git Bash with
MSF_PYTHON pinned: directed vectors all modes (~36k lines:
specials incl. NaN payloads and both settled cells in all
modes, dyadic anchors, huge/tiny/subnormal, hardest-known
excerpts, bounce pairs, seeded class sweep); f16 exhaustive
differential (all 63,488 finite per function, all modes);
f64 100% of published worst-case inputs (mechanical parse of
the pinned scratch tree, MPFR re-decided) + seeded >= 2^21
per function; f32 EXHAUSTIVE finite differential, sharded by
input range with per-shard logs and a summed total (decider
may use exact odd/even symmetry and the Section 1 specials
to skip redundant MPFR evaluations, with raw-MPFR audits on
a stride sample and on every disagreement - the kernel side
is called on every finite encoding in every mode regardless);
forced-stage runs; negative controls (dropped table limb
fails worst-case gate, quadrant sign flip, delta-branch sign
error, directed neighbour wrong side, non-integer reduction
input); smoke + standard PASS; firmware targets compile via
the board CMake build only (no flashing); inventory Tier 2
prints 39 implemented of 39. Ledger checkpoints at the f16
gate, the worst-case gate, and f32 exhaustive completion.
If any format gate cannot close, the bundle returns REFUSED
whole with the smallest failing evidence.

Believed: stage 1 (160-bit) decides every gate input except
possibly a handful of engineered ones; stages 2-3 exist for
the termination argument and will be exercised by forced
starts rather than by natural hits.
For: lead

## 2026-10-27 19:21:16 -07:00 - Checkpoint: binary16 gate green

Measured: src/msf_math.c, tools/gen_trig_tables.py and
src/msf_trig_tables.h written per the design entry. Host and
ARM (cortex-m0plus, -Os) compiles clean under
-Wall -Wextra -Werror; ARM object 7,904 B text including the
~4 KB table, undefined symbols only MSF_FMT_PARAMS,
msf_pack_generic, msf_u128_from_u64/to_u64_trunc and the
integer __aeabi_llsl/llsr/lmul + memcpy from struct copies
(no refused helpers). Binary16 exhaustive differential
(tests/trig_exhaustive.c, MPFR 4.2.2 decider, log
scratch/parcel-w4trig/out/f16_gate.log): checked=507,904
(63,488 finite encodings x 2 functions x 4 modes),
mismatches=0, decider undecided=0, escalations=0, kernel
stage hits 376,832/0/0, final_undecided=0 -> PASS in 6 s.
Design-entry correction, one item: the dropped-limb mutant
is realized at stage width (MSF_TRIG_DROP_LIMB zeroes the two
low limbs of every table-derived endpoint after stage
truncation), because a literal one-limb drop from the
384-bit stored entries perturbs results by at most 2^-352
relative - provably invisible against the measured 2^-111.6
closest boundary in the worst-case sets; the byte-identical
regeneration check separately catches any literal one-limb
table change. The mutant as built is unsound by up to 2^-96
relative at stage 1 and must fail the worst-case gate
(watched at that gate, next checkpoint).
Believed: kernel shape is right; remaining risk concentrates
in the f64 hard cases and f32 wall-clock, measured next.
For: lead

## 2026-10-27 19:52:26 -07:00 - Checkpoint: worst-case gate green; design amendment (scalar + Ek)

Measured amendment first, because the gate below was run
with it. The interval-arithmetic kernel measured 182k
host calls/s (5.5 us/call, scratch kernel_bench.c), which
prices the f32 exhaustive differential at ~74 core-hours -
outside any honest wall-clock for this parcel. Stage
evaluation is therefore the brief's own formulation: one
truncating scalar approximation A per stage with the proven
relative bound Ek, endpoints A +- A*2^-Ek formed outward and
packed (interval pack decision unchanged). The Ek recurrence
was re-derived for the scalar order (generator-checked in
tools/gen_trig_tables.py scalar_ek_exp, cross-printed by
scratch/parcel-w4trig/error_budget.py): Ek <= 2^-155.9 /
2^-251.9 / 2^-379.9 at W = 160/256/384; code uses exponents
146/242/370 (9-bit margin). Same tables, same reduction,
same delta branch, same stage-final rule. Kernel now
383,700 calls/s with bit-identical bench results; the f16
exhaustive gate re-passed unchanged after the rewrite
(507,904 checked, 0 mismatches, stage hits 376,832/0/0).

Worst-case gate (logs scratch/parcel-w4trig/out/wc_*.log):
mechanical parse of the pinned tree's binary64 sinpi.wc /
cospi.wc (tokens read as their correctly rounded binary64,
the census reading; parsed input sets verified byte-equal
as sets to the spike's independent float.fromhex extraction:
74,258 sinPi and 44,334 cosPi unique finite inputs, 0
symmetric difference). MPFR re-decided every value at
320-bit start with bracketed narrowing: sinPi checked
297,084 (74,271 inputs x 4 modes), cosPi 206,232 (51,558 x
4), mismatches 0, decider undecided 0, kernel stage hits
all at stage 1 (294,952 / 202,112 kernel evaluations,
final_undecided=0) -> PASS, ~1 s per file. Two decider
defects found and fixed on the way, recorded here because
the lead should know the decider's shape: (1) mpfr_get_ui
truncates to this host's 32-bit unsigned long - extraction
now splits at 2^32; (2) saturation at 1-|y| below MPFR
resolution needs the 2560-bit final escalation (smallest
binary64 input has delta ~ 2^-2145). The spike's own
prec-320 redecided file is blind in exactly that family
(3 cosPi rows in the first 3000 claim exactly 1.0 towardZero
where the true value is strictly below 1; mpmath via
1-cosPi = 2 sinPi(x/2)^2 adjudicates delta > 0, e.g.
1.20e-646 at 2^-1074) - my decider's directed answers there
(3fefffffffffffff) are the correct ones, cross-checked 3000
rows per function against the spike file outside that
family with 0 disagreements.
Believed: stage 1 deciding every published worst case with
~44 bits of Ek slack matches the leg-(c) arithmetic; the
remaining long pole is f32 wall-clock, sized next.
For: lead

## 2026-10-27 23:51:32 -07:00 - Checkpoint: binary32 exhaustive gate green; all format gates closed

Measured: binary32 exhaustive finite differential completed
as 32 magnitude shards of 2^26 magnitudes, both signs,
8 concurrent shard processes (launcher
scratch/parcel-w4trig/run_f32_shards.sh), launched
2026-10-27 20:18:45 -0700 and complete at 23:48:58 -0700
(12,613 s wall; per-shard logs in
scratch/parcel-w4trig/out/f32shards/shard_*.log, progress in
progress.log). Summed by scratch/parcel-w4trig/sum_f32.py
against the exact finite total: shard logs 32; checked
34,225,520,640 = 4,278,190,080 finite encodings x 2
functions x 4 modes; mismatches 0; decider undecided 0;
audits 2,478 with audit_fail 0; summed kernel stage hits
19,864,223,744 / 0 / 0; summed final_undecided 0 -> F32
EXHAUSTIVE: PASS. The kernel was invoked on every finite
encoding in every mode; the decider decided every magnitude
with MPFR once per function and derived the negative twin
by the exact odd/even symmetry, with raw-MPFR stride audits
(all passing) and specials decided on their own encodings.
With this, every format gate in the brief is closed: f16
exhaustive PASS, binary64 worst-case 100% PASS, binary64
seeded 2^21 per function PASS (16,777,216 checks, 0
mismatches), f32 exhaustive PASS, forced stage-2/stage-3
gates PASS with zero final-undecided everywhere, negative
controls watched failing (dropped-limb worst-case FAIL
50,244 + 7,326 mismatches; quadrant-sign 1,360; delta-sign
1,368; directed-side 3,104; non-integer-reduction 464
runner failures), smoke PASS and standard PASS in the
worktree with inventory Tier 2 39 implemented of 39, and
all 5 firmware targets compile (CMake/Ninja, 447/447 steps,
no flashing, no board lock). Committed vectors 43,492 lines
and the constant tables regenerate byte-identically.
Believed: the six-row bundle is merge-ready as one bundle;
planted-copy verification and board sampled replay remain
lead/verifier work as named in the report.
For: lead

## 2026-10-27 23:54:20 -07:00 - Close: bundle committed on wave4-trig, report READY

Measured: final pre-commit `tools/run.sh standard` after the
f32 shards passed again (48 s, 1,117,504 runner cases in the
final summary line, Tier 2 39 implemented of 39). Report is
scratch/parcel-w4trig/report.md with first line READY.
Committed as 81b76357b357b802ebca9ba39a1e1d9005d5f485 on
branch wave4-trig ("Built SF-1 Step 2c: correctly rounded
sinPi/cosPi (6 rows)"), 16 named files, 45,768 insertions,
21 deletions; nothing pushed or merged. Worktree status
after commit is clean. Remaining by design: planted-copy
verification before merge and board sampled replay under the
board lock are lead/verifier work; KissFFT compat wrappers
are the next parcel.
For: lead

