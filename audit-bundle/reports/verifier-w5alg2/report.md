NOT READY

# verifier-w5alg2: SF-2 Step 2b hypot verification of worktrees/verify5-alg2

Role: verifier-w5alg2. Copy: `worktrees/verify5-alg2` (detached HEAD
`6aa816c`, parent `0f08aa3`). Never consulted: `worktrees/w5-alg2`,
any other worktree, `ledger/lead.md`, `scratch/lead/`,
`scratch/parcel-w5alg2/`; nothing with `cft` in its name opened,
searched, or listed; no board flashing. Governing: brief
`ledger/briefs/verify-w5alg2.md`, the copy's `docs/studies/SF-2.md`,
the parcel ledger `ledger/parcel-w5alg2.md` (addendum adjudicated,
not trusted), study `scratch/sf2-algebraic/report.md` Secs.
3.2/5.2/6. Method: clean-room - my own exact decider
(`mydecide.py`, integer/Fraction arithmetic from the study design),
a fast integer twin (`fastdec.py`, proved equal on 300,000
decisions), a C probe harness linked against the copy's sources, and
the MPFR oracle decider from the copy (executed, values only).
All runs from script files in `scratch/verifier-w5alg2/` under Git
Bash, `MSF_PYTHON` = workspace `.venv` Python 3.12.15, `ulimit -v`
ceilings per script (see the env caveat in Sec. 10).

## 1. Verdict

NOT READY. Five findings: three wrong-answer (b), two
regression/evidence-chain (a). The shipped kernel fabricates
exactness on most wide-gap f32/f64 pairs (dropped tail+parity
sticky), mis-signs two signed-zero pairs, and does not compile
under the project's own `-Werror`; the seam is missing
`msf32_hypot` (44/45 implemented, parity broken, 3 generated files
drifted); the copy's generator cannot regenerate the committed
vectors (its exact-py flag rule disagrees with MPFR); one committed
f16 vector line is wrong. Smoke, standard, and target-compile all
FAIL. Counts below are measured, not estimated.

| # | class | defect | smallest repro |
|---|---|---|---|
| F1 | (b) | tail+parity sticky computed but never fed to the pack (remainder-only in all builds) | `msf32_hypot tp 3fc00000 1 -> 3fc00001 10` (file:3049): kernel `3fc00000/00` |
| F2 | (b) | signed-zero pair returns first-operand sign, not +0 | `msf16_hypot te 8000 0` kernel `8000`, want `0` |
| F3 | (b) | one committed f16 expectation wrong | `alg-f16.vec:1206 msf16_hypot te 0 8000 -> 8000 00`, want `0 00` |
| F4 | (a) | `msf32_hypot` missing from `tables/implemented.tsv` | regen flips header/dispatch/COVERAGE to `planned`/NULL |
| F5 | (a) | generator `hypot_round_sqrt` flags `val*val > S`, drops inexact on downward rounding | regen refuses: `DISAGREE msf16_hypot 3c00 3c00` exact-py `...00` vs decider `...10` |

Gate outcomes: vector regen REFUSES (rc=1); table regen DRIFTs 3/4
files; `smoke` FAIL (drift check); `standard` FAIL (same);
target-compile FAIL (`-Werror=unused-but-set-variable` on `tail`,
`pdrop`).

## 2. Own decider and its validation

`mydecide.py` decides hypot from first principles: decode to
`(sig, exp2)`, specials in the study Sec. 5.2 evaluation order
(sNaN first, then any-inf to +inf, then first-qNaN, then both-zero
to +0), else exact `S = A^2 + B^2` as a Fraction, exact
floor-root plus exact midpoint compare at the delivered
granularity, per-mode choice (te/tz/tp/tn/ta, ta = away/up, ties
detected exactly, never by float), overflow iff the unbounded
precision-p rounding reaches `2^(emax+1)`, tiny iff it is below
`2^emin`, underflow = tiny AND inexact, inexact iff the delivered
value differs from the exact value. A bit-accurate u128 window
simulation (`window_sim`: floor-full / jam / dropped forms) plus a
pure-function pack model (`pack_pure`, guard/round/sticky from fed
bits, no truth consulted) supports the jam adjudication.

