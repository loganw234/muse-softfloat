# parcel-w6ci report: library CI on Linux (Wave 6 queue item 2)

**Tip:** `eda5812d2803b113fe0eaa37b626d5d097a4a979` on branch
`wave6-ci`, worktree `worktrees/w6-ci`, base
`50aac59f6035d56c37340ff07c59252cfd22d5d4`. One commit, not
pushed (the lead pushes to trigger the real Actions run).

**Files changed (3, +94/-1):**

- `.github/workflows/ci.yml` (new, 85 lines): two independent
  jobs on `ubuntu-latest` triggered by push, pull_request and
  workflow_dispatch. `smoke` (timeout 20 min) and `standard`
  (the merge gate, timeout 60 min). Each job: checkout@v4,
  `sudo apt-get update && sudo apt-get install -y gcc
  libc6-dev python3 gcc-arm-none-eabi`, a toolchain-inventory
  step that prints versions and fails loudly if a tool is
  missing, `MSF_PYTHON=python3 bash tools/run.sh <budget>`,
  then upload-artifact@v4 (`if: always()`) with the
  `build/<budget>` logs (`*.log`, `*.txt`, `*.out`,
  `controls/*.log`).
- `tools/run.sh`: two portability-only guards (+9/-1). Nothing
  the gate checks changed; no refusal weakened.
- `docs/metrics/briefs.jsonl`: own wave6 row appended in
  binary (+554 bytes, 12350 -> 12904; prefix hash-verified
  unchanged).

Deliberately NOT changed: no HARNESS.md/AGENTS.md pointer -
the ci.yml header comment documents the workflow in place and
the brief allows a pointer only "if truly needed". No
src/include/RECORD/README edits.

## Windows/MSYS2 assumption inventory for tools/run.sh

Line numbers are post-edit. "Disposition" is the Linux answer
for each.

1. **PATH prepend `/c/msys64/...` (line 28). CHANGED.** Was an
   unconditional prepend of two Windows-only directories. Now
   fires only when `/c/msys64/mingw64/bin` exists; on Linux
   the directories are absent and gcc/python3 resolve from
   the system PATH. Windows behaviour probed identical (guard
   fires here).
2. **Python resolution (lines 34-40). CHANGED.** Was
   MSF_PYTHON, then `../.venv/Scripts/python.exe` (Windows
   venv layout), then bare `python` - which Ubuntu does not
   provide. Added a `python3` fallback reached only when both
   earlier resolutions miss AND bare `python` does not
   resolve, so no existing Windows resolution can change.
   CI pins `MSF_PYTHON=python3` regardless; this is the
   belt-and-suspenders for a bare Ubuntu shell.
3. **`cygpath -w` for TMP/TEMP (line 32). No change.** Already
   falls back (`2>/dev/null || echo "$TMPDIR"`); on Linux
   cygpath is absent and the POSIX path is used verbatim -
   exactly what Linux gcc wants.
4. **`.exe` output names (probe.exe, msf_runner.exe, the
   tininess runner, aug_exhaustive.exe). No change.** On
   Linux, `gcc -o name.exe` writes an ELF with the exec bit
   and every invocation is by explicit path; the extension
   is cosmetic to exec. Inspected, not Linux-runnable here;
   the first CI run is the proof.
5. **dumpmachine pattern `x86_64-*` (line 56). No change.**
   Ubuntu gcc reports `x86_64-linux-gnu` and passes. The
   check still refuses i386 and would refuse an aarch64
   runner by design (SF-0 pinned x86-64 path); ubuntu-latest
   is x86_64, and a future arm64 runner would fail loudly,
   never silently pass.
6. **x87 control / FLT_EVAL_METHOD probe (lines 57-62). No
   change.** The compiled probe refuses any host compiler
   with `__FLT_EVAL_METHOD__ != 0`; x86_64 Linux uses SSE2,
   so it prints 0 and passes. Items 5+6 are the substantive
   x87 refusals and both run on Linux.
7. **x87 negative control hardcodes
   `/c/msys64/mingw32/bin/gcc` (line 214). No change.** On
   Ubuntu that path is absent, so the control prints its
   designed `SKIP-BY-NAME /c/msys64/mingw32 absent on this
   host` line - the same line a Windows host without the
   32-bit toolchain prints. This is the one control that
   will read SKIP on Ubuntu; it was watched refusing here
   (`control x87-compiler-refusal: refused as required` in
   both standard runs) and the refusals it demonstrates
   (items 5, 6) still execute in CI. No verdict that can
   FAIL became a pass.
