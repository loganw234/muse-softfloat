# Brief: Wave 4 Step 1 - Clause 9.6 min/max + 9.7 payloads (33 rows)

Role: parcel-w4minmax. Base: `8578114a8bfce73173e484f0d345a87a8ba6d532`
(Step 0 closed). Worktree: `worktrees/w4-minmax` (lead-cut;
work only there). Time box: 300 minutes. Ceiling: 3,000
hand-written lines (src + test code), generated files/vectors
excluded. Report: `scratch/parcel-w4minmax/report.md`; ledger:
`ledger/parcel-w4minmax.md` with a design entry **before code**.

## Authority and first action

SF-1 Sections 5, 8, 14; Clause 9 survey Sections 4.1-4.2
(`scratch/tier2-clause9/report.md`, paraphrase of Clauses
9.6/9.7/6.2.1 via S1 - cite clauses, never open the PDF).
First action is the design entry: restate the semantic pins
below in your own table and second-read them against the
survey. Any ambiguity or shared-kernel inadequacy is an
escalation in your ledger, never an edit to lead-owned files
(`src/msf_decode.h`, `src/msf_internal.h`,
`src/msf_roundpack.c`, generator, runner).

## Frozen semantics (SF-1 approval + survey pins)

All 11 names at binary16/32/64 (format parity; one bundle or
none). No rounding anywhere; min/max take flags, payloads never
signal and take none.

9.6 (24 rows): result is an operand selected by value (plain /
Number) or magnitude with the value form as tie-break
(Magnitude). Signed zeros are ordered: -0 is the minimum, +0
the maximum (a deliberate tweak over `msf_cmp_finite`, which
compares zeros equal). Equal values otherwise: **first operand
wins**. Plain forms: any NaN operand delivers per the SF-0 2.5
matrix (`msf_nan_delivery`: first signaling quieted else first
quiet, sign+payload preserved); invalid only from a signaling
operand. Number forms: exactly one NaN operand delivers the
**number**, yet a signaling NaN still signals invalid even when
ignored (do not reuse `msf_nan_delivery` wholesale there); both
NaN deliver per the matrix. No 2008 `minNum`-style aliases.

9.7 (9 rows): operand encoding is the same-format floating
pattern already frozen by the Step 0a table declarations
(SF-1 S6 entry gate). Payload = trailing bits below the quiet
bit (9/22/51 bits). `getPayload`: NaN -> payload as the exact
non-negative integral value in the same format (input sign
ignored); non-NaN -> -1. Setters: admissible non-negative
integral operand builds a **positive** quiet/signaling NaN
with that payload; anything else delivers +0 and signals
nothing - including signaling-NaN input. Admissible sets:
quiet 0..max (0 = the existing default quiet NaN encoding),
signaling 1..max; -0 is admissible-as-0 for the quiet form
only (signaling form: inadmissible, delivers +0). Character
payload suffixes stay out; the string grammar is not reopened.

## Owned files

`src/msf_performat.inc` (format-generic core instantiated by
all three TUs; a new shared `.inc` in the same style is allowed
if the design entry argues it, plus its one-line includes),
`tests/gen_vectors_tier2.py` (fresh), committed vectors under
`tests/vectors/`, `tables/implemented.tsv` (append only),
regenerated outputs, tests/VECTORS.md (new tag rows),
`docs/metrics/briefs.jsonl` (this brief's row only).

Forbidden: generator/runner/tables (operations/formats),
lead-owned shared kernels above, `src/msf_string.c`, compat,
board, `tools/run.sh` (VECS wiring is the lead's at merge),
README/RECORD. Nothing with `cft` in its name; no third-party
source as design input; Berkeley is silent here and MPFR only
corroborates Number-form values on finite/zero/infinity.

## Evidence (project-exact decides; C-754 claim)

- Fresh generator with an independent bit/class reference (no
  imports of shipped generators' expectation logic). One
  provenance family for the generator (`exact-py-t2:*`).
- Committed directed sets: every (class, class, sign,
  magnitude-order) cell with directed NaN payloads for all 8
  min/max names x 3 formats; payload boundaries (0, 1, max,
  max+1 as values, just-below-max integral, subnormals, +/-0,
  infinities, both NaN kinds) for all 3 payload names x 3
  formats. Regeneration byte-identical.
- Generated-at-gate sets (build dir): binary16 payload
  exhaustive over all 65,536 encodings per payload op,
  including `getPayload(setPayload(k)) == k` round-trips and
  `is_signaling` agreement; binary16 min/max second-operand
  sweeps against named boundary first operands; seeded pair
  sweeps for binary32/64. Counts printed in the report.
- Negative controls watched failing (scratch): ignored-sNaN
  invalid stripped; plain/Number swapped on single-qNaN;
  -0/+0 selections swapped; magnitude tie-break corrupted;
  NaN payload altered; quiet bit flipped on a signaling
  setter; `setPayload(0)` expected +0; inadmissible input
  expected NaN; flags token `00` where `--` is required.
- Budgets in the worktree via script files (Git Bash,
  `MSF_PYTHON` pinned to workspace `.venv`): `smoke` and
  `standard` PASS (your committed vectors replayed explicitly
  with the runner + expect-counts until lead wiring); drift
  byte-identical; inventory prints Tier 2 33 implemented.

Implemented appends are all 33 rows at wave 4 or none - a
partial-format or partial-family landing violates parity and
is a send-back. Planted-copy verification follows before merge.
