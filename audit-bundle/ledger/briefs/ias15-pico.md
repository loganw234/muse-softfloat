**Role:** ias15-pico (IAS15 RP2040 firmware parcel)

**Authorization:** Ledger: `ledger/README.md`; standing rules
`<repo>/AGENTS.md` (board evidence rules especially); SF-0 §3.4/§9/
§11; the plan you execute is `scratch/ias15/report.md` §8 (read the
whole report + `scratch/S4/report.md` §6 first). REBOUND 5.2.2 is
GPL-3.0-or-later: extracted sources live in `scratch/ias15/` ONLY,
never enter `muse-softfloat/` (not even a header); the repo gains
only the general AEABI compat surface + firmware glue that is ours.

**Deliverable (firmware-ready, lead flashes):**
1. Extraction per S4 §6.2 keep-list into `scratch/ias15/extract/`
   (IAS15 step core, BASIC gravity, minimal sim state, warning
   sink stub; GPL notices preserved in scratch).
2. **Host gate (before any board claim):** extracted source built
   on host with the pinned flags reproduces IAS15FH1 hashes
   `scratch/ias15/out/hashes_native.txt` for 2,000 steps; the same
   extraction under the host softfloat shim matches again. Both
   gates scripted, logs kept.
3. AEABI compat surface in the repo worktree (`compat/`):
   `__aeabi_dadd/dsub/dmul/ddiv`, `__aeabi_dcmpeq/lt/gt/le/ge/un`
   (+ `dcmple` family as emitted), `__aeabi_i2d/ui2d/l2d/ul2d`,
   `__aeabi_d2iz/d2lz` etc. as the link demands, `sqrt` → all over
   `msf64_*` at `548a1b9`, following `compat/msf_wrap.{c,h}` house
   style (per-core flag state contract as documented there); trap
   stubs (loud, named) for anything else the link references —
   never approximations. Board-side selftest firmware mirroring
   `scratch/ias15/work/shim_selftest.c` checks to validate the
   AEABI comparison contract on silicon before trusting hashes.
4. Demo firmware in the worktree (`board/ias15_main.c` + CMake
   wiring beside the existing targets): figure-8, ICs as hex from
   `scratch/ias15/work/ic_fig8.txt`, tables as hex from
   `out/tables_expected.txt` (values transcribed as bit patterns
   with provenance comment — these are mathematical constants,
   carry them as data), static arena, per-step (or per-K-step,
   configurable) IAS15FH1 digests over USB CDC using the harness
   protocol style. Firmware formats NO doubles; host renders.
5. A run script + expected-output spec so the lead can flash under
   `ledger/board.lock` and compare with
   `scratch/ias15/work/compare_hashes.py` unchanged; step-rate
   measurement hooks (timer around 1,000 accepted steps) with
   named clock, per §8.2 — measurement apparatus only, you claim
   no rate (the lead measures under the lock).

**Base:** `548a1b9`. Worktree `worktrees/w-ias15` (branch
`w-ias15`). Time box: **360 minutes** from first ledger entry;
checkpoint at 300. Ceiling: **3,500 hand-written lines** in the
repo worktree (extraction in scratch is evidence, not counted;
generated/transcribed constant tables excluded).

**Files you own:** `compat/*` (extend; landed copysign behavior
bit-identical), `board/ias15_main.c` + whatever new `board/ias15_*`
files you need, `board/CMakeLists.txt` (add targets only),
`ledger/ias15-pico.md`, scratch `scratch/ias15/` (extend ias15-port's
tree; keep its scripts/out intact). Off-limits: `src/`, `include/`,
`tables/`, `tools/` (run.sh wiring is the lead's; propose the line
in your report), `tests/`, `docs/` except `docs/BOARD.md` additive
sections. **Board: you do NOT flash.** No picotool, no COM port;
the lead runs the board under the lock from your artifacts.
Kernel inadequacy = escalation. Never push/merge; detailed commits
ending `Co-Authored-By: Muse Code (muse-wonder-full-1.0)
<noreply@meta.ai>`. Clean room: nothing with `cft` in its name,
ever.

**First action:** escalation test `ledger/urgent/ias15-pico-test.md`,
then design entry (extraction file list with line counts kept,
arena layout, compat symbol table vs measured undefined-symbol
surface, CDC record format). Corrections under
`## What this brief got wrong`.

**Tests (counts by provenance):** host gates (2) both green with
hash-file equality printed; compat host-compile under
arm-none-eabi-gcc with `-Wall -Wextra -Werror`; firmware builds
clean for RP2040 (UF2 + ELF sha256 in report); undefined-symbol
census of the final link (every FP symbol accounted: msf64-backed,
inline bit-op, or named trap); `tools/run.sh smoke` green
(regression — your compat additions must not disturb it).
Negative control: an extraction with a deliberately perturbed
table entry fails the host gate (name it, revert it).

**Reporting:** `scratch/ias15/pico-report.md` (gates, symbol census,
sizes: UF2/ELF/.text/.bss, arena bytes, artifact hashes, exact
lead run instructions), then ledger close READY (lead can flash
and expect hash equality) or NOT READY with gaps named.
