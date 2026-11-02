NOT READY

verifier-w5exp2, second attempt. Planted copy `worktrees/verify5-exp2`
(HEAD 9fffbb1, parent a0acf2a, worktree clean at end of run).
Every check below was executed by this attempt (rebuilt driver from the
current `mydecider.c` + unmodified copy sources; copy never modified).
Stance: disconfirm only. Correct rounding or it does not ship.

FINDINGS (each blocks shipment; smallest repro first)

F1 — WRONG ANSWER (b): exp2 exact tie at E_tie = emin-p delivers +0
instead of u in roundTiesToAway, all three formats.
IEEE 754-2019 4.3.3 ties-to-away on the exact value 2^E_tie = u/2
(equidistant from +0 and +u) requires the larger magnitude u, with
inexact (+underflow). The kernel delivers (0, UNDERFLOW|INEXACT).
- f64: `vdriver.exe one 2 0 c090cc0000000000` (x = -1075.0):
  `ta got=0000000000000000/18 want=0000000000000001/18 BAD`
- f32: `vdriver.exe one 1 0 c3160000` (x = -150.0): same ta BAD.
- f16: `vdriver.exe one 0 0 ce40` (x = -25.0): same ta BAD.
Root cause in the copy (`worktrees/verify5-exp2/src/msf_math.c:1062-1068`):
the exp2 zero cut reads `if (explog_cmp_int(&d, e_tie) <= 0)` and packs
the proxy 2^(E_tie-1). The parcel design (ledger/parcel-w5exp2.md Sec. 4)
requires `x < E_tie` cut with `x == E_tie` falling through to the integer
exact branch; `<=` swallows the tie. The proxy u/4 is a non-tie, so only
ta differs (te/tz/tn/tp coincide by masking); flags 0x18 are accidentally
right, bits wrong. The copy's own decider, the copy's own committed vecs
(1/18 ta lines), and my independent MPFR decider all agree against the
kernel. The sibling saturation cut (`< -(p+1)`, msf_math.c:1075) is strict
and its ta ties pass — only the exp2 zero cut is off by one.

F2 — REGEN STOP: committed `src/msf_explog_tables.h:20` carries
`MSF_EXPLOG_EK_EXP[3] = { 147, 243, 200 }`; the copy's own generator
re-run in scratch proves `{ 147, 243, 371 }` (exact Fraction arithmetic,
9-bit reserve, deterministic across two regens). Byte-compare differs on
that one line only (ln2 + 67 entries + NTERMS identical). The stage-3
agreement bound in the shipped header (2^-200) is weaker than the proven
bound (2^-371); no leg below hit stage 3, so no manifested mis-decision,
but the proof artifact does not match its proof. Brief probe 2 STOP.

F3 — SEAM DRIFT (regen STOP + flags-column violation): committed
`tables/operations.tsv:141` gives exp2m1 flags=`no`, while the committed
generated `include/muse_softfloat.h:1781-1785`,
`tests/msf_dispatch.h:893-895,1729-1731`, `docs/COVERAGE.tsv:839-841`
all give exp2m1 flags=`yes` (matching kernel, vecs, brief "flags column
true"). Regenerating `tools/gen_tables.py` from the committed tables
reproduces the `no` shape (3 files drift, `src/msf_formats.h` identical).
Committed inputs and committed outputs disagree; regeneration not
byte-stable. Brief probe 4 STOP.

F4 — WRONG COMMITTED VECTOR: `tests/vectors/explog-f64.vec:4`
`msf64_exp2 te 0 -> 3ff0000000000000 10` claims INEXACT on the exact
result +1. Correct is (1, 0): IEEE (no exception), parcel Sec. 2 table,
the copy's own decider (`decide` on `msf64_exp2 0` gives flags 0 all
modes), and the f32/f16 committed vecs (`te 0 -> ... 00`). The copy's
own runner refuses it (`got .../00 want .../10`, my smoke run).

F5 — BROKEN VECTOR GENERATOR: `tests/gen_vectors_explog.py:54`
`INEXACT = 0x08` (duplicates UNDERFLOW; correct is 0x10 per
`include/muse_softfloat.h:70-74`). Regeneration refuses immediately:
`TABLE DISAGREE msf16_exp2 4c00: settled [..., 12)...] decider [...,
20)...]` (bits agree, flags 0x0C vs correct 0x14), exit 1, no files
written. Committed vectors (0x10/0x14-style flags throughout) are
irreproducible from the committed generator.

Consequence for gates: the copy's own runner over its own committed
explog vecs gives 45,606/45,610 (the 3 F1 lines + F4 line); full surface
228,124/228,128 (same 4). smoke/standard cannot pass (drift gate fails
first, vector gate fails second).

PER-PROBE EVIDENCE (all re-run by this attempt)

