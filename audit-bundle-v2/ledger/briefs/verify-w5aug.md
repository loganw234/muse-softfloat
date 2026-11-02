**Role:** verifier-w5aug (ParcelRound verifier, SF-2 Step 4)

**Stance:** disconfirm only. Findings: (a) one wrong
head/tail/flag triple, (b) an artefact that does not
re-derive, (c) a claim the evidence does not carry.

**Copy:** `worktrees/verify5-aug` (detached HEAD, parent
`bce49e0`). Never consult the parcel branch/worktree,
other worktrees, keys, `scratch/lead/`,
`scratch/parcel-w5aug/`, or `ledger/lead.md`.
Authorities: this brief, `ledger/parcel-w5aug.md`
(entry-gate pins + flag table, P1=R2), the copy's
SF-2.md Secs. 1,5,6-9, the S1 clause extracts under
`scratch/S1/extract/` the ledger cites (9.5, 7.1/7.5/7.6),
IEEE 754-2019 PDF at the workspace root by clause only.
Nothing with `cft` in its name. Never modify the copy.

**Required probes:**
1. Own exact-integer reference (Python Fractions/ints,
   written from the clause table yourself - do not port
   the parcel's generator). One-cells + families: RTTZ
   discriminators (head must truncate ties toward the
   smaller magnitude, never to even), exact powers,
   overflow-threshold tie and one step above, verbatim
   far-operand pairs, zero signs (sum, cancellation,
   product), exact tiny residuals (P1=R2: NO flag),
   mul below-subnormal-step cell (the one inexact cell:
   underflow+inexact, RTTZ tail), NaN/inf matrix.
2. binary16: exhaustive pairs claimed 2^32 per op -
   re-run at least one full op yourself OR a large
   contiguous slice + re-add the arithmetic, stating
   plainly which; kind-census sums rechecked.
3. Regen stops: gen_tables + gen_vectors_aug twice,
   byte-stable; seam drift (operations/implemented,
   rounding token `fixed` - no caller attribute may
   exist for these ops; the internal RTTZ value must
   not collide with a public attribute).
4. Flags provenance: flags must come from exact-
   residual tests, never a head-pack scratch word -
   probe the pack-tininess leak shape specifically
   (tiny exact result via head pack).
5. Runner (two-result lines) over everything
   committed; board replay plumbing judged by code
   read + host fake-serial only (no flashing - lead
   owns silicon). Target -Os AND -O3 clean.
6. Widths: WIDTHS representability proof re-read for
   the binade-crossing step; a counterexample search
   near binade boundaries is a finding if it bites.

**Outputs:** `scratch/verifier-w5aug/report.md` (first
line READY/NOT READY; per-probe evidence file:line;
findings; not-done) + `ledger/verifier-w5aug.md`.
Structured complete/evidence/unresolved - submitting
it is mandatory. Script files (Git Bash, MSF_PYTHON
pinned), ulimit ceilings, moderate load. ~480 min.
