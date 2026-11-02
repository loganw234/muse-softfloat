# Bench records

This file is a set of measurement records from the bench firmware
(`board/bench_main.c`) running on the project board. The numbers
here are records of what was measured on the runs labelled below;
they are never performance claims, and no correctness verdict
rests on them (SF-0 Sections 5.1 and 6 item 9; the bench budget
stays never-a-verdict). The baseline rows are labelled rows
recorded under the same labels; the tables are not a race and
support no ranking between rows or flavours.

The design position these records sit under: this library is
built for exactness, not speed. It spends cycles on full
IEEE 754 semantics - correct rounding under every rounding
attribute, exception flags, exact results - that the stock
SDK routines in the baseline rows do not provide. The tables
below simply record what those choices measured out as on
the labelled runs.

## Graphs

Both graphs are drawn by `tools/bench_graphs.py` from the same
retained raw logs as the tables below (medians of 5 repetitions,
log scale). They show these records; they make no claim beyond
them.

![Grouped bar chart, log scale, of median cycles per operation on the RP2040 at 125 MHz (bench-pico run) for binary32 and binary64 add, multiply, fused multiply-add, divide and square root: muse-softfloat beside the stock SDK routines. Recorded medians: 32_add: muse-softfloat 3855.66 vs stock SDK 187.94 cycles/op, 32_mul: muse-softfloat 2115.44 vs stock SDK 174.69 cycles/op, 32_fma: muse-softfloat 9369.53 vs stock SDK 589.48 cycles/op, 32_div: muse-softfloat 48568.26 vs stock SDK 193.75 cycles/op, 32_sqrt: muse-softfloat 22325.00 vs stock SDK 126.01 cycles/op, 64_add: muse-softfloat 3758.06 vs stock SDK 243.81 cycles/op, 64_mul: muse-softfloat 2018.40 vs stock SDK 309.35 cycles/op, 64_fma: muse-softfloat 3353.69 vs stock SDK 501.97 cycles/op, 64_div: muse-softfloat 57083.63 vs stock SDK 345.14 cycles/op, 64_sqrt: muse-softfloat 21762.85 vs stock SDK 252.59 cycles/op.](img/bench_compare.png)

![Horizontal bar chart, log scale, of median cycles per operation for every library bench row (binary16/32/64 arithmetic, recommended-math, conversion and exemplar rows plus the empty-loop overhead row), recorded under both SDK flavours on the RP2040 at 125 MHz; values are the medians in the tables below.](img/bench_library.png)

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
  Rounding is ties-to-even on every library row.
- Stock-SDK baseline rows (`sdk32_*` / `sdk64_*`): native
  `float`/`double` operations - the arithmetic operators,
  `fmaf`/`fma`, `sqrtf`/`sqrt`, and casts - routed to whatever
  the build flavour selects (the pico default routes to the
  SDK/ROM routines, `compiler` to the compiler runtime). Their
  loop bodies have the same shape as the library rows: operands
  are regenerated from the same LCG on every iteration, with
  the same per-row seeding scheme and the same exponent ranges
  as the matching library rows (divisors never zero, square-
  root operands positive normals, conversion inputs in-range
  so the native conversions are defined), and result bit
  patterns accumulate into the printed 64-bit row sink. The
  two retained `sdk-flavour ... (baseline)` rows keep their
  original volatile accumulator bodies, reset per repetition,
  with the final accumulator bits as the row sink.
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
  row's sink is the same in both flavour logs. The baseline
  sinks are recorded per flavour and are not required to agree
  with anything: a baseline row has its own per-row seed and
  its own iteration count, so its sink is not an operand-
  matched checksum against the library row it sits beside.
  The checks above passed for the runs below, including the combined
  `msf_sink` on the `BENCH-DONE` line (`ddf708d4b1430c13` in both logs).
  In the `bench-pico` log, baseline sinks that happen to equal the
  matching library row's sink: none.
  In the `bench-compiler` log, baseline sinks that happen to equal the
  matching library row's sink: none.
  Baseline sinks identical in both flavour logs: `sdk32_add`, `sdk32_mul`, `sdk32_fma`, `sdk32_div`, `sdk32_sqrt`, `sdk64_add`, `sdk64_mul`, `sdk64_fma`, `sdk64_div`, `sdk64_sqrt`, `sdk32_from_i32`, `sdk64_to_i32`, `sdk32_from_f64`, `sdk-flavour float add (baseline)`, `sdk-flavour double add (baseline)`.
