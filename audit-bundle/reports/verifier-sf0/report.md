# verifier-sf0 report — SF-0 draft 1 (33c59f9), disconfirm-only

Verdict: **NOT READY**. (a) 0. (b) 6. Notes: 15.
Target: `33c59f9f971f95715dc3bdcc3a2c8dfd3595272` in muse-softfloat/
(one new file, `docs/studies/SF-0.md`, 724 lines). No project file touched
by this verifier; all probes read-only (greps, exact-line reads, one web
corroboration). Ledger verdict appended only to `ledger/verifier-sf0.md`.

Stance: disconfirm only. "Found nothing" was not the outcome: one
self-contradiction, three false sentences, one miscite against S1, and one
incomplete Tier 2 enumeration block the push gate. Nothing below redesigns
the study; each (b) names the exact line and the minimal repair.

## Method and probes run

Formed my view from the study first (full read, both passes), then read
`ledger/README.md`, `ledger/lead.md` (ends 12:26:47, no later entry),
KICKOFF, RECORD, HARNESS, BOARD, AGENTS, WORKFLOW Phase 2, PROJECT nine
questions, scratch S1/S2/S3/S4 reports, and the sf0-evidence-auditor
report. Never read `scratch/lead/` or any other agent scratch; nothing
with `cft` in its name opened, searched, or listed; spawned nothing.

Probe scripts (Git Bash, TMPDIR into this scratch):
- `probeA.sh`: greps for tininess/before/after, `w = emax`, pin hash,
  "all MEASURED", fallback conversions, augmented, board scope, plants,
  roundToOdd, S1 section cites. Outputs confirmed lines 56 vs 186
  (before/after), 120 (`w = emax + 2`), 611 (`262a9cc`), 384
  ("all MEASURED there"), 129 (fallback integer conversions), 265
  ("augmented addition/multiplication"), 462 vs 531-532 (board scope),
  572-573/580 (plants), 153 (roundToOdd Tier 2).
- `probeB.sh`: exact-line extracts. S4 pin is
  `` `262a9cce102c69ca2cf7f3c6c1264e5e6002b7d` `` — first 7 chars
  `262a9cc`, so SF-0 line 611 is a CORRECT truncation (no finding).
  S1 §6 lines 466-472 explicitly drop direct binary16-integer conversions
  for interchange-only. S2 lines 413-419 tag x86 tininess BELIEVED.
  S1 §3.4 lines 328-340 record quiet-NaN narrowing with NO invalid signal.
- Web corroboration (one search + one fetch of Berkeley TestFloat history,
  primary source): Release 3b "changed the default to be the detection of
  tininess after rounding (`-tininessafter`) instead of before rounding".
  So Berkeley 3e-line default IS after-rounding: SF-0 §2.5's rationale is
  true, §0.4's "before rounding" is the false side.

## Per-item verdicts (attack list)

1. Conformance contract — MIXED (defects B1, B2, B4, B5, B6 below;
   counts/inventory confirmed: 81 names S1 §1, H=20 marked BELIEVED,
   Pmin 5/9/17, FMA 7.2(c) ruling present, Tier 2 claim levels present).
2. Authorities — CONFIRMED sufficient as plan (order, disagreement
   protocol §4.4, per-instantiation ledger §4.3, envelope §4.2), except
   false provenance sentence B3 and undesigned decimal-string recipe
   (note N5). MPFR+exact for decimal is named but not specified.
3. Architecture/API/state — CONFIRMED except: interrupt caveat promised
   (§2.4) but never written (N11); roundToOdd Tier-2-only (§2.3) missing
   from §2.7 list (N9). No flags-API contradiction found (NULL wording
   vs non-null default is coherent). formatOf naming rule complete.
   uint16_t containers decide the S3-flagged storage probe (good).
4. Gates/P0 — CONFIRMED buildable/acceptable as written (oracle bring-up
   P0 item 5 before dependence; budgets priced from measurement §6.5;
   Wave-1-brief acceptance named), except board-scope ambiguity N3 and
   missing tininess/IRQ/MPFR negative controls N4. Refusals carry S2's
   x87/PATH traps and S3's interpolator warning.
