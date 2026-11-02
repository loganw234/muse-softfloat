# verifier-w6sanitize report (2026-10-30, host DESKTOP-T33SK86, Git Bash)

Copy: `worktrees/verify6-sanitize` (detached HEAD `549832e`), untouched
(`git status --short` clean after all probes). All gates ran in duplicate
`scratch/verifier-w6sanitize/dup` with `MSF_PYTHON` = workspace
`.venv/Scripts/python.exe` (Python 3.12.15), toolchain gcc 16.1.0
`x86_64-w64-mingw32` (MSYS2 mingw64). Original copy never modified.

## Probe 1 — sanitize trap run + canary liveness: FAIL (two defects)

Default `bash tools/run.sh sanitize` (MSF_SANITIZE unset) does **not**
reproduce the parcel's "trap PASS x3 in 44-56 s". It SKIPs in 0 s:

- `sanitize flavour trap: SKIP-BY-NAME sanitizer runtime absent for gcc
  (x86_64-w64-mingw32)` — `ld.exe: cannot find -lubsan`
  (`dup/build/sanitize-trap/canaries/clean-build.log`).
- Final: `budget sanitize: SKIP-BY-NAME flavour=trap in 0s
  (no PASS verdict; logs in build/sanitize-trap/)` — no PASS line,
  no per-set totals, no canary trap evidence (`sanitize-default.log`).
