PRICED-GO exp2/exp2m1, PRICED-GO log2/log2p1, PRICED-GO exp/expm1 (fences F1), PRICED-GO exp10/exp10m1 (hygiene H1), PRICED-GO log/logp1 (fences F1), PRICED-GO log10/log10p1

# SF-2 input spike: exp/log Clause 9.2 families (study-sf2-explog)

Brief: `ledger/briefs/sf2-explog.md`. Method mirrors
`scratch/tier2-trig-spike/report.md` (read in full): published
worst-case inputs re-decided here by MPFR at 320 bits, margins
measured with the same metric (`extra = -log2(dist/ulp)`;
deciding needs about `p + extra` error-free significand bits),
kernel reuse audited against the shipped
`muse-softfloat/src/msf_math.c` +
`muse-softfloat/tools/gen_trig_tables.py` (both read in
full). Scratch only; no repository writes. All scripts under
`scratch/sf2-explog/`, run via Git Bash wrappers with
`MSF_PYTHON` pinned to the workspace `.venv` Python 3.12.15
(mpmath 1.4.1) and TMP inside the scratch dir; C probes use
MSYS2 gcc 16.1.0 + MPFR 4.2.2 (`probe_env.sh` /
`out/probe_env.log`).

Headline numbers (details in Sections 2-3): binary64
published sets exist and were re-decided for **all 12 names**
(4.94M unique finite inputs total). Plain-class (width-driving)
hardest margins land at **56.4-69.8 extra bits** for every
function except one directed near-1 case in `exp` (105.6,
composition-decided); RN maxima are 55.4-69.8 plain and at
most 100.8 inside the composition classes. The shipped trig
three-stage widths (160/256/384, stage-1 error budget
2^-140 class) therefore decide everything observed on the
direct path except two named pockets, and the unbounded-extra
cases are all input-structural (integer/tiny/power-of-two
attractors) that a pack-scale composition branch decides -
the same role the trig delta branch plays. Nothing measured
here needs a fourth stage or wider tables. Estimated
programme: **220-310 hands-on hours** for all six bundles
(Section 7), first bundle `exp2`/`exp2m1` at 55-75 h
including the shared infrastructure delta.

Two fenced findings replace assumptions a parcel might
otherwise make, both measured (Section 5): **F1** - as built
on this host, the foreign `cr_expm1{f}` and `cr_log1p{f}`
binaries are not correctly rounded in directed modes at tiny
inputs (hundreds of 1-2 ulp disagreements, adjudicated
against them), plus isolated RN 1-ulp disagreements on
subnormal results in four cells; directed corroboration for
those two functions is MPFR-only until a Linux documented
check says otherwise (the Step 0b `cr_cospif` pattern, now
with a second and third instance). **Precision trap** - a
fixed-precision wide-then-narrow MPFR side (my own 320-bit
smoke reference, and by extension any 320-bit vector
generator) silently collapses near-1/tiny results onto the
representable grid; 44,917 published `log1p` inputs looked
"exact" at 320 bits and are not (Section 2.4). Every parcel
generator must be precision-adaptive (two-precision agreement
or direct correct-rounded evaluation at target precision)
near attractors. My margin table was audited against exactly
this failure (1024-bit re-decision, Section 2.4) and the
plain-class maxima are unaffected.

## 0. Basis, fences, disclosures

Authorities read: SF-1 Sections 8/11
(`muse-softfloat/docs/studies/SF-1.md`), Clause 9 survey
Section 4.6 (`scratch/tier2-clause9/report.md`, ranks 5-8 =
the 12 names here, all TR-B), trig spike report + its
`margins.py`/`mpfr_wc_redecide.c`/`trig_common.py`/
`wc_aggregate.py` method files, Step 0b report
(`scratch/tier2-oracle-0b/report.md`), S1 Clause 9.2/9.2.1
extracts (`scratch/S1/extract/combined.txt` lines
2620-2814), `muse-softfloat/src/msf_math.c` (702 lines),
`muse-softfloat/tools/gen_trig_tables.py`,
`muse-softfloat/tools/run.sh` (MSF_PYTHON pin pattern).

Fences held: nothing with `cft` in its name was opened,
searched, or listed. CORE-MATH contact was execution and
metadata only: directory listings (file names + sizes), the
binary64 `.wc` files parsed mechanically (first token of
each data line; census proves exactly one token per data
line in all 12 files, so no expected-value column exists in
what was extracted; comment lines counted, never printed or
used), 24 units (12 functions x binary32/64) compiled
without being opened and executed via a fresh harness over
the public `cr_*` names (symbol names recovered with `nm`,
not by reading source). No implementation source, constants,
or coefficients were read or used as design input; every
numeric value below was decided by MPFR/mpmath/exact
Fraction code written for this spike. Two compiler
diagnostics in build logs quoted a one-line `asm` barrier
idiom at error sites (Step 0b precedent disclosure; no use
made of it). Fetches (Section 1): three official
documentation pages, recorded with sha256 in
`ledger/study-sf2-explog.md`; the pinned oracle tree was
*not* re-fetched (Step 0b pin reused).

Host-condition disclosure: for most of this spike a sibling
agent's runaway Python process held 19-43 GB RAM and paged
heavily; it was identified as not belonging to this study
(`scratch/sf2-algebraic/proto4.py`, fully re-verified
command line) and stopped only on the workflow owner's
explicit second instruction, at 43.4 GB working set. Host
rates below were measured after the stop unless noted, and
are records, not performance claims. One bench artefact
found and recorded, not smoothed: MPFR rates measured with
stdout to `/dev/null` under this Git Bash are ~20x low
(5.6k/s vs 88k/s to a file sink, output byte-identical,
`out/bench_diag.log`); all quoted rates use a file sink.

## 1. Published worst-case authority (leg (a) reading)

SF-1 Section 8's ladder: (a) published hardest-to-round
cases pass, (b) directed + seeded MPFR differentials
(binary16 exhaustive), (c) intermediate precision + proven
error bound exceeding the known worst-case gap, or a Ziv
loop with a termination bound - for all three formats in one
parcel (parity rule). The trig parcel closed binary64 leg
(c) on published-completeness authority; the same reading
is available here, on this evidence:

- Official worst-cases page (fetched 2026-10-28,
  `out/fetch_worst.html`, sha256 in the ledger): "For
  binary64, all worst cases cover the full range of the
  function (worst cases that would give an output beyond
  the underflow/overflow thresholds are not included), with
  the following exceptions: pow, atan2, hypot, atan2pi"
  (restricted sets). **None of the 12 exp/log names is an
  exception.** Files are `xxx.wc` beside each function,
  "mostly computed with the BaCSeL software tool"; identical-
  bit counts live in file comments, which the fences forbid
  using - hence measured margins below.
- Official project page (same fetch): "correct rounding is
  claimed for all IEEE-754 rounding modes. For univariate
  binary32 functions it is checked by exhaustive search."

