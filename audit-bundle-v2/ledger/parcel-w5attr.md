## 2026-10-28 05:28:26 -07:00 - Design entry: roundTiesToAway as fifth public rounding attribute (SF-2 Step 1, 255 attr rows, 0 new rows), written BEFORE any code change

Measured/read: brief `ledger/briefs/w5-attr.md` read first and
obeyed; `docs/studies/SF-2.md` Secs. 2,6-9 (worktree copy) and
`scratch/sf2-attribute/report.md` in full. Worktree
`worktrees/w5-attr` verified on branch `wave5-attr` at base
`889ec2e`, clean. Fences: nothing with `cft` in its name
opened/searched/listed; raw MPFR `RNDNA` prohibited (study
Sec. 2.2, executed incoherence); Berkeley stays an executed
oracle only; no board flashing; never push/merge.

### 1. Kernel delta (exactly the study's two sites)

Study Sec. 1.1-1.2 re-verified in source: internal mode 4
already exists, `msf_roundpack.c` `round_inc` already carries
the ties-to-away arm and the study measured 6,275,532 Berkeley
`-rnear_maxMag` cases PASS on the unmodified kernel. The only
out-of-pack rounding sites are in `src/msf_string.c`:
- `dec_round_inc` (line 411): add
  `case MSF_IROUND_TIES_TO_AWAY: return gt_half || eq_half;`
  (magnitude increment iff dropped > half or exactly half;
  sign-independent because the function decides magnitude).
- `to_hex_generic` precision switch (line 1151): add
  `case MSF_IROUND_TIES_TO_AWAY: inc = dropped >= half;`
No other `src/` edit. Stop condition (study 1, brief 1): if
generation/replay exposes a third out-of-pack rounding site
in the kernel, STOP and report; the enum must not ship
partially honoured. `src/msf_roundpack.c` is NOT owned and
will not be touched.

### 2. Seam

`tools/gen_tables.py` header prelude (lines 351-358): add
`MSF_ROUND_TIES_TO_AWAY = 4`, rewrite the "exists only in the
operation-named forms" sentence to name five attributes (the
decimal-required ties-to-away now provided for binary as a
permitted extension, claimable per row). Regenerate
`include/muse_softfloat.h` + `docs/COVERAGE.tsv` (and the
other drift-checked generated files); contents otherwise
unchanged, 0 new rows, inventory stays 783+39.
`tests/VECTORS.md`: rm token line gains `ta` for public
attribute-taking operations (no longer internal-pack-only),
plus provenance rows for any new ta tag (see 4).
`tools/run.sh` `controls()`: new control 3b swapping te<->ta
(wrong-mode; must be refused) alongside the existing te<->tz
pack64 control. Shape: run it on a committed file that after
regeneration carries both te and ta lines with genuinely
different expectations (a tie-rich directed file), swapping
the rm token both ways; the runner must FAIL. Chosen file and
awk shape fixed at implementation after counts confirm tie
lines exist in it; the control is watched to fail before it
is trusted (and watched again in the scratch gate against a
deliberately unswapped file as a positive check of the awk).
`docs/metrics/briefs.jsonl`: append my row (wave5, base
889ec2e..., time box 600 from the brief).

### 3. Generators (evidence side; mode lists to five)

- `gen_vectors_f16.py`, `gen_vectors_f32.py`: `RMS4` ->
  five modes incl. `ta`. References verified already ta-armed
  (`_round_inc_mag`/`to_inf`/integer refs carry `ta`).
- `gen_vectors_f64.py`: `RMS` -> five; pool-mixing modulo at
  line 580 `% 4` -> `% len(RMS)`. The directed FMA subset
  `("te","tn")` at line 605 stays a two-mode subset as today
  (it is not the full directed sweep; ta FMA volume comes from
  Berkeley + xf/f16/f32 directed + the pair-mode cycle now
  reaching ta). Existing `("te","ta")` tininess pair at 614
  unchanged.
