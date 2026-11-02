# verifier-w6examples (ParcelRound, examples on-ramp)

Copy `worktrees/verify6-examples` at `4bed622` (parent `537b08e`; parcel
claims `b6e08fd` — findings are against the copy as given). Duplicates in
`scratch/verifier-w6examples/` (`dup/`, `fresh/`); copy untouched. Full
evidence: `scratch/verifier-w6examples/report.md` (+ `derive.py`).

## Findings (disconfirm-only)

- F1 (blocks build at tip): `examples/host/main.c:155` pins f64 1/10 TE as
  `0x3fb999999999999b`; exact rational derivation gives `...999a` (library
  agrees). Pristine build: `EXAMPLE FAIL failures=1`, `rc=1`. Wrong: main.c.
- F2: `examples/host/expected.txt:6` pins mul 1.5*2 as `...0001`; exact
  value 3.0 is `0x4008000000000000` (main.c, README, library agree).
  Wrong: expected.txt.
- F3 (check that cannot fail): `examples/host/build.sh:57-59` — a failed
  stdout diff prints `diff noted`, then false `PASS (stdout matches...)`,
  `rc=0` (one-digit corruption of expected.txt demonstrated). No `fail`.
- F4: CI `example-host` job (`.github/workflows/ci.yml:100`) runs
  `build.sh regen` (overwrite, `rc=0`) despite its `output diff enforced`
  name. Existing jobs byte-unchanged; `tools/` untouched. No enforced pin.
- V1 numbers otherwise exact: f32 1/10 pair, sqrt2 f64/f32 (+ vector row
  `arith-f64.vec:2468`), augmul pair/prod `400001000001`, 0/0 NaN/flags,
  all decimals under per-line rounding, flag words per header. No finding.
- V2/V5: self-check fails `rc=1`; expectation corruption passes `rc=0`;
  fresh `.git`-free `bash examples/host/build.sh` runs literally, fails
  `rc=1` on F1 only; README output block byte-identical to real output.
- V3/V4/V6: CI diff additive-only; owned files only (`examples/**`, ci.yml
  job, briefs row). Pico demo sections identical; UF2 built, not flashed
  (`8abcfcfc...f6f8`, 284160 B; SDK 2.3.1/ARM 14.2.1/CMake 4.4.4).
  `run_example.sh` follows board pattern by reading (lock, serial-targeted
  flash+read, verbatim compare + RESULT gate); silicon run lead-only,
  unverified. Standard gate in `dup/`: PASS, 411213+1117504+5505024
  checks, all controls refused.

## Verdict

NOT merge-ready as copied. Fix F1 (both `main.c` files — pico mirrors the
wrong constant), F2, the non-enforcing diff (F3), and the CI `regen`
invocation (F4); then re-verify. Full detail in
`scratch/verifier-w6examples/report.md`.
