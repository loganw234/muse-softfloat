# verifier-w6examples report (ParcelRound, examples on-ramp)

Copy: `worktrees/verify6-examples` at `4bed622` (parent `537b08e`).
Note: parcel claims tip `b6e08fd`; the issued copy sits at `4bed622`.
All findings below are against the copy as given. Work was done in
duplicates under this directory (`dup/`, `fresh/`); the copy is untouched.
`derive.py` holds the independent exact-rational derivation (venv python).
Fences honored: no parcel branch, no other worktrees, no keys, no lead
material, no GitHub history, no `plants.jsonl`, nothing `cft`, no flashing.

Stance: disconfirm only. Three blocking findings (F1, F3, F4) plus one
wrong artefact line (F2). Everything else checked out (V1..V6).

## F1 (blocks the one-command build at tip): host main.c TE constant wrong

`examples/host/main.c:155` pins f64 `1/10` under ties-to-even as
`0x3fb999999999999b`. Exact rational derivation (`Fraction(1,10)` bracketed
by adjacent doubles): `...9999 = 7205759403792793/72057594037927936 < 1/10`
(diff `-3/360287970189639680`), `...999a` above by `+1/180143985094819840`,
and `|...a - 1/10| < |...9 - 1/10|`, so TE delivers `...999a` (even mantissa).
The library prints `...999a`; the `...9b` want fails the program self-check:
pristine-tree build exits `rc=1` with `EXAMPLE FAIL failures=1`.
Artefact wrong: `main.c` (expected.txt line 2 `...999a`, README block, and
the committed `arith`/vector pattern neighbourhood agree with the library).

## F2: expected.txt mul line wrong

`examples/host/expected.txt:6` pins `mul 1.5*2` bits as `...0001`. Exact
arithmetic: `1.5 * 2 = 3`, whose binary64 encoding is `0x4008000000000000`
(`...0001` is one ulp above 3). The library prints `...0000`; `main.c:176`
and the README block agree on `...0000`. Artefact wrong: `expected.txt`.
(Masked at tip by F1 failing first; after fixing F1 alone, the stdout diff
fails on this line — which leads to F3.)

## F3: build.sh stdout diff cannot fail the build

`examples/host/build.sh:57-59`: on diff mismatch it runs
`{ cat diff.log; echo "host example: diff noted"; }` and falls through to
`echo "host example: PASS (stdout matches examples/host/expected.txt)"`
with `rc=0` (no `set -e`, no `fail`). Demonstrated in `dup/`: with the F1
constant fixed locally, a one-digit corruption of `expected.txt`
(`3dcccccd` -> `3dccccce`) still yields `PASS ... rc=0`, and the PASS line
falsely claims stdout matches. The script enforces the program self-check
(F1 fails `rc=1`) but not the committed expectation file.

## F4: CI example-host job regenerates instead of enforcing

`.github/workflows/ci.yml:89-100` (additive-only vs parent, existing jobs
byte-identical): the new job's run step is
`bash examples/host/build.sh regen`, which overwrites `expected.txt` and
exits 0. The step is even named `Build and run host example (output diff
enforced)` — false: nothing in that job can fail on a stale expectation.
The only enforcement CI inherits is the program self-check, which is red
at tip because of F1. Combined with F3, no enforced pinning of
`expected.txt` exists anywhere.

## Checks that passed (no finding)

- V1 numbers: every other pinned value re-derived exactly and matching —
  f32 `1/10` TE `3dcccccd`/TZ `3dcccccc` (one ulp apart, nearest verified);
  `sqrt(2)` f64 `3ff6a09e667f3bcd` / f32 `3fb504f3` (nearest verified, and
  `arith-f64.vec:2468` pins the f64 sqrt cell `-> ...bcd flags 10`);
  augmul pair `head 3f800002 = 1+2^-22`, `tail 28800000 = 2^-46`,
  `prod=sum=0x400001000001`; `0/0 -> 7ff8000000000000` invalid-only
  (flag words `10`/`01`/`00` match `muse_softfloat.h:86-90`); all decimal
  strings re-derived under the per-line rounding mode (TZ lines truncate:
  f64 `...991`, f32 `...940`), including the README block, which is
  byte-identical to actual program output (12/12 lines).
- V2 failure paths: self-check corruption fails `rc=1` (F1 at tip);
  expectation corruption passes `rc=0` (F3); `regen` overwrites silently
  `rc=0` and is CI-reachable (F4).
- V3 CI: additive-only diff (`+13` lines, one job); `tools/` untouched;
  only owned files differ from parent (`examples/**`, `ci.yml` new job,
  `docs/metrics/briefs.jsonl` parcel row, which the parcel brief owns).
- V4 pico: demo sections of `host/main.c` and `pico/main.c` byte-identical
  (diff of `Input operands`..`Deliberate invalid` empty); `CMakeLists.txt`
  compiles the same 10 sources with the same pins (SDK 2.3.1/ARM 14.2.1/
  CMake 4.4.4 all present); UF2 built, no flash:
  `msf_example.uf2 sha256 8abcfcfc...f6f8` (284160 B),
  `msf_example.elf sha256 f030a937...ad460`. `run_example.sh` follows the
  board pattern by reading: `take_lock` (common.sh), serial-targeted flash
  (`flash_uf2` honours `MSF_BOARD_SERIAL`) and serial-targeted read
  (`read_until.py` honours `MSF_BOARD_PORT`), verbatim grep of every
  `expected.txt` line plus `EXAMPLE-RESULT PASS` gate. Unverified by design:
  on-silicon run (lead-only, needs the board; not flashed).
- V5 fresh clone: `.git`-free copy of the tree, `bash examples/host/build.sh`
  literally from its root, runs with no missing steps — and fails `rc=1` on
  the F1 self-check, i.e. no README defect; the failure is the tree's.
- V6 gate: `tools/run.sh standard` in `dup/` with `MSF_PYTHON` pinned to the
  workspace `.venv`, unchanged: `PASS` in 55 s,
  totals `411213 + 1117504 + 5505024` checks (parcel's counts), all
  negative controls refused.

## Verdict

NOT merge-ready as copied. Fix F1 (`...9b` -> `...9a` in both `main.c`
files — pico mirrors the same wrong constant), fix F2 (`...001` ->
`...000` in `expected.txt`), make the diff fail the build (`fail` on
diff mismatch), and point the CI job at the enforcing invocation instead
of `regen`. Re-run this verification after the fix; silicon run of
`run_example.sh` remains lead-only per the parcel brief.
