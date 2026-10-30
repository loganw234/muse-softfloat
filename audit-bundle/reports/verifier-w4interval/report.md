NOT READY

# verifier-w4interval report (planted-copy verification, Step 1c host proof)

Copy: `worktrees/verify4-interval`, HEAD `b577456`, clean before and after.
All probes ran from script files in `scratch/verifier-w4interval/`
(`00_env.sh` … `14_run_stage.sh`, `03_audit.py` + helpers) under Git Bash,
`MSF_PYTHON` pinned to the workspace `.venv` (Python 3.12.15, numpy 2.5.4),
host compiler `x86_64-w64-mingw32` gcc 16.1.0. The copy was never modified
(`git status` clean; `smoke`/`standard` build dirs are gitignored).
Governing texts read in full: `ledger/briefs/verify-w4interval.md`,
`ledger/briefs/w4-interval.md`, `ledger/parcel-w4interval.md`,
`scratch/tier2-interval/report.md` (Secs. 1/2/6, G1–G7), and every source
body cited below. The parcel branch/worktree, `scratch/parcel-w4interval/`,
`scratch/lead/`, `ledger/lead.md`, `cft*`, and the PDF were never consulted.

## Findings (one claim per line)

(b1) Lo endpoints round-to-nearest: `IW_RM_LO` defaults to
`MSF_ROUND_TIES_TO_EVEN` (`board/interval_workload.c:8`), not
`MSF_ROUND_TOWARD_NEGATIVE`. Every lo-endpoint op (interval add/sub/mul/sq
lo, stage-1 outward `msf32_from_f64` conversion, slab `idiv_pt` lo, box
inner-hi) rounds RN, breaking outward containment on the lo side. My
independent exact-rational audit (`03_audit.py`, Fraction on stored bits)
finds **485 HARD containment violations** (finite endpoints, exact
discriminant outside): tangent400 303, limb 163, adv2k 18, ordinary 1;
plus 4 NaN-interval rows (guard 682/683 s1+s2, overflow→NaN, all
UNCERTAIN, safe). Zero decided-wrong and zero flips on this catalogue
(unsound intervals, luck of the draw, not soundness). Smallest repros:
row id 4 fam tangent400 s1; row id 6 s2 (`s2lo == s2hi`,
exact outside the degenerate point). Repro: `01_rebuild_run.sh` then
`03_run_audit.sh`.
(b2) The owned generator's exact sphere oracle has the wrong sign:
`disc_exact` returns `b*b + a*c`
(`tests/gen_interval_catalogue.py:69`); the discriminant is `b*b - a*c`
(cf. the naive columns at :83/:93 and the host `isub(isqr(b), imul(a,cc))`).
Regeneration does not merely differ — it **crashes**:
`fam_limb` assertion `disc_py(lo) > 0 > disc_py(hi)` fails because the
buggy formula is positive on both sides. Repro: `02_regen.sh`
(`AssertionError` at line 186, no output file). The byte-identical
regeneration gate fails catastrophically.
(b3) Catalogue row id 2 is internally inconsistent: exact column `MISS`
but `exact_extra` = `3155251/8796093022208` (positive ⇒ HIT); independent
recompute gives `b²−a·c = +3155251/8796093022208` ⇒ HIT
(`04_run_row2.sh`). The TSV oracle column says wrong on this row.
The host (final=HIT) agrees with the true class, so no decided-wrong —
the defect is in the frozen oracle column.
(a1) `min64` uses the suppressing Number form `msf64_minimum_number`
(`board/interval_workload.c:44`) in the containment path (imul/isqr/slab/box),
while `max64`/`min32`/`max32` use the propagating forms. The brief bans
Number forms from the containment path and the header comment claims
propagating forms throughout — both contradicted. The brief's source-scan
gate (`no *_number in the workload core`) FAILS on the as-shipped core
(1 hit, :44; host main is clean). Behaviorally inert on this catalogue
(no NaN geometry rows; P1-vs-M3 hashes identical), so the scan, not the
audit, is the catching oracle — recorded honestly.
(a2) `guard_tripped` (`:395-404`) checks `UNDERFLOW|INVALID` but not
`MSF_FLAG_OVERFLOW` (exists, `include/muse_softfloat.h:69`), against the
design entry's "overflow/underflow/invalid" guard. Behaviorally masked on
this catalogue: every overflow path in the EFT also raises INVALID
(TwoProduct `fma(a,b,-inf)` ⇒ NaN), and all 4 guard rows yield UNCERTAIN
at stage 3 under the corrected build. Latent deviation, note-grade.
(a3) Measured host proof does not reproduce the ledger claim: IW1 SHA-256
`3c6b85800687b9b77c3b815224630d50ad23026cd3cf8ce15a87cf8b3c614e0c`
(≠ claimed `ce81d66e…a9aec`), 710 rows, sphere UNCERTAIN 470/107/4
(≠ 488/139/4), 616,723 ops (≠ 616,754). Cause is (b1): rebuilding with
`-DIW_RM_LO=MSF_ROUND_TOWARD_NEGATIVE` (P1) reproduces the claimed hash,
counts, and op total **exactly**, plus the parcel's staging numbers
(tangent400 decided 0/285/400; limb UNCERTAIN band 63, see below). The
parcel report therefore describes a correctly-rounded build, not the
shipped copy.
note The header's claim (`interval_workload.h:20-23`) that the
`IW_RM_LO`/`IW_RM_HI`/`IW_STAGE3_GUARD` defaults "are the correct
behaviour" is false for `IW_RM_LO`. Line-by-line audit otherwise passes:
EFT preconditions (RN TwoSum/FMA-TwoProduct, capacity/distillation caps,
100-iteration dominance with RU remainder bound on its own flags word),
box outer/inner rounding swap with explicit axis-parallel branch on exact
comparisons, torus 3D-form evaluation over t∈[0,11] with dyadic bisection
in t-order, per-ray op cap (cap-hit→UNCERTAIN), HIT only on chained
proven-OUT + point-proven-negative bracket. No hardware float words and no
allocation calls in the core (one English "error-free" false positive);
host main clean.

