**Role:** parcel-w6judgemap (Wave 6 queue item 5, first parcel: judge's map)

**Base:** `af364643549b305abbaaa7fc428ae2b16b0e1afd`, branch
`wave6-judgemap`, worktree `worktrees/w6-judgemap`. Work only there.

**Job:** a judge landing on the repo should know in under a
minute what to watch, run, and audit - in that order. Add a
short "Start here" map near the top of README.md (after the
intro/live-demo lines, before Status): numbered steps with
exact links/commands - (1) the 169 s film
(video/out/assembly_v5.mp4, silent, music pending owner -
say so honestly), (2) the live WASM site + what to click,
(3) run it yourself in 5 minutes (examples/host/build.sh,
then tools/run.sh smoke; Linux CI runs the same gates -
name the four jobs), (4) reproduce the workloads
(demo/run_demo.sh), (5) audit the method (RECORD,
audit-bundle README walk order, plant score as counted from
docs/metrics/plants.jsonl at your tip - derive it, don't
copy a stale number). Every number in the map re-derived by
your own commands from the tree (instantiations, vectors,
plants, boards, hashes); every relative link must resolve;
every command must be one you ran in the worktree or that
CI runs (say which). Claim discipline as everywhere:
timings are records, KissFFT never "unmodified", no
performance claims, film is the v5 assembly not the old
180 s cut. Also sweep the rest of README for the Wave 6
state (augmented consumption, examples, sanitize budget,
CI) - the Status section was written at SF-2 close;
restate what's stale, in place, with the same discipline.

**Owned files:** README.md, docs/metrics/briefs.jsonl (own
row, wave "wave6", binary-append). Nothing else.

**Acceptance:** (a) every map command run by you in the
worktree (or named CI-only with the job that runs it);
(b) link check: every relative link in README resolves on
disk; (c) per-number table in your report (claimed vs
re-derived with the command); (d) `tools/run.sh standard`
PASS unchanged. Readability: the map itself is for a
non-specialist judge - plain language, no clause numbers
in the map steps.

**Outputs:** tip commit(s) with detailed body +
`Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>`;
`scratch/parcel-w6judgemap/report.md` +
`ledger/parcel-w6judgemap.md`. Structured
complete/evidence/unresolved mandatory. Script files, Git
Bash, MSF_PYTHON pinned. Nothing with `cft` in its name.
~240 min.