8. **Exec tricks / `$BASH` delegation (board/bench only,
   lines 284/287). No change.** CI runs only smoke/standard;
   board and bench need the physical RP2040 and stay
   lead-run. The `#!/usr/bin/env bash` shebang is fine on
   Linux and CI invokes `bash tools/run.sh` explicitly, so
   the file's exec bit is irrelevant either way.
9. **`${ARM_CC%gcc}nm` (line 98). No change.**
   `arm-none-eabi-nm` ships in binutils-arm-none-eabi, a hard
   Depends of Ubuntu's gcc-arm-none-eabi. The workflow's
   inventory step runs `arm-none-eabi-nm --version`, so a
   missing nm fails the job instead of producing an empty
   symbol list.
10. **symbol_scan SKIP-BY-NAME if ARM compiler absent (lines
    87-90). No gate change; CI closes the hole.** The
    workflow installs gcc-arm-none-eabi and the inventory
    step runs `arm-none-eabi-gcc --version` before the gate,
    so on Ubuntu the scan cannot silently skip: a missing
    ARM toolchain fails the inventory step first.
11. **GNU userland (sha256sum, cmp, sort, grep -E/-w, sed,
    awk, wc, head/tail, date). No change.** All in the
    Ubuntu base install. One nuance: Ubuntu's default awk
    is mawk, this host's is gawk; the scripts use POSIX awk
    only (field assignment, `-F '\t'`, printf, one-dim
    arrays) - inspected; a residual risk below.
12. **Generators (tools/gen_tables.py,
    tests/gen_vectors.py). No change (not owned files).**
    gen_tables.py writes via `write_bytes(text.encode(
    "utf-8"))`, so regenerated files are LF-byte-identical
    on both OSes and the drift `cmp` holds. gen_vectors.py
    uses `write_text` (CRLF on Windows, LF on Linux) but
    only for build-dir vectors with no manifest over them;
    the runner already accepts the CRLF form (Windows
    standard passes), so Linux LF is the safe side. Both
    are stdlib-only (fractions, random, pathlib, sys): CI
    needs no pip step. The seeded pack64 sweep is generated
    and verified inside the same run, so even a CPython
    version wobble could change sweep content but not
    verdict validity.
13. **tests/aug_exhaustive.c `windows.h` /
    SetPriorityClass (lines 35-37, 329-330). No change.**
    Both are `#ifdef _WIN32`-guarded (inspected);
    `unsigned __int128` is GCC x86_64 on both platforms.
14. **No `-lm` on host links. No change.** MinGW folds libm
    into its runtime and glibc does not, but nothing in the
    host build references libm: no math.h anywhere in src/,
    include/ or the host test files (inspected includes).
15. **Line endings. No change.** `.gitattributes` is
    `* -text`, so checkout bytes on Ubuntu equal this
    host's. New/edited files verified LF-only (CRLF count 0
    in ci.yml and run.sh).

## Acceptance evidence

(a) **standard PASS on this Windows host after edits,
byte-for-byte same verdicts.** Runs via Git Bash with
MSF_PYTHON pinned to the workspace `.venv` (Python 3.12.15),
machine under other wave load. Baseline (pre-edit) standard:
PASS in 62 s. Post-edit standard: PASS in 60 s. Normalized
outputs (date line removed, elapsed seconds normalized) are
byte-identical: `cmp` clean, 9169 bytes each
(`scratch/parcel-w6ci/gate-*-standard.summary`, full logs
beside them). Shared measured lines: drift check 4 files
byte-identical; committed vectors `total 411213 passed
411213 failed 0`; standard-generated `total 1117504 passed
1117504 failed 0`; inventory `tier1 783 implemented of 783;
tier2 66 implemented, 0 planned, 66 registered; bad rows 0`;
manifest 66 entries all match; all negative controls
refused including x87. Post-edit smoke also run separately:
PASS in 26 s. Workflow artifact globs resolve against real
output (23 files under build/smoke matched locally).

