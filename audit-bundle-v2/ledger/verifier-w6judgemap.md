# Ledger: verifier-w6judgemap (ParcelRound verifier, judge's map)

Copy `worktrees/verify6-judgemap` at `ee0c8b9` (parent
`af36464`), verified `.git`-free in
`scratch/verifier-w6judgemap/dup`. Full evidence:
`scratch/verifier-w6judgemap/report.md` with logs.

## 2026-10-30 result entry

**NOT READY as written.** All five brief probes ran
(demo host run included). The map fails use-exactly-as-
written on four README facts plus one committed nibble;
everything else verified.

Map errors: (1) step 1 gives the film as 180 s 1920x1080
— those are `final.mp4`'s numbers; `assembly_v5.mp4`
probes 169.000 s 2560x1440, silent (single video trak).
(2) Step 5 claims plants "145 caught of 145"; mechanical
recount gives 145 rows, 138 caught (Status and the
parcel's own briefs row say 138/145). (3) Step 4 quotes
interval hash `ce81d66e…a9aec`; the runner prints
`ae04caf0…66c1422` (Status, BOARD, RECORD agree).
(4) "All three legs passed" is false: demo host gives
IAS15 PASS (2001/2001), KissFFT PASS (12/12), interval
FAIL. (5) `demo/expected-interval.txt` ends `...66c1423`
vs program/BOARD/RECORD/commit `...66c1422` — the lead
restamp mistyped the last nibble.

Holds: 849/849 (783 + 66), 273 attribute rows, 822/849
site ops (live 200, buttons present), smoke PASS
(411213/411213), standard PASS (plus 1117504 and
5505024, 0 FAIL), sanitize trap PASS canaries-first,
interval rows=710 total_ops=396745 with RECORD counts
reconciled (2079 = 3x693), 12 KF sizes, 576/576 manifest
hashes, 93/94/20 metrics rows, four CI jobs, 26/26 links
resolve, KissFFT Fork B named and "unmodified" properly
disclaimed, timings as records, silent film as stated.

Gaps: "latest round 20 of 20" unverifiable under the
plants totals-only fence; site clicks not
browser-exercised; board-mode step not run (no hardware,
no-flash fence — and the step names no Pico
prerequisite). Diff vs parent limited to `README.md`,
`demo/expected-interval.txt`, `docs/metrics/briefs.jsonl`
(+1 row). An early demo failure under Git Bash python3
3.10 (stale tarfile filter vs benign symlink) resolved by
the pinned MSF_PYTHON rerun — environmental.
