# verifier-w5alg2 (SF-2 Step 2b hypot) - verification note

Copy: `worktrees/verify5-alg2` (HEAD `6aa816c`, parent `0f08aa3`).
Verdict: NOT READY. Full evidence:
`scratch/verifier-w5alg2/report.md` (first line NOT READY).

## Findings

- (b) F1: `hypot_core` computes `tail`/`pdrop` but feeds the pack
  remainder-only sticky in ALL builds (`msf_alg.c:267-273`;
  compiler-confirmed dead stores). Fabricates exactness on
  wide-gap pairs: seeded f32 116,851/200,000 pairs wrong, f64
  188,323/200,000; tp rounds down (`msf32_hypot tp 3fc00000 1`:
  kernel `3fc00000/00`, file+truth `3fc00001/10`). Also fails
  every `-Werror` build (host + target).
- (b) F2: `(+-0, +-0)` returns the first operand's sign, not `+0`
  (`msf_alg.c:205`): `(-0,+0)`/`(-0,-0)` -> `-0` in all formats
  x 5 modes (30/3,870 specials decisions).
- (b) F3: one committed line wrong: `alg-f16.vec:1206`
  `msf16_hypot te 0 8000 -> 8000 00` (want `0 00`).
- (a) F4: `msf32_hypot` missing from `tables/implemented.tsv`
  (44/45 implemented; parity broken); regen drifts header,
  dispatch (live -> NULL), COVERAGE (implemented -> planned).
- (a) F5: copy generator `hypot_round_sqrt` flags inexact only on
  `val*val > S`: regen REFUSES (`DISAGREE msf16_hypot 3c00 3c00`
  exact-py `00` vs MPFR `10`).

## Gates

Own decider (integer/Fraction, MPFR-cross-checked 300k/0mm;
integer twin self-tested 300k/0mm) vs kernel: f16 pool sweep
6,553,600 decisions / 10 mm (F2 only); f16 seeded 1.5M / 0;
f32/f64 directed+seeded FAIL per F1; committed replay 7,500
lines: file 1 mm (F3), kernel 1,311 mm. Specials 3,870 / 30 mm
(F2). Ties 20/20 kernel==truth; study tie te==ta==`087a`
(ledger `087a/0879` is a typo). Smoke FAIL (drift), standard FAIL
(same), target FAIL (`-Werror`). Seam 44/45. rSqrt half untouched
(kernel + vectors pure-addition).

## Jam adjudication (mine)

Copy floor != jam (1,527,435/8,553,600 kernel divergences; jam ==
truth 300k/0mm, floor wrong). Mandated floor-full == jam packed:
f16 model 825,340 pairs 0 divergences; 3 constructed site-1
cross-square witnesses (Qj=Qf+1, dirty) agree floor==jam==truth
x5; f64 2M model volume result in the report (s08c). Addendum
CONFIRMED; "jam must fail" does not occur for shr_jam (ties
20/20 pass); NOSTICKY is a no-op macro here.

## Not done

Board work (lead); VECTORS.md tag wording (escalated, no gate);
rSqrt re-sweep (inherited green, out of scope); `cr_hypot*`
(optional; random-volume cross-square count is 0, mechanism
covered by 3 constructed witnesses + parity analysis). Copy
untouched (status clean). Scripts: `scratch/verifier-w5alg2/`
(s00-s13 + deciders + harness + classifiers + logs).
