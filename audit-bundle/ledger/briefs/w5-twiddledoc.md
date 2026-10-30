**Role:** parcel-w5twiddledoc (owner dispatch: preserve the MPFR twiddle derivation in-repo)

**Deliverable:** `docs/TWIDDLES.md` on branch
`wave5-twiddledoc` (worktree `worktrees/w5-twiddledoc`,
base `a51f31e`): the complete, self-contained record of
how the KissFFT Fork B twiddle provenance was derived
and gated, so the derivation survives without the
workspace scratch. Time box 240 min. Light load.

**Sources (read as evidence, cite by path + hash where
the trail has them):** `scratch/parcel-w4kissfft/
report.md` + `gate_main.c` + `02b_gate.sh` + `out/` gate
logs, `scratch/tier2-kissfft/report.md`,
`scratch/tier2-oracle-0b/report.md` (MPFR recipes),
`scratch/tier2-trig-spike/report.md` (f64 recipe), the
copy's `docs/studies/SF-1.md` Sec. 6, `docs/BOARD.md`
Fork B entry, `docs/RECORD.md` Step 2c paragraphs,
`ledger/parcel-w4kissfft.md`. Never open/search/list
anything with `cft` in its name. KissFFT source itself
is **not** copied into the document beyond naming the
three patch sites and the fraction formulas (our math,
not their code); quote no upstream code lines.

**The document must let a competent reader re-derive
the gate from zero. Required content:**
1. The claim and its exact scope: which tables, which
   sizes (gated power-of-two set), complex + fftr
   super-twiddles, why exact cycle fractions make the
   twiddle argument exact at those sizes (the dyadic
   argument, sinkhorn/precompute contrast), and what is
   explicitly NOT claimed (other N, float config,
   unmodified KissFFT).
2. The derivation chain end-to-end: patch sites (3,
   named, with the phase->fraction algebra incl. the
   u += 2 du carry analysis and the no-fused-multiply
   requirement), how runtime tables were extracted from
   the actual alloc path (not recomputed on the side),
   the field census per N (256/1024 exhaustive, 4096
   stride-37: counts per class summing to 8,856).
3. The decider: native `mpfr_sinpi`/`mpfr_cospi` at the
   recorded precision with the Step 0b emin/emax recipe
   (binary64 -1073/1024, `mpfr_check_range`, zero guard)
   and per-mode rounding; why the first oracle
   (`sin(pi_256 * x)`) was wrong (29 quarter-point
   artifacts - keep this failure; it is evidence about
   oracle choice, exactly the kind of thing that gets
   lost).
4. Results as recorded (0 mismatches; the negative
   controls around it: 1-ulp flip moving one row,
   radian/libm differing 12/12), and the boundary with
   the sinPi/cosPi correctness proof (the gate decides
   twiddles *given* correctly rounded sinPi/cosPi; it
   is not itself that proof - pointer to the trig
   evidence legs).
5. Reproduction appendix: our gate driver logic
   (include `gate_main.c` essentially verbatim if it is
   ours - it is - as an appendix file
   `demo/twiddle_gate.c` with a header saying what it
   needs: MPFR + a Fork-B tree from
   `demo/make_kissfft_tree.py`), the exact commands,
   and expected output lines. If the appendix driver
   needs edits to build against today's tree, make them
   and say what changed; re-running it yourself against
   a freshly patched tree (via the demo scripts) is
   required: report your own field count + mismatches.
6. Provenance block: archive/pin hashes, patched-file
   sha256s, where the original logs lived, and the
   sentence that scratch is evidence, this document is
   the retained derivation.

**Style:** RECORD-grade plain technical prose; numbers
only where the trail has them; mark anything you could
not re-derive from the sources as unverified rather
than smoothing it over. No new claims.

**Owned files:** `docs/TWIDDLES.md`, `demo/twiddle_gate.c`,
`docs/BOARD.md` (one pointer sentence in the Fork B
entry), `demo/README.md` (one pointer line),
`docs/metrics/briefs.jsonl` (your row).

**Report:** `scratch/parcel-w5twiddledoc/report.md`
(first line READY/NOT READY; your own gate re-run count;
anything in the trail you could not reproduce or find)
+ `ledger/parcel-w5twiddledoc.md`. Detailed commits
ending the Co-Authored-By trailer. Never push/merge.
Script files for runs (Git Bash, MSF_PYTHON pinned in-
workspace). Structured complete/evidence/unresolved.
