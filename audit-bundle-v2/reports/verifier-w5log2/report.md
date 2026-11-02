NOT READY

# verifier-w5log2 report (SF-2 Step 3b, copy worktrees/verify5-log2)

Verdict: NOT READY. Four load-bearing findings; the first alone is
dispositive. All probes were run from script files in
scratch/verifier-w5log2 (Git Bash, MSF_PYTHON pinned to the workspace
.venv, ulimit -v 4194304, at most 4 parallel workers). The copy was
never modified (git status clean at start and end; all builds and
probes land outside it). No cft-named material was opened, searched,
or listed. No foreign oracle was executed: the only oracle is the
verifier's own adaptive-precision MPFR decider plus the copy's own
committed harness as a second route.

## F1 (result/flag defect): wrong recentre branch in log_core

`src/msf_math.c` `log_big_sq_ge_pow2` (line 1407) returns
`big_top_bit(sq, 2*nu) >= bit2` while its own comment (lines
1403-1406) states the correct rule `bitlen(a^2) > bit2`. The `>=`
takes the recentre branch for every significand with mm in
[1, sqrt2) and for every exact power of two. Consequences observed:

- `log2(1.0)` is not `+0`: f64 returns `34d1f49d2ff62bf3/10`,
  f32 returns `05010a99/10`, f16 returns `0000/18`
  (scratch/verifier-w5log2/logs, cells2 + ownharness2 runs).
- Every exact power returns an inexact residue with directed-mode
  splits, e.g. f64 `log2(2.0)` te `3ff0000000000000/10` vs exact
  `.../00`; f16 `log2(0x0001)` `ce00/10` vs `ce00/00`.
- The copy's OWN harness agrees with the verifier decider and
  disagrees with the kernel on these cells (BAD in both drivers).
- f16 exhaustive (own decider): checked=655360 mismatches=310
  undecided=0 final_undecided=0 -> FAIL (logs/f16.log).
