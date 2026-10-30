# rechecker-tininess report (muse-spark-1.3, scoped recheck, disconfirm-only)

Scope: target commits `53acb1a` (pack tininess + ingest eq) and `b37fb12`
(control 9 op + LF normalisation) in `muse-softfloat/`, parent `4cdb912`.
Fix nothing in project files: no project file was modified; all probes live
in `scratch/rechecker-tininess/`. Nothing with `cft` in its name was created.
`worktrees/` and the board were not touched.

Verdict: READY. Counts: (a) 0, (b) 0, notes 5 (all procedural, below).

## Probe inventory (all executed, Git Bash, TMP into scratch)

Toolchain notes (procedural): the owner's `Temp` ACL denies compiler temp
files (`Cannot create temporary file ... Permission denied`, measured), so
every probe script sets `TMPDIR` to `scratch/rechecker-tininess/tmp` (POSIX
form) with `TMP`/`TEMP` in Windows form via `cygpath -w`, and prepends
`/c/msys64/mingw64/bin:/c/msys64/usr/bin` to `PATH` exactly as `tools/run.sh`
does (without it, `cc1.exe` fails to resolve its DLLs and gcc dies silently
with exit 1 and empty stderr; diagnosed via `p2_isolate*.sh`). `p1_diff.sh`
used a `grep -c $'\r'` CRLF check that returned 0 against Git-Bash grep;
the authoritative `tr -cd '\r' | wc -c` count in `p1b_tsv.sh` supersedes it.

### (1) Diffs 4cdb912..b37fb12 file-by-file vs the two commit messages

`p1_diff.sh`, `p1b_tsv.sh`, `p1c_full.sh`. `name-status` shows exactly 8
modified files: `src/msf_roundpack.c`, `tests/berkeley_ingest.py`,
`tests/gen_vectors.py`, `tests/vectors/pack16.vec`, `pack32.vec`,
`pack64.vec` (commit `53acb1a`) plus `tables/implemented.tsv`,
`tools/run.sh` (commit `b37fb12`). No other file changed.

- `tools/run.sh`: exactly 1 hunk = control 9 re-point
  (`msf64_add te 3ff...` to `msf16_add te 3c00 3c00 -> 4000 00`) + comment.
- `tests/berkeley_ingest.py`: exactly 1 hunk = `eq` row
  `compare_signaling_equal` to `compare_quiet_equal` + asymmetry comment.
- `tests/gen_vectors.py`: exactly 1 hunk = `pack_ref` unbounded-rounded
  `scale_u`/`q_u` block + comment.
- `src/msf_roundpack.c`: 4 hunks, all inside the claimed change: header
  comment restatement, `round_inc` + `extract_k2` helpers, call-site
  refactor to those helpers, flags-only unbounded-scale `tiny_after` block.
- `tables/implemented.tsv`: parent blob 71 CR + 71 LF (CRLF), tip 0 CR +
  71 LF; `diff --ignore-cr-at-eol --stat` empty: pure CRLF-to-LF
  normalisation, zero content change.
- Pack vectors: 96 insertions + 96 deletions = 96 changed expectations
  (32 per file), matching the commit message's "96 boundary expectations".

No unclaimed hunk, no extra file: matches both commit messages exactly.

### (2) ORACLE DIFFERENTIAL (decisive): 2400/2400 agree, 0 disagreements

`tinydiff.c` + `p2_oracle.sh` (`p2-results.log`), `focus.c` + `p2_focus.sh`
(`p2-focus.log`). The corrected `msf_pack_generic` (flags+bits, fed exact
`sig`/`exp2` pack inputs: exact `u64 x u64` product for mul, fresh
shift-and-subtract long division for div, written independently of
`msf32.c`/`msf64.c`) was compared against the real Berkeley library
(`scratch/oracles/SoftFloat-3e/build/Linux-x86_64-GCC/softfloat.a`,
`f32_mul`/`f32_div`/`f64_mul`/`f64_div` + `softfloat_exceptionFlags`,
translated 1/2/4/8/16 to MSF 0x10/0x08/0x04/0x02/0x01 by `p2` itself) with
`softfloat_detectTininess` set to after-rounding explicitly.

Coverage: operand pairs crafted so exact products/quotients land in
`[2^emin - 2^(emin-p-1), 2^emin)` and just above `2^emin` for f32 and f64
(min-normal, max-subnormal and near-unity operand sets in `tinydiff.c`),
all 5 rounding modes, both signs: 2400 cases total (f32 mul 1080, f32 div
600, f64 mul 480, f64 div 240), disagreements 0. Delivered BITS agreed
everywhere too.

Escalation examples pinned explicitly (`p2-focus.log`, te mode, both sides):

- A `f32 mul 00800000 x 3f7fffff`: Berkeley bits `00800000` flags `18`,
  msf-pack bits `00800000` flags `18`, want `00800000`/`18`: underflow present.
- B `f32 mul bf800001 x 007fffff`: Berkeley bits `80800000` flags `10`,
  msf-pack bits `80800000` flags `10`, want `80800000`/`10`: no underflow.

Any disagreement would have been class (b). There were none: no (b).

