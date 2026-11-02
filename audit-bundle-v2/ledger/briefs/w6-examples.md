**Role:** parcel-w6examples (Wave 6 queue item 4: examples on-ramp)

**Base:** `537b08edce17112da8f84353abcb2c693f2a5e65`, branch
`wave6-examples`, worktree `worktrees/w6-examples`. Work only there.

**Job:** give a new user a working on-ramp without
reverse-engineering `board/`. Deliver:
- `examples/host/main.c` - one small program over the public
  API only (bit-pattern in/out): a few binary64 + binary32 ops
  across two rounding attributes, one augmented pair showing
  head+tail reconstructing the exact product (check it in the
  program with integer arithmetic or a second library route,
  print PASS/FAIL), flag inspection after a deliberate invalid
  op, and decimal output via the library's own conversion -
  no hardware float/double named for results. Deterministic
  stdout, committed as the expected output next to it.
- One-command host build (`examples/host/build.sh` or a
  Makefile-free documented gcc line in the README, your call
  with reason): builds the library sources + example, runs
  it, diffs stdout vs the committed expectation, nonzero on
  any mismatch.
- `examples/pico/` - minimal Pico SDK CMake project in the
  `board/` shape (study board/CMakeLists.txt + common.sh
  conventions) running the same calls on the RP2040 and
  printing the same result lines over USB CDC, with a
  run script in the board pattern (lead-only under the lock
  at the merge gate - you build the UF2, never flash).
- `examples/README.md` - what each example proves, exact
  build/run commands from a fresh clone's repo root,
  expected output, and what to read next (header, COVERAGE,
  demo).
- CI: a job in `.github/workflows/ci.yml` that builds and
  runs the host example on Ubuntu and diffs its output
  (additive job only; do not touch the existing jobs).

**Owned files:** examples/** (new), .github/workflows/ci.yml
(new job only), docs/metrics/briefs.jsonl (own row, wave
"wave6", base above, binary-append). Library src/include and
tools/run.sh frozen; no RECORD/README edits.

**Acceptance:** (a) host example builds+runs clean in the
worktree; its self-checks fail when you deliberately corrupt
one expectation in scratch (watched failing); (b) UF2 for the
pico example builds in your worktree (command + hashes in
report); (c) `tools/run.sh standard` PASS unchanged;
(d) a fresh-clone rehearsal: copy the worktree tree (no .git)
to scratch, follow examples/README.md literally, host path
works. The lead pushes the branch for the CI job proof and
runs the pico example on silicon at the merge gate.

**Outputs:** tip commit(s) with detailed body +
`Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>`;
`scratch/parcel-w6examples/report.md` +
`ledger/parcel-w6examples.md`. Structured
complete/evidence/unresolved mandatory. Script files, Git
Bash, MSF_PYTHON pinned to workspace .venv. Nothing with
`cft` in its name. ~360 min.
