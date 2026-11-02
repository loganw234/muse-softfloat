# Bench records

This file is a set of measurement records from the bench firmware
(`board/bench_main.c`) running on the project board. The numbers
here are records of what was measured on the runs labelled below;
they are never performance claims, and no correctness verdict
rests on them (SF-0 Sections 5.1 and 6 item 9; the bench budget
stays never-a-verdict). The SDK-flavour rows are labelled baseline
rows recorded under the same labels; the tables are not a race and
support no ranking between rows or flavours.

## Method

- Firmware: `msf_bench` from `board/bench_main.c`, built under both
  SDK flavours (the pico default and `compiler`), code placed in
  flash and executed through the XIP cache at the default system
  clock. A short discarded warm-up per row runs before the timed
  repetitions so the timed loops start with a warm cache.
- Inputs: an in-code linear congruential generator (multiplier
  1664525, increment 1013904223, named seed `BENCH_LCG_SEED` =
  0x2545F491, per-row seed derived from it in the source). The
  generator restarts from the same seed for every repetition, so
  each repetition of a row sees the same operand sequence.
  Mantissas vary on every iteration; exponents stay in a mid
  normal range (binary16 biased exponents 8..22, binary32
  110..145, binary64 1000..1047; near-unity ranges for the
  `exp2`/`log2`/`sin_pi` rows), so operands are finite normals
  and divisors are never zero. Results accumulate into a printed
  64-bit row sink, together with the accumulated exception flags.
  Rounding is ties-to-even on every library row. The two SDK
  baseline rows retain their original volatile accumulator
  bodies, reset per repetition, with the final accumulator bits
  as the row sink.
- Timing: the RP2040 1 MHz timer (`time_us_64`) around each
  repetition's loop; cycles per operation are derived as
  `total_us * clk_sys_hz / (iters * 10^6)` (Cortex-M0+ has no
  cycle counter). Each row runs 5 repetitions; the table records
  the median cycles/op of the 5, with the minimum and maximum as
  the spread. Iteration counts are fixed per row (the same count
  in both flavours) and were scaled from on-board calibration
  passes so that every repetition takes at least 0.2 s; the
  count for each row is in the tables and in every raw log line.
- Sinks: the generator script below checks that each row prints
  the same sink on all 5 repetitions, and that every library
  row's sink is the same in both flavour logs (the SDK baseline
  sinks are recorded per flavour and are not required to agree).
  Both checks passed for the runs below, including the combined
  `msf_sink` on the `BENCH-DONE` line (`ddf708d4b1430c13` in both logs).
- The `empty_loop` row records the loop, generator and sink
  overhead measured the same way. It is reported as its own row;
  no overhead subtraction is applied anywhere in the tables.
- Source of the tables: the retained raw board logs
  `scratch/parcel-psbench/raw/bench-pico.log` (sha256 `c25b8f9db504b58bf90692d8f8b3d1498f7be3a4f60f6aa1cb4b6e35980e334b`)
  and `scratch/parcel-psbench/raw/bench-compiler.log` (sha256 `2f0574cc5d585a3ac1fba8c96103f9e2bfb4d47ed12905b458c0a9a5f4f0e69e`),
  each a label header (artifact hashes, compiler, sizes, target
  serial, port, lock holder) followed by the verbatim board
  output captured with `board/read_until.py`. The tables below
  are generated from those logs by the retained script
  `scratch/parcel-psbench/gen_bench.py`, which also recomputes
  every cycle figure from the raw `total_us`, iteration count
  and clock before writing anything; rerunning it on the same
  logs regenerates this file byte-identically. Sizes come from
  `arm-none-eabi-size` on each flavour's `msf_bench.elf`,
  recorded in the log headers.

## Run labels

