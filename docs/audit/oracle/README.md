# Audit oracle (2026-10-31)

Independent differential tests written for the external audit in
[`../2026-10-31-audit-report.md`](../2026-10-31-audit-report.md). They
are not part of the project's gate, and they share no code with the
library or its generators.

The references are:

- x86-64 hardware arithmetic: SSE2/FMA3/F16C/AVX-512F under MXCSR
  rounding control, with flags read from MXCSR;
- glibc 2.39 C23 functions;
- MPFR 4.2.

For destinations narrower than binary64, results are computed with
round-to-odd in binary64 and then rounded once, so there is no double
rounding. roundTiesToAway is decided by an exact midpoint test.

```bash
bash docs/audit/oracle/run.sh
```

| Setting | Effect |
|---|---|
| `SCALE=1` (default) | about 1 minute |
| `SCALE=25` | about 250 M checks for `hwdiff` |
| `F16EXH=1` | adds the exhaustive binary16 add/mul/div sweeps (11 minutes or more per operation on 3 threads; div is the slowest) |

Requirements: x86-64 Linux with SSE4.1, FMA3, F16C and AVX-512F, gcc,
python3, and `libmpfr-dev`. Build outputs go to `build/audit-oracle/`,
which is gitignored.

The runner builds a tininess-before-rounding variant of the library and
requires the oracle to report mismatches against it. If the oracle
accepts that variant, the oracle is broken and the run fails.
