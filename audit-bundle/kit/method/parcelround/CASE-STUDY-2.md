# A second round, recorded as it runs

The first case study ([CASE-STUDY.md](CASE-STUDY.md)) was written after
the fact, from a round that produced the method. This one is written
**during** the round it describes - one of the first applications of
the method since it was extracted - so that what the method predicted
and what happened can be set beside each other with timestamps rather
than reconstructed. It is a draft until the round ends; the final
section says what METHOD.md should say differently.

## The setting

cft-fp256: a deterministic floating-point coprocessor for an Alveo U50
- RTL, a Python golden model that is the authority, a C library with
software, XRT and remote backends, nine language bindings, and a
conformance census in the millions of cases. The invariant is bit
identity across every backend and the tile, and anything the hardware
cannot do is refused by name. The requester is a second repository, an
N-body integrator ported onto the library, whose own document ranks the
things it wants.

The round: four asks from that document deferred from an earlier
round - a device-side scatter, a gather, a per-run lane mask, a scalar
broadcast. Lead: one Claude session (the author of this record).
Parcels: Opus agents in git worktrees of the same repository. The
build box and the card belong to the lead; the parcels see neither.

**How the round was run.** For the majority of its twelve-hour-plus
runtime no human monitored progress. Logan's touches on the day were
the approval of the plan and the ABI at 03:30, the instruction to
dispatch on the quick tests at 06:3x, the instruction to keep this
record, two questions about the method (whether the ledger helped;
how it held up under start/stop), a status question at eleven hours
with the agent cards, and the cost figures afterwards - the desktop
app's own accounting puts the human-active time at 1 h 38 min against
23 h 40 min of API time across every agent. Every other decision was
the lead's: five dispatches and four verifier dispatches, four
send-backs, six merges with their staging branches and box runs, the
corrections to the plan (the bindings item, the cwrap premise, the
value statement for ask 5), the answers to every escalation, the docs
sweep, and the two corrections of the lead's own work. Each was taken
within the plan Logan approved and the repository's standing standards
- bit identity across backends, refusal by name, every gate green with
fresh binaries, the box's suite at every merged tip, nothing pushed on
a report alone - and each is in the ledger at the time it was taken,
with what it rested on, so the record does not depend on anyone's
memory of it. The round did not need a human in the loop to keep its
standards; it needed one to set them, and to be told, at the end, what
the standards had produced.

## Timeline (2026-09-15, local time; commit times and file mtimes where they exist, `~` where only an agent's own stamp does)

