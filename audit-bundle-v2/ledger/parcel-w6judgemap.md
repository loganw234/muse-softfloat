# Ledger: parcel-w6judgemap (Wave 6 queue item 5, first parcel: judge's map)

Base `af364643549b305abbaaa7fc428ae2b16b0e1afd`, branch
`wave6-judgemap`, worktree `worktrees/w6-judgemap`. Brief:
`ledger/briefs/w6-judgemap.md`. Full evidence:
`scratch/parcel-w6judgemap/report.md` (per-number
claimed-vs-derived table, command list, logs).

## 2026-10-30 result entry

**READY.** Tip `245a4f5b0aa7108f99852b385b51c397d44b6ae2`
(one commit, detailed body + Co-Authored-By; not pushed).
Owned files only: `README.md` and own `docs/metrics/briefs.jsonl`
row (wave6, binary-append, prefix verified).

Landed: a five-step plain-language "Start here" map before
Status (watch the silent 169 s v5 film; live WASM site with
the exact clicks; `examples/host/build.sh` then
`tools/run.sh smoke` with CI's four jobs - smoke, standard,
example-host, sanitize - named, full sanitize CI-only;
`demo/run_demo.sh host`; RECORD + audit-bundle walk order,
plants 138/145 counted from `docs/metrics/plants.jsonl`),
plus the Wave 6 sweep (examples, sanitize fifth budget,
Linux CI, metrics recency split, plant score off its stale
`bc807e6` pin, where-things-live rows for `examples/`,
`audit-bundle/`, `.github/workflows/`).

Verification (Git Bash, MSF_PYTHON = workspace `.venv`):
host example PASS; smoke PASS (411,213/411,213, controls
refused); standard PASS before/after/at tip, verdict
unchanged; sanitize trap PASS with canaries live; demo
host IAS15 PASS + KissFFT PASS + interval FAIL (below);
26/26 relative README links resolve at tip; live site 200
with the named buttons. Numbers re-derived per the report
table (COVERAGE/vector/plants counting, MP4 box probe,
ops.json, 576-entry audit manifest all-hash-OK, own
interval run `rows=710 total_ops=396745 ae04...c1422`).
Silicon and one-time-exhaustive figures remain
RECORD-quoted, not re-run in this parcel.

## Real finding (outside owned files)

`demo/expected-interval.txt` still expects the
pre-augmented-consumption `ce81d66e...a9aec`, so
`demo/run_demo.sh host` exits FAIL on the interval leg at
this base (program prints the recorded `ae04...c1422`;
classifications unchanged; board scripts compute the
expectation live and never read the file). Named in
README intro line, map step 4 and Status. Lead follow-up:
restamp that one file and restate the three README
sentences. Minor, same handling: the frozen bundle's CRLF
`MANIFEST.sha256` defeats its own literal `sha256sum -c`
under Git Bash here (contents verify 576/576 CR-tolerant);
frozen means frozen - document only.
