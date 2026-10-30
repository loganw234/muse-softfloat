# verifier-readme (ParcelRound, lead README update)

NOT READY. Full report: `scratch/verifier-readme/report.md`.

## Verdict

Six disconfirming findings against `worktrees/verify-readme/README.md`:

1. "833 of 822 instantiations" — copy's `docs/COVERAGE.tsv` holds 822 data
   rows (783 tier-1 + 39 tier-2, all implemented); `tools/run.sh` pins the
   same 783/39. Correct: 822 of 822.
2. "1,463,946 committed vectors" — recount of `tests/vectors/*.vec` gives
   146,442 data lines; `docs/RECORD.md` agrees ("smoke is now 146,442").
3. "50 of 50 plants caught across four waves" —
   `docs/metrics/plants.jsonl` has 50 rows with wave1 plant 5 graded
   `missed`; RECORD's Step 2c workload entry says "49 of 50 cumulative".
4. KissFFT described as "unmodified" — `docs/BOARD.md` and RECORD's Step 2c
   entry state Fork B's one named change and that "unmodified KissFFT is
   never claimed".
5. On-silicon 12/12 KissFFT sentence vs stale `docs/BOARD.md` ("not yet run
   on silicon ... gates any on-silicon sentence") in the same copy; RECORD
   records the 12/12 run, so BOARD.md must be updated before the sentence
   stands.
6. "Expansion studies for the deferred families are under way" — no
   authority located in the copy.

Agreed (sourced): 783/783 Tier 1, 39 Tier-2 rows, `standard` +1,117,504,
IAS15 2,000 steps / 2,001 records exact vs unmodified desktop, interval
710/710 host==board, KissFFT sizes/licence/scratch-only/12 configs, trig
evidence shape, deferred list vs SF-1 §7 + SF-0 §2.7, location table paths,
silent 180 s `video/out/final.mp4`, front-door/merge-gate wording.

## Unresolved (unaudited, not findings)

- Live `tools/run.sh smoke` not executed; counts rest on file recounts +
  RECORD/`run.sh` reading.
- `final.mp4` duration/silence via `video/README.md`, no independent probe.
- Process sentences (external ledger archiving, commit trailers, standing
  permission) spot-checked only.
