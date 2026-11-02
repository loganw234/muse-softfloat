import json
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
fails = []


def load(rel):
    p = ROOT / rel
    raw = p.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    return p, raw.replace("\r\n", "\n"), crlf


def save(p, text, crlf):
    if crlf:
        text = text.replace("\n", "\r\n")
    p.write_bytes(text.encode("utf-8"))


def sub(rel, old, new, count=1):
    p, text, crlf = load(rel)
    n = text.count(old)
    if n != count:
        fails.append(f"{rel}: expected {count} of {old[:70]!r}, found {n}")
        return
    save(p, text.replace(old, new), crlf)
    print(f"edit {rel}: {old[:50]!r}")


# README: current video master
sub("README.md", "is a 3-minute programmatic video;",
    "is a 169-second programmatic video;")
sub("README.md",
    "The silent 180-second cut is\n"
    "[video/out/final.mp4](video/out/final.mp4). Its frame-rendering\n"
    "pipeline, data loaders, timelines, and source-traced storyboard live in",
    "The current silent cut is the 169-second, 2560x1440\n"
    "[video/out/assembly_v5.mp4](video/out/assembly_v5.mp4) (the earlier\n"
    "180-second 1080p cut remains at\n"
    "[video/out/final.mp4](video/out/final.mp4)). Its frame-rendering\n"
    "pipeline, data loaders, timelines, and source-traced storyboard live in")

# BOARD: broken link + dated clone note after the details table
sub("docs/BOARD.md", "[docs/TWIDDLES.md](../TWIDDLES.md)",
    "[docs/TWIDDLES.md](TWIDDLES.md)")
p, text, crlf = load("docs/BOARD.md")
anchor = "| who may hold it besides the lead, if anyone | nobody yet; a parcel may be granted a named slot by the lead, recorded in the ledger |\n"
if text.count(anchor) != 1:
    fails.append("BOARD anchor row not found once")
else:
    note = anchor + (
        "\n**Update (2026-10-28):** five RP2040-Zero clones joined the genuine\n"
        "Pico above - `5303284740c0ac1c`, `5303284740e09a9c`,\n"
        "`5303284718e6579c`, `5303284738b5859c`, `50543165208e249c`. Their\n"
        "activity LED is a PIO-driven WS2812 on GP16 (the Pico uses GP25);\n"
        "see `board/msf_led.h` and the six-board IAS15 entry in\n"
        "[docs/RECORD.md](RECORD.md). The COM8 row above is the genuine\n"
        "board's port on this machine, not a property of the clones.\n")
    save(p, text.replace(anchor, note), crlf)
    print("edit docs/BOARD.md: clone update note")

# src comments: attribute count + design-record paths into the frozen bundle
sub("src/msf_math.c", "all four attributes at binary16/32/64 (SF-1 Step 2c)",
    "all five attributes at binary16/32/64 (SF-1 Step 2c;\n * the fifth, roundTiesToAway, arrived at SF-2 Step 1)")
for rel, cnt in [("src/msf_math.c", 3), ("src/msf_alg.c", 2), ("src/msf_aug.c", 1),
                 ("tools/gen_explog_tables.py", 3)]:
    sub(rel, "ledger/parcel-", "audit-bundle/ledger/parcel-", count=cnt)
sub("src/msf16.c",
    "{binary16, binary32, binary64} grid (ledger design entry,\n * parcel-f16).",
    "{binary16, binary32, binary64} grid (design entry:\n * audit-bundle/ledger/parcel-f16.md).")
sub("src/msf32.c",
    "sources stay inside {binary32, binary64} (ledger design entry,\n * parcel-f32).",
    "sources stay inside {binary32, binary64} (design entry:\n * audit-bundle/ledger/parcel-f32.md).")
sub("src/msf64.c",
    "Wave 1 binary64-destination instantiations (ledger parcel-f64\n * design entry).",
    "Wave 1 binary64-destination instantiations (design entry:\n * audit-bundle/ledger/parcel-f64.md).")

# tools: trig generator design/scratch refs
sub("tools/gen_trig_tables.py",
    "these floors; see ledger/parcel-w4trig.md design entry and\n"
    "scratch/parcel-w4trig/error_budget.py for the budget that",
    "these floors; see audit-bundle/ledger/parcel-w4trig.md\n"
    "(design entry) for the error budget that")
sub("tools/gen_trig_tables.py",
    "    entry; must match scratch/parcel-w4trig/error_budget.py,\n"
    "    checked by the printed values at generation time.\"\"\"",
    "    entry; must match the error budget recorded with that\n"
    "    entry, checked by the printed values at generation\n"
    "    time.\"\"\"")

# tools: decimal semantics frozen (header regenerated from this template)
sub("tools/gen_tables.py",
    " * Exact field semantics are the Wave 3 gate's to freeze. */",
    " * Exact field semantics were frozen at the Wave 3 gate\n"
    " * (docs/RECORD.md, Wave 3 close). */")