| when | what |
|---|---|
| 02:00-03:30 | The plan written (`cft-fp256/docs/ROUND2.md`, ~850 lines: the seam, five briefs, two verifiers, the ledger, the merge order), after reading both repositories rather than remembering them. |
| 03:30 | Plan delivered; Logan approves the ABI shape and dispatching every parcel, including the two the plan had flagged as optional or low-value. |
| 04:00-05:15 | P0 written and built on the host: ABI 0.14 declared and refused everywhere, five registers, VERSION 0xA00, seventeen kernel arguments, the model's signature, eleven new refusal checks. |
| 05:13-05:16 | Host gates green. A Python harness's hand-declared ctypes struct refused by the size handshake (74 disagreements at once) - the first thing P0 found. |
| 05:18-06:30 | Proofs: the runner's quick budget (22/25 ok; two skips for tools off PATH; two FAILs, neither the seam's), the box's Verilator suite, multi-pass census, Icarus confirmations, lint. |
| 05:40 | Ledger created outside every worktree; lead.md seeded with environment facts and two rules from the day before; the lead's watcher armed over the whole directory. |
| 06:0x | The plan's paths re-checked before dispatch: `bind_role` named in the wrong file in two briefs. Corrected on main and noted in the ledger. |
| 06:3x | Logan: "we may want to utilize the quick tests" - dispatch on the Verilator suite, census and lint; Icarus confirms in the background. |
| 06:30 | **P1** (indexed inputs, the long pole) and **P4** (beat-wide accumulator, disjoint files) dispatched. |
| 06:31 | The Icarus tail lands, all green; nothing changes. |
| 06:32 | **P1 escalates through `urgent/`** (two minutes after dispatch): the plan's ownership list forbids the one CSR edit its brief requires; the dispatch message had granted it; the dispatch said the document wins. P1 stops and asks instead of guessing. |
| 06:33 | Lead answers on `urgent/` (one minute after the escalation), decides once for P1 and P3, corrects the plan on main. |
| ~07:20 | P4's first two ledger entries: the brief's rate claim is an asymptote (100% adder utilisation), the target is the memory's rate; and a disclosed crossing into the module's bench wrapper. |
| ~07:25 | Lead acknowledges both in lead.md. |
| ~07:30 | **P4 finds a gate defect with its own negative control**: a single bench target exits 0 when its tests fail (only the full suite runs the results checker). Also its measurement: fp32 sum 11.3 -> 1.4 cycles a beat, every declined shape cycle-identical. |
| 07:33 | Lead puts the gate defect on `urgent/` for every parcel and verifier; the briefs' build sections corrected on main at 07:34. |
| 08:14 | **P4 discloses on `urgent/`** that a blanket `docker kill` of every sim container at 08:09/08:11 took two of P1's benches with it; names the IDs, the commands, and what P1 will have seen. |
| ~08:16 | Lead acknowledges, restates the rule as the command to use. |
| 08:2x-08:32 | P1 posts seven entries: the CSR diff as granted; a bench expectation now derived from both CAPS2 bits; a remote-route hole the seam left and P1 closed; the software backend publishing INDEXED; doc counts are the lead's; the read side is one burst in flight (a gathered element is a whole round trip); the plan's fold sketch used an input stream as the accumulator. |
| 08:32-08:33 | Lead decides the caps consistency on `urgent/`, corrects the plan for the last two, acknowledges the rest. |
| 08:54 | **P1 reports**: 2 h 24 min wall, 279 tool uses, ~530k tokens; eight commits; every gate quoted by the checker; three controls shown failing; five brief corrections; six disclosed crossings, all previously approved through the ledger. |
| 08:57 | **V1 dispatched** against P1's tip with a twelve-item attack list; the box runs the full suite at the same tip in parallel. Nothing merged on the report. |
| 09:04 | **The lead's seam test** (§7): a gathered program between segmented reductions on one tile, written in the lead's own worktree at P1's tip while V1 runs; 2/2 with the checker. It belongs to no parcel, which is exactly why the method says the lead writes it. |
| 09:06 | **P4 reports**: 2 h 37 min wall, 209 tool uses, ~490k tokens; three commits; 8.0x marginal on the fp32 sum with every bit unchanged; every gate by the checker; six brief corrections, among them that the brief described the tree as sharing the accumulator's issue port when it uses the other lanes of the same beat-op - the brief's own lane arithmetic contradicted its own prose. |
| 09:08 | **V4 dispatched** against P4's tip. The plan had no verifier for P4; the method's own criterion (a numerical invariant on a hot path) says there should be one, and the lead followed the method over the plan. |
| 09:14 | The lead fixes the gate defect on main (every bench target runs the checker), proven both ways on one bench, before wave 2's briefs are written. About a hundred minutes from P4's finding to the durable fix. |
| 09:29 | **V1's first entries**, thirty minutes into its list: a pre-existing decode rule (any operand field below three marks a stream as needed) that the gather turns from a beat read into a whole table plus a round trip per entry; the XRT path staging an indexed source at the dense size; the parcel's own device-test leg reading past its buffer and passing because the deposits do not depend on it. P1 sent back to fix all three; V1 continues. |
| 09:57 | P1 returns with the three fixes (tip b812a53) twenty-six minutes after being sent back. The decode fix changes the dense path for every program, not only gathered ones, and P1 held it to the model with a bench case that derives operand use for all 256 opcodes from the model's own steering - and fails on a table that is all-three everywhere, so the case cannot pass vacuously. V1 asked to re-check the three on the new tip; the box re-runs the suite there after its Icarus tail. |
| 10:07 | **V4 returns: no defect.** Every gate reproduced from a clean build, quarter added, eleven probes of its own, both fatal guards fired, a pair-preserving permutation shown to pass. Two findings of the second kind: the wide-path-off build is a source edit no gate builds, and the quarter-tile bench was missing from the parcel's list. P4 merged onto a staging branch; the lead makes the switch a parameter so the control becomes a gate. |
| 10:24 | **V4 finds a regression after reporting none**: the reduce-then-program probe - the diagnostic written for yesterday's shared-array hang, and NOT in the suite - fails at P4's tip with a spurious underflow flag, bits correct, with the tree built out too. P4's nine benches and V4's eleven probes all ran reductions back to back, where nothing is left in the array to leak; only a different kind of run first exposes it. P4 sent back; the merge held. |
| 10:28 | P1 re-reports at b812a53: 3 h 57 min wall in all, 360 tool uses, ~620k tokens, nine commits; every gate green, the dense cycle table unchanged after a decode change that touches every program. The lead promotes the probe that caught P4 into the suite on main. |
| 10:38 | V1 confirms P1's three fixes at the new tip by its own reading of the model, re-runs every gate there, and finds the old stream-loading rule still stated in the RTL declaration and in the document - a false sentence in two places a reader goes first. Fixed by the lead on the staging branch; the branch runs on the box. |
| 10:41 | **V4's final report**: 1 h 32 min, 190 tool uses, ~420k tokens. One defect, ten confirmations, two gate gaps, one latent coupling handed to the next parcel. Its own earlier "found nothing" entry stands in the ledger with the correction appended beneath it, as the ledger asks. Its gate-quality verdict is the sentence the method wants: strong for a pairing break (five of nine cases fail, two of them pre-existing), absent for a flags break (no bench sequences a different run before a reduction). |
| 10:49 | **V1's final report**: 1 h 52 min, 325 tool uses, ~555k tokens. Everything confirmed at P1's fixed tip, by its own cases as much as by re-running P1's; four "gate would not catch it" items and three false sentences named, two of them the lead's own. P1 resumed for the two real gaps; the lead fixes its own paragraph. |
| 11:27 | **P4 reports its fix** (tip 778dabf): 4 h 54 min wall in all, 252 tool uses, ~550k tokens; the flag arm now contributes only on its own levels' return strobes, closed by construction; both regression shapes fail with the fix reverted; redprog green under both simulators; the cycle table byte-identical. V1 closes out clean. |
| 11:37 | **P1 is on main** (5c0c655, a fast-forward of the staging branch). The verdict: the box's suite at 1c6b63a (24 benches, the suite-level line present this time, census, lint), the one commit after it shown comment-only by diff, and the host-side gates re-run on the desktop at the tip in six minutes (build, api-test, 66 model tests, the 200-program corpus with its three sub-corpora, device-test both legs, docs index, five generators, the Arduino copy). 5 h 07 min after P1 was dispatched (06:30, this timeline). |
| 11:41 | **The wave-2 briefs amended before dispatch** (d4e4529, e0f211f): twenty minutes of the lead's time converting what the ledger and the verifiers produced into the two sections P2 and P3 read - the opcode read rule, P1's remote route and its three lines, P1's CSR items quoted for P3's mirror, V4's parameter fact, P4's flag fact with the two cases it implies, the one-burst read side, and the regions of P1's in-flight follow-up. A V2 list added: the method's criterion said yes for P2 as it had for P4. |
| 11:43 | **Wave 2 dispatched**: P2 (the composed `cft_run_ex`) and P3 (the lane mask), Opus, isolated worktrees from main at e0f211f. Four agents share the desktop (P1's follow-up and V4 still running). |
| 11:44 | **P1's follow-up reports** (991603f; 5 h 15 min and 425 tool uses for the parcel in all): MODE[22] without a scratch block refused at the header check from the header's own bits; the `-b` leg gates the tables' binding path with a resident-versus-staged assertion no gate had; the stale probe comment fixed. Its rule for P3, in the ledger with a `For:` line: a MODE bit whose selected object does not exist is refused at the header check, never skipped in the state machine. Staged as round2/merged-p1b (29809cb), the box's suite in the first checkout, V1 resumed for a scoped check. |
| 11:50 | **The lead's own gate had a hole.** The `-b` device-test count did not move across a commit that adds a leg - because `make all` does not build the test executables, and the lead's script had been running a device-test binary from 05:13, P0's, on two merge gates. The number that refused to change was the tell; the verdicts stood on the verifier's and the parcel's own builds and on the box, not on the lead's binary. Corrected in the ledger as a correction entry (the 11:37 and 11:48 entries left standing), the script fixed to build every test executable by name and to print their build times. |
| 12:05 | **V4 confirms P4's fix** (2 h 54 min in all, 266 tool uses, ~504k tokens): the defect gone under both simulators; the two new bench cases fail with only the narrowing reverted; an instrumented copy measured the guard doing real work (8,690 flag collections, the earliest at edge 21; the unqualified OR non-zero at edges 0..15 on 127 occasions) rather than being vacuously true; the tap pinned both ways (one stage early fails nine of eleven cases, losing a real flag and gaining a spurious one); nothing outside the tree and the decode changed, by section hashes; the cycle table identical in all 21 rows. Two of V4's "still open" items were already closed on main (redprog in the suite, EN_WIDE through the kernel) - a verifier at the parcel's tip cannot see the lead's branch, and says so. |
| 12:03 | P4 merged into main locally (27c424d, not pushed); the seam test runs on the desktop on the combined P1+P4 tree, which no suite has run; the push waits for the box's suite at P4's staging commit; then the box runs the merged main. Six stated bench counts become twenty-five. |
| 12:18 | **The seam test on the combined P1+P4 tree** (the lead's local merge, 16 minutes on the loaded desktop): redprog 2/2 - a segmented reduction, an indexed fold through the scratch pool, a gathered fold across a block, a reduction again, on one tile - reduce 11/11, reducenowide 11/11, krnlseq 1/1. The two parcels had never run together; the shared-array hand-off where the previous day's hang lived is the thing this test exists for, and it held first time. |
| 12:22 | **The box on P4's staging commit**: 25 benches, the suite-level line present, the census, lint - 58 minutes from launch, three suites sharing the box. |
| 12:24 | **P4 is on main** (a061d3f): the second parcel merged, 5 h 54 min after its dispatch (06:30), one send-back in between. The merge itself was the cheap part: two clean auto-merges, one seam test, one box run. |
| 12:34 | **P3's first findings**, 50 minutes in: four environment facts for its siblings (the remote target's Python default, the unused variable at HEAD, the WSL route to the XRT 2.14 compile check through PowerShell, the XRT file warning-free on 2.14); the two P0 controls it had to flip, disclosed; and a rule question - MODE[23] on an elementwise run is accepted and ignored, the shape MODE[18:16] already has on a program run - asked rather than answered by inventing a refusal. P3 stamped all three entries 13:07, then read the clock, and appended a correction addressed "For: the case study": the guess was 33 minutes ahead. |
| 12:36 | The lead's answer in the ledger within the hour: the rule is one rule already (the build's, not the run's), stated once in the sequencer doc on main; the flipped controls are the expected shape; the merge of the bench file where three neighbours now meet is the lead's by hand. |
| 12:37 | **P3 measures the value statement's premise wrong**: the lane mask saves no compute on this tile - the sequencer issues per beat, and the active bit decides what is written, not what is computed - so half-masked and all-masked cost the same, dense plus one beat read a block (four cycles), and the early exit sees the mask. The plan had priced ask 5 at up to two percent of a step on "compute and bytes"; the bytes half stands, the compute half was never there. P3 stopped at the brief's line ("if the RTL wants to grow past the block setup and the drains, stop and report") and reported, with the two mechanisms that would buy the compute named and placed outside its ownership. |
| 12:38 | The lead's answer within the hour: the mask ships as built; the beat-skipping is a revision-7 item for the roadmap with P3's numbers as the before-side; the plan's value statement corrected on main the same hour, dated; V3's list gains "the dense column unchanged, re-measured". |
| 12:49 | **P2's first findings**, an hour in: a program run requires stream a, so the naive operand-to-stream mapping over-reads a one-element scalar buffer beside an indexed operand - the trap the brief named, met and solved by packing the streams by what the opcode reads and expanding a scalar into a constant with its k bit (measured in the RTL parser, not assumed); the remote route gathers on the client and the handle publishes the bit again (419 checks); two rules decided and written down (a table on an unread operand refused by name; d aliases nothing when a table is present); two environment traps for the next brief (Python text-mode writes flip a file to CRLF; a heredoc eats a backslash and an assert on the match count cannot see it); the two integrator gates red at its tip, named, and left to the lead. Then a self-correction: its first probe had read a lazy `cwrap` as proof an export existed. |
| 12:56 | **P1 is whole on main** (01729e4): the follow-up merged on its box verdict with the lead's three merge-time edits (V1's two notes and the warning), krnlseq and the fresh-binary host gates green on the merged tree, the box's suite launched on the pushed tip in a fourth checkout. Main now carries P0, P1 both parts, P4, and every wave-1 gate fix; 6 h 25 min after the first dispatch. |
| 13:11 | **P2 reports** (1 h 27 min, 336 tool uses, ~547k tokens): the composed route measured by a one-line control that makes the software backend compose instead of gather, with the whole device-test agreeing (8,754 checks); three new rules refused by name; the remote route rebuilt as a client-side gather with no frame sent on a refusal; the stream-a constraint solved by packing; four things the brief got wrong named with their evidence; one thing it chose not to do (the C export without its JavaScript half) explained rather than done. V2 dispatched within ten minutes with the plan's list plus four items the lead added from the report. |
| 13:16 | **P3 reports** (1 h 31 min, 658 tool uses, ~716k tokens): eighteen files; every gate green on both the RTL and the host side; four controls; the value statement's correction as the headline; six brief errors named with evidence - among them that a program run is not split across tiles today (the repack's slice offset is always zero) and that the brief's own remote sketch would have leaked a masked lane's flag, which compaction fixes. It kept its bench cases in a new test as the lead asked at 12:13, and the merge preview shows every code file auto-merging. V3 dispatched within minutes with five items added from the report. Both wave-2 parcels landed within four minutes of each other, 1 h 31 min after dispatch. |
| 13:34 | **V2 finds a regression in P2** twenty minutes into its list: the new per-index bound loop runs before the elementwise path's own n-sanity check, so an absurd n that the dense call refuses without touching a byte now walks the caller's table - a segfault, reproduced at n = 2^61 with an eight-entry table. One hoisted check. V2 also corrected the report's "+4,720 checks" to 4,676 by rebuilding both tips: the parcel had subtracted the lead's retracted stale-binary number, which is how a wrong number propagates - it was in the ledger for fifteen minutes and got used once. And four sentences in the public header go false at the merge (the lead's file, the lead's job). |
| 13:38 | P2 sent back within three minutes (the hoisted check with its case; the refusal order on a device without the scalar capability, which V2 read rather than ran - there is no card); the header sentences prepared as a two-half patch so main never states a falsehood between the two wave-2 merges. |
| 13:41 | **V2's full report** (29 minutes, 137 tool uses, ~305k tokens - a third of a parcel): every item on the list confirmed by its own drivers (six scalar/indexed pairs at every format; a one-byte overlap; flags reachable only through the gather; the wire frame byte-identical; three controls rebuilt from copies, the off-by-one caught cleanly by api-test alone), plus the defect, the wrong number, a gate gap (scalar b and c beside a table are right but unheld), a pre-existing sticky error string, and the card-day gap no host can hold (bus_out on the composed route). The cheapest agent of the round found the round's only host-side regression. |
| 13:50 | **P2's fix** (13:45-13:50; 2 h 07 min for the parcel in all, 407 tool uses): the memory-touching rules moved BEHIND every check the dense path makes rather than beside two of them - so a check added later is inherited - with a poisoned-pointer case that segfaults when the check is neutered; the capability refusal moved to where exactly the runs that use the thing it names reach it, proved both ways; the gate gap closed with a derived pair count. P2 also stated the general rule in the ledger for P3 (a rule that dereferences a caller's buffer belongs behind every rule that does not), and the lead forwarded it to V3 as an item, because the lane mask and P1's tables have the same shape. V2 resumed for the re-check. |
| 13:56 | **Wave 1 verified on the box at its pushed tip**: the full merged main (P0, both parts of P1, P4, every gate fix) - 25 benches, the census, lint, nothing failing. Seven box runs today across four checkouts, every one green; the only launch that failed was the lead's grep mark in the wrong file. Wave 2 merges onto this line. |
| 13:59 | **V2's re-check** (11 minutes): all three fixes hold; the read-before-check property proved with a poisoned pointer in eighteen shapes (a read would have killed the process); the new gate shown live by neutering the check (a segfault is the only faithful witness of "no read happened"); the pair sweep's count derived by hand (28 pairs a format, 10 checks a pair, 800 added, 9,554 total); the dense stages' increments identical. P2 merged within a minute of the entry, the header's seam sentences made true in the same push, the host gates re-run with fresh binaries before it. |
| 14:09 | **P2 is on main** (e8638f5): the third parcel merged, 2 h 26 min after its dispatch, one send-back in between; host-only, so the merge's gates were the host's with fresh binaries and the parcel's own composed-versus-program leg stood as the seam evidence; the RTL suite deliberately not re-run for a diff with no RTL, and the ledger says so rather than pretending. |
| 14:12 | **P3's staging branch built before V3 reports** - the merge with its three conflicts resolved (two mechanically, one by hand where each side had written a sentence about the other parcel that the other parcel had made false), the header's mask sentences, the vendored copy, the seam test written, the sims and the host gates launched - so that V3's word makes the merge a fast-forward and a push. A resolver script refused the test file for twenty shared lines that turned out to be generic C, and the lead's own command chain committed the unresolved merge anyway (a `;` where `&&` belonged); reset and redone in four minutes, on a branch nobody else reads. |
| 14:56 | **V3's findings** (1 h 40 min in): no defect in the shipped mask, and two things the lead will not merge without - the RTL gate cannot see ACTALL reviving a masked lane (the drains hide it in bytes; only a flag would tell, and no case combined the two - V3 built the case), and the mask's block slice elaborates to a priority chain worth 59 percent of the sequencer's cells after a full optimisation pass, 191 under the lint flow, a column the value statement never had. Plus the program-run twin of V2's finding (a table walked before the n guard - P1's inheritance, the lead's), and a conservative remote refusal. The remote compaction held at every chunk shape; the brief's own sketch, built as a control, leaked the masked lane's overflow exactly as P3 had argued. |
| 14:58 | P3 sent back for the case and the rewrite, with the area to be measured the way V3 measured it; the ledger answer decides the other two (the lead's, after the merge; the under-promise stays and is documented once for both features). Third send-back of the round that was a gate or a cost rather than a wrong bit. |
| 15:01 | **V3's full report** (1 h 44 min, 167 tool uses, ~366k tokens): fourteen items, every one re-run from a clean tree with cases of its own beside the parcel's (a converged lane under a mask at fp256; a mask straddling two beat boundaries with a ragged tail; the compaction at every chunk shape with the chunk size cut to twelve lanes; 1,764 repack shapes past the ones the parcel swept); the shipped code right everywhere; the gate hole and the area column as findings; a comment stating half a rule. The four verifiers of this round cost 29 to 112 minutes each and together sent back three parcels for things no parcel could have seen. |
| 15:03 | The docs sweep begun while P3 fixes - the parts no parcel touches (compatibility sections for three parcels, the remote doc's under-promise paragraph, the roadmap's built asks and its new debts list, the card day's round-2 list) - so the end of the round is P3's section and ask 5 rather than a sweep. The lead's own idle time in a round is the sweep's. |
| 15:04 | **P5 dispatched** - the bindings' elementwise entry point, the one thing the round still owed that no parcel owned: two brief errors of the morning became a brief of their own (the export and its JavaScript half in one commit with the rebuilt module, because the loader's table is eager). A parcel spawned from the ledger's own record of what was wrong. |
| 15:30 | **P5 corrects a premise the lead had written into the plan** (a missing export's wrapper is `undefined`, not lazy; the node gates would have passed with a silently absent entry point) - and turns the rule it was protecting into two mechanisms (a load-time call; a named gate). The conclusion had been right and its mechanism wrong; a parcel that measured the mechanism made the rule enforceable instead of assumed. Third time today a parcel corrected the plan within its first half hour. |
| 15:57 | **P5 reports** (52 min, 353 tool uses, ~411k tokens): the entry point whole in one commit, six cases at four formats with every expected bit taken from the dense call, the negative control breaking the marshalling two ways (a refusal by name; a deterministic wrong lane), the module's growth explained (the whole indexed path linked in for the first time), three brief errors named - one of them the lead's premise about the loader, corrected on main within a minute of the entry. The smallest parcel of the round found the plan wrong three times. Merged locally at 15:57; the lead's own re-run of its six gates is its verification. |
| 16:04 | **P3's fix** (2 h 51 min for the parcel in all, 939 tool uses, ~814k tokens - the largest of the round): the gate hole closed with the case V3 predicted, failing its control by the exact bits; the block slice rewritten from a per-position equality chain into eight part-selects - 690 cells over the maskless tile where the first version cost 4,019 under a full pass and 18,803 under the lint flow - with the old numbers reproduced before the change, "which is what says the two of us are measuring the same thing"; a rule for the record beside P4's (a per-position equality around a per-bit assignment is a priority chain, not a select; read the mux count). Two general lessons volunteered: when a mechanism is enforced in two places, a gate that reads only the cheapest observable cannot see a defect in the other. |
| 17:39 | **The lead's own patch failed its gate.** The program-run twin of V2's finding, written by the lead from V3's example, crashed api-test on its first run: the example had used eight deposit slots at fp256, the test's program has one slot at fp32, so the bound the guard checks sat four times higher than the case's n and the poisoned table was walked exactly as before the patch. Fixed in two commits (the guard bounds every program; the case above the bound at every format; then a substring that did not match its own sentence). Nobody verified the lead's patch but the gate - which is the point of having one that cannot pass a read. |
| 17:49 | **P3 is on main** - the last parcel, 6 h 06 min after its dispatch, two send-backs in between (the second for a gate hole and a cost, not a wrong bit). Every parcel of the round is merged: P0, P1, P4, P2, P3, P5, in that order, each on a verifier's word where it had one and on the box's suite at its tip. What remains is the lead's: the box verdict on this tip, the image at 135 MHz, the card day, the records. |
| 18:47 | **The box on the round's final main**: 25 benches, the census, lint, nothing failing - the sixth and last merge verified at its tip. Every merge of the round was verified this way; none was pushed on a report. |
| 18:49 | **The image build launched** on the box from the final main at 135 MHz, after the build script's own dry run had passed every assertion at that tip: single tile first, the quad only if the single verifies, staged only past the image check. The build phase of round 2 ends here, 16 h 49 min after the plan was begun and 12 h 19 min after the first dispatch; what follows - the image's timing, the card day - is the lead's and Logan's, and joins this timeline when it exists. |
| 19:27 | **The card day begins** on Logan's word: the card free, no image loaded, the round's tools built with XRT on the box. Its first half is the round's library against the previous image, which no host could test: the first run found P2's elementwise legs counting a refusal by name as a failure - the library right, the test ungated - fixed and re-run within four minutes: 1,361 checks, none failing, the three new features absent by name. The long runs on that image follow; the round's own image is still linking. |
| 19:37 | **Card day, first half done**: the round's library against the previous image - every leg and the 892,548-case replay green, the new features absent by name. The test gate it found wrong was fixed in four minutes and pushed; two more small card-day instruments went in while the image linked (the STATUS comparison V2 asked for; a masked timing in the gather tool). The second half's script waits for the image on the box. |
| 20:57 | **The round's image lands**: single tile, 135 MHz, kernel margin +0.266 ns, image check 8 of 8; the quad links after it. |
| 21:03 | **The card day's first gate on the new image fails**: the lane mask does not work on the tile - every masked lane written, at every format and density, flags and status clean - while the gather, the composition and the reductions are right on the same image. A register-readback trace added to the library within twenty minutes proves the host side (the MODE bit, the pointer, the device's bytes) and puts the defect on the tile, in a shape the simulations at the model's memory latency never saw. The lane-mask benches are re-running at HBM-like latency to reproduce it. |
| 21:15 | **The card's number for the gather** (asks 1 and 4 on silicon): at fp64 with 64 bodies, one indexed program run replaces 63 calls at 3.25 times their speed, 335 nanoseconds a gathered element, the deposits equal to the host fold; 1.4 to 2.0 times at fp32 and fp128. The plan's cost model - a gathered element is a round trip - was right in shape and the round trip is a third of a microsecond. |
| 21:27 | **The masked slots' fingerprint**: one added line in the timing tool shows every masked slot holding exactly the value its lane would have deposited unmasked, at fp32 and fp64 - not the pattern, not garbage. The RTL had been the suspect since 21:03; this is the first fact that does not fit it. |
| 21:33 | **FLAGS says the mask reached the lanes**: a new probe (`host/tools/maskflags.py`) poisons the masked lanes (+inf + -inf) and reads FLAGS - INVALID unmasked, clean masked, on the card at both formats. The flags are ORed under the active bits, so the tile applied the mask; only the bytes are wrong. |
| 21:36 | **The strobes hold**: a pattern in the count window's staging pad (the lanes past n, strobed off with no mask involved) survives dense runs at n = 5, 13 and 3; trailing, leading and interleaved masks all write their masked lanes. The memory path honours WSTRB, and the pattern's shape is not it either. |
| 21:41 | **The defect is the host's, fixed, no rebuild** (be1ac1f): the tile leaves a masked lane's bytes as they are ON THE DEVICE, and a staged deposit window's device copy held the previous run's output - a deposit window is an output the host never uploaded. Under a mask the library now stages the caller's deposit window and counts first. Every mask pattern untouched; the gather at 64 bodies masked every third lane runs at 1.026x the unmasked run. device-test relaunched twice - the first time with a statically linked test binary from 21:06 that still carried the old backend, the day's second stale-binary lesson. |
| 21:50 | **A third mask leg, and the crash bracketed**: the same contract sentence names a masked lane's scratch-out slots; never staged, never tested - now both (301c21d), 2,248 checks 0 failed on the card. The 128-body crash: 100 bodies fine, 112 aborts, and device-test -n 336 alone dies in its first elementwise legs; the seq6 image with the same library does not. |
| 21:53 | **AddressSanitizer on the box** stops on XRT sizing a 4 KiB-aligned host allocation to exactly the library's beat-rounded byte count (1,344 bytes = 336 fp32 lanes). |
| 21:56 | **Buffer capacities are whole pages** (d40ad23): device-test -n 336 / 1000 / 4097 at 2,248 checks 0 failed each, the resident legs 729/0, 112 and 128 bodies three reps each. |
| 21:58 | **128 bodies on silicon**, the requester's shape: one run 15.6 / 15.1 / 16.5 ms at fp64 / fp32 / fp128 against 127 calls at 26.7 / 24.7 / 24.9 ms - x1.71 / x1.64 / x1.51 with 127 host gathers removed as well; 320 / 310 / 338 ns a gathered element; the mask 1.3% on top. |
| 02:55 | **The quad misses timing at 135 MHz** after 359 minutes: kernel-side WNS -0.363 ns on the elementwise engine's FIFO-to-FMA bypass paths (17-18 logic levels through the DSP cascade) - the path every earlier image carried, which nine previous quads closed with 0.009-0.143 ns to spare. Not the round's logic. Relaunched at 03:01, quad only, same commit and clock, with the placement and routing directives the build script names as the axis that moves timing by this much; the single stays as validated. |
| 07:50 | **Logan's word on the clock**: if the quad fails to close, 130 MHz is acceptable - 135 was tight every time, a minor drop is fine, and the tile already beat expectations when used to its potential. Banked as a standing rule; a wrapper on the box was armed to launch the 130 MHz build the moment the 135 MHz attempt failed to stage. |
| 10:47 | **The quad closes at 135 MHz** on the directive rebuild: kernel WNS +0.040 ns, routed +0.031, zero failing endpoints, 468 minutes; staged beside the single with a README saying which half used which directives. The wrapper read the staged file and stood down. The router's intermediate slack had sat at -0.317 ns for hours; the post-route optimisation recovered the rest. |
| 10:49 | **Four tiles on the card, 74 seconds after staging**: device-test at 8, 64, 336 and 4,097 lanes 2,248 checks 0 failed each, the resident legs 729/0; the 128-body gather at 316 ns an element (a program run is one tile's) against 127 dense calls that cost twice what they cost on one tile; a thousand segmented sums in one call at 1.45 ms against 2.35 on the single; 168 sets, 1,224,915 cases, all matching. |
| 12:30 | **Saturating the pair** on Logan's ask: four tiles are four times one on resident elementwise work at every format and size (each unit at the single's 107 M beats a second, 55 GB/s in all); through the library the four-tile cost is a fixed cost a call, a fifth at a million fp32 elements and under three percent at sixteen million; the largest resident shape is bigger on four tiles because a buffer is sliced per tile. Reductions were the outlier - a whole-array sum at an eighth of the engine's rate - recorded as an open question with its candidates, not explained. Two drivers, one script written for it (`segsat.py`), a driver mistake (element counts that were not multiples of the segment) caught by the script's own check and corrected mid-run without editing the running driver. |

## Observations against the method, so far

**§1, the lead's model is wrong - but this time before dispatch.** The
first case study's headline was that every parcel corrected its brief.
Here the plan itself, written from reading both repositories rather
than from memory, found three things the ask list had wrong before any
parcel existed: one ask had already shipped three days earlier and was
never marked done; two asks were one mechanism (the requester's
"scatter" is a table gather followed by a fixed-order fold, not a
scatter-add); the third's value had a two-percent ceiling by the
requester's own table. Reading the upstream's code, not its summary,
is where that came from. The method should say so as a step: *read the
requester's implementation, not its ask.*

**§2, P0 preserved behaviour, and the proof found three unrelated
things.** The seam - every new field refused by name, every new bit
zero - did what §2 asks, and running the whole suite on both sides of
it found (a) a harness mirroring a C input struct by hand, refused at
its old size (the size handshake working as designed, on a caller
nobody had listed); (b) a generated table stale since an earlier
commit; (c) a language leg broken for eleven days on this host,
untested since. None was the seam's. §2's "run the full suite before
and after" is what made them visible; a P0 proven only by its own
tests would have missed all three.

**§3, "verify the constraints you write down" - done, and still not
enough.** Every path in the plan was checked to exist. A function was
still named in the wrong file in two briefs; a second pass, checking
what each named function *is* rather than whether it exists, caught it
before dispatch. What that pass did not catch: an ownership list that
forbade a file the parcel's own job required (the CSR's reserved-bits
guard). The seam's own code comment said the parcels would change it;
the plan's list said they must not. **Two artefacts stated one fact and
drifted** - §1's own rule, violated by the lead in the plan.

