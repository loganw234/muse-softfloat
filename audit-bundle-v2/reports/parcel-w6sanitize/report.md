# parcel-w6sanitize: the `sanitize` budget (Wave 6 queue item 3)

Brief: `ledger/briefs/w6-sanitize.md`. Authority (read in full):
`scratch/study-w6sanitize/report.md` - its S1+S3 shapes are what
shipped; S2 (MSVC script) untouched. Base
`537b08edce17112da8f84353abcb2c693f2a5e65`, branch
`wave6-sanitize` in `worktrees/w6-sanitize`, tip
`1bc097977e44f86be4d3c984bbaf19ca8225fd63` (one commit, **not
pushed** - the lead pushes to prove the CI job, acceptance (d)).

## What shipped (owned files only)

- `tools/run.sh` (+169/-6): fifth budget `sanitize`.
  - `MSF_SANITIZE` = `trap` (default; `-fsanitize=undefined
    -fsanitize-undefined-trap-on-error
    -fno-sanitize-recover=all`) or `full`
    (`-fsanitize=address,undefined -fno-sanitize-recover=all`,
    `ASAN_OPTIONS=halt_on_error=1`,
    `UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1` exported
    with caller values respected via `:-`).
  - `MSF_SANITIZE` with any other budget is REFUSED by name
    (exit 2) and a bogus flavour likewise - the merge gate can
    never be silently re-flavoured; unset, other budgets are
    byte-for-byte as before (incl. `build_host`'s id: the flavour
    suffix `-trapubsan`/`-asanubsan` only exists inside sanitize).
  - Seam exactly as the study prescribed: flags flow through
    `build_host` and the aug harness build; the
    `check_host_compiler` probe stays plain; ARM objects never
    see them (no symbol scan in this budget - named in the
    inventory as not-in-budget). Artifacts in
    `build/sanitize-<flavour>/`.
  - Sets: canaries, unit, committed VECS per-file (51
    invocations, so a bare trap names its file) then all-files
    with manifest+expect-counts, standard extras
    (f16-exhaustive + pack-sweep), aug pool, smoke control 1 on
    the sanitized twin. Inventory (flavour, flags, seam, sets,
    trap boundaries) prints before any result.
  - SKIP semantics (decided here, brief (c)): if the clean
    canary will not link and the error names the sanitizer
    runtime, the budget prints `SKIP-BY-NAME`, runs no sets,
    claims **no** zero-findings, prints **no PASS verdict**,
    and exits 0 (house SKIP-BY-NAME precedent: symbol scan,
    control 8). Any other clean-canary failure FAILs. The lead
    judging the CI run must therefore look for `budget
    sanitize: PASS`, not the job tick alone - said in the
    ledger too.
- `tests/sanitize_canary_{clean,ub,ub_shift,heap,heap_far}.c`
  (new, canaries only): clean must exit 0; ub/ub_shift/heap
  must be caught under the active flavour or the budget FAILs
  before any set runs; heap_far (size lost across a call) is
  required-caught under `full` and printed NOT CAUGHT under
  `trap` with the boundary spelled out.
- `.github/workflows/ci.yml` (+39/-): additive `sanitize` job,
  ubuntu-latest, 30 min, `MSF_PYTHON=python3 MSF_SANITIZE=full
  bash tools/run.sh sanitize`, same install/inventory/artifact
  shape as smoke/standard (which are byte-untouched apart from
  the header comment). YAML parsed with PyYAML 6.0.3
  (scratch-only `pip --target` install): jobs =
  sanitize/smoke/standard, gate command as above.
- `AGENTS.md` (budget list only) + run.sh header: `sanitize`
  with measured cost ~44-56 s (2026-10-30, this host, trap).
