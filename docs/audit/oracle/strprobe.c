#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "muse_softfloat.h"
static void dec(const char *label, const char *s) {
    for (int m = 0; m < 5; m++) {
        msf_flags_t f = 0; size_t c = 0;
        unsigned long long r = msf64_from_decimal(s, &c, (msf_rounding_t)m, &f);
        printf("%-34s rm=%d -> %016llx flags=%02x consumed=%zu\n", label, m, r, f, c);
    }
}
int main(void) {
    dec("exact 0.1 expansion (55 digits)", "0.1000000000000000055511151231257827021181583404541015625");
    dec("above RNE overflow threshold", "1.79769313486231580793729e308");
    /* F2: exponent clamp + long digit string */
    size_t n = 150000;
    char *s = malloc(n + 20); s[0] = '1'; memset(s + 1, '0', n); strcpy(s + 1 + n, "e-150000");
    msf_flags_t f = 0; size_t c = 0;
    unsigned long long r = msf64_from_decimal(s, &c, MSF_ROUND_TIES_TO_EVEN, &f);
    printf("\"1\"+150000 zeros+\"e-150000\" (value 1.0) -> %016llx flags=%02x consumed=%zu of %zu\n", r, f, c, strlen(s));
    char *t = malloc(n + 20); t[0] = '1'; memset(t + 1, '0', 100000); strcpy(t + 100001, "e-100000");
    f = 0; r = msf64_from_decimal(t, &c, MSF_ROUND_TIES_TO_EVEN, &f);
    printf("\"1\"+100000 zeros+\"e-100000\" (value 1.0) -> %016llx flags=%02x\n", r, f);
    free(s); free(t);
    return 0;
}
