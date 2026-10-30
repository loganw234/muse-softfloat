# Verifier-w5twiddledoc: NOT READY

Copy `worktrees/verify5-twiddledoc` (HEAD `3e55ff2`, parent `a51f31e`).
Gate re-run reproduces (`FORKB-PATCH OK`, MPFR 4.2.2,
`PROVENANCE checked_fields=8856 mismatches=0`; census recomputed
leg-by-leg 4096+3072+448+344+512+384=8856, agrees). Controls,
decider recipe, failed-oracle mechanism (bit-exact independent
probe), hash-file identity, trig-pointer figures, claim surface,
and proof-boundary wording all corroborate. Full evidence:
`scratch/verifier-w5twiddledoc/report.md`.

Blocking findings (document claims the trail contradicts):

- `docs/TWIDDLES.md:166` census total `8956`; rows sum to 8856.
- `docs/TWIDDLES.md:370` kiss_fftr.c sha256 is 56 hex chars
  (invalid); recorded/measured value is the 64-char
  `b34ff3...07389c470ad848744f` enforced by
  `demo/make_kissfft_tree.py:70`.
- `docs/TWIDDLES.md:36` `"Unmodified KissFFT" is claimed wherever
  convenient` - inverted; every authority says never claimed.
- `docs/TWIDDLES.md:45-46` claims N=256 ran fwd+inv; the driver
  (`demo/twiddle_gate.c:169-170`), census, Sec. 4, and the parcel
  report all say fwd-only. Census pointer also misdirects
  ("Section 3" for the Sec. 2.3 census).
- `docs/TWIDDLES.md:213` "128-bit choice" for the 256-bit decider.
- `docs/BOARD.md:137` pointer `[docs/TWIDDLES.md](../TWIDDLE.md)`
  is broken (no repo-root `TWIDDLE.md`; singular name).
- Parcel-results "four items marked unverified" overstates: the
  doc explicitly marks two (lines 212, 224).

Unresolved: 29-count over the full domain (no surviving log;
correctly marked unverified in the doc); board-run
`tree-inputs.sha256` quote not directly checkable from available
authorities (scratch-tree measurement used instead).