**§4, the urgent channel, first live use in this round: it worked in
both directions within twenty-five minutes of dispatch.** P1 found the
contradiction, wrote one file into `urgent/`, and *kept working on the
narrower grant* rather than stopping cold; the lead's watcher fired,
the answer went back through the same directory ten minutes later, and
the decision was made once for the parcel that would hit the same wall
in wave 2. The rule "the document wins where the dispatch disagrees"
was written for the case where the document is the more careful of
the two; here it was the less careful, and the rule's cost was one
escalation rather than an hour on a wrong path - which is the channel
working, not failing.

**§4, the lead's watcher echoes the lead's own entries.** Every entry
the lead appends comes back as a notification. Harmless, but noise;
the watcher loop should skip the author's own file.

**§5, a parcel's negative control found a gate that could not fail.**
P4, told to break one pairing and watch the bench name the size, saw
the bench fail *and the container exit 0*: cocotb cannot set an exit
code, and only the full suite runs the checker. Every brief in the
round told parcels to run single targets. The method's §5 is exactly
about this shape, and the control it demands is what found it - on the
first parcel to run one. Propagated to every parcel in ten minutes
through `urgent/`; the durable fix (each target running the checker
itself) is the lead's, after wave 1, because the file is in every
worktree.

**§3, the brief got the mechanism's arithmetic wrong.** P4's brief said
"a beat a cycle"; the parcel measured the serial path at 1.41 cycles an
element (not 1.0) and argued that epb adds a beat against epb adders is
100% of the port with no margin. Same lesson as the first case study's
"the lead described a mechanism backwards in a way that changed what
the feature cost": the lane arithmetic was right, the rate was an
asymptote, and the parcel corrected it in its first hour and built to
the honest target.

