# Brief: Wave 4 Step 0a - Tier 2 table/inventory seam

Role: lead-seam (lead-owned seam, implemented in a lead-cut
worktree; independent planted verification before merge).
Base: `fe213fd256b54da2a73c57cc02c23e5030cfef3d` (approved SF-1).
Time box: 180 minutes. Ceiling: 900 hand-written lines
(tools + table schema text + docs), generated files and the
mechanical per-row tier/claim appends excluded.

## Authority and scope

SF-1 Sections 3-5 and 8, as approved in SF-1 Section 14. This
parcel is **Step 0a only**: no Tier 2 semantics, no function
bodies, no vectors, no board claim. SF-1 Step 0 is not declared
closed until Step 0b oracle bring-up (MPFR f16/f32 probes and
the CORE-MATH pin/smoke) also lands under its own brief.

## Frozen design decisions

1. `tables/operations.tsv` gains two appended columns, `tier`
   and `claim`; `docs/COVERAGE.tsv` generation appends the same
   two columns. Existing Tier 1 families: `tier=1`,
   `claim=required` ( SF-0 required-set claim). New Step 1
   families: `tier=2`, `claim=C-754`.
2. Generator admission is a closed set at this step:
   tier 1 admits only `required`; tier 2 admits only `C-754`.
   Reserved SF-1 tokens (`C-754-EXC`, `C-ULP`, `C-API`) are
   **refused** until their own seam work exists. Authority
   tokens are validated against the existing closed set
   (`berkeley`, `mpfr-exact`, `project-exact`,
   `project-exact+berkeley-check`, `auto-arith`, `auto-int`).
   Unknown tier/claim/authority aborts generation.
3. Register exactly the SF-1 Step 1 surface as planned,
   homogeneous, wave 4, authority `project-exact`, comparison
   `exact`:
   - Clause 9.6 (sig `minmax`, rounding `none`, flags `yes`):
     `minimum`, `maximum`, `minimum_number`,
     `maximum_number`, `minimum_magnitude`,
     `maximum_magnitude`, `minimum_magnitude_number`,
     `maximum_magnitude_number` (8 names x 3 formats = 24).
   - Clause 9.7 (sig `payload_un`, rounding `none`, flags
     `no`): `get_payload`, `set_payload`,
     `set_payload_signaling` (3 names x 3 formats = 9).
   New sig names are truthful aliases of the existing
   homogeneous-pair / homogeneous-unary expansion shapes; append
   them at the end of the dispatch sig enum to avoid renumbering
   existing sig values. `tables/implemented.tsv` is untouched:
   all 33 Tier 2 rows stay planned.
4. Inventory split replaces run.sh control 9's single equality.
   It prints Tier 1 and Tier 2 registered counts separately,
   names Tier 2 planned rows, and refuses unless Tier 1 is
   exactly 783 implemented of 783. The registered Tier 2 total
   is frozen at 33 for this step (a later lead table expansion
   updates the constant in the same commit, never silently).
   Watched-failing controls, permanent in `tools/run.sh`:
   a Tier 1 COVERAGE row flipped to planned must refuse, and a
   Tier 2 COVERAGE row deleted must refuse.
5. Public-header prelude gains one SF-1 paragraph: Tier 2 rows
   are planned until COVERAGE says implemented and the wave-4
   gate closes; Tier 2 families ship as binary16/32/64 bundles
   or not at all. Per-declaration comments keep today's shape.
6. Provenance rule recorded in `tests/VECTORS.md` if it is not
   already equivalent: one tag family per generator, not per
   function file; the 128-tag cap moves only by seam work that
   re-watches the overflow refusal. No new tags in this parcel.

## Owned files

`tables/operations.tsv`, `tools/gen_tables.py`, `tools/run.sh`,
generated `include/muse_softfloat.h`, `tests/msf_dispatch.h`,
`docs/COVERAGE.tsv` (`src/msf_formats.h` must stay
byte-identical), `tests/VECTORS.md` (rule sentence only),
`docs/metrics/briefs.jsonl` (this brief's row only).

Forbidden: `src/*.c`, `src/*.h` hand edits, `compat/`,
`board/`, `tests/runner.c`, `tables/implemented.tsv`, vectors,
README/RECORD claim text. No pair/vector/stateful shapes, no
CORE-MATH fetch, no MPFR probe work (Step 0b). Nothing with
`cft` in its name is opened, searched, or listed; the IEEE PDF
is not opened; no third-party source is design input.

## Gates (all from the worktree, Git Bash via script files)

- Generator run: 816 instantiations (783 implemented, 33
  planned); drift check byte-identical.
- `bash tools/run.sh smoke` PASS with split inventory printed
  (Tier 1 783/783; Tier 2 0 implemented, 33 planned named).
- `bash tools/run.sh standard` PASS (merge gate; machine may be
  under load - timings recorded, never used as claims).
- Scratch mutant evidence (script file, logs kept): unknown
  claim token aborts the generator; a tier/claim mispairing
  aborts; the two inventory mutants above are refused by the
  permanent controls.
- Independent planted verification (Spark) on the branch diff
  before merge; only (a) regression / (b) wrong answer sends
  back. Merge, RECORD, and push follow only on PASS.

Escalate rather than widen: any need to touch runner semantics,
implemented status, or a new vector shape stops this parcel and
returns to the lead ledger as a design entry.
