---
type: design
description: parcel-w5aug SF-2 Step 4 Clause 9.5 augmented arithmetic; entry-gate pins P1/P4/P5, Sec 1.3 flag-table second read
status: ENTRY-GATE-COMPLETE; SEAM/KERNEL/EVIDENCE NOT STARTED (2026-10-29)
---

**parcel-w5aug** (brief ledger/briefs/w5-aug.md). Base bce49e0,
worktree worktrees/w5-aug, branch wave5-aug (verified clean at
entry). Governing reads: docs/studies/SF-2.md Secs 1,5,6-9 and
scratch/sf2-augmented/report.md Secs 0-2,5,6. Entry-gate second
read below is against the S1 extracts directly
(scratch/S1/extract/p069.txt, p070.txt for 9.5; combined.txt
L2298-2460 for 7.1/7.4/7.5/7.6). Nothing with `cft` in its name
opened/searched/listed; semantics from clause extracts only.

## Entry-gate dispositions (written before any kernel code)

- **P1 = R2, RATIFIED by independent second read.** An exact tiny
  non-zero residual signals underflow but raises NO underflow flag
  under default handling. Reasoning below.
- **P4 = `fixed`.** Rounding-column token for the three rows;
  caller attribute forbidden (9.5 fixes roundTiesTowardZero).
  Never `attr`, never `named`, never `none`.
- **P5 = 5.** Internal pack mode `MSF_IROUND_RTTZ = 5` in
  src/msf_internal.h. Public/internal values 0..4 are taken
  (ties-to-even=0, toward-zero=1, toward-positive=2,
  toward-negative=3, ties-to-away=4); no round-to-odd value exists
  in the tree, so 5 is free and can never equal a caller-passable
  public attribute value (public enum ends at ties-to-away=4).
  round_inc: `guard && (round_bit || stick)` (increment only
  strictly above half; exact tie stays = toward zero). Overflow
  joins the to-infinity modes; the threshold tie (all-ones
  candidate, guard set, round+sticky clear) yields max-finite
  with half-ulp tail.

## Sec 1.3 flag table - independent second read vs S1 extracts

Texts (paraphrased, clause numbers cited):

- **9.5 pair (p069/p070):** finite head: tail = exact residual,
  zero tail takes head's sign; infinite head: both results = head;
  NaN propagates to both; invalid: same quiet NaN twice;
  exceptional behaviour = 5.4.1 op under roundTiesTowardZero plus
  the 9.5 sentences. roundTiesTowardZero overflow: magnitude
  strictly above the threshold -> signed infinity; equal ->
  max-finite.
- **9.5 add/sub underflow sentence (p069):** residual non-zero
  strictly between +-b^emin => "the underflow exception shall be
  signaled." Then: "Under default exception handling, the
  operation signals inexact only when [head] overflows; the
  operation's subnormal and zero results are exact."
- **9.5 mul (p070):** same signaled sentence; unrepresentable
  residual (digits below +-b^(emin-p+1)) => tail = RTTZ(residual)
  and "Default exception handling raises the underflow flag and
  signals the inexact exception in this case." Otherwise inexact
  only on overflow.
- **7.1 (combined L2300-2312):** default handling raises the flag
  "except in the case of exact underflow, see 7.5"; "Exceptions
  are handled without raising status flags only in the case of
  exact underflow."
- **7.5 (combined L2439-2444):** under default handling, "if the
  rounded result is inexact ... the underflow flag shall be
  raised and the inexact exception shall be signaled. If the
  rounded result is exact, no flag is raised and no inexact
  exception is signaled. This is the only case in this standard
  of an exception signal receiving default handling that does
  not raise the corresponding flag. Such an underflow signal has
  no observable effect under default handling."

### Why R2 (and not R1)