Validation (kernel-independent): mydec vs the copy's MPFR decider
(`alg_decider.c decide`, executed) on 60,000 seeded finite pairs
(20k/format): 300,000 decisions, 0 mismatches (s02). `fastdec.py`
(integer-only twin) vs `mydecide.py` on the same 60k pairs:
300,000 decisions, 0 mismatches (s03b). Specials are table reads on
both sides here and are audited separately against hard-coded
study cells (Sec. 6), not against either decider.

## 3. Paper re-derivation (floor-sum lemma, window bounds)

Floor-sum lemma: `isqrt(floor(N)) = floor(sqrt(N))` for `N >= 0`.
Proof: let `m = isqrt(floor(N))`, so `m^2 <= floor(N) <= N`, hence
`m <= sqrt(N)`; and `(m+1)^2 >= floor(N)+1 > N` (a square strictly
above `floor(N)` is at least `floor(N)+1`), hence `m+1 > sqrt(N)`.
So `m = floor(sqrt(N))`. The kernel's `Q = isqrt(rad)` with exact
`rad = floor(sum at window scale)` is therefore exactly
`floor(true * 2^(-E))`, and with `sticky = (true != Q)` the pack
sees the exact guard/round/sticky of the true value (pack-feed
lemma, study Sec. 2.1).

Window bounds (re-derived): squares `sa, sb <= (2^p-1)^2 < 2^106`
single `msf_u128_mul_u64_u64` products. `la2 = bitlen(sa) >= 1`
(the larger operand is nonzero), `lsh = 121 - la2 in [15, 120]`,
`a_win = sa << lsh in [2^120, 2^121)`. `net = lsh - 2*(ea-eb)`;
`ea >= eb` holds under the ordered magnitudes (design-entry
lemma: a smaller ea bounds the value below `2^p * 2^eb`, and a
subnormal carries the minimum decode exponent; checked
empirically on all sweeps, both operand orders). If `net >= 0`,
`sb << net` satisfies `sb*2^net <= sa*2^lsh` as values (from
`|b| <= |a|`), so `tot < 2^122`; else truncation with the tail bit
keeps `tot < 2^122`. `2*(ea-eb)` and `2*ea - lsh` fit `int32`
(f64 extremes `+-2097`, `+-2373`). Shifts: right-shift counts
`>= 128` clamp to zero in `msf_u128_shr` (read
`src/msf_wide.c:130-153`); left shifts in the `net >= 0` arm are
`<= lsh <= 120`. `rad < 2^122`, so the 61-iteration root search
(`k = 60..0`) covers `Q`. `tot` cannot wrap mod 2^128
(`tot < 2^122`). The ordering compare `msf_cmp_finite` only shifts
when top-bit positions agree, so shift counts stay `< 128` (read
`src/msf_decode.h:146-157`).

Margin (sliver argument): `Q` carries `>= 60` bits against
destination `p <= 53` (at least seven bits below the destination
significand in normal binades; more below the subnormal ulp under
the clamp), so no rounding boundary (multiple of half-ulp) can lie
strictly inside the fed sliver `[Q*2^E, (Q+1)*2^E)`: two distinct
multiples of `2^E` differ by at least `2^E`, while a boundary
strictly inside would differ from an endpoint by a nonzero
multiple of `2^E` smaller than `2^E`. Hence the pack's
`(guard, round, sticky)` decision from fed bits plus a sound
sticky matches the truth's side in all five modes, ties arrive as
`guard=1, round=0, sticky=0` (dyadic at half-ulp, hence exactly at
`Q` scale since the margin is `>= 1` bit), and exactness is exact.
This is the soundness proof of the mandated floor-sum-plus-sticky
form (F1 is precisely its violation: the copy feeds
remainder-only sticky).

## 4. Sticky-assembly audit, arm by arm (`hypot_core`, lines 174-277)

- Tail arm (lines 228-244): `net < 0` truncates with
  `tail = any_bits_below128(sb, -net)`. Read `any_bits_below128`
  (lines 163-172) and `msf_u128_shr` (wide.c:130-153): correct for
  all shift counts including `>= 128` (returns zero; tail still
  reads the unshifted `sb`). Verdict on the arm's LOGIC: sound -
  but its VALUE is dead: `tail` is never ORed into `sticky`
  (line 267 assigns `sticky = !is_zero(rem)`; the `#if` block at
  268-274 re-assigns the identical expression). Compiler-confirmed:
  `-Wunused-but-set-variable` for `tail` in the floor build,
  `-Wunused-variable` under `MSF_ALG_TEST_JAM` (s01 logs).