| label | bench-pico | bench-compiler |
|---|---|---|
| date | 2026-11-01 18:43:48 -0700 | 2026-11-01 18:44:38 -0700 |
| git HEAD (worktree) | 1229010af903e6f061b5a55fd137156cdd6a24d9 | 1229010af903e6f061b5a55fd137156cdd6a24d9 |
| firmware ELF sha256 | 0a18c67dbecbfdaa056bad2c7ee1dd6d5c74c49f826a99415a3ceebed6526c4d | bb383ce11c1bddad4b79ab18a6269f18febd817377a226701b843f11f9bc86dd |
| firmware UF2 sha256 | 1e0d841ecb8c1922f48e710ff349005d300e411c5b18f85959da7cb324c4533a | a4186c8d18984d77de71c883b1d8fc7f66db9c200a37c31352f8a7f6e579f17d |
| compiler | arm-none-eabi-gcc.exe (Arm GNU Toolchain 14.2.Rel1 (Build arm-14.52)) 14.2.1 20241119 | arm-none-eabi-gcc.exe (Arm GNU Toolchain 14.2.Rel1 (Build arm-14.52)) 14.2.1 20241119 |
| board serial (flash target) | E66440A2CB6F5C2B | E66440A2CB6F5C2B |
| board COM port (detected by serial) | COM8 | COM8 |
| board lock holder | parcel-psbench via board/common.sh take_lock (job: parcel-psbench measured bench records (postseal-bench)) | parcel-psbench via board/common.sh take_lock (job: parcel-psbench measured bench records (postseal-bench)) |
| board ID in banner | e66440a2cb6f5c2b | e66440a2cb6f5c2b |
| SDK flavour in banner | pico(default: ROM-routed) | compiler |
| clk_sys (Hz) | 125000000 | 125000000 |
| placement | flash(xip,cached) | flash(xip,cached) |

## Sizes (`arm-none-eabi-size`, bytes)

| flavour build | text | data | bss |
|---|---:|---:|---:|
| bench-pico | 260012 | 0 | 3328 |
| bench-compiler | 267524 | 0 | 2812 |

## Records: bench-pico (flavour `pico(default: ROM-routed)`, clk_sys 125000000 Hz)

Median of 5 repetitions, with min/max spread. Cycles are derived
from the microsecond timer and the clock above. `sink` is the
row sink printed by every repetition of the row.

