# Time boxes and size ceilings, against the actuals

The leads' brief rule since 2026-10-19: every brief carries a scope ceiling and a time box, and the record sets each against what happened.

## 13a. First passes against their boxes

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the coverage wave, closed", line 22770. Not in this kit.
- **What it shows** (the kit's reading): Time boxes against first passes, the overruns named, and size ceilings against sizes, reported on his question.
- **Cut:** nothing.

> - **The time boxes** (reported to Logan on his question): the authors' first passes against their boxes were DR1 86/120, CL 93/240, HC 111/240, SG 135/180, XG 157/240, DR2 193/240, FX 117/90, GS 77/75 and CK 54/75 minutes; the two overruns were small parcels' boxes (90 and 75 minutes). Most went past their briefs' size ceilings, from about 1.2 times (GS, 308 changed lines against "About 80 to 250") to about ten (XG, 3,317 against "a few hundred lines in all"), each size at its report's HEAD. Haiku verifiers' first passes took 14 to 54 minutes of boxes of 30 to 120.

## 13b. A size past its mark, accepted after the fact

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "six small tool defects a user meets", line 23114. Not in this kit.
- **What it shows** (the kit's reading): A size past its mark, accepted by the lead after the fact and named as the parcel's slip, and every fix with a test shown red once.
- **Cut:** nothing.

> **What was asked, and decided.** Logan, 2026-10-21, verbatim: "the remainder of this week will be focusing on whats present and polishing/refining things that were able to slip by." Parcel KL's census of the record's open known limits (the round's `polish/KL-known-limits.md`) put seven small Python tool defects in its Bundle 6; this parcel took them, on branch `polish-p6` cut from `aa7cb603`. Three decisions of the lead's and Logan's shaped it: **KL-330** was held by the lead and then decided by Logan (below); **hw/gen_layouts.py** was fixed with the hw-area figure remade (the lead's option A, below); and **the size**, 1,193 changed lines (at `92916078`, before this entry) against a mark of 700 for a message first, was accepted by the lead after the fact, since most of it is the tests the brief asked for (the late flag is this parcel's slip). Every fix has a test shown red once, either against the base's file (`git checkout aa7cb603 -- FILE`, the test run, `git checkout HEAD -- FILE`) or with the fix broken by hand where the base has nothing for the test to call; the red runs are in the parcel's ledger.

---

These passages are excerpts of cft-fp256's docs/VALIDATION.md. cft-fp256 is Copyright 2026 Logan W., under the Apache License 2.0. The kit's NOTICE.md says what else it carries, and under which licence.
