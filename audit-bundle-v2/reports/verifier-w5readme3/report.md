# verifier-w5readme3 report — NOT READY

Copy: `worktrees/verify5-readme3` at `5986b5d` (parent `e9c57fb`).
Method: every number re-derived by scripts in this directory (Git Bash,
`MSF_PYTHON` = workspace `.venv`); the copy was never modified
(`git status` clean at close). Rerun: `v01_counts.sh v02_runner.sh
v03_standard.sh v04_augpool.sh v05_wasm.sh v06_wasmdet.sh v07_wasmsame.sh
v08_gates.sh regen_data.py status_line.py`.

## Claimed vs re-derived

| Public number | Claimed (tree) | Re-derived | Verdict |
|---|---|---|---|
| Instantiations headline (README.md:21) | 859 of 859 | 849 (COVERAGE 849 = Tier1 783 + Tier2 66; `msf_dispatch.h` 849; data.json 849) | WRONG (F1) |
| Tier 1 / Tier 2 (README.md:26,29) | 783/783, 66/66 | 783 / 66, all implemented, 0 unconfirmed | OK |
| Attribute-carrying rows (README.md:36) | 273 | COVERAGE `rounding==attr` 273 = dispatch `has_rm` 273 | OK |
| Committed vectors (README.md:44, data.json) | 411,213 | counted lines 411,213 = runner `verify` total 411213 PASS (51 files) | OK |
| Standard extras (README.md:45) | +1,117,504 (917,504 + 200,000) | regen 917,504 + 200,000; runner total 1117504 PASS | OK |
| f16 aug-pool leg (README.md:46) | 5,505,024 checks | `aug_exhaustive pool` total=5505024 mismatches=0 PASS | OK |
| Plants at e9c57fb (README.md:48) | 109 of 115 | 109/115 (wave1 9/10, wave2 10/10, wave3 5/5, wave4 25/25, wave5 41/45, readme 9/10, site 10/10); plants.jsonl == e9c57fb's | OK |
| data.json plants header | 115 of 115 | 109/115; header contradicts its own by_wave rows (sum 109/115) | WRONG (F4) |
| data.json pair-excluded (numbers table) | 0 | 9 (`msf16/32/64_augmented_{add,sub,mul}`); 822+0+18=840 != 849 | WRONG (F3,F6) |
| ops.json (849, 9 pairs) | 849 / 9 pair flags | regen identical (`ops equal: True`) | OK |
| Sample vs committed vectors | 1,620 bundled | 1,619/1,620 match; idx 1258 `msf64_exp2 te 0 -> 3ff0000000000001` vs explog-f64.vec:4 `...3ff0000000000000` | WRONG (F5) |
| replay-log.txt | 1620 replayed, 0 mismatches | committed wasm + committed sample: 1 mismatch, exit 1 | STALE (F7) |
| WASM through rebuilt wasm (regen sample) | 0 mismatches required | 1620/1620, 0 mismatches (rebuilt wasm); wasm exp2(0) = `3ff0000000000000` exactly 1 | OK (library correct) |
| msf.wasm byte-identity (770,233 B, 4ddb8192…) | identical across builds | rebuild 768,126 B (01025e1c…); code sections byte-identical, 3 DWARF custom sections differ (absolute paths); same-path rebuilds identical | QUALIFIED (F8) |
| Metrics (README.md:81-82) | 93 usage / 94 pass / 20 escalations | 93 / 94 / 20 | OK |
| Briefs (31 rows, frozen prefix, base real) | append-only | 30-row prefix byte-identical to e9c57fb's; new row base e9c57fb8c… (real) | OK |
| Augmented benefit (README.md:68-70) | "realized in the shipped workload, not a study-model claim" | RECORD.md:971-975: "remains a study model, not a shipped claim"; README:68 says interval "does not yet consume" | CONTRADICTS (F2) |
| Workloads (README §Status, site §silicon) | 2,001/2,001 + `4d4530a6`, 968/968 LED, 710/710 + `ce81d66e` + 7.92 s, KissFFT 12/12 N=256/1024/4096 Fork B | match RECORD.md:558-560,859-860,868,705-706,761 (+797 TWIDDLES pointer) | OK |
| Exhaustives (README.md:50-53) | 42,949,672,960 x2, 12,884,901,888 | match RECORD.md:880,912,958 (= 10x2^32, 3x2^32); quoted, not re-run | OK |
| Claim surface vs e9c57fb | README + site/ + 1 briefs row | `git diff` stat: exactly those 13 paths; no other tree changes | OK |
| Serve (staged copy, :8123) | status == data == recounts; no 404s | 9/9 assets HTTP 200; status line prints data.json (incl. wrong 115/115, pair 0) | OK-except-data |

