# rechecker-sf0 report — SF-0 draft 2 (4f7f870), scoped re-check, disconfirm-only

Verdict: **NOT READY**. (a) 0. (b) 2. Notes: 4.
Target: `4f7f870818eb2a0e736af264bb069df6306c7d744` in `muse-softfloat/`
(amended commit; parent `2bac8e9`; draft-1 object
`33c59f9f971f95715dc3bdcc3a2c8bdfd3595272` still exists locally but is
unreachable from any ref). One file changed: `docs/studies/SF-0.md`,
126 insertions, 43 deletions. No project file touched by this rechecker;
all probes read-only. Ledger append was **blocked** (sandbox denies every
`bash` spawn, so kit `tools/ledger.sh` cannot run here); the ready-made
body waits at `scratch/rechecker-sf0/ledger-body.txt` for the lead to
append. Stance: disconfirm only. The six technical restatements all verify
as real; the two (b)s are new false accounting sentences (one in the commit
message, one in Section 14), not technical regressions.

## Method and environment limits

Read `ledger/verifier-sf0.md` and `scratch/verifier-sf0/report.md` first,
then formed my own view from the full draft-2 file (807 lines, read whole)
and the complete `33c59f9..4f7f870` diff (323 lines, read whole, in three
windows covering lines 1-323). Corroborated against S1 §0/§1/§3.4/§5/§6,
S2 §3.1-§3.4, S4 §1.2/§2/§3/§5.2, the evidence-auditor report (1205 lines,
count re-measured: exactly 1205), kit `WORKFLOW.md` Phase 4 + planted-fault
protocol, and the ledger stamps cited. Never read `scratch/lead/` or any
other agent scratch; nothing with `cft` in its name opened, searched, or
listed; spawned nothing; no background work exists to stop.

Tooling deviation (forced): `bash` cannot spawn in this session
(`Bash/ServerInstance/CreateInstance/E_ACCESSDENIED` on `bash --version`
and on `bash scratch/rechecker-sf0/r1.sh`). Probe scripts are still filed
as Git Bash script files under `scratch/rechecker-sf0/` (`r1.sh`, `r2.sh`)
as the command record; each was executed as a PowerShell equivalent with
**identical `git -c safe.directory=... -C muse-softfloat` argv**, `git`
config never touched. Whole-file sweeps ran through the granted search
reader (regex mode) rather than `grep`.

## The change under review (evidence)

- `git -C muse-softfloat show -s --format=... 4f7f870`: subject `Drafted
  SF-0: the plan of record for Muse-Softfloat`, parent `2bac8e9` (an amend
  that orphaned `33c59f9`), full body captured in
  `scratch/rechecker-sf0/tmp/commitmsg.txt`.
- `git diff --stat 33c59f9 4f7f870`: `docs/studies/SF-0.md | 169
  ++++---` / `1 file changed, 126 insertions(+), 43 deletions(-)`.
  `git diff --numstat` agrees (`126 43`). No other file touched.
- Hunks touch: §0 item 5, §1 quote, §2.2 (widths + fallback), §2.5 (B5),
  §2.7 (augmented + roundToOdd), §3.4 (interrupt contract), §4.2 (B3
  retag), §4.3 (decimal design), §4.4 (context only), §5.1 (sampled),
  §5.2 (new controls), §5.3 (context), P0 items 4/5(context)/7/9,
  P0 acceptance, Wave 1 (totalOrder), Wave 2 (planted-copy), Wave 3
  (context), Wave 4 (context), §9 (pin split + converter), Q12.9 (new),
  §13 (audit citation), §14 (draft-2 paragraph).

## (1) B1-B6: restated true, nothing old left standing

Whole-file sweep for each old claim and near-variants (regex over the
current file): `before rounding` 0 hits; `emax + 2` 0 hits;
`all MEASURED` 0 hits; `integer <-> binary16` 0 hits; `invalid signaled`
0 hits; `canonical quiet NaN` 0 hits; `augmented` only in the corrected
forms (lines 272, 726, 789). Per item:

- **B1 tininess — TRUE RESTATEMENT.** §0 line 56 now `after rounding`;
  §2.5 line 190 `- **Tininess: after rounding**`; Q12.9 line 750 repeats
  `after rounding`; §14 line 785 records the fix. No `before rounding`
  remains anywhere. Consistent with §4.1 (specialization matching §2.5),
  §5.1 (choices printed), §5.2 (wrong-polarity control), Q12.5/Q12.9.
- **B2 exponent widths — TRUE RESTATEMENT.** §2.2 lines 119-121 state
  per-format `w=5/8/11, emax=15/127/1023` under "the standard's Table 3.5".
  Self-check: `emax = 2^(w-1)-1` holds for all three (15/127/1023). The
  false formula is gone file-wide. `(S1 section 6)` residue on that line
  correctly became `(S1 section 0)`, where S1's format-status table lives.
