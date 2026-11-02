"""Fixer timing-equality proof: compare base dump (UTF-16) vs fixer dump (UTF-8)
on decoded lines; first 11 lines must be identical; POPUP5 diff limited to
the two fixed cards."""
from pathlib import Path

D = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w6popups")


def read(name):
    raw = (D / name).read_bytes()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        text = raw.decode("utf-16")
    else:
        text = raw.decode("utf-8-sig")
    return text.replace("\r\n", "\n").splitlines()


base = read("before_timings.txt")
parcel_after = read("after_timings.txt")
fix = read("fix_after_timings.txt")
assert base[:11] == fix[:11], "TIMING MISMATCH:\n%r\n%r" % (base[:11], fix[:11])
print("TIMING_EQUALITY_PASS: first 11 lines identical to base f01dc96")
print("POPUP_WORDS", fix[0])
for i, (a, b) in enumerate(zip(parcel_after, fix)):
    if a != b:
        print("line %d parcel: %s" % (i + 1, a))
        print("line %d fixer : %s" % (i + 1, b))
print("COPY_DIFF_LINES_ABOVE_ONLY (expect POPUP5 card0 + card1)")
