# S3 — Target survey: pico-sdk float/double on RP2040, bootrom, SIO, memory

Surveyor S3 (target), read-only. Sources, all READ directly this run:

- pico-sdk 2.3.1 at `C:\Users\logan\pico\pico-sdk` (version READ:
  `pico_sdk_version.cmake` sets 2.3.1). No git was run there.
- RP2040 Datasheet, official PDF `RP-008371-DS-1-rp2040-datasheet.pdf`
  (build-date 2025-02-20, 642 pages; MEASURED: downloaded 5,301,205 bytes,
  text-extracted with pypdf to `scratch/S3/datasheet_text.txt`). Datasheet
  cites below are section/table numbers; the page numbers in the running
  footer are also given where useful.
- `<ledger>/README.md` and `<ledger>/lead.md`, read before starting and
  again before writing this report.

Claim marks: READ = stated in a cited source. MEASURED = obtained by
running something this session (extraction/count only; no board code was
run, no cycle was measured by me). BELIEVED = my inference from the cited
facts, not stated in a source.

SDK paths below are relative to the pico-sdk root unless they start with
`scratch/`.

## 1. pico-sdk float/double support on RP2040

### 1.1 The wrapping mechanism is GNU-ld `--wrap`, not weak symbols (READ)

- `src/CMakeLists.txt:71-73`:
  `function(pico_wrap_function TARGET FUNCNAME)` does exactly one thing:
  `target_link_options(${TARGET} INTERFACE "LINKER:--wrap=${FUNCNAME}")`.
- The replacement symbols are named `__wrap_<name>`:
  `src/rp2_common/pico_platform_compiler/include/pico/platform/compiler.h:188`
  `#define WRAPPER_FUNC(x) __wrap_ ## x` (and `:209` `WRAPPER_FUNC_NAME`
  for assembler). C replacements are written `float WRAPPER_FUNC(ldexpf)(...)`
  (e.g. `src/rp2_common/pico_float/float_math.c:92`).
- Assembler replacements are strong globals, not weak:
  `src/rp2040/pico_platform/include/pico/asm_helper.S` defines
  `wrapper_func x` as `regular_func WRAPPER_FUNC_NAME(x)`, and
  `regular_func` emits `.global`. (A `weak_wrapper_func` macro exists in
  the same file but is not what the RP2040 float/double files use;
  MEASURED by grep of the two `*_aeabi_rp2040.S` files.)
- Consequence of `--wrap` (BELIEVED, standard GNU ld semantics, not
  re-verified on target here): every undefined reference to the wrapped
  name from any linked object or archive member resolves to `__wrap_<name>`;
  the original definition remains reachable as `__real_<name>`.
  `REAL_FUNC(x)` is defined at `compiler.h:189` but the float/double
  implementations do not call through to `__real_` (MEASURED by grep).

### 1.2 Which symbols are wrapped (the interposition surface) (READ)

The wrap lists are the `wrap_float_functions` /
`wrap_double_functions` CMake functions:

- Float: `src/rp2_common/pico_float/CMakeLists.txt:21-103`. On RP2040 it
  is invoked with no `NO_*` options (`:127` `wrap_float_functions(pico_float_pico)`),
  so all groups are wrapped:
  - arithmetic (`:24-28`): `__aeabi_fadd`, `__aeabi_fdiv`, `__aeabi_fmul`,
    `__aeabi_frsub`, `__aeabi_fsub`
  - compares (`:31-39`): `__aeabi_cfcmpeq`, `__aeabi_cfrcmple`,
    `__aeabi_cfcmple`, `__aeabi_fcmpeq`, `__aeabi_fcmplt`, `__aeabi_fcmple`,
    `__aeabi_fcmpge`, `__aeabi_fcmpgt`, `__aeabi_fcmpun`
  - int32 conv (`:42-45`): `__aeabi_i2f`, `__aeabi_ui2f`, `__aeabi_f2iz`,
    `__aeabi_f2uiz`
  - int64 conv (`:48-51`): `__aeabi_l2f`, `__aeabi_ul2f`, `__aeabi_f2lz`,
    `__aeabi_f2ulz`
  - float->double (`:54`): `__aeabi_f2d`
  - `sqrtf` (`:58`); SCI (`:61-67`): `cosf sinf tanf atan2f expf logf
    sincosf`; SCI_EXTRA (`:70-98`): `ldexpf copysignf truncf floorf ceilf
    roundf asinf acosf atanf sinhf coshf tanhf asinhf acoshf atanhf exp2f
    log2f exp10f log10f powf powintf hypotf cbrtf fmodf dremf remainderf
    remquof expm1f log1pf`; `fmaf` (`:101`).
- Double: `src/rp2_common/pico_double/CMakeLists.txt:24-103`, likewise
  invoked wrap-everything on RP2040 (`:114`). Same shape with `d` names:
  `__aeabi_dadd/ddiv/dmul/drsub/dsub` (`:27-31`); `__aeabi_cdcmpeq/
  cdrcmple/cdcmple/dcmpeq/dcmplt/dcmple/dcmpge/dcmpgt/dcmpun` (`:34-42`);
  `__aeabi_i2d/ui2d/d2iz/d2uiz` (`:45-48`); `__aeabi_l2d/ul2d/d2lz/d2ulz`
  (`:51-54`); `__aeabi_d2f` (`:57`); `sqrt` (`:60`); `cos sin tan atan2
  exp log` (`:63-68`); SCI_EXTRA (`:71-101`): `ldexp copysign trunc floor
  ceil round sincos asin acos atan sinh cosh tanh asinh acosh atanh exp2
  log2 exp10 log10 pow powint hypot cbrt fmod drem remainder remquo
  expm1 log1p fma`. Note asymmetry (READ): `fma` is inside double's
  SCI_EXTRA group, while `fmaf` has its own `NO_FMAF` group in float;
  `sincosf` is in float's SCI group, `sincos` in double's SCI_EXTRA.

### 1.3 "Wrapped" does not mean "in ROM": three implementation tiers (READ)

On RP2040 the `pico` flavour is assembled from four files each
(float: `CMakeLists.txt:120-128`; double: `:106-114`):

- `float_aeabi_rp2040.S` / `double_aeabi_rp2040.S` — the `__wrap_`
  entry points;
- `float_init_rom_rp2040.c` / `double_init_rom_rp2040.c` — runtime-init
  table copy (section 1.5);
- `float_math.c` / `double_math.c` — SDK C implementations of the
  SCI_EXTRA libm set, built on top of the basic ops;
- `float_v1_rom_shim_rp2040.S` / `double_v1_rom_shim_rp2040.S` — SDK
  software shims for ROM V1 (section 1.5).

