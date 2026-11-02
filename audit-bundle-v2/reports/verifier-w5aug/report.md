NOT READY

verifier-w5aug vs the copy at worktrees/verify5-aug (HEAD e784ee7,
parent bce49e0; `git status --short` clean at end of work). Own
exact reference: scratch/verifier-w5aug/myref.py (integer grid
arithmetic written from p069/p070 + ratified P1=R2 table, not ported
from the parcel generator). Runners: Git Bash, MSF_PYTHON pinned to
the workspace .venv (Python 3.12.15), x86-64 gcc 16.1.0 via the
run.sh PATH export, `ulimit -v 3000000` in scripts, one job at a
time (two only while the full-op run continued in background).

FINDINGS (disconfirm-only)

- F1 [wrong triple]: roundTiesTowardZero is implemented as
  ties-to-even. worktrees/verify5-aug/src/msf_roundpack.c:60-64
  returns `guard && (round_bit || stick || (cand & 1u))` for
  MSF_IROUND_RTTZ — character-identical to the ties-to-even arm
  (:56-57) — while its own comment (:61-63), the P5 pin
  (`guard && (round_bit || stick)`, ledger/parcel-w5aug.md:30-34),
  and p069 L10-12 (ties keep the smaller magnitude) require no
  increment on an exact tie. Exhibits (all formats symmetric):
  onecells 153 tie cells incl. the overflow-threshold tie
  (f16/add/ovf-threshold-tie 7bff 4c00: kernel inf/inf/14 vs
  max-finite/half-ulp-tail/00); pool 604678/604678 want==myref with
  20507+20507 pair-exact / 9212+9212+2322 tiny-exact /
  6846+8134 mul-combined tie shapes; boundary search 544+32.
  Corroboration: MSF_AUG_TEST_TE_HEAD is a no-op in this copy
  (0/1045 one-cell diffs vs shipped, x86-64), so the HEAD message's
  "te-head 5,478 refusing" cannot hold here.
- F2 [wrong triple]: exact-zero sign uses `||` for `&&`.
  worktrees/verify5-aug/src/msf_aug.c:277
  (`zs = da->sign || eff_b`) delivers -0 for add(+0,-0),
  add(-0,+0), sub(+,+), sub(-,-) and every add(x,-x)/sub(x,x)
  cancellation; 6.3 (difference of like signs exactly zero -> +0
  except roundTowardNegative), the ledger ("+0 on opposite-sign
  cancellation; common sign for like-signed zeros",
  ledger/parcel-w5aug.md:110-118), and the committed generator
  (`sa if sa == eff_b else 0`, tests/gen_vectors_aug.py:216-217)
  require `&&` (-0 only when both effective operands are -0).
  Exhibits: onecells 24 zero/cancel cells; pool exact-zero badkind
  46; slice exact-zero badkind 8192 (every nonzero cancellation).
- F3 [wrong triple]: the mul unrepresentable-residual cell raises
  inexact but NOT underflow. worktrees/verify5-aug/src/msf_aug.c:352
  (`*flags |= MSF_FLAG_INEXACT;` only) contradicts p070 L21
  ("raises the underflow flag and signals the inexact exception"),
  the ledger row (ledger/parcel-w5aug.md:107), and the kernel's own
  comment (:344-351). Tail bits are right; only the flag is short.
  Exhibits: onecells 72 flag-only diffs (got /10 want /18, all
  formats); pool mul-inexact-tail badkind 542720 (every one).
- F4 [wrong evidence triple]: tests/vectors/aug-f64.vec:554 carries
  flags 18 on a P1 tiny-exact add cell
  (1.0 + min-subnormal -> 1.0/min-subnormal); P1=R2 requires 00.
  Its swapped twin :555 carries 00; the committed generator cannot
  emit 18 here (tests/gen_vectors_aug.py:244-245 emits 0,
  :344-349 asserts 0); regen of the file differs by this line only
  (diff 554c554, 18 vs 00). No other add/sub line in 138380 carries
  flags outside {00,01,14}.
