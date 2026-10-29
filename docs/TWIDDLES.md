# TWIDDLES - the KissFFT Fork B twiddle-provenance derivation

This document is the complete self-contained record of how the
KissFFT Fork B twiddle provenance was derived and gated. It is
written so a competent reader can re-derive the gate from zero
without the workspace scratch. Scratch
(`scratch/parcel-w4kissfft/`, `scratch/tier2-kissfft/`,
`scratch/tier2-oracle-0b/`, `scratch/tier2-trig-spike/`) is
evidence; this document is the retained derivation. Numbers
appear only where the trail has them. Anything that could not
be re-derived from the sources is marked **unverified** rather
than smoothed over. No new claims are made here.

Sources: `scratch/parcel-w4kissfft/report.md`, `gate_main.c`,
`02b_gate.sh`, `03_controls.sh`, `out/` gate logs,
`patch_tree.py`, `01_extract_patch.sh`, `out/forkb.diff`,
`scratch/tier2-kissfft/report.md`,
`scratch/tier2-oracle-0b/report.md`,
`scratch/tier2-trig-spike/report.md`,
`ledger/parcel-w4kissfft.md`, `docs/studies/SF-1.md` Sec. 6.4,
`docs/BOARD.md` (Fork B entry), `docs/RECORD.md` (Step 2c
paragraphs). KissFFT source itself is not copied here beyond
naming the three patch sites and our fraction math; no
upstream code lines are quoted.

## 1. The claim and its exact scope

At the gated power-of-two sizes only, N in {256, 1024, 4096},
double configuration: the board twiddles are the correctly
rounded values of the exact mathematical twiddles, generated
at runtime on-device; FFT outputs are bit-identical host vs
board under the same patched source. The workload is
KissFFT 131.2.0 with one named change (Fork B): twiddle
generation takes exact cycle fractions into correctly rounded
`sinpi`/`cospi` instead of radian phases into `sin`/`cos`.
"Unmodified KissFFT" is never claimed; the patch is named in
the firmware header, the CMake comment, `docs/BOARD.md`, and
here. KissFFT source never enters this repository
(fresh-extract + patch by script in scratch).

Tables covered: complex FFT twiddle tables at each gated N,
and, for real-input sizes, the half-size substate twiddles
plus the super-twiddles (`st->super_twiddles`, N/4 entries
per real plan). Forward and inverse plans are both gated at
N=1024 and N=4096; at N=256 the gate ran forward plans only
(see the census in Section 3).

Why the exact cycle fractions make the twiddle argument
exact at these sizes: every sinpi/cospi argument the patched
alloc computes is a dyadic rational - a small integer divided
by a power of two (Section 2) - and is therefore represented
exactly in binary64. A correctly rounded sinPi/cosPi of an
exact argument is the correctly rounded value of the exact
mathematical twiddle. This argument is power-of-two-only,
which is why the claim is gated to these sizes. Contrast the
precompute variant the tier2 study priced and rejected as an
earning route: twiddle tables generated offline against MPFR
and pinned per N (the IAS15 coefficient pattern) run on Tier 1
with zero new core operations and earn nothing - they merely
consume. Fork B earns its keep precisely because the
twiddles are generated at runtime from exact arguments.

What is explicitly NOT claimed:

- Other sizes. For non-power-of-two N the cycle-fraction
  argument is itself a correctly rounded binary64 division,
  not an exact value (SF-1 Sec. 6.4 restate rule); no public
  sentence covering those sizes may reuse this claim without
  restating it, and no such size was gated.
- The float configuration. It costs a second scalar build
  plus float wrappers the brief did not ask to earn; it was
  not done.
- Unmodified KissFFT. The three-site patch below is the one
  named change; every claim sentence names it.
- Tolerance comparisons. No numpy/FFTW-style tolerance
  reading is called byte-identical; analytic anchors are
  exact checks, not tolerances.
- Execution accuracy. This gate covers the twiddle tables
  only - the inputs to the FFT butterflies, not the
  butterfly arithmetic (which is Tier 1 `add`/`sub`/`mul`,
  already gated elsewhere).

## 2. The derivation chain

### 2.1 The three patch sites and the phase-to-fraction algebra

