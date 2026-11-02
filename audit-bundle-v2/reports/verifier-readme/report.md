NOT READY

Audit of `worktrees/verify-readme/README.md` against in-copy evidence only
(`docs/COVERAGE.tsv`, `docs/RECORD.md`, `docs/BOARD.md`,
`docs/metrics/*.jsonl`, `docs/studies/SF-0.md`/`SF-1.md`, `tables/`,
`tools/run.sh`, `board/` and `video/` listings). Stance: disconfirm only.
Copy is a detached worktree; it was not modified. No `cft` names were
opened. No smoke run was executed; counts below are recounted from the
artefacts by read-only commands.

## Per-claim table

| README claim (line) | In-copy source | Agree? |
|---|---|---|
| L18-19 "833 of 822 instantiations" | `docs/COVERAGE.tsv`: 822 data rows, all `implemented` (783 tier 1 + 39 tier 2, recounted); `tools/run.sh` L134-135 pins TIER1 783 / TIER2 39 | DISAGREE (F1) |
| L22-23 "full Clause 5 surface ... (783/783)" | COVERAGE recount: 783 tier-1 rows, all implemented | Agree |
| L25-28 "plus 39 Tier 2 rows: 9.6 min/max, payload accessors, correctly rounded sinPi/cosPi, every family at all three formats" | COVERAGE recount: 39 tier-2 rows implemented; RECORD Step 1 (L670-689) + Step 2c kernel (L716-724) | Agree |
| L29-30 "gated against Berkeley TestFloat 3e, MPFR, or an exact reference" | COVERAGE `authority` column + `tests/VECTORS.md` provenance tags | Agree |
| L30 "1,463,946 committed vectors" | `tests/vectors/*.vec` recount: 146,442 data lines; RECORD L735 "smoke is now 146,442 vectors (43,492 trig lines)" | DISAGREE (F2) |
| L30 "`standard` adds 1,117,504" | RECORD L247-248 (917,504 exhaustive-binary16 + 200,000 pack sweep); `tools/run.sh` `standard()` generates `f16-exhaustive` + 200,000 `pack-sweep` | Agree (by code/record reading; gate-time generation not executed) |
| L31-32 "50 of 50 plants caught across four waves" | `docs/metrics/plants.jsonl`: 50 rows, wave1 plant 5 graded `missed`; RECORD Step 2c workload entry: "5 of 5 plants (49 of 50 cumulative)" | DISAGREE (F3) |
| L33-36 "IAS15 ... reproduces the unmodified desktop build's state hashes for 2,000 steps (2,001/2,001 records)" | RECORD L557-560 (`matched=2001 first_divergence=None`); BOARD L75-80 (`R 2000 1`, equal for all 2001 records) | Agree |
| L36-37 "interval-geometry catalogue streams host==board bit-for-bit" | RECORD L703-706 (710/710 rows, IW1 `ce81d66e...a9aec` both sides); BOARD L102-105; `tests/interval_catalogue.tsv` recount: 710 data rows | Agree |
| L37-39 "KissFFT — BSD-3, scratch-only, unmodified, runtime twiddles by sinpi/cospi, all 12 configuration hashes at N=256/1024/4096" | `docs/metrics/fetches.jsonl` KissFFT row (131.2.0, BSD-3, never vendored); BOARD L115-132 (Fork B, sizes, 12 configs) | DISAGREE on "unmodified" (F4); sizes/count/licence/scratch-only agree |
| L39 on-silicon KissFFT match | RECORD Step 2c workload entry (12/12 KF rows bit-identical) BUT BOARD L110-113 in the same copy says "not yet run on silicon ... gates any on-silicon sentence" | DISAGREE — internally inconsistent evidence (F5) |
| L27-28 "correctly rounded sinPi/cosPi ... all three formats" | RECORD L716-724 (f16 exhaustive, f32 exhaustive finite 34,225,520,640 checks, f64 worst-case + 2^21 sweep, zero mismatches vs MPFR deciders) | Agree |
| L49-56 deferred/refused list | SF-1 §7 (L560-586): wrappers, ties-to-away, roundToOdd (never public), 9.5, 9.4, other 9.2 deferred; SF-0 §2.7 (L264-290): binary128/decimal/Clause 8 never | Agree, except F6 |
| L56-57 "Expansion studies for the deferred families are under way" | No authority located in copy (no RECORD hit) | DISAGREE — no authority (F6) |
| L61-62 "silent 180-second cut is video/out/final.mp4" | `video/out/final.mp4` exists (17,014,776 bytes); `video/README.md` L5/L32/L102: 180.0 s, silent, no audio stream | Agree (durations via video/README, not an independent probe) |
| L69-86 location table (every path) | All paths exist in copy (KICKOFF/HARNESS/BOARD/studies/RECORD/COVERAGE/WIDTHS/tables/include/src/compat/tests/board/tools/video/metrics/AGENTS.md/LICENSE checked) | Agree |
| L74 "studies/ SF-0 and SF-1, the approved plans of record" | `docs/studies/` holds exactly SF-0.md + SF-1.md | Agree |
| L44-47 front door, inventories, drift/controls refusal, `standard` merge gate, AGENTS budgets | `tools/run.sh` (budgets, drift_check, controls, inventory_check); AGENTS.md L8-16 budgets with measured costs | Agree |
| L93-104 ground rules (authority, negative controls, parcel/verifier split, standing permission, commit trailers) | Spot-checked: SF-0 §4, run.sh controls, RECORD chain, KICKOFF 2026-10-26 | Not fully audited — see not-done list |
| L105-106 clean-room, SF-0 §4.5 | SF-0 L466+ §4.5 + L296-306 | Agree |
| L88-89 ledger/scratch live outside repo, archived at close | No in-copy authority (external by design) | Unaudited — see unresolved |
| L10-14 headline (IAS15 bit-identical, same source/same bits; 3-minute video) | IAS15: RECORD L557-560; video: video/README | Agree |

