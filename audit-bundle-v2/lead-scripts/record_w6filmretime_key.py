from pathlib import Path

path = Path("muse-softfloat/docs/metrics/plant_keys.sha256")
before = path.read_bytes()
line = Path("scratch/lead/copy_w6filmretime_keyline.txt").read_text(encoding="utf-8").strip()
assert line.encode() not in before
nl = b"\r\n" if b"\r\n" in before[-200:] else b"\n"
with path.open("ab") as out:
    if not before.endswith((b"\n",)):
        out.write(nl)
    out.write(line.encode() + nl)
after = path.read_bytes()
assert after[:len(before)] == before
print("appended:", line)
print("eol style:", nl)
print("lines now:", after.count(b"\n"))
