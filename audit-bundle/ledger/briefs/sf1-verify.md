# Brief: independent verification of SF-1 (Tier 2 study)

Role: verifier-sf1. Model: muse-spark-1.3. Read-only on the
repository and board. Writes allowed only to
`scratch/sf1-verify/` and `ledger/verifier-sf1.md`.

## Target

`muse-softfloat/docs/studies/SF-1.md` as it stands in the
working tree (uncommitted, 771 lines at hand-off) on base
`32dac7d`. SF-1 is a draft study, revised after the owner's
2026-10-27 format-parity direction (the first verification run
was stopped before verdict; you verify the revised text only):
seam-first Tier 2 prefix, interval geometry earning Clause 9.6
minimum/maximum in the semantics-owning sense, KissFFT earning
the binary64 trig pair only under runtime twiddle generation
(Fork A sin/cos vs Fork B sinPi/cosPi) with binary16/32 as
parity-mandated matching rows, everything else deferred by
name. Every added family is a binary16+32+64 bundle or is not
added.

## Must read before judging

- SF-1 in full.
- The four source surveys in full:
  `scratch/tier2-kissfft/report.md`,
  `scratch/tier2-interval/report.md`,
  `scratch/tier2-clause9/report.md`,
  `scratch/tier2-architecture/report.md`.
- `muse-softfloat/docs/studies/SF-0.md` Sections 2.7, 3, 4, 5,
  7, 8, 11; `docs/RECORD.md` closing sections; `AGENTS.md`.
- Spot-open any repository file SF-1 makes a factual claim
  about (tables, generator, runner, compat, board harness) -
  a claim about code is verified against code, not prose.

## Verification duties

1. **Fidelity of restated evidence.** Every load-bearing number
   or measured claim SF-1 restates from a survey must match the
   survey: 180+5 surface; 33 = 24+9 and the 6/27 split; 249
   attr rows; 43/128 provenance; KissFFT call census and
   twiddle counts (1,022/1,024; 620/1,024; 590/1,024; 3/4 of
   2,048); interval E1-E8 numbers SF-1 quotes; 783 Tier 1 rows;
   multi-board 201/201 and ~1.5003 steps/s. A wrong restatement
   is a (b) wrong answer.
2. **Arithmetic closes.** Tier 2 accounting must sum: authorised
   prefix (33 + 6 = 39) + deferred (9 augmented, 21 reductions,
   111 other math rows = 141) = 180. Flag any double-count, gap,
   or row count that is not a multiple-of-3 bundle where a core
   family is meant (global wrapper/attribute items excepted and
   must be identified as such).
3. **Earning logic not overstated, parity not inflated.** Check
   SF-1 never claims a workload earns what its survey rejected
   (KissFFT: only the binary64 trig pair, only under runtime
   generation; interval: at most 9.6 semantics-owning at
   f32/f64). Check parity-mandated rows (binary16/32 trig,
   binary16 min/max) and compliance-breadth rows are labelled
   unearned everywhere counts appear, and that no family is
   authorised, merged, priced, gated, or claimed at fewer than
   all three formats (owner format-parity rule, 2026-10-27).
   A surviving single-format addition or partial-bundle claim
   path is a (b) wrong answer.
4. **Claim honesty.** Fork A/B public-wording sections must not
   promise "correctly rounded twiddles" ambiguously, partial-
   domain trig under conforming names, tolerance results as
   byte-identical, or board claims for unclosed steps. Claim
   tokens (C-754 etc.) must be used consistently.
5. **Seam feasibility.** Section 4's seam must be consistent
   with the actual generator/runner/control-9 code as read -
   no invented mechanism presented as existing, no existing
   blocker omitted that the architecture survey named.
6. **Decision coverage.** SF-1 Section 10 Q1-Q10 must cover, or
   consciously defer, the Clause 9 survey's Q1-Q13 and the
   architecture survey's D1-D10. Name any owner decision the
   surveys required that SF-1 silently decided or dropped.
7. **Standing rules.** No copied IEEE text (clauses cited
   only); no third-party source as design input; clean-room
   fences intact; nothing with `cft` in its name opened,
   searched, or listed; PDF not opened; board untouched;
   records-moved/pre-push rules not violated by the draft.

## Output

- `scratch/sf1-verify/report.md`: verdict first line
  (`PASS` or `SENDBACK`), then findings. Under HonestFramework
  only (a) regression or (b) wrong answer sends back; label
  each finding (a)/(b)/suggestion. Suggestions never block.
  Cite SF-1 line + source line for every (a)/(b).
- `ledger/verifier-sf1.md`: append-only entries (start, plan,
  close) in house format.
- Structured result: complete/evidence/unresolved per schema;
  evidence strings carry the finding list compactly; any duty
  you could not inspect goes in unresolved, not silence.

Escalate, do not edit: SF-1 text, repository files, survey
reports, and other ledgers are read-only to you. If a survey
and SF-1 disagree, the survey is evidence and SF-1 is the
suspect - unless the code itself proves the survey wrong, in
which case cite the code.
