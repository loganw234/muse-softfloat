**Role:** study-sf2-algebraic (SF-2 input study, scratch only)

**Question:** design and price the algebraic Clause 9.2
bundle - `rSqrt`, `hypot`, `rootn`, `pown`, `compound` - as
three-format parcels (15 core rows): exact-decision kernel
shapes over the existing wide pack machinery, complete
specials from Clause 9.2.1, WIDTHS additions, vector
authorities and volumes per format, and a parcel split with
worked-hour estimates. The owner has authorised starting on
the deferred families; this study feeds SF-2. No repo changes.

**Sources (read as governing):** `muse-softfloat/docs/
studies/SF-1.md` Sec.7 + survey ranking, `scratch/
tier2-clause9/report.md` Sec.4.6 (ALG rows: ranks 1-4),
`scratch/S1/` extracts (Clause text extracts; cite clause
numbers, never quote beyond a few words), the existing core
(`src/msf_roundpack.c`, `src/msf_wide.c`, sqrt/div kernels in
`src/msf{16,32,64}.c`, `docs/WIDTHS.md`), and MPFR 4.2.2 as an
executed probe. Never open/search/list anything with `cft`
in its name. No third-party implementation source as design
input - your designs derive from the standard text + exact
integer arithmetic. CORE-MATH may be executed as an oracle
probe only (recipes and the `cr_cospif` fence are in
`scratch/tier2-oracle-0b/report.md`).

**Required content:**
1. Per function: exact decision procedure (integer
   comparisons / remainder evidence) at each format, max
   widths (audit against `docs/WIDTHS.md`; name every new
   width), degenerate branches for huge/tiny operands and
   `|n|` extremes (pown/rootn/compound), tie-attainability
   analysis (pown/compound can hit midpoints exactly - prove
   the tie path).
2. Complete specials tables per Clause 9.2.1 (NaN payloads,
   signed zeros, infinites, invalid/divideByZero cases,
   hypot's inf-over-NaN precedence), each cell traceable to a
   clause/extract line.
3. Oracle recipes proven by execution: MPFR probes incl.
   `emin/emax` recipes per format (reuse the Step 0b pattern)
   and a small exhaustive/self-check run at binary16 for at
   least `rSqrt` (your prototype decision code in scratch vs
   MPFR on all encodings x 4 modes, count printed).
4. Inventory shape: operation-family kinds needed
   (homogeneous unary, homogeneous binary, float-int),
   proposed `operations.tsv` rows and manifest counts, claim
   token (C-754), committed-vector volumes per format in the
   project's idiom.
5. Parcel split + price: order, dependencies on lead-owned
   kernels (new pack entry points?), hours per parcel, risks
   and stop conditions. Flag anything that should stay
   deferred.

**Outputs:** `scratch/sf2-algebraic/report.md` (design +
tables + measured probe counts; first line the bundle's
one-line verdict GO/NO-GO per function) and
`ledger/study-sf2-algebraic.md` (Measured/Believed/For).
Structured complete/evidence/unresolved; name every readout
you skipped. Script files for runs (Git Bash, MSF_PYTHON
pinned to workspace `.venv`, TMP in your scratch).
