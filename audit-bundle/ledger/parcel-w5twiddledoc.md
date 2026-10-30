# Ledger: parcel-w5twiddledoc (Wave 5 twiddle-derivation record)

## 2026-10-29 design entry (before writing)

Base `a51f31e`, worktree `worktrees/w5-twiddledoc`, branch
`wave5-twiddledoc`. Brief: `ledger/briefs/w5-twiddledoc.md`.
No board flashing; no silicon claims. Nothing with `cft` in
its name will be opened, searched, or listed; the IEEE PDF
will not be opened. KissFFT source is never copied into the
document beyond naming the three patch sites and our
fraction math - no upstream code lines are quoted.

Claim wording frozen (brief): `docs/TWIDDLES.md` is the
complete self-contained record of how the KissFFT Fork B
MPFR twiddle provenance was derived and gated, so the
derivation survives without the workspace scratch. No new
claims; anything not re-derivable from sources is marked
unverified.

Decisions frozen here, before writing:

- **Sources.** `scratch/parcel-w4kissfft/report.md`,
  `gate_main.c`, `02b_gate.sh`, `out/` gate logs,
  `scratch/tier2-kissfft/report.md`,
  `scratch/tier2-oracle-0b/report.md` (MPFR recipes),
  `scratch/tier2-trig-spike/report.md` (f64 recipe),
  `ledger/parcel-w4kissfft.md`, the copy's `docs/studies/SF-1.md`
  Sec. 6, `docs/BOARD.md` Fork B entry, `docs/RECORD.md`
  Step 2c paragraphs. Numbers only where the trail has them.
- **Document contents** (brief order): claim scope (gated
  power-of-two sizes, complex + fftr super-twiddles, what is
  NOT claimed); the 3 patch sites with the
  phase-to-exact-fraction algebra per site (site (a):
  `-2.0*i/nfft` left-to-right exactness, small-int times 2
  then exact power-of-two division; site (b):
  `-((i+1)/m + .5)` with the dyadic addition-carry analysis,
  result in [0.5, 1.5) needing <= 13 significand bits;
  site (c): `cospi`/`sinpi` of the 2c-form argument; the
  `if (inverse) phase *= -1` negation exact; the
  no-fused-multiply requirement, i.e. the expressions contain
  no multiply-add so contraction cannot reshape them, and
  every build pins `-ffp-contract=off` regardless);
  runtime-table extraction from the actual alloc path
  (`#include` of the patched TUs, read `cfg->twiddles` after
  real `kiss_fft_alloc`/`kiss_fftr_alloc` - never a
  side recomputation); the 8,856-field census per N/class
  (N=1024 exhaustive fwd+inv incl. fftr super-twiddles =
  4096 + 3072 = 7168; N=4096 stride-37 sampled = 448 + 344
  = 792; N=256 exhaustive fwd-only = 512 + 384 = 896;
  total 8856 - recomputed here from `gate_main.c` loop
  bounds); the native `mpfr_sinpi`/`cospi` decider at
  256-bit with the Step 0b emin/emax recipe authority
  (binary64 -1073/1024, `mpfr_check_range`, zero guard -
  proven for p=53 in the trig spike, 120/120) and
  round-to-nearest delivery via `mpfr_get_d` (the workload's
  mode; the recipe itself is proven in all four modes);
  the failed first oracle (`sin(pi_256 * x)`, 29
  quarter-point artifacts) kept as evidence about oracle
  choice, with the signed-zero mechanism re-derived by a
  probe where the trail has no surviving log; results
  (0 mismatches) + negative controls (1-ulp flip moves one
  row, unpatched radian/libm differs 12/12, `-ffp-contract=fast`
  inert at baseline / diverges with `-mfma`, anchors,
  aliasing); the boundary with the sinPi/cosPi correctness
  proof (the gate decides twiddles *given* correctly rounded
  sinPi/cosPi - pointer to the trig evidence legs, not
  itself that proof); provenance block (archive/pin hashes,
  patched-file sha256s, original log paths, scratch-is-evidence
  sentence).
- **Reproduction appendix.** `demo/twiddle_gate.c` is
  `scratch/parcel-w4kissfft/gate_main.c` with an added
  header (what it needs: MPFR + a Fork-B tree from
  `demo/make_kissfft_tree.py`); minimal edits to build
  against today's tree, each stated. Re-run required:
  fresh patched tree via the demo script, compile, report
  my own field count + mismatches in the scratch report.
- **Owned files.** `docs/TWIDDLES.md`, `demo/twiddle_gate.c`,
  one pointer sentence in `docs/BOARD.md` Fork B entry, one
  pointer line in `demo/README.md`, one `docs/metrics/briefs.jsonl`
  row.
