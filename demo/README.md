# Reproducing the three workloads

This directory lets a stranger reproduce muse-softfloat's three
workload evidences from a fresh clone with one script - without
REBOUND or KissFFT source ever entering the repository:

```sh
bash demo/run_demo.sh host            # fetch + host proofs (start here)
bash demo/run_demo.sh host --offline  # same, from a seeded cache only
bash demo/run_demo.sh board           # host proofs, then the RP2040 runs
```

Everything downloaded or generated from third-party source lands
in `demo/cache/`, which is gitignored; `demo/fetch.sh` refuses to
run at all if that path would be tracked. Delete `demo/cache/`
to start over.

## What runs

| stage | what happens | verdict against |
|---|---|---|
| fetch | downloads only the REBOUND 5.2.2 and KissFFT 131.2.0 archives pinned in `docs/metrics/fetches.jsonl`; verifies archive sha256, then licence sha256, before extracting | the fetches rows |
| IAS15 extract | `demo/make_ias15_extract.py` regenerates the 5-file extract the board build consumes (anchored transforms over the fetched sources; tables as bit patterns from `board/ias15_tables.h`) | asserted transform hit counts; the hashes below |
| KissFFT tree | `demo/make_kissfft_tree.py` applies the 3-site Fork B patch to a copy of the fetched tree | recorded patched-file sha256 (hard fail on mismatch) |
| IAS15 host identity | figure-8, 2,000 steps, through the firmware's own path (`board/ias15_api.h` + `ias15_hash.c` + `ias15_ic.h`): once with strict native flags, once with every binary64 operation interposed into muse-softfloat | `demo/expected-ias15.txt` - all 2,001 IAS15FH1 records bit-for-bit |
| KissFFT host proof | 12 configurations (N=256/1024/4096, complex/real, fwd/inv) of the patched tree, twiddles via wrapped `sinpi`/`cospi`, plus analytic anchors | `demo/expected-kissfft.txt` - 12/12 hashes |
| interval host run | the frozen 710-row catalogue through `board/interval_host.c` | `demo/expected-interval.txt` - IW1 sha256 |
| board (optional) | drives `board/ias15_run.sh`, `board/kissfft_run.sh`, `board/interval_run.sh` unmodified under the board lock | the same expected files, on silicon |

A passing host run ends with:

```
== summary (host) ==
  IAS15      PASS
  KissFFT    PASS
  interval   PASS
demo host: PASS
```

## Prerequisites

Host stages (every missing item is named by the scripts):

- **bash** - Git Bash on Windows; any POSIX bash elsewhere.
- **Python >= 3.8** (`python3` or `python`; `MSF_PYTHON` overrides).
  Standard library only.
- **An x86-64 gcc** with `FLT_EVAL_METHOD == 0` (`MSF_HOST_CC`
  overrides). The soft IAS15 build interposes through soft-float
  libcalls (`-msoft-float -mno-sse2`), so the compiler must
  support those flags; the run refuses a soft build whose shim
  counted zero operations rather than passing vacuously. This is
  the one stage tied to the project's pinned x86-64 path (SF-0);
  other host architectures are out of scope for the identity
  claim, not silently approximated.
- **Network** to exactly two URLs (the pinned GitHub archives),
  or a pre-seeded cache for `--offline`. To seed by hand, place
  `rebound-262a9cce102c69ca2cf7f3c6c1264e5e60002b7d.tar.gz` and
  `kissfft-131.2.0.tar.gz` in `demo/cache/archives/`; their
  hashes are still verified before anything is extracted.

Board stage additionally: Pico SDK (`PICO_SDK_PATH`),
`arm-none-eabi-gcc`, cmake, ninja, picotool, a pyserial-capable
python, a Pico on USB, and the workspace ledger layout
(`../ledger` holds the board lock - see `docs/BOARD.md`). The
preflight names anything missing and refuses before a lock is
taken or anything flashes. Set `MSF_BOARD_SERIAL` when several
boards share the bus.

## What this proves - and what it does not

Proves, on your machine: the pinned archives are the recorded
bytes (archive + licence hashes); the extract and patched tree
regenerate deterministically (patched KissFFT files hash-match
the board-run record); the IAS15 extract reproduces the recorded
desktop state hashes step-for-step both with native IEEE doubles
and with every operation routed through this library; the
Fork-B-patched KissFFT reproduces its 12 recorded hashes with
twiddles from the library's `sinPi`/`cosPi`; the interval
catalogue reproduces its recorded IW1 digest.

Does **not** prove: anything about silicon. Host identity is not
the board claim - the RP2040 evidence (same hashes from the
chip, under the lock, artifacts named in `docs/RECORD.md`) comes
only from the optional board stage, which is lead-run in this
project. Nor does it re-prove the library's per-operation
conformance - that is `tools/run.sh`, with authorities per
`docs/COVERAGE.tsv`. KissFFT here is the double configuration
with the one named Fork B change; "unmodified KissFFT" is never
claimed, and the float configuration is not covered.

Two recorded traps the flags are pinned against: FMA contraction
changes these trajectories (every build uses
`-ffp-contract=off`; a contracting build diverges at step 1 of
the figure-8), and on MinGW hosts the native IAS15 build needs
`-O3` so `sqrt` executes as inline `sqrtsd` - the libmingwex
`sqrt` body is 1 ulp wrong on recorded operands (AGENTS.md).

## Licences

REBOUND is GPL-3.0-or-later. It stays in your `demo/cache/`:
this repository contains only the generator that extracts the
pinned subset and our own glue - nothing here redistributes
REBOUND, and the generated extract must not be committed.
KissFFT is BSD-3-Clause and is treated the same way (fetched,
patched in cache, never vendored); the Fork B patch sites are
listed in `demo/make_kissfft_tree.py`. Demo sources themselves
are MIT like the rest of the repository. Licence files are
hash-verified inside each archive before extraction, so the
exact licence texts you are under are the recorded ones.

## Expected wall times (recorded facts, re-measure before quoting)

Host, this project's desktop (gcc 16.1, machine under other
load, 2026-10-28): full `run_demo.sh host` about a minute
including builds - downloads ~7 MB on a cold cache; the soft
IAS15 run is the slow stage at ~9 s for 2,000 steps (~26 million
interposed operations); native IAS15, KissFFT, and interval runs
are each under a second. Board, recorded: IAS15 steps at a
measured 1.58 accepted steps/s at 125 MHz, so budget roughly
20 minutes for its 2,000-step capture; interval board compute
was 7.9 s of workload time plus USB streaming; KissFFT board
runs its 12 configurations at boot in seconds.

## File inventory

Ours (committed): `fetch.sh`, `fetch.py`, `make_ias15_extract.py`,
`make_kissfft_tree.py`, `ias15_host_main.c`, `ias15_host_shim.c`,
`kissfft_host_main.c`, `kissfft_host_shim.c`, `twiddle_gate.c`
(MPFR provenance gate over the patched tree - see `docs/TWIDDLES.md`), `compare_ias15.py`,
`run_demo.sh`, `expected-ias15.txt`, `expected-kissfft.txt`,
`expected-interval.txt` (hash data - provenance in each header),
this README. Fetched/generated (never committed, all under
`demo/cache/`): the two archives, pristine trees, the IAS15
extract, the patched KissFFT tree, build output and logs.
