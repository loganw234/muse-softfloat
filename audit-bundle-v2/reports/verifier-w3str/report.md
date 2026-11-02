# Verifier-w3str report (Wave 3 string parcel, planted copy f58f299)

Verdict: **NOT READY — send back.** Three code defects + one vector defect
in the copy. Fault isolation is complete: a scratch-only diagnostic build
with three one-line fixes replays 9148/9149 committed vectors and passes
all 7383 adversary/slice lines plus all 262144 f16-exhaustive output lines.

Scope judged: the copy at worktrees/verify3-str @ f58f299
("Added the character-conversion references and committed vectors",
parent 548a1b9 = the parcel base chain, working tree clean).
The copy was never modified; all probes ran from scratch/verifier-w3str/
against a probe runner built from the copy's own sources with only
-Wno-unused-parameter relaxed (project -Werror is what fails).

## Budgets

- smoke: FAILS at the host build. Drift check passes (4/4 byte-identical),
  then `cc1.exe: all warnings being treated as errors` on
  src/msf_string.c:411 `dec_round_inc` unused parameter `last_kept`
  (finding F-A). No unit tests, vectors, or controls execute.
- standard: cannot run (same build gate). Substitutes executed via the
  probe runner (see Regressions): the 29 wired VECS (75999/75999),
  the standard arithmetic tail f16-exhaustive 917504 + pack-sweep 200000
  (1117504/1117504), all PASS.
- control 9 (planned-only-verdict): NOT REFUSED in the copy, which is the
  known merge-time state, not a parcel defect. Two independent reasons:
  (a) msf16_from_decimal is implemented in the copy (op surface reports
  783 implemented, 0 planned), so the refusal premise is gone;
  (b) the control's probe line uses the pre-char space format and is now
  rejected as `char-from vector shape` malformed (0 vectors, 1 malformed),
  never reaching the SKIP-not-implemented path the control requires.

## Findings (class a = regression/claim-surface deviation, b = wrong answer)

- F-A (b, root cause; also blocks the build hence the smoke budget):
  `dec_round_inc` ties-to-even ignores `last_kept`
  (src/msf_string.c:418-419 `return gt_half || eq_half;`), rounding exact
  halves up instead of to even. The unused `last_kept` is exactly what
  -Werror rejects. Blast radius, all confirmed through the probe runner:
  6 committed to-decimal lines (3290-file lines 97,143,258,511,557,672),
  committed beyond-H line 3276 (0x1 vs ruled 0x2 at the subnormal bottom),
  my adversary ties/off-ties, f16-exhaustive to-dec 4516/262144 at every
  SPEC 5/9/17. Fixed-TU collapse: 0 fails on all of these.
- F-B (b): from_hex exponent compensation uses 2 bits per fraction hex
  digit instead of 4 (src/msf_string.c:746
  `exp2 = pexp - 2*frac_digits + extra_exp`), shifting every hex-fraction
  input by +2 exponent bits per fraction digit (verified +2/+6/+26 on
  1/3/13-digit cases incl. overflow/underflow deliveries). Blast radius:
  500/1314 committed from-hex lines, 196/2284 MPFR-slice lines, all with
  fraction digits; zero failures on fraction-less hex lines (incl. the
  committed `0xabcdefp10` grammar/mode copies). Fixed-TU collapse: 0.
- F-C (b): `parse_special` consumes 3 chars for "snan" instead of 4
  (src/msf_string.c:351-352), while delivering the correct signaling value
  (7c01 etc.). Blast radius: all 36 committed snan lines + 3 slice lines
  (got C=len-1, want C=len); inf/infinity/nan consumed all pass.
  Fixed-TU collapse: 0.
- F-D (b, vector-side): committed from-decimal-str.vec line 118 expects
  `snan -> 7e00` (quiet). Five sibling lines (119-123), the copy's
  generator (`i + 4`, clean), my independent reference (7c01/00/C=4),
  fixed-TU output (7c01/00/C=4), and ruling R2 (signaling, no invalid)
  all say 7c01. Single-line anomaly; fixed-TU replay is 9148/9149 with
  this the only failure.
- F-E (a, generator/vector mismatch): the copy's generator emits
  `0xabcdeeep10` where the committed vectors test `0xabcdefp10`
  (from-hex lines 39, 204-207, 477, 642-645, 915, 1080-1083: 15 lines).
  Both sides are arithmetically self-consistent (f16 overflow inf,
  f32 0x502bcdef exact, f64 exact), but regen is NOT byte-identical, so
  the committed file cannot have been produced by the committed generator.
  Non-byte-identical regen is a finding per project norm.

## Evidence and controls

- Committed replay (probe runner): 9149 vectors, 8606 pass, 543 fail,
  all in F-A/F-B/F-C classes (37 from-dec = 36 snan + line 3276 tie;
  500 from-hex frac-scaled; 6 to-dec ties; 0 to-hex fails).