Tier A — tail-call into the bootrom via the copied pointer table.
`table_tail_call` loads `sf_table[offset]` and `bx`s to it
(float: `float_aeabi_rp2040.S:81-91`; double via `sd_table`,
`double_aeabi_rp2040.S:83-95`). MEASURED (grep of `SF_TABLE_` uses):
float ROM-routed entry points are `__aeabi_fadd/fsub/fmul/fdiv`
(`float_aeabi_rp2040.S:136,139,165,226`), `sqrtf` (`:624`),
`cosf/sinf/tanf` (`:649,678,766`, each behind a range check, section 2.3),
`expf/logf` (`:799,803`), `atan2f` (`:795`), `__aeabi_f2d` (`:615`),
the 64-bit conversions `__aeabi_l2f/ul2f/f2lz(partly)/f2ulz`
(`:533,544,573,589`), and the non-AEABI SDK helpers
`float2int/float2fix/float2uint/float2ufix/fix2float/ufix2float/
fix642float/ufix642float/float2int64/float2fix64/float2ufix64`
(`:472-594`). Double mirrors this with the same `SF_TABLE_*` offsets
applied to `sd_table` (`double_aeabi_rp2040.S:167-933`, grep list in my
scratch notes), including `__aeabi_d2f` via `SF_TABLE_FLOAT2DOUBLE`
(`:698`) and `sincos` via `SF_TABLE_V3_FSINCOS` (`:814`).

Tier B — implemented in SDK assembler in the wrapper file itself, never
touching the ROM table (READ):
- All compares. Float compares are hand-written bit manipulation that
  flushes denormals and detects NaNs before an integer compare
  (`float_aeabi_rp2040.S:228-362`); double likewise
  (`double_aeabi_rp2040.S:269-418`). The ROM compare slots are never
  called: `SF_TABLE_FCMP_FAST` (0x10), `SF_TABLE_FCMP_FAST_FLAGS` (0x14)
  and `SF_TABLE_FCMP_BASIC` (0x54) appear only as defines in
  `src/rp2_common/pico_bootrom/include/pico/bootrom/sf_table.h:16,17,36`
  and nowhere else in `src/` (MEASURED by grep). The datasheet marks
  0x10/0x14 "deprecated, do not use" (Table 169).
- 32-bit int<->float conversions: `__aeabi_i2f/ui2f` are SDK asm using
  the ROM CLZ32 function pointer (`float_aeabi_rp2040.S:365-420`, calls
  through `sf_clz_func` at `:390-392`); `__aeabi_f2iz` is SDK asm
  (`:423-452`). `__aeabi_f2uiz` does go to ROM `FLOAT2UINT` (`:505`),
  which rounds toward -Infinity — for the C truncating semantics this
  only coincides because negative inputs clamp to 0 (BELIEVED reading of
  the code; the ROM function's -Inf rounding is READ, datasheet
  Table 169 offset 0x24). The SDK-only round-toward-zero and
  round-toward--Inf helpers are distinct exported names:
  `float2int_z` vs `float2int` (`float_aeabi_rp2040.S:426,471`).
- Double 32-bit conversions are likewise SDK asm:
  `__aeabi_i2d/ui2d` (`double_aeabi_rp2040.S:426-456`),
  `__aeabi_d2iz` (`:460-...`), while `__aeabi_d2uiz` tail-calls ROM
  (`:512`). This matches the datasheet note: "some conversion functions
  are re-implemented in the SDK to be faster" (Section 2.8.3.2.2).
- `sincosf` on RP2040 float is SDK asm that calls the ROM `_fsin` slot
  and unpacks two results from r0/r1 (`float_aeabi_rp2040.S:698-739`);
  there is no separate ROM sincos call on the float side (the V3
  `_fsincos` slot 0x48 is used only on the double side,
  `double_aeabi_rp2040.S:814`).

Tier C — implemented in SDK C in `float_math.c` / `double_math.c`
(READ; MEASURED list from `WRAPPER_FUNC(` grep): exactly the SCI_EXTRA
sets plus `ldexpf/copysignf` etc. — float: `float_math.c:92` (ldexpf)
through `:580` (remainderf); double: `double_math.c:95` (ldexp) through
`:624` (remainder). Notable accuracy-relevant facts in the source:
`fmaf` is `(float)((double)x*(double)y+(double)z)` with the comment
"has double rounding so not exact" (`float_math.c:334-338`); `fma`
(double) is plain `x*y+z`, unfused (`double_math.c:348`); `expm1/log1p`
(both precisions) are naive `exp(x)-1` / `log(1+x)`
(`double_math.c:345-346`, float via double intermediates
`float_math.c:332-333`).

### 1.4 Flavours and selection switches (READ)

- Three flavours per precision: `pico` (default), `compiler` (empty
  library, "no custom implementation; falls thru to compiler",
  float `CMakeLists.txt:5-6`), `none` (every wrapped symbol is a
  `panic("float support is disabled")` stub sharing one body,
  `float_none.S:13-73` and tail). Documented the same way in
  `pico/float.h:23-31` and `pico/double.h:23-31`.
- Selection is per-executable: CMake var `PICO_DEFAULT_FLOAT_IMPL` /
  `PICO_DEFAULT_DOUBLE_IMPL` (default `pico`, float `CMakeLists.txt:15`,
  double `:18`), or `pico_set_float_implementation(TARGET IMPL)` /
  `pico_set_double_implementation(...)`, which set target properties
  `PICO_TARGET_FLOAT_IMPL=pico_float_${IMPL}` (float `:189-196`) /
  `PICO_TARGET_DOUBLE_IMPL=pico_double_${IMPL}` (double `:142-149`);
  a generator expression picks that library (float `:18-19`).
- Linkage by default: `pico_runtime`'s library list includes
  `pico_float`, `pico_double`, `pico_divider`, `pico_int64_ops`,
  `pico_bit_ops`, `pico_thread_local`
  (`src/rp2_common/pico_runtime/CMakeLists.txt:21-39`), and
  `pico_stdlib` pulls in `pico_runtime` — so a normal SDK executable
  gets the wrapped implementation without naming it.
- Placement switches: `PICO_FLOAT_IN_RAM` / `PICO_DOUBLE_IN_RAM`
  (PICO_CONFIG, default 0; `pico/float.h:151-154`, `pico/double.h:132-135`)
  switch the wrapper sections from flash `.text.*` to RAM sections
  (float `float_aeabi_rp2040.S:17-23`; double `:18-24`). They move only
  the SDK wrapper/shim code; the ROM routines stay in ROM (which is
  single-cycle anyway, section 4.2).
