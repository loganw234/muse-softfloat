# ias15-port: host de-risking for REBOUND IAS15 on RP2040 via muse-softfloat

Agent ias15-port, 2026-10-27. Verdict: **FEASIBLE WITH GAPS** (extraction
and the AEABI compat surface remain; no softfloat semantic gap found).
Headline, measured this session: **a build of unmodified REBOUND 5.2.2
whose every binary64 operation is routed through muse-softfloat at
dd48b08 produces step-by-step state hashes identical to the unmodified
SSE2 desktop build for 20,001 consecutive records** (figure-8, three
bodies, t = 122.3), plus 2,001 records each in three further
configurations. Everything below is reproducible with
`scratch/ias15/scripts/00_all.sh` from Git Bash. Claims are tagged
READ / MEASURED / BELIEVED in S4's style. S4's survey
(`scratch/S4/report.md`) is built on and not repeated; section cites to
it are given where this pass relies on it.

Workspace: `scratch/ias15/` (scripts/, work/, out/, tmp/). Ledger:
`ledger/ias15-port.md` (design 07:04, proof 07:26, verdict at close).
Clean room kept: nothing with the forbidden name was opened, searched,
or listed. `muse-softfloat/` was not modified (read-only `git archive`
export; porcelain clean at export). No board access.

## 1. Pins (MEASURED)

| Item | Pin | SHA-256 / evidence |
|---|---|---|
| REBOUND | `https://github.com/hannorein/rebound/archive/262a9cce102c69ca2cf7f3c6c1264e5e60002b7d.tar.gz`, `version.txt` = 5.2.2 | archive `9221d38a7a3f6a5d134e4b92e7dc63648c6dfe01eb1753a3e570c24a384a2887` (6,112,479 B); `scratch/ias15/fetch.md`, `scripts/01_fetch.sh` |
| Licence | GPL-3.0-or-later | root `LICENSE` sha256 `8ceb4b9ee5adedde47b31e975c1d90c73ad27b6b165a1dcd80c7c545eb65b903`; stays in scratch, never enters the library tree (SF-0 4.5, 9) |
| muse-softfloat | dd48b08c7cb2f1aa957d15972d919c6d3051ad78 | exported to `work/msf-dd48b08/`; per-file hashes `out/msf_dd48b08_sha256.txt` (`scripts/02_export_msf.sh`) |
| Host compiler | gcc 16.1.0 x86_64-w64-mingw32 (MSYS2 Rev5), `C:\msys64\mingw64` | `out/02_export_msf.log`; must be first on PATH or cc1 exits 1 silently (Git Bash ships its own `/mingw64/bin`) |
| ARM compiler | arm-none-eabi-gcc 14.2.1, Cortex-M0+ | `out/14_tables.log`, `out/15_sizes_arm.log` |
| Problem ICs | binary64 bit patterns | `work/ic_fig8.txt` sha256 `19024eef43533b5adefca0ee66aab03eaa6166a04ecd2ec52a900fe3a4764af0` |

## 2. The desktop reference run (task 2)

Same driver source (`work/driver.c`, integer/hex I/O only, zero FP
literals or conversions) drives both builds. Upstream source is
compiled whole (29 of 30 `src/Makefile` C files; `integrator_whfast512.c`
replaced by a one-symbol link stub in *both* builds because gcc 16's
`immintrin.h` `__m512d` typedef collides with upstream's own and its
step is AVX-512 asm; it is never selected, the driver asserts the
integrator name is `ias15`). No upstream file was edited.

Problem: equal-mass three-body figure-8 (Chenciner-Montgomery),
`G=1`, `dt0=0.01`, IAS15 defaults pinned explicitly from the IC file:
`epsilon=1e-9`, `min_dt=0`, adaptive mode PRS23 (2), gravity BASIC (1),
`additional_forces=NULL`, stepping via the public
`reb_simulation_steps(r,1)` in a loop. ICs are frozen hex bit patterns
(SF-0 Section 9); the generating decimals live only in
`work/make_ic.py` comments/provenance. Variants: `ic_fig8_global.txt`
(GLOBAL mode), `ic_fig8_comp.txt` (COMPENSATED gravity), `ic_ecc.txt`
(two-body e=0.9 binary) via `work/make_ic2.py`.