1. 9.5 says *signaled*, not *flag raised*. Signaling invokes the
   general machinery (7.1: "the signal invokes default or
   alternate handling"); 7.5 default handling then decides the
   flag by exactness. In the disputed cell the tiny delivered
   result (the tail) is delivered *exactly* (9.5 add/sub:
   "subnormal and zero results are exact"; mul representable
   branch likewise), so 7.5's exact branch applies: no flag.
2. Grammatical contrast inside 9.5 itself: the mul
   unrepresentable-tail paragraph explicitly adds "raises the
   underflow flag". That sentence is pointless if the exact
   case also raised the flag. The drafters distinguish the two
   cells deliberately.
3. 7.5's universality ("the only case in this standard") is
   preserved only under R2. R1 needs 9.5 to silently override
   7.5 without override language ("shall raise"), which the
   mul paragraph shows the drafters use when they mean it.
4. Consequence check: under R2 the signal stays observable only
   under Clause 8 alternate handling, which the project refuses
   by standing rule (SF-1 Sec 7) - hence nothing observable in
   *flags under default handling, exactly as 7.5 describes.

P1 = R2 ratified. Owner pin (2026-10-28) and this second read
agree; no NOT READY stop on P1.

### Flag table as to be shipped (default handling only)

| Cell | head | tail | Flags raised |
| sNaN input | Q | Q | invalid |
| qNaN only | Q | Q | none |
| invalid, no NaN in | default qNaN | same | invalid |
| exact inf from inf operand | +-inf | same | none |
| finite in, RTTZ overflows | signed inf | same | overflow+inexact |
| residual r=0 (incl. exact subnormal/zero head) | exact | zero, head sign | none |
| r!=0 exact, \|r\| >= b^emin | RTTZ(s) | r exact | none |
| r!=0 exact, 0<\|r\|<b^emin (P1) | RTTZ(s) | r exact | **none (R2)**; underflow signaled, unobservable by default |
| mul r!=0 unrepresentable below b^(emin-p+1) | RTTZ(s) | RTTZ(r) | underflow+inexact |
| divisionByZero | - | - | never |

Three ratified subtleties: (1) head tininess alone never raises;
flags computed from exact-residual tests, never inherited from a
head pack (pack tininess leak = named mutant; tininess test is
on exact r, before any rounding of r). (2) Inexact tracks pair
exactness (overflow + mul-unrepresentable only), never head
rounding - header comment must state this. (3) Zero signs per 6.3
read with RTTZ (+0 on opposite-sign cancellation; common sign
for like-signed zeros; product sign XOR; mul nonzero rounding to
zero head takes exact sign).

## Kernel shape accepted (Sec 1.5)

src/msf_aug.c (house name; brief owns src/msf_aug.c) +
src/msf_roundpack.c internal mode only. Add/sub: exact 128-bit
window when span <= 128, else verbatim far-operand pair
(head = larger operand, tail = smaller, effective sign). Mul:
exact 2p product in u128, tail split at head grid (+- one step
when head rounded up in magnitude). Specials via
msf_nan_delivery bits delivered twice.

## Not started (checkpoint 2026-10-29)

Seam slice (aug_pair sig, 3 table rows, pair header + msf64
hidden-pointer ABI note, two-result runner lines + trampoline,
board harness two-result reply in board/harness_main.c +
board/host_replay.py, run.sh counts, regen twice, smoke),
kernel, WIDTHS rows, project-exact reference, vector families,
binary16 exhaustive-pairs C run, six mutants, smoke/standard,
target-compile -Os and -O3. See scratch/parcel-w5aug/report.md.

## Results (2026-10-29, append-only)

READY, merge-ready on wave5-aug, not pushed/merged. Commits:
2c89edd seam (aug_pair sig, 9 rows C-754 project-exact flags-yes
rounding fixed, pair header + msf64 hidden-pointer ABI note,
two-result runner/trampoline, board pair reply, run.sh counts,
regen twice byte-stable, smoke with rows planned); 0ecdd11
kernel (src/msf_aug.c exact window + verbatim branch, RTTZ
mode 5 in msf_roundpack.c, WIDTHS proof incl. binade-crossing);
3741453 evidence (house-style project-exact reference,
directed/seeded vectors 46,088/46,146/46,146, f16 harness).
Final: smoke PASS, standard PASS (pool 5,505,024, 0 mismatches);
exhaustive f16 pairs 2^32 per op x3, 0 mismatches, counts in
scratch/parcel-w5aug/logs/exh-summary-{add,sub,mul}.txt; six
mutants refused; ARM -Os/-O3 clean. Full report:
scratch/parcel-w5aug/report.md. Open: on-silicon replay (lead),
interval integration (not this parcel).
