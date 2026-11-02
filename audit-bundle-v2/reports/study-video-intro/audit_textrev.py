"""Word-count / dwell audit for the text/pacing pass (Agent A).

Imports the three NEW render modules' BLOCKS tables (single source of
truth for new copy+timing) and audits every block against THE RULE:
dwell_min = smallest 0.5 s multiple >= max(1.5, 0.5 + words/2.5).
Word = whitespace token containing a letter/digit. Dwell given =
t_gone - t0 (reveal beat to scene cut / fade start / dive start /
clip end; typed bubbles use FULL-text time as t0). Also checks:
<=2 new lines per block (beat), every line <=10 words, headline
lines <=6 words. OLD blocks transcribed from render_idea.py /
render_why2.py (+render_why.py data) / render_v2.py for word totals
and dwell-before. Writes audit3.json. Run: $MSF_PYTHON audit_textrev.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "study-video-idea"))
sys.path.insert(0, str(HERE.parent / "study-video-why"))
import render_v3 as V3  # noqa: E402
import render_idea2 as ID2  # noqa: E402
import render_why3 as W3  # noqa: E402


def words(s: str) -> int:
    return sum(1 for tok in s.split() if any(c.isalnum() for c in tok))


def rule_min(w: int) -> float:
    return math.ceil(max(1.5, 0.5 + w / 2.5) * 2) / 2


def blk_words(lines) -> int:
    return sum(words(s) for s in lines)


NEW = {
    "intro": [("intro",) + b[1:] for b in V3.BLOCKS_INTRO],
    "idea": list(ID2.BLOCKS),
    "why": list(W3.BLOCKS),
    "outro": [("outro",) + b[1:] for b in V3.BLOCKS_OUTRO],
}

OLD = {
    "intro": [("intro", 2.0, 2.5, ["Hey Muse, I've got an idea..."])],
    "idea": [
        ("idea", 0.5, 3.0, ["THE IDEA", "one sentence, then what it demands"]),
        ("idea", 0.5, 3.0, ["A software IEEE 754 floating-point library"]),
        ("idea", 1.0, 3.0, ["for the RP2040 \u2014 a chip with no FPU,"]),
        ("idea", 1.5, 3.0, ["where every float is already software \u2014"]),
        ("idea", 2.0, 3.0, ["so real science code runs bit-identically:"]),
        ("idea", 2.5, 3.0, ["same source on desktop and chip, same bits out."]),
        ("correct", 3.0, 6.5, ["WHAT \u201cCORRECT\u201d MEANS HERE",
                               "every result the correctly rounded one \u2014 every flag exact"]),
        ("correct", 3.0, 6.5, ["representable", "value A", "next value", "A + 1 ULP"]),
        ("correct", 3.0, 5.0, ["one operation, done exactly \u2014 where must it land?"]),
        ("correct", 4.0, 6.5, ["exact result", "(infinitely precise)"]),
        ("correct", 5.0, 6.5, ["correctly rounded \u2192 A",
                               "a neighbour is a wrong answer"]),
        ("correct", 5.5, 6.5, ["not close \u2014 exact: right value, right flags, every time  (illustrative)"]),
        ("prove", 6.5, 10.0, ["WHAT WILL PROVE IT", "three real workloads, run on the chip"]),
        ("prove", 6.5, 10.0, ["IAS15", "orbital integrator", "binary64, bit-identical",
                              "desktop = chip,", "every bit, every step"]),
        ("prove", 7.5, 10.0, ["INTERVAL GEOMETRY", "guaranteed enclosures",
                              "directed rounding:", "down for one end,",
                              "up for the other"]),
        ("prove", 8.5, 10.0, ["KISSFFT \u2014 FORK B", "exact-angle FFT",
                              "sinPi / cosPi twiddles", "made at runtime,",
                              "correctly rounded"]),
        ("method", 10.0, 12.0, ["HOW IT GETS BUILT",
                                "the short version \u2014 the film shows the rest"]),
        ("method", 10.0, 12.0, ["1", "briefed agents build it, parcel by parcel"]),
        ("method", 10.5, 12.0, ["2", "every piece independently verified \u2014"]),
        ("method", 11.0, 12.0, ["3", "a verifier whose only job is to disconfirm"]),
        ("method", 11.5, 12.0, ["watch it land, commit by commit, in a minute."]),
        ("question", 12.0, 13.5, ["BUT FIRST \u2014", "WHY NOT USE WHAT",
                                  "ALREADY SHIPS?"]),
    ],
    "why": [
        ("title", 0.5, 2.5, ["WHY NOT USE WHAT", "ALREADY SHIPS?"]),
        ("title", 1.0, 2.5, ["The RP2040 has no FPU \u2014 every float is software. Three workloads go shopping."]),
        ("workloads", 2.5, 8.5, ["FIRST: THE WORKLOADS",
                                 "what actually has to run on the chip"]),
        ("workloads", 2.5, 8.5, ["IAS15", "orbital integrator", "NEEDS:",
                                 "binary64 bit-identical,", "desktop = chip,",
                                 "every bit, every step"]),
        ("workloads", 4.5, 8.5, ["INTERVAL GEOMETRY", "guaranteed enclosures",
                                 "NEEDS:", "directed rounding on demand:",
                                 "round down / round up,", "chosen per call"]),
        ("workloads", 6.5, 8.5, ["KISSFFT \u2014 FORK B", "exact-angle FFT", "NEEDS:",
                                 "sinPi / cosPi twiddles", "generated at runtime,",
                                 "correctly rounded"]),
        ("spec", 8.5, 12.5, ["TOGETHER, THAT'S A JOB SPEC",
                             "the IEEE 754-2019 semantics the three workloads stand on"]),
        ("spec", 8.5, 12.5, ["rounding attributes: all four, + tiesToAway"]),
        ("spec", 9.0, 12.5, ["exception flags: invalid \u00b7 div-by-zero \u00b7 overflow \u00b7 underflow \u00b7 inexact"]),
        ("spec", 9.5, 12.5, ["subnormals kept \u2014 never flushed to zero"]),
        ("spec", 10.0, 12.5, ["NaN payloads preserved through arithmetic"]),
        ("spec", 10.5, 12.5, ["formats: binary16 + binary32 + binary64"]),
        ("spec", 11.0, 12.5, ["correctly rounded \u2014 FMA, sqrt, sinPi/cosPi, hard cases"]),
        ("spec", 11.5, 12.5, ["augmented add / sub / mul: head + exact tail"]),
        ("opt1", 12.5, 19.0, ["OPTION 1 \u2014 THE DEFAULT",
                              "SDK \u2018pico\u2019 flavour \u2192 bootrom"]),
        ("opt1", 13.0, 19.0, ["five basic ops correctly rounded *  (+ \u2212 \u00d7 \u00f7 \u221a)"]),
        ("opt1", 14.0, 19.0, ["subnormals flushed to zero \u2014 in and out"]),
        ("opt1", 15.0, 19.0, ["NaNs rendered as infinities \u2014 payloads gone"]),
        ("opt1", 16.0, 19.0, ["one rounding mode: ties-to-even. No directed modes"]),
        ("opt1", 17.0, 19.0, ["exception flags: none exist"]),
        ("opt1", 17.5, 19.0, ["e.g. a tiny subnormal result \u2192 0, silently.",
                              "* five basic ops, under the flush rules (SF-0 \u00a78)"]),
        ("opt1", 18.5, 19.0, ["ELIMINATED"]),
        ("opt2", 19.0, 24.5, ["OPTION 2 \u2014 THE FALL-THROUGH",
                              "SDK \u2018compiler\u2019 flavour \u2192 libgcc"]),
        ("opt2", 19.5, 24.5, ["directed rounding?  not measured"]),
        ("opt2", 20.5, 24.5, ["exception flags?  not measured"]),
        ("opt2", 21.5, 24.5, ["NaN payloads? subnormals? binary16?  not measured"]),
        ("opt2", 22.5, 24.5, ["compiler FMA contraction varies by target (SF-0 \u00a79)"]),
        ("opt2", 23.0, 24.5, ["e.g. a\u00d7b+c may fuse on one target, not another \u2014 different bits.",
                              "SF-0 gated none of it \u2014 unmeasured semantics can't carry a proof"]),
        ("opt2", 24.0, 24.5, ["NOT MEASURED"]),
        ("opt3", 24.5, 26.5, ["OPTION 3", "SDK \u2018none\u2019 flavour"]),
        ("opt3", 25.0, 26.5, ['panic("float support is disabled")']),
        ("opt3", 25.5, 26.5, ["every float entry point is this stub",
                              "e.g. the first  a + b  in any workload never returns."]),
        ("opt3", 26.0, 26.5, ["NO FLOATS AT ALL"]),
        ("lineup", 26.5, 28.0, ["THE LINEUP vs THE SPEC",
                                "only what SF-0 actually measured or stated \u2014 ? means not measured"]),
        ("lineup", 26.5, 28.0, ["BOOTROM", "LIBGCC", "CUSTOM"]),
        ("lineup", 26.5, 28.0, ["rounding attrs"]),
        ("lineup", 26.65, 28.0, ["5 flags"]),
        ("lineup", 26.8, 28.0, ["subnormals"]),
        ("lineup", 26.95, 28.0, ["NaN payloads"]),
        ("lineup", 27.1, 28.0, ["b16+b32+b64"]),
        ("lineup", 27.25, 28.0, ["correct rounding"]),
        ("lineup", 27.4, 28.0, ["augmented ops"]),
        ("lineup", 27.0, 28.0, ["* five basic ops, under the flush rules"]),
        ("settle", 28.0, 31.0, ["SO BUILD THE FOURTH OPTION", "MUSE-SOFTFLOAT"]),
        ("settle", 28.5, 31.0, ["IEEE 754-2019 \u00b7 binary16 / 32 / 64 \u00b7 849 instantiations"]),
        ("settle", 29.0, 31.0, ["five rounding attributes \u00b7 five exact flags \u00b7 payloads preserved",
                                "subnormals kept \u00b7 augmented ops \u00b7 correctly rounded, hard cases in"]),
        ("settle", 29.5, 31.0, ["proven bit-identical on RP2040 silicon"]),
    ],
    "outro": [
        ("outro", 3.0, 6.0, ["Done \u2014 it held up."]),
        ("outro", 5.0, 6.0, ["849/849 ops across b16/b32/b64. 411,213 vectors in the gate, IAS15 identical on all 6 boards. Small parcels; verifiers that only disconfirm."]),
        ("outro", 3.5, 6.0, ["HUMAN : AI \u2014 THE WORK SPLIT",
                             "PROJECT BILLED   1,196,128,770 tokens",
                             "OWNER TYPED   ~1,928 tokens (est.)",
                             "1 px is too wide \u2014 shown 3 px",
                             "\u2248 1 : 620,000",
                             "Owner: chars/4 \u00b130% over 40 typed prompts (tokens study, 2026-10-28). Project: API-billed input+output from docs/metrics/usage.jsonl @ a73e97d (93 rows, waves 0\u20135); cached is inside input, not added."]),
        ("outro", 4.0, 6.0, ["849 / 849", "instantiations \u00b7 b16/b32/b64"]),
        ("outro", 4.5, 6.0, ["411,213", "vectors in the merge gate"]),
        ("outro", 5.0, 6.0, ["6 boards", "IAS15 \u00b7 2,001/2,001 state hashes"]),
    ],
}

# headline lines (must be <=6 words each; question/title pair summed)
HEADLINES = [
    ID2.HD_IDEA[0], ID2.HD_COR[0], ID2.HD_PROVE[0], ID2.HD_METH[0],
    W3.HD_WORK[0], W3.HD_SPEC[0], W3.O1_HEAD[0], W3.O1_HEAD[1],
    W3.O2_HEAD[0], W3.O2_HEAD[1], W3.O3_HEAD[0], W3.O3_HEAD[1],
    W3.ST_KICK, W3.ST_TITLE, V3.LP_TITLE,
    ID2.CARDS[0][0], ID2.CARDS[1][0], ID2.CARDS[2][0],
    W3.WORK[0][0], W3.WORK[1][0], W3.WORK[2][0],
    W3.O1_STAMP, W3.O2_STAMP, W3.O3_STAMP,
]
HEADLINE_PAIRS = [(ID2.Q_H1 + " " + ID2.Q_H2), (W3.T_H[0] + " " + W3.T_H[1])]


def audit(blocks):
    rows, viol = [], []
    for scene, t0, tg, lines in blocks:
        w = blk_words(lines)
        dwell = round(tg - t0, 3)
        mn = rule_min(w)
        nlines = len(lines)
        maxline = max(words(s) for s in lines)
        ok = dwell >= mn - 1e-9 and nlines <= 2 and maxline <= 10
        rows.append(dict(scene=scene, t0=t0, t_gone=tg, lines=lines, words=w,
                         dwell=dwell, rule_min=mn, n_lines=nlines,
                         max_line_words=maxline, ok=ok))
        if not ok:
            viol.append(rows[-1])
    return rows, viol


def main() -> int:
    out = {"segments": {}, "headline_checks": []}
    all_viol = []
    for seg in ("intro", "idea", "why", "outro"):
        nrows, nviol = audit(NEW[seg])
        orows, _ = audit(OLD[seg])
        ow = sum(r["words"] for r in orows)
        nw = sum(r["words"] for r in nrows)
        out["segments"][seg] = dict(
            old_words=ow, new_words=nw,
            cut_pct=round(100 * (1 - nw / ow), 1) if ow else None,
            new_blocks=nrows, old_blocks=orows)
        all_viol += [dict(seg=seg, **v) for v in nviol]
        print(f"{seg}: old {ow}w -> new {nw}w "
              f"({out['segments'][seg]['cut_pct']}% cut), "
              f"blocks {len(nrows)}, violations {len(nviol)}")
    for h in HEADLINES:
        out["headline_checks"].append(dict(line=h, words=words(h), ok=words(h) <= 6))
    for h in HEADLINE_PAIRS:
        out["headline_checks"].append(dict(line=h, words=words(h), ok=words(h) <= 6))
    bad_h = [h for h in out["headline_checks"] if not h["ok"]]
    out["violations"] = all_viol
    out["headline_failures"] = bad_h
    tot_o = sum(s["old_words"] for s in out["segments"].values())
    tot_n = sum(s["new_words"] for s in out["segments"].values())
    out["totals"] = dict(old_words=tot_o, new_words=tot_n,
                         cut_pct=round(100 * (1 - tot_n / tot_o), 1))
    print(f"TOTAL: {tot_o} -> {tot_n} ({out['totals']['cut_pct']}% cut)")
    print(f"headline failures: {len(bad_h)}; block violations: {len(all_viol)}")
    for v in all_viol:
        print(" VIOL", v["seg"], v["scene"], v["t0"], v["words"], "w dwell",
              v["dwell"], "min", v["rule_min"], "lines", v["n_lines"],
              "maxline", v["max_line_words"], v["lines"])
    (HERE / "audit3.json").write_text(json.dumps(out, indent=1))
    print("wrote audit3.json")
    return 0 if not all_viol and not bad_h else 2


if __name__ == "__main__":
    raise SystemExit(main())
