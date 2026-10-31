#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "muse_softfloat.h"
/* usage: drv <rm 0..4> < file-with-one-decimal-string-per-line ; prints bits flags consumed/len */
int main(int argc, char **argv){
    int rm = argc > 1 ? atoi(argv[1]) : 0;
    static char buf[1<<20];
    while (fgets(buf, sizeof buf, stdin)) {
        size_t L = strlen(buf); while (L && (buf[L-1]=='\n'||buf[L-1]=='\r')) buf[--L]=0;
        msf_flags_t fl = 0; size_t used = 0;
        msf64_t r = msf64_from_decimal(buf, &used, (msf_rounding_t)rm, &fl);
        printf("bits=%016llx flags=%02x consumed=%zu/%zu\n", (unsigned long long)r, (unsigned)fl, used, L);
    }
    return 0;
}
