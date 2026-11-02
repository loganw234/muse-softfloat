# verifier-w5exp2 (second attempt; first verifier child died mid-verification)

## 2026-10-28 (second attempt) — verdict NOT READY (5 findings)

Copy `worktrees/verify5-exp2` @ 9fffbb1 (parent a0acf2a), clean before
and after. All legs re-executed by this attempt; first-attempt logs
treated as pointers only (most used a stale pre-fix decider).

Findings:
- F1 (b) kernel: exp2 E_tie tie in ta delivers +0 not u, all formats
  (`msf_math.c:1066` cut `<=` swallows x == E_tie; design requires `<`).
  Repro: `vdriver.exe one 2 0 c090cc0000000000` ta BAD (want 1/18).
- F2 regen STOP: `src/msf_explog_tables.h:20` Ek `{147,243,200}` vs
  generator-proven `{147,243,371}` (deterministic double regen).
- F3 seam STOP: `tables/operations.tsv:141` exp2m1 flags=`no` vs
  generated header/dispatch/COVERAGE flags=`yes`; 3-file drift.
- F4 vector: `explog-f64.vec:4` (`exp2 te 0 -> 1 10`) inexact-on-exact;
  copy's own decider/runner say (1, 0).
- F5 generator: `gen_vectors_explog.py:54` INEXACT=0x08; regen refuses
  (TABLE DISAGREE), committed vectors irreproducible.

Evidence: f16 exhaustive 655,359/655,360; f32 shards+seeds pass except
the F1 cell (~0.058% sampled + re-added parcel arithmetic closes:
2^32x2x5 = 42,949,672,960); f64 wc 100% both fns (77,121 + 240,825
unique, hashes match) except F1 cell; cuts 987/990; vec xcheck 1 diff;
runner full surface 228,124/228,128; standard extras 1,117,504 PASS;
target -Os/-O3 clean (math.o 17,304/65,972 B); 0 undecided and 0
final-undecided in every leg. Full record:
scratch/verifier-w5exp2/report.md (first line NOT READY).
For: lead