- NaN behaviour switch: `PICO_FLOAT_PROPAGATE_NANS` /
  `PICO_DOUBLE_PROPAGATE_NANS` guard extra pre/post checks in the asm
  wrappers (`float_aeabi_rp2040.S:35,44,52-79` and passim) and in the
  `*_math.c` files (`float_math.c:57-68`). MEASURED: I found no
  `PICO_CONFIG` declaration and no default `#define` for either switch
  anywhere under `src/` headers/CMake — they are simply undefined
  (hence 0) unless the user defines them. The SDK's own double test
  defines both to 1 (`test/pico_float_test/CMakeLists.txt`, READ).
  Default build therefore does **not** propagate NaNs; it inherits the
  ROM behaviour of section 2.2.

### 1.5 ROM versions on RP2040, and the V1 shim machinery (READ)

- Version mapping: byte at `0x13` is the ROM version;
  `rp2040_rom_version()` returns "1 for RP2040-B0, 2 for RP2040-B1, 3 for
  RP2040-B2" (`src/rp2040/pico_platform/include/pico/platform.h:143-152`).
  Datasheet Section 2.8 says the same: "versions 1, 2 and
  3 of the bootrom … correspond to the B0, B1 and B2 silicon". So
  "RP2040 = ROM V1" is false in general; the project board is rev B2
  (lead ledger, Phase 0 entry), i.e. ROM V3.
- Table sizes: `SF_TABLE_V1_SIZE 0x54`, `SF_TABLE_V2_SIZE 0x80`
  (`sf_table.h:34,48`). The same header/offsets serve both precisions;
  the double table is a separate ROM table under code `'S','D'`, the
  float table under `'S','F'` (datasheet Table 171, Section 2.8.3.3;
  SDK lookups at `float_init_rom_rp2040.c:25` and
  `double_init_rom_rp2040.c:50-51`).
- Init: `__aeabi_float_init` / `__aeabi_double_init` are registered as
  runtime-init functions at priority `"00350"` for both
  (`float_aeabi_rp2040.S:13`, `double_aeabi_rp2040.S:16`,
  `pico/runtime_init.h:205-211`). Each copies the ROM table into a
  single shared RAM array — `uint32_t sf_table[SF_TABLE_V2_SIZE / 2]`
  (`float_init_rom_rp2040.c:14`) / `sd_table[...]`
  (`double_init_rom_rp2040.c:14`) — and resolves `sf_clz_func` from
  `ROM_FUNC_CLZ32`. The header warns the table is "NOT PUBLIC OR
  NECESSARILY COMPLETE … NOT SAFE TO CALL … FROM ARBITRARY CODE"
  (`float_init_rom_rp2040.c:12-13`).
- V1 (B0) gaps: float entries at offsets >= 0x54 do not exist, and
  there is no double table at all (datasheet Section 2.8.3.2.2 note;
  Table 169/170 "N/A" cells). What happens is governed by the
  conjunction `PICO_FLOAT_SUPPORT_ROM_V1 && PICO_RP2040_B0_SUPPORTED`
  (resp. DOUBLE). Both default to 1
  (`src/rp2040/pico_platform/include/pico/platform.h:45-57`), but board
  headers override `PICO_RP2040_B0_SUPPORTED` per board — e.g.
  `boards/pico.h:83` sets 1, `boards/pico_w.h:82` sets 0 (MEASURED by
  grep across `src/boards/include/boards/`).
  - Conjunction true: missing table entries are pre-filled with
    `float_table_shim_on_use_helper` / `double_table_shim_on_use_helper`;
    each `shimmable_table_tail_call` embeds an SVC-encoded table offset
    plus a shim pointer after the branch (float macro
    `float_aeabi_rp2040.S:93-104`), and on first use the helper patches
    the RAM table entry to the SDK software shim in
    `float_v1_rom_shim_rp2040.S` / `double_v1_rom_shim_rp2040.S`
    (init comments `float_init_rom_rp2040.c:43-53`; the double shim
    file is a full software double implementation — `dadd_shim` …
    `dln_shim`, ~2000 lines, READ by symbol grep). Float also shims
    `FLOAT2INT/FLOAT2FIX` on V1 for "-0 and -denormal handling"
    (`float_init_rom_rp2040.c:54-55`).
  - Conjunction false and ROM is V1: entries are filled with a
    `panic()` stub (`missing_float_func_shim`, float init `:17-20,58-64`;
    double init `:16-19,42-47` — double fills *every* entry).
- V2 vs V3 differences that the SDK cares about: the `_fsincos`/
  `_sincos` slot at 0x48 exists only in V3 (datasheet Tables 169/170);
  on ROM < 3 the double init installs the shim-on-use helper into
  `sd_table[SF_TABLE_V3_FSINCOS/4]` (`double_init_rom_rp2040.c:67-70`),
  and `double_aeabi_rp2040.S:814-831` bootstraps a software sincos.
  `_fsqrt` of a negative returns +Inf on V1, -Inf on V2/V3 (datasheet
  Table 169 offset 0x18); the float wrapper contains V1-only fixup asm
  for this (`float_aeabi_rp2040.S:619-638`).

### 1.6 What stays with the compiler / C library (READ + BELIEVED)

- Anything not in the two wrap lists of section 1.2. Concretely
  unwrapped (MEASURED against the CMake lists): `fabsf/fabs`,
  `frexpf/frexp`, `modff/modf`, `scalbn*`, `rint*`/`nearbyint*`,
  `erf*`, `tgamma*`/`lgamma*`, `nan*`, all `*l` long-double names,
  half-precision helpers (`__aeabi_f2h`, `__aeabi_h2f`, `__gnu_*2h*`),
  and every other libm function. Those come from the toolchain C
  library (newlib/picolibc per `PICO_CLIB`) — BELIEVED for the specific
  library, READ for "compiler flavour = fall through to compiler"
  (section 1.4).
- Non-FP `__aeabi` helpers are wrapped by *other* SDK libraries, not
  pico_float/pico_double: integer divide `__aeabi_idiv/uidiv/ldivmod…`
  by `pico_divider` (`src/rp2_common/pico_divider/CMakeLists.txt:43-48`),
  `__aeabi_lmul` by `pico_int64_ops` (`CMakeLists.txt:30`), bit ops
  `__clzsi2/__popcountsi2…` by `pico_bit_ops` (`CMakeLists.txt:27-39`).
  A drop-in FP replacement does not need to supply these (READ).
