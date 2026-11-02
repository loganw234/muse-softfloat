# What the brief got wrong

ParcelRound METHOD.md section 3: every parcel's report ends with anything it found that its brief got wrong.

## 19a. A parcel's list

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the stress driver's sweep reorganised", lines 22478-22487. Not in this kit.
- **What it shows** (the kit's reading): What the brief got wrong, the size among it.
- **Cut:** nothing.

> **What the brief got wrong:**
> - **Its file list** left out hw/card_stress_standin.py, hw/test_card_stress_report.py and hw/test-card-stress.sh. The pool needed lines in the stand-in (what a soak job was handed, so that a test can see a host job got neither variable; later the rule `badenc`); the report's own test lists the report's sections (eight now), and since test_card_stress.py runs that test as a plants control, leaving it would have turned the control red; the wrapper's header names the groups.
> - **"About 300 to 600 changed lines with tests"** was a third of what the three parts and their plants took: 1,929 insertions and 165 deletions in eight files (a07f7c0 to b5462f7, the tip before the merge, counted before this entry and the README), 1,753 and 140 of them in the six Python files, and 22 new plants (43 at a07f7c0, 65 at b5462f7; 68 after the merge, with DR1's three). The lead accepted the size.
> - **"The run records the RTL tree: `git rev-parse HEAD:rtl` of the tree it runs from"** is the checkout's tree, which the brief does not say differs from the images' in general; it also says nothing of a host where git cannot read the tree (WSL on a Windows worktree), where the record is null and the suite's one check of it is skipped by name.
> - **"n for each item then starts above the highest n those directories used"** I read as the highest n of a completed slice (the report's own `highest_seed_n` and `sweep_coverage` read it so); a slice that did not complete is served again by its own run.
> - **"(item index << 40)"** did not say index in what. By the catalog's position it would shift when a probe drops items; I used a table by name, and the catalog refuses an item that is not in it.
> - **"Host items run ... all through the run"** did not say what `--quick` does: the smoke serves three host items once each and waits for them, or the host items named by `--sweep-items`.
> - **It did not say what the report's "on the card" time does with the pool's legs;** left alone it would have counted them, and been near 100 per cent for ever.
> - **"Run the full suite and `--no-plants` from Git Bash or WSL"** did not say that WSL cannot read the git of a Windows worktree (its .git file names a Windows path), so that the tree-record check cannot run there; the Windows run is the one that does it.
> - **"A plant red then green for each"** is a check at one moment; the brief did not say that a later change can leave a plant meaningless (the lesson above). The plants stage is where that is found, and only if its output is read for "applies ... found 0 times" and "caught by nothing".

## 19b. A suggestion that would have made a check unable to fail

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the stress driver's three fixes", lines 22206-22211. Not in this kit.
- **What it shows** (the kit's reading): What the brief got wrong, one suggestion of which would have made a check unable to fail.
- **Cut:** nothing.

> **What the brief got wrong:**
> - **"Every telemetry call takes a value from the stand-in's counter":** a call in the test takes four, one for each examine call (electrical; thermal; mechanical as JSON and as text), and the temperature is the thermal one's, so consecutive samples step by 2.0.
> - **The record's two suggestions** ("take the stand-in's temperature from the call's own sample, or compare in counter order") cannot work, as above: the stand-in knows no sample, and a counter order is a temperature order, so the second makes the check unable to fail. The brief's own alternative, fixing the driver, was the right one.
> - **"About 100 to 300 changed lines in all"** had an upper figure about half of what three fixes took when each wants a check and a plant; it also came before the lead's two added checks.
> - **The brief's wording of (a)** ("the first two on a single image") can be read as the same two items on every image; the rotation (above) is the better rule and is not that.
> - **It did not say that the lock can lengthen stopping.** The lead asked about the lock's worst case after the brief; the stop rule above is the answer.

## 19c. The author's own drafts

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "a design study of the card scheduler", lines 22864-22869. Not in this kit.
- **What it shows** (the kit's reading): What the author's own drafts got wrong, and what changed, before the first commit.
- **Cut:** nothing.

> **What my own drafts got wrong, and what changed** (before the first commit):
> - `latency.py` first grouped a cycle's sweep legs into waves by a five-second start rule and found 102 waves where the legs' own `jobs` field gives 105; the grouping is now by overlapping intervals, held to the sum of 1/jobs, with a plant.
> - `coverage_state.py` first read a pace from the last six hours and said that only the four wide items ran in them; the other items ran until 11.9 of the 12.4 hours. The method is now the file's slot-seconds with a range, and the false sentence is gone.
> - `guard_probe.py`'s control first put `.xclbin` into the lead's pattern and overstated what it flags; it now uses the lead's pattern alone.
> - `script_census.py`'s HEAD pattern also matched `HEAD:rtl`, found by its own positive and negative lines.
> - In the study: the end of the finite campaign (to 2026-10-29 with the preamble counted), a year of run directories (2.2 GB: the `du` includes the metrics), the report's limit (about 2 GB, not 1.6), the `dt-i` pair (13 to 21 s, not 30), "four days" for the 24 hours between 881bbcb and 0b7c959, the lead's A/B marked READ and not MEASURED, a sentence on both ends of the transport that had no support, the telemetry share ("three fifths to two thirds"), and a second driver "refused by the guard" (now BELIEVED, with its reason).

---

These passages are excerpts of cft-fp256's docs/VALIDATION.md. cft-fp256 is Copyright 2026 Logan W., under the Apache License 2.0. The kit's NOTICE.md says what else it carries, and under which licence.
