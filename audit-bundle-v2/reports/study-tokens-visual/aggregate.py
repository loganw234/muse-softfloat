"""Regeneration step (production refresh): re-sum provider usage across the
lead session tree. Read-only over session logs; writes tree_usage.json.
Usage: MSF_PYTHON=.venv/Scripts/python.exe scratch/study-tokens-visual/aggregate.py
(streaming; ~570 MB across 242 files; run when idle, not beside a parcel sweep).
Method mirrors muse-softfloat/tools/extract_session_metrics.py: only
payload.event.kind == model_completed usage dicts count; per-file exact
duplicates (timestamp, model, duration, usage) counted once.
"""
import json, os, re, collections

S = 'C:/Users/logan/.local/share/muse/sessions/2026/10/26'
LEAD = '01a17907-4147-7333-a565-56071da9d971'
FIELDS = ('input_tokens', 'output_tokens', 'cached_tokens',
          'cache_write_tokens', 'cache_read_tokens', 'reasoning_tokens')

def scan(path):
    usage = collections.Counter()
    msgs = collections.Counter()
    seen = set()
    tmin = tmax = None
    n_mc = 0
    with open(path, encoding='utf-8', errors='replace') as fh:
        for line in fh:
            s = line.strip()
            if not s:
                continue
            try:
                d = json.loads(s)
            except Exception:
                continue
            ts = d.get('recorded_at')
            if isinstance(ts, int):
                tmin = ts if tmin is None or ts < tmin else tmin
                tmax = ts if tmax is None or ts > tmax else tmax
            pay = d.get('payload')
            if not isinstance(pay, dict):
                continue
            ev = pay.get('event')
            if not isinstance(ev, dict):
                continue
            if ev.get('kind') != 'model_completed':
                continue
            u = ev.get('usage')
            model = ev.get('model')
            if not isinstance(u, dict) or not isinstance(model, str):
                continue
            key = (ts, model, ev.get('duration_ms')) + tuple(u.get(f) for f in FIELDS)
            if key in seen:
                continue
            seen.add(key)
            n_mc += 1
            for f_ in FIELDS:
                v = u.get(f_, 0)
                if isinstance(v, int) and v >= 0:
                    usage[(model, f_)] += v
            msgs[model] += 1
    return usage, msgs, n_mc, tmin, tmax

TU = collections.Counter()
TM = collections.Counter()
tmin = tmax = None
n_with = n_zero = 0
files = [(S + '/' + LEAD + '/session.jsonl')]
sub = os.path.join(S, LEAD, 'subagent')
for n in sorted(os.listdir(sub)):
    f = os.path.join(sub, n, 'session.jsonl')
    if os.path.isfile(f):
        files.append(f)
for path in files:
    u, m, n_mc, a, b = scan(path)
    if n_mc:
        n_with += 1
    else:
        n_zero += 1
    for k, v in u.items():
        TU[k] += v
    for k, v in m.items():
        TM[k] += v
    if a is not None:
        tmin = a if tmin is None or a < tmin else tmin
        tmax = b if tmax is None or b > tmax else tmax
out = {'totals': {'%s|%s' % k: v for k, v in TU.items()},
       'messages': dict(TM), 'tmin': tmin, 'tmax': tmax,
       'sessions_with_usage': n_with, 'sessions_zero': n_zero, 'files': len(files)}
json.dump(out, open('C:/Users/logan/source/repos/Muse-Softfloat/scratch/study-tokens-visual/tree_usage.json', 'w'))
print('files=%d with_usage=%d zero=%d' % (len(files), n_with, n_zero))
for (model, f_) in sorted(TU):
    print('TREE', model, f_, TU[(model, f_)])
