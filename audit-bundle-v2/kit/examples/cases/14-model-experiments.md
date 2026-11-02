# A model experiment, reported as data

How an experiment with models is reported: as data, with its caveats, its criteria applied as they were fixed, and the lead's reading marked as the lead's.

## 14a. One tier of authors, another of verifiers

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the coverage wave, closed", lines 22685-22698. Not in this kit.
- **What it shows** (the kit's reading): An experiment of his, reported as data, with what it did not show, and the lead's reading for him.
- **Cut:** 2 line(s): 22686 (a term from the gate's list); 22689 (a term from the gate's list).

> **The experiment: Sonnet 5.5 authors, Haiku 5.5 verifiers** (Logan's, for this wave). What it showed, as data (MEASURED from the transcripts and the harness's notices; COMPUTED where it is a sum):
> [line 22686 cut: it holds a term from the gate's arithmetic list]
> - **What they found that mattered beyond wording:**
>   - VDR2's (b-1): the host pool's workers did not stop on a moved tree, shown by a probe (71 host slices in about 85 s after a commit);
> [line 22689 cut: it holds a term from the gate's arithmetic list]
>   - VDR1's (b-1): the empty-wave message called a campaign finished when it was not;
>   - VCK's three passes: `make clean` removing what it did not make, each pass a decoy shape the author's own test did not have (a name with digits after the size, then a regular file named like an object directory, then a symlink and a FIFO named like a product);
>   - VCL found an exact count identity the author and the lead had missed (15,654 = 16,292 - 638) and measured the mechanism behind it.
> - **What they did not do:** no Haiku pass found an (a) in an author's first commit; the (a)s were all in fixes (VCK's two). Whether a Sonnet verifier would have found more is not known: no parcel of this wave had both.
> - **Time:** first passes took 14 to 54 minutes (median 23) against boxes of 30 to 120; re-checks up to 41. The wave-8 Sonnet verifiers' first passes took 70 to 119 minutes on that wave's parcels (median 94; that wave's record), so Haiku's were about a quarter as long by the medians; the parcels differ, so this is not a measured comparison.
> - **Tokens** (output, the lead's method: the last line of each response summed): Haiku verifiers 3,832,047 in all, a chain 219,385 to 498,230; Sonnet authors 4,450,402, a parcel 187,107 to 815,942.
> - **Conduct:** one serious slip (VGS's `git bundle unbundle` in the main checkout, repaired and checked), one wasteful habit (VDR1's polling, stopped when asked), and small setup errors each verifier found and re-ran itself (VCK, VHC, VGS). Every frozen tree was clean before and after its pass. This wave's Haiku verifiers kept the ten-minute check-in rule (VDR1, VHC), which VRC, a Haiku verifier of 2026-10-14, had not.
> - **The Sonnet authors:** first passes took 54 to 193 minutes; FX (117 against 90) and GS (77 against 75) ran past their boxes, the small ones; DR1 (664 lines against 100 to 300), CL, HC, SG, XG (3,317 against "a few hundred") and DR2 went past their size ceilings and said so (READ, their reports; each size at its report's HEAD). One conduct slip (GS's global `safe.directory`, removed) and one leak (DR2's, found and removed by DR2).
> - **The lead's reading,** for Logan: on this wave, Haiku verifiers were adequate for checking Sonnet parcels by Logan's rule: their findings held, their passes were short, and their slips were caught. The cost was more passes: CK took four, GS three, and the lead's own small fixes drew (b)s on most of their first passes.

## 14b. Not met, by the letter

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the math library round's experiment E1", lines 19140-19148. Not in this kit.
- **What it shows** (the kit's reading): An experiment's verdict with its criteria applied as fixed in advance: "Not met, by the letter".
- **Cut:** nothing.

> **E1's verdict, the criteria applied as fixed** (COMPUTED from the above):
> 1. **Met.** Sonnet's arm needed 0 send-backs, Opus's 1.
> 2. **Met.** VE1-a found M1 to M7 met.
> 3. **Not met, by the letter.**
>    - Item 1: 0 cases each.
>    - Item 2: Sonnet's arm has 4 unshared cases and Opus's 3, so Sonnet's count is the larger. All seven are checks with no plant, and none is a wrong answer.
>    - On the substance of item 2 the comparison scored Sonnet's arm higher, 3 to 2.
>    - The lead's reading of the rules' undefined terms ("shares", "in all", "found") was recorded before the comparison reported.
> - **So by the rules as written, Sonnet's parcel did not succeed,** by one minor case on item 2. Both lists go to Logan, as the rules say: their counts went with E1's result (2026-10-12), and the seven cases were named to him after verifier-VIE1's check of this entry, which found they had not been.

## 14c. The experiment's own limits

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the math library round's experiment E1", lines 19180-19184. Not in this kit.
- **What it shows** (the kit's reading): The experiment's known limits: n = 1, a seal held by instruction only, position bias, default effort.
- **Cut:** nothing.

> **Known limits:**
> - **n = 1.** One run an arm shows what one Sonnet run did, not a rate.
> - **The third criterion's count favours the arm with fewer checks** (233 tests against 111, at the tips each arm ended at). The comparison's list of cases is its own enumeration, not a census of every check in both arms.
> - **The seal held against the comparison by instruction only:** the lead's ledger names each arm's agent, whose transcript names its model. The comparison's merge choice may carry a position bias, since it ran once.
> - **Each model ran at its own default effort.**

---

These passages are excerpts of cft-fp256's docs/VALIDATION.md. cft-fp256 is Copyright 2026 Logan W., under the Apache License 2.0. The kit's NOTICE.md says what else it carries, and under which licence.