**§3, a boundary crossing judged on disclosure.** P4 had to edit the
module's bench wrapper (a new port; the simulator treats a missing pin
as fatal). It said so in the ledger before doing it, said what the diff
would contain, and named the reviewer. Approved in the next lead entry.

**Costs, so far.** The lead's time went overwhelmingly to P0 and its
proofs (about three hours) and to the plan (ninety minutes); the two
dispatch briefs took minutes because the plan already was the brief.
The escalation and the gate defect each cost the lead about fifteen
minutes to answer and propagate. Parcel wall time: P1 and P4 both
still running at 08:30.

**§4, nobody in the round knew what time it was.** The lead's ledger
headings from mid-morning on ran up to ninety minutes ahead of the
clock, and P4's ran thirty-five minutes ahead; both were guessed, not
read. The first draft of this timeline copied the guesses. Commit
times and file mtimes told the truth when checked: P1's escalation was
two minutes after dispatch and the answer one minute after that, not
twenty-five and ten. The method's entry format should carry a
machine-written stamp - `date` in the entry, or the watcher stamping
what it sees - because a timeline is the measurement the case study
rests on, and this one had to be reconstructed.

**§3, a working rule stated as a prohibition was broken under pressure, and disclosed within minutes.** lead.md's environment entry said "never kill a process by image name; your own PIDs only". P4, with a hung lint container, ran `docker kill $(docker ps -q --filter ancestor=cft-sim)` twice (08:09, 08:11) and killed five containers, two of them P1's benches. It noticed within four minutes, wrote one file into `urgent/` naming the container IDs, the commands, what P1 would have seen ("a hang, a truncated log, a missing results.xml - that was me, not your RTL") and what it had changed. Two lessons for the method: (a) a rule that protects a sibling must be written as **the command to use**, not only the command to avoid - "`docker ps --no-trunc`, then kill one ID whose command line is yours" survives pressure where "never kill by name" did not; (b) the disclosure standard held - prompt, precise, actionable by the victim - and the lead judged it on that, as §3 says. Cost: P1 re-runs whatever was in flight in those two minutes; the lead spent ten minutes.

