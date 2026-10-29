/* ias15_main.c - IAS15 figure-8 demo firmware (RP2040, USB CDC).
 *
 * OUR glue only: the integrator/gravity objects come from the
 * GPL extraction outside this repo at build time (ias15_api.h,
 * -DIAS15_EXTRACT_DIR). Protocol (docs/BOARD.md, IAS15 section):
 * banner on connect and on "I"; "R <nsteps> <kevery>" emits
 * IAS15FH1 hash lines byte-shaped like the host reference rows so
 * scratch/ias15/work/compare_hashes.py consumes a capture
 * unchanged; "T <nsteps>" is the step-rate measurement hook
 * (RP2040 time_us_64 around 1000-step stepping blocks only).
 * This file formats NO doubles: every value printed is an integer
 * or a binary64 bit pattern in hex.
 *
 * Before accepting a run it validates the AEABI surface it relies
 * on (directed selftest) and cross-checks the workload's table
 * bits against the repo-carried data (ias15_tables.h); either
 * failure refuses R/T loudly.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "hardware/clocks.h"
#include "ias15_api.h"
#include "ias15_hash.h"
#include "ias15_ic.h"
#include "ias15_selftest.h"
#include "ias15_tables.h"
#include "msf_led.h"

static unsigned char g_arena[IAS15X_ARENA_BYTES] __attribute__((aligned(8)));
static int g_ready; /* AEABI-lite + tables both passed */

static void print_banner(void)
{
    pico_unique_board_id_t id;
    int i;
    pico_get_unique_board_id(&id);
    printf("MSF-IAS15 1 ID ");
    for (i = 0; i < PICO_UNIQUE_BOARD_ID_SIZE_BYTES; i++) {
        printf("%02x", id.id[i]);
    }
    printf(" NMAX %d clk_sys_hz %lu\n", IAS15X_NMAX,
           (unsigned long)clock_get_hz(clk_sys));
}

static int check_tables(void)
{
    static const uint64_t *const repo[4] = {
        ias15_table_h_bits, ias15_table_rr_bits,
        ias15_table_c_bits, ias15_table_d_bits
    };
    int which;
    size_t i;
    for (which = 0; which < 4; which++) {
        if (ias15x_table_len(which) == 0) {
            return -1;
        }
        for (i = 0; i < ias15x_table_len(which); i++) {
            if (ias15x_table_bits(which, i) != repo[which][i]) {
                printf("TABLES-MISMATCH which=%d i=%u\n", which, (unsigned)i);
                return -1;
            }
        }
    }
    return 0;
}

static void print_hash_line(ias15x_t *sim, uint64_t step,
                            const uint8_t h_state[32], const uint8_t h_full[32])
{
    int i;
    printf("%llu ", (unsigned long long)step);
    for (i = 0; i < 32; i++) {
        printf("%02x", h_state[i]);
    }
    printf(" ");
    for (i = 0; i < 32; i++) {
        printf("%02x", h_full[i]);
    }
    printf(" %016llx %016llx %016llx\n",
           (unsigned long long)ias15x_t_bits(sim),
           (unsigned long long)ias15x_dt_bits(sim),
           (unsigned long long)ias15x_dt_last_done_bits(sim));
}

static ias15x_t *start_fig8(void)
{
    ias15x_t *sim = NULL;
    int i;
    if (ias15x_init(g_arena, sizeof(g_arena), &sim) != 0) {
        printf("E ias15x_init failed (arena %u bytes)\n",
               (unsigned)sizeof(g_arena));
        return NULL;
    }
    ias15x_set_scalars(sim, IAS15_IC_G_BITS, IAS15_IC_DT_BITS,
                       IAS15_IC_T0_BITS, IAS15_IC_EPS_BITS,
                       IAS15_IC_MINDT_BITS, IAS15_IC_ADAPTIVE_MODE);
    for (i = 0; i < IAS15_IC_N; i++) {
        if (ias15x_add_particle(sim, IAS15_IC_PARTICLES[i]) != 0) {
            printf("E add_particle %d failed\n", i);
            ias15x_shutdown(sim);
            return NULL;
        }
    }
    return sim;
}

static void finish_run(ias15x_t *sim, uint64_t nonfinite)
{
    printf("# END nonfinite_hashed_fields=%llu steps_done_field=%llu "
           "warnings=%lu errors=%lu\n",
           (unsigned long long)nonfinite,
           (unsigned long long)ias15x_steps_done(sim),
           (unsigned long)ias15x_warnings(sim),
           (unsigned long)ias15x_errors(sim));
    printf("IAS15-DONE steps=%llu\n",
           (unsigned long long)ias15x_steps_done(sim));
    msf_led_idle();
    ias15x_shutdown(sim);
}

