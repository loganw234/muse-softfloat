/* strdiff.c - line driver for msf64 character conversions (te mode).
 * D <str>            -> bits flags consumed
 * H <str>            -> bits flags consumed
 * T <hexbits> <prec> -> OUT|flags|len   (scientific style)
 * X <hexbits>        -> OUT|flags|len   (exact hex) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "muse_softfloat.h"
int main(void){
    static char line[8192], buf[4096];
    while (fgets(line, sizeof line, stdin)) {
        size_t L = strlen(line); while (L && (line[L-1]=='\n' || line[L-1]=='\r')) line[--L] = 0;
        if (L < 2) continue;
        msf_flags_t f = 0; size_t consumed = 0;
        if (line[0] == 'D') { msf64_t r = msf64_from_decimal(line+2, &consumed, MSF_ROUND_TIES_TO_EVEN, &f); printf("%016llx %02x %zu\n", (unsigned long long)r, (unsigned)f, consumed); }
        else if (line[0] == 'H') { msf64_t r = msf64_from_hex(line+2, &consumed, MSF_ROUND_TIES_TO_EVEN, &f); printf("%016llx %02x %zu\n", (unsigned long long)r, (unsigned)f, consumed); }
        else if (line[0] == 'T') { unsigned long long a; int p; if (sscanf(line+2, "%llx %d", &a, &p) != 2) { puts("ERR"); continue; }
            msf_decimal_spec_t spec = { p, MSF_DECIMAL_STYLE_SCIENTIFIC, 0 }; size_t n = msf64_to_decimal((msf64_t)a, &spec, buf, sizeof buf, MSF_ROUND_TIES_TO_EVEN, &f); printf("%s|%02x|%zu\n", buf, (unsigned)f, n); }
        else if (line[0] == 'X') { unsigned long long a; if (sscanf(line+2, "%llx", &a) != 1) { puts("ERR"); continue; }
            msf_hex_spec_t spec = { -1 }; size_t n = msf64_to_hex((msf64_t)a, &spec, buf, sizeof buf, MSF_ROUND_TIES_TO_EVEN, &f); printf("%s|%02x|%zu\n", buf, (unsigned)f, n); }
        else puts("ERR");
        fflush(stdout);
    }
    return 0;
}