- Parity-drop arm (lines 247-255): odd-`ew` shift drops
  `tot.w[0]` into `pdrop` (floor) or jams it into `rad.w[0]`
  (JAM). Same verdict: `pdrop` never reaches `sticky`; dead in all
  builds (compiler-confirmed as above).
- Remainder arm (lines 259-267): `Q = isqrt(rad)`,
  `rem = rad - Q*Q`, `sticky = (rem != 0)`. This is the ONLY live
  arm in every build, including under `MSF_ALG_TEST_NOSTICKY`
  (lines 268-274 re-assign the same expression, so the NOSTICKY
  macro is a no-op in this copy: floor == nosticky, bit for bit).
- Census (s04b, binary16 pool sweep, 825,340 finite pairs):
  `tail=1`: 0; `pdrop=1`: 0; `rem==0`: 127,122. The window always
  covers both squares at binary16 (exponent gap `<= 29`, alignment
  `lsh >= 99`), so F1 is invisible at f16 and every f16 check
  passes. At f32/f64 the tail arm fires on most wide-gap pairs and
  the dropped value fabricates exactness (Sec. 5, F1).
- Consequence chain of F1: `-Werror=unused-but-set-variable`
  fails the host build (smoke) and the target build (s11/s12 logs);
  inexact is dropped (flags `00` instead of `10`); tp (and ta-up
  cases with fraction above mid) round the wrong way
  (Sec. 5 counts).

## 5. Kernel-vs-truth differentials (all counts printed)

Oracle throughout: `fastdec` (== mydec, Sec. 2). Kernel: floor
build (shipped code path).

- Binary16 pool sweep (s04): boundary pool of 20 as first operand
  x all 65,536 second-operand encodings = 1,310,720 pairs x 5
  modes = 6,553,600 decisions: 10 mismatches, all the F2
  zero-sign class (`(8000,0)`, `(8000,8000)` x 5 modes). Zero
  tail-class mismatches (consistent with the Sec. 4 census).
- Binary16 seeded volume (s05): 300,000 pairs (specials-bearing,
  unfiltered) = 1,500,000 decisions: 0 mismatches.
- Binary32/64 directed (s05): 448 pairs each (boundary pool
  squared both orders, exponent lattice both orders, subnormal
  corners, Pythagorean exacts, sign variants) = 2,240 decisions
  each: 860 mismatches each = 20 zero-sign lines (F2, duplicated
  pairs counted per instance) + 840 tail-class lines (F1). Exact
  families (3-4-5 etc., 48 pairs): 0 mismatches (exactness path
  unaffected).
- Binary32/64 seeded finite (s05): f32 200,000 pairs = 1,000,000
  decisions: 584,255 mismatches (116,851 pairs, 58.4%); f64
  200,000 pairs = 1,000,000 decisions: 941,615 mismatches
  (188,323 pairs, 94.2%). Signature (s05 classifier): same-bits
  `inexact-dropped` on te/tz/tn/ta (kernel `00` vs truth `10`)
  plus `bits-diverge` on tp (kernel rounds down to the fabricated
  exact, e.g. `msf32_hypot tp 3f800000 1`: kernel `3f800000/00`,
  truth `3f800001/10`). Smallest committed repro: file line 3049
  `msf32_hypot tp 3fc00000 1 -> 3fc00001 10`; kernel gives
  `3fc00000/00` (quoted by direct harness run, s05 logs).
- Committed vector replay (s09): 7,500 hypot lines (500 pairs x 5
  modes x 3 formats). fastdec-vs-file: 1 mismatch (F3, the single
  f16 `(0,8000)` te line). kernel-vs-file: 1,311 mismatches =
  f16: 11 (10 F2 kernel-wrong + 1 F3 file-wrong, kernel right);
  f32: 605 (470 directed + 85 seeded + 10 specials + 40 ties-tagged
  wide-gap tail witnesses); f64: 695 (470 + 175 + 10 + 40).
  The 470 directed lines are all F1 tail-class (split:
  376 inexact-dropped + 94 tp bits-diverge, zero zero-sign lines -
  zeros live in the specials family: 10 lines = the two F2 pairs).
  The 40+40 ties-tagged kernel failures are the "wide-gap
  exactness boundary" pairs (e.g. `msf32_hypot tp 3fc00000 1`),
  tagged ties but actually tail-sticky witnesses.

