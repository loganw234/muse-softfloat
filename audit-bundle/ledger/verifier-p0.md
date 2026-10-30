
## 2026-10-26 19:31:23 -0700 - READY on P0 23a740f (a)0 (b)0 notes 4 (lead-filed staged body; child sandbox ledger tool unrunnable)

READY on P0 (23a740f): (a) 0, (b) 0, 4 notes. Full report in scratch/verifier-p0/report.md.

Measured: re-ran tools/run.sh smoke (PASS, 17662/17662, 8/8 controls refused)
and standard (PASS, 1117504/1117504) from the clean tree; regenerated all 4
outputs byte-identical; independent recount 81/783/63/0-unconfirmed; dispatch
63 bound + in host build, 720 NULL; own pack differential 3121 cases 0
mismatches; own u128 differential 5726 cases 0 mismatches; own f16 exhaustive
1048576 + copysign 20576 + directed 283 vectors all pass; own flag differential
1297 cases 0 mismatches; oracle zips re-hashed exact; board hash 4573ac09...f28a7
identical host/board in logs; UF2/ELF prefixes match on disk; hello 12 CHECKs =
12 PASS lines; metrics-p0 sums 848844/143025602 exact; isSignaling probe re-run
65728/0; MPFR 4.2.2 live; S1 extract confirms ANY flag-test reading; tree still
clean (build/ only, ignored).
Believed: board evidence from logs/hashes only (board untouched per brief);
level-2 40284288/81-97s pricing re-runnable live, not re-run; Wave-1 parcels can
name disjoint owned files (msf32.c vs msf64.c; shared kernels lead-owned).
For: lead (P0 push gate).