The patch is applied by `patch_tree.py` (exact-string
replacement, hard failure on any non-match); `out/forkb.diff`
touches exactly these three sites:

**(a) Complex alloc.** The radian phase `-2*pi*i / nfft`
becomes the cycle-fraction phase `-2.0*i / nfft`. Evaluated
left to right in binary64: `-2.0*i` is an exact small integer
(|i| <= 4095, |2i| <= 8190, far below 2^53); dividing it by
the power-of-two `nfft` is an exact exponent shift. So the
stored `phase` is the exact dyadic value -2i/N. The twiddle
is cos/sin of 2*pi times (phase/2), i.e. exactly
`cospi(phase)`/`sinpi(phase)` with `phase` as the 2c-form
argument: cos(2*pi*c) = cospi(2c).

**(b) Real super-twiddles.** The radian phase
`-pi * ((i+1)/nfft + .5)` becomes `-((i+1)/nfft + .5)` (the
radian phase was pi times this, so the remainder is exactly
the sinpi/cospi argument). With m = N/2: `(i+1)/m` is exact
(small integer over a power of two); adding `.5` is exact by
the carry analysis below; negation is exact. As a single
rational the argument is -(2(i+1)+m)/(2m) with denominator
2m still a power of two, hence dyadic-exact. The
`if (inverse) phase *= -1` lines are unchanged, and negation
is exact.

**(c) Trig dispatch.** The floating-point branch macros
`KISS_FFT_COS`/`KISS_FFT_SIN` call `cospi`/`sinpi` (declared
in the header patch) instead of `cos`/`sin`. The fixed-point
and SIMD branches are untouched - they are never compiled
here (`kiss_fft_scalar` is `double`).

Carry analysis for site (b): adding `.5` to `(i+1)/m` can
carry out of the fraction field (e.g. 0.75 + 0.5 = 1.25),
but both operands are dyadic and the sum lies in [0.5, 1.5),
needing at most 13 significant bits (k+1 for m = 2^k <= 2048
plus the integer bit) - far inside the 53-bit significand,
so the addition is exact regardless of the carry. The same
bit-counting covers site (a): `-2.0*i` needs at most 14 bits
including sign. No rounding happens anywhere in the argument
construction at the gated sizes.

No-fused-multiply requirement: none of the three argument
expressions contains a multiply-add - site (a) is
multiply-then-divide, site (b) is divide-then-add, negation
is free - so there is no contraction site for an FMA-capable
build to reshape even in principle. Every build in the trail
additionally pins `-ffp-contract=off` (and `-fno-fast-math`);
the negative controls in Section 4 show what happens when
contraction is deliberately switched on.

### 2.2 Runtime-table extraction from the actual alloc path

The gate (`scratch/parcel-w4kissfft/gate_main.c`, reproduced
as `demo/twiddle_gate.c`) `#include`s the patched
`kiss_fft.c`/`kiss_fftr.c` translation units directly, calls
the real `kiss_fft_alloc` / `kiss_fftr_alloc` at runtime, and
reads `cfg->twiddles`, `cfg->substate->twiddles`, and
`cfg->super_twiddles` out of the returned state. What is
compared is therefore the actual runtime-produced table
contents - the same bytes the FFT execution path consumes -
never a side recomputation of what the tables "should" be.
The build wraps `sinpi`/`cospi`/`floor` into the
muse-softfloat core (`--wrap=sinpi,--wrap=cospi,--wrap=floor`,
`-ffp-contract=off`), so the tables under inspection are the
library's own correctly rounded outputs.

### 2.3 The field census: 8,856 per the gate loops

Each stored twiddle contributes 2 fields (r and i). Reading
the loop bounds of the gate driver:

| Leg | Indices checked | Fields |
|---|---|---|
| N=1024 complex fwd+inv, exhaustive | 2 dirs x 1024 | 4096 |
| N=1024 fftr fwd+inv, exhaustive (sub 512 + super 256 per dir) | 2 dirs x (512 + 256) | 3072 |
| N=4096 complex fwd+inv, stride 37 (every 37th index plus the last: 112 per dir) | 2 dirs x 112 | 448 |
| N=4096 fftr fwd+inv, stride 37 (sub 57 + super 29 per dir) | 2 dirs x (57 + 29) | 344 |
| N=256 complex fwd only, exhaustive | 256 | 512 |
| N=256 fftr fwd only, exhaustive (sub 128 + super 64) | 128 + 64 | 384 |
| Total | | **8856** |

