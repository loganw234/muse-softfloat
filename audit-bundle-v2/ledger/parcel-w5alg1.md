
## 2026-10-28 06:22:52 -07:00 - Design entry: SF-2 Step 2a seam (math_bin) + correctly rounded rSqrt at binary16/32/64 (3 rows), hypot registered planned, written before any code

Measured: brief ledger/briefs/w5-alg1.md read first and obeyed
exactly; governing docs/studies/SF-2.md Secs. 1, 3, 6-9 and
scratch/sf2-algebraic/report.md read in full (its Sec. 3.1 kernel
design, Sec. 5.1 specials, Sec. 6 oracle recipes, Sec. 7.1-7.3
inventory, Sec. 8 split/stops bind). worktrees/w5-alg1 verified
on branch wave5-alg1 at base 7c3819c, clean. Current inventory
verified in-tree: Tier 1 = 783 instantiations, Tier 2 = 39
registered / 39 implemented (tools/run.sh TIER2_TOTAL_EXPECTED=39,
tables/implemented.tsv tail: minmax 24 + payload 9 + sin_pi/cos_pi
6); docs/COVERAGE.tsv matches. Shared layers read and judged
sufficient, no kernel inadequacy found in the escalate-only files:
msf_pack_generic (src/msf_roundpack.c:85; exact magnitude
(sig+f)*2^exp2 over msf_u128 + sticky, five internal modes incl.
MSF_IROUND_TIES_TO_AWAY=4 already armed in round_inc and the
overflow arm), msf_u128 helpers incl. msf_u128_mul_u64_u64
(src/msf_wide.c), msf_decode / msf_nan_delivery (src/msf_decode.h),
the sqrt_core bit-search craft (src/msf64.c:235), the trig_core
one-TU three-format wrapper shape (src/msf_math.c:579-702), the
generator expansion + REPLAYABLE + SIGS (tools/gen_tables.py:97-475),
the runner kind widths (tests/runner.c:43, I64 already present -
not needed by this parcel, recorded for the hypot/math_int
successors), and the MPFR decider precedent
(tests/trig_exhaustive.c narrow/decide). Fences held: nothing with
cft in its name opened, searched, or listed; no third-party source
used as design input (the study's own scratch probe
scratch/sf2-algebraic/rsqrt_mpfr.c was read as the Step 0b recipe
record it is); IEEE PDF not opened - clause meaning enters via the
study's S1-extract citations only. No code written yet; this entry
is the design gate. Format parity: rSqrt ships binary16/32/64 or
not at all; hypot registers planned in the seam and is NOT
implemented here (its parcel is A2 in the study split).

### 1. Seam design (its own first commit)

math_bin: homogeneous binary f(f,f)->f, expansion shape identical
to the minmax branch (gen_tables.py:131) but under its own token -
reusing minmax for hypot would typecheck (rounding comes from the
row) but lie in dispatch metadata, refused per study Sec. 7.1.
Changes: one expand() branch (grouped with the existing binary
branch), math_bin added to REPLAYABLE and to SIGS, so dispatch
emits MSF_SIG_MATH_BIN and a typed trampoline once a math_bin row
is implemented (hypot stays planned => NULL call, runner reports
not-implemented BY NAME, never a pass). operations.tsv gains the
two study Sec. 7.2 rows verbatim (wave 5, tier 2, C-754, exact,
mpfr-exact, vectors directed-alg;ties;seeded-random):

  r_sqrt  rSqrt  9.2  math_un   attr yes 5 mpfr-exact ...
  hypot   hypot  9.2  math_bin  attr yes 5 mpfr-exact ...