## 6. Specials (whole table, both operand orders; s06)

774 hard-coded study-cell cases (sNaN payloads/signs x every
class both orders; inf x {inf, qNaN payloads, finite, zero} both
orders and both signs; qNaN payload/sign matrix both orders;
all four signed-zero pairs) = 3,870 kernel decisions: 30
mismatches, ALL the F2 zero-sign class (`(-0,+0)`, `(-0,-0)` in
all 3 formats x 5 modes: kernel `-0`, table `+0`). sNaN-first
(invalid + first-sNaN quieted, 1,800 decisions): 0. inf-over-qNaN
(660): 0, both orders. qNaN matrix incl. payloads/signs,
first-wins (1,350): 0. Flags exact everywhere checked.

## 7. Ties (s07/s09/census; study tie adjudicated)

- The study tie (`1580*2^-24, 1659*2^-24`, i.e. f16
  `(062c, 067b)`): truth `2291*2^-24`, an exact midpoint between
  `2290` and `2292`. te -> `087a` (even), ta -> `087a` (away =
  up = the even candidate): te == ta. The kernel, the file
  (`te/ta 087a/087a`, inexact set), mydec, and MPFR agree. The
  parcel ledger's `087a/0879` rendering is a ledger typo (ta-down
  would violate ties-to-away); the committed file is correct.
- My Euclid-triple construction (odd (p+1)-bit hypotenuse, <= p-bit
  odd legs, several exponents): 18 exact ties (6/format), all with
  te != ta (even-is-down cases). Kernel floor == truth on all 18
  x 5 modes (defect needs wide gaps; ties need both squares live,
  so ties are unaffected by F1).
- Committed census: file te != ta pairs = 17/16/16 (f16/f32/f64).
  The f16 17th is the F3 planted zero line (`(0,8000)` te/ta
  `8000/0`); the other 16+16+16 are true even-is-down ties, and
  ta == away-up on every one (file matches mydec on all of them).
  Subnormal-output hypot lines: 222/format (666 total); all
  match mydec (flags, underflow where due).
- Floor is RIGHT on the tie families (20/20 tie pairs kernel ==
  truth, Sec. 5 + this section). The brief's "jam must fail the
  tie family" does not occur for the shr_jam mutant in any
  realization tested: jam kernel == truth on all 20 tie pairs
  (s08b extension), because jam preserves the stickiness the
  floor build drops.

## 8. Jam adjudication (my own: construct + exhaust + reasons)

Question: can the shipped floor form and the `MSF_ALG_TEST_JAM`
form ever diverge, and is floor right on ties.

- Divergent in THIS copy: YES. floor-kernel vs jam-kernel (s08):
  f16 pool sweep 6,553,600 decisions: 0 divergences; f32 seeded
  1,000,000: 585,145 divergences; f64 seeded 1,000,000:
  942,290 divergences (total 1,527,435 / 8,553,600). Direction:
  jam == truth (s08b: jam-kernel vs mydec, 300,000 decisions, 0
  mismatches), floor wrong. Cause: in this copy floor feeds
  remainder-only sticky while jam preserves the dropped tail by
  jamming it into the sum (sticky survives as `rem != 0`).
