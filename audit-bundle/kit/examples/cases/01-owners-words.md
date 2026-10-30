# The owner's words, recorded beside the lead's reading

ParcelRound METHOD.md section 7: the owner's decisions are kept as the owner gave them, with their dates, and the lead's reading goes beside them, marked as the lead's.

## 1a. A wave's requests, verbatim, then the lead's readings

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the coverage wave, closed", lines 22531-22553. Not in this kit.
- **What it shows** (the kit's reading): His words verbatim, one request a bullet, then the lead's readings and decisions, each reported to him as it was made.
- **Cut:** 5 line(s): 22532 (a term from the gate's list); 22543 (a term from the gate's list); 22547 (a test-design detail of that repository's own sweeps (the kit's reading)); 22548 (a term from the gate's list); 22549 (a term from the gate's list).

> **What Logan asked,** verbatim, on 2026-10-20:
> [line 22532 cut: it holds a term from the gate's arithmetic list]
> - "Go ahead and do a quick check on the stress test once you are able as well"
> - "As an experiment, try utilizing only Sonnet parcels and Haiku verifiers for this section of the plan"
> - "Go with all three outside generators if possible, more coverage isn't a bad thing even to have"
> - "1. A now, B planned. 2. Build time override for now with future plans to make adjustable more easily. 3. Go ahead and delete the clones"
> - "If needed it can have more time, though how have the time bounds been working so far? I noticed you started giving the agents them, good choice"
> - "Once you wrap up and push go ahead and resume the stress test and pause till tomorrow"
> - "Ill be using my PC so runs may be slower, no need to stop work though."
> - "*Clear to push once the gate and verifier finish, though do a quick check as it may have finished already"
> - "*The PC is free for heavy work again, go ahead and investigate the 2 failures as you already are"
>
> [line 22543 cut: it holds a term from the gate's arithmetic list]
>
> **The lead's readings and decisions,** reported to Logan as they were made:
> 1. **Every author Sonnet 5.5, every verifier Haiku 5.5,** the integration verifier included, by Logan's word. The very small fixes were the lead's, each with its Haiku verifier (his rule of 2026-10-13).
> [line 22547 cut: a test-design detail of that repository's own sweeps (the kit's reading)]
> [line 22548 cut: it holds a term from the gate's arithmetic list]
> [line 22549 cut: it holds a term from the gate's arithmetic list]
> 5. **The pass size:** a build-time override (parcel CK), not a runtime one; the stress driver's use of it is parcel DR3's, after this record.
> 6. **Windows `--require-all` with `generated` now fails, honestly:** GS's packager plant for backslash entries cannot run on Windows, and the stage now counts it. CI runs ubuntu only (gates.yml, READ), and the desktop is not a full verification host, so this is a known limit, not a change.
> 7. **Sent back, by Logan's rule** (a regression or a wrong answer): DR1 once, SG once, XG once, GS twice, DR2 once, CK three times. FX, HC and CL went back to no author: their verifiers' (b)s were the lead's to fix (FX's entry was restated by the lead; HC's and CL's were wording).
> 8. **The card-stress suite's two failures in the gate's clone** are not a regression: the same two fail before the wave in a checkout with host/ built, and pass at 9255ab8 in a fresh one (the box, below). They are a known limit of the test, by Logan's rule.

## 1b. How the record is kept, in his words

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the figures refresh and the header's sentence", lines 23534-23536. Not in this kit.
- **What it shows** (the kit's reading): His decision on how the record is kept before a push, verbatim; his choice among the lead's three ways, in the lead's words; and the four marks defined in one sentence.
- **Cut:** nothing.

> ## 2026-10-22 - the figures refresh and the header's sentence (parcel FR, Sonnet 5.5, the polish week): Logan's sentence on what history is returns to this file's header, the history extracts are read at the commit that carries it (15f96c8) with the ledger's whole file as their prefix, the one new statement of the two forms the scan reads is listed, and the history-size figure's scales and canvas follow its data; **no drawn build changes, nothing in this ledger is edited but the header's sentence (this entry is appended after the prefix the figures pin), and no host/, rtl/, hw/ or verify/ file, driver, card or box is touched**
>
> **What was asked, and decided.** Logan, 2026-10-22, verbatim, on this header: "Yes, add that sentence to the header, rewriting the current entry is common for the verifier send backs, correcting them with new entries would unnecessarily bloat the ledger more". The lead had added it (9af92cef) and taken it out (dc033cf1): the project figures pin a prefix of this file (the ledger extract, the first 1,891,030 bytes, read at 0b77387 on 2026-10-19), a change in the header moved those bytes and `python python/project_figures.py --check` failed, and a default remake kept the byte count and failed history-size's claim `ledger-size` (21,038 lines against git's 21,037). Of the lead's three ways to land it Logan chose, verbatim, "Go with 1", in the lead's words "a small polish parcel this week moves the figures to a current commit and puts the sentence in the header in the same change". Branch `figures-refresh`, cut from the local main at 6b73da70, which was not pushed when this was written; the merge is to be a fast-forward, so the commit the extracts name lies on main's own line. Marks: READ a file, COMPUTED arithmetic on what was read, MEASURED a run of mine, BELIEVED mine and unverified.

## 1c. Decisions beside the recommendation they answer

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the math library round's experiment E1", lines 19161-19172. Not in this kit.
- **What it shows** (the kit's reading): His decisions verbatim beside the recommendation they answer, and a cap on send-back cycles reached, so the merge went to him, and he waived it.
- **Cut:** 2 line(s): 19163 (a term from the gate's list); 19169 (a term from the gate's list).

> **Logan's decisions** (verbatim, 2026-10-13):
> - **On models:** "Use Sonnet for M1's build parcels as you recommended, it performed well". The lead's recommendation was:
> [line 19163 cut: it holds a term from the gate's arithmetic list]
>   - Sonnet verifiers;
>   - Opus for M2's study and for the language and cftc work.
> - **On the merge:** "Lead fixes sentence at merge".
>   - After the comparison, arm a's after-end fixes had to pass before it merged:
>     - plants for its six checks with no plant (076a108, with a check that every check has one);
> [line 19169 cut: it holds a term from the gate's arithmetic list]
>   - The first re-check, VE1-a2, found one false sentence, fixed in e854615. The second, VE1-a3 on Haiku, found two clauses of that sentence still false.
>   - The rules allow two such cycles, so the merge went to Logan. Arm a merged at b9d96be, the lead restating the two clauses in the merge commit by Logan's waiver of the cap.
>   - Arm b stays as branch m1-exp-b at 5a701ab.

---

These passages are excerpts of cft-fp256's docs/VALIDATION.md. cft-fp256 is Copyright 2026 Logan W., under the Apache License 2.0. The kit's NOTICE.md says what else it carries, and under which licence.