Footnote on the stride-37 counts: indices kept are those
with `i % 37 == 0` plus the final index when 37 does not
divide it (4095 % 37 = 25, 2047 % 37 = 12, 1023 % 37 = 24,
so each leg gains its endpoint): floor(4095/37)+1+1 = 112
complex per dir; floor(2047/37)+1+1 = 57 substate and
floor(1023/37)+1+1 = 29 super per dir. Recomputed here from
the driver source; the re-run in Section 5 prints the same
total independently.

## 3. The decider

Each table field is decided by MPFR's native `mpfr_sinpi` /
`mpfr_cospi` at 256-bit precision, applied to the exact
rational argument: `p` is set as a small integer and divided
by `q` (both powers of two at our sizes), each step exact,
so the 256-bit input is the exact cycle fraction. Delivery
to binary64 is `mpfr_get_d` in round-to-nearest - the mode
the workload links. Two properties make the native
sinpi/cospi oracle the recorded one:

- Exact at quarter points. At arguments where the true value
  is exactly 0, +-1 (and signed zero matters),
  `mpfr_sinpi`/`cospi` deliver it exactly. The `p == 0` case
  keeps the patched expression's signed zero explicitly:
  forward plans pass `neg_zero` (phase `-2.0*0/n` is `-0.0`),
  inverse plans negate it to `+0.0`.
- Recipe authority for the binary64 delivery. Trust that
  MPFR narrowing to binary64 is sound at boundaries rests on
  the Step 0b recipe - `emin = -1073`, `emax = 1024`
  (p = 53), `mpfr_check_range` on the narrowing path, zero
  guard - proven for binary64 in the trig spike at 120/120
  exact-rational cross-checks (68/68 set-path, 52/52
  operation-path), in all four rounding modes. The gate
  itself checks round-to-nearest; the recipe's other three
  modes are not exercised by this workload and no claim here
  needs them.

Margin note (derived from two trail numbers, not a new
measurement): the hardest genuine f64 sinPi/cosPi input in
the full published worst-case sets needs 58.6 extra bits
(trig spike), i.e. at most 53 + 58.6 = 111.6 significand
bits to decide; the 256-bit intermediate carries ~144 bits
of margin above that. The trail contains no written
double-rounding bound for the 256-to-53 narrowing step, so
that bound is **unverified** - what the trail does contain
is the 256-bit choice plus 0 mismatches over the 8,856
fields.

### 3.1 The failed first oracle, kept as evidence

The first oracle attempt used `sin(pi_256 * x)` - sine of
pi-at-256-bits times the argument - and showed 29
mismatches, all oracle artifacts at exact quarter points
(ledger/parcel-w4kissfft.md results entry; code comment in
the driver). No script or log of that run survives in the
trail, so the count 29 itself is ledger-recorded and
**unverified** by re-run. The mechanism, however, was
re-derived for this document with a probe
(`scratch/parcel-w5twiddledoc/first_oracle_probe.c`): at
exact quarter-point arguments in [-2, 2], `sincos` of
(pi_256 * x) evaluated at 256 bits returns tiny nonzero
values (e.g. `0x2fe452821e638d01`, about 1e-77, and
`0x300452821e638d01`) where the native `sinpi`/`cospi`
is exactly signed zero:

```
ARTIFACT sin(-8/4): sincos(pi256*x)=300452821e638d01 native=8000000000000000
ARTIFACT cos(-6/4): sincos(pi256*x)=3000c21e6935563f native=0000000000000000
ARTIFACT sin(-4/4): sincos(pi256*x)=aff452821e638d01 native=8000000000000000
ARTIFACT cos(-2/4): sincos(pi256*x)=2fe452821e638d01 native=0000000000000000
ARTIFACT cos(2/4): sincos(pi256*x)=2fe452821e638d01 native=0000000000000000
ARTIFACT sin(4/4): sincos(pi256*x)=2ff452821e638d01 native=0000000000000000
ARTIFACT cos(6/4): sincos(pi256*x)=3000c21e6935563f native=0000000000000000
ARTIFACT sin(8/4): sincos(pi256*x)=b00452821e638d01 native=0000000000000000
```

