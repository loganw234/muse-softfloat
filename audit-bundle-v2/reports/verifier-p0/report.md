# verifier-p0 report (muse-spark-1.3) — SF-0 Section 6 P0 acceptance

Target: `23a740f0d5d39f5bc0375a9537faf4ea877c6280` (parent `0bfa964` pushed).
Workspace `C:\Users\logan\source\repos\Muse-Softfloat`, repo `muse-softfloat/`.
Stance: disconfirm only; project files untouched (all probes/scripts under
`scratch/verifier-p0/`; gate re-runs only rewrote git-ignored `build/` logs).
Tree was clean at start (`git status --porcelain` empty) and is clean at end.
Machine was under third-party load throughout (owner notice); timings noted.

Read first: `muse-softfloat/docs/studies/SF-0.md` sections 2–6.
Acceptance text (SF-0 Section 6 last paragraph, verbatim):

> P0 acceptance (its own verifier, Spark): the runner refuses each named
> negative control; generated files regenerate byte-identically; the
> symbol scan is clean; board smoke hashes match host; the interposition
> hello and Section 3.4 wrapper-state tests pass; every Wave 1 brief can
> name its owned files without overlap.

## 1. Regeneration + independent recount — HOLD

Commands:

- `python muse-softfloat/tools/gen_tables.py scratch/verifier-p0/gen-check`
  output: `wrote include/muse_softfloat.h (115270 bytes)`,
  `wrote src/msf_formats.h (1836 bytes)`,
  `wrote tests/msf_dispatch.h (121392 bytes)`,
  `wrote docs/COVERAGE.tsv (112176 bytes)`,
  `instantiations: 783 (implemented 63)`.
- SHA-256 compare of each file vs the tree: **4/4 IDENTICAL**
  (`include/muse_softfloat.h`, `src/msf_formats.h`,
  `tests/msf_dispatch.h`, `docs/COVERAGE.tsv`).
- Independent recount (`scratch/verifier-p0/recount.py`, hand-written
  per-sig expansion counts, no `gen_tables.py` logic):
  **81 families, 783 instantiations, 63 implemented** from 24 implemented
  families (copy/negate/abs/copy_sign/class/9 predicates/radix/
  3 global versions/6 flag ops), **0 `authority=unconfirmed`** in
  `docs/COVERAGE.tsv` (783 rows). Authority split:
  mpfr-exact 327, berkeley 180, project-exact 165,
  project-exact+berkeley-check 111. Status: planned 720, implemented 63.
- Signature spot-checks vs SF-0 3.3 (exact lines in
  `include/muse_softfloat.h`):
  `msf64_add(msf64_t a, msf64_t b, msf_rounding_t rm, msf_flags_t *flags)`
  line 229;
  `msf32_add_f64_f64(msf64_t a, msf64_t b, ...)` line 211;
  `msf64_fma_f32_f32_f64(msf32_t a, msf32_t b, msf64_t c, ...)` line 547.
  Spellings match the SF-0 3.3 rule (destination first, sources appended).
- Dispatch audit (`scratch/verifier-p0/dispatch_audit.py` over
  `tests/msf_dispatch.h` + `nm` of a host build):
  783 rows; all 63 status=1 rows bind `(void *)<same-name>` and every name
  resolves in `build/smoke/msf_runner.exe`; all 720 status=0 rows carry
  fn `0` (NULL). Zero inconsistencies.

## 2. Gates re-run + controls + runner attacks — HOLD

- `tools/run.sh smoke` (Git Bash, 2026-10-26 ~19:20): **PASS in 8 s**.
  `total 17662 passed 17662 failed 0 malformed 0 skipped-planned 0`,
  provenance exact-py:directed-encodings 7056,
  exact-py:copysign-sample 4336, exact-py:pack64-directed 6270.
  Type scan clean; target compiler Arm GNU 14.2.1; symbol scan clean
  (7 undefined: `__aeabi_lmul`, `__gnu_thumb1_case_uqi`, five `msf_u128_*`
  own symbols — no float helpers, no malloc/printf).
- `tools/run.sh standard`: **PASS in 33 s**.
  `f16-exhaustive.vec` 917504 + `pack-sweep.vec` 200000 =
  `total 1117504 passed 1117504 failed 0`, with the
  `dropped 37821 non-invariant cases` line the RECORD quotes (37,821).
