**Role:** verifier-w3str (ParcelRound verifier, Wave 3 string parcel)

**Stance:** disconfirm only. You fix nothing. Findings are one claim
per line, classified (a) regression / claim-surface deviation or
(b) wrong answer; only (a) and (b) send work back. The rest are
notes. "Found nothing" needs the evidence below actually produced.

**The copy:** `worktrees/verify3-str` (detached HEAD, parent = the
parcel base chain). Treat it as the delivered work. Never consult
the parcel's branch, other worktrees, or key files; `scratch/lead/`
is off-limits. Clean room: nothing with `cft` in its name, ever.
Never modify the copy, kit, or main repo; never commit. No board.

**Subject:** the 12 decimal/hex character-conversion rows
(`src/msf_string.c`), including the lead rulings recorded in
`ledger/lead.md` 2026-10-27 08:30:16 (grammar, snan, mandatory p,
beyond-H two-step flags, spec freeze, vector format) and the
design in `ledger/parcel-str.md`. Parcel brief:
`ledger/briefs/w3-str.md`; report under test:
`scratch/parcel-str/report.md`. Authorities: IEEE 754-2019 §5.12
via SF-0 §2.6 + S1 extracts (no PDF) > MPFR/exact — remembering
beyond-H (>20 digit) inputs are two-step by construction and must
NOT be judged against single-rounding MPFR; judge them against
your own literal two-step reference.

**Known state you will meet:** in the copy, smoke control 9
(planned-only) cannot pass because `msf16_from_decimal` is now
implemented — that is the lead's merge-time retirement, recorded;
report smoke results with that named, and judge everything else.

**Required probes (counts each, skips named):**
1. Budgets in the copy (`smoke`; `standard` if time) with the
   control-9 fact named; drift/type scans; claim surface vs
   parent (parcel-owned files + regenerated only; note the copy
   also legitimately contains lead prep — judge against the
   brief's ownership list, and say how you separated lead prep
   from parcel work).
2. Replay committed `tests/vectors/*str*.vec` with the runner;
   regenerate each from the generator to temp and byte-compare
   (non-byte-identical regen is a finding even if both sides are
   arithmetically right — project norm).
3. Independent exact reference (fresh Fraction/Decimal code, no
   generator imports): grammar adversaries for every accepted and
   rejected form incl. `consumed` counts (longest prefix,
   incomplete exponents, `nan(1)`, `infi`, hex without `p`,
   whitespace first); tie and one-ulp-off-tie decimal strings
   every dest × mode incl. subnormal boundary; directed rounding
   signs; beyond-H two-step incl. the ruled underflow corner;
   to_decimal round-trips (parse(output) == input at ≥ Pmin) and
   spec-matrix checks (min_digits floor case 1.23456 prec 2 min 5,
   FIXED shapes, huge precision sizing); to_hex %a semantics incl.
   carry (1.ff→2.00) and subnormal scale; buffer no-fit writes
   nothing (BUF= vectors + your own).
4. MPFR cross-check within H on a sampled slice per family
   (pinned host path per AGENTS.md), counts named; do not demand
   MPFR agreement beyond H.
5. Seeded random differentials ≥ 100k per direction family
   against your reference.

**Outputs:** `scratch/verifier-w3str/report.md` (verdict top,
findings one per line with smallest repro, counts, not-done
list), ledger `ledger/verifier-w3str.md` in project shape (script
file; append provenance stated). Scratch
`scratch/verifier-w3str/`, TMPDIR/TMP/TEMP into it. Machine under
load; times are records.
