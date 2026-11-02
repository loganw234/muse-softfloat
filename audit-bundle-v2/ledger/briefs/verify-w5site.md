**Role:** verifier-w5site (ParcelRound verifier, demo site)

**Stance:** disconfirm only. Findings (a) a page claim the
repo contradicts, (b) wrong behavior in the instrument
(flag decode, result display, recorded-vs-live honesty),
(c) a deploy/link break.

**Copy:** `worktrees/verify5-site` (detached HEAD, parent
`a0acf2a`). Never consult the parcel branch/worktree,
other worktrees, keys, `scratch/lead/`,
`scratch/parcel-w5site/`, or `ledger/lead.md`. Governing:
this brief, the parcel ledger, the copy's docs (RECORD,
COVERAGE, README, metrics). Clean room: nothing with
`cft` in its name, ever. Never modify the copy. Light
machine load (another sweep owns the box): single-
threaded checks, no parallel builds.

**Required probes (counts each; skips named):**
1. WASM honesty: replay the bundled sample through the
   copy's `site/msf.wasm` under Node yourself (count +
   mismatches printed); known-answer probes incl. a
   te/ta tie pair and a flag-raising op; flag chips vs
   the header's bit values (read `include/
   muse_softfloat.h`).
2. Every displayed number traced: instantiations from
   COVERAGE, vector total by recount, plants from
   plants.jsonl (by-wave too), workload facts vs RECORD
   (IAS15, interval, KissFFT incl. "unmodified" wording
   anywhere and the gated sizes), in-progress labelling
   vs COVERAGE implemented status.
3. Degraded mode: with WASM blocked/renamed in your
   scratch copy of the site, the page must say recorded
   results are recorded (exercise it; static reasoning
   does not count).
4. Deploy shape: pages.yml uploads `site/` correctly
   (paths, permissions); README live URL matches the
   repo's Pages address for this repo name exactly;
   all internal links resolve inside the copy; no
   external requests (grep the site for http(s) srcs).
5. Regeneration: `site/build_data.py` (and build.py if
   present) rerun in scratch produces byte-identical
   data.json (wasm rebuild may be skipped for load -
   name it); claim surface vs parent = brief-owned files.

**Outputs:** `scratch/verifier-w5site/report.md` (first
line READY/NOT READY; replay count; per-claim table;
findings with file refs; not-done) and
`ledger/verifier-w5site.md`. Structured
complete/evidence/unresolved.