- **B3 host-oracle retag — TRUE RESTATEMENT.** New §4.2 lines 397-399:
  `(the compiler-path trap and contraction refusal are MEASURED in S2
  section 3; parts of the architectural exactness and tininess account
  there are READ or BELIEVED, as tagged)`. Verified: compiler-path trap
  MEASURED (S2 §3.2, probe/probe3/probe4 logs); contraction refusal
  MEASURED (S2 §3.4c, probe4: `-ffp-contract=fast` fuses, `=off` does not);
  exactness READ+BELIEVED (S2 §3.3 header: Intel/MDM READ + block tagged
  BELIEVED); tininess BELIEVED (S2 line 415: x86 tininess after rounding
  BELIEVED). Every tag in the retag matches S2's own tags.
- **B4 fallback conversions — TRUE RESTATEMENT.** New §2.2 lines 130-134
  owe `binary32/64 <-> binary16` + `decimal/hex character conversions`
  `(S1 section 6, marked BELIEVED application there)` and route integer
  conversions through an arithmetic format. Verified: S1 §6 lines 469-472
  drop exactly `binary16-integer conversions under 5.4.1/5.8`; S1 §6 lines
  457-461 + BELIEVED summary lines 480-483 require the conversion core
  (binary16 <-> arithmetic formats + decimal/hex). The parenthetical is
  accurate: S1 §6's application to interchange binary16 is S1-tagged
  BELIEVED throughout.
- **B5 quiet-payload truncation — TRUE RESTATEMENT.** New §2.5 lines
  218-221: `the default quiet NaN is returned (no invalid is claimed for
  truncating a quiet payload itself; signaling inputs still signal under
  (b))`. Verified: S1 §3.4 line 340 records only `shall still return a
  quiet NaN (6.2.3)` — no invalid (the dropped claim is gone file-wide);
  the added `signaling inputs still signal` is grounded in READ 6.2
  behavior S1 records (same-format convertFormat quiets signaling NaNs
  with invalid signaled, S1 line 148; signaling-NaN input behaviour and
  flags follow 6.2/Clause 7, S1 lines 463-465), and matrix item (b)
  already covers non-character conversions, which `convertFormat` is.
- **B6 augmented list — TRUE RESTATEMENT.** §2.7 line 272 now names
  `augmented addition, subtraction, and multiplication` (all three S1 §5
  names); the `roundToOdd`-style helper joins the Tier 2 list (line 271),
  closing old note N9 inside the same fix; Q12.3 line 725-728 still claims
  the list is `the only way extra time is spent`, now against a complete
  list. No two-item `augmented addition/multiplication` phrasing remains.

## (2) Note dispositions: real except where noted

- **Decimal design in §4.3 — REAL.** Lines 435-450 add an exact-authority
  design (integer-times-power-of-two expansion, one rounding; exact
  rational on input; MPFR cross-check at +64 bits doubling to agreement
  with wide exponent range and modeled subnormals; split stops the gate;
  sampled digit counts `{1, 2, Pmin-1, Pmin, Pmin+1, H-1, H}` per format
  and mode plus ties/subnormal/wide-exponent/grammar cases; exhaustive
  binary16 + binary32 round-trip sweeps at wave gates). It is new design
  under unchanged proposals (H=20, MPFR oracle), technically sound, and
  its own §5.2 decimal-oracle control targets it. Old note N5 closed.
- **Coverage ledger — REAL.** Per-instantiation ledger with deciding
  authority + project-owned exact references for the Berkeley tail
  (lines 423-433) plus P0 item 5 header-level coverage check (lines
  552-557) were already present and are now pointed at by the new
  controls; auditor finding (2) has a named closure path.
- **Plants from Wave 1 — REAL and kit-conformant.** §5.2 lines 515-517
  (`from Wave 1 onward`), §7 lines 616-618 (`in force from Wave 1`).
  Kit `WORKFLOW.md` Phase 4 step 4 (`Verify, on a planted copy`) applies
  to *each wave* with no Wave-2-only rule, and the planted-fault protocol
  exempts only `the lead's own work` (P0) — so Wave-1 start is compliant,
  and the old deviation note is closed, not renamed.
- **Sampled board scope — REAL.** §5.1 line 495: `the same sampled
  vectors on RP2040`. Old ambiguity gone.
- **New negative controls — REAL and aimed.** §5.2 lines 511-515 add
  exactly the four missing families: wrong-tininess-polarity at the
  smallest-normal boundary (tininess), wrong NaN payload / missing
  signaling-NaN invalid (NaN policy), wrapper-state leak via same-core
  IRQ interleaving + second-core cross-talk (IRQ/dual-core), decimal
  oracle with too-narrow range / subnormalization off (MPFR recipe).
  Each control targets the section that designs the choice.
