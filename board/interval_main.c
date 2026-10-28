/* interval_main.c - Step 1c interval workload firmware (RP2040).
 *
 * Streams the frozen catalogue rows from the host over USB CDC,
 * classifies each ray through board/interval_workload.c, and
 * folds exactly the host runner's IW1 field sequence into a
 * SHA-256 (board/interval_host.c is the layout definition).
 * The board digest must equal the host digest for the same row
 * stream; that equality is the Step 1c on-silicon claim.
 *
 * Protocol (docs/BOARD.md, interval section):
 *   I                       banner (also printed on connect)
 *   B                       begin: reset context + hash -> OK begin
 *   S id o0 o1 o2 d0 d1 d2 c0 c1 c2 r   sphere row -> R id
 *   X id o0 o1 o2 d0 d1 d2 lo0 lo1 lo2 hi0 hi1 hi2
 *                           box row -> R id
 *   T id o0 o1 o2 d0 d1 d2  torus row -> R id
 *   E                       end: SUMMARY + BOARD_SHA256 + done
 * All words are binary64 bit patterns in hex; this file formats
 * no doubles. compute_us in the summary is RP2040 timer time
 * inside the workload calls only (hashing/stdio excluded), a
 * measurement record, not a performance claim.
 */
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/time.h"
#include "pico/unique_id.h"
#include "hardware/clocks.h"
#include "interval_workload.h"
#include "../tests/sha256.h"

static iw_ctx_t g_ctx;
static msf_sha256_t g_hash;
static uint32_t g_rows, g_sphere, g_box, g_torus;
static uint32_t g_unc1, g_unc2, g_unc3;
static uint64_t g_compute_us;

static void h_u8(unsigned v)
{
    uint8_t b = (uint8_t)v;
    msf_sha256_update(&g_hash, &b, 1);
}

static void h_u32(uint32_t v)
{
    uint8_t b[4] = {(uint8_t)v, (uint8_t)(v >> 8),
                    (uint8_t)(v >> 16), (uint8_t)(v >> 24)};
    msf_sha256_update(&g_hash, b, 4);
}

static void h_u64(uint64_t v)
{
    uint8_t b[8];
    int i;
    for (i = 0; i < 8; i++) {
        b[i] = (uint8_t)(v >> (8 * i));
    }
    msf_sha256_update(&g_hash, b, 8);
}

static void print_banner(void)
{
    pico_unique_board_id_t id;
    int i;
    pico_get_unique_board_id(&id);
    printf("MSF-INTERVAL 1 ID ");
    for (i = 0; i < PICO_UNIQUE_BOARD_ID_SIZE_BYTES; i++) {
        printf("%02x", id.id[i]);
    }
    printf(" clk_sys_hz %lu\n", (unsigned long)clock_get_hz(clk_sys));
}

static iw_class_t staged_final(iw_class_t s1, iw_class_t s2, iw_class_t s3)
{
    if (s3 != IW_UNCERTAIN) {
        return s3;
    }
    if (s2 != IW_UNCERTAIN) {
        return s2;
    }
    return s1;
}

static void cmd_begin(void)
{
    iw_ctx_init(&g_ctx);
    msf_sha256_init(&g_hash);
    msf_sha256_update(&g_hash, "IW1", 3);
    g_rows = g_sphere = g_box = g_torus = 0;
    g_unc1 = g_unc2 = g_unc3 = 0;
    g_compute_us = 0;
    printf("OK begin\n");
}

static void cmd_sphere(char **tok)
{
    msf64_t O[3], D[3], C[3], r;
    msf32_t lo1, hi1;
    msf64_t lo2, hi2;
    uint64_t o1, o2, o3, t0;
    uint32_t id = (uint32_t)strtoul(tok[1], NULL, 10);
    iw_class_t s1, s2, s3, fin;
    int i;
    for (i = 0; i < 3; i++) {
        O[i] = (msf64_t)strtoull(tok[2 + i], NULL, 16);
        D[i] = (msf64_t)strtoull(tok[5 + i], NULL, 16);
        C[i] = (msf64_t)strtoull(tok[8 + i], NULL, 16);
    }
    r = (msf64_t)strtoull(tok[11], NULL, 16);
    t0 = time_us_64();
    s1 = iw_sphere_stage1_f32(&g_ctx, O, D, C, r, &lo1, &hi1, &o1);
    s2 = iw_sphere_stage2_f64(&g_ctx, O, D, C, r, &lo2, &hi2, &o2);
    s3 = iw_sphere_stage3_exact(&g_ctx, O, D, C, r, &o3);
    g_compute_us += time_us_64() - t0;
    fin = staged_final(s1, s2, s3);
    g_rows++;
    g_sphere++;
    if (s1 == IW_UNCERTAIN) g_unc1++;
    if (s2 == IW_UNCERTAIN) g_unc2++;
    if (s3 == IW_UNCERTAIN) g_unc3++;
    h_u32(id);
    h_u8(0);
    h_u8((unsigned)s1); h_u32(lo1); h_u32(hi1); h_u64(o1);
    h_u8((unsigned)s2); h_u64(lo2); h_u64(hi2); h_u64(o2);
    h_u8((unsigned)s3); h_u64(o3);
    h_u8((unsigned)fin);
    printf("R %" PRIu32 "\n", id);
}

