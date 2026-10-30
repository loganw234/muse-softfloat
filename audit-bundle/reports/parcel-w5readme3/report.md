READY

README + site refresh at SF-2 close on branch
`wave5-readme3` (worktree `worktrees/w5-readme3`), base
`e9c57fb8c100913502d67242cad0d0729b7ce46a`, commits
`4f39357` (site, 11 files) and `498a916` (README +
briefs row). Never pushed/merged. Owned files only:
`README.md`, `site/**`, `docs/metrics/briefs.jsonl`
(this parcel's row last, 31 rows, frozen prefix proven
byte-identical). Every number below was re-derived
from the tree this session by the named script file,
run under Git Bash with `MSF_PYTHON` pinned to the
workspace `.venv`, `TMP`/`TEMP`/`TMPDIR` in
`scratch/parcel-w5readme3/`, and a `ulimit -t` ceiling
in each script. Logs in `scratch/parcel-w5readme3/out/`.

## Every changed number, with its derivation

### README.md

| Was | Now | Derivation |
|---|---|---|
| 822 of 822 instantiations | 849 of 849 (Tier 1 783 + Tier 2 66) | `01-counters.sh` header-aware count of `docs/COVERAGE.tsv` (849 rows, all `implemented`); agrees with the gate's own line `inventory: tier1 783 implemented of 783; tier2 66 implemented, 0 planned, 66 registered` in `03-smoke.sh` |
| 39 Tier 2 rows | 66/66: 9.6 min/max 24, 9.7 payloads 9, sinPi/cosPi 6, rSqrt/hypot 6, exp2/exp2m1/log2/log2p1 12, 9.5 augmented 9 | Tier 2 census by `std_name`/`clause` in `01-counters.sh` (`9.2: 24, 9.5: 9, 9.6: 24, 9.7: 9`) |
| 255 attribute-carrying rows | 273 | Two agreeing counts in `01-counters.sh` + `03-smoke.sh`: COVERAGE `rounding=attr` census 273 and dispatch `has_rm=1` census 273. 255 was true at Step 1; Steps 2-3 added 18 five-mode `attr` rows (273 = 255 + 6 alg + 12 explog). Augmented rows carry token `fixed` (9), no attribute |
| 171,423 committed vectors | 411,213 | Counted lines in `tests/vectors/*.vec` (`01-counters.sh`, per-file table) = host runner's smoke total `total 411213 passed 411213` (`03-smoke.sh`, repeated on the edited tree in `09-final.sh`). Matches RECORD Step 4 total |
| `standard` adds 1,117,504 | Same figure, re-derived; plus the 5,505,024-check f16 aug-pool leg now stated separately | `04-standard.sh` (`tools/run.sh standard`): generated files counted 917,504 (f16-exhaustive) + 200,000 (pack-sweep) = 1,117,504; runner `total 1117504 passed`; `aug_exhaustive pool: total=5505024 mismatches=0` |
| 61 of 65 plants | 109 of 115 at `e9c57fb` | `docs/metrics/plants.jsonl` recount in `01-counters.sh` (by wave: w1 9/10, w2 10/10, w3 5/5, w4 25/25, w5 41/45, readme 9/10, site 10/10). Pinned to the named base commit in the README |
| (no metrics paragraph) | 93 usage / 94 passes / 20 escalations at `e9c57fb`, append-only through SF-2 close | Row counts in `05-counters2.sh` (every line JSON-parsed). Agrees with merge bodies `3f29682`/`a1a888f` (usage 39->93 etc.) |
| Single-board IAS15 2,001/2,001 | Six chips (genuine Pico + five RP2040-Zero clones), 2,001/2,001 each; LED build re-verified 968/968 on all six | Quoted from `docs/RECORD.md` "Six-board IAS15 (appended 2026-10-28)" (step-2000 hash `4d4530a6...f48abb`, harness hash `4573ac09...28a7`). No board run by this parcel; no timings quoted in the README |
| (no exhaustive lines) | binary32 exhaustive per exp/log bundle 42,949,672,960 mode-checks each, 0 mismatches; binary16 aug pairs 12,884,901,888 checks, 0 mismatches | Quoted from RECORD Steps 3a/3b/4 as recorded one-time evidence ("beyond the budgets"); arithmetic cross-checked here (2^32 x 2 fn x 5 modes; 2^32 x 3 ops). Not re-executed - see Not done |
| KissFFT "one named Fork B change" | Same discipline + `docs/TWIDDLES.md` derivation pointer; interval/KissFFT 12/12 unchanged | `docs/TWIDDLES.md` exists at base (link-checked in `09-final.sh`); KissFFT is never called unmodified (sweep in `09-final.sh`: "unmodified" attaches only to the REBOUND desktop reference and the KissFFT disclaimer) |
| (aug benefit unstated) | 616,754 -> 394,666 labelled a study model; interval does not consume augmented yet | Quoted from RECORD Step 4 verbatim in substance; wording keeps it a study count, not a shipped claim |