Mechanical census of the pinned tree
(`scratch/oracles/core-math-3b2163bb...`, Step 0b pin;
`wc_census.py`, `wc_inputs.py`; logs `out/wc_census2.log`,
`out/wc_inputs2.log`). Directory metadata first: all 12
function directories exist at binary16/32/64 (the 754 name
`logp1` is `log1p` there, as in MPFR). `.wc` files exist
**only at binary64 - for all 12 names**; none at
binary16/32 (same shape as the Pi pair at Step 0b). So no
family is missing its binary64 published set, and the
binary32 leg follows the trig settlement (exhaustive
MPFR-decided differential, foreign binary as pre-screen
only where Section 5 verifies it), not a published set.

| fn (754 name; oracle dir) | .wc bytes | data lines | comment lines | finite unique inputs | unparsed |
|---|---|---|---|---|---|
| exp2 | 1,661,958 | 77,182 | 31 | 77,120 | 2 nan + 2 inf tokens, 2 signed-letter 5-char tokens |
| exp2m1 | 5,358,578 | 240,834 | 49 | 240,824 | same 6 |
| log2 | 729,771 | 33,248 | 31 | 33,237 | same 6 |
| log2p1 | 28,782,572 | 1,263,804 | 36 | 1,263,796 | same 6 |
| exp | 25,400,537 | 1,129,433 | 46 | 1,129,356 | same 6 |
| expm1 | 2,737,457 | 123,591 | 32 | 123,545 | same 6 |
| exp10 | 1,451,023 | 65,430 | 38 | 65,373 | same 6 |
| exp10m1 | 5,090,217 | 227,807 | 31 | 227,791 | same 6, plus **H1: 8 hex tokens not exactly binary64** |
| log | 3,073,160 | 134,960 | 27 | 134,950 | same 6 |
| logp1 (log1p) | 7,767,674 | 347,771 | 34 | 347,759 | same 6 |
| log10 | 1,498,370 | 65,528 | 25 | 65,518 | same 6 |
| log10p1 | 29,091,583 | 1,276,879 | 43 | 1,276,872 | same 6 |

Total finite unique binary64 inputs re-decided: 4,941,977.
Token conversion here is stricter than the trig spike's
`float.fromhex` route: each token was parsed exactly as a
rational and accepted only if it *is* a binary64 value
(round-trip through the exact rounder). Inexact tokens: 0
for eleven files; **H1** - `exp10m1.wc` carries 8 hex-float
tokens whose exact values are not binary64 numbers. They
were excluded from measurement; a parcel importing these
vectors must decide their status explicitly (higher-
precision encodings of inputs? symmetry artefacts?) rather
than silently rounding them - hygiene item, not a
completeness hole (8 in 227,807). The 5-char signed-letter
tokens (2 per file) match the trig census's unparsed class;
they sit alongside explicit nan/inf tokens (2 each) as
specials anchors, excluded from margin work by design.

Completeness reading, stated carefully (trig spike's
discipline): measured maxima below are *lower bounds* on
each function's true hardest margin; they are the true gap
only under the fetched full-range completeness claim. The
measured distributions support threshold-collected hard
sets (bulk of genuine cases above extra 40, sharp cutoff at
each maximum; Section 2), as with the Pi pair. The kernel
sketch in Sections 4/6 carries stage widths with ~80-300
bits of headroom over the measured maxima, so leg (c) as
designed tolerates substantially harder unpublished cases;
parcels resting leg (c) on completeness should still say so
in their claim text, knowingly, per the trig precedent.

## 2. Margins measured: binary64

Method (`mpfr_redecide.c` + `aggregate.py`, drivers
`run_f64_wc.sh`, `run_f64_fix.sh`; logs
`out/wc_f64_aggregate2.log`, `out/hp_aggregate.log`,
`out/attractor_all.log`): every finite unique input
evaluated by the direct MPFR function (`mpfr_exp`,
`mpfr_expm1`, `mpfr_exp2`, `mpfr_exp2m1`, `mpfr_exp10`,
`mpfr_exp10m1`, `mpfr_log`, `mpfr_log1p`, `mpfr_log2`,
`mpfr_log2p1`, `mpfr_log10`, `mpfr_log10p1` - all present in
MPFR 4.2.2, verified in the installed header) at prec 320
with default exponent bounds, wide value printed in hex,
narrowed to binary64 in all four modes by the proven recipe
(emin -1073, emax 1024, `mpfr_check_range` +
`mpfr_subnormalize`, zero guard). The Python aggregator
re-parses every wide value exactly as a Fraction and
cross-checks all four C output patterns against the trig
spike's first-principles rounder: **mismatches 0 over all
4.94M inputs x 4 modes**. Runtime: re-decision itself is
seconds-to-14 s per function (~30-120k eval/s); the exact
Fraction aggregation dominates (up to ~310 s for the 1.27M-
line files) - a parcel gate should use a C aggregator or
accept that shape (Section 7 prices it).

Classes, all decided from the input/result structure (trig
saturation discipline): EXACT (representable result);
OVERFLOW region (|y| > fmax, boundaries = fmax and the
midpoint above it); M1SAT (expm1 forms with y within 2 ulp
above -1: 1-result distance is the exponentially tiny
base^x, cut-decided); ZEROTHR (0 < |y| <= 2u: exact input-
side exponent cut); BOUNDARY@320 (wide value exactly on a
rounding boundary at 320 bits - only 5 inputs total, all
proven true ties at 1024 bits, Section 2.3); GENUINE
(everything else) split further by `attractor.py` into
PLAIN (width decides) versus ATTRACTOR (input-structural:
power-of-two inputs for log forms, x or 1+x a power of two
for p1 forms, |y-1| <= 2^-(p+2) for plain exp forms,
integer inputs for exp2m1, |x| <= 2^-8 for m1/p1 forms -
pack-composition decides, Section 2.2).

### 2.1 The margin table (binary64, prec 320, audited in 2.4)

Counts below are evaluated finite inputs after removing
domain tokens (MPFR NaN for out-of-domain anchors: 5 each
in log/log2/log10, 1-2 in p1 files; MPFR infinite: log
files carry one x=0 pole anchor each; exp-family files
carry 152-154 inputs so large the wide result overflows
even MPFR's default range - beyond-threshold anchors,
decided by the input-side cut, counted in the aggregate log
as WIDE-INF/WIDE-HUGE and excluded here). "Exact" counts
are the 1024-audited ones where they differ (Section 2.4;
only logp1 and exp10m1 move materially).

