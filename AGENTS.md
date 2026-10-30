# Working on muse-softfloat

Short and true: only what is non-obvious and has already cost time. Delete an
entry the day it stops being true.

## Start here: one command answers "does it still hold?"

`tools/run.sh <budget>` from this repo's root, under Git Bash (P0,
2026-10-26; SF-0 Sections 5.1, 6). Budgets, with real costs measured
that day on a machine under other load (re-measure before quoting):
`smoke` (~15 s: drift check, builds, unit tests, committed vectors,
symbol/type scans, the negative controls), `standard` (~1 min: smoke
plus exhaustive binary16 and the seeded pack64 sweep; the merge gate),
`board` (~20 s plus builds: lead-only under `<ledger>/board.lock`,
CDC replay + interposition hello on the RP2040), `bench` (~75 s:
skeleton only, never a correctness verdict), `sanitize` (~44-56 s
measured 2026-10-30, trap flavour: `MSF_SANITIZE=trap|full`,
default trap — host runners under sanitizer instrumentation,
canaries watched trapping first, then unit + committed vectors +
standard extras + aug pool; `full` needs a sanitizer runtime
this host lacks, SKIPs-BY-NAME here, runs in Linux CI). Every
budget prints its inventory before any verdict; a green run that cannot name its
vectors has failed. The plan of record is `docs/studies/SF-0.md`
(approved 2026-10-26); per-instantiation status and authorities are
in `docs/COVERAGE.tsv`.

## The authority

SF-0 Section 4, in this order when they disagree — stop, classify,
never average: (1) meaning is **IEEE 754-2019** (owner's PDF, outside
every repository; cite by clause, never commit or quote at length);
(2) executable semantic authority is **Berkeley SoftFloat Release 3e**,
pinned by archive SHA-256 in `docs/metrics/fetches.jsonl`, built in
scratch only, 8086-SSE specialization (tininess after rounding,
matching SF-0 Section 2.5) through the pinned x86-64 MinGW path with
`FLT_EVAL_METHOD==0` asserted — the default 32-bit x87 `gcc` on this
host is refused for oracle work; (3) **MPFR / exact-integer** generation
decides what Berkeley does not cover (decimal, cross-format
instantiations, 8/16-bit integers, hardest cases); host SSE2 only
inside its fenced envelope (SF-0 4.2). Header-measured Berkeley
coverage (P0): add/sub/mul/div/sqrt/mulAdd/rem/roundToInt, eq/le/lt
quiet+signaling, isSignalingNaN, format and 32/64-bit integer
conversions. No nextUp/scaleB/logB/totalOrder/class/decimal there —
those rows in `docs/COVERAGE.tsv` name their own authorities. Berkeley
flag bits are ordered differently from ours (inexact=1 … invalid=16);
translate at ingest. **No third-party softfloat source enters `src/`
or `include/`** (clean room, SF-0 4.5), and nothing with `cft` in its
name is ever opened, searched, or listed.

## The machines

One machine: the owner's Windows desktop (DESKTOP-T33SK86). The Pico is on USB
here; the lead holds the board (docs/BOARD.md). Agents run in Muse; the
shell sandbox user is `muse-sbx-r1`, escalated commands run as the owner.
Full mechanism map: docs/HARNESS.md.

Layout (all under the workspace root `Muse-Softfloat/`):

- `muse-softfloat/` — this repository (the only worktree parcels branch from)
- `ledger/` — the round ledger, outside the worktree; briefs in `ledger/briefs/`
- `scratch/<agent>/` — one per agent; the lead's is `scratch/lead/` (keys live there)
- `worktrees/<parcel>/` — `git worktree add` targets cut by the lead
- `.venv/` — project Python (workspace root): numpy, mpmath, pypdf, Pillow,
  matplotlib, imageio(+ffmpeg), ninja. Use `.venv/Scripts/python.exe`.
- pico-sdk 2.3.1 in the owner's pico directory (`PICO_SDK_PATH` names it)

## What bites on this host (measured 2026-10-26 unless dated otherwise)

- **mingw64 libmingwex `sqrt` is not correctly rounded** (measured
  2026-10-27, ias15-port): 1-ulp errors on rare operands (largest double
  below 1 → 1.0). Oracle/reference builds must execute inline `sqrtsd`
  (i.e. -O3 without -fno-builtin-sqrt), never the library body; an -O0
  strict build silently swaps sqrt implementations and diverges.

