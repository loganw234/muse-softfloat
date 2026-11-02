# study-w6sanitize: ASan/UBSan over the host runners - feasibility

Base: `muse-softfloat/` at `50aac59f6035d56c37340ff07c59252cfd22d5d4`,
read-only. All work in a copied tree (`git archive HEAD`, archive
sha256 `e4f08ac1d31adb3a8a64acafe7f03c97d94eb7559b4abbf3aac9271929b8c65d`,
817 files) under `scratch/study-w6sanitize/tree/`. Scripts in
`scripts/`, raw logs in `logs/` (cited by name below). Ran 2026-10-30
on DESKTOP-T33SK86, Git Bash, `MSF_PYTHON` = workspace `.venv`
(Python 3.12.15). Nothing with `cft` in its name was opened,
searched, or listed; the one WSL distro besides `docker-desktop`
is off-limits under that rule and was not touched.

## Headline

1. **No compiler on this host can link
   `-fsanitize=address,undefined` today.** The gate compiler
   (MSYS2 mingw64 gcc 16.1.0, `x86_64-w64-mingw32`) accepts the
   flags but the runtime libraries do not exist in the install:
   every canary fails at link with `cannot find -lasan` /
   `cannot find -lubsan` (same for the i686 gcc). No clang is
   installed anywhere (no clang64/ucrt64/LLVM).
2. **Two complementary half-solutions run today with zero
   installs**, and both were run over the full committed vector
   set with **zero findings**:
   - gate gcc + `-fsanitize=undefined
     -fsanitize-undefined-trap-on-error -fno-sanitize-recover=all`
     (trap-on-error UBSan: full `undefined` check group, no
     libubsan needed, no diagnostics - a violation is an illegal
     instruction). Clean over unit + 411,213 committed cases +
     1,117,504 generated standard-extra cases + the 5,505,024-case
     aug pool harness.
   - MSVC cl 19.51 (`/fsanitize=address`): real AddressSanitizer
     with source-line reports. Clean over unit + 411,213 +
     1,117,504 cases (aug harness does not build under MSVC -
     `__int128`, see Sec. 3).
3. Neither half sees what the other sees (proven by canaries,
   Sec. 1): trap-UBSan misses object-size-unknown memory errors
   and use-after-free; MSVC ASan misses all UB. The full
   ASan+UBSan-with-diagnostics combo needs an install on this
   host (pacman clang64, Sec. 1.3) or Linux CI (parcel-w6ci).

## 1. Probe 1: which compilers support sanitizers end-to-end

Canaries (`canary/*.c`): `clean` (must exit 0), `heap` (write 56
bytes past an 8-byte `malloc`, index from argv), `ub`
(`volatile int INT_MAX + argc`, signed overflow), `ub_shift`
(`1u << 40`), `heap_dyn` (malloc size from argv), `heap_far`
(overflow through a `noinline` helper taking a bare `char*`).
Every cell below is compile **and** run, with exit codes from two
routes (Python `subprocess` true Windows code + bash status;
an early script using MSYS `timeout` masked trap exits and was
superseded - Sec. 5). Logs: `01_inventory.log`,
`02_canaries.log`, `04_trap_verify.log`, `05_msvc_and_dyn.log`,
`06_msvc_retry.log` (`03_fallbacks.log` was corrupted by the
host offset-0 append bug and is superseded by 04-06; do not cite).

### 1.1 Matrix

Compiler versions, verbatim first lines:

- `/c/msys64/mingw64/bin/gcc`: `gcc.exe (Rev5, Built by MSYS2
  project) 16.1.0`, dumpmachine `x86_64-w64-mingw32` (the gate
  compiler; `cc` and `x86_64-w64-mingw32-gcc` are the same).
- `/c/msys64/mingw32/bin/gcc`: same 16.1.0, `i686-w64-mingw32`
  (gate-refused architecture anyway).
- MSVC via `vswhere`: `C:\Program Files\Microsoft Visual
  Studio\18\Community`, tools `14.51.36231`, `Microsoft (R) C/C++
  Optimizing Compiler Version 19.51.36248 for x64` (also a VS2019
  BuildTools install, unprobed).
- `arm-none-eabi-gcc` 14.2.1: target compiler, cannot run host
  binaries; out of scope for host runners.
- clang / clang-cl / cl-on-PATH / zig / tcc: absent.
  Miniconda `Library/mingw-w64/bin/gcc`: absent.

