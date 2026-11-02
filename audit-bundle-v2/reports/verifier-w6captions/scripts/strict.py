"""Independent strict parser for assembly_v6.srt / .vtt (verifier-owned).

Checks: SRT comma timestamps + 1-based numbering; VTT header + dot
timestamps; monotonic strictly-increasing starts; no overlaps
(start < prev_end is a failure); 0 < start < end <= duration;
srt cue set == vtt cue set (times + text). Duration probed from
the committed assembly_v6.mp4 (default 179.03 fallback, printed).
"""
import re
import subprocess
import sys
from pathlib import Path

COPY = Path("C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify6-captions")
SRT = COPY / "video/out/assembly_v6.srt"
VTT = COPY / "video/out/assembly_v6.vtt"
MP4 = COPY / "video/out/assembly_v6.mp4"

TS = r"(\d{2}):(\d{2}):(\d{2})([.,])(\d{3})"


def ts_to_ms(h, m, s, ms):
    if int(m) >= 60 or int(s) >= 60:
        raise ValueError(f"timestamp out of range {h}:{m}:{s}")
    return ((int(h) * 60 + int(m)) * 60 + int(s)) * 1000 + int(ms)


def probe_duration():
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        # use ffprobe if present beside ffmpeg, else parse ffmpeg -i stderr
        import shutil
        pp = shutil.which("ffprobe")
        if pp is None:
            r = subprocess.run([exe, "-i", str(MP4)], capture_output=True,
                               text=True)
        else:
            r = subprocess.run(
                [pp, "-v", "error", "-show_entries", "format=duration",
                 "-of", "csv=p=0", str(MP4)], capture_output=True, text=True)
            try:
                return float(r.stdout.strip().split()[0])
            except Exception:
                pass
        m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
        if m:
            return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    except Exception as e:
        print(f"probe failed: {e}")
    return 179.03


def parse_srt(text):
    if "\r" in text:
        raise ValueError("srt: CR found")
    blocks = [b for b in text.rstrip("\n").split("\n\n") if b.strip()]
    line_re = re.compile(rf"^{TS} --> {TS}$")
    spans = []
    for i, block in enumerate(blocks, start=1):
        rows = block.split("\n")
        if len(rows) < 3 or rows[0] != str(i):
            raise ValueError(f"srt cue {i}: bad header {rows[:1]!r}")
        m = line_re.match(rows[1])
        if not m or m.group(4) != "," or m.group(9) != ",":
            raise ValueError(f"srt cue {i}: bad timing (need commas): {rows[1]!r}")
        spans.append((ts_to_ms(m.group(1), m.group(2), m.group(3), m.group(5)),
                      ts_to_ms(m.group(6), m.group(7), m.group(8), m.group(10)),
                      tuple(rows[2:])))
    return spans


def parse_vtt(text):
    if "\r" in text:
        raise ValueError("vtt: CR found")
    if not text.startswith("WEBVTT\n"):
        raise ValueError("vtt: missing WEBVTT header")
    blocks = [b for b in text.rstrip("\n").split("\n\n") if b.strip()]
    if not blocks or blocks[0] != "WEBVTT":
        raise ValueError("vtt: header block not exactly WEBVTT")
    line_re = re.compile(rf"^{TS} --> {TS}$")
    spans = []
    seps = {}
    for i, block in enumerate(blocks[1:], start=1):
        rows = block.split("\n")
        if len(rows) < 2:
            raise ValueError(f"vtt cue {i}: malformed {rows!r}")
        m = line_re.match(rows[0])
        if not m:
            raise ValueError(f"vtt cue {i}: bad timing line: {rows[0]!r}")
        seps[i] = (m.group(4), m.group(9))
        spans.append((ts_to_ms(m.group(1), m.group(2), m.group(3), m.group(5)),
                      ts_to_ms(m.group(6), m.group(7), m.group(8), m.group(10)),
                      tuple(rows[1:])))
    return spans


def check(spans, what, limit_ms):
    errs = []
    per_seg = {}
    prev_start = prev_end = None
    for idx, (a, b, lines) in enumerate(spans, start=1):
        if not lines or any(not ln.strip() for ln in lines):
            errs.append(f"{what} cue {idx}: empty text")
        if not (0 < a < b <= limit_ms):
            errs.append(f"{what} cue {idx}: bounds 0 < {a} < {b} <= {limit_ms} fail")
        if prev_start is not None and a <= prev_start:
            errs.append(f"{what} cue {idx}: start {a} not > prev start {prev_start}")
        if prev_end is not None and a < prev_end:
            errs.append(f"{what} cue {idx}: OVERLAP start {a} < prev end {prev_end}")
        prev_start, prev_end = a, b
    return errs


def unescape_vtt(lines):
    return tuple(ln.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
                   for ln in lines)


def main():
    dur = probe_duration()
    limit_ms = int(round(dur * 1000))
    print(f"probed duration: {dur:.3f}s -> limit {limit_ms}ms")
    srt = parse_srt(SRT.read_text(encoding="utf-8"))
    vtt_text = VTT.read_text(encoding="utf-8")
    vtt = parse_vtt(vtt_text)
    print(f"srt cues: {len(srt)}  vtt cues: {len(vtt)}")
    errs = check(srt, "srt", limit_ms) + check(vtt, "vtt", limit_ms)
    # vtt separator strictness: every cue must use dots
    import re as _re
    for i, tl in enumerate(vtt_text.split("\n\n")[1:], start=1):
        first = (tl.strip().split("\n") or [""])[0]
        if "-->" in first and "," in first.split("-->")[0]:
            errs.append(f"vtt cue {i}: comma timestamp (need dots): {first!r}")
    vttu = [(a, b, unescape_vtt(ls)) for a, b, ls in vtt]
    if [(a, b, tuple(ls)) for a, b, ls in srt] != [(a, b, tuple(ls)) for a, b, ls in vttu]:
        errs.append("srt cue set != vtt cue set (times or text differ)")
        for i, (s, v) in enumerate(zip(srt, vttu), start=1):
            if s != v:
                print(f"  diff at cue {i}: srt={s} vtt={v}")
    # segment histogram by start time (scaled bounds: intro<6.77 idea<31.94 why<62.90 git<167.74 outro)
    bounds = [("intro", 6.774), ("idea", 31.935), ("why", 62.903),
              ("gitvisual", 167.742), ("outro", 1e9)]
    hist = {}
    for a, b, ls in srt:
        for name, top in bounds:
            if a / 1000 < top:
                hist[name] = hist.get(name, 0) + 1
                break
    print("per-segment histogram (by start):", hist)
    if errs:
        print(f"FAIL ({len(errs)} errors):")
        for e in errs:
            print("  " + e)
        return 1
    print("STRICT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
