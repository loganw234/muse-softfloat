**Role:** study-sf2-augmented (SF-2 input study, scratch only)

**Question:** design and price Clause 9.5 augmented
arithmetic (`augmentedAddition/Subtraction/Multiplication`,
9 core rows) plus a fresh verdict on Clause 9.4 reductions
(21 rows) and the 9.3-shaped dynamic rounding wrappers -
the three deferred non-math families of SF-1 Sec.7. For
augmented: exact (head, tail) pair semantics, flag table,
API shape fitting this library's explicit-argument core, and
whether an interval-workload speed path honestly benefits
(remove-it test against `board/interval_workload.c` op
counts). No repo changes.

**Sources:** `scratch/S1/` extracts (Clauses 9.3/9.4/9.5;
cite clause numbers only), `muse-softfloat/docs/studies/
SF-1.md` Sec.7 + E5 cost note, `scratch/tier2-clause9/
report.md` (9.4/9.5 sections), the core kernels
(`src/msf_roundpack.c`, `include/muse_softfloat.h` header
shape, `compat/msf_aeabi.{c,h}` per-core state),
`board/interval_workload.c` + `scratch/parcel-w4interval/
report.md` op counts. Never open/search/list anything with
`cft` in its name; no third-party implementation source as
design input (the pair semantics must come from the clause
text, second-read where the survey flagged ambiguity).

**Required content:**
1. Augmented: result-pair definition per clause incl. when
   the tail is signed zero / NaN / infinity, which rounding
   attributes apply (and which the clause forbids), the
   complete flag table (inexact from head? tail? invalid
   cases), exactness proof sketch over the existing wide
   pack (head = RN of exact value, tail = exact residual
   rounded - is the residual always representable?), header
   shape (two outputs - fits which existing operation kind,
   or a new one?), vector/runner format implications.
2. Interval remove-it test: measured op-count delta of the
   shipped catalogue's hot path if augmented replaced the
   current multi-call expansions (execute a host variant in
   scratch; counts, not wall claims).
3. Reductions: restate the survey dispute (core
   exact-round-once vs nowhere); recommend one home with
   reasons, name the claim problem (9.4 has no accuracy
   contract - what would C-754 even assert?), and price only
   if recommendable.
4. Dynamic wrappers: confirm or overturn SF-1's provisional
   ruling (compat-only over per-core state, invalid enum =
   ignore-write); price the compat implementation + unit
   gate; name what would earn them (IAS15? future workload?)
   or keep deferred.
5. Recommendation order for SF-2 with hours per family and
   stop conditions.

**Outputs:** `scratch/sf2-augmented/report.md` (first line:
GO/NO-GO per family) and `ledger/study-sf2-augmented.md`.
Structured complete/evidence/unresolved. Script files for
any run (Git Bash, MSF_PYTHON pinned, TMP in your scratch).
