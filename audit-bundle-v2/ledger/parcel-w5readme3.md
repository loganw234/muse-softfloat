## 2026-10-29 13:05:00 -07:00 - Design entry: Wave 5 close README + site refresh at SF-2 close, written before any README/site edit

Measured: brief ledger/briefs/w5-readme3.md read first
and obeyed exactly. worktrees/w5-readme3 verified on
branch wave5-readme3 at base e9c57fb8190913502d67242cad0d0729b7ce46a
(e9c57fb "Landed verifier-w5metrics plant grades (4 of
5)"), clean. AGENTS.md read (Git Bash for builds, TMP
into workspace, LF bytes, one heavy job at a time,
script files only). Owned files only: README.md,
site/**, docs/metrics/briefs.jsonl (this parcel's row
last). Never push/merge. Commits detailed + trailer
Co-Authored-By: Muse Code (muse-wonder-full-1.0)
<noreply@meta.ai>.

State of record to verify, none to copy (brief figures
are claims): 849 instantiations (Tier 1 783 + Tier 2
66/66); 411,213 committed vectors (+1,117,504 under
standard); plants 109/115 at e9c57fb; IAS15 six-board
2,001/2,001 + interval + KissFFT 12/12; RECORD.md the
narrative source. README currently claims 822 /
171,423 (stale); site/data.json currently stamps base
a0acf2a with 828 / 182,518 / 75-of-80 (Step 2b-era,
stale). Every displayed number will be re-derived from
this tree by script files under Git Bash with
MSF_PYTHON pinned to the workspace .venv, TMP/TEMP in
scratch/parcel-w5readme3/, ulimit ceilings set in each
script; derivation commands logged to scratch and
quoted in the report.

Derivations planned (counter script +
tools/run.sh):
- docs/COVERAGE.tsv row/tier/status counts (header-
  aware, mirroring tools/run.sh inventory_check:
  TIER1_TOTAL_EXPECTED=783, TIER2_TOTAL_EXPECTED=66);
  Tier 2 family census (minmax/payload, sinPi/cosPi,
  rSqrt/hypot, exp2/exp2m1, log2/log2p1, augmented x9
  with rounding token "fixed").
- tests/msf_dispatch.h MSF_OPS census: total entries,
  single-result call!=0, char/flag call==0 pair==0,
  aug pair_call!=0 (MSF_SIG_AUG_PAIR). Hypothesis to
  test before any edit: site/build_data.py's row
  regex predates the pair_call column (rows now end
  ", call, pair_call }") and will parse zero rows;
  site/build.py SRC predates src/msf_aug.c (run.sh
  SRC includes it). Both are site/** fixes if proven.
- Committed vectors: counted lines in
  tests/vectors/*.vec per file + the host runner's
  own total from tools/run.sh smoke verify log (the
  two must agree; report both). Standard-only total:
  tests/gen_vectors.py f16-exhaustive + pack-sweep
  200000 outputs counted, plus the aug f16 pool leg
  stated separately (never folded silently).
- docs/metrics/plants.jsonl caught/total overall and
  by wave; README pins the figure to the named base
  commit e9c57fb. Metrics-refresh row counts
  (usage/passes/escalations/briefs) quoted from the
  merged commits 3f29682/a1a888f bodies, not
  recomputed here.
- Workload/evidence facts quoted from docs/RECORD.md
  with units (six-board IAS15 incl. the hash-verified
  LED build; interval 710/710; KissFFT 12/12 with the
  one named Fork B change - never "unmodified"; two
  binary32 exhaustives at 42,949,672,960 mode-checks
  each; binary16 augmented pairs 12,884,901,888 pair
  checks). Timings stay records, never performance
  claims. The augmented op-count benefit (616,754 ->
  394,666) stays labelled a study model; interval
  does not consume the operations yet.

Site plan (numbers/content slots only, no visual
redesign):
- Toolchain correction, recorded now: the delegated
  task text says "emsdk in scratch"; the parcel
  scratch holds no emsdk. The recorded recipe
  (ledger/parcel-w5site.md, site/build.py docstring)
  is Zig 0.17.0 "zig cc -target wasm32-freestanding",
  extracted tree + archive present in
  scratch/parcel-w5site/ (zig version -> 0.17.0 this
  session). Plan: verify the archive sha256 against
  the recorded b5663f69... before use and reuse it;
  reinstall into scratch only if proven absent/broken.
  No emsdk install: build.py drives a clang-shaped
  command and the proven bytes are Zig's.
- Augmented representation decision rule (brief):
  the page's existing shape is one uint64 result +
  flags (site/glue.c msf_result_lo/hi, replay.mjs
  single-value compare, app.js single result panel);
  Clause 9.5 returns a head+tail pair with
  clause-fixed roundTiesTowardZero and pin P1=R2.
  Default: EXCLUDE the 9 augmented instantiations
  from the runnable UI/sample with the exclusion
  printed on the page and in site/README.md (what
  they are, why one slot cannot hold two results,
  where they are gated). Include them only if a
  two-result shape proves to be a slot change, not a
  redesign - never pack head+tail into one value or
  show the head alone as "the" result. exp2/exp2m1/
  log2/log2p1 are ordinary single-result MATH_UN ops
  and join the UI/sample with the regrowth.
- Re-run site/build_data.py, rebuild site/msf.wasm +
  glue via site/build.py --cc "zig cc", headless
  replay (site/replay.mjs under Node) over the
  refreshed sample at 0 mismatches; page numbers
  stamped as-of the base commit via data.json base;
  site/README.md kept in step (runnable counts,
  sample size, aug exclusion).
- Fences: nothing with the forbidden three letters in
  its name is opened, searched or listed; no
  REBOUND/KissFFT source into the repo (pointers
  only); WASM tooling scratch-only.

Report: scratch/parcel-w5readme3/report.md
(READY/NOT READY; every changed number with its
derivation command; WASM build + replay counts; aug
decision; not-done) + this ledger file.

## 2026-10-29 13:34:11 -07:00 - Results: README + site refreshed, verified, committed (READY)

Commits on wave5-readme3 (not pushed/merged): 4f39357
"Refreshed the demo site at SF-2 close (849
instantiations)" (site/** 11 files) and 498a916
"Audited the README at SF-2 close and ledgered the
brief" (README.md + docs/metrics/briefs.jsonl row
last, 31 rows, frozen prefix byte-identical). Owned
files only; detailed bodies + Co-Authored-By trailer.
Worktree clean at 498a916.

Recounts (script files in scratch/parcel-w5readme3/;
commands + logs in the report): 849 = 783 + 66/66
all implemented (COVERAGE = gate inventory); 411,213
committed vectors (line count = runner smoke total);
standard +1,117,504 (917,504 + 200,000, runner
agrees) + 5,505,024 aug-pool leg stated separately;
plants 109/115 at e9c57fb; attr rows 255 -> 273
(two agreeing censuses). Brief figures confirmed;
README stale figures replaced. Two corrections
recorded: RECORD's 138,392 aug subtotal is a raw-line
count (counted: 138,380; totals unaffected), and the
task text's "emsdk" is proven absent - the recorded
Zig 0.17.0 recipe was reused (archive sha256
re-verified b5663f69...).

Site: build_data.py pair_call regex + sampler
exact-shape guard + build.py msf_aug.c (both breaks
watched failing at base first); explog included
(822/849 runnable, sample 1,620/810); 9 augmented
pairs EXCLUDED by single-result shape with the
exclusion printed (index.html, numbers table,
site/README.md), never faked. msf.wasm 770,233 bytes
sha256 4ddb8192..., byte-identical across two builds;
Node replay 1,620/1,620, 0 mismatches; explog/aug
known-answer probes pass; data stamped as-of e9c57fb;
headless Edge DOM shows WASM-ready + e9c57fb status
line. No visual redesign. Gates: smoke PASS,
standard PASS (smoke repeated on the edited tree).

Not done, named: push/merge/Pages (lead; live-page
check after merge); pixel QA and non-Edge browsers;
board budget (RECORD quotes only); one-time
exhaustives quoted, not re-executed. Full detail:
scratch/parcel-w5readme3/report.md (first line READY).