- The wrap lists use only Arm EABI names (`__aeabi_*`). No
  compiler-rt-style names (`__addsf3`, `__mulsf3`, …) are wrapped for
  Arm; those names appear in the SDK only on the RISC-V/Hazard3 path
  (`pico/float.h:140-146`, `float_single_hazard3.S`). BELIEVED:
  LLVM/Clang for `arm-none-eabi` soft-float also emits the `__aeabi_*`
  names, which is why the same single wrap list serves both toolchains
  in the SDK test matrix.
- Negation/absolute value: no `__aeabi_fneg/dneg` wrappers exist (the
  AEABI has no such required helper; BELIEVED the compiler inlines a
  sign-bit flip — `fneg/dneg` helpers inside `*_math.c` do exactly a
  sign-bit XOR on the bit pattern, `float_math.c:152-156`).

## 2. Bootrom floating point: routine list, accuracy, caveats

All READ from datasheet Section 2.8.3.2 (pp. 135-142 of the PDF
footer pagination), cross-checked against `sf_table.h` offsets.

### 2.1 Routine list (Tables 169 and 170)

Single-precision table (`'S','F'`), offsets common to V1/V2/V3 unless
noted. Average cycles are in section 4.1.

| Off | Routine | Notes |
|---|---|---|
| 0x00 | `_fadd` | |
| 0x04 | `_fsub` | |
| 0x08 | `_fmul` | |
| 0x0c | `_fdiv` | |
| 0x10 | deprecated | SDK name `SF_TABLE_FCMP_FAST`; do not use |
| 0x14 | deprecated | SDK name `SF_TABLE_FCMP_FAST_FLAGS`; do not use |
| 0x18 | `_fsqrt` | negative -> -Inf (V1: +Inf) |
| 0x1c | `_float2int` | round -Inf, clamp |
| 0x20 | `_float2fix` | round -Inf, clamp |
| 0x24 | `_float2uint` | round -Inf, clamp |
| 0x28 | `_float2ufix` | round -Inf, clamp |
| 0x2c | `_int2float` | round-nearest-even |
| 0x30 | `_fix2float` | round-nearest-even |
| 0x34 | `_uint2float` | round-nearest-even |
| 0x38 | `_ufix2float` | round-nearest-even |
| 0x3c | `_fcos` | only -128 < x < 128 |
| 0x40 | `_fsin` | only -128 < x < 128 |
| 0x44 | `_ftan` | only -128 < x < 128 |
| 0x48 | deprecated in V1/V2; `_fsincos` in V3 | sin in r0, cos in r1; -128..128 |
| 0x4c | `_fexp` | |
| 0x50 | `_fln` | |
| 0x54 | `_fcmp` (V2/V3 only) | returns -1/0/1; SDK never calls it |
| 0x58 | `_fatan2` (V2/V3 only) | |
| 0x5c | `_int642float` (V2/V3) | |
| 0x60 | `_fix642float` (V2/V3) | |
| 0x64 | `_uint642float` (V2/V3) | |
| 0x68 | `_ufix642float` (V2/V3) | |
| 0x6c | `_float2int64` (V2/V3) | round -Inf, clamp |
| 0x70 | `_float2fix64` (V2/V3) | round -Inf, clamp |
| 0x74 | `_float2uint64` (V2/V3) | round -Inf, clamp |
| 0x78 | `_float2ufix64` (V2/V3) | round -Inf, clamp |
| 0x7c | `_float2double` (V2/V3) | |

Double-precision table (`'S','D'`, V2/V3 only — absent entirely in V1):
identical offsets with `double` substituted for `float` —
`_dadd _dsub _dmul _ddiv`, deprecated 0x10/0x14, `_dsqrt`,
`_double2int/_fix/_uint/_ufix`, `_int2double/_fix2double/
_uint2double/_ufix2double`, `_dcos/_dsin/_dtan` (range -1024..1024),
`_dexp`, `_dln`, `_dcmp`, `_datan2`, `_int642double`, `_fix642double`
(datasheet Table 170 prints this one as `_dix642double` at 0x60 —
BELIEVED typo; the SDK offset name is `SF_TABLE_FIX642FLOAT`),
`_uint642double/_ufix642double`,
`_double2int64/_fix64/_uint64/_ufix64`, `_double2float` at 0x7c, and
V3-only `_sincos` at 0x48 (sin in r0/r1, cos in r2/r3).

Bootrom data entries `fplib_start` (`'F','S'`) and `fplib_end`
(`'F','E'`) delimit the FP library so it can be copied to RAM if
desired (Table 171). The SDK does not do this (READ of the init files:
it copies only the pointer table).

### 2.2 Accuracy and IEEE-754 deviations (READ, Section 2.8.3.2.1)

Documented verbatim semantics of the ROM implementation:

- "The IEEE single- and double-precision data formats are used
  throughout, but … input denormals are treated as zero, input NaNs
  are treated as infinities, output denormals are flushed to zero,
  and output NaNs are rendered as infinities."
- "Only the round-to-nearest, even-on-tie rounding mode is
  supported. Traps are not supported."
- "The five basic operations return results that are always correctly
  rounded." (The five = add, subtract, multiply, divide, square root;
  named in the preceding paragraph as the performance-emphasised set.)
  Correctly rounded *subject to* the flush/treat-as rules above —
  e.g. a result in the denormal range is flushed to zero rather than
  returned as the correctly rounded denormal (my reading of the two
  sentences together; the datasheet does not reconcile them further).
- "The scientific functions always return results within 1 ULP …
  In many cases results are better", with poorer ULP accuracy where a
  large normalising shift occurs on reconversion (sin near a multiple
  of pi, cos near an odd multiple of pi/2, log near 1, tan for very
  large results).
- No exception flags exist anywhere in this design: the datasheet
  defines no status/flags register or memory flag word for FP, traps
  are unsupported, and the ROM functions follow plain Arm EABI
  register passing (Section 2.8.3.2.2). MEASURED: no `fenv`/flags
  symbol is wrapped or defined by pico_float/pico_double (grep of
  the four RP2040 source files and the two headers — `float.h`/
  `double.h` contain no flags API). Any IEEE flags a replacement
  wants must be entirely new state (section 6).
- Error cases render as infinities, not NaNs: `_fsqrt` of negative
  -> -Inf (V1: +Inf); `_fln/_dln` of non-positive -> -Inf (extracted
  text: "If … return -Infinity", Tables 169/170). SDK tier-C code
  inherits this unless `PICO_*_PROPAGATE_NANS=1`, in which case
  wrappers convert some Inf results back to NaN with explicit asm
  checks (e.g. `float_aeabi_rp2040.S:174-199` fdiv/fsub helper,
  `:201-226` fmul "infinite to nan") and `*_math.c` substitutes
  `NAN`/`NANF` in `fnan_or/dnan_or` (`float_math.c:166-172`).
