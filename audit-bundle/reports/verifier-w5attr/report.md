NOT READY — 3 (a) + 2 (b) findings; copy fails its own smoke and 966 committed lines

Copy: worktrees/verify5-attr @ 2f5e79d (parent 889ec2e). Scripts + logs:
scratch/verifier-w5attr/{00-env,01-rmaudit,02-stringprobe,03-tavector,
04-berkeley,05-determinism,06-census,07-sqrt,08-control,09-trigrelabel,
10-selfreplay,11-relabdiff,12-regen,13-strref,14-hexref,15-hextie,
16-fullreplay,17-gate}.sh, out-*.log. Git Bash, MSF_PYTHON pinned to
workspace .venv (Python 3.12.15), gcc 16.1.0 x86_64-w64-mingw32.
(New PATH/TMP lesson, recorded in scripts: gcc needs
/c/msys64/mingw64/bin first on PATH and TMPDIR/TMP/TEMP in scratch.)

## Per-family ta evidence (my counts from committed sets + own runs)

| family | ta lines | decided | relabeled | own replay |
|---|---|---|---|---|
| arith f16/f32/f64/xf | 2328 (612/528/621/567) | 2328 | 0 | PASS all 4 files |
| conv/misc/rint/traps | 1258 (168+349+223+92+205+108+108+5) | 1258 | 0 | PASS all files |
| fma+sqrt | 1014 (348/196/470); sqrt-ta 1095 total, 144 narrowing | 1014 | 0 | PASS all 3 files |
| str from/to dec+hex | 2667 (840/357/1140/330) | 2667 | 0 | 965 ta FAIL (924 to-dec, 41 from-dec); hex PASS |
| trig sinPi/cosPi | 10873 | 0 | 10873 | 1 FAIL (f64:8 flags) |
| pack16/32/64 (internal) | 3718 (1232/1232/1254) | pre-existing | — | PASS all 3 files |
| total | 21858 (=21,861 grep hits minus 3 `# ta lines:` comments) | 10985 | 10873 | 39/42 files PASS, 966 FAIL |

Coverage: COVERAGE.tsv 822 rows parent and copy (0 new rows); 255
rounding=attr rows (249 Tier 1 + 6 Tier 2), every one has a committed
ta line (0 missing, script 06). tz total 21,883 ≈ ta 21,858
(directed volume as designed). Claim surface vs parent is exactly the
34 brief-owned files (no COVERAGE/dispatch/formats drift — all three
regenerate MATCH except the header, see (a1)).

## Findings

(a1) Seam: generator emits a sixth value. tools/gen_tables.py:360
`MSF_ROUND_TIES_TO_AWAY = 5`, but include/muse_softfloat.h:65 `= 4`
and src/msf_internal.h:19 `= 4`. Regen differs by exactly this line
(script 05, `diff` 65c65) → copy `tools/run.sh smoke` FAILs at drift
check (script 17 log: `GENERATED FILE DRIFT:
include/muse_softfloat.h`). Runtime chain agrees today (runner ta→4,
dispatch unfiltered cast, pack arm; traced
`msf32_add ta 3f800000 bf800000 -> 0 00`, script 03) — the 5 is latent
until regen, then public value 5 hits every `default:` arm = silent
toward-zero, the study's named trap. Smallest repro: regen + `cmp`,
or run smoke. Likely fix: `= 5` → `= 4` in the prelude.

