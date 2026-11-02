## 2026-10-28 14:52:00 -07:00 - Design entry: Wave 5 static demo site (GitHub Pages, real library via WebAssembly), written before any page code

Measured: brief ledger/briefs/w5-site.md read first and
obeyed exactly; bundled:taste loaded via read_skill before
any page file (anti-slop constraints adopted: no purple/blue
gradient hero, no gradient headline text, no identical
3-card icon grids, no glassmorphism-everywhere, no emoji
icons, no centered eyebrow-pill hero). worktrees/w5-site
verified on branch wave5-site at base a0acf2a, clean.
AGENTS.md read (Git Bash for builds, TMP into workspace,
LF bytes, light machine load, max 2 parallel jobs).

Inventory recounted at base a0acf2a (brief said recount,
don't trust it - brief numbers were stale in two places):
docs/COVERAGE.tsv has 828 instantiation rows (not 822):
783 Tier 1 + 45 Tier 2, every row status=implemented.
tests/vectors/*.vec totals 182,518 counted lines (matches
docs/RECORD.md Wave 5 Step 2b close "smoke 182,518", not
the brief's 171,423 which was the Step 1 close).
docs/metrics/plants.jsonl: 80 rows, 75 caught / 5 missed.
The page will use the recounted figures and cite the file
each came from; site/build_data.py recomputes them from
COVERAGE.tsv + docs/metrics/*.jsonl + vector line counts
at build time into site/data.json (no hand-typed totals).

Workload facts the page may state (all docs/RECORD.md):
IAS15 on RP2040 2,001/2,001 IAS15FH1 records bit-identical
to the unmodified desktop run, step-2000 H_state
4d4530a6...f48abb, measured 1.58 accepted steps/s at
125 MHz (recorded fact with units, not a speed claim);
interval catalogue 710/710 host==board, IW1
ce81d66e...a9aec, 7.92 s of workload-call time at 125 MHz;
KissFFT 12/12 hash rows at gated sizes N=256/1024/4096,
BSD-3 scratch-only with the one named change (exact cycle
fractions into sinpi/cospi) - never "unmodified".
Wave 5 in-progress (exp2/log2/augmented) labelled
in-progress; roundTiesToAway, rSqrt, hypot landed (Tier 2
45/45). No performance claims anywhere.

Interactivity design (brief step 1, WASM first):
- Toolchain: no clang/emcc/wasi-sdk on PATH (gcc 16.1
  MinGW32, node v22.19.0, python 3.12 present). WASI SDK
  34 Windows tarball is 619 MB; Zig (zig cc, clang-based,
  -target wasm32-freestanding) is ~50 MB and sufficient
  because src/*.c is freestanding: only <stddef.h>/
  <stdint.h> plus own headers, msf_u128 is a two-u64
  struct (no __int128), no libc string/mem calls in src.
  Fetch Zig into scratch/parcel-w5site/ only, URL+sha256
  recorded below before use. Fallback order if Zig fails:
  WASI SDK tarball; 90-min cap on the toolchain battle
  total, then the brief's vector-playback fallback.
- Glue (site/glue.c, outside src/, src/ unmodified):
  #includes tests/msf_dispatch.h (generated op table:
  name, nargs, has_rm, has_flags, call(args,rm,flags)
  -> uint64) and exports for wasm: op_count, run(op_index,
  rm, a_lo,a_hi,b_lo,b_hi,c_lo,c_hi) writing {result u64,
  flags u32, ok u32} to an exported memory cell, plus
  out_ptr(). i32 lo/hi pairs avoid BigInt ABI variance.
  site/build_data.py parses MSF_OPS order from
  tests/msf_dispatch.h into site/ops.json (name, std_name,
  nargs, arg/ret kinds, has_rm, has_flags) so JS indices
  match the C table deterministically; character ops
  (CHAR sigs) and non-hex-drivable entries are excluded
  from the UI list by an explicit filter in the generator.
- UI (plain HTML/CSS/JS, no framework, no external
  requests): format selector (binary16/32/64 by dest),
  op selector (filtered), rounding-mode selector (five
  attributes where has_rm), per-operand hex + decimal
  entry (decimal converted in JS via DataView/f16 encode;
  hex is the source of truth shown back), result bits with
  sign/exponent/significand field breakdown, five flag
  chips, and "deal me a committed vector": loads a real
  line from bundled site/vectors-sample.json (generated
  by build_data.py from tests/vectors/, stratified across
  formats/ops, each entry carrying its provenance tag and
  source file), runs it through WASM live, shows
  match/mismatch against the recorded result+flags.
- Proof: site/replay.mjs under Node instantiates
  site/msf.wasm and replays >=500 bundled committed
  vectors; build log committed as site/replay-log.txt
  (0 mismatches required; comparison rules mirror
  tests/VECTORS.md: # compare=nan-class handled, flags
  "--" skipped, internal.pack* excluded from WASM replay
  since pack is not a public op - sample is public ops
  only and says so).
- Panels: metrics strip from site/data.json (plant score
  by wave, vector totals, instantiation counts); IAS15
  panel (facts above; any orbit sketch labelled
  "illustration"); "how this was verified" linking
  RECORD.md/COVERAGE.tsv/studies on GitHub.
- Look: technical-instrument / lab-notebook. System font
  stack, monospace for bits, squared corners mostly,
  ruled hairlines, one restrained accent (bench-equipment
  teal on white/graph paper), no gradients, no glow,
  respects prefers-reduced-motion.
- Deploy: .github/workflows/pages.yml uploading site/ as
  the Pages artifact (Actions route per brief);
  site/README.md documents local view + rebuild; README.md
  gets one link line under the title block to
  https://loganw234.github.io/muse-softfloat/. Lead
  enables Pages at merge; repo settings untouched.
  site/build.py regenerates data.json + ops.json +
  vectors-sample.json + msf.wasm + replay log from repo
  root (toolchain path via $MSF_ZIG or scratch default).
- Verification: local static serve + Node-driven checks
  (WASM replay, JS logic checks); a real browser only if
  already present - named honestly in the report.
  Every displayed number spot-checked against its source.
  Light load: single-threaded builds, no parallel make.
- Owned files only: site/**, .github/workflows/pages.yml,
  README.md link line, docs/metrics/briefs.jsonl row.
  Clean room: nothing with the forbidden three letters in
  its name is opened or created.

Toolchain fetch record (filled when the archive lands):
pending - Zig x86_64-windows zip from ziglang.org, sha256
computed on download and appended below before first use.

## 2026-10-28 15:06:00 -07:00 - Toolchain fetch + first WASM proof

Fetch (scratch only, owner-cleared): Zig 0.17.0
x86_64-windows from
https://ziglang.org/download/0.17.0/zig-x86_64-windows-0.17.0.zip
(100,268,137 bytes) into scratch/parcel-w5site/;
archive sha256
b5663f69581dcf391293fbf16c06cb80d81d806545ce618b4d0bab7f0eb8c428
- matches the shasum published in ziglang.org's download
index.json (fetched same session). `zig version` -> 0.17.0.
The 619 MB WASI SDK route was not needed. Scratch holds
the extracted tree + zig-cache (ZIG_GLOBAL_CACHE_DIR /
ZIG_LOCAL_CACHE_DIR pointed there); nothing entered the
repo except site build outputs.

First proof (single-threaded, light load): site/build.py
ran build_data.py (ops=828 runnable=810 vectors=182518
sample=1596 sample_ops=798 plants=75/80 base=a0acf2a),
compiled src/*.c unmodified + site/glue.c with
`zig cc -target wasm32-freestanding -O2 -nostdlib
--no-entry` to site/msf.wasm (676,669 bytes), and replayed
the 1,596-vector sample under Node v22.19.0:
msf_op_count=828, mismatches=0. WASM verdict: GO - the page
may claim "the actual library, compiled to WebAssembly";
the vector-playback fallback is implemented in-page only
as the honest degraded mode if a visitor's browser cannot
load the build.

## 2026-10-28 15:11:00 -07:00 - Results: site built, verified, committed (READY)

Commits on wave5-site (not pushed/merged): 36f12c6 "Added
the static demo site with the real library in WebAssembly"
(site/** 13 files + .github/workflows/pages.yml) and
cd09700 "Linked the demo site from the README and ledgered
the brief" (README one link line to
https://loganw234.github.io/muse-softfloat/ under the
title block + docs/metrics/briefs.jsonl row). Owned files
only; src/, tests/, tables, other docs untouched. Both
commits carry detailed bodies + the Co-Authored-By trailer.

What shipped: bench-instrument static page (taste rules
obeyed: white ground, hairlines, dark-teal accent, system
fonts, no gradients/glass/emoji/hero-pill; orbit sketch
labelled illustration; prefers-reduced-motion honoured).
Instrument over 810 runnable dispatch entries: format/op
(five-mode rounding where applicable) selectors, hex +
decimal operand entry, bit-field breakdown, flag chips,
deal-me-a-committed-vector with live MATCH verdict. Numbers
table + plants-by-wave from site/data.json (build_data.py
from COVERAGE.tsv / plants.jsonl / vector counts); workload
facts quoted from RECORD.md with units; exp2/log2/augmented
labelled in-progress; no performance claims; zero external
requests (only user-clicked GitHub doc anchors).

Verification (all this session, light load - single-threaded
throughout, sweep undisturbed): Node replay 1,596/1,596,
0 mismatches (site/replay-log.txt); wasm rebuild
byte-identical (sha256 02431bee...); known-answer probes
(hypot 3-4-5, r_sqrt, te/ta tie pair, div-by-zero); node
--check + DOM-free JS helper tests pass; py_compile + JSON
+ PyYAML (scratch-installed) parse pass; static serve +
headless Edge (preinstalled) --dump-dom shows WASM-ready
banner and default run 0x40000000 = 2. Edge --screenshot
produced no file in two attempts (DOM dump worked) - pixel
QA not claimed. tools/run.sh not run (no library/test code
changed; merge gate is the lead's, sweep owns the machine).

Brief corrections found by recount (as instructed): 828
instantiations, not 822; 182,518 committed vectors, not
171,423 (matches RECORD Step 2b close). Not done, named:
Pages enablement (lead, at merge - workflow committed but
never run, cannot be exercised without pushing); live URL
404s until then; non-Edge browsers unchecked. Full detail:
scratch/parcel-w5site/report.md (first line READY).
