import io
p = 'scratch/verifier-w2xf/scripts/03_indref.py'
s = io.open(p, encoding='utf-8').read()
s = s.replace('return deliver(dest, d), True', 'return deliver(dest, d, True), True')
s = s.replace('return deliver(dest, d), False', 'return deliver(dest, d, False), False')
s = s.replace('return deliver(dest, A), INV', 'return deliver(dest, A, True), INV')
s = s.replace('return deliver(dest, A), 0', 'return deliver(dest, A, False), 0')
s = s.replace('return deliver(dest, C), INV', 'return deliver(dest, C, True), INV')
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
