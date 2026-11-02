import csv, sys
root = sys.argv[1]
lines = [l for l in open(root + '/docs/COVERAGE.tsv', encoding='utf-8') if not l.startswith('#')]
import io
rows = list(csv.DictReader(io.StringIO(''.join(lines)), delimiter='\t'))
print('cover_data_rows=%d' % len(rows))
print('cols=' + ','.join(rows[0].keys()))
impl = sum(1 for r in rows if r.get('status') == 'implemented')
print('implemented=%d' % impl)
import collections
print(collections.Counter(r.get('status') for r in rows))
print(collections.Counter(r.get('tier') for r in rows if 'tier' in r))