- The parcel addendum's claim is about the MANDATED floor-full
  form (floor + full sticky), not this copy's dropped feed.
  Adjudication of THAT claim, independently:
  (a) f16 model census (s04b, 825,340 finite pairs): floor-full
  packed == jam packed == truth on all pairs, 0 divergences;
  (b) f64 model volume (s08c, 2,000,000 seeded pairs):
  floor-full packed == truth on all pairs (0 divergences);
  jam packed == truth on all pairs (0); jam packed ==
  floor-full packed on all pairs (0); cross-square witnesses
  in the random volume: 0; jam fabricated-exact: 0.
  Dropped-model packed != truth: 1,884,706 pairs (94.2%) -
  matching the copy kernel's 94.2% seeded mismatch rate,
  confirming the dropped model IS the shipped behavior;
  (c) constructed site-1 cross-square witnesses (Qj = Qf+1 on
  dirty input, built by Pell-guided search over the window
  geometry, e.g. `f64 hypot(68051dccc0ce7c5, 4a6da37c874b15a)`):
  3/3 have floor-kernel == jam-kernel == truth in all 5 modes
  (end-to-end harness runs). So a crossed square packs
  identically, as the addendum predicts: the crosser is odd,
  its bit 0 sits >= 7 bits below the destination ulp inside the
  pack's sticky region, and the sliver argument (Sec. 3) keeps
  every boundary on the same side.
  (d) reasons: the floor-sum lemma + sliver argument prove
  floor-full sound; the jam sites only ever add `< 2` radicand
  ulps inside a sliver that contains no boundary, except the
  crossed-square case, which the witnesses + parity analysis
  cover.
- Verdict: the addendum's packed-equivalence (mandated floor-full
  vs jam) is CONFIRMED by independent construction and
  measurement; the copy does NOT ship the mandated form (F1), so
  in the copy floor != jam and floor is wrong where jam is
  right. The "jam must fail" negative control cannot occur for
  shr_jam here (it passes ties 20/20 and the wide-gap family);
  and `MSF_ALG_TEST_NOSTICKY` is a no-op macro in this copy
  (Sec. 4), so neither test-only control is a live control.

## 9. Seam, regeneration, gates, target, claims

- Seam census (s10/s13): `tables/implemented.tsv` carries
  `msf16_hypot` + `msf64_hypot` but NOT `msf32_hypot` (F4): Tier 2
  is 44 implemented / 45 registered, and format parity (owner
  rule: all three formats or none) is broken at the source of
  truth. The committed generated surface claims all three
  implemented (header comment, dispatch live entries, COVERAGE
  `implemented`), so the seam is internally inconsistent:
  committed-COVERAGE inventory reads tier1 783/783, tier2 45 impl /
  0 planned / 45 reg (passes the run.sh shape), but it is not
  reproducible from the tables.
- Regeneration (s10): vector regen REFUSES (rc=1) on the first
  finite directed pair: `DISAGREE msf16_hypot 3c00 3c00:
  exact-py [(15784, 0), ...] decider [(15784, 16), ...]` -
  hypot(1,1): the copy's generator `hypot_round_sqrt` flags
  inexact only when `val*val > S` (F5), missing every
  downward-rounded inexact case (te/tz/tn/ta here); MPFR is
  right. Not byte-stable (nothing is emitted). Table regen
  (`gen_tables.py` with the pinned venv python) DRIFTs 3/4 files,
  all from F4: header `implemented`->`planned` for `msf32_hypot`,
  dispatch live entry -> NULL/`0` row, COVERAGE
  `implemented`->`planned` (exact diffs in s10 log).
- `smoke` (s11): FAIL at the first gate - `GENERATED FILE DRIFT:
  include/muse_softfloat.h differs from tables/`. `standard`:
  FAIL identically (same drift check inside its smoke prefix).
  `VECTORS.md` mpfr-alg tag rows still say rSqrt only (parcel's
  named escalation for merge touch-up; no gate depends on it -
  not a finding).
