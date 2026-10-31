/* mathdiff.c - line driver: "<fmt> <op> <rm> <a> [<b>]" -> "<hex> <flags>" */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "muse_softfloat.h"
int main(void){
    static char line[512]; char op[32]; int fmt, rm; unsigned long long a, b;
    while (fgets(line, sizeof line, stdin)) {
        int n = sscanf(line, "%d %31s %d %llx %llx", &fmt, op, &rm, &a, &b);
        if (n < 4) { puts("ERR"); continue; }
        msf_flags_t f = 0; unsigned long long r = 0;
        if (fmt == 64) {
            if (!strcmp(op,"sinpi")) r = msf64_sin_pi((msf64_t)a, rm, &f);
            else if (!strcmp(op,"cospi")) r = msf64_cos_pi((msf64_t)a, rm, &f);
            else if (!strcmp(op,"rsqrt")) r = msf64_r_sqrt((msf64_t)a, rm, &f);
            else if (!strcmp(op,"hypot")) r = msf64_hypot((msf64_t)a, (msf64_t)b, rm, &f);
            else if (!strcmp(op,"exp2")) r = msf64_exp2((msf64_t)a, rm, &f);
            else if (!strcmp(op,"exp2m1")) r = msf64_exp2m1((msf64_t)a, rm, &f);
            else if (!strcmp(op,"log2")) r = msf64_log2((msf64_t)a, rm, &f);
            else if (!strcmp(op,"log2p1")) r = msf64_log2p1((msf64_t)a, rm, &f);
            else { puts("ERR"); continue; }
        } else if (fmt == 32) {
            if (!strcmp(op,"sinpi")) r = msf32_sin_pi((msf32_t)a, rm, &f);
            else if (!strcmp(op,"cospi")) r = msf32_cos_pi((msf32_t)a, rm, &f);
            else if (!strcmp(op,"rsqrt")) r = msf32_r_sqrt((msf32_t)a, rm, &f);
            else if (!strcmp(op,"hypot")) r = msf32_hypot((msf32_t)a, (msf32_t)b, rm, &f);
            else if (!strcmp(op,"exp2")) r = msf32_exp2((msf32_t)a, rm, &f);
            else if (!strcmp(op,"exp2m1")) r = msf32_exp2m1((msf32_t)a, rm, &f);
            else if (!strcmp(op,"log2")) r = msf32_log2((msf32_t)a, rm, &f);
            else if (!strcmp(op,"log2p1")) r = msf32_log2p1((msf32_t)a, rm, &f);
            else { puts("ERR"); continue; }
        } else {
            if (!strcmp(op,"sinpi")) r = msf16_sin_pi((msf16_t)a, rm, &f);
            else if (!strcmp(op,"cospi")) r = msf16_cos_pi((msf16_t)a, rm, &f);
            else if (!strcmp(op,"rsqrt")) r = msf16_r_sqrt((msf16_t)a, rm, &f);
            else if (!strcmp(op,"hypot")) r = msf16_hypot((msf16_t)a, (msf16_t)b, rm, &f);
            else if (!strcmp(op,"exp2")) r = msf16_exp2((msf16_t)a, rm, &f);
            else if (!strcmp(op,"exp2m1")) r = msf16_exp2m1((msf16_t)a, rm, &f);
            else if (!strcmp(op,"log2")) r = msf16_log2((msf16_t)a, rm, &f);
            else if (!strcmp(op,"log2p1")) r = msf16_log2p1((msf16_t)a, rm, &f);
            else { puts("ERR"); continue; }
        }
        printf("%llx %02x\n", r, (unsigned)f);
    }
    return 0;
}