| route | `-fsanitize=address` | `-fsanitize=undefined` | both |
|---|---|---|---|
| mingw64 gcc 16.1.0 | link FAIL `-lasan` | link FAIL `-lubsan` | link FAIL |
| mingw32 gcc 16.1.0 | link FAIL `-lasan` | link FAIL `-lubsan` | link FAIL |
| mingw64 gcc + trap-on-error | n/a | **WORKS** (below) | n/a |
| MSVC cl 19.51 `/fsanitize=address` | **WORKS** (below) | no such feature | n/a |

Link failure, verbatim (all 12 mingw64 sanitize cells identical
in kind): `ld.exe: cannot find -lasan: No such file or directory`
and `cannot find -lubsan: No such file or directory`.
`-print-file-name=libasan.a` etc. return the bare name (not
found); no `libasan*`/`libubsan*` file exists under the mingw64
or mingw32 lib/bin dirs checked. `-fsanitize-minimal-runtime`
is not a gcc option (`unrecognized command-line option`).

Unsanitized controls behaved as expected (proves the canaries
are live): `heap` printed `HEAP-WROTE idx=64` exit 0, `ub`
printed `UB-RESULT -2147483648` exit 0.

### 1.2 The two working halves, canary by canary

**Trap-UBSan** (`gcc -O1 -g -fsanitize=undefined
-fsanitize-undefined-trap-on-error -fno-sanitize-recover=all`):

- `clean`: exit 0, `CLEAN-OK 1 x argv`.
- `ub`: killed, Windows RC 3221225501 (`0xC000001D`
  STATUS_ILLEGAL_INSTRUCTION, the `ud2` from
  `__builtin_trap`); bash reports exit 132 + `Illegal
  instruction`. Caught.
- `ub_shift 40`: same RC. Caught.
- `heap 64` (constant malloc size): same RC - caught by the
  `object-size` member of the `undefined` group.
- `heap_dyn 8 64` (runtime malloc size): same RC - gcc 16
  tracks the dynamic object size through `malloc`.
- `heap_far 8 64` (size lost across a function call): **NOT
  caught** - exit 0, `HEAPFAR-WROTE n=8 idx=64`. This is the
  boundary: trap-UBSan catches UB plus out-of-bounds accesses
  whose object size is known at the access site. It has no
  redzones, no use-after-free detection, no leak detection, and
  prints nothing on failure (localize by bisect/per-file rerun
  or a debugger).

**MSVC ASan** (`cl /std:c11 /Od /Zi /fsanitize=address /MD`,
run inside a vcvars64 session so the ASan runtime DLL resolves):

- `clean`: exit 0.
- `heap 64`: exit 1 with full report, verbatim summary:
  `SUMMARY: AddressSanitizer: heap-buffer-overflow ...\canary\heap.c:9 in main`
  (`WRITE of size 1`, `56 bytes after 8-byte region`, allocation
  stack at `heap.c:7`).
- `heap_dyn 8 64`: exit 1, same class, `heap_dyn.c:10`.
- `ub`: **NOT caught** - exit 0, `UB-RESULT -2147483648`.
  MSVC has no UBSan equivalent.

### 1.3 Install / off-host routes (evidenced, not taken)

- **pacman (local sync db, no sync performed):**
  `mingw-w64-clang-x86_64-clang 22.1.7-1` (download 31.04 MiB,
  installed 282.03 MiB) and `mingw-w64-clang-x86_64-compiler-rt
  22.1.7-1` (780.96 KiB / 26864.17 KiB) exist, as do
  `mingw-w64-x86_64-compiler-rt` and ucrt64 variants. Installing
  writes `C:\msys64` - outside this study's scratch and sandbox
  write roots - so the clang64 route is **unprobed**: whether
  clang there links+runs ASan+UBSan on this host is believed
  (compiler-rt is the sanitizer runtime package) but not
  measured. Note clang's `-dumpmachine` (`x86_64-w64-windows-gnu`)
  would pass run.sh's `x86_64-*` pattern, so a future pinned
  clang leg is not ruled out by `check_host_compiler`'s shape -
  but that is a pinning decision for the lead, not this study.
- **Docker:** daemon reachable (`docker info` exit 0); the only
  local image is `eko/google-chrome:latest` - no toolchain
  image. Pulling one is network + disk, unmeasured; CI (Sec. 4)
  covers the same ground better.
- **WSL:** only `docker-desktop` plus one off-limits distro
  (host rule); no usable general-purpose Linux route.

## 2. Probe 2: the flag injection point in tools/run.sh

Read at `50aac59` (line numbers that commit):