- 8 negative controls independently confirmed refused from the fresh
  `build/smoke/controls/*.log` (my run, not the lead's):
  1. corrupted-expected-bit: `total 2352 passed 2351 failed 1 ... FAIL`;
  2. wrong-nan-expectation: `passed 2351 failed 1 ... FAIL`;
  3. wrong-rounding-mode: `passed 5414 failed 856 ... FAIL`;
  4. wrong-flag-bit: `passed 6269 failed 1 ... FAIL`;
  5. stale-manifest: `MANIFEST MISMATCH for *src/msf16.c (want 0c82... got 1c82...) - refusing`, VERDICT: FAIL;
  6. count-mismatch: three `COUNT MISMATCH` lines, VERDICT: FAIL;
  7. wrong-tininess-polarity: 66 `^FAIL` lines in `tininess.log`, nonzero exit;
  8. x87-compiler-refusal: `compiler REFUSED: .../mingw32/bin/gcc dumpmachine=i686-w64-mingw32 (need x86_64-*)`.
- Own runner attacks (`scratch/verifier-p0/attacks/`, fresh
  `build/smoke/msf_runner.exe`, unpiped exit code 1 on FAIL verified):
  1. my-corrupt.vec → `VERDICT: FAIL` (got/want printed);
  2. my-wrongflag.vec → `VERDICT: FAIL` (bits ok, `00` vs `01` flagged);
  3. my-unknownop.vec → `unknown op`, malformed 1, `VERDICT: FAIL`;
  4. my-plannedop.vec (`msf64_add`) → `SKIP ... msf64_add not implemented
     (planned wave 1)`, passed 0, skipped-planned 1. NOTE: the file-level
     verdict reads `PASS` (nothing failed); the line itself never passes
     and is named. Gate-level `--expect-counts` guards smuggling.
  5. my-empty.vec → `VERDICT: FAIL (no vectors ran)`.

## 3. Round-and-pack disproof — HOLD (no class-b found)

Own reference `scratch/verifier-p0/pack_disproof.py` (Fractions only;
`tests/gen_vectors.py` never read; contract from `msf_internal.h`,
`msf_formats.h`, IEEE rules). Own probe `vpack_probe.c` compiled with the
pinned path (`x86_64-w64-mingw32 gcc 16.1.0`, `-ffp-contract=off`).

- Directed: smallest-normal boundary both sides × 5 modes × 2 signs
  (exact `2^-1022`, largest subnormal, half-ulp-below tie, just-above with
  sticky, ±1 ulp), exact ties (`2^52±0.5`, `2^52+1.5`, ±, tie+sticky),
  overflow deliveries ± (`2^1024-2^970`, exact `2^1024`, exact maxfinite,
  just above maxfinite), exact subnormals, round-to-zero basics, huge/tiny
  exponents (±2000, 128-bit-wide sigs), zero, sticky-sensitivity pairs.
- Plus 3000 seeded random cases (`seed 0xC10C`); sticky=1 sampled at three
  fractions; 69 f-sensitive (interval straddles a boundary — undecidable
  through a sticky bit by construction) skipped.
- Result: **3121 cases, 0 (bits,flags) mismatches.**
- `msf_u128` adversarial (`u128_disproof.py`, 5726 cases: 64-bit mul incl.
  `max*max`, shifts 0/1/31/32/63/64/95/96/97/126/127, jam × sticky 0/1,
  clz incl. 0/max): **0 mismatches** after correcting two of MY OWN oracle
  bugs (fed >u64 operands into the u64×u64 mul probe; expected jam-by-0 as
  identity where the documented Berkeley-style jam folds `sticky_in` into
  bit 0 — `msf_wide.c:160-165`, consistent on all n>0 cases). The mul
  carry-fold at `msf_wide.c:100` was hand-bounded safe (upper limbs still
  zero at write time) and the differential agrees.

## 4. Classification / sign / flags / version — HOLD

- Own exhaustive oracle (`gen_myf16.py`, field definitions only):
  all 65536 binary16 encodings × 16 lines (class, 9 predicates, copy,
  negate, abs, radix, 2 version preds) + 576 directed + 20000 seeded
  copysign pairs + 280 f32/f64 directed encodings + 3 global versions =
  **1,069,435 vectors, 1,069,435 passed, 0 failed** through the freshly
  built runner under my own provenance tags. Class order matches the
  header enum and S1's 5.7.2 order; `is_canonical` is 1 on all 65536
  patterns (SF-0 2.5: no non-canonical binary encodings); `is_signaling`
  = nan && !quiet-bit on all patterns.
- Flag ops (`vflag_probe.c` + `flag_disproof.py`, 1297 cases over
  adversarial state/group swatches incl. out-of-range bits 0x20/0xFF...):
  **0 mismatches** vs the ANY-of-group model with 5-bit masking.
  The lead's ANY reading was attacked against the survey extract and
  SURVIVED: `scratch/S1/extract/combined.txt:1749-1754` quotes the clause
  twice ("Queries whether **any** of the flags ... are raised", for both
  `testFlags` and `testSavedFlags`). Discriminators (`test 2 3` → 1,
  `test 10 1f` → 1, `test 0 1f` → 0) all agree ANY.
- Versions: global + all per-format predicates return 0/0/1 (1985/2008/
  2019) in the probe and the exhaustive run — matches SF-0 2.1.

## 5. Claims audit (RECORD.md P0 entry + commit message vs evidence)

- Hashes: `docs/metrics/fetches.jsonl` archive hashes recomputed from
  `scratch/oracles/SoftFloat-3e.zip` / `TestFloat-3e.zip`:
  `21130ce8...c746` and `6d4bdf00...aad6` — **exact match.**
- Counts: 783 / 63 (recount §1); 17662 (smoke re-run §2);
  1117504 = 917504 + 200000 (standard re-run §2, incl. the 37,821
  dropped non-invariant line); 968 (board `host-verify.log`:
  `total 968 passed 968`, provenance 798 directed-encodings + 170
  pack64-directed); 65728 (`probe_snan.exe` re-run live:
  `isSignaling cross-check: 65728 checked, 0 disagreements`;
  = 65536 + 96 + 96 per `probe_snan_xcheck.c`).
- Board claims: `replay.log` (COM8, banner ID `e66440a2cb6f5c2b`,
  `board: SHA256 4573ac09...f28a7 COUNT 968`, hash matches host,
  `board replay: PASS`) vs `host-hash.log`
  (`whole-run-sha256 4573ac098f2f8a5bf8c6b09fb9746ee206e24a3870c19b4b07f3dd3fee5f28a7`)
  — **exact match.** On-disk `build/board-fw/fw/`: harness UF2
  `987bb37b...`, ELF `020de7f9...`, hello UF2 `40e21e7c...` — all match
  the RECORD/BOARD.md prefixes. `run_board.sh:44-46` prints per-build
  artifact hashes every run (discipline holds in the script).
- hello 12/12: `hello.log` has exactly 12 `hello PASS` lines +
  `HELLO-RESULT PASS failures=0`; `board/hello_main.c` has exactly 12
  `CHECK(...)` (4 --wrap copysign bit-exactness incl. NaN payload
  `0x7fc00001`, 3 cross-core isolation, IRQ-hit + DIV0 sharing,
  3 save/restore round-trip) + the `sink=c4bae3d6 flags=12` note
  (`0x12` = DIV0|INEXACT, the contracted IRQ sharing). Mechanism and
  evidence agree line for line.
- Metrics: `scratch/lead/metrics-p0/{usage,passes}.jsonl` (26 rows each)
  sum to **848,844 out / 143,025,602 in** — exact match with RECORD.
  (Only `metrics-p0` read in `scratch/lead`; no keys touched.)
- Oracle pricing spot-checks from saved logs: level-1 binary slice 46,464
  (`tsf-f64_add.log`, 6 rounding slices clean), mulAdd level-1 6,133,248
  (`tsf-f64_mulAdd.log` header), conversion slice 768 (`tsf-f64_to_i32.log`),
  `testsoftfloat.log` clean (408/408). MPFR 4.2.2 re-ran live
  (`mpfr_probe.exe`: `sqrt(3)@200b=1.732050807568877293527446e0`).
  NOT re-run: level-2 40,284,288 streaming count + 81–97 s timing (no
  saved output log; `price-*.err` are empty stderr captures; scripts in
  `scratch/lead/oracle5.sh`/`oracle6.sh` reproduce it live).
- Bench skeleton: both flavours ran with placement/clock labels
  (`flash(xip,cached)`, 125 MHz), identical sinks `fc38e392e13b0fc8`,
  `note: skeleton only - no performance claim`. RECORD quotes no bench
  number. Item-9 discipline holds.
- Clean room: word-boundary grep over `src/ include/ compat/ board/`
  plus runner/generator sources finds NO Berkeley symbols (`f64_add`,
  `softfloat_`, Hauser/Berkeley/TestFloat as code) — only the word
  "Berkeley" in `gen_tables.py` authority-token comments (naming the
  oracle, not code). `float`/`double` words: none in `src/`/`include/`
  (the `-w` scan; `compat/msf_wrap.c` necessarily names C `float`/`double`
  in its memcpy bit-cast interposition signatures — outside the
  SF-0 3.2/5.3 core scan surface, by design). No home paths in
  `src/include/compat/tests/tools/tables`; `board/common.sh` carries
  `/c/Users/logan/pico/...` tool-path DEFAULTS (env-overridable) and
  `BOARD.md`/`HARNESS.md` name the machine — documentation, noted.
  `git ls-files` shows exactly the 50 committed files: no zips, PDFs,
  exes, ELFs, UF2s vendored. Oracle trees live only in `scratch/oracles/`.
  (Never opened/searched/listed anything with the fenced name pattern.)

## 6. SF-0 Section 6, nine items one by one

1. Study + AGENTS: `AGENTS.md` carries front door (run.sh + budgets +
   measured costs), authority (order, pins, Berkeley flag translation,
   clean-room rule), and discipline (SF-0 §5 gate paragraph) — all filled
   from SF-0 §§4–5. `README.md` status links approved `SF-0.md`. HOLD.
2. Operation table: machine-readable `tables/operations.tsv` (81 families)
   → header + dispatch + `COVERAGE.tsv`; drift refused in every budget
   (re-verified §1). HOLD.
3. Format generation: `tables/formats.tsv` (16/11/5, 32/24/8, 64/53/11,
   Pmin 5/9/17) → `msf_formats.h`; no hand-typed duplicates (all consumers
   use `MSF_F*` macros). HOLD.
4. Core exemplar + first ops: `msf_wide.c`, `msf_roundpack.c` (tininess
   AFTER rounding, wrong-polarity hook compiled and watched failing in
   control 7), classification/sign/radix/version via `msf_performat.inc`,
   six flag ops, `WIDTHS.md` proof notes. 63 implemented, rest declared +
   SKIP-by-name. No arithmetic claimed (README + RECORD say so). HOLD.
5. Oracle bring-up: pinned archives + hashes (§5), 8086-SSE build,
   `testsoftfloat` clean on 10 sampled functions, header coverage
   (`sf-functions.txt`: no nextUp/scaleB/logB/totalOrder/class/decimal,
   int conv 32/64-bit only — matches the authority map), streamed pricing
   (level-1/mulAdd/unary verified in logs; level-2 count/timing not
   re-logged — note above), Berkeley invalid-int + flag-order
   dispositions in header comment + `VECTORS.md`, 65728 cross-check
   reproduced, MPFR live. HOLD with the one logging note.
6. Runner + coverage + controls: budgets wired with
   inventory-before-verdict, replay, coverage ledger (0 unconfirmed),
   8/8 P0-applicable controls refused (§2). Remaining §5.2 controls
   (bootrom, board-identity, decimal-range, wrapper-leak-as-fault) arm
   with their surfaces per RECORD — the wrapper one is exercised as
   contract-observed sharing in hello. HOLD.
7. Board harness: CDC replay + whole-run hash (§5), unique ID two ways
   (picotool serial `E664...` in `flash.log`, firmware banner in
   `replay.log`/`hello.log`), hands-free `picotool load -f -x`,
   968-vector smoke on rev B2, 12/12 interposition hello incl. §3.4
   second-core/IRQ self-test (§5). Full-volume replay explicitly not
   promised and not claimed. HOLD. (Board not touched by this verifier;
   `ledger/board.lock` absent at check time.)
8. Metrics scaffolding: briefs/corrections/escalations/plants/fetches
   JSONL shapes beside usage/passes, kit-`round_metrics` compatible
   (shapes read; committed files still end at Wave 0 cutoff by design,
   extension named in RECORD). HOLD.
9. Bench skeleton only: placement/clock-labelled, both SDK flavours,
   baselines present, zero performance claims anywhere. HOLD.

Wave-1 ownership: `src/msf32.c` vs `src/msf64.c` are disjoint per-format
translation units over lead-owned shared kernels (`msf_wide.c`,
`msf_roundpack.c`, `msf_internal.h`, generated tables/header/dispatch —
SF-0 §7 shared-helper rule). Two format parcels CAN name disjoint owned
files (their TU + their new vector files); shared surfaces are
escalation-only. Overlap notes (do not break the acceptance text):
`compat/msf_wrap.c` spans f32+f64 wrap names but Wave-1 scope needs no
compat change (AEABI surface is Wave 3); `board/*`, `tests/runner.c`,
`tools/*` are shared/lead-owned.

## Verdict inputs

- Class (a) regressions: none.
- Class (b) wrong answers: none.
- Notes: (i) planned-op SKIP file-verdict reads PASS with passed=0
  (expect-counts guards the gates); (ii) level-2 oracle count/timing has
  no saved output log (re-runnable live, not re-run here);
  (iii) machine-path tool defaults in `board/common.sh`;
  (iv) my own two probe-oracle bugs found and fixed during the run
  (documented in §3; neither implicates the tree).

Verdict: **READY** — (a) 0, (b) 0.
Report: `scratch/verifier-p0/report.md` (this file).
Ledger: appended via kit `ledger.sh` (see ledger/verifier-p0.md).
Not done: board/bench budgets (board untouched by rule; judged from
logs/hashes); level-2 streaming re-pricing; reading `scratch/lead/keys`
or any non-`metrics-p0` lead files; full `standard` provenance
re-derivation beyond the re-run.
