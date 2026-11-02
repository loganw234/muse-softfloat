READY

# parcel-w4minmax report: SF-1 Step 1, Clause 9.6 min/max + 9.7 payloads (33 rows)

Branch `wave4-minmax` in `worktrees/w4-minmax`, base
`8578114a8bfce73173e484f0d345a87a8ba6d532`. Brief:
`ledger/briefs/w4-minmax.md`; design entry before code in
`ledger/parcel-w4minmax.md` (2026-10-27 17:11:32 -0700),
second-read against `scratch/tier2-clause9/report.md` 4.1-4.2.
Nothing with `cft` in its name was opened, searched, or listed;
the IEEE PDF was not opened; no board; no third-party
implementation source as design input.

## Design summary

All 33 rows implemented format-generically in the owned
`src/msf_performat.inc` (instantiated by the binary16/32/64
TUs; no TU or lead-owned file edited, no escalation needed -
`msf_decode`, `msf_nan_delivery`, `msf_cmp_finite`, and the
u128 helpers proved sufficient). No rounding anywhere.

- 9.6 (24 rows, flags, invalid only): one `minmax_core`
  (want_min, by_magnitude, is_number) behind the 8 names.
  Value order via infinities + `msf_cmp_finite` with the
  both-zero tweak (-0 minimum, +0 maximum); magnitude order
  via sign-cleared encodings with the value form as
  tie-break; equal values deliver the first operand. Plain
  forms deliver any NaN via the SF-0 2.5 matrix
  (`msf_nan_delivery`); Number forms deliver the number for a
  single NaN (signaling still signals invalid, raised by the
  core itself) and the matrix result for two NaNs.
- 9.7 (9 rows, no flags, never signal): payload = trailing
  bits below the quiet bit (9/22/51 bits). `get_payload`
  encodes the payload as an exact non-negative integer
  (sign ignored; -1 for non-NaN) built from the generated
  format constants. Setters test integrality/range on the
  decoded exact `sig*2^exp` (quiet 0..max, signaling 1..max,
  -0 admissible-as-0 for quiet only), build a positive NaN
  (quiet 0 = `MSF_F*_DEFAULT_QNAN`), and deliver +0 for
  anything else, signaling-NaN input included.

Fresh `tests/gen_vectors_tier2.py` (450 lines; provenance
family `exact-py-t2:*`): an independent bit/class reference
deciding finite value/magnitude on exact rationals; no
imports of shipped generators' expectation logic.

## Gate counts (all measured in this worktree)

Committed directed vectors (regeneration byte-identical):
`minmax-f16/f32/f64.vec` 5,832 each (27-operand class/sign/
magnitude pool, all ordered pairs x 8 names, directed qNaN/
sNaN payloads both signs) + `payload-f16/f32/f64.vec` 102
each (0, 1, max-1, max, max+1, large integral, fractional,
subnormals, +-0, +-inf, both NaN kinds x 3 names). All 33
names appear. Replay with `--expect-counts`: 17,802 passed,
0 failed (`exact-py-t2:directed-minmax` 17,496,
`exact-py-t2:directed-payload` 306).

Generated-at-gate sets (build dir, replayed exact):

- binary16 payload exhaustive: 197,631 passed = 65,536
  encodings x 3 payload ops (196,608) + 1,023
  `is_signaling` cases on every setter-result encoding.
  Reference round-trips asserted at generation:
  `getPayload(setPayload(k)) == k` for 512 values,
  signaling form for 511; the C composition holds
  transitively through these sets.
- binary16 min/max second-operand sweeps: 4,194,304 passed
  = 8 named boundary first operands (-inf, -1, -0, +0, +1,
  +inf, +qNaN(pattern), -sNaN(pattern)) x 65,536 second
  operands x 8 names.
- seeded binary32/64 sweeps (seed 20261027): 288,000 passed
  = per format 12,000 class-weighted pairs x 8 names +
  12,000 encodings x 3 payload names + 4,000
  integral-focused payload encodings x 3 names.

Combined Tier 2 replay with the standard-budget runner and
expect-counts: 4,697,737 passed, 0 failed/malformed/skipped.

Negative controls (scratch, each watched failing; 10
hand-written positive counterparts pass 10/10): ignored-sNaN
invalid stripped; plain/Number swapped on single-qNaN;
-0/+0 selections swapped; magnitude tie-break corrupted;
NaN payload altered; quiet bit flipped on a signaling
setter; `setPayload(0)` expected +0; inadmissible input
(-1, signaling NaN) expected NaN; flags token `00` where `--`
is required (refused as malformed). 9/9 refused.

Budgets via script files under Git Bash, `MSF_PYTHON` pinned
to the workspace `.venv`: `smoke` PASS 18s (committed sets
85,148 passed; drift, symbol/type scans, all permanent
controls green); `standard` PASS 45s (binary16 exhaustive +
pack sweep 1,117,504 passed). Inventory in both budgets:
`tier1 783 implemented of 783; tier2 33 implemented,
0 planned, 33 registered; bad rows 0`. Drift/regeneration:
4 generated files and all 6 committed vector files
byte-identical on regeneration (`cmp` clean).

`tables/implemented.tsv`: all 33 rows appended at wave 4
(none partial). Hand-written lines: `src/msf_performat.inc`
+226/-5 and `tests/gen_vectors_tier2.py` 450, plus 5 tag rows
in `tests/VECTORS.md` and 1 row in `docs/metrics/briefs.jsonl`
- far inside the 3,000 ceiling.

## Not done

- `tools/run.sh` VECS wiring for the 6 new vector files is
  the lead's at merge (forbidden file here); until then the
  committed sets are replayed explicitly as above.
- Planted-copy verification: lead, before merge (per brief).
- Board replay: not run (brief: no board).
- MPFR corroboration of Number-form values: not re-run in
  this parcel; the brief fences it as corroboration only
  (survey probed it), and the project-exact sets above are
  the deciding evidence.
- Exhaustive binary16 ordered pairs (2^32 per name) not run;
  the brief's gate is the boundary-first sweeps + directed
  class cells run above.
- Never pushed or merged.
