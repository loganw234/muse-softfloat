# A verifier's notes not taken, with reasons

A note that does not send work back is still answered: taken, or not taken with a reason, in the record.

## 18a. The verifiers' other notes

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "CI's RTL suite as three parallel jobs", lines 21023-21036. Not in this kit.
- **What it shows** (the kit's reading): The verifiers' notes not taken, each with its reason: "The lead takes the trade".
- **Cut:** nothing.

> **Known limits** (the verifiers' other notes, not taken):
> - **The docs check:**
>   - On a tree whose SIM_BENCHES it cannot expand, three prose controls also print NEGATIVE CONTROL FAILED TO FAIL (VCI's note 3, its second half). It is a failure path, rc 1 either way, and its first line says why.
>   - It reads `# comment` text as values (VCI2's note 5): `SIM_GROUPS = 1 2 3 # the groups` is refused as "cannot expand", and `SIM_GROUP_2 = # emptied` counts two benches. In VCI2's words, after its re-check of this entry: "Pre-existing. In the cases tried it fails closed or gives a false alarm; it is no guarantee, since a bare trailing `#` can stand in for a removed bench and pass."
> - **The order costs a parallel run time** (VCI2's note 3, COMPUTED from the CI times):
>   - In VCI2's words: "From the CI per-bench times, `make -j4 sim` is about +591 s against 5eb35c2's order and about +232 s against d3fef4b's (+82 s at -j8)."
>   - verify/run.sh's sim stage runs `make -k -j"${SIM_JOBS:-1}" sim`, and under -k the order changes nothing about when a failure is reported.
>   - The lead takes the trade. CI's group jobs run serially, without -k, and there a broken quick bench in group 1 or 2 now stops its job after 115 to 170 s on average, where it waited about 5,300 s behind the long bench, at the faster pace; at the slower, 155 and 226 s against about 6,800 s (VCI2, COMPUTED).
> - **Group 3 still waits behind krnlseq,** which is not in SIM_LAST (VCI2's note 4, COMPUTED): a quick bench's failure there comes after a mean of 2,022 s and at worst 2,568 s at the faster pace.
> - **The unlisted-group refusal's small behaviours** (VCI2's note 6):
>   - it names the SIM_GROUP_<n> variables, in `.VARIABLES` order;
>   - an exported SIM_GROUP_9 in the environment triggers it;
>   - `SIM_GROUPS = 1 2 3 3` is refused as group 3's benches being in two groups.
> - **A plain `make -n` of the suite is not a faithful plan** (VCI2's note 7): the bench recipes contain `$(MAKE)`, so the checker's tail runs for real and stops at the first bench. `make -pq` or `-nk` is.

## 18b. An integration verifier's notes

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the coverage wave, closed", line 22783; the entry "the coverage wave, closed", line 22790. Not in this kit.
- **What it shows** (the kit's reading): An integration verifier's notes not taken, each with its reason.
- **Cut:** nothing.

>   - **Not taken:** the single quotation marks nested inside three double-quoted quotations (the words are verbatim, VIW9's note); its notes on what it did not check, which its ledger lists.
> [...]
>   - **Not taken:** card-stress's log totals 658 checks where its group lines sum to 584; in VIW9's reading, its plants print no group total. The record quotes the log's own total. The bundle's sha256 and the chip cannot be shown from the copies.

---

These passages are excerpts of cft-fp256's docs/VALIDATION.md. cft-fp256 is Copyright 2026 Logan W., under the Apache License 2.0. The kit's NOTICE.md says what else it carries, and under which licence.