- The SDK headers say the same in vaguer words: the implementations
  "don't support all the features of a fully compliant floating point
  implementation" (`pico/float.h:33-37`, `pico/double.h:33-37`).

### 2.3 SDK-side corrections around ROM limits (READ)

- Range reduction: ROM `_fsin/_fcos/_ftan` are only correct for
  -128 < x < 128 (double: -1024..1024). The SDK wrappers check the
  exponent and, out of range, call `remainderf(x, 2*pi)` first
  (`float_aeabi_rp2040.S:640-667` cosf, same shape sinf/tanf). Note the
  reduction constant is the single-precision `0x40c90fdb` (2*pi in
  float), so large-argument accuracy is bounded by that float
  constant (BELIEVED consequence; the constant is READ).
- Divider interaction: wrappers whose ROM path uses the SIO divider
  (`__aeabi_fdiv`, `tanf`, `__aeabi_ddiv`) save/restore divider state
  when CSR.DIRTY, or disable interrupts instead if
  `PICO_DIVIDER_DISABLE_INTERRUPTS` (`float_aeabi_rp2040.S:149-172`,
  `:750-773`; double `:180-208`). This is the established pattern a
  kernel using the divider inside an AEABI helper must follow
  (section 3.1).

## 3. SIO hardware usable by integer softfloat kernels

SIO facts are READ from datasheet Section 2.3.1 (SIO overview),
2.3.1.5 (divider), 2.3.1.6 (interpolator), and the SDK headers/SVD
cited per line.

Per-core-ness (READ): "The SIO has a dedicated bus interface for each
processor's IOPORT" (Section 2.3.1); Figure 7 shows per-core CPUID,
Integer Divider, Interpolator 0, Interpolator 1, with FIFOs and the
32 spinlocks shared. The same address (`SIO_BASE 0xd0000000`,
`hardware/regs/addressmap.h:77`) from
either core reaches that core's own divider/interpolators. SIO is not
on the main bus — processor (or debugger) access only. Access is
single-cycle IOPORT, 32-bit words only (Section 2.3.1; Cortex-M0+
IOPORT segment 0xd0000000-0xdfffffff).

### 3.1 Hardware integer divider (one per core)

- Function: signed and unsigned 32/32 divide/modulo. Write dividend
  then divisor (signed aliases `DIV_SDIVIDEND/DIV_SDIVISOR` at SIO
  offsets 0x68/0x6c, unsigned `DIV_UDIVIDEND/DIV_UDIVISOR` at
  0x60/0x64 — `hardware/regs/sio.h:336-380`); result in
  `DIV_QUOTIENT` (0x70) / `DIV_REMAINDER` (0x74); status `DIV_CSR`
  (0x78) bits READY (bit 0) and DIRTY (bit 1) (`sio.h:419-452`).
- Latency: "8-cycle" computation, results readable on the 9th cycle;
  either poll READY or insert a fixed 8-cycle delay (datasheet
  2.3.1.5; identical text `hardware/divider.h:17-21`). Other CPU work
  may proceed during the wait — it is a latency, not a stall, unless
  the result registers are read early (BELIEVED: early read value is
  not defined by the datasheet text I extracted; the SDK always waits
  the 8 cycles, e.g. branch-padding in `divider.S` return path).
- Restart semantics: "A new calculation begins immediately with every
  write to an operand register, and a new operand write immediately
  squashes any calculation currently in progress" (2.3.1.5). The alias
  last written determines signedness. Writing a *result* register
  cancels any operation in progress — that is the restore mechanism.
- Save/restore contract (the part that bites): DIRTY is set by any
  divider register write and cleared by reading the quotient; SDK
  convention is quotient read last, always, even if unwanted
  (2.3.1.5 NOTE; `hardware/divider.h` result functions). State type is
  4 words (`hw_divider_state_t { uint32_t values[4] }`,
  `divider.h:478-480`) with `hw_divider_save_state` /
  `hw_divider_restore_state` implemented in `divider.S:39-62`
  (save reads dividend, divisor, remainder, quotient-last; restore
  writes back through the *unsigned* aliases to avoid re-signing the
  results — comment in `divider_helper.S`, macro
  `restore_div_state_and_return`). Assembly macros
  `save_div_state_and_lr` / `restore_div_state_and_return`
  (`hardware/divider_helper.S:24-71`) are what the float wrappers use;
  the macro comments document the interrupt-mid-restore windows in
  detail — a replacement kernel should reuse these macros rather than
  reinvent them (BELIEVED advice; the macros are READ).
- 64-bit division is *software* over this unit: `pico_divider`'s
  `divider_hardware.S` implements `divmod_u64u64_unsafe`
  (`:396-...`), `divmod_s64s64` etc. and wraps `__aeabi_ldivmod/
  uldivmod` (`:273,301`). There is no 64/32 hardware mode. For a
  softfloat kernel: the divider gives one 32/32 -> (q,r) step per
  ~8 cycles + register traffic; wide divisions must be multi-stepped
  in software exactly as `divmod_u64u64_unsafe` demonstrates
  (BELIEVED synthesis from the two READ facts).

### 3.2 Interpolators (two per core: INTERP0, INTERP1)

Register-level shape per interpolator (READ,
`hardware/structs/interp.h` and `hardware/regs/sio.h:454-...`):
`ACCUM[2]`, `BASE[3]`, `POP[3]`, `PEEK[3]`, `CTRL[2]`,
`ACCUM0_ADD/ACCUM1_ADD` (24-bit add-to-accumulator aliases),
`BASE_1AND0` (write both BASE0/BASE1 as 16+16). Struct size 0x40;
INTERP0 starts at SIO offset 0x80, INTERP1 at 0xc0
(`SIO_INTERP0_ACCUM0_OFFSET`, `hardware/regs/sio.h:456`;
`SIO_INTERP1_ACCUM0_OFFSET`, `sio.h:805`).

What a lane computes in one cycle (READ, datasheet 2.3.1.6 +
Figure 8, `hardware/interp.h:125-260` config setters):
result = BASEk + signextend(mask(ACCUM >> SHIFT)) with per-lane
controls SHIFT (0-31 logical right shift), MASK_LSB/MASK_MSB,
SIGNED, CROSS_INPUT (use other lane's accumulator), ADD_RAW (bypass
shift/mask), CROSS_RESULT (feed other lane's result to this
accumulator on POP), FORCE_MSB. Reading POPx returns the result and
simultaneously writes both lane results back to the accumulators;
PEEKx is side-effect-free. "The processor can write or read any
interpolator register in one cycle, and the results are ready on the
next cycle" (2.3.1.6).