- F5 [non-rederiving artefact]: tables/operations.tsv:148 pins
  `attr` on augmented_mul, contradicting P4 (`fixed` for all three
  rows, ledger/parcel-w5aug.md:21-23) and the file's own comment
  (:19-22, fixed is 9.5-aug_pair-only). The committed generated
  files were built from `fixed` (tests/msf_dispatch.h:1763-1765
  has_rm=0; docs/COVERAGE.tsv:854-856 fixed); regen from the
  committed tables yields has_rm=1 / `attr`. `tools/run.sh smoke`
  therefore fails officially at the drift gate
  ("GENERATED FILE DRIFT: tests/msf_dispatch.h differs from
  tables/"). Read-through consequence: with has_rm=1,
  tests/runner.c:427-431 would mark every committed aug-mul vector
  line malformed.
- (c) HEAD commit-message claims not carried by evidence:
  "standard PASS (pool 5,505,024, 0 mismatches)" vs committed
  harness pool 5,505,024 total / 604,678 mismatches / VERDICT FAIL
  (x86-64, unmodified tests/aug_exhaustive.c); "six mutants
  refused" vs TE_HEAD a proven no-op (see F1). The message's
  "ARM -Os/-O3 clean" DOES hold (re-verified below).

PROBES (evidence per probe)

1. Own reference + one-cells/families (scratch/verifier-w5aug/
   myref.py, onecells.py, logs/onecells-x64.log): 1045 cases over
   3 formats x 3 ops (RTTZ discriminators incl. odd candidates and
   binade crossings, exact powers, overflow-tie/above/below,
   verbatim far pairs f32/f64, zero signs, P1 cells, the mul
   inexact cell, NaN/inf matrix both orders). 796 pass; 249
   mismatches = 153 F1 + 24 F2 + 72 F3, zero unexplained.
2. Committed vectors vs myref (check_vectors.py,
   logs/check_vectors.log): 138380 lines, 138379 agree, 1 differs
   (F4). Committed runner over the same files (build/runner.exe,
   logs/runner-aug-x64.log): total 138380 passed 120986 failed
   17394 VERDICT FAIL; adjudicated case-by-case with myref
   (close_fails.py, logs/close_fails.log): file-right 17393,
   kernel-right 1 (f64:554), neither 0.
3. binary16 exhaustive, FULL OP re-run: `pairs add 0 65536`
   (all 2^32 pairs, adapted harness at i686 after faithfulness
   proof faith.py 300768/0 vs myref + static shift bounds;
   logs/full-add.log): total 4294967296 (kind census re-adds
   exactly: 132911100+131076096+2+253954+8382464+63490+
   377544702+2890502824+754232664), mismatches 105938944
   VERDICT FAIL, all in three badkinds — exact-zero 63488 (F2;
   every cancellation/mixed-zero cell; only add(+,+) and add(-,-)
   correct), pair-exact 69185536 + tiny-exact 36689920 (F1 ties);
   snan/qnan/invalid/inf-exact/overflow/exact/mul-inexact-tail 0.
   Large contiguous slice `pairs add 0 8192` = 536870912 cases
   also DONE x86-64 (logs/slice-add-8k.log): census re-adds,
   13153196 mismatches = 8192 F2 + 130636+13014368 F1, no other
   shape. Standing pool leg via the UNMODIFIED committed harness
   x86-64 (logs/pool-committed.log): total 5505024 (census
   re-adds: 279390+463884+12+381066+151546+127068+1050608+
   1543042+965688+542720) mismatches 604678 VERDICT FAIL; every
   one adjudicated want==myref (logs/pool-adjudicated.log:
   want!=myref 0; shapes 46 F2 / 41166+20746+146+2322+20507x2 F1
   / 527740+6846+8134 F3 incl. combined / 3+3 F1-ovf-tie).
4. Regen (regen.sh, logs/regen.log): gen_tables twice stable;
   committed match for header+formats, DRIFT on dispatch+COVERAGE
   (F5). gen_vectors_aug twice stable; f16/f32 match, f64 differs
   by line 554 only (F4).
5. Seam (code read): operations.tsv:146-147 fixed (add/sub) vs
   :148 attr (mul, F5); header :56-68 pair types + ABI note, :1814-
   1830 nine decls with NO rounding parameter, :401-407 public
   enum ends at 4; MSF_IROUND_RTTZ=5 in src/msf_internal.h:26,
   passed only by src/msf_aug.c:86,104, handled only in
   src/msf_roundpack.c:60,124 — no caller-passable collision (5s
   elsewhere are unrelated enums); tables/implemented.tsv:849-857
   nine rows wave 5; COVERAGE tier 2 / C-754; gen_tables.py:73-75
   validates only fixed-on-non-aug_pair (attr-on-aug_pair gap
   noted). msf64 hidden-pointer ABI note present, not executed
   (no silicon; host ABI differs) — read only.
6. Flags provenance: P1 cells carry 00 in shipped builds
   (onecells pass); MSF_AUG_TEST_PACK_LEAK changes 581/1045 one-
   cells (mutdiff.py, logs/mutdiff-x64.log) proving the leak shape
   is live and shipped flags do not inherit it; P1_OPPOSITE live
   (108). TE_HEAD 0 (F1 corollary).
7. WIDTHS re-read (docs/WIDTHS.md:34-35, proof :37-133): window
   bound (kernel :222 `> 127` matches "span <= 127" window),
   verbatim gap lemma (ta==tb tiebreak shown dead: span > 127
   forces tops apart by >= 74 at f64), residual representability
   incl. the binade-crossing centred form (:77-82). Boundary
   counterexample search (bsearch.py, logs/bsearch.log): 9264
   f32/f64 binade-boundary x neighbour/cross-sign cases + far
   verbatim pairs, 2568 explained (32 F1-ovf-tie, 544 F1-tie,
   1048 F2, 944 F3), 0 NEW.
8. ARM (arm.sh, logs/arm.log): arm-none-eabi-gcc 14.2.1,
   -mcpu=cortex-m0plus -mthumb -ffreestanding, -Wall -Wextra
   -Werror: -Os clean (10 objects) and -O3 clean (10 objects);
   undefined symbols integer-only (__aeabi_llsl/llsr/lmul,
   uidiv/uidivmod/uldivmod, case tables, memcpy, intra-project),
   no float helpers at either level.
9. Board (code read + fake serial, no flashing): harness pair
   branch (board/harness_main.c:187-211) replies two results +
   folds the runner-identical canonical line; host_replay.py:99-
   116 compares both results and the whole-run hash. Fake-serial
   replay of 96 kernel-correct pair cells (sample_cells.py,
   fakeboard/ stub serial): PASS, whole-run SHA-256
   8648ecf5fea43ddcc3d69d18891c87c3c8c8b4c8c8de8ec2bde967e9c0a08284
   matches the C runner's `hash` digest byte-for-byte. Note:
   board-smoke.vec (board/run_board.sh) carries no pair lines
   (tests/gen_vectors.py:321-328); on-silicon replay is lead work.
10. run.sh smoke: host-compiler gate passes under Git Bash
    (x86_64, FLT_EVAL_METHOD=0); drift gate FAILS (F5; quoted
    above). Committed `unit`: PASS. Copy never modified
    (git status clean).

NOT DONE

- Per-mutant full-runner refusal runs (switches proved live by
  one-cell diffs instead; beyond the brief's probe list).
- On-silicon replay (lead-owned; explicitly out of scope).
- msf64 hidden-pointer ABI execution (needs the target).
