# parcel-w6examples report - Wave 6 queue item 4 (examples on-ramp)

Brief: `ledger/briefs/w6-examples.md`. Base
`537b08edce17112da8f84353abcb2c693f2a5e65`, branch
`wave6-examples`, worktree `worktrees/w6-examples` (the only
tree written). Tip: `b6e08fd2a1fa555c561c33b0c20c2fca5b3d970b`
("Add examples on-ramp: host + Pico public-API programs
(wave6)", one commit, 9 files, 815 insertions, worktree
clean afterwards). Nothing pushed, nothing flashed.

## Delivered

| file | what |
|---|---|
| `examples/host/main.c` | one program over the public API only, bit patterns in/out: f64+f32 `1/10` under TE vs TZ, exact `1.5*2`, `sqrt(2)` both formats, augmented `(1+2^-23)^2` with in-program integer proof, `0/0` flag inspection, library decimal output throughout |
| `examples/host/expected.txt` | pinned deterministic stdout (12 lines) |
| `examples/host/build.sh` | one command: build library+example, run, diff vs `expected.txt`, nonzero on any mismatch (`regen` rewrites the expectation) |
| `examples/pico/main.c` | same calls on RP2040, same result lines over USB CDC, banner + `EXAMPLE-RESULT` framing |
| `examples/pico/CMakeLists.txt` | minimal Pico SDK project in the `board/` shape (same SDK import, same `msf_core` target, USB stdio) |
| `examples/pico/run_example.sh` | lead-only runner in the board pattern (`board/common.sh` lock/flash, `read_until.py`, every host-expected line required verbatim) |
| `examples/README.md` | what each proves, exact fresh-clone commands, expected output verbatim, reading next (header, COVERAGE, demo, board) |
| `.github/workflows/ci.yml` | additive `example-host` job only (+13 lines, no deletions; existing jobs untouched) |
| `docs/metrics/briefs.jsonl` | own wave6 row, binary append (below) |

Library `src/include`, `tools/run.sh`, RECORD/README
untouched, per the brief's owned-files list.

## Design decisions, with reasons

- **Script over bare compiler line**: `build.sh` contains
  the single gcc line but also runs the program and
  enforces the diff, so one command serves a fresh clone,
  Git Bash on this host, and Ubuntu CI identically. It
  mirrors `tools/run.sh` toolchain/TMP resolution and
  CR-strips program output before diffing (Windows text
  mode emits CRLF; committed files are LF - no-op on Linux).
- **`1/10`, not `1/3`**: exact-rational derivation showed
  binary64 `1/3` rounds down (TE == TZ `3fd5555555555555`),
  which would make the two-attribute demonstration
  invisible in binary64. `1/10` rounds up under TE in both
  formats (f64 `...999a` vs `...9999`, f32 `3dcccccd` vs
  `3dcccccc`). The first idea was discarded on evidence.
- **Augmented pair in binary32**: `(1+2^-23)^2 =
  1 + 2^-22 + 2^-46` (head `3f800002`, tail `28800000`).
  The exact product fits in 47 bits, so the in-program
  proof (decode to significand x 2^e, integer multiply,
  rescale head/tail exactly to the product exponent, sum,
  compare) stays in portable `uint64_t` C11, identical on
  host and Cortex-M0+. Pair flags are `00` (pair exact).
- **Decimal conversion gets its own flags cell**: conversion
  can itself raise inexact; printed flags are always the
  arithmetic operation's. Fixed style, 17/9 significant
  digits.
- **Pico program mirrors, run script reconciles**: the demo
  section of `examples/pico/main.c` is kept in step with
  the host file; `run_example.sh` requires every line of
  `expected.txt` verbatim in the board output, so drift
  fails at the merge gate. A scratch check confirmed the
  literal/constant/call sequences of the two demo sections
  match exactly (21 string literals, 21 hex constants,
  27 `msf` identifiers each).
- Neither example source names the hardware arithmetic
  types anywhere (verified by word scan), so results never
  leave integer bit containers.

## How the pinned expectations were derived

Independently of the library under test, in
`scratch/parcel-w6examples/derive.py` (workspace `.venv`
Python): positive rational `1/10` rounded to 53/24-bit
significands by integer scaling with remainder-vs-half
comparison (TE/TZ); `sqrt(2)` TE by integer square root
with guard bits (irrational, so no tie); operand patterns
for 1/10/2/1.5 by integer packing; decimal strings by
exact `Decimal` division of the result's rational value at
precision 80, rounded half-even/down to 17/9 significant
digits. Host hardware results were printed only as a
cross-check (they agree). Two expectations are
library-defined rather than standard-derived and were
taken from the committed authority vectors instead: the
augmented pair (`tests/vectors/aug-f32.vec` has exactly
`3f800001 x 3f800001 -> 3f800002 28800000 00`) and the
`0/0` quiet-NaN pattern `7ff8000000000000` with flags `01`
(committed f64 division vectors). The host program then
passed against these pre-derived pins on its first run -
`expected.txt` was written from the derivation, not
captured from the program.

