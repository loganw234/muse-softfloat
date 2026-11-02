# The clean room

**One repository is off limits: Logan's cft-fp256.** In his words (2026-10-23): "Web access to read third-party
code and solutions, the only restriction is staying away from cft", and "cft-fp256 only, as thats the only project
where code could be copied from".

Why: cft-fp256 already implements binary32 and binary64 arithmetic, with the same source on every target. It
compiles for the RP2040, though it has never run on one. Its code would answer the question this hackathon asks
you to answer, and the measurement of how you work would then measure nothing.

## What counts as cft-fp256

- the repository named cft-fp256 on Logan's GitHub account, in any form: its pages, its raw files, its API, its
  archives, and any fork or mirror of it;
- its project site, on GitHub Pages;
- a copy of it shown through another repository, such as a submodule's view;
- pages of Logan's site that show it. This is the lead's reading of "staying away from cft", and Logan may correct
  it. That is why, wherever the kit's texts name the site, they name it as text, not as a link (rule R6).

Nothing else of Logan's is restricted.

## A copy on the machine

A clone of cft-fp256 on a machine the agents use counts as cft-fp256. Some harnesses put files into an agent's
context by themselves: agent notes, project instructions, the files of a directory they were given. So no clone of
it sits in, under or beside any directory an agent or its harness is given, and none is among what a harness loads
on its own. The lead checks this with Logan on day 1, and docs/HARNESS.md records what the harness loads by itself.

This kit's own cold read met the case (MEASURED, 2026-10-23): the harness that built the kit loaded cft-fp256's
agent notes into a reader's context, because the repository was attached to that harness's session. The reader
disclosed it before anything else, as below.

Every third-party source is open to read: the literature, Berkeley SoftFloat and TestFloat, pico-sdk, MPFR and
others. Before you copy from one, record its licence (PROJECT.md, question 8).

## If a search lands there

Do not open it. Searching for an RP2040 softfloat could surface it; that is BELIEVED, and not tried.

If you opened it:
1. Stop.
2. Write the URL, and what you saw, in your own ledger file.
3. Escalate to the lead. The lead tells Logan.

This is judged on disclosure, as ParcelRound judges a crossing of a boundary
([method/parcelround/METHOD.md](method/parcelround/METHOD.md), section 3: "judge a crossing on whether it was
disclosed and reasoned, not on whether it happened"). A disclosed crossing is a fact in the record, and the work goes
on from it. A hidden one is what the audit below is for.

## What the kit carries of it

None of its arithmetic, and none of its code but what its record quotes of its tooling where a situation needs
it: names of its files, functions and commands, and short expressions of its tests and its runner, as in samples
3a, 9b and 18a. The kit carries:
- passages of its record that show how situations were handled (examples/cases/), with any line that names its
  arithmetic cut;
- short quotations of its record in OWNER.md, GLOSSARY.md and METRICS.md, each cited by its line, sample or header;
- two entries of its agent notes, about Logan's desktop, in AGENTS.md.

The gate's check 3 reads each of those files, and the builder read each whole.

ParcelRound's texts and QRO-Crate cite it by file and line; those citations dangle by design. The kit's gate refuses
a URL into it in the forms check 2 lists, a fork's on GitHub among them, with backslashes and percent-encoding undone
first, in every file, every archived ledger and every commit of the QRO-Crate bundle (`python3 -I tools/check_kit.py`,
check 2). Not on its list: a mirror on another host, a fork under another name, and a copy shown through another
repository, such as a submodule's view on GitHub. The rule above, and disclosure, cover those.

## The audit

Logan checks the project repository against fingerprints of cft-fp256's sources, at each wave's close and at the
end. The fingerprints are not in this kit. A match decides nothing by itself; it opens a question, and the record
answers it.

## The standard

Logan gives the lead the IEEE 754 standard as a PDF, outside the kit. It is licensed to him, and it is the contract:
what the work must do. It is not the authority the gates compare against (PROJECT.md).
