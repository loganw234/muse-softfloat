# The board

A Pico is "constantly connected for debugging", and "Lead controls hardware access" (Logan, 2026-10-23). This file is
the protocol, and a template for the details. Fill a copy of the details on day 1, with Logan, as docs/BOARD.md in
the project repository; this file stays as it is.

## The protocol

- **The lead holds the board.** A parcel that needs board time asks the lead by the escalation channel. The lead
  runs the job itself, or grants a slot by name and by time. One holder at a time.
- **The lock is a file:** `<ledger>/board.lock`, holding the holder's name, the job, and the time from `date`. Take
  it before touching the board, and remove it by its exact path when done. A lock the holder did not write is not
  theirs to remove.
- **Every board result names its artifact:** the ELF's sha256, the commit it was built from (asserted for its SHA and
  its content apart: HonestFramework [METHOD.md](method/honest/METHOD.md), section 6), the build's flags, and the
  board's id. A result that cannot name these is not evidence.
- **A board run goes in the record** like any other run: the command, its output, and what it showed.
- **Long runs are the lead's** (OWNER.md, rule 2, if it applies), and they run at hours that do not load a machine
  someone else is using (rule 9).
- **A board result is checked against the authority,** never against the board's own earlier result.

## The details (to fill on day 1)

| what | the answer |
|---|---|
| the machine the board is attached to | |
| the debug probe, and how it is reached (SWD, OpenOCD, picotool) | |
| the serial port, and its settings | |
| the board's id, or its unique serial | |
| how a build is flashed, as a command | |
| how a run's output is read, as a command | |
| how the board is reset to a known state | |
| what the lock file's path is | |
| who may hold it besides the lead, if anyone | |
