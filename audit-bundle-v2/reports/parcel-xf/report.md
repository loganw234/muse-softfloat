# parcel-xf report - Wave 2 cross-format (126 rows)

Verdict: **READY**. All 126 wave=2 `msf32_*`/`msf64_*` instantiations
are implemented, appended to `tables/implemented.tsv`, regenerated
clean, and gated green. Worktree `worktrees/w2-xf`, branch `w2-xf`,
base `dd48b08c7cb2f1aa957d15972d919c6d3051ad78`, never pushed,
never merged. Commits:

- `09c0acd` Wave 2 parcel-xf: 126 cross-format instantiations in msf32.c/msf64.c
- `7935fab` Reword an msf32.c comment the smoke type scan refused

First ledger entry (design): 2026-10-27 07:08:30 -0700 in
`ledger/parcel-xf.md`; this report written ~07:45 same day, well
inside the 300-minute box (240-minute checkpoint not reached).
Machine was under third-party load throughout; wall times are
records, not rates. Escalation channel test:
`ledger/urgent/parcel-xf-test.md` (07:02:22). One objection filed
and ruled: dest-f64 convert-first traps are vacuous (converting to
f64 first is exact); lead upheld (ledger 2026-10-27 07:12) and the
designed substitution stands (unfused-fma and via-binary32 traps
for dest f64, plus the counted zero-difference convert-first
proof). No other brief corrections; my row count matched the
brief exactly (126; authorities mpfr-exact 80,
project-exact+berkeley-check 24, project-exact 20, berkeley 2).

## What was built

Per dest (63): add/sub/mul/div in source pairs (f16,f16),
(f16,f32), (f16,f64), (f32,f16), (f64,f16); `sqrt_f16`; 19 `fma`
triples with at least one f16 source; `from_f16`; 22
`compare_*_f16` predicates with sources (dest, f16).

Implementation: new public wrappers only, over the landed Wave 1
format-generic kernels (`add_impl`/`mul_impl`/`div_impl`/
`sqrt_impl`/`fma_impl`/`conv_impl`/`cmp_impl` in `src/msf32.c`;
`addsub_core`/`mul_core`/`div_core`/`sqrt_core`/`fma_core`/
`conv_core`/`compare_core` in `src/msf64.c`). Every source decodes
exactly in its own format via `msf_decode`; exact work over
`msf_u128`; one pack. No source is converted to the dest format
first anywhere (single rounding, SF-0 2.3). NaN delivery is the
shared SF-0 2.5 matrix (`msf_nan_delivery`), operand order
preserved, payloads shift-mapped into the dest format with
truncate-to-default when an f64 payload narrows to zero in f32.
Landed Wave 1 behavior: the diff vs base in `src/msf32.c` is 83
insertions / 0 deletions and in `src/msf64.c` 77 insertions /
1 deletion (one comment line); no landed wrapper or kernel body
changed. Bit-identity evidence: smoke/standard replay below.

Tests: `tests/gen_vectors_xf.py` (new, 1,042 lines), independent
Fraction references parameterized by destination; pack reference
uses Clause 7.5 unbounded-rounded tininess per the lead ruling.
It is never called by the implementation and shares no code shape
with the C kernels beyond decode. Committed directed vector files
total 939,666 bytes (< 1 MB ceiling). Hand-written lines: src 161
+ generator 1,042 = 1,203 (< 3,000 ceiling).

## Gate results (every count by provenance)

Runner: `build/w2/msf_runner.exe` (gcc x86_64-w64-mingw32 16.1.0,
FLT_EVAL_METHOD=0, `-std=c11 -O2 -Wall -Wextra -Werror
-ffp-contract=off`), all runs from `worktrees/w2-xf` via Git Bash
script files in `scratch/parcel-xf/scripts/` (numbered 00-19),
logs in `scratch/parcel-xf/logs/` and `build/w2/`.

1. `tools/run.sh smoke` - PASS in 12 s (log
   `scratch/parcel-xf/logs/11_smoke_full.log`): drift check 4
   generated files byte-identical; unit PASS; committed Wave 1
   vectors **52,168 passed / 0 failed** across 16 provenance tags
   (exact-py:* 29,982; exact-py-f32:* 11,129; exact-f64:* 11,057);
   type scan clean; symbol scan clean; 9/9 permanent negative
   controls refused, including planned-only (now
   `msf16_from_decimal`). First smoke attempt failed only the
   type scan on a word in my new comment; fixed in `7935fab`,
   re-run PASS. This is the landed-rows bit-identity proof.
2. `tools/run.sh standard` - PASS in 33 s (log
   `scratch/parcel-xf/logs/19_standard_full.log`): smoke contents
   plus 917,504 exhaustive-f16 and 200,000 pack64 sweep vectors,
   **1,117,504 passed / 0 failed** in the standard leg.