Special modes (READ, `hardware/interp.h:211-244`):
- BLEND, INTERP0 only: LANE1 result is a linear interpolation between
  BASE0 and BASE1 by the low 8 bits of lane 1's shift/mask value
  (alpha in 1/256ths). This is the only true multiply-like operation
  in the unit, and it is 8-bit-alpha only.
- CLAMP, INTERP1 lane 0 only: shifted/masked ACCUM0 clamped to
  [BASE0, BASE1].
- OVERF flags in CTRL report masked-off MSBs set (structs header
  CTRL field comments) — these are interpolator-local status bits,
  not visible to any FP flags mechanism.

Ownership/save semantics (READ): SDK claim state is a single global
byte `static uint8_t _claimed` in
`src/rp2_common/hardware_interp/interp.c:15`, claimed via
`hardware/claim.h` (`interp_claim_lane` panics if already claimed,
`hardware/interp.h:74-84`). The claim namespace is *global*, not
per-core — bit index is `(interp_index<<1)|lane` (interp.c) — even
though the hardware instances are per-core; two cores cannot
independently SDK-claim "their own" INTERP0 lane 0 (READ of the code;
whether that is a known SDK wart or intended, I did not investigate).
`interp_save/restore` copy exactly `accum[2], base[3], ctrl[2]`
(`interp_hw_save_t`, `hardware/interp.h:314-344`; `interp.c:48-66`).
Unlike the divider there is no DIRTY bit and no automatic save/restore
in IRQ paths — a kernel using an interpolator inside a wrapped AEABI
function must claim it for exclusive use or save/restore all 7 words
itself, on every call, including nested/IRQ re-entry on the same core
(BELIEVED consequence of the READ facts; no SDK precedent of
interpolator use inside AEABI helpers was found — the float/double
code does not use interpolators at all, MEASURED by grep).

Useful-to-softfloat assessment (BELIEVED, from the operation list):
lanes can fuse shift+mask+sign-extend+add-base in one cycle, which
maps to exponent extraction, sticky-mask generation, alignment
shifts, and table-address generation; POP writeback gives a
one-instruction iterate step. It cannot do wide shifts >31,
left shifts, multiplies (except 8-bit blend alpha), or 64-bit
anything; and every use pays the claim/save cost above plus one-cycle
SIO reads, so the win case is inner loops that keep data in
ACCUM/BASE across many PEEK/POP reads.

## 4. Costs that set the yardstick

### 4.1 Published ROM cycle counts (READ, datasheet Tables 169/170)

The tables give *average* cycles over random input ("Cycles (Avg)"
column headers). Caution: the table captions as extracted read
"Timings are average time in us over random (worst case) input" while
the columns are headed Cycles — the numbers are only plausible as
cycles (a 71-cycle `_fadd` vs a nonsensical 71 us), so I report them
as cycles and flag the caption as a datasheet inconsistency
(BELIEVED interpretation; both texts are READ).

Single precision, V1 -> V2/V3 average cycles:
`_fadd` 71/71, `_fsub` 74/74, `_fmul` 69/58, `_fdiv` 71/71,
`_fsqrt` 63/63, `_float2int` 37/40, `_float2fix` 36/39,
`_float2uint` 38/39, `_float2ufix` 38/38, `_int2float` 55,
`_fix2float` 53, `_uint2float` 54, `_ufix2float` 52,
`_fcos` 603/587, `_fsin` 593/577, `_ftan` 669/653, `_fexp` 542/524,
`_fln` 810/789; V2-only additions: `_fcmp` 25, `_fatan2` 667,
`_int642float` 62, `_fix642float` 60, `_uint642float` 58,
`_ufix642float` 57, `_float2int64` 54, `_float2fix64` 53,
`_float2uint64` 42, `_float2ufix64` 41, `_float2double` 15;
V3-only `_fsincos` 577.

Double precision (V2/V3 only, one column): `_dadd` 91, `_dsub` 95,
`_dmul` 155, `_ddiv` 183, `_dsqrt` 169, `_double2int` 75,
`_double2fix` 74, `_double2uint` 63, `_double2ufix` 62,
`_int2double` 69, `_fix2double` 68, `_uint2double` 64,
`_ufix2double` 62, `_dcos` 1617, `_dsin` 1618, `_dtan` 1891,
`_dexp` 804, `_dln` 428, `_dcmp` 39, `_datan2` 2168,
`_int642double` 55, `_fix642double` 56, `_uint642double` 50,
`_ufix642double` 49, `_double2int64` 64, `_double2fix64` 63,
`_double2uint64` 53, `_double2ufix64` 52, `_double2float` 23;
V3-only `_sincos` 1718.

What these do NOT cover (READ): SDK wrapper overhead on top
(range checks, NaN checks if enabled, divider save/restore on
fdiv/ddiv/tanf, table indirection), the SDK-asm compares and
32-bit conversions (not ROM functions), and all tier-C libm. The
datasheet itself points at the SDK docs for "real world timings"
(Section 2.8.3.2.2). I found no published SDK-level cycle table in
the SDK tree (MEASURED grep for "cycle" over pico_float/pico_double:
only comments). What exists is a *measurement harness*:
`test/pico_float_test/float_benchmark.c` and `double_benchmark.c`
time each operation with the core SysTick and subtract input/output
overheads; their CMake builds them `copy_to_ram` with
`PICO_FLOAT_IN_RAM=1` / `PICO_DOUBLE_IN_RAM=1`
(`test/pico_float_test/CMakeLists.txt`, float/double benchmark
targets) — i.e. the SDK's own yardstick excludes XIP effects by
construction. Any replacement benchmark must state placement, clock
(default clk_sys 125 MHz, `platform_defs.h` `SYS_CLK_HZ` 125000000,
READ), and cache state to be comparable (BELIEVED methodology note).

### 4.2 Memory model (READ, datasheet Section 2.6 + SDK linker files)

- ROM: 16 kB at 0x00000000, "single-cycle read-only bus access …
  on a dedicated AHB-Lite arbiter" (2.6.1). ROM FP code therefore
  never pays flash costs — a structural advantage any flash-resident
  replacement does not have (BELIEVED framing of a READ fact).
- SRAM: 264 kB total — four 64 kB banks word-striped over
  0x20000000-0x2003ffff, two non-striped 4 kB banks at 0x20040000
  ("scratch X") and 0x20041000 ("scratch Y"), single-cycle access
  barring same-bank contention; the 64 kB banks are also mirrored
  non-striped at 0x21000000+ (2.6.2). SDK defaults match exactly:
  `RAM 0x20000000 256k, SCRATCH_X 0x20040000 4k, SCRATCH_Y
  0x20041000 4k, XIP_RAM 0x15000000 16k`
  (`src/rp2040/pico_platform/script_include/default_locations.ld`).