- `gen_vectors_xf.py`: `RMS4` -> five PLUS reference fixes:
  `_round_q` (line 137) gains `ta: inc = twice >= den`;
  `pack_mag` `to_inf` (line 188) gains `rm in ("te","ta")`
  form. Trap/pair mode cycles `% 4` (lines 738,757) ->
  `% len(RMS4)`. `exhaustive_f16` sqrt mode tuple
  `("te","tp","tn")` (line 1023): leave as-is for that legacy
  scratch entry point (conv is exact/widening; sqrt ta==te by
  proof in 4); the parcel's binary16 five-mode exhaustive
  gate is separate (see 5) and does not rely on it. If time
  permits, widening it is a one-word change recorded here as
  optional, not load-bearing.
- `gen_vectors_str.py`: `RMS` -> five PLUS reference fixes.
  Study names 3 arms; my read finds FOUR sites lacking a ta
  arm, and all four get one (recorded as a study undercount
  in the results entry, generator-side only, NOT a kernel
  third site): `_round_ratio_to_int` (90, `ta: twice >= den`),
  `pack_ratio` `to_inf` (129, `rm in ("te","ta")`),
  `dec_round_inc` (194, `ta: tail >= half`),
  `to_hex_ref` precision switch (514, `ta: dropped >= half`).
  Bulk mode pick `randint(0,3)` (864) -> `randint(0,len-1)`.
  Directed pass at line 699 `["tz","tp","tn"]  # te covered
  above` gains `ta` (it enumerates the non-te modes for that
  family; ta belongs in that enumeration).
- `gen_vectors_trig.py`: relabel route (see 4), RMS for the
  decider stays four; a ta line is emitted per decided line
  from the te expectation with relabel provenance.
- `gen_vectors.py`: already five-mode, no change.
  `berkeley_ingest.py`: already maps ta, no change.
  `gen_vectors_tier2.py`: min/max + payload take no rounding
  attribute, no change (verified: no RMS list).
Volume: ta at directed-mode volume (~tz column, ~+20k
committed lines). Directed loops (`for rm in RMS/RMS4` over
tie-rich directed pools) are the gate; seeded/random sweeps
gaining ta via `rng.choice` are volume, not the gate (study
Sec. 2.1: random sets are tie-poor). After regeneration,
count ta lines per file and ta lines whose expected
result/flags differ from the same-operand te line (tie
witnesses) per family; a family with zero tie witnesses
where ties can occur (study Sec. 2.2 list) is a design
failure to be fixed with directed tie cases, not shipped.
Determinism: regenerate twice, byte-compare committed files;
no wall-time fields (existing headers checked).

### 4. Trig/sqrt relabel + theorem second-read (stop cond. 2)

Second-read, my own derivation (full text in the parcel
report; summary here so the code follows the proof):
- sinPi/cosPi: a ta-vs-te difference needs the exact result
  to be an exact rounding tie: a midpoint between adjacent
  destination values (or, for the unbounded-exponent tininess
  judge, a midpoint on that grid). A midpoint is a dyadic
  rational with p+1 significand bits, hence rational. For
  dyadic (rational) x, Niven's theorem: if x/pi... precisely,
  if r is rational and sin(r*pi) is rational then
  sin(r*pi) in {0,+-1/2,+-1} (same for cos by shift). Binary
  x is dyadic-rational, so sinPi(x)/cosPi(x) is either
  irrational (no tie, ta==te because both are round-to-
  nearest with the tie rule unreachable, flags equal incl.
  the tininess judge whose midpoints are the same dyadic
  set) or in {0,+-1/2,+-1}. None of those is a p+1-bit odd-
  LSB midpoint at any binade (they are 1-bit significands,
  exactly representable, delivered exactly incl. settled
  specials/zero signs, mode-independent). Hence ta==te in
  bits and flags for all 6 rows. Failure of this second
  read is stop condition 2 (real MPFR-RNA battery, reprice);
  it does not fail.
