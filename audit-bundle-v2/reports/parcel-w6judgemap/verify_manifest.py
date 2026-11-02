import hashlib, os, sys
bundle = sys.argv[1]
raw = open(os.path.join(bundle, "MANIFEST.sha256"), "rb").read()
print(f"manifest bytes={len(raw)} CRLF={raw.count(b'\r\n'.encode()) if False else raw.count(bytes([13,10]))} LF={raw.count(bytes([10]))}")
ok = bad = missing = 0
badlist = []
for ln in raw.decode("utf-8").splitlines():
    if not ln.strip():
        continue
    want, _, name = ln.partition("  ")
    if not name:
        want, _, name = ln.partition(" ")
    name = name.strip().lstrip("*")
    path = os.path.join(bundle, *name.split("/"))
    if not os.path.exists(path):
        missing += 1; badlist.append(("missing", name)); continue
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    if h.hexdigest() == want.strip():
        ok += 1
    else:
        bad += 1; badlist.append(("mismatch", name))
print(f"entries ok={ok} mismatch={bad} missing={missing}")
for b in badlist[:10]:
    print(b)
