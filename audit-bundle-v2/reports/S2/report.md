# S2 surveyor report — authority and oracles

Author: surveyor-oracles (S2), read-only parcel. Workspace:
`C:\Users\logan\source\repos\Muse-Softfloat`. Read first: `ledger/README.md`,
`ledger/lead.md` (3 entries), `muse-softfloat/AGENTS.md`,
`softfloat-bootstrap-kit/tools/ledger.sh` header. Local probes are kept as
script files with logs in `scratch/S2/` (`probe*.sh/.log`, `mpmath_probe.py`);
nothing was built from third-party source and nothing outside `scratch/S2/`
and `ledger/S2.md` was written.

Tags, per brief: **READ** = read in a primary source fetched this run (URL
given). **MEASURED** = executed/observed on this host this run (script + log
in `scratch/S2/`). **BELIEVED** = inference or prior knowledge not verified
this run; treat as a pointer to verify, not a fact to gate on.

Clean room: no file, directory, or search result with `cft` in its name was
opened, searched inside, or listed by this parcel. The workspace top-level
listing taken at start contains no such name. No landing to disclose beyond
that statement (also in my ledger entry).

## Headlines

1. Berkeley authority is frozen: SoftFloat **3e** and TestFloat **3e**, both
   2018-01-20, both UC Regents **BSD-3-Clause** — copying code, redistributing
   generated vectors, and linking as a test-only oracle are all licence-legal;
   any bar on copying is project clean-room policy, not licence. (READ)
2. The host's default `gcc` in Git Bash is the **i686 (32-bit, x87,
   `FLT_EVAL_METHOD=2`)** compiler — as an oracle path it is wrong by default.
   The x86-64 SSE2 oracle exists only after putting
   `/c/msys64/mingw64/bin` first in `PATH`; invoking the 64-bit `gcc.exe` by
   absolute path with the wrong `PATH` fails *silently* (exit 1, no output)
   on any real compile. (MEASURED)
3. MPFR needs no installation: `mingw-w64-x86_64-mpfr 4.2.2-3` is already
   installed, headers/libs present, and a link+run smoke test passes — a
   genuinely foreign correctly-rounded oracle is available today. (MEASURED)
4. TestFloat's own docs declare its blind spots (hard div/sqrt rounding,
   decimal, post-1985 ops); the named supplements worth gating are the IBM
   Haifa FPgen IEEE-754R vectors, exhaustive binary16/binary32-unary sweeps,
   and MPFR-directed randoms for binary64 div/sqrt/FMA. (READ)
5. Licence triage in one line each: Berkeley = BSD-3 (copy allowed),
   compiler-rt = Apache-2.0 WITH LLVM-exception (copy allowed),
   libgcc soft-fp = GPLv3+ + Runtime Exception (read; do not copy source into
   a non-GPL library). (READ)

---

## 1. Berkeley SoftFloat + TestFloat

### 1.1 Current release

- **READ** — The latest SoftFloat is **Release 3e (2018 January)** and the
  current TestFloat is **Release 3e (2018 January)**; both interface docs are
  dated 2018 January 20 (John R. Hauser).
  Sources: https://www.jhauser.us/arithmetic/SoftFloat.html,
  https://www.jhauser.us/arithmetic/TestFloat.html,
  https://www.jhauser.us/arithmetic/SoftFloat-3/doc/SoftFloat.html
  ("The current version of SoftFloat is Release 3e"),
  http://www.jhauser.us/arithmetic/TestFloat-3/doc/TestFloat-general.html.
- **READ** — Release history that matters for pinning: 3b added binary16; 3c
  added optional round-to-odd; **3d (2017-08) fixed sqrt bugs in the 64/80/128
  functions present in all prior Release-3 versions** (f64 flaw ~1 ulp a few
  times per 10^9; 80/128 flaws could corrupt many low bits); 3e is minor fixes
  plus ARM specialization. Any pin older than 3d is a defective oracle for
  sqrt. Same sources as above.
- **READ/MEASURED (fetch)** — Pinning hazard: the `ucb-bar/berkeley-softfloat-3`
  GitHub `master` Makefile (`build/Linux-x86_64-GCC/Makefile`, fetched raw)
  lists bfloat16 objects (`s_normSubnormalBF16Sig`, `s_roundPackToBF16`,
  `s_bf16UIToCommonNaN`) that do not exist in the 3e documentation's five
  formats. `master` has therefore drifted beyond pristine 3e. Pin the
  jhauser.us 3e archive (or a named commit) and record its hash; do not
  clone-and-trust `master` as "3e".
  Source: https://raw.githubusercontent.com/ucb-bar/berkeley-softfloat-3/master/build/Linux-x86_64-GCC/Makefile,
  build-dir inventory via https://api.github.com/repos/ucb-bar/berkeley-softfloat-3/contents/build
  (lists `Linux-386-GCC`, `Linux-386-SSE2-GCC`, `Linux-ARM-VFPv2-GCC`,
  `Linux-RISCV64-GCC`, `Linux-x86_64-GCC`, `Win32-MinGW`, …).

### 1.2 Licence — may we copy code? vectors? link test-only?