**§2, the seam put a refusal where the parcel would remove it.** P0 refused every new field in one function, and told P1 to turn that function's refusals into bounds checks. P1 noticed that doing so would have let the REMOTE backend - which has no field for a table - run the dense stream and return wrong elements with clean flags, and added a refusal in the remote route itself. The method's §2 says the seam should make shared facts shared; here the seam made one refusal stand for three backends, and the parcel removing it for one backend silently removed it for the others. **A refusal at a seam belongs in every backend that cannot yet do the thing, not in the one place the first parcel will edit.**

**§3, the brief's cost model named a divisor that did not exist.** The P1 brief said a gathered element costs a round trip "divided by the reads in flight"; the sequencer issues one burst at a time, so there is no divisor. And the plan's three-instruction fold sketch accumulated into a register that is an input stream. Both corrected by the parcel from the code within its first two hours, both fixed in the plan the same hour; neither would have been caught by "every path exists".

**§6, the plan under-provisioned verifiers and the method corrected it.** The plan named verifiers for P1 and P3 only. P4 changes the pairing path of every reduction - a numerical invariant on a hot path, which §6 lists as exactly when a verifier is worth the agent. The lead dispatched V4 anyway. Worth stating in the method: a verifier is chosen by what the parcel touches, decided at dispatch of the verifier, not fixed in the plan.

**§6, the verifier found within thirty minutes what the parcel's green gates could not.** Three findings, each of a shape §6 names: a false sentence in a docstring ("the fold names no stream"), measured wrong by counting bursts; a staging size unreachable from any gate on this host (no XRT build, no card), believed from the source and flagged as believed; and a test that reads past its own buffer and passes because nothing it asserts depends on the bytes it reads - the verifier put the buffer against a guard page to prove it. The parcel's report was honest and its gates were green; the defects lived where the gates could not look. The one the lead most wants in the method: **a rule inherited from an earlier revision can change cost class under a new mechanism** (a defaulted field cost a beat read dense and the whole gather indexed) - the brief should say which existing rules the mechanism makes expensive.

**§6 and §7, the defect lived in the combination no parcel's gate could reach, and the probe outside the suite found it.** P4's new flag arm reads the array's lane flags on every accepted edge; the array is shared with the sequencer, and the first sixteen edges of a reduction still carry the previous program's work. Every reduction bench runs reductions after reductions, where the idle lanes hold zero, so nine benches and eleven verifier probes passed; the probe written on 2026-09-14 for the shared-array hang - which sits outside `make sim` precisely because it was "a diagnostic, not a bench" - failed at once. Three lessons: (a) the verifier's "found nothing" was honest and provisional, and it kept going into the seam the parcel did not own, which is where §7 says the lead should be looking; (b) a diagnostic that caught a defect once should be in the suite, and this one was not; (c) the shape of the bug is the first case study's canonical failure in miniature - a mechanism correct in isolation and wrong in a sequence its own gates never produce.

