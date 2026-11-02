# Wave 4 Step 0b - Tier 2 oracle bring-up (study-tier2-oracle0b)

Base: `e12492e9fd281dfe90b4c92c46f0c2e518ff7e35`. Brief:
`ledger/briefs/w4-oracle0b.md`. Host records (machine under load;
times are records, not claims): 2026-10-27, MSYS2 gcc 16.1.0
(Rev5, x86_64-w64-mingw32), MPFR 4.2.2, workspace `.venv` Python.
No repository writes: everything below is under
`scratch/tier2-oracle-0b/`, `scratch/oracles/` (CORE-MATH fetch),
and `ledger/study-tier2-oracle0b.md`. `git status` in
`muse-softfloat` verified clean at close.

Clean-room record: nothing with `cft` in its name was opened,
searched, or listed; the IEEE PDF was not opened. For CORE-MATH
only official documentation (project page, README), licence,
release/tag metadata, directory listings, four public
`function_under_test.h` interface headers, and build logs were
read; built binaries were executed. No function implementation
source, constants, polynomials, proofs, or `.wc` contents were
read. Disclosure: compiler diagnostics inside build logs (which
the brief authorises reading) quoted single source lines at error
sites - two in the binary16 units (`M_PI` undeclared) and two in
the upstream support checker (`getline`); no foreign file was
opened by this agent and no use was made of those lines for design.

## Verdicts

- **Part A (MPFR binary16/32 emulation): BRING-UP PASS.** The
  believed constants binary32 `emin=-148, emax=128` (p=24) and
  binary16 `emin=-23, emax=16` (p=11) are proven correct at every
  boundary probed, in all four rounding modes, by a fresh C probe
  cross-decided by an independent exact-rational Python rounder:
  232/232 exact checks, 136/136 C-side boundary expectations.
  Two recipe ingredients beyond the brief's sketch are required
  and were found the hard way (Section A.2).
- **Part B (CORE-MATH corroboration): BRING-UP PASS for the
  corroboration role, with one PRICED FAILURE sub-item and one
  fenced defect.** Pin + listing metadata + harness build + MPFR
  smoke all completed. The documented `./check.sh` path fails on
  this Windows host (priced in B.3); execution proceeded via the
  brief-sanctioned tiny harness over the public interface. Fenced
  defect: as built here, `cr_cospif` is **not** correctly rounded
  in toward-zero/downward modes for small |x| (297 disagreements
  in each directed mode, adjudicated against it by MPFR). Every
  other smoked cell agrees (23,926 agreements vs 594
  disagreements out of 24,520 unique comparisons).

## Part A - MPFR probe

### A.1 What ran

- `scratch/tier2-oracle-0b/mpfr_recipe_probe.c` (fresh): for each
  format, 17 boundary inputs narrowed from exact wide values
  (set path) x 4 modes, plus add/mul/sqrt operations on
  representable operands (13 binary32 + 11 binary16 cases) x 4
  modes. Prints raw value (hex), MPFR ternary values, and MPFR
  overflow/underflow/inexact flags as MPFR facts only.
- `scratch/tier2-oracle-0b/exact_check.py` (fresh): IEEE rounding
  from first principles over `Fraction` (ties-to-even, directed,
  overflow delivery, signed zero on underflow), plus exact sqrt
  decisions via midpoint squares (no floats anywhere). Decides
  every probe line independently; it shares no code and no
  expectation table with the C probe.
- Driver + logs: `run_partA.sh`, `out/probe.log`,
  `out/exact_check.log`, `out/probe_build.log`.

Boundary coverage, both formats, all modes: smallest subnormal
`u` (2^-149 / 2^-24) exact; `u/2` tie (to-even zero, directed to
the correct side, negative mirror with `-0` sign checked);
`1.5u` and `2.5u` midpoints both signs; largest finite exact;
first midpoint above it and one step (2^80 / 2^-4) to each side;
smallest normal, largest subnormal, the midpoints immediately
below and above smallest normal, and smallest normal + u.
Operations include subnormal-result cases per format
(`2^-70 * 2^-70 = 2^-140`; `2^-12 * 2^-12 = 2^-24`), products
landing exactly on `u/2`, just above `u/2` (+2^-173 / +2^-35),
and at `u/4`, subnormal-to-normal crossing adds, ties at 1,
overflow adds/multiply, exact and inexact sqrts including
`sqrt(u)`.

### A.2 The proven recipe

Per format: precision p = 24/11; `mpfr_set_emin(-148/-23)`;
`mpfr_set_emax(128/16)` (readback via `mpfr_get_emin/emax`
verified in the log). Then:

1. **Operation path** (operands already format values):
   `t = mpfr_op(r, ..., rnd)`, then `mpfr_subnormalize(r, t, rnd)`.
