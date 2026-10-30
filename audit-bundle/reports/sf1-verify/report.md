PASS

Synthesis verification of revised `muse-softfloat/docs/studies/SF-1.md`
(working tree, 771 lines, base `32dac7d`) after the owner 2026-10-27
format-parity direction. Read in full by the synthesiser: SF-1 lines 1-771.
Lens evidence reused via runtime handoff (prior result 1 = Lens A duties 1-2;
prior result 2 = Lens B duties 3-7 + fidelity spot-checks); both lenses carry
inspected line citations, so their number-match evidence is adopted as
evidence, and survey-line restatements below are attributed to the lenses.
No (a)/(b) finding was reported by either lens; the synthesis re-checked the
SF-1 lines behind every suggestion below and found no surviving regression or
wrong answer to promote. Dedupe: Lens A and Lens B fidelity checks overlap
and agree; kept once.

Findings labelled (a)/(b)/suggestion (SF-1 line citations inspected here):
- (a) regression: NONE. No surviving single-format addition, pricing, gate,
  merge, or claim path: parity bundle rule stated SF-1:158-170, enforced at
  SF-1:265-273 (Steps 1a/1b/2c all 3-format bundles), SF-1:462-468 (partial
  merge refused), SF-1:613-620 (bundle refused unless all three formats close),
  SF-1:524-527 (traps retired only for binary64 spellings KissFFT links).
- (b) wrong answer: NONE. Accounting closes SF-1:282-283 (33+6=39;
  9+21+111=141; 39+141=180); earning classes labelled everywhere counts appear
  SF-1:97-106, 246-251, 352-361, 562; Fork A argument named SF-1:77-80, Fork B
  patch named SF-1:81-85; seam matches code per Lens B code reads; Q1-Q10
  cover or consciously defer Clause 9 Q1-Q13 / arch D1-D10 per Lens B.
- suggestion S1 (parity-scope gloss): SF-1:158-170, :250, :524-527 read as
  settled that compat spellings sit outside parity; defensible but narrows the
  standing owner rule without an owner question. Recommend one-line
  confirmation under Q9/Q10. Not a blocker.
- suggestion S2 (Fork B wording): public sentence SF-1:83-84, :503-504
  ("exact mathematical twiddles") vs exact-only-for-N=2^k argument
  SF-1:492-495; gated N set is all 2^k so evidence holds in-gate, but qualify
  the public sentence. Not a blocker.
- suggestion S3 (control-9 rename): SF-1:89-94 vs retired-into-inventory
  code shape; functionally identical refusal, rename to avoid rot. Not a
  blocker.
- suggestion S4 (§11 risk-1 count split): SF-1:~705 "33 K0/K1 rows" omits the
  earned/breadth split SF-1:104-106 mandates wherever counts are published.
  Not a blocker.
- suggestion S5 (invalid-enum ruling): SF-1:557 states ignore-write inside
  deferred §7 though the Clause 9 sub-choice was never put to owner; mark
  provisional. Not a blocker.
- suggestion S6 (payload encoding entry pin): SF-1:363-371 pins sets/sign/-0
  but not the operand encoding; name it before 1b code. Not a blocker.

Lens evidence carried (compact):
- Lens A (duties 1-2): 180+5, 33=24+9 with 6/27 split, 249 attr rows, 43/128
  provenance, KissFFT census + twiddle counts (1022/1024, 620/1024, 590/1024,
  3dbl/4flt of 2048), interval E1-E8 numbers, 783 rows, 201/201 multi-board
  ~1.5003 steps/s, 39/141/180 arithmetic with all core counts multiples of 3
  — all match surveys/ledger.
- Lens B (duties 3-7): earning honest (binary64-only trig under
  runtime-generation contract; interval at most 9.6 semantics-owning f32/f64,
  strict bar earns zero stated); parity holds with S1 carve-out as suggestion;
  forks honest with S2 wording note; seam feasible vs generator/runner/compat/
  board code with S3 rename note; Q1-Q13/D1-D10 covered or deferred via Q10
  with S4-S6 notes; standing rules intact (clause-only citations, no
  third-party design input, no cft contact, no PDF, board untouched, draft
  disclaims authorisation).

Duties not inspected (preserved verbatim):
- Duties 3-7 (earning logic/parity labelling, claim honesty, seam vs code,
  Q1-Q13/D1-D10 coverage, standing rules) out of scope for Lens A - not
  inspected.
- No code-level re-verification of generator counts (relied on surveys'
  MEASURED runs); SF-0/RECORD/AGENTS spot-checks beyond Lens A numbers not
  done.
- Per-kernel line-by-line audit of msf16/32/64.c internals (relied on surveys
  + generator/runner/compat reads; no finding depends on it).
- Per-function worst-case gap bit counts (deliberately untranscribed by
  clause9 survey; owned by SF-1 Step 2b pricing spike).
- Silicon re-measurement of cited board figures (board untouched per brief;
  figures corroborated via ledger entries only).
- Owner confirmation of S1 parity-scope carve-out, S2-S6 wording/entry-gate
  tightenings (suggestions, not blockers).
