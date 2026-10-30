/* Sanitizer canary: deliberate overshift UB (run with 40).
   Must trap (trap flavour) or report+halt (full flavour). */
#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    int sh = (argc > 1) ? atoi(argv[1]) : 40;
    volatile unsigned int v = 1u;
    unsigned int y = v << sh;
    printf("UBSHIFT-RESULT %u (printed = NOT caught)\n", y);
    return 0;
}
