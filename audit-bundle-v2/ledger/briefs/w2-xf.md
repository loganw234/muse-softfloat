**Role:** parcel-xf (cross-format parcel, Wave 2)

**Authorization:** Ledger: `ledger/README.md`. Standing rules:
`<repo>/AGENTS.md`. The study: `muse-softfloat/docs/studies/SF-0.md`
(§2 semantics, §3 organization, §4 evidence, §5 discipline, §7 wave
map). Authority chain: IEEE 754-2019 > pinned Berkeley SoftFloat 3e >
MPFR/exact rational. Your clause sources are SF-0 and the S1 survey
`scratch/S1/report.md` (its clause extracts in `scratch/S1/extract/`
may be READ for wording; never copy standard text into committed
files — cite clause numbers only). Do not open the PDF; escalate
clause questions. Clean room: never open, search, or list anything
with `cft` in its name; no third-party softfloat source is read for
design — algorithm mandates below are the lead's, from SF-0 §3.2,
`docs/WIDTHS.md`, and the landed Wave 1 parcels (`src/msf32.c`,
`src/msf64.c` at base — your work extends these files; read them).

**Deliverable:** Every wave-2 cross-format instantiation in the
binary32/binary64 files implemented and gated: `docs/COVERAGE.tsv`
rows with wave=2 whose name starts `msf32_` or `msf64_` —
**126 instantiations** (63 per dest file: add/sub/mul/div/fma/
comparisons etc. with at least one binary16 source, dest f32 or
f64). The full name list is the coverage file filtered as stated;
if your count differs, escalate before coding. Authorities per
row: mpfr-exact 80, project-exact+berkeley-check 24,
project-exact 20, berkeley 2.

**The load-bearing rule:** these instantiations compute the EXACT
operation on the exact source values and round ONCE to the dest.
Converting a source to the dest format first and then operating is
a double rounding and is wrong wherever the conversion is inexact
(f64 source → f32 dest is the live case; f16/f32 sources widen to
f64 exactly but the operation must still be exact before the
single pack). Decode every source exactly (sig×2^exp via
`msf_decode`), compute exactly over `msf_u128`, pack once. Your
design entry must name, per operation family, why no intermediate
rounding exists. NaN delivery order follows operand position per
SF-0 §2.5 regardless of source format (first signaling, quieted,
wins; payload mapped into the DEST format by field shift,
truncate-to-default applies at the dest). Comparison predicates
compare exact values cross-format (`msf_cmp_finite` already does).

**Base:** the pushed main tip including the lead prep commit (your
spawn prompt names the exact SHA). Worktree: `worktrees/w2-xf`
(branch `w2-xf`), cut by the lead. Time box: **300 minutes** wall
from your first ledger entry; at 240, post an honest checkpoint.
Scope ceiling: **3,000 hand-written lines** (src + your test code;
generated files and vector data excluded; committed vector files
≤ 1 MB total). Escalate rather than exceed. A sibling parcel
(parcel-f16) runs concurrently in `src/msf16.c` only — no file
overlap with you; do not touch its files or worktree.

**Design first (no hard stop):** before writing code, append your
design entry to `ledger/parcel-xf.md`: per-operation special-value
tables (NaN/∞/±0/finite per Clause 6–7, flags, signed zeros), the
no-double-rounding argument per family, and how you reuse or
generalize the Wave 1 kernels in msf32.c/msf64.c without changing
any landed instantiation's behavior. If a mandate cannot be built
as specified, objection + urgent BEFORE coding around it.

**Files you own:** `src/msf32.c`, `src/msf64.c` (extend; landed
Wave 1 instantiations must stay bit-identical — your smoke +
directed replays are the regression proof);
`tests/gen_vectors_xf.py` (new); `tests/vectors/*xf*.vec` (new);
`tables/implemented.tsv` (append ONLY your rows, at the end, LF);
regenerated outputs of `tools/gen_tables.py`. Everything else is
off-limits — especially `src/msf16.c` (sibling parcel), the shared
kernels, `tools/`, `tests/runner.c`, existing generators,
`board/`, `compat/`, `docs/`. A kernel that is inadequate is an
escalation, not an edit. Never push; never merge; commit in your
worktree with detailed bodies ending
`Co-Authored-By: Muse Code (muse-wonder-full-1.0) <noreply@meta.ai>`.

**Your first action — test the escalation channel:** write
`ledger/urgent/parcel-xf-test.md` (one line: channel test + start
time), then the design entry. Escalations: new file in
`ledger/urgent/` with question + evidence; keep working other
fronts. Corrections to this brief: ledger prose in
`ledger/parcel-xf.md` headed `## What this brief got wrong`.
**Scratch:** `scratch/parcel-xf/` (create it). Script files for
bash work, TMPDIR/TMP/TEMP into it (AGENTS.md ## What bites).

**Tests (your gate; report every count by provenance):**
1. `tools/run.sh smoke` green in your worktree (regression over all
   Wave 1 vectors — this is your bit-identity proof for landed
   rows), incl. symbol/type scans and drift.
2. Berkeley-decided rows: `tests/berkeley_ingest.py` into
   `build/w2/`, level 1 complete every applicable mode. The
   project-exact+berkeley-check rows (24): Berkeley cross-check at
   level 1 where a generator exists, named where none does.
   Berkeley `eq` is QUIET (Wave 1 ruling).
3. Exact sets from your own `tests/gen_vectors_xf.py` (independent
   Fraction references; patterns from the f32/f64 generators, do
   not edit them): committed directed files for every row,
   including deliberate double-rounding traps — cases where
   convert-then-operate and exact-then-round differ, constructed
   and counted (at least one per arithmetic family per dest);
   seeded ≥ 300k sweeps per dest into build/ (not committed),
   operand pools mixing all three formats' edge encodings
   (subnormals, ties at both formats' boundaries, NaN payloads
   that truncate). Every instantiation you claim appears in at
   least one set.
4. Negative controls demonstrated refused (report, with logs):
   one flipped result bit in a committed directed file; one
   double-rounding trap vector whose expectation you flip to the
   convert-first answer — your implementation must FAIL it (proof
   the trap discriminates); smoke's planned-only control still
   refused.

**Reporting and verdicts:** full report FIRST to
`scratch/parcel-xf/report.md` (every run: command + counts +
outcome; skips by name), then your ledger entry (stage the body in
scratch if the ledger tool refuses, and say so). READY means: all
126 rows appended and regenerated clean, test groups green with
counts, controls demonstrated, no off-limits file touched,
worktree clean but for your commits. Report gaps by name. If you
stop at a checkpoint, say READY or NOT READY plainly and write the
report for the regater who continues.