P1 correctness, independently decided (my MPFR Ziv decider, W=256..4096
ladders, two-precision certification, specials/integer path exact;
escalation counting; memory ceiling `ulimit -v 4194304`; sequential).
- f16 exhaustive: 131,072 inputs x2 fns x5 modes = 655,360 checks,
  1 mismatch (F1 f16 cell), 0 undecided, final_undecided=0, stage hits
  389410/0/0, wall 5 s. Log: scratch/verifier-w5exp2/50_f16.log.
- f32 sampled shards (both fns, per-fn 2,097,152 patterns = 2^21 =
  1/2048 of 2^32, plus 2x200k seeds/fn): S1 subnormal, S2 one, S3 tie25,
  S4 overflow, S5 etie, S6 sat25, S7 8x32k windows; all PASS except S5
  single F1 cell (in=c3160000 ta). Seeded f32: 796,878 finite inputs,
  3,983,910 checks, 0/0/0. Seeded f64: 799,575 finite, 3,997,875 checks,
  0/0/0. Final_undecided=0 everywhere; stage-2/3 hits 0 everywhere.
  Log: scratch/verifier-w5exp2/70_f32shards.log (wall 382 s).
- f64 worst-case, 100% of published inputs, both functions, re-decided
  from the pinned Step 0b tree (hashes 51f847cf.../70516fe2..., match
  the parcel ledger record): exp2 77,121 unique (census 77,120 + -0),
  385,605 checks, 1 mismatch (F1 f64 cell), 0 undecided;
  exp2m1 240,825 unique (240,824 + -0), 1,204,125 checks, 0 mismatch.
  inexact_tokens=0, nonfinite=4, unparsed=2 per file. All kernel
  decisions at stage 1 or exact/cut paths (373845/0/0, 1198925/0/0).
  Logs: 60_wc_hashes.log, 60_wc_exp2.log, 60_wc_exp2m1.log (wall 47 s).
- Parcel shard arithmetic re-added from ledger/parcel-w5exp2.md (parcel
  scratch not consulted): 256 shards; 2^32 patterns x2 fns x5 modes =
  42,949,672,960 total mode-checks (matches); finite 4,278,190,080 =
  2^32 - 2^24 per fn (nonfinite 2^24 = all-ones-exponent class);
  finite checks 42,781,900,800 + specials-class 167,772,160 close the
  total exactly. Stage hits 22,386,767,760 (~52%; remainder exact/cut/
  specials paths) plausible, not independently verifiable from here.
- Hand selftest (25_selftest.py, 35 cells incl. all tie/saturation/
  overflow/zero-cut cells): decider 35/35 vs hand; kernel 32/35 (only
  the 3 F1 ta cells miss). Log: 45_selftest.log.
- Vec cross-check (my decider vs committed vecs): f16 14,845 0 diffs;
  f32 15,350 0 diffs; f64 15,415 1 diff (F4 line). Logs: 45_explog-*.log.
- Cuts/ties/specials battery (80_cuts.py, boundary-1/0/+1 and -3/+3 per
  cut per format, saturation deep, zero/overflow deep, full specials
  sweep flags-exact): 198 kernel-vs-decider invocations (990
  mode-checks), 3 BAD (the F1 cells), 0 undecided. (Exit 1 = the 3.)

P2 Ek re-derivation: generator re-run in scratch/verifier-w5exp2/ekregen
prints `stage terms [35,49,66]; Ek 147,243,371`, ln2 bracket
|dps260-dps210| ~ 2^-702.3; regen1 == regen2 (deterministic);
byte-compare vs committed fails only at the EK line (F2).
Spike margins restated (scratch/sf2-explog/report.md Secs. 2.1, 6.1):
exp2 plain RN 60.54 / DIR 60.43 @0x3f5e4596526bf94d; exp2m1 plain RN
59.10 / DIR 56.74 @0xbf73918e8608bd5b, attractor in-class RN <=59.92
(M1SAT strip 48.86); exact ties exp2(-1075)=u/2, exp2m1(54),
exp2m1(-54) (Sec. 2.3); stage reach ~2^-150/2^-246/~2^-318, i.e. stage 1
decides observed plain (needs 2^-114, ~36 bits spare), stage 3 ~5.3x the
exp2 maximum (4.6x programme max log10 69.77). Observed: every wc/seed/
shard decision at stage 1 or exact/cut path; R4 tripwire intact (0 final
undecided) but stage-3 bound unproven as shipped (F2). No foreign oracle
executed anywhere (F1 fence holds trivially). Log: 90_ekregen.sh output
+ ekregen/msf_explog_tables.h.

