# verifier-w5aug

## 2026-10-29 — verdict NOT READY (5 findings + 2 disproved claims)

Copy `worktrees/verify5-aug` @ e784ee7 (parent bce49e0), clean
before and after (git status empty; all builds/probes outside the
copy in scratch/verifier-w5aug). Own exact-integer Clause 9.5
reference written for this verification (myref.py: integer grid
RTTZ with ties to smaller magnitude, exact residuals, ratified
P1=R2 table; not ported from the parcel generator). The copy's own
harness and runner rebuilt outside the copy as second routes (x86-64
gcc 16.1.0 via the run.sh PATH; FLT_EVAL_METHOD=0). No parcel
branch/worktree, key files, lead scratch, parcel scratch, or
lead ledger touched; the forbidden-name rule observed throughout.

Findings:
- F1 (a) kernel: `src/msf_roundpack.c:60-64` round_inc for
  MSF_IROUND_RTTZ is character-identical to ties-to-even
  (`|| (cand & 1u)`), against its own comment, the P5 pin, and
  p069 L10-12. Every exact tie with an odd smaller-magnitude
  neighbour rounds the wrong way, including the overflow-threshold
  tie (inf+O+I instead of max-finite+none). Repro: one-cell
  `f16/add/ovf-threshold-tie 7bff 4c00`, or pool (604678 BAD, every
  want==myref). TE_HEAD mutant is a 0-diff no-op, disproving the
  HEAD message's "te-head refusing" claim with it.
- F2 (a) kernel: `src/msf_aug.c:277` zero sign `||` should be `&&`
  (6.3: difference of like signs exactly zero takes +0; ledger and
  committed generator agree). add(+0,-0), add(-0,+0), sub(+,+),
  sub(-,-) and all cancellations deliver -0/-0. Repro: one-cell
  `f16/sub/zero+zero 0000 0000` (got 8000/8000, want 0000/0000).
- F3 (a) kernel: `src/msf_aug.c:352` mul unrepresentable-residual
  cell sets INEXACT only; p070 L21 and the ratified row require
  underflow+inexact (tail bits already right). Repro: every pool
  mul-inexact-tail case (542720, got /10 want /18).
- F4 (a/b) evidence: `tests/vectors/aug-f64.vec:554` flags 18 on a
  P1 tiny-exact add cell (twin :555 has 00); the committed
  generator emits 00 and would refuse 18. Regen diff is that line
  only.
- F5 (b) seam: `tables/operations.tsv:148` augmented_mul
  rounding=attr vs P4=fixed and vs committed dispatch (has_rm=0)
  and COVERAGE (fixed). Regen flips 3 dispatch rows + 3 COVERAGE
  rows; `tools/run.sh smoke` fails officially at the drift gate.
  Regen'd dispatch would additionally mark all committed aug-mul
  lines malformed (runner.c:427-431 needs !has_rm).

Disproved HEAD-message claims: pool "0 mismatches" (committed
harness x86-64: 5505024 total, 604678 mismatches, FAIL) and "six
mutants refused" (te-head: 0 diffs; other five switches live).
"ARM -Os/-O3 clean" re-verified true.

Evidence: one-cells 1045 (796 pass; 249 = 153 F1 + 24 F2 + 72 F3,
zero unexplained); committed vectors 138380 (myref agrees 138379;
runner FAILs 17394 = 17393 file-right + 1 kernel-right f64:554);
f16 pool (unmodified harness) census re-adds, all BAD want==myref;
full-op `pairs add 0 65536` = 4294967296 cases, census re-adds,
105938944 mismatches (63488 F2 + 69185536+36689920 F1, rest 0);
slice `pairs add 0 8192` = 536870912 cases, census re-adds,
13153196 mismatches (F1+F2 shapes only); adapted-harness
faithfulness 300768/0 vs myref; regen twice stable both
generators; boundary search 9264 f32/f64 cases, 0 new;
ARM -Os/-O3 -Werror clean, integer-only symbols; fake-serial board
replay 96 pair cells PASS with byte-identical whole-run hash
(8648ecf5…); committed `unit` PASS. Full record:
scratch/verifier-w5aug/report.md (first line NOT READY).
For: lead
