# A failure shown not to be a regression, or not a defect

ParcelRound METHOD.md section 7: never call a failure a defect or a false alarm until a clean re-run says which.

## 8a. Four fresh clones, the tip and the base

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the coverage wave, closed", lines 22655-22663. Not in this kit.
- **What it shows** (the kit's reading): Two failures shown not to be a regression: four fresh clones, at the tip and at the base, built and unbuilt.
- **Cut:** 3 line(s): 22655 (a term from the gate's list); 22659 (a term from the gate's list); 22662 (a term from the gate's list).

> [line 22655 cut: it holds a term from the gate's arithmetic list]
>     - The clone's status after the suites: 0 lines.
>   - **The two card-stress failures are not a regression** (MEASURED, box_br_ab.sh, sha256 eb65cf82...; 18:58:28 to 18:59:56; four fresh clones from the gate's bundle, each one's HEAD and clean status recorded in its summary; the logs copied with the box's sha256s into box/wave9/brab/, every copy equal). `bash hw/test-card-stress.sh --only buildreal`, which needs no card, in each:
>     - 9255ab8, nothing built: 7 checks, 0 failed;
> [line 22659 cut: it holds a term from the gate's arithmetic list]
>     - 881bbcb, before the wave, built the same way: 2 failed, the same two, after the same event;
>     - 881bbcb, nothing built: 7 checks, 0 failed.
> [line 22662 cut: it holds a term from the gate's arithmetic list]
>   - **The lead's:** box_wave9_gate.sh ran the suites in the gate's clone after the gate had built host/ there. The stress run's dry tests run in a fresh clone before anything is built (the 2026-10-19 run's: "481 checks, 0 failed, 0 skipped"), so they are not affected.

## 8b. The check was frozen

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the card stress driver before the nights run it", line 23413. Not in this kit.
- **What it shows** (the kit's reading): A failure on the box traced to a check frozen on old data: "The planner and the tally were right; the check was frozen". The check now derives what it expects.
- **Cut:** nothing.

> - **The lead's added row (2026-10-22, found on the box): DR4's `resume real` check was frozen on the two-night file.** The check (`resume_real_checks`, run when `CARD_STRESS_RESUME_RUN` names a directory with the stress run's `metrics.jsonl`) asserted the two-night file's own numbers, so on the box at `f707fa3b` with the three-night copy 4 of 869 failed, all `resume real`. **MEASURED here with both real files** (copied from `box/resume-1020/run` and `box/nightly-1021/run`, read only; sha256 `38f243c7...` for 1,308 lines and `de4ee379...` for 1,910, each equal to the box's SHA256SUMS.box), the function the group calls run in-process: the BASE's test file on the two-night copy 6 checks, 0 failed; **on the three-night copy 6 checks, 4 failed** - "two run_starts ... 552 finished sweep slices" got (3, 756); the whole-file plan and the resumed plan got the four wide gaps 1,519,386,624, 1,541,406,720, 1,537,212,416 and 1,544,552,448 (0x5a900000, 0x5be00000, 0x5ba00000, 0x5c100000, the nightly's own `first_uncovered`) where the two-night file's were expected; "320 tile slices counted" got more. The planner and the tally were right; the check was frozen. **Now the check derives what it expects from the file itself:** the run_starts and the finished sweep slices scanned from the records; each run's rtl/ and host/ trees as recorded or git's for its commit; the slices of the resumed class counted and their intervals merged here (the resume stays at the second run's commit, `0b7c959`, as before); the whole file's first gaps from `docs/studies/sched-a/coverage_state.py` run on the file (it holds its union to an independent merge; 0.75 s); the unknown-class tally from the run_starts without a compiler. **The figures measured on the lead's two files are held exactly, only for a file whose sha256 is theirs** (two nights: 2 run_starts, 552 slices, 320 tile slices counted, the first run's 232 host slices unknown for "compiler not recorded", the committed capture's four gaps; three nights: 3 run_starts, 756 slices, 524 tile slices counted, 0 host counted, the same 232 unknown, the four gaps above). **MEASURED after the change: the two-night copy 9 checks, 0 failed; the three-night copy 8 checks, 0 failed. With a planted wrong plan** (`pick_item` forgetting the last interval of every item) **it is red on both, 3 checks each**; the plant is in the suite (skipped by name unless `CARD_STRESS_RESUME_RUN` is set, which is when it can go red).

## 8c. A test that encodes the card's image

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "step 6's closing records, part one", lines 18310-18313. Not in this kit.
- **What it shows** (the kit's reading): A failing check read as "a test that encodes the card's image, not a defect", with the negative control failing as it must.
- **Cut:** nothing.

> - **card-segrun, its first run** (hw/card-segrun.sh at 688b653, 01:02:48 to 01:05:37, 169 s; card-segrun.log, card-segrun-gate1.log): **6 checks, 1 failed**; its gate, segrun_check, 678 checks, 2 failed, 0 skipped, 104 s.
>   - The two are one case of section 14's card leg (h): "f. refused device (exit 69): the per-lane block asked of a revision-7 tile (CAPS2[13] clear) - exit 0, no refusal named", and its follow-on, "and no certificate, the files written before the refusal left and said so". The negative control, device-test's SHA-256 handed as the image's, failed the device lines by name, rc 1, as it must.
>   - Everything else passed on the revision-8 tile. Among it is markstep, which q135b refused at load (RAISE, CAPS2[14] clear; box/w3-card-4449c49/card-segrun.log): keyed and open, "the segment lines carry flags [6, 3, 2, 31, 30] and STATUS [64, 64, 64, 0, 0] - the mark, STATUS[6], reached the certificate", and every run block is the software backend's, byte for byte (card-segrun-gate1.log). So a tile on a card set STATUS[6], measured, for the first time; simulation had measured it on 2026-10-05 (krnl_flag_control's STATUS 0x40, the round-2 entry above).
>   - **The lead's reading** (lead.md, 01:16:23): a test that encodes the card's image, not a defect of the tile or the tool. hold_card (host/tests/segrun_check_v2.py:1293 at 688b653) was written while the card held revision 7's quad, and always expected `--lane-flags` refused. rev8a publishes CAPS2[13], so cft-segrun rightly ran the block and wrote the certificate (exit 0). The other 676 checks of the card leg passed (COMPUTED, 678 - 2).

---

These passages are excerpts of cft-fp256's docs/VALIDATION.md. cft-fp256 is Copyright 2026 Logan W., under the Apache License 2.0. The kit's NOTICE.md says what else it carries, and under which licence.