- Existing env seams: `MSF_PYTHON` (l.31-33), `MSF_HOST_CC`
  (l.34, default `gcc`), `MSF_ARM_CC` (l.35). `CFLAGS` is
  **hardcoded** (l.36: `-std=c11 -O2 -Wall -Wextra -Werror
  -ffp-contract=off`); there is no env extension point today.
- `build_host()` (l.71-77) is the seam: `$HOST_CC $CFLAGS "$@"
  -DMSF_BUILD_ID=... $SRC tests/runner.c tests/sha256.c` -
  extra flags already flow through it (control 7 passes
  `-DMSF_TININESS_AFTER_ROUNDING=0`, l.200).
- Two more host compile sites do **not** go through
  `build_host`: the `check_host_compiler` probe (l.55) and the
  aug harness in `standard()` (l.258, its own hardcoded flags).
- MSVC **cannot** enter via `MSF_HOST_CC`: `check_host_compiler`
  (l.46-59) requires `-dumpmachine`/`-dumpversion` and a
  `__FLT_EVAL_METHOD__` probe binary, none of which `cl`
  provides. Any MSVC leg is a separate script with its own
  inventory lines, never a value of `MSF_HOST_CC`.

Recommended shape (parcel-authored, not implemented here - this
repo is read-only for the study):

