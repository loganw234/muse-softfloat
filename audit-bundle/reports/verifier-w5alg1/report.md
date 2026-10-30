NOT READY

# verifier-w5alg1 report - SF-2 Step 2a rSqrt copy at worktrees/verify5-alg1

Copy HEAD `db941a6` (parent `7c3819c`). All probes from script files
in `scratch/verifier-w5alg1/` under Git Bash (MSYS2 gcc 16.1.0
x86_64, MPFR 4.2.2, MSF_PYTHON=` .venv/Scripts/python.exe` 3.12.15),
explicit `ulimit -v` ceilings on the long sweeps. The copy was never
modified (`git status` clean at close); regeneration targets went to
`out/` outside the copy. Nothing with `cft` in its name was opened,
searched, or listed; no parcel branch/worktree, key, scratch/lead,
or ledger/lead material was consulted. MPFR was executed as an
oracle only (Step 0b recipe); the `-0` verdict comes from the clause
extracts via the study, never from MPFR.

Own exact decider (`10_mydecider.py`, fresh integer implementation of
study Sec 3.1: normalize, `S = p + 9 + (p-1)/2`, `Q = isqrt(2^2S //
M')`, sticky, integer guard/round/sticky rounding; specials from the
study Sec 5.1 table): validated three ways before use - (i) MPFR
cross-decide 25,268 comparisons, 0 mismatches (`16_run.sh`); (ii)
boundary probe 17,595 decisions by independent midpoint-square
arithmetic, 0 fails, 0 ties (`18b_run.sh`); (iii) agreement with the
copy's committed vectors 3,594/3,595 (the 1 exception is committed
defect D3 below); exact-case census f16 20/31,743 reproduces the
study Sec 3.1 datum exactly. Zero ties seen in 577,233 decisions, so
`ta == te` everywhere per case, not by assumption.

## Counts (copy kernel vs own decider, counts printed by scripts)

- binary16 exhaustive: 65,536 encodings x 5 modes = **327,680
  total, 158,720 mismatches** (`12_run_f16.sh`). Split: 158,715 =
  all 31,743 positive-finite inputs x 5 modes; 5 = `-0` x 5 modes.
  All 168,960 remaining decisions match.
- binary32 directed (169 inputs) + seeded (20,000): 20,169 x 5 =
  **100,845 total, 50,840 mismatches** = 50,835 positive-finite +
  5 `-0` (`14_run_f32f64.sh`, `14b_run.sh`: negative-finite
  49,980/49,980 match).
- binary64 directed + seeded, same volume: **100,845 total, 51,195
  mismatches** = 51,190 positive-finite + 5 `-0` (negative-finite
  49,625/49,625 match).
- Copy's own runner on its committed vectors (`02_runner_alg.sh`):
  alg-f16 1,195 total: 140 pass / 1,055 fail; alg-f32 1,200: 140 /
  1,060; alg-f64 1,200: 139 / 1,061. VERDICT: FAIL x3.
- Specials whole table, three-way (`15_run.sh`): 375 kernel
  decisions, 15 mismatches, all `-0` x 5 modes x 3 formats. Both
  signed zeros, both infinities, negative-finite samples, qNaN/sNaN
  payload samples (sign x payload incl. quiet-bit variants) all
  otherwise bit- and flag-exact; NaN payload/sign preserved.

## Findings

**(b1) wrong answer - kernel finite-positive path (all formats,
all modes).** `alg_cmp_sq` returns the inverted sign
(`prod[i] > tv ? -1 : 1`): it reports -1 when `cand^2 * M'` EXCEEDS
2^(2S). The caller keeps the bit on `cmp <= 0`, i.e. keeps bits
while `cand^2 * M' >= 2^2S`. The top bit is always kept
(`2^(2*top) * M' >= 2^(2*top) * 2^(p-1) = 2^2S`), and every lower
bit preserves the property, so `q` saturates to `2^(top+1) - 1`
for every input with `sticky = 1` always. Observed: kernel outputs
depend only on the input exponent class (f16 inputs 1, 2, 3 all
give `7000/6fff`); exact cases get wrong+inexact.
Smallest repro (`01_probe.sh`, modes 0..4 = te/tz/tp/tn/ta):
`msf16_r_sqrt(0x3C00 /* 1.0 */, te)` -> `0x4000` flags `10`;
want `0x3C00` flags `00`.
Paper re-derivation (study Sec 3.1 checked, not replayed): with
`2^(p-1) <= M' < 2^(p+1)`, `Q = floor(2^S/sqrt(M'))` lies in
`(2^(S-(p+1)/2), 2^(S-(p-1)/2)]` = `(2^(p+7), 2^top]`, top =
20/33/62, so `cand < 2^63`, `M' < 2^54`; `cand^2 = a*2^64 + b`
gives `M'*a < 2^116`, `M'*b < 2^118`, sum `< 2^181` in 6 limbs vs
target limb (tl, tb) = (1,18)/(2,24)/(5,16) - the assembly is sound,
only the returned sign is inverted. Correct behavior (own decider,
MPFR-cross-decided): floor + sticky, i.e. keep bit iff
`cand^2 * M' <= 2^2S`.

