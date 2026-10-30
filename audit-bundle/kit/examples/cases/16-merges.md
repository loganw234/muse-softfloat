# Merges recorded, and what a merge exposed

ParcelRound METHOD.md section 7: the integration verifier makes each merge again, from its parents, with git merge-tree.

## 16a. Each merge's conflicts, recomputed

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the coverage wave, closed", lines 22619-22638. Not in this kit.
- **What it shows** (the kit's reading): Merges recorded, their conflicts recomputed with `git merge-tree` from each merge's two parents.
- **Cut:** 4 line(s): 22624 (a term from the gate's list); 22629 (a term from the gate's list); 22630 (a term from the gate's list); 22635 (a term from the gate's list).

> **The merges** (MEASURED, the main checkout; READ, each merge's message for its checks: `check_docs_index.py` and `project_figures.py --check` rc 0 at every one, 60b363e's two run on its branch before a merge with no conflicts; `git diff --check` clean at every one but 60b363e, whose message does not say; the conflicts recomputed for this record by `git merge-tree` of each merge's two parents):
>
> | merge | of | conflicts, resolved by keeping both sides and recounting |
> |---|---|---|
> | ca807c6 | CL (classes at ad944e4) | none |
> [line 22624 cut: it holds a term from the gate's arithmetic list]
> | c1e5413 | SG (sweep-sign at 6c6534c) | VALIDATION, README |
> | c9741e0 | FX (figures-crlf at 6eb1c1b) | VALIDATION, README |
> | 330bdeb | DR1 (driver-fixes at e579245) | VALIDATION, README |
> | aa62f14 | the lead's draw-order fix (lead-draw at 7583ae2) | VALIDATION, README |
> [line 22629 cut: it holds a term from the gate's arithmetic list]
> [line 22630 cut: it holds a term from the gate's arithmetic list]
> | 2c188c9 | GS (gate-skips at 3698a8f) | VALIDATION, README |
> | 9255ab8 | DR2 (driver-coverage at 60d435c) | VALIDATION, README |
> | 3e02cdf | CK (soak-chunk at c66a0a4) | VALIDATION, README |
>
> [line 22635 cut: it holds a term from the gate's arithmetic list]
> - **DR2's branch carried DR1's second pass** (its merge 8d753f4 of driver-fixes at e579245), which main already had (330bdeb); those commits brought no conflict of their own.
> - **The docs check during a merge:** while a conflicted file is still unresolved in the index, `git ls-files` lists it once per stage, and the check said "74 tracked documents, 235 links" against 70 and 131 once resolved. Its rc was 0 either way; cosmetic.
> - **No `__pycache__` written today** in the main checkout: none of its 15 such directories (outside .venv and Data) holds a file newer than 2026-10-20 00:00 (MEASURED, `find -newermt`, after DR2's merge).

## 16b. A silent fallback, exposed by a merge

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the nightly progress page", lines 23643-23647. Not in this kit.
- **What it shows** (the kit's reading): A merge that exposed a silent fallback, and the fix: "an error from the report is a failure, not a fallback"; plants shown red in scratch copies.
- **Cut:** nothing.

> **After parcel RG's merge.** Parcel RG is in main (`acfd6d15`), and the lead merged main into this branch at `ddeef8ac`, where the test gave 341 checks and 1 failed. The first passes' figures above are kept; these are the new ones.
> - **What broke, and why it was silent.** RG changed the report's private `_tree_class`. The reducer's `_empty_class` called it inside a `try/except Exception`, with the lib's `tree_key` as the fallback, so it fell back without a word: a current class nothing was swept under got the label `host tree d4d4d4d4d4d4` where the report says `host/ tree d4d4d4d4d4d4, compiler cc (Fixture) 1.0`. Only a fixture expectation, written against the old label, saw it.
> - **The fix.** RG's public `tree_class(kind, run_start, rev)` is the call, and `_empty_class`, its `try` and the `tree_key` import are gone: an error from the report is a failure, not a fallback. The limit "no public way to place a class nothing was swept under" goes with it, and RG's contract is seen, not believed: `rev` is on by default in `summarize()` and in `tree_class()`, `rev=None` is the CLI's `--no-git`, a function given for `rev` is the "given rev" view, and `derived_from_git` is a list of {commit, dir, tree}.
> - **The relabel is gone.** `register()` reworded an unrecorded tree as "commit X, tree not recorded in the run". The report's label now names the commit and `resolve_tree`'s reason, and says "unknown" for a recorded tree that git contradicts, which that wording would have called "not recorded", and that is false; the page shows the report's label as it comes. **A reason could carry a path or a host:** the label of a class kept apart ends in `resolve_tree`'s reason, and `[git: ...]` carries what stopped git, so the publish refusal applies, and a plant holds it (a rev whose git stopped with a message naming a directory is refused by name and not published). **The labels of the real copy** (READ in the new data file): `RTL tree 44b963dd6ba2 (read from git at commit 881bbcb676bb)`, `host/ tree 276ed15a3019 (read from git at commit 881bbcb676bb), compiler not recorded` and `host/ tree 4d9905f82759, compiler cc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0`: none carries a reason, a path or a host.
> - **The tests.** The fixture's label expectations follow the report (`tree_class(..., rev=None)`), and each served class's label is compared with `--json`'s on every copy. The stand-in is gone: the real report is given a function for `rev` that reads night 1's tree, and the tile class then spans the three nights and carries `derived_from_git`, held to the oracle. A plant makes `tree_class` raise, and the reduction must fail. The check group makes its data file with the command, so that `--check` re-derives it in the view it was made in (the command's default reads git of the checkout, whose reasons the labels of made-up commits carry). **Red, in scratch copies:** with the fallback put back, the raise plant fails; with the relabel put back (the first passes' block verbatim, and my scratch variant with a constant label, which fail the same checks), **four** checks fail without the real copies named (MEASURED: 372 checks, 4 failed, 1 skipped): the fixture's shared-figures check, naming the two class-label rows t1 and h1; its two label checks (a class's label is the report's own, and an unrecorded tree's label names the commit as the report writes it); and the git-problem plant, since the reword hides the path and nothing is refused; and **six** with the two copies named, in a scratch copy outside the repository (388 checks, 6 failed): the shared-figures check of each copy is added, because with no git there night 1 stays an unrecorded class, which the reword then reaches (my first count, six, was this second case; verifier VNP's four is the first); with the path guard off, the git-problem plant fails (with the older leak plants).

---

These passages are excerpts of cft-fp256's docs/VALIDATION.md. cft-fp256 is Copyright 2026 Logan W., under the Apache License 2.0. The kit's NOTICE.md says what else it carries, and under which licence.