| fn | evaluated | exact (audited) | plain max extra (RN / DIR) at input bits | attractor n, max RN, max DIR | other classes |
|---|---|---|---|---|---|
| exp2 | 76,966 | 2,101 | 60.54 / 60.43 @3f5e4596526bf94d | 0 | ovf 96 (max 1.0 @x=1024), zthr 2, tie 1 |
| exp2m1 | 240,823 | 108 | 59.10 / 56.74 @bf73918e8608bd5b | 206,300 + 703 reclassified, RN 59.92, DIR 267.00* | m1sat 65, ovf 2, ties 2 |
| log2 | 33,231 | 83 | 55.78 / 56.37 @7fe61555f75885b4 | 0 | - |
| log2p1 | 1,263,794 | 115 | 60.54 / 59.85 @44ee499f19ecc9fb | 203,059 + 703, RN 62.07, DIR 267.00* | zthr 2 |
| exp | 1,129,202 | 5 | 59.25 / **105.58** @3cafffffffffffff | 0 | ovf 96, zthr 700 |
| expm1 | 123,390 | 4 | 55.44 / 58.88 @40183d4bcdebb3f4 | 91,762, RN 59.86, DIR 97.83 | m1sat 47, ovf 96 |
| exp10 | 65,372 | 26 | 61.57 / 66.24 @bfe1416c72a588a6 | 0 | ovf 2, zthr 8, tie 1 |
| exp10m1 | 227,790 | 23 | 58.24 / 67.24 @bfe1416c72a588a6 | 198,109, RN 62.88, DIR 59.63 | m1sat 483+125, tie 1 |
| log | 134,944 | 1 | 62.03 / 65.15 @6a562a88613629b6 | 2 (trivial) | - |
| logp1 | 347,756 | 29 | 62.03 / 65.15 @6a562a88613629b6 | 113,141 + 44,888, RN **100.83**, DIR 267.00* | - |
| log10 | 65,512 | 23 | **69.77** / 67.65 @5ace12d66744ff81 | 2 (trivial) | - |
| log10p1 | 1,276,870 | 16 | **69.77** / 67.65 @5ace12d66744ff81 | 211,668, RN 60.40, DIR 59.83 | zthr 2 |

*267.00 is the 320-bit quantization value (320-53); at
1024 bits the same classes measure up to 973 (Section 2.4)
and their true format-bounded maximum is ~1021 (smallest
subnormal input). These are never width demands (2.2).

Readings:

- Plain RN maxima: 55.78-69.77. Plain DIR maxima:
  56.37-67.65, except exp's 105.58 (next bullet). In
  p+extra terms: a direct-path kernel needs proven error
  below 2^-123 relative for the worst plain case
  (log10/log10p1) - inside a 160-bit stage-1 budget of
  2^-140 class with ~17 bits to spare before accounting
  shape differences (Section 6).
- exp DIR 105.58 at x = 0x3cafffffffffffff (x just below
  2^-52): exp(x) lands 2^-105.6 ulp from the representable
  1+2^-52 because x + x^2/2 cancels against the grid.
  Genuine searched hardness, but its natural decision path
  is the m1 form composed onto 1 at pack scale (correction
  ~2^-52 computed relatively); on a direct path it needs
  stage 2. Price both, choose in the parcel (Section 6).
  exp10/exp10m1 share their DIR-max input
  (0xbfe1416c72a588a6, x ~ -0.532) across bases - the same
  Diophantine structure surfacing through ln10 vs 1.
- logp1 attractor RN 100.83 at 0xbcd7fffffffffffd
  (x ~ -2^-50): the hardest *midpoint* approach anywhere
  in the 12 sets. On the correction-composition path it
  needs ~102 correction-relative bits (Section 2.2
  formula); on a direct path 53+100.8 = 154 bits, i.e.
  stage 1 is marginal and stage 2 decides. Not a blocker
  either way, but it kills any single-stage 128-bit design
  for logp1 - named here so nobody prices one.
- Distributions: genuine bulk sits in the 40-59 buckets
  for every file (threshold collection), with attractor
  ladders visible as flat ~10-700-per-10-bits tails to 260
  in exp2m1/log2p1/logp1 (exponent-scaled copies of one
  significand structure - e.g. log2's top-10 are one
  significand at ten exponents, since log hardness is
  exponent-invariant up to the integer part). Genuine
  counts above extra 80 outside attractor ladders: exp 51,
  expm1 24, all others 0.
- Overflow region is undemanding everywhere measured:
  worst RN extra 1.0 (exp2 at x=1024 exactly), most files
  negative (far past the midpoint). The input-side cut
  still must be exact (Section 6), but no hidden hardness
  lives at the threshold in these sets.

Independent second route: the 25 hardest genuine inputs
per function (300 total) re-evaluated with mpmath at
dps 130 via first-principles stable forms
(`spot_mpmath.py`): 300/300 rounding agreement with the
MPFR C outputs, after one route artefact was isolated and
re-decided by the direct-power form (exp10 at x ~ -182,
where the 1+expm1 form collapses; `spot_fix1.py`, both
dps 130 and 200 agree with MPFR). Logs: `out/spot_f64.log`.

### 2.2 Attractor classes: why they are not widths

The unbounded extras all have the shape result = B + c
where B is *exactly known* (an integer, 1, the input x
itself, or 2^n) and c is a correction computed from a
reduced argument with *relative* accuracy. Directed
closeness to B grows without bound as c -> 0 (tiny inputs,
huge exponents), so no fixed stage width decides the
directed side; what decides it is forming B + c exactly at
pack scale - integers plus a wide-float correction with
sticky - exactly the trick `trig_pack_one_minus` already
ships for 1-delta (Section 4 generalizes it). The measured
attractor RN maxima bound the correction-relative accuracy
actually needed: deciding B + c against a midpoint at
distance 2^-rn * ulp(B+c) needs error(c) < that distance;
with c carried as a W-bit wide float, error(c) ~ |c| 2^-W,
so W > rn + (p-1) - log2(|B+c|/|c|) roughly: the logp1
100.83 case needs ~102 bits, every other attractor RN case
(<= 62.9) needs <= ~115 bits at its own |c| scale - inside
stage 1. Parcels must prove this per branch with the
generator recurrence (same obligation shape as the trig
delta proof); the spike's claim is only that the measured
numbers leave comfortable room.

### 2.3 Exact ties exist (unlike sinPi/cosPi)

Five inputs across all sets sit exactly on a rounding
boundary at 320 bits and remain exact boundaries at 1024
bits (`out/hp_aggregate.log`); each is a provable exact tie
by integer arithmetic: exp2(-1075) = u/2;
exp2m1(54) = 2^54-1 (midpoint of the spacing-2 binade);
exp2m1(-54) = -(1-2^-54) (midpoint below 1);
exp10(23) = 10^23 (odd part 5^23 is 54 bits - the classic
tie); exp10m1(16) = 10^16-1 (odd, spacing-2 binade). A
Ziv interval [lo,hi] around a true tie never decides by
agreement, so - unlike the trig kernel, where Niven's
theorem bans ties outside two exact branches - each parcel
must enumerate its exact/tie-capable branches and deliver
ties through exact integer paths. That enumeration is
finite and standard: by Lindemann-Weierstrass exp(x) is
transcendental for nonzero algebraic x (so exp/expm1 have
no exacts or ties beyond x=0), and by Gelfond-Schneider /
direct dyadic analysis the base-2 and base-10 families
reach dyadic values only through integer inputs (2^n,
2^n-1, 10^n = 2^n 5^n with the odd part's bit length
deciding representable-vs-midpoint, 10^n-1), log-family
results are dyadic only at the anchors log_b(1) = 0 and
log2(2^k) = k (log2p1(2^k - 1) = k). The parcels carry
these arguments with citations; they also fix the inexact
flag rule (inexact always outside enumerated exact
branches; ties are inexact results and signal).

