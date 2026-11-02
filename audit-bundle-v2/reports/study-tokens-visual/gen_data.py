"""tokens-visual gen_data: derive every visual number from primary sources.

Reads (repo untouched, read-only):
  owner_prompts.json   - 40 owner-typed run/started prompts, lead session
  tree_usage.json      - lead + 241 subagent model_completed sums (aggregate.py)
  muse-softfloat/docs/metrics/usage.jsonl + passes.jsonl (frozen audit inputs)
Writes: data/tokens.json (sole numbers source for render + report).
Estimator: no tokenizer lib in .venv (tiktoken/transformers absent) ->
  tokens ~= chars/4, band +/-30% (words*1.33 cross-check must fall inside).
"""
import json
from datetime import datetime, timezone

S = 'C:/Users/logan/source/repos/Muse-Softfloat/scratch/study-tokens-visual/'
owner = json.load(open(S + 'owner_prompts.json'))
tree = json.load(open(S + 'tree_usage.json'))
U = [json.loads(l) for l in open(
    'C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat/docs/metrics/usage.jsonl')]
P = [json.loads(l) for l in open(
    'C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat/docs/metrics/passes.jsonl')]

oc = sum(len(m['text']) for m in owner)
ow = sum(len(m['text'].split()) for m in owner)
est = oc / 4.0
band = (est * 0.7, est * 1.3)
assert ow * 1.33 > band[0] and ow * 1.33 < band[1], 'word cross-check outside band'

bounds = []
for w in ['wave0', 'wave1', 'wave2', 'wave3']:
    ends = [r['end'] for r in P if r['wave'] == w]
    bounds.append((w, max(ends)))
per_wave_owner = {w: {'msgs': 0, 'chars': 0, 'words': 0} for w in
                  ['wave0', 'wave1', 'wave2', 'wave3', 'post']}
for m in owner:
    ts = datetime.fromtimestamp(m['ts'] / 1e6, tz=timezone.utc).astimezone().isoformat()
    w = 'post'
    for ww, b in bounds:
        if ts <= b:
            w = ww
            break
    a = per_wave_owner[w]
    a['msgs'] += 1
    a['chars'] += len(m['text'])
    a['words'] += len(m['text'].split())

uw = {}
for w in ['wave0', 'wave1', 'wave2', 'wave3']:
    rows = [r for r in U if r['wave'] == w]
    uw[w] = {'in': sum(r['input_tokens'] for r in rows),
             'out': sum(r['output_tokens'] for r in rows),
             'cached': sum(r['cached_tokens'] for r in rows),
             'msgs': sum(r['messages'] for r in rows)}
stale = {k: sum(v[k] for v in uw.values()) for k in ('in', 'out', 'cached', 'msgs')}
spans = {w: {'start': min(r['start'] for r in P if r['wave'] == w),
             'end': max(r['end'] for r in P if r['wave'] == w)} for w in uw}

missing3 = [r for r in U if r.get('note', '').startswith('session 8186e494')
            or r.get('note', '').startswith('session 6473dc2e')
            or r.get('note', '').startswith('session 29d5a20a')]
miss = {'in': sum(r['input_tokens'] for r in missing3),
        'out': sum(r['output_tokens'] for r in missing3),
        'msgs': sum(r['messages'] for r in missing3)}
tin = sum(v for k, v in tree['totals'].items() if k.endswith('|input_tokens'))
tout = sum(v for k, v in tree['totals'].items() if k.endswith('|output_tokens'))
tcached = sum(v for k, v in tree['totals'].items() if k.endswith('|cached_tokens'))
tmsgs = sum(tree['messages'].values())
grand = {'in': tin + miss['in'], 'out': tout + miss['out'],
         'msgs': tmsgs + miss['msgs'], 'cached': tcached}
billed = grand['in'] + grand['out']
ratio = billed / est

def iso(mic):
    return datetime.fromtimestamp(mic / 1e6, tz=timezone.utc).astimezone().isoformat(timespec='seconds')

data = {
    'owner': {'msgs': len(owner), 'chars': oc, 'words': ow,
              'est_tokens': round(est), 'band': [round(band[0]), round(band[1])],
              'per_wave': per_wave_owner,
              'span': [iso(min(m['ts'] for m in owner)), iso(max(m['ts'] for m in owner))]},
    'usage_jsonl_stale': {'rows': len(U), 'per_wave': uw, 'totals': stale,
                          'span': [spans['wave0']['start'], spans['wave3']['end']],
                          'verdict': 'STALE: waves 0-3 only, ends 2026-10-27T11:16:42-07:00; '
                                     'no wave4/wave5/site/video-rework coverage'},
    'tree': {'files': tree['files'], 'with_usage': tree['sessions_with_usage'],
             'zero': tree['sessions_zero'], 'in': tin, 'out': tout,
             'cached': tcached, 'msgs': tmsgs,
             'span': [iso(tree['tmin']), iso(tree['tmax'])]},
    'missing_sessions': {'n': len(missing3), 'in': miss['in'], 'out': miss['out'],
                         'msgs': miss['msgs'],
                         'ids': ['8186e494-fc47-7ef3-84ff-c65e28c6f1ab (verifier-w2xf)',
                                 '6473dc2e-845f-7556-8162-001ea5ff0ef4 (auditor-wave2)',
                                 '29d5a20a-8d33-7152-86e9-a3196570c7aa (auditor-final)'],
                         'note': 'usage rows survive; transcripts absent from disk'},
    'grand': dict(grand, billed=billed,
                  span=[iso(tree['tmin']), iso(tree['tmax'])]),
    'headline': {'owner_est': round(est), 'band': [round(band[0]), round(band[1])],
                 'project_billed': billed,
                 'ratio_1_in_N': round(ratio),
                 'human_share_pct': est / billed * 100,
                 'per_owner_msg': round(billed / len(owner))},
    'definitions': {
        'owner_tokens': 'chars/4 heuristic over 40 owner-typed lead prompts, +/-30%',
        'project_tokens': 'API-billed provider usage from model_completed events: '
                          'input_tokens + output_tokens; cached_tokens is a subset of input '
                          '(prompt-cache reads), NOT additive; reasoning_tokens excluded '
                          'from billed sum, reported separately'},
    'stamp': '2026-10-28 (America/Los_Angeles); repo has no VCS (no git); '
             'session log window ends 2026-10-28 per tree tmax',
}
json.dump(data, open(S + 'data/tokens.json', 'w'), indent=1)
print('owner msgs=%d chars=%d words=%d est=%d band=%s' % (
    len(owner), oc, ow, round(est), [round(band[0]), round(band[1])]))
print('stale usage.jsonl billed=%d span %s -> %s' % (
    stale['in'] + stale['out'], spans['wave0']['start'], spans['wave3']['end']))
print('tree in=%d out=%d msgs=%d span %s -> %s' % (
    tin, tout, tmsgs, iso(tree['tmin']), iso(tree['tmax'])))
print('grand billed=%d ratio 1:%d share=%.5f%%' % (billed, round(ratio), est / billed * 100))
