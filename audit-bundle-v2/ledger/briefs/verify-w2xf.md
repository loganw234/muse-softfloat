**Role:** verifier-w2xf (ParcelRound verifier, Wave 2 cross-format parcel)

**Stance:** disconfirm only. You fix nothing. A finding is one claim
per line, classified (a) regression / claim-surface deviation or
(b) wrong answer; only (a) and (b) send work back. Everything else
is a note. "Found nothing" is an acceptable outcome only with the
evidence below actually produced.

**The copy:** `worktrees/verify2-xf` (detached HEAD; its parent is
base `dd48b08`). Treat it as the parcel's delivered work. Do not
consult the parcel's own branch, other worktrees, or any key files;
`scratch/lead/` is off-limits to you. Clean room: never open,
search, or list anything with `cft` in its name. Never modify the
copy, the kit, or the main repo; never commit. Board is out of
scope.

**Subject:** 126 wave=2 cross-format instantiations (`msf32_*` /
`msf64_*` with at least one binary16 source) claimed implemented in
the copy, as wrappers over landed Wave 1 kernels in `src/msf32.c` /
`src/msf64.c`. Two claims to attack: (1) the new rows are correct
under SINGLE rounding (no convert-first double rounding); (2)
landed Wave 1 behavior is bit-identical (wrappers only). The
parcel's report is at `scratch/parcel-xf/report.md`, its ledger at
`ledger/parcel-xf.md` (incl. a lead ruling on dest-f64 trap shape —
claims to test, not evidence). Brief: `ledger/briefs/w2-xf.md`.
Authority chain: IEEE 754-2019 (via SF-0 + S1 extracts; do not open
the PDF) > Berkeley 3e > exact arithmetic.

**Required probes (report counts for each, skips by name):**
1. Budgets in the copy: `tools/run.sh smoke` (this replays the
   Wave 1 sets — the regression proof), `standard` if time allows;
   inventory, drift, type scan.
2. Claim surface vs base: diff vs parent; only brief-owned files +
   regenerated outputs changed; landed function bodies untouched
   (insertions-only claim is checkable — check it).
3. Independent replay of `tests/vectors/*xf*.vec` and regeneration
   of each from its generator to temp, byte-compared; a directed
   file that does not regenerate byte-identically is a finding
   even if both sides are arithmetically correct (project norm).
4. Berkeley-decided rows (2) level 1 complete; the 24
   berkeley-check comparison rows: re-derive the parcel's
   transform argument yourself or replace it with your own exact
   differential — flag any predicate whose invalid behavior
   (quiet vs signaling) is wrong, with a NaN repro.
5. Your own independent exact reference (fresh code, no generator
   imports): seeded sweeps per dest across all 126 names with
   edge-heavy pools, and independently constructed double-rounding
   discriminators (f64-source→f32-dest convert-first cases; unfused
   FMA cases; evaluate-at-f32→f64 cases). Verify the committed
   traps actually discriminate: a convert-first mutant answer must
   FAIL them.
6. Wrapper-table audit: every DEF/wrapper line's format indices
   against the instantiation name (a source decoded in the wrong
   format is the characteristic defect of this parcel's shape) —
   cover all 126 by reading, and state how many your sweeps
   exercised with operands that would expose a wrong-format decode.

**Outputs:** full report to `scratch/verifier-w2xf/report.md`
(verdict READY or NOT READY at top; findings one per line with
smallest repro vector each; probe counts; explicit not-done list),
then a ledger entry in `ledger/verifier-w2xf.md` (project ledger
shape; stage via script file if needed and say so — append
provenance is part of the record). Scratch:
`scratch/verifier-w2xf/`, TMPDIR/TMP/TEMP into it, script files not
inline heredocs. Machine under load; wall times are records.