**(b2) wrong answer - `rSqrt(-0)` pole sign (all formats, all
modes).** The zero path returns `fp->infinity` unconditionally,
discarding the input sign: `msf16_r_sqrt(0x8000, te)` ->
`0x7C00 (+inf)` flags `02`; the paired-sign cell (study Sec 5.1,
second-read in the parcel design entry) requires `0xFC00 (-inf)`
flags `02`. First-hand oracle record (`16_negzero.sh`): executed
MPFR `rec_sqrt(-0)` gives `+inf` - which is why this cell must be
(and in the committed vectors is) table-decided, never
oracle-sourced; the kernel's unsigned zero path agrees with MPFR
and disagrees with the clause. The committed vectors require
`-inf` x 5 modes x 3 formats, so the kernel fails its own
specials tree on this cell.

**(a) regression - table-seam regeneration refused; smoke/standard
cannot pass drift.** `tables/operations.tsv` carries the r_sqrt
row with claim `C-ULP`, but `CLAIM_BY_TIER` admits only `C-754`
for tier 2 and SF-2 Sec 1 pins the core-row claim token at
`C-754`. The copy's own generator refuses its own tables:
`gen_tables.py` -> `SystemExit: claim 'C-ULP' not admitted for
tier 2 family r_sqrt` (`17_run.sh`, `19b_standard.sh`:
`build/smoke/gen.log`). Consequence: smoke FAILs at drift
(`RUN.SH: FAIL - generator failed`), standard FAILs identically.
Smallest repro: `MSF_PYTHON=<pinned> python
worktrees/verify5-alg1/tools/gen_tables.py <tmpdir>`.

**(b3) wrong committed expectation (1 line).**
`tests/vectors/alg-f64.vec:4`: `msf64_r_sqrt te 0 ->
7ff0000000000000 00`; all four sibling modes (and every other
format) carry flags `02`, and the settled table requires
divideByZero on the `+0` pole. Regenerating the alg sets twice
(`18_run.sh`: byte-identical regen1 vs regen2 for all three
formats; f16/f32 match committed) produces `02` on that line, so
the committed file cannot have come from its own generator (whose
specials fill all 5 modes identically) - diff is exactly that
line (`18b_diff.sh`).

## Seam census (all `17_run.sh`, watched, not replayed)

- operations.tsv: 15 Tier-2 family rows incl. r_sqrt (`math_un`)
  and hypot (`math_bin`); implemented.tsv: 825 rows, 3 r_sqrt, 0
  hypot (planned-only holds).
- COVERAGE inventory: tier1 783/783; tier2 42 implemented, 3
  planned (`msf{16,32,64}_hypot`), 45 registered; bad rows 0;
  claim tokens exactly {C-754, required} in COVERAGE (the C-ULP
  token lives only in the operations row - see (a)).
- `math_bin` dispatch traced: gen_tables groups it with the
  binary branch, in REPLAYABLE + SIGS; `msf_dispatch.h` hypot rows
  carry `MSF_SIG_MATH_BIN` with NULL call, status 0 (planned);
  runner on a hypot line: `SKIP ... not implemented (planned wave
  5)` by name, never a pass.
- Controls watched: unknown sig token refused (`SystemExit:
  unknown sig class: math_bogus`); tier-inventory mutants
  (tier1-planned-flip, tier2-row-deleted) both refused by the
  inventory predicate.
- gen_tables regeneration: impossible in-copy (see (a)); the
  refusal itself is the byte-stability verdict. alg-set regen:
  twice byte-identical, f16/f32 match committed, f64 differs by
  (b3) only.

## Gates in the copy (`19_gates.sh`, `19b_standard.sh`)

- smoke: FAIL (drift, cause above). standard: FAIL (same drift
  stage). Unit/type/symbol/controls stages not reached.
- Target-compile `src/msf_alg.c` (arm-none-eabi-gcc 14.2.1,
  cortex-m0plus, run.sh flags): clean (`out/arm/msf_alg.o`).
- Type scan (`float|double` over src/ include/): clean.
- Claim surface vs parent `7c3819c`: 16 files, +4,575/-12, all
  brief-owned (2 ops rows, 3 implemented rows, gen_tables
  math_bin, run.sh totals+SRC+VECS, 4 regenerated outputs,
  msf_alg.c, decider+generator+3 vec files, VECTORS.md, WIDTHS
  row, metrics row); no board/ files (the board wiring escalation
  stands, untouched).

## Not done (named, not silent)

- No green smoke/standard in the copy: blocked by (a), (b1),
  (b2) - re-run after fix, not waived.
- Board sampled replay: board lock / lead work; no board
  flashing attempted.
- Binary32-exhaustive foreign-decider run: not brief-required;
  seeded MPFR differentials shipped instead (moot until (b1) is
  fixed).
- hypot parcel (A2), pown/compound/rootn legs: out of scope,
  hypot stays planned-only by name.
- f32/f64 full-exhaustive: infeasible volume; directed+seeded
  20,169 inputs x 5 modes per format is the stated evidence.

Defects are format-uniform (parity holds structurally): every
finding reproduces at binary16/32/64 alike.