## Mutants (scratch copies, watched against my audit)

| mutant | result |
|---|---|
| M1 lo swapped to RU (`-DIW_RM_LO=…POSITIVE`) | FAILS: 1333 violations, 244 s1-wrong, 50 s2-wrong, 243 flips, final-wrong id 685 guard HIT vs MISS |
| M2 RN everywhere | FAILS: 1332 violations, 224 s1-wrong, 55 s2-wrong, 223 flips, final-wrong id 685 |
| M3 Number form (`minimum_number`) | audit-inert on this catalogue (hash unchanged); **refused by the source scan** (shipped core fails the gate) |
| M4 guard off (`-DIW_STAGE3_GUARD=0`) | FAILS: guard rows 684/685 decided s3=HIT; id 685 decided-wrong (exact MISS); cf. baseline/M4 guard rows printed in `08_mutants.sh` |
| P1 positive counterpart (correct RD lo) | PASSES: 0 hard violations, 0 wrong, 0 flips; hash == claimed `ce81d66e…` |
| M3-fixed + RD (`minimum`, scan-clean) | PASSES identically to P1; scan clean |

## Further probes (all scripted)

- Monotonicity: stage UNCERTAIN non-increasing (baseline 470≥107≥4;
  P1 488≥139≥4), zero flips; torus tol-halving identical decisions, no
  flips, UNCERTAIN 0→0 (`06_run_compare.sh`).
- Op cap: `--cap 100` ⇒ 5/5 torus UNCERTAIN, all `caphit=1`.
- `smoke`: PASS in 22 s. `standard`: PASS in 52 s (1,117,504 vectors),
  both untouched in-copy, copy clean after.
- Claim surface vs parent `b704b4c`: exactly the 6 brief-owned files;
  1419 hand-written lines ≤ 3500; metrics row present; all 710 catalogue
  rows carry provenance, ids 1–710 contiguous (`13_surface.sh`).
- Survey-count sanity, recomputed: tangent400 naive disagreements 386 ✓;
  limb exact crossing steps 29/30 ✓, 31 TANGENT0 + ~31-step naive
  displacement ✓, s1-UNCERTAIN band 47 shipped / 63 under P1 (claimed 63 —
  matches only the corrected build); torus march-miss id 710
  (exact HIT / naive MISS) ✓; TSV naive column matches recomputation on
  all 710 rows.

## Counts

710 rows (693 sphere / 12 box / 5 torus). Baseline: 485 hard violations,
4 NaN-interval-safe rows, 0/0/0/0 decided-wrong (s1/s2/s3/final), 0 flips,
guard 4/4 UNCERTAIN, TSV-exact mismatches 1 (id 2), TSV-naive mismatches 0.

## Not done

Board sample / on-silicon hash match (lead work after merge; gates any
on-silicon sentence); per-op board bench; the fixes themselves (a verifier
fixes nothing). `standard`/`smoke` re-verified here; no other gate left
unrun. Times are records only.