P3 cuts/ties/specials detail: every exact exponent cut probed at
boundary-3/-1/0/+1/+3 ulp per format per brief (exp2 ov T=emax+1, zero
T=E_tie; exp2m1 ov T=emax+2, sat T=-(p+1)), plus zero-cut-deep
(E_tie-50), sat-deep, ov-deep both functions, full specials sweep
(+0/-0/+inf/-inf/sNaN/qNaN payloads, sign-exact, flags-exact) — all PASS
except the exact-T E_tie ta cell (F1). exp2m1(+-(p+1)) ties, -1075 tie,
saturation cell (inc. tp->u / ta->-1 directions) all PASS. The -1075
tie in te/tz/tn/tp passes; only ta is wrong (proxy-masking, F1 root
cause). 80_cuts.py run by this attempt (no 80 log existed).

P4 seam/smoke/standard/target (mirrored outside the copy; copy clean):
- Census (re-run 100_seam.sh): tier2 57 registered / 51 implemented /
  6 planned, claim column clean (bad=[]), tier1 783/783 intact, VECS
  present, TIER2_TOTAL_EXPECTED=57. Claim surface a0acf2a..HEAD purely
  additive (47,875+/5-; the 5 deletions are dispatch line updates).
- Regen byte-stable: NO (F2 explog header; F3 gen_tables 3-file drift;
  F5 vector generator refuses). src/msf_formats.h identical.
- smoke: FAIL. drift gate fails (F3); runner unit PASS; vector verify
  over full VECS (my runner build, manifest+expect-counts clean):
  228,128 vectors, 228,124 pass, 4 FAIL (F1 x3 + F4 x1; log
  smoke/verify-explog.log, smoke/verify.log). type scan clean; symbol
  scan clean (26 undefined, all intra-library/allowed aeabi-ll/memcpy).
  run.sh itself not executed (would write build/ into the copy and use
  the broken mingw64 toolchain here; recipe mirrored with WSL gcc
  11.4.0 x86-64 + ARM 14.2.1). run.sh controls battery (NC0) not
  re-run: gate already fails at drift; inventory arithmetic re-checked
  directly above.
- standard extras (tier1 f16-exhaustive 917,504 + pack-sweep 200,000,
  generated with workspace .venv python): 1,117,504/1,117,504 PASS.
  Log: smoke/verify-standard.log.
- target: arm-none-eabi-gcc 14.2.1, -mcpu=cortex-m0plus -mthumb
  -ffreestanding, -Wall -Wextra -Werror: -Os AND -O3 both clean (all 9
  TUs); msf_math.o 17,304 B (-Os) / 65,972 B (-O3). Host -O2/-O3 clean.
  Logs: smoke/target-Os.log, smoke/target-O3.log.
  (Parcel-recorded 13,908/60,724 B differ — different toolchain; sizes
  are records only.)

NOT DONE (named, not silent)
- Parcel negative controls NC1-NC5 (Ek-narrow replay, table digit flip,
  cut off-by-one, flag strip, 1-ulp hardest): not re-run; verdict does
  not depend on them. Note the Ek-narrow control shape is moot while
  the header itself carries an unproven bound (F2).
- Board replay: no board caller for this family; genuine board busy,
  board.lock not mine. Not run.
- f32 full exhaustion: sampled falsification only, per brief (sample
  fraction honestly ~0.058% per fn + targeted worst-case/special cells);
  completeness rests on the parcel's 256-shard claim, whose arithmetic
  re-adds exactly (above) but was not re-executed.
- Independent hand re-proof of the Ek recurrence: relied on the
  generator's exact-Fraction assertions + deterministic double regen.
- run.sh controls battery + run.sh native execution: see P4 (copy
  cleanliness + broken mingw64 toolchain on this host).

LEFTOVER ARTIFACTS (first attempt): re-ran, not trusted.
Rebuilt vdriver from current mydecider.c + unmodified copy sources and
re-executed every leg: 45_rebuild_xcheck (selftest+vec xcheck),
50_f16, 60_wc (+hashes), 70_f32shards, 80_cuts (never previously run),
90_ekregen (+gen drift), 100_seam. Prior logs (50/60/70/45/46/41/92/93/
etc.) treated as pointers only — all superseded, most were built from a
stale (pre-fix) decider; the stale VEC-UNDECIDED counts (285/1135/1270)
do not reproduce with the current decider (0 undecided everywhere).
New scripts this attempt: my_smoke.sh, my_verify_explog.sh,
my_verify_full.sh, my_target.sh, my_symbols.sh, my_standard.sh.
Toolchain notes: WSL gcc 11.4.0 + MPFR 4.1.0 for vdriver/runner (copy
decider harness built with MSYS2 mingw32 gcc 16.1.0 + MPFR 4.2.2 for
mpfr_exp2m1; mingw64 gcc broken on this host — silent exit 1).
MSF_PYTHON pin: workspace .venv (3.12.15, mpmath 1.4.1) for generators
needing it; WSL python3 3.10 otherwise. Copy HEAD 9fffbb1, `git status`
clean after all runs. Sequential legs, ulimit -v 4194304 throughout.

