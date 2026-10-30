# Verifier w5attr (SF-2 Step 1, copy worktrees/verify5-attr @ 2f5e79d)

Verdict: NOT READY. Full evidence:
scratch/verifier-w5attr/report.md (scripts 00–17 + out-*.log, Git
Bash, MSF_PYTHON pinned to workspace .venv).

Load-bearing defects (smallest repro in the report):

- (b) `src/msf_string.c:421` `dec_round_inc` ta arm `return gt_half`
  drops exact ties (must be `gt_half || eq_half`): ±2.5 at prec 1 under
  ta give ±2e+00, want ±3e+00; 924 + 41 committed str ta lines FAIL.
- (a) `tools/gen_tables.py:360` emits `MSF_ROUND_TIES_TO_AWAY = 5`
  vs committed/internal `= 4`: regen drifts one line; copy `smoke`
  FAILs at drift check. Latent silent-toward-zero if shipped.
- (a) `tools/run.sh:183` control 3b ends `|| control_ok` on both
  arms: the te/ta swap is caught by the runner (106 FAILs) but the
  control can never report refusal.
- (a) `tests/gen_vectors_str.py:101` `_round_ratio_to_int` ta arm
  `2*r > den` must be `>=`: from_hex ref blind on ties, `directed`
  crashes (`AssertionError: f16`), committed str sets unreproducible,
  from-hex ta coverage vacuous (kernel from_hex itself correct).
- (b) `tests/vectors/trig-f64.vec:8` relabeled `ta 0 -> 0 01` must be
  `00` (te mate + kernel agree); sole divergence of 10,873 relabeled.

Sound parts: 3 rm switches + 3 integer rounders all ta-armed, no
third site; to_hex arm correct; 255/255 attr rows carry ta lines, 0
new rows, 34-file surface exactly brief-owned; Berkeley ta subset
187,428/187,428 PASS; sqrt narrowing scope re-derived (33/144 relabel
fails, 272/272 wide pass); 39/42 committed files PASS outright.

Not done: `standard` (smoke-blocked); trig decider rebuild / (b2)
origin; full 51-function Berkeley gate; board replay (lead
post-merge); tie-witness recount. No copy files modified (tracked
tree clean; only ignored `build/` written by the smoke run).
