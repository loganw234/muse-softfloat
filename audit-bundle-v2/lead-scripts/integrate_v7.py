import pathlib
import shutil
import sys

WS = pathlib.Path.cwd()
SRC = WS / "scratch/study-video-gitvisual-v6"
SEG = WS / "muse-softfloat/video/segments"
fails = []


def load(p):
    raw = p.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    return raw.replace("\r\n", "\n"), crlf


def save(p, text, crlf):
    if crlf:
        text = text.replace("\n", "\r\n")
    p.write_bytes(text.encode("utf-8"))


def sub(p, old, new, count=1, label=""):
    text, crlf = load(p)
    n = text.count(old)
    if n != count:
        fails.append(f"{p.name} {label}: expected {count}, found {n} of {old[:60]!r}")
        return
    save(p, text.replace(old, new), crlf)
    print(f"edit {p.name}: {label}")


# 1. sync renderer + data + prep scripts into production
for name, dest in [("gitvisual7.py", "gitvisual.py"),
                   ("process_graph.json", "process_graph.json"),
                   ("augint_sample.json", "augint_sample.json"),
                   ("prep_process_graph.py", "prep_process_graph.py"),
                   ("prep_augint_sample.py", "prep_augint_sample.py")]:
    shutil.copyfile(SRC / name, SEG / dest)
    print("copied", dest)

g = SEG / "gitvisual.py"
# run-line names follow the production filename
sub(g, "Run: $MSF_PYTHON gitvisual7.py --still 12.0 --out stills7/test.png\n     $MSF_PYTHON gitvisual7.py --out gitvisual7.mp4",
    "Run: $MSF_PYTHON gitvisual.py --still 12.0 --out stills7/test.png\n     $MSF_PYTHON gitvisual.py --out gitvisual7.mp4",
    label="docstring run lines")
sub(g, "# v6 scratch copy: production lives at muse-softfloat/video/segments/\n# (ROOT=HERE.parent.parent there); the scratch copy sits two levels\n# below the workspace root, so resolve whichever layout is present.",
    "# production layout: ROOT = muse-softfloat/ (HERE.parent.parent);\n# the scratch study copy sat two levels below the workspace root,\n# so resolve whichever layout is present (kept for study reuse).",
    label="layout comment")
# owner cut 1: chase bottom-left phase strip entirely
sub(g, """            d.rounded_rectangle([px(36), H - px(76), px(1100), H - px(24)], px(12), fill=(255, 255, 255, 215))
            text(d, (px(52), H - px(64)), f"1 - THE CHASE  |  {ph}",
                 "mono_reg", 23, (110, 118, 145))
""", "", label="chase bottom-left phase strip removed (owner)")
# owner cut 2: flyby top-left titles; counters move up
sub(g, """        text(d, (px(48), px(42)), title, "black", 42, ink)
        text(d, (px(48), px(96)),""",
    """        text(d, (px(48), px(42)),""", label="flyby title removed, counters up (owner)")
# owner cut 3: opening title; its two content lines move up
sub(g, """    text(d, (px(48), px(42)), "3 - KEPT", "black", 44, S.INK)
    text(d, (px(48), px(98)), "every system drops in, kept", "mono", 24, S.CYAN)
    text(d, (px(48), px(136)), f"marbles in: {n_in} / 7", "mono", 21, S.DIM)""",
    """    text(d, (px(48), px(42)), "every system drops in, kept", "mono", 24, S.CYAN)
    text(d, (px(48), px(80)), f"marbles in: {n_in} / 7", "mono", 21, S.DIM)""",
    label="opening title removed (owner)")

a = WS / "muse-softfloat/video/assemble.py"
sub(a, '"""Assemble the segment-based cut (v5) at 2560x1440.',
    '"""Assemble the segment-based cut (v6) at 2560x1440, 124 BPM.',
    label="assemble docstring v6")
sub(a, "concatenates intro -> idea -> why -> gitvisual -> outro into\nmuse-softfloat/video/out/assembly_v5.mp4 and pixel-checks the joins.",
    "concatenates intro -> idea -> why -> gitvisual -> outro into\nmuse-softfloat/video/out/assembly_v6.mp4 and pixel-checks the joins.\nThe concatenation is tempo-scaled by 120/124: every segment\nlength is a whole number of 120 BPM beats, so after scaling\nevery cut lands exactly on a 124 BPM beat (music sync;\n169.0 s -> 163.5 s, a uniform 3.3% motion speedup).",
    label="assemble tempo note")
sub(a, '("gitvisual.py", "gitvisual5.mp4", 102.0),',
    '("gitvisual.py", "gitvisual7.mp4", 102.0),  # v7 process-graph renderer',
    label="assemble segment name")
sub(a, 'ORDER = ["intro3.mp4", "idea2-1440p.mp4", "why3-1440p.mp4",\n         "gitvisual5.mp4", "outro3.mp4"]',
    'ORDER = ["intro3.mp4", "idea2-1440p.mp4", "why3-1440p.mp4",\n         "gitvisual7.mp4", "outro3.mp4"]',
    label="assemble order")
sub(a, 'cmd += ["--out", str(SEG / "gitvisual5.mp4")]',
    'cmd += ["--out", str(SEG / "gitvisual7.mp4")]',
    label="assemble render out")
sub(a, '''    fc = ";".join(filters) + ";" + "".join(f"[v{i}]" for i in range(len(ORDER))) \\
        + f"concat=n={len(ORDER)}:v=1:a=0[v]"
    out = OUT / "assembly_v5.mp4"''',
    '''    tempo = 120.0 / 124.0  # native 120 BPM grid -> 124 BPM music sync
    fc = ";".join(filters) + ";" + "".join(f"[v{i}]" for i in range(len(ORDER))) \\
        + f"concat=n={len(ORDER)}:v=1:a=0[vc];[vc]setpts=PTS*{tempo:.10f},fps=30[v]"
    out = OUT / "assembly_v6.mp4"''', label="assemble tempo filter")
sub(a, "    for name in ORDER[:-1]:\n        t += durs[name]\n        bounds.append(t)",
    "    for name in ORDER[:-1]:\n        t += durs[name] * (120.0 / 124.0)  # bounds in scaled time\n        bounds.append(t)",
    label="assemble join bounds scaled")

# old rendered segment superseded
old = SEG / "gitvisual5.mp4"
if old.exists():
    old.unlink()
    print("removed segments/gitvisual5.mp4 (superseded; assembly_v5.mp4 keeps the cut)")

if fails:
    print("FAILURES:")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("integrate_v7 OK")
