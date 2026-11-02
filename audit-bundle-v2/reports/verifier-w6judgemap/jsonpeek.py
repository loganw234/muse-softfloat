import json, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
def walk(o, depth=0):
    if isinstance(o, dict):
        print('dict keys: %s' % list(o.keys())[:12])
        for k in list(o.keys())[:6]:
            print('key %r type %s' % (k, type(o[k]).__name__))
        return
    if isinstance(o, list):
        print('list len=%d first=%r' % (len(o), o[0] if o else None))
        return
    print(type(o).__name__, repr(o)[:200])
walk(d)