- `docs/metrics/briefs.jsonl`: own wave6 row by binary append
  (13504 -> 14264 B, prefix intact verified in-process; the
  file's 5 pre-existing CRLF lines left byte-identical).

## Acceptance probes (all actually ran; logs in logs/)

- (a) trap: `bash tools/run.sh sanitize` PASS - three full
  runs (56 s, 44 s, 56 s final tree). Canaries: clean exit 0;
  ub, ub_shift, heap caught exit 132 (Illegal instruction);
  heap_far NOT CAUGHT printed as the known boundary. Totals:
  unit PASS; `total 411213 passed 411213 failed 0`;
  `total 1117504 passed 1117504 failed 0`;
  `aug_exhaustive pool: total=5505024 mismatches=0`; corrupt
  control refused on the sanitized twin. Zero findings, as
  the study measured - and meaningful: the unsanitized ub
  canary exits 0 (`UB-RESULT -2147483648`), so the traps are
  the instrumentation firing, not the programs.
- (b) standard: PASS before any edit (56 s) and twice after
  (55 s, 57 s final tree); normalized outputs byte-identical
  (9169 bytes, date + elapsed-seconds normalized away;
  `scripts/normalize_compare.py`).
- (c) full on this host: `MSF_SANITIZE=full` -> SKIP-BY-NAME
  in 1 s, exit 0, no PASS, log shows `cannot find -lasan` /
  `cannot find -lubsan` and "zero findings NOT claimed"
  (`logs/sanitize-full-host.log`).
- Negative probes (`scripts/negative_probes.sh`): MSF_SANITIZE
  with standard refused (exit 2), bogus flavour refused,
  usage names sanitize. v1 of that script was itself bitten
  by the documented Git-Bash->MSYS2 `MSF_*` env drop (bare
  `bash` resolved to MSYS2 through an MSYS2-first PATH);
  v2 invokes `$BASH` like run.sh's board delegation. The v1
  accident doubles as evidence the unset path is untouched.
- Memory: sanitized runner peak working set 3.9 MB committed
  verify / 3.7 MB extras / 3.6 MB aug (study method,
  `scripts/peak.py`; study trap figure 4.0 MB) - three orders
  under the 4 GB ceiling. Cost: 44-56 s wall per trap run.

## Where the tree disagreed with the study

Nothing material. The study's line numbers predate w6-ci's two
portability guards; the seams it named (`build_host`, the aug
build, the l.55 probe to avoid) are exactly where it said,
shifted by a few lines. Study S2 (MSVC ASan leg) not built -
out of scope per brief; `full` in CI covers real ASan.

## Unresolved / for the lead

- (d) Push `wave6-sanitize` and prove the `sanitize` CI job:
  expected `budget sanitize: PASS` with canaries caught incl.
  heap_far, totals 411213 + 1117504 + 5505024 under flavour
  full. Ubuntu gcc must link -lasan/-lubsan via the existing
  apt line; if not, the job will say SKIP-BY-NAME loudly (exit
  0) rather than PASS - judge by the line, not the tick.
- `full` has never run anywhere yet (this host cannot link
  it); the first CI run is its first live-fire test, canaries
  included by design.
- No real sanitizer finding occurred anywhere, so the STOP
  path (per-file naming + fail) is wired but unexercised
  against library code; it is exercised against canaries.

## Evidence index (scratch/parcel-w6sanitize/)

- logs: standard-before.log, sanitize-trap.log,
  sanitize-full-host.log, sanitize-trap-final.log,
  standard-after.log, standard-final.log (+.norm pairs),
  peak.log, neg/ (v1 probes), neg2/ (v2), ub-plain-probe.log
- scripts: run_budget.sh, run_sanitize_flavour.sh,
  peak.py, normalize_compare.py, negative_probes.sh,
  ub_plain_probe.sh, append_metrics.py, check_yaml.py,
  check_lf.py, commit.sh; commit-msg.txt
- pylibs/: scratch-only PyYAML (not in repo, not in .venv)

Nothing with `cft` in its name was opened, searched, or
listed. No other worktree, no main checkout, no board, no
push touched.

## Revision round (CI run 41061712195): strncpy idiom fix

Lead pushed 1bc0979; CI smoke+standard passed; sanitize job
FAILED at the host build step (not a sanitizer finding: all
four canaries caught under full ASan+UBSan first). gcc 15
x86_64-linux-gnu with the sanitizer flags + project -Werror
promoted -Wstringop-truncation at tests/runner.c:477
`strncpy(raw, line, sizeof(raw) - 1u)` -> `RUN.SH: FAIL -
host build failed`. Fix committed as
`77e6e647cac519a35975b1adadecfb157e0c93b5` on wave6-sanitize
(**not pushed**; lead re-pushes for the live CI proof).
Owned files expanded for exactly this one hunk in
tests/runner.c (+6/-2); nothing else in runner.c touched:

    {
        const char *nul = memchr(line, '\0', sizeof(raw) - 1u);
        size_t n = nul ? (size_t)(nul - line) : sizeof(raw) - 1u;
        memcpy(raw, line, n);
        memset(raw + n, 0, sizeof(raw) - n);
    }

Spelling note (deviation from the briefed `strnlen`, stated
for the lead): n above is exactly `strnlen(line,
sizeof(raw)-1)`. It is spelled with memchr because strnlen
is POSIX.1-2008 - glibc declares it only with
_POSIX_C_SOURCE >= 200809L, so under the project's
-std=c11 -Werror it would be an implicit declaration (hard
error on gcc >= 14) on the very Linux build being fixed,
and the feature-test macro would need a top-of-file edit
outside this hunk. memchr/memcpy/memset are ISO C11. Host
MinGW *does* declare strnlen under -std=c11 (probed,
scripts/strnlen_probe.*) - that decides nothing for glibc.

Byte-equivalence (all uses of raw read first): raw[4096] is
written once in process_line, then passed only as
const char* to fail_line / process_pack_line /
process_char_line / process_pair_line; the helpers forward
it only to fail_line, whose sole read is printf("%s", raw).
No hashing/measuring/memcmp of raw anywhere, so only bytes
up to the first NUL are observable - but all 4096 bytes are
identical anyway. L=strlen(line): L<4095 - old copies L
bytes, zero-pads to 4095, forces raw[4095]=0; new copies L,
zero-fills [L,4096). L>=4095 (incl. the >=4095-char case) -
old copies line[0..4094] (count exhausted) + forced NUL;
new finds no NUL in bound, n=4095, copies 4095, 1-byte
memset. So strncpy's zero-padding is fully reproduced, not
just the first NUL. Only caller is process_file
fgets(buf[4096]), so in practice L<=4095 and a physical
line >=4095 chars arrives as successive 4095-char chunks;
L>4095 remains byte-identical regardless. Empirically
proven: scripts/equiv_probe.c full-4096 memcmp (buffers
poisoned 0xA5) old vs new identical for L in
0,1,2,63,4093,4094,4095,4096,4097,5000,8190, embedded-NUL,
typical line - `EQUIV PASS fails=0` (logs/rev/equiv.log).

Proof (Git Bash, MSF_PYTHON=.venv; logs in logs/):
- (1) standard PASS 54 s (`budget standard: PASS`);
  normalized verdict surface vs pre-revision
  standard-final.log: `before bytes=9169 after bytes=9169
  identical=True`.
- (2) sanitize trap PASS 52 s, zero findings: canaries
  clean exit 0; ub/ub_shift/heap caught exit 132; heap_far
  NOT CAUGHT printed (trap boundary, as before); unit PASS;
  total 411213 + 1117504; aug 5505024 mismatches=0;
  `budget sanitize: PASS` (logs/rev-sanitize-trap.log).
- (3) Warning class gone as far as this host can show
  (scripts/rev_probes.sh, logs/rev/): build_host-shaped
  one-shot build with full SANFLAGS
  (-fsanitize=address,undefined -fno-sanitize-recover=all)
  + project CFLAGS over tests/runner.c + library: NO
  compile diagnostics; fails only at link, `cannot find
  -lasan` / `cannot find -lubsan` - i.e. compilation passed
  the former warning point. Compile-only (-c) runner.c
  under same flags rc=0 (object 1002447 B); explicit
  -Werror=stringop-truncation compile-only rc=0 plain and
  full. NOT claimed: a full-flavour run (no sanitizer
  runtime on this host) - first live proof remains CI on
  the lead's re-push.
- (4) Committed 77e6e64 (detailed body + Co-Authored-By
  Muse Code (muse-wonder-full-1.0)); working tree clean;
  not pushed.

Revision evidence index: logs/rev-standard.log (+.norm
pair), logs/rev-sanitize-trap.log, logs/rev-probes.out,
logs/rev/{equiv,fullflags-build,fullflags-compileonly,
plain-stringop,full-stringop,strnlen-probe}.log;
scripts/{equiv_probe.c,rev_probes.sh,strnlen_probe.c,
strnlen_probe.sh,commit_rev.sh}; commit-msg-rev.txt.
Nothing with `cft` in its name touched.
