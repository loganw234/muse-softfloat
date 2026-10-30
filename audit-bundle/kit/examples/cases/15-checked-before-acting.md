# A report checked before the lead acts on it

ParcelRound METHOD.md section 4: verify an escalation like any other report.

## 15a. His question on a parcel's time

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the side parcels of 2026-10-19, closed", line 21717; the entry "the side parcels of 2026-10-19, closed", lines 21729-21733. Not in this kit.
- **What it shows** (the kit's reading): His question on a parcel's time, answered from its ledger and transcript, and the brief rule that came of it.
- **Cut:** nothing.

> - "PK has been going for over 4 hours, check in on their progress and what might be taking so long"
> [...]
> 7. **Logan's question on PK's time,** answered from its ledger and transcript:
>    - the brief asked for five plants, and PK built a 260-mutation harness at about 27 s a `--check`, about two hours of compute;
>    - it also built a 210-control self-test, a stdlib PNG reader, an HTML page and an independent audit;
>    - the desktop was shared and niced, and the lead's CI constraint arrived mid-run.
>    - Briefs now carry a scope ceiling and a time box.

## 15b. Two suites that collided

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the card stress driver's resume counted per tree class", line 23000; the entry "the host pool's slices as signed sweep records", line 23041. Not in this kit.
- **What it shows** (the kit's reading): One parcel's measured collision with another's suite, relayed by the lead; both sides discount the overlapping runs.
- **Cut:** nothing.

> - **Two driver suites in one distro collide through the guard** (READ, the lead's message of 2026-10-21, which gives it as parcel SR2's measurement at 13:54): the driver's guard scans every process in the distro, so the stand-ins of two suites make each other's drivers refuse to start (`guard_refused`, rc 2, a run with no records, IndexErrors after it). My first whole-suite run in WSL (13:46, the bundle of 0bb856f0) overlapped SR2's driver runs (13:47 to 13:55): I had stopped it by PID at 13:55:50 to restart at the final code, none of its group lines had a failure (kept in scratch), and it is NOT counted; the run in the first bullet above started at 13:56 from a clean clone, after SR2's, and nothing else ran drivers in the distro while it did (the same rule on the Windows desktop for the `--no-plants` run and the plants' driver scenarios after it).
> [...]
> - **Two driver suites in one WSL distro collide through the card guard**, which scans every process of the distro: a fresh dry driver run ended in 0.1 s, rc 2, with `event guard_refused: pid ... CFT_SOAK_ARTIFACT=cft_hw_quad.xclbin` while another parcel's suite was alive (MEASURED 13:54: its driver, a `plant-control` run of the plants stage, was in `ps`), and the guard works both ways. **This parcel's runs between about 13:47 and 13:55 (the plants one at a time, the `records` group three times, two debug runs) overlapped DR4's whole suite, which the lead says started about 13:50**, and may have made its drivers refuse to start; the lead holds every run until DR4 is done.

---

These passages are excerpts of cft-fp256's docs/VALIDATION.md. cft-fp256 is Copyright 2026 Logan W., under the Apache License 2.0. The kit's NOTICE.md says what else it carries, and under which licence.
