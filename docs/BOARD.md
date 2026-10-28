# The board

Filled 2026-10-26 (Phase 0) from the bootstrap kit's BOARD.md. A Pico is
"constantly connected for debugging", and "Lead controls hardware access"
(owner, 2026-10-23). Rows not yet measured say so; a board result that cannot
name its artifact is not evidence.

## The protocol

- **The lead holds the board.** A parcel that needs board time asks the lead by
  the escalation channel. The lead runs the job itself, or grants a slot by
  name and by time. One holder at a time.
- **The lock is a file:** `<ledger>/board.lock`, holding the holder's name, the
  job, and the time from `date`. Take it before touching the board, remove it
  by its exact path when done. A lock the holder did not write is not theirs
  to remove.
- **Every board result names its artifact:** the ELF/UF2's sha256, the commit
  it was built from (SHA and content asserted apart), the build's flags, and
  the board's id.
- **A board run goes in the record** like any other run: command, output, what
  it showed. A board result is checked against the authority, never against
  the board's own earlier result.
- **Long runs are the lead's**, at hours that do not load a machine someone
  else is using (owner rules 2 and 9).

## The details (2026-10-26)

| what | the answer |
|---|---|
| the machine the board is attached to | the owner's desktop, DESKTOP-T33SK86 (this machine) |
| the debug probe, and how it is reached | **None configured yet.** picotool 2.3.1 over the Pico's own USB (BOOTSEL) is the working route (MEASURED). OpenOCD is not installed; whether a Debug Probe is attached is an open kickoff question for the owner. |
| the serial port, and its settings | USB CDC enumerates as **COM8** (VID 2E8A) under P0 firmware (MEASURED 2026-10-26); baud is CDC-ignored, host opens at 115200. Discovery is by VID in `board/host_replay.py`, so the COM number may move. COM1/COM5 remain not-the-board. |
| the board's id, or its unique serial | RP2040 rev **B2** per `picotool info -a`; unique ID **`e66440a2cb6f5c2b`** (MEASURED 2026-10-26 two ways: picotool's tracked serial `E66440A2CB6F5C2B` and the harness banner from `pico_get_unique_board_id`). |
| how a build is flashed, as a command | `picotool load -f -x <file.uf2>` under the lock (MEASURED 2026-10-26). The `-f` is required to reboot a running device with a USB serial connection; a plain `picotool reboot -u` was not answered by running P0 firmware. Hands (BOOTSEL) needed only if that fails. |
| how a run's output is read, as a command | `board/host_replay.py` (vector replay + whole-run hash compare) and `board/read_until.py <marker>` (hello/bench), both pyserial over the CDC port, driven by `tools/run.sh board|bench`. First on-silicon evidence 2026-10-26: 968 board-smoke vectors, whole-run SHA-256 `4573ac09...f28a7` identical host and board; harness UF2 sha256 `987bb37b...8456`, hello UF2 `40e21e7c...78b7` (per-build hashes; each run prints its own). |
| how the board is reset to a known state | Reflashing via the row above is the reset: `load -f -x` reboots into BOOTSEL, loads, and starts the application (MEASURED hands-free across harness→hello→bench cycles, 2026-10-26). |
| what the lock file's path is | `<ledger>/board.lock` (ledger root is defined in docs/HARNESS.md) |
| who may hold it besides the lead, if anyone | nobody yet; a parcel may be granted a named slot by the lead, recorded in the ledger |

## IAS15 demo firmware (SF-0 Sec.9)

Two further targets beside the P0 harness/hello/bench, both lead-run
under the same lock and protocol above:

- `msf_aeabi_selftest` (no workload): validates the AEABI binary64
  compat surface (`compat/msf_aeabi.c`) on silicon before any board
  hash is trusted. Banner `MSF-AEABI-SELFTEST 1`, verdict line
  `AEABI-RESULT PASS/FAIL checks=... failures=...`.
- `msf_ias15` (figure-8 demo): needs the GPL REBOUND extraction at
  build time via `-DIAS15_EXTRACT_DIR=<workspace>/scratch/ias15/extract`
  (the repo holds only glue, the opaque `board/ias15_api.h`, and the
  coefficient/IC bit-pattern data). At startup it runs the directed
  AEABI subset (`AEABI-LITE PASS`) and cross-checks the workload's
  table bits against `board/ias15_tables.h` (`TABLES PASS`), then
  refuses run commands unless `IAS15-READY 1`.
  - `I` prints the banner (`MSF-IAS15 1 ID ... NMAX 16 clk_sys_hz ...`)
    plus the readiness line.
  - `R <nsteps> <kevery>` resets to the figure-8 ICs and streams
    IAS15FH1 hash rows (same field shapes as the desktop reference
    file) for step 0, every kevery steps, and the final step, then
    `# END nonfinite_hashed_fields=... steps_done_field=...
    warnings=... errors=...` and `IAS15-DONE`. The non-finite count
    covers hashed steps, so the equality run uses kevery=1.
  - `T <nsteps>` is the step-rate apparatus: per 1000-accepted-step
    block it prints `RATE block_steps=1000 elapsed_us=...
    clk_sys_hz=...` (interval measured with the RP2040 1 MHz timer
    via `time_us_64()`, stepping only) plus that block's hash row.
    A rate claim names these lines, the UF2 hash, and the clock;
    the firmware prints integers and bit patterns only, never a
    formatted double.
