# Examples: the on-ramp

Two small programs over the public API only
([`../include/muse_softfloat.h`](../include/muse_softfloat.h)):
the same calls on your host machine and on a Raspberry Pi
Pico (RP2040). Values enter and leave as integer bit
patterns - the IEEE 754 interchange encodings - so nothing
here depends on the host's hardware arithmetic, and both
programs print the same result lines.

## What each example proves

Both programs run one fixed demonstration:

- binary64 and binary32 division of 1 by 10 under two
  rounding attributes (`MSF_ROUND_TIES_TO_EVEN` vs
  `MSF_ROUND_TOWARD_ZERO`): the exact quotient has no finite
  binary expansion, so the attribute picks the neighbour,
  the results differ by one ulp, and both raise `inexact`;
- an exact binary64 product, which raises no flag;
- square roots in both formats;
- one Clause 9.5 augmented multiplication,
  `(1 + 2^-23)^2`, whose exact result needs one bit more
  than a single binary32 value can hold: the program proves
  with plain integer arithmetic that `head + tail` is the
  exact product, and prints `PASS`/`FAIL` for that proof;
- a deliberate invalid operation (`0/0`) with flag
  inspection (`msf_test_flags`) afterwards;
- decimal text from the library's own conversion operations
  throughout (17 significant digits for binary64, 9 for
  binary32, fixed style).

Every printed value is checked inside the program against a
pinned expectation, and the whole output is pinned again by
[`host/expected.txt`](host/expected.txt). The host program
exits nonzero if any check fails; the build script below
also diffs the output, so a silent change anywhere fails
the one command.

## Host: build, run, check

From the repository root of a fresh clone (Git Bash on
Windows, per [`../AGENTS.md`](../AGENTS.md); any bash with a
C11 `gcc` elsewhere):

```sh
bash examples/host/build.sh
```

That one command compiles the library sources in
[`../src/`](../src/) with [`host/main.c`](host/main.c),
runs the program, and diffs stdout against
`host/expected.txt`, exiting nonzero on any mismatch.
Artifacts land in `build/example-host/`. If you change the
demonstration on purpose, `bash examples/host/build.sh
regen` rewrites the expectation - review that diff before
committing it. The build itself is the single compiler line
in `build.sh` (the script exists so the run and the diff
are enforced, identically on a fresh clone and in CI).

Expected output (the script prints two extra status lines
around it):

```text
muse-softfloat example (public API, bit patterns in/out)
f64 div 1/10 TE bits=3fb999999999999a flags=10 dec=0.10000000000000001
f64 div 1/10 TZ bits=3fb9999999999999 flags=10 dec=0.099999999999999991
f32 div 1/10 TE bits=3dcccccd flags=10 dec=0.100000001
f32 div 1/10 TZ bits=3dcccccc flags=10 dec=0.0999999940
f64 mul 1.5*2 TE bits=4008000000000000 flags=00 dec=3.0000000000000000
f64 sqrt 2 TE bits=3ff6a09e667f3bcd flags=10 dec=1.4142135623730951
f32 sqrt 2 TE bits=3fb504f3 flags=10 dec=1.41421354
f32 augmul (1+2^-23)^2 head=3f800002 tail=28800000 flags=00
augcheck exact-product prod=400001000001 head+tail=400001000001 PASS
f64 div 0/0 TE bits=7ff8000000000000 flags=01 invalid=1 inexact=0
EXAMPLE PASS
```

## Pico: build the UF2

[`pico/`](pico/) is a minimal Pico SDK CMake project in the
[`../board/`](../board/) shape: same SDK import, same
library target, USB CDC stdio. Prerequisites: pico-sdk
2.3.1, the Arm GNU toolchain, CMake and Ninja. From the
repository root:

```sh
cmake -S examples/pico -B build/example-pico -G Ninja \
    -DPICO_SDK_PATH=<path-to-pico-sdk> -DCMAKE_BUILD_TYPE=Release
cmake --build build/example-pico
```

The firmware is `build/example-pico/msf_example.uf2`. On
the project host, [`pico/run_example.sh`](pico/run_example.sh)
does the whole board run - build, flash, read back, and
check every host-expected line - lead-only under the board
lock (see [`../docs/BOARD.md`](../docs/BOARD.md)):

```sh
bash examples/pico/run_example.sh
```

On the board the output is the same block as above, framed
by a banner naming the chip (`MSF-EXAMPLE 1 ID <hex>`) and
a final `EXAMPLE-RESULT PASS failures=0` line.

## What to read next

- [`../include/muse_softfloat.h`](../include/muse_softfloat.h)
  - the whole public surface; each declaration names its
  clause and claiming wave.
- [`../docs/COVERAGE.tsv`](../docs/COVERAGE.tsv) - what is
  implemented per instantiation, and against which
  authority it is gated.
- [`../demo/`](../demo/README.md) - the three workload
  proofs (IAS15, interval geometry, KissFFT) reproduced
  from a fresh clone.
- [`../board/`](../board/README.md) - how the project
  itself flashes and replays vectors on silicon.