3. Directed xf sets (`gen_vectors_xf.py directed tests/vectors`,
   replayed explicitly since `tools/run.sh` has a fixed smoke
   list and tools/ is off-limits; lead wires at merge):
   **11,066 passed / 0 failed** - exact-py-xf:directed-arith
   6,044; directed-fma-sqrt 2,560; directed-conv 368;
   directed-compare 1,980; trap-convert-first 48; trap-unfused
   25; trap-via-f32 41. Generator asserts all 126 names present.
   Directed operands include f16 subnormals, tie boundaries at
   both dest precisions, f64 tie-zone values (1+2^-24 etc.),
   NaN payloads at the f64-to-f32 truncation threshold
   (payloads 1, 2^29-1, 2^29, quiet variants, both signs) and
   widening f16 payloads, signed zeros, infinities.
4. Seeded sweeps into `build/w2/` (not committed), templates
   cycling all 63 instantiations per dest, operand pools mixing
   all three formats' edge encodings incl. f64 danger-zone
   significands: **1,260,000 passed / 0 failed** -
   exact-py-xf:sweep-20261027 (f32) 315,000; sweep-777001 (f64)
   315,000; sweep-555 (f32) 315,000; sweep-556 (f64) 315,000.
   Brief floor was 300k per dest; delivered 630k per dest.
5. Exhaustive binary16 unary (`exhaustive-f16`): every one of
   65,536 f16 encodings through `from_f16` (te, both dests) and
   `sqrt_f16` (te/tp/tn, both dests):
   exact-py-xf:exhaustive-f16-unary **524,288 passed / 0 failed**.
6. Berkeley-decided rows (the 2 `berkeley` authorities),
   `tests/berkeley_ingest.py` with `MSF_TESTFLOAT_GEN` set to the
   pinned `scratch/oracles` build, into `build/w2/`, level 1
   complete, every applicable attribute mode (te/tz/tp/tn; ta is
   not an attribute mode for convertFormat): 8 jobs
   (`f16_to_f32`, `f16_to_f64` x 4 modes) x 408 cases =
   berkeley:testfloat_gen-f16_to_f32-* 1,632 and
   berkeley:testfloat_gen-f16_to_f64-* 1,632, **3,264 passed /
   0 failed**, compare=nan-class per ingest policy for
   conversions (payload-exact coverage for these rows comes from
   the exhaustive item 5 under compare=exact).
7. Berkeley cross-check for the 24
   `project-exact+berkeley-check` comparison rows. No direct
   TestFloat generator exists (Berkeley comparators are
   same-format pairs only - named here per the brief). Cross-check
   by transformation (`scratch/parcel-xf/scripts/
   15_berkeley_cmp_driver.py`): pinned f16 streams eq,
   eq_signaling, le, lt, le_quiet, lt_quiet at level 1 seed 1
   (46,464 cases each); first operand widened exactly to the dest
   format by field construction (payload left shift preserving
   the quiet bit for NaNs), expectations and flags Berkeley's
   (translated at the driver), greater/greaterEqual read from the
   same streams swapped, notEqual complemented. Covers all 12
   check predicates per dest: berkeley-xf:testfloat_gen-f16_*-
   l1-s1-widened, 6 tags x 185,856 = **1,115,136 passed /
   0 failed**, compare=exact. Berkeley `eq` treated as QUIET per
   the Wave 1 ruling (ingest mapping already encodes this).
