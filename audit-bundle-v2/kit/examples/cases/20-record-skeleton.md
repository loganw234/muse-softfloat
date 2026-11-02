# The skeleton of a closed-wave record entry

The sections of a record entry that closes a wave, in the order the six most recent such entries put them (MEASURED by the read-only surveyor's script over cft-fp256's docs/VALIDATION.md; its report is in the builder's docs/reviews/KIT-0/survey-cases.md). Each line gives how many of the six carry the section.

1. What Logan asked, verbatim (6 of 6, always first).
2. The lead's readings and decisions, reported to him as they were made (4).
3. The chain: each piece of work, its author, its verifier's passes with (a) and (b) per pass, and its send-backs (4).
4. The runs on the build host, the card or the gate, each asserted and copied with its sha256 (5).
5. Merge messages and earlier entries, restated where they claimed too much (2).
6. Conduct: what agents did outside their briefs, and its repair (3).
7. Time and tokens, per agent, with the method of the count (4).
8. Known limits carried, by the owner's rule (6 of 6).
9. The follow-ups (2).
10. Records: what was recounted, and where the copies are (4, always last).

Two of those sections follow, from the wave whose entry the other samples quote most, "the coverage wave, closed", with their cuts marked. The chain's section runs on past 20a's last line: its lines after that are sample 6a. The rest of that entry is quoted by samples under their own situations. In the entry's order, its passages are 1a, 20a, 6a, 10a, 16a, 8a, 7a, 14a, 20b (which holds 13a's line), 18b, and 6c's first line.

