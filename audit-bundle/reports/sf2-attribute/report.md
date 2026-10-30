PRICED-GO — land `roundTiesToAway` as the fifth public attribute as the FIRST SF-2 implementation parcel (before the algebraic and exp/log bundles, so they are born five-mode), after owner SF-2 consolidation; public `roundToOdd`: NO-GO (keep nonexistent; internal-only if a future kernel proves it needs it).

# SF-2 input study: fifth rounding attribute + roundToOdd verdict

Brief: `ledger/briefs/sf2-attribute.md`. Scratch only; no repo
changes (`git status` in muse-softfloat clean at close). Probes:
`scratch/sf2-attribute/{counts.py,mpfr_probe.c,mpfr_probe2.c,
string_ta_probe.c,rodd_check.py,run_probes.sh,run_probes2.sh,
run_probes3.sh}`, logs in `out/`. Git Bash, MSF_PYTHON pinned to
workspace `.venv` (Python 3.12.15), gcc 16.1.0 x86_64-w64-mingw32,
MPFR 4.2.2, pinned Berkeley TestFloat-3e in `scratch/oracles/`.
Tags: [M] measured here, [R] read in a named source, [A] analysis.

**Corrections to the brief's premises (load-bearing):**

1. `roundToOdd` is **not** "currently an internal pack mode used
   inside the trig kernel". It does not exist anywhere:
   zero hits for `odd` in `src/*.{c,h,inc}` + `include/*.h` [M];
   `msf_internal.h:14-20` has five internal modes (the four public
   + ties-to-away=4) and no odd mode [R]; `msf_math.c` decides
   correct rounding by packing proven interval *endpoints* under
   the caller's own `rm` (`trig_decide`, lines 551-577), not by
   round-to-odd [R]. The Clause 9 survey already recorded this
   (`scratch/tier2-clause9/report.md`, 4.3.3: "the shipped pack
   does **not** implement it"). RoundToOdd therefore prices as
   *build-from-scratch*, not *promote*.
2. Runner note: the brief names `tests/msf_runner.c`; the shipped
   runner is `tests/runner.c` (binary `msf_runner.exe`).

## 0. The surface, counted [M, out/counts.log]

`docs/COVERAGE.tsv` (822 rows): **255 attribute-carrying rows =
249 Tier 1 + 6 Tier 2** (`sinPi`/`cosPi` x 3 formats), all
implemented. By deciding authority: 39 berkeley, 216 mpfr-exact.
Families: add/sub/mul/div 27 each (3 berkeley homogeneous + 24
mpfr-exact cross-format), fma 81 (3+78), sqrt 9 (3+6),
convertFormat 9, convertFromInt 24 (12+12), scaleB 3,
roundToIntegralExact 3, four character conversions 3 each,
sinPi/cosPi 3 each. Separately, **51 named ties-to-away rows are
already public Tier 1 surface** (roundToIntegralTiesToAway 3,
convertToInteger{Exact}TiesToAway 24+24) — the *operation* is
shipped; only the *attribute* is missing. Clause 4.3 (S1 Sec.2):
five attributes defined, `roundTiesToAway` required only for
decimal; adding it for binary is a permitted extension with
standard-defined semantics, claimable per-row like the other four.

## 1. Kernel delta

### 1.1 Already done (the seam exists)

- `src/msf_internal.h:19` `MSF_IROUND_TIES_TO_AWAY = 4`, same
  numeric slot the public enum would take [R].
- `src/msf_roundpack.c:58-59` `round_inc` ties-to-away arm
  (`return guard` — increment iff discarded fraction >= half ulp),
  overflow-to-infinity included with the nearest modes at line
  118, and the flags-only unbounded-exponent tininess judge
  (lines 134-149) calls the same `round_inc(rm)`, so tininess
  under ta is mode-consistently judged [R].
- The runner already parses `ta` (`tests/runner.c:91`), the board
  harness too (`board/harness_main.c:50`), the dispatch passes
  `(msf_rounding_t)rm` unfiltered (`tools/gen_tables.py:255`),
  `tests/berkeley_ingest.py:31-32` already maps `ta ->
  -rnear_maxMag`, and committed pack vectors already carry 3,720
  ta lines (pack16/32/64, 5-mode since P0) plus 2 stray public-op
  ta lines in arith-f64.vec [M counts].
- Compat state is `msf_rounding_t`-typed (`compat/msf_wrap.h:21`)
  and AEABI wrappers pass `s->rounding` straight through
  (`compat/msf_aeabi.c:31ff`) — a fifth value flows with no
  wrapper change; zero-init still reads ties-to-even [R].

**Measured**: Berkeley level-1 ties-to-away vectors ingested and
replayed on the *current unmodified kernel* through the real
runner: f16_add, f32_mul, f64_add (46,464 each), f64_sqrt,
f64_to_f32, f32_to_f16, i64_to_f64, f64_mulAdd (6,133,248) —
**6,275,532 / 6,275,532 PASS, flags exact** (out/verify_ta.log).
The pack path — arithmetic, cross-checks homogeneous, FMA jam,
format/int conversion — is already ties-to-away-correct today.

### 1.2 The proof sketch, and where it breaks

Every attribute-taking operation rounds exactly once, and the
mode enters the delivered result only through (a) `round_inc`
in the shared pack, (b) overflow delivery in the pack, (c) the
exact-zero sign rule (positive except roundTowardNegative,
Clause 6.3 — the per-format files test only
`rm == MSF_IROUND_TOWARD_NEGATIVE`, e.g. `msf16.c:80,103`, so ta
is automatically right), and (d) integer-target rounding
helpers (`msf16.c:331ff`, `msf32.c:334ff`, `msf64.c:349ff` —
all already carry a `MSF_IROUND_TIES_TO_AWAY` case because the
named forms use them). Conversion (format/int), scaleB,
roundToIntegralExact, FMA (exact widened core, one pack,
Berkeley mulAdd ta measured above incl. jam/sticky paths), and
the trig kernel (rm passed through; `trig_decide` is sound for
any *monotone* rounding, ta included) are all in class (a) [R+A].
Min/max take no rounding attribute (`rounding=none`, operand
selection) — no delta [R operations.tsv]. Remainder is
definition-fixed — no delta.

**Counterexample class — `src/msf_string.c` rounds outside the
pack in two places, and today value 4 silently means
toward-zero there** [M, out/string_ta.log; runner replay
out/ta_string_probe.vec, 4 pass / 2 fail as predicted]:

- `dec_round_inc` (lines 411-427): no TA case -> default arm.
  Decides `to_decimal` digit rounding (call site line 1021)
  and the 5.12.2 beyond-H first step in `from_decimal` (565).
  Probe: `msf64_to_decimal(2.5, prec=1, rm=4)` gives `2e+00`;
  ties-to-away must give `3e+00` (tp control gives `3e+00`,
  pack-path f32-add control gives the ta answer `3f800001`).
- `to_hex_generic` precision switch (lines 1151-1164): no TA
  case -> `inc=0`. Probe: `msf32_to_hex(1+2^-9, prec=2, rm=4)`
  gives `0x1.00p+0`; ta must give `0x1.01p+0`.
- `from_decimal` beyond-H: fix is the `dec_round_inc` case
  only. The 55-digit exact-binary-tie probe string returned
  the ties-to-even bits under rm=4, but under the project's
  stated semantics that input is *beyond-H* (header prelude:
  "Correct rounding is promised for significant-digit counts
  1..H", H=20; `msf_string.c:558` "5.12.2 beyond-H first
  step"), i.e. it is *defined* by the two-step (round digit
  string to H digits under the attribute, then pack), and for
  that string the H-step does not increment under any nearest
  mode — the current bits are the two-step-correct ones. So
  no exact-long-digit redesign is needed; what ta changes
  beyond-H is only exact digit-ties at position H+1
  (dropped == `5` followed by zeros, last-kept even) [A].
  `from_hex` is pack-only (u128 + sticky jam into pack) and
  measured correct under ta (probe vec lines 3-6 pass) [M].

Hazard worth naming in the parcel brief: the pack's default arm
makes *any* out-of-enum rm silently toward-zero today; the
string switches do the same. Publishing value 4 without the two
string cases would make one family observably wrong; the
parcel must not ship enum-first-vectors-later.

### 1.3 Exact file/function list whose mode handling grows

Kernel (2 functions, both one case):
- `src/msf_string.c:dec_round_inc` — add
  `case MSF_IROUND_TIES_TO_AWAY: return gt_half || eq_half;`
- `src/msf_string.c:to_hex_generic` (switch at 1151) — add
  `case MSF_IROUND_TIES_TO_AWAY: inc = dropped >= half;`

Seam / generated (lead):
- `tools/gen_tables.py:352-358` — add
  `MSF_ROUND_TIES_TO_AWAY = 4`, rewrite the "exists only in
  the operation-named forms" sentence; regenerate
  `include/muse_softfloat.h` (+ COVERAGE/dispatch drift-watch;
  contents otherwise unchanged — 0 new rows).
- `tests/VECTORS.md` — rm token line: `ta` no longer
  internal-pack-only.
- `docs/RECORD.md:65` and any "four binary rounding attributes"
  claim sentence; README at gate.
- `tools/run.sh` controls() — add a ta<->te wrong-mode control
  (existing control 3 swaps te<->tz on pack64 only).

Generators (tests/, evidence side):
- `gen_vectors_f16.py`, `gen_vectors_f32.py`: `RMS4` -> 5.
  References already implement ta (`_round_inc_mag`, `to_inf`,
  integer refs) [R].
- `gen_vectors_f64.py`: `RMS` -> 5 (refs ready; pool-mixing
  arithmetic at line 580 uses `% 4`, update).
- `gen_vectors_xf.py`: `RMS4` -> 5 **plus** reference fixes —
  `_round_q` (143) and `to_inf` (188) have no ta arm today
  (would silently emit toward-zero expectations).
- `gen_vectors_str.py`: `RMS` -> 5 **plus** `_round_ratio_to_int`
  (90), `dec_round_inc` (194), `pack_ratio` `to_inf` — none has
  a ta arm today (independent integer forms; each is one branch).
- `gen_vectors_trig.py`: `RMS` (47) — relabel route, Sec.2.2.
- `gen_vectors.py`: already 5-mode (RMS incl. ta) — no change.
- `berkeley_ingest.py`: already maps ta — no change.
- `trig_exhaustive.c`: unchanged under the relabel route.

Nothing else switches on rm: audited `MSF_IROUND` / `(int)rm` /
`rm ==` across `msf16/32/64.c`, `msf_math.c`, `msf_string.c`,
`msf_performat.inc` (no rounding there) [M grep].

## 2. Oracle audit, by execution

### 2.1 Berkeley (pinned TestFloat-3e) [M]

`-rnear_maxMag` accepted for: f16_add, f32_mul, f64_add,
f64_div, f64_sqrt, f64_mulAdd, f64_to_f32, f32_to_f16,
i64_to_f64, ui32_to_f16, f64_roundToInt, f64_to_i64 (named
forms), f64_rem (accepted, mode-irrelevant). Rejected as
invalid argument: `f64_scaleB`, `f64_sinPi` — **functions
absent**, mode support moot. So Berkeley can decide ta for
every operation it covers at all; the 39 berkeley-authority
attr rows are fully coverable, and it cross-checks homogeneous
cases inside mpfr-exact families (as in Sec.1.1). Level-1 tie
density (same seed, near_even vs near_maxMag diff): f64_add
592/46,464 lines differ (all result-bit diffs are ties by
construction), f32_mul 69/46,464, f64_sqrt 0/768 — random sets
are tie-poor; directed tie-rich pools are the real gate
(Sec.4). **Gaps named**: scaleB (3 rows) and all Clause 9.2
math — Berkeley silent, as for the other modes.

### 2.2 MPFR 4.2.2 [M, out/mpfr_*.log, mpfr_probe2_*.log]

Three different answers, all measured:

1. **`MPFR_RNDNA` as a general mode: DO NOT USE.** It is
   incoherent across entry points: in `mpfr_set` narrowing it
   behaves as away-from-zero-*always* (below-half case
   `1+2^-30` at p=24 incremented — that is `MPFR_RNDA`, not
   ties-to-away); in `mpfr_subnormalize` it behaves as
   ties-to-even (`2^-150` tie -> +0). The header says so
   ("Definition of rounding modes (DON'T USE MPFR_RNDNA!)",
   `mpfr.h:89`; enum comment "ties away from zero
   (mpfr_round)", line 108 — the integer `mpfr_round` only).
   Mapping ta -> `MPFR_RNDA` is likewise wrong (away-always;
   it increments below-half values) — the Clause 9 survey's
   warning stands, now with executions.
2. **The sanctioned `mpfr_round_nearest_away` macro**
   (`mpfr.h:865`) delivers true ties-to-away for operations
   and set-narrowing *inside the oracle-0b emulation context*:
   binary32 cases — normal tie, below-half (correctly *not*
   incremented), above-half, `u/2` subnormal tie via
   macro + check_range + subnormalize(RNDN), f16/f32 boundary
   battery in probe 1's narrow section using RNDNA spot values
   re-checked against exact expectations (ties all correct;
   only the below-half discriminator exposes raw RNDNA).
   **Fence measured**: at *default* emin the macro aborts
   (`rndna.c:76` assertion) — it only ran with the recipe's
   narrowed emin/emax set first. And N=2 spot cases do not
   make a proven recipe: any generator use needs the
   oracle-0b-style boundary battery cross-decided by exact-py
   before trust (~3 h in the estimate).
3. **`mpfr_get_flt`/`mpfr_get_d` with RNDNA** returned the
   ties-to-away bits on exact-tie inputs (the trig decider's
   fast path) — but given (1), treat as unproven for
   below-half/sticky inputs; not needed under the trig route
   below.

**Consequence by family**: nobody needs MPFR to decide ta.
Berkeley decides its 39 rows + homogeneous cross-checks;
exact-py references (already ta-capable in f16/f32/f64/pack;
one-branch fixes in xf/str) decide the 216 mpfr-exact rows
exactly as they do for directed modes today. The MPFR
*math-function* decider for sinPi/cosPi (trig_exhaustive.c,
bracket at 640 bits then narrow in 4 modes) does not need a
ta narrowing at all: **sinPi/cosPi have no exact ties**. For
binary (dyadic-rational) x, sinPi(x) is rational only for
values in {0, +-1/2, +-1} (Niven's theorem [R, to be
second-read in the parcel]); a rounding tie is an exact
rational midpoint with p+1 significand bits, which none of
{0,+-1/2,+-1} is at any binade incl. the subnormal grid, and
the settled specials are exact results, mode-independent.
Hence ta == te bit+flag for all 6 trig rows, *including* the
tininess judge (same midpoint set at the unbounded grid).
Gate shape: replay the te sets relabeled `ta` (machine-checks
that the kernel's endpoint-decide path agrees; strongest at
the hardest-to-round excerpts) + the cited theorem in the
parcel text, provenance tag stating the relabel. Same
argument, classical form, for **sqrt** (a p+1-bit odd-LSB
midpoint squared has >= 2p+1 significand bits with odd LSB,
never a p-bit operand): sqrt's 9 rows are ta==te by proof;
Berkeley sqrt ta (768 lines, pass) corroborates. Families
where ties *do* occur and real ta sets are owed: add/sub/
mul/div/fma (Berkeley + exact), format/int conversion,
scaleB, roundToIntegralExact, character conversions
(decimal digit ties; hex binary ties) [A+M].

### 2.3 Other authorities

- **Exact-py path**: primary for 216 rows; refs audited above.
- **CORE-MATH**: cannot be asked for ta on this host — it
  honours the C floating-point environment and the mingw
  `fenv.h` defines exactly four FE modes (no ties-away) [M];
  it is corroboration-only anyway, with the oracle-0b fenced
  directed defect. No loss: for transcendental families
  ta==te (Sec.4 note).
- **Host SSE/libm**: no ties-to-away RC mode exists; already
  fenced (Clause 9 survey Sec.9) — nothing changes.

### 2.4 Coverage matrix (deciding authority for ta)

| Family class | Rows | ta decider | Kernel code change |
|---|---|---|---|
| Homog. arith + sqrt + fma (berkeley) | 18 | Berkeley -rnear_maxMag | none (measured pass) |
| Cross-format arith/fma/sqrt (mpfr-exact) | 180 | exact-py (refs ready; xf 2 fixes) | none |
| convertFormat + convertFromInt (berkeley) | 21 | Berkeley | none |
| convertFromInt (mpfr-exact) + scaleB + rintExact | 18 | exact-py | none |
| from_decimal / to_decimal / from_hex / to_hex | 12 | exact-py str ref (3 fixes) | 2 switch cases |
| sinPi / cosPi | 6 | te relabel + Niven note | none |

(18+180+21+18+12+6 = 255, matching the Sec.0 census.)

### 2.5 Vector volume and wall budget [M]

Committed smoke sets: 146,442 lines / 42 files; public
four-mode lines 95,753 (te 34,662; tz 20,171; tp 20,164;
tn 20,756); rm-less 46,969; existing ta (pack) 3,720.
Modes are *not* uniformly replicated (te carries extra
directed/NaN sets), so the honest adder is per-generator:

- ta at **directed-mode volume** (~tz column): +~20.2k lines
  -> smoke x1.138.
- ta at **mean-mode volume** (public attr / 4): +23,938
  -> smoke **x1.164**, attr-lines x1.25 exactly.
- Trig files are mode-balanced (10,873/mode): relabel adds
  +10,873 lines (already inside the figures above).
- Standard budget: smoke + f16-exhaustive (65,536 x 13
  no-rm ops, mode-free) + pack-sweep 200,000 (already
  5-mode) => denominator ~1,198,410; adder +23,938 ->
  **x1.020**. Generation of the two standard extras is
  unaffected.
- Parcel-gate (not budget) volume: per-family f16 exhaustive
  streams sweep RMS4 per unary op: x5/4 (Clause 9 survey:
  262,144 -> 327,680 unary cases); Berkeley level-1 ta
  ingest+replay for 8 functions measured end-to-end in this
  study at minutes of wall (verify of 6,133,248 mulAdd lines
  = 17 s; full smoke verify = 1 s at SECONDS granularity,
  ~360k lines/s on FMA-heavy sets) — verify wall is noise
  (+<0.1 s); the real wall is Python exact generation at
  parcel time, budgeted in hours below. Board: harness
  already parses ta; sampled replay grows only by whatever
  ta lines the sampler draws.

## 3. roundToOdd verdict

**Do not promote; do not build speculatively; do not bundle
with the fifth attribute.**

What it is: jamming — exact results unchanged, inexact
results delivered with odd LSB. Not a 754-2019 attribute or
operation (S1 Sec.2: five attributes defined, round-to-odd
nowhere; Clause 9 survey 4.3.3 same). Public exposure ceiling
is C-API project-extension labelling; putting a non-standard
mode in `msf_rounding_t` beside five standard ones would
blunt the enum's claim shape and invite exactly the silent
default-arm hazard of Sec.1.2 — *bundle* is the worst option.

Cost if a future kernel wants it *internally* (priced,
not recommended now): one `round_inc` arm is expressible
(`inexact && !(cand & 1)`), but the pack's overflow arm must
*not* deliver infinity — Berkeley `-rodd` measured delivery
on overflow is **largest finite** (49/49 observed cases,
`0x7fefffffffffffff`/`0xffefffffffffffff`) with
overflow+inexact flags [M, out/rodd_add.log]. Berkeley
generates `-rodd` for its operations, and an exact-py
round-to-odd reference is demonstrably cheap: my scratch
decider agreed with Berkeley on 43,050 decided f64 add+sqrt
lines (single mismatch = my checker's signed-zero blindness
on `(-0)+(-0)`, Berkeley right). Tininess-under-jamming was
not exercised by flag patterns in these sets (no underflow
flag combos among decided lines) — would need pinning from
Berkeley at build time. Total as internal mode 5 with
pack-level vectors: ~2-3 h *inside the parcel that needs it*
(exp/log Ziv kernels are the candidate consumers; the trig
kernel already shipped without it). No header value, no
COVERAGE row, internal.pack `to` token only.

## 4. Sequencing, plants, hours, stop conditions

**Land it first in SF-2.** Reasons, measured where possible:
(a) SF-1 Sec.7 placed it "after the first math function"
— that condition is now satisfied (sinPi/cosPi landed in
Step 2c), and the landed math turned out ta-trivial
(Sec.2.2); (b) the retrofit bill grows with every SF-2
family: 255 attr rows today vs up to ~396 if the deferred
141 rows land first; (c) SF-2 families split by tie
existence [A]: exp/log family and rSqrt/rootn have **no
exact ties** for binary inputs (transcendence of exp/log
values at nonzero algebraic arguments; root-of-midpoint
LSB argument as sqrt) so being *born* five-mode costs them
a theorem paragraph + relabeled replay, while retrofitting
costs a re-opened evidence ladder; pown/compound
and reductions *can* tie (exact rational cores) and would
owe real ta sets either way — cheaper generated in-parcel
than revisited. In-flight interaction: only SF-2 *studies*
are in flight (no implementation parcels); no merge
contention. Dynamic wrappers (sibling study) are unaffected
(state is enum-typed; if wrappers land first they inherit
the fifth value automatically, but must not claim it before
this gate).

Plant shapes a verifier would cut (expect these):
1. String digit-tie: to_decimal exact `…5` dropped digit
   with even kept digit under ta (catches missing
   `dec_round_inc` case — today's live bug shape);
   to_hex dropped == exactly half with even kept digit.
2. Beyond-H digit-tie: from_decimal 21+-digit string with
   dropped == `500…0`, even 20th digit, value positioned so
   the H-increment crosses a binary midpoint.
3. Subnormal-boundary ties: u/2 per format (ta -> u with
   underflow+inexact where te -> 0), tie just below
   2^emin where ta and te differ in *tininess flag only*
   (unbounded judge reaches 2^emin under ta, not te, or
   vice-versa) — flags-only plant.
4. Overflow midpoint ties both signs (ta -> inf where a
   plant that routes ta to the directed arm gives Fmax).
5. te<->ta relabeled trig/sqrt vectors with one flipped
   expectation (tests that the relabel gate really runs
   the kernel under rm=4, incl. the stage-fallback path).
6. fma jam tie: product+addend landing exactly on a
   midpoint at subnormal granularity; cross-format
   double-rounding trap zone with ta (xf trap generator
   under ta — its `_round_q` fix is plant-visible).

**Hours (agent + verifier, calibrated to Tier-1 parcels):**

| Item | Hours |
|---|---|
| Lead seam: gen_tables prelude, regen, VECTORS.md, control, claim wording | 0.5-1 |
| Kernel: 2 string cases + unit spot checks | 0.5 |
| Generator refs: xf (2 arms), str (3 arms), mode lists x6 files | 1.5-2 |
| Tie-rich directed design + regen of smoke sets (6 generators) | 2-3 |
| Berkeley ta gate replay (level-1 all covered fns; level-2 ruling for fma volume) | 1.5-2 |
| f16 exhaustive 5-mode streams (generation + verify wall) | 1.5-2 |
| Trig/sqrt theorem notes (second read) + relabel sets | 1 |
| MPFR-RNA recipe battery (only if a generator wants MPFR ta; skippable) | 0-3 |
| Board sampled replay incl. ta (lead, board time) | 0.5-1 |
| Verifier parcel (plants per above) | 2-3 |
| **Total** | **~11-17 (14-20 with MPFR route)** |

Stop conditions: (1) any *fourth* out-of-pack rounding site
found (audit says two; if generation exposes another, stop
and reprice — the enum must not ship partially honoured);
(2) Niven second-read fails -> trig needs a real MPFR-RNA
decider battery (+3 h and a recipe proof), still GO but
reprice; (3) Berkeley level-2 mulAdd volume blows the
gate wall -> lead ruling: level-1 + exact directed as the
ta gate for fma (ta at level-2 for the other modes was a
Tier-1 choice, not a rounding-semantics necessity);
(4) do not carve out from_decimal — an attribute one family
half-honours is a NO-GO for the whole parcel.

Claim when landed: every attr row's existing token
(required Tier 1 / C-754 Tier 2) extends to five
attributes row-by-row at gate close; 0 new rows, headline
counts unchanged (783 + 39), claim text gains "five
rounding-direction attributes (754-2019 4.3, incl. the
decimal-required roundTiesToAway provided for binary)".

## Evidence index

- `out/counts.log` — row/mode census (Sec.0, 2.5).
- `out/verify_ta.log` — 6,275,532 Berkeley ta cases PASS
  on current kernel (the 797 MB f64_mulAdd .vec was
  deleted after replay; regenerate via run_probes.sh §7).
- `out/string_ta.log`, `out/ta_string_probe.vec` (runner:
  4 pass / 2 predicted fail) — string counterexample.
- `out/mpfr_narrow.log`, `out/mpfr_getd.log`, `out/mpfr_op.log`,
  `out/mpfr_probe2_{op,narrow}.log` — RNDNA incoherence,
  RNA macro behaviour + emin fence.
- `out/rodd_{add,sqrt}.log` — round-to-odd Berkeley
  semantics vs exact-py (overflow -> Fmax).
- `out/time_{smoke,muladd}.log` — verify rates.

...[truncated 13571 chars]