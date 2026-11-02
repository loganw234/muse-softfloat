# Ledger: parcel-w6augint (Wave 6 queue item 1: augmented stage 3)

## 2026-10-30 design entry (before code)

Base `50aac59f6035d56c37340ff07c59252cfd22d5d4`, worktree
`worktrees/w6-augint`, branch `wave6-augint`. Brief:
`ledger/briefs/w6-augint.md`. API names as shipped are
`msf64_augmented_add` / `msf64_augmented_mul` (the brief's
camelCase is the clause's spelling). Library `src/`/`include/`
frozen; board is lead-only at the merge gate; nothing is flashed
in this parcel.

### Expansion algebra with augmented pairs

Stage 3 proves the exact sign of `disc = b*b - a*c`
(`a = D.D`, `b = L.D`, `c = L.L - r*r`, `L = O - C`) from term
lists whose exact rational sum equals the listed quantity. Every
transformation in the file needs exactly one property of its
two-output primitive:

- sum primitive: `s + e = a + b` exactly (VecSum element step,
  the `L = O - C` split);
- product primitive: `p + e = a * b` exactly (`tpush_prod`).

`distill` (iterated VecSum + zero drop), the `b*b - a*c`
pair-product assembly, and `sign_of_terms` (largest term vs an
RU-summed bound on the rest) preserve/decide using only that
exactness. No step uses ties-to-even specifically: the decided
sign is sound for any exactly-summing list, and failure to
distill within the existing pass caps yields UNCERTAIN.

The Clause 9.5 pair supplies the same property with a different
head: `head` is the exact result rounded by roundTiesTowardZero
(fixed by the clause; no rounding argument exists) and `tail`
is the exact residual `exact - head` whenever representable
(`src/msf_aug.c` header, ratified flag table; representability
proof in `docs/WIDTHS.md`). Consequences used here:

- `|tail|` is below one grid step at `head` (vs half a step for
  the RN head), and a nonzero tail carries the sign of the exact
  result. Distillation speed per VecSum pass may therefore
  differ from the FMA/RN sequence; the pass caps (8 in
  `distill`, 100 in `sign_of_terms`) and the UNCERTAIN fallback
  are unchanged, so containment cannot depend on convergence
  speed - only the UNCERTAIN rate can move, and acceptance (a)
  measures it over the whole catalogue.
- The internal primitives keep their shape (`aug_sum`,
  `aug_prod` after the rename) so `vecsum`, `tpush_prod`,
  `distill`, `sign_of_terms`, capacities and the containment
  contract (capacity overflow -> UNCERTAIN) are untouched.

### Guard derivation for augmented semantics

The guard watches one fresh flags word `fl` per stage-3 call.
After the swap, every write to `fl` inside stage 3 comes from
an augmented call: `neg64` takes no flags, and the dominance
bound in `sign_of_terms` already uses its own word (`dfl`).
The augmented flag contract (9.5 as implemented and ratified in
`src/msf_aug.c`): for finite inputs, add's pair is always
exact; mul's pair is exact except the below-step residual cell,
which raises underflow+inexact; a finite head that overflows
raises overflow+inexact; invalid specials raise invalid; pin
P1 = R2 - an exact tiny residual delivered exactly as a
subnormal tail raises NO flag, and head-only rounding raises
nothing (inexact tracks exactness of the pair, never the head).

Therefore, for this consumer:

- Old guard (overflow|underflow|invalid over RN add/sub/mul/fma
  internals) bailed whenever any internal op lost bits near the
  subnormal step, because the 6-op TwoSum and the FMA residual
  are only exact while every internal result is. Inexact had to
  be ignored: RN heads are inexact by design.
- New guard: overflow|underflow|invalid|inexact over the
  augmented calls. Here inexact is raised exactly when a pair
  itself is inexact (overflow head, or mul's unrepresentable
  residual), so the guard is quiet **iff every pair consumed
  was exact** - the precise precondition of the algebra above.
  An exact tiny residual no longer forces UNCERTAIN: it enters
  the expansion as an exact subnormal term, which is the
  benefit this parcel exists to make real.
- One gap the clause leaves: an exact-infinity pair (infinite
  input, delivered twice) and quiet-NaN pairs raise no flag,
  where the old FMA/Twosum internals raised invalid (inf - inf,
  fma residual of an infinite product) or never decided. The
  primitives therefore poison `fl` with `MSF_FLAG_INVALID` when
  a returned head or tail is infinite or NaN (bit test on the
  `msf64_t` pattern, no library call, uncounted like
  `drop_zeros`' shift test). Finite-overflow heads already
  raise overflow, so the poison is redundant there and decisive
  exactly for non-finite inputs. Guard outcome is unchanged:
  UNCERTAIN, never a sign.

`IW_STAGE3_GUARD` keeps its negative-control meaning (0 disables
the guard test; mutant builds are watched failing in scratch
and never shipped).

### Op-count model (to be replaced by the measured record)

Per primitive call, counted library calls (the workload's own
counter; one increment per library call as the header defines
`ops_out`):

- two_sum: 6 (add, 3 sub chain... exactly: 1 add + 4 sub + 1 add)
  -> `msf64_augmented_add`: 1;
- two_product: 3 (mul + negate + fma)
  -> `msf64_augmented_mul`: 1;
- VecSum per element: 6 -> 1; `tpush_prod` negation unchanged
  (0 or 2 negates); `L` split per axis: 7 -> 2 (negate + add).

VecSum pass counts may shift with RTTZ heads, so catalogue
totals are empirical: report records base vs new `s3ops` sums
and `total_ops` from the host runner over the frozen catalogue.
That delta is a counted-calls record, never a performance claim
(one augmented call is not promised cheaper than one FMA call
inside the library).

### Acceptance plan (script files, Git Bash, MSF_PYTHON pinned)

(a) Base and new host runners over `tests/interval_catalogue.tsv`;
full-stream comparison of every RAY field except the ops fields
(and the IW1 hash, which covers s3 ops) - classifications must
be identical on every row. (b) A scratch-instrumented copy of
the workload dumps the distilled `la/lb/lc` lists and the
assembled `ld` list; a Python Fraction oracle over the same
catalogue inputs checks each list's exact sum against
`a`, `b`, `c`, `disc` - stated subset: every sphere row
(includes the tangent400 near-tangent family). (c) Ops totals
before/after from (a). (d) The three negative-control hooks
(`IW_RM_LO`/`IW_RM_HI` swapped, `IW_STAGE3_GUARD=0`) rebuilt on
the new code in scratch and watched disagreeing with the exact
oracle while the stock build agrees wherever it decides.
(e) `tools/run.sh standard` in the worktree. (f) No board run.

Scratch ceiling: host builds and catalogue streams only (rows
are ~700; term dumps are a few MB at most). Nothing at GB scale.

## 2026-10-30 close entry

Implemented as designed above (instrumented term dump measured
147 KB, inside the stated ceiling). Report:
`scratch/parcel-w6augint/report.md`, first line READY.

Measured: base stream reproduced the recorded IW1
`ce81d66e...9aec` / 616,754 ops before any edit. (a) base vs
new full stream over all 710 catalogue rows: zero mismatches
outside `s3ops`; stage-3 classifications identical, sphere
UNCERTAIN 488/139/4 both builds; new IW1
`ae04caf012294919c432aedd6d80f2a04e6416010291ca83110e4757a66c1422`
(moves only because the hash covers s3 ops). (b) Fraction
oracle over dumped A/B/C/D expansion sums, all 693 sphere rows
incl. tangent400: sums exact on all 689 decided rows, inexact
exactly on guard rows 682-685 (UNCERTAIN); computed disc
equals catalogue `exact_extra` 693/693; zero decided-wrong.
(c) stage-3 counted calls 283,314 -> 63,305 (-220,009),
catalogue total 616,754 -> 396,745; 2,079 above the SF-2
study model = 3 negates x 693 rays (negate+augmentedAdd kept
for O-C) - a counted-calls record, not a performance claim;
no decided row carries a subnormal expansion term.
(d) mutants on new code watched failing: RM swap
decided-wrong 2 (ids 402/404); `IW_STAGE3_GUARD=0` decides
684/685 and gets 685 wrong (HIT vs MISS) - re-derived guard
is load-bearing. Non-finite mini catalogue: UNCERTAIN in both
builds. (e) `tools/run.sh standard` PASS (59 s) in worktree;
ARM compile-only probe of the workload core PASS.
(f) no board run.

Lead merge actions (unowned files, flagged not edited):
`board/interval_run.sh` host-build line and `demo/run_demo.sh`
`SRC=` need `src/msf_aug.c` to link the host runner (firmware
`msf_core` already has it); record new IW1 and run the board
sample at the gate. Commit hash: see branch tip (recorded in
the structured result).
