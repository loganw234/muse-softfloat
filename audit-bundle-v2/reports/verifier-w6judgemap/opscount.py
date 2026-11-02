import json, sys
ops = json.load(open(sys.argv[1], encoding='utf-8'))
run = sum(1 for o in ops if o.get('runnable'))
print('ops=%d runnable=%d nonrunnable=%d' % (len(ops), run, len(ops) - run))
rm = sum(1 for o in ops if o.get('rm'))
print('attribute-carrying(rm)=%d' % rm)
