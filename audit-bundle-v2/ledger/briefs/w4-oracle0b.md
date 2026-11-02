# Brief: Wave 4 Step 0b - Tier 2 oracle bring-up

Role: study-tier2-oracle0b (scratch evidence work; no repository
writes). Base: `e12492e9fd281dfe90b4c92c46f0c2e518ff7e35`.
Time box: 240 minutes. Ceiling: 0 repository lines; all work in
`scratch/tier2-oracle-0b/` plus `ledger/study-tier2-oracle0b.md`.

## Authority

SF-1 Sections 4 item 5, 6.2, 8 and 14 (Q8 approved); SF-0
Section 4. Step 0a has landed and been verified; Step 0 closes
only when this bring-up is checked by the lead. No Tier 2
vector from any new oracle is trusted before that check.

Clean-room fences (hard): nothing with `cft` in its name is
opened, searched, or listed; the IEEE PDF is not opened; no
third-party implementation source, constants, polynomials, or
proof material is read or used as design input. For CORE-MATH
you may read official project documentation, licence text,
release metadata, directory *listings*, public header/interface
declarations, and build logs, and you may execute built
binaries. You may not open its function `.c` implementations or
worst-case `.wc` contents in this step.

## Part A - MPFR binary16/32 emulation probes (the floor)

MPFR 4.2.2 is installed on the MSYS2 path used by
`scratch/tier2-clause9/oracle_probes.sh` (read that script and
Clause 9 survey Section 5 first). Believed recipe constants to
prove or refute by known answers: binary32 `emin=-148`,
`emax=128`; binary16 `emin=-23`, `emax=16`, each with precision
p (24/11), exponent bounds set, and `mpfr_subnormalize` after
every operation.

Write a fresh C probe (script-file build/run, TMP into your
scratch) printing PASS/FAIL counts and raw values for, at both
formats and in all four MPFR rounding modes where meaningful:

- smallest subnormal exactness (2^-149 / 2^-24) and its half
  (ties-to-even to zero; directed modes to the correct side;
  negative mirror);
- subnormal midpoint directed rounding (1.5 x and 2.5 x the
  smallest subnormal, both signs);
- largest finite exactness and overflow threshold behaviour at
  the first midpoint above it (value delivered, ternary, MPFR
  overflow flag state recorded as MPFR facts only);
- smallest normal exactness and values just below/above it;
- a small set of add/mul/sqrt results cross-decided by exact
  rational arithmetic in Python (your own script), including at
  least one subnormal-result case per format.

Report the exact recipe (precision, emin/emax calls,
subnormalize placement) that passes, or the smallest failing
case if the believed constants are wrong. MPFR flags are never
transcribed as IEEE flags.

## Part B - CORE-MATH pin and smoke (corroboration only)

Start from the official project page cited in the Clause 9
survey (Section 5 / Appendix B) and follow official links only.

1. Pin: identify the current release archive or git commit,
   fetch it into `scratch/oracles/` (never the repo), record
   URL, version/commit, archive SHA-256, licence and licence
   SHA-256, fetch date - as one proposed `fetches.jsonl` row in
   your report, in the existing file's shape.
2. Metadata: from the fetched tree's directory listing only,
   confirm or refute per-function availability for
   `sinpi`/`cospi` (and note `sin`/`cos`, `rsqrt`) at
   binary16/32/64, and list worst-case file existence + sizes
   for the Pi pair without reading their contents.
3. Build/smoke: build only the documented check/test
   executables (or a tiny harness over the public interface)
   needed to execute `sinpi`/`cospi` on this Windows host. If
   the documented build fails here, stop at a priced failure:
   exact commands, first errors from logs, and what a fix would
   cost - do not read implementation files to debug it.
4. If it builds: smoke it against MPFR on regular numbers only
   (its documentation fences specials/flags): directed anchors
   plus a seeded sample per format and mode it claims, counts
   and every disagreement printed; disagreements are reported,
   never adjudicated by the foreign binary.

## Output

`scratch/tier2-oracle-0b/report.md`: verdict per part
(BRING-UP PASS / PRICED FAILURE), the proven MPFR recipe, probe
counts with script/log paths, the CORE-MATH pin row, build
outcome, smoke counts, and an explicit list of what SF-1 Step 2b
may and may not rely on. Ledger in house format. Machine under
load; times are records, not claims. Escalate, do not widen:
any need to read foreign implementation source stops Part B.