## Findings

- F1 (README L18-19): "833 of 822 instantiations" is impossible against the
  copy's own ledger: 822 data rows total, 783 tier-1 + 39 tier-2, all
  `implemented`. Correct figure is 822 of 822. (Likely origin: 783 + 50
  plants = 833.)
- F2 (README L30): "1,463,946 committed vectors" contradicts the recount:
  146,442 committed data lines across `tests/vectors/*.vec`, confirmed by
  RECORD L735. Appears to be a 10x digit error.
- F3 (README L31-32): "50 of 50 plants caught across four waves" contradicts
  `docs/metrics/plants.jsonl` (50 rows; wave1 plant 5 graded `missed`,
  regen-drift filing) and RECORD's own "49 of 50 cumulative". Correct: 49 of
  50 (four waves is correct: wave1-wave4 present).
- F4 (README L37-38): "unmodified" KissFFT contradicts BOARD L118-122 and
  RECORD's Step 2c workload entry: Fork B carries exactly one named change
  (exact cycle fractions into sinpi/cospi instead of radian phases into
  sin/cos) and "unmodified KissFFT is never claimed".
- F5 (README L39 vs BOARD L110-113): the on-silicon 12/12 KissFFT sentence
  has RECORD authority (Step 2c workload entry) but the same copy's BOARD.md
  still says the target is "not yet run on silicon" and that the run "gates
  any on-silicon sentence". The copy is internally inconsistent; BOARD.md is
  stale and must be updated before the README sentence can stand.
- F6 (README L56-57): "Expansion studies for the deferred families are under
  way" — no authority located anywhere in the copy. Either cite it or drop
  the sentence.

## Not-done list

- `bash tools/run.sh smoke` was not executed (brief permits it for vector
  counts); committed total is recounted from files + RECORD, and the
  `standard` +1,117,504 figure rests on `run.sh` code reading + RECORD, not a
  live gate-time generation.
- `final.mp4` duration/silence taken from `video/README.md` + `probe.py`
  record, not an independent ffprobe of the file.
- Ground-rules/process sentences (L88-104: ledger archiving, commit
  trailers, standing permission, verifier-between-parcels) spot-checked only,
  not audited claim by claim.
- Style/taste not assessed per brief.
