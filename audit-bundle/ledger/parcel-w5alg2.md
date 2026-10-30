
## 2026-10-28 07:10:18 -07:00 - Design entry: SF-2 Step 2b correctly rounded hypot at binary16/32/64 (3 rows), written before any code

Measured: brief ledger/briefs/w5-alg2.md read first and obeyed
exactly; governing docs/studies/SF-2.md Secs. 1, 3, 6-9 and
scratch/sf2-algebraic/report.md Secs. 3.2 (kernel), 5.2
(specials + evaluation order), 6 (recipes incl. the measured
midpoint ties), 7.3 (volumes), 8 (stops) read in the worktree /
scratch copies; the rest of the study (Secs. 1-2, 4, 7.1-7.2,
9) read as context. worktrees/w5-alg2 verified on branch
wave5-alg2 at base 0f08aa3 ("the alg1 merge commit" of the
brief), clean. Current inventory verified in-tree: operations
rows r_sqrt + hypot are registered (wave 5, tier 2, C-754,
math_un/math_bin from the Step 2a seam); tables/implemented.tsv
carries the 3 r_sqrt rows only, so Tier 2 is 45 registered /
42 implemented; include/muse_softfloat.h already declares
msf{16,32,64}_hypot as planned and tests/msf_dispatch.h carries
the three MSF_SIG_MATH_BIN descriptors - no seam work is needed
or owned here. Board wiring for src/msf_alg.c (the brief: check
it exists, escalate if not) verified present: board/CMakeLists.txt
MSF_SRC and board/run_board.sh both list src/msf_alg.c (landed
with the alg1 merge, commit 109b814) - no escalation. Shared
layers read and judged sufficient, no inadequacy in files I do
not own: msf_pack_generic (src/msf_roundpack.c:85; exact
magnitude (sig+f)*2^exp2 over msf_u128 + sticky, five internal
modes incl. ties-to-away, tininess-after flags-only unbounded
rounding at lines 130-154), msf_u128 helpers incl.
msf_u128_mul_u64_u64 / shr / shl / clz (src/msf_wide.c),
msf_decode / msf_nan_delivery / msf_cmp_finite (src/msf_decode.h),
the sqrt_core craft (src/msf64.c:235 - 120-bit radicand, bit
search, exact remainder as sticky, one pack), the shipped
rSqrt half of my own TU (src/msf_alg.c, ledger/parcel-w5alg1.md
design entry), tools/run.sh (SRC already lists src/msf_alg.c,
VECS already lists tests/vectors/alg-*.vec, TIER2_TOTAL_EXPECTED
already 45; only the freeze comment at lines 129-132 needs its
counts restated - the brief's "counts only"), the MPFR decider
precedents (tests/alg_decider.c rSqrt decide path,
tests/trig_exhaustive.c narrow() flag derivation at lines
214-268). The study's validated hypot prototype
(scratch/sf2-algebraic/proto_alg.py:276 hypot_proto) and its
153,600-decision log (out/proto2.log: HYPOT_CHECK disagree=0)
were read as the design's measuring record. For the second
reads in Sec. 3 below I read the S1 extracts directly
(scratch/S1/extract/p059.txt, p060.txt, p063.txt in full, p061
hypot line located by search) - the IEEE PDF itself not opened,
clause meaning cited by extract page + line, no standards text
reproduced beyond a few words. Fences held: nothing with cft in
its name opened, searched, or listed; no third-party
implementation source used as design input; MPFR and (optionally,
Sec. 4) foreign binaries are execution-only oracles. No code
written yet; this entry is the design gate. Format parity:
hypot ships binary16/32/64 or not at all (owner parity rule).

### 1. Registration state (no seam in this parcel)

The seam half of Step 2a already registered math_bin, the six
public declarations, and the dispatch rows. This parcel's only
inventory moves: add the 3 msf*_hypot rows to
tables/implemented.tsv, regenerate (include/muse_softfloat.h +
docs/COVERAGE.tsv change; src/msf_formats.h and
tests/msf_dispatch.h expected byte-unchanged, verified at
regeneration), and restate the tools/run.sh freeze comment to
45 registered / 45 implemented. Regeneration twice,
byte-identical (run.sh drift_check is the standing gate over all
four generator outputs).

### 2. Kernel design: hypot in src/msf_alg.c (study Sec. 3.2, exact)

One core parameterized by format, appended to the shipped TU:
hypot_core(fmt, abits, bbits, rm, flags) + three wrappers
msf{16,32,64}_hypot(a, b, rm, flags). Pure integer C11, no
allocation/recursion, no hardware arithmetic types (run.sh type
and symbol scans are the gates).

Decision [study Sec. 3.2, re-derived here]: finite operands
decode to magnitudes A*2^ea, B*2^eb (signs discarded; the
function is even in both operands, extract p061 L37). Order so
the first is the larger by exact decoded comparison
(msf_cmp_finite on the finite pair; signs do not affect it after
the specials order of Sec. 3, and both-zero returns before the
kernel arithmetic). Lemma used below: with that ordering
ea >= eb always - for two normals a smaller ea would bound the
value below 2^p * 2^ea <= the other's minimum; a subnormal's
decode exponent emin-t is the minimum any finite operand
carries, and a larger-magnitude operand over a subnormal is
normal-or-subnormal with exponent >= emin-t. Squares
sa = A*A, sb = B*B are single msf_u128_mul_u64_u64 products
(each <= 106 bits at binary64). Let la2 = bit length of sa.
Anchor a window at the top of a^2 inside the existing u128
class: a_win = sa << (121 - la2), so a_win lies in
[2^120, 2^121); the b^2 term enters aligned by
net = (121 - la2) - 2*(ea - eb) (ea - eb >= 0 by the lemma):
shifted left exactly if net >= 0 (the product is then
<= a_win because b^2 <= a^2 as values, so nothing overflows
u128), else shifted right by TRUNCATION with tail sticky
"any shifted-out bit of sb" - never a jam into the sum. The
window occupies at most 122 of the 128 bits (tot = a_win +
b_win < 2^122, since b_win <= a_win), which is the study's
128-bit anchored window realized with the carry headroom left
inside the word; no new width (WIDTHS hypot row restated
below). The exact sum of squares is then
(tot + f) * 2^(2ea - (121 - la2)) with 0 <= f < 1 and
f = 0 iff the tail sticky is 0 (a_win is exact, so floor of the
sum at window scale is a_win + floor(aligned sb)). Finish with
the sqrt_core scaling: if the window exponent
ew = 2ea - (121 - la2) is odd, shift tot right one (floor; the
dropped bit joins the sticky) and increment ew, giving the
radicand R (119..122 bits - the study's ~120-bit radicand) with
exact value (R + f') * 2^ew, ew even. Q = isqrt(R) by the
sqrt_core bit search (candidates < 2^61, squares < 2^122 in
single u128 multiplies; Q is 60 or 61 bits - the study's 61-bit
root). By isqrt(floor(N)) = floor(sqrt(N)) and (Q+1)^2 >= R+1
> R + f', Q is exactly floor(true * 2^(-ew/2)) with fractional
part zero iff f' = 0 and R - Q^2 = 0; one call of the
unmodified msf_pack_generic on (sign 0, ew/2, Q,
sticky = tail OR parity-dropped OR (R - Q^2 != 0)) is therefore
the correctly rounded result in all five attributes
(pack-feed lemma, study Sec. 2.1). Margin: Q carries >= 60
bits against p <= 53, i.e. at least seven bits below the
destination significand in normal binades; in the subnormal
clamp the pack's dropped-bit count only grows while Q's least
bit sits (60 - p) + (emin - e_top) >= 7 bits below the
subnormal ulp, so guard, round and sticky are always the true
value's. The floor (never jam) form is mandatory exactly
because ties are attainable [study Sec. 6, measured: hypot of
1580*2^-24 and 1659*2^-24 is 2291*2^-24, an odd 12-bit
significand at binary16 - a true midpoint]: a jammed bit can
push R across (Q+1)^2 and fabricate an exact root; with the
floor form an exact tie arrives at the pack as guard=1,
round=0, sticky=0 and is decided by the pack's tie path, not
by a kernel special case. Overflow is attainable only through
the true value (max sqrt(2)*Fmax) and underflow only when both
operands are tiny; both are the pack's judgements (kernel
never pre-judges tininess, SF-0 2.5). Exactness iff sticky
computes 0 (e.g. 3-4-5). Result sign is always +, including
the +0 and +inf deliveries of Sec. 3. Cost class: two squares,
one window add, <= 61 search multiplies - sqrt_core-class by
shape; target text/stack measured at gate time, no performance
claims.

Test-only mutant, declared here before code (the brief's
jam negative control, MSF_ALG_TEST_TRUNC precedent):
MSF_ALG_TEST_JAM (never defined in a build whose results are
quoted) replaces the truncating alignment with
msf_u128_shr_jam and suppresses the tail sticky - the unsound
jam-into-the-sqrt-input form. It must be watched failing the
committed tie family (Sec. 4); the family therefore includes
jam witnesses (pairs where a recorded scratch search shows the
jam form's Q/sticky diverging from the floor form's), embedded
as explicit pairs in the generator.

WIDTHS hypot row (owned file, one row added): hypot -
"128-bit anchored sum + sticky" with the realization sentences:
squares <= 106 bits, window anchored at the top of a^2 with the
sum < 2^122 inside msf_u128, floor alignment plus separate
sticky (never a jam), ~120-bit radicand, 60/61-bit root, one
pack. No existing row widens [study Sec. 4 concurs].

### 3. Specials in the study's evaluation order, with both [2R] second reads

Evaluation order is part of the semantics [study Sec. 5.2];
the kernel implements it in exactly this sequence (all five
modes identical; rounding never applies to these deliveries):

| step | condition | result | flags | basis |
|---|---|---|---|---|
| 1 | any sNaN operand | first sNaN, quieted (SF-0 2.5 via msf_nan_delivery) | invalid | [2R] cell A below |
| 2 | any +-inf operand (either order, incl. other operand qNaN) | +inf | none | extract p063 L26 (qNaN case stated); [2R] cell B below (finite case) |
| 3 | any qNaN operand | first qNaN (matrix) | none | extract p059 L26-27 + SF-0 2.5 |
| 4 | both +-0 | +0 | none | extract p063 L26 |
| 5 | finite | Sec. 2 kernel, sign + | overflow/underflow/inexact via pack only | Table 9.1 (p060 L32) exceptions overflow; underflow |

Implementation shape: msf_nan_delivery is called for step 1
only when a signaling operand is present (it delivers the
first sNaN + invalid), step 2 is a direct +inf return tested
BEFORE the qNaN delivery, step 3 calls msf_nan_delivery for
the quiet case - a single un-ordered nan_delivery call would
wrongly let qNaN beat infinity, which is precisely the
hypot(qNaN, +-inf) -> NaN mutant the brief names as a watched
negative control. NaN payload/sign follow the matrix
(homogeneous rows, first operand wins).

Second read, cell A - hypot(+-inf, sNaN) -> qNaN + invalid
(step 1 beats step 2). Stop rule: if this read flipped the
cell I stop and report NOT READY naming the cell - it does
not flip. (i) The 9.2 head rules in extract p059 separate the
two NaN kinds asymmetrically: the signaling-NaN sentence
(L25-26, "shall return a quiet NaN ... if there is a signaling
NaN") carries no exception clause, while the very next
sentence for quiet NaNs adds "except in the cases stated
otherwise in this subclause" (L26-27); the invalid rule that
follows is scoped "For all operations" (L28-29). (ii) The only
hypot "case stated otherwise" in 9.2.1 names qNaN twice, in
both operand orders (p063 L26), and never sNaN - so the
infinity exception is a derogation from the quiet-NaN sentence
only, and the unconditional signaling sentence stands in full.
(iii) Consistency with the tree's gated Tier 1 surface: every
shipped binary operation signals invalid and quiet-delivers on
an sNaN operand even beside an infinity (add/mul/div via
msf_nan_delivery's signaling arm, Berkeley-gated); hypot
delivering +inf over an sNaN would be the library's sole
silent sNaN swallow. MPFR cannot corroborate this cell (its
NaN is quiet; the study probe's hypot(+-inf, nan) = +inf lines
exercise the qNaN cell only), so the cell is table-decided in
kernel, decider and generator alike, cross-checked between
the three implementations and never oracle-sourced.

Second read, cell B - hypot(+-inf, finite) -> +inf, no flag
[the study's D cell]. Stop rule as above - it does not flip.
(i) Domain + affine value: Table 9.1 (p060 L32) puts hypot's
domain at all pairs of affinely extended reals with function
sqrt(x^2+y^2), and p059 L19-22 defines domain as where the
mathematical function is well defined and requires correctly
rounded results for all operands in it; on the affinely
extended reals sqrt(inf^2 + finite^2) = +inf is an exact
value, so +inf is delivered exactly - overflow (a finite
exact value rounding past Fmax) is not signalled for an exact
infinite result, matching the "with no exception" idiom the
subclause uses for its other exact infinite deliveries.
(ii) Composition through this tree's gated cells gives the
same value and flags: mul(+-inf, +-inf) = +inf,
add(+inf, finite square) = +inf, sqrt(+inf) = +inf
(sqrt_core infinity arm), none signalling; evenness in both
operands (p061 L37) fixes the sign +. (iii) Executed MPFR
agrees as value corroborator [study Sec. 6 probe log:
hypot (-inf,3) -> +inf flags=00; Sec. 6 licenses MPFR on
values/class, never on flags - the no-flag part rests on
(i)/(ii)]. The adjacent stated cell hypot(+-inf, qNaN) = +inf
(p063 L26) is the stronger statement (an exception carved out
of the qNaN rule); the finite case needs no exception at all
because no head rule competes with it.

No other hypot cell is [2R]: p063 L26 states the zero and
qNaN/inf cells verbatim; qNaN-with-finite is the head rule.

### 4. Evidence design (generator, decider, volumes, controls)

Extend tests/alg_decider.c with a hypot path beside the rSqrt
path (same binary, decide lines "msf64_hypot <hex> <hex>").
Finite pairs: the Step 0b operation recipe - per-format
precision and emin/emax (11/-23/16, 24/-148/128, 53/-1073/1024,
set and read back), operands set exactly from decoded
significands (magnitudes; hypot is even), mpfr_hypot under
RNDN/RNDZ/RNDU/RNDD, mpfr_subnormalize skipped on zero/inf/NaN
intermediates. Bits extracted for normal, subnormal, zero and
infinity results (trig narrow() extract shape). Flags derived,
never transcribed (MPFR exception flags never read): inexact
from the subnormalize ternary chain; overflow and tininess
judged per mode from a separate unbounded-exponent precision-p
rounding w of the same pair (overflow iff |w| >= 2^(emax+1),
tiny iff |w| < 2^emin - the pack's own Clause 7 semantics,
re-derived from MPFR state); underflow = tiny AND inexact
(tininess after rounding), overflow is delivered with
inexact set. Ties-to-away WITHOUT raw RNDNA and without the
mpfr_round_nearest_away macro: ta equals te except at an exact
midpoint of the delivered granularity, where it takes the away
(upward, results being positive) neighbour; the decider tests
exact-tie-ness from a 256-bit RNDN evaluation (a delivered
midpoint is dyadic with <= p+1 significant bits, hence exact -
ternary 0 - at 256 bits, and its half-ulp position is checked
by exact power-of-two scaling; ternary nonzero proves
non-tie), and on a tie forms the away neighbour's bits from
that exact value. ta flags equal te flags (at a tie the
unbounded judges agree: the away neighbour at either boundary
is the even candidate te also takes). Specials in the decider
are table-decided from Sec. 3, implemented independently of
the kernel (own evaluation-order code, own NaN matrix walk),
so generation is a three-way cross-check.

Extend tests/gen_vectors_alg.py: the rSqrt sections regenerate
byte-identically (same jobs, same decider lines - verified by
diffing the rSqrt prefix at first regeneration), and each
alg-{fmt}.vec gains a hypot section of ~500 pairs x 5 modes =
~2,500 lines per format under the existing provenance family
mpfr-alg:{specials,directed,ties,seeded}: specials (the full
Sec. 3 order: sNaN/qNaN payload-and-sign samples in both
operand positions, inf x {finite, zero, inf, qNaN, sNaN} in
both orders, signed-zero pairs); directed (boundary pool
squared - pool of binade edges/smallest-largest subnormal/
smallest normal/largest finite/one/powers of two, all pairs
both orderings; exponent-span lattice across binade gaps both
orderings; subnormal-corner pairs incl. exact and inexact
subnormal outputs; Pythagorean exacts); ties (exact midpoint
constructions - odd (p+1)-bit hypotenuse triples at several
scales incl. the study's two measured binary16 ties,
midpoint-adjacent nearest-encoding pairs, and the embedded
jam witnesses of Sec. 2); seeded (seeded finite pairs, seeds
in the generator). The generator's independent exact-Python
decider decides every hypot pair in all five modes by exact
integer squaring (floor root + midpoint compare at the
unbounded precision-p scale and at subnormal granularity,
overflow/underflow/inexact from first principles matching the
pack's Clause 7 shapes) - generation REFUSES on any
disagreement among MPFR decider, exact-Python and the Sec. 3
table (study stop rule, brief stop rule). Regeneration
byte-stable twice before the vectors commit.

Gate-only differentials (scratch scripts, ulimit -v ceilings,
counts printed): (a) binary16 second-operand sweep - every one
of 65,536 encodings as second operand against a fixed boundary
pool as first operand (both orders covered by pool symmetry
cases incl. specials), kernel vs decider x 5 modes; (b)
binary16 counted sampled full sweep - seeded pairs over all
encodings at a stated count; (c) binary32/64 seeded +
directed-pool pair volume at stated counts. Optional
cr_hypot* execution corroboration (~1 h, study Sec. 6 harness
shape, execution only over my own cases, regular positives)
- attempted only if the units are already present on this
host from the Step 0b pin; named in the report either way,
never a gate substitute. Negative controls, each watched
refused before trusted: hypot(qNaN,inf)->NaN expectation
mutant; MSF_ALG_TEST_JAM build must fail the committed tie
family; 1-ulp-moved hardest (tie) expectation; inexact
stripped on a known tie (tie lines carry inexact - stripping
10 -> 00 must fail); directed-mode swap on a subnormal-output
case (tp<->tn where the committed pair lands subnormal).
Then tools/run.sh smoke + standard PASS, target objects from
run.sh inspected for msf_alg text size and hypot stack frames
(object inspection, stated as measured; no performance claims).

### 5. Owned files and escalations

Owned (brief): src/msf_alg.c (hypot half + file header
restatement), tables/implemented.tsv (3 rows), generated
include/muse_softfloat.h + docs/COVERAGE.tsv (whichever of the
four generator outputs regeneration changes),
tests/gen_vectors_alg.py, tests/alg_decider.c,
tests/vectors/alg-*.vec, docs/WIDTHS.md (hypot row),
tools/run.sh (freeze-comment counts only),
docs/metrics/briefs.jsonl (my row, same shape as the
parcel-w5alg1 row). Named non-owned item, reported not
touched: tests/VECTORS.md mpfr-alg tag rows currently say
"rSqrt ..." - the hypot lines ride the same four tag tokens
(study Sec. 7.3 one tag family), so the row wording needs a
lead/owner touch-up at merge; the runner derives provenance
counts from the files themselves, so no gate depends on it.
Board wiring: verified present (Sec. 0 above), nothing to
escalate; board sampled replay and planted-copy verification
remain lead/verifier work (no board flashing by me). Commit
shape: kernel+registration commit(s) with detailed bodies
ending with the Co-Authored-By trailer; never push or merge.
All runs from script files in scratch/parcel-w5alg2/ under Git
Bash, MSF_PYTHON pinned to the workspace .venv, TMPDIR/TMP/TEMP
inside scratch, explicit ulimit -v ceilings on the long sweeps.

Stop conditions carried verbatim: any unadjudicated
disagreement (decider vs exact-Python vs table vs kernel)
stops the parcel - classify, never average, never relabel;
either Sec. 3 second-read cell flipping without an owner
ruling stops the parcel as NOT READY naming the cell (both
reads above hold, so implementation proceeds). If any format's
gate cannot close, the bundle returns NOT READY whole (parity).

Believed: hypot is an exact-decision kernel in the shipped
128-bit class; the live risks are the evaluation-order
specials (pinned above), the subnormal-clamp pack margin
(proved by bit count, exercised by the subnormal-corner family),
and decider flag derivation at overflow/tininess corners
(three-way cross-decided per committed case).
For: lead

### Addendum (2026-10-28 07:29:54 -07:00, still before any code): the jam mutant cannot bite in this realization - mutant plan revised

While hunting the Sec. 2 jam witnesses I proved, and then
measured, that the tree-idiom jam variant (msf_u128_shr_jam
alignment + parity jam + remainder-only sticky) is
PACKED-EQUIVALENT to the mandated floor+sticky form in the
anchored-window realization, on every input: the two jam sites
compose to exactly R_jam = R | (f>0) at radicand scale (R =
floor radicand, f the dropped fraction), and a parity case
analysis on (R even/odd) x (remainder zero / R+1 a perfect
square) shows the pack's guard/round/sticky decision is
unchanged in all five modes - a crossed square is always an
odd root, whose bit 0 sits in the pack's sticky region
(Q >= 60 bits) and recreates the suppressed stickiness.
Measured [scratch/parcel-w5alg2/jam_equivalence.py, log
out/jam_equivalence.log]: 300,040 finite pairs (seeded random
binary16/32/64 + structured tiny-b), jam vs floor packed
(bits+flags, 4 MPFR-shaped modes) divergences = 0, and the
floor sim agrees with the study's independent exact decider
on the stride sample (0 disagreements). A 30M-point scan for
cross-square witnesses found the one-parameter family is a
factor-pair equation (finitely many solutions); a CRT
construction produced 87 true cross-square pairs at binary64,
all packed-identical, as the proof predicts. The study's
"jammed sum can cross a square boundary" warning bites at
coarser jam scales (a natively-scaled TOT jammed then scaled
up); at the anchored window's radicand scale it cannot. The
floor form ships regardless - it is the form the pack-feed
lemma makes sound directly, and the brief mandates it; the
equivalence is a measured property of this realization, not
a license to ship the jam.

Revised mutant plan (declared before code, replacing the
Sec. 2/4 jam-witness language): two test-only macros.
MSF_ALG_TEST_JAM (shr_jam form above) is built and watched
over the committed vectors and the gate differentials with
the EXPECTATION THAT IT PASSES - recorded as equivalence
evidence, never claimed as a refused control.
MSF_ALG_TEST_NOSTICKY (floor alignment kept, tail/parity
sticky dropped - the other half of the study's
floor-PLUS-sticky lemma) is the biting mutant in this defect
class: measured divergent on 183,390 of the same 300,040
pairs (every wide-exponent-gap pair where b^2 falls below
the window fabricates exactness), and it must fail the
committed tie family - the family therefore carries
wide-gap exactness-boundary pairs (hypot(x, tiny) just above
x) under the ties tag. The results entry and report will
state plainly that the brief's "jam mutant must fail the tie
family" does not occur for the shr_jam mutant in this
realization, with this addendum as the adjudication record;
forcing a failure by weakening the shipped kernel or
contriving a mutant is refused.

## 2026-10-28 07:51:02 -07:00 - Results: hypot landed, all gates green; Tier 2 at 45/45

Measured: implemented exactly per the design entry + jam
addendum above. Two commits on wave5-alg2, tree clean:
kernel 656660493b122e248569cbb84f571e8e2c20dca5 (7 files:
src/msf_alg.c hypot_core - ordered magnitudes, 121-bit-
anchored window inside u128 with the sum < 2^122,
truncation + tail sticky floor-sum, sqrt_core scaling,
one pack, sign always +; specials in the Sec. 5.2
evaluation order, both [2R] cells held as second-read and
never oracle-sourced; implemented.tsv +3 rows; regenerated
header/COVERAGE/dispatch byte-stable twice, generator
prints tier1 783/783 tier2 45/45 828 total; WIDTHS hypot
row; run.sh freeze-comment counts only) and evidence
e858498242967f2ef4713e96521253dd6c7a088d (6 files).
Evidence (scratch/parcel-w5alg2 scripts 01-12, logs in
out/): committed hypot vectors 2,500 lines/format
(500 pairs x 5; specials 500, directed 1,140, ties 675,
seeded 185), rSqrt sections line-identical to pre-parcel,
regeneration byte-stable twice and post-commit leaving
the tree clean; every committed pair three-way
cross-decided (Step 0b MPFR recipe in tests/alg_decider.c
vs the generator's exact integer decider vs the settled
evaluation-order table), ta decided per case (16 te!=ta
tie pairs per format incl. the study tie 062c/067b ->
087a/0879 flags 10). Differentials 0 mismatches:
binary16 pool sweep 6,553,600 + sampled 1,500,000;
binary32/64 seeded 1,750,000 each. Negative controls
refused: qNaN/inf mutant, 1-ulp tie, inexact stripped on
the study tie, tp/tn swap on a subnormal output,
MSF_ALG_TEST_NOSTICKY kernel (1,280 lines, 80 of them
ties-tagged). MSF_ALG_TEST_JAM watched PASSING all
11,095 committed lines and 1,500,000 jam-build decider
checks (0 divergences) - the addendum equivalence,
reported as such, never claimed refused. Optional
cr_hypot execution corroboration: 48,000 checks, 41,103
agree; the 6,897 disagreements are all FE_UPWARD-only
at binary32/64 and adjudicated foreign-host oracle-limit
(MPFR == exact-Python on every one, F1-class fence).
smoke PASS (182,518) and standard PASS (+1,117,504),
re-run post-commit (12_final.sh): inventory tier1 783/783,
tier2 45 implemented / 0 planned / 45 registered; drift,
type and symbol scans clean; all 11 standing controls
refused. Target arm-none-eabi-gcc 14.2.1 cortex-m0plus
-Os clean: msf_alg.o text 2,224 B total (hypot_core
1,032 B), data/bss 0, hypot_core stack 520 B static,
undefined symbols integer-only + memcpy. Report:
scratch/parcel-w5alg2/report.md, first line READY.
Not done, named in the report: tests/VECTORS.md tag-row
wording still says rSqrt (same four mpfr-alg tokens now
carry hypot too; outside my owned files, escalated for
merge-time touch-up, no gate depends on it); board
sampled replay and planted-copy verification are
lead/verifier work; no owner ruling was sought on the two
[2R] cells because neither second read flipped. Nothing
pushed or merged; no board flashing.
Believed: the 3-row hypot bundle is merge-ready; the one
judgement a verifier should re-examine is the jam
equivalence (its own plant in shr_jam form will pass by
the same proof - the floor form shipped is the mandated
one regardless).
For: lead