(b) **YAML parses; commands - local vs CI-only.** Checker:
PyYAML 6.0.3 (`yaml.safe_load`), installed into
`scratch/parcel-w6ci/pylibs` only (shared .venv untouched).
Parse OK: triggers pull_request/push/workflow_dispatch, two
jobs as designed (PyYAML reads the bare `on:` key as True
per YAML 1.1 - the same shape pages.yml already ships).
Run locally in equivalent form: the toolchain-inventory
commands (host outputs: gcc 16.1.0 x86_64-w64-mingw32,
arm-none-eabi-gcc 14.2.1, nm 2.43.1) and both gate commands
(`bash tools/run.sh smoke|standard` with MSF_PYTHON pinned
to the .venv interpreter instead of python3). CI-only,
never run here: actions/checkout@v4 and
actions/upload-artifact@v4 (marketplace actions), and the
apt-get install line (no apt on this host). The Linux sides
of the two run.sh guards are likewise CI-only proof (items
1, 2, 4).

(c) **What a green run will show, and what could still
differ on Ubuntu.** Green: both jobs complete; job logs
carry the full gate inventory before verdicts (host compiler
`x86_64-linux-gnu` with FLT_EVAL_METHOD=0, drift 4 files
identical, the same 411213 committed-vector total, symbol
scan clean with its target-compiler line, negative controls
all refused except the x87 SKIP-BY-NAME line named above),
ending `budget smoke: PASS` / `budget standard: PASS`
(plus the 1117504 generated-vector total in standard);
artifacts `smoke-logs` and `standard-logs` attached. Named
risks, in order: (i) **package versions are the risk** -
ubuntu-latest (24.04 today) brings gcc 13.x, Python 3.12,
gcc-arm-none-eabi 13.2, versus this host's gcc 16.1.0 / Arm
GNU 14.2.1; under `-Werror` a warning that exists on either
side only can red a build with no library change; (ii)
ubuntu-latest floats - the next LTS migration changes every
version at once (pin to ubuntu-24.04 later if that churn
bites); (iii) package names: the brief's three packages are
installed plus `libc6-dev`, named explicitly because `gcc`
only Recommends it and the runner image merely happens to
preinstall it; (iv) mawk vs gawk (item 11); (v) first-run
proof still owed for the .exe-named ELF execution and the
two guards' Linux branches; (vi) apt-get update network
flakiness (ordinary CI weather). None of these can produce
a false green: every one fails a step loudly or prints a
named skip in the inventory.

## For the lead at review

Push branch `wave6-ci` to trigger: the push event fires
both jobs. Judge the run by the inventory lines above, not
the green tick alone. If the only surprise is the x87
SKIP-BY-NAME line, that is the expected Ubuntu shape.
Scratch: `scratch/parcel-w6ci/` (run-gate.sh,
toolchain-equiv.sh, check_yaml.py, append_brief_row.py,
gate logs + summaries, pylibs/, commit-msg.txt, this
report). Ledger: `ledger/parcel-w6ci.md`.

## Revision round: CRLF $NF control failure on Ubuntu

**What happened.** The lead pushed `wave6-ci`; first Ubuntu
Actions run 41052508849: all 411,213 vectors PASS, type/
symbol/target clean, exactly one negative control NOT
refused: wrong-nan-expectation (control 2). Cause (lead
diagnosis, re-measured here): `tests/vectors/encodings-
f32.vec` is fully CRLF (2353/2353 lines). The control's
awk matched `$NF=="exact-py:directed-encodings"`; on Linux
the CR stays attached to $NF, so nothing matched,
nanpol.vec was unmutated, and the runner passed it. MSYS
text mode masked this on Windows. My original inventory
item 15 ("line endings: no change") verified only that
checkout bytes are identical across OSes - true, but the
wrong property: identical bytes are *parsed* differently
by awk once text mode is absent. Item 11's mawk/gawk note
was looking at the wrong layer; the failure is awk-input
bytes, not awk dialect.