## Acceptance probes (all measured in this worktree/scratch)

(a) Host build+run clean: `bash examples/host/build.sh`
  (Git Bash, gcc x86_64-w64-mingw32 16.1.0) - `EXAMPLE
  PASS`, stdout diff PASS, rc 0; re-run after the tip
  commit on the clean tree: PASS again. Watched failing,
  in the scratch rehearsal copy: one hex digit flipped in
  `expected.txt` -> diff FAIL rc 1; one digit flipped in a
  pinned constant in `main.c` -> program prints `EXAMPLE
  FAIL failures=1`, script rc 1; restored tree PASS.
(b) Pico UF2 built, never flashed. Configure:
  `cmake -S examples/pico -B build/example-pico -G Ninja
  -DCMAKE_MAKE_PROGRAM=<workspace .venv ninja>
  -DPICO_SDK_PATH=<pico-sdk> -DCMAKE_BUILD_TYPE=Release`,
  then `cmake --build build/example-pico`. Toolchain:
  CMake 4.4.4, Arm GNU 14.2.1, pico-sdk 2.3.1 (host
  `PICO_SDK_PATH`). Artifacts: `msf_example.uf2` 284,160 B
  sha256 `40f58637a5b81f03789ad171647d569842d5613a41bc01f
  0896dc2fc00562de9`; `msf_example.elf` 1,403,068 B sha256
  `a6abe67c14c2c65b7379745ab78b6d94bafcdad97be197631afcd9
  3e8d46e5c0`. Build log warning/error grep empty. Board-
  less corroboration only: demo strings present in the ELF
  image (title, augcheck, decimal pins, banner); runtime
  output on silicon is the lead's merge-gate run of
  `examples/pico/run_example.sh`, not claimed here.
(c) `tools/run.sh standard` PASS unchanged in 58 s
  (`MSF_PYTHON` pinned to the workspace `.venv`, Python
  3.12.15): drift check clean, 411,213 committed vectors,
  1,117,504 generated (f16 exhaustive + pack sweep),
  5,505,024-check aug pool differential, type/symbol scans
  clean, all 12 negative controls refused including the
  tier-inventory trio (tier1 783/783, tier2 66/66).
  Full log: `scratch/parcel-w6examples/standard.log`.
(d) Fresh-clone rehearsal: worktree tree copied without
  `.git` (tar exclude, verified absent) to
  `scratch/parcel-w6examples/rehearsal/`; followed
  `examples/README.md` literally from that root -
  `bash examples/host/build.sh` PASS rc 0 (logs in the
  rehearsal directory).

Metrics row: `docs/metrics/briefs.jsonl` by single binary
append (`scratch/parcel-w6examples/append_brief.py`):
before 13,504 B / 34 lines, sha256 `ad8cefe9a3dffd5ef5dbe
bb02c72e30be9276dfb4ddafa4d43053d5dce57fca3`; appended
531 B; after 14,035 B / 35 lines, sha256 `643f5f4f0bea13
c170fe7e5801a5c66411aa8c80e864bb430693e8eab9c77bd6`; old
bytes verified a strict prefix, appended line round-trips
as JSON (wave `wave6`, base as above).

## Honest limits

- No board was flashed and no branch pushed (brief): the
  Pico program's on-silicon output and the CI job's remote
  run are unobserved by this parcel; both are the lead's
  merge-gate proofs. `run_example.sh` itself was read for
  consistency with `board/run_board.sh`/`common.sh` but
  not executed (it flashes by design).
- `ci.yml` was validated as an additive, indentation-
  matched diff; neither local interpreter has a YAML
  parser installed, and none was installed for this - the
  lead's push is the parse/run proof.
- All new/edited text files verified LF-only, LF-
  terminated; `examples/README.md` embeds `expected.txt`
  verbatim (checked).

Scratch (`scratch/parcel-w6examples/`): `derive.py`,
`check_mirror.py`, `check_elf.py`, `append_brief.py`,
`run_host.sh`, `build_pico.sh`, `rehearsal.sh` +
`rehearsal/` copy and its logs, `run_standard.sh` +
`standard.log`, `postcommit.sh`, `commit_msg.txt`, this
report. Ledger: `ledger/parcel-w6examples.md`.