| row | iters/rep | median cycles/op | min cycles/op | max cycles/op | median time/rep (us) | sink |
|---|---:|---:|---:|---:|---:|---|
| empty_loop | 2400000 | 13.00 | 13.00 | 13.00 | 249669 | 00124fe69679cb80 |
| msf16_add | 10000 | 3120.86 | 3119.92 | 3121.76 | 249669 | 0000000014c14e0c |
| msf16_mul | 16000 | 2051.26 | 2050.25 | 2051.60 | 262562 | 000000001f5797e4 |
| msf16_fma | 9000 | 7410.56 | 7401.04 | 7411.36 | 533561 | 00000000132d72cf |
| msf16_div | 650 | 48784.42 | 48770.38 | 48788.84 | 253679 | 0000000001436c28 |
| msf16_sqrt | 1400 | 22530.89 | 22521.16 | 22531.96 | 252346 | 00000000014e54a9 |
| msf32_add | 9000 | 3573.06 | 3571.48 | 3574.72 | 257261 | 00001215ff112bd3 |
| msf32_mul | 16000 | 2047.93 | 2046.88 | 2048.15 | 262136 | 00001f4c130730b1 |
| msf32_fma | 3200 | 10092.85 | 10076.71 | 10099.29 | 258377 | 000006636bc8180c |
| msf32_div | 650 | 48699.61 | 48681.53 | 48707.30 | 253238 | 00000141d3596fa5 |
| msf32_sqrt | 1400 | 22456.87 | 22448.75 | 22459.10 | 251517 | 0000015d613b2b67 |
| msf64_add | 12000 | 2658.92 | 2658.05 | 2659.56 | 255257 | 0a2758cfd6b6ed92 |
| msf64_mul | 15000 | 2121.88 | 2120.58 | 2122.26 | 254626 | a54fb6a6f83f2085 |
| msf64_fma | 9000 | 3454.33 | 3452.62 | 3454.84 | 248712 | 0f5bb42a829cc989 |
| msf64_div | 550 | 56412.50 | 56387.04 | 56420.90 | 248215 | 42e5e01114ef9153 |
| msf64_sqrt | 1400 | 21862.67 | 21856.42 | 21864.19 | 244862 | e299829ceee3e538 |
| msf32_exp2 | 220 | 142592.04 | 142267.04 | 142618.75 | 250962 | 000000368be207c6 |
| msf32_log2 | 150 | 214334.16 | 213961.66 | 214527.50 | 257201 | 0000003d1e27a436 |
| msf32_sin_pi | 340 | 93118.75 | 92970.22 | 93189.70 | 253283 | 000000a9b4edb229 |
| msf64_exp2 | 210 | 148495.23 | 148294.64 | 148585.11 | 249472 | 783d58059f644e53 |
| msf64_log2 | 150 | 212218.33 | 211908.33 | 212254.16 | 254662 | f57c53ca48f6f8e7 |
| msf64_sin_pi | 330 | 94410.98 | 94193.93 | 94464.39 | 249245 | 588889e6b84f7379 |
| msf32_from_i32 | 37000 | 854.26 | 854.13 | 854.27 | 252862 | 00005033255eb30d |
| msf64_to_i32_ties_to_even | 28000 | 2365.18 | 2364.44 | 2366.30 | 529801 | 00001d68035a2d5b |
| msf32_from_f64 | 28000 | 1450.73 | 1450.43 | 1450.84 | 324964 | 000036a25f723daa |
| msf16_class | 750000 | 42.22 | 42.22 | 42.22 | 253360 | 00000000003d2536 |
| msf32_is_signaling | 1000000 | 33.03 | 33.03 | 33.03 | 264287 | 0000000000000770 |
| msf64_copy_sign | 250000 | 133.02 | 133.02 | 133.02 | 266045 | 8156999a081c5ec4 |
| msf_pack_f64(exemplar) | 47000 | 669.15 | 669.06 | 669.17 | 251601 | b1f8e38e38ef06e8 |
| sdk-flavour float add (baseline) | 400000 | 88.01 | 88.00 | 88.01 | 281647 | 00000000495bba18 |
| sdk-flavour double add (baseline) | 300000 | 113.01 | 113.01 | 113.02 | 271245 | 4124997300000000 |

Combined sinks from the `BENCH-DONE` line: `msf_sink=ddf708d4b1430c13`
(library rows), `sdk_sink=41249973495bba18` (the two SDK baseline
rows).

## Records: bench-compiler (flavour `compiler`, clk_sys 125000000 Hz)

Median of 5 repetitions, with min/max spread. Cycles are derived
from the microsecond timer and the clock above. `sink` is the
row sink printed by every repetition of the row.

