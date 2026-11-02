from pathlib import Path

path = Path("muse-softfloat/docs/metrics/plant_keys.sha256")
before = path.read_bytes()
line = Path("scratch/lead/copy_w6popups_keyline.txt").read_text(encoding="utf-8").strip()
assert line.encode() not in before
with path.open("ab") as out:
    if not before.endswith(b"\n"):
        out.write(b"\n")
    out.write(line.encode() + b"\n")
after = path.read_bytes()
assert after[:len(before)] == before
print("appended:", line)