pi_256 differs from true pi by ~2^-256, so pi_256 * x at a
quarter point misses the exact multiple of pi/2 by ~1e-77
and its sine/cosine misses the exact zero by the same
order - while the true twiddle component there is exactly
zero. The comparison then fails on bits that are the
oracle's error, not the table's. This failure is evidence
about oracle choice - the kind of thing that gets lost -
and is why the recorded decider is native sinpi/cospi.

## 4. Results, negative controls, and the proof boundary

Recorded gate result (`scratch/parcel-w4kissfft/out/gate.txt`,
MPFR 4.2.2):

```
mpfr 4.2.2
PROVENANCE checked_fields=8856 mismatches=0
```

N=1024 exhaustive forward+inverse including fftr
super-twiddles, N=4096 stride-37 sampled, N=256 exhaustive
forward-only. The 12 host-proof hashes
(`out/hashes-main.txt`, identical rows in
`demo/expected-kissfft.txt`) are the bit-identity half of
the same claim; state sizes measured alongside
(4096: complex_state=65800 real_state=82208 cpx=16).

Negative controls, each watched (`03_controls.sh`; any
control not behaving as stated was a stop-and-escalate):

| Control | Result (recorded) |
|---|---|
| 1-ulp flip of one twiddle (8th... precisely the 1000th `sinpi` call, landing inside the N=1024 complex-fwd alloc) | only the `KF 1024 complex fwd` row changes |
| unpatched tree, radian alloc, host libm | all 12 KF rows differ |
| `-ffp-contract=fast` on baseline x86-64 (no FMA instruction) | 0 rows differ - recorded, not hidden: inert, as expected |
| `-ffp-contract=fast -mfma` (contraction operative) | all 12 rows diverge |
| analytic anchors (delta-flat-64, hand N=4/N=8 DFTs, bin-centred tone) | PASS |
| in-place aliasing (`fin == fout`) vs out-of-place | equal |

The 1-ulp control proves the hash comparison can see a
single twiddle bit; the `-mfma` control proves the
`-ffp-contract=off` fence is load-bearing rather than
decorative.

Boundary with the sinPi/cosPi correctness proof: this gate
decides twiddles *given* correctly rounded sinPi/cosPi - it
is not itself that proof. A gate that routed twiddles
through broken trig would still read 0 mismatches against a
broken decider; what makes 0 mismatches mean something is
the independent trig evidence: the Step 2c kernel parcel
(binary16 exhaustive differential, binary32 exhaustive
finite differential of 34,225,520,640 checks over 32 shards,
binary64 at 100% of the published worst-case inputs plus a
2^21-per-function seeded sweep, all MPFR-decided, zero
mismatches, zero final-undecided at any Ziv stage;
`ledger/parcel-w4trig.md`, `docs/RECORD.md` Step 2c kernel
paragraph). The kernel proof and this provenance gate meet
exactly at the `--wrap=sinpi,cospi` boundary: the kernel
proves the functions, the gate proves the tables built from
them.

## 5. Reproduction appendix

`demo/twiddle_gate.c` is the scratch gate driver verbatim
plus a header comment (what it needs, exact commands,
expected output). No source edits were needed to build it
against today's tree - checked 2026-10-29: `compat`
still provides `__wrap_sinpi`/`__wrap_cospi`/`__wrap_floor`
over the `msf64_sin_pi`/`msf64_cos_pi` core rows, and the
demo shim `demo/kissfft_host_shim.c` supplies the same
`msf_wrap_state`/bit-cast/trap contract the scratch
`host_shim.c` did.

Re-run procedure (Git Bash from the repository root; the
parcel's own run is `scratch/parcel-w5twiddledoc/run_gate.sh`
with `MSF_PYTHON` pinned to the workspace `.venv`):