- New env `MSF_SANITIZE` (empty = today's behavior, byte-for-byte)
  mapped by run.sh to an extra-flags string: `trap` ->
  `-fsanitize=undefined -fsanitize-undefined-trap-on-error
  -fno-sanitize-recover=all`; `full` -> `-fsanitize=address,undefined
  -fno-sanitize-recover=all` (only meaningful once a compiler
  that links it is pinned). Pass the string through `build_host`
  **and** the l.258 aug build; never into the l.55 probe (it
  certifies the plain compiler) and never into `symbol_scan`'s
  ARM flags (l.88).
- Prefer a new budget `sanitize` over silently re-flavoring
  `smoke`/`standard`: budgets are a fixed case at l.23, and a
  separate budget keeps the verdict namespace clean. The
  sanitizer leg is additive - the merge gate stays the
  unsanitized `standard`; nothing about `MSF_SANITIZE` may
  change what `smoke`/`standard` build or print when unset.
- Namespace the artifacts: `BUILD=build/$BUDGET` (l.26) becomes
  `build/sanitize-$MSF_SANITIZE` for the new budget, and the
  flavor rides in `MSF_BUILD_ID` (l.73-74 already embeds an id;
  append e.g. `-trapubsan`), so a sanitized binary can never be
  mistaken for a gate binary. The budget inventory header must
  print the sanitizer flavor next to the compiler lines (l.41-44
  pattern).
- Failure semantics must not be able to print PASS over a
  finding: trap flavor fails by signal (bash exit 132) - the
  runner invocation's nonzero status already fails the budget
  via the existing `|| fail` wiring, provided the verify call is
  not wrapped in anything that masks status (MSYS `timeout` did
  exactly that in this study's first script - do not use it).
  For a future `full` flavor, run.sh must also export
  `ASAN_OPTIONS=halt_on_error=1` and
  `UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1`, because
  recoverable UBSan otherwise prints and exits 0.
- Trap localization: the sanitize budget should verify
  **per file** (51 invocations) before/instead of one all-files
  call, so a bare trap names its vector file. Measured cost of
  per-file vs single call: 3.7 s vs 3.0 s (Sec. 3) - cheap.
- Negative controls to add with the parcel (gate discipline:
  each watched failing before trusted): (a) the `heap` and `ub`
  canaries above built with the same flag string must be
  refused (nonzero) - this is the control that would have caught
  a silent `-lasan`-missing no-op; (b) existing control 1
  (corrupted expected bit) re-run against the sanitized twin -
  manually verified in this study for both twins (rc=1,
  `VERDICT: FAIL`, Sec. 3).

## 3. Probe 3: sanitized runs over the vector sets

Builds in the copied tree (`tree/build-san/`), same `$SRC` list
as run.sh l.37. Baseline twin = exact gate `CFLAGS` (cost
reference; not a gate run). Logs: `07_tree_and_trap.log`,
`08_trap_verify.log`, `09_baseline_and_controls.log`,
`10_base_verify.log`, `11_trap_standard_extras.log`,
`12_msvc_build.log`, `12_msvc_run.log`, `13_asan_verify.log`,
`15_peak_ctypes.log`.

Coverage per twin: `unit`, then per-file `verify` of all 51
files in run.sh's `VECS`, then one all-files `verify`, then the
`standard` extras generated exactly as run.sh l.247-248
(`f16-exhaustive` 917,504 lines + `pack-sweep` 200,000 with
37,821 dropped non-invariant), then the control-1 corrupt
vector. The aug pool harness ran under the gcc twins only.

**Result: zero sanitizer findings anywhere.** No trap, no ASan
report, no nonzero exit except the deliberate corrupt control.
Verbatim totals (identical under all three twins):

- committed VECS: `total 411213 passed 411213 failed 0 malformed 0 skipped-planned 0` / `VERDICT: PASS`
- standard extras: `total 1117504 passed 1117504 failed 0 malformed 0 skipped-planned 0` / `VERDICT: PASS`
- unit: `unit: PASS (0 failures)` (incl. `unit flags: 1024 exhaustive state/group cases`)
- aug pool (gcc twins): `aug_exhaustive pool: total=5505024 mismatches=0` / `VERDICT: PASS`
- corrupt control: rc=1, `FAIL ... msf16_is_signaling - 0 -> 1 ...` / `VERDICT: FAIL` under base, trap, and ASan twins alike.

So each sanitizer leg covered 1,528,717 vector cases + unit;
the trap leg additionally covered the 5,505,024-case aug pool.
There is therefore **no real finding to attach a repro to**;
the minimal repros that do exist are the canaries of Sec. 1.2
(proving each leg can see its own class).

MSVC limitation, verbatim: the aug harness fails to build -
`tests\aug_exhaustive.c(40): error C4235: nonstandard extension
used: '__int128' keyword not supported on this architecture`
(line 40 is `typedef unsigned __int128 u128;`). `src/`,
`include/`, `tests/runner.c`, `tests/sha256.c` contain no
`__int128`/`__attribute__`/`__builtin_` (searched), which is
why the runner builds under cl at all. Porting the harness's
reference arithmetic off `__int128` is the only blocker for an
MSVC-ASan aug leg; the trap leg covers it meanwhile.

Honest scope of the clean result: the trap leg proves "no UB of
the `undefined` group and no known-object-size OOB on the
executed paths"; the ASan leg proves "no heap/stack/global
memory error ASan instruments, on the executed paths". Neither
leg exercised error paths the vectors don't reach (e.g.
malformed-input handling beyond what `verify` feeds, malloc
failure), and LeakSanitizer was not in play (MSVC ASan default
off here; the runner is short-lived and streaming - peak
working set 4.0 MB unsanitized).

Measured costs (this host, repeated; all-files `verify` of the
411,213 committed cases unless noted):

| twin | build | verify wall | per-file wall | extras 1.12M | aug 5.5M | peak WS | exe size |
|---|---|---|---|---|---|---|---|
| base (gcc -O2, gate CFLAGS) | 6 s | 2.42-2.49 s | 2.7 s | 4 s | 1 s | 4.0 MB | 888 KB |
| trap-UBSan (gcc -O2 + trap flags) | 7 s | 2.98-3.03 s | 3.7 s | 4 s | 1 s | 4.0 MB | 911 KB |
| MSVC ASan (cl /Od /Zi) | ~3 s (bat incl. vcvars) | 10.25-10.72 s | 10.9 s | 13 s | build FAIL | 13.3 MB | 1094 KB |

Trap overhead vs base: about +21% verify wall, +2.6% binary,
same memory. MSVC ASan wall (~4.2x base) confounds ASan with
`/Od` and a different compiler - an `/O2` ASan build was not
measured. Generated extras cost 1 s + 23 s to generate (shared
with `standard` if its artifacts are reused). Everything is
orders of magnitude under the ~4 GB ceiling (largest observed:
ASan peak pagefile commit 50.5 MB).

## 4. Probe 4: recommended parcel shape

**Both, phased** - host legs now, full combo in CI with
parcel-w6ci:

- **Parcel S1 (host, now, zero installs):** `tools/run.sh`
  gains the `sanitize` budget + `MSF_SANITIZE=trap` per Sec. 2
  (trap twin over unit + VECS per-file + extras + aug pool +
  canary and corrupt controls). Measured added wall over a
  `standard` run: ~15 s excluding vector regeneration (7 s
  build + ~8 s runs), ~39 s with. This is the same pinned
  compiler as the gate, so it can be merge-gating as soon as it
  exists. Authoring estimate: small (run.sh surgery + two
  canary sources + inventory lines).
- **Parcel S2 (host script, optional leg):**
  `tools/sanitize_msvc.bat` (+ thin bash wrapper if wanted)
  discovering cl via `vswhere` (never hardcoding the
  `14.51.36231` path), ASan over unit + VECS + extras, skipped
  by name when VS is absent (the `symbol_scan` SKIP-BY-NAME
  pattern, l.80-83). Measured: ~25 s of runs + build. This is a
  bug-finding leg, not a conformance verdict (different
  compiler/CRT, `/Od`); its evidence should be labeled as such
  anywhere it is recorded. Decide separately whether to port
  `tests/aug_exhaustive.c` off `__int128` for this leg.
- **Parcel S3 (CI, needs parcel-w6ci):** Linux gcc or clang
  `-fsanitize=address,undefined -fno-sanitize-recover=all`
  with halt-on-error options - the only route to ASan+UBSan
  diagnostics (and LeakSanitizer) in one binary. Extrapolating
  the measured ASan factor, budget ~1-2 min for committed +
  extras. The canary controls from S1 port directly (same flag
  string variable), which is the reason to name the flavor
  `full` in run.sh now even though no host compiler links it
  yet - CI sets `MSF_SANITIZE=full`, the host refuses it at the
  canary control, loudly.
- **Optional owner decision (not a parcel prerequisite):**
  `pacman -S mingw-w64-clang-x86_64-clang
  mingw-w64-clang-x86_64-compiler-rt` (~32 MiB download) would
  likely light up a host `full` flavor; it needs the Sec. 1
  canary matrix re-run before any reliance, plus a lead pinning
  decision (second host compiler beside the SF-0 pinned path).

## 5. Method notes and host hazards hit

- The documented offset-0 append corruption (AGENTS.md item 13)
  ate one log built from many `>>` appends; all cited logs were
  re-produced as single-stream writes and read back. `02` was
  single-stream per candidate block and cross-checked against
  `04`-`06`.
- MSYS `timeout` returned 0 for a process killed by the trap in
  an early script; all verdicts here rest on two independent
  exit-code routes (Python subprocess RC + direct bash status).
- `psutil` is not in the workspace `.venv`; PowerShell
  `PeakWorkingSet64` read 0 under the sandbox. Final memory
  numbers come from `GetProcessMemoryInfo` via ctypes on a
  handle held across child exit (`scripts/peak.py`).
- MSVC from Git Bash: use `/c/Windows/System32/cmd.exe` with
  `MSYS2_ARG_CONV_EXCL='*'` (the MSYS `cmd` shim is broken),
  `vcvars64.bat` for environment, and the MSVC bin dir must be
  on PATH at ASan-binary run time (runtime DLL).
- One heavy job at a time was observed; runs are seconds-scale.

## 6. Unresolved / not done

- Real `-fsanitize=address,undefined` (gcc or clang, with
  diagnostics) was **not run on this host** - it cannot be
  until a runtime is installed (clang64 route unprobed,
  Sec. 1.3) or CI lands. UBSan-with-diagnostics and LSan are
  likewise unexercised anywhere.
- MSVC `/O2` ASan timing and behavior unmeasured (`/Od` only).
- Docker toolchain-image route unmeasured (no pull attempted).
- VS2019 BuildTools cl unprobed (VS18 is newer and works).
- Target (RP2040/ARM) sanitization out of scope by brief.
- The flag-injection and budget changes of Secs. 2/4 are a
  recommendation only - the repo was read-only for this study
  and is untouched.

## 7. Evidence inventory (scratch/study-w6sanitize/)

- `scripts/01_inventory.sh`, `02_canaries.sh`,
  `04_trap_verify.sh`, `05_msvc_and_dyn.sh`, `06_msvc_retry.sh`,
  `07_tree_and_trap.sh`, `09_baseline_and_controls.sh`,
  `10_trap_standard_extras.sh`, `12_msvc_run.sh`,
  `msvc_canary.bat`, `msvc_build.bat`, `run_canary.py`,
  `verify_driver.py`, `count_run.py`, `peak.py`,
  `13_peak_mem.ps1` (superseded by `peak.py`).
- `canary/{clean,heap,ub,ub_shift,heap_dyn,heap_far}.c`.
- `logs/01,02,04,05,06,07,08,09,10,11,12*,13,15` as cited;
  `logs/03_fallbacks.log` corrupt-superseded, `logs/14*`
  zeros-superseded.
- `tree/` - the copied repo with `build-san/` twins and run
  logs; `tree.tar` sha256 in the header above.

