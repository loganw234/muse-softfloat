NOT READY

Gate re-run (mine, Git Bash, MSF_PYTHON=.venv/Scripts/python.exe):
FORKB-PATCH OK (3 sites; patched sha256 match the copy's recorded
values) + `PROVENANCE checked_fields=8856 mismatches=0` (MPFR 4.2.2).
Log: `scratch/verifier-w5twiddledoc/out/gate-verify.txt`.
Census recomputed from the driver loop semantics: 4096 + 3072 +
448 + 344 + 512 + 384 = 8856, agrees with the gate (CENSUS-OK).
Scripts: `scratch/verifier-w5twiddledoc/run_gate.sh`,
`census_check.py`, `controls_check.py`, `oracle_check.c`
(+ `out/oracle_check.txt`).

Per-claim verdicts (copy = `worktrees/verify5-twiddledoc`,
detached HEAD `3e55ff2`, parent `a51f31e`):

| # | Claim (docs/TWIDDLES.md unless noted) | Verdict |
|---|---|---|
| 1 | Census per class, Sec. 2.3 table | FAIL: total `8956`, rows sum to 8856 |
| 2 | Decider: native 256-bit sinpi/cospi + Step 0b recipe | PASS, fully corroborated |
| 3 | Patched-file sha256 provenance block | FAIL: kiss_fftr.c hash 56 chars, contradicts trail |
| 4 | Coverage scope vs driver source | PASS except Sec. 1 N=256 sentence (FAIL) |
| 5 | Failed-oracle story vs ledger/parcel-w4kissfft.md | PASS; mechanism reproduced bit-exact |
| 6 | Not-claimed list vs SF-1 Sec. 6.4 | PASS |
| 7 | "Unmodified" wording discipline | FAIL: Sec. 1 line 36 inverted |
| 8 | Proof boundary not overstated | PASS |
| 9 | Unverified items actually marked | PARTIAL: 2 of 4 explicitly marked |
| 10 | BOARD.md + demo/README pointers resolve | FAIL: BOARD link broken; README ok |
| 11 | No quoted upstream KissFFT code in owned files | PASS |
| 12 | Claim surface = owned files vs a51f31e | PASS (5 files) |
| 13 | Appendix gate reproduces 8856/0 | PASS (my re-run) |

Findings (all in the copy; line numbers from the copy):

- F1 (Sec. 2.3 census total). `docs/TWIDDLES.md:166` totals the
  field table as `8956`. The six rows sum to
  4096+3072+448+344+512+384 = 8856; the section header, Sec. 4,
  Sec. 5, `demo/twiddle_gate.c:62`, the recorded gate log
  (`scratch/parcel-w4kissfft/out/gate.txt`), and my re-run all
  say 8856. Transposed digits; the table contradicts the trail.
- F2 (provenance hash). `docs/TWIDDLES.md:370` records kiss_fftr.c
  sha256 `b34ff3...07389c470ad848744f`, 56 hex chars - not a valid
  SHA-256. The copy's own `demo/make_kissfft_tree.py:70`, the
  measured evidence tree
  (`scratch/parcel-w4kissfft/tree/kiss_fftr.c`, sha256sum), and my
  fresh-tree build (FORKB-PATCH OK enforces the 64-char value)
  all carry `b34ff3b21594c61e295f61bbf8a9fd86d6310fcceb459d07389c470ad848744f`.
  The other two hashes (lines 368, 372) match. A reader
  re-verifying the provenance block against the script fails.
- F3 ("unmodified" inversion). `docs/TWIDDLES.md:36`:
  `"Unmodified KissFFT" is claimed wherever convenient`. The
  parcel ledger (`ledger/parcel-w5twiddledoc.md` design entry,
  results entry), `ledger/parcel-w4kissfft.md:20`,
  `docs/studies/SF-1.md` Sec. 6.4 (`"unmodified KissFFT" is not
  claimed`), the doc's own NOT-claimed entry (line 73),
  `docs/BOARD.md:123`, and `demo/README.md:88` all say the
  opposite. One-word-class inversion with claim-discipline weight.
- F4 (N=256 scope overstatement). `docs/TWIDDLES.md:45-46`: "at
  N=256 the gate ran forward and inverse plans". The driver runs
  only forward at N=256 (`demo/twiddle_gate.c:169-170`:
  `gate_complex(256, 0, 1)`, `gate_fftr(256, 0, 1)`); the Sec. 2.3
  census rows say "fwd only"; Sec. 4 says "N=256 exhaustive
  forward-only"; the parcel report's fourth unverified item is
  "N=256 inverse ungated". The parenthetical "(see the census in
  Section 3)" also mis-points: the census is Sec. 2.3.
- F5 (margin-note slip). `docs/TWIDDLES.md:212-214`: "what the
  trail does contain is the 128-bit choice plus 0 mismatches".
  The decider is 256-bit (`mpfr_inits2(256, ...)` in
  `demo/twiddle_gate.c:87`, Sec. 3 header). Minor but factual.