**Fix (commit `5b53bf3db94100b401eb6f7bef516472d9d28dc1`
on `wave6-ci`, not pushed; `tools/run.sh` only, +11/-3,
still LF-only).** Two patterns now handle the last field
CR-stripped *on a copy* -
`t=$NF; if (substr(t,length(t))=="\r") t=substr(t,1,length(t)-1)` -
pure substr/length string ops (no regex escape whose
reading could differ between gawk and Ubuntu's mawk) and
no field assignment, so records awk does not mutate print
byte-identically, CRLFs included. What each site checks is
unchanged.

1. Control 2 (line 186): compare uses the stripped copy
   `t`. Same target line, same flip.
2. `write_expect_counts` first stage (line 130): tags
   printed from the stripped copy (see audit item A -
   the one other real instance).

**Per-pattern audit** (every awk/sed in tools/run.sh;
line numbers post-revision; input endings measured
byte-wise this round - `rev_audit_probe.py` /
`rev-audit-probe.txt`):

- **A. L130 write_expect_counts `{print $NF}` -> FIXED.**
  Inputs are all 51 $VECS: 12 fully CRLF, 39 fully LF, 0
  mixed. Under Linux semantics 41,871 of 411,213 tags
  (10 distinct tags) carried a trailing CR into the
  sort/uniq pipeline and thence into expect.txt as
  `tag<CR> count`. Benign on the first Ubuntu run only by
  two accidents: no provenance tag spans CRLF and LF
  files today (measured 0 split of 77 tags), and the
  runner parses expect.txt with `sscanf "%63s %lu"`
  (tests/runner.c:685) where %s stops at CR as whitespace.
  A future LF file reusing a CRLF-file tag would have
  produced two expect lines for one tag, each failing
  against the runner's combined count - a false red, and
  expect.txt bytes differing by OS. Now the first-stage
  output is byte-identical on both OS channels (proved
  below) and identical to the old Windows output. The
  second awk on the same line (`{print $2,$1}` over
  uniq -c output) needed no change: with the first stage
  fixed, no CR enters the pipe.
- **B. L151 inventory_check (awk -F tab, header-named
  columns). No fix - not a real instance.** Input
  docs/COVERAGE.tsv is LF-only (856 lines, 0 CRLF) by
  construction: generated by tools/gen_tables.py via
  `write_bytes` (line 624), so its bytes are LF on every
  OS, and the drift check would refuse a CRLF copy before
  inventory ever ran. The only $NF-touching column is
  claim (col 14 of 14); tier/status are interior ($13,
  $9). Even hypothetically CRLF, the failure direction is
  loud: the header name would register as `claim<CR>`,
  every claim compare would count bad rows, and the
  tier-inventory control would go NOT REFUSED -> gate
  FAIL. It cannot silently pass.
- **C. L177 control 1 (corrupted-expected-bit). Safe.**
  Input encodings-f16.vec is fully CRLF (2353/2353), but
  the patterns are a start-anchored regex
  (`/^msf16_is_signaling/`) and interior fields ($i=="->",
  result at $(i+1), which precedes the `--` and tag). The
  CR rides only on $NF, never compared. Refused on
  Ubuntu run 41052508849 as independent confirmation.
- **D. L186 control 2 (wrong-nan-expectation). THE bug -
  FIXED (above).**
- **E. L191 control 3 (wrong-rounding-mode). Safe.**
  pack64.vec fully CRLF (6271/6271); patterns touch $1/$2
  only. Refused on Ubuntu.
- **F. L197 control 3b (te<->ta). Safe twice over.**
  arith-f32.vec is LF-only (4241 lines, 0 CRLF) and the
  pattern touches $2 only. Refused on Ubuntu.
- **G. L202 control 4 (wrong-flag-bit). Safe.** pack64.vec
  CRLF, but the patterns are $1 and $(NF-1): the CR
  attaches to $NF without changing NF, so NF-1 is the
  same flags field on both OSes. Refused on Ubuntu.
- **H. L207 control 5 (sed '1s/^./0/'). Safe.** Input is
  the same-run generated manifest.txt (sha256sum output,
  LF on Linux). The substitution is start-anchored on
  line 1 - immune to any line ending. One of the
  controls that did refuse on Ubuntu.
- **I. L211 control 6 (`$2=$2+1` on expect.txt). Safe.**
  Input is same-run generated by awk print (LF), and $2
  is consumed by numeric coercion (`$2+1`), which parses
  the leading number even if a CR trailed - it cannot
  miss the way a string equality does. With fix A the
  file is CR-free everywhere anyway.
- **J. L231/232/235 control 9 tier listing + two COVERAGE
  mutants (awk -F tab). Safe.** Same LF-by-construction
  input as B; comparisons are $1/$9/$13, all interior
  (NF=14 on every data row, measured). A CR could only
  ever sit in $14 (claim), which none of these compare.
  Both mutants were refused on Ubuntu.

Also swept (not awk/sed): every grep refusal check in
run.sh is a substring or start-anchored match
(`VERDICT: FAIL`, `^FAIL`, `MANIFEST MISMATCH`,
`COUNT MISMATCH`) - a trailing CR cannot defeat any of
them. The runner itself tokenises with C whitespace
(CR included), which is why the 411,213 committed vectors
- including the 12 CRLF files - verified identically on
Ubuntu.

**Proof (all this round, scripts in scratch/parcel-w6ci/,
Git Bash, MSF_PYTHON = workspace .venv).**

1. **Windows standard still PASSes, byte-for-byte same
   verdicts.** `run-gate.sh rev1 standard`: PASS in 56 s;
   log carries `control wrong-nan-expectation: refused as
   required` and all other controls refused; 411,213
   committed + 1,117,504 generated vectors, 0 failed;
   expect-counts 77 provenance tags (== the 77 distinct
   CR-stripped tags in the probe); gate-produced
   nanpol.vec line 1024 flipped to `-> 1`, runner
   FAILs exactly that line (2351 passed / 1 failed);
   expect.txt contains 0 CR bytes. Normalised summary
   `gate-rev1-standard.summary` is byte-identical (cmp
   clean) to the pre-revision `gate-after-standard.summary`.
2. **Linux semantics without MSYS text mode**
   (`rev_linux_semantics.sh` -> `rev-linux-semantics.txt`;
   byte compares by `rev_byte_diff.py`). Method: GNU
   awk `BINMODE=3` forces binary input+output - text
   translation off, which is exactly Linux awk behaviour
   (no text mode; CR is an ordinary byte). Used the
   gate's own awk, /c/msys64/usr/bin/awk (gawk 5.4.0).
   Channel check on line 1024: default mode
   `length($NF)=27` (CR silently eaten - the masking),
   BINMODE=3 `length($NF)=28` (CR present). Program
   texts verified verbatim against run.sh (new) and
   `eda5812:tools/run.sh` (old) by grep -F before use.
   Results through the BINMODE=3 channel:
   - OLD program: output **byte-identical to the input**
     (150,556 bytes; 0 differing byte positions, 0
     differing lines) - the Ubuntu failure reproduced
     on this host.
   - NEW program: exactly **1 differing byte** (offset
     64,779: `0` -> `1`), exactly 1 differing line -
     line 1024 `msf32_class - 7f800001 -> 0 -- exact-py:directed-encodings<CR>`
     becomes `... -> 1 -- ...<CR>` - same total length,
     all 2,353 CRLFs preserved. Under the Windows
     text-mode channel the same NEW program flips the
     same line: identical mutation on both OSes.
   - Tag first stage over all 51 $VECS: OLD under Linux
     channel emits 41,871 CR-terminated tags of 411,213;
     NEW emits 0 CRs with the same tag multiset; NEW
     output is **byte-identical across the Windows and
     Linux channels** (cmp), and OLD==NEW on the Windows
     channel (cmp), so Windows behaviour is unchanged.
3. **Committed, not pushed.** `5b53bf3` on wave6-ci,
   detailed body + Co-Authored-By trailer; tools/run.sh
   only (+11/-3), CRLF count in run.sh still 0, metrics
   untouched per lead instruction. The lead re-pushes
   and watches Actions; the remaining unproven-in-advance
   item is only mawk executing the new substr idiom on
   Ubuntu (pure POSIX string ops chosen precisely to
   minimise that risk; the re-run is the proof, and any
   surprise there fails loud as a NOT REFUSED control,
   never a false green).

**For the lead at re-push:** expect the same inventory as
run 41052508849 plus `control wrong-nan-expectation:
refused as required` and `negative controls: all refused`
(the x87 SKIP-BY-NAME remains the designed Ubuntu shape).
Revision scratch: rev_audit_probe.py, rev_probe_awk.sh,
rev_linux_semantics.sh, rev_byte_diff.py, rev-*.txt,
rev-nanpol-*.vec, rev-tags-*.txt, rev-commit-msg.txt,
gate-rev1-standard.{log,summary}.
