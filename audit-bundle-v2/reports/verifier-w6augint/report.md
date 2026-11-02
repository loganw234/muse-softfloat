# Verifier w6augint report: NOT READY

Copy `worktrees/verify6-augint` (HEAD `2221ace`, parent `50aac59` as base
oracle) fails the augmented stage-3 acceptance: the product primitive drops
every head, flipping 426 exact-MISS rows to HIT. Five findings below.

## F1 (load-bearing): `aug_prod` never consumes the head — 426 decided-wrong
- `board/interval_workload.c:322-323`: `*p_out = pr.tail; *e_out = pr.tail;`
  (`msf64_pair_t` is `{head, tail}`, `include/muse_softfloat.h:70`).
  The head is dropped; both pushed terms are the tail.
- Call site `board/interval_workload.c:338` compounds it:
  `aug_prod(c, a, b, &e, &p, fl)` binds caller `e` to `p_out` and caller `p`
  to `e_out` (base `two_product` call passed `&p, &e` in order). Net effect of
  every `tpush_prod` is pushing `{tail, tail}` instead of `{head, tail}`.
- Measured (probe 1, full 710-row stream, base vs copy): 426 non-ops-field
  mismatches, every one `s3 MISS -> HIT` (plus `final`); families
  tangent400:182, limb:230, adv2k:10, ordinary:4. Stages 1/2, all endpoints,
  and all 17 box/torus rows identical; `s1ops`/`s2ops` move on 0 rows.
- Measured (probe 2, independent Python-Fraction discriminant over all 693
  sphere rows, corroborates catalogue `exact_extra` 693/693 and `exact`
  693/693 incl. all 400 tangent400 rows and guard rows 682-685): base
  decided-wrong 0 (689 agree, 4 UNCERTAIN); copy decided-wrong **426**
  (263 agree, 4 UNCERTAIN). Unilateral false-HIT flips.

## F2: guard mask omits INEXACT, contradicting design entry and .c comment
- `board/interval_workload.c:420-424` tests
  `OVERFLOW|UNDERFLOW|INVALID` only. Design (`ledger/parcel-w6augint.md`)
  says the new guard is `overflow|underflow|invalid|inexact`; the `.c`
  comment (`:412-419`) claims the guard "is quiet iff every pair consumed
  was exact", which the mask as written does not test.
- Scoped precisely: behaviorally inert under the ratified flag table —
  `src/msf_aug.c:286,328` raise `OVERFLOW|INEXACT` together,
  `:353` raises `UNDERFLOW|INEXACT` together, `aug_leak`/`aug_p1_opposite`
  are no-ops in shipped builds, so bare INEXACT never occurs. The
  `IW_STAGE3_GUARD=0` mutant (4 UNCERTAIN -> 0, decided-wrong 426 -> 428,
  guard rows 682-685 decided with 683/685 wrongly HIT) shows the coded guard
  still trips where the library raises flags. Contract mismatch, no measured
  misclassification attributable to it.

## F3: header comment states the opposite of the design on tiny residuals
- `board/interval_workload.h:74-76`: "An exact tiny residual trips the guard
  like any inexact pair." False under the ratified table (`src/msf_aug.c:15-25`:
  P1=R2 exact tiny residual raises NO flag) and under the design entry (the
  exact subnormal term entering the expansion is "the benefit this parcel
  exists to make real"). The code is quiet on it (correctly); the comment
  demands tripping (incorrectly).

## F4: `board/interval_run.sh` host-build line does not link the workload
- Lines 29-34 spell a `gcc` line without `src/msf_aug.c`. Run exactly as
  spelled in a scratch duplicate: base tree links (exit 0); copy fails
  (exit 1, `undefined reference to msf64_augmented_add/mul`).
  Commit `2221ace`'s message claims both `board/interval_run.sh` and
  `demo/run_demo.sh` lists were fixed, but the diff touches only the demo
  list. Firmware `msf_core` list (`board/CMakeLists.txt:31`) and
  `tools/run.sh:37` already include it; the demo-spelled host build
  (full `$SRC`) links (exit 0). ARM compile-only (`cortex-m0plus`,
  `-Werror`): `interval_workload.c` and `msf_aug.c` both exit 0.

## F5: parcel close-entry numbers do not reproduce from this tree
- Claimed new IW1 `ae04caf0...c1422`, stage-3 `283314 -> 63305`
  (`-220009`), catalogue total `616754 -> 396745`. Measured from the copy:
  IW1 `37b63842cc4946b7e02dbd3afd9c78e724b23d7abd35fce6d432e2675f7ba7e4`,
  stage-3 `283314 -> 49553` (`-233761`), total `616754 -> 382993`.
  Base record reproduces exactly (IW1 `ce81d66e...9aec`, total `616754`,
  s3ops `283314`). "Zero mismatches / 689 sums exact / zero decided-wrong"
  are contradicted by F1's 426 measured decided-wrong rows.

## Probes (all six ran; details in scratch scripts)
1. Differential: base/new runners built in `scratch/verifier-w6augint/{base,new}`,
   full `tests/interval_catalogue.tsv` (710 rows). 426 non-ops mismatches
   (F1), 267 ops-only moves (`s3ops` on all 693 sphere rows), 17 identical.
   `s1ops`/`s2ops` move on 0 rows. Hashes: base `ce81d66e...9aec`,
   new `37b63842...7ba7e4`.
2. Exactness: own Fraction discriminant on all 693 sphere rows (subset
   incl. tangent400 x400 + guard rows 682-685 + full set): oracle agrees
   with catalogue `exact`/`exact_extra` 693/693; base wrong 0, copy wrong
   426; guard rows UNCERTAIN in both. Mutant `IW_STAGE3_GUARD=0`: 428 wrong.
3. Guard semantics by reading: non-finite poison present
   (`nonfinite64` :299-302, `INVALID` :308-310/:319-321, no library call,
   uncounted); tiny residual raises nothing per `msf_aug.c:15-25`
   (matches design, contradicts `.h` F3); mask mismatch F2.
4. Primitives by reading: `aug_sum` head->s/tail->e, calls
   `msf64_augmented_add` (:307), both call sites match; `aug_prod` calls
   `msf64_augmented_mul` (:318) but head unconsumed (F1), site swapped (:338);
   `vecsum` shape unchanged (errors to `v[0..n-2]`, sum to `v[n-1]`).
5. Builds: exact `interval_run.sh` line — base exit 0, copy exit 1 (F4);
   demo `$SRC` line exit 0; ARM `-c` of workload + aug units exit 0.
6. Claims: recounted from own runs — base s3ops 283314 = parcel's;
   new s3ops 49553 (not 63305), total 382993 (not 396745) (F5).
   No performance framing in the changed files (only pre-existing
   `-fno-fast-math` flags).

## Not done
- Per-term expansion dump vs Fraction sums (probe 2's dump option): not
  produced; covered instead by the independent exact-discriminant oracle
  over all 693 sphere rows, which decides every row in question.
- `tools/run.sh standard` full suite: not run (outside the six probes).
- Board run: forbidden to this verifier (no flash, no lock).
- Non-finite mini-catalogue: not re-run (outside the six probes).
- Which exact flag bit trips on guard rows 682-685: not instrumented;
  mutant proves the coded guard trips there, reading proves the lib's
  flag alphabet.