Native flags (SF-0 Section 9 / S4 Section 5.2, MEASURED in
`scripts/04_build_native.sh`):

```
-std=c99 -O3 -march=x86-64 -ffp-contract=off -fno-fast-math
-fno-unsafe-math-optimizations -fexcess-precision=standard
-DBUILDINGLIBREBOUND -D_GNU_SOURCE
```

Driver prints `FLT_EVAL_METHOD=0`, `sizeof(reb_particle)=112`
(reproducing S4's measured sizes). Non-finite hashed fields over all
runs: 0. Figure-8 sanity (Python decode of raw records): energy
-1.2871419917663258 at step 0 vs -1.2871419917663254 at step 2000;
particle 0 back at its start position after two periods at t=12.6518;
`dt` ranges 4.2e-12 to 0.0497 over 20,000 steps (`out/12_matrix.log`).
Native run wall time 0.13 s for 2,000 steps on this host under load
from sibling agents; treat as approximate.

## 3. Field-hash specification IAS15FH1 (task 2, Pico contract)

Implemented in `work/driver.c` (SHA-256 in `work/sha256.c`,
cross-checked against Python `hashlib` on dumped raw records:
`out/06_validate_native.log`). One pair of hashes is emitted
for the initial state (step 0) and after each accepted step. All
integers are little-endian fixed-width, emitted byte by byte (the
framing is endian-free by construction); every `f64` is its IEEE
binary64 bit pattern as u64. No pointers, padding, wall-clock, or
allocator data ever enters. Whole-file upstream archive comparison is
refused for the reasons in S4 Section 4.3.

`H_state` (trajectory identity), SHA-256 over:

```
"IAS15FH1" (8 B ASCII) | u8 0x53 | u64 step_index | u64 N
| f64 t | f64 dt | f64 dt_last_done | f64 G
| per particle in index order: x y z vx vy vz ax ay az m r   (11 x f64)
```

`H_full` (restart identity), SHA-256 over:

```
"IAS15FH1" | u8 0x46 | u64 step_index | u64 N
| f64 epsilon | f64 min_dt | u32 adaptive_mode | u32 0
| u64 iterations_max_exceeded | u64 N3 (=3(N+N_var))
| u8 allocated (0 => nothing further; the step-0 case)
| if allocated: at,x0,v0,a0,csx,csv,csa0 (N3 f64 each)
                then g,b,csb,e,br,er (7*N3 f64 each, storage order)
```

A Pico firmware reproduces a record by running the same stepping loop
and emitting the same byte string (or the digest, using `sha256.c`
verbatim). Record sizes here: H_state 321 B, H_full 3,594 B (N=3).
Reference digests (`out/hashes_native.txt`, file sha256
`9bedb078b1de37c399312e27a65f971229c2cd8353d5f671ae8ed64a63993ab3`):
step 0 `H_state=62bb23b04627c30227a7fb999fee22d0ac9eb4349631d9c41f138c6bde333e01`;
step 2000 `H_state=4d4530a668d360897477a63f90dfb0f7c86b33eb3e462f5a464028d083f48abb`,
`H_full=32689328ee80ff8b90685b10087a747cfbba9ac236f2b35c2481ce531c26a4c7`.

## 4. FP operation inventory mapped to msf64 (task 3)

Static census re-run on the fetched tree (`scripts/16_inventory.sh`,
`out/16_inventory.log`) corroborates S4 Sections 2.1-2.5 exactly, so
S4's per-site tables stand; what this pass adds is the *executed*
census and the msf64 mapping. Runtime counts are shim counters over
the 20,000-step figure-8 (`out/h_fig8_long_soft.txt`), i.e. what the
step actually executes, wrapper `gettimeofday` bookkeeping included
(it is ~2 int->double conversions per step).

| Executed operation (IAS15 step path) | Runtime count / 20k steps | msf64 instantiation (dd48b08) | Status per `docs/COVERAGE.tsv` |
|---|---:|---|---|
| binary64 add | 72,125,098 | `msf64_add` | implemented (wave 1) |
| binary64 sub (incl. Kahan `add_cs` innards, negation-by-sub) | 70,753,828 | `msf64_sub` | implemented |
| binary64 mul | 88,232,799 | `msf64_mul` | implemented |
| binary64 div (incl. `sqrt7` Newton, gravity prefactor) | 28,345,375 | `msf64_div` | implemented |
| binary64 sqrt (gravity per pair, PRS23 timescale) | 1,045,057 | `msf64_sqrt` | implemented |
| quiet `!=` (libcall form) | 80,000 | `msf64_compare_quiet_equal` (negated) | implemented |
| quiet `<` | 163,097 | `msf64_compare_quiet_less` | implemented |
| quiet `>` | 505,849 | `msf64_compare_quiet_greater` | implemented |
| quiet `>=` | 427 | less/equal composition | implemented |
| int32 -> binary64 | 654 | `msf64_from_i32` | implemented |
| int64 -> binary64 | 40,000 | `msf64_from_i64` | implemented |
| uint64 -> binary64 (`size_t` casts) | 1,025,058 | `msf64_from_u64` | implemented |
| `fabs`, `copysign`, unary `-`, `isnormal` | inlined integer bit ops in both builds (asm MEASURED: `btr`, `btc`, high-word blend, exponent mask; `work/probe_fp.c` disassembly) | `msf64_abs`, `msf64_copy_sign`, `msf64_negate`, `msf64_is_normal` are the same bit functions by definition | implemented (wave 0 rows) |
| fused multiply-add | **0 executed**; no source call exists; compiler contraction forbidden in reference and impossible on M0+ | `msf64_fma` exists and is shim-wired | implemented |
| binary64 -> integer | **0 executed** | `msf64_to_*_toward_zero` wired in shim | implemented |
| `pow`, trig, exp, log | **0 in step path** (whole-tree `pow(` sites: `tools.c` sampling, `integrator_bs.c`, one comment; none executed; libm traps in shim stayed at 0) | none needed | n/a |

Negative space verified by the link itself: mingw64 `libgcc.a`
contains no `__adddf3`-family routines, so any binary64 operation not
covered by the shim would have failed the interposed link. Undefined
FP surface of the soft objects (`out/07_soft_census.log`,
`out/soft_undefined_unique.txt`): `__adddf3 __subdf3 __muldf3
__divdf3`, `__eqdf2 __nedf2 __ltdf2 __ledf2 __gtdf2 __gedf2
__unorddf2`, `__floatsidf __floatdidf __floatunsidf __floatundidf
__fixdfsi __fixdfdi`, `__extendsfdf2 __truncdfsf2`, `sqrt`, plus 18
trap-stubbed libm names from never-executed code. Mean FP work
(N=3 figure-8): ~3,606 add + 3,537 sub + 4,411 mul + 1,417 div + 52
sqrt + ~90 comparisons/conversions = **~13,100 binary64 ops per
accepted step**.

Per-operation flag behaviour is a non-issue for this workload: the
step never reads FP exception flags or touches `fenv` (whole-tree
count 0, corroborating S4 2.6.10); the shim accumulates flags into
unread static state, rounding fixed at `MSF_ROUND_TIES_TO_EVEN`.

**Gap list (named).** Semantic gaps in muse-softfloat for IAS15:
*none* - every executed operation maps to a wave-1-implemented
instantiation. Remaining gaps are integration work, Section 8:
(G1) extraction + extract-vs-full hash equivalence not yet done;
(G2) the repo's compat layer at dd48b08 wraps only `copysignf`/
`copysign` (its own header comment says the AEABI arithmetic surface
lands in wave 3), so the Pico-side `__aeabi_d*` wrappers still have
to be written; (G3) bare-metal CRT surface (`malloc`/`gettimeofday`/
stdio warnings/`signal`) to stub or take from pico-sdk at extraction.

## 5. Memory budget vs RP2040 (task 3)

Struct sizes MEASURED fresh (`scripts/15_sizes_arm.sh`): ARM ILP32
`reb_particle` 112 B, `reb_simulation` 592 B,
`reb_integrator_ias15_state` 88 B, `reb_vec3d` 24 B (S4's numbers
reproduced). Workspace formula (S4 4.2, re-read at
`integrator_ias15.c:244-275`): 49 x 3N doubles = **1,176 B/particle**,
plus particle 112 B (plus 24 B `gravity_cs` only if COMPENSATED).
Tables `h/rr/c/d/w` = 86 doubles = 688 B of `.rodata` (flash).

| N | workspace+particles | SRAM note (264 KB total) |
|---:|---:|---|
| 3 (this proof) | 3.9 KB | trivial |
| 10 | 12.9 KB | trivial |
| 50 | 64.4 KB | comfortable |
| 100 | 128.8 KB | fits with stack + USB buffers |
| 200 | 257.6 KB | does not fit responsibly |

Flash (2 MB): whole-file ARM text MEASURED `integrator_ias15.o`
28,257 B + `gravity.o` 16,115 B + boundary 2,488 B; muse-softfloat
whole-file `msf64.o` 21,444 B + `msf32.o` 19,048 B + support 2,832 B.
The extracted subset keeps an estimated 500-560 of IAS15's ~1,070
lines and one of gravity's ~930 (S4 6.2), and `--gc-sections` will
cut the core to the ~15 instantiations actually linked; even
unshrunk, everything is two orders under the flash budget. Zero
allocation per step at fixed N (S4 6.3): one static arena of
`1176*Nmax + 88 + 112*Nmax` bytes replaces all `realloc` traffic;
if N ever grows mid-run, upstream re-zeroes the predictor buffers
(`integrator_ias15.c:230-235,266-272`) and the port must reproduce
that to stay bit-identical.

## 6. The host proof (task 4)

### 6.1 Mechanism

Interposition on x86-64 is achieved at the ABI level, not by source
rewrites. MEASURED flag search (`scripts/03_probe_softfloat.sh`,
`scripts/07b_variant_probe.sh`): plain `-msoft-float` is silently
ignored by x86_64-w64-mingw32; `-msoft-float -mno-sse2` (SSE1 kept so
Windows headers compile) turns every binary64 operation into a
libcall (`__adddf3` etc.) with **zero** SSE-double and zero x87
instructions in every workload object (`scripts/07_soft_census.sh`).
`-mno-sse2` alone falls back to x87 and was rejected (8 x87 insns in
the probe). The shim (`work/msf_shim.c`, scratch-only) defines those
libcalls over `msf64_*`, plus `sqrt`/`fma`/`fabs`/`copysign` and
loud-failure traps for 18 never-executed libm names. Comparison
libcalls return `int64_t` -1/0/+1 with per-routine unordered values
derived from this compiler's emitted result tests
(`scripts/08_cmp_probe.sh`: `shr 63` for `<`, `setle` for `<=`,
`~R>>63` for `>=`, `sete/setne` for `==`/`!=`), not from documentation
memory. The only SSE-double instructions in the final executable are
55 inside the CRT's `__gdtoa` (printf float formatting, never executed:
all program output is integer/hex; `scripts/13_sse_owners.sh`).
Binary32 SSE1 survives only in `display.o` (8 insns) and
`rotations.o` (79), both outside the step path and unexecuted.