**§6, the verifier distinguished the shipped code from the gate, as asked - and the second answer was the useful one.** V4's report closes with two sentences: the gate is strong for a pairing break and absent for a flags break. The first says P4's tests are good; the second says where the next defect will live. The lead acted on the second (the probe into the suite, a regression case into the reduction bench) before the first parcel's fix arrived.

**§6, the verifier's list was a floor, not a ceiling, and the lead's own artefacts were on the findings list.** V1 built the cases P1 did not (all four tables at once; a dense preload followed by an indexed stream; a whole block of sentinels; a burst-length corner where a misaligned table base would issue a 256-beat read), then checked the parcel's sentences and the LEAD's - the seam paragraph in the public header, written that morning, was out of step on three counts by the time the parcel landed. A brief cannot ask for that; the instruction "tell me what I did not think to ask" got it.

**§6 and §8, the verifier loop under start/stop - measured on two parcels.** P1 went back twice (V1's three findings at 09:27, fixed by 09:55; V1's final report at 10:49 named two gaps, back again), P4 once (V4's regression at 10:25, fixed by 10:54). Each cycle: the parcel's fix took 25-30 minutes because the harness RESUMES the agent with its whole context (a send-back costs no re-brief - the method assumed a brief is written once and that the parcel cannot be re-entered; here it can); the verifier's re-check 20-30 minutes; the box's suite at the new tip an hour, which is the real cost and the one §8 predicts. Not one send-back was a style disagreement: every one was a defect the parcel's own gates could not see (a cost class, a staging size, a test reading past its buffer, a flag arm reading the array in cycles that were not its run's). The alternative - no verifier - would have merged both parcels with those in them, and two of the four would have reached the card. One near-miss worth stating: V4 posted "no defect" before running the one target outside its list, and the lead had P4 merged onto a staging branch within minutes of that entry; the regression note arrived twenty minutes later. "Never merge on a report" held only because staging is not pushing. The method should say: a verifier's report is due when its LIST is exhausted, not when its first pass is, and a merge is a push. And a practice that paid for itself: a second checkout on the build box, so two suites run at once and a send-back does not queue behind a sibling's hour.

**§2, a brief is written once - so the lead's job between waves is to write the next one from the ledger.** The method says the ledger exists because a brief cannot be updated. What it does not say is the corollary the lead met at 11:20: a wave boundary is the one moment a brief CAN be updated, and everything the ledger accumulated (seven urgent files, four author files, two verifier lists) has to be folded into the next wave's sections there and then, or the next wave starts from the plan as it was written the night before, learns the same facts from the ledger in its own time, and the ledger's latency becomes the brief's. Two things made it tractable: the ledger's "For:" lines said which entries were for P2 and which for P3 without re-reading everything, and the lead had been keeping a list of "for the next brief" items in its own notes since the first send-back. The twenty minutes it took is the cheapest twenty minutes in the round. One wording lesson from doing it: a brief that names its base commit exactly is wrong the moment the brief itself is committed on top of that base - name the base "at or after", and put the exact tip in the dispatch message, where it can be right.

**§5, the lead is a participant, not an auditor - and its own artefacts need the same controls it demands.** The lead had written "verify the fact, not its neighbour: a stale binary" into P1's brief that morning and then ran one on two merges. What caught it was not a rule but a number: a check count that stayed exactly equal across a commit whose report said "+20". Two things follow. The lead's gate script should print the build time of every binary it runs - a line that costs nothing and would have said "05:13" at 11:36. And a merge verdict should name what it rests on: this one rested on V1's build, P1's build and the box, and the lead's numbers were decoration - which is why the correction cost a ledger entry and not a revert. The method's §5 says the verifier disconfirms the parcel; nobody disconfirms the lead except the lead's own habit of asking why a number did not move.

**§4 again, the clock.** Every author in this round - the lead three times, P1, P4, V4, P3 - has written a guessed time into a stamped entry at least once, and every guess was AHEAD of the clock (by 3 to 90 minutes), which suggests the guess is "when I expect to finish writing this" rather than "now". The fix that finally held for the lead was mechanical: write the entry with a placeholder and let the append command substitute `date`. P3's self-correction is the other half: an author who reads the clock after writing and corrects in the open. The method should say: stamps are substituted, not typed.

**§2 and §7, the parcel that measures the plan.** The brief's last sentence for P3 was a stop line, written because the parcel was priced small. It fired for a reason the lead had not imagined: not the RTL growing, but the VALUE not being there. P3 did the thing the method asks of a parcel that finds its brief wrong - measured it, named the mechanism, named what would fix it and whose it is, and did not build it - and the plan is corrected on main with the parcel's table in it. Two lessons for the method. A value statement that names a mechanism ("removes compute and bytes") should also name the measurement that would falsify it, so the parcel knows it is a claim and not a fact; and a stop line in a brief should say what to measure before stopping, because the measurement is what made this report decidable in one reading rather than a debate.

**§3, a brief that names the trap gets the trap solved; a brief that names the wrong file gets a correction in ten minutes.** P2's brief carried a sentence beginning "That is the trap" about a scalar beside an indexed operand, and the parcel's first substantive entry is the measured shape of that trap and the design that avoids it. The same brief named two functions that did not exist, and the parcel's first entry of all, at ten minutes, was that fact with a grep beside it. Both are the brief working: one by being right about what is hard, the other by being falsifiable about what is there. The parcels in this round correct their own entries in the open (P2 on the module's state, P3 on its stamps, V4 on "no defect"), which the ledger's append-only rule makes cheap and the "measured / believed" line makes natural - a correction is just a later measurement.

**§6, the verifier catches the parcel's use of the lead's wrong number.** The lead retracted a stale-binary count at 11:52; P2, reading the ledger for the base's count, took the 11:37 figure rather than the 12:00 replacement and reported an increment 44 too high. The correction entry was in the file, in order, with a "CORRECTION" headline - and it still lost to the earlier number, because a reader looking for "the count at 5c0c655" finds the first entry that has one. Two things follow for the method: a correction should EDIT nothing but should be linked from the entry it corrects ("see 11:52" appended below the old entry is an append, not an edit), and a number a sibling might reuse should be stated in the entry that supersedes it in the form the sibling would search for. V2 found it because its list said "derive the increment", which is the lead's own rule applied to the lead's own arithmetic.

**§8, a merge conflict is not two piles of text.** The lead's "keep both sides" resolver assumed a conflict block holds each side's whole addition. Git had aligned the identical last lines of both parcels' final functions - a closing brace and a blank line - and hoisted them out of the block, so "both sides" plus the hoisted tail closed one function and nested the other; the compiler said so in the next gate, twenty seconds in ("invalid storage class for function"), with a shadow warning for every local. The resolution is each side followed by the shared ending. Two lessons: a resolver that has not read the lines after the block has not read the conflict; and the gate that catches a bad merge is the one that runs first after it, which is why the host build sits at the top of the lead's script.

**§6, what a verifier finds that a parcel cannot.** Every verifier in this round found at least one thing the parcel's own gates could not have shown: a cost class (V1), a flag arm reading stale lanes (V4), a read before a check (V2), a defect invisible in bytes and an area column nobody had priced (V3). None was a wrong bit; each was a property the parcel had no instrument for - a cycle count, a yosys cell count, a poisoned pointer, a control that revives a lane. The parcel measures what its brief names; the verifier measures what the brief did not know to name. That is the argument for a verifier per parcel, and this round has four data points for it.

**§6 and §7, a send-back can be a cost, not a defect.** The round's fourth send-back was for a number no gate holds: the mask's logic, measured by a verifier with a tool the parcel had not thought to run on itself. The parcel's answer was not a patch but a different shape for the same function, and the numbers it produced (a factor of nearly six under the flow the project's own lint runs) are the kind that decide whether a feature is in an image. A brief for RTL should say which numbers will be measured at verification - cycles, cells, the mux count - so the parcel measures them first; and a verifier for RTL should have yosys on its list by default, as this round now does by example.

**§5, the lead's patches are parcels without a verifier.** Twice today a lead-side change was wrong on its first run (the stale binary; this guard), and both times a gate caught it - a count that did not move, a segfault. The lead had written the rule "a rule that dereferences a caller's buffer belongs behind every rule that does not" into two briefs and then got the arithmetic of the bound wrong while applying it. The method should say that the lead's own code goes through the same gates as a parcel's and, where it is more than a line, through a verifier: the lead is the one author in a round nobody disconfirms by default.