- The `empty_loop` row records the loop, generator and sink
  overhead measured the same way. It is reported as its own row;
  no overhead subtraction is applied anywhere in the tables.
- Source of the tables: the retained raw board logs
  `scratch/parcel-psbench2/raw/bench2-pico.log` (sha256 `5d66bf6f45ce62e70e47ea4c2b5d5d4f1d0585f75980a8571e46081abcde2f49`)
  and `scratch/parcel-psbench2/raw/bench2-compiler.log` (sha256 `0fddcc1defe8e648c3eddf63d7d6ee21f43c5f2fc9471ad7d36ec569726e4787`),
  each a label header (artifact hashes, compiler, sizes, target
  serial, port, lock holder) followed by the verbatim board
  output. Capture used the retained long-window reader
  `scratch/parcel-psbench2/read_until_long.py` (the extended
  suite outruns `board/read_until.py`'s 60 s window); the exact
  capture command is in each log's label header. The tables
  below are generated from those logs by the retained script
  `scratch/parcel-psbench2/gen_bench2.py`, which also recomputes
  every cycle figure from the raw `total_us`, iteration count
  and clock before writing anything; rerunning it on the same
  logs regenerates this file byte-identically. Sizes come from
  `arm-none-eabi-size` on each flavour's `msf_bench.elf`,
  recorded in the log headers.

## Run labels

| label | bench-pico | bench-compiler |
|---|---|---|
| date | 2026-11-01 20:27:36 -0700 | 2026-11-01 20:29:10 -0700 |
| git HEAD (worktree) | 607cab63d62d5fce463968a1d33c23d20a819cbd | 607cab63d62d5fce463968a1d33c23d20a819cbd |
| firmware ELF sha256 | 94586e8bf004e77e3b14131b477863f97e6c905415fc4765dad11361a2b288fa | 3e1da72f23b99c8a84e4e9169821844611776ecf0b2d6c8c9664ed5b6b445b51 |
| firmware UF2 sha256 | 022cf7c84a6b1a8883a4fcb9aeedd920f11ef56dc970561c1cc1a8b1f7aa724f | 4e8eb324148fb5e43cafc6df7ed94a99ca5ee1043fc7e3604d78b8f30e349ac8 |
| compiler | arm-none-eabi-gcc.exe (Arm GNU Toolchain 14.2.Rel1 (Build arm-14.52)) 14.2.1 20241119 | arm-none-eabi-gcc.exe (Arm GNU Toolchain 14.2.Rel1 (Build arm-14.52)) 14.2.1 20241119 |
| board serial (flash target) | E66440A2CB6F5C2B | E66440A2CB6F5C2B |
| board COM port (detected by serial) | COM8 | COM8 |
| board lock holder | parcel-psbench2 via board/common.sh take_lock (job: parcel-psbench2 bench2 final both (postseal-bench2)) | parcel-psbench2 via board/common.sh take_lock (job: parcel-psbench2 bench2 final both (postseal-bench2)) |
| board ID in banner | e66440a2cb6f5c2b | e66440a2cb6f5c2b |
| SDK flavour in banner | pico(default: ROM-routed) | compiler |
| clk_sys (Hz) | 125000000 | 125000000 |
| placement | flash(xip,cached) | flash(xip,cached) |

## Sizes (`arm-none-eabi-size`, bytes)

| flavour build | text | data | bss |
|---|---:|---:|---:|
| bench-pico | 269644 | 0 | 3328 |
| bench-compiler | 281436 | 0 | 3124 |

## Records: bench-pico (flavour `pico(default: ROM-routed)`, clk_sys 125000000 Hz)

Median of 5 repetitions, with min/max spread. Cycles are derived
from the microsecond timer and the clock above. `sink` is the
row sink printed by every repetition of the row.

| row | iters/rep | median cycles/op | min cycles/op | max cycles/op | median time/rep (us) | sink |
|---|---:|---:|---:|---:|---:|---|
| empty_loop | 2400000 | 14.00 | 14.00 | 14.00 | 268850 | 00124fe69679cb80 |
| msf16_add | 10000 | 2987.68 | 2986.35 | 2988.23 | 239015 | 0000000014c14e0c |
| msf16_mul | 16000 | 1918.46 | 1917.21 | 1918.50 | 245564 | 000000001f5797e4 |
| msf16_fma | 9000 | 3631.68 | 3629.95 | 3631.95 | 261481 | 00000000132d72cf |
| msf16_div | 650 | 48647.50 | 48637.11 | 48651.15 | 252967 | 0000000001436c28 |
| msf16_sqrt | 1400 | 22396.60 | 22390.17 | 22398.57 | 250842 | 00000000014e54a9 |
| msf32_add | 9000 | 3855.66 | 3854.73 | 3856.66 | 277608 | 00001215ff112bd3 |
| msf32_mul | 16000 | 2115.44 | 2115.17 | 2116.14 | 270777 | 00001f4c130730b1 |
| msf32_fma | 3200 | 9369.53 | 9366.01 | 9375.66 | 239860 | 000006636bc8180c |
| msf32_div | 650 | 48568.26 | 48550.00 | 48570.57 | 252555 | 00000141d3596fa5 |
| msf32_sqrt | 1400 | 22325.00 | 22318.30 | 22325.17 | 250040 | 0000015d613b2b67 |
| msf64_add | 12000 | 3758.06 | 3754.72 | 3759.38 | 360774 | 0a2758cfd6b6ed92 |
| msf64_mul | 15000 | 2018.40 | 2017.32 | 2018.57 | 242208 | a54fb6a6f83f2085 |
| msf64_fma | 9000 | 3353.69 | 3352.90 | 3354.41 | 241466 | 0f5bb42a829cc989 |
| msf64_div | 550 | 57083.63 | 57071.59 | 57095.68 | 251168 | 42e5e01114ef9153 |
| msf64_sqrt | 1400 | 21762.85 | 21756.51 | 21765.44 | 243744 | e299829ceee3e538 |
| msf32_exp2 | 220 | 144306.81 | 144222.15 | 144405.11 | 253980 | 000000368be207c6 |
| msf32_log2 | 150 | 216429.16 | 216055.00 | 216507.50 | 259715 | 0000003d1e27a436 |
| msf32_sin_pi | 340 | 93388.60 | 93296.69 | 93521.69 | 254017 | 000000a9b4edb229 |
| msf64_exp2 | 210 | 148429.76 | 148172.02 | 148610.11 | 249362 | 783d58059f644e53 |
| msf64_log2 | 150 | 212260.83 | 211879.16 | 212315.83 | 254713 | f57c53ca48f6f8e7 |
| msf64_sin_pi | 330 | 94803.40 | 94642.80 | 94826.13 | 250281 | 588889e6b84f7379 |
| msf32_from_i32 | 37000 | 855.18 | 855.15 | 855.25 | 253135 | 00005033255eb30d |
| msf64_to_i32_ties_to_even | 28000 | 1400.21 | 1399.80 | 1400.55 | 313649 | 00001d68035a2d5b |
| msf32_from_f64 | 28000 | 1153.46 | 1153.23 | 1153.53 | 258377 | 000036a25f723daa |
| msf16_class | 750000 | 40.22 | 40.22 | 40.22 | 241362 | 00000000003d2536 |
| msf32_is_signaling | 1000000 | 33.03 | 33.03 | 33.03 | 264289 | 0000000000000770 |
| msf64_copy_sign | 250000 | 133.02 | 133.02 | 133.03 | 266059 | 8156999a081c5ec4 |
| msf_pack_f64(exemplar) | 47000 | 677.18 | 677.11 | 677.21 | 254621 | b1f8e38e38ef06e8 |
| sdk32_add | 200000 | 187.94 | 187.94 | 187.95 | 300710 | 00018fe69ec53546 |
| sdk32_mul | 215000 | 174.69 | 174.68 | 174.69 | 300469 | 0001a57c90508b66 |
| sdk32_fma | 65000 | 589.48 | 589.43 | 589.50 | 306534 | 000082e5cb67cb85 |
| sdk32_div | 195000 | 193.75 | 193.73 | 193.75 | 302250 | 00017b2faffc94cb |
| sdk32_sqrt | 300000 | 126.01 | 126.01 | 126.01 | 302432 | 000123c0c3c41fc6 |
| sdk64_add | 155000 | 243.81 | 243.80 | 243.81 | 302325 | ff222a112b39f5bd |
| sdk64_mul | 125000 | 309.35 | 309.34 | 309.36 | 309353 | 15dc67a7790c9b6b |
| sdk64_fma | 75000 | 501.97 | 501.96 | 501.97 | 301183 | 44ff88c50e3fbd8f |
| sdk64_div | 110000 | 345.14 | 345.13 | 345.16 | 303728 | 9b2400a035d7d945 |
| sdk64_sqrt | 150000 | 252.59 | 252.57 | 252.60 | 303119 | b06da5377092b25f |
| sdk32_from_i32 | 560000 | 67.21 | 67.21 | 67.21 | 301122 | 0004bf3333a3378a |
| sdk64_to_i32 | 340000 | 111.30 | 111.30 | 111.31 | 302755 | 000158a66c185289 |
| sdk32_from_f64 | 305000 | 123.52 | 123.52 | 123.52 | 301405 | 000253dc56bb1b52 |
| sdk-flavour float add (baseline) | 400000 | 94.01 | 94.00 | 94.01 | 300845 | 00000000495bba18 |
| sdk-flavour double add (baseline) | 300000 | 119.01 | 119.01 | 119.01 | 285645 | 4124997300000000 |

Combined sinks from the `BENCH-DONE` line: `msf_sink=ddf708d4b1430c13`
(library rows), `sdk_sink=e6c31cb807017a9a` (the stock-SDK baseline
rows, including the two retained volatile rows).

## Records: bench-compiler (flavour `compiler`, clk_sys 125000000 Hz)

Median of 5 repetitions, with min/max spread. Cycles are derived
from the microsecond timer and the clock above. `sink` is the
row sink printed by every repetition of the row.

| row | iters/rep | median cycles/op | min cycles/op | max cycles/op | median time/rep (us) | sink |
|---|---:|---:|---:|---:|---:|---|
| empty_loop | 2400000 | 14.00 | 14.00 | 14.00 | 268849 | 00124fe69679cb80 |
| msf16_add | 10000 | 2987.41 | 2986.30 | 2987.78 | 238993 | 0000000014c14e0c |
| msf16_mul | 16000 | 1918.15 | 1917.31 | 1918.25 | 245524 | 000000001f5797e4 |
| msf16_fma | 9000 | 3631.01 | 3629.95 | 3631.16 | 261433 | 00000000132d72cf |
| msf16_div | 650 | 48655.57 | 48637.69 | 48660.19 | 253009 | 0000000001436c28 |
| msf16_sqrt | 1400 | 22398.03 | 22390.08 | 22398.57 | 250858 | 00000000014e54a9 |
| msf32_add | 9000 | 2877.47 | 2875.76 | 2877.59 | 207178 | 00001215ff112bd3 |
| msf32_mul | 16000 | 1948.35 | 1947.25 | 1948.51 | 249389 | 00001f4c130730b1 |
| msf32_fma | 3200 | 9236.95 | 9231.52 | 9241.83 | 236466 | 000006636bc8180c |
| msf32_div | 650 | 49208.46 | 49185.38 | 49217.69 | 255884 | 00000141d3596fa5 |
| msf32_sqrt | 1400 | 22326.51 | 22317.58 | 22326.87 | 250057 | 0000015d613b2b67 |
| msf64_add | 12000 | 2559.31 | 2558.07 | 2559.61 | 245694 | 0a2758cfd6b6ed92 |
| msf64_mul | 15000 | 2018.26 | 2017.25 | 2018.32 | 242192 | a54fb6a6f83f2085 |
| msf64_fma | 9000 | 4677.01 | 4673.12 | 4680.13 | 336745 | 0f5bb42a829cc989 |
| msf64_div | 550 | 56320.22 | 56287.72 | 56326.13 | 247809 | 42e5e01114ef9153 |
| msf64_sqrt | 1400 | 21763.03 | 21756.51 | 21765.17 | 243746 | e299829ceee3e538 |
| msf32_exp2 | 220 | 143172.72 | 142943.18 | 143239.20 | 251984 | 000000368be207c6 |
| msf32_log2 | 150 | 218145.00 | 217870.83 | 218250.83 | 261774 | 0000003d1e27a436 |
| msf32_sin_pi | 340 | 93279.04 | 93101.10 | 93311.39 | 253719 | 000000a9b4edb229 |
| msf64_exp2 | 210 | 150595.83 | 150375.59 | 150707.14 | 253001 | 783d58059f644e53 |
| msf64_log2 | 150 | 214882.50 | 214480.83 | 214965.83 | 257859 | f57c53ca48f6f8e7 |
| msf64_sin_pi | 330 | 93253.40 | 93070.07 | 93288.63 | 246189 | 588889e6b84f7379 |
| msf32_from_i32 | 37000 | 855.24 | 855.22 | 855.36 | 253153 | 00005033255eb30d |
| msf64_to_i32_ties_to_even | 28000 | 1204.20 | 1203.95 | 1204.23 | 269741 | 00001d68035a2d5b |
| msf32_from_f64 | 28000 | 1153.43 | 1153.14 | 1153.48 | 258369 | 000036a25f723daa |
| msf16_class | 750000 | 40.22 | 40.22 | 40.23 | 241376 | 00000000003d2536 |
| msf32_is_signaling | 1000000 | 33.03 | 33.03 | 33.03 | 264292 | 0000000000000770 |
| msf64_copy_sign | 250000 | 133.02 | 133.02 | 133.02 | 266054 | 8156999a081c5ec4 |
| msf_pack_f64(exemplar) | 47000 | 677.14 | 677.08 | 677.15 | 254605 | b1f8e38e38ef06e8 |
| sdk32_add | 200000 | 224.28 | 224.27 | 224.28 | 358858 | 00018fe69ec53546 |
| sdk32_mul | 215000 | 262.33 | 262.32 | 262.33 | 451220 | 0001a57c90508b66 |
| sdk32_fma | 65000 | 882.95 | 882.92 | 882.96 | 459134 | 000082e5cb67cb85 |
| sdk32_div | 195000 | 557.51 | 557.50 | 557.52 | 869728 | 00017b2faffc94cb |
| sdk32_sqrt | 300000 | 879.82 | 879.81 | 879.82 | 2111574 | 000123c0c3c41fc6 |
| sdk64_add | 155000 | 314.32 | 314.32 | 314.32 | 389763 | ff222a112b39f5bd |
| sdk64_mul | 125000 | 494.69 | 494.67 | 494.70 | 494694 | 15dc67a7790c9b6b |
| sdk64_fma | 75000 | 747.28 | 747.26 | 747.29 | 448371 | 44ff88c50e3fbd8f |
| sdk64_div | 110000 | 624.46 | 624.44 | 624.47 | 549531 | 9b2400a035d7d945 |
| sdk64_sqrt | 150000 | 1902.53 | 1902.49 | 1902.54 | 2283038 | b06da5377092b25f |
| sdk32_from_i32 | 560000 | 122.09 | 122.08 | 122.09 | 546986 | 0004bf3333a3378a |
| sdk64_to_i32 | 340000 | 137.13 | 137.13 | 137.14 | 373016 | 000158a66c185289 |
| sdk32_from_f64 | 305000 | 165.03 | 165.01 | 165.03 | 402681 | 000253dc56bb1b52 |
| sdk-flavour float add (baseline) | 400000 | 124.01 | 124.01 | 124.01 | 396848 | 00000000495bba18 |
| sdk-flavour double add (baseline) | 300000 | 177.02 | 177.00 | 177.02 | 424852 | 4124997300000000 |

Combined sinks from the `BENCH-DONE` line: `msf_sink=ddf708d4b1430c13`
(library rows), `sdk_sink=e6c31cb807017a9a` (the stock-SDK baseline
rows, including the two retained volatile rows).

## Reading the comparison

The `sdk32_*` / `sdk64_*` rows and the library rows now share
the same loop-body shape (operand generation from the same
LCG on every iteration, results folded into a printed sink),
and no overhead subtraction is applied anywhere: every number
above is the recorded cost of the full loop body as written
in `board/bench_main.c`. The operations inside the bodies
are not doing the same IEEE work, and that difference is the
point of recording them side by side: a library row computes
the exact result, rounds it under the requested rounding
attribute, and reports exception flags; a stock row computes
with whatever rounding and flag behaviour the SDK routine
provides and reports no flags. On these labelled runs the
recorded medians were the ones in the tables above; any
ratio computed from them is arithmetic on these records and
nothing more. For convenience, that arithmetic for the ten
operation-matched pairs (library median divided by baseline
median, `bench-pico` run):

| pair | muse-softfloat median cycles/op | stock SDK median cycles/op | ratio of the two recorded medians |
|---|---:|---:|---:|
| msf32_add / sdk32_add | 3855.66 | 187.94 | 20.52 |
| msf32_mul / sdk32_mul | 2115.44 | 174.69 | 12.11 |
| msf32_fma / sdk32_fma | 9369.53 | 589.48 | 15.89 |
| msf32_div / sdk32_div | 48568.26 | 193.75 | 250.67 |
| msf32_sqrt / sdk32_sqrt | 22325.00 | 126.01 | 177.17 |
| msf64_add / sdk64_add | 3758.06 | 243.81 | 15.41 |
| msf64_mul / sdk64_mul | 2018.40 | 309.35 | 6.52 |
| msf64_fma / sdk64_fma | 3353.69 | 501.97 | 6.68 |
| msf64_div / sdk64_div | 57083.63 | 345.14 | 165.39 |
| msf64_sqrt / sdk64_sqrt | 21762.85 | 252.59 | 86.16 |

Those ratios describe only these runs, these operand ranges
and these loop bodies. They are not a general statement
about either implementation, and no ranking between rows
or flavours is made anywhere in this file.

## Reading the rows

- Rows are grouped as recorded: the `empty_loop` overhead row,
  binary16/32/64 arithmetic (`add`, `mul`, `fma`, `div`, `sqrt`),
  Clause 9.2 recommended-math rows (`exp2`, `log2`, `sin_pi`) at
  binary32 and binary64, three library conversion rows, the
  four retained P0 exemplar rows, the thirteen stock-SDK
  baseline rows in library loop-body shape, and the two
  retained volatile baseline rows. Every row reports the cost
  of the full loop body as written in `board/bench_main.c`,
  including operand generation from the in-code generator on
  every iteration (the two retained volatile rows excepted,
  whose bodies are the original accumulator form).
- A re-run is `tools/run.sh bench` from the repository root under
  the board lock (see `docs/BOARD.md`); it rebuilds both flavours
  and prints fresh records. Fresh records replace nothing here by
  themselves: this file is regenerated from retained raw logs by
  the script named in the Method section, and the graphs are
  redrawn from the same logs by `tools/bench_graphs.py`.