static void cmd_box(char **tok)
{
    msf64_t O[3], D[3], loB[3], hiB[3], tmin, tmax;
    uint64_t ops, t0;
    uint32_t id = (uint32_t)strtoul(tok[1], NULL, 10);
    iw_class_t cls;
    int i;
    for (i = 0; i < 3; i++) {
        O[i] = (msf64_t)strtoull(tok[2 + i], NULL, 16);
        D[i] = (msf64_t)strtoull(tok[5 + i], NULL, 16);
        loB[i] = (msf64_t)strtoull(tok[8 + i], NULL, 16);
        hiB[i] = (msf64_t)strtoull(tok[11 + i], NULL, 16);
    }
    t0 = time_us_64();
    cls = iw_box(&g_ctx, O, D, loB, hiB, &tmin, &tmax, &ops);
    g_compute_us += time_us_64() - t0;
    g_rows++;
    g_box++;
    h_u32(id);
    h_u8(1);
    h_u8((unsigned)cls); h_u64(tmin); h_u64(tmax); h_u64(ops);
    printf("R %" PRIu32 "\n", id);
}

static void cmd_torus(char **tok)
{
    msf64_t O[3], D[3];
    iw_torus_result_t tr;
    uint64_t t0;
    uint32_t id = (uint32_t)strtoul(tok[1], NULL, 10);
    int i;
    for (i = 0; i < 3; i++) {
        O[i] = (msf64_t)strtoull(tok[2 + i], NULL, 16);
        D[i] = (msf64_t)strtoull(tok[5 + i], NULL, 16);
    }
    t0 = time_us_64();
    iw_torus_first_hit(&g_ctx, O, D, IW_TORUS_TOL_BITS, 4000000u, &tr);
    g_compute_us += time_us_64() - t0;
    g_rows++;
    g_torus++;
    h_u32(id);
    h_u8(2);
    h_u8((unsigned)tr.cls); h_u64(tr.br_lo); h_u64(tr.br_hi);
    h_u64(tr.ops); h_u64(tr.evals); h_u32(tr.max_depth);
    h_u8((unsigned)tr.cap_hit);
    printf("R %" PRIu32 "\n", id);
}

static void cmd_end(void)
{
    msf_sha256_t copy = g_hash;
    uint8_t dig[32];
    int i;
    msf_sha256_final(&copy, dig);
    printf("SUMMARY rows=%" PRIu32 " sphere=%" PRIu32 " box=%" PRIu32
           " torus=%" PRIu32 " sphere_uncertain s1=%" PRIu32
           " s2=%" PRIu32 " s3=%" PRIu32 " total_ops=%" PRIu64
           " compute_us=%" PRIu64 "\n",
           g_rows, g_sphere, g_box, g_torus, g_unc1, g_unc2, g_unc3,
           g_ctx.ops, g_compute_us);
    printf("BOARD_SHA256 ");
    for (i = 0; i < 32; i++) {
        printf("%02x", dig[i]);
    }
    printf("\nINTERVAL-DONE rows=%" PRIu32 "\n", g_rows);
}

static void handle_line(char *line)
{
    char *tok[16];
    int ntok = 0;
    char *p;
    for (p = strtok(line, " \t\r\n"); p && ntok < 16;
         p = strtok(NULL, " \t\r\n")) {
        tok[ntok++] = p;
    }
    if (ntok == 0 || tok[0][0] == '#') {
        return;
    }
    if (strcmp(tok[0], "I") == 0) {
        print_banner();
    } else if (strcmp(tok[0], "B") == 0) {
        cmd_begin();
    } else if (strcmp(tok[0], "S") == 0 && ntok == 12) {
        cmd_sphere(tok);
    } else if (strcmp(tok[0], "X") == 0 && ntok == 14) {
        cmd_box(tok);
    } else if (strcmp(tok[0], "T") == 0 && ntok == 8) {
        cmd_torus(tok);
    } else if (strcmp(tok[0], "E") == 0) {
        cmd_end();
    } else {
        printf("E malformed\n");
    }
}

int main(void)
{
    char line[384];
    size_t len = 0;
    stdio_init_all();
    while (!stdio_usb_connected()) {
        sleep_ms(50);
    }
    sleep_ms(200);
    print_banner();
    cmd_begin();
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