Brief/RECORD corrections found by recount (as
instructed):

- Brief figures 849 / 411,213 / +1,117,504 / 109/115
  all confirmed by recount. README's 822 / 171,423
  confirmed stale, as briefed.
- RECORD Step 4's "138,392 committed aug vector lines"
  counts raw lines including 12 comment lines
  (4 per aug file). Counted (runner) lines are
  138,380 (`02-probes.sh` raw vs counted per file;
  smoke provenance agrees: augmented-directed 130,580
  + augmented-seeded 7,800). The 411,213 total is the
  counted total and is exact either way; the README
  states no aug subtotal, and this note records the
  definitional slip for the lead. RECORD's explog
  subtotal 90,315 is the counted figure and matches.
- The delegated task text said "emsdk in scratch".
  Proven absent: `scratch/parcel-w5site/` holds no
  emsdk; the recorded recipe
  (`ledger/parcel-w5site.md`, `site/build.py`) is
  Zig 0.17.0 `zig cc`. Reused; archive sha256
  re-verified before use (below). No reinstall.

### site/ (generated data + content slots)

| Was (base a0acf2a) | Now (as of e9c57fb) | Derivation |
|---|---|---|
| base `a0acf2a` | base `e9c57fb` | `site/build_data.py` `git rev-parse --short HEAD`, run with HEAD at e9c57fb in `06-build.sh` |
| 828 total / 45 Tier 2 / 828 implemented | 849 / 66 / 849 | Same COVERAGE count as README, via the generator |
| 182,518 vectors, 45 files | 411,213 vectors, 51 files (+3 explog, +3 aug) | Same counted-line census as README |
| Plants 75/80 | 109/115 (w5 41/45, site 10/10 join) | Same plants recount |
| 810 of 828 runnable | 822 of 849 runnable | Dispatch census (`01-counters.sh`): 822 single-result `call!=0`, 9 aug `pair_call!=0`, 18 char/flag both-0. +12 is exactly the explog bundle |
| Sample 1,596 over 798 ops | 1,620 over 810 ops | Deterministic first+middle sample; predicted in `05-counters2.sh` before the fix (1620/810) and produced identically by the fixed generator in `06-build.sh`. The 12 uncovered runnable ops are the `is754version*` set (no committed lines), as before |
| (no exclusion counts) | `ops_pair_excluded: 9`, `ops_nonhex_excluded: 18` | New `data.json` fields from the same census; rendered as a numbers-table row |
| IAS15 rate 1.58 steps/s (1,000-step block) | 1.60 steps/s on every chip (2,000-step `T 2000`, six-board sweep) + LED 968/968 note | RECORD six-board entry; shown with units/context as a recorded fact, not a speed claim |

## WASM build + replay counts

Toolchain (scratch-only, reused): Zig 0.17.0
`zig cc -target wasm32-freestanding` from
`scratch/parcel-w5site/zig-x86_64-windows-0.17.0/`
(`zig version` -> 0.17.0). Archive
`zig-x86_64-windows-0.17.0.zip` re-hashed in
`01-counters.sh`: 100,268,137 bytes, sha256
`b5663f69581dcf391293fbf16c06cb80d81d806545ce618b4d0bab7f0eb8c428`
- exactly the value recorded in
`ledger/parcel-w5site.md`. Caches pointed at
`scratch/parcel-w5site/zig-cache/`; nothing installed.

