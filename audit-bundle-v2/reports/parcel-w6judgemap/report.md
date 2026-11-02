# parcel-w6judgemap report (Wave 6 queue item 5, first parcel: judge's map)

**Verdict: READY** (with one real finding, below, that sits
outside this parcel's owned files and is named in the README
itself).

- Base `af364643549b305abbaaa7fc428ae2b16b0e1afd`, branch
  `wave6-judgemap`, worktree `worktrees/w6-judgemap`.
- Tip `245a4f5b0aa7108f99852b385b51c397d44b6ae2` (one commit,
  detailed body, Co-Authored-By trailer). Not pushed.
- Owned files only: `README.md`,
  `docs/metrics/briefs.jsonl` (own row, wave `wave6`,
  binary-append; prefix bytes verified unchanged,
  14795 -> 15696 bytes, 37 rows after).
- All runs: Git Bash (`C:\Program Files\Git\bin\bash.exe`),
  `MSF_PYTHON=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe`
  (Python 3.12.15), script files in this scratch dir, logs
  redirected to files here. Nothing with `cft` in its name
  was opened, searched, or listed. Main checkout and other
  worktrees untouched.

## What landed

1. `## Start here` map after the intro/live-demo lines,
   before Status: five numbered, plain-language steps, no
   clause numbers - watch the 169 s silent v5 film (music
   an owner decision, said so), live WASM site with the
   exact clicks (Deal me a committed vector -> Run), run
   it yourself (`examples/host/build.sh`, then
   `tools/run.sh smoke`; Linux CI's four jobs named),
   reproduce the workloads (`demo/run_demo.sh host`), audit
   (RECORD -> audit-bundle README walk order -> plant score
   counted from `docs/metrics/plants.jsonl`).
2. Wave 6 sweep of the rest: plants 114/120@bc807e6 ->
   138/145 counted; front door gains `sanitize`; sanitize
   trap/full + canary + skip-by-name described; Linux CI
   four jobs + log artifacts; examples on-ramp; metrics
   split by recency (93/94/20 still SF-2-close; briefs and
   plants through Wave 6); Wave 6 items 1-4 recorded beside
   SF-2 completion; where-things-live rows for `examples/`,
   `audit-bundle/`, `.github/workflows/`; the stale demo
   interval expectation named in intro line, map step 4,
   and Status.

## Real finding (outside owned files - NOT fixed here)

`bash demo/run_demo.sh host` at base FAILS its interval leg:
`demo/expected-interval.txt` expects `ce81d66e...a9aec`
(pre-augmented-consumption); the program prints
`ae04caf0...c1422`, the recorded new host==board hash
(RECORD "Wave 6 augint landed"; hash moves only through
hashed stage-3 op counts; classifications unchanged).
IAS15 (2,001/2,001 native and soft) and KissFFT (12/12)
legs PASS. `board/interval_run.sh` computes its expectation
live from the host runner and never reads that file, so the
on-silicon claim is unaffected. The fix is a one-file lead
follow-up: restamp `demo/expected-interval.txt` (and adjust
the two README sentences here that name the gap, plus this
parcel's step-4 wording, once it lands).

Related minor quirk, deliberately not given as a map
command: `audit-bundle/MANIFEST.sha256` is CRLF (576/576
lines), so the bundle README's literal `sha256sum -c`
fails under Git Bash here (filenames grow a `\r`). The
hashes themselves verify 576/576 when read CR-tolerantly
(`verify_manifest.py` in this scratch dir). The frozen
bundle must not be edited; noted for the lead only.

## Per-number table (claimed in README vs re-derived)

Derivation scripts: `derive.py`, `derive2.py`,
`verify_manifest.py`, `linkcheck.py`; logs beside them,
plus `smoke.log`, `standard-before/after/tip.log`,
`sanitize-trap.log`, `demo-host.log`, `example.log`,
`interval-out.txt`.

| Number (where claimed) | Re-derived | How |
|---|---|---|
| 169 s, 2560x1440, silent film (intro, step 1, Video) | 169.0 s (169000/1000), tkhd 2560x1440, no `soun`/`mp4a` atoms; sha256 `bbb2f2c9...020cb` | MP4 box probe in `derive.py` over `video/out/assembly_v5.mp4` |
| 180 s, 1080p old cut (Video) | 180.0 s, 1920x1080, no audio atoms | same probe over `video/out/final.mp4` |
| 849 of 849, 783 Tier 1, 66 Tier 2, 273 attribute rows (Status, step 2 denominator) | rows=849, tier {1:783, 2:66}, status implemented=849, rounding attr=273 | counted `docs/COVERAGE.tsv` (csv parse, `derive.py`) |
| 822 of 849 runnable on the site (step 2) | 822 runnable, 9 pair, 27 non-runnable, 849 total | counted `site/ops.json` `runnable` flags; live site fetched 2026-10-30: HTTP 200, buttons Run / "Deal me a committed vector" |
| 411,213 committed vectors (step 3, Status) | 411,213 data lines (411,298 total minus 85 `#` lines, 51 files); gate repeats it | `derive2.py` over `tests/vectors/*.vec`; smoke `total 411213 passed 411213` |
| standard adds 1,117,504 + 5,505,024 (Status) | f16-exhaustive 917,504 + pack64-sweep 200,000 = 1,117,504; aug pool total=5,505,024 mismatches=0 | `tools/run.sh standard` inventory, run three times |
| smoke 27 s (step 3, stated as a record) | `budget smoke: PASS in 27s` | `bash tools/run.sh smoke` on the project desktop, this session |
| Four CI jobs: smoke, standard, example-host, sanitize (step 3, Status, table) | jobs exactly those; run lines `run.sh smoke`, `run.sh standard`, `bash examples/host/build.sh`, `MSF_SANITIZE=full run.sh sanitize` | read `.github/workflows/ci.yml` in full |
| 2,000 steps / 2,001 records (step 4, Status) | expected file: 2,001 records, steps 0..2000; demo: native matched=2001, soft matched=2001 (26,083,624 shim ops) | counted `demo/expected-ias15.txt`; ran `bash demo/run_demo.sh host` |
| 12 KissFFT configurations, N=256/1024/4096 (step 4, Status) | 12 KF rows = 3 sizes x complex/real x fwd/inv; demo `12/12 KF rows identical; anchors PASS` | counted `demo/expected-kissfft.txt`; same demo run (KissFFT never called "unmodified" in the map) |
| 710 interval rows; counted calls 396,745; hash ae04...c1422 (step 4, Status) | catalogue 710 data rows; own run `rows=710 total_ops=396745`, `HOST_SHA256 ae04caf0...c1422` | counted `tests/interval_catalogue.tsv` (excl. `#`); compiled/ran the demo's exact interval leg, then the full demo |
| 616,754 -> 396,745; stage 3 283,314 -> 63,305; model 394,666 (Status) | total 396,745 re-measured by my run; the "before" figures and stage split are RECORD/augint-brief records | my interval run for the after-total; before-values quoted from `docs/RECORD.md` augint entry (not re-measurable without the pre-swap binary) |
| 138 of 145 plants, Wave 6 20 of 20 (step 5, Status) | total=145, caught=138, missed=7; wave6 20/20 | parsed every row of `docs/metrics/plants.jsonl` (`derive.py`) at base==tip for that file |
| 576 frozen audit files (step 5) | 576 entries, 576 OK, 0 mismatch, 0 missing | `verify_manifest.py` hashes every manifest entry on disk |
| 93 usage / 94 passes / 20 escalations, SF-2-close (Status) | rows=93/94/20; latest wave in each is wave5 | parsed the three `docs/metrics/*.jsonl` files |
| Example output pinned, ends EXAMPLE PASS (step 3) | expected file 12 lines ending `EXAMPLE PASS`; run diff clean | `bash examples/host/build.sh` -> `host example: PASS` |

Record-quoted, deliberately NOT re-run in this parcel
(no board access, one-time shards): the six-chip IAS15
sweep and 968/968 LED-build harness vectors; host==board
interval/KissFFT silicon hashes; the binary32 `exp2`/`log2`
exhaustive 42,949,672,960 mode-checks each and the
binary16 augmented-pairs exhaustive 12,884,901,888. The
README attributes these to `docs/RECORD.md`, which carries
the shard, census and board detail; verified here only
that RECORD does carry those entries.

## Commands run (acceptance a, d)

All in `worktrees/w6-judgemap` under Git Bash with
MSF_PYTHON pinned; every command printed in the map was run
here except full-flavour sanitize, named CI-only (job
`sanitize`) in both map and Status.

- `bash examples/host/build.sh` -> PASS (`example.log`).
- `bash tools/run.sh smoke` -> PASS 27 s; 411,213/411,213;
  all 12 named controls refused (`smoke.log`).
- `bash tools/run.sh standard` -> PASS (58 s before edits,
  56 s after, 57 s at the committed tip - records);
  verdict unchanged (`standard-*.log`). Acceptance (d).
- `bash tools/run.sh sanitize` (trap) -> PASS 53 s;
  canaries caught; `heap_far` boundary stated by the tool
  (`sanitize-trap.log`).
- `bash demo/run_demo.sh host` -> IAS15 PASS, KissFFT PASS,
  interval FAIL (stale expectation, above); archives
  fetched and hash-verified by the script (`demo-host.log`).
- Link check `linkcheck.py README.md`: 26 relative links,
  0 bad, at base text (14/0) and at tip (`linkcheck*.log`).
  Acceptance (b).
- Live site fetch -> 200; instrument text and buttons match
  the map's click instructions.
- `sha256sum -c MANIFEST.sha256` in audit-bundle -> fails
  on CRLF only; CR-tolerant re-verification 576/576 OK.

## Unresolved for the lead

1. `demo/expected-interval.txt` stale since the augint hash
   move (outside owned files). Until restamped, the demo
   exits FAIL on that leg; README now says so in three
   places (intro line, map step 4, Status) - restate those
   when fixed.
2. `audit-bundle/MANIFEST.sha256` CRLF makes its own
   documented verify command fail under Git Bash on this
   host; contents verify. Frozen bundle - document, don't
   edit (a future bundle version is the sanctioned route).
3. Nothing else: no number in the map lacks a derivation
   above; silicon/exhaustive figures are RECORD-quoted as
   labelled.
