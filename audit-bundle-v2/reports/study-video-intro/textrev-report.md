READY

# Text/pacing pass - Agent A (intro/outro + idea + why)

Brief: `ledger/briefs/study-video-textpacing.md` (THE RULE). Scratch only; repo untouched; nothing committed; all prior versions preserved byte-identical (verified in verify3.json). New scripts (old ones untouched): `render_v3.py` (this dir), `scratch/study-video-idea/render_idea2.py`, `scratch/study-video-why/render_why3.py`. Audit: `audit_textrev.py` -> `audit3.json`. Probe: `verify3.py` -> `verify3.json`. 1440p measurements: `measurements3.json`.

## Durations and film budget

| segment | old | new | delta |
|---|---|---|---|
| intro | 5.0 s | 7.0 s | +2.0 s |
| idea | 14.5 s | 22.5 s | +8.0 s |
| why | 32.0 s | 33.5 s | +1.5 s |
| outro | 6.0 s | 8.5 s | +2.5 s |
| FRONT total (A) | 57.5 s | 71.5 s | +14.0 s |

Film estimate with gitvisual4 (88.0 s, ledger study-video-gitvisual v4): 71.5 + 88.0 = 159.5 s <= 160 s (v4 assembly was 145.5 s). Agent B's gitvisual5 duration was still in flight when this ran; if v5 keeps v4's 88.0 s the film is 159.5 s before music. Dwell growth (+14.0 s front) is bought by the word cuts below plus three structural cuts (why lineup scene, idea prompt line, two option 'e.g.' lines) - each named in the copy table.

## THE RULE as applied (conventions, stated once)

- Word = whitespace token containing a letter or digit (em dashes, middots, arrows, `*`, `+`, check/cross/? glyphs are not words; circled numerals 1/2/3 ARE counted).
- Block = all text first appearing on one 0.5 s beat. Dwell given = beat time -> the moment the text stops being readable (scene cut, white-fade start, intro dive start, or clip end). Text persists (never dimmed below readable) until that moment, per the brief's persistence clause; new load per beat is capped at 2 lines and audited. Typed bubbles are timed from FULL text (stricter than first character).
- Reveal start = the beat the fade/pop begins (fades are 0.25 s, pops 0.35 s; card text appears at pop scale >0.6, up to ~0.2 s after the beat - dwells at exactly the rule minimum carry that much less full-size time).
- Phone chrome (9:41 / Muse / online / Message...) is excluded from word counts old and new: ambient UI furniture present from frame 0 for the whole clip either way.
- Headlines checked <=6 words (the two-line WHY NOT... headline counts as one 6-word headline; see audit3.json headline_checks, 0 failures). Every body line <=10 words (max seen in new copy: 7).
- Source tags on screen (max 1 per scene): why opt1 `(SF-0 section 8)`, opt2 foot `(SF-0)`; idea correct keeps `(illustrative)`; everything else's sourcing lives in options-facts.md / the reports, per the brief.

### Named interpretation risk (not counted as a violation above)

