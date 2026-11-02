# Verifier report: parcel-w6judgemap (judge's map)

Copy: `worktrees/verify6-judgemap` at `ee0c8b9` (parent `af36464`,
confirmed by log), duplicated `.git`-free to
`scratch/verifier-w6judgemap/dup`. All runs in the duplicate under
Git Bash with `MSF_PYTHON` = workspace `.venv` python. Fences kept:
no parcel branch/worktree, no `muse-softfloat/`, no `scratch/lead/`,
no `ledger/lead.md`, no history; `plants.jsonl` totals-only;
nothing with `cft`; no board flashed.

## VERDICT: NOT READY as written

The map does not survive use exactly as written. Four factual
errors in `README.md` plus one wrong nibble in the committed
`demo/expected-interval.txt`. Everything else probed verified.

## Findings (map claims vs re-derivation)

1. Step 1 mislabels the film. `video/out/assembly_v5.mp4` box
   probe: 169.000 s, 2560x1440, one `vide` trak, no audio
   (silent claim holds). Map step 1 says "runs 180 seconds at
   1920x1080" — those are `video/out/final.mp4`'s numbers
   (180.000 s, 1920x1080, probed). The intro (169-second) and
   Demo-video section (169 s, 2560x1440) are correct.
2. Step 5 plant score is false. Mechanical recount of
   `docs/metrics/plants.jsonl`: 145 rows, 138 `caught`.
   Map step 5 claims "145 caught of 145". Status ("138 of
   145") and the parcel's own `briefs.jsonl` row ("plants
   138/145") are correct. "Latest round 20 of 20" cannot be
   checked under the totals-only fence (unresolved).
3. Step 4 interval hash is stale. Map quotes
   `ce81d66e…a9aec`; the runner prints
   `ae04caf0…66c1422` (my run, `SUMMARY rows=710 ...
   total_ops=396745`), matching Status, `docs/BOARD.md`,
   `docs/RECORD.md`, and the lead commit message. `ce81…`
   matches nothing current.
4. Step 4 "All three legs passed" is false on this
   machine: `demo/run_demo.sh host` gives IAS15 PASS
   (2001/2001 native+soft), KissFFT PASS (12/12), interval
   FAIL.
5. Committed `demo/expected-interval.txt` line 11 ends
   `...66c1423`; the program reproduces `...66c1422`
   (BOARD/RECORD/commit message agree on `...422`). The
   lead restamp mistyped the last nibble, so the interval
   leg cannot pass at this commit.

## Verified numbers (each re-derived)

- COVERAGE: 849 rows, 849 implemented; tier1 783, tier2 66.
- `site/ops.json`: 849 ops, 822 runnable, 273 `rm`
  (attribute-carrying). Live site HTTP 200 with "Deal me a
  committed vector", "Run", "The instrument"; exclusions
  named with reasons (augmented pairs: head+tail).
- smoke: `budget smoke: PASS`, 411213/411213, controls
  refused (18 s here vs 27 s record — a record, no conflict).
- standard: PASS, 411213 + 1117504 extras +
  5505024 aug-pool differential, 0 FAIL.
- sanitize trap: PASS (50 s); canaries trap first
  (documented `heap_far` trap boundary reproduced).
- Interval: rows=710, total_ops=396745; RECORD carries
  616,754 → 396,745, stage 3 283,314 → 63,305; SF-2 study
  model 394,666; 396745-394666 = 2079 = 3x693 sphere rows.
- KissFFT expectation: 12 rows, 256/1024/4096 x
  complex/real x fwd/inv; IAS15+KissFFT legs diff the
  committed expectation files (both PASS).
- Audit manifest: 576 entries, 576/576 hashes OK
  (CR-tolerant; file is CRLF so literal `sha256sum -c`
  fails under Git Bash — document-only, contents fine).
- Metrics: 93 usage / 94 pass / 20 escalations rows. CI:
  four jobs smoke/standard/example-host/sanitize.
- RECORD-quoted, spot-confirmed present: 968/968 harness
  vectors, six-board sweep (genuine + five clones),
  114/120 with `bc807e6` pin in frozen bundle, exhaustive
  42,949,672,960 + 12,884,901,888 with shard detail,
  120 BPM grid in video pipeline, Pico example RECORD entry.
- Links: 26 occurrences / 17 unique relative targets in
  README, all resolve on disk.
- Discipline: KissFFT Fork B change named; "unmodified
  KissFFT" explicitly disclaimed; README "unmodified"
  hits refer to the REBOUND desktop build (shim-based,
  integrator unpatched); timings framed as records;
  augmented text matches code + RECORD.

## Boundaries and notes

- `run_demo.sh board` (the literal step-4 command) was
  not executed: no Pico attached and no-flash fence. The
  step names no board prerequisite ("needs network once"
  only), so a boardless judge cannot perform it as
  written. Host run covers the same three proofs.
- Site click-through not browser-exercised (no browser
  here): HTTP 200 + button names + `site/replay-log.txt`
  (`replayed=1620 mismatches=0`) only.
- First demo attempt failed at REBOUND extraction under
  Git Bash `python3` 3.10.12, whose backported tarfile
  `data` filter wrongly refuses the benign in-root
  `docs/changelog.md -> ../changelog.md` symlink.
  Re-ran with pinned MSF_PYTHON (3.13) per brief:
  extraction OK. Environmental, not a map defect.
- Diff vs parent `af36464`: `README.md` (134+/11-),
  `demo/expected-interval.txt` (9+/6-),
  `docs/metrics/briefs.jsonl` (+1 parcel row). The
  interval file is outside the parcel's stated owned list
  (lead fix, still wrong per finding 5).

## Logs

`scratch/verifier-w6judgemap/`: `build_host.log`,
`smoke.log`, `standard.log`, `demo_host.log` (unpinned
python, extraction refusal), `demo_host2.log`
(MSF_PYTHON: IAS15 PASS, KissFFT PASS, interval FAIL),
`sanitize.log`; scripts `mp4probe.py`, `links.py`,
`plantcount.py`, `covercount.py`, `opscount.py`,
`mancheck.py`, `tarlist.py`, `jsonpeek.py`.
