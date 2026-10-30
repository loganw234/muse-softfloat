# A flake, recorded as one

A check that fails under load and passes alone is measured both ways before it is called anything.

## 9a. Measured both ways

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the card stress driver before the nights run it", line 23429; the entry "the card stress driver before the nights run it", line 23461. Not in this kit.
- **What it shows** (the kit's reading): A check that failed once under load and passed alone twice, measured both ways, and carried as load-sensitive.
- **Cut:** nothing.

> - **`sweep` alone, WSL** (the stage's one failure): `sweep: 9 checks, 0 failed` in 29 s, and again `9 checks, 0 failed` in 30 s, run alone at 08:22: so it failed once, niced inside the 583 s stage run on the loaded desktop, and passed alone twice (MEASURED both ways): load-sensitive.
> [...]
> - **`sweep resume: rates were rebuilt from the records` is load-sensitive** (the suite's own check, not changed): it needs a stand-in soak's measured rate to come out above about 1.05 M cases a second, and a niced process on a loaded desktop measured less, so the resumed run's first slice was the probe size: it failed once niced under load (the stage's WSL run) and passed alone, twice, niced in the same clone at 08:22 (MEASURED both ways: failed under load inside the 583 s stage run; `sweep: 9 checks, 0 failed`, 29 s, and again 30 s, alone). The box runs the stage in quiet hours.

## 9b. Pre-existing, and not touched

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "(parcel EX, Sonnet)", line 21590. Not in this kit.
- **What it shows** (the kit's reading): A pre-existing, timing-flaky check, not touched, recorded as a known limit by agreement with the lead; no gate is exposed.
- **Cut:** nothing.

> - **A pre-existing, timing-flaky check in the driver's suite, not touched**: `telemetry: the stand-in's temperature rises with time and the samples show it, in order` (hw/test_card_stress.py, scn_telemetry: `ts == sorted(ts)`), fed by the stand-in's xbutil emulation, whose counter every telemetry call takes: the driver's telemetry thread and its per-leg `telemetry()` calls can take counter values in one order and append their records in the other (READ by the lead in hw/card_stress.py and the stand-in). Seen once in this parcel's runs of the suite - run 4, a busy desktop (load 2.15), the sequence as printed `[31.0, 33.0, 35.0, 37.0, 40.0, 39.5, 43.0, 44.5, 47.0, 49.0, 51.0, 53.0, 54.5, 57.5, 58.0, 61.0, 63.0, 65.0]`, every value 30 + 0.5 n for a counter n taken, one pair recorded in the other order - and it passed in the other runs, in the old tests' runs included. Found at 0b77387's code and tests, which this parcel did not change here; reported to the lead, who agreed to record it as a known limit and put it on the round's follow-up list. No runner stage runs hw/test_card_stress.py (verify/run.sh does not mention it; hw/test-card-stress.sh is its only caller), so no gate is exposed.

---

These passages are excerpts of cft-fp256's docs/VALIDATION.md. cft-fp256 is Copyright 2026 Logan W., under the Apache License 2.0. The kit's NOTICE.md says what else it carries, and under which licence.
