import re, os, sys

root = sys.argv[1]
text = open(os.path.join(root, 'README.md'), encoding='utf-8').read()
targets = re.findall(r'\[[^\]]*\]\(([^) ]+)\)', text)
rel = sorted(set(t for t in targets if not re.match(r'[a-z]+:', t)))
print('relative link targets: %d' % len(rel))
bad = []
for t in rel:
    p = t.split('#')[0]
    full = os.path.normpath(os.path.join(root, p))
    ok = os.path.exists(full)
    print(('OK   ' if ok else 'MISS ') + t)
    if not ok:
        bad.append(t)
print('missing=%d' % len(bad))
