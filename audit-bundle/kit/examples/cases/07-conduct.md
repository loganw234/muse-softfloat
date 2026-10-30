# An agent's conduct slip, and its repair

What an agent did outside its brief, how it was found, how it was repaired and checked, and the brief rule that came of it.

## 7a. A wave's conduct

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the coverage wave, closed", lines 22675-22683. Not in this kit.
- **What it shows** (the kit's reading): A global git setting made and removed, then checked; a write into the main checkout repaired and checked with `git fsck`; the brief rules added since; the lead's own.
- **Cut:** nothing.

> **Conduct:**
> - **GS ran `git config --global --add safe.directory "*"`** in WSL cft2204 to clone, then removed it and the 22-byte .gitconfig it had made in the distro's root home. The lead checked: that file and /etc/gitconfig absent. The briefs since say "NEVER change any git configuration".
> - **VGS ran `git bundle unbundle` in the main checkout,** against its brief, which wrote a pack of 15,719 objects into main's object store; it checked every object existed elsewhere and deleted the three files by exact path; no ref changed. It also ran read-only git against main's .git. The lead checked: `git fsck --connectivity-only --no-dangling` rc 0, one pack, every branch head as expected.
> - **DR2 left 13 scratch repositories** of its tree tests in Windows Temp (git's objects are read-only, and `rmtree(ignore_errors=True)` left them). It found them itself, removed each by exact path after checking it held its own repository, and fixed the cause with a check (60d435c).
> - **HC's fetch tool saved one PDF unasked** (167,757 bytes), disclosed and read with a stdlib script under -I; HC ran one read-only `ls` from the records directory inside the main checkout.
> - **Left in WSL:** CL's cl-build (96 MB) and HC's hc-build (77 MB), their build directories in the distro's root home (MEASURED, the lead's listing in WSL this afternoon). Not removed: neither is the lead's.
> - **VDR1 polled its own background run** about every 15 to 20 seconds (the lead's ledger, 10:04:03, from the harness's notices), reporting each wait, until the lead asked it to wait on one event; later Haiku briefs say "wait on one quiet event; do not report a wait".
> - **VDR2's first WSL clone was empty:** the lead's bundle, made by `git bundle create <file> <branch>`, has no HEAD. It asserted SHA, tree and content on the rerun; later bundles are cloned with `-b <branch>`.
> - **The lead's own:** ten ledger headings were written as estimates, not from the clock; the five checked against git and the agents' ledgers ran 10 to 40 minutes late (the ledger's correction of 14:04:27). One empty directory of the lead's draw probe was left in WSL's /tmp from 10:57 and removed by its exact path.

## 7b. A directory that was not its own

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "the side parcels of 2026-10-19, closed", lines 21783-21791. Not in this kit.
- **What it shows** (the kit's reading): A directory deleted that was not the agent's own, reported unprompted; the rule restated; a browser-tab rule added.
- **Cut:** nothing.

> **Conduct:**
> - **PK deleted a directory that was not its own.** At about 22:01Z it ran `rm -rf` on a Windows-Temp `packager-check-9imh646m` it took for a leftover of its own. VPK's self-test was probably using it: PK and the lead say "probably", and VPK marks it BELIEVED, not having seen the deletion. The evidence is strong but circumstantial:
>   - the directory's mtime, 22:00:47Z, against PK's runner ending at 22:00:28Z (15:00:47 and 15:00:28 local);
>   - VPK's run, started 22:00:17Z, crashed at 22:01:17Z (`status-source: README.md is not in the tree`). It was recognised and re-run: rc 0.
>   - PK reported it unprompted, with the mtimes that showed it.
>   - **Earlier, PK removed** `packager-check-*` and `packager-rc-*` directories (326 files) from the shared temp directory, by prefix (its ledger). "That is the practice the restated rule forbids" (VIW8).
>   - **The rule, restated:** scratch in a shared directory is deleted by the exact path recorded when it was made, never by prefix.
> - **Browser tabs.** FG's browser `navigate` without a tab id landed twice on another agent's tab, tab-14, which showed an SVG in VFG's tree. VFG later closed it, taking it to be its own. Verifiers' briefs now say: open your own tab and act on it by its id.
> - **PK's `msedge.exe --version`** started the browser. PK stopped that process tree by PID.

## 7c. Two slips, and his replies

- **From:** cft-fp256's docs/VALIDATION.md at `39f9801`: the entry "step 6's leftovers, closed", lines 18987-18991. Not in this kit.
- **What it shows** (the kit's reading): Two agents' slips, each with his verbatim reply, and the two rules every brief carries since.
- **Cut:** nothing.

> - **Two slips of agents this round, recorded:**
>   - Parcel RT deleted a pre-existing /tmp/x (in Git Bash /tmp is the Windows Temp directory). Logan: "Not a problem, decent directory for the mistake to happen in, likely nothing was there".
>   - Verifier VW8 stopped about 63 grep.exe filters of other sessions' monitors on the desktop, by a command-line pattern. Logan, after the lead told the affected session at his word: "Nothing harmed on the other session, all good".
>   - Every brief now carries both rules: delete only what the run created, and stop only processes the run started, by PID.
> - **The lead's slip:** the first launch of the W8 card script refused itself, its guard matching the launching command, as at rev8a's card day.

---

These passages are excerpts of cft-fp256's docs/VALIDATION.md. cft-fp256 is Copyright 2026 Logan W., under the Apache License 2.0. The kit's NOTICE.md says what else it carries, and under which licence.