Probe-self-correction on record: the first `p2` run showed 760 div
disagreements, all div-side, caused by an off-by-one in the probe's own
`div_exact` bit stream (`at >> (i-64)` instead of `(i-63)`); the mul side
was fully green from the first run. After the one-line probe fix, 2400/2400
agree. The kernel was never implicated: the probe bug was identified by
inspection (even exact-division-by-1.0 cases differed on the MSF side).

### (3) Pack regression: changed lines ONLY smallest-normal-boundary flags

`p3_analyze.py` (`p3-analysis.log`) pairs all 96 changed expectations by
exact inputs (multiset-matched; the vec files contain duplicate input keys
because `pack_directed` lists `s_sub` twice, so unique-key counting gave 48
and line counting gives the true 96): every changed pair keeps IDENTICAL
result bits, differs ONLY by the underflow bit (`0x08`), and the result
magnitude is the smallest normal of its format (`0x0400` / `0x00800000` /
`0x0010000000000000`) in all 96. Replay of the committed pack vectors with
a freshly built runner: 18590 passed, 0 failed (`p3-verify.log`).

### (4) Ingest: eq maps quiet; 3600/3600 ingested lines match the oracle

`eqcheck.c` + `p4_ingest.sh` (`p4-partA.log`, `p4-partB.log`,
`p4-ingest.log`). Part A drives Berkeley directly: `f32_eq` on quiet-NaN
operands (incl. the escalation pair `3dfffe1e` vs `ffc18073`) returns
result 0 with flags `00`, while `f32_eq_signaling` gives `01`; `le`/`lt`
give `01` on quiet NaN (signaling family) and `le_quiet`/`lt_quiet` give
`00`; sNaN operands give `01` everywhere. This is exactly the asymmetric
historical set the corrected row encodes. Part B: ingested 300 cases each
for all 12 compare functions (`f32/f64 x eq/eq_signaling/le/lt/le_quiet/
lt_quiet`, level 1, seed 1) via the corrected `berkeley_ingest.py`
(`f32_eq` maps to `msf32_compare_quiet_equal`, `f64_eq` maps to
`msf64_compare_quiet_equal`) and re-drove every line through `softfloat.a`:
3600 lines, 0 mismatches in result bit or translated flags (requirement
was 100+).

### (5) run.sh smoke AND standard PASS; controls refuse

`p5_runsh.sh` (`p5-smoke.log`, `p5-standard.log`): smoke PASS (7 s),
standard PASS (34 s; 917504 f16-exhaustive + 200000 pack-sweep, all pass).
Control 9 (`build/standard/controls/planned.log`): runner prints
`SKIP ... msf16_add not implemented (planned wave 2)` with
`VERDICT: FAIL (no vectors passed; skips are not passes)`, and run.sh
reports `control planned-only-verdict: refused as required`.
Wrong-tininess control (`-DMSF_TININESS_AFTER_ROUNDING=0` build vs
corrected `pack64.vec`): still refused as required, with 34 FAIL lines
(`p5_check.sh`); every one is the complementary class-B shape (expectation
min-normal flags `10`, before-rounding build delivers `18`, bits agree),
i.e. the polarity control remains sensitive in the opposite direction.

### (6) Independent spot derivation of the unbounded-rounded definition

`p6_arith.py` (`p6-arith.log`, 40 rows, Fractions only, not the repo's
reference): class-A magnitudes are tiny in ALL modes (unbounded value is
the exact value itself, below `2^emin`); class-B magnitude
`(2^46-1)*2^-172` unbounded-rounds to exactly `2^-126` under te, hence not
tiny (`10`); f64 analogs behave identically at their boundary. Matches the
ruling's hand derivation and the kernel's outputs.

## Classification

(a) 0. (b) 0.

Notes (procedural, not findings against the targets):

1. `p1_diff.sh`'s `grep -c $'\r'` CRLF check misreported 0 under Git-Bash
   grep; superseded by `tr`-based counts in `p1b_tsv.sh` (71 CRLF to 0).
2. `p3_analyze.py` first counted 48 (unique input keys) before multiset
   line matching gave the true 96; duplicate input keys come from the
   generator listing `s_sub` twice.
3. First `p2` run's 760 div disagreements were the probe's own off-by-one
   (`p2_triage.sh` showed mul fully green throughout); fixed, 2400/2400.
4. `msf64` compare ops are not implemented in this tree (Wave 1 unmerged),
   so Part B validates the ingest translation against Berkeley itself
   (3600/3600) rather than replaying through the MSF runner; runner replay
   of unimplemented compare ops would SKIP, not PASS.
5. `p5_check.sh`'s final shape-filter regex did not match the runner's
   `got/ want/` FAIL format and re-listed lines; the class-B-only shape is
   established by the `uniq -c` counts (17+17 min-normal/`10` expectations)
   and the sampled FAIL lines, not by that filter.

## What was not done

- No `27.26M`-case parcel re-run (parcels' volumes); the differential
  covers the boundary class (2400 cases) plus the full committed pack
  vectors (18590) plus the standard gate (1.1M).
- No board/bench budgets (host-only recheck; target files are host-shared
  kernel/reference/ingest/run-script).
- No `testfloat_gen`-level eq volumes beyond 300 per function (3600 lines
  audited vs the oracle directly).
- Ledger: appended to `ledger/rechecker-tininess.md` via kit `ledger.sh`
  (`p7_ledger.sh`, exit 0); body staged at
  `scratch/rechecker-tininess/ledger-body.txt`.