- Target-compile (s12): FAIL under the exact project flags
  (`-mcpu=cortex-m0plus -Os -Werror`): `msf_alg.c:184:24,34:
  -Werror=unused-but-set-variable` on `tail`, `pdrop` (F1's
  fingerprint). Informational relaxed build: `msf_alg.o` text
  2,224 B (== parcel's 2,224 B), `hypot_core` 0x408 = 1,032 B
  (== parcel's 1,032 B), `hypot_core` static stack 512 B
  (parcel: 520 B), undefined symbols integer-only + `memcpy`
  (matches the parcel's claim; sizes describe the defective
  kernel and are not a gate pass).
- Claim surface vs parent `0f08aa3` (s13): 13 files, +8,442/-37.
  `implemented.tsv` +2 rows (should be +3); vectors +2,502 lines
  each with 0 deletions (rSqrt sections byte-identical to parent
  - confirmed by numstat); `run.sh` comment-only; `rsqrt_core`
  body untouched (diff hunks are header comment + new helpers +
  hypot only). `msf32_hypot` kernel wrapper exists (`nm`:
  0x1a B text) - only its registration row is missing.

## 10. Environment caveat (measured, affects wording only)

Under this launcher, a script's `export` does NOT reach `bash -c`
grandchildren (probe_env5: `export -p` shows the vars, `env`
does not, `bash -c` children see empty), while python children
inherit everything (probe_env4: all three vars arrive). Effects:
(a) `tools/run.sh` ignored the pinned `MSF_PYTHON` and used
system python 3.14.5 (log line `python: python (Python 3.14.5)`);
the drift verdict is interpreter-independent and was
independently re-verified with the pinned venv python 3.12.15
(s10: identical 3-file drift set), so the gate outcome stands;
(b) `MSF_ALG_DECIDER` set in s10 DID reach its python child
(probe_env4 + no stale copy decider exists + DISAGREE output
requires the decider), so the regen refusal used my probe
binary; (c) `TMPDIR`-inside-scratch did not propagate to
children (launch temp used instead - no evidence harmed);
(d) `ulimit -v` ceilings are in-shell rlimits and held for all
sweeps. All my differentials expand `$MSF_PYTHON` in-shell, so
every python oracle ran under the pinned 3.12.15.

## 11. Not done (named gaps, not silence)

- s08c f64 model volume (2M pairs): LANDED - Sec. 8(b)
  filled (floor-full == jam == truth throughout; dropped wrong
  on 94.2%, matching the kernel).
- Board: no board flashing per the brief; sampled replay and
  planted-copy verification remain lead work.
- `VECTORS.md` hypot tag wording: named non-owned escalation
  (parcel's, for merge touch-up).
- rSqrt half: inherited green (kernel untouched, vectors
  pure-addition, Step 2a verifier closed) - not re-swept here;
  the brief scopes this verification to hypot plus seam.
- `cr_hypot*` foreign-binary corroboration: not run (optional
  per brief; MPFR + exact-Fraction oracles already agree on
  300k+ decisions and the file on 7,499/7,500 lines).
- F4's fix direction (add the row vs delist f32) and F5's
  generator repair are owner/parcel work; I changed nothing in
  the copy (git status clean throughout).

## 12. Script inventory and times

All in `scratch/verifier-w5alg2/`, Git Bash, `MSF_PYTHON` pinned,
`ulimit -v` ceilings: `s00_env.sh`, `s01_build.sh`,
`harness.c` (floor/jam probe builds), `mydecide.py` (own
decider + window sims + pure pack), `fastdec.py` (+ selftest),
`diff_pairs.py` + `s02/s03/s03b` (300k MPFR cross-check PASS;
300k kernel-floor FAIL signature), `s04_pool_f16` (6,553,600
decisions, 10 F2), `s04b_arms` (census), `s05_volumes`
(300k f16 PASS; 1M f32 584,255 FAIL; 1M f64 941,615 FAIL),
`s06_specials` (3,870 decisions, 30 F2), `s07_ties` + `census_teta`
(20 ties kernel==truth; file 17/16/16 te!=ta; 666 subnormal),
`s08_jam_kernel` (8,553,600 decisions, 1,527,435 divergences),
`s08b_jam_truth` (300k jam==truth), `s08c_f64sim` (2M: 0/0/0,
dropped 1,884,706),
`site1_witness.py` (3 constructed cross-squares, all forms agree),
`s09_vectors` (7,500 lines: 1 file-mm, 1,311 kernel-mm),
`s10_regen` (refuse + drift), `s11_runsh` (smoke/standard FAIL),
`s12_target` (FAIL + info sizes), `s13_seam_claims`,
`split_directed.py`, `classify_mism.py`, `mk_ties_file.py`,
`t_repro.txt`, `t_witness.txt`, `t_ties.txt`, probe files.
Wall times: pool sweep ~80 s, arms census ~8 min, volumes ~80 s,
jam-kernel ~30 s, f64sim ~10 min (est.), smoke/standard < 60 s
(fail fast), target < 60 s.