2. **Narrowing path** (exact wide value to format value - the
   vector-generation shape): `t = mpfr_set(r, wide, rnd)`, then
   **`t = mpfr_check_range(r, t, rnd)`** (required - `mpfr_set`
   does not range-check, and a below-emin intermediate then makes
   `mpfr_subnormalize` abort), then `mpfr_subnormalize(r, t, rnd)`.
3. **Zero guard** (required): skip `mpfr_subnormalize` when the
   intermediate result is zero, infinite, or NaN. Calling it on
   the below-emin/zero intermediate produced an MPFR assertion
   abort (`init2.c:53`, computed precision 0) in the first probe
   run - the crash is recorded in the run history, not smoothed
   over; with `check_range` + zero guard the full table passes.

Why the constants are what they are (corroborates, does not
replace, the probes): MPFR `emin = emin_IEEE - p + 2`,
`emax = emax_IEEE + 1`, matching the S2 binary64 anchor
(-1073/1024) and both pairs proven here.

### A.3 Counts and notable MPFR facts (never IEEE flags)

- C-side set-path expectations: pass=136 fail=0 (runs 1-2
  recorded: run 1 aborted at the `u/2` case before the recipe
  fix; run 2 had 6 false fails from a zero-sign bug in my C
  comparator, fixed in run 3; the exact checker was green from
  its first complete run).
- Exact-rational cross-check: SET f32 68/68, SET f16 68/68,
  OP f32 52/52, OP f16 44/44; TOTAL 232/232.
- Overflow threshold: at the first midpoint above largest
  finite, nearest and toward-+inf deliver `+inf`, toward-zero
  and toward--inf deliver largest finite (mirror for negative);
  ternary and value agree with exact decisions everywhere.
- MPFR flags are not Clause 7 flags, measured: the exact
  smallest subnormal delivered via the narrowing path still
  raises MPFR's underflow flag with inexact clear; at the
  overflow midpoint the narrowing path reports overflow flag
  **clear** when it delivers largest finite in toward-zero mode,
  while the operation path (`Fmax + Fmax`) reports it **set**
  for the same delivered value. Tier 2 generators must derive
  754 flags from exact state, never transcribe these.
- The `u/2` tie vs just-above-`u/2` products distinguish
  correctly through op + subnormalize in every mode: the
  ternary channel carries the needed information; no flushing.

## Part B - CORE-MATH pin, metadata, build, smoke

### B.1 Pin (official links only)

Route: Clause 9 survey citation -> official project page
`https://core-math.gitlabpages.inria.fr/` -> its `[git]` link
`https://gitlab.inria.fr/core-math/core-math/`. The official
releases page lists no releases and the tags page shows no
version tag (checked 2026-10-27), so the pin is the master
commit via `git ls-remote` (ref metadata only), fetched as the
GitLab archive of that commit into `scratch/oracles/`
(`fetch_coremath.sh`, `out/fetch_coremath.log`). Archive
195,782,173 bytes; SHA-256 agreed by two tools (`sha256sum`,
`Get-FileHash`): `e1060951...dbd` (full value in the row below).
Licence file `LICENSE` (1,132 bytes): MIT text, read in full.