```sh
# 1. Fresh patched tree (verifies patched-file sha256s itself):
V=.venv/Scripts/python.exe  # or $MSF_PYTHON
$V demo/make_kissfft_tree.py <pristine-KissFFT-131.2.0-dir> /tmp/kissfft-tree
# expect: FORKB-PATCH OK (3 sites; patched sha256 match the recorded values)

# 2. Build the gate against today's tree:
WT=.
CORE="$WT/src/msf16.c $WT/src/msf32.c $WT/src/msf64.c $WT/src/msf_flags.c \
  $WT/src/msf_wide.c $WT/src/msf_roundpack.c $WT/src/msf_string.c \
  $WT/src/msf_math.c"
gcc -std=c11 -O2 -Wall -Wextra -ffp-contract=off -fno-fast-math \
  -Dkiss_fft_scalar=double -I$WT -I$WT/compat -I/tmp/kissfft-tree \
  demo/twiddle_gate.c $CORE $WT/compat/msf_aeabi.c \
  demo/kissfft_host_shim.c \
  -Wl,--wrap=sinpi,--wrap=cospi,--wrap=floor -lm -lmpfr -lgmp \
  -o /tmp/twiddle_gate.exe

# 3. Run:
./tmp/twiddle_gate.exe   # from the repo root: /tmp/twiddle_gate.exe
# expect:
#  mpfr 4.2.2
#  PROVENANCE checked_fields=8856 mismatches=0
```

The parcel's own re-run (2026-10-29, fresh tree from
`demo/make_kissfft_tree.py` over the pinned pristine tree,
today's `wave5-twiddledoc` sources, MPFR 4.2.2) printed
`PROVENANCE checked_fields=8856 mismatches=0` - the same
field count and the same zero. Log:
`scratch/parcel-w5twiddledoc/out/gate5.txt`.

## 6. Provenance block

- KissFFT pin: tag `131.2.0`,
  `https://github.com/mborgerding/kissfft/archive/refs/tags/131.2.0.tar.gz`,
  archive SHA-256
  `205a8f6a448ef12b091f8ac6a514b5091bb5f6b0b543431ed75f673116cf5cbf`
  (re-measured 2026-10-28 at `out/archive.sha256`, matches
  the tier2-kissfft record; re-verified present at re-run
  time), licence BSD-3-Clause `4d6bcab46f27d6d0c878e8305d4bdcfe040d52bf6656b9771f04c9fb9902c0ed`
  (plus `COPYING` `a2840585...` in `out/licence.sha256`).
  Proposed `fetches.jsonl` row in the parcel report; landed
  row in `docs/metrics/fetches.jsonl`.
- Patched-file SHA-256 (recorded, enforced by
  `demo/make_kissfft_tree.py`, reproduced by the parcel
  re-run): `kiss_fft.c`
  `8fcc496897ce2844a08a8ca74268b28149bd3a8949fc31e78538151366062305`,
  `kiss_fftr.c`
  `b34ff3b21594c61e295f61bbf8a9fd86d6310fcceb459d07389c470ad848744f`,
  `_kiss_fft_guts.h`
  `42fd7132fdb19e986d66693a081d90239b19b9a9496f319e86510f5fe7be9402`.
- Original logs live at `scratch/parcel-w4kissfft/out/`:
  `gate.txt` (the 8856/0 line), `hashes-main.txt` (12 KF
  rows + SIZE lines + anchors), `hashes-main-2.txt`
  (rerun-identical), `hashes-flip.txt`,
  `hashes-unpatched.txt`, `hashes-fast.txt`,
  `hashes-fastfma.txt`, `forkb.diff`, `archive.sha256`,
  `licence.sha256`. Driver and scripts:
  `scratch/parcel-w4kissfft/gate_main.c`, `patch_tree.py`,
  `01_extract_patch.sh`, `02_host_proof.sh`
  (embodies `02b_gate.sh`), `03_controls.sh`.
- Oracle authorities: MPFR 4.2.2 (`mpfr 4.2.2` banner in
  both gate logs); the binary64 Step 0b recipe extension in
  `scratch/tier2-trig-spike/report.md` Sec. 1; f16/f32
  recipes in `scratch/tier2-oracle-0b/report.md` Sec. A.2.

Scratch is evidence; this document is the retained
derivation.
