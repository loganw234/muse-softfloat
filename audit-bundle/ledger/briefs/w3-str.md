**Role:** parcel-str (decimal/hex character conversions, Wave 3)

**Authorization:** Ledger: `ledger/README.md`. Standing rules:
`<repo>/AGENTS.md`. Study: `muse-softfloat/docs/studies/SF-0.md`
(**Section 2.6 is your specification**, H = 20; read it and §4's
decimal oracle discussion in full). Authority chain: IEEE 754-2019
§5.12 (via SF-0 + S1 extracts; do not open the PDF; escalate clause
questions) > MPFR/exact rational (your rows are mpfr-exact).
Clean room: never open, search, or list anything with `cft` in its
name; no third-party conversion source (no Grisu/Ryu/Eisel-Lemire
code or tables copied) — algorithms are exact big-integer
arithmetic of your own construction over `msf_u128` and your own
wider accumulators inside your TU.

**Deliverable:** the 12 wave=3 rows (`docs/COVERAGE.tsv`):
`msf{16,32,64}_from_decimal`, `_to_decimal`, `_from_hex`,
`_to_hex`, at the header's signatures (`include/muse_softfloat.h`:
`msf_decimal_spec_t`, `msf_hex_spec_t`, `MSF_DECIMAL_H 20`).
Correct rounding per §5.12 within H=20 digits; correct flags
(overflow/underflow-tininess-after/invalid/inexact per the landed
kernel semantics — route final rounding through `msf_pack_generic`
wherever the exact value is in hand as sig×2^exp); `consumed`
semantics and malformed-input behavior exactly as SF-0 §2.6
specifies (design entry restates them; anything §2.6 leaves open
is an escalation BEFORE coding, not a choice).

**Base:** `548a1b9` (pushed main; spawn prompt has the full SHA).
Worktree: `worktrees/w3-str` (branch `w3-str`), cut by the lead.
Time box: **360 minutes** from your first ledger entry; checkpoint
at 300. Scope ceiling: **3,500 hand-written lines** (src + test
code; vectors excluded; committed vectors ≤ 1 MB).

**Design first (hard content requirements):** design entry in
`ledger/parcel-str.md` BEFORE code, covering: grammar accepted
(§5.12.1 external character sequences: signs, inf/infinity, nan
with payload syntax, decimal and hex forms, exponent syntax) with
per-form `consumed`/invalid outcomes; the exact conversion
algorithms both directions incl. how correct rounding is decided
at H=20 (exact remainder comparison, no floating point anywhere);
to_decimal style handling (scientific vs fixed per spec struct,
precision semantics, shortest/exact-enough behavior if §2.6 names
one, buffer-too-small behavior + return value); hex output
precision < 0 = exact-enough per header comment; and YOUR PROPOSED
VECTOR LINE FORMAT for string ops (the runner has no string shape
yet — propose tokens for input string, expected output string, and
consumed count; the lead rules on it in the ledger and implements
runner support on main for you to merge; until then gate with a
scratch C harness).

**Files you own:** `src/msf_string.c` (new TU — all 12
implementations + your internal helpers; if the build needs it
added to a file list somewhere off-limits, escalate); your header
companion if needed as `src/msf_string.h` internal-only;
`tests/gen_vectors_str.py` (new); `tests/vectors/*str*.vec` (new,
in the ruled format); `tables/implemented.tsv` (append only your
12 rows, LF); regenerated outputs. Everything else off-limits —
especially shared kernels, `tests/runner.c` (lead wires your
format), `tools/`, `board/`, `compat/`, `docs/`. Inadequate kernel
= escalation, not an edit. Never push/merge; detailed commit
bodies ending `Co-Authored-By: Muse Code (muse-wonder-full-1.0)
<noreply@meta.ai>`.

**First action:** escalation test `ledger/urgent/parcel-str-test.md`,
then the design entry. Corrections to this brief under
`## What this brief got wrong` in your ledger. Scratch:
`scratch/parcel-str/`, script files, TMPDIR/TMP/TEMP into it.

**Tests (report every count by provenance):**
1. `tools/run.sh smoke` green (regression; your TU must join the
   host builds the budgets already perform — if a build file list
   must change and it's off-limits, escalate immediately).
2. Exact-reference differentials (independent Fraction/Decimal
   references in YOUR generator; MPFR via the pinned host path
   where it adds authority — name counts per oracle):
   from_decimal: grammar torture (every §5.12.1 form + malformed
   near-misses with consumed counts), exact-tie and just-off-tie
   decimal strings at all dest precisions and all 5 rounding
   modes, subnormal-boundary decimals, huge/tiny exponents,
   ≥ 200k seeded random decimal strings per dest.
   to_decimal: exhaustive f16 (65,536) at several precisions/styles
   with round-trip property (parse(output) == input at precision
   ≥ Pmin); seeded f32/f64 ≥ 200k with round-trip; shortest-form
   claims only where you prove them.
   hex both directions: exact by construction oracles; precision
   edge cases; round-trip properties.
3. Negative controls demonstrated: one flipped expected digit in a
   committed vector refused; one wrong `consumed` expectation
   refused; a deliberately truncating (not correctly rounded)
   mutation in your scratch harness failing the tie sets (name +
   revert).

**Reporting:** `scratch/parcel-str/report.md` first (every count,
skips by name, grammar decisions table), then ledger close READY
or NOT READY with gaps named. If SF-0 §2.6 under-specifies a
behavior that blocks you, that is an escalation with options, not
a silent pick.
