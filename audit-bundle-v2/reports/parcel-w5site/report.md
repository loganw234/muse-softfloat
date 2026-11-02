READY

Static demo site on branch `wave5-site` (worktree
`worktrees/w5-site`), base `a0acf2a`, commits `36f12c6`
(site + Pages workflow) and `cd09700` (README link +
briefs row). Never pushed/merged; repo settings untouched.

## WASM-or-fallback verdict

**WASM works — the real library runs in the browser.** No
clang/emcc existed on PATH; Zig 0.17.0 (`zig cc`, clang-based)
was fetched into `scratch/parcel-w5site/` only
(URL `https://ziglang.org/download/0.17.0/zig-x86_64-windows-0.17.0.zip`,
sha256 `b5663f69581dcf391293fbf16c06cb80d81d806545ce618b4d0bab7f0eb8c428`,
matching ziglang.org's published shasum; the 619 MB WASI SDK
route was unnecessary). `src/*.c` compiled **unmodified**
(freestanding wasm32; the library needs only
`<stddef.h>`/`<stdint.h>`) with `site/glue.c` driving the
repository's generated dispatch table
(`tests/msf_dispatch.h`). `site/msf.wasm` is 676,669 bytes.

Proof: **1,596 bundled committed vectors replayed through the
WASM build under Node v22.19.0, 0 mismatches** (result bits
masked to kind width, flags exact — the committed files carry
no `compare=` directives; `~`-masked lines, `internal.pack*`,
and the non-hex-drivable char/flag ops are excluded by the
generator). Log: `site/replay-log.txt`
(`msf_op_count=828 ops_json=828 sample=1596 /
replayed=1596 mismatches=0`). Sample covers 798 of 810
runnable ops (first + middle committed line per op; 12
runnable ops have no committed lines to sample). Rebuild is
byte-identical: msf.wasm sha256
`02431beee60b225c6351322df1b6ee90fd8bf187ae921df43f0363f09916ac4d`
across two `site/build.py` runs. Known-answer probes through
the same exports also pass (hypot 3-4-5, rSqrt, the
ties-to-even vs ties-to-away tie pair, div-by-zero flag).

The vector-playback fallback exists only as the page's honest
degraded mode: if WebAssembly cannot load, free entry is
disabled and dealt vectors show recorded results labelled
"Recorded result shown — no live computation".

## What a visitor can do

- Pick format (binary16/32/64/general), operation (810
  runnable instantiations from the dispatch table, shown as
  `stdName — msf_name` with clause/tier), and rounding mode
  (all five attributes where the op takes one).
- Enter operands as hex bits (what executes) or decimal
  (display conversion, kept in sync), run, and see: result
  bits + decimal value, sign/exponent/significand bit-field
  breakdown, and the five exception flags as chips.
- "Deal me a committed vector": loads a real line (with
  source file + provenance tag) from the bundled sample,
  runs it through WASM live, and shows MATCH/MISMATCH
  against the recorded result and flags.
- Read the generated numbers table (with a source column),
  plant scores by wave, the three silicon workloads (IAS15
  panel with a figure-8 sketch labelled "illustration — not
  simulation output"), and the verification story with links
  to RECORD/COVERAGE/studies on GitHub.

## Number provenance (every displayed number)

| Displayed | Value | Source at a0acf2a |
|---|---|---|
| Instantiations total / Tier 1 / Tier 2 / implemented | 828 / 783 / 45 / 828 | counted from `docs/COVERAGE.tsv` by `site/build_data.py` |
| Committed vectors / files | 182,518 / 45 | counted lines in `tests/vectors/*.vec` (matches RECORD Wave 5 Step 2b "smoke 182,518") |
| Runnable ops in page | 810 of 828 | `tests/msf_dispatch.h` (call != 0; 12 char + 6 flag ops excluded) |
| Replay count / ops covered | 1,596 (0 mismatches) / 798 | `site/replay-log.txt`, sample from `tests/vectors/` |
| Plants caught (total + by wave) | 75 of 80 | `docs/metrics/plants.jsonl` |
| IAS15 agreement + rate | 2,001/2,001 hashes; 1.58 steps/s at 125 MHz (1,000-step block); step-2000 hash `4d4530a6…` | `docs/RECORD.md` Wave 3 entry |
| Interval agreement | 710/710 rows; hash `ce81d66e…`; 7.92 s workload-call time at 125 MHz | `docs/RECORD.md` Step 1c entry |
| KissFFT agreement | 12/12 hash rows; N=256/1024/4096; one named change, never "unmodified" | `docs/RECORD.md` Step 2c workload entry |
| Wave 5 status | roundTiesToAway/rSqrt/hypot landed (Tier 2 45/45); exp2/log2/augmented in-progress | `docs/RECORD.md` Wave 5 entries + COVERAGE |

Brief corrections (recounts the brief asked for): the
brief's "822 instantiations" and "171,423+ vectors" were
stale (Step 1-era). At base the tree says **828** and
**182,518**; the page uses the recounted figures. Plants
75/80 confirmed as briefed.

## Verification performed here

- Node replay of 1,596 vectors through the WASM build:
  0 mismatches (above); rebuild byte-identical.
- `node --check site/app.js`; DOM-free unit checks of the
  page's conversion helpers (f16 codec, per-kind decimal
  rendering) — all pass; `py_compile` on both build scripts;
  JSON/JSONL parse; workflow YAML parsed with PyYAML
  (installed into scratch for the check).
- Local static serve (`python -m http.server`) + **headless
  Microsoft Edge** (already installed) `--dump-dom`: WASM
  "ready" banner present, status line rendered from
  data.json, default `msf32_add` run shows `0x40000000 = 2`,
  tables populated. (Edge `--screenshot` produced no file
  on this host after two attempts despite the DOM dump
  succeeding, so layout was verified from the rendered DOM
  + CSS, not from pixels — named here rather than smoothed
  over.)
- External-request audit: the only `https://` strings are
  anchor `href`s to the GitHub repo docs (required by the
  brief); no external scripts, styles, fonts or fetches.
  All linked repo paths exist at base.
- Machine load kept light throughout: single-threaded
  compiles, no parallel builds (another parcel's sweep was
  running).
- `tools/run.sh` was **not** run: this parcel changes no
  library/test code (owned files only: `site/**`, the Pages
  workflow, README link line, one briefs.jsonl row using the
  established field set), and the sweep owns the machine.
  The merge gate remains the lead's to run.

## How to view it locally

```
python -m http.server 8000 --directory site
```

then open <http://127.0.0.1:8000/> (from the worktree root;
`file://` will not work — the page fetches its JSON/WASM).
Rebuild after tree changes:
`python site/build.py --cc "zig cc"` (any wasm32-freestanding
clang works; Node required for the replay proof).

## Not done (by design / for the lead)

- **Pages enablement**: Settings → Pages → Source: GitHub
  Actions is a one-time owner/lead action at merge.
  `.github/workflows/pages.yml` (Actions route, uploads
  `site/` as the Pages artifact) is committed but has never
  run — it cannot be exercised from this branch without
  pushing, which the brief forbids. Its YAML parses; the
  first real run happens after merge to `main`.
- The live URL in the README
  (<https://loganw234.github.io/muse-softfloat/>) will 404
  until the above happens.
- Screenshot-level visual QA (see verification note) and any
  non-Edge browser check; Chrome is installed but the DOM
  evidence from Edge was judged sufficient under the
  light-load rule.
- No `tools/run.sh` gate run from this parcel (above).
