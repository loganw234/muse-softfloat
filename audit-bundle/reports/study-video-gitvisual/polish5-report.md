READY

Text/pacing revision of v4 per ledger/briefs/study-video-textpacing.md
(Agent B, git segment). v1-v4 untouched (sizes verified); v5 beside
them: render_gitvisual5.py, gitvisual5.mp4, stills5/, beats5.md,
audit_text5.py + audit_text5.json, measure_sync5.py +
sync_measurements5.json, verify_handoff5.py, render_checks5.py.
No 1080p twin this round (not requested; make one like make_twin4.py
if assembly still needs it).

## Clip (probe-verified)

- gitvisual5.mp4: **102.0 s exactly (delta +14.0 vs v4's 88.0 s)**,
  2560x1440, 30 fps, H.264, silent, 3,060/3,060 frames decoded
  clean (video/probe.py, decode_rc 0), 30,201,691 bytes.
  Render wall 132 s, frames streamed to ffmpeg (never buffered).
- Run: $MSF_PYTHON render_gitvisual5.py --out gitvisual5.mp4
  (workspace .venv).
- Film budget: assembly v4 was 145.5 s with this segment at 88.0 s,
  so the other segments total 57.5 s; with v5 at 102.0 s the film
  is **~159.5 s, inside the <=160 s ceiling** (before music, and
  before any duration change from Agent A's parallel revision).
  The +14.0 s is bought exactly as briefed: word cuts first
  (below), then dwell = THE RULE on what remains. Breakdown: popup
  holds 7x2.3 = 16.1 s -> rule dwells summing 30.0 s (+13.9);
  bridge 2.4 -> 2.5 s (+0.1, keeps the replay on a whole second).
  Every other duration is v4's, shifted later in wall time only.
- Stills: stills5/ 31 MP4 grabs + 20 render checks; eyeballed this
  session (all popups, all three windows incl. PASS frames,
  sendbacks, box sequence, both handoffs).

## Handoffs (measured on the MP4, verify_handoff5.py)

VALUES unchanged from v1-v4 at 2560x1440 (3,686,400 px):
- IN t=0.5: all 3,686,400 px exactly (255,255,255).
- OUT t=101.5: 3,685,908 px (2,3,8) = outro2 first frame;
  492 px (2,2,10) within 2 levels per channel - encoder noise
  of the same class as v3/v4 (v4: 1,024 px at (2,3,6)).

## THE RULE, as applied

Dwell = smallest 0.5 s-grid multiple >= max(1.5 s, 0.5 + words/2.5),
computed in-code (`rule_dwell`); popup arrivals/holds are derived
from the copy itself, so copy and dwell cannot drift apart.
Headlines <=6 words, body lines <=10 words (asserted for popups in
audit_text5.py), <=2 new lines per beat (window captions that v4
drew from lt=0 or all at once are now gated to staggered beats;
the tokens zoom's third line is its own later beat). Per-claim
src stamps collapse to ONE short tag per scene: chase
"src: project RECORD + git log", replay footer
"src: git log @ a73e97d", and one in each window's title bar.
Full sourcing is preserved below. Legend unchanged, per brief.

Total on-screen copy (audit inventory of 63 blocks, distinct
strings incl. stamps/tags/HUD/box; commit-subject ticker and
branch-name data labels excluded from the total, see audit notes):
**633 words (v4) -> 335 words (v5), -47.1%** (target was ~-33%).

## Copy table (old -> new; words; dwell before -> after)

Chase popups (dwell before: flat 2.3 s for all; word counts include
v4's per-popup src stamp, now removed):

| popup | v4 copy (words) | v5 copy (words) | dwell |
|---|---|---|---|
| parcel | "PARCEL / parcel-f32: 173 binary32 instantiations / owns src/msf32.c only - shared kernels stay lead-owned" + src (17) | "PARCEL / 173 binary32 routines / one file: msf32.c" (7) | 2.3 -> 3.5 s |
| escalation | "ESCALATION / parcel-f32 escalates: pack tininess is wrong (Clause 7.5) / Berkeley disagreed; every self-consistent gate had passed / ruled for the parcel - lead fixes 53acb1a / b37fb12" + src (32) | "ESCALATION / tiny results packed wrong / fixes: 53acb1a / b37fb12" (9) | 2.3 -> 4.5 s |
| verifier | "VERIFIER - SENDBACK / verifier-w5twiddledoc: NOT READY / printed SHA-256 is 56 hex chars - truncated, invalid / measured 64-char value is what the demo tooling enforces" + src (26) | "VERIFIER / SHA-256 too short / 56 characters, needs 64" (8) | 2.3 -> 4.0 s |
| plants | "PLANTS GRADED / Wave 1: 9 of 10 planted defects caught / the miss: weakened generator boundary, filed benign / detection without the byte-identity norm" + src (28) | "PLANTS / 9/10 planted bugs caught / one miss, harmless" (8) | 2.3 -> 4.0 s |
| gates | "GATES / smoke 52,168 vectors - standard adds 1,117,504 / 9/9 negative controls refused / board: 2,767 sampled vectors, host == RP2040 hash" + src (24) | "GATES / 52,168 quick + 1,117,504 standard tests / chip matches computer exactly" (11) | 2.3 -> 5.0 s |
| study | "STUDY / feasibility first, read-only, in scratch / two study visuals wait ahead - as gates" + src (17) | "STUDY / try in scratch first / two studies wait ahead" (9) | 2.3 -> 4.5 s |
| lead merge | "LEAD MERGE / only READY work rejoins the main line / 2843792 - Merged Wave 1 binary32 parcel (READY 26c76aa)" + src (22) | "LEAD MERGE / finished work joins main / first merge: 2843792" (9) | 2.3 -> 4.5 s |

Sendback labels (badge "SENDBACK - FIXED - REJOIN" -> "FIXED -
REJOINS"; per-label src lines removed; dwell before = measured
v4 apex->rank+5 on v4's cursor, after = measured v5 visible
apex->rank+18 minus gate overlap):

| rank | v4 label + sub + src (words) | v5 label + sub (words) | dwell |
|---|---|---|---|
| 7 | "SENDBACK FIX 4cdb912 / verifier-w1prep N1: dead NaN branch fixed" + src + badge (18) | "SENDBACK FIX 4cdb912 / error-value branch fixed" (6) | 0.48 -> 1.78 s |
| 12 | "RE-GATE: tininess fix loops back / 53acb1a / b37fb12 into w1-f32 + w1-f64, re-gated READY" + src + badge (27) | "TININESS FIX RETURNS / both rechecked: READY" (6) | 0.42 -> 1.70 s |
| 38 | "LEAD FIX 83622cf / runner char-to width fixed before W3 / IAS15 land" + src + badge (23) | "LEAD FIX 83622cf / runner width fixed" (6) | 0.95 -> 4.53 s |
| 99 | "DEFECT FIX 048aa29 / exp2 delta shape + near-1 attractor hardened" + src + badge (19) | "DEFECT FIX 048aa29 / exp2 edges hardened" (6) | 0.23 -> 1.02 s |
| 114 | "VERIFIER SENDBACK > FIX a41f026 / NOT READY: SHA-256 was 56 hex chars - now the 64-char value" + src + badge (26) | "VERIFIER SENDBACK a41f026 / now 64 characters" (6) | 0.27 -> 1.59 s |

Gate windows (titles <=6 words now; dwell for window blocks is
measured to lt 7.2, when the window starts closing):
- "WINDOW - IAS15 ON SILICON / merge d9718cf, rank 44 - its true
  beat; the stream waits" (16) -> "IAS15 RUNS ON THE CHIP /
  merge d9718cf - the stream waits" (11).
- "WINDOW - KISSFFT STUDY / merge 32bbd93, rank 69 - the stream
  waits" (12) -> "KISSFFT STUDY / merge 32bbd93 - the stream
  waits" (8).
- "WINDOW - TOKENS, RECOUNTED / metrics merge a1a888f, rank 134
  (editorial anchor, S6)" (12) -> "TOKENS, RECOUNTED / metrics
  merge a1a888f (chosen anchor)" (7); S6 wording plain-ified, the
  anchor honesty stays on screen.
- "SIX BOARDS (1 Pico + 5 Zero) - mockup" -> "SIX BOARDS
  (mockup)", now its own beat at lt 0.8. "PASS - all six LEDs
  hold solid" (7 w, would need 3.5 s) -> "PASS" (1 w): the PASS
  hold is by design exactly 1.5 s (lt 6.5-8.0), and the six
  solid LEDs beside it say the rest.
- IAS15: "figure-8 orbit (illustration) / real ICs, integrated
  in float64" -> "(picture) / real start, drawn on desktop";
  "IAS15FH1 H_state: desktop == RP2040" -> "state check-values:
  desktop == chip" (per-row "desktop == RP2040" kept - RP2040
  is the chip's actual name); two proof lines -> one
  ("check-values at right are the proof", lt 1.6); "IAS15 on
  RP2040 via muse-softfloat (AEABI surface)" + src line ->
  "IAS15 on the chip, via muse-softfloat" (lt 4.0); stamp
  "2,001 / 2,001 RECORDS / BIT-IDENTICAL ON SILICON" ->
  "2,001 / 2,001 IDENTICAL / desktop == chip", landing at
  lt 3.5 (hash rows type in 0.8 s steps from lt 0.4, was
  1.05 s steps from 0.6; stamp dwell 2.0 -> 3.7 s).
- KissFFT: "waveform -> twiddles -> spectrum" -> "sound wave
  in, spectrum out"; "(illustration; spectrum via numpy - NOT
  KissFFT output)" -> "(picture only - not KissFFT output)"
  (honesty kept); input caption "shared LCG input, N=256
  complex fwd (cfg 0)" DROPPED (the stamp lands at lt 3.6 now
  and would have covered it mid-dwell; detail below);
  "exact-fraction twiddles e^-2pik/N" -> "exact twiddle
  factors" (lt 2.7); "magnitude spectrum builds bin by bin"
  -> "spectrum, bin by bin" (lt 4.5); stamp "12 / 12
  CONFIGURATIONS - HASHES RECORDED" + src (9 w @0.9 s) ->
  "12 / 12 SETUPS CHECKED / check-values recorded" (7 w
  @3.6 s, appears lt 3.6 not 6.3).
- Tokens: "REGENERATED at a73e97d - definition below; v1
  number retired (stale)" -> "recounted at a73e97d";
  "project billed = input + output, 93 labeled rows
  (usage.jsonl)" -> "billed = input + output (93 rows)"
  (lt 0.6); in/out+cache as two short lines at lt 1.2
  ("input 1,190,490,305 + output 5,638,465" /
  "cached 1,165,653,139 sits inside input" - numbers
  unchanged, verified against gate2_numbers.json);
  "owner-typed ~1,928 tokens (chars/4, frozen study est.) -
  amber tick is to scale" -> "you typed ~1,928 tokens
  (amber, to scale)" (lt 1.8); zoom "x500,000 ZOOM (drawn
  parametrically) / YOU: ~1,928 tokens [1,350-2,507] / 40
  owner prompts - 7,713 chars (study, frozen)" ->
  "x500,000 ZOOM / YOU: ~1,928 tokens" (lt ~3.2) then
  "40 prompts, 7,713 characters" as its own beat (lt 4.2;
  the [1,350-2,507] band moves to this report); final
  "~1 : 620,399 - human share 0.00016% - 7,756 logged msgs"
  + src (19 w @2.4 s) -> "~1 : 620,399 - 7,756 messages /
  your share: 0.00016%" (9 w @4.6 s, appears lt 2.6 not 4.8).

HUD/chase/box: "2 - THE REPO, AS IT HAPPENED (marble track)"
-> "2 - AS IT HAPPENED"; beat strings -> "next: <window>" /
"close: HEAD a73e97d"; the 19-word footer key -> the replay
src tag + "green = merge | red loop = fix"; "NEWEST ^
(up-stream)" / "OLDEST v (behind)" -> "NEWEST ^" / "OLDEST v";
chase strip -> "1 - THE CHASE | flat plane / lifting into
3D... / marbles split at branches"; box sub "every system
files its colours away - then the lid shuts" -> "every
system packed away"; the counter's kept-list dropped (the
box-front stamps RECORD/LEDGERS/VECTORS/METRICS say it).

Facts that moved off-screen into this report (claim pools,
sources and every number that is the point are unchanged;
on-screen numbers re-verified against history.json /
gate2_numbers.json / video/data.py): gates popup's 9/9
negative controls and 2,767 sampled board vectors;
escalation's Clause 7.5 / Berkeley detail; plants' missed-
plant identity; KissFFT N=256 cfg 0 shared-LCG input; IAS15
names IAS15FH1 / H_state / AEABI surface; tokens owner band
[1,350-2,507] and chars/4 method; lead-merge READY hash
26c76aa. Full per-popup sources (as in history.json):
parcel - muse-softfloat/docs/RECORD.md Wave 1 (lines
323-332); escalation - RECORD.md Wave 1 (334-347) +
docs/metrics/escalations.jsonl wave1 parcel-f32
2026-10-26T22:11:37-07:00; verifier -
ledger/verifier-w5twiddledoc.md, fix a41f026; plants -
RECORD.md Wave 1 (348-363) + docs/metrics/plants.jsonl;
gates - RECORD.md Wave 1 (364-374, whole-run SHA-256
4d7c2a28... host == board); study -
scratch/study-kissfft-visual/report.md +
scratch/study-tokens-visual/report.md; lead merge - git
log merge 2843792 (parents 52a6715 + 26c76aa). Sendbacks:
4cdb912 (main), RECORD Wave 1 + merges 9bb8723/80cbc97,
f3c48b8 + 83622cf (main), 048aa29 (wave5-exp2),
ledger/verifier-w5twiddledoc.md + fix a41f026. Windows:
video/data.py SOURCES[ias15] + RECORD Wave 3;
scratch/study-kissfft-visual/report.md; regen_gate2.py <-
usage.jsonl @ a73e97d + study-tokens-visual (owner estimate).

## Dwell audit (audit_text5.py -> audit_text5.json)

63 blocks inventoried with words, dwell given, rule minimum.
Conventions: word = whitespace token (a 64-hex check-value
and the big token count each count as 1 - they are read as
one artefact, not word by word); window dwell runs to lt
7.2 (close start) except PASS, whose specified hold is the
1.5 s to window end; cursor-paced dwells (sendbacks, branch
labels) are measured by inverting cursor_rank, gate-window
overlap removed. **Every popup and every window block meets
THE RULE exactly or better** (popups sit exactly on their
rule dwell by construction). Named violations, all
cursor-paced event/data labels whose dwell is set by the
unchanged v4 leg speeds:

| block | words | dwell given | rule min |
|---|---|---|---|
| sendback label+badge, rank 7 | 6 / 3 | 1.78 s | 3.0 / 2.0 s |
| sendback label+badge, rank 12 | 6 / 3 | 1.70 s | 3.0 / 2.0 s |
| sendback label+badge, rank 99 | 6 / 3 | 1.02 s | 3.0 / 2.0 s |
| sendback label+badge, rank 114 | 6 / 3 | 1.59 s | 3.0 / 2.0 s |
| branch labels, worst of 25 lanes | 1 | 1.11 s | 1.5 s |

(Rank 38's sendback passes at 4.53 s.) These labels ride the
marble to their loop apex and stay anchored there - that
anchoring is the v4 sync idiom, and in the fastest leg the
apex leaves the drawn 66-rank window in ~1 s, below even
the rule's 1.5 s floor. Meeting the rule here would mean
slowing the replay legs (owner pacing, more duration) or
detaching the labels from their events. Instead they were
cut to 6 words (from 18-27) and their visible dwell raised
3-6x vs v4 (readable to rank+14, dimmed to rank+18, the
window edge; branch-label tail 8 -> 16 ranks). Two further
scope notes, named not silent: the HUD commit ticker is a
data readout (real date/hash/subject at the cursor, changes
as the cursor moves), not a reading block - unchanged from
v4; and window text remains drawn (shrinking) during the
7.2-8.0 s close, which the audit does not count.

## Marble sync re-measurement (measure_sync5.py)

Machinery untouched in behavior: marble position is still a
pure function of head_x / cursor_rank; the only clock change
is that chase holds are longer (marbles wait on their nodes)
and all post-chase wall times shift by +14.0 s. Measured on
v5 with its own camera/model (px at 1440p, marble centroid
vs node center at the continuous event time / nearest frame):

| event set | n | v4 at-event max | v5 at-event max | v5 nearest-frame max |
|---|---|---|---|---|
| chase node lightings | 7 | 0.0 | 0.0 | 0.0 |
| merge splits | 25 | 0.0 | 0.0 | 22.1 |
| merge absorbs | 25 | 0.0 | 0.0 | 24.8 |
| exclusive-commit sample | 17 | 0.0 | 0.0 | 26.1 |
| sendback entries / exits | 5+5 | 0.0 | 0.0 | 7.6 / 5.0 |
| sendback apex vs stamp | 5 | 0.0 | 0.0 | 23.8 |
| gate arrivals | 3 | 0.0 | 0.0 | 0.0 |

BPM-pulse centroid drift in a gate hold: 0.0 px. Event
identity vs v4 asserted in the same run: NODE_X equal,
gate ranks (44/69/134) and 8.0 s durations equal, leg rank
spans and durations (8/5/7/4 s) equal, sendback ranks
equal, head_x at each arrival exactly NODE_X, cursor at
each gate t0 exactly the gate rank. Popup dwell growth did
not desync anything: events never moved, marbles wait.

## Carry-overs / debts

- Real history, topology, gates/windows mechanics, PASS
  six-LED 1.5 s hold, packaging (7 marbles, artefact
  stamps, lid waits for 7/7) all as v4; simplifications
  S1-S19 unchanged. Tokens numbers unchanged (billed
  1,196,128,770 = in 1,190,490,305 + out 5,638,465, 93
  rows @ a73e97d; still_087.7s.png eyeballed).
- Carried v4 visual debts: PASS impact ring briefly crosses
  window captions; in dense frames a branch label can kiss
  a sendback sub-line (stills at 47.0/48.5 s); chunky lane
  exits at the bottom edge; popup boxes keep v4's fixed
  width so short copy leaves white space at right.
- No 1080p twin rendered (see header). Assembly resolution
  flag from v3/v4 stands.
- Fences: scratch only + ledger append; nothing committed
  (`git -C muse-softfloat status` clean); v1-v4 files
  untouched (sizes verified); no path with cft in its name
  opened, searched or listed; stayed in this study dir;
  renders streamed and bounded (132 s, few-layer frames).
