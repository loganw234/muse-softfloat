**Role:** verifier-w5twiddledoc (ParcelRound verifier, TWIDDLES.md)

**Stance:** disconfirm only. Findings (a) a document
claim the trail contradicts, (b) a derivation step that
does not actually re-derive (broken reproduction),
(c) upstream KissFFT code quoted into the repo.

**Copy:** `worktrees/verify5-twiddledoc` (detached HEAD,
parent `a51f31e`). Never consult the parcel branch/
worktree, other worktrees, keys, `scratch/lead/`,
`scratch/parcel-w5twiddledoc/`, or `ledger/lead.md`.
Authorities: this brief, the parcel ledger, the copy's
docs, and the evidence trail (`scratch/parcel-w4kissfft/`
report + gate logs, `scratch/tier2-oracle-0b/report.md`,
`ledger/parcel-w4kissfft.md`). Nothing with `cft` in its
name. Never modify the copy. Light load.

**Required probes:**
1. Re-run the appendix gate yourself: build
   `demo/twiddle_gate.c` against a tree from the copy's
   `demo/make_kissfft_tree.py` (offline from any cache
   present, else the demo fetch into your scratch) and
   reproduce the field count + mismatch count. The
   document's census arithmetic recomputed from the
   driver loops, not trusted.
2. Every load-bearing number/claim traced: census per
   class, decider precision + recipe vs Step 0b,
   patched-file hashes vs the board-run log quotes,
   coverage scope (which N, fwd/inv, super-twiddles)
   vs the driver source, the failed-oracle story vs
   the ledger, what-is-not-claimed vs SF-1 Sec. 6.
3. Claim wording: "unmodified" discipline everywhere
   in the diff; proof-boundary paragraph (gate vs the
   trig correctness proof) not overstated; unverified
   items actually marked unverified.
4. Links/pointers resolve (BOARD.md + demo/README
   pointers to the new doc); no upstream code lines
   quoted (diff-read for it); claim surface = owned
   files.

**Outputs:** `scratch/verifier-w5twiddledoc/report.md`
(first line READY/NOT READY; your gate count; per-claim
table; findings; not-done) and
`ledger/verifier-w5twiddledoc.md`. Structured
complete/evidence/unresolved. Script files (Git Bash,
MSF_PYTHON pinned in-workspace).
