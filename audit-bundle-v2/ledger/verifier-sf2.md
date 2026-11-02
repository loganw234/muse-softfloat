# Ledger: verifier-sf2

Role: verifier-sf2 (ParcelRound verifier, SF-2 draft). Brief:
`ledger/briefs/verify-sf2.md`, obeyed exactly.

Copy: `worktrees/verify-sf2` (read-only; unmodified). Verdict object:
`docs/studies/SF-2.md` as delivered there. Authorities read: the four
input studies in full (`scratch/sf2-{attribute,algebraic,explog,
augmented}/report.md`); the copy's `docs/studies/SF-0.md` (partial),
`docs/studies/SF-1.md` (Secs. 0/2/7/8/9/10/11/14), `docs/COVERAGE.tsv`
(recomputed: 822 implemented = 783 tier 1 + 39 tier 2; 255 attr rows),
`docs/RECORD.md` (head), `src/msf_internal.h`, `src/msf_roundpack.c`,
`src/msf_string.c`, `src/msf_math.c` (targeted), `tests/VECTORS.md`
(ta token), `tools/run.sh` (presence). Never consulted: delivery
branch/worktree, other worktrees, keys, `scratch/lead/`, other ledger
files, anything with `cft` in its name.

Verdict: **FAIL** — see `scratch/verifier-sf2/report.md` (first line
FAIL). Two hard contradictions plus three lesser findings:

- F1: Sec.5 "616,754 to 594,666 (-78.4%)" — study says 394,666;
  594,666 breaks the cited percentage and delta (augmented Sec.2/5).
- F2: Sec.5 pins P1 at "R1 (underflow not raised)" — in the study R1
  raises and R2 (recommended) does not; Sec.9 correctly says R2, so
  Sec.5 contradicts Sec.9 (augmented Sec.1.3).
- F3: Sec.2 "pack has no ties-to-away mode yet; internal mode 4
  added" — copy already has mode 4 + pack arms; only the public enum
  and string cases are owed (attribute Sec.1.1).
- F4: Sec.2 "MPFR-RNDA/exact elsewhere" drops the study's RNDNA
  prohibition, emin fence, and trig/sqrt relabel + Niven stop
  condition (attribute Sec.2.2/4).
- F5 (minor): Sec.4 "4.6x the exp2 demand" misattributes the
  programme-wide headroom denominator (explog Sec.6.1).

Counts and price sums recomputed and all hold (822 + 27 = 855;
0/6/12/9 steps; 28-44+seam, 95-130, 7-10 h bands). Deferral list,
fences (rSqrt(-0), hypot sNaN, F1/H1 scoping), string-trap (2 cases),
roundToOdd nonexistence, C-754 token, parity, and sequencing all
traced clean. Under-specification list (8 items) and not-done list
(4 items) in the report. Margin/probe figures verified by
transcription only, not re-execution.
