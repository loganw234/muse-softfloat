# The harness, mapped

Filled 2026-10-26 (Phase 0) from the bootstrap kit's HARNESS.md template.
Harness: **Muse** (Muse Code, lead model muse-wonder-full-1.0) on the
owner's Windows desktop. Facts below are MEASURED 2026-10-26 unless tagged
BELIEVED. Which fallbacks were used is part of the record, so this file is
updated when a row's answer changes, with the date.

| mechanism the methods assume | this harness: how, or "none" | used? |
|---|---|---|
| a separate checkout (worktree) for each agent | The lead cuts worktrees itself: `git worktree add ../worktrees/<name>` from this repo, and names the absolute path in the brief. Native subagent worktree isolation is NOT used: the session's workspace is this repo's parent, not this repo (the wrong-repo trap, ParcelRound §3). | from Wave 1 |
| messages between agents | Yes: lead→running child messages exist; a child's final report is auto-delivered to the lead (MEASURED, smoke parcel 2026-10-26). A child has no mid-run message to the lead, so child→lead urgency rides the file channel below. Ledger entry always first. | yes |
| a background watch whose output wakes an agent | A Monitor primitive exists (each stdout line becomes a notification; timed watches cap at 30 min). Chosen: file channel — `ledger/urgent/` + a Monitor armed inline by each agent on `urgent/`, lead's over the whole ledger dir skipping `lead.md`; re-arm + full read on expiry. Three read moments are the floor. | armed per dispatch |
| resuming an agent with its context | MEASURED 2026-10-26: a follow-up to a *finished* child starts a successor that keeps the conversation but loses its work-tool grant (4 of 4 reader follow-ups could not write a file). So the fallback is the mechanism: a newly briefed agent given the verifier's findings, the parcel's report, its ledger file and its worktree. A running child can still be sent messages. | fallback (measured) |
| agents that start agents of their own | Possible. Every brief carries §3's two lines: say so in the ledger at dispatch; never finish while one runs. | by brief rule |
| a transcript of each agent | Yes: one session JSONL per agent under the owner's `.local/share/muse/sessions/` (lead's and each child's paths are returned by the harness). Reading own-session logs is a lead task; the extractor for tool uses + stamps is a P0/SF-0 item. | yes, extractor todo |
| a usage log: tokens, model per message | Not yet located in machine-readable form (2026-10-26). Interim: harness counters transcribed into the metrics JSONL and marked transcribed, per METRICS.md. Adapter is an SF-0 item. | fallback |
| a network policy that can keep cft-fp256 out | **None.** The filesystem is broadly readable and the web is open. Fence = CLEAN-ROOM rule in every brief + disclosure + the owner's fingerprint audit. Measured hazard: cft-named clones sit *beside* the workspace (directory names only ever seen, disclosed to owner 2026-10-26); no such path is inside the workspace, and none appeared in the lead's starting context. | rule only |
| the board's debug link | picotool 2.3.1 over USB (BOOTSEL). No SWD probe configured; OpenOCD not installed. The lead runs every board job itself (BOARD.md). | picotool |
| a git remote, and who may push | Public remote github.com/loganw234/muse-softfloat. Only the lead pushes, only on the owner's word (KICKOFF.md records each). Parcels commit in their own worktrees, never push. | yes |
| what the harness puts in context by itself | At session open: a skills catalog, a memory snapshot, workspace identity. It does not load sibling repositories. The workspace root contains no cft-fp256 path (MEASURED by listing, 2026-10-26). Subagents inherit the same surfaces; briefs restate the clean-room rule because "not loaded today" is not a mechanism. | checked Phase 0 |
| whether an agent can read another's scratch | **Yes, technically** — one shared filesystem, one sandbox user for children. The planted-fault blinding therefore rests on instruction + disclosure, and the record says so (WORKFLOW.md's stated limit). Keys live in `scratch/lead/`; every brief forbids reading it. | stated limit |
| the clock each agent reads | Git Bash `date`; the kit's `tools/ledger.sh` stamps headings and is the only ledger writer briefs use. Host zone −0700 (MEASURED). | yes |
| how long a session lasts, what ends one | Sessions end at owner/runtime discretion without notice guarantee. Fallback = the method's: pause/resume notes in the ledger; the lead's state is the ledger + this repo, not its memory. | fallback |

**Where the agents run:** this desktop, in Muse. Sandboxed shells run as
`DESKTOP-T33SK86\muse-sbx-r1` (constrained PowerShell, `\\?\` cwd — AGENTS.md
says what that breaks and the Git-Bash route around it); escalated commands run
as the owner, only with his approval.

**Where the ledger is:** `<workspace>/ledger`, outside every worktree, where
`<workspace>` is this repository's parent directory. Briefs define that root
once (it is the one absolute path a brief carries) and say `<ledger>/`
afterwards; reports and this file never carry the absolute home path.

**Each agent's scratch directory:** `..\scratch\<agent-name>\` beside this repo;
keys only in `..\scratch\lead\`.

**The usage log's format:** not yet established — see the usage-log row; the
adapter that reads transcripts into `round_metrics.py` input JSONL is named in
SF-0, and transcribed rows are marked until it exists.