### 2.4 Audit against fixed-precision collapse

A 320-bit wide evaluation rounds any result whose distance
to a representable is below ~2^-267 ulp onto that
representable, so "exact" classifications at 320 bits are
suspect in attractor territory. Every input classified
exact at 320 bits (49k total, dominated by log1p's 44,917,
whose input exponents all lie in [-1074, -320] - the tell)
was re-decided at 1024 bits (`exact_recheck.py`,
`run_exact_hp.sh`, `out/exact_hp_aggregate.log`): true
exacts stay exact (exp2 2,101/2,106; log2 83/83; log10
23/23; log10p1 16/16; log 1/1), and everything that
reclassifies is attractor-class with rn = 1.00 and dir up
to 973 (= the 1024-bit quantization, true values to
~1021): exp2m1 703, log2p1 703, log1p 44,888, exp10m1 125
(into M1SAT), a handful elsewhere. **No reclassified case
carries RN hardness, so no plain-class maximum in 2.1 is
understated by the 320-bit pass.** The same audit is
mandatory shape for parcel generators (Section 5's smoke
shows what happens without it).

## 3. Margins measured: binary32 (directed + seeded)

No binary32 `.wc` exists (Section 1), so - mirroring the
trig spike's f32 construction - margins come from
directed + seeded sets (~41-54k inputs per function,
domain-aware: dyadic ladders near 0/±1, ulp neighbourhoods
of 1 and of overflow/underflow thresholds, powers of two,
subnormal inputs, 30,000 seeded random finite patterns
filtered to domain, 10,000 exponent-window patterns;
`f32_inputs.py`, drivers/logs `run_f32.sh`,
`out/f32_aggregate.log`), re-decided at prec 320 with the
Step 0b-proven binary32 recipe (emin -148, emax 128).
C-vs-exact-rounder mismatches: 0 everywhere. mpmath spot
check of the 25 hardest per function: 300/300 agree
(`out/spot_f32.log`). One BOUNDARY@320 input (exp2 at
x = -150) stays a boundary at 1024 bits: 2^-150 = u/2, a
true tie, same structure as f64.

| fn | evaluated | plain max extra (RN / DIR) | attractor max DIR (class) |
|---|---|---|---|
| exp2 | 42,458 | 14.95 / 13.26 | 126.53 (near-1, x=2^-149) |
| exp2m1 | 43,440 | 12.48 / 15.53 | 72.00 (integer x=96) |
| log2 | 41,337 | 16.84 / 14.56 | - |
| log2p1 | 45,892 | 17.28 / 23.19 | 21.47 (pow2 x=2^40) |
| exp | 42,545 | 27.00 / 47.58 | 126.00 (near-1) |
| expm1 | 43,418 | 15.32 / 16.05 | 148.00 (tiny identity) |
| exp10 | 42,408 | 14.23 / 15.10 | 124.80 (near-1) |
| exp10m1 | 43,296 | 13.67 / 15.00 | 14.11 max_RN |
| log | 41,349 | 24.58 / 23.58 | 5.38 (pow2, trivial) |
| logp1 | 45,926 | 17.43 / 16.19 | 148.00 DIR, 42.83 RN (tiny) |
| log10 | 41,410 | 15.87 / 15.67 | 7.46 (pow2, trivial) |
| log10p1 | 45,878 | 16.48 / 16.89 | 14.57 |

