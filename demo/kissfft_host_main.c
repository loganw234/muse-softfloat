/* kissfft_host_main.c - KissFFT Fork B host proof for the demo.
 * SPDX-License-Identifier: MIT
 *
 * Runs the 12 gated configurations (N in {256, 1024, 4096} x
 * {complex fwd/inv, real fwd/inv}, double config) of the
 * Fork-B-patched KissFFT 131.2.0 tree (demo/make_kissfft_tree.py;
 * twiddles from correctly rounded sinpi/cospi of exact cycle
 * fractions, routed into muse-softfloat by --wrap) and prints one
 * "KF <N> <kind> <dir> <sha256>" row per configuration.  The rows
 * must equal demo/expected-kissfft.txt bit-for-bit.  SHA-256 is
 * over each output field's 8 bytes little-endian, r then i per
 * bin - the same field hash the firmware prints.
 *
 * Inputs come from the integer LCG below, duplicated verbatim in
 * board/kissfft_main.c so host and firmware feed identical bits
 * with no shared file.  Analytic anchors (exact delta/hand-DFT/
 * tone results and in-place aliasing) run after the matrix; the
 * exit status is non-zero if any anchor fails.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "kiss_fft.h"
#include "kiss_fftr.h"
#include "../tests/sha256.h"

/* ---- shared deterministic inputs (verbatim in firmware) ---- */
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
    printf("KF %d %s %s ", n, kind, dir);
    for (i = 0; i < 32; i++) printf("%02x", d[i]);
    printf("\n");
}

static uint64_t d2u(double v) { uint64_t u; memcpy(&u, &v, 8); return u; }
static int g_anchor_fails;
static void anchor(const char *what, int ok)
{
    printf("ANCHOR %s %s\n", what, ok ? "PASS" : "FAIL");
    if (!ok) g_anchor_fails++;
}

#define NMAX 4096
static kiss_fft_cpx cin[NMAX], cout_[NMAX];
static kiss_fft_scalar rin[NMAX];
static kiss_fft_cpx rout[NMAX / 2 + 1];