| row | iters/rep | median cycles/op | min cycles/op | max cycles/op | median time/rep (us) | sink |
|---|---:|---:|---:|---:|---:|---|
| empty_loop | 2400000 | 13.00 | 13.00 | 13.00 | 249650 | 00124fe69679cb80 |
| msf16_add | 10000 | 2986.72 | 2985.30 | 2986.95 | 238938 | 0000000014c14e0c |
| msf16_mul | 16000 | 1917.18 | 1916.18 | 1917.44 | 245400 | 000000001f5797e4 |
| msf16_fma | 9000 | 3631.20 | 3629.22 | 3631.68 | 261447 | 00000000132d72cf |
| msf16_div | 650 | 48655.76 | 48635.76 | 48658.46 | 253010 | 0000000001436c28 |
| msf16_sqrt | 1400 | 22397.05 | 22388.83 | 22397.67 | 250847 | 00000000014e54a9 |
| msf32_add | 9000 | 4862.90 | 4861.62 | 4864.70 | 350129 | 00001215ff112bd3 |
| msf32_mul | 16000 | 1947.20 | 1946.23 | 1947.45 | 249242 | 00001f4c130730b1 |
| msf32_fma | 3200 | 9379.33 | 9363.63 | 9383.16 | 240111 | 000006636bc8180c |
| msf32_div | 650 | 49581.73 | 49565.19 | 49585.57 | 257825 | 00000141d3596fa5 |
| msf32_sqrt | 1400 | 22326.60 | 22316.33 | 22327.23 | 250058 | 0000015d613b2b67 |
| msf64_add | 12000 | 3762.62 | 3760.09 | 3764.17 | 361212 | 0a2758cfd6b6ed92 |
| msf64_mul | 15000 | 2021.31 | 2020.18 | 2021.43 | 242558 | a54fb6a6f83f2085 |
| msf64_fma | 9000 | 5321.65 | 5320.76 | 5324.45 | 383159 | 0f5bb42a829cc989 |
| msf64_div | 550 | 56322.72 | 56286.36 | 56327.50 | 247820 | 42e5e01114ef9153 |
| msf64_sqrt | 1400 | 21763.57 | 21755.62 | 21765.08 | 243752 | e299829ceee3e538 |
| msf32_exp2 | 220 | 142543.75 | 142338.63 | 142584.65 | 250877 | 000000368be207c6 |
| msf32_log2 | 150 | 216014.16 | 215748.33 | 216085.00 | 259217 | 0000003d1e27a436 |
| msf32_sin_pi | 340 | 93652.20 | 93439.33 | 93673.16 | 254734 | 000000a9b4edb229 |
| msf64_exp2 | 210 | 148767.85 | 148544.64 | 148875.00 | 249930 | 783d58059f644e53 |
| msf64_log2 | 150 | 214815.00 | 214435.83 | 214860.00 | 257778 | f57c53ca48f6f8e7 |
| msf64_sin_pi | 330 | 93888.25 | 93723.86 | 93920.45 | 247865 | 588889e6b84f7379 |
| msf32_from_i32 | 37000 | 854.26 | 854.20 | 854.32 | 252861 | 00005033255eb30d |
| msf64_to_i32_ties_to_even | 28000 | 1203.19 | 1202.93 | 1203.26 | 269516 | 00001d68035a2d5b |
| msf32_from_f64 | 28000 | 1152.56 | 1152.11 | 1152.63 | 258175 | 000036a25f723daa |
| msf16_class | 750000 | 42.22 | 42.22 | 42.22 | 253364 | 00000000003d2536 |
| msf32_is_signaling | 1000000 | 33.03 | 33.03 | 33.03 | 264307 | 0000000000000770 |
| msf64_copy_sign | 250000 | 133.03 | 133.02 | 133.03 | 266064 | 8156999a081c5ec4 |
| msf_pack_f64(exemplar) | 47000 | 669.14 | 669.07 | 669.14 | 251597 | b1f8e38e38ef06e8 |
| sdk-flavour float add (baseline) | 400000 | 118.01 | 118.01 | 118.01 | 377649 | 00000000495bba18 |
| sdk-flavour double add (baseline) | 300000 | 171.02 | 171.02 | 171.02 | 410452 | 4124997300000000 |

Combined sinks from the `BENCH-DONE` line: `msf_sink=ddf708d4b1430c13`
(library rows), `sdk_sink=41249973495bba18` (the two SDK baseline
rows).

## Reading the rows

- Rows are grouped as recorded: the `empty_loop` overhead row,
  binary16/32/64 arithmetic (`add`, `mul`, `fma`, `div`, `sqrt`),
  Clause 9.2 recommended-math rows (`exp2`, `log2`, `sin_pi`) at
  binary32 and binary64, three conversion rows, the four retained
  P0 exemplar rows, and the two retained SDK-flavour baseline
  rows. The library rows report the cost of the full loop body as
  written in `board/bench_main.c`, including operand generation
  from the in-code generator on every iteration.
- A re-run is `tools/run.sh bench` from the repository root under
  the board lock (see `docs/BOARD.md`); it rebuilds both flavours
  and prints fresh records. Fresh records replace nothing here by
  themselves: this file is regenerated from retained raw logs by
  the script named in the Method section.
