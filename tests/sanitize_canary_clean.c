/* Sanitizer canary: clean control. Must exit 0 under every
   flavour - proves a trap/report from the other canaries is the
   deliberate violation, not broken instrumentation. */
#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    char *p = (char *)malloc(8);
    if (!p) return 2;
    p[0] = (char)argc;
    p[7] = 'x';
    printf("CLEAN-OK %d %c %s\n", (int)p[0], p[7], argv[0] ? "argv" : "null");
    free(p);
    return 0;
}
