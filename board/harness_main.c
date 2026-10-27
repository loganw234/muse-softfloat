/* harness_main.c - RP2040 USB CDC vector replay (SF-0 6 item 7).
 *
 * Protocol (board/README.md): the host sends vector lines in the
 * tests/VECTORS.md format; the board executes each implemented
 * operation, replies "R <result-hex> <flags-hex>", and folds a
 * canonical result line into a running SHA-256 that "H" reports.
 * The canonical line is byte-identical to the host runner's hash
 * mode, so host and board digests compare directly.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "../include/muse_softfloat.h"
#include "../src/msf_internal.h"
#include "../tests/msf_dispatch.h"
#include "../tests/sha256.h"

static msf_sha256_t g_hash;
static unsigned long g_count = 0;

static int kind_width(uint8_t kind)
{
    switch (kind) {
    case MSF_AK_F16: case MSF_AK_I16: case MSF_AK_U16: return 16;
    case MSF_AK_F32: case MSF_AK_I32: case MSF_AK_U32: return 32;
    case MSF_AK_I8: case MSF_AK_U8: return 8;
    default: return 64;
    }
}

static const msf_op_desc_t *find_op(const char *name)
{
    size_t i;
    for (i = 0; i < MSF_OP_COUNT; i++) {
        if (strcmp(MSF_OPS[i].name, name) == 0) {
            return &MSF_OPS[i];
        }
    }
    return NULL;
}

static int parse_rm(const char *tok, int *rm)
{
    if (strcmp(tok, "te") == 0) { *rm = MSF_IROUND_TIES_TO_EVEN; return 0; }
    if (strcmp(tok, "tz") == 0) { *rm = MSF_IROUND_TOWARD_ZERO; return 0; }
    if (strcmp(tok, "tp") == 0) { *rm = MSF_IROUND_TOWARD_POSITIVE; return 0; }
    if (strcmp(tok, "tn") == 0) { *rm = MSF_IROUND_TOWARD_NEGATIVE; return 0; }
    if (strcmp(tok, "ta") == 0) { *rm = MSF_IROUND_TIES_TO_AWAY; return 0; }
    if (strcmp(tok, "-") == 0) { *rm = -1; return 0; }
    return -1;
}

static int hex_u128(const char *s, msf_u128_t *out)
{
    msf_u128_t r = msf_u128_from_u64(0u);
    if (strlen(s) > 32u) {
        return -1;
    }
    for (; *s; s++) {
        unsigned v;
        if (*s >= '0' && *s <= '9') { v = (unsigned)(*s - '0'); }
        else if (*s >= 'a' && *s <= 'f') { v = (unsigned)(*s - 'a') + 10u; }
        else if (*s >= 'A' && *s <= 'F') { v = (unsigned)(*s - 'A') + 10u; }
        else { return -1; }
        r = msf_u128_shl(r, 4u);
        r.w[0] |= v;
    }
    *out = r;
    return 0;
}

static void hash_result(const char *opname, const uint64_t *args, int nargs,
                        uint64_t result, uint32_t flags)
{
    char line[256];
    int n = 0, i;
    n += snprintf(line + n, sizeof(line) - (size_t)n, "%s", opname);
    for (i = 0; i < nargs; i++) {
        n += snprintf(line + n, sizeof(line) - (size_t)n, " %016llx",
                      (unsigned long long)args[i]);
    }
    n += snprintf(line + n, sizeof(line) - (size_t)n, " -> %016llx %02x\n",
                  (unsigned long long)result, (unsigned)flags);
    msf_sha256_update(&g_hash, line, (size_t)n);
    g_count++;
}

static void handle_line(char *line)
{
    char *tok[16];
    int ntok = 0;
    char *p;
    for (p = strtok(line, " \t\r\n"); p && ntok < 16; p = strtok(NULL, " \t\r\n")) {
        tok[ntok++] = p;
    }
    if (ntok == 0 || tok[0][0] == '#') {
        return;
    }
    if (strcmp(tok[0], "I") == 0) {
        pico_unique_board_id_t id;
        int i;
        pico_get_unique_board_id(&id);
        printf("MSF-HARNESS 1 ID ");
        for (i = 0; i < PICO_UNIQUE_BOARD_ID_SIZE_BYTES; i++) {
            printf("%02x", id.id[i]);
        }
        printf("\n");
        return;
    }
    if (strcmp(tok[0], "Z") == 0) {
        msf_sha256_init(&g_hash);
        g_count = 0;
        printf("OK reset\n");
        return;
    }
    if (strcmp(tok[0], "H") == 0) {
        msf_sha256_t copy = g_hash;
        uint8_t dig[32];
        int i;
        msf_sha256_final(&copy, dig);
        printf("SHA256 ");
        for (i = 0; i < 32; i++) {
            printf("%02x", dig[i]);
        }
        printf(" COUNT %lu\n", g_count);
        return;
    }
    if (strncmp(tok[0], "internal.pack", 13) == 0) {
        int rm, sign, sticky, fmt;
        long exp2;
        msf_u128_t sig;
        msf_flags_t flags = 0u;
        uint64_t got, args[3];
        fmt = strcmp(tok[0], "internal.pack16") == 0 ? MSF_FMT_F16
            : strcmp(tok[0], "internal.pack32") == 0 ? MSF_FMT_F32 : MSF_FMT_F64;
        if (ntok != 10 || strcmp(tok[6], "->") != 0
            || parse_rm(tok[1], &rm) != 0 || rm < 0 || hex_u128(tok[4], &sig) != 0) {
            printf("E malformed\n");
            return;
        }
        sign = atoi(tok[2]);
        exp2 = atol(tok[3]);
        sticky = atoi(tok[5]);
        got = msf_pack_generic(&MSF_FMT_PARAMS[fmt], sign, (int32_t)exp2, sig,
                               sticky, rm, &flags);
        args[0] = msf_u128_to_u64_trunc(sig);
        args[1] = msf_u128_to_u64_trunc(msf_u128_shr(sig, 64u));
        args[2] = (uint64_t)(uint32_t)exp2;
        hash_result(tok[0], args, 3, got, flags);
        printf("R %016llx %02x\n", (unsigned long long)got, (unsigned)flags);
        return;
    }
    {
        const msf_op_desc_t *op = find_op(tok[0]);
        uint64_t args[3] = {0u, 0u, 0u};
        uint64_t got = 0u;
        msf_flags_t flags = 0u;
        int arrow = -1, i, rm = -2;
        if (op == NULL) { printf("E unknown\n"); return; }
        if (op->status == 0) { printf("E planned\n"); return; }
        for (i = 0; i < ntok; i++) {
            if (strcmp(tok[i], "->") == 0) {
                arrow = i;
            }
        }
        if (arrow != 2 + op->nargs || ntok != 2 + op->nargs + 1 + 3
            || parse_rm(tok[1], &rm) != 0
            || (op->has_rm && rm < 0) || (!op->has_rm && rm != -1)) {
            printf("E malformed\n");
            return;
        }
        for (i = 0; i < op->nargs; i++) {
            args[i] = strtoull(tok[2 + i], NULL, 16);
        }
        if (op->call == NULL) {
            printf("E noshape\n");
            return;
        }
        got = op->call(args, rm, &flags);
        {
            int w = kind_width((uint8_t)op->retkind);
            if (w < 64) {
                got &= (1ULL << w) - 1u;
            }
        }
        hash_result(op->name, args, op->nargs, got, flags);
        printf("R %016llx %02x\n", (unsigned long long)got, (unsigned)flags);
    }
}

int main(void)
{
    char line[512];
    size_t len = 0;
    pico_unique_board_id_t id;
    stdio_init_all();
    while (!stdio_usb_connected()) {
        sleep_ms(50);
    }
    sleep_ms(200);
    pico_get_unique_board_id(&id);
    printf("MSF-HARNESS 1 ID ");
    for (int i = 0; i < PICO_UNIQUE_BOARD_ID_SIZE_BYTES; i++) {
        printf("%02x", id.id[i]);
    }
    printf(" BUILD %s %s\n", __DATE__, __TIME__);
    msf_sha256_init(&g_hash);
    for (;;) {
        int c = getchar_timeout_us(100000);
        if (c == PICO_ERROR_TIMEOUT) {
            continue;
        }
        if (c == '\n' || c == '\r') {
            if (len > 0u) {
                line[len] = '\0';
                handle_line(line);
                len = 0;
            }
        } else if (len < sizeof(line) - 1u) {
            line[len++] = (char)c;
        }
    }
}
