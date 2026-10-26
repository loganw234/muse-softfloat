# Working on muse-softfloat

Short and true: only what is non-obvious and has already cost time. Delete an
entry the day it stops being true.

## Start here: one command answers "does it still hold?"

**None yet (2026-10-26, Phase 0).** P0 writes the runner; this section then
names it, its budgets, each budget's real cost in minutes, and whether a
repeated run is cheap. Until then no command's green is a verdict.

## The authority

Not named yet. SF-0 names the executable authority and its foreign oracles, and
what is refused by name. IEEE 754-2019 (owner's PDF, outside every repository)
is the contract, cited by clause — never committed, never quoted at length.

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

## The discipline that matters most here

SF-0 writes this paragraph. Placeholder until then — do not invent one.