- **totalOrder / flag ops / version predicates — REAL homes.** Wave 1
  line 606 (`comparisons including the totalOrder family`); P0 item 4
  lines 549-551 (six flag operations over caller-owned state +
  `is754version*` predicates, first gated operations). Old note N6 closed.
- **Section 1 quotation ellipsized — REAL.** Line 92 ends `...`.
- **Interrupt contract — REAL.** §3.4 lines 347-354 write the caveat
  (per-core shared thread/IRQ, never cross-core, no implicit save/
  restore, caller saves or uses the stateless core API) and task the
  self-test; P0 item 7 lines 574-576 builds it; P0 acceptance lines
  587-588 requires it to pass. The §2.4 line 186 pointer now resolves.
- **Serial risk — REAL.** P0 item 7 lines 567-570: no board serial proven
  at study date, COM1/COM5 are not the board, establishing CDC is P0
  scope and risk. Old note N12 closed in the exact words asked.
- **Q12.9 settled-in-body choices — REAL.** Lines 748-757 put every old
  N1 item to Logan individually (tininess, NaN matrix, Clause 8 out, no
  fifth dynamic attribute, `uint16_t` storage, C11-first + descriptive
  goals + toolchain pins, H/logBFormat/integer formats/spellings).
  `the eight questions above` is correct — Q12.9 is itself the ninth.
- **IAS15 pin separation + coefficient converter — REAL and S4-grounded.**
  §9 lines 664-668 split extraction pins (delete variational/collision/
  additional-force branches both sides) from runtime configuration
  (BASIC, PRS23, OpenMP off, no MEGNO); S4 confirms each default
  (BASIC §1/S56-61, PRS23 §3/S352, MEGNO/collisions off-path §1/S73-75).
  Lines 670-674 name the converter (MPFR >=256-bit from source decimal
  literals, cross-checked against the strict-host compiler literal
  conversion per entry, verified hex carried both sides, disagreement
  stops the brief) — strictly stronger than S4 §1.2's `carry as hex`
  recommendation. Old note N15 closed.
- **Section 14 accounting and stamps — COUNTS/STAMPS TRUE, audit mapping
  TRUE, with one false closing sentence (F2 below).** `(a) 0, (b) 6,
  notes 15` match the verifier ledger/report; each B-line (784-789)
  describes its fix accurately; each note line (790-798) points at text
  that exists (verified line by line above); the audit paragraph
  (799-803) maps all ten auditor findings correctly — decimal hole,
  tail coverage, bring-up, board sample, Tier 2 definition to §§4-7;
  IBM terms refused (§4.3 line 413); budgets-from-measurement (P0 item 5
  + §8); hex `shall` picked (§2.6 lines 257-259); licence/timing left
  open in Q12.8 (declared open, honestly); SDK-level baseline declared
  open (assignment pointer imprecise — see note N-ii). Stamps: verifier
  `2026-10-26 13:16:25 -0700` matches `ledger/verifier-sf0.md`;
  `ledger/sf0-evidence-auditor.md` `2026-10-26 12:37:24 -0700` matches;
  auditor report re-measured at exactly **1205** lines, matching the
  commit message; `ledger/lead.md` `2026-10-26 12:06:41 -0700` Wave-0
  entry exists as cited.
- **Tagging promise (old N10) — PARTIAL, remains a note.** New tags were
  added where restatements landed (§2.2 BELIEVED, §2.6 BELIEVED, §2.5
  believed-x86, §4.2 MEASURED/READ/BELIEVED), but §8 cycle numbers and
  the new §4.3 decimal recipe still carry no tags. Non-blocking, as
  before; recorded so the claim `dispositions the ... notes` is not
  over-read.

## (3) New breakage from the restatement

No technical regression: no renumbering (P0 items, Q12.1-8, Wave order
all keep their numbers), every touched cross-reference resolves (§3.4
self-test cited three times consistently at lines 352-354, 574-576,
587-588; P0 item 9 exists at 581-583; Q12.9 exists; `Section 14` exists),
and tininess/NaN/tier language is uniform across §§0/2/4/5/7/12
(`after rounding` at lines 56/190/750/785; `default quiet NaN` at 59/208;
Tier 1 = §§2.1-2.6 at line 264, Tier 2 ordered list at 268-283, Wave 4
gated per-item at 623-625, Q12.2/12.3/12.9 aligned). Grammar changes
preserve meaning (§0.5 parallel participle; §4.3 `subnormalization
represented in the checker` is awkward but unambiguous in context).
Two new false sentences and two imprecisions:

