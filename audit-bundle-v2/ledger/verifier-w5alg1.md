
## 2026-10-28 - verifier-w5alg1: NOT READY (3 wrong-answer + 1 seam-regression finding)

Measured: verified ONLY worktrees/verify5-alg1 (HEAD db941a6,
parent 7c3819c) per ledger/briefs/verify-w5alg1.md; own exact
integer decider from scratch/sf2-algebraic/report.md Sec 3.1,
validated by MPFR cross-decide (25,268 comparisons, 0 mismatches,
Step 0b recipe) + boundary midpoint-square probe (17,595, 0
fails) + committed-vector agreement 3,594/3,595; 0 ties in 577,233
decisions. Copy never modified.

Counts (kernel vs own decider): f16 exhaustive 327,680 total /
158,720 mismatch (all 31,743 positive-finite x5 + -0 x5); f32
volume 100,845 / 50,840; f64 volume 100,845 / 51,195 (same shape;
all negatives match). Copy runner on committed vectors: FAIL x3
(f16 140/1,055; f32 140/1,060; f64 139/1,061). Specials 375
decisions / 15 mismatches, all -0.

(b1) kernel finite-positive wrong all formats/modes: alg_cmp_sq
sign inverted, bit search saturates q to 2^(top+1)-1, sticky
always 1. Smallest: msf16_r_sqrt(0x3C00, te) -> 0x4000/10, want
0x3C00/00. (b2) rSqrt(-0) -> +inf, want -inf (clause paired-sign
cell; executed MPFR gives +inf first-hand, hence fenced).
Smallest: msf16_r_sqrt(0x8000, te) -> 0x7C00/02, want 0xFC00/02.
(a) operations.tsv r_sqrt claim C-ULP (SF-2 pins C-754);
gen_tables.py refuses its own tables, smoke+standard FAIL at
drift. (b3) alg-f64.vec:4 +0/te flags 00, want 02 (regen gives
02; f16/f32 regen stable+clean).

Seam holds: 45 registered / 42 implemented / hypot planned-only
(NULL dispatch, SKIP by name); Tier1 783/783; claims closed in
COVERAGE; unknown-sig + both inventory mutants refused.
Target-compile clean, type scan clean, claim surface 16
owned files, no board files. Full report (NOT READY first line,
paper re-derivation, not-done list):
scratch/verifier-w5alg1/report.md. Scripts 00-20 in
scratch/verifier-w5alg1/ (Git Bash, MSF_PYTHON pinned, ulimit
ceilings); logs in out/.
For: lead
