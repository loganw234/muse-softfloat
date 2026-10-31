/* f16exh.c - exhaustive binary16 x binary16 differential (all 2^32 ordered
 * pairs) for msf16_add / msf16_mul / msf16_div in a chosen mode, against
 * x86 hardware via the exact/round-to-odd double path. Threads split the
 * first operand. NaN results compared by the project rule (first sNaN,
 * else first NaN, quieted; default NaN for invalid). Scratch audit code. */
#define _GNU_SOURCE
#include "hwcore.h"
#include <pthread.h>

static int OP, MODE, NT;
static long long mism[16], checked[16];
static uint32_t firstbad[16][3];

static void *work(void *arg) {
    int t = (int)(intptr_t)arg;
    long long mm = 0, ck = 0;
    for (uint32_t a = (uint32_t)t; a < 65536; a += (uint32_t)NT) {
        int an = b_isnan(&FM16, a);
        double x = h2d(a);
        for (uint32_t b = 0; b < 65536; b++) {
            msf_flags_t fl = 0; uint64_t got;
            if (OP == 0) got = msf16_add((msf16_t)a, (msf16_t)b, (msf_rounding_t)MODE, &fl);
            else if (OP == 1) got = msf16_mul((msf16_t)a, (msf16_t)b, (msf_rounding_t)MODE, &fl);
            else got = msf16_div((msf16_t)a, (msf16_t)b, (msf_rounding_t)MODE, &fl);
            uint64_t exp; uint32_t efl;
            int bn = b_isnan(&FM16, b);
            if (an || bn) {
                int s = b_issnan(&FM16, a) || b_issnan(&FM16, b);
                uint64_t pick = b_issnan(&FM16, a) ? a : b_issnan(&FM16, b) ? b : an ? a : b;
                exp = b_nanconv(&FM16, &FM16, pick); efl = s ? MSF_FLAG_INVALID : 0;
            } else {
                double y = h2d(b), r; uint32_t f1;
                hw_begin(1);
                r = OP == 0 ? hadd(x, y) : OP == 1 ? hmul(x, y) : hdiv(x, y);
                f1 = hw_end();
                if (r == 0 && !(f1 & MSF_FLAG_INEXACT)) { hw_begin(MODE == 4 ? 0 : MODE); r = OP == 0 ? hadd(x, y) : OP == 1 ? hmul(x, y) : hdiv(x, y); f1 = hw_end(); }
                if (isnan(r)) { exp = b_defnan(&FM16); efl = f1 & MSF_FLAG_INVALID; }
                else { uint32_t f2; exp = round_from_double(odd(r, f1), 16, MODE, &f2); efl = (f1 & (MSF_FLAG_INVALID | MSF_FLAG_DIVISION_BY_ZERO)) | f2; }
            }
            ck++;
            if (got != exp || fl != efl) { if (mm == 0) { firstbad[t][0] = a; firstbad[t][1] = b; firstbad[t][2] = (uint32_t)got; } mm++; }
        }
    }
    mism[t] = mm; checked[t] = ck;
    return 0;
}
int main(int argc, char **argv) {
    OP = atoi(argv[1]); MODE = atoi(argv[2]); NT = argc > 3 ? atoi(argv[3]) : 3;
    pthread_t th[16];
    for (int t = 0; t < NT; t++) pthread_create(&th[t], 0, work, (void *)(intptr_t)t);
    long long M = 0, C = 0;
    for (int t = 0; t < NT; t++) { pthread_join(th[t], 0); M += mism[t]; C += checked[t]; if (mism[t]) printf("  thread %d first mismatch a=%04x b=%04x got=%04x\n", t, firstbad[t][0], firstbad[t][1], firstbad[t][2]); }
    printf("f16 exhaustive %s mode=%s: checked=%lld mismatches=%lld\n", OP == 0 ? "add" : OP == 1 ? "mul" : "div", MN[MODE], C, M);
    return M != 0;
}
