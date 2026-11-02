import json, sys
rows = [json.loads(l) for l in open(sys.argv[1], encoding='utf-8') if l.strip()]
print('rows=%d caught=%d' % (len(rows), sum(1 for r in rows if r.get('grade') == 'caught')))