**§9, the card day's diagnosis (added 22:00).** The round's first
image failed its first gate on the card, and for twenty minutes the
RTL was the suspect: the bench had passed under both simulators, the
host side had been proved right register by register, and what was
left was synthesis. What moved the diagnosis was not reading the RTL
again but three instruments in cost order, each built to disconfirm
one reading - the fingerprint of a masked slot (WHAT value is there,
not whether it is wrong), FLAGS under a poisoned mask (did the tile
apply the mask: yes), and a pattern in a staging pad (are strobes
honoured: yes). Three facts that fit only one story, and the story was
the host's: a staged output buffer whose device copy held the previous
run. No bitstream was rebuilt. The lesson is the verifier's again, an
instrument per hypothesis and the cheapest first, with the RTL last
because it is the most expensive thing to be wrong about. The second
lesson is about what the suite could not see: cocotbext's memory
starts every test empty and the C executor writes the caller's buffer
in place, so no host in the suite ever had a device copy with a
previous run in it. The one test that did was device-test's masked leg
on the card, which is why it caught the defect and nothing else could
have. The seam test worth adding is exactly that one, against a
software "device" whose buffers are not the caller's. The 128-body
crash that followed was the same shape in a different place: a size
the whole round's tests never reached (64 lanes everywhere), and a
runtime's page-granular behaviour behind a beat-granular capacity.

## What is not yet known (at the end of the build phase, 18:00)

The build phase is complete: every parcel is merged and every merge
was verified on the box at its tip except the last, whose suite is
running as this is written. What the round cannot know from a host:
the image's timing and utilisation at 135 MHz with the mask's logic in
it (V3's area column, after P3's rewrite); the card's numbers for the
gather (one HBM round trip a gathered element is the model's
prediction), for the mask (one round trip a block), and for the
accumulator's segmented sums against the seq6 entry; whether the
composed elementwise run's STATUS word matches the dense run's on a
tile; whether `device-test`'s resident-binds assertion, which has
never counted on any host, passes the first time it counts; and
whether cft-rebound's agent adopts what was built, which is theirs.
The image build and the card day are the lead's and the owner's, after
this document's build phase ends; their rows go in the timeline when
they exist.

### What is known now (22:10, the card day's end for the single tile)