- XIP flash: 16 MB window at 0x10000000 behind a 16 kB, two-way
  set-associative cache, "1 cycle hit" (2.6.3.1). There is no fixed
  "wait states" number for a miss: a miss is a serial QSPI transfer
  whose cost depends on the SSI clock divider and flash command —
  SDK boot2 defaults `PICO_FLASH_SPI_CLKDIV 4`
  (`src/rp2040/boot_stage2/boot2_w25q080.S:44-45`), i.e. flash clock
  = clk_sys/4 = 31.25 MHz at 125 MHz (datasheet 2.6.3 NOTE), so
  miss latency is tens of system cycles per cache line and highly
  working-set dependent (BELIEVED quantification from the READ
  divider fact; I measured nothing). Cache can be disabled and used
  as a 16 kB SRAM bank at 0x15000000, one-cycle reads/writes with a
  write-read wait state (2.6.3.1).
- Placement idioms (READ,
  `src/rp2_common/pico_platform_sections/include/pico/platform/sections.h`):
  `__not_in_flash(group)` -> section attr via
  `PICO_NOT_IN_FLASH_PLACEMENT` (`:249-250`);
  `__not_in_flash_func(f)` (`:272-273`) and
  `__no_inline_not_in_flash_func` (`:283`);
  `__time_critical_func(f)` (`:318-319`, same default destination,
  `.time_critical.<group>` sections via `__in_ram`, `:42`);
  scratch placement `__scratch_x/__scratch_y(group)` (`:72-73,103-104`)
  -> `.scratch_x.*` / `.scratch_y.*`, linked into SCRATCH_X/Y regions
  (`pico_standard_link/script_include/sections_scratch.incl`).
  For assembler kernels the float wrappers show the pattern to copy:
  `float_section` macro picks `RAM_SECTION_NAME` (= `.time_critical.*`,
  `sections.h:337-338`) vs `SECTION_NAME` (= `.text.*`, `:341-342`)
  on `PICO_FLOAT_IN_RAM` (`float_aeabi_rp2040.S:17-23`).
  `pico_set_binary_type(T copy_to_ram)` / `no_flash` move whole
  binaries (used by the SDK benchmarks, section 4.1).

## 5. How a drop-in replacement interposes (READ facts, BELIEVED recipe)

Facts established in section 1 that determine the options:
interposition is `LINKER:--wrap=<name>` INTERFACE link options
(`src/CMakeLists.txt:71-73`) plus strong `__wrap_<name>` symbols
from the selected `pico_float_<impl>` / `pico_double_<impl>` library;
impl selection is a per-executable target property consumed by a
generator expression (`pico_float/CMakeLists.txt:18-19,189-196`).

Three routes, in increasing invasiveness (recipe = BELIEVED, each
step grounded in the cited READ mechanism; I did not build any of
them):

1. **New flavour library (the SDK-shaped route).** Define
   INTERFACE libraries `pico_float_<ourname>` /
   `pico_double_<ourname>` that (a) add our sources defining
   `__wrap___aeabi_fadd` etc. (via `WRAPPER_FUNC` in C or
   `wrapper_func` in asm), and (b) attach the same
   `pico_wrap_function(...)` calls — the helper functions
   `wrap_float_functions` / `wrap_double_functions`
   (pico_float `CMakeLists.txt:21-103`) exist precisely to emit the
   full list and accept `NO_*` exclusions; then select with
   `pico_set_float_implementation(app <ourname>)`. This keeps
   `pico/float.h` custom converters available only if we also
   provide the non-wrapped symbols (`int2float`, `float2fix`, … —
   plain `regular_func` exports in the RP2040 asm files) or accept
   their absence; `LIB_PICO_FLOAT_<IMPL>` compile definitions are
   generated from library target names by `pico_add_library`
   machinery (BELIEVED detail — flag for whoever implements:
   `float.h` behaviour keys off `LIB_PICO_FLOAT_COMPILER` etc.).
2. **Compiler flavour + own wraps.** `pico_set_float_implementation
   (app compiler)` (and double) removes all SDK wraps, then add our
   own `target_link_options(app PRIVATE -Wl,--wrap=__aeabi_fadd …)`
   with `__wrap_` definitions. Simpler to reason about (no
   interaction with SDK flavour machinery), loses the
   `wrap_*_functions` list maintenance and the pico header extras.
3. **Direct strong symbols, no --wrap.** Define `__aeabi_fadd`
   etc. directly in a normal object/library linked before libgcc;
   archive semantics then pre-empt the libgcc members. Requires the
   SDK wraps to be off (route 2's compiler flavour, or don't link
   `pico_float` at all — it arrives via `pico_runtime`'s list,
   section 1.4, so this also means using `pico_minimize_runtime`
   or not using `pico_stdlib`). Most fragile: any *other* object
   that also defines or wraps the same name is a hard duplicate
   instead of a `--wrap` redirection (BELIEVED, standard archive/ld
   behaviour).

Whichever route: the wrapped set of section 1.2 is the contract
surface. A partial replacement is possible in principle — wrap only
some names and let the rest fall through to `__real_` libgcc — but
only if the SDK flavour is `compiler` underneath; layering our
`--wrap` over `pico_float_pico`'s own `--wrap` for the same symbol
does not compose (one `__wrap_` definition wins; BELIEVED ld
semantics, untested here). Also note libm functions we do not wrap
will still execute our wrapped AEABI ops internally if the archive
member references them after wrapping is applied (BELIEVED, same ld
semantics) — so basic-op semantics changes (denormals, NaNs, flags)
propagate into unwrapped libm automatically.

## 6. Dual-core: what per-core state exists that FP flags could use

Facts only, per brief. There is today **no FP state at all**:
no flags, no rounding-mode storage, no per-core FP context (READ:
section 2.2). The candidate homes that exist in hardware/SDK:

- **Core identity**: SIO `CPUID` reads 0/1 by executing core
  (`hardware/structs/sio.h` CPUID field); `get_core_num()` is a
  one-load inline (`src/rp2040/pico_platform/include/pico/platform.h:114`).
- **Per-core SIO blocks**: divider and both interpolators are
  physically per-core at identical addresses (datasheet 2.3.1
  Figure 7). They are stateful but are *arithmetic* state with SDK
  save/restore contracts (sections 3.1/3.2) — using e.g. an ACCUM
  register as a flags word would collide with any interpolator user
  and with IRQ re-entry; no SIO register is designated spare
  (READ of the SIO register list; the collision consequence is
  BELIEVED).
