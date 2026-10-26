# The board

Filled 2026-10-26 (Phase 0) from the bootstrap kit's BOARD.md. A Pico is
"constantly connected for debugging", and "Lead controls hardware access"
(owner, 2026-10-23). Rows not yet measured say so; a board result that cannot
name its artifact is not evidence.

## The protocol

- **The lead holds the board.** A parcel that needs board time asks the lead by
  the escalation channel. The lead runs the job itself, or grants a slot by
  name and by time. One holder at a time.
- **The lock is a file:** `<ledger>/board.lock`, holding the holder's name, the
  job, and the time from `date`. Take it before touching the board, remove it
  by its exact path when done. A lock the holder did not write is not theirs
  to remove.
- **Every board result names its artifact:** the ELF/UF2's sha256, the commit
  it was built from (SHA and content asserted apart), the build's flags, and
  the board's id.
- **A board run goes in the record** like any other run: command, output, what
  it showed. A board result is checked against the authority, never against
  the board's own earlier result.
- **Long runs are the lead's**, at hours that do not load a machine someone
  else is using (owner rules 2 and 9).

## The details (2026-10-26)

| what | the answer |
|---|---|
| the machine the board is attached to | the owner's desktop, DESKTOP-T33SK86 (this machine) |
| the debug probe, and how it is reached | **None configured yet.** picotool 2.3.1 over the Pico's own USB (BOOTSEL) is the working route (MEASURED). OpenOCD is not installed; whether a Debug Probe is attached is an open kickoff question for the owner. |
| the serial port, and its settings | Not established: COM1 (motherboard) and COM5 (Bluetooth) enumerate; neither is the board while it sits in BOOTSEL (MEASURED 2026-10-26). Revisit once firmware enumerates a CDC port; record port + settings here before the first serial gate. |
| the board's id, or its unique serial | RP2040 rev **B2** per `picotool info -a` (MEASURED 2026-10-26). Unique serial not yet read — recorded here at P0's board harness, before any board number is quoted. |
| how a build is flashed, as a command | To be frozen by P0's board harness. Working candidate (BELIEVED, standard picotool): `picotool load -x <file.uf2>` with the board held by the lead under the lock. |
| how a run's output is read, as a command | To be frozen by P0 (USB CDC serial capture is the candidate; no command is a verdict until P0 watches it fail). |
| how the board is reset to a known state | `picotool reboot` (BELIEVED standard); BOOTSEL re-entry may need hands — owner question if unattended cycles are required. |
| what the lock file's path is | `<ledger>/board.lock` (ledger root is defined in docs/HARNESS.md) |
| who may hold it besides the lead, if anyone | nobody yet; a parcel may be granted a named slot by the lead, recorded in the ledger |