- **The image works, and the round's RTL was never wrong on the card.**
  Both failures the card produced were the host's: a staged output
  window whose device copy held the previous run (the mask's "every
  masked lane written"), and buffer capacities that were beat-granular
  where the runtime is page-granular (the crash above ~300 lanes).
  Neither could have been seen by a bench (memory starts empty, the C
  executor writes in place, every test ran at 64 lanes). Both were
  found by instruments built in the hour, each to disconfirm one
  reading; neither needed a rebuild.
- **The numbers the round was for** are in `docs/VALIDATION.md` (the
  card day's second half): 310-340 ns a gathered element at every
  format; 128 bodies at x1.5-1.7 against the dense calls with the
  host gathers removed as well; the mask at 1.3% of a run; the
  segmented reduction at 2.4 ms against 91 ms in a thousand calls.
- **The quad**: its first implementation missed 135 MHz by 0.363 ns on
  the elementwise engine's oldest critical path (not the round's
  logic); the second, with the placement and routing directives,
  closed at +0.040 ns on 2026-09-16 and ran green on four tiles within
  two minutes of staging. The pair is the round's deliverable on the
  card.
- **Still open**: the ledger's fold into VALIDATION and memory; the
  method proposals above, which are Logan's to settle.

## What METHOD.md should say differently (proposed at the end of the round's build phase, 2026-09-15 18:00; adopted in full on 2026-09-16 - Logan went over every item - and integrated into METHOD.md that day, with the card day's lessons beside them)

Every item below is one sentence the method does not have and this
round paid for; the row or paragraph that paid is in brackets. None is
a retraction of the method - the round confirmed its shape (a seam
first, parcels in worktrees, a ledger with a push channel, a verifier
that disconfirms, serial merges with the suite after each). They are
the places the method was silent and the round had to decide.

**§1-§2, the failure mode and the seam.**

- **Read the requester's code, not its ask list.** The plan's largest
  corrections came from there before dispatch: ask 6 was already
  delivered, asks 1 and 4 were one mechanism, ask 5's ceiling was two
  percent. [02:00-03:30; §1]
- **A seam's refusal belongs in every backend**, never in the one
  function the first parcel will edit; P0 put the indexed refusal where
  P1 removed it, and the remote route opened. [§2, 08:2x]
- **A value statement names the measurement that would falsify it.**
  "The mask removes idle lanes' compute and bytes" was a claim that read
  as a fact until P3 measured that the sequencer issues per beat; the
  compute half was never there. A brief's stop line should say what to
  measure before stopping, because the measurement made the report
  decidable in one reading. [12:37; §2 and §7]
- **A wave boundary is the one moment a brief can be updated.** Fold
  the ledger into the next wave's sections there and then, or the next
  wave starts from the plan as it was written the night before. The
  ledger's `For:` lines are what made twenty minutes enough. [11:41; §2]
- **Name a base commit "at or after"** and put the exact tip in the
  dispatch message, where it can be right; a brief that names its base
  exactly is wrong the moment it is itself committed. [11:41]

**§3, the brief.**

- **Derive the ownership list from the seam's own comments**, or diff
  the two before dispatch: the first escalation of the round, two
  minutes after dispatch, was a CSR edit the brief required and the
  ownership list forbade. [06:32; §3]
- **A brief's cost model names the divisor it assumes.** "A gathered
  element costs about one beat" assumed a read side that pipelines; it
  keeps one burst in flight, and the number was a round trip. [§3, 08:2x]
- **Name the trap, and name what will be measured at verification** -
  cycles, cells, the mux count, a poisoned pointer - so the parcel
  measures it first. The named trap got solved (P2); the unmeasured
  column got a send-back (P3's area). [12:49; 14:56; §6 and §7]
- **Verify the functions you name.** Two briefs named functions that
  did not exist (`cftw_run_ex`, an elementwise `runEx`) and one carried
  a premise about the loader that was wrong as a mechanism; each cost a
  parcel its first half hour and was found by a grep. [11:53; 15:30; §3]
- **A prohibition is written as the command to use.** "Never kill by
  image name" was broken under pressure; `docker ps --no-trunc`, then
  one container ID, was not. [08:14; §3]
- **Environment facts belong in the brief, not in the parcel's first
  hour**: which interpreter runs the gates, the heredoc and CRLF traps,
  the pipeline that deadlocks at zero CPU, the vector sets a fresh
  worktree lacks. Every one of these was learned twice. [P1.md, P2.md,
  P3.md, P5.md entries]

**§4, the ledger.**

- **Stamps are substituted, not typed.** Every author - the lead three
  times, P1, P4, V4, P3, P2 - typed a guessed time at least once, and
  every guess ran ahead of the clock by three to ninety minutes. The
  fix that held was mechanical: write the entry with a placeholder and
  let the append substitute `date`. [§4, twice]
- **The lead's watcher skips the lead's own file**; every entry the
  lead wrote came back as a notification. [§4]
- **A correction is linked from the entry it corrects** - an appended
  "see HH:MM" line under the old entry is an append, not an edit - and
  a number a sibling might reuse is restated in the form the sibling
  would search for. A retracted count was in the file for fifteen
  minutes, in order, headlined CORRECTION, and was used once anyway.
  [13:34; §6]
- **A background job that writes to the ledger stamps at write and says
  what it describes.** A launch wrapper from 11:24 appended its entry
  at 12:45, an hour after the state it described had been superseded.
  [12:45, 12:46]

**§5, gates and negative controls.**

- **A single target's exit code is not a verdict** where the harness
  cannot set one; the brief says which command is. P4 found it; main
  fixed it the same morning. [07:30; §5]
- **The lead's code goes through the same gates as a parcel's**, and
  where it is more than a line, through a verifier. Twice the lead's
  own change was wrong on its first run - a stale test binary standing
  in for a gate, a bound computed from the wrong example - and both
  times a gate caught it, not a person. [11:50; 17:39; §5 twice]
- **Print the build time of every binary a gate runs.** The tell for
  the stale binary was a count that did not move; the line that would
  have said "05:13" costs nothing. [11:50]
- **When a mechanism is enforced in two places, a gate that reads the
  cheapest observable cannot see a defect in the other.** The mask was
  enforced at the active set and again at the drain strobes; the
  strobes hid an ACTALL that revived a masked lane from every byte-level
  case, and only a flag could tell. [14:56; 16:04]
- **A crash can be a gate's faithful signal** when the property is "no
  read happened": a regression cannot pass it silently, which is what
  matters. [13:59]
- **A probe that has caught a defect goes into the suite.** The
  reduce-then-program probe sat outside `make sim` and caught two real
  defects from there; it is in the suite now, and the third seam case
  joined it. [10:24; 12:18]

**§6, the verifier.**

- **A verifier per parcel pays.** Four verifiers were 38 percent of the
  agents' tokens and produced four send-backs, none for a wrong bit:
  each found a property the parcel had no instrument for - a cost
  class, a flag arm reading stale lanes, a read before a check, a gate
  hole beside an unpriced area column. The parcel measures what its
  brief names; the verifier measures what the brief did not know to
  name. [§6, five paragraphs]
- **A verifier's report is due when its LIST is exhausted, not when its
  first pass is** - "no defect" was posted before the one target outside
  the list ran, and the lead had the parcel staged within minutes of it.
  [10:07, 10:24; §6 and §8]
- **A verifier's default list carries the instruments the parcel lacks**:
  yosys cell and mux counts for RTL, a poisoned pointer for anything
  that reads a caller's buffer, "derive the increment" for any count a
  report quotes, and the lead's own artefacts (the seam paragraph, the
  plan's premise) beside the parcel's. [09:29; 10:49; 13:34; 14:56]
- **The scoped re-check after a fix is the default** - eleven to
  twenty-three minutes each here - not a re-run of the whole list.
  [10:38; 12:09; 13:59; 17:31]
- **A verifier's report distinguishes "the shipped code is right" from
  "the gate would catch it if it weren't"**; the second half produced
  most of this round's send-backs. [§6]

**§7, what the lead keeps.**

- **A staging branch per merge, the suite on the box at the staging
  commit, and main moves on the verdict**; a second, third and fourth
  checkout on the box so a send-back never queues behind a sibling's
  hour. A merge is a push, not a staging. [11:06; 11:47; 12:57; §6 and
  §8]
- **A merge conflict is not two piles of text.** Git hoists a shared
  ending out of the block; a resolver that has not read the lines after
  the block has not read the conflict, and the compiler is the gate
  that says so twenty seconds later. [14:12; §8]
- **The docs sweep happens in the lead's idle time during the round**,
  for every file no parcel touches, so the end of the round is one
  section, not a sweep. [15:03]
- **A merge with no RTL in its diff gets no RTL suite, and the ledger
  says so** rather than the lead pretending it ran one; the box's run
  at the next merge with RTL covers the combined tree. [14:09]
- **The lead's summary to the owner carries the cost**, from the
  cards, per agent, with the verifiers' share stated. [Cost section]

**§8, sequencing.**

- **Dispatch on the fast simulator; the slow one confirms in the
  background.** The owner said so; the confirmation changed nothing all
  day. [06:3x; every Icarus tail]
- **A send-back needs no re-brief**: the harness resumes the agent with
  its whole context, so a fix costs 25-30 minutes of parcel and 20-30 of
  verifier, and the hour is the box. The method assumed a parcel cannot
  be re-entered; it can, and the loop is cheap enough to run three times
  on one parcel. [§6 and §8]
- **A stop line in a brief fires for value, not only for size**: the
  parcel priced smallest stopped at its line because the value was not
  there, and the plan is corrected with its table. [12:37]
- **The round's build phase is done when every parcel is merged and
  box-verified; the image and the card day are the lead's and the
  owner's, after.** [17:49]

## Cost of the round (from the desktop app's agent cards, read by Logan at 11 hours)

| agent | wall (card) | tokens | tool uses |
|---|---|---|---|
| P1 indexed inputs | 5 h 15 min | 676.0k | 425 |
| P4 beat-wide accumulator | 4 h 54 min | 547.6k | 252 |
| V4 on P4 | 2 h 54 min | 503.8k | 266 |
| V1 on P1 (card shows the last resume) | 23 min | 603.3k | 31 |
| V3 on P3 | 1 h 44 min | 365.9k | 167 |
| V2 on P2 (card shows the last resume) | 12 min | 386.8k | 64 |
| P2 composed run_ex | 2 h 11 min | 614.7k | 410 |
| P5 bindings entry point | 52 min | 411.4k | 353 |
| P3 lane mask | 4 h 22 min | 814.1k | 939 |
| **nine agents** | **22.8 h of agent wall inside an 11 h round** | **4.92M** | **2,907** |

The lead used about 1.6M tokens over the same 11 hours (Logan's figure), so the round to this point is about 6.5M tokens by the cards' measure, of which the four verifiers are 1.86M (38 percent of the agents' total) and they produced four send-backs, each for something the parcel could not have seen. **To the round's end** (Logan's figures, 2026-09-16): the wall was about 24 hours, of which the last ten were the tile builds and the runs against them, with the lead alone; the agents' tokens are the cards above, and the lead's grew by about a million handling the builds, the card days and the records - roughly 2.6M for the lead and 7.5M for the round. The largest parcel (P3) cost 814k and 939 tool uses for a feature the round measured to be worth bytes and flags rather than compute; the smallest (P5) 411k for the entry point the plan had assumed existed. Agent wall time exceeds the round's wall by 2.1x, which is the parallelism the method bought; the lead's own idle time went to the docs sweep.

**The session panel's figures** (read by Logan after the twelfth hour), which
are a different measure and do not reconcile with the cards by addition:
API time 23 h 40 min across every agent; human-active time 1 h 38 min;
+15,544 / -987 lines; model split Opus 76 percent, the lead's model 24;
cache hit 99 percent. Tokens: input 92.9k, output 818.9k (the parcels' and
verifiers' 797.2k, the lead's 21.7k), cache read 3.5 billion, cache write
37.5 million. The cards' "tokens" count what each agent's turns carried;
the panel counts what the API was asked for - so the 819k of output is the
round's generated text and code, and the 3.5 billion is the same context
re-read on every turn at a 99 percent cache hit. The round ran on a
subscription; no fees were paid, and the panel's price estimates are not
recorded here.

## The round's end (2026-09-16, 12:30)

**What was delivered.** ABI 0.14 and sequencer revision 6: an input
block fetched through an index table (asks 1 and 4, one mechanism), a
per-run lane mask (ask 5), a beat-wide reduction accumulator, the
composed indexed elementwise route, and the bindings' entry point -
five parcels, four verifiers, every one merged and box-verified by the
eleventh hour. A pair of images from one commit at 135 MHz: the single
built and run on the card the same night; the quad closed on its second
implementation and ran green on four tiles within two minutes of
staging. Every published case reproduced on silicon through one tile
and through four. A conformance profile written on the last morning,
with the vector sets' hashes as its identity. And the numbers the
requester asked for, measured rather than promised: a gathered element
at 316 to 335 ns, one call for a thousand segments at 1.5 to 2.4 ms
against 91 ms of calls, four tiles at exactly four times one on
resident work.

**What went wrong, and where the record has it.** Two host defects the
suite could not see and the card found in its first hour - a masked
run reading a device copy the caller's bytes were never uploaded to,
and buffer capacities kept at page granularity behind a per-beat
contract - both fixed the same night, neither in the RTL, no rebuild.
The quad's first implementation missed timing by a third of a
nanosecond on the engine's oldest path, six hours of build with nothing
to show, and closed on the second with the tool's own directives. A
stale test binary standing in for a gate, twice. Guessed timestamps
from every author. A driver mistake in the saturation runs caught by
the script's own check. Each is a row in the timeline and a rule in
METHOD.md now.

**What carries forward.** The reductions that do not overlap across
tiles, the buffer allocated for a bound role, program runs on one
tile, beat skipping for masked lanes - all in the roadmap's debts, as
the seed of the next card day or the next round. The requester's four
asks are built and measured; adopting them is that project's own work.

**The ledger** is archived at archive/round2-ledger.zip (not in this kit)
(eighteen files: the lead's 84 entries, the five parcels', the four
verifiers', the seven urgent messages) for a reader of this case study
who wants an entry by its time; the working copy is deleted, as the
method says.
