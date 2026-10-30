/* Sanitizer canary: deliberate signed-integer-overflow UB.
   argc keeps it runtime so the compiler cannot fold it away.
   Must trap (trap flavour) or report+halt (full flavour). */
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    (void)argv;
    volatile int x = INT_MAX;
    int y = x + argc;
    printf("UB-RESULT %d (printed = NOT caught)\n", y);
    return 0;
}
