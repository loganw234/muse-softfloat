READY - derivation retained in docs/TWIDDLES.md; gate re-run matches (8856/0).

# parcel-w5twiddledoc report: Fork B MPFR twiddle-provenance derivation record

Base `a51f31e`, worktree `worktrees/w5-twiddledoc`, branch
`wave5-twiddledoc`. Brief: `ledger/briefs/w5-twiddledoc.md`.
No board flashing; no silicon claims. Nothing with `cft` in
its name was opened, searched, or listed; the IEEE PDF was
not opened. No upstream KissFFT lines are quoted anywhere in
the deliverable (patch sites + our fraction math only).
Design entry written in `ledger/parcel-w5twiddledoc.md`
before the document.

## What was delivered (all in the worktree)

- `docs/TWIDDLES.md` - the complete self-contained record:
  claim scope (gated power-of-two sizes, complex + fftr
  super-twiddles, NOT-claimed list); the 3 patch sites with
  the phase->exact-fraction algebra incl. the dyadic
  addition-carry analysis and the no-fused-multiply
  requirement; runtime-table extraction from the actual
  alloc path; the 8,856-field census per N/class recomputed
  from the driver loop bounds; the native mpfr_sinpi/cospi
  decider with the Step 0b emin/emax recipe authority
  (binary64 -1073/1024, check_range, zero guard) and RNDN
  delivery; the failed first oracle (sin(pi_256*x), 29
  quarter-point artifacts) kept as evidence; results +
  negative controls; the boundary with the sinPi/cosPi
  correctness proof; reproduction appendix; provenance block.
- `demo/twiddle_gate.c` - the scratch gate driver byte-
  verbatim plus a header comment (verified: file ends with
  the exact `gate_main.c` bytes). Zero source edits needed
  to build against today's tree.
- `docs/BOARD.md` - one pointer sentence in the Fork B entry.
- `demo/README.md` - one pointer line in the file inventory.
- `docs/metrics/briefs.jsonl` - this parcel's row.

## Own gate re-run (required by the brief)

Fresh Fork-B tree via `demo/make_kissfft_tree.py` over the
pinned pristine tree (`scratch/parcel-w4kissfft/pristine`,
archive hash re-verified `205a8f6a...cf5cbf`): FORKB-PATCH OK,
patched sha256s match the recorded values. Gate built from
today's worktree sources + `demo/kissfft_host_shim.c` + the
fresh tree, run with MPFR 4.2.2
(`scratch/parcel-w5twiddledoc/run_gate.sh`,
log `scratch/parcel-w5twiddledoc/out/gate5.txt`):

```
mpfr 4.2.2
PROVENANCE checked_fields=8856 mismatches=0
```

Same field count, same zero as the recorded
`scratch/parcel-w4kissfft/out/gate.txt`.

## Own corroboration beyond the ledger prose

Control numbers re-checked by diffing the surviving logs
directly (not by trusting prose): flip changes exactly one
row (`KF 1024 complex fwd`); unpatched differs 12/12;
`-ffp-contract=fast` differs 0 rows; `-ffp-contract=fast
-mfma` differs 12/12. Census recomputed from the driver
loop bounds: 7168 + 792 + 896 = 8856 (matches both gate
runs). First-oracle mechanism re-derived with
`first_oracle_probe.c`: at exact quarter points in [-2, 2],
sincos(pi_256*x) at 256 bits returns tiny nonzeros
(~1e-77) where native sinpi/cospi is exactly signed zero
(8/8 such points artifact in that interval).

## Gaps found in the trail (marked unverified in TWIDDLES.md)

1. The first-oracle count (29 mismatches): no script or log
   of that run survives - ledger-recorded only. Only the
   mechanism class was re-derivable (probe above).
2. The 256-to-53 double-rounding step of `mpfr_get_d` has no
   written bound in the trail; recorded is the 256-bit
   choice plus 0 mismatches. Margin arithmetic from trail
   numbers (hardest need 111.6 bits vs 256 carried) is in
   the document as derived, not measured.
3. N=256 inverse plans were never gated (driver calls
   `gate_complex(256, 0, 1)` / `gate_fftr(256, 0, 1)` -
   forward only); the document states this.
4. The trig-proof boundary rests on `ledger/parcel-w4trig.md`
   by pointer; that parcel's vectors were not re-run here.

## Commits

Detailed commits on `wave5-twiddledoc`, each ending with the
Co-Authored-By trailer. Never pushed/merged (no push/merge
per brief).

## 2026-10-29 fix result: verifier finding F2 (kiss_fftr.c hash)

- **Defect.** `docs/TWIDDLES.md` line ~370 recorded the
  `kiss_fftr.c` patched-file SHA-256 as the 56-hex-char
  `b34ff3b21594c61e2956f61bb8a9fd86d6310f07389c470ad848744f`.
  The enforced value in `demo/make_kissfft_tree.py`
  (`EXPECTED_SHA256["kiss_fftr.c"]`) is the 64-char
  `b34ff3b21594c61e295f61bbf8a9fd86d6310fcceb459d07389c470ad848744f`.
  Both strings read directly from the files; confirmed
  different before the fix.
- **Fix.** Single replacement in `docs/TWIDDLES.md` only:
  doc value replaced with the script's exact 64-char string.
  No other file touched in the commit.
- **Programmatic re-check (post-fix).** Every backtick-quoted
  32+ hex string in `docs/TWIDDLES.md` is exactly 64 chars
  (5/5, non-64 count 0); all three patched-file hashes in the
  doc equal the three `EXPECTED_SHA256` values in
  `demo/make_kissfft_tree.py` exactly (kiss_fft.c, kiss_fftr.c,
  _kiss_fft_guts.h - ALL_MATCH).
- **Ledger send-back.** `ledger/parcel-w5twiddledoc.md`
  results entry said "four items marked unverified"; search of
  `docs/TWIDDLES.md` for `unverified` shows 3 lines (line 11
  generic policy + explicit `**unverified**` marks at doc
  lines 212 and 224) - verified explicitly-marked count is 2,
  not 4. Correction appended to that ledger file (append-only).
- First line of this report left as READY; fix committed on
  branch `wave5-twiddledoc` (commit holds only
  `docs/TWIDDLES.md`). Never pushed/merged.
