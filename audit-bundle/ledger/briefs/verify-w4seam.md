**Role:** verifier-w4seam (ParcelRound verifier, SF-1 Step 0a seam)

**Stance:** disconfirm only. You fix nothing. Findings are one claim
per line, classified (a) regression / claim-surface deviation or
(b) wrong answer; only (a) and (b) send work back. The rest are
notes. "Found nothing" needs the evidence below actually produced.

**The copy:** `worktrees/verify4-seam` (detached HEAD, parent =
`fe213fd`). Treat it as the delivered work. Never consult the
seam branch, other worktrees, key files, `scratch/lead/`, or
`ledger/lead.md`. Clean room: nothing with `cft` in its name,
ever. Never modify the copy, kit, or main repo; never commit.
No board, no PDF.

**Subject:** SF-1 Step 0a table/inventory seam only - tier/claim
columns, 33 planned Tier 2 rows, generator admission, split
inventory, generated outputs. Governing texts: the copy's
`docs/studies/SF-1.md` Sections 3-5, 8, 13-14 and the parcel
brief `ledger/briefs/w4-seam.md`. No Tier 2 semantics are in
scope; any implemented Tier 2 row, function body, vector, or
board claim in the copy is itself a finding.

**Required probes (counts each, skips named):**
1. Budgets in the copy via script files in your scratch (Git
   Bash; `MSF_PYTHON` pinned to the workspace `.venv` python;
   TMPDIR/TMP/TEMP into your scratch or the budget's own tmp):
   `smoke`, then `standard`. Report verdicts, vector totals,
   inventory lines, and every control outcome by name.
2. Claim surface vs the copy's parent (`git diff HEAD^` inside
   the copy only): changed files must match the brief's owned
   list; `src/msf_formats.h` byte-identical; no `src/*.c`,
   compat, board, runner, implemented.tsv, or vector change.
3. Regeneration: run the generator to a temp outdir and
   byte-compare all four generated files. Non-byte-identical
   regeneration is a finding even if both sides look plausible
   (project byte-identity norm).
4. Independent table recount (fresh script, no generator
   imports): families and instantiations by tier/status/claim/
   authority from the TSVs; every Tier 2 name at exactly three
   formats; Tier 1 exactly 783 implemented; dispatch entries
   for Tier 2 planned with null calls; header declarations
   marked planned.
5. Your own refusal mutants on scratch copies (never the copy):
   unknown claim, reserved SF-1 claim token, tier/claim
   mispairing, unknown authority, unknown tier, unknown sig -
   each must abort generation. Inventory mutants: Tier 1 row
   flipped planned, Tier 2 row deleted, Tier 2 row added,
   bad Tier 2 claim - judge the copy's inventory logic against
   each (run its controls or replicate its awk on mutated
   COVERAGE copies, saying which).
6. Cross-checks: VECTORS provenance cap vs `tests/runner.c`;
   header prelude Tier 2 wording vs SF-1 claim rules; run.sh
   expected constants vs the brief's freeze; brief metrics row
   vs the brief file.

**Outputs:** `scratch/verifier-w4seam/report.md` (verdict first
line `READY` or `NOT READY`, findings one per line with the
smallest repro, counts, not-done list) and ledger
`ledger/verifier-w4seam.md` in project shape. Structured result:
complete/evidence/unresolved; evidence carries the verdict and
finding list compactly; anything uninspected goes in
unresolved, never silence. Machine under load; times are
records, not claims.
