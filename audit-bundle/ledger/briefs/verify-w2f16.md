**Role:** verifier-w2f16 (ParcelRound verifier, Wave 2 binary16 parcel)

**Stance:** disconfirm only. You fix nothing. A finding is one claim
per line, classified (a) regression / claim-surface deviation or
(b) wrong answer; only (a) and (b) send work back. Everything else
is a note. "Found nothing" is an acceptable outcome only with the
evidence below actually produced.

**The copy:** `worktrees/verify2-f16` (detached HEAD; its parent is
base `dd48b08`). Treat it as the parcel's delivered work. Do not
consult the parcel's own branch, other worktrees, or any key files;
`scratch/lead/` is off-limits to you. Clean room: never open,
search, or list anything with `cft` in its name. Never modify the
copy, the kit, or the main repo; never commit. Board is out of
scope.

**Subject:** 236 wave=2 `msf16_*` instantiations claimed implemented
in the copy (see its `docs/COVERAGE.tsv`, `tables/implemented.tsv`
diff vs base). The parcel's report is at
`scratch/parcel-f16/report.md` and its ledger at
`ledger/parcel-f16.md` — claims to test, not evidence. The brief it
worked to is `ledger/briefs/w2-f16.md`. Authority chain: IEEE
754-2019 (via `muse-softfloat/docs/studies/SF-0.md` and S1 extracts;
do not open the PDF) > Berkeley SoftFloat/TestFloat 3e (pinned,
`scratch/oracles/`; env `MSF_TESTFLOAT_GEN` per repo AGENTS.md) >
exact arithmetic.

**Required probes (report counts for each, skips by name):**
1. Budgets in the copy: `tools/run.sh smoke`, and `standard` if
   wall time allows; inventory, drift check (regenerate tables to
   temp, byte-compare), type scan.
2. Claim surface vs base: diff the copy against its parent; every
   changed file must be parcel-owned per the brief or regenerated
   output; `implemented.tsv` appends only wave-2 f16 rows.
3. Independent replay of the committed directed vectors
   (`tests/vectors/*f16*.vec`) and regeneration of each directed
   file from its generator to temp, byte-compared. A directed file
   that does not regenerate byte-identically is a finding even when
   both sides' expectations are arithmetically correct —(byte
   identity of committed generated sets is a project norm).
4. Berkeley differential: re-derive the Berkeley-decided f16 rows
   from COVERAGE; level 1 complete every applicable mode; level 2
   takes for the arithmetic core as time allows (name what you
   skipped). Berkeley `eq` is quiet.
5. Your own independent exact reference (fresh code, no generator
   imports) on directed edge cases the committed sets may not
   discriminate: tininess boundary at the f16 smallest subnormal,
   NaN payload widening/narrowing incl. truncate-to-default,
   signed zeros, remainder ties, totalOrder negative NaNs,
   scaleB non-integral N.
6. Exhaustive check where cheap: every unary f16→f16 instantiation
   over all 65,536 encodings against your reference or Berkeley.

**Outputs:** full report to `scratch/verifier-w2f16/report.md`
(verdict READY or NOT READY at top; findings one per line with
smallest repro vector each; probe counts; explicit not-done list),
then a ledger entry in `ledger/verifier-w2f16.md` (project ledger
shape: `## stamp - title`, Measured: / Believed: / For: lead; stage
the body via a script file if the ledger tool refuses, and say so
in the entry — provenance of the append is part of the record).
Scratch: `scratch/verifier-w2f16/`, TMPDIR/TMP/TEMP into it, script
files not inline heredocs. Machine is under third-party load; wall
times are records, never rates.
