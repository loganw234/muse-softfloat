/* twiddle_gate.c - MPFR twiddle-provenance gate (reproduction appendix).
 * SPDX-License-Identifier: MIT
 *
 * Provenance: verbatim the scratch gate driver
 * (parcel-w4kissfft's gate_main.c) from the SF-1 Step 2c
 * workload parcel, which produced the recorded PROVENANCE
 * checked_fields=8856 mismatches=0; the derivation is
 * retained in docs/TWIDDLES.md (which names this file).
 * Only this header comment was added; the gate logic below is
 * unchanged. It builds against today's tree with no source
 * edits (checked 2026-10-29: compat still provides
 * __wrap_sinpi/__wrap_cospi/__wrap_floor over the
 * msf64_sin_pi/msf64_cos_pi core rows).
 *
 * What it does: it #includes the patched kiss_fft.c /
 * kiss_fftr.c, so the twiddle tables it inspects are the
 * actual runtime-produced tables from the real alloc path
 * (kiss_fft_alloc / kiss_fftr_alloc) - never a
 * side recomputation. Every stored twiddle (r and i = 2
 * fields) is compared bit-for-bit against correctly rounded
 * sinpi/cospi of the exact cycle argument as a rational,
 * decided by MPFR's native mpfr_sinpi/mpfr_cospi at 256-bit
 * precision. p==0 keeps the patched expression's signed
 * zero: caller passes p as 0 and neg_zero per direction
 * (the patched alloc phase is -2.0*0/nfft = -0.0; the
 * inverse branch negates it to +0.0).
 *
 * What it needs:
 *  - a Fork-B-patched KissFFT 131.2.0 tree from
 *    demo/make_kissfft_tree.py (pass its path as TREE),
 *  - MPFR 4.2.2 (libmpfr + libgmp),
 *  - the library core + compat sources and a host shim for
 *    msf_wrap_state (demo/kissfft_host_shim.c).
 *
 * Build + run (Git Bash, from the repository root; MSF cc/grep):
 *  TREE=demo/cache/kissfft-tree  # from make_kissfft_tree.py
 *  WT=.  # this repository root
 *  CORE="$WT/src/msf16.c $WT/src/msf32.c $WT/src/msf64.c \
 *    $WT/src/msf_flags.c $WT/src/msf_wide.c \
 *    $WT/src/msf_roundpack.c $WT/src/msf_string.c \
 *    $WT/src/msf_math.c"
 *  gcc -std=c11 -O2 -Wall -Wextra -ffp-contract=off \
 *    -fno-fast-math -Dkiss_fft_scalar=double \
 *    -I$WT -I$WT/compat -I$TREE \
 *    demo/twiddle_gate.c $CORE \
 *    $WT/compat/msf_aeabi.c demo/kissfft_host_shim.c \
 *    -Wl,--wrap=sinpi,--wrap=cospi,--wrap=floor \
 *    -lm -lmpfr -lgmp -o /tmp/twiddle_gate.exe
 *  /tmp/twiddle_gate.exe
 *
 * Expected output (recorded 2026-10-28, re-run 2026-10-29):
 *  mpfr 4.2.2
 *  PROVENANCE checked_fields=8856 mismatches=0
 * Any other result is a failure of the twiddle claim, not of
 * the comparison: the decider is MPFR, never host libm.
 *
 * Coverage: N=1024 exhaustive fwd+inv incl. fftr
 * super-twiddles; N=4096 sampled stride 37 (every 37th index
 * plus both ends); N=256 exhaustive fwd-only. Field census:
 * 1024: complex 2*1024*2=4096 + fftr 2*(512*2+256*2)=3072
 * = 7168; 4096: complex 2*112*2=448 + fftr 2*(57+29)*2=344
 * = 792; 256 fwd: 256*2 + (128*2+64*2) = 512+384 = 896.
 * Total 7168+792+896 = 8856. See docs/TWIDDLES.md.
 */
/* gate_main.c - twiddle provenance gate (scratch).
 * Includes the patched kiss_fft.c / kiss_fftr.c so the actual
 * runtime-produced twiddle tables are inspected, and compares
 * every stored twiddle against MPFR (256-bit) correctly rounded
 * sinpi/cospi of the exact cycle argument as a rational. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mpfr.h>
#include "kiss_fft.c"
#include "kiss_fftr.c"

static uint64_t d2u(double v) { uint64_t u; memcpy(&u, &v, 8); return u; }

/* Correctly rounded sinpi(p/q) / cospi(p/q) as double bits, via
 * MPFR's native sinpi/cospi at 256 bits (exact at quarter points,
 * unlike sin(pi_256 * x)). p==0 keeps the patched expression's
 * signed zero: caller passes p as 0 and neg_zero per direction. */
