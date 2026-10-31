"""Captions for the final cut: out/assembly_v6.srt + .vtt (179.03 s).

Inclusion rule: a cue is emitted for every beat of readable
headline/body text a viewer is meant to read in sequence -- the
phone message and replies, the idea/why scene headlines and the
body lines that land one beat at a time, the chase popup cards,
the three gate-window titles, the outro panels and stat cards.
Excluded by name: HUD counters and the commit ticker strip,
graph branch/lane/marble labels and the retained-plate label,
hashes and check-value rows, both legends, source tags (the
``(SF-0 ...)`` tags, gate ``src:`` tags, SRC_CHASE/SRC_REPLAY),
phone UI chrome, and gate-window interiors other than the title
bar (chart/hash furniture, covered by the categories above).
Cue text is never hand-transcribed where an audit table exists:
this module imports the segment renderers and reads their own
audit data (idea.BLOCKS, why.BLOCKS, intro_outro.BLOCKS_INTRO /
BLOCKS_OUTRO, gitvisual.POPUP5 with ARRIVALS/POPUP_DWELL, and
gitvisual.GATES titles). The one readable beat no audit table
expresses -- the gitvisual opening headline -- is the single
explicit entry in EXTRA_CUES, with its source named there.

Timing model: assembly-native time is segment-local time plus
the segment's native offset (derived from assemble.SEGMENTS in
assemble.ORDER: intro 0, idea 7, why 33, gitvisual 65, outro
173; total 185.0 s), scaled by 120/124 into assembly time --
the same uniform setpts tempo scale assemble.py applies, so
every cue lands on the same scaled instant as its on-screen
beat (185.0 x 120/124 = 179.03 s, the probed assembly length).
BLOCKS entries co-exist on screen (a scene accumulates lines,
each t_gone is the scene cut); captions may not overlap, so each
BLOCKS cue ends at the earlier of its t_gone and the next cue's
start in the same segment -- the instant the next new text lands.

Run from the workspace root with the project venv:
    .venv\\Scripts\\python.exe muse-softfloat\\video\\captions.py
        [--validate] [--stills]
Outputs are byte-stable across re-runs (no wall-clock content);
--validate re-parses the written .srt/.vtt with the strict
parsers below; --stills regenerates out/stills_v6/ + INDEX.md
(one still per scene beat, grabbed from out/assembly_v6.mp4 in
scaled time; beat times computed from the same audit data).
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEG = HERE / "segments"
OUT = HERE / "out"
sys.path.insert(0, str(SEG))
sys.path.insert(0, str(HERE))

import assemble  # noqa: E402  (segment order + native durations)
import idea  # noqa: E402
import why  # noqa: E402
import intro_outro  # noqa: E402
import gitvisual  # noqa: E402

SCALE = 120.0 / 124.0  # the assemble.py setpts tempo scale
ASSEMBLY_DUR_S = 179.03  # probed out/assembly_v6.mp4 duration (brief cap)

# native offsets derived, not copied: cumulative assemble durations
_DUR = {mp4: dur for _s, mp4, dur in assemble.SEGMENTS}
_OFFSET: dict[str, float] = {}
_t = 0.0
for _mp4 in assemble.ORDER:
    _OFFSET[_mp4] = _t
    _t += _DUR[_mp4]
NATIVE_TOTAL_S = _t
OFF_INTRO = _OFFSET["intro3.mp4"]      # 0
OFF_IDEA = _OFFSET["idea2-1440p.mp4"]  # 7
OFF_WHY = _OFFSET["why3-1440p.mp4"]    # 33
OFF_GIT = _OFFSET["gitvisual7.mp4"]    # 65
OFF_OUTRO = _OFFSET["outro3.mp4"]      # 173

# a BLOCKS beat whose only line(s) are a bare source tag is not a cue
_SOURCE_TAG_RE = re.compile(r"^\(SF-0\b.*\)$")
# gate windows rise over 0.8 s and close over the last 0.8 s
# (gitvisual.draw_gate_window: rise = ss(lt / 0.8), close ditto);
# the title is only readable between those, so the cue is trimmed.
GATE_RISE_S = 0.8


@dataclass(frozen=True)
class Cue:
    start: float  # scaled (assembly) seconds
    end: float    # scaled (assembly) seconds
    lines: tuple[str, ...]
    segment: str
    source: str


@dataclass(frozen=True)
class Still:
    slug: str
    native_s: float  # assembly-native (pre-scale) seconds of the beat
    segment: str
    segment_local_s: float
    shows: str


def _scaled(native_assembly_s: float) -> float:
    return native_assembly_s * SCALE


# --- the one readable beat no audit table expresses --------------
# gitvisual.draw_opening draws this headline top-left from T_BOX
# until the end-scene dim reaches 0.9: dim = clamp((lt -
# PACK_DIM_LT) / 1.4), so it clears at lt = PACK_DIM_LT + 1.4*0.9.
# The text is an inline literal in draw_opening (nothing to
# import); the times are computed from imported constants.
EXTRA_CUES = [
    Cue(
        start=_scaled(OFF_GIT + gitvisual.T_BOX),
        end=_scaled(OFF_GIT + gitvisual.T_BOX
                    + gitvisual.PACK_DIM_LT + 1.4 * 0.9),
        lines=("every system drops in, kept",),
        segment="gitvisual",
        source="gitvisual.draw_opening headline (inline literal; "
               "T_BOX..dim<0.9 from imported constants)",
    ),
]


def _blocks_to_cues(blocks, offset_native, segment, source_prefix):
    """(name, t0, t_gone, lines) audit rows -> non-overlapping cues."""
    rows = []
    for name, t0, t_gone, lines in blocks:
        lines = tuple(str(ln) for ln in lines)
        if lines and all(_SOURCE_TAG_RE.match(ln) for ln in lines):
            continue  # bare source tag: excluded by the header rule
        if not lines or any(not ln.strip() for ln in lines):
            raise ValueError(f"{source_prefix}.{name}: empty line(s)")
        rows.append((name, float(t0), float(t_gone), lines))
    cues = []
    for i, (name, t0, t_gone, lines) in enumerate(rows):
        end_local = t_gone
        if i + 1 < len(rows):
            end_local = min(end_local, rows[i + 1][1])
        cues.append(Cue(
            start=_scaled(offset_native + t0),
            end=_scaled(offset_native + end_local),
            lines=lines,
            segment=segment,
            source=f"{source_prefix} {name}",
        ))
    return cues


def build_cues() -> list[Cue]:
    # cross-check the audit modules against assemble.py's durations
    assert idea.DUR == _DUR["idea2-1440p.mp4"], (idea.DUR, _DUR)
    assert why.DUR == _DUR["why3-1440p.mp4"], (why.DUR, _DUR)
    assert intro_outro.INTRO_DUR == _DUR["intro3.mp4"]
    assert intro_outro.OUTRO_DUR == _DUR["outro3.mp4"]
    assert gitvisual.TOTAL == _DUR["gitvisual7.mp4"]
    assert abs(_scaled(NATIVE_TOTAL_S) - ASSEMBLY_DUR_S) < 0.01, (
        _scaled(NATIVE_TOTAL_S), ASSEMBLY_DUR_S)

    cues: list[Cue] = []
    cues += _blocks_to_cues(intro_outro.BLOCKS_INTRO, OFF_INTRO,
                            "intro", "intro_outro.BLOCKS_INTRO")
    cues += _blocks_to_cues(idea.BLOCKS, OFF_IDEA, "idea", "idea.BLOCKS")
    cues += _blocks_to_cues(why.BLOCKS, OFF_WHY, "why", "why.BLOCKS")
    # chase popup cards: drawn from each arrival while
    # t < arrival + dwell (gitvisual.draw_chase_world/frame_at)
    for i, (title, lines) in enumerate(gitvisual.POPUP5):
        a = float(gitvisual.ARRIVALS[i])
        cues.append(Cue(
            start=_scaled(OFF_GIT + a),
            end=_scaled(OFF_GIT + a + float(gitvisual.POPUP_DWELL[i])),
            lines=(title, *lines),
            segment="gitvisual",
            source=f"gitvisual.POPUP5[{i}] ARRIVALS/POPUP_DWELL",
        ))
    # gate-window titles (title bar; sub carries a merge hash and
    # src is a source tag: both excluded by the header rule)
    for gate in gitvisual.GATES:
        cues.append(Cue(
            start=_scaled(OFF_GIT + float(gate["t0"]) + GATE_RISE_S),
            end=_scaled(OFF_GIT + float(gate["t1"]) - GATE_RISE_S),
            lines=(gate["title"],),
            segment="gitvisual",
            source=f"gitvisual.GATES[{gate['id']}] title",
        ))
    cues += EXTRA_CUES
    cues += _blocks_to_cues(intro_outro.BLOCKS_OUTRO, OFF_OUTRO,
                            "outro", "intro_outro.BLOCKS_OUTRO")
    cues.sort(key=lambda c: (c.start, c.end))
    validate_cues(cues)
    return cues


# --- formatting (millisecond grid; the grid the parsers see) ------

def _ms(t: float) -> int:
    return int(round(t * 1000.0))


def _ts(total_ms: int, sep: str) -> str:
    h, rem = divmod(total_ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def _vtt_escape(line: str) -> str:
    # WebVTT cue text: &, <, > must be escaped or they parse as markup
    return line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _end_ms(c: Cue) -> int:
    # the final outro beat runs to the native end (185.0 s), whose
    # scaled value 179.032... rounds past the probed container
    # duration; no cue may end after the film does
    return min(_ms(c.end), _ms(ASSEMBLY_DUR_S))


def render_srt(cues: list[Cue]) -> str:
    out = []
    for i, c in enumerate(cues, start=1):
        out.append(str(i))
        out.append(f"{_ts(_ms(c.start), ',')} --> {_ts(_end_ms(c), ',')}")
        out.extend(c.lines)
        out.append("")
    return "\n".join(out)


def render_vtt(cues: list[Cue]) -> str:
    out = ["WEBVTT", ""]
    for c in cues:
        out.append(f"{_ts(_ms(c.start), '.')} --> {_ts(_end_ms(c), '.')}")
        out.extend(_vtt_escape(ln) for ln in c.lines)
        out.append("")
    return "\n".join(out)


# --- strict validation + parsers ----------------------------------
_TS_RE = r"(\d{2}):(\d{2}):(\d{2})([.,])(\d{3})"


def _ts_to_ms(h: str, m: str, s: str, ms: str) -> int:
    if int(m) >= 60 or int(s) >= 60:
        raise ValueError(f"timestamp out of range: {h}:{m}:{s}")
    return ((int(h) * 60 + int(m)) * 60 + int(s)) * 1000 + int(ms)


def _check_span_list(spans, what: str) -> None:
    """spans: [(start_ms, end_ms, lines)] on the millisecond grid."""
    limit_ms = _ms(ASSEMBLY_DUR_S)
    prev_start = prev_end = None
    for start_ms, end_ms, lines in spans:
        if not lines or any(not ln.strip() for ln in lines):
            raise ValueError(f"{what}: empty cue text at {start_ms} ms")
        if any("-->" in ln for ln in lines):
            raise ValueError(f"{what}: cue text contains '-->' at {start_ms} ms")
        if not (0 < start_ms < end_ms <= limit_ms):
            raise ValueError(
                f"{what}: need 0 < start < end <= {limit_ms} ms, "
                f"got {start_ms}..{end_ms}")
        if prev_start is not None and start_ms <= prev_start:
            raise ValueError(f"{what}: starts not strictly monotonic "
                             f"at {start_ms} ms")
        if prev_end is not None and start_ms < prev_end:
            raise ValueError(f"{what}: cue at {start_ms} ms overlaps "
                             f"previous end {prev_end} ms")
        prev_start, prev_end = start_ms, end_ms


def validate_cues(cues: list[Cue]) -> None:
    if not cues:
        raise ValueError("no cues")
    _check_span_list(
        [(_ms(c.start), min(_ms(c.end), _ms(ASSEMBLY_DUR_S)), c.lines)
         for c in cues], "generated cues")
    for c in cues:
        for ln in c.lines:
            if "\n" in ln or "\r" in ln:
                raise ValueError(f"{c.source}: line contains a newline")


def parse_srt(text: str):
    if "\r" in text:
        raise ValueError("srt: CR found (LF-only file expected)")
    blocks = [b for b in text.rstrip("\n").split("\n\n") if b.strip()]
    spans = []
    line_re = re.compile(rf"^{_TS_RE} --> {_TS_RE}$")
    for i, block in enumerate(blocks, start=1):
        rows = block.split("\n")
        if len(rows) < 3 or rows[0] != str(i):
            raise ValueError(f"srt: cue {i} malformed header: {rows[:1]!r}")
        m = line_re.match(rows[1])
        if not m or m.group(4) != "," or m.group(9) != ",":
            raise ValueError(f"srt: cue {i} bad timing line: {rows[1]!r}")
        spans.append((_ts_to_ms(m.group(1), m.group(2), m.group(3), m.group(5)),
                      _ts_to_ms(m.group(6), m.group(7), m.group(8), m.group(10)),
                      tuple(rows[2:])))
    _check_span_list(spans, "srt")
    return spans


def parse_vtt(text: str):
    if "\r" in text:
        raise ValueError("vtt: CR found (LF-only file expected)")
    if not text.startswith("WEBVTT\n"):
        raise ValueError("vtt: missing WEBVTT header")
    blocks = [b for b in text.rstrip("\n").split("\n\n") if b.strip()]
    if not blocks or blocks[0] != "WEBVTT":
        raise ValueError("vtt: header block is not exactly 'WEBVTT'")
    spans = []
    line_re = re.compile(rf"^{_TS_RE} --> {_TS_RE}$")
    for i, block in enumerate(blocks[1:], start=1):
        rows = block.split("\n")
        if len(rows) < 2:
            raise ValueError(f"vtt: cue {i} malformed: {rows!r}")
        m = line_re.match(rows[0])
        if not m or m.group(4) != "." or m.group(9) != ".":
            raise ValueError(f"vtt: cue {i} bad timing line: {rows[0]!r}")
        for ln in rows[1:]:
            if "<" in ln or ">" in ln:
                raise ValueError(f"vtt: cue {i} has unescaped markup: {ln!r}")
        spans.append((_ts_to_ms(m.group(1), m.group(2), m.group(3), m.group(5)),
                      _ts_to_ms(m.group(6), m.group(7), m.group(8), m.group(10)),
                      tuple(ln.replace("&lt;", "<").replace("&gt;", ">")
                            .replace("&amp;", "&") for ln in rows[1:])))
    _check_span_list(spans, "vtt")
    return spans


def validate_files(srt_path: Path, vtt_path: Path, cues: list[Cue]) -> int:
    srt = parse_srt(srt_path.read_text(encoding="utf-8"))
    vtt = parse_vtt(vtt_path.read_text(encoding="utf-8"))
    if srt != vtt:
        raise ValueError("srt and vtt cue lists differ")
    expect = [(_ms(c.start), min(_ms(c.end), _ms(ASSEMBLY_DUR_S)), c.lines)
              for c in cues]
    # parsed lines are tuples; cue lines are tuples already
    expect = [(a, b, tuple(ls)) for a, b, ls in expect]
    if [(a, b, tuple(ls)) for a, b, ls in srt] != expect:
        raise ValueError("files do not round-trip to the generated cues")
    return len(srt)


# --- stills: one per scene beat, times from the same audit data ---

def _scene_beat(blocks, scene):
    """Native segment-local instant when a scene's text is complete:
    midway between its last new-text beat and its scene cut."""
    rows = [(float(a), float(b)) for (s, a, b, _ls) in blocks if s == scene]
    if not rows:
        raise ValueError(f"no BLOCKS scene {scene!r}")
    last_start, gone = rows[-1][0], rows[-1][1]
    return (last_start + gone) / 2.0


_IDEA_SHOWS = {
    "idea": "THE IDEA card complete: software IEEE 754 for the RP2040, "
            "'Same answer everywhere.'",
    "correct": "WHAT 'CORRECT' MEANS number line: exact answer, "
               "correctly rounded arrow to A, neighbour crossed",
    "prove": "WHAT WILL PROVE IT: IAS15 / INTERVAL GEOMETRY / "
             "KISSFFT - FORK B cards complete",
    "method": "HOW IT GETS BUILT: numbered method rows 1-3 + "
              "'Watch it land.'",
    "question": "BUT FIRST - WHY NOT USE WHAT ALREADY SHIPS? "
                "(full two-line question)",
}
_WHY_SHOWS = {
    "spec": "TOGETHER: A JOB SPEC checklist complete (seven rows)",
    "opt1": "OPTION 1 - THE DEFAULT card, rows complete, "
            "ELIMINATED stamp",
    "opt2": "OPTION 2 - THE FALL-THROUGH card, rows complete, "
            "NOT MEASURED stamp",
    "opt3": "OPTION 3 card: panic line + NO FLOATS AT ALL stamp",
    "settle": "SO BUILD THE FOURTH OPTION / MUSE-SOFTFLOAT settle "
              "card complete (four lines)",
}


def build_stills() -> list[Still]:
    stills: list[Still] = []

    def add(slug, offset, local, segment, shows):
        stills.append(Still(slug=slug, native_s=offset + local,
                            segment=segment, segment_local_s=local,
                            shows=shows))

    _n, a, b, _ls = intro_outro.BLOCKS_INTRO[0]
    add("intro-msg", OFF_INTRO, (float(a) + float(b)) / 2.0, "intro",
        "phone with the full typed message 'Hey Muse, I've got "
        "an idea...' held before the dive")
    for scene, shows in _IDEA_SHOWS.items():
        add(f"idea-{scene}", OFF_IDEA, _scene_beat(idea.BLOCKS, scene),
            "idea", shows)
    for scene, shows in _WHY_SHOWS.items():
        add(f"why-{scene}", OFF_WHY, _scene_beat(why.BLOCKS, scene),
            "why", shows)
    g = gitvisual
    add("git-chase-start", OFF_GIT, 2.0, "gitvisual",
        "flat teaching track with systems legend before the first "
        "popup (frame is white before 1.0 s by design)")
    for i, (title, _lines) in enumerate(g.POPUP5):
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        add(f"git-popup-{slug}", OFF_GIT,
            float(g.ARRIVALS[i]) + float(g.POPUP_DWELL[i]) / 2.0,
            "gitvisual", f"{title} popup card on its lit node, mid-dwell")
    add("git-bridge", OFF_GIT, (float(g.T_BRIDGE) + float(g.T_REPLAY)) / 2.0,
        "gitvisual", "bridge cross-fade: teaching track carried into "
                     "the real-history replay, HUD counters live")
    add("git-replay-early", OFF_GIT,
        (float(g.T_REPLAY) + float(g.GATES[0]["t0"])) / 2.0, "gitvisual",
        "replay climbing the process graph before the IAS15 gate")
    for gate in g.GATES:
        add(f"git-gate-{gate['id']}", OFF_GIT, float(gate["t0"]) + 6.0,
            "gitvisual", f"{gate['title']} gate window open over the "
                         "track (window-local 6.0 s: content complete, "
                         "before PASS footer at 6.5 s)")
    add("git-replay-late", OFF_GIT,
        (float(g.GATES[1]["t1"]) + float(g.GATES[2]["t0"])) / 2.0,
        "gitvisual", "replay between the KissFFT gate and the "
                     "augmented-interval epilogue gate")
    add("git-opening-fall", OFF_GIT, float(g.T_BOX) + 3.5, "gitvisual",
        "opening in the slab: system marbles travelling/falling in, "
        "'every system drops in, kept' headline")
    add("git-opening-plate", OFF_GIT, float(g.T_BOX) + 8.0, "gitvisual",
        "all system marbles in; muse-softfloat plate with kept "
        "stamps, headline still up before the fade")
    bo = intro_outro.BLOCKS_OUTRO
    add("outro-replies", OFF_OUTRO, (float(bo[1][1]) + float(bo[2][1])) / 2.0,
        "outro", "phone with both replies: 'Done - it held up.' and "
                 "'Identical on all 6 boards.'")
    add("outro-human-ai", OFF_OUTRO, (float(bo[4][1]) + float(bo[5][1])) / 2.0,
        "outro", "HUMAN : AI SPLIT panel complete (project/owner bars "
                 "and the 1 : 620,000 ratio)")
    add("outro-stats", OFF_OUTRO, (float(bo[7][1]) + float(bo[7][2])) / 2.0,
        "outro", "final hold: phone, HUMAN : AI panel and all three "
                 "stat cards on screen")
    stills.sort(key=lambda s: s.native_s)
    return stills


def still_filename(index: int, still: Still) -> str:
    return f"{index:02d}_t{_scaled(still.native_s):06.2f}_{still.slug}.png"


def render_index(stills: list[Still]) -> str:
    lines = [
        "# stills_v6 - one still per scene beat of assembly_v6.mp4",
        "",
        "Grabbed from the committed `../assembly_v6.mp4` (179.03 s) by "
        "`captions.py --stills`. Scaled time is the film (assembly) "
        "time the frame was grabbed at; native time is the same "
        "instant before assemble.py's uniform 120/124 tempo scale "
        "(scaled = native x 120/124; native total 185.0 s). Local "
        "time is within the named segment. All times are recomputed "
        "by the generator from the segment audit data, never copied.",
        "",
        "| # | Still | Scaled (s) | Native (s) | Segment (local s) | Shows |",
        "|---|---|---:|---:|---|---|",
    ]
    for i, s in enumerate(stills, start=1):
        lines.append(
            f"| {i} | `{still_filename(i, s)}` | {_scaled(s.native_s):.2f} "
            f"| {s.native_s:.2f} | {s.segment} ({s.segment_local_s:.2f}) "
            f"| {s.shows} |")
    lines.append("")
    return "\n".join(lines)


def grab_stills(stills_dir: Path) -> list[Still]:
    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    mp4 = OUT / "assembly_v6.mp4"
    if not mp4.exists():
        raise SystemExit(f"missing {mp4} (run assemble.py first)")
    stills = build_stills()
    stills_dir.mkdir(parents=True, exist_ok=True)
    for old in stills_dir.glob("*.png"):
        old.unlink()
    for i, s in enumerate(stills, start=1):
        out = stills_dir / still_filename(i, s)
        subprocess.run([exe, "-y", "-hide_banner", "-loglevel", "error",
                        "-ss", f"{_scaled(s.native_s):.3f}", "-i", str(mp4),
                        "-frames:v", "1", str(out)], check=True)
        print(f"still {i:02d}/{len(stills)} t={_scaled(s.native_s):.2f}s "
              f"-> {out.name}")
    (stills_dir / "INDEX.md").write_text(render_index(stills),
                                         encoding="utf-8", newline="\n")
    return stills


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", type=Path, default=OUT,
                    help="directory for assembly_v6.srt/.vtt (default: out/)")
    ap.add_argument("--validate", action="store_true",
                    help="re-parse the written files with the strict parsers")
    ap.add_argument("--stills", action="store_true",
                    help="also regenerate out/stills_v6/ + INDEX.md")
    a = ap.parse_args()
    cues = build_cues()
    a.out_dir.mkdir(parents=True, exist_ok=True)
    srt_path = a.out_dir / "assembly_v6.srt"
    vtt_path = a.out_dir / "assembly_v6.vtt"
    srt_path.write_text(render_srt(cues), encoding="utf-8", newline="\n")
    vtt_path.write_text(render_vtt(cues), encoding="utf-8", newline="\n")
    per_seg: dict[str, int] = {}
    for c in cues:
        per_seg[c.segment] = per_seg.get(c.segment, 0) + 1
    print(f"cues: {len(cues)} " +
          " ".join(f"{k}={per_seg[k]}" for k in
                   ("intro", "idea", "why", "gitvisual", "outro")))
    print(f"wrote {srt_path} ({srt_path.stat().st_size} bytes)")
    print(f"wrote {vtt_path} ({vtt_path.stat().st_size} bytes)")
    if a.validate:
        n = validate_files(srt_path, vtt_path, cues)
        print(f"validate: PASS ({n} cues, srt == vtt == generated, "
              f"monotonic, no overlaps, 0 < start < end <= "
              f"{ASSEMBLY_DUR_S:.2f}s)")
    if a.stills:
        stills = grab_stills(OUT / "stills_v6")
        print(f"stills: {len(stills)} -> {OUT / 'stills_v6'} + INDEX.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