### 6.2 Shim validated before trust

`work/shim_selftest.c`, 346,901 checks (24 directed operands covering
+-0/subnormals/min-max normal/Inf/qNaN/sNaN/halfway cases, all pairs,
plus 20,000 fixed-seed LCG pairs; Kahan `add_cs` replay, Horner chain,
IAS15-shaped `isnormal && x>max` compounds, conversions):

- SOFT build (C op via shim vs direct `msf64_*`): **0 failures**
  (`SELFTEST_SOFT PASS`). The only wrinkle: GCC's commutative
  operand-order canonicalization is visible through NaN payloads on
  add/mul; accepted either order after inspection (12 cases, all
  explained). Both IAS15 builds share the same mid-end, so the
  end-to-end hash is the arbiter.
- NATIVE differential (volatile SSE2 vs `msf64_*`): **0 arithmetic,
  sqrt, or branch mismatches**.

### 6.3 Result

| Configuration | Records compared (step 0 + steps) | H_state | H_full |
|---|---:|---|---|
| figure-8, PRS23, BASIC, 2,000 steps | 2,001 | identical every step | identical every step |
| figure-8, PRS23, BASIC, 20,000 steps | 20,001 | identical | identical |
| figure-8, GLOBAL, BASIC, 2,000 steps | 2,001 | identical | identical |
| figure-8, PRS23, COMPENSATED, 2,000 steps | 2,001 | identical | identical |
| eccentric binary e=0.9, PRS23, BASIC, 2,000 steps | 2,001 | identical | identical |