r_sqrt is math_un (already exists and is REPLAYABLE); hypot is
the only math_bin consumer and registers planned (no
implemented.tsv rows for it). run.sh TIER2_TOTAL_EXPECTED 39 -> 45
with the freeze comment restated to name Step 2a's 6 rows; the
45 registered / 42 implemented headline is the state after the
kernel commit adds the 3 r_sqrt rows to implemented.tsv (seam
commit alone prints 45 registered / 39 implemented / 6 planned by
name - inventory_check judges the registered total and the
Tier 1 = 783 invariant, both watched). Regeneration stamps all
four generator outputs (include/muse_softfloat.h gains 6
declarations, docs/COVERAGE.tsv gains 6 rows, tests/msf_dispatch.h
gains the sig enum entry + 6 descriptors, src/msf_formats.h is
expected byte-unchanged); regenerate twice, byte-identical, or
the seam does not commit. Seam negative controls watched from
scratch scripts before the seam commit is trusted: (a) an unknown
sig token fed to expand() refuses (SystemExit "unknown sig
class"); (b) Tier 1 still prints 783 implemented of 783 in the
generator output and in run.sh inventory; (c) the two standing
inventory mutants in run.sh controls() (tier1-planned-flip,
tier2-row-deleted) still refuse under the new total. API names by
generation: msf{16,32,64}_r_sqrt, msf{16,32,64}_hypot (planned).

### 2. Kernel design: src/msf_alg.c, rSqrt only (study Sec. 3.1, exact)

One TU, one core parameterized by format (trig_core shape):
rsqrt_core(fmt, bits, rm, flags) + three wrappers
msf{16,32,64}_r_sqrt(a, rm, flags). Pure integer C11, no
allocation/recursion/float-or-double tokens (type scan in run.sh
is the gate), --wrap-clean in the run.sh sense: no undefined
symbols beyond the integer helpers the shipped TUs already carry
(symbol scan over the ARM objects is the evidence).

Decision [study Sec. 3.1, re-derived here]: decode finite x > 0
as M*2^E (msf_decode; M < 2^p, p = 11/24/53). Normalize by exact
left shift to M' in [2^(p-1), 2^p), E' = E - shift; if E' is odd,
double M' (now < 2^(p+1)) and decrement E', so E' is even and
x = M' * 2^E' exactly. With S = p + 9 + (p-1)/2 (25/44/88), let
Q = floor(2^S / sqrt(M')). By the integer lemma
isqrt(floor(A)) = floor(sqrt(A)), Q = isqrt(floor(2^(2S)/M'));
equivalently Q is the largest integer with Q^2 * M' <= 2^(2S).
Bounds: M' >= 2^(p-1) gives Q <= 2^(S - floor((p-1)/2)) (2^20 /
2^33 / 2^62), and M' < 2^(p+1) gives Q > 2^(S - ceil((p+1)/2))
> 2^(p+7); Q therefore carries at least 7 bits below the
destination precision-p significand in every attainable binade,
so one pack of (sign 0, exp2 = -S - E'/2, sig = Q as u128,
sticky = (Q^2 * M' != 2^(2S))) through the unmodified
msf_pack_generic is the correctly rounded result in all five
attributes (pack-feed lemma, study Sec. 2.1): the pack's guard,
round and sticky are the exact floor remainder's, inexact is
raised exactly when sticky makes the delivered value differ,
and no kernel-side tininess/overflow judgement exists.
Realization chosen (the study licenses either and requires the
WIDTHS row to say which): sqrt_core-style bit search on Q from
the proven top bit down, each candidate tested by the
split-u128 compare cand^2 * M' vs 2^(2S): write cand^2 =
a*2^64 + b from one msf_u128_mul_u64_u64; both M'*a (< 2^116 at
the binary64 bound) and M'*b (< 2^118) are single
msf_u128_mul_u64_u64 products; the 178-bit logical product
(3p + 19 <= 178, study Sec. 3.1) is assembled limbwise as
M'*b + (M'*a << 64) over six 32-bit limbs and compared against
the single-bit target 2^(2S) from the top limb down. No new
storage width: every stored value is a u128 or a u64; the
six-limb assembly is compare-only. Sticky/equality comes from
the same compare at the final Q (== 0 iff M' is a perfect
square and the result is exact). Cost class: at most 63 search
steps (21/34/63 by format) of three 64x64->128 limb multiplies
- sqrt_core-class, recorded as shape only; RP2040 text/stack
are measured from the run.sh target objects at gate time, no
performance claim is made.
Range [study Sec. 3.1, re-checked]: results are strictly
interior at every format (binary64 [2^-512.01, 2^537]), so
overflow and underflow are unattainable and subnormal delivery
cannot occur; the only flags ever raised are invalid,
divideByZero, inexact. The pack still owns every flag decision
on the finite path (defence in depth: nothing in the kernel
pre-judges what the range proof says cannot happen).
Ties [D, study Sec. 3.1]: unattainable - a rounding midpoint
is an odd dyadic with p+1 significant bits, and its reciprocal
square would force the integer M' to be the reciprocal square
of an odd integer > 1. The kernel does not use this (the pack
decides ties from true bits if one ever arrived); it is used
exactly once, in evidence design (Sec. 4 below): it is why
ties-to-away and ties-to-even must agree in bits and flags on
every finite input, which the exact-Python decider verifies
case by case instead of assuming.

Test-only mutant, declared here before code: MSF_ALG_TEST_TRUNC
(never defined in a build whose results are quoted) reduces S
by 12, putting Q's least significant bit at/above the
destination round bit so the pack-feed lemma's two-bit margin
is destroyed. It exists so the brief's truncated-stage-width
negative control is a build of the shipped TU, watched failing
from scratch - the MSF_TRIG_DROP_LIMB precedent
(src/msf_math.c:408).

### 3. Specials (study Sec. 5.1 restated; second read of the [2R] cell)

Domain [0, +inf]. NaNs ride the SF-0 2.5 matrix unchanged via
msf_nan_delivery(fmt, [decoded], [fmt], 1, invalid_without_nan):
signaling NaN -> quieted delivery (sign + payload preserved)
+ invalid; quiet NaN -> itself quieted-form, no flag. Table
as shipped (all five modes identical; rounding never applies):

| input | result | flags | basis |
|---|---|---|---|
| +0 | +inf | divideByZero | study 5.1 (extract p063 L27) |
| -0 | -inf | divideByZero | [2R] paired-sign cell, second read below |
| +inf | +0 | none | study 5.1 (p063 L27) |
| -inf, finite < 0 | default qNaN (positive canonical) | invalid | study 5.1 (p060 L33 domain) |
| qNaN / sNaN | matrix delivery | invalid iff sNaN | SF-0 2.5 via msf_nan_delivery |
| finite > 0 | Sec. 2 kernel | inexact iff sticky | Sec. 2 |

Second read of rSqrt(-0) (the parcel's [2R] obligation; stop
rule: if this read flipped the cell, I stop and report - it
does not flip): three routes agree on -inf. (i) The study's
extract record: the 9.2.1 line states the signed-zero pole
with paired signs (p063 L27). (ii) Sign composition through
operations whose signed-zero cells are Tier 1 settled in this
tree: squareRoot(-0) = -0 (shipped msf*_sqrt via sqrt_core
zero_bits(sign), Berkeley-gated), and the reciprocal pole
1/(-0) = -inf + divideByZero is the shipped division cell
(div_core: divisor zero -> signed infinity + divideByZero);
rSqrt is by definition that composition at the pole, so a
+inf delivery would contradict the tree's own gated cells.
(iii) The 9.2 head rule for a simple pole at a finite operand
is a "correctly signed infinity" (study 5.0 common rules,
p059 L32-33); the sign of the pole of 1/sqrt(x) at a signed
zero is the sign carried by sqrt of that zero, i.e. route
(ii). MPFR's +inf on this cell (measured by the study, 4
fenced cases of 262,144) is therefore classified oracle-limit
on a specials cell, exactly as the study fences it: the cell
is generator-table-decided in tests/alg_decider.c and in the
generator's independent table, cross-checked against each
other, and NEVER sourced from MPFR output. No other rSqrt
cell is [2R]; hypot's (inf, sNaN) [2R] cell belongs to the
hypot parcel and is untouched here (hypot stays planned).

### 4. Evidence design (generators, volumes, controls)

Oracle: tests/alg_decider.c (new, test-only like
trig_exhaustive.c; links MPFR, never the shipped library's
decisions). decide mode reads "msf64_r_sqrt <hex>" lines and
prints bits+flags for all five modes. Finite positive inputs:
the proven Step 0b operation recipe, verbatim shape from the
study probe - per-format precision/emin/emax (11/-23/16,
24/-148/128, 53/-1073/1024) set and read back, input set
exactly from its decoded significand at format precision (it
fits by construction), mpfr_rec_sqrt under RNDN/RNDZ/RNDU/RNDD,
then mpfr_subnormalize skipped on zero/inf/NaN intermediates.
Flags derived, never transcribed: inexact iff the final
ternary is nonzero (overflow/underflow unattainable, Sec. 2;
if MPFR ever produced inf/zero on a finite positive input the
decider aborts - a recipe violation must be loud, not
averaged). Ties-to-away: raw MPFR RNDNA is prohibited as a
general mode (SF-2 Sec. 2) and is not used; the decider prints
ta = te and the generator REFUSES unless its independent
exact-Python decider agrees on ta for that input (the no-ties
argument of Sec. 2 verified per case, not assumed globally).
Specials in the decider are table-decided from Sec. 3 above,
implemented independently of the kernel (trig precedent), so
generation is a three-way cross-check: MPFR recipe (4 modes,
finite positive) vs exact-Python integer decider (5 modes, all
inputs; floor at doubled working scale via integer isqrt and
midpoint compares by exact squaring - a different code path
from the C kernel) vs the settled specials table (all special
inputs, in both the decider and the generator; any
disagreement aborts generation - the study stop rule).

Committed vectors (tests/gen_vectors_alg.py -> tests/vectors/
alg-f16.vec, alg-f32.vec, alg-f64.vec; provenance family
mpfr-alg:{specials,directed,ties,seeded}, one family per study
Sec. 7.3, ~1,200 lines per format = ~240 inputs x 5 modes):
specials tree (both zeros both signs of inf, quiet/signaling
NaN payload samples incl. sign variants, negative finite
samples); directed (perfect-square lattice incl. powers of
two - the exact-result cases - and their +-3 ulp neighbours,
binade edges at every exponent class incl. smallest/largest
subnormal and smallest normal inputs and largest-finite
neighbourhoods, odd/even-E' shapes); ties (midpoint-adjacent
constructions: for sampled destination midpoints m (odd p+1
-bit significands), the encodings nearest 1/m^2 and their
+-1 ulp neighbours - the hardest-to-round inputs this
function admits, since exact ties are unattainable; the tag
name follows the study Sec. 7.2/7.3 vocabulary and
VECTORS.md will say midpoint-adjacent, not ties); seeded
(seeded finite-encoding sweep, seeds in the generator).
Regeneration byte-stable twice or the files do not commit.

Gate-only differentials (generated, not committed, run from
scratch scripts with explicit ulimit -v memory ceilings on
the long sweeps): binary16 EXHAUSTIVE - every one of 65,536
encodings x 5 modes = 327,680 kernel-vs-decider comparisons,
count printed (the study's 262,144 four-mode probe extended
to the fifth attribute; kernel invoked on the original signed
encoding in every mode, specials decided by the table in both
paths); binary32/64 seeded volume differential (seeded finite
encodings + the committed directed families re-decided, counts
printed, MPFR adjudicates every line - no sampling shortcut
and no foreign correctly-rounded binary is needed at these
volumes). Negative controls, each watched failing from
scratch before it is trusted: (1) 1-ulp-moved expectation on a
midpoint-adjacent (hardest) committed case -> runner FAIL;
(2) specials mutants as vector mutations (rSqrt(-0) flipped
to +inf - the MPFR cell, proving the committed line is not
MPFR-sourced; rSqrt(qNaN) payload-mangled; rSqrt(-1) made
finite) -> FAIL each; (3) inexact stripped (flags 10 -> 00)
on a known inexact midpoint-adjacent case (the brief's
"known tie" - exact ties are unattainable for rSqrt per
Sec. 2, so the control takes its attainable form: the flag
strip is on a case whose guard/round/sticky pattern is the
tie pattern plus sticky) -> FAIL; (4) directed-mode swap
(tp<->tn over a committed file) -> FAIL; (5) truncated stage
width (MSF_ALG_TEST_TRUNC build over the committed files)
-> FAIL. Then tools/run.sh smoke + standard PASS, target
objects from run.sh's symbol scan inspected for msf_alg text
size (stack: fixed arrays only, six-limb compare frame -
measured by object inspection, stated as measured).

### 5. Owned files and escalations

Owned (brief): tables/operations.tsv (2 rows),
tables/implemented.tsv (3 r_sqrt rows, kernel commit only),
tools/gen_tables.py (math_bin), tools/run.sh (TIER2 total +
freeze comment; SRC += src/msf_alg.c; VECS += alg-*.vec in the
kernel commit so the seam commit builds standalone), generated
include/muse_softfloat.h + docs/COVERAGE.tsv (+ the other two
generator outputs wherever regeneration changes them),
src/msf_alg.c (new), tests/gen_vectors_alg.py,
tests/alg_decider.c, tests/vectors/alg-*.vec,
tests/VECTORS.md (tag rows), docs/WIDTHS.md (one r_sqrt row:
"128-bit storage; 178-bit logical split compare over u128" +
the realization sentence), docs/metrics/briefs.jsonl (my row).
Named escalation, not touched: board/CMakeLists.txt MSF_SRC
and board/run_board.sh source list also carry the core TUs -
adding src/msf_alg.c there is lead merge wiring outside my
owned list (board sampled replay is lead work under the board
lock regardless); the report names it. msf_roundpack.c /
msf_wide.c: judged sufficient above; any inadequacy appearing
during implementation stops the parcel for escalation, never
an improvisation (brief seam rule). Commit shape: seam commit
first (own commit), then kernel+evidence commit(s); detailed
bodies ending with the Co-Authored-By trailer; never push or
merge; no board flashing. All runs from script files in
scratch/parcel-w5alg1/ under Git Bash with MSF_PYTHON pinned
to the workspace .venv and TMPDIR/TMP/TEMP inside scratch.

Stop conditions carried verbatim from the study: any
unadjudicated disagreement (decider vs exact-Python vs table
vs kernel) stops the parcel - classify, never average, never
relabel; a second-read specials cell flipping without an
owner ruling stops the parcel (Sec. 3 read does not flip).
If any format's gate cannot close, the bundle returns NOT
READY whole (parity); binary16-green alone never ships.

Believed: the exact decision needs no margin argument beyond
the pack-feed lemma's bit count, so the exhaustive binary16
gate plus directed/seeded binary32/64 differentials are the
whole correctness risk surface; wall-clock risk is decider
throughput only.
For: lead

## 2026-10-28 06:36:21 -07:00 - Results: seam + rSqrt landed, all gates green; hypot remains planned

Measured: implemented exactly per the design entry above.
Two commits on wave5-alg1, tree clean: seam 628a18d
(math_bin in tools/gen_tables.py, the two study Sec. 7.2
operations rows wave 5, run.sh Tier 2 total 39 -> 45,
regenerated header/dispatch/COVERAGE; seam controls watched
from scratch/parcel-w5alg1/01_seam.sh - unknown sig token
refused, Tier 1 prints 783/783, seam-tree smoke PASS with
45 registered / 39 implemented / 6 planned by name), then
kernel b886e038d095bfad643ccb937f44abd03bcaaa7f (14 named
files, 4,545 insertions). src/msf_alg.c is the design
entry's realization (bit search + 178-bit split compare
over u128, one unmodified pack call, five modes from
birth; MSF_ALG_TEST_TRUNC test-only mutant as declared).
Evidence (script files 02-09 in scratch/parcel-w5alg1/,
logs in out/): tests/alg_decider.c on the Step 0b recipe
cross-decided on every committed input by the generator's
exact integer decider, generation refusing disagreement
(none occurred; the study stop rule never engaged, and
the [2R] rSqrt(-0) = -inf cell did not flip - it shipped
table-decided, with the flipped-cell mutant watched
refused). Committed vectors alg-f16/f32/f64.vec =
1,195/1,200/1,200 lines (specials 435, directed 2,000,
midpoint-adjacent ties 750, seeded 410), regenerated
twice byte-identical. Binary16 exhaustive differential:
327,680 checked (65,536 encodings x 5 modes), 0
mismatches, plus the same 327,680 from exact-Python alone
through the runner, PASS. Binary32/64 seeded: 1,750,000
checked per format (350,000 inputs x 5), 0 mismatches.
Negative controls all refused (1-ulp hardest, three
specials mutants, stripped inexact, tp<->tn swap 384
lines, trunc mutant 745 lines). smoke PASS (175,018
cases; type/symbol scans clean; inventory tier1 783/783,
tier2 42 implemented / 3 planned / 45 registered) and
standard PASS (+1,117,504), re-run post-commit in
09_final.sh, after which a full regeneration left the
committed tree clean. Target: arm-none-eabi-gcc 14.2.1
cortex-m0plus -Os clean; msf_alg.o text 1,032 B, data/bss
0; stack frames rsqrt_core 192 B / alg_cmp_sq 128 B /
wrappers 16 B; undefined symbols integer-only (no refused
helpers). Report: scratch/parcel-w5alg1/report.md, first
line READY.
Not done, by design and named in the report: hypot is
registered PLANNED only (its A2 parcel follows; the
(inf, sNaN) [2R] cell is untouched); board source lists
(board/CMakeLists.txt MSF_SRC, board/run_board.sh) need
src/msf_alg.c added at lead merge - escalated, outside my
owned files; board sampled replay and planted-copy
verification are lead/verifier work; the study's optional
recorded binary32-exhaustive foreign-decider run was not
run (not brief-required; seeded MPFR volume shipped
instead). Nothing pushed or merged; no board flashing.
Believed: the 3-row rSqrt bundle plus seam is merge-ready;
residual risk is the merge-time board wiring above.
For: lead
