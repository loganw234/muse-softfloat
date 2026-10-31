import sys; sys.path.insert(0, 'harness')
from msf import *
# exponent clamp (EXP_CLAMP=100000) interaction with very long mantissas
def show(name, s, want):
    for w in (64,):
        b, fl, c = from_decimal(w, s, 0)
        print('%-52s bits=%016x flags=%02x consumed=%d  want=%016x %s' % (name, b, fl, c, want, 'OK' if b == want else '*** MISMATCH ***'))
ONE = 0x3FF0000000000000
show('1 + 100001 zeros, e-100001  (=1)', '1' + '0'*100001 + 'e-100001', ONE)
show('1 + 100001 zeros, e-100002  (=0.1)', '1' + '0'*100001 + 'e-100002', 0x3FB999999999999A)
show('1 + 200000 zeros, e-200000  (=1)', '1' + '0'*200000 + 'e-200000', ONE)
show('1 + 1000 zeros, e-1000 (control, =1)', '1' + '0'*1000 + 'e-1000', ONE)
show('0.(200000 zeros)1 e200001 (=1)', '0.' + '0'*200000 + '1e200001', ONE)
show('0.(100000 zeros)1 e100001 (=1)', '0.' + '0'*100000 + '1e100001', ONE)
show('0.(99998 zeros)1 e99999 (=1) control', '0.' + '0'*99998 + '1e99999', ONE)
show('0.(300000 zeros)1 e300001 (=1)', '0.' + '0'*300000 + '1e300001', ONE)
show('1 + 300000 zeros e-300000 (=1)', '1' + '0'*300000 + 'e-300000', ONE)
# hex analogue: exponent clamp 100000 vs 4*frac digits
def showh(name, s, want):
    b, fl, c = from_hex(64, s, 0)
    print('%-52s bits=%016x flags=%02x consumed=%d  want=%016x %s' % (name, b, fl, c, want, 'OK' if b == want else '*** MISMATCH ***'))
showh('0x0.(30000 zeros)1p120004 (=1)', '0x0.' + '0'*30000 + '1p120004', ONE)
showh('0x0.(24990 zeros)1p99964 (=1) control', '0x0.' + '0'*24990 + '1p99964', ONE)
showh('0x1(30000 zeros)p-120000 (=1)', '0x1' + '0'*30000 + 'p-120000', ONE)