Proposed `docs/metrics/fetches.jsonl` row, in the existing shape
(not written - repository writes are the lead's):

```json
{"name": "CORE-MATH", "url": "https://gitlab.inria.fr/core-math/core-math/-/archive/3b2163bb87c222c7db17a721425fbef31e98fd94/core-math-3b2163bb87c222c7db17a721425fbef31e98fd94.tar.gz", "version": "master commit 3b2163bb87c222c7db17a721425fbef31e98fd94 (no upstream release/tag)", "archive_sha256": "e1060951eacb6e8081b92bfc796a2588a87ab97ab35e013c75459dff45551dbd", "licence": "MIT", "licence_sha256": "81830875362f4d477637de58eecd6d458db108cc90c40904fca3694807b86de3", "fetched": "2026-10-27", "by": "study-tier2-oracle0b", "note": "host corroboration oracle only (SF-1 Step 0b): tree in scratch/oracles, never vendored; execution + directory metadata only, implementation source and .wc contents never read; cr_cospif directed-mode defect on this host - see scratch/tier2-oracle-0b/report.md"}
```

### B.2 Metadata (directory listings only)

From `list_coremath.sh` / `out/list_coremath.log` on the pinned
tree (confirms the survey's documentation parse; supersedes it):

| Function | binary16 | binary32 | binary64 | binary80 | binary128 |
|---|---|---|---|---|---|
| sinpi | units present | present | present | absent | absent |
| cospi | units present | present | present | absent | absent |
| sin | present | present | present | dir only (.sage/.wc, no .c) | present |
| cos | present | present | present | dir only (.sage/.wc, no .c) | present |
| rsqrt | present | present | present | present | present |

Worst-case files for the Pi pair (existence + size only,
contents never read): binary64 `sinpi.wc` 1,608,960 bytes and
`cospi.wc` 1,090,690 bytes; **none** in the binary16/binary32
sinpi/cospi directories. Public entry points confirmed from
README + interface headers: `cr_sinpi`/`cr_cospi` (binary64),
`cr_sinpif`/`cr_cospif` (binary32), `cr_sinpif16`/`cr_cospif16`
(binary16).

### B.3 Build outcomes

**Documented path (`./check.sh --worst --rndn sinpi`):
PRICED FAILURE** (`build_coremath.sh`, `build_f16_retry.sh`,
`adjudicate.sh`, `build_check3.sh`; logs in `out/`). Exact
attempts: (1) Git Bash with MSYS2 tools - `Cannot create
temporary file in C:\WINDOWS\: Permission denied`, make Error 3
(environment mixing, ours to route around); (2) MSYS2-native
bash - gets into its own support checker and fails compiling
it: `error: implicit declaration of function 'getline'`
(`../support/check_worst_uni.c:75`), make Error 1, plus a `%lx`
vs `uint64_t` format warning (LP64 assumption); (3) same with
the README-documented `CFLAGS` knob (`-O2 -std=gnu11`,
then also `-D_GNU_SOURCE`) - identical failure, so the knob
does not reach that compilation. Price to fix: either a Linux
host (the documented environment; WSL is denied to the sandbox
user here) - estimated half a day including worst-case runs -
or editing foreign build files, which is outside this step's
fences. Not needed for the corroboration role below.

**Tiny harness over the public interface (brief-sanctioned
alternative): builds and runs.** The six standalone units named
by the official documentation table were compiled without being
opened (`gcc -O2 -frounding-math -ffp-contract=off`; contract
choice consistent across all units per README). binary32/64
units compile clean under `-std=c11`; binary16 units fail under
strict c11 with `'M_PI' undeclared` and compile clean under
`-std=gnu11` (dialect flag only, no source contact). Harness
`cm_harness.c` (mine) calls the public `cr_*` names under
`fesetround` per mode; `mpfr_ref.c` (mine) is the MPFR side
using the Part A recipe (wide p+120 evaluation narrowed with
check_range + subnormalize - smoke-grade, see limits).

### B.4 Smoke vs MPFR (regular numbers only)

Cases (`smoke.py gen`, seed 20261027): directed anchors
(±1/8, 1/4, 1/2, 3/4, 1, 3/2, 2, 3, 10, 100, 1234.5, -987.25,
2^±20, 16777217, 0.1; format-filtered) + 1,000 seeded random
finite normals per format (f64 |x| in [2^-40, 2^41), f32 similar,
f16 all normal exponent bands), x {sinpi, cospi} x 4 modes.
No zeros, subnormals, infinities, or NaNs (the project's own
fences). Unique input patterns compared per mode: 6,130
(f16 2,034 after duplicate collapse; f32 2,048; f64 2,048).

| Mode | f32 sinpi | f32 cospi | f64 sinpi | f64 cospi | f16 sinpi | f16 cospi |
|---|---|---|---|---|---|---|
| N | 1024/1024 | 1024/1024 | 1024/1024 | 1024/1024 | 1017/1017 | 1017/1017 |
| Z | 1024/1024 | **727/1024** | 1024/1024 | 1024/1024 | 1017/1017 | 1017/1017 |
| U | 1024/1024 | 1024/1024 | 1024/1024 | 1024/1024 | 1017/1017 | 1017/1017 |
| D | 1024/1024 | **727/1024** | 1024/1024 | 1024/1024 | 1017/1017 | 1017/1017 |

(agreeing/compared; full disagreement lines in
`out/smoke_Z.log` and `out/smoke_D.log`, identical 297-input
lists in both modes.) Disagreement pattern, complete: all 297
are binary32 cospi inputs with |x| roughly 1e-13..3e-5
(result within a few ulp of 1); the foreign binary returns
`0x3f7ffffd` (1 - 3 ulp) - once `0x3f7ffffe` (1 - 2 ulp) at
|x| = 2^-20 - where correct toward-zero/downward rounding
delivers `0x3f7fffff` (1 - 1 ulp). Adjudication (MPFR decides,
never the foreign binary; `adjudicate.c/.sh`,
`out/adjudicate.log`): three independent routes - the smoke's
wide-then-narrow MPFR, direct MPFR `mpfr_cospi` at p=24 under
the Part A recipe, and mpmath at 200-bit precision - all
deliver `0x3f7fffff` on exemplars from the disagreement set.
`cr_sinpif` agreeing in the same modes rules out a harness-wide
rounding-mode failure. Whether this is an upstream directed-mode
defect or a Windows-build artifact (the README's own known-issue
note warns that some routines depend on `fenv.h` macro values
that differ on Windows) is **undecided from inside the fences**;
either way the binary as built on this host must not corroborate
directed binary32 cospi. Price to decide: run the documented
`./check.sh --exhaustive --rndz cospif` on a Linux host
(half-day class, same trip as B.3's fix), or try an
`-ffp-contract=on` rebuild here (~10 minutes, tests one
build-knob hypothesis only).

## What SF-1 Step 2b may and may not rely on

May rely on (measured here):

- The Part A MPFR recipe exactly as in A.2 (constants, bounds
  calls, `check_range` on the narrowing path, zero guard,
  subnormalize placement) for binary16/binary32 known-answer
  work at p=11/24 on MPFR 4.2.2, all four modes, including
  subnormal and overflow boundaries.
- MPFR as the deciding oracle for sinpi/cospi values on regular
  numbers (it decided every smoke disagreement).
- The pinned CORE-MATH tree as a *corroboration* executable for
  sinpi/cospi binary16/32/64 in round-to-nearest (6,130/6,130
  unique comparisons agree), and in all modes except the fenced
  cell below; harness + build scripts in this scratch are the
  runnable route.
- The B.2 availability matrix (pinned-tree listings), including
  absence of binary80/128 Pi-pair code and of binary16/32 `.wc`
  files; binary64 `.wc` files exist at the recorded sizes for a
  later provenance-tagged import decision.

May not rely on:

- `cr_cospif` binary32 in toward-zero or downward modes, on this
  host/build, for anything (297/1024 sample disagreements near
  result 1). Directed-mode binary32 cospi corroboration awaits
  the Linux exhaustive check or another decider.
- Any CORE-MATH binary for specials, flags, NaN behaviour,
  subnormal inputs/results, or signed zeros: untested here by
  design and fenced by upstream's own documentation. Nothing
  here licenses a foreign binary to adjudicate; disagreements
  route to MPFR/exact (SF-0 4.4).
- The documented `./check.sh` route on this Windows host
  (priced failure, B.3); `./check.sh`-grade exhaustive/worst
  evidence does not exist yet for any cell. Smoke agreement is
  corroboration, not an exhaustive or worst-case proof; binary32
  exhaustive differentials remain a Step 2b costing item.
- MPFR flags/ternary as IEEE flags, in any generator (A.3
  measured mismatches). Also not: naive `mpfr_set` +
  `mpfr_subnormalize` narrowing without `check_range` (aborts),
  and not `mpfr_subnormalize` on a zero intermediate.
- The smoke MPFR reference's wide-then-narrow shape (p+120) as a
  production vector generator: adequate for regular-number
  smoke, not a Ziv-rigorous hardest-case decider.
- Anything about sin/cos/rsqrt executables: listing metadata
  only in this step; none were built or smoked.

## Unresolved (priced, not silent)

1. Documented check build on Windows - priced in B.3
   (Linux host half-day, or forbidden-here build patch).
2. Build-artifact vs upstream for the `cr_cospif` Z/D defect -
   priced in B.4.
3. binary64 `emin/emax` (-1073/1024) not re-probed here; it is
   the S2 documented anchor and the A.2 formula's third point.
   Price: extend the probe one format (~30 min) before any
   binary64 MPFR narrowing is trusted at its boundaries.
4. Throughput for exhaustive binary32 differentials and any
   binary16 exhaustive run: unmeasured (smoke only). Price:
   timed 2^24-sample benchmark (~15 min) at Step 2b planning.
5. sin/cos/rsqrt units built/smoked: none. Price: ~15 min per
   function-format with the existing harness when a parcel
   needs them.
6. `.wc` contents and all CORE-MATH implementation/proof
   material: unread by design; any worst-case import needs its
   own brief and provenance handling.
7. MPFR behaviour outside the probed envelope (NaNs,
   infinities, ties-to-away - MPFR has no such mode): untouched;
   those decisions remain with the exact references and pack
   semantics, per the Clause 9 survey's authority table.

## Artefacts

All under `scratch/tier2-oracle-0b/`: `mpfr_recipe_probe.c`,
`exact_check.py`, `run_partA.sh`, `fetch_coremath.sh`,
`list_coremath.sh`, `build_coremath.sh`, `build_smoke.sh`,
`build_f16_retry.sh`, `build_check3.sh`, `adjudicate.c/.sh`,
`cm_harness.c`, `mpfr_ref.c`, `smoke.py`, this report, and
`out/` logs (`probe.log`, `exact_check.log`,
`fetch_coremath.log`, `list_coremath.log`, `build_*.log`,
smoke logs, `adjudicate.log`, `cases.txt`). CORE-MATH fetch:
`scratch/oracles/core-math-<sha>.tar.gz` + extracted tree.
