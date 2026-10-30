/* Sanitizer canary: heap overflow through a separate function
   that only sees a bare char* - object size unknown at the
   write site. This is the trap flavour's proven blind spot
   (study-w6sanitize Sec. 1.2): expected NOT caught under trap,
   must be caught under full (AddressSanitizer redzones). */
#include <stdio.h>
#include <stdlib.h>
#if defined(__GNUC__)
__attribute__((noinline))
#endif
static void poke(char *p, int idx) { p[idx] = 'Z'; }
int main(int argc, char **argv) {
    size_t n = (argc > 1) ? (size_t)atoi(argv[1]) : 8u;
    int idx = (argc > 2) ? atoi(argv[2]) : 64;
    char *p = (char *)malloc(n);
    if (!p) return 2;
    poke(p, idx);
    printf("HEAPFAR-WROTE n=%u idx=%d (printed = NOT caught)\n", (unsigned)n, idx);
    free(p);
    return 0;
}
