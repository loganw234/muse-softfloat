"""Check line endings of the two report files (read-only)."""
from pathlib import Path

for name in ["scratch/parcel-w6popups/report.md", "ledger/parcel-w6popups.md"]:
    raw = Path(r"C:\Users\logan\source\repos\Muse-Softfloat") .joinpath(*name.split("/")).read_bytes()
    lines = raw.split(b"\n")
    crlf = sum(1 for l in lines[:-1] if l.endswith(b"\r"))
    print(name, "lines:", len(lines) - 1, "crlf:", crlf, "lf-only:", len(lines) - 1 - crlf)
