**Role:** parcel-w5site (owner side parcel: web demo page)

**Deliverable:** a static demo site in `site/` on branch
`wave5-site` (worktree `worktrees/w5-site`, base
`a0acf2a`), deployable to GitHub Pages, plus the README
link line. Time box 600 min. Owner asks: showcase page,
linked from the README, with real interactivity.

**First action:** `read_skill` for `bundled:taste`
(anti-slop preflight) before creating any page file, and
obey it: no purple/blue gradient hero, no gradient
headline text, no identical 3-card grids with icon
tiles, no glassmorphism-everywhere, no emoji icons, no
centered eyebrow-pill hero. A technical-instrument look
fits this project (think bench equipment / lab notebook).
System font stack or one bundled font at most; no CDN
fonts (Pages must work offline-ish; no external requests
at all is the rule - everything vendored in `site/`).

**Content rules (project honesty discipline applies to
marketing copy):** every number on the page must trace to
`docs/RECORD.md`, `docs/COVERAGE.tsv`, or
`docs/metrics/*.jsonl` at your base commit - cite nothing
you cannot point at. Wave 5 in-progress items (exp2/log2/
augmented) must be labelled in-progress or omitted;
`roundTiesToAway`, rSqrt, hypot are landed. Exp2's
inventory at base: 822 instantiations, Tier 2 45/45,
171,423+ committed vectors (recount, don't trust this
brief), plants 75/80, the three silicon workloads with
their hashes/qualifications (KissFFT = one named change,
gated sizes - never "unmodified").

**Interactivity (the center):** try in this order, hard
90-min cap on step 1:
1. **Real library in the browser via WebAssembly.**
   Install a WASM toolchain into scratch only
   (fetch-recorded in your ledger: URL + sha256; nothing
   into the repo except build outputs). Compile the
   repo's own `src/*.c` (the same files the runner and
   RP2040 use - no edits to `src/` for this; your glue
   lives in `site/` or scratch) to `site/msf.wasm` with a
   small exported surface: run one vector line (op token,
   mode, operands as hex) -> result bits + flags. UI:
   format/op/mode selectors, hex + decimal operand entry,
   result with bit-field breakdown (sign/exponent/
   significand coloured by field), flags as labelled
   chips, and a "deal me a committed vector" mode that
   loads a real line from a bundled sample of
   `tests/vectors/` and checks the WASM result against
   it live. Decided-outcome honesty: if WASM works, the
   page may say "the actual library, compiled to
   WebAssembly" - prove it by replaying >=500 bundled
   committed vectors through the WASM build in a build
   log (Node is available) with 0 mismatches.
2. **Fallback if WASM is blocked:** vector-playback
   explorer over a bundled sample of committed vectors
   (same UI shell; results come from the recorded lines,
   and the page must say so plainly - "recorded results
   from the repository's test vectors", never implying
   live computation). Plus the panels below.
Either way, add: an IAS15 panel (what runs on the Pico,
2,001/2,001 hashes, honest speed figure from RECORD -
an animated orbit sketch is allowed only if labelled
"illustration"), a metrics strip generated from
`docs/metrics/*.jsonl` at build time by a committed
script (`site/build_data.py` -> `site/data.json`: plant
score by wave, vector totals, instantiation counts), and
a "how this was verified" section (planted copies,
authorities, board hashes) linking RECORD/studies on
GitHub. No performance claims anywhere - timings may
appear only as recorded facts with units and context.

**Build/deploy shape:** plain HTML/CSS/JS, no framework,
no build-time JS dependencies; `site/build.sh` (or .py)
regenerates data + wasm deterministically from the repo
root; `site/README.md` states the Pages publish steps
(Settings -> Pages -> deploy from branch, `/site` is not
a stock Pages folder: either document the `gh-pages`
branch copy step your script performs into scratch, or
add `.github/workflows/pages.yml` uploading `site/` as
the Pages artifact - pick the Actions route, it is the
stock one). The lead enables Pages at merge; do not
touch repo settings yourself. README change: one link
line under the title block (exact URL
`https://loganw234.github.io/muse-softfloat/`) - that
file is owned for this change only.

**Owned files:** `site/**`, `.github/workflows/pages.yml`,
`README.md` (link line only), `docs/metrics/briefs.jsonl`
(your row). `src/`, `tests/`, tables, docs other than
above: read-only. **Light machine load:** another parcel
is running a multi-hour exhaustive sweep at lowered
priority - keep your own compute light (no parallel
builds beyond 2 jobs), memory ceilings on anything long.

**Verification on your side:** local static serve +
headless check if a browser is available (name what you
used; if none, say so and validate by Node-driven DOM-
free checks of the JS logic + the WASM replay log);
every displayed number spot-checked against its source;
links resolve to repo paths that exist.

**Report:** `scratch/parcel-w5site/report.md` (first line
READY/NOT READY; WASM-or-fallback verdict with the replay
count; what a visitor can do; number-provenance table;
not-done incl. Pages enablement) + `ledger/
parcel-w5site.md` (design before code). Detailed commits
ending the Co-Authored-By trailer. Never push/merge.
Clean room: nothing with `cft` in its name. Structured
complete/evidence/unresolved.