## Findings (disconfirming only)

- F1 `worktrees/verify5-readme3/README.md:21` — "859 of 859 instantiations"
  contradicts every re-derivation (849) and the README's own 783/783 +
  66/66 (= 849). Fix to 849.
- F2 `README.md:68-70` — benefit "realized in the shipped workload, not a
  study-model claim" inverts the authority (`RECORD.md:971-975`) and
  self-contradicts line 68. Restore study-model labelling.
- F3 `site/data.json` `sample.ops_pair_excluded: 0` — re-derived 9; the same
  file's `ops.json` carries 9 pair flags, and 822+0+18 != 849. Not producible
  by the committed `site/build_data.py:215-216` from this tree.
- F4 `site/data.json` `plants.caught/total: 115/115` — re-derived 109/115;
  the file's own `by_wave` rows sum to 109/115. Same non-reproducibility.
- F5 `site/vectors-sample.json` idx 1258 — `msf64_exp2 te 0` expects
  `3ff0000000000001`, but `tests/vectors/explog-f64.vec:4` commits
  `3ff0000000000000`. The exp2(0)=1 known-answer cell is violated in the
  sample; wasm and the .vec agree on exactly 1. 1,619/1,620 sample lines match.
- F6 consequence of F3: the numbers table (`site/app.js:320-321`) renders
  "Augmented pair operations excluded here: 0 (host/board gated)". The
  exclusion IS printed in `site/index.html:77-86`, `site/README.md:19-28`,
  and `README.md:190-192`, but not (correctly) in the numbers table.
- F7 `site/replay-log.txt` ("replayed=1620 mismatches=0") does not reproduce:
  `node site/replay.mjs` over the committed artifacts reports 1 mismatch
  (the F5 line) with exit 1. The `msf.wasm` under test is itself correct.
- F8 `site/msf.wasm` byte-identity: rebuilds via the recorded Zig 0.17.0
  recipe (archive sha256 `b5663f69…` re-verified this session) are 768,126 B
  (`01025e1c…`), not 770,233 B (`4ddb8192…`). All 9 code/data sections are
  byte-identical; only 3 DWARF custom sections differ (embedded absolute
  paths). Same-directory rebuilds are byte-identical, so the recipe is
  deterministic only at a fixed absolute path — it cannot reproduce the
  committed bytes from any other worktree path.

No other disconfirmations: Tier counts, attr 273, P1=R2 + clause-fixed
`roundTiesTowardZero` (`src/msf_aug.c:6-23,299,341`, `tables/` rounding token
`fixed`), fifth-attribute scope, KissFFT never "unmodified"
(`site/index.html:157`; README "unmodified" occurrences are REBOUND desktop),
timings only as recorded rates with units, drift 4/4, unit PASS, serve clean,
claim surface exactly owned files.

## Not done (named, not silence)

- Full `smoke` negative-control battery, symbol/type scans: not re-run
  (vector verify + drift + unit re-ran read-only from scratch builds).
- One-time exhaustives (2 x 42,949,672,960; 12,884,901,888) quoted from
  RECORD, not re-executed. Board budgets not run. Pixel QA / non-Edge
  browsers not checked. Live Pages page check stays post-merge (lead).