- Regen byte-compare (copy's generator to temp): to-dec/to-hex IDENTICAL;
  from-dec differs at line 118 only (F-D); from-hex differs at the 15
  abcdef lines only (F-E).
- Independent reference (scratch vw_ref.py: fresh exact-rational code,
  no generator imports; integer IEEE pack mirroring the landed kernel):
  MPFR cross-check within H — from 1146/1146 agree (0 dropped,
  54 skipped non-tokens), to-dec/to-hex 1084/1084 agree (116 dropped
  specials). Slice vec through probe runner: 2084/2284 pass, 200 fails
  all in F-A/F-B/F-C (3+196+1, disjoint).
- Adversaries (scratch vw_gen.py, 5123 lines: grammar/consumed, ties and
  1-ulp-off-tie every dest x mode incl. subnormal boundary, directed
  overflow signs, beyond-H two-step incl. the ruled step-2-exact underflow
  corner, spec matrix, %a carry/subnormal scale, BUF fit/no-fit):
  regular runner 4833/5099 pass, 266 fails = 108 snan + 150 hexfrac +
  8 ties (disjoint: 24 from_hex snan lines sit in the snan bucket).
  Within-H from_decimal ties (kernel pack path): 0 fails; all 1-ulp-off-tie
  lines: 0 fails — the tie defect is confined to dec_round_inc's two call
  sites (beyond-H step 1, to_decimal output). The ruled underflow corner
  (step-2-exact tiny, inexact-only) passes on the copy.
  Fixed runner 7383/7383 pass incl. slice.
- f16-exhaustive output sweep (my ref, 262144 lines): regular runner
  257628 pass, 4516 fails all te-tie pattern at SPEC 5/9/17, 0 elsewhere;
  fixed runner 262144/262144.
- API edges (scratch C harness, 24 checks): NULL s/consumed/spec/buf,
  whitespace-first, empty, inner spaces, trailing space, exact-fit,
  one-short, zero-size buf, prec=1000000 sizing, unknown style,
  min_digits floor, FIXED shapes — 23/24 pass; the one failure is F-B
  manifesting (documented, expected).
- Fuzz (scratch vw_gen.py, seeds 1101-1104, expectations from vw_ref):
  100000 vectors per direction family (from-dec / from-hex / to-dec /
  to-hex, 3 dests x 4 modes mixed, extremes capped at 2% with the rest
  covered by directed sets). Regular runner: 366620/400000 pass, 33380
  fail = 890 snan (F-C) + 32363 hex-frac (F-B) + 127 to-dec ties (F-A),
  disjoint, 0 elsewhere (to-hex 0 fails; all 127 tie fails are te mode;
  zero from-dec fails outside snan — the step-1 tie is unobservable at
  normal magnitudes since a 20-digit decimal ulp (1e-20 relative) is far
  below the binary ulp, so only engineered near-boundary inputs like the
  committed 3276/adversarial pair manifest it). Fixed runner: 400000/400000.
- Round-trips, mode-matched parse-back via my ref (te claim scope):
  committed 772/772 finite + 414/414 NaN; f16-exhaustive 190464/190464 +
  63488/63488; fuzz 31731/31731 te-finite + to-hex 20963/20963 (directed
  lines excluded from the claim: 30386 RT-DIR misses documented as the
  expected non-invertibility of directed rounding, e.g. tp output parsed
  back under tp lands on a neighbor); adv te-finite all pass.
  NaN round-trips assert class+sign (payload canonically defaults, R2).
- NaN payloads: the copy delivers canonical payloads only (quiet ->
  default_qnan 7E00/7FC00000/7FF8..., signaling -> infinity|1, quiet bit
  clear; src/msf_string.c:362-373, formats header). Proven by code reading
  + all committed NaN rows passing with canonical expectations (except
  F-C consumed and F-D), and round-trip checks assert class+sign only.
- Regressions: 29 wired VECS 75999/75999; standard arithmetic tail
  1117504/1117504 (f16-exhaustive + 200k pack-sweep, 37821
  non-invariant dropped at generation per lead protocol). to-hex: 0
  committed fails and 0 adversary fails — the output directions other
  than the tie bug are clean.
- Static: drift 4/4 byte-identical (same command as run.sh);
  type scan clean (`grep -rnwE 'float|double' src include`, same command);
  claim surface = parcel-owned (src/msf_string.c, tests/gen_vectors_str.py,
  4 str vecs, implemented.tsv +12 rows with mixed 779-CRLF/12-LF endings
  as disclosed) + regenerated headers/COVERAGE + lead prep (tests/runner.c
  char support incl. f3c48b8/83622cf fixes, run.sh/board wiring, RECORD
  docs). Separation method: parent-diff file list by commit; the copy
  squashes to one commit on 548a1b9, so separation is by file ownership
  per the brief, not by commit.
- Timings (loaded machine): smoke to build-fail ~15 s; probe build ~40 s;
  committed replay ~60 s; regen ~45 s; adv 5123-line gen ~10 min;
  MPFR slice ~3 min; f16 exhaustive gen+run ~6 min; standard tail
  gen+run ~8 min; fuzz 400k gen ~3 min + both-runner replay ~8 min;
  round-trips ~4 min.

## Not done

- Board budget (lead-run; unreachable — build gate fails first).
- Full myref-vs-committed-expectations sweep as one background job (two
  duplicate runs produced no output in 1h+ and were terminated; covered
  equivalently by regen byte-compare + single-case checks on both
  divergent lines + MPFR triangulation + fixed-TU agreement on all 9149
  committed vectors).
