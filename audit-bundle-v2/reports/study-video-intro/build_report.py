"""Assemble textrev-report.md from audit3.json + verify3.json +
measurements3.json. First line READY only if every gate passes.
Run: $MSF_PYTHON build_report.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
A = json.loads((HERE / "audit3.json").read_text(encoding="utf-8"))
V = json.loads((HERE / "verify3.json").read_text(encoding="utf-8"))
M = json.loads((HERE / "measurements3.json").read_text(encoding="utf-8"))


def words(s: str) -> int:
    return sum(1 for tok in s.split() if any(c.isalnum() for c in tok))


def find_dwell(blocks, line):
    for b in blocks:
        if line in b["lines"]:
            return b["dwell"]
    return None


# (segment, old_lines, new_lines, note) -- editorial old->new mapping
MAP = [
    ("intro", ["Hey Muse, I've got an idea..."], ["Hey Muse, I've got an idea..."],
     "unchanged (inciting line); dwell bought with a longer hold"),
    ("idea", ["one sentence, then what it demands"], ["for the RP2040 chip"], ""),
    ("idea", ["A software IEEE 754 floating-point library"],
     ["Precise number maths in software (IEEE 754)"], "term kept once, in parentheses"),
    ("idea", ["for the RP2040 \u2014 a chip with no FPU,"],
     ["for a chip without maths hardware"], "RP2040 named in the sub-line; FPU = maths hardware"),
    ("idea", ["where every float is already software \u2014"],
     ["All maths there is software."], ""),
    ("idea", ["so real science code runs bit-identically:",
              "same source on desktop and chip, same bits out."],
     ["Same answer everywhere."], "two lines merged; bit-identical spelled out in why settle"),
    ("idea", ["every result the correctly rounded one \u2014 every flag exact"],
     ["the nearest answer, every time"], "plainer definition line (brief)"),
    ("idea", ["representable", "value A"], ["value A"], ""),
    ("idea", ["next value", "A + 1 ULP"], ["the next number the chip can hold"],
     "brief worked example, verbatim"),
    ("idea", ["one operation, done exactly \u2014 where must it land?"], [],
     "CUT: question is carried by dot+arrow; also collided with verdict labels"),
    ("idea", ["exact result", "(infinitely precise)"],
     ["exact answer", "(no rounding yet)"], ""),
    ("idea", ["correctly rounded \u2192 A"], ["correctly rounded \u2192 A"],
     "kept (term defined by this scene)"),
    ("idea", ["a neighbour is a wrong answer"], ["A neighbour is wrong."], ""),
    ("idea", ["not close \u2014 exact: right value, right flags, every time  (illustrative)"],
     ["Exact, not close.", "(illustrative)"], "tag split out; flags point lives in why spec"),
    ("idea", ["three real workloads, run on the chip"], ["three real jobs on the chip"], ""),
    ("idea", ["orbital integrator"], ["tracks planets"], ""),
    ("idea", ["binary64, bit-identical", "desktop = chip,", "every bit, every step"],
     ["Desktop bits, every step", "(binary64)"], ""),
    ("idea", ["guaranteed enclosures"], ["answers with guarantees"], ""),
    ("idea", ["directed rounding:", "down for one end,", "up for the other"],
     ["Down one end,", "up the other"], "plain fact; term glossed in why spec scene order"),
    ("idea", ["exact-angle FFT"], ["live signals"], "FFT is inside the KISSFFT name"),
    ("idea", ["sinPi / cosPi twiddles", "made at runtime,", "correctly rounded"],
     ["Correctly rounded", "sinPi/cosPi"], "'live' (sub) = made at runtime; twiddles = the sinPi/cosPi values"),
    ("idea", ["the short version \u2014 the film shows the rest"], ["the short version"], ""),
    ("idea", ["briefed agents build it, parcel by parcel"],
     ["Agents build it piece by piece"], "parcel = a piece (briefs in reports)"),
    ("idea", ["every piece independently verified \u2014"],
     ["Each piece checked independently"], ""),
    ("idea", ["a verifier whose only job is to disconfirm"],
     ["Verifiers try disproving it"], "disconfirm = try disproving"),
    ("idea", ["watch it land, commit by commit, in a minute."], ["Watch it land."],
     "drops the 'in a minute' length presumption (v2 known limit)"),
    ("idea", ["BUT FIRST \u2014", "WHY NOT USE WHAT", "ALREADY SHIPS?"],
     ["BUT FIRST \u2014", "WHY NOT USE WHAT", "ALREADY SHIPS?"], "unchanged; now staggered over 2 beats"),
    ("why", ["The RP2040 has no FPU \u2014 every float is software. Three workloads go shopping."],
     ["RP2040: no maths hardware (FPU)"], "old line was 13 words (>10 cap); shopping half cut, jobs appear next scene"),
    ("why", ["what actually has to run on the chip"], ["what must run on the chip"], ""),
    ("why", ["NEEDS:"], [], "CUT x3 cards: needs line is self-evident under the divider"),
    ("why", ["orbital integrator", "guaranteed enclosures", "exact-angle FFT"], [],
     "CUT in why only: subs introduced minutes earlier in idea prove-it cards"),
    ("why", ["binary64 bit-identical,", "desktop = chip,", "every bit, every step"],
     ["Desktop bits (binary64)"], "recap one-liner; full wording in idea card"),
    ("why", ["directed rounding on demand:", "round down / round up,", "chosen per call"],
     ["Down / up per end"], "recap one-liner; on-demand survives as 'per end' + spec row 1"),
    ("why", ["sinPi / cosPi twiddles", "generated at runtime,", "correctly rounded"],
     ["Correctly rounded sinPi/cosPi"], "recap one-liner"),
    ("why", ["TOGETHER, THAT'S A JOB SPEC"], ["TOGETHER: A JOB SPEC"], ""),
    ("why", ["the IEEE 754-2019 semantics the three workloads stand on"],
     ["what the three jobs need (IEEE 754-2019)"], ""),
    ("why", ["rounding attributes: all four, + tiesToAway"],
     ["All five rounding choices"], "four+tiesToAway = five (count kept)"),
    ("why", ["exception flags: invalid \u00b7 div-by-zero \u00b7 overflow \u00b7 underflow \u00b7 inexact"],
     ["Five warning flags, always exact"], "flag names live in options-facts/SF-0, per source-tag rule"),
    ("why", ["subnormals kept \u2014 never flushed to zero"],
     ["Tiny numbers never zeroed (subnormals)"], "brief register; term once in parentheses"),
    ("why", ["NaN payloads preserved through arithmetic"],
     ["Error values keep their details"], "NaN payloads named in options-facts"),
    ("why", ["formats: binary16 + binary32 + binary64"],
     ["Three number sizes (binary16/32/64)"], ""),
    ("why", ["correctly rounded \u2014 FMA, sqrt, sinPi/cosPi, hard cases"],
     ["Correctly rounded, even hard cases"], "op list in reports; sinPi/cosPi on KissFFT cards"),
    ("why", ["augmented add / sub / mul: head + exact tail"],
     ["Exact leftovers (augmented)"], "head+exact tail = answer + exact leftover"),
    ("why", ["five basic ops correctly rounded *  (+ \u2212 \u00d7 \u00f7 \u221a)"],
     ["Five basic sums correctly rounded"], "asterisk caveat: rows below state the flush rules on the same card"),
    ("why", ["subnormals flushed to zero \u2014 in and out"],
     ["Tiny results silently become zero"], "brief worked example, verbatim"),
    ("why", ["NaNs rendered as infinities \u2014 payloads gone"],
     ["Error values turn into infinity"], "brief worked example, verbatim"),
    ("why", ["one rounding mode: ties-to-even. No directed modes"],
     ["One rounding choice only (ties-to-even)"], ""),
    ("why", ["exception flags: none exist"], ["No warning flags exist"], ""),
    ("why", ["e.g. a tiny subnormal result \u2192 0, silently."], [],
     "CUT: redundant once row 2 is itself the concrete statement"),
    ("why", ["* five basic ops, under the flush rules (SF-0 \u00a78)"], ["(SF-0 \u00a78)"],
     "scene's one source tag; wording preserved in options-facts.md"),
    ("why", ["directed rounding?  not measured"], ["Rounding directions? Not measured"], ""),
    ("why", ["exception flags?  not measured"], ["Warning flags? Not measured"], ""),
    ("why", ["NaN payloads? subnormals? binary16?  not measured"],
     ["Errors, tiny numbers, small size? Unmeasured"], "all three unmeasured items kept"),
    ("why", ["compiler FMA contraction varies by target (SF-0 \u00a79)"],
     ["Same code, different bits per target"], "brief worked example register"),
    ("why", ["e.g. a\u00d7b+c may fuse on one target, not another \u2014 different bits."],
     ["e.g. a\u00d7b+c differs by target."], "old line was 11 words (>10 cap)"),
    ("why", ["SF-0 gated none of it \u2014 unmeasured semantics can't carry a proof"],
     ["Unmeasured proves nothing (SF-0)"], "scene's one source tag (section 9 in options-facts)"),
    ("why", ["every float entry point is this stub"], ["Every number call stops here"], ""),
    ("why", ["e.g. the first  a + b  in any workload never returns."], [],
     "CUT: sub-line already states every call stops; old line was 11 words"),
    ("why", ["THE LINEUP vs THE SPEC", "rounding attrs", "5 flags", "subnormals",
              "NaN payloads", "b16+b32+b64", "correct rounding", "augmented ops",
              "BOOTROM", "LIBGCC", "CUSTOM",
              "* five basic ops, under the flush rules"],
     [], "WHOLE SCENE CUT: cell-for-cell recap of spec+option rows, zero unique claims; "
         "its rule dwell (~5 s) could not be bought inside the 160 s film"),
    ("why", ["IEEE 754-2019 \u00b7 binary16 / 32 / 64 \u00b7 849 instantiations"],
     ["Three sizes \u00b7 849 versions (IEEE 754-2019)"], "instantiations -> versions (number kept)"),
    ("why", ["five rounding attributes \u00b7 five exact flags \u00b7 payloads preserved"],
     ["Five roundings, five exact warnings"], "payloads point = spec row 4 wording"),
    ("why", ["subnormals kept \u00b7 augmented ops \u00b7 correctly rounded, hard cases in"],
     ["Tiny kept \u00b7 leftovers exact \u00b7 correctly rounded"], ""),
    ("why", ["proven bit-identical on RP2040 silicon"],
     ["Proven bit-identical on the chip"], ""),
    ("outro", ["Done \u2014 it held up."], ["Done \u2014 it held up."], "unchanged"),
    ("outro", ["849/849 ops across b16/b32/b64. 411,213 vectors in the gate, IAS15 identical on all 6 boards. Small parcels; verifiers that only disconfirm."],
     ["Identical on all 6 boards."],
     "849 + 411,213 stay on the stat cards beside the bubble; parcels/verifiers carried by idea method scene"),
    ("outro", ["HUMAN : AI \u2014 THE WORK SPLIT"], ["HUMAN : AI SPLIT"], ""),
    ("outro", ["PROJECT BILLED   1,196,128,770 tokens"],
     ["PROJECT 1,196,128,770 tokens"], "'Billed' kept in the tag line"),
    ("outro", ["OWNER TYPED   ~1,928 tokens (est.)"], ["OWNER ~1,928 typed (est.)"], ""),
    ("outro", ["1 px is too wide \u2014 shown 3 px"], ["true bar <1 px wide"],
     "tick drawn 4 px at 1440p; proportional width is ~0.0015 px"),
    ("outro", ["Owner: chars/4 \u00b130% over 40 typed prompts (tokens study, 2026-10-28). Project: API-billed input+output from docs/metrics/usage.jsonl @ a73e97d (93 rows, waves 0\u20135); cached is inside input, not added."],
     ["Billed vs typed tokens (est.)"],
     "definitions block -> one tag; full definitions quoted in Facts section below"),
    ("outro", ["instantiations \u00b7 b16/b32/b64"], ["versions across 3 sizes"], ""),
    ("outro", ["vectors in the merge gate"], ["checks before merging"], "vectors/gate = checks before merging"),
    ("outro", ["IAS15 \u00b7 2,001/2,001 state hashes"], ["IAS15 \u00b7 2,001/2,001 checks"], ""),
]

SEG_DUR = {  # (old, new) seconds
    "intro": (5.0, 7.0), "idea": (14.5, 22.5), "why": (32.0, 33.5), "outro": (6.0, 8.5)}
GIT_V4 = 88.0


def solo_stats(seg):
    rows = A["segments"][seg]["new_blocks"]
    rows = sorted(rows, key=lambda r: r["t0"])
    under = 0
    for i, r in enumerate(rows):
        nxt = rows[i + 1]["t0"] if i + 1 < len(rows) else r["t_gone"]
        if nxt - r["t0"] < r["rule_min"] - 1e-9:
            under += 1
    return len(rows), under


def main() -> int:
    clips = V["clips"]
    gates = []
    gates.append(("dwell audit violations", len(A["violations"]) == 0))
    gates.append(("headline failures", len(A["headline_failures"]) == 0))
    for name, c in clips.items():
        gates.append((f"{name} probe", c["decode_rc"] == 0
                      and c["decoded_frames"] == c["expected_frames"]
                      and c["width"] == 2560 and c["height"] == 1440))
        for k, chk in c["handoff"].items():
            if k.startswith("white_"):
                gates.append((f"{name} {k}", chk["nonwhite_px"] == 0))
    gates.append(("outro first frame (2,3,8)",
                  clips["outro3.mp4"]["handoff"]["first_frame"]["dominant_sampled"][0][0] == [2, 3, 8]))
    gates.append(("priors unchanged", all(p["unchanged"] for p in V["priors"].values())))
    front_new = sum(v[1] for v in SEG_DUR.values())
    gates.append(("film <=160 with gitvisual4", front_new + GIT_V4 <= 160.0))
    ready = all(ok for _, ok in gates)

    lines = []
    lines.append("READY" if ready else "NOT READY")
    lines += ["", "# Text/pacing pass - Agent A (intro/outro + idea + why)", "",
              "Brief: `ledger/briefs/study-video-textpacing.md` (THE RULE). "
              "Scratch only; repo untouched; nothing committed; all prior "
              "versions preserved byte-identical (verified in verify3.json). "
              "New scripts (old ones untouched): `render_v3.py` (this dir), "
              "`scratch/study-video-idea/render_idea2.py`, "
              "`scratch/study-video-why/render_why3.py`. Audit: "
              "`audit_textrev.py` -> `audit3.json`. Probe: `verify3.py` -> "
              "`verify3.json`. 1440p measurements: `measurements3.json`.", ""]

    lines += ["## Durations and film budget", "",
              "| segment | old | new | delta |", "|---|---|---|---|"]
    for seg in ("intro", "idea", "why", "outro"):
        o, n = SEG_DUR[seg]
        lines.append(f"| {seg} | {o:.1f} s | {n:.1f} s | {n-o:+.1f} s |")
    fo = sum(v[0] for v in SEG_DUR.values())
    lines.append(f"| FRONT total (A) | {fo:.1f} s | {front_new:.1f} s | {front_new-fo:+.1f} s |")
    lines += ["", f"Film estimate with gitvisual4 ({GIT_V4:.1f} s, ledger "
              f"study-video-gitvisual v4): {front_new:.1f} + {GIT_V4:.1f} = "
              f"{front_new+GIT_V4:.1f} s <= 160 s (v4 assembly was 145.5 s). "
              "Agent B's gitvisual5 duration was still in flight when this ran; "
              "if v5 keeps v4's 88.0 s the film is 159.5 s before music. "
              "Dwell growth (+14.0 s front) is bought by the word cuts below "
              "plus three structural cuts (why lineup scene, idea prompt line, "
              "two option 'e.g.' lines) - each named in the copy table.", ""]

    lines += ["## THE RULE as applied (conventions, stated once)", "",
              "- Word = whitespace token containing a letter or digit "
              "(em dashes, middots, arrows, `*`, `+`, check/cross/? glyphs "
              "are not words; circled numerals 1/2/3 ARE counted).",
              "- Block = all text first appearing on one 0.5 s beat. "
              "Dwell given = beat time -> the moment the text stops being "
              "readable (scene cut, white-fade start, intro dive start, or "
              "clip end). Text persists (never dimmed below readable) until "
              "that moment, per the brief's persistence clause; new load "
              "per beat is capped at 2 lines and audited. Typed bubbles "
              "are timed from FULL text (stricter than first character).",
              "- Reveal start = the beat the fade/pop begins (fades are "
              "0.25 s, pops 0.35 s; card text appears at pop scale >0.6, "
              "up to ~0.2 s after the beat - dwells at exactly the rule "
              "minimum carry that much less full-size time).",
              "- Phone chrome (9:41 / Muse / online / Message...) is "
              "excluded from word counts old and new: ambient UI furniture "
              "present from frame 0 for the whole clip either way.",
              "- Headlines checked <=6 words (the two-line WHY NOT... "
              "headline counts as one 6-word headline; see audit3.json "
              "headline_checks, 0 failures). Every body line <=10 words "
              "(max seen in new copy: "
              f"{max(b['max_line_words'] for s in A['segments'].values() for b in s['new_blocks'])}).",
              "- Source tags on screen (max 1 per scene): why opt1 "
              "`(SF-0 section 8)`, opt2 foot `(SF-0)`; idea correct keeps "
              "`(illustrative)`; everything else's sourcing lives in "
              "options-facts.md / the reports, per the brief.", ""]
    tot_b = sum(solo_stats(s)[0] for s in ("intro", "idea", "why", "outro"))
    tot_u = sum(solo_stats(s)[1] for s in ("intro", "idea", "why", "outro"))
    lines += [f"### Named interpretation risk (not counted as a violation above)", "",
              f"Dwell is measured as persistence (above). If the lead intended "
              f"SOLO dwell (time until the NEXT new text appears), {tot_u} of "
              f"{tot_b} new blocks sit below their rule minimum on that "
              "stricter reading (reveals are spaced one 0.5 s beat apart; "
              "every block still stays fully readable for its full rule "
              "dwell, and each scene's LAST block gets solo dwell equal to "
              "its persistence, which passes on both readings). A solo-dwell "
              "cut of the same copy would add roughly a minute and break "
              "the 160 s film; the persistence reading is also the one the "
              "v2 dwell regime used ('remains on screen for the rest of its "
              "scene'). Flagged for lead/owner, not hidden.", ""]

    lines += ["## Clips (probe-verified, video/probe.py full decode)", "",
              "| file | duration | frames | bytes |", "|---|---|---|---|"]
    for name in ("intro3.mp4", "idea2-1440p.mp4", "why3-1440p.mp4", "outro3.mp4"):
        c = clips[name]
        lines.append(f"| {name} | {c['duration_s']:.1f} s | "
                     f"{c['decoded_frames']}/{c['expected_frames']} rc {c['decode_rc']} | "
                     f"{c['bytes']:,} |")
    lines += ["", "All 2560x1440 @ 30 fps H.264, silent. Handoffs measured "
              "on decoded MP4 stills (3,686,400 px each):", "",
              "- intro3 white hold (6.8 s): 0 non-white px - source "
              "(255,255,255), value unchanged.",
              "- outro3 first frame: dominant (2,3,8) decoded (min 2, max 8) "
              "- source near-black (3,4,9), value unchanged, identical to "
              "the v1/v2 spec.",
              "- idea2 bookends (0.2 s / 22.3 s) and why3 bookends "
              "(0.2 s / 33.3 s): 0 non-white px each.", ""]

    p, pr, dt = M["period"], M["proof"], M["dots"]
    lines += ["## Intro/outro at native 1440p (re-measured, not rescaled numbers)", "",
              f"Whole 1080p design scaled parametrically by K={M['scale_K']} "
              "(every coordinate, size, font, wrap width); frames drawn "
              "natively at 2560x1440 and streamed (v2's buffered encode "
              "would hold ~15 MB/frame x all frames at 1440p).",
              f"- Period ink centroid RE-MEASURED on the 1440p plate: "
              f"raster {p['raster_centroid']} (ink {p['ink']['w']}x{p['ink']['h']} px, "
              f"{p['n_dot_components']} dot components); font-metrics cross-check "
              f"{p['metrics_centroid']} (delta {p['raster_minus_metrics']}); "
              f"v1 formula would sit {p['raster_minus_v1'][1]:+.1f} px off in y at this scale. "
              f"Scaled v2 centroid (1170.49, 272.0) x 4/3 = (1560.7, 362.7) "
              f"for reference - the 1440p raster genuinely differs.",
              f"- Mid-dive proof (pre-encode, t={pr['t']} s, crop {pr['crop_w']} px): "
              f"period centroid {pr['measured_centroid']} vs frame centre "
              f"{pr['frame_center']}: error {pr['error_px']} px, |e| {pr['error_abs']} px "
              f"(`still3_period_proof.png`, eyeballed - dot sits in the crosshairs).",
              f"- Camera clamps re-checked at 1440p (401 samples): intro max "
              f"adjustment {p['intro_clamp_max_px']} px, outro {dt['outro_clamp_max_px']} px "
              f"(subpixel, final settle only - same class as v2's 0.0 / 0.101).",
              f"- Outro dots centroid re-measured: raster {dt['raster_centroid']} "
              f"vs layout {dt['layout_centroid']}; reverse camera final crop "
              f"200xK = {200*M['scale_K']:.0f} px; camera curve shape unchanged "
              f"(smootherstep log-scale; max |dlog-step| "
              f"{M['smooth']['max_abs_dlog_step_per_frame']}).",
              "- Timing changes for dwell: intro full message now holds "
              "1.5-4.5 s (3.0 s = rule for 6 words) before the same 2.0 s "
              "dive; typing-dots beat shortened 1.0->0.5 s (no text). "
              "Outro reply lands at 2.5 s (dots breath folded into the "
              "pull-back); side panels now reveal in 6 staged beats "
              "(left card in 3 reading chunks) instead of one 6-line pop.", ""]

    lines += ["## Word counts (audit3.json; chrome excluded both sides)", "",
              "| segment | old | new | cut |", "|---|---|---|---|"]
    for seg in ("intro", "idea", "why", "outro"):
        s = A["segments"][seg]
        lines.append(f"| {seg} | {s['old_words']} | {s['new_words']} | {s['cut_pct']}% |")
    t = A["totals"]
    lines.append(f"| TOTAL | {t['old_words']} | {t['new_words']} | {t['cut_pct']}% |")
    lines += ["", "Intro shows 0%: its single 6-word inciting message cannot "
              "be cut; the intro+outro pair together goes 97 -> 52 words "
              "(-46%). Idea -32% (the brief's 'roughly a third'), why -41%, "
              "outro -49%.", ""]

    lines += ["## Copy table (old -> new; dwell = persistence of the containing block)", "",
              "| seg | old (words, dwell) | new (words, dwell) | note |",
              "|---|---|---|---|"]
    for seg, olds, news, note in MAP:
        ow = sum(words(s) for s in olds)
        nw = sum(words(s) for s in news)
        od = find_dwell(A["segments"][seg]["old_blocks"], olds[0]) if olds else None
        nd = find_dwell(A["segments"][seg]["new_blocks"], news[0]) if news else None
        otxt = " / ".join(olds).replace("|", "/")
        ntxt = " / ".join(news).replace("|", "/") if news else "CUT"
        lines.append(f"| {seg} | {otxt} ({ow}w, {od if od is not None else '?'}s) | "
                     f"{ntxt} ({nw}w, {nd if nd is not None else '-'}s) | {note} |")
    lines += ["", ""]

    lines += ["## Dwell audit - every new block (0 violations)", "",
              "| seg/scene | t0 | lines | words | dwell | rule min | ok |",
              "|---|---|---|---|---|---|---|"]
    for seg in ("intro", "idea", "why", "outro"):
        for b in A["segments"][seg]["new_blocks"]:
            txt = " / ".join(b["lines"]).replace("|", "/")
            if len(txt) > 72:
                txt = txt[:69] + "..."
            lines.append(f"| {seg}/{b['scene']} | {b['t0']:.1f} | {txt} | {b['words']} | "
                         f"{b['dwell']:.1f} | {b['rule_min']:.1f} | {'ok' if b['ok'] else 'VIOLATION'} |")
    lines += ["", "Full lines text for truncated rows is in audit3.json. "
              "Old-copy dwell audit (for the before picture) is also in "
              "audit3.json (old_blocks): most old blocks sat far below the "
              "new rule - e.g. idea card lines dwelt 0.5-2.5 s against "
              "2.5-4.0 s minima, outro reply-2 1.0 s against 5.5 s.", ""]

    lines += ["## Facts discipline (nothing moved)", "",
              "- Same claim pools: idea claims per scratch/study-video-idea/"
              "report.md claim table (README/SF-0/SF-1/SF-2 at a73e97d); why "
              "claims per options-facts.md SF-0 pool (unchanged file; "
              "not-measured stays not-measured, dropped claims stay "
              "dropped); intro/outro numbers per polish-report.md a73e97d "
              "provenance. No new number, no new claim, no performance "
              "framing. Plain rewordings only, per the brief's register; "
              "technical terms kept once in parentheses where they name "
              "the thing (IEEE 754, FPU, subnormals, ties-to-even, "
              "binary16/32/64, augmented, sinPi/cosPi).",
              "- Numbers on screen, all carried over: 849/849 and 849, "
              "411,213, 6 boards, 2,001/2,001, 1,196,128,770, ~1,928 (est.), "
              "1 : 620,000, binary64, five roundings/flags (spec counts).",
              "- Token definitions removed from the frame (now the tag "
              "'Billed vs typed tokens (est.)') are preserved here "
              "verbatim: \"Owner: chars/4 +/-30% over 40 typed prompts "
              "(tokens study, 2026-10-28). Project: API-billed "
              "input+output from docs/metrics/usage.jsonl @ a73e97d "
              "(93 rows, waves 0-5); cached is inside input, not added.\" "
              "The owner tick is drawn 4 px wide at 1440p; proportional "
              "width is ~0.0015 px, hence 'true bar <1 px wide'.",
              "- The bootrom 'five basic sums correctly rounded' line "
              "loses its on-screen asterisk; the flush-rules caveat is "
              "stated by the next two rows on the same card and in full "
              "in options-facts.md (SF-0 section 8).",
              "- 'Versions' replaces 'instantiations' (849) in settle + "
              "stat card: same count, plainer noun.", ""]

    lines += ["## Stills eyeballed by the author", "",
              "- Pre-encode frames (frameprobe/): idea2 all 5 scenes, why3 "
              "title/workloads/spec/opt1/opt2/opt3/settle, intro plate, "
              "outro final composite - no overflow, no collisions "
              "(one-line 'next number' label fits; INTERVAL GEOMETRY "
              "card titles fit their cards).",
              "- MP4 grabs: stills3/intro (enter, typing, hold, mid-dive "
              "at proof crop, white), stills3/outro (near-black, dots "
              "pull-back, reply, mid-panel-staging, final), "
              "stills-idea2 (7), why/stills3 (9), plus "
              "still3_period_proof/midzoom/bubble.",
              "- Two defects caught at probe stage and fixed before "
              "render: a 3-new-lines beat in why workloads cards (split "
              "into name+one-line recap), and an 8-word why interval "
              "block that broke its dwell (needs shortened to "
              "'Down / up per end').", ""]

    lines += ["## Assembly notes / still open", "",
              "- Order and joins unchanged: intro3 (white out) -> idea2 "
              "-> why3 -> git -> outro3 (near-black in); all four now "
              "native 2560x1440 so the intro/outro 1080p mismatch flagged "
              "since v2 is gone. Front total 71.5 s (was 57.5 s).",
              "- Owner sign-off still needed on: plainer copy overall, "
              "the lineup-scene cut, 'versions', outro bubble trim, "
              "left-panel tag replacing the definitions block.",
              "- Silent as before; reveals sit on the 0.5 s (120 BPM) "
              "grid for music. At-speed watch-through by a human is "
              "still the real pacing test - dwells here are analytic "
              "(rule audit) + still-based, as in v2.",
              f"- Gates: " + "; ".join(f"{n}={'PASS' if ok else 'FAIL'}"
                                        for n, ok in gates) + ".", ""]

    (HERE / "textrev-report.md").write_text("\n".join(lines), encoding="utf-8")
    print("READY" if ready else "NOT READY", gates)
    print("wrote textrev-report.md")
    return 0 if ready else 3


if __name__ == "__main__":
    raise SystemExit(main())