## 20a. The chain

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the coverage wave, closed", lines 22583-22600. Not in this kit.
- **What it shows** (the kit's reading): One row per piece of work: its commits, its author, each verifier pass as (a), (b), and how often it was sent back.
- **Cut:** 2 line(s): 22593 (a term from the gate's list); 22600 (a term from the gate's list).

> **The chain** (READ, each verifier's ledger and report; (a), (b) per pass):
>
> | work | author | verifier's passes | sent back |
> |---|---|---|---|
> | CL (f5fc412, fd44a19, 3cc054d, 5320e24; 4e6163f, a401025, ad944e4) | Sonnet 5.5, then the lead | VCL 0, 2; 0, 1; 0, 2; 0, 0 | no: the lead fixed the wording three times, its own in the third pass's two |
> | HC (2f8bee4, d3411ad, bdb62ec, 4187c01; df9ed6d, 6907f0f) | Sonnet 5.5, then the lead | VHC 0, 1; 0, 2; 0, 0 | no: the lead fixed it, and its own words twice |
> | SG (bc962f4; 1f4625b, 42caf81, 6c6534c) | Sonnet 5.5 | VSG 0, 3; 0, 0 | once |
> | FX (e6c31f9, 32d1b86; b6f2493, 6eb1c1b) | Sonnet 5.5, then the lead | VFX 0, 0; 0, 1; 0, 0 | no: the lead restated the entry with VFX's notes, and its own sentence once |
> | DR1 (dcc171b, a07f7c0; 9700b5b, 7445ed6, ab92598, 1f1470b, e579245) | Sonnet 5.5 | VDR1 0, 3; 0, 0 | once |
> | the draw-order fix (1db9592; 5db9ac1, 7583ae2) | the lead | VLD 0, 2; 0, 2; 0, 0 | the lead's own, twice |
> [line 22593 cut: it holds a term from the gate's arithmetic list]
> | XG (six commits to 81aacfa; 8b18ad3, d4527b2, b16d2d8) | Sonnet 5.5 | VXG 0, 4; 0, 0 | once |
> | GS (1093c90, 55be365, 7a197ef; ca8e6b0, 93f882b, 8477471, 3905e62; 3698a8f) | Sonnet 5.5 | VGS 0, 2; 0, 2; 0, 0 | twice |
> | DR2 (b29f996, 32f7ec3, f3c3bc1, 0ae1a13, b5462f7, 8d753f4, 48c40a8, c75d7ce, 1c036ce; 43660c2, f76b7fc, fe4f4b0, 60d435c) | Sonnet 5.5 | VDR2 0, 2; 0, 0 | once |
> | CK (6098f21, 318b597; 98a1ac6, 67fd3f6; 1dd88ac, 5446351; 6395650, f2af491, c66a0a4) | Sonnet 5.5 | VCK 0, 1; 1, 4; 1, 2; 0, 0 | three times |
> | the merges (ca807c6 to 3e02cdf) and this record (1c16d73, restated in place) | the lead | VIW9 0, 0; 0, 0 | no: the lead restated the record with VIW9's notes and the gate's result, twice (Records) |
>
> [line 22600 cut: it holds a term from the gate's arithmetic list]

## 20b. Time and tokens

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the coverage wave, closed", lines 22742-22771. Not in this kit.
- **What it shows** (the kit's reading): One row per agent: its model, passes, minutes for the first pass and in all, tool uses and output tokens, with the method of the count stated first.
- **Cut:** nothing.

> **Time and tokens** (MEASURED, the agents' transcripts: output tokens summed from the last line of each response, tool uses as distinct ids, minutes from each prompt of the lead's to the pass's last line, a message mid-pass splitting nothing in the sum; agent_usage.py and agent_stats.py in the lead's scratchpad):
>
> | agent | model | passes | minutes, first pass; all | tool uses | output tokens |
> |---|---|---|---|---|---|
> | CL | Sonnet 5.5 | 1 | 93 | 237 | 438,730 |
> | HC | Sonnet 5.5 | 1 | 111 | 375 | 510,586 |
> | SG | Sonnet 5.5 | 2 | 135; 155 | 231 | 474,021 |
> | FX | Sonnet 5.5 | 1 | 117 | 128 | 187,107 |
> | DR1 | Sonnet 5.5 | 2 | 86; 157 | 314 | 484,729 |
> | XG | Sonnet 5.5 | 2 | 157; 171 | 678 | 815,942 |
> | GS | Sonnet 5.5 | 3 | 77; 96 | 244 | 321,857 |
> | DR2 | Sonnet 5.5 | 2 | 193; 247 | 623 | 773,998 |
> | CK | Sonnet 5.5 | 4 | 54; 100 | 352 | 443,432 |
> | VCL | Haiku 5.5 | 4 | 28; 42 | 108 | 396,939 |
> | VHC | Haiku 5.5 | 3 | 49; 65 | 263 | 398,767 |
> | VSG | Haiku 5.5 | 2 | 23; 33 | 65 | 297,606 |
> | VFX | Haiku 5.5 | 3 | 54; 65 | 94 | 323,569 |
> | VDR1 | Haiku 5.5 | 2 | 41; 44 | 214 | 380,517 |
> | VLD | Haiku 5.5 | 3 | 19; 29 | 90 | 303,131 |
> | VFD | Haiku 5.5 | 2 | 14; 20 | 73 | 219,385 |
> | VXG | Haiku 5.5 | 2 | 23; 29 | 91 | 329,028 |
> | VGS | Haiku 5.5 | 3 | 22; 34 | 105 | 296,562 |
> | VDR2 | Haiku 5.5 | 2 | 40; 80 | 190 | 388,313 |
> | VCK | Haiku 5.5 | 4 | 22; 67 | 205 | 498,230 |
> | VIW9, the integration verifier | Haiku 5.5 | 2 | 34; 47 | 157 | 420,003 |
>
> - **Sums** (COMPUTED from the rows): the nine Sonnet authors 4,450,402 output tokens, 3,182 tool uses, about 1,246 minutes; the eleven Haiku verifiers of the parcels 3,832,047, 1,498 and about 508 minutes. VIW9's 47 minutes are its first pass (34), its check of the overnight copies (2) and its re-check (11).
> - VDR1's first pass is its transcript's span (41 min), in which it polled its own run about every 15 to 20 seconds; its active minutes sum to fewer.
> - **The time boxes** (reported to Logan on his question): the authors' first passes against their boxes were DR1 86/120, CL 93/240, HC 111/240, SG 135/180, XG 157/240, DR2 193/240, FX 117/90, GS 77/75 and CK 54/75 minutes; the two overruns were small parcels' boxes (90 and 75 minutes). Most went past their briefs' size ceilings, from about 1.2 times (GS, 308 changed lines against "About 80 to 250") to about ten (XG, 3,317 against "a few hundred lines in all"), each size at its report's HEAD. Haiku verifiers' first passes took 14 to 54 minutes of boxes of 30 to 120.
>

---

These passages are excerpts of cft-fp256's docs/VALIDATION.md. cft-fp256 is Copyright 2026 Logan W., under the Apache License 2.0. The kit's NOTICE.md says what else it carries, and under which licence.