Honest weight (trig spike's caveat, numbers updated): for
~45k samples the expected plain maximum under uniform
fraction parts is ~log2(N) ~ 15.5, and most maxima above
sit within a few bits of that - these are machinery
confirmation and *lower bounds* (any correct f32 kernel
needs > 24+47.6 = 71.6 bits at exp's near-1 pocket, etc.),
not worst-case evidence. The directed ladders did their
job at the known pockets: exp's plain DIR 47.58 at
0x33ffffff is the f32 analogue of the f64 near-1 case, and
log's RN 24.58 sits at x = 1-2^-23. Binary32 leg (c)
cannot rest on these numbers; it rests on the SF-1
settlement: an exhaustive MPFR-decided differential over
the whole format (Section 5.3 prices it at ~4-7 h per
function single-core at measured MPFR rates, embarrassingly
shardable), which is *complete* evidence for the shipped
binary at that format. The shared kernel runs f32 through
the same 160/256/384 stages, so its f32 p+extra demand
(24+70 ~ 94 bits even if the true f32 gap matched f64's -
nothing suggests it exceeds it) is far inside stage 1; the
exhaustive leg is what converts that comfort into a claim.

Binary16 was not measured (brief asks f64/f32): exhaustive
generation over 65,536 encodings x 12 functions is minutes
of MPFR at the rates in Section 5.3 and is complete
evidence per the ladder; parcel routine, priced in
Section 7. One f16-specific caution carried from the S1
read: Table 9.1's note that formats with large precision
relative to exponent range might signal exceptions beyond
those listed (their example is log underflow) - f16 log
results *can* be subnormal (x = 1-2^-11 gives ~-2^-11), so
the pack's after-rounding tininess judgement, not the
table's exception column, governs flags; that is already
the shared-pack behaviour the trig kernel relies on.

## 4. Kernel reuse audit (src/msf_math.c, tools/gen_trig_tables.py)

What carries over mechanically (all families): the `wf_t`
wide float (W-bit normalized significand over 32-bit limbs,
`int32` exponent) with `wf_mul`, `wf_addsub`,
`wf_normalize` (truncate/round-away), `wf_from_entry`
(384-bit floor entries truncated to stage limbs); the
three-stage loop 160/256/384 with one generated table; the
interval decision (`trig_decide`: pack A-Ek and A+Ek
endpoints through the existing mode-complete pack, require
bit *and flag* agreement) with `trig_pack_wf` /
`trig_pack_big` exact-endpoint packing; `msf_decode`
extraction; the specials skeleton (`msf_nan_delivery` call
site shape, zero branches via `msf_pack_generic`); the
`DEF_TRIG`-style one-line per-format wrappers keeping all
three formats in one TU. From the generator: `floor_entry`
(exact 384-bit floors, per-entry Fraction proof), the
bracket-stability pattern for irrational constants (pi
there; ln2/ln10 here - computable by our own mpmath side,
bracket-checked at two precisions, emitted as integer
limbs, never decimal literals), `tail_terms`/`tail_exp`
exact-rational tail bounds, and the `scalar_ek_exp`
recurrence *shape* (one truncating op <= 2^(1-W), Horner
amplification with per-family ratio bounds, 9-bit safety
margin, generator-asserted at generation time). Taylor
coefficients for exp are again exact rationals (1/k!); the
atanh coefficients 1/(2k+1) likewise. Net: the trig
parcel's machinery is the right substrate; no new wide
type, no fourth stage, no pack changes.

What is genuinely new, per family:

1. **Signed results.** Shipped `wf_t` values are
   *positive only* (trig folds signs out before the
   kernel). exp/log cannot fully do that: log results
   change sign at 1, the m1/p1 corrections change sign
   with x. Cheapest faithful extension: keep wf positive
   and carry a separate sign through the small number of
   signed compositions (k + t for log, x + c for tiny
   m1/p1), as the kernel already does with `result_sign`;
   the polynomial cores stay positive (exp(u) for u in
   [-ln2/2, ln2/2] via exp|u| and, for u<0, the delta form
   1-exp(u) > 0 - one extra series shape, same trick as
   trig's delta branch). No signed-wide-arithmetic rewrite.
2. **Pack composition** (the generalization of
   `trig_pack_one_minus`): exact pack-scale formation of
   (a) integer + wide correction (log family: k + log_b(m),
   including sticky from a correction far below the
   integer's ulp - the 267-to-973-bit attractor cases);
   (b) 1 + m1-form and x + correction (exp near 1, tiny
   m1/p1 identity class); (c) 2^n * v - 1 (exp2m1 at
   moderate/large n: pack (v - 2^-n) at exponent n with
   sticky when 2^-n falls below the wide ulp). One new
   helper family (~120-180 lines) sharing the
   `trig_pack_big` exact-endpoint core; interval decision
   applies to the composed endpoints identically.
3. **Wide division** (log families only): s = (m-1)/(m+1).
   Newton reciprocal from existing wf_mul/wf_addsub with a
   small seed table or bit-hack seed (~80-120 lines + two
   Ek terms), or long-division by limbs; priced in the
   log2 bundle. log10/log avoid a second division: the
   base change is a multiply by a generated reciprocal
   constant (1/ln10, 1/ln2 floor entries), charged to Ek
   like any table constant.
4. **Constant-factor reductions** (rank 7-8 families):
   exp: k = round(x * log2(e)), r = x - k*ln2 with ln2
   split hi/lo so r is exact-enough by construction
   (reduction error charged in Ek; k range is small since
   |x| <= ~710 f64 before the overflow cut, so no
   Payne-Hanek class problem - ln2 to stage width plus
   one hi/lo split suffices, but the parcel proves it).
   exp10: same with log2(10)/ln10 and |r| <= ln10/2
   (kernel series is longer - Section 6 term counts - or
   reduce exp10 through exp2 machinery: 10^x = 2^(x*log2
   10) with the product formed in wide arithmetic and the
   exp2 split applied to the *wide* argument; the parcel
   chooses, both are priced in the same band). log/log10:
   log2 kernel then multiply by ln2 or log10(2) constant.
5. **Exact exponent cuts** (all exp forms): overflow
   (e.g. exp2: x >= 1024 decided on decoded integers,
   boundary strip 1023 <= x < 1025 decided by the kernel
   interval at that exponent), underflow-to-zero
   (exp2: x < -1075 exact cut delivering 0 or u by mode;
   x = -1075 the tie branch), m1 saturation
   (base^x below half the ulp below 1: deliver -1 or its
   neighbour by mode - an integer-threshold comparison on
   the reduced exponent, per format). All cuts are integer
   comparisons on decoded (sig, exp); the parcel derives
   each threshold as an exact rational in its generator
   (no floating literals).
6. **Exact/tie branch tables** (Section 2.3) and the
   associated inexact-flag rule - new *proof* burden per
   function, small code.

Specials burden per Clause 9.2 (S1 extracts, Table 9.1 +
9.2.1 as read): common to all 12 - sNaN signals invalid and
delivers qNaN; qNaN delivers qNaN (no 9.2.1 exceptions for
these 12, so wholesale NaN delivery survives, with
infinity *not* invalid: the trig call site's inf-invalid
argument becomes 0 and infinities fall to explicit
branches). exp/exp2/exp10: f(±0) = +1, f(+inf) = +inf,
f(-inf) = +0, no exceptions; domain all reals; overflow +
underflow listed. expm1 family: f(+0) = +0, f(-0) = -0,
f(+inf) = +inf, f(-inf) = -1, no exceptions. log/log2/
log10: domain [0, +inf]; f(±0) = -inf + divideByZero,
f(1) = +0, f(+inf) = +inf, x < 0 invalid + qNaN; no
overflow/underflow listed (results bounded, pack decides
any tininess). logp1 family: domain [-1, +inf];
f(±0) = ±0, f(-1) = -inf + divideByZero, f(+inf) = +inf,
x < -1 invalid; underflow listed. That is 4 specials shapes
for 12 functions - materially cheaper than trig's
per-cell settled tables, and every cell above is quoted
from the extracts, not inferred.

## 5. Oracle execution verification (Step 0b discipline)

The brief requires any *executed* foreign function to be
verified per `scratch/tier2-oracle-0b/report.md` (the
`cr_cospif` precedent). I executed 24 units (12 functions x
binary32/64; binary16 not executed - nothing below relies
on it). Build: `gcc -O2 -frounding-math -ffp-contract=off`;
20 units clean under `-std=c11`; binary64 exp/expm1/exp2/
exp10 need `-std=gnu11` (asm keyword; dialect flag only,
Step 0b B.3 precedent). Link needed one shim of mine
(`cm_shim.c`): mingw libm lacks C23 `roundeven`/
`roundevenf`, referenced by the exp10/exp10m1 units;
implemented as nearbyint under saved/restored FE_TONEAREST
(mode-independent ties-to-even, no inexact - the C23
contract). Disclosed because it is the one place my code
sits inside the foreign execution environment; it decides
no margin and touches only those two functions' smoke
cells (their smoke outcomes are clean except one f64 RN
cell also seen without the shim in exp2m1 - not shim
shaped).

### 5.1 Smoke design and adjudication

Cases (`cm_smoke.py`, `cm_harness.c`, drivers
`run_cm_smoke.sh`; logs `out/smoke_cmp.log`,
`out/adjudicate2.log`): 1,024 regular normals per
function/format (directed anchors + seeded randoms,
domain-filtered, exp-family |x| <= 64; no zeros,
subnormals, infinities, or NaNs - the Step 0b fences) x
{12 functions} x {f32, f64} x 4 modes = 98,304 comparisons
against my MPFR 320-bit wide-then-narrow reference. Raw
result: 90,288 agree, 8,016 disagree - but the
disagreements indict *both* sides, which is why they were
all adjudicated by a third, stable-form route
(`adjudicate.py`: mpmath at dps 450, exp forms via
1 + expm1-form exact Fractions, p1 forms via direct
log1p; MPFR never voted, the foreign binary never decided).

Adjudicated outcome, by class:

- **Plain exp forms, binary64 directed (3,073 cells: exp
  979, exp2 1,056, exp10 1,038): every cell adjudicated
  foreign-RIGHT, my
  320-bit reference wrong.** Mechanism: for tiny |x| the
  true result is 1 ± 2^-k with k > 319; the 320-bit wide
  value collapses to exactly 1, so the reference answered
  1 in directed modes where the correct answer is
  1 ± ulp. This is the Section 2.4 trap firing on my own
  reference. It does not touch the margin table (audited
  in 2.4) but it retires naive 320-bit narrowing as a
  smoke/vector reference for these families.
- **expm1 / logp1 directed (both formats): foreign-WRONG
  at tiny inputs, massively.** cr_expm1f: U 791/791
  disagreeing cells foreign-wrong, Z 366/366; cr_log1pf:
  D 636/636, Z 318/318; binary64 same shape (expm1 U/Z,
  log1p D/Z), including NEITHER cells where the foreign
  answer is 1 ulp past the truth on the far side from my
  (also wrong) 320-bit reference - e.g. expm1 f64 Z at
  0x820887c03f078713: foreign ...711, MPFR-320 ...713,
  truth ...712. All adjudicated examples are tiny-input
  cases (f(x) ~ x regime) with 1-2 ulp errors. Whether
  this is an upstream directed-mode defect or a Windows
  host/build artifact (the upstream README's fenv caveat
  Step 0b recorded) is undecided from inside these fences;
  the deciding experiment is the same one Step 0b priced
  (documented `./check.sh` on Linux, half-day class).
- **RN: four cells foreign-wrong, all subnormal-result
  1-ulp at tiny inputs** - cr_expm1f 8 cells, cr_exp2m1
  (f64) 1, cr_exp10m1 (f64) 1, cr_log1p (f64) 2 (the last
  also decided only after the dps-450 stable-form fix;
  first-pass dps-200 adjudication mislabelled its class -
  recorded in `out/adjudicate.log`, superseded by
  `adjudicate2.log`). Everything else RN agrees:
  24,564/24,576 RN cells.
- Clean everywhere in this sample: exp2m1, exp10m1
  directed (both formats), log/log2/log10/log2p1/log10p1
  all modes, plain exp forms f32 all modes (320 bits is
  deep enough at f32 scales that my reference never
  collapsed and no foreign defect showed).

### 5.2 What parcels may rely on

- Foreign RN execution as a *pre-screen* for all 12 at
  f32/f64, with every disagreement routed to a precision-
  adaptive MPFR decision; expect ~1 per 10^4 false alarms
  in the subnormal-result corner for the four cells above.
- Foreign directed execution for exp2m1/exp10m1/log/log2/
  log10/log2p1/log10p1 (sample-clean, all modes) and for
  plain exp forms - in all cases corroboration only.
- **Not** foreign directed expm1/logp1 on this host/build,
  for anything. Their f32 exhaustive differential runs
  MPFR-decided in directed modes without a pre-screen
  (priced as such in Section 7), or waits for the Linux
  documented check. This is fence F1 on the
  exp/expm1 and log/logp1 bundles.
- Not any foreign binary for specials/flags/subnormal
  inputs (upstream fences its own scope to regular
  numbers; untested here by design), and not the
  documented `./check.sh` on this Windows host
  (Step 0b B.3 priced failure stands).

### 5.3 Measured rates for gate pricing

Foreign RN in-process bench (20M evals, checksums
verified, `run_bench2.sh` / `out/bench2.log`): f32
24-144M eval/s (exp10f slowest at 24M; most ~100M), f64
18-52M/s. Pre-screening a full 2^32 RN sweep therefore
costs ~30-180 s per function - noise against the MPFR
side. MPFR wide-eval + 4-mode narrow, file sink
(`out/bench_mpfr3.log`): f64 exp 155k/s at prec 160,
125k/s at 320; log2 107k/89k; f32 exp 167k/130k.
Whole-set re-decision at prec 320 as run: 0.5-14 s per
function. Derived: binary32 exhaustive MPFR-decided pass
= 2^32 evals (wide value once, narrowed 4 ways; log
families ~half that after domain filtering) at ~130-170k/s
is 7.0-9.2 h per exp-family function, ~3.5-4.5 h per
log-family function, single-core, shardable by input
range; a production in-process generator (no %Ra
formatting, adaptive precision starting ~160) should land
near the top of that band or better - the trig spike
measured 300k/s for the same shape at f32, so plan
**4-7 h per function, 50-85 core-hours for all 12**,
unattended wall-clock, before kernel-side throughput
(unknown until kernels exist; measure on parcel day 1,
trig spike's standing warning). Binary16 exhaustive
generation at these rates: seconds per function.

## 6. First family: exp2/exp2m1, with log2/log2p1 second

Recommendation: first parcel = **exp2 + exp2m1** (survey
rank 5), second = **log2 + log2p1** (rank 6). Rationale:
exp2's reduction is exact with no irrational constant in
the argument path and no division anywhere - it exercises
the whole new pipeline (generator constants, composition
pack, cuts, tie branches, wc import, f32 exhaustive) with
the fewest new proof obligations; log2 then adds exactly
one new mechanism (division) plus the integer-composition
pack in full generality. Shipping exp2 alone first also
de-risks the rank-7/8 reductions, which are exp2/log2
kernels plus one constant each.

### 6.1 exp2 at binary64: worked sketch

Reduction (exact, integer-only; same shape as the trig
split in `trig_core`): decode |x| = sig * 2^e (sig < 2^53);
split x = n + f with n integer, f in [-1/2, 1/2] nearest-
integer form, f an exact dyadic with <= 54 significant
bits. 2^x = 2^n * 2^f; the 2^n factor is a final exponent
adjustment in the pack input, never a multiply. Kernel
argument u = f * ln2, |u| <= 0.34658; kernel value
v = exp(u) in [0.7072, 1.4143] by Taylor in u directly (or
in z = u^2 with the exp2m1 forms below). Exact branches
before the kernel: f = 0 with n in range (result 2^n
exact, including subnormal 2^n for -1074 <= n < -1022);
n >= 1025 or (n = 1024: kernel decides against the
overflow midpoint at exponent 1024 - measured overflow
hardness 1.0 bit, no cut needed inside the strip);
x < -1075 -> zero-threshold cut (deliver +0, or u in
roundTowardPositive, with underflow+inexact per the pack's
judgement on the cut values - flags from exact state, as
always); x = -1075 -> the exact tie u/2, delivered by
packing the exact value 2^-1075 through the pack (it knows
ties-to-even; inexact signals).

Series sizing (`kernel_sizing.py`, exact-rational tails):
terms to reach truncation 2^-T with |u| <= ln2/2: T=140: 29,
T=160: 32, T=200: 38, T=240: 44, T=300: 52, T=380: 63.
Stage term counts at the trig convention (tail <=
2^-(W+24)): stage 1 (W=160) ~35 terms, stage 2 (W=256)
~47, stage 3 (W=384) ~66. One table at 384-bit floors:
ln2 + 66 factorial-reciprocal entries + (for exp2m1) the
delta-form reuse of the same entries; ~67 entries x 52 B
~ 3.5 KB, all formats (trig's table is 1.3 KB for 45
entries at 28 B in the spike's sizing; the shipped trig
table format is 12 limbs + exponent per entry).

Error budget sketch (parcel proves the integers; shape
and magnitudes here): per truncating op eps = 2^(1-W).
e_ln2 <= eps (floor entry at stage width), e_u <= 3 eps
(one multiply + constant), Horner over the exp series:
partial sums bounded by exp(0.3466) < 1.415 for u > 0; for
u < 0 evaluate the delta form instead (below) so all
Horner terms stay positive-bounded by 1/(1-|u|/(k+1))
ratios - amplification < 4 eps per step, 35 steps, plus
tail 2^-(W+24) and coefficient floors 35 eps. Relative
budget Ek(W) ~ 2^-(W-9) class after the generator's
standard 9-bit reserve: Ek1 ~ 2^-150, Ek2 ~ 2^-246,
Ek3 ~ 2^-374. Demand from Section 2.1: plain cases need
error < 2^-(53+60.54) = 2^-113.6 relative (v in [0.71,
1.42], binade ulp tracks v to within a factor 2, charged
as 1 bit): stage 1 decides every observed plain f64 case
with ~36 bits to spare; stage 2 decides plain extra up to
~190; stage 3 to ~318. At f32 the same stages need
2^-(24+extra): stage 1 covers extra to ~125. Leg (c)
termination on the published-completeness reading: final
undecided is unreachable if the true plain gap is at most
~318 bits - 4.6x the measured maximum - with attractor
classes removed by construction (next paragraph), which
is a strictly more comfortable margin than the trig
parcel shipped with (there: decided to ~140-190 against a
measured 58.6).

exp2m1 shapes (all composition, no new series): let
m = 2^f - 1 = expm1-form of the kernel: m = u * M(u) with
M the expm1 Taylor ratio (positive series), |m| <= 0.4143.
For x >= 0 (n >= 0 in the split, f signed): result =
2^n * (1 + m) - 1 = 2^n * (m + (1 - 2^-n)) - pack the
bracket exactly at pack scale: for n = 0 it is m itself;
for n >= 1, 1 - 2^-n is an exact dyadic with n bits,
added to the wide m by the composition helper with
sticky; for n > W the 2^-n term is pure sticky of known
sign (the 267-bit integer cases live here: 2^320 - 1 is
decided by m = 0 exactly, f = 0 branch, tie analysis in
Section 2.3). For x < 0: result = -(1 - 2^x), computed as
delta = 1 - exp(u_total) where u_total = x * ln2 in
(-inf, 0): split x = n + f as before, delta =
1 - 2^n * v with n <= -1: = (1 - 2^n) - 2^n * m, both
terms positive, composed at pack scale; saturation cut
when 2^x < 2^-54 (f64): delta within 2^-54 of 1, result
-1 or its upper neighbour by mode (M1SAT class, 65 cases
measured, max RN extra in-class 48.86 also decided by the
same composition before the cut strip).

### 6.2 log2/log2p1 at binary64: compact sketch

Decode x = 2^k * mm, mm in [1, 2), sig exact. Recentre:
if mm^2 >= 2 (exact integer compare sig^2 vs 2^(2p-1)),
k += 1, mm /= 2 (exponent-only): mm in [2^-1/2, 2^1/2).
s = (mm - 1)/(mm + 1), |s| <= 0.17158, via the new wide
division; t = (2/ln2) * atanh(s) = (2/ln2) * s * A(s^2),
A = sum s^(2j)/(2j+1). Sizing (`kernel_sizing.py`): odd
terms for 2^-T: T=140: 27, 160: 31, 200: 38, 240: 46,
300: 58, 380: 74 (without recentring, s < 1/3 needs
62 at T=200 and 118 at 380 - recentring is worth its one
exact compare). Result = k + t by composition pack
(Section 4 item 2a): endpoints k + (t ± Ek) formed
exactly at pack scale with sticky - this is what decides
the 971-bit attractor tail (x = 2^k exactly makes t = 0
and the branch exact: log2(2^k) = k, also for subnormal
x = 2^-1074: k = -1074 exactly by construction). Demand:
plain max 56.37 -> stage 1 with ~40 bits spare. Exact
branches: x = 1 (+0), x a power of two (k, exact), poles
and domain per Section 4. Special care: mm - 1 in the
s numerator is exact (mm is a decoded dyadic; for mm near
1 the numerator keeps full relative precision because
both are wide floats - the log2-near-1 relative accuracy
is structural, not a branch).

log2p1: form w = 1 + x exactly in decoded integer form
(sig arithmetic on a common exponent; x in (-1, -1/2]
gives w with up to 1075 significant bits in the worst
subnormal corner - carried as (sig128+, exp) into the
same log2 path, whose decode-equivalent split handles the
wide significand by taking stage-width top bits plus
sticky *into the s division error term* - one extra Ek
line the parcel must not forget). Tiny |x| <= 2^-8 class:
result = x * (1/ln2) * B(x) computed relatively and
composed as x * C + correction at pack scale (the
identity-attractor path; measured in-class RN max 62.07
needs ~110 correction-relative bits - stage 1). Pole
x = -1 exact; near-pole w subnormal-tiny flows through
the general path (log2 of the smallest w is ~-1074,
normal result, no cut needed).

## 7. Price, order, risks, stop conditions

Hands-on hours per bundle (two functions x three formats
x four modes, C-754; includes generator + Ek proof work,
kernel, specials, vector generation and import, f16
exhaustive + f32 exhaustive supervision, planted
independent verification and negative controls, board
slots; excludes unattended f32-exhaustive wall-clock,
Section 5.3, and lead review time). Basis: the trig spike
priced its two-function bundle at 3-5 working days
(kernel TU 700-900 lines) from a standing start; these
bundles reuse that TU pattern but each adds the items
noted, and vector volume is 2-17x the wc-import size.
Estimates are planning bands, not measurements.

| # | bundle | new machinery it pays for | hours |
|---|---|---|---|
| 1 | exp2, exp2m1 | exp/log generator (ln2 bracket floors, factorial tables, Ek recurrences), pack composition (b)+(c), exponent cuts, tie-branch machinery, 12-fn-capable MPFR vector pipeline (adaptive precision), f32 exhaustive harness | **55-75** |
| 2 | log2, log2p1 | wide division (+Ek), integer composition (a) in full, 1+x wide formation | **40-55** |
| 3 | exp, expm1 | ln2 hi/lo reduction chain; near-1 directed pocket (composition path or stage-2 reliance - decide in design); F1: f32 directed legs MPFR-only | **32-44** |
| 4 | exp10, exp10m1 | ln10/log2(10) chain; H1 token hygiene decision | **28-40** |
| 5 | log, logp1 | 1/ln2 multiply chain; logp1 tiny-RN design point (100.8); F1 directed fences | **34-46** |
| 6 | log10, log10p1 | log10(2) chain; largest plain RN (69.77) - stage discipline only | **30-42** |

Programme total: **219-302 hands-on hours** (~6-8 working
weeks at full focus) + 50-85 core-hours of unattended
binary32 exhaustive compute (shardable; ~1-2 nights per
bundle on one host, less if sharded). Dependency order:
1 -> 2 -> {3, 5} -> {4, 6}; bundles 3-6 are independent of
each other once 1-2 land (exp10 wants exp's chain or
exp2's - either exists after 1; log10 wants log2). No
bundle's leg (a) is missing, so **no family needs to stay
deferred for worst-case-publication reasons**; deferral
levers, if the schedule needs them, are taste, not
evidence: log10/log10p1 last (least workload pull,
largest wc import at 1.28M lines), then exp10 pair.

Risks and stop conditions:

- R1 (leg-c authority): binary64 termination rests on the
  fetched full-range completeness claim plus 4.6x width
  headroom. Stop condition per bundle: if a parcel finds a
  plain-class input (directed/seeded leg-b volume) whose
  extra exceeds the final stage's reach (~318 f64), the
  bundle refuses - do not narrow the claim silently
  (SF-1 parity rule). Expected: never fires; it is the
  falsifiable form of the bet.
- R2 (generator precision trap): any non-adaptive
  fixed-precision reference produces wrong vectors near
  attractors *silently* (measured twice here). Gate each
  bundle's generator with a two-precision agreement check
  and a planted near-attractor canary set (tiny inputs
  with hand-derived directed answers like
  expm1(±2^-1074) directional outcomes) watched to fail
  when perturbed - negative control, survey 4.6.4 shape.
- R3 (composition sticky): the 971-bit attractor tail
  lives or dies on sticky correctness in the new
  composition helper. Planted verification must include
  exponent-scaled attractor families (x = 2^k for
  log2p1 across the full exponent range; x = ±2^-j for
  m1/p1) decided by exact rational arithmetic in the
  verifier, not by another wide-float path.
- R4 (tie completeness): Section 2.3's branch enumeration
  is a proof obligation per function; a missed tie branch
  shows up as a final-stage undecided input in wc
  replays - treat any final-undecided counter > 0 as a
  stop, never as a fallback pack (the trig kernel's
  defined fallback is *not* acceptable here because ties
  are reachable).
- R5 (foreign corroboration gaps): F1 cells have no
  directed pre-screen; if the Linux documented check
  later clears them, re-price bundles 3 and 5 down by
  ~4-6 h each (supervision, not correctness).
- R6 (wc import hygiene): H1's 8 tokens, the 6
  specials-anchor tokens per file, and the UTF-8 comment
  bytes that broke a strict-ASCII census on first pass
  here (`wc_census.py` history): the import path must be
  byte-tolerant in comments and exact in data, with the
  exclusions itemized in the parcel ledger.
- R7 (host rates): f32 exhaustive wall-clock assumes the
  kernel side is not the bottleneck (unmeasured) and a
  host not paging under a sibling's 43 GB process
  (Section 0); parcel day 1 re-benchmarks both before
  committing the schedule.

## 8. Artefacts and unresolved

Artefacts (all under `scratch/sf2-explog/`): this report;
scripts `wc_census.py`, `wc_inputs.py`, `mpfr_redecide.c`,
`aggregate.py`, `attractor.py`, `f32_inputs.py`,
`spot_mpmath.py`, `spot_fix1.py`, `exact_recheck.py`,
`kernel_sizing.py`, `cm_harness.c`, `cm_shim.c`,
`cm_smoke.py`, `adjudicate.py`, drivers `probe_env.sh`,
`fetch_worst.sh`, `run_f64_wc.sh`, `run_f64_fix.sh`,
`run_f32.sh`, `run_attractor.sh`, `run_exact_hp.sh`,
`cm_symbols.sh`, `cm_retry.sh`, `run_cm_smoke.sh`,
`run_bench2.sh`, `run_bench_mpfr3.sh` (+ diagnostic
`run_bench_diag.sh`), and `out/` logs (census, inputs,
per-function redecide, aggregates x3 precisions,
attractor, spots, smoke, adjudications 1-2, benches,
fetched pages). Helper diagnosis scripts `find_nan*.py`
are retained as the record of the inf//10 aggregate bug
and its fix.

Unresolved (priced or named, not silent):

1. True binary64 gaps vs measured maxima: bounded by the
   completeness authority only (Section 1). Re-deriving a
   gap from scratch (BaCSeL-class search) is out of scope
   and unpriced; the 4.6x stage headroom is the hedge.
2. F1 upstream-vs-host question for cr_expm1/log1p
   directed defects, and the 12 RN subnormal-result
   cells: undecided inside the fences; deciding
   experiment priced at the Step 0b Linux trip (half-day
   class). Also unexecuted: all binary16 foreign units
   (~15 min per function with this harness when a parcel
   wants them; nothing here relies on them).
3. H1: status of the 8 non-binary64 tokens in
   exp10m1.wc - cannot be resolved without reading
   context the fences exclude; parcel import decides and
   records.
4. Kernel host throughput and RP2040 latency/stack for
   the exp/log kernels: unmeasured (no kernel exists);
   stage-3 fallthrough rates on real inputs will set
   board numbers. Wide-division cost on target is the
   largest unknown in the log bundles' runtime.
5. Ek integers, term counts per stage, cut thresholds,
   and the exact composition-helper error terms: sketched
   with magnitudes in Section 6, proof-grade values are
   parcel work via the generator recurrence (budgeted in
   Section 7's bands).
6. Binary32 true worst gaps: only lower bounds measured
   (Section 3); the exhaustive leg supersedes the
   question for the shipped binary, but anyone wanting
   the *number* (e.g. to slim stage widths at f32) would
   extract it from that same exhaustive run by recording
   near-boundary cases - free by-product if specified
   before the run, noted here so parcels can ask.
7. The 5-char signed-letter tokens (2 per wc file):
   unparsed by exact discipline, presumed specials
   anchors; parcel import identifies them mechanically
   before relying on any specials coverage from wc files.
