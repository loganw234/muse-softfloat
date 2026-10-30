# Skips named and counted

HonestFramework METHOD.md section 5: a stage whose tools are missing is skipped by name, with its reason.

## 11a. A gate's skips, by name

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "M1's build, seventh wave, closed", lines 21352-21363. Not in this kit.
- **What it shows** (the kit's reading): A gate's skips, each by name with its reason, the same as the earlier gates'; its clone asserted before the run.
- **Cut:** 4 line(s): 21352 (a term from the gate's list); 21353 (a term from the gate's list); 21361 (a term from the gate's list); 21363 (a term from the gate's list).

> [line 21352 cut: it holds a term from the gate's arithmetic list]
> [line 21353 cut: it holds a term from the gate's arithmetic list]
>   - "36 stage(s) executed, 0 cached from earlier in the run, 0 failed, 8 skipped". 36 and 8 make the budget's 44.
> - **Its clone,** asserted before the run (READ, the run's summary): HEAD df7dc43cd59d1c5f6f06f0b9f7b44ea02bcd8a79, a clean status, rtl's tree 44b963dd6ba2fcf99e002c5face5ca94aad4515c, one hit each for a string of rev8-routines, rule_compare, the sim groups and the stress record, and no branch outside main's ancestry.
> - **The skips,** each by name:
>   - buildargs: "a real Vitis at /data/Xilinx is sourced by rebuild-2022.sh and takes PATH from the stub";
>   - lang-rust, lang-julia, lang-go, lang-csharp, lang-r and lang-fortran: "no rustc", "no julia", "no go", "no dotnet", "no Rscript" and "no gfortran on PATH";
>   - demos: "no node on PATH".
> - **The inner skips:**
> [line 21361 cut: it holds a term from the gate's arithmetic list]
>   - remote's WebSocket leg, "no node on PATH".
> [line 21363 cut: it holds a term from the gate's arithmetic list]

## 11b. A verdict line that counts its inner skips

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the card stress driver before the nights run it", line 23427. Not in this kit.
- **What it shows** (the kit's reading): A verdict line that counts its inner skips, each named with its reason.
- **Cut:** nothing.

> - **The stage, Windows, with the timing groups skipped by name** (Git Bash, at `a8de4401`, 08:10:53, under the lock): `cardstress ok 600s + 10 inner skip(s)`, **`VERDICT: PASS with 10 inner skip(s) in cardstress (10)`**; the suite's line "853 checks, 0 failed, 10 skipped, 599 s". The ten skips, each named with its reason: `deaf`, `stopfile`, `guard`, `buildreal`, `signal`, `pool`, `records args (POSIX)`, `records real`, `fx filter`, `resume real` (the stage's log, kept in this parcel's scratch directory).

---

These passages are excerpts of cft-fp256's docs/VALIDATION.md. cft-fp256 is Copyright 2026 Logan W., under the Apache License 2.0. The kit's NOTICE.md says what else it carries, and under which licence.