Build (`06-build.sh`: `site/build.py --cc "zig cc"`):
`ops=849 runnable=822 coverage_rows=849 vectors=411213
sample=1620 sample_ops=810 plants=109/115
base=e9c57fb`; `msf.wasm` 770,233 bytes (was 676,669),
sha256
`4ddb8192a2c961ee57af653ea146c41089a9fe7c41cf71eeeb9aa3db30628706`,
byte-identical across two full builds
(`07-verify-site.sh`). Headless replay
(`site/replay.mjs` under Node v22.19.0, inside the
build): `msf_op_count=849 ops_json=849 sample=1620 /
replayed=1620 mismatches=0` (`site/replay-log.txt`).

Generator fixes that made this possible (both proven
broken at base before editing): (1) `build_data.py`'s
row regex predated the `pair_call` dispatch column
and parsed 0 of 849 rows - watched failing with
"no ops parsed from tests/msf_dispatch.h"
(`02-probes.sh`); (2) `build.py` omitted
`src/msf_aug.c` (needed by the pair trampolines even
with pairs excluded from the UI). Plus a sampler
exact-shape guard (`len(tok) != arrow+4` skips) so a
two-result line can never be misread; the guard skips
0 current runnable lines (pure defence, proven in
`05-counters2.sh`).

Surface probes (`07b-probes.sh`, all pass): exp2(0)=1,
exp2m1(0)=0, log2(1)=0, log2p1(0)=0, exp2(1)=2 (f16),
log2(+0)=-inf/divideByZero; augmented ops report
`pair=true, runnable=false` and the WASM surface
refuses them; a dealt explog sample line reproduces
live. Browser proof (`10-browser.sh`): local static
serve + headless Edge `--dump-dom` shows "WebAssembly
build ready", status line "Status at e9c57fb: 849 of
849 instantiations implemented and gated - 411,213
committed test vectors - planted-copy score 109 of
115", default run `0x40000000`, and the head+tail
exclusion text. `node --check`, `py_compile` pass.
Gates: `tools/run.sh smoke` PASS and `standard` PASS
this session, smoke repeated on the edited tree
(`09-final.sh`). Discipline note: two read-only
`python -c` one-liners inside `07-verify-site.sh`
(JSON parse/print) bend the script-files rule; no
evidence rests only on them (replay + Edge fetch parse
the same JSON), and the one `-c` that mattered (CRLF,
path bug) was redone as a file (`09b-crlf.sh`):
hand-edited files are LF-clean; `briefs.jsonl`'s 5
CRLFs are pre-existing at HEAD, my appended tail adds
0, frozen prefix untouched (`09c-crlf-base.sh`).

## Augmented representation decision

**Excluded, with the exclusion printed.** The page's
existing shape is a single uint64 result + flags end
to end (`glue.c` `msf_result_lo/hi`, `replay.mjs`
single-value compare, `app.js` single result panel).
Clause 9.5 returns a head+tail pair under
clause-fixed roundTiesTowardZero; squeezing that into
one slot (head only, or packed bits) would fake the
shape the brief forbids, and a true two-result panel
+ exports + comparator is beyond the brief's
"numbers/content slots only" fence for this parcel.
So the 9 augmented instantiations carry
`pair: true, runnable: false` in `ops.json`, never
enter the sample (0 aug lines, proven), and the
exclusion is printed in three places: the instrument
fineprint in `index.html`, the generated numbers
table, and `site/README.md` - each stating what the
operations are, why one slot cannot hold them, and
that they stay host-gated and board-replayed. The
`exp2`/`exp2m1`/`log2`/`log2p1` families fit the
existing shape honestly and are fully included
(24 sampled lines, replayed at 0 mismatches).

## Not done

- Push/merge/Pages: forbidden to this parcel. Pages
  deploys from `main`; the lead verifies the live page
  after merge. The live URL is untouched by this
  branch.
- Screenshot/pixel QA: not done. CSS untouched, no
  visual redesign (per fence); evidence is DOM-level
  (Edge dump) as in the site parcel, which measured
  Edge `--screenshot` producing no file on this host.
  Non-Edge browsers unchecked.
- Board budget: not run (lead holds the board; no
  library or board code changed). Silicon facts are
  RECORD quotes with hashes/units.
- One-time exhaustives (f32 exp/log, f16 pairs):
  quoted from RECORD with attribution, not
  re-executed; the budgeted standing legs (smoke,
  standard incl. the 5.5M aug pool) were re-run green.
- `tools/run.sh bench`: never a correctness verdict;
  not run. No performance claims made anywhere.