5. Waves — CONFIRMED except plants deviation N2 and unassigned families
   N6. No dependency error: Wave-1 exit (binary64+basic) covers IAS15's
   needs (S4: binary64 +−×÷√ + fabs/copysign/isnormal). Widening language
   is a coherent constraint (exact intermediates; binary32-path forbidden
   unless proven immune). Caps respected (draft 1 of 3+2; loose cap named).
6. IAS15 — CONFIRMED except notes N13/N14/N15. Pin correct (7-char prefix
   of S4's MEASURED hash). BASIC default, PRS23, strict-flags set, hex
   initial conditions, field-parsed (not whole-file) comparison, GPL
   boundary all match S4 and are put to Logan in Q12.7 (answers KICKOFF Q4).
7. Internal consistency — DEFECT (B1 tininess; B2 w-formula; B6 augmented
   list; N3 board scope; N9 roundToOdd). Scope/tiers/models/licences
   otherwise agree across §§0/2/4/5/6/7/12; owner quotes accurate bar N7;
   Option sets settled-in-body but thinly interrogated in §12 (N1);
   links/file refs real (tools/run.sh and generated headers are named as
   P0 deliverables, correctly forward-referenced).
8. Anything else — the six (b)s and N1–N15 are the full list; no further
   faults found in a second full pass.

## (b) findings (must fix; each one line + evidence)

- B1 §0 line 56 "tininess detected before rounding" contradicts §2.5
  line 186 "Tininess: after rounding". Berkeley 3e default is after
  (TestFloat history, Release 3b, primary source). Fix: "after".
- B2 §2.2 line 120 "w = emax + 2 exponent bits". False for all three
  (S1 Table 3.5: w=5/8/11; emax+2=17/129/1025). Fix the formula.
- B3 §4.2 line 384 "(S2 section 3, all MEASURED there)". False: S2 §3.3
  architectural block is tagged BELIEVED-in-part (S2 lines 398-401),
  §3.4 carries BELIEVED items. Fix: "READ+BELIEVED" or equivalent.
- B4 §2.2 line 129 fallback "owes ... integer <-> binary16 conversions
  (S1 section 6)". S1 §6 lines 469-472 explicitly drop direct
  binary16-integer conversions for interchange-only. Fix: drop the
  integer clause (routing via binary32/64 stays covered).
- B5 §2.5 lines 215-216 "where narrowing would truncate a payload to the
  infinity pattern, Clause 7's rule applies (default quiet NaN, invalid
  signaled)". S1 §3.4 records only "shall still return a quiet NaN
  (6.2.3)" — no invalid signal. Fix: cite the clause or drop "invalid
  signaled".
- B6 §2.7 lines 265-266 Tier 2 "augmented addition/multiplication"
  omits augmentedSubtraction (S1 §5 names three), while Q12.3 claims the
  list is "the only way extra time is spent". Fix: add it or refuse it
  by name.

## Notes (not blocking; recommended before owner approval)

- N1 §12 asks 8 decisions but PROJECT Q3-ties-to-away-attribute,
  Q4-Clause-8, Q5-tininess-side/NaN-matrix, Q6-binary16-storage,
  Q7-speed/size/yardstick/flash/language, Q8-toolchain-pins, and the
  language-defined H/logBFormat/integer-format choices are settled
  in-body under whole-approval. WORKFLOW Phase 2 wants each question put
  to Logan. Recommend explicit questions, especially the tininess side.
- N2 §7 "Planted faults ... from Wave 2 onward" deviates from WORKFLOW
  Phase 4 step 4 ("Verify, on a planted copy") for Wave 1 without naming
  it as a deviation.
- N3 §5.1 board budget "the same vectors on RP2040" vs §6 "on-silicon
  sample; full-volume board replay is explicitly not promised". Ambiguous
  scope; one-word fix ("the same sampled vectors").
- N4 Negative controls (8 named) lack tininess-polarity, NaN-policy,
  IRQ/dual-core, and MPFR-recipe controls — the auditor's top
  gate-integrity items (§2 item 4, §4.2). A wrong-tininess build passes
  default-tolerance vectors uncaught.