- sqrt: a tie needs sqrt(x) exactly a p+1-bit odd-LSB
  midpoint m; then x = m^2 has an odd-LSB significand of
  >= 2p+1 bits (odd * odd, no trailing zeros gained), but a
  binary operand has at most p significand bits. Contradiction;
  including the subnormal grid (same bit-count argument with
  the destination quantum) and cross-format sqrt (operand
  bits <= max source p... care: destination p can exceed
  source p in widening sqrt; then sqrt is either exact or
  requires > p_dest bits by the same squaring count applied
  at the destination grid: a midpoint on the destination
  grid squares to a value needing >= 2*p_dest+1 - (p_dest -
  p_src)... stated carefully in the report: m = odd *
  2^(e-(p_dest)) in lowest terms has odd numerator with
  p_dest+1 bits; m^2 has odd numerator with 2*p_dest+1 or
  2*p_dest+2 bits in lowest terms, while x in lowest terms
  has odd numerator <= p_src <= ... x's significand bit
  count is <= p_src + (exponent slack 0) < 2*p_dest+1
  whenever p_src < 2*p_dest+1, always true here). So sqrt
  ta==te by proof; Berkeley sqrt ta corroborates by
  execution. NOTE: committed sqrt ta lines from the exact
  generators are independently DECIDED by the ta-armed
  references (stronger than relabel) and counted as decided,
  never as relabeled; separately, as a gate, the te sqrt
  lines are replayed relabeled `ta` in scratch. Trig ta
  lines ARE relabeled and counted as such.
Trig generator change: per job, after the four decided
lines, emit `{op} ta {x} -> {te bits} {te flags}
mpfr640-trig:{fam}-ta-relabel` (provenance states the
relabel on the line; header comment states the theorem
basis). Never present these as independently decided.

### 5. Gates (script files in scratch/parcel-w5attr, Git Bash)

All runs from script files, `MSF_PYTHON` pinned to workspace
`.venv/Scripts/python.exe`, `TMPDIR/TMP/TEMP` inside
`scratch/parcel-w5attr/tmp`, logs read not exit codes.
(a) Unit spot checks of the two string cases (study probes:
`msf64_to_decimal(2.5,prec=1,rm=4)` -> `3e+00`;
`msf32_to_hex(1+2^-9,prec=2,rm=4)` -> `0x1.01p+0`) plus
below-half non-increment discriminators and both signs.
(b) Berkeley `-rnear_maxMag` level-1 replay for EVERY
covered function (all ingest-mappable attr functions across
f16/f32/f64: add/sub/mul/div/sqrt/mulAdd, format and
int-to-float conversions; named int/roundToInt forms are
already-public surface, replayed as cross-check where cheap).
Enumerate the function list in the script from
`berkeley_ingest.py`'s mapping; ingest + runner verify;
report per-function counts. Level-1 per brief (study stop
condition 3 reserves level-2 mulAdd volume to a lead ruling;
not needed if level-1 + directed exact closes).
(c) Binary16 five-mode exhaustive streams: per study Sec.
2.5 / Clause-9 survey shape - the f16 generator's exhaustive
unary sweep at five modes (65536 encodings x attribute
unary ops x 5 modes) plus `gen_vectors.py` f16-exhaustive
(standard budget leg), generated to scratch/build and
verified; counts reported. (f16 `exhaustive` uses RMS4, so
the five-mode widening flows automatically - verified by
counting ta lines in its output before trusting it.)
(d) `tools/run.sh smoke` then `standard`, PASS, with the new
te/ta control refused.
(e) Negative controls watched to fail (scratch, named in
brief): (i) ta routed to toward-zero in ONE string case -
scratch build with the `dec_round_inc` ta arm reverted only
(sed on a copied tree/build-dir source, never in the
worktree), replay committed str vectors, must FAIL on ta
digit-tie lines; (ii) te/ta wrong-mode control (as in 2);
(iii) one flipped relabeled trig expectation, must FAIL.
(f) Determinism: two full regenerations of every touched
committed vector/header file, `cmp` byte-identical.
Relabeled-vs-decided split reported as counts: decided =
exact-py generator ta lines + Berkeley ta replay lines;
relabeled = trig ta lines (+ sqrt scratch relabel replay
lines, listed separately from committed decided sqrt).

### 6. Owned files / escalations

Touch only: `src/msf_string.c`, `tools/gen_tables.py`,
generated `include/muse_softfloat.h` + `docs/COVERAGE.tsv`
(+ drift-checked generated siblings if the generator emits
them identically), `tests/gen_vectors*.py` (f16/f32/f64/xf/
str/trig), `tests/VECTORS.md`, `tests/vectors/*.vec` (attr
sets regenerated), `tools/run.sh` (control only),
`docs/metrics/briefs.jsonl` (my row). Escalate, not touch:
anything else; lead must restate at merge: README / RECORD /
BOARD "four attributes" claim sentences (listed in report).
Commit on `wave5-attr` with detailed body ending
`Co-Authored-By: Muse Code (muse-wonder-full-1.0)
<noreply@meta.ai>`. Report:
`scratch/parcel-w5attr/report.md` + results entry below.