int main(void)
{
    static const int Ns[3] = {256, 1024, 4096};
    uint64_t cfgidx = 0;
    int ni, i, n;

    for (ni = 0; ni < 3; ni++) {
        size_t len = 0, lenr = 0;
        n = Ns[ni];
        kiss_fft_alloc(n, 0, NULL, &len);
        kiss_fftr_alloc(n, 0, NULL, &lenr);
        printf("SIZE %d complex_state=%zu real_state=%zu cpx=%zu\n",
               n, len, lenr, sizeof(kiss_fft_cpx));
    }

    for (ni = 0; ni < 3; ni++) {
        n = Ns[ni];
        /* complex forward, then inverse */
        int inv;
        for (inv = 0; inv < 2; inv++, cfgidx++) {
            kiss_fft_cfg cfg = kiss_fft_alloc(n, inv, NULL, NULL);
            msf_sha256_t h;
            if (!cfg) { printf("ALLOC FAIL\n"); return 1; }
            kf_seed(cfgidx);
            for (i = 0; i < n; i++) { cin[i].r = kf_next(); cin[i].i = kf_next(); }
            kiss_fft(cfg, cin, cout_);
            msf_sha256_init(&h);
            for (i = 0; i < n; i++) { hash_field(&h, cout_[i].r); hash_field(&h, cout_[i].i); }
            print_hash(n, "complex", inv ? "inv" : "fwd", &h);
            free(cfg);
        }
        /* real forward */
        {
            kiss_fftr_cfg cfg = kiss_fftr_alloc(n, 0, NULL, NULL);
            msf_sha256_t h;
            if (!cfg) { printf("ALLOC FAIL\n"); return 1; }
            kf_seed(cfgidx++);
            for (i = 0; i < n; i++) rin[i] = kf_next();
            kiss_fftr(cfg, rin, rout);
            msf_sha256_init(&h);
            for (i = 0; i < n / 2 + 1; i++) { hash_field(&h, rout[i].r); hash_field(&h, rout[i].i); }
            print_hash(n, "real", "fwd", &h);
            free(cfg);
        }
        /* real inverse: input is N/2+1 cpx from the same LCG */
        {
            kiss_fftr_cfg cfg = kiss_fftr_alloc(n, 1, NULL, NULL);
            static kiss_fft_scalar iout[NMAX];
            msf_sha256_t h;
            if (!cfg) { printf("ALLOC FAIL\n"); return 1; }
            kf_seed(cfgidx++);
            for (i = 0; i < n / 2 + 1; i++) { rout[i].r = kf_next(); rout[i].i = kf_next(); }
            rout[0].i = 0.0; rout[n / 2].i = 0.0; /* DC/Nyquist are real in this API */
            kiss_fftri(cfg, rout, iout);
            msf_sha256_init(&h);
            for (i = 0; i < n; i++) hash_field(&h, iout[i]);
            print_hash(n, "real", "inv", &h);
            free(cfg);
        }
    }

    /* ---- analytic anchors ---- */
    {
        kiss_fft_cfg cfg = kiss_fft_alloc(64, 0, NULL, NULL);
        int ok = 1;
        for (i = 0; i < 64; i++) { cin[i].r = (i == 0); cin[i].i = 0.0; }
        kiss_fft(cfg, cin, cout_);
        for (i = 0; i < 64; i++)
            if (d2u(cout_[i].r) != d2u(1.0) || d2u(cout_[i].i) != d2u(0.0)) ok = 0;
        anchor("delta-flat-64", ok);
        free(cfg);
    }
    {
        /* N=4 hand DFT: x=[1,2,3,4] -> X=[10, -2+2i, -2, -2-2i] */
        kiss_fft_cfg cfg = kiss_fft_alloc(4, 0, NULL, NULL);
        static const double xr[4] = {1, 2, 3, 4};
        static const double wr[4] = {10, -2, -2, -2};
        static const double wi[4] = {0, 2, 0, -2};
        int ok = 1;
        for (i = 0; i < 4; i++) { cin[i].r = xr[i]; cin[i].i = 0.0; }
        kiss_fft(cfg, cin, cout_);
        for (i = 0; i < 4; i++)
            if (d2u(cout_[i].r) != d2u(wr[i]) || d2u(cout_[i].i) != d2u(wi[i])) ok = 0;
        anchor("hand-dft4", ok);
        free(cfg);
    }
    {
        /* N=8: delta at 1 (exact quarter twiddles), constant input,
         * and a bin-centred tone with exact-quarter samples. */
        kiss_fft_cfg cfg = kiss_fft_alloc(8, 0, NULL, NULL);
        int ok = 1;
        for (i = 0; i < 8; i++) { cin[i].r = (i == 1); cin[i].i = 0.0; }
        kiss_fft(cfg, cin, cout_);
        if (d2u(cout_[0].r) != d2u(1.0) || d2u(cout_[0].i) != d2u(0.0)) ok = 0;
        if (d2u(cout_[2].r) != d2u(0.0) || d2u(cout_[2].i) != d2u(-1.0)) ok = 0;
        if (d2u(cout_[4].r) != d2u(-1.0) || d2u(cout_[4].i) != d2u(0.0)) ok = 0;
        if (d2u(cout_[6].r) != d2u(0.0) || d2u(cout_[6].i) != d2u(1.0)) ok = 0;
        for (i = 0; i < 8; i++) { cin[i].r = 1.0; cin[i].i = 0.0; }
        kiss_fft(cfg, cin, cout_);
        if (d2u(cout_[0].r) != d2u(8.0)) ok = 0;
        for (i = 1; i < 8; i++)
            if (cout_[i].r != 0.0 || cout_[i].i != 0.0) ok = 0;
        {
            static const double tone[8] = {1, 0, -1, 0, 1, 0, -1, 0};
            for (i = 0; i < 8; i++) { cin[i].r = tone[i]; cin[i].i = 0.0; }
        }
        kiss_fft(cfg, cin, cout_);
        for (i = 0; i < 8; i++) {
            double er = (i == 2 || i == 6) ? 4.0 : 0.0;
            if (cout_[i].r != er || cout_[i].i != 0.0) ok = 0;
        }
        anchor("hand-dft8-tone", ok);
        free(cfg);
    }
    {
        /* in-place aliasing equals out-of-place, N=1024 */
        kiss_fft_cfg cfg = kiss_fft_alloc(1024, 0, NULL, NULL);
        msf_sha256_t h1, h2;
        uint8_t d1[32], d2_[32];
        kf_seed(4); /* same seed slot as "1024 complex fwd" */
        for (i = 0; i < 1024; i++) { cin[i].r = kf_next(); cin[i].i = kf_next(); }
        memcpy(cout_, cin, sizeof(kiss_fft_cpx) * 1024);
        kiss_fft(cfg, cout_, cout_);
        msf_sha256_init(&h1);
        for (i = 0; i < 1024; i++) { hash_field(&h1, cout_[i].r); hash_field(&h1, cout_[i].i); }
        msf_sha256_final(&h1, d1);
        kiss_fft(cfg, cin, cout_);
        msf_sha256_init(&h2);
        for (i = 0; i < 1024; i++) { hash_field(&h2, cout_[i].r); hash_field(&h2, cout_[i].i); }
        msf_sha256_final(&h2, d2_);
        anchor("inplace-alias-1024", memcmp(d1, d2_, 32) == 0);
        free(cfg);
    }

    printf("HOST-PROOF anchors_fails=%d\n", g_anchor_fails);
    return g_anchor_fails ? 1 : 0;
}
