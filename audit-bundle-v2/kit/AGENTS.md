# Working on the project (seed notes)

These are seed agent notes for the project repository, after HonestFramework's template
([method/honest/templates/agent-notes.md](method/honest/templates/agent-notes.md)). Copy them into the project
repository, as AGENTS.md or whatever file your harness reads, and keep them short and true: only what is non-obvious
and has already cost time. P0 writes the front door, and the study writes the authority. Delete an entry the day it
stops being true.

## Start here: one command answers "does it still hold?"

`<P0 writes this: the runner, its budgets, each one's real cost in minutes, and whether a repeated run is cheap.>`

## The authority

`<The study writes this: what defines a correct answer, and what is refused by name.>`

## The machines

`<From docs/HARNESS.md and docs/BOARD.md: where the agents run, and where the board is attached.>`

## What bites, if you run on Logan's Windows desktop

Each of these comes from the agent notes of one of his other projects, where it has already cost time. Each holds
only on that desktop.

1. "**A Python heredoc in Git Bash can lose a backslash** (`\\n` arrives as a newline, `\\` as `\`), and a long one
   can fail on an apostrophe. Write the script to a file and run the file." (QRO-Crate's CLAUDE.md, "What bites",
   item 1.)
2. "**Line endings are part of the bytes.** `.gitattributes` is `* -text`: git converts nothing." Decide your
   repository's line endings in P0, and say which files differ. (QRO-Crate's CLAUDE.md, item 2.)
3. "**Never pipe a long make or test through `| grep | head -N` on this desktop.** It deadlocks at zero CPU with no
   message (2026-09-15, twice in one round). Redirect to a file, then grep the file." (cft-fp256's agent notes.)
4. "**A make recipe on this desktop runs two MSYS runtimes that disagree about `/tmp`.** MSYS2's make runs a recipe
   in its own `/bin/sh`, whose `/tmp` is `C:/msys64/tmp` ... But the `cat`, `rm` and `mktemp` it finds on PATH are Git
   for Windows', whose `/tmp` is the Windows Temp directory." So keep data in the shell, or use a path relative to
   the recipe's directory, or give a `/tmp` path its drive form with `cygpath -m` before anything else reads it.
   (cft-fp256's agent notes.)
5. **WSL cannot read the git of a Windows worktree:** its `.git` file names a Windows path. So a check that reads git
   runs on the Windows side (examples/cases/19-what-the-brief-got-wrong.md, 19a).
6. **No agent loads the machine on purpose** (OWNER.md, rule 9). Run one heavy job at a time, and when a run was made
   under load, say so.
7. **In Git Bash, `/tmp` is the Windows Temp directory, which other sessions share.** Delete only what your run
   created, by its exact path (OWNER.md, the leads' rules; examples/cases/07-conduct.md).

## The discipline that matters most here

`<One paragraph, from the study: the one thing that, if forgotten, makes the work wrong rather than late.>`