(a2) Control 3b is wired always-ok. tools/run.sh:183 ends
`... && control_ok wrong-rounding-mode-te-ta || control_ok
wrong-rounding-mode-te-ta` — both arms ok, can never refuse (compare
control 3's `|| control_bad`). The swap itself is sound: my scratch
run swaps te<->ta on arith-f32.vec → 106 FAILs, VERDICT FAIL;
unswapped → PASS (script 08). So the test catches, the wiring blinds.
Smallest repro: read line 183; or force `$R` to exit 0 and watch it
still print "refused as required". Fix: `|| control_bad`.

(a3) str generator crashes; committed str sets unreproducible.
tests/gen_vectors_str.py:101 `_round_ratio_to_int` ta arm
`inc = 2 * r > den` must be `>=` (exact tie must increment away).
Effect: from_hex_ref te==ta on every genuine binary midpoint (script
14: all 12 f16 candidates same; script 15: ref says 0x3c00, kernel
rightly 0x3c01), so `gen_from_hex_ties` finds zero → `directed`
dies `AssertionError: f16` (script 12). f16/f32/xf/f64 directed regen
twice-identical + committed-match; str regen never completes.
Committed from-hex-ties lines (720) are exact values (`0x1.8p0`),
not ties — vacuous ta coverage for from_hex. Kernel from_hex itself
is correct (pack path; hand tie 2/2 PASS, script 15).

(b1) Kernel drops exact decimal ties under ta. src/msf_string.c:421
`dec_round_inc` ta arm `return gt_half` must be
`return gt_half || eq_half` (parcel's own design entry says so).
Observed (own harness, script 02): `msf64_to_decimal(2.5,prec=1,ta)`
→ `2e+00` want `3e+00`; `-2.5` → `-2e+00` want `-3e+00`;
to_hex study case correct (`0x1.01p+0`); below-half discriminator
correct; beyond-H tie string packs to 2.5 under both modes (two-step
semantics, as the study predicts). Committed vectors confirm:
to-decimal-str 924/924 fails are ta, from-decimal-str 41/41 are ta
(script 10/16). Smallest repro: script 02, or
`runner verify tests/vectors/to-decimal-str.vec`.

(b2) One committed relabeled trig line is wrong.
tests/vectors/trig-f64.vec:8
`msf64_sin_pi ta 0 -> 0 01 mpfr640-trig:specials-ta-relabel`:
te mate (line 4) and kernel both give `0 00`. f16/f32 zero lines are
correctly `00`. Of 10,873 relabeled lines this is the only one whose
flags differ from its te mate (script 11). Generator source copies
exp[0] verbatim (gen_vectors_trig.py:339-342), so no run of the
committed generator reproduces `01` from a `00` te set — reservation:
a flickering decider across two assembly runs is not excluded (no
decider rebuild here). Kernel is correct (exact zero, no inexact).
Smallest repro: `runner verify tests/vectors/trig-f64.vec` → 1 FAIL.
Fix: `01` → `00` on that line (then re-derive why it appeared).

Note (no-exact-ties, my second read): trig scope sound — a tie needs
a p+1-bit odd-LSB midpoint (dyadic rational, hence rational); Niven
restricts sinPi/cosPi of dyadic x to irrational or {0,±1/2,±1}, none
a midpoint at any binade incl. the subnormal grid; settled specials
exact and mode-independent (zero-sign cells verified in committed
sets). Sqrt scope = homogeneous/widening only (parcel correction
stands): 144 committed narrowing sqrt ta lines are decided, and my
relabel control fails exactly 33/144 (the ties) while
homogeneous/widening relabel passes 272/272 (script 07). Never relabel
narrowing sqrt.

Independent oracle: Berkeley `-rnear_maxMag` level-1 via pinned
testfloat_gen, 7 fns (f32_add/mul/div, f16_add, f32_sqrt, f32_to_f16,
i32_to_f32), 187,428/187,428 PASS flags-exact (script 04).

## Not done (named, not silent)

- `standard` in the copy: not run (blocked — smoke fails at drift;
  standard's prefix). Vector stage covered instead by own-runner
  replay of all 42 committed files (script 16).
- Trig regen determinism + decider rebuild (MPFR): not run; (b2)
  origin (hand-edit vs decider flicker) unresolved.
- Berkeley beyond the named 7-function subset (parcel's 51-function
  gate): not repeated. No level-2. MPFR-RNA route: untouched (unused).
- Board sampled replay: lead post-merge per brief, not run.
- Tie-witness recount (parcel's 2,143): not independently recounted.
- Times are records only; no wall-time claims needed for NOT READY.