First divergence: none. Largest step count with identical hashes:
**20,000 accepted steps** (the longest run). Raw record bytes are also
byte-identical at dumped steps 0/1/2000 (`out/11_compare.log`).
Determinism control: native rerun is byte-identical. Negative
controls, watched failing (`scripts/17_negative_controls.sh`): an
FMA-contracting build (`-march=x86-64-v3 -ffp-contract=fast`, same
machine) diverges at **step 1**, so the comparator has teeth.
Interposed run time 6.9 s vs 0.13 s native for 2,000 steps (~53x on
this host; says nothing transferable about RP2040 rates, see 8.3).

### 6.4 Two SSE2-vs-msf64 differences that cannot reach a trajectory

Found by the native differential, classified, and argued unreachable
in this workload (both are also documented design choices, not
defects):

1. **NaN sign/payload** (1,376 cases): SSE2 delivers the negative
   indefinite QNaN `0xFFF8...`, msf64 the canonical positive
   `0x7FF8...` per the SF-0 2.5 matrix. In the step, NaNs arise only
   inside error estimates (`0/0`, `x/0`) and are consumed exclusively
   by `isnormal` guards and comparisons (S4 2.6.1-2.6.3), all
   payload-insensitive; hashed fields stayed finite in every run
   (counter in driver: 0 non-finite hashed fields over 28,000
   stepped records across configurations). If a future problem
   choice ever put a NaN into particle state, H_state would diverge
   on payload alone; the driver counts that case explicitly so it
   cannot pass silently.