- **F1 (b) — commit message miscounts the approval questions.** Message:
  `eight numbered approval questions for Logan`. The tree has **nine**
  (Q12.1-12.9, lines 719-757; Q12.9 `Settled-in-body choices` is numbered
  `9.`). Whichever draft the `What occurred` paragraph describes, the
  message as attached to this tree misstates its count. Fix: `nine`.
- **F2 (b) — §14 closing sentence falsifies its own paragraph.** Line
  803: `No proposal's substance changed except removing the Section 0
  tininess self-contradiction.` The same paragraph lists added substance
  (decimal design, four controls, Q12.9, pin split, converter), P0 gained
  obligations (flag ops + predicates in item 4, serial scope + wrapper
  self-test in item 7), and even the B-fixes changed specified behavior
  (B4 removed owed conversions; B5 removed a signaled invalid). No
  proposal *reversed* — but substance was added. Fix: `No proposal
  reversed; the rest is added obligation and design detail listed above.`
- **N-i (note) — `Sections 0.8/8` (line 754) resolves to no label.** No
  `0.8` heading exists; toolchain pins are stated in §0 item 8 only
  (lines 74-76), §8 states none. Readers can find the referents, but the
  cite is private shorthand. Fix: `Sections 0 (items 7-8) and 8`.
- **N-ii (note) — SDK-baseline assignment pointer overstates.** §14
  assigns `the SDK-level benchmark baseline ... to P0 item 9`; item 9
  tasks skeleton reporting against bootrom/libgcc baselines, and only §8
  adopts the SDK harness methodology `as the comparison shape` — SDK-
  harness baseline *production* is not explicitly tasked. The item is
  honestly declared open, so this is mispointing, not false closure.
  Fix: name SDK-harness baseline production in P0 item 9 or soften §14.
- **N-iii (note) — old N10 tagging still partial** (see above).
- **N-iv (note) — commit `What occurred` says `Wrote ... (draft 1)`**
  while the tree holds draft 2.** The Verification paragraph discloses
  the amend, so this reads as history, but attached to an amended commit
  it is stale without a `draft 1 wrote; this amend restates` marker.

## (4) Commit message vs reality (counts, stamps, claims)

- Counts: `(a) 0, (b) 6, notes 15` TRUE; `1205 lines` TRUE (re-measured);
  `eight numbered approval questions` FALSE (F1); `All six were the
  lead's own sentences` TRUE.
- Stamps: verifier `2026-10-26 13:16:25 -0700` TRUE; evidence-audit
  `2026-10-26 12:37:24` TRUE; lead `12:06:41` Wave-0 entry TRUE.
- Claims: `Section 14 keeps the counts beside the changes` TRUE;
  `dispositions the gate-strengthening notes` substantially TRUE
  (every note touched; N10 tagging partial, N-ii pointer soft);
  `pushed for Logan's approval only on READY (or at the study cap with
  open findings listed)` matches the auditor's exit rule — TRUE.

## Commands run (read-only)

1. `git -C muse-softfloat log --oneline` → 3 commits; `33c59f9` is a
   dangling object (`cat-file -t` = commit) unreachable from refs —
   consistent with an amend; diff works.
2. `git -C muse-softfloat show -s --format=... 4f7f870` → message saved
   to `tmp/commitmsg.txt` (quoted above).
3. `git -C muse-softfloat diff --stat/--numstat 33c59f9 4f7f870` →
   `docs/studies/SF-0.md | 169 ++---`, `126 43`.
4. Full diff saved to `tmp/full.diff` (323 lines / 42862 bytes), read in
   full via three windows (1-120, 121-230, 231-323).
5. Whole-file regex sweeps over draft-2 `SF-0.md` (results quoted in
   §(1)); targeted reads of S1 (§0, §1.1, §3.4, §5, §6), S2 (§3.1-3.4),
   S4 (§1.2, §2, §3, §5.2), auditor report (findings list + closing),
   kit `WORKFLOW.md` (Phase 4, planted-fault protocol); line count of
   auditor report (1205); stamp greps in `ledger/`.

## What was not done (limits)

- `bash` spawn denied session-wide, so kit `tools/ledger.sh append`
  could not run: **no ledger entry was written** (nothing hand-appended,
  per the tools-only rule); `ledger-body.txt` is staged for the lead.
- Did not re-verify S1's 81-name enumeration or the licensed IEEE PDF
  (took S1 + auditor + arithmetic self-checks as authorities, as tasked
  scope allows); did not run builds/board work (textual study).
- Did not read `scratch/lead/` or non-allowed scratch; no `cft` contact;
  no processes started, none to stop.

Report path: `scratch/rechecker-sf0/report.md` (this file).
Ledger intent: `ledger/rechecker-sf0.md` via kit `ledger.sh` — BLOCKED,
body staged at `scratch/rechecker-sf0/ledger-body.txt`.
