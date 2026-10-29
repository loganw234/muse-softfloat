/* kissfft_main.c - KissFFT 131.2.0 Fork B workload firmware
 * (SF-1 Step 2c). LEAD-RUN under the board lock after merge;
 * this parcel compile-checks it only.
 *
 * Claim shape (named patch, never "unmodified"): the workload
 * is KissFFT 131.2.0 with one named change - twiddle generation
 * takes exact cycle fractions into correctly rounded
 * sinpi/cospi (compat/msf_aeabi.c over msf64_sin_pi/cos_pi)
 * instead of radian phases into sin/cos. At the gated
 * power-of-two sizes below, the twiddles generated at runtime
 * on this device are the correctly rounded values of the exact
 * mathematical twiddles (host MPFR provenance gate:
 * scratch/parcel-w4kissfft), and the KF output hashes must be
 * bit-identical to the host proof's under the same patched
 * source. The KissFFT tree lives outside the repo
 * (MSF_KISSFFT_DIR at build time); only this glue is here.
 *
 * RAM (ledger design entry, lenmem measured on host): static
 * workspace 128 KiB (two 4096-cpx double unions) + malloc'd
 * state, worst real-4096 82208 B, one configuration live at a
 * time; stack 4 KiB. Prints banner, one KF hash row per
 * configuration in the host proof's frozen order, KISSFFT-DONE.
 * On 'R' over USB it runs again (re-sync after a raced open).
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/unique_id.h"
#include "kiss_fft.h"
#include "kiss_fftr.h"
#include "../tests/sha256.h"
#include "msf_led.h"

/* ---- shared deterministic inputs (verbatim in the host proof,
 * scratch/parcel-w4kissfft/host_main.c) ---- */
static uint64_t kf_lcg;
static void kf_seed(uint64_t cfg)
{
    kf_lcg = 0x4B49534646540001ULL ^ (cfg * 0x9E3779B97F4A7C15ULL);
}
static double kf_next(void)
{
    int32_t k;
    kf_lcg = kf_lcg * 6364136223846793005ULL + 1442695040888963407ULL;
    k = (int32_t)((kf_lcg >> 40) % 2048u) - 1024;
    return (double)k / 1024.0; /* exact: int->double, /2^10 */
}
/* ---- end shared ---- */

#define NMAX 4096
static union { kiss_fft_cpx c[NMAX]; double d[2 * NMAX]; } buf_in, buf_out;

static void hash_field(msf_sha256_t *h, double v)
{
    uint64_t u;
    uint8_t b[8];
    int i;
    memcpy(&u, &v, 8);
    for (i = 0; i < 8; i++) b[i] = (uint8_t)(u >> (8 * i));
    msf_sha256_update(h, b, 8);
}

static void print_hash(int n, const char *kind, const char *dir,
                       msf_sha256_t *h)
{
    uint8_t d[32];
    int i;
    msf_sha256_final(h, d);
    msf_led_busy();
    printf("KF %d %s %s ", n, kind, dir);
    for (i = 0; i < 32; i++) printf("%02x", d[i]);
    printf("\n");
}

static int run_all(void)
{
    static const int Ns[3] = {256, 1024, 4096};
    uint64_t cfgidx = 0;
    int ni, i, n, inv;
    for (ni = 0; ni < 3; ni++) {
        n = Ns[ni];
        for (inv = 0; inv < 2; inv++, cfgidx++) {
            kiss_fft_cfg cfg = kiss_fft_alloc(n, inv, NULL, NULL);
            msf_sha256_t h;
            if (!cfg) { printf("E alloc complex %d\n", n); return 1; }
            kf_seed(cfgidx);
            for (i = 0; i < n; i++) {
                buf_in.c[i].r = kf_next();
                buf_in.c[i].i = kf_next();
            }
            kiss_fft(cfg, buf_in.c, buf_out.c);
            msf_sha256_init(&h);
            for (i = 0; i < n; i++) {
                hash_field(&h, buf_out.c[i].r);
                hash_field(&h, buf_out.c[i].i);
            }
            print_hash(n, "complex", inv ? "inv" : "fwd", &h);
            free(cfg);
        }
        {
            kiss_fftr_cfg cfg = kiss_fftr_alloc(n, 0, NULL, NULL);
            msf_sha256_t h;
            if (!cfg) { printf("E alloc real %d\n", n); return 1; }
            kf_seed(cfgidx++);
            for (i = 0; i < n; i++) buf_in.d[i] = kf_next();
            kiss_fftr(cfg, buf_in.d, buf_out.c);
            msf_sha256_init(&h);
            for (i = 0; i < n / 2 + 1; i++) {
                hash_field(&h, buf_out.c[i].r);
                hash_field(&h, buf_out.c[i].i);
            }
            print_hash(n, "real", "fwd", &h);
            free(cfg);
        }
        {
            kiss_fftr_cfg cfg = kiss_fftr_alloc(n, 1, NULL, NULL);
            msf_sha256_t h;
            if (!cfg) { printf("E alloc reali %d\n", n); return 1; }
            kf_seed(cfgidx++);
            for (i = 0; i < n / 2 + 1; i++) {
                buf_in.c[i].r = kf_next();
                buf_in.c[i].i = kf_next();
            }
            buf_in.c[0].i = 0.0;
            buf_in.c[n / 2].i = 0.0; /* DC/Nyquist real in this API */
            kiss_fftri(cfg, buf_in.c, buf_out.d);
            msf_sha256_init(&h);
            for (i = 0; i < n; i++) hash_field(&h, buf_out.d[i]);
            print_hash(n, "real", "inv", &h);
            free(cfg);
        }
    }
    return 0;
}

int main(void)
{
    pico_unique_board_id_t id;
    int i, ch;

    stdio_init_all();
    msf_led_init();
    while (!stdio_usb_connected()) {
        sleep_ms(50);
    }
    sleep_ms(200);
    pico_get_unique_board_id(&id);
    printf("MSF-KISSFFT 1 ID ");
    for (i = 0; i < PICO_UNIQUE_BOARD_ID_SIZE_BYTES; i++) {
        printf("%02x", id.id[i]);
    }
    printf("\n");
    if (run_all() == 0) {
        printf("KISSFFT-DONE\n");
    }
    msf_led_idle();
    for (;;) {
        ch = getchar_timeout_us(100000);
        if (ch == 'R') {
            if (run_all() == 0) {
                printf("KISSFFT-DONE\n");
            }
            msf_led_idle();
        } else if (ch == PICO_ERROR_TIMEOUT) {
            msf_led_idle();
        }
    }
}