2. **binary64->integer invalid delivery** (1,135 cases, all of the
   native differential's non-NaN mismatches): x86 `cvttsd2si`
   delivers `INT_MIN` for NaN/overflow; msf64 saturates per its
   stated project rule (754-2019 5.8 leaves the value
   implementation-defined; header documents it). Executed
   double->int conversions in all IAS15 runs: **0**.

### 6.5 A host landmine found and isolated: library `sqrt`

The strict reference's identity depends on *which* sqrt executes.
MEASURED: a `-O0` strict build diverges from the `-O3` reference at
H_full step 53 (trajectory follows at step 89); `-O3
-fno-builtin-sqrt` reproduces the `-O0` run exactly (2,001 records),
isolating the cause to library-vs-inline sqrt. The library body is
statically linked `sqrt.c` from libmingwex (symbol `sqrt` present in
the exe, no DLL import; `scripts/17e_sqrt_provider.sh`). Quantified
with the selftest forced through the library
(`scripts/17d_libsqrt_quantify.sh`): exactly 2 directed failures,
e.g. sqrt of the largest double below 1 returns `1.0`
(`0x3FF0000000000000`) where correct rounding (and `sqrtsd`, and
`msf64_sqrt`) give `0x3FEFFFFFFFFFFFFF` - a 1-ulp error on rare
operands, one of which the figure-8 first hits around step 53. The
`-O3` reference executes inline `sqrtsd` for the (always
non-negative) step operands, which is correctly rounded and equals
msf64 on all 346,901 differential checks. Consequences: (a) the SF-0
phrase "unmodified desktop run" must keep pinning the exact flag set
including `-O3`, as Section 9 already does - optimisation level is
load-bearing on this host, now with a named mechanism; (b) on the
Pico side this failure mode cannot occur, since sqrt will be
`msf64_sqrt` itself. Suggested AGENTS.md addition for the lead:
"mingw64 libmingwex `sqrt` is not correctly rounded (1-ulp cases);
oracle/reference builds must execute inline `sqrtsd`, never the
library body."

## 7. Literal / coefficient-table verification (SF-0 Section 9)

All 86 table entries (`h[8]`, `rr[28]`, `c[21]`, `d[21]`, `w[8]`) were
extracted verbatim from `integrator_ias15.c:185-193`
(`work/gen_table_probe.py`), converted with mpmath at 300-bit
precision to correctly rounded binary64 (`out/tables_expected.txt` -
this file is the verified hex carry set SF-0 prescribes), and checked
against three compiler conversions: host gcc native, host gcc soft,
and arm-none-eabi-gcc 14.2.1 (read out of the ARM object's `.rodata`,
since no ARM execution was available; `scripts/14_tables.sh`).
**Zero mismatches in all four.** The Pico port should still carry
the tables as these hex patterns and assert them at build time,
which removes the question entirely.

## 8. Pico port plan (task 5)

### 8.1 What firmware needs (MEASURED ARM surface)

`integrator_ias15.c`, `gravity.c`, and `boundary.c` already compile
clean for `-mcpu=cortex-m0plus -mfloat-abi=soft` today;
`simulation.c`, `rebound.c`, `particle.c` fail only on POSIX glue
(`usleep`, `strnlen`/`strdup`/`posix_memalign`, a newlib `_N` macro
collision) that the extraction deletes anyway - S4's
extract-don't-link recommendation is now measured fact
(`out/15_sizes_arm.log`). Undefined FP symbols of the step TUs,
i.e. the complete Pico interposition surface:

```
__aeabi_dadd __aeabi_dsub __aeabi_dmul __aeabi_ddiv
__aeabi_dcmpeq __aeabi_dcmplt __aeabi_dcmpgt __aeabi_dcmpge __aeabi_dcmpun
__aeabi_i2d __aeabi_ui2d        sqrt
(__aeabi_lmul: 64-bit integer multiply from the softfloat core itself)
```

plus `__aeabi_dcmple` and the `d2i/l2d` family if the extracted
wrapper code happens to emit them, and inline-bitop `fabs`/
`copysign` (on ARM soft these compile to `BIC`/`ORR`; the repo's
compat layer already wraps `copysign`/`copysignf` via
`msf64_copy_sign`/`msf32_copy_sign` as the P0 exemplar). Route: the
SDK's own float-flavour mechanism (SF-0 3.4 item 2) or
`pico_wrap_function`/`--wrap`, wrappers patterned on `work/msf_shim.c`
(memcpy bit casts into `msf64_*`, flags into per-core compat state;
single-core demo firmware makes this trivial). AEABI comparison
helpers set NZCV-style results via the `__aeabi_cdcmple`-family
contract - implement from the AEABI spec and validate with a
board-side port of `shim_selftest.c` before trusting any hash, the
same order this pass used. Provide trap stubs, not approximations,
for any other `__aeabi_*`/libm name the extracted link references.

Firmware checklist:

1. Extract per S4 6.2 keep-list (IAS15 step core, BASIC gravity -
   upstream default, matching this proof's main configuration -
   minimal sim state, warning sink stub). Carry GPL notices; keep
   the extracted tree outside `muse-softfloat/`.
2. **Gate before board work:** build the extracted source on the
   host with the Section 2 flags and require IAS15FH1 equality
   against `out/hashes_native.txt` for 2,000 steps (closes G1).
   Then the same extraction cross-compiled soft must match again
   under the host shim - only then flash.
3. Tables as hex from `out/tables_expected.txt`; ICs as hex from
   `work/ic_fig8.txt`; static arena (Section 5); `min_dt > 0`
   considered only as a hang guard - it *changes* the hash stream
   if it ever binds, so default stays 0 and any change re-pins the
   reference hashes.
4. Flags for the workload TUs: `-ffp-contract=off -fno-fast-math
   -O2/-O3 pinned` (M0+ has no FMA and no library-sqrt ambiguity,
   but pin anyway; Section 6.5 is the cautionary tale).
5. Output: per-step or per-K-step IAS15FH1 records (or digests via
   `sha256.c` verbatim) over USB CDC; host comparator is
   `work/compare_hashes.py` unchanged.
6. Decimal printing only on the host side from transferred bit
   patterns; firmware never formats a double (also avoids any
   bootrom/`__aeabi` float formatting paths, SF-0 Section 11).

### 8.2 Expected step rate: measurement approach

Exact host-side input now exists: ~13,100 binary64 ops per accepted
step at N=3 (Section 4; arithmetic mix 89% add/sub/mul, 11% div,
0.4% sqrt), scaling as O(N^2) pair work plus O(N) series work per stage.
Procedure for the Pico pass (no number is claimed here): (a) take
per-op cycle costs from the project's own board `bench` budget for
`msf64_add/sub/mul/div/sqrt` at the pinned clock; step-rate estimate
= cycles-per-op weighted sum, sanity-bracketed; (b) measure directly
on board with the RP2040 timer around 1,000 accepted steps of the
exact IC file, reporting steps/s at named clock/voltage with the
UF2 hash, per AGENTS.md board-evidence rules; (c) report the
encounter-phase worst case separately (dt collapses to ~1e-11 near
figure-8 close approaches; steps get *more* expensive there through
more predictor-corrector iterations, so a single mean rate misleads).
The ~53x host slowdown of the soft build is a libcall-overhead
artifact of x86-64 and must not be quoted as a Pico prediction.

### 8.3 Demo scenario for the video (BELIEVED)

Figure-8, N=3, exactly this proof's configuration: three equal
stars endlessly chasing each other through the same curve is
self-explaining on screen, numerically vicious (close triple
encounters, dt swinging over ten decades), and already has 20,000
steps of reference hashes (`out/h_fig8_long_native.txt`). Camera
script: desktop (unmodified strict build) and Pico run side by side;
host renders orbit trails from transferred bit patterns; every K
steps the IAS15FH1 digest types onto the screen from both machines
and locks identical - video-tools' hash-reveal primitive already
exists (`video/STORYBOARD.md` per ledger 2026-10-27 07:11) and can
consume `out/hashes_*.txt` directly. End card quotes the claim
precisely: "bit-identical to the unmodified desktop build
(gcc 16.1, -O3, -ffp-contract=off) for 20,000 steps" - never stronger
than the hash evidence (SF-0 Section 11). If step rate makes a full
period (t=6.33, MEASURED 944 accepted steps in this configuration,
`scripts/18_period.sh`) too slow for the cut, show one
close-encounter passage in real time and time-lapse the rest; the
hashes do not care.

## 9. What remains (honest subset accounting)

- Extraction (G1) and its host gate; AEABI compat wrappers (G2,
  wave-3 repo work, semantics prototyped here); board build, CDC
  replay, step-rate measurement, footage.
- `H_full` across *optimisation levels* is compiler-sensitive for
  the library-sqrt reason only (Section 6.5); the desktop reference
  pins `-O3`, and the Pico build has no second sqrt, so no action
  beyond pinning.
- Only the configurations of Section 6.3 were run. Untested by
  design (would each want one matrix row before any stronger claim):
  AARSETH85 and INDIVIDUAL modes, `min_dt>0` clamping, step
  rejection storms with restarts mid-run (the figure-8 long run's
  tiny dt passages make some rejections likely but I did not count
  them), N>3, test particles, ghost boxes, MEGNO. The driver's
  IC-file knobs cover the first three cheaply.
- The `sqrt7` negative/zero/subnormal corners were exercised only
  as far as these trajectories took them (plus the directed
  selftest); `epsilon=0` fixed-dt mode untested.

## 10. Reproduction index

`scripts/00_all.sh` runs, in order: 01 fetch -> 02 msf export ->
04/05 native build+run -> 06 independent validation (hashlib +
determinism) -> 09 shim selftests -> 10 soft build+run ->
11 comparison -> 12 configuration matrix + 20k steps -> 14 tables ->
15 sizes/ARM census -> 16 inventory -> 17 negative controls.
Probes that informed design: `03*` (flag search), `07*` (soft
census), `08` (comparison contract), `13` (SSE attribution),
`17b-e` (sqrt root cause). Logs in `out/`, sources in `work/`.
Elapsed for this pass: ~30 minutes of the 240-minute box (dispatch
07:01, proof 07:26 per ledger; remainder used on controls,
inventories, and this report).