- This contradicts `run.sh:36-38` ("trap needs no sanitizer runtime
  library (the only flavour that links on this Windows host)"):
  gcc 16.1.0 MinGW needs `-lubsan` at link even for
  `-fsanitize=undefined`.

Liveness, re-derived by own builds in `live/`:

- All five canaries built **without** flags exit 0
  (`CLEAN-OK`, `UB-RESULT 2147483548`, `UBSHIFT-RESULT 256`,
  `HEAP-WROTE idx=64`, `HEAPFAR-WROTE n=8 idx=64`) — UB silent
  uninstrumented, as required for the control half.
- The instrumented half is **unverifiable on this host**: the file's
  flags don't link (above), and the linkable variant
  `-fsanitize-undefined-trap-on-error` emits **zero** instrumentation
  (asm check: 0 `ud2|ubsan` refs vs 6 for plain `-fsanitize=undefined`;
  even genuine `INT_MAX+1` wraps with rc=0).
- By reading, the `ub` canary is **dead as invoked**: the script runs it
  with no args (`run.sh:366`), so `argc=1` and
  `(INT_MAX-100)+1 = INT_MAX-99` never overflows — it cannot trap even
  under a working UBSan, and would trip the budget's own
  `CAN_FAIL` gate there. `ub_shift` (run 40), `heap` (run 64), `heap_far`
  are genuine UB as documented; `clean` is a proper control.

## Probe 2 — flavour machinery: FAIL (refusal inverted, `run.sh:44`)

`if [ -n "${MSF_SANITIZE:-}" ] && [ "$BUDGET" = sanitize ]` refuses a
*set* var exactly when the budget *is* sanitize. Measured:

- `MSF_SANITIZE=trap + sanitize` → `REFUSED`, rc=2 (parcel: "works").
- `MSF_SANITIZE=full + sanitize` → `REFUSED`, rc=2 (parcel:
  "SKIP-BY-NAME"). Full-flavour path (`run.sh:52-54`) unreachable.
- `MSF_SANITIZE=bogus + sanitize` → `REFUSED`, rc=2 — right outcome,
  wrong gate (line 44 fires before the flavour check at line 55).
- `MSF_SANITIZE=full + standard` → **rc=0, full standard PASS, no
  refusal** (parcel: "REFUSES (exit 2)"). The merge gate silently
  ignores the var — the exact re-flavour leak the guard claims
  to prevent. Build id confirms unflavoured
  (`host-x86_64-w64-mingw32-gcc16.1.0`, no suffix).

Inventory line (`run.sh:385`) prints `flags: [$SANFLAGS]`; trap
`flags: -fsanitize=undefined` observed in the default run. The full
inventory can never be observed while line 44 stands.

## Probe 3 — non-perturbation: PASS (in code; sanitized build unrunnable here)

- `standard` PASS in the duplicate in 58 s: committed
  `total 411213 passed 411213`, extras `total 1117504 passed 1117504`,
  aug pool `VERDICT: PASS`, `budget standard: PASS`.
  (Run with `MSF_SANITIZE=full` in env — silently ignored per Probe 2,
  so a genuine unflavoured standard; build id has no flavour suffix.)
- Every control refused: corrupted-bit, wrong-nan, wrong-rm (both),
  wrong-flag, stale-manifest, count-mismatch, wrong-tininess,
  x87-refusal, tier-inventory + both mutants; `negative controls:
  all refused`.
- Seams read: `check_host_compiler` builds the probe with plain
  `$cc -std=c11` (`run.sh:95-99`, no SANFLAGS); `symbol_scan` ARM
  objects use plain flags (`run.sh:135`); SANFLAGS enters only via
  canary builds (`:333,350,371`), `build_host` (`:397`), aug harness
  (`:421`). Sanitized artifacts namespaced `build/sanitize-*`.

## Probe 4 — CI sanitize job: FAIL (does not run what it claims)

`.github/workflows/ci.yml`: header comment "The sanitize job runs the
full flavour" (`:10-14`), step name "Run sanitize gate (full flavour,
ASan+UBSan)" (`:111`), artifact path `build/sanitize-full/*`
(`:119-123`) — but the run line is
`MSF_SANITIZE=trap bash tools/run.sh sanitize` (`:112`). Trap builds
into `build/sanitize-trap/`, so the upload globs match nothing; and
with the Probe 2 bug the step exits 2 (REFUSED) — the job as committed
cannot go green. Separately: SKIP exits 0 with no `grep PASS` assertion
in the job, so a SKIP-BY-NAME would be a green check without the PASS
line (final lines are textually distinct — `SKIP-BY-NAME ... (no PASS
verdict ...)` vs `budget sanitize: PASS` — but the word "PASS" does
appear in the SKIP body: "zero findings, PASS for this flavour").

## Probe 5 — AGENTS.md / usage truthfulness: FAIL (stale cost + flavours)

`AGENTS.md:16-21` claims `sanitize` "~44-56 s measured 2026-10-30, trap
flavour" PASS-able on this host; measured: SKIP in 0 s, PASS
unachievable (trap won't link; explicit flavours refused). It also
claims `full` "SKIPs-BY-NAME here" (actually REFUSED, rc=2) and "runs
in Linux CI" (CI run line says trap). `tools/run.sh:16-23` header
repeats the 44-56 s figure.

## Consistency notes

- `tests/runner.c:478-481` carries the parcel's `memchr`/`memcpy`
  strncpy replacement — copy matches the revised tip.
- SKIP text claims "all sets clean, zero findings, PASS for this
  flavour" while running nothing; only the final line clarifies
  "(no PASS verdict ...)". Verdict discipline holds if judged strictly
  by the `budget sanitize: PASS` line, which never prints on SKIP.

## Verdict

**REJECT.** One inverted comparison (`run.sh:44`, `=` for `!=`)
disables every flavour path the parcel claims (explicit trap, full
SKIP, bogus refusal, non-budget refusal) and lets `MSF_SANITIZE`
pass silently into the merge gate; the trap flavour cannot link on
this host (`-lubsan` absent), so the claimed 44-56 s PASS does not
reproduce (SKIP in 0 s); the `ub` canary cannot fire as invoked; the
CI job runs trap while claiming full (and exits 2 as written);
AGENTS.md cost/flavour text is stale. Probe 3 (standard + seams)
is the only clean pass.
