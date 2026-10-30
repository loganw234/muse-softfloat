/* Sanitizer canary: deliberate heap-buffer-overflow WRITE past
   an 8-byte malloc whose size is known at the access site.
   Index from argv (run with 64) so it cannot be folded away.
   Caught by the undefined group's object-size check (trap
   flavour) and by AddressSanitizer (full flavour). */
#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    int idx = (argc > 1) ? atoi(argv[1]) : 64;
    char *p = (char *)malloc(8);
    if (!p) return 2;
    p[idx] = 'X';
    printf("HEAP-WROTE idx=%d (printed = NOT caught)\n", idx);
    free(p);
    return 0;
}