- **TLS**: `pico_thread_local` defaults to per-thread mode
  (`pico_thread_local/CMakeLists.txt`: `PICO_DEFAULT_THREAD_LOCAL_IMPL`
  default `per_thread`). On Arm there is no TP register use by
  default path extracted here: the linker reserves one TLS region
  per core (`.tls0`/`.tls1`, `__tls0_base`/`__tls1_base` in
  `pico_standard_link/script_include/section_tls.incl`), and
  `thread_local.c` keeps `__tls_adjusted_by_core[2]` indexed by
  `get_core_num()` (`thread_local.c`, READ). So a
  `__thread uint32_t fp_flags;` would be per-core (not per-RTOS-
  thread) under the default mode, at the cost of the TLS access
  sequence on every flag touch (BELIEVED costing; mode facts READ).
  Modes `global` and `none` also exist and would make such a
  variable shared or undefined respectively.
- **Plain arrays indexed by core**: the SDK's own precedent for
  emulated divider results is `hw_divider_results[NUM_CORES]`
  (RP2350 path, `hardware/divider.h:55`) — i.e. `flags[2]` plus
  `get_core_num()` is an established in-SDK idiom (READ precedent;
  suitability BELIEVED — note it is per-core, not IRQ-nesting or
  RTOS-task aware, same caveat as TLS default mode).
- **Scratch registers**: watchdog `SCRATCH0..7` are eight shared
  32-bit registers (`hardware/regs/watchdog.h:106-...`), global to
  the chip, surviving watchdog resets per their purpose — not
  per-core, and writes are APB-peripheral accesses, not single-cycle
  SIO (READ addresses/bus; cost characterisation BELIEVED). They
  are a fact to know, not a good FP-flags home (BELIEVED).
- **Scratch X/Y SRAM banks** (4 kB each) are ordinary shared SRAM;
  "per-core" only by software convention to avoid bank contention
  (datasheet 2.6.2). A flags word in scratch X for core 0's stack
  bank is the same array-indexed-by-core idea with a contention
  benefit (BELIEVED).
- **Spinlocks**: 32 hardware spinlocks in SIO
  (`hardware/regs/sio.h:1146-...`, `NUM_SPIN_LOCKS 32` in
  `platform_defs.h`) exist for protecting shared state if flags
  were made global — but taking a spinlock, or any lock, inside an
  AEABI helper that IRQs also call invites deadlock on same-core
  re-entry (BELIEVED; the divider DIRTY-bit dance of section 3.1
  exists precisely because AEABI helpers must be IRQ-reentrant).
- **Interrupt masking** is the SDK's other established tool for
  AEABI-helper critical sections: `PICO_DIVIDER_DISABLE_INTERRUPTS`
  path saves PRIMASK and `cpsid i` around divider-using ROM calls
  (`float_aeabi_rp2040.S:155-162`). Any flags update that must be
  atomic against IRQ FP use on the same core has to use this, the
  save/restore pattern, or be a single SIO/SRAM store (BELIEVED
  synthesis of READ precedents).

Also relevant: `sf_table`/`sd_table` and `sf_clz_func` are single
shared globals initialised once at runtime init (section 1.5); the
ROM routines themselves take operands in registers and keep no
documented cross-call state other than the per-core divider
(BELIEVED from the EABI description + divider evidence; the
datasheet does not use the word "reentrant" for them). A replacement
that adds *shared* mutable FP state would be new failure surface
that the incumbent simply does not have.

## 7. Anything this brief got wrong

1. **"which helpers … are wrapped to bootrom" conflates two hops.**
   Everything is wrapped to SDK `__wrap_*` symbols; only Tier A
   (section 1.3) tail-calls the bootrom. All compares, the 32-bit
   conversions (mostly), and the entire SCI_EXTRA libm set are SDK
   code. There is no direct libgcc->ROM interposition.
2. **RP2040 is not "ROM V1 specifically".** V1 is B0 only;
   B1=V2, B2=V3 (section 1.5). The live board is B2/V3. V1 handling
   (shims) matters only if B0 support is kept, and it is gated by a
   conjunction of two switches that board headers frequently negate.
3. **The wrap mechanism guess "linker --wrap? weak?" resolves to
   --wrap only** for the FP symbols; weak is used only for shared
   helper pointers (`sf_clz_func` is `__attribute__((weak))`,
   `float_init_rom_rp2040.c:15`, so float+double can both declare it).
4. **"XIP flash wait states" is the wrong mental model** (section
   4.2): XIP is a cached serial interface — 1-cycle hits, serial
   misses at clk_sys/CLKDIV — with no datasheet wait-state constant.
   Yardsticks need working-set/cache-state declarations instead.
5. **Published cycle counts exist but are ROM-only, averages over
   random inputs, and the datasheet's own caption contradicts its
   column headers** (us vs cycles, section 4.1). There are no
   published end-to-end SDK numbers to beat; the yardstick must be
   produced with the SDK benchmark harnesses (which run from RAM).
6. Minor, found while reading (not brief errors): `pico/double.h:56`
   documents double compares under the float names (`__aeabi_cf*`)
   and `:68` names `__aeabi_d2d` where the wrapped symbol is
   `__aeabi_d2f`; datasheet Table 170 prints `_dix642double`;
   `sf_table.h` gives the deprecated compare slots respectable names
   (`SF_TABLE_FCMP_FAST*`) that the datasheet says not to use and
   the SDK never calls. None affect code, all could mislead a
   survey that trusts headers over tables.
7. The brief assumed interpolators might be straightforwardly
   "usable by integer softfloat kernels"; the hardware is, but the
   SDK ownership model is not AEABI-helper-shaped (global claim byte,
   7-word manual save/restore, no DIRTY fast path — section 3.2).
   Budget that cost before planning on them.

## Appendix: methods and limits

- MEASURED this session: SDK version string; grep-derived symbol and
  SF_TABLE-use lists; datasheet PDF byte size (5,301,205), page
  count (642), build date; ledger reads at start and pre-report.
  Grep scripts and raw outputs are under `scratch/S3/` (`grep*.sh`,
  `ds_grep*.sh`, outputs alongside; extracted datasheet text
  `datasheet_text.txt`).
- Nothing was compiled, linked, or run on the board. Every claim
  about runtime behaviour is READ from source/datasheet, not
  observed. In particular the ROM accuracy statements of section
  2.2 are the datasheet's claims, untested by me.
- Not investigated (out of brief or unreachable): RP2350 DCP/VFP
  paths beyond naming them; the bootrom source repository; newlib
  vs picolibc libm internals; FreeRTOS context-switch handling of
  divider/interp/TLS; worst-case (vs average) ROM timings, which
  neither source publishes.



