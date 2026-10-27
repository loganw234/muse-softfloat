/* ias15_hash.c - IAS15FH1 streaming record builders (see header). */
#include <stddef.h>
#include <string.h>
#include "ias15_hash.h"
#include "../tests/sha256.h"

static void put_u8(msf_sha256_t *h, uint8_t v)
{
    msf_sha256_update(h, &v, 1);
}

static void put_u32le(msf_sha256_t *h, uint32_t v)
{
    uint8_t b[4] = {(uint8_t)v, (uint8_t)(v >> 8),
                    (uint8_t)(v >> 16), (uint8_t)(v >> 24)};
    msf_sha256_update(h, b, 4);
}

static void put_u64le(msf_sha256_t *h, uint64_t v)
{
    uint8_t b[8];
    int i;
    for (i = 0; i < 8; i++) {
        b[i] = (uint8_t)(v >> (8 * i));
    }
    msf_sha256_update(h, b, 8);
}

static int is_nonfinite(uint64_t bits)
{
    return ((bits >> 52) & 0x7FFu) == 0x7FFu;
}

static uint64_t bits_of(const double *p)
{
    uint64_t u;
    memcpy(&u, p, sizeof(u));
    return u;
}

static void put_array_count(msf_sha256_t *h, const double *arr, size_t n,
                            uint64_t *nonfinite_inout)
{
    size_t i;
    for (i = 0; i < n; i++) {
        uint64_t b = bits_of(&arr[i]);
        if (nonfinite_inout != NULL && is_nonfinite(b)) {
            (*nonfinite_inout)++;
        }
        put_u64le(h, b);
    }
}

void ias15_hash_pair(ias15x_t *sim, uint64_t step,
                     uint8_t h_state[32], uint8_t h_full[32],
                     uint64_t *nonfinite_inout)
{
    msf_sha256_t h;
    size_t i, n = ias15x_particle_count(sim);
    uint64_t n3 = (uint64_t)ias15x_n3(sim);
    int which;

    /* H_state: "IAS15FH1" | 0x53 | step | N | t dt dt_last_done G |
     * per particle x y z vx vy vz ax ay az m r */
    msf_sha256_init(&h);
    msf_sha256_update(&h, "IAS15FH1", 8);
    put_u8(&h, 0x53);
    put_u64le(&h, step);
    put_u64le(&h, (uint64_t)n);
    put_u64le(&h, ias15x_t_bits(sim));
    put_u64le(&h, ias15x_dt_bits(sim));
    put_u64le(&h, ias15x_dt_last_done_bits(sim));
    put_u64le(&h, ias15x_g_bits(sim));
    for (i = 0; i < n; i++) {
        size_t f;
        for (f = 0; f < 11; f++) {
            uint64_t b = ias15x_particle_field_bits(sim, i, f);
            if (nonfinite_inout != NULL && is_nonfinite(b)) {
                (*nonfinite_inout)++;
            }
            put_u64le(&h, b);
        }
    }
    msf_sha256_final(&h, h_state);

    /* H_full: "IAS15FH1" | 0x46 | step | N | epsilon min_dt |
     * adaptive_mode 0 | iterations_max_exceeded | N3 | allocated |
     * flat arrays (N3 each) then dp7 arrays (7*N3 each) */
    msf_sha256_init(&h);
    msf_sha256_update(&h, "IAS15FH1", 8);
    put_u8(&h, 0x46);
    put_u64le(&h, step);
    put_u64le(&h, (uint64_t)n);
    put_u64le(&h, ias15x_epsilon_bits(sim));
    put_u64le(&h, ias15x_min_dt_bits(sim));
    put_u32le(&h, ias15x_adaptive_mode(sim));
    put_u32le(&h, 0);
    put_u64le(&h, ias15x_iterations_max_exceeded(sim));
    put_u64le(&h, n3);
    put_u8(&h, ias15x_allocated(sim) ? (uint8_t)1 : (uint8_t)0);
    if (ias15x_allocated(sim)) {
        for (which = 0; which < 7; which++) {
            put_array_count(&h, ias15x_flat_array(sim, which),
                            (size_t)n3, nonfinite_inout);
        }
        for (which = 0; which < 6; which++) {
            put_array_count(&h, ias15x_dp7_array(sim, which),
                            (size_t)(7u * n3), nonfinite_inout);
        }
    }
    msf_sha256_final(&h, h_full);
}
