import hashlib, os, sys
root = sys.argv[1]
man = open(root + '/audit-bundle/MANIFEST.sha256', encoding='utf-8').read().splitlines()
n = ok = 0
bad = []
for line in man:
    line = line.strip()
    if not line:
        continue
    want, path = line.split(None, 1)
    p = os.path.join(root, 'audit-bundle', path.replace('/', os.sep))
    n += 1
    if not os.path.isfile(p):
        bad.append('MISSING ' + path)
        continue
    got = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    if got == want:
        ok += 1
    else:
        bad.append('HASH-MISMATCH ' + path)
print('entries=%d ok=%d bad=%d' % (n, ok, len(bad)))
for b in bad[:10]:
    print(b)