## 2026-10-28 06:00:46 -07:00 - Results entry: fifth attribute landed, merge-ready on wave5-attr (full detail in scratch/parcel-w5attr/report.md, first line READY)

Kernel: exactly the study's two cases in src/msf_string.c
(dec_round_inc and the to_hex_generic precision switch gain
MSF_IROUND_TIES_TO_AWAY arms). A full src/ mode-switch audit
found no third out-of-pack rounding site - study stop
condition (1) did not trigger. Seam: gen_tables prelude
gains MSF_ROUND_TIES_TO_AWAY = 4; include/muse_softfloat.h
regenerated (enum block only); COVERAGE.tsv, msf_formats.h,
msf_dispatch.h regenerate byte-identical (0 new rows,
783+39). tests/VECTORS.md token note + relabel provenance
row; tools/run.sh gains control wrong-rounding-mode-te-ta
(watched refused in smoke); briefs.jsonl row appended.
Generators five-mode with the study's ta-arm reference
fixes (xf 2 arms, str arms - see correction 1 below, f64
pool modulo %len(RMS)), plus searched tie-rich directed
sections in every arith/fma/conv/str generator (kept only
where the exact reference's te != ta, decided in all five
modes). Committed: 171,423 counted lines, ta = 21,858
(directed-mode volume; tz 21,883), 2,143 ta-vs-te tie
witnesses, and a cross-check shows all 255 rounding=attr
COVERAGE rows carry a committed ta line (0 missing, 0
extra). Trig ta = 10,873 relabeled lines (tagged
mpfr640-trig:<fam>-ta-relabel, never counted as decided);
decided committed ta = 10,985. Raw MPFR RNDNA unused; no
MPFR ta narrowing was needed at all.

Second reads (report has the full theorem notes):
(1) Niven holds for sinPi/cosPi incl. the tininess judge
and settled specials - stop condition (2) not engaged;
trig relabel gate incl. a binary16-exhaustive relabeled
stream (131,072 cases) PASS.
(2) CORRECTION to the study: its sqrt ta==te claim is
over-broad - the midpoint-square proof covers homogeneous
and widening sqrt only; narrowing cross-format sqrt can
tie exactly (x = (1+2^-11)^2 in binary32 is an exact
binary16 midpoint under sqrt). No committed line relied
on the broad claim (all sqrt ta decided by exact refs);
directed narrowing tie vectors added (33 witnesses), and
the scratch relabel gate confirms the scope: theorem-scope
replay 272/272 PASS, full-file relabel fails on exactly
the 33 narrowing ties.
(3) CORRECTION to the study: gen_vectors_str.py has FOUR
ta-less reference arms, not three (to_hex_ref ~line 514
was missed). Generator-side only; all fixed.

Gates, all from script files in scratch/parcel-w5attr
(Git Bash, MSF_PYTHON pinned, TMP in scratch): smoke PASS
(171,423 cases; every control refused) and standard PASS
(+917,504 f16-exhaustive + 200,000 pack sweep); Berkeley
-rnear_maxMag level-1 for all 51 covered functions =
18,978,288 cases PASS flags-exact; binary16 five-mode
exhaustive 6,947,324 PASS (sqrt stream 327,680 = 65536x5)
+ xf exhaustive-f16 655,360 PASS + trig relabel 131,072
PASS + str bulk 80,000 PASS; string unit probe 13/13;
determinism byte-identical across two regenerations and
the committed tree. Negative controls watched failing:
(a) dec_round_inc ta-arm-deleted mutant FAILs with 1,044
ta lines wrong (to_hex mutant: 166), each PASSing the
unrelated files; (b) te/ta swap FAIL (106 lines) here and
in smoke; (c) one flipped relabeled trig expectation FAIL
(1 line). Not done / lead's at merge: README/RECORD/BOARD
"four attributes" wording restatement, board sampled
replay (lead post-merge per brief), Berkeley level-2 (not
in brief), verifier parcel (separate). traps-xf carries
only 5 ta lines by its quota search - decided, thin, noted
in the report. Commit on wave5-attr follows this entry;
never pushed or merged.