8. Independent neighbor-boundary audit
   (`scratch/parcel-xf/scripts/17_neighbor_audit.py`): every 37th
   line of the four sweep files and the committed arith/fma-sqrt/
   conv files; exact result recomputed with Fractions (sqrt by
   squared boundaries), expected bits verified as the correct
   rounding by the neighbor/midpoint definition (no shared code
   with the generator's packer beyond decode), inexact flag
   checked against exact-vs-delivered: **17,630 audited, 0 bad**
   (16,663 sampled lines skipped by construction: NaN/inf inputs,
   overflow-boundary results, comparisons - counted per file in
   `build/w2/neighbor-audit.log`).
9. Convert-first-to-f64 sampled proof (inside directed
   generation): 1,170 dest-f64 cases where sources were converted
   to f64 first and then operated; **0 differences** from
   exact-then-round, as the exactness of widening requires.
   Count is also recorded as a comment header in
   `tests/vectors/traps-xf.vec`.
10. Regeneration stability: `gen_vectors_xf.py directed` into a
    scratch directory reproduces all five committed vector files
    byte-identically; `tools/gen_tables.py` drift is enforced by
    smoke/standard (item 1).

Double-rounding traps (committed in `traps-xf.vec`, 114 lines;
every expectation is the exact single-rounding answer, selected
because the named wrong pipeline's result bits differ):

| pipeline | family | dest | count |
|---|---|---|---|
| convert-sources-to-f32-first | add | f32 | 6 |
| convert-sources-to-f32-first | sub | f32 | 6 |
| convert-sources-to-f32-first | mul | f32 | 6 |
| convert-sources-to-f32-first | div | f32 | 6 |
| convert-sources-to-f32-first | fma | f32 | 24 |
| unfused mul-then-add | fma | f32 | 16 |
| unfused mul-then-add | fma | f64 | 9 |
| evaluate-at-binary32-then-widen | add/sub/div | f64 | 5 each |
| evaluate-at-binary32-then-widen | mul | f64 | 4 |
| evaluate-at-binary32-then-widen | sqrt | f64 | 3 |
| evaluate-at-binary32-then-widen | fma | f64 | 19 |

Convert-first traps at dest f32 exist only for f64-bearing rows
(f16/f32 sources convert to f32 exactly); at dest f64 they cannot
exist at all (item 9). Some unfused-fma combos provably have no
trap (exact product always fits dest precision, e.g. f16*f16 into
f32); counts above are per family/dest as the brief requires.

Negative controls demonstrated refused (logs in
`build/w2/controls/`, driver log `scratch/parcel-xf/logs/
16_controls.log`):

- Flipped result bit in committed `arith-xf.vec` (line 2,
  `msf32_add_f16_f16 te 0 0 -> 1`): runner exit 1, exactly 1
  failure of 6,044, VERDICT: FAIL.
- Trap expectation flipped to the convert-first answer
  (`msf32_add_f16_f64 te 1 bfe0000010000002`: exact `beffffff`/10
  vs convert-first `bf000000`/00): runner exit 1, implementation
  FAILS it as required - the trap discriminates.
- Smoke planned-only control (`msf16_from_decimal`): refused as
  required (item 1), along with the other 8 permanent controls.

## Skips, by name

- Board budget: lead-only, not run.
- Berkeley level 2: not run; the brief gates these rows at
  level 1 (berkeley rows are unary conversions whose level 1 is
  408 cases; payload-exact exhaustive project evidence in item 5
  covers all 65,536 encodings anyway).
- Direct Berkeley generators for the 80 mpfr-exact and 20
  project-exact rows: none exist (Berkeley has no cross-format
  arithmetic); those rows rest on the exact-rational references,
  sweeps, and the neighbor audit. The 24 berkeley-check rows are
  covered by item 7's transformation, not by a direct generator.
- Host-FPU oracle cross-checks: not used.
- `tools/run.sh` smoke does not name the five new committed xf
  vector files (fixed list, tools/ off-limits to this parcel);
  they were replayed explicitly (item 3) for the lead to wire at
  merge, the Wave 1 parcel pattern.

## Files and scope audit

Changed vs base (12 files, all parcel-owned or generated outputs):
`src/msf32.c`, `src/msf64.c`, `tests/gen_vectors_xf.py` (new),
`tests/vectors/{arith,fma-sqrt,conv,compare,traps}-xf.vec` (new),
`tables/implemented.tsv` (+126 appended rows, 0 deletions, LF),
and regenerated `include/muse_softfloat.h`, `src/msf_formats.h`
(unchanged content), `tests/msf_dispatch.h`, `docs/COVERAGE.tsv`
(126 rows planned -> implemented, nothing else). No off-limits
file touched: nothing in `src/msf16.c`, shared kernels, `tools/`,
`tests/runner.c`, existing generators, `board/`, `compat/`,
`docs/` beyond the generated COVERAGE.tsv. Worktree clean but
for the two commits above. Total xf-provenance replayed vectors:
2,913,754 (directed 11,066 + sweeps 1,260,000 + exhaustive
524,288 + Berkeley 3,264 + 1,115,136), plus 52,168 smoke and
1,117,504 standard regression vectors.

Reproduce: from `worktrees/w2-xf` under Git Bash,
`bash tools/run.sh smoke`; `python tests/gen_vectors_xf.py
directed tests/vectors` (byte-stable); runner verify over the
five `tests/vectors/*xf*.vec` files; sweeps/exhaustive/Berkeley
exactly as scripted in `scratch/parcel-xf/scripts/13_sweeps.sh`,
`14_berkeley_conv.sh`, `15_berkeley_cmp.sh`, `18_extra.sh`.

Gaps against the brief as ruled: none. The one brief wording
fault (per-dest convert-first traps) was escalated before coding
around it and is dispositioned by the lead ruling recorded in
the ledger; evidence for the substituted construction is items
9 and the trap table above.