1. **Run builds and kit tools via Git Bash, not the sandboxed PowerShell.**
   Its working directory carries a `\\?\` prefix: the compilers then fail with
   "Permission denied" on paths that exist, and the kit gate's git clone of
   its bundle fails "could not open" — the gate REFUSES from PowerShell and
   PASSes from Git Bash. Plain git itself works from PowerShell (item 8).
2. **Temp must point into the workspace.** The sandbox user cannot write the
   owner's `AppData\Local\Temp` ("Cannot create temporary file ... Permission
   denied"). In Git Bash: `export TMPDIR=$PWD/<tmp>` plus `TMP`/`TEMP` in
   Windows form (`C:\...`) for native tools like arm-none-eabi-gcc.
3. **`python` is Miniconda 3.12; `python3` does not exist and `py -3` is
   broken** (Access denied to the WindowsApps shim). Kit commands say
   `python3`; run them with the Miniconda or `.venv` interpreter by full path.
4. **Line endings are bytes.** `.gitattributes` is `* -text`; git converts
   nothing. Write LF. Host `core.autocrlf=true` is overridden by that file.
5. **A Python heredoc in Git Bash can lose a backslash** (`\n` arrives as a
   newline), and a long one can fail on an apostrophe. Write the script to a
   file and run the file. (Owner's other projects, carried in the kit.)
6. **Never pipe a long make/test through `| grep | head -N`** on this desktop:
   deadlocks at zero CPU with no message (2026-09-15, twice). Redirect to a
   file, then grep the file. Read logs, not exit codes.
7. **Windows Python prints CRLF.** The kit's `plant.py` works, but its
   selftest fails here on exactly that (its own regex, plant.py:650 in the
   kit). Parse kit-tool output trimming `\r`; the kit is frozen — record,
   don't patch.
8. **git says "dubious ownership"** for repos owned by the other user
   (sandbox vs owner). This repo was cloned as the owner; sandboxed git needs
   `-c safe.directory=<path>` per command. Never change git configuration.
9. **WSL is access-denied to the sandbox user.** Git Bash is the POSIX route.
   In Git Bash `/tmp` is the shared Windows Temp — see (2).
10. **System ninja/ffmpeg exist (winget) but the sandbox cannot execute from
    WinGet Packages.** Use `.venv/Scripts/ninja.exe` (1.13.2) and the
    imageio-ffmpeg binary; point CMake at them.
11. **No agent loads the machine on purpose** (owner rule, 2026-09-25). One
    heavy job at a time; say when a run was made under load.
12. Delete only what your run created, by its exact recorded path; stop only
    processes your run started, by PID.
13. **Loop appends can land at offset 0** (measured 2026-10-26): a
    `for f; do sha256sum "$f" >> out; done` loop produced a file holding
    only the last line plus byte remnants. Write multi-line artifacts
    from one process/stream (`sha256sum files... > out`), and check
    byte counts, not exit codes.
14. **MSYS2 `make` drops the TMP exports** its parent shell set, and
    gcc then fails on `C:\WINDOWS` (measured building the oracle).
    Invoke it as `env TMPDIR=... TMP=... TEMP=... make`.
15. **picotool needs `-f`** to load over a running USB-serial device on
    this board (`picotool load -f -x`); `picotool reboot -u` alone was
    not answered by running firmware (measured 2026-10-26, BOARD.md).

## The discipline that matters most here

The gate is the product (SF-0 Section 5). Nothing is claimed before
its gate closes: a declaration in the header is not conformance, a
vector without provenance does not count, and coverage is per
instantiation in `docs/COVERAGE.tsv` — no row may sit at
`unconfirmed` when a wave gate closes. Only (a) a regression or
(b) a wrong answer sends work back; a verifier pass precedes every
move of `main`, and generated files regenerate byte-identically or
the run refuses. The negative controls in `tools/run.sh` are
permanent: each was watched failing before it was trusted, and a
budget that stops refusing one has failed even if every vector
passes. Board results name their artifact hash, commit, flags, and
board ID, or they are not evidence. When authorities disagree:
stop, classify in the ledger (implementation defect, oracle
defect/limit, standard-reading dispute), never average, never let
test count outvote an authority.
