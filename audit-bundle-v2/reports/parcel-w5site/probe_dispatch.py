import re, collections, glob
t = open(r'C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w5-site\tests\msf_dispatch.h').read()
i = t.find('static const msf_op_desc_t MSF_OPS[]')
j = t.find('};', i)
body = t[i:j]
rows = re.findall(r'\{\s*"([^"]+)",\s*"([^"]+)",\s*(MSF_SIG_\w+),\s*(MSF_RK_\w+),\s*\{\s*(MSF_AK_\w+),\s*(MSF_AK_\w+),\s*(MSF_AK_\w+)\s*\},\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\w+)\s*\}', body)
print('ops parsed', len(rows))
print(collections.Counter(r[2] for r in rows))
print('null calls', sum(1 for r in rows if r[11] == 'NULL'))
print('retkinds', collections.Counter(r[3] for r in rows))
print('argkinds', collections.Counter(k for r in rows for k in r[4:7] if k != 'MSF_AK_NONE'))
# vector compare directives + result quirks
cmp_modes = collections.Counter()
for f in glob.glob(r'C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w5-site\tests\vectors\*.vec'):
    for line in open(f, errors='ignore'):
        if line.startswith('# compare='):
            cmp_modes[(f.split('\\')[-1], line.strip())] += 1
print(cmp_modes)
# how many vector lines reference ops with NULL call or char sigs
byname = {r[0]: r for r in rows}
missing = collections.Counter()
tilde = 0
for f in glob.glob(r'C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w5-site\tests\vectors\*.vec'):
    for line in open(f, errors='ignore'):
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        op = s.split()[0]
        if '~' in s:
            tilde += 1
        if op.startswith('internal.'):
            continue
        if op not in byname:
            missing[op] += 1
print('ops in vectors not in dispatch:', dict(list(missing.items())[:20]), 'tilde lines', tilde)
