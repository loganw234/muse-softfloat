from pathlib import Path

path = Path("muse-softfloat/docs/metrics/plant_keys.sha256")
before = path.read_bytes()
lines = [l for l in Path("scratch/lead/copy_seal_keylines.txt")
         .read_text(encoding="utf-8").splitlines() if l.strip()]
assert len(lines) == 2
for line in lines:
    assert line.encode() not in before, line
with path.open("ab") as out:
    if not before.endswith(b"\n"):
        out.write(b"\n")
    for line in lines:
        out.write(line.encode() + b"\n")
after = path.read_bytes()
assert after[:len(before)] == before
for line in lines:
    print("appended:", line)
