# ias15-pico report: IAS15 RP2040 firmware, firmware-ready for lead flashing

Agent ias15-pico, 2026-10-27. Verdict: **READY** (lead can flash and
expect hash equality). The board was not touched: no picotool, no
COM port, no `board.lock` from this parcel. Everything below the
board line is host evidence; the single remaining unknown is
silicon behaviour itself, which the selftest firmware is built to
fail loudly on before any hash is trusted.

Base `548a1b9aa7e71ab988cea77d9f2a1591ca84328e`, worktree
`worktrees/w-ias15` branch `w-ias15`, three commits (not pushed,
not merged):

- `0493615` compat AEABI surface (`compat/msf_aeabi.{h,c}`)
- `b09e572` board glue (selftest + demo firmware + host capture)
- `361bf05` `docs/BOARD.md` IAS15 protocol section

Ledger: `ledger/ias15-pico.md` (design 08:35 with 4 brief
corrections, close entry at the end of this run); escalation test
`ledger/urgent/ias15-pico-test.md` 08:24 -0700 (watcher observed
delivering). GPL boundary kept: all REBOUND-derived code is in
`scratch/ias15/extract/`; the repo commits were checked to contain
no upstream text (no GPL marker, no `reb_particle`). Clean room
kept throughout.

## 1. Extraction (scratch/ias15/extract/, GPL-3.0-or-later)

Produced by `scratch/ias15/scripts/pico_21_extract.py` (anchored
transforms over the pinned 5.2.2 tree; regenerates byte-identical,
hashes below) plus hand-written minimal wrapper:

| file | lines | sha256 |
|---|---:|---|
| `extract/integrator_ias15_min.c` | 663 | `770d3ac9482d9b821f3b2df1294a9ff430bd5bcc129f3cad5cfdc8b41b9cca20` |
| `extract/gravity_basic_min.c` | 153 | `99065d96b24171d9e2805edb0cc03c390281fa9d5fd2fa1951dde879dbc99bfc` |
| `extract/sim_min.c` | ~170 | `d24563198d3f527849e0d37659931d257288059ddb6dc02ea73f62b62dd4d1f1` |
| `extract/reb_min.h` | ~140 | `0a8966fd88f3d46a0a986d4bbeab4c0644228b41e93fa9bed9bb0fbe1a7c134f` |
| `extract/ias15x.c` | ~115 | `bc5cdb2bebbcad724a4bad70ffcd741f4673a7c9bd9322e99dca256f70bb0ddb` |
| `extract/driver_extract.c` | 247 | `9a42bf343cd85e7ffef4659e05476b76b2d0a30ad9ac8eaf7dcb4ac8d4196c9a` |

Keep-list per S4 §6.2 / SF-0 §9: IAS15 step core with all four
adaptive modes verbatim (PRS23 stays a runtime pin), BASIC gravity
non-OpenMP path verbatim including the `(gb.x + x)` forms against
the all-`+0.0` default ghostbox, warning/error sinks as counters.
Deleted: variational/`map` branches, MEGNO, velocity-predict
branch, COMPENSATED csa0 branch (executed else-branch kept
verbatim), timescale helper, descriptors/registry,
GENERATE_CONSTANTS, `w[8]` (MEGNO-only). Tables `h/rr/c/d` are
binary64 bit patterns from `out/tables_expected.txt` (union
initialisers; use sites unchanged). Allocation: one caller-owned
arena, zeroed at init, carved once (upstream `realloc_dp7`
whole-buffer zeroing + csx/csv kill reproduced in the arena
alloc); zero allocation per step; `N > NMAX` is a loud error.
ARM-measured sizes: particle 88 B, state 88 B, min sim 152 B;
arena required at NMAX=16 is 20,464 B of the 32,768 B firmware
buffer (`g_arena`, rest is headroom). One live simulation per
arena is a documented limitation.

Honest scope of the extract: BASIC gravity only (any other
`gravity` value increments the error sink instead of falling
back), PRS23 pinned by the IC data though the other modes' code is
present, no `min_dt>0` (IC pins 0; changing it re-pins reference
hashes), no growth of N mid-run beyond NMAX. `driver_extract.c`
is the host-proof driver with exactly one include changed.