# board: flavour-library future that never landed
sub("board/CMakeLists.txt",
    "# Wave 3 registers a full flavour library in this same switch shape.",
    "# (A full flavour library was once planned for this switch shape;\n"
    "# none is registered - Waves 3 and 5 closed without one.)")

# video: run commands after the in-repo move
p, text, crlf = load("video/README.md")
block_old = (
    ".\\.venv\\Scripts\\python.exe video\\inventory.py          # what renders here\n"
    ".\\.venv\\Scripts\\python.exe video\\data.py               # real numbers the charts will show\n"
    ".\\.venv\\Scripts\\python.exe video\\timeline.py           # validate both timelines\n"
    ".\\.venv\\Scripts\\python.exe video\\render.py             # -> video\\out\\proof.mp4\n"
    ".\\.venv\\Scripts\\python.exe video\\render.py --which final --out video\\out\\final.mp4\n"
    ".\\.venv\\Scripts\\python.exe video\\assemble.py           # -> video\\out\\assembly_v5.mp4 (segments + joins)\n"
    ".\\.venv\\Scripts\\python.exe video\\probe.py video\\out\\final.mp4 --stills video\\out\\stills --at 2.5 13.0 34.5 66.0 102.0 108.5 120.0 128.0 141.5 160.0 172.5 178.0\n")
if text.count(block_old) != 1:
    fails.append("video/README render block not found once")
else:
    save(p, text.replace(block_old, block_old.replace("video\\", "muse-softfloat\\video\\")), crlf)
    print("edit video/README.md: render block paths")
sub("video/assemble.py",
    "Segments live in video/segments/ (production copies of the",
    "Segments live in muse-softfloat/video/segments/ (production copies\nof the")
sub("video/assemble.py",
    "video/out/assembly_v5.mp4 and pixel-checks the joins.",
    "muse-softfloat/video/out/assembly_v5.mp4 and pixel-checks the joins.")
sub("video/assemble.py",
    "    .venv\\\\Scripts\\\\python.exe video\\\\assemble.py [--force]",
    "    .venv\\\\Scripts\\\\python.exe muse-softfloat\\\\video\\\\assemble.py [--force]")
sub("video/probe.py",
    "Usage: ..\\\\.venv\\\\Scripts\\\\python.exe probe.py",
    "Usage: ..\\\\..\\\\.venv\\\\Scripts\\\\python.exe probe.py")
sub("video/STORYBOARD.md", "`..\\.venv\\Scripts\\python.exe",
    "`..\\..\\.venv\\Scripts\\python.exe", count=2)
sub("video/segments/idea.py", "Run: $MSF_PYTHON render_idea2.py",
    "Run: $MSF_PYTHON idea.py")
sub("video/segments/why.py", "Run: $MSF_PYTHON render_why3.py",
    "Run: $MSF_PYTHON why.py")
sub("video/segments/gitvisual.py", "$MSF_PYTHON render_gitvisual5.py",
    "$MSF_PYTHON gitvisual.py", count=2)
sub("video/segments/intro_outro.py", "Run: $MSF_PYTHON render_v3.py",
    "Run: $MSF_PYTHON intro_outro.py")

# briefs.jsonl: own row
p, text, crlf = load("docs/metrics/briefs.jsonl")
row = {
    "wave": "polish",
    "work": "Post-close stale-information cleanup from the Spark audit (site plant figures, README video master, BOARD link/clones, attribute count, path qualifications; frozen audit bundle untouched)",
    "author": "lead-polish1",
    "base": "400b27147518a1b9e704776c6df1f8150681a8e9",
    "time_box_min": 240,
    "ceiling_lines": 0,
    "ceiling_text": "brief ledger/briefs/polish-stale1.md owned-files list is the bound; regenerated site data/header excluded",
}
if "lead-polish1" in text:
    fails.append("briefs row already present")
else:
    if not text.endswith("\n"):
        text += "\n"
    save(p, text + json.dumps(row) + "\n", crlf)
    print("edit docs/metrics/briefs.jsonl: own row")

# RECORD: append-only erratum
p, text, crlf = load("docs/RECORD.md")
appendix = (
    "\n**Post-close polish erratum (appended 2026-10-29):**\n"
    "the Wave 5 close entries above say the metrics\n"
    "refresh took `briefs 27->30`, and an earlier entry\n"
    "left the Step 3a briefs row owed to the close.\n"
    "Both were overtaken inside the same close:\n"
    "`498a916` landed the Step 3a row (parcel-w5exp2),\n"
    "so briefs stood at 31 rows at the close, not 30,\n"
    "and nothing remained owed. The earlier lines stand\n"
    "as written; this appendix is the current reading.\n"
    "A Spark stale-information audit the same day\n"
    "(frozen audit bundle excluded) drove the\n"
    "polish-stale1 cleanup recorded with that parcel.\n")
if "Post-close polish erratum" in text:
    fails.append("RECORD appendix already present")
else:
    if not text.endswith("\n"):
        text += "\n"
    save(p, text + appendix, crlf)
    print("edit docs/RECORD.md: polish erratum appendix")

if fails:
    print("FAILURES:")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("apply_polish1 OK")