- Host side: `board/ias15_host.py` captures by VID with
  inactivity timeouts (a 2000-step run is minutes-scale at kevery=1;
  `board/read_until.py`'s 60 s window is too short for it) and
  writes hash rows verbatim for the desktop comparator.
  `board/ias15_run.sh` is the whole lead sequence (selftest, flash,
  `R 2000 1`, compare, `T 2000`); its header names the environment
  variables. Expected-output spec: selftest PASS with 0 failures;
  run capture compares equal for all 2001 records against the
  reference hashes (first divergence: none) with
  `nonfinite_hashed_fields=0`.

## Interval workload firmware (SF-1 Step 1c)

`msf_interval` streams the frozen Step 1c catalogue
(`tests/interval_catalogue.tsv`) from the host and folds the
identical IW1 field sequence as `board/interval_host.c`
(layout in that file's header). Protocol: banner
`MSF-INTERVAL 1 ID ... clk_sys_hz ...`; `B` begins a run; `S` /
`X` / `T` carry one sphere/box/torus row as binary64 bit
patterns and are acked `R <id>`; `E` prints `SUMMARY ...`
(with `compute_us`, RP2040-timer time inside workload calls
only - a measurement record, not a rate claim), then
`BOARD_SHA256 ...` and `INTERVAL-DONE`. The board digest must
equal the host runner's `HOST_SHA256` for the same file.

`board/interval_run.sh` is the lead sequence under the lock:
regeneration check, host hash, firmware build, targeted flash
(`picotool load --ser <serial> -f -x` - never untargeted while
other boards share the bus; `MSF_BOARD_SERIAL` selects, default
the genuine board above), full-catalogue stream via
`board/interval_board_host.py` (selects the CDC port by USB
serial), artifact hashes printed. First silicon evidence
2026-10-27: all 710 rows, IW1 `ce81d66e...a9aec` identical on
host and board `e66440a2cb6f5c2b` at 125 MHz, `compute_us`
7,918,838 for 616,754 counted ops; UF2 sha256
`a9b7cf1d...1b3a5` (per-build; every run prints its own).

## KissFFT Fork B workload firmware (SF-1 Step 2c)

One further guarded target, lead-run under the same lock and
protocol above. First silicon evidence 2026-10-28: all 12 KF
rows bit-identical to the host proof on the genuine board
`e66440a2cb6f5c2b` (serial-targeted flash, `MSF_BOARD_SERIAL`
uppercase); UF2 sha256 `bafafa24...568f` (per-build; every run
prints and hashes its own artifacts):

- `msf_kissfft` (KissFFT runtime-twiddle workload): built only
  with `-DMSF_KISSFFT_DIR=<patched KissFFT 131.2.0 scratch tree>`;
  without it the target is absent and all other targets build
  unchanged. The workload is BSD-3 KissFFT 131.2.0 with **one
  named change** (Fork B): twiddle generation takes exact cycle
  fractions into correctly rounded `sinpi`/`cospi` instead of
  radian phases into `sin`/`cos` - "unmodified KissFFT" is never
  claimed. Its source never enters this repository.
  - At boot (and again on `R`) it runs N in {256, 1024, 4096} x
    {complex fwd/inv, real fwd/inv} (double config) from the
    shared integer-LCG inputs, twiddles generated at runtime
    on-device, and prints banner `MSF-KISSFFT 1 ID ...`, one
    `KF <N> <kind> <dir> <sha256>` row per configuration, then
    `KISSFFT-DONE`. At these gated power-of-two sizes the
    twiddles are the correctly rounded values of the exact
    mathematical twiddles (host MPFR provenance gate, 0
    mismatches); the KF rows must equal the host proof's
    bit-for-bit under the same patched source.
  - Run: `board/kissfft_run.sh` (lock, serial-targeted flash
    via `MSF_BOARD_SERIAL`, capture/compare via
    `board/kissfft_host.py`, port by VID or `MSF_BOARD_PORT`).