- F6 (parcel-report overstatement, for the record).
  `ledger/parcel-w5twiddledoc.md` results entry claims "four
  items marked unverified". The doc explicitly marks two
  (`**unverified**` at lines 212 and 224); N=256-inverse and
  trig-legs-by-pointer appear as scope/pointer prose, not marked.
  Compounded by F4, which asserts the opposite of one of them.
- F7 (broken pointer, owned file). `docs/BOARD.md:137`:
  `[docs/TWIDDLES.md](../TWIDDLE.md)` - target resolves to
  repo-root `TWIDDLE.md`, which does not exist (and the name is
  singular). Should be `TWIDDLES.md` relative to `docs/`.
  `demo/README.md:128-129` pointer line resolves fine.

Corroborated (no finding):

- Driver verbatim: `demo/twiddle_gate.c:64-174` byte-identical to
  `scratch/parcel-w4kissfft/gate_main.c` (header-only addition).
- Decider authority: trig-spike Sec. 1 gives binary64
  emin=-1073/emax=1024, `mpfr_set`+`mpfr_check_range`+
  `mpfr_subnormalize`+zero guard, SET 68/68 + OP 52/52 = 120/120
  (17x4 set-path, 13x4 op-path: all four modes); matches doc
  lines 194-203. RNDN delivery via `mpfr_get_d` matches the
  driver; signed-zero `neg_zero` handling matches driver
  lines 90/124-128/140-144.
- Failed oracle: 29-count is ledger-recorded
  (`ledger/parcel-w4kissfft.md:207-209`) with no surviving log in
  `scratch/parcel-w4kissfft/out/` (listing confirms none); doc
  marks it **unverified** (line 224) - correct handling. The
  mechanism table (lines 234-242) I reproduced bit-exact with my
  own probe (`oracle_check.c`): all 8 artifact rows identical
  down to the hex (e.g. sin(-8/4) pi-route `300452821e638d01`
  vs native `8000000000000000`).
- Controls by direct log diff (`controls_check.py`):
  flip changes exactly `KF 1024 complex fwd` (1 row); unpatched
  12/12; `-ffp-contract=fast` 0 rows; `+ -mfma` 12/12. Exactly
  as the doc's table states.
- Stride-37 footnote: floor(4095/37)+1+1=112,
  floor(2047/37)+1+1=57, floor(1023/37)+1+1=29 - recomputed,
  matches driver endpoint rule (`i == n-1` kept) and my census
  recompute leg-by-leg (448/344).
- Site-(b) algebra: `nfft >>= 1` precedes the super-twiddle loop
  (`scratch/parcel-w4kissfft/tree/kiss_fftr.c:33,53-57`), so the
  doc's "m = N/2" reading of the code's `nfft` is correct;
  dyadic-exactness argument stands.
- 12 KF rows in `demo/expected-kissfft.txt` identical to
  `scratch/parcel-w4kissfft/out/hashes-main.txt`; `fetches.jsonl`
  KissFFT row matches the parcel proposal (archive
  `205a8f6a...cf5cbf`, licence `4d6bcab4...2c0ed`); state sizes
  65800/82208/cpx16 match the w4 ledger.
- Trig-leg pointer figures: binary32 34,225,520,640 over 32
  shards, 0 mismatches, final_undecided 0
  (`ledger/parcel-w4trig.md:325-344`); f16 exhaustive + f64 100%
  worst-case + seeded >= 2^21 (lines 217-220). As cited.
- Claim surface: `git diff a51f31e --stat` shows only
  `docs/TWIDDLES.md`, `demo/twiddle_gate.c`, `docs/BOARD.md`,
  `demo/README.md`, `docs/metrics/briefs.jsonl`. No upstream
  code lines quoted in owned files (one-line phase paraphrases
  match the parcel ledger's own wording; exact-match anchors
  live in the pre-existing `demo/make_kissfft_tree.py`,
  untouched by this diff).
- Compat/shim appendix claims: `__wrap_sinpi/cospi/floor`
  present in `compat/msf_aeabi.[ch]`; `demo/kissfft_host_shim.c`
  provides `msf_wrap_state`/bit-casts/`copysign`/trap sink.

Not done (could not verify; left for the parcel):

- The 29 first-oracle mismatches over the full gate domain: no
  surviving log exists in the trail and the parcel scratch is
  out of bounds, so the count itself is unreproducible by
  anyone. Doc handles it correctly (marked unverified).
- `build/kissfft-tree/tree-inputs.sha256` board-run quote: the
  lead's tree is not an authority available here; relied on the
  scratch-tree measurement + script enforcement instead. The
  two intact hashes corroborate the chain; F2 breaks it for
  kiss_fftr.c in the doc text.
- No silicon/board claims re-checked (out of scope; no board
  flashing in this parcel or verification).