- N5 Decimal-string oracle is the largest undesigned item: §4.3 names
  "MPFR/exact arithmetic" and §2.6 sets H=20, but no MPFR
  string-conversion recipe (emin/emax/subnormalize for decimal paths) or
  digit-count sampling plan; S2 never surveyed one. Backstopped by §4.3
  "no unconfirmed at a wave gate" + P0 bring-up — acceptable for a study,
  must be designed before Wave 3.
- N6 No wave home named for `is754version*` predicates or the six flag
  operations (5.7.4); totalOrder lands in Wave 1 "comparisons" only
  implicitly. P0 classification/sign-bit coverage is named; these are not.
- N7 §1 first blockquote drops KICKOFF's tail "(cfts most recent work has
  been tracked the most I believe)" without ellipsis.
- N8 §2.2 line 121 cites "(S1 section 6)" for binary16-not-basic; the fact
  lives in S1 §0 (Table 3.5 + basic-format text). §6 is the
  interchange-only residue.
- N9 §2.3 line 153 puts roundToOdd-style helpers "Tier 2 only", but §2.7's
  ordered Tier 2 list never mentions them.
- N10 §0 line 10 promises READ/MEASURED/BELIEVED tagging "where the
  distinction matters"; only H (§2.6) and the x86 tininess belief (§2.5)
  are tagged. E.g. §8 cycle numbers (S3 READ) and §4.3 recipe details
  (S2 BELIEVED-in-part) are untagged.
- N11 §2.4 "documents the interrupt caveat" points at §3.4, which holds no
  interrupt-caveat sentence; IRQ re-entry/nesting, who-clears, second-core
  isolation test, and RTOS posture are unnamed (S3 §6 demands them; Q12.4
  does not ask). P0 item 7 should add the dual-core + IRQ self-test the
  auditor's §4.2 requires.
- N12 §6 P0 item 7 tasks USB CDC replay but never states BOARD.md's
  standing fact (no serial channel proven; COM1/COM5 are not the board).
  Fine as P0 scope; name the risk.
- N13 Evidence audit (scratch/sf0-evidence-auditor/report.md) is never
  cited in SF-0 (only hit for "audit" is Q12.8's clean-room audit); its
  10 open findings have no status line in §14. Implicitly closed: IBM
  terms (refused §4.3), tail references (§4.3), budgets-from-measurement
  (§6.5), Tier 2 definition (§2.7). Still open: decimal design (N5),
  SDK-level baseline producer (§6 item 9 implies P0; say so), licence
  timing (Q12.8 asks — good), hex sentence (closed §2.6 — good).
- N14 §9 "configuration, not build accidents" conflates runtime
  configuration (MEGNO/OpenMP/exact-finish off) with extraction deletion
  (variational/collision branches). Harmless given "same extracted source
  both sides", but loose.
- N15 §9 "carried as verified hex bit patterns ... after a one-time
  conversion check against the source literals" names no converter or
  oracle for that check (host compiler? MPFR cross-check?).

## Auditor-disposition check (as tasked)

The lead made no ledger claim to have dispositioned the evidence audit
(last lead entry 12:26:47 starts drafting; audit landed 12:37:24; no later
lead entry). SF-0 does not cite it. Disposition is therefore partial and
implicit (see N13), not claimed-and-complete. Nothing in the study
contradicts the audit's headlines; B1/B4/B5 are instances of the audit's
predicted failure modes (unstated choice smuggled past Logan; §6
overreading) that SF-0 did not fully close.

## What was not done (limits)

- Did not read the licensed IEEE PDF (outside tasked evidence; S1 and the
  auditor are the clause authorities here; single web corroboration only
  for Berkeley's tininess default).
- Did not verify S1's 81-name enumeration independently; took S1 + auditor.
- Did not read scratch/lead/ or other agents' scratch; no cft-named path
  touched; spawned nothing; no background work to stop.
- No builds or board work: study verification is textual; probes were
  read-only greps/exact-line reads with outputs quoted above.
- Ledger verdict appended only to ledger/verifier-sf0.md via kit ledger.sh.