## 2. Host gates (all green; logs in scratch/ias15/out/pico_*.log)

| gate | script | result |
|---|---|---|
| ARM census (design input) | `pico_20_arm_census.sh` | workload TUs emit only `__aeabi_dadd/dsub/dmul/ddiv`, `dcmpeq/ge/gt/lt/un`, `sqrt`; probe adds `dcmple` + conversions; **no `cdcmple` family** at -O2/-O3 |
| A: extract \| native strict flags | `pico_22_gate_native.sh` | **2,001/2,001 records equal** to `out/hashes_native.txt`, first divergence none |
| B: extract \| soft shim, core at 548a1b9 | `pico_23_gate_soft.sh` | **2,001/2,001 equal**; shim op counts printed (7.23M add etc., no traps) |
| C: firmware path (ias15x + repo IC + repo hash builder), native and soft | `pico_26_gate_hashbuilder.sh` | **2,001/2,001 equal, both variants**, warnings=errors=nonfinite=0 |
| E: compat logic + ARM `-Wall -Wextra -Werror` | `pico_27_gate_compat.sh` | 5,504 direct checks 0 fails (drsub order, state rounding/flags, named pow/exp traps); cross-compile clean; compat object references no FP helper |
| D: negative control | `pico_28_negative_control.sh` | `rr[0]` +1 ulp in a throwaway copy **diverges at step 1** (H_full), copy deleted, real extract hash unchanged |
| F1: firmware build | `pico_29_fw_build.sh` | both targets link (hashes in §4) |
| F2: final-link census | `pico_30_fw_census.sh` | 0 problems (§3) |
| F3: regression | `pico_31_smoke.sh` | all pre-existing board targets still build; `tools/run.sh smoke` **PASS in 15 s**, 9/9 controls refused |

Reproduce everything: `bash scratch/ias15/scripts/pico_00_all.sh`
from the workspace root (includes the generated-header
byte-identity check against the committed tree).

## 3. Symbol census of the final links (Gate F2, pico_30 log)

Per ELF (`msf_aeabi_selftest`, `msf_ias15`), every FP symbol
accounted:

- **msf64-backed (ours):** 23 `__wrap_` bodies defined from
  `compat/msf_aeabi.c` (+ `__wrap_copysign` from the landed
  `compat/msf_wrap.c`) — dadd/dsub/dmul/ddiv, dcmpeq/lt/le/gt/ge/un,
  i2d/ui2d/l2d/ul2d, d2iz/d2uiz/d2lz/d2ulz, f2d/d2f, sqrt, fabs.
  Workload/selftest functions (`reb_integrator_ias15_step`,
  gravity, `pair_checks`, `single_checks`) call **only** these
  wraps + direct `msf64_*`/`msf32_*` core symbols (call lists in
  the log). `drsub/d2ulz` coverage: drsub exercised by host gate
  E; d2ulz now also exercised by the board selftest.
- **Named traps:** no trap body is in either ELF because nothing
  references the trapped names (`pow`, `exp`, ...); the `--wrap`
  entries exist so any future reference lands on
  `MSF-TRAP <name>` + hang instead of a libm approximation.
- **No unwrapped double helper exists in either ELF** (the only
  defined `__aeabi_*` are `__aeabi_bits_init/mem_init` and the
  integer div-by-zero stubs), and **no libm-named body** is
  defined. There are also no binary32 `__aeabi_f*` helpers
  defined at all, so the design-open float-scope question is moot
  for these binaries.
- **Integer/SDK, accounted:** `__wrap___aeabi_lmul/idiv/uidiv`
  are the SDK's own pico_int64_ops/pico_divider wraps (SIO
  divider convention), `__wrap_memcpy/memset/printf/...` the
  SDK stdio/mem wraps — all integer/IO, none in the FP path.
- Inline bit-ops: `fabs/copysign/isnormal`/negation in the
  workload compile to ARM integer bit ops (as ias15-port
  measured); the wrapped `fabs/copysign` bodies cover call forms.

## 4. Artifacts and sizes (built from final source, gate F1)

