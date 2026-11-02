# Ledger: verifier-w4interval (Step 1c planted-copy verification)

Verdict: **NOT READY**. Copy `worktrees/verify4-interval` @ `b577456`
(parent `b704b4c`), clean throughout. Report:
`scratch/verifier-w4interval/report.md`. All probes ran from script files
in `scratch/verifier-w4interval/` under Git Bash with `MSF_PYTHON` pinned
to the workspace `.venv`; the copy was never modified.

Findings (repros in the report; row ids are catalogue ids):

- (b) `IW_RM_LO` defaults to RN (`interval_workload.c:8`), not RD: 485
  hard containment violations over finite-interval endpoints (tangent400
  303, limb 163, adv2k 18, ordinary 1; smallest: id 4 s1, id 6 s2), 0
  decided-wrong on this catalogue by luck. Measured IW1
  `3c6b85…0c`, 470/107/4, 616,723 ops — none matching the parcel claim.
- (b) Generator oracle sign error (`b*b + a*c`,
  `gen_interval_catalogue.py:69`): regeneration crashes in `fam_limb`
  (assertion, line 186) — byte-identical gate fails, no output.
- (b) TSV row id 2: exact column `MISS` contradicts its own `exact_extra`
  (`+3155251/8796093022208`, HIT) and independent recompute.
- (a) `min64` uses suppressing `msf64_minimum_number` (:44); the
  no-`*_number` source-scan gate fails on the shipped core (behaviorally
  inert here; scan is the catching oracle).
- (a) `guard_tripped` omits `MSF_FLAG_OVERFLOW` (masked here: overflow
  paths also raise INVALID; guard rows UNCERTAIN verified).
- Positive counterpart `-DIW_RM_LO=MSF_ROUND_TOWARD_NEGATIVE` reproduces
  the claimed hash `ce81d66e…a9aec`, counts 488/139/4, 616,754 ops, and
  staging 0/285/400 + limb band 63 exactly — the parcel measured a
  correctly-rounded build, not this copy.

Mutants watched failing: RD/RU swap (1333 viol, 244+50 wrong, 243 flips),
RN-everywhere (1332 viol, 224+55 wrong), guard-off (decided-wrong id 685
guard HIT vs exact MISS). Monotonicity (stage + tol-halving), op-cap
(5/5 UNCERTAIN, caphit), `smoke` PASS, `standard` PASS (1,117,504 vectors).
Claim surface exactly the 6 brief-owned files; 1419/3500 lines; provenance
on all 710 rows; survey counts recomputed (tangent 386 disagreements,
limb crossing 29/30 with 31 TANGENT0, torus march-miss id 710).

Not done: board sample / silicon hash / per-op bench (lead work, gates
on-silicon sentences); fixes (verifier fixes nothing).