- **Report.** `scratch/parcel-w5twiddledoc/report.md`
  (first line READY/NOT READY; my gate re-run count; gaps)
  + ledger results entry below. Never push/merge.
  Git Bash script files, MSF_PYTHON pinned to the
  workspace `.venv`.

## 2026-10-29 results entry

- **Document landed.** `docs/TWIDDLES.md` in the worktree
  covers the brief's required contents in order: claim scope
  (gated N, complex + fftr super-twiddles, NOT-claimed
  list incl. the precompute-variant contrast); the 3 patch
  sites with per-site exactness algebra (small-int-times-2,
  dyadic addition-carry in [0.5, 1.5), 2c-form dispatch,
  exact negation) and the no-fused-multiply requirement;
  runtime-table extraction from the actual alloc path; the
  8,856-field census recomputed from the driver loop bounds
  (7168 + 792 + 896); the native mpfr_sinpi/cospi decider
  (256-bit, exact quarter points, signed-zero handling,
  RNDN delivery, Step 0b binary64 -1073/1024 recipe
  authority); the failed first oracle kept as evidence with
  a re-derived mechanism probe; results + controls with
  control numbers re-checked by direct log diffs (flip: 1
  row; unpatched: 12/12; fast: 0; fast+mfma: 12/12);
  proof boundary at the `--wrap=sinpi,cospi` line with
  pointer to the trig legs; reproduction appendix;
  provenance block (archive 205a8f6a...cf5cbf, licence
  4d6bcab4...2c0ed, patched-file sha256s, log paths,
  scratch-is-evidence sentence). No new claims; four items
  marked unverified (first-oracle count 29, the 256->53
  double-rounding bound, N=256 inverse ungated, trig legs
  by pointer). No upstream code lines quoted; nothing with
  `cft` in its name touched; IEEE PDF unopened.
- **Re-run: PROVENANCE checked_fields=8856 mismatches=0.**
  Fresh tree via `demo/make_kissfft_tree.py` (FORKB-PATCH OK,
  sha256s match recorded); `demo/twiddle_gate.c` is the
  scratch driver byte-verbatim plus header - zero source
  edits to build against today's tree; MPFR 4.2.2; log at
  `scratch/parcel-w5twiddledoc/out/gate5.txt`. First-oracle
  mechanism probe at
  `scratch/parcel-w5twiddledoc/first_oracle_probe.c` (tiny
  nonzeros ~1e-77 vs exact signed zeros at quarter points).
- **Owned files complete.** `docs/TWIDDLES.md`,
  `demo/twiddle_gate.c`, BOARD.md pointer sentence,
  demo/README.md pointer line, briefs.jsonl row. Report at
  `scratch/parcel-w5twiddledoc/report.md` (first line
  READY). Never pushed/merged.

## 2026-10-29 correction entry (append-only; history above untouched)

- **Ledger overstatement corrected.** The 2026-10-29 results
  entry says "four items marked unverified". Verified by
  searching `docs/TWIDDLES.md` (worktree
  `worktrees/w5-twiddledoc`, branch `wave5-twiddledoc`) for
  `unverified`: 3 lines match - line 11 (generic policy
  sentence, not an item mark) plus exactly 2 explicit item
  marks (`**unverified**` at doc lines 212 and 224). The
  scratch report Sec. "Gaps found in the trail" lists 4 gap
  paragraphs, but only 2 of those gaps carry an explicit
  `**unverified**` mark in the document. Verified count of
  explicitly-marked items in the doc: 2, not 4.
- **Hash fix + send-back noted.** Verifier finding F2:
  `docs/TWIDDLES.md` line ~370 recorded a 56-hex-char
  `kiss_fftr.c` patched-file SHA-256
  (`b34ff3b21594c61e2956f61bb8a9fd86d6310f07389c470ad848744f`),
  while the enforced value in
  `demo/make_kissfft_tree.py` (`EXPECTED_SHA256`) is the
  64-char
  `b34ff3b21594c61e295f61bbf8a9fd86d6310fcceb459d07389c470ad848744f`.
  Fixed by replacing the doc value with the script's exact
  string (single-line change, `docs/TWIDDLES.md` only).
  Post-fix programmatic check: every backtick-quoted 32+
  hex string in the doc is exactly 64 chars (5/5), and all
  three patched-file hashes in the doc equal the three
  `EXPECTED_SHA256` values exactly. Fix committed on
  `wave5-twiddledoc`; ledger/scratch appends left
  uncommitted per the fix scope (commit holds only
  `docs/TWIDDLES.md`). Never pushed/merged.