Dwell is measured as persistence (above). If the lead intended SOLO dwell (time until the NEXT new text appears), 59 of 73 new blocks sit below their rule minimum on that stricter reading (reveals are spaced one 0.5 s beat apart; every block still stays fully readable for its full rule dwell, and each scene's LAST block gets solo dwell equal to its persistence, which passes on both readings). A solo-dwell cut of the same copy would add roughly a minute and break the 160 s film; the persistence reading is also the one the v2 dwell regime used ('remains on screen for the rest of its scene'). Flagged for lead/owner, not hidden.

## Clips (probe-verified, video/probe.py full decode)

| file | duration | frames | bytes |
|---|---|---|---|
| intro3.mp4 | 7.0 s | 210/210 rc 0 | 863,260 |
| idea2-1440p.mp4 | 22.5 s | 675/675 rc 0 | 881,976 |
| why3-1440p.mp4 | 33.5 s | 1005/1005 rc 0 | 1,574,914 |
| outro3.mp4 | 8.5 s | 255/255 rc 0 | 732,530 |

All 2560x1440 @ 30 fps H.264, silent. Handoffs measured on decoded MP4 stills (3,686,400 px each):

- intro3 white hold (6.8 s): 0 non-white px - source (255,255,255), value unchanged.
- outro3 first frame: dominant (2,3,8) decoded (min 2, max 8) - source near-black (3,4,9), value unchanged, identical to the v1/v2 spec.
- idea2 bookends (0.2 s / 22.3 s) and why3 bookends (0.2 s / 33.3 s): 0 non-white px each.

## Intro/outro at native 1440p (re-measured, not rescaled numbers)

Whole 1080p design scaled parametrically by K=1.3333 (every coordinate, size, font, wrap width); frames drawn natively at 2560x1440 and streamed (v2's buffered encode would hold ~15 MB/frame x all frames at 1440p).
- Period ink centroid RE-MEASURED on the 1440p plate: raster [1561.46, 361.5] (ink 4x4 px, 4 dot components); font-metrics cross-check [1562.0, 362.0] (delta [-0.54, -0.5]); v1 formula would sit +17.0 px off in y at this scale. Scaled v2 centroid (1170.49, 272.0) x 4/3 = (1560.7, 362.7) for reference - the 1440p raster genuinely differs.
- Mid-dive proof (pre-encode, t=5.4 s, crop 144.8 px): period centroid [1278.9, 719.6] vs frame centre [1279.5, 719.5]: error [-0.6, 0.1] px, |e| 0.6 px (`still3_period_proof.png`, eyeballed - dot sits in the crosshairs).
- Camera clamps re-checked at 1440p (401 samples): intro max adjustment 0.0 px, outro 0.146 px (subpixel, final settle only - same class as v2's 0.0 / 0.101).
- Outro dots centroid re-measured: raster [1320.0, 545.3] vs layout [1319, 546]; reverse camera final crop 200xK = 267 px; camera curve shape unchanged (smootherstep log-scale; max |dlog-step| 0.01131).
- Timing changes for dwell: intro full message now holds 1.5-4.5 s (3.0 s = rule for 6 words) before the same 2.0 s dive; typing-dots beat shortened 1.0->0.5 s (no text). Outro reply lands at 2.5 s (dots breath folded into the pull-back); side panels now reveal in 6 staged beats (left card in 3 reading chunks) instead of one 6-line pop.

## Word counts (audit3.json; chrome excluded both sides)

| segment | old | new | cut |
|---|---|---|---|
| intro | 6 | 6 | 0.0% |
| idea | 195 | 132 | 32.3% |
| why | 337 | 198 | 41.2% |
| outro | 91 | 46 | 49.5% |
| TOTAL | 629 | 382 | 39.3% |

Intro shows 0%: its single 6-word inciting message cannot be cut; the intro+outro pair together goes 97 -> 52 words (-46%). Idea -32% (the brief's 'roughly a third'), why -41%, outro -49%.

## Copy table (old -> new; dwell = persistence of the containing block)

| seg | old (words, dwell) | new (words, dwell) | note |
|---|---|---|---|
| intro | Hey Muse, I've got an idea... (6w, 0.5s) | Hey Muse, I've got an idea... (6w, 3.0s) | unchanged (inciting line); dwell bought with a longer hold |
| idea | one sentence, then what it demands (6w, 2.5s) | for the RP2040 chip (4w, 4.0s) |  |
| idea | A software IEEE 754 floating-point library (6w, 2.5s) | Precise number maths in software (IEEE 754) (7w, 3.5s) | term kept once, in parentheses |
| idea | for the RP2040 — a chip with no FPU, (8w, 2.0s) | for a chip without maths hardware (6w, 3.0s) | RP2040 named in the sub-line; FPU = maths hardware |
| idea | where every float is already software — (6w, 1.5s) | All maths there is software. (5w, 2.5s) |  |
| idea | so real science code runs bit-identically: / same source on desktop and chip, same bits out. (15w, 1.0s) | Same answer everywhere. (3w, 2.0s) | two lines merged; bit-identical spelled out in why settle |
| idea | every result the correctly rounded one — every flag exact (9w, 3.5s) | the nearest answer, every time (5w, 5.0s) | plainer definition line (brief) |
| idea | representable / value A (3w, 3.5s) | value A (2w, 4.5s) |  |
| idea | next value / A + 1 ULP (5w, 3.5s) | the next number the chip can hold (7w, 4.5s) | brief worked example, verbatim |
| idea | one operation, done exactly — where must it land? (8w, 2.0s) | CUT (0w, -s) | CUT: question is carried by dot+arrow; also collided with verdict labels |
| idea | exact result / (infinitely precise) (4w, 2.5s) | exact answer / (no rounding yet) (5w, 3.5s) |  |
| idea | correctly rounded → A (3w, 1.5s) | correctly rounded → A (3w, 3.0s) | kept (term defined by this scene) |
| idea | a neighbour is a wrong answer (6w, 1.5s) | A neighbour is wrong. (4w, 2.5s) |  |
| idea | not close — exact: right value, right flags, every time  (illustrative) (10w, 1.0s) | Exact, not close. / (illustrative) (4w, 2.0s) | tag split out; flags point lives in why spec |
| idea | three real workloads, run on the chip (7w, 3.5s) | three real jobs on the chip (6w, 5.0s) |  |
| idea | orbital integrator (2w, 3.5s) | tracks planets (2w, 4.5s) |  |
| idea | binary64, bit-identical / desktop = chip, / every bit, every step (8w, 3.5s) | Desktop bits, every step / (binary64) (5w, 4.0s) |  |
| idea | guaranteed enclosures (2w, 2.5s) | answers with guarantees (3w, 3.5s) |  |
| idea | directed rounding: / down for one end, / up for the other (10w, 2.5s) | Down one end, / up the other (6w, 3.0s) | plain fact; term glossed in why spec scene order |
| idea | exact-angle FFT (2w, 1.5s) | live signals (2w, 2.5s) | FFT is inside the KISSFFT name |
| idea | sinPi / cosPi twiddles / made at runtime, / correctly rounded (8w, 1.5s) | Correctly rounded / sinPi/cosPi (3w, 2.0s) | 'live' (sub) = made at runtime; twiddles = the sinPi/cosPi values |
| idea | the short version — the film shows the rest (8w, 2.0s) | the short version (3w, 4.0s) |  |
| idea | briefed agents build it, parcel by parcel (7w, 2.0s) | Agents build it piece by piece (6w, 3.5s) | parcel = a piece (briefs in reports) |
| idea | every piece independently verified — (4w, 1.5s) | Each piece checked independently (4w, 3.0s) |  |
| idea | a verifier whose only job is to disconfirm (8w, 1.0s) | Verifiers try disproving it (4w, 2.5s) | disconfirm = try disproving |
| idea | watch it land, commit by commit, in a minute. (9w, 0.5s) | Watch it land. (3w, 2.0s) | drops the 'in a minute' length presumption (v2 known limit) |
| idea | BUT FIRST — / WHY NOT USE WHAT / ALREADY SHIPS? (8w, 1.5s) | BUT FIRST — / WHY NOT USE WHAT / ALREADY SHIPS? (8w, 3.0s) | unchanged; now staggered over 2 beats |
| why | The RP2040 has no FPU — every float is software. Three workloads go shopping. (13w, 1.5s) | RP2040: no maths hardware (FPU) (5w, 2.5s) | old line was 13 words (>10 cap); shopping half cut, jobs appear next scene |
| why | what actually has to run on the chip (8w, 6.0s) | what must run on the chip (6w, 4.5s) |  |
| why | NEEDS: (1w, 6.0s) | CUT (0w, -s) | CUT x3 cards: needs line is self-evident under the divider |
| why | orbital integrator / guaranteed enclosures / exact-angle FFT (6w, 6.0s) | CUT (0w, -s) | CUT in why only: subs introduced minutes earlier in idea prove-it cards |
| why | binary64 bit-identical, / desktop = chip, / every bit, every step (8w, 6.0s) | Desktop bits (binary64) (3w, 4.0s) | recap one-liner; full wording in idea card |
| why | directed rounding on demand: / round down / round up, / chosen per call (11w, 4.0s) | Down / up per end (4w, 3.5s) | recap one-liner; on-demand survives as 'per end' + spec row 1 |
| why | sinPi / cosPi twiddles / generated at runtime, / correctly rounded (8w, 2.0s) | Correctly rounded sinPi/cosPi (3w, 3.0s) | recap one-liner |
| why | TOGETHER, THAT'S A JOB SPEC (5w, 4.0s) | TOGETHER: A JOB SPEC (4w, 5.5s) |  |
| why | the IEEE 754-2019 semantics the three workloads stand on (9w, 4.0s) | what the three jobs need (IEEE 754-2019) (7w, 5.5s) |  |
| why | rounding attributes: all four, + tiesToAway (5w, 4.0s) | All five rounding choices (4w, 5.0s) | four+tiesToAway = five (count kept) |
| why | exception flags: invalid · div-by-zero · overflow · underflow · inexact (7w, 3.5s) | Five warning flags, always exact (5w, 4.5s) | flag names live in options-facts/SF-0, per source-tag rule |
| why | subnormals kept — never flushed to zero (6w, 3.0s) | Tiny numbers never zeroed (subnormals) (5w, 4.0s) | brief register; term once in parentheses |
| why | NaN payloads preserved through arithmetic (5w, 2.5s) | Error values keep their details (5w, 3.5s) | NaN payloads named in options-facts |
| why | formats: binary16 + binary32 + binary64 (4w, 2.0s) | Three number sizes (binary16/32/64) (4w, 3.0s) |  |
| why | correctly rounded — FMA, sqrt, sinPi/cosPi, hard cases (7w, 1.5s) | Correctly rounded, even hard cases (5w, 2.5s) | op list in reports; sinPi/cosPi on KissFFT cards |
| why | augmented add / sub / mul: head + exact tail (7w, 1.0s) | Exact leftovers (augmented) (3w, 2.0s) | head+exact tail = answer + exact leftover |
| why | five basic ops correctly rounded *  (+ − × ÷ √) (5w, 6.0s) | Five basic sums correctly rounded (5w, 4.5s) | asterisk caveat: rows below state the flush rules on the same card |
| why | subnormals flushed to zero — in and out (7w, 5.0s) | Tiny results silently become zero (5w, 4.0s) | brief worked example, verbatim |
| why | NaNs rendered as infinities — payloads gone (6w, 4.0s) | Error values turn into infinity (5w, 3.5s) | brief worked example, verbatim |
| why | one rounding mode: ties-to-even. No directed modes (7w, 3.0s) | One rounding choice only (ties-to-even) (5w, 3.0s) |  |
| why | exception flags: none exist (4w, 2.0s) | No warning flags exist (4w, 2.5s) |  |
| why | e.g. a tiny subnormal result → 0, silently. (7w, 1.5s) | CUT (0w, -s) | CUT: redundant once row 2 is itself the concrete statement |
| why | * five basic ops, under the flush rules (SF-0 §8) (9w, 1.5s) | (SF-0 §8) (2w, 2.0s) | scene's one source tag; wording preserved in options-facts.md |
| why | directed rounding?  not measured (4w, 5.0s) | Rounding directions? Not measured (4w, 5.0s) |  |
| why | exception flags?  not measured (4w, 4.0s) | Warning flags? Not measured (4w, 4.5s) |  |
| why | NaN payloads? subnormals? binary16?  not measured (6w, 3.0s) | Errors, tiny numbers, small size? Unmeasured (6w, 4.0s) | all three unmeasured items kept |
| why | compiler FMA contraction varies by target (SF-0 §9) (8w, 2.0s) | Same code, different bits per target (6w, 3.5s) | brief worked example register |
| why | e.g. a×b+c may fuse on one target, not another — different bits. (11w, 1.5s) | e.g. a×b+c differs by target. (5w, 3.0s) | old line was 11 words (>10 cap) |
| why | SF-0 gated none of it — unmeasured semantics can't carry a proof (11w, 1.5s) | Unmeasured proves nothing (SF-0) (4w, 2.5s) | scene's one source tag (section 9 in options-facts) |
| why | every float entry point is this stub (7w, 1.0s) | Every number call stops here (5w, 3.0s) |  |
| why | e.g. the first  a + b  in any workload never returns. (10w, 1.0s) | CUT (0w, -s) | CUT: sub-line already states every call stops; old line was 11 words |
| why | THE LINEUP vs THE SPEC / rounding attrs / 5 flags / subnormals / NaN payloads / b16+b32+b64 / correct rounding / augmented ops / BOOTROM / LIBGCC / CUSTOM / * five basic ops, under the flush rules (27w, 1.5s) | CUT (0w, -s) | WHOLE SCENE CUT: cell-for-cell recap of spec+option rows, zero unique claims; its rule dwell (~5 s) could not be bought inside the 160 s film |
| why | IEEE 754-2019 · binary16 / 32 / 64 · 849 instantiations (7w, 2.5s) | Three sizes · 849 versions (IEEE 754-2019) (6w, 4.0s) | instantiations -> versions (number kept) |
| why | five rounding attributes · five exact flags · payloads preserved (8w, 2.0s) | Five roundings, five exact warnings (5w, 3.5s) | payloads point = spec row 4 wording |
| why | subnormals kept · augmented ops · correctly rounded, hard cases in (9w, 2.0s) | Tiny kept · leftovers exact · correctly rounded (6w, 3.0s) |  |
| why | proven bit-identical on RP2040 silicon (5w, 1.5s) | Proven bit-identical on the chip (5w, 2.5s) |  |
| outro | Done — it held up. (4w, 3.0s) | Done — it held up. (4w, 6.0s) | unchanged |
| outro | 849/849 ops across b16/b32/b64. 411,213 vectors in the gate, IAS15 identical on all 6 boards. Small parcels; verifiers that only disconfirm. (21w, 1.0s) | Identical on all 6 boards. (5w, 4.5s) | 849 + 411,213 stay on the stat cards beside the bubble; parcels/verifiers carried by idea method scene |
| outro | HUMAN : AI — THE WORK SPLIT (5w, 2.5s) | HUMAN : AI SPLIT (3w, 5.0s) |  |
| outro | PROJECT BILLED   1,196,128,770 tokens (4w, 2.5s) | PROJECT 1,196,128,770 tokens (3w, 5.0s) | 'Billed' kept in the tag line |
| outro | OWNER TYPED   ~1,928 tokens (est.) (5w, 2.5s) | OWNER ~1,928 typed (est.) (4w, 4.5s) |  |
| outro | 1 px is too wide — shown 3 px (8w, 2.5s) | true bar <1 px wide (5w, 4.5s) | tick drawn 4 px at 1440p; proportional width is ~0.0015 px |
| outro | Owner: chars/4 ±30% over 40 typed prompts (tokens study, 2026-10-28). Project: API-billed input+output from docs/metrics/usage.jsonl @ a73e97d (93 rows, waves 0–5); cached is inside input, not added. (26w, 2.5s) | Billed vs typed tokens (est.) (5w, 4.0s) | definitions block -> one tag; full definitions quoted in Facts section below |
| outro | instantiations · b16/b32/b64 (2w, 2.0s) | versions across 3 sizes (4w, 3.5s) |  |
| outro | vectors in the merge gate (5w, 1.5s) | checks before merging (3w, 3.0s) | vectors/gate = checks before merging |
| outro | IAS15 · 2,001/2,001 state hashes (4w, 1.0s) | IAS15 · 2,001/2,001 checks (3w, 2.5s) |  |


## Dwell audit - every new block (0 violations)

| seg/scene | t0 | lines | words | dwell | rule min | ok |
|---|---|---|---|---|---|---|
| intro/intro | 1.5 | Hey Muse, I've got an idea... | 6 | 3.0 | 3.0 | ok |
| idea/idea | 0.5 | THE IDEA / for the RP2040 chip | 6 | 4.0 | 3.0 | ok |
| idea/idea | 1.0 | Precise number maths in software (IEEE 754) | 7 | 3.5 | 3.5 | ok |
| idea/idea | 1.5 | for a chip without maths hardware | 6 | 3.0 | 3.0 | ok |
| idea/idea | 2.0 | All maths there is software. | 5 | 2.5 | 2.5 | ok |
| idea/idea | 2.5 | Same answer everywhere. | 3 | 2.0 | 2.0 | ok |
| idea/correct | 4.5 | WHAT “CORRECT” MEANS / the nearest answer, every time | 8 | 5.0 | 4.0 | ok |
| idea/correct | 5.0 | value A / the next number the chip can hold | 9 | 4.5 | 4.5 | ok |
| idea/correct | 6.0 | exact answer / (no rounding yet) | 5 | 3.5 | 2.5 | ok |
| idea/correct | 6.5 | correctly rounded → A | 3 | 3.0 | 2.0 | ok |
| idea/correct | 7.0 | A neighbour is wrong. / (illustrative) | 5 | 2.5 | 2.5 | ok |
| idea/correct | 7.5 | Exact, not close. | 3 | 2.0 | 2.0 | ok |
| idea/prove | 9.5 | WHAT WILL PROVE IT / three real jobs on the chip | 10 | 5.0 | 4.5 | ok |
| idea/prove | 10.0 | IAS15 / tracks planets | 3 | 4.5 | 2.0 | ok |
| idea/prove | 10.5 | Desktop bits, every step / (binary64) | 5 | 4.0 | 2.5 | ok |
| idea/prove | 11.0 | INTERVAL GEOMETRY / answers with guarantees | 5 | 3.5 | 2.5 | ok |
| idea/prove | 11.5 | Down one end, / up the other | 6 | 3.0 | 3.0 | ok |
| idea/prove | 12.0 | KISSFFT — FORK B / live signals | 5 | 2.5 | 2.5 | ok |
| idea/prove | 12.5 | Correctly rounded / sinPi/cosPi | 3 | 2.0 | 2.0 | ok |
| idea/method | 14.5 | HOW IT GETS BUILT / the short version | 7 | 4.0 | 3.5 | ok |
| idea/method | 15.0 | 1 / Agents build it piece by piece | 7 | 3.5 | 3.5 | ok |
| idea/method | 15.5 | 2 / Each piece checked independently | 5 | 3.0 | 2.5 | ok |
| idea/method | 16.0 | 3 / Verifiers try disproving it | 5 | 2.5 | 2.5 | ok |
| idea/method | 16.5 | Watch it land. | 3 | 2.0 | 2.0 | ok |
| idea/question | 18.5 | BUT FIRST — / WHY NOT USE WHAT | 6 | 3.0 | 3.0 | ok |
| idea/question | 19.0 | ALREADY SHIPS? | 2 | 2.5 | 1.5 | ok |
| why/title | 0.5 | WHY NOT USE WHAT / ALREADY SHIPS? | 6 | 3.0 | 3.0 | ok |
| why/title | 1.0 | RP2040: no maths hardware (FPU) | 5 | 2.5 | 2.5 | ok |
| why/workloads | 3.5 | FIRST: THE WORKLOADS / what must run on the chip | 9 | 4.5 | 4.5 | ok |
| why/workloads | 4.0 | IAS15 / Desktop bits (binary64) | 4 | 4.0 | 2.5 | ok |
| why/workloads | 4.5 | INTERVAL GEOMETRY / Down / up per end | 6 | 3.5 | 3.0 | ok |
| why/workloads | 5.0 | KISSFFT — FORK B / Correctly rounded sinPi/cosPi | 6 | 3.0 | 3.0 | ok |
| why/spec | 8.0 | TOGETHER: A JOB SPEC / what the three jobs need (IEEE 754-2019) | 11 | 5.5 | 5.0 | ok |
| why/spec | 8.5 | All five rounding choices | 4 | 5.0 | 2.5 | ok |
| why/spec | 9.0 | Five warning flags, always exact | 5 | 4.5 | 2.5 | ok |
| why/spec | 9.5 | Tiny numbers never zeroed (subnormals) | 5 | 4.0 | 2.5 | ok |
| why/spec | 10.0 | Error values keep their details | 5 | 3.5 | 2.5 | ok |
| why/spec | 10.5 | Three number sizes (binary16/32/64) | 4 | 3.0 | 2.5 | ok |
| why/spec | 11.0 | Correctly rounded, even hard cases | 5 | 2.5 | 2.5 | ok |
| why/spec | 11.5 | Exact leftovers (augmented) | 3 | 2.0 | 2.0 | ok |
| why/opt1 | 13.5 | OPTION 1 — THE DEFAULT / SDK ‘pico’ flavour → bootrom | 8 | 5.0 | 4.0 | ok |
| why/opt1 | 14.0 | Five basic sums correctly rounded | 5 | 4.5 | 2.5 | ok |
| why/opt1 | 14.5 | Tiny results silently become zero | 5 | 4.0 | 2.5 | ok |
| why/opt1 | 15.0 | Error values turn into infinity | 5 | 3.5 | 2.5 | ok |
| why/opt1 | 15.5 | One rounding choice only (ties-to-even) | 5 | 3.0 | 2.5 | ok |
| why/opt1 | 16.0 | No warning flags exist | 4 | 2.5 | 2.5 | ok |
| why/opt1 | 16.5 | (SF-0 §8) | 2 | 2.0 | 1.5 | ok |
| why/opt1 | 17.0 | ELIMINATED | 1 | 1.5 | 1.5 | ok |
| why/opt2 | 18.5 | OPTION 2 — THE FALL-THROUGH / SDK ‘compiler’ flavour → libgcc | 8 | 5.5 | 4.0 | ok |
| why/opt2 | 19.0 | Rounding directions? Not measured | 4 | 5.0 | 2.5 | ok |
| why/opt2 | 19.5 | Warning flags? Not measured | 4 | 4.5 | 2.5 | ok |
| why/opt2 | 20.0 | Errors, tiny numbers, small size? Unmeasured | 6 | 4.0 | 3.0 | ok |
| why/opt2 | 20.5 | Same code, different bits per target | 6 | 3.5 | 3.0 | ok |
| why/opt2 | 21.0 | e.g. a×b+c differs by target. | 5 | 3.0 | 2.5 | ok |
| why/opt2 | 21.5 | Unmeasured proves nothing (SF-0) | 4 | 2.5 | 2.5 | ok |
| why/opt2 | 22.5 | NOT MEASURED | 2 | 1.5 | 1.5 | ok |
| why/opt3 | 24.0 | OPTION 3 / SDK ‘none’ flavour | 5 | 4.0 | 2.5 | ok |
| why/opt3 | 24.5 | panic("float support is disabled") | 4 | 3.5 | 2.5 | ok |
| why/opt3 | 25.0 | Every number call stops here | 5 | 3.0 | 2.5 | ok |
| why/opt3 | 25.5 | NO FLOATS AT ALL | 4 | 2.5 | 2.5 | ok |
| why/settle | 28.0 | SO BUILD THE FOURTH OPTION / MUSE-SOFTFLOAT | 6 | 4.5 | 3.0 | ok |
| why/settle | 28.5 | Three sizes · 849 versions (IEEE 754-2019) | 6 | 4.0 | 3.0 | ok |
| why/settle | 29.0 | Five roundings, five exact warnings | 5 | 3.5 | 2.5 | ok |
| why/settle | 29.5 | Tiny kept · leftovers exact · correctly rounded | 6 | 3.0 | 3.0 | ok |
| why/settle | 30.0 | Proven bit-identical on the chip | 5 | 2.5 | 2.5 | ok |
| outro/outro | 2.5 | Done — it held up. | 4 | 6.0 | 2.5 | ok |
| outro/outro | 4.0 | Identical on all 6 boards. | 5 | 4.5 | 2.5 | ok |
| outro/outro | 3.5 | HUMAN : AI SPLIT / PROJECT 1,196,128,770 tokens | 6 | 5.0 | 3.0 | ok |
| outro/outro | 4.0 | OWNER ~1,928 typed (est.) / true bar <1 px wide | 9 | 4.5 | 4.5 | ok |
| outro/outro | 4.5 | ≈ 1 : 620,000 / Billed vs typed tokens (est.) | 7 | 4.0 | 3.5 | ok |
| outro/outro | 5.0 | 849 / 849 / versions across 3 sizes | 6 | 3.5 | 3.0 | ok |
| outro/outro | 5.5 | 411,213 / checks before merging | 4 | 3.0 | 2.5 | ok |
| outro/outro | 6.0 | 6 boards / IAS15 · 2,001/2,001 checks | 5 | 2.5 | 2.5 | ok |

Full lines text for truncated rows is in audit3.json. Old-copy dwell audit (for the before picture) is also in audit3.json (old_blocks): most old blocks sat far below the new rule - e.g. idea card lines dwelt 0.5-2.5 s against 2.5-4.0 s minima, outro reply-2 1.0 s against 5.5 s.

## Facts discipline (nothing moved)

- Same claim pools: idea claims per scratch/study-video-idea/report.md claim table (README/SF-0/SF-1/SF-2 at a73e97d); why claims per options-facts.md SF-0 pool (unchanged file; not-measured stays not-measured, dropped claims stay dropped); intro/outro numbers per polish-report.md a73e97d provenance. No new number, no new claim, no performance framing. Plain rewordings only, per the brief's register; technical terms kept once in parentheses where they name the thing (IEEE 754, FPU, subnormals, ties-to-even, binary16/32/64, augmented, sinPi/cosPi).
- Numbers on screen, all carried over: 849/849 and 849, 411,213, 6 boards, 2,001/2,001, 1,196,128,770, ~1,928 (est.), 1 : 620,000, binary64, five roundings/flags (spec counts).
- Token definitions removed from the frame (now the tag 'Billed vs typed tokens (est.)') are preserved here verbatim: "Owner: chars/4 +/-30% over 40 typed prompts (tokens study, 2026-10-28). Project: API-billed input+output from docs/metrics/usage.jsonl @ a73e97d (93 rows, waves 0-5); cached is inside input, not added." The owner tick is drawn 4 px wide at 1440p; proportional width is ~0.0015 px, hence 'true bar <1 px wide'.
- The bootrom 'five basic sums correctly rounded' line loses its on-screen asterisk; the flush-rules caveat is stated by the next two rows on the same card and in full in options-facts.md (SF-0 section 8).
- 'Versions' replaces 'instantiations' (849) in settle + stat card: same count, plainer noun.

## Stills eyeballed by the author

- Pre-encode frames (frameprobe/): idea2 all 5 scenes, why3 title/workloads/spec/opt1/opt2/opt3/settle, intro plate, outro final composite - no overflow, no collisions (one-line 'next number' label fits; INTERVAL GEOMETRY card titles fit their cards).
- MP4 grabs: stills3/intro (enter, typing, hold, mid-dive at proof crop, white), stills3/outro (near-black, dots pull-back, reply, mid-panel-staging, final), stills-idea2 (7), why/stills3 (9), plus still3_period_proof/midzoom/bubble.
- Two defects caught at probe stage and fixed before render: a 3-new-lines beat in why workloads cards (split into name+one-line recap), and an 8-word why interval block that broke its dwell (needs shortened to 'Down / up per end').

## Assembly notes / still open

- Order and joins unchanged: intro3 (white out) -> idea2 -> why3 -> git -> outro3 (near-black in); all four now native 2560x1440 so the intro/outro 1080p mismatch flagged since v2 is gone. Front total 71.5 s (was 57.5 s).
- Owner sign-off still needed on: plainer copy overall, the lineup-scene cut, 'versions', outro bubble trim, left-panel tag replacing the definitions block.
- Silent as before; reveals sit on the 0.5 s (120 BPM) grid for music. At-speed watch-through by a human is still the real pacing test - dwells here are analytic (rule audit) + still-based, as in v2.
- Gates: dwell audit violations=PASS; headline failures=PASS; intro3.mp4 probe=PASS; intro3.mp4 white_6.8s=PASS; outro3.mp4 probe=PASS; idea2-1440p.mp4 probe=PASS; idea2-1440p.mp4 white_0.2s=PASS; idea2-1440p.mp4 white_22.3s=PASS; why3-1440p.mp4 probe=PASS; why3-1440p.mp4 white_0.2s=PASS; why3-1440p.mp4 white_33.3s=PASS; outro first frame (2,3,8)=PASS; priors unchanged=PASS; film <=160 with gitvisual4=PASS.