static uint64_t mpfr_sinpi_bits(long p, long q, int is_cos, int neg_zero)
{
    mpfr_t x, z;
    double d;
    mpfr_inits2(256, x, z, (mpfr_ptr)0);
    mpfr_set_si(x, p, MPFR_RNDN);
    mpfr_div_si(x, x, q, MPFR_RNDN); /* exact: p/q dyadic at our q */
    if (p == 0 && neg_zero) mpfr_neg(x, x, MPFR_RNDN);
    if (is_cos) mpfr_cospi(z, x, MPFR_RNDN);
    else mpfr_sinpi(z, x, MPFR_RNDN);
    d = mpfr_get_d(z, MPFR_RNDN);
    mpfr_clears(x, z, (mpfr_ptr)0);
    return d2u(d);
}

static long g_mismatch, g_checked;

static void check_cpx(const char *tag, int idx, kiss_fft_cpx t,
                      long p, long q, int neg_zero)
{
    uint64_t wr = mpfr_sinpi_bits(p, q, 1, neg_zero);
    uint64_t wi = mpfr_sinpi_bits(p, q, 0, neg_zero);
    g_checked += 2;
    if (d2u(t.r) != wr || d2u(t.i) != wi) {
        if (g_mismatch < 10)
            printf("MISMATCH %s[%d] got r=%016llx i=%016llx want r=%016llx i=%016llx\n",
                   tag, idx, (unsigned long long)d2u(t.r),
                   (unsigned long long)d2u(t.i),
                   (unsigned long long)wr, (unsigned long long)wi);
        g_mismatch++;
    }
}

static void gate_complex(int n, int inv, int stride)
{
    kiss_fft_cfg cfg = kiss_fft_alloc(n, inv, NULL, NULL);
    int i;
    if (!cfg) { printf("GATE ALLOC FAIL\n"); exit(1); }
    for (i = 0; i < n; i++) {
        long p;
        if (stride > 1 && i % stride != 0 && i != n - 1) continue;
        /* patched alloc argument: phase = -2i/n, negated if inv */
        p = inv ? 2L * i : -2L * i;
        /* phase=-2.0*0/n is -0.0; inverse negates it to +0.0 */
        check_cpx(inv ? "ctw-inv" : "ctw-fwd", i, cfg->twiddles[i], p, n,
                  !inv);
    }
    free(cfg);
}

static void gate_fftr(int n, int inv, int stride)
{
    kiss_fftr_cfg cfg = kiss_fftr_alloc(n, inv, NULL, NULL);
    int m = n / 2, i;
    if (!cfg) { printf("GATE ALLOC FAIL\n"); exit(1); }
    /* substate twiddles */
    for (i = 0; i < m; i++) {
        long p;
        if (stride > 1 && i % stride != 0 && i != m - 1) continue;
        p = inv ? 2L * i : -2L * i;
        check_cpx(inv ? "subtw-inv" : "subtw-fwd", i,
                  cfg->substate->twiddles[i], p, m, !inv);
    }
    /* super_twiddles: argument -((i+1)/m + 1/2) = -(2(i+1)+m)/(2m),
     * negated if inv. As p/q with q=2m (still dyadic-exact). */
    for (i = 0; i < m / 2; i++) {
        long p = -(2L * (i + 1) + m);
        if (stride > 1 && i % stride != 0 && i != m / 2 - 1) continue;
        if (inv) p = -p;
        check_cpx(inv ? "suptw-inv" : "suptw-fwd", i,
                  cfg->super_twiddles[i], p, 2L * m, 0);
    }
    free(cfg);
}

int main(void)
{
    printf("mpfr %s\n", mpfr_get_version());
    gate_complex(1024, 0, 1);
    gate_complex(1024, 1, 1);
    gate_fftr(1024, 0, 1);
    gate_fftr(1024, 1, 1);
    gate_complex(4096, 0, 37);
    gate_complex(4096, 1, 37);
    gate_fftr(4096, 0, 37);
    gate_fftr(4096, 1, 37);
    gate_complex(256, 0, 1);
    gate_fftr(256, 0, 1);
    printf("PROVENANCE checked_fields=%ld mismatches=%ld\n",
           g_checked, g_mismatch);
    return g_mismatch ? 1 : 0;
}