Build: pico-sdk 2.3.1, arm-none-eabi-gcc 14.2.1, CMake/Ninja,
`-DCMAKE_BUILD_TYPE=Release`, workload TUs pinned
`-std=c99 -O2 -ffp-contract=off -fno-fast-math
-fno-unsafe-math-optimizations -fno-builtin-sqrt`. Build tree
`scratch/ias15/fw-build/` (lead's run script builds its own in
`build/board-fw/ias15fw` and prints fresh hashes — prefer those;
these are the pre-verification builds of the identical sources).

| artifact | bytes | sha256 |
|---|---:|---|
| `msf_aeabi_selftest.uf2` | 246,784 | `205d0bbb9254d37cda7bf03ddf5e00a3104699618c3933dd85dd5ca61c65df00` |
| `msf_aeabi_selftest.elf` | 1,290,716 | `2de9b2c038d5ac5648b2e7e89d17e8a3923cb28c2be94b6be225a8a6558a5cb9` |
| `msf_ias15.uf2` | 299,520 | `e85fc01db3a3f796ddb30a285a6e63782a18c9518e344aabb12d6ccd248c1338` |
| `msf_ias15.elf` | 1,437,884 | `715a1080877ce7872ab48886429e71bd76c51a608228d87de1d8920c147bced3` |

Sections: selftest `.text` 116,128 B, `.bss` 2,616 B; ias15
`.text` 139,560 B, `.rodata` 5,468 B, `.bss` 35,720 B (arena
32,768 B; required 20,464 B at NMAX 16, workspace formula
1176·N + 88·N + sim/state). Stack: 4 KiB core-0
(`-fstack-usage`: step 816 B, gravity 288 B; 8 KiB does not fit
SCRATCH_Y and was refused by the linker, kept at 4 KiB).

## 5. Exact lead run instructions

One command from the worktree root (it takes the lock, builds,
flashes, checks, compares; full protocol in `docs/BOARD.md`):

```
cd worktrees/w-ias15
IAS15_EXTRACT_DIR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/ias15/extract \
IAS15_REF_HASHES=/c/Users/logan/source/repos/Muse-Softfloat/scratch/ias15/out/hashes_native.txt \
IAS15_COMPARE=/c/Users/logan/source/repos/Muse-Softfloat/scratch/ias15/work/compare_hashes.py \
bash board/ias15_run.sh
```

Expected: `AEABI-RESULT PASS` with `failures=0`; then the
2000-step capture comparing **2001 matched, first divergence
none**, `nonfinite_hashed_fields=0 steps_done_field=2000
warnings=0 errors=0`; then two `RATE block_steps=1000
elapsed_us=... clk_sys_hz=...` lines. Duration expectations:
step rate is unmeasured (no claim); the `R 2000 1` capture allows
600 s of line silence — if the run is slower than that between
lines it cannot be (kevery=1), but a full run could take tens of
minutes wall time; `R 200 1` via `board/ias15_host.py --cmd
"R 200 1"` is the cheap first smoke (step-0 H_state must be
`62bb23b0...333e01`, step 2000 in the full run
`4d4530a6...f48abb`). Failure triage order: `MSF-TRAP` line =
unproven FP surface reached (name printed, firmware hangs — reflash
to recover); `E not-ready` = AEABI-lite or table check failed at
startup (do not trust hashes; the selftest log has the failing
check); hash divergence at step k = bisect by step exactly as
SF-0 §9 prescribes, gates A–C here localise it to the ARM build
if they still pass.

## 6. What remains / proposals

- Board run + step-rate measurement (lead, above). Encounter-phase
  worst-case rate is a separate `T` run per report §8.2(c) if the
  video needs it.
- Proposed `tools/run.sh` line (tools/ is the lead's): a
  `ias15` budget aliasing the sequence in `board/ias15_run.sh`
  (lead-only, under the same lock), e.g. beside the `board`
  budget, with the three env vars defaulting to the workspace
  scratch paths and refusing when the extract tree is absent.
- Nothing here claims conformance beyond its gates: compatibility
  of the committed `compat/` surface with Wave-3 string work or
  float (`__aeabi_f*`) consumers is unimplemented and unwrapped
  by design; adding the f-family is a same-file extension if a
  consumer ever needs it.
- The demo accepts only the built-in figure-8; other ICs mean
  regenerating `board/ias15_ic.h` + a fresh host reference (the
  extract + driver already support the other ias15-port IC files
  on the host).