static void cmd_run(long nsteps, long kevery)
{
    ias15x_t *sim;
    uint8_t hs[32], hf[32];
    uint64_t nonfinite = 0;
    long k;
    if (nsteps < 0 || kevery < 1) {
        printf("E bad-args\n");
        return;
    }
    sim = start_fig8();
    if (sim == NULL) {
        return;
    }
    for (k = 0; k <= nsteps; k++) {
        if (k > 0) {
            ias15x_step(sim);
        }
        msf_led_busy(); /* per step: a step is ~0.7 s here */
        if (k % kevery == 0 || k == nsteps) {
            ias15_hash_pair(sim, (uint64_t)k, hs, hf, &nonfinite);
            print_hash_line(sim, (uint64_t)k, hs, hf);
        }
    }
    finish_run(sim, nonfinite);
}

static void cmd_timed(long nsteps)
{
    ias15x_t *sim;
    uint8_t hs[32], hf[32];
    uint64_t nonfinite = 0;
    long done = 0;
    if (nsteps < 1) {
        printf("E bad-args\n");
        return;
    }
    sim = start_fig8();
    if (sim == NULL) {
        return;
    }
    ias15_hash_pair(sim, 0, hs, hf, &nonfinite);
    print_hash_line(sim, 0, hs, hf);
    while (done < nsteps) {
        long block = nsteps - done;
        uint64_t t0, t1;
        long j;
        if (block > 1000) {
            block = 1000;
        }
        /* Named clock: RP2040 1 MHz timer via pico time_us_64();
         * the interval covers accepted stepping only, never the
         * hashing/printing below. */
        t0 = time_us_64();
        for (j = 0; j < block; j++) {
            ias15x_step(sim);
        }
        t1 = time_us_64();
        msf_led_busy(); /* outside the timed region, with the printing */
        done += block;
        printf("RATE block_steps=%ld elapsed_us=%llu clk_sys_hz=%lu\n",
               block, (unsigned long long)(t1 - t0),
               (unsigned long)clock_get_hz(clk_sys));
        ias15_hash_pair(sim, (uint64_t)done, hs, hf, &nonfinite);
        print_hash_line(sim, (uint64_t)done, hs, hf);
    }
    finish_run(sim, nonfinite);
}

static void handle_line(char *line)
{
    char *tok[4];
    int ntok = 0;
    char *p;
    for (p = strtok(line, " \t\r\n"); p && ntok < 4; p = strtok(NULL, " \t\r\n")) {
        tok[ntok++] = p;
    }
    if (ntok == 0) {
        return;
    }
    if (strcmp(tok[0], "I") == 0) {
        print_banner();
        printf("IAS15-READY %d\n", g_ready);
        return;
    }
    if (strcmp(tok[0], "R") == 0 || strcmp(tok[0], "T") == 0) {
        if (!g_ready) {
            printf("E not-ready (aeabi-lite or tables check failed)\n");
            return;
        }
        if (tok[0][0] == 'R') {
            if (ntok != 3) {
                printf("E usage R nsteps kevery\n");
                return;
            }
            cmd_run(strtol(tok[1], NULL, 10), strtol(tok[2], NULL, 10));
        } else {
            if (ntok != 2) {
                printf("E usage T nsteps\n");
                return;
            }
            cmd_timed(strtol(tok[1], NULL, 10));
        }
        return;
    }
    printf("E unknown\n");
}

int main(void)
{
    char line[128];
    size_t len = 0;
    unsigned long long checks = 0, fails = 0;
    int lite_rc, tables_rc;

    stdio_init_all();
    msf_led_init();
    while (!stdio_usb_connected()) {
        sleep_ms(50);
    }
    sleep_ms(200);
    print_banner();
    msf_led_busy();
    lite_rc = msf_aeabi_selftest(0, &checks, &fails);
    printf("AEABI-LITE %s checks=%llu failures=%llu\n",
           lite_rc == 0 ? "PASS" : "FAIL", checks, fails);
    tables_rc = check_tables();
    printf("TABLES %s\n", tables_rc == 0 ? "PASS" : "FAIL");
    g_ready = (lite_rc == 0 && tables_rc == 0);
    printf("IAS15-READY %d\n", g_ready);
    msf_led_idle();
    for (;;) {
        int c = getchar_timeout_us(100000);
        if (c == PICO_ERROR_TIMEOUT) {
            msf_led_idle();
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