- **READ** — Both packages carry the identical UC Regents text (BSD-3-Clause
  in substance). Verbatim conditions fetched from
  https://raw.githubusercontent.com/ucb-bar/berkeley-softfloat-3/master/COPYING.txt
  and https://raw.githubusercontent.com/ucb-bar/berkeley-testfloat-3/master/COPYING.txt
  ("License for Berkeley SoftFloat/TestFloat Release 3e … Copyright
  2011–2018 The Regents of the University of California"): redistribution and
  use in source and binary forms, **with or without modification**, are
  permitted provided (1) source redistributions retain copyright notice +
  conditions + disclaimer; (2) binary redistributions reproduce them in
  documentation/materials; (3) neither the University's name nor
  contributors' names may endorse/promote derived products without prior
  written permission. AS-IS, no warranty.
- **READ** — Therefore, as a licence matter: **copying code is allowed**
  (with notice retention), **linking `libsoftfloat.a` into a test harness is
  allowed** (it is TestFloat's designed use — "TestFloat works by comparing
  the behavior of the floating-point under test with that of the Berkeley
  SoftFloat software implementation", TestFloat page above), and a binary
  test harness that is *distributed* triggers only clause (2) notice-in-docs.
  Nothing in the licence distinguishes test-only from production use.
- **BELIEVED** — Generated vectors (`testfloat_gen` output lines: operands,
  expected result, expected flags, in hex) are machine-generated data from a
  BSD-3 program; no separate licence claim on output was found in the docs
  fetched. Redistributing vector files with attribution is the safe and
  conventional reading; regenerating them from a pinned seed avoids the
  question entirely and is cheaper than storing them (see 1.4).
- **READ** — Version caveat: "Unlike past versions, Release 3 and later have
  a U.C. Berkeley open-source license" (both product pages). Release 2c-era
  terms are a different, older text — irrelevant if the pin is 3e, a trap if
  anyone reaches for 2c for its no-64-bit-int property.
- Separation of concerns for the lead: the licence permits copy/link/read.
  Whether muse-softfloat's *own* code may contain copied Berkeley code is a
  project-integrity decision (clean-room posture in `ledger/lead.md` is about
  a different, forbidden codebase), not a licence constraint. S2 takes no
  position; SF-0 should state the project's rule explicitly.

### 1.3 What TestFloat covers

Formats — **READ** (TestFloat-general §1, SoftFloat interface §1): binary16
(`f16`), binary32 (`f32`), binary64 (`f64`), 80-bit double-extended
(`extF80`), binary128 (`f128`). No decimal formats; "TestFloat cannot test
decimal floating-point."

Operations — **READ** (SoftFloat interface §1/§8; TestFloat-general §6
contents: 6.1 conversions, 6.2 basic arithmetic, 6.3 FMA, 6.4 remainder,
6.5 round-to-integer, 6.6 comparisons): for each format — add, sub, mul,
div, sqrt; fused multiply-add (**all formats except extF80**); IEEE
remainder; round-to-integral-value; comparisons; conversions among all five
FP formats; conversions to/from 32- and 64-bit signed/unsigned integers;
signaling-NaN tests. Explicitly **not** covered: conversions to/from decimal
(the one 1985 requirement omitted). **BELIEVED** (mirror README snippet via
search, not fetched in full): most operations added by IEEE 754-2008 beyond
the 1985 core (e.g. the 2019 minimum/maximum family, augmented arithmetic)
are not in 3e — verify against 754-2019 clause list at SF-0 if the project
claims 2019 coverage.

Roundings — **READ** (`testfloat` doc): "`testfloat` will ordinarily test an
operation for **all five rounding modes** defined by the IEEE Floating-Point
Standard, one after the other, plus possibly a sixth mode, *round to odd*
(depending on compile options)"; ops unaffected by rounding are checked in
nearest/even only; extF80 also sweeps its three rounding-precision modes.
The five = roundTiesToEven, roundTiesToAway, towardZero, towardPositive,
towardNegative (754-2008 set); the sixth (round-to-odd/jamming) needs
`SOFTFLOAT_ROUND_ODD` compiled in (the fetched x86_64 Makefile above sets
it in `SOFTFLOAT_OPTS`).

Flags — **READ** (SoftFloat interface §§6–7 contents; `testfloat_gen` doc):
every generated case carries "**two results: first, a value … and, second,
the floating-point exception flags** raised by the operation" — the five IEEE
flags (invalid, division-by-zero/infinite, overflow, underflow, inexact).
**BELIEVED** (interface structure, §6.2 "Underflow Detection"): tininess
detection (before vs after rounding) is a specialization-time global
(`softfloat_detectTininess`), flags accumulate in a global the harness must
clear per case — standard SoftFloat-3 interface, verify in header at build.
TestFloat-general §8 (**READ**, contents) names the three allowed-variation
areas its comparisons tolerate: underflow tininess, NaN payloads,
float→integer conversion behaviour. A gate built on TestFloat inherits those
tolerances unless the harness tightens them.

Programs — **READ** (TestFloat-general §1, `testfloat_gen`/`testfloat`
docs): `testfloat` (all-in-one: generates operands, invokes the impl it was
compiled against — default build tests C `float`/`double` ops — compares vs
SoftFloat), `testsoftfloat` (tests SoftFloat against itself; the compile
sanity check), `timesoftfloat`, `testfloat_gen` (emits operand+expected+flags
vectors to stdout for one function per invocation), `testfloat_ver` (checks
vector files). For a software library like muse-softfloat the natural routes
are (a) retarget `testfloat`'s function-invocation layer to call the
project's functions, or (b) pipe `testfloat_gen` output into a project-owned
runner — (b) keeps Berkeley code out of the project's test binary entirely
at run time after generation.

### 1.4 Vector volume and generation model

- **READ** (`testfloat_gen` doc; `testfloat` doc): generation is
  pseudo-random and **seeded** (`-seed`, default 1); same binary + same args
  + same seed ⇒ identical sequence; `-level 1|2` (default 1; level 2 = "many
  more test cases … with better coverage"); `-n <num>` has a per-function
  per-level **minimum** that it can only raise, never lower; with no `-n`
  the minimum is generated. Output "can be large, so piping … may be the
  best choice to avoid using inordinate file space."
- **BELIEVED** — Exact per-function counts live in TestFloat's `genCases_*`
  source tables, which S2 did not fetch (docs fetched state the mechanism,
  not the numbers). Prior-knowledge order of magnitude: level 1 is
  ~10^5–10^6 cases per binary function/rounding, level 2 roughly an order
  more; a full level-2 sweep across formats×ops×roundings is a 10^8-case
  class run, i.e. minutes-to-hours in C and gigabytes if stored as text.
  **Do not gate on these numbers.** First build task: measure with
  `testfloat_gen -level 2 <fn> | wc -l` (redirect, don't pipe through
  `head` — AGENTS.md item 6 deadlock warning) and record the real table.
- **READ** — Declared weakness, verbatim in substance from the TestFloat
  page: TestFloat "performs relatively simple tests designed to check the
  fundamental soundness"; it "is not especially good at testing difficult
  rounding cases for divisions and square roots" and "makes no attempt to
  find bugs specific to SRT division and the like". Generation is
  distribution-biased randoms (special values, boundary exponents), not
  midpoint-targeted search. This is the gap §4 below fills.

### 1.5 Realistic build route on this Windows host

Prerequisites — **MEASURED** (`scratch/S2/probe.log`): Git Bash present
(`C:\Program Files\Git\bin\bash.exe`, bash 5.2.26 under MINGW64_NT-10.0);
GNU Make 4.4.1 at `/c/msys64/usr/bin/make`; MSYS2 gcc 16.1.0 installed for
both `i686-w64-mingw32` and `x86_64-w64-mingw32` targets
(`pacman -Q`: `mingw-w64-i686-gcc 16.1.0-5`, `mingw-w64-x86_64-gcc
16.1.0-5`); CMake on PATH (not needed for Berkeley). Route — **READ**
Makefile + **BELIEVED** assembly of steps (S2 did not perform the build;
read-only brief):

1. Fetch SoftFloat Release 3e and TestFloat Release 3e archives from
   jhauser.us (links in §1.1); record SHA-256 in the project record. Avoid
   GitHub `master` (drift, §1.1).
2. In Git Bash with `TMPDIR` (POSIX) + `TMP`/`TEMP` (Windows form) pointed
   into the workspace scratch (lead's ledger entry; AGENTS.md item 2), and
   `PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"` exported **first**
   (measured necessity, §3.2):
   `cd SoftFloat-3e/build/Linux-x86_64-GCC && make` — the Makefile (fetched)
   is POSIX-shell (`rm -f`, `ar crs`), `SPECIALIZE_TYPE=8086-SSE`,
   `gcc -c -Werror-implicit-function-declaration -DSOFTFLOAT_FAST_INT64
   -DSOFTFLOAT_ROUND_ODD -DINLINE_LEVEL=5 … -O2`, producing `softfloat.a`.
   Despite the "Linux" name nothing in the fetched Makefile head is
   Linux-specific; it is a gcc+ar build. (`build/Win32-MinGW` also exists in
   the repo inventory if a 32-bit build were ever wanted — it is not, §3.)
3. Build TestFloat's matching `build/<target>` with its Makefile pointed at
   the SoftFloat build (include dir + `softfloat.a`). **BELIEVED**: TestFloat
   3e makefiles take the SoftFloat location via make variables/edit of the
   platform Makefile — S2 fetched TestFloat's *source* doc ("SoftFloat is
   not included with the TestFloat sources. It can be obtained from…",
   TestFloat-source §5, READ) but not its Makefile text; confirm variable
   names at first build, don't transcribe from memory.
4. Sanity-gate the oracle itself before trusting it: run `testsoftfloat`
   (SoftFloat vs itself through TestFloat's comparison machinery) at level 1
   for the project's formats; a mis-specialized build (wrong tininess/NaN
   specialization for the intended semantics) shows up as systematic
   mismatches against the host FPU in step 5, not here.
5. Cross-check Berkeley vs host SSE2 on binary32/64 basic ops (§3) and vs
   MPFR on sampled div/sqrt/FMA (§2) — three-way disagreement procedure is
   an SF-0 design item, but the build route must expect NaN-payload and
   tininess-policy diffs (§1.3 tolerances) rather than treat them as bugs.
6. **BELIEVED** risk, small: 2018 C89-ish code under gcc 16.1 (defaults to a
   modern C std) — only `-Werror-implicit-function-declaration` is an error
   class in the fetched flags; expect warnings, not failures. If gcc 16
   balks, `-std=gnu89`-style pinning in `COMPILE_C` is the first lever.
   Unmeasured until someone builds it.

For the RP2040 target side (**MEASURED**: `arm-none-eabi-gcc 14.2.1`
present, probe2 log): SoftFloat's `Linux-ARM-VFPv2-GCC` specialization is
the wrong model for Cortex-M0+ (no VFP); a target build would use a generic
specialization chosen to match the project's *specified* semantics, not any
hardware. **BELIEVED**: host-side oracle use (x86_64) is the realistic
primary route; on-board runs consume pre-generated vectors.

---

## 2. MPFR (and mpmath) as foreign oracle

### 2.1 Correct rounding claim

- **READ** — GNU MPFR manual (4.2.2, https://www.mpfr.org/mpfr-current/mpfr.html;
  §1 text via search extract of the manual): "The value stored in the
  destination variable is **correctly rounded**, i.e., MPFR behaves as if it
  computed the result with an infinite precision, then rounded it to the
  precision of this variable. The input variables are regarded as exact."
  Precision is settable exactly per variable; results do not depend on
  machine word size or hardware rounding mode. Rounding modes (**READ**,
  manual §4.4 via search extract): `MPFR_RNDN` (ties-to-even), `MPFR_RNDZ`,
  `MPFR_RNDU`, `MPFR_RNDD`, `MPFR_RNDA` (away) — the five IEEE modes.
- Foreignness: MPFR (INRIA, built on GMP integer arithmetic, entirely
  different codebase/algorithms from Hauser's SoftFloat) is a genuinely
  independent oracle for +, −, ×, ÷, sqrt, FMA and conversions — a shared
  bug would require a shared misconception, not shared code. That is the
  property SF-0 wants from a "foreign oracle"; the host FPU (§3) is the
  second foreigner for the ops it implements in hardware.
- **READ — the emulation contract, do not skip**: MPFR's native model has a
  much wider exponent range and **no subnormals**; binary64 semantics are
  reproduced only by the documented recipe (manual, "MPFR and the IEEE 754
  Standard" / example extracts via search): 53-bit precision,
  `mpfr_set_emin(-1073)`, `mpfr_set_emax(1024)`, and
  `mpfr_subnormalize(result, ternary, rnd)` applied after **each**
  operation. An oracle harness that sets precision 53 and stops there will
  silently produce non-IEEE results exactly in the subnormal/overflow
  neighbourhoods the gate most cares about. (binary32 analogously: 24 bits,
  emin −148, emax 128 — **BELIEVED** arithmetic from the binary64 recipe:
  emin = 1 − emax − (p−1); verify in the manual's table at implementation.)
- **READ** — Licence: MPFR 4.2.x is **LGPLv3 or later** ("This version of
  MPFR is released under the GNU Lesser General Public License, version 3 or
  any later version", manual extracts). Test-only linking inside the project
  is unproblematic; *distributing* a statically linked oracle binary carries
  LGPL relink/source obligations — keep the oracle test-only/internal or
  link the DLL. It is not a copy-source candidate for the library itself.

### 2.2 Windows availability on this host — MEASURED

From `scratch/S2/probe.log` (read-only `pacman -Q` / `pacman -Ss`, no `-Sy`):

- Installed: `mingw-w64-x86_64-mpfr 4.2.2-3`, `mingw-w64-i686-mpfr 4.2.2-3`,
  `mpfr 4.2.2-1` (msys), plus matching GMP 6.3.0-2 / MPC 1.4.1-1.
- Sync DB also offers `mingw-w64-ucrt-x86_64-mpfr`, `…-clang-x86_64-mpfr`,
  `…-clang-aarch64-mpfr` (all 4.2.2-3) and `mpfr-devel` (msys) — not needed.
- Files present: `C:\msys64\mingw64\include\mpfr.h`,
  `C:\msys64\mingw64\lib\libmpfr.a` + `libmpfr.dll.a` (and `libgmp.*`).
- Link+run smoke test (`scratch/S2/probe4.log`, x86_64 gcc 16.1 after the
  PATH fix): builds clean, prints `mpfr version=4.2.2`. So the MPFR oracle
  route is: zero installs, `#include <mpfr.h>`, `-lmpfr -lgmp`, with
  `/c/msys64/mingw64/bin` first in PATH (also puts `libmpfr-*.dll` /
  `libgmp-*.dll` in run-time reach if dynamically linked).

### 2.3 mpmath in `.venv` — precision model and its limits

**MEASURED** (`.venv\Scripts\python.exe`, Python 3.12.15, mpmath 1.4.1;
`scratch/S2/mpmath_probe.py` + follow-up one-liners):

- Default context: `mp.prec = 53` bits, `mp.dps = 15`, rounding `'n'`.
  Rounding is selected by single-letter codes — `'n','f','c','d','u'` all
  accepted; the word `'floor'` is rejected ("invalid rounding mode").
- At default prec 53, `a*b − 1` for the §3 probe operands returns `0.0`
  while at prec 300 the exact product differs from 1 by ~1.11e-16 —
  i.e. **default-precision mpmath cannot decide binary64 rounding of a
  product at all** (needs ≥106 exact bits before the final rounding; add/
  mul of binary64 operands are exact at 2p bits, div/sqrt need guard bits
  plus a sticky/ternary argument, conventionally p+64 or more with a
  re-check at higher precision when the result lands near a midpoint).
- Exponent range is effectively unbounded: `mpf(2)**2000` is finite.
  **There is no binary64 overflow-to-inf, no emin, and no gradual
  underflow in mpmath's native model** — precision is a fixed significand
  width regardless of exponent, so a result that should be a 12-bit-
  significand subnormal is computed at full prec unless the caller emulates
  subnormal rounding by hand. No IEEE exception flags exist to compare.
- The reliable binary64 final-rounding step in Python is not mpmath at all:
  CPython's `float()` conversion is correctly rounded RNE including
  subnormals and ties — measured: `float(2**-1075) = 0x0.0p+0` (tie to
  even), `float(2**-1074) = 0x0.0000000000001p-1022`,
  `float.fromhex('0x1.00000000000008p+0') = 1.0` (exact midpoint ties to
  even). But `float()` only implements **RNE**: directed-rounding and
  ties-to-away decisions cannot be obtained from it; they need either
  mpmath at prec 53 with the right rounding letter **plus** hand-rolled
  emin/emax/subnormal emulation, or exact rational arithmetic
  (`float.as_integer_ratio()` / `fractions.Fraction`) deciding the rounding
  from the exact remainder — S2's **BELIEVED** recommendation for a Python
  oracle is the exact-rational route for +/× and high-precision
  mpmath-with-midpoint-escalation for ÷/sqrt/FMA, because both make the
  rounding decision auditable.
- Construction trap, measured in effect: `mpf(1.0000000000000002)` first
  rounds the literal to binary64 in CPython, then widens exactly — fine if
  binary64 operands are intended (they usually are), silently wrong if a
  decimal operand was meant. Build operands from hex (`float.fromhex` /
  bit patterns) or strings under `workprec`, never from bare literals.
- **BELIEVED**: mpmath does not claim correct rounding for transcendental
  functions (it aims for high accuracy with heuristic guard precision);
  irrelevant while transcendentals are out of scope, decisive if they ever
  enter: MPFR (which does claim it) is then the Python-reachable oracle
  only via a C harness or a binding, not via mpmath.
- **BELIEVED** (not benchmarked): pure-Python mpmath throughput is orders
  below the C oracles — fit for thousands of spot/adversarial cases and for
  generating directed hard cases, not for 10^7-case gates.

---

## 3. Host x86-64 FPU (SSE2) as oracle for binary32/64 basic ops

### 3.1 The machine — MEASURED

`scratch/S2/probe*.log`: host `DESKTOP-T33SK86`, CPU `Intel64 Family 6
Model 151 Stepping 2, GenuineIntel`, `PROCESSOR_ARCHITECTURE=AMD64`;
`__builtin_cpu_supports`: sse2 / avx / avx2 / fma all supported (nonzero).
Toolchain: MSYS2 gcc 16.1.0 in **two** flavours (see 3.2 — the crux),
GNU Make 4.4.1, arm-none-eabi-gcc 14.2.1. Git Bash is the working POSIX
shell (AGENTS.md item 1; WSL is access-denied to the sandbox user).

### 3.2 The measured trap: "gcc" here is 32-bit x87 by default

- **MEASURED** (`probe.log`): with the inherited Git Bash PATH, `which gcc`
  = `/c/msys64/mingw32/bin/gcc`, `gcc -dumpmachine` = `i686-w64-mingw32`,
  and the predefined macros include `__FLT_EVAL_METHOD__ 2` and `__SSE2__ 1`
  — i.e. a 32-bit compiler whose default evaluation keeps intermediates in
  the 80-bit x87 stack (**excess precision / double rounding**),
  `sizeof(long double)=12`. Anything built this way is *not* a binary32/64
  oracle, however IEEE the silicon is: a `double` expression may compare
  unequal to itself after a spill, and overflow/underflow instants move.
- **MEASURED** (`probe3.log`): invoking `/c/msys64/mingw64/bin/gcc.exe` by
  absolute path while `mingw32/bin` precedes it in PATH: `--version` works,
  but `-dM -E` and every real compile **exit 1 with empty stdout and empty
  stderr** (no `.exe` produced). **BELIEVED** mechanism: `cc1` loads the
  wrong-architecture support DLLs found first via PATH (mingw32), and the
  driver reports nothing. Not proven — but operationally irrelevant,
  because the fix is measured:
- **MEASURED** (`probe4.log`): `export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"`
  ⇒ `gcc` resolves to the x86_64 compiler, `-dumpmachine` =
  `x86_64-w64-mingw32`, macros `__FLT_EVAL_METHOD__ 0`, `__x86_64__ 1`,
  `__SSE2__ 1`, `sizeof(long double)=16`; compiles, MPFR link, and runs all
  succeed. **Every oracle build script must set this PATH itself and assert
  `-dumpmachine` + `FLT_EVAL_METHOD==0` at startup** — the failure mode is
  silent and the wrong-default mode is subtly non-IEEE, both worse than a
  loud error.
- Note: even on the x86_64 mingw path, `long double` is the 80-bit x87
  format (16-byte storage) — **MEASURED** sizeof above. It is not
  binary128, and its libm is a mingw/msvcrt mixture; keep `long double` out
  of the oracle entirely.

### 3.3 Where SSE2 is exactly IEEE (with the x86_64 compiler path)

**READ** (Intel SDM / AMD64 manual extracts via search: MXCSR bits 14–13
are the rounding-control field with the four IEEE modes; SSE exception set
I/D/Z/O/U/P) + architectural facts, tagged as a block **BELIEVED** where S2
did not re-derive them from the SDM this run:

- Scalar `addss/addsd, sub*, mul*, div*, sqrt*`: single operation,
  correctly rounded to the MXCSR rounding mode, gradual underflow with
  subnormal results (FTZ/DAZ clear), subnormal operands honoured. These
  five are a legitimate bit-exact oracle for binary32/64 + − × ÷ √ in all
  four directed/RNE modes — but not ties-to-away (no x86 rounding mode for
  it) and not round-to-odd.
- Conversions `cvtss2sd/cvtsd2ss`, float↔int (with the §3.4 caveat),
  comparisons (`comiss/ucomiss` family) with correct quiet/signaling NaN
  flag behaviour; `fma` via FMA3 (`vfmadd*`) is a single-rounding IEEE
  fused operation **when actually emitted** (3.4c).
- Flags: MXCSR accumulates the five IEEE status flags plus a denormal-
  operand flag (not an IEEE flag — mask it out when comparing against
  SoftFloat/MPFR). **BELIEVED**: x86 underflow tininess is detected
  *after* rounding; SoftFloat's `8086-SSE` specialization exists precisely
  to match this class of choice — whichever way SF-0 specifies tininess,
  the specialization and the expectation must be chosen together, and
  TestFloat's §8 tolerance will otherwise hide the difference.

### 3.4 Where it is not / pitfalls (each with control)

a. **The compiler, not the silicon, is the interface.** Constant folding
   (GCC folds with MPFR — correctly rounded, benign), reassociation under
   fast-math (never enable), spill/reload on the x87 path (3.2). Control:
   oracle runner reads operands as runtime bit patterns (`memcpy` from
   `uint32_t/uint64_t`), one operation per statement, results stored to
   memory before inspection; no `-ffast-math` anywhere in the build
   (measured present in `gcc --help`; it also links crtfastmath-style
   FTZ/DAZ setting on some targets — **BELIEVED** for mingw).
b. **FTZ/DAZ are modes, and someone may have set them.** **READ** (Intel
   extracts: DAZ is MXCSR bit 6, support discoverable via FXSAVE
   MXCSR_MASK). Control: the harness must `_mm_setcsr` explicitly
   (RC as intended, FTZ=DAZ=0, flags cleared) before each case batch and
   verify, rather than trusting process defaults inherited through
   whichever CRT ran first.
c. **FMA contraction is a flag away from changing answers — MEASURED**
   (`probe4.log`): baseline x86-64 (no `-march`) defines no `__FMA__` /
   `__FP_FAST_FMA*`; `a*b+c` on the probe operands yields `0.0`.
   `-march=native` defines `__FMA__`/`__FP_FAST_FMA*`; with
   `-ffp-contract=fast` the same expression yields `-4.93e-32` (fused,
   single rounding), with `-ffp-contract=off` back to `0.0`. `gcc --help`
   (**MEASURED**) lists `-ffp-contract=[off|on|fast]` and
   `-fexcess-precision=[fast|standard|16]`. Control: oracle code pins
   `-ffp-contract=off` explicitly for non-FMA ops, calls
   `fma()/fmaf()` (or intrinsics) deliberately for FMA, and never lets
   `-march=native` sneak contraction into mul/add test paths.
   **BELIEVED**: GCC's default is `fast` in GNU dialect modes; do not
   rely on remembering — pin it.
d. **x87 excess precision on any 32-bit or `long double` path.**
   **READ** (musl/GCC sources via search): with `FLT_EVAL_METHOD=2`, GCC's
   default `-fexcess-precision=fast` keeps intermediates at 80-bit;
   `-fexcess-precision=standard` (implied by strict `-std=c99` dialects)
   forces rounding back on assignment/cast — at real cost and only where
   the standard demands. On this host the correct control is stronger:
   don't be on that path (§3.2); if a 32-bit build is ever forced,
   `-mfpmath=sse -msse2 -fexcess-precision=standard` is the minimum.
e. **No ties-to-away, no round-to-odd, no 754-2019 min/max.** `minsd/
   maxsd` return the second operand on unordered and are not IEEE
   `minimum/maximum` nor `minNum/maxNum` semantics (**BELIEVED**,
   standard x86 behaviour). Missing modes/ops simply aren't coverable by
   the FPU oracle — Berkeley/MPFR only.
f. **NaN payloads and float→int overflow are implementation-defined.**
   **BELIEVED** (classic x86): invalid operations deliver the QNaN
   "indefinite" pattern; payload propagation selects an operand payload;
   `cvttsd2si` overflow delivers `0x8000000000000000`. TestFloat-general
   §8 (**READ**) lists exactly these as allowed variations. Control:
   compare NaNs by class (signalling/quiet — and sign only if SF-0 says
   so), not by payload bits, whichever oracle pair is compared.
g. **Transcendentals: excluded, correctly.** SSE2 has none; the x87
   `fsin/f2xm1/fyl2x` family is not correctly rounded (argument-reduction
   error grows without bound for large arguments — **BELIEVED**, textbook
   result), and mingw libm implementations carry no <0.5-ulp guarantee.
   The brief's exclusion is endorsed; if transcendentals ever enter
   scope, MPFR/CORE-MATH is the oracle, never the host libm.
h. **Divide/sqrt are right; `rcpps/rsqrtps` are not instructions an
   oracle may touch** (approximate by design — **BELIEVED**/architectural).
   GCC won't emit them without fast-math/reciprocal flags; one more reason
   those flags stay off.

Summary for SF-0: host SSE2 is a **bit-exact foreign oracle for binary32/64
+, −, ×, ÷, √, FMA (explicit), conversions and comparisons in RNE +
3 directed modes**, reached exclusively through the x86_64 compiler path
with pinned `-ffp-contract=off`, explicit MXCSR state, and NaN-payload
masking. Everything else (ties-away, round-odd, binary16/128, extF80-as-
format, transcendentals, decimal) has no host oracle.

---

## 4. Published hard cases / suites beyond TestFloat worth gating on

Framing (**READ**, TestFloat page): TestFloat declares itself weak on
"difficult rounding cases for divisions and square roots" and SRT-class
bugs. The named supplements, in S2's recommended gate order:

1. **IBM Research Haifa FPgen test suites for IEEE 754R.**
   Provenance — **READ**: M. Aharoni, S. Asaf, L. Fournier, A. Koifman,
   R. Nagel (IBM Haifa), "FPgen — a test generation framework for datapath
   floating-point verification", HLDVT 2003; suite document "Floating-Point
   Test-Suite for IEEE 754R" (IBM Labs in Haifa, FPgen Team, v1.02 Jan
   2008) with per-feature test files whose vectors "were generated by
   means of IBM FPgen"; previously hosted at IBM Haifa's verification site,
   mirrored at https://github.com/sergev/ieee754-test-suite (with
   `ieee-test-suite-v2.pdf`). Model-based operand-class coverage
   complements TestFloat's biased randoms and includes decimal (skip that
   part). Gate value: high for binary basic ops/conversions. Check the
   mirror's licence/terms before vendoring vectors — S2 found no licence
   text in what was fetched (**BELIEVED** gap, verify before use).
2. **Exhaustive sweeps where the format allows** (a method, named here
   because it out-gates any published list for small formats):
   binary16 all unary + all-pairs binary ops (2^32 pairs — feasible in C,
   **BELIEVED** hours-class single-threaded, much less for unary);
   binary32 unary ops exhaustive (√, conversions, round-to-int: 2^32
   each); binary32 div/sqrt hard cases sink into this net completely.
   For binary64, exhaustive is impossible; substitute (4).
3. **Kahan's Paranoia** (W. Kahan; original in BASIC, canonical versions on
   Netlib — **READ** via Burkardt/Netlib descriptions). Not a vector gate:
   a properties diagnostic (radix, guard digit, sticky, rounding sanity).
   Gate value: run it **against the host oracle path itself** (and later
   against the project library through C operators) as a smoke verdict
   that the §3.2 trap hasn't bitten — Paranoia classically sniffs out
   excess-precision and missing sticky behaviour.
4. **Directed worst-case generation for binary64 ÷/√/FMA** using the MPFR
   oracle (§2) to manufacture near-midpoint cases TestFloat's randoms
   rarely hit: operands whose exact quotient/root lands within a few ulp
   of a rounding boundary (searchable by construction with rationals),
   FMA cancellation triples a·b ≈ −c (the Boldo–Muller regime —
   **READ**: S. Boldo & J.-M. Muller showed the exact error of an FMA is
   representable and gave the ErrFma algorithms; Muller/Boldo FMA work is
   the design source for adversarial FMA vectors). Gate value: this is
   the direct answer to TestFloat's declared blind spot.
5. **UCBTEST** (Netlib `fp/ucbtest.tgz` — **READ** via Oracle Numerical
   Computation Guide summary: "versions of Paranoia, Z. Alex Liu's
   Berkeley Elementary Function test program, the IEEE test vectors, and
   programs based on number-theoretic methods developed by Prof. W. Kahan
   that generate hard test cases for correctly rounded [arithmetic]").
   Gate value: mostly elementary functions — park unless/until
   transcendentals enter scope; the Kahan hard-case generators for
   div/sqrt-style correct rounding may merit a look for (4).
6. **Lefèvre/Muller worst cases + CORE-MATH `.wc` files.**
   Provenance — **READ**: V. Lefèvre, J.-M. Muller et al. computed the
   hardest-to-round cases (Table Maker's Dilemma) for binary64 elementary
   functions (Handbook of Floating-Point Arithmetic, Muller et al.;
   CORE-MATH project, P. Zimmermann/INRIA, distributes `foo.wc` worst-case
   files per function, e.g. `src/binary64/exp/exp.wc` on its GitLab).
   Gate value: **only** if elementary functions are ever claimed correctly
   rounded; zero for the basic-op library. Listed so SF-0 can refuse them
   by name with provenance rather than by omission.
7. **ELEFUNT** (W. J. Cody & W. Waite, from *Software Manual for the
   Elementary Functions*) and **Nelson H. F. Beebe's IEEE 754 test
   software** — named, **BELIEVED** provenance (Beebe item via a citing
   paper's reference list in search results, not fetched). Historical
   elementary-function suites; not recommended over (5)/(6) for any
   near-term gate.

Also worth a line: MPFR's and GCC's own test suites are regression suites
for *those* implementations, not portable vector sources for this project
(**BELIEVED**); Oracle-vs-oracle cross-checks (§1.5 step 5) capture their
value without importing them.

---

## 5. Third-party soft-float code: READ vs COPY, licence each

One line each, per brief ("copy" = copying source into muse-softfloat's
own tree; project licence note follows):

- **Berkeley SoftFloat 3e — BSD-3-Clause (UC Regents, §1.2).** READ ✔,
  COPY ✔ legally (retain notice/conditions/disclaimer; no UC-name
  endorsement). Any restriction is project policy, not licence.
- **LLVM compiler-rt builtins (`__adddf3` etc.) — Apache-2.0 WITH
  LLVM-exception.** **READ**: current file headers carry
  `SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception` (e.g.
  `adddf3.c` in FreeBSD's vendor import, via search). Caution: the
  compiler-rt project web page still says "dual licensed under the MIT
  license and the UIUC License" (**READ** via search result) — that page
  predates LLVM's relicensing; **trust the per-file headers of the actual
  checkout**. READ ✔, COPY ✔ legally (Apache-2.0 conditions + NOTICE if
  present; the exception removes attribution-through-binary friction for
  runtime embedding). **BELIEVED**: the generic builtins FP code is
  largely original LLVM work in C — verify per-file headers before any
  copy, since compiler-rt aggregates multiple origins.
- **libgcc soft-fp (GCC `libgcc/config/soft-fp/`, shared with glibc) —
  GPLv3-or-later with GCC Runtime Library Exception 3.1** (some soft-fp
  headers historically LGPL-2.1+ with exception, per GCC list discussion
  — **READ** via search extracts; `COPYING.RUNTIME` governs). The Runtime
  Exception permits *linking the compiled runtime* into otherwise
  non-GPL executables when produced by GCC's compilation process; it does
  **not** relicense copied *source*. READ ✔, COPY ✘ for a non-GPL
  library (copying makes the copied code GPL). This also describes the
  `__adddf3`-style helpers inside the arm-none-eabi libgcc already on this
  host: fine as the toolchain's runtime, not as source to lift.

Project-side unknown S2 must flag: `muse-softfloat/` top level
(**MEASURED** listing) contains no `LICENSE` file yet (README, AGENTS,
docs/, dotfiles only), so the "COPY ✔/✘" verdicts above are stated against
licences in the abstract. The day the project picks its own licence, §5's
Berkeley/compiler-rt rows should be re-checked for compatibility (both are
compatible with every common choice — **BELIEVED**), and the soft-fp row
flips only under a GPL-compatible project licence.

---

## Appendix A — What was executed (independent reruns possible)

All under `scratch/S2/`, script-file route via Git Bash per lead's rule,
`TMPDIR=scratch/S2/tmp` (+ Windows forms): `probe.sh/.log` (toolchain,
pacman read-only queries, CPU, default-gcc macros, FMA smoke),
`probe2.sh/.log` (x86_64 attempt — the silent-failure observation),
`probe3.sh/.log` (failure isolated: exit 1, empty output),
`probe4.sh/.log` (PATH fix; FLT_EVAL_METHOD=0; MPFR 4.2.2 link+run; FMA
contract on/off/native three-way), `mpmath_probe.py` (mpmath 1.4.1 model
limits, CPython float() tie/subnormal behaviour). No packages installed,
no third-party source downloaded, `pacman` used query-only.

## Anything this brief got wrong

1. **"gcc via Git Bash" is not the oracle the brief imagines.** The brief's
   §1 build route and §3 "FMA contraction control flags for MSYS gcc here"
   presume one host gcc; this host has two MSYS2 gcc 16.1 installs and the
   Git Bash default is the **i686 x87** one (MEASURED, §3.2). The "lead.md"
   line "host gcc 16.1" inherits the ambiguity. Correction recorded for
   every parcel: assert `x86_64-w64-mingw32` + `FLT_EVAL_METHOD 0`, pin
   PATH, or the FPU-oracle section of any future report is void.
2. **Invoking the 64-bit compiler by absolute path does not work around
   PATH** — it fails silently (MEASURED). Any parcel brief that says "use
   `C:\msys64\mingw64\bin\gcc.exe`" without the PATH export will produce
   empty logs and false conclusions.
3. **MPFR availability is not an open question** the brief hedges ("measured
   if you can check pacman db"): it is installed now (4.2.2-3, x86_64 +
   headers + libs, link-tested). The SF-0 step "obtain a foreign oracle"
   is already done; budget accordingly.
4. **The brief's mpmath framing ("mpmath already in .venv as Python
   oracle") overstates it.** Measured: no subnormals/emin-emax/flags
   natively, precision-53 default decides nothing, and the only trustworthy
   binary64 rounding in Python (CPython `float()`) covers RNE alone.
   mpmath is an ingredient for an oracle (with exact-rational or
   hand-emulated rounding), not an oracle out of the box. Directed
   roundings via Python need the engineered route in §2.3.
5. **"Current release" is 2018.** Both Berkeley packages are frozen at 3e
   (2018-01-20); and the obvious GitHub mirror's `master` is *newer than
   3e* in content (bfloat16). A brief that says "download the current
   Berkeley SoftFloat" is ambiguous between the 3e archive and a moving
   mirror; §1.5's pin-and-hash step is the correction.
6. **TestFloat coverage is narrower than a casual reading of the brief's
   question implies** — no decimal conversions, self-declared weakness on
   hard div/sqrt rounding, and (BELIEVED) most post-1985 IEEE operations
   absent. The brief was right to ask §4; SF-0 must not let "passes
   TestFloat level 2" be phrased as "IEEE 754-2019 conformant".
7. **The `long double` trap is worse than "x87 pitfalls" suggests**: on
   the *x86_64 mingw* path `long double` remains the 80-bit format
   (MEASURED sizeof 16), so a harness that reaches for `long double` as
   "extra precision to check double" imports x87 semantics and a
   mixed-provenance libm even after the PATH fix.
8. Minor/mechanical: the brief says "TMPDIR scratch/S2/tmp" for ledger.sh;
   per `ledger/lead.md` and AGENTS.md item 2 the Windows-form `TMP`/`TEMP`
   must accompany it for native tools in the same script — followed in
   S2's scripts. Also "append ledger entry ledger/S2.md via kit ledger.sh"
   resolves correctly only by passing author `S2` (the tool appends to
   `<author>.md`); stated here so the next surveyor doesn't pass a path.
9. Nothing in the brief asked S2 to consider that `muse-softfloat/` has
   **no project licence yet** (MEASURED), which makes its §5 question
   ("could be READ vs COPIED") answerable only in the abstract. Picking
   the project licence is a lead/owner decision that should land before
   any parcel is briefed to copy anything, however permissive.

— End of S2 report. Ledger entry: `ledger/S2.md` (via
`softfloat-bootstrap-kit/tools/ledger.sh append`, script-file route).
