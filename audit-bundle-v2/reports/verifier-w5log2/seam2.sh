#!/usr/bin/env bash
# seam2.sh - tier counts from generated COVERAGE + wave usage.
set -u
COPY=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify5-log2
cd "$COPY" || exit 9
echo "=== tier2 totals (generated COVERAGE.tsv) ==="
awk -F'\t' 'BEGIN{t2=0;i2=0;p2=0} /^#/||NF<3{next} $1=="tier"&&$2=="status"{next} {t2++; if($0~/implemented/){i2++} if($0~/planned/){p2++}} END{print "lines="t2" implemented~"i2" planned~"p2}' docs/COVERAGE.tsv
echo "=== exact tier2 field counts ==="
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
"$PY" -c "
import csv
t2=i2=p2=0; bad=[]
with open('docs/COVERAGE.tsv') as fh:
    r=csv.DictReader(filter(lambda l: not l.startswith('#'), fh), delimiter='\t')
    print('columns:', r.fieldnames)
    for row in r:
        if row['tier']=='2':
            t2+=1
            if row['status']=='implemented': i2+=1
            elif row['status']=='planned': p2+=1
            else: bad.append(row['name'])
print('tier2 total=%d implemented=%d planned=%d bad=%s' % (t2,i2,p2,bad))
"
echo "=== wave column usage in gen_tables.py ==="
grep -n 'wave' tools/gen_tables.py | head -20
echo "=== git diff parent stat ==="
git diff 54ac1bb --stat | tail -25
