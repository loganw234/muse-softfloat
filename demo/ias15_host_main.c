/* ias15_host_main.c - IAS15 host identity proof driver for the demo.
 * SPDX-License-Identifier: MIT
 *
 * Runs the figure-8 problem through the exact path the board
 * firmware uses - the generated IAS15 extract behind the opaque
 * board/ias15_api.h, initial conditions from board/ias15_ic.h,
 * IAS15FH1 digests from board/ias15_hash.c over tests/sha256.c -
 * and writes one hash row per step:
 *   <step> <H_state> <H_full> <t bits> <dt bits> <dt_last bits>
 * plus a final "# END ..." line.  Integer/hex I/O only: this file
 * performs no floating-point arithmetic, so the identical source
 * serves both demo builds:
 *
 *   native  - workload compiled with the strict desktop-reference
 *             flags (SSE2, -ffp-contract=off); its rows must equal
 *             demo/expected-ias15.txt, the recorded desktop run.
 *   soft    - the same sources compiled -msoft-float -mno-sse2
 *             with demo/ias15_host_shim.c, so every binary64
 *             operation is a libcall into muse-softfloat; its rows
 *             must equal the same expected file bit-for-bit.  The
 *             soft build defines DEMO_IAS15_SOFT and ends with a
 *             "# SHIMOPS total=... traps=..." line: a run whose
 *             total is zero interposed nothing and proves nothing.
 *
 * Before stepping, the extract's coefficient tables are checked
 * bit-for-bit against board/ias15_tables.h (the firmware's TABLES
 * check, same data).  Usage: ias15_host <nsteps> <outfile>
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "ias15_api.h"
#include "ias15_hash.h"
#include "ias15_ic.h"
#include "ias15_tables.h"

#ifdef DEMO_IAS15_SOFT
unsigned long long demo_ias15_shim_ops(void);
unsigned long long demo_ias15_shim_traps(void);
#endif

static unsigned char g_arena[512u * 1024u];

static void hex32(const uint8_t d[32], char out[65])
{
    static const char H[] = "0123456789abcdef";
    int i;
    for (i = 0; i < 32; i++) {
        out[2 * i] = H[d[i] >> 4];
        out[2 * i + 1] = H[d[i] & 15];
    }
    out[64] = 0;
}

static int tables_match(void)
{
    static const uint64_t *const want[4] = {
        ias15_table_h_bits, ias15_table_rr_bits,
        ias15_table_c_bits, ias15_table_d_bits
    };
    int which;
    for (which = 0; which < 4; which++) {
        size_t i, n = ias15x_table_len(which);
        if (n == 0) return 0;
        for (i = 0; i < n; i++) {
            if (ias15x_table_bits(which, i) != want[which][i]) return 0;
        }
    }
    return 1;
}

int main(int argc, char **argv)
{
    ias15x_t *sim = NULL;
    long nsteps, k;
    int i;
    FILE *out;
    uint64_t nonfinite = 0;

    if (argc != 3) {
        fprintf(stderr, "usage: ias15_host <nsteps> <outfile>\n");
        return 2;
    }
    nsteps = strtol(argv[1], NULL, 10);
    if (nsteps < 0) {
        fprintf(stderr, "ias15_host: bad nsteps\n");
        return 2;
    }
    if (!tables_match()) {
        fprintf(stderr, "ias15_host: TABLES FAIL - extract coefficient "
                        "bits differ from board/ias15_tables.h\n");
        return 1;
    }
    out = fopen(argv[2], "w");
    if (!out) {
        fprintf(stderr, "ias15_host: cannot open %s\n", argv[2]);
        return 2;
    }
#ifdef DEMO_IAS15_SOFT
    fprintf(out, "# IAS15FH1 build=soft (binary64 via muse-softfloat shim)\n");
#else
    fprintf(out, "# IAS15FH1 build=native (host SSE2, strict flags)\n");
#endif
    if (ias15x_init(g_arena, sizeof(g_arena), &sim) != 0) {
        fprintf(stderr, "ias15_host: ias15x_init failed\n");
        fclose(out);
        return 1;
    }
    ias15x_set_scalars(sim, IAS15_IC_G_BITS, IAS15_IC_DT_BITS,
                       IAS15_IC_T0_BITS, IAS15_IC_EPS_BITS,
                       IAS15_IC_MINDT_BITS, IAS15_IC_ADAPTIVE_MODE);
    for (i = 0; i < IAS15_IC_N; i++) {
        if (ias15x_add_particle(sim, IAS15_IC_PARTICLES[i]) != 0) {
            fprintf(stderr, "ias15_host: add_particle %d failed\n", i);
            fclose(out);
            return 1;
        }
    }
    for (k = 0; k <= nsteps; k++) {
        uint8_t hs[32], hf[32];
        char sS[65], sF[65];
        if (k > 0) ias15x_step(sim);
        ias15_hash_pair(sim, (uint64_t)k, hs, hf, &nonfinite);
        hex32(hs, sS);
        hex32(hf, sF);
        fprintf(out, "%lld %s %s %016llx %016llx %016llx\n",
                (long long)k, sS, sF,
                (unsigned long long)ias15x_t_bits(sim),
                (unsigned long long)ias15x_dt_bits(sim),
                (unsigned long long)ias15x_dt_last_done_bits(sim));
    }
    fprintf(out, "# END nonfinite_hashed_fields=%llu steps_done_field=%llu "
                 "warnings=%u errors=%u\n",
            (unsigned long long)nonfinite,
            (unsigned long long)ias15x_steps_done(sim),
            (unsigned)ias15x_warnings(sim),
            (unsigned)ias15x_errors(sim));
#ifdef DEMO_IAS15_SOFT
    fprintf(out, "# SHIMOPS total=%llu traps=%llu\n",
            demo_ias15_shim_ops(), demo_ias15_shim_traps());
#endif
    fclose(out);
    ias15x_shutdown(sim);
    return 0;
}
