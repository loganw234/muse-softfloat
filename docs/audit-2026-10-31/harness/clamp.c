#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "muse_softfloat.h"
static void t(const char *label, const char *s, int hex){ msf_flags_t f=0; size_t c=0; unsigned long long r = hex ? msf64_from_hex(s,&c,MSF_ROUND_TIES_TO_EVEN,&f) : msf64_from_decimal(s,&c,MSF_ROUND_TIES_TO_EVEN,&f); printf("%-32s -> %016llx flags=%02x consumed=%zu of %zu\n", label, r, (unsigned)f, c, strlen(s)); }
int main(void){
    char *s = malloc(300000); 
    sprintf(s, "1"); memset(s+1,'0',100001); sprintf(s+100002, "e-100001"); t("1+0*100001 e-100001 (=1.0)", s, 0);
    sprintf(s, "1"); memset(s+1,'0',100002); sprintf(s+100003, "e-100002"); t("1+0*100002 e-100002 (=1.0)", s, 0);
    sprintf(s, "1"); memset(s+1,'0',200000); sprintf(s+200001, "e-200000"); t("1+0*200000 e-200000 (=1.0)", s, 0);
    sprintf(s, "0x1"); memset(s+3,'0',25001); sprintf(s+25004, "p-100004"); t("0x1+0*25001 p-100004 (=1.0)", s, 1);
    t("9007199254740993.0000001 (>H)", "9007199254740993.0000001", 0);
    t("1e99999999999999999999", "1e99999999999999999999", 0);
    return 0; }