- f16 exhaustive (copy's own harness): checked=1310720 mismatches=310
  undecided=0 final_undecided=0 -> FAIL (logs/ownf16.log). The two
  independent deciders agree on the count exactly.
- Committed-vector runner: total 90315 passed 87884 failed 2431
  VERDICT: FAIL; failures = 2391 `powers` + 40 `tiny` families, all
  other 11 families pass (logs/runnerexplog.log).

## F2 (artefact): committed EK_LOG[2] != generator proof

`tools/gen_explog_tables.py` re-run twice byte-identical; it proves
`EK_LOG = {146, 242, 370}` (log line in logs/genexpA.log). The
committed `src/msf_explog_tables.h` line 22 carries
`{146, 242, 300}`: the full-file diff is exactly that one integer.
The parcel ledger claims EK_LOG `{146, 242, 370}` as proven AND
committed, and docs/WIDTHS.md row 31 claims `2^-370`; the committed
header's 300 matches neither. ln2 bracket diff `~2^-702.3` and term
counts `{35,54,79}/{23,35,51}` reproduce as claimed.

## F3 (seam): committed tables fail the committed generator

`tables/implemented.tsv` line 848 claims `msf64_log2p1` wave 4 while
`tables/operations.tsv` (and its 5 siblings) claim wave 5.
`tools/gen_tables.py` line 290 asserts equality and aborts:
`AssertionError: implemented.tsv wave drift: msf64_log2p1`
(logs/gentab1.log). So the committed generated files
(include/muse_softfloat.h, src/msf_formats.h, tests/msf_dispatch.h,
docs/COVERAGE.tsv) cannot re-derive; `tools/run.sh` smoke drift
check would fail at this gate. Tier-2 inventory itself re-derives
fine from committed COVERAGE.tsv: tier2 total=57 implemented=57
planned=0.

## F4 (artefact + committed vector): vector generator broken, one wrong flag

`tests/gen_vectors_explog.py` line 58 defines `UNDERFLOW = 0x04`
(parent 54ac1bb line 53: `0x08`; Step-3b diff `-0x08/+0x04`). The
settled-table cross-check therefore disagrees with the C decider on
the first underflow cell (`TABLE DISAGREE msf16_exp2 ce40: settled
...20 decider ...24`, i.e. 0x14 vs 0x18) and the generator exits 1
with no output: vector regen is impossible on the committed tree.
With a scratch-only copy restoring 0x08, generation completes (rc 0),
the settled tables agree with the C decider everywhere, f16/f32
regenerate byte-identical to committed, and Step-3a exp lines are
byte-prefixes of the committed files (14848/15353/15418 lines).
The f64 regen differs in exactly one line: committed
`tests/vectors/explog-f64.vec:25369`
`msf64_log2p1 te bff0000000000000 -> fff0000000000000 00`
should carry `02` like its tz/tp/tn/ta siblings (pole flag is
mode-independent); the kernel delivers /02 and the runner flags the
committed te line as FAIL.

## Probe ledger (all run by the verifier)

P1 one-cell/family probes (probes.sh/runprobes.sh, 379 cells across
all 6 ops x 5 modes: powers incl. subnormal x, sqrt2-recentre
neighbourhood, pole -1 +-ulp, tiny-|x| ladder across 2^-8, specials,
negatives, NaN/inf, hardest patterns 0x7fe61555f75885b4 /
0x44ee499f19ecc9fb, sticky-attractor x=2^k ladder): 261 pass, 118
cell-records fail, every failure a power / mm<sqrt2 / tiny-residue
cell (F1). Poles, domain, specials, sqrt2-upper-side pass.
P2 binary16 exhaustive: see F1 (both deciders, 310 each).
P3 binary32 shards: 256 shards of 2^24 over [0,2^32) re-derived
from the copy's `f32 LO HI [FN]` harness contract
(tests/explog_exhaustive.c:285-306; 256*2^24 = 2^32). Sampled
shards 0,1,128,255 x log pair run here (own decider, 5 modes;
checked = 2^24*5 = 83886080 per shard-fn; full re-exhaustion NOT
re-executed - stated plainly):
shard 0 [0x0,0x1000000) log2: 120 mismatches (24 subnormal powers
x 5), undecided 0, audits 167/0, final_undecided 0 -> FAIL;
log2p1: 0 mismatches -> PASS.
shard 1 [0x1000000,0x2000000) log2: 10 mismatches (2^-125,
2^-124 x 5), rest 0 -> FAIL; log2p1: 0 -> PASS.
shard 128 [0x80000000,0x81000000): both 0 -> PASS (log2 all
domain-table; 167 stride audits pass on log2p1).
shard 255 [0xFF000000,0x100000000): both 0 -> PASS (all
non-finite table path, stage hits 0/0/0).
Sampled total 671088640 mode-checks; final_undecided 0 in all 8.
Seeded legs (own decider): f64 log2/log2p1 and f32 log2/log2p1,
20000 patterns each (100000 mode-checks per leg), all PASS,
undecided 0, final_undecided 0 (logs/seed1-4.log).
Full committed surface via the copy's runner: total 272833
passed 270402 failed 2431 malformed 0 VERDICT: FAIL, with zero
FAILs outside explog-*.vec (logs/fullsurf.log).
P4 regen stops: gen_tables FAILS (F3); gen_explog_tables twice
identical but != committed (F2); vector generator refuses (F4).
P5 seam: Tier 2 57/57/0 confirmed from generated COVERAGE.tsv;
header declares all 6 fns (lines 1787-1797); dispatch carries all 6
(12 rows); VECTORS.md/WIDTHS.md/briefs.jsonl rows present.
P6 full runner over committed vectors: FAIL 2431 (F1).
P7 target ARM: arm-none-eabi-gcc 14.2.1 -Os AND -O3 both -Werror
clean (msf_math.o 27848 / 103552 B); symbol scan clean (integer
__aeabi + memcpy only, no soft-float helpers).
P8 negatives: NC-1ULP (log hardest line low-bit flip, input
0x7fe61555f75885b2 family) -> runner rc=1 VERDICT: FAIL (bites);
NC-POLEFLAG (scratch mutant stripping the 2 pole flag sites) -> all
5 pole cells x 5 modes flag-mismatch (bites).
final_undecided = 0 and decider-undecided = 0 in every leg run here.

## Not done

- Full binary32 re-exhaustion (256 shards) not re-executed; 4
  sampled shards only (shard logs below), per brief allowance.
- tools/run.sh smoke/standard NOT executed in-copy (would write
  build/ into the copy); every gate it owns was executed outside
  the copy instead (host build, regen, runner, controls, ARM).
- No binary64 worst-case corpus leg (no .wc corpus reachable under
  the allowed paths; hardest patterns covered as one-cells).
