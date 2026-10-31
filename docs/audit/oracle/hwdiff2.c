/* hwdiff2.c - audit differential part 2: comparisons, min/max, totalOrder,
 * payload ops, remainder, nextUp/Down, logB, scaleB, class/predicates,
 * sign ops. References: glibc C23 functions (x86-64) and direct rules. */
#define _GNU_SOURCE
#define __STDC_WANT_IEC_60559_BFP_EXT__ 1
#define __STDC_WANT_IEC_60559_EXT__ 1
#include "hwcore.h"

typedef int (*cfn)(uint64_t, uint64_t, msf_flags_t *);
typedef uint64_t (*mfn)(uint64_t, uint64_t, msf_flags_t *);
typedef struct { const char *n; int a, b; const char *rel; int sig; cfn f; } CmpEnt;
typedef struct { const char *n; int d, kind; mfn f; } MmEnt;
#include "wrappers3.h"

static long g_mism = 0, g_checked = 0;
#define REPORT(...) do { g_mism++; if (printed++ < 6) { printf("  MISMATCH "); printf(__VA_ARGS__); printf("\n"); } } while (0)

static uint64_t gen_cmp(const Fmt *f, uint64_t other_bits, int other_w) {
    (void)other_bits; (void)other_w;
    uint64_t v = gen_val(f);
    if (rnd() % 8 == 0) { uint64_t m = rnd() & f->mmask; if (!m) m = 1; v = ((rnd() & 1) ? f->sign : 0) | f->emask | m; }
    return v;
}

static void test_cmps(long n) {
    for (size_t i = 0; i < sizeof CMPS / sizeof CMPS[0]; i++) {
        const CmpEnt *e = &CMPS[i];
        const Fmt *fa = FMT(e->a), *fb = FMT(e->b);
        int printed = 0; long m0 = g_mism;
        for (long k = 0; k < n; k++) {
            uint64_t a = gen_cmp(fa, 0, 0), b;
            int r = rnd() % 4;
            if (r == 0 && e->a == e->b) b = gen_rel(fb, a);
            else if (r == 1) { /* same value in the other format when representable */
                double x = b2d(e->a, a); uint32_t fl;
                b = (e->b == 64) ? d2u(x) : round_from_double(x, e->b, (int)(rnd() % 4), &fl);
                if (b_isnan(fa, a)) b = gen_cmp(fb, 0, 0);
            } else b = gen_cmp(fb, 0, 0);
            int an = b_isnan(fa, a), bn = b_isnan(fb, b);
            int unord = an || bn, lt = 0, eq = 0, gt = 0;
            if (!unord) { double x = b2d(e->a, a), y = b2d(e->b, b); lt = x < y; eq = x == y; gt = x > y; }
            int exp = 0;
            for (const char *p = e->rel; *p; p++) {
                if (*p == 'L' && lt) exp = 1; if (*p == 'G' && gt) exp = 1; if (*p == 'E' && eq) exp = 1; if (*p == 'U' && unord) exp = 1;
            }
            uint32_t efl = 0;
            if (b_issnan(fa, a) || b_issnan(fb, b)) efl = MSF_FLAG_INVALID;
            if (e->sig && unord) efl = MSF_FLAG_INVALID;
            msf_flags_t fl = 0; int got = e->f(a, b, &fl);
            g_checked++;
            if ((got != 0) != exp || fl != efl) REPORT("%s %llx %llx -> got %d fl=%02x expected %d fl=%02x", e->n, (unsigned long long)a, (unsigned long long)b, got, fl, exp, efl);
        }
        if (g_mism != m0) printf("%s: %ld mismatches\n", e->n, g_mism - m0);
    }
}

/* glibc reference for the 9.6 family, computed in double (exact for all three formats when no NaN) */
static double mm_ref(int kind, double x, double y) {
    switch (kind) {
    case 0: return fminimum(x, y); case 1: return fmaximum(x, y);
    case 2: return fminimum_num(x, y); case 3: return fmaximum_num(x, y);
    case 4: return fminimum_mag(x, y); case 5: return fmaximum_mag(x, y);
    case 6: return fminimum_mag_num(x, y); default: return fmaximum_mag_num(x, y);
    }
}
static long mm_nan_payload_other = 0;
static void test_mms(long n) {
    for (size_t i = 0; i < sizeof MMS / sizeof MMS[0]; i++) {
        const MmEnt *e = &MMS[i];
        const Fmt *f = FMT(e->d);
        int printed = 0; long m0 = g_mism;
        int number = (e->kind == 2 || e->kind == 3 || e->kind == 6 || e->kind == 7);
        for (long k = 0; k < n; k++) {
            uint64_t a = gen_cmp(f, 0, 0), b = (rnd() & 1) ? gen_rel(f, a) : gen_cmp(f, 0, 0);
            if (rnd() % 16 == 0) { a &= ~f->sign & f->all; b = a | f->sign; if (rnd() & 1) { uint64_t t = a; a = b; b = t; } } /* +-x pairs incl. +-0 */
            msf_flags_t fl = 0; uint64_t got = e->f(a, b, &fl);
            int an = b_isnan(f, a), bn = b_isnan(f, b);
            uint32_t efl = (b_issnan(f, a) || b_issnan(f, b)) ? MSF_FLAG_INVALID : 0;
            uint64_t exp;
            g_checked++;
            if (an || bn) {
                if (number && !(an && bn)) exp = an ? b : a;
                else {
                    /* both NaN, or a NaN-propagating op: a NaN; payload per project rule (first sNaN, else first qNaN) */
                    uint64_t pick = b_issnan(f, a) ? a : b_issnan(f, b) ? b : an ? a : b;
                    exp = b_nanconv(f, f, pick);
                    if (!b_isnan(f, got) || fl != efl) { REPORT("%s %llx %llx -> got %llx fl=%02x expected NaN fl=%02x", e->n, (unsigned long long)a, (unsigned long long)b, (unsigned long long)got, fl, efl); }
                    else if (got != exp) mm_nan_payload_other++;
                    continue;
                }
            } else {
                double x = b2d(e->d, a), y = b2d(e->d, b), r = mm_ref(e->kind, x, y); uint32_t d;
                exp = (e->d == 64) ? d2u(r) : round_from_double(r, e->d, 0, &d);
            }
            if (got != exp || fl != efl) REPORT("%s %llx %llx -> got %llx fl=%02x expected %llx fl=%02x", e->n, (unsigned long long)a, (unsigned long long)b, (unsigned long long)got, fl, (unsigned long long)exp, efl);
        }
        if (g_mism != m0) printf("%s: %ld mismatches\n", e->n, g_mism - m0);
    }
}

/* total order per 754-2019 5.10 on encodings (direct rule) */
static int tot_ref(const Fmt *f, uint64_t a, uint64_t b, int mag) {
    if (mag) { a &= ~f->sign & f->all; b &= ~f->sign & f->all; }
    int sa = (a & f->sign) != 0, sb = (b & f->sign) != 0;
    uint64_t ma = a & ~f->sign & f->all, mb = b & ~f->sign & f->all;
    if (sa != sb) return sa; /* negative before positive */
    if (!sa) return ma <= mb;   /* positive: magnitude order of encodings is totalOrder (qNaN > sNaN > inf, payload order) */
    return ma >= mb;
}

int main(int argc, char **argv) {
    long scale = argc > 1 ? atol(argv[1]) : 1;
    seed(argc > 2 ? strtoull(argv[2], 0, 0) : 777);
    int printed; long negz = 0;

    test_cmps(20000 * scale);
    printf("[cmp] checked=%ld mism=%ld\n", g_checked, g_mism); fflush(stdout);
    test_mms(60000 * scale);
    printf("[minmax] checked=%ld mism=%ld (NaN payload differs from first-sNaN rule: %ld)\n", g_checked, g_mism, mm_nan_payload_other); fflush(stdout);

    /* totalOrder / totalOrderMag vs glibc (f32/f64) and the direct rule (all) */
    printed = 0;
    for (long k = 0; k < 200000 * scale; k++) {
        uint64_t a = gen_cmp(&FM64, 0, 0), b = (rnd() & 1) ? gen_rel(&FM64, a) : gen_cmp(&FM64, 0, 0);
        double x = u2d(a), y = u2d(b);
        int g = totalorder(&x, &y) != 0, gm = totalordermag(&x, &y) != 0;
        int l = msf64_total_order(a, b) != 0, lm = msf64_total_order_mag(a, b) != 0;
        int r = tot_ref(&FM64, a, b, 0), rm = tot_ref(&FM64, a, b, 1);
        g_checked++;
        if (l != g || lm != gm || l != r || lm != rm) REPORT("msf64_total_order %llx %llx lib=%d,%d glibc=%d,%d rule=%d,%d", (unsigned long long)a, (unsigned long long)b, l, lm, g, gm, r, rm);
        uint64_t a32 = gen_cmp(&FM32, 0, 0), b32 = (rnd() & 1) ? gen_rel(&FM32, a32) : gen_cmp(&FM32, 0, 0);
        float xf = u2f((uint32_t)a32), yf = u2f((uint32_t)b32);
        g = totalorderf(&xf, &yf) != 0; gm = totalordermagf(&xf, &yf) != 0;
        l = msf32_total_order((msf32_t)a32, (msf32_t)b32) != 0; lm = msf32_total_order_mag((msf32_t)a32, (msf32_t)b32) != 0;
        if (l != g || lm != gm) REPORT("msf32_total_order %llx %llx lib=%d,%d glibc=%d,%d", (unsigned long long)a32, (unsigned long long)b32, l, lm, g, gm);
    }
    for (uint32_t a = 0; a < 65536; a += 1) for (uint32_t b = (a * 7919u) & 0xFFFF, j = 0; j < 64; j++, b = (b * 40503u + 1) & 0xFFFF) {
        int l = msf16_total_order((msf16_t)a, (msf16_t)b) != 0, lm = msf16_total_order_mag((msf16_t)a, (msf16_t)b) != 0;
        int r = tot_ref(&FM16, a, b, 0), rm = tot_ref(&FM16, a, b, 1);
        g_checked++;
        if (l != r || lm != rm) REPORT("msf16_total_order %x %x lib=%d,%d rule=%d,%d", a, b, l, lm, r, rm);
    }
    printf("[totalorder] checked=%ld mism=%ld\n", g_checked, g_mism); fflush(stdout);

    /* payload operations vs glibc (f32/f64) */
    printed = 0;
    for (long k = 0; k < 200000 * scale; k++) {
        uint64_t a = gen_cmp(&FM64, 0, 0);
        double x = u2d(a), r;
        r = getpayload(&x); uint64_t lib = msf64_get_payload(a); g_checked++;
        if (lib != d2u(r)) REPORT("msf64_get_payload %llx lib=%llx glibc=%llx", (unsigned long long)a, (unsigned long long)lib, (unsigned long long)d2u(r));
        /* candidate payload values: small integers, non-integers, negatives, large */
        double pv;
        switch (rnd() % 6) { case 0: pv = (double)(rnd() % 4096); break; case 1: pv = (double)(rnd() & ((1ull << 51) - 1)); break;
        case 2: pv = ldexp(1.0, 51) + (double)(rnd() % 4); break; case 3: pv = -(double)(rnd() % 8); break; case 4: pv = (double)(rnd() % 100) + 0.5; break; default: pv = x; }
        uint64_t pb = d2u(pv);
        double out = 0; setpayload(&out, pv); lib = msf64_set_payload(pb); g_checked++;
        if (pb == 0x8000000000000000ull) negz++; else if (lib != d2u(out)) REPORT("msf64_set_payload %llx lib=%llx glibc=%llx", (unsigned long long)pb, (unsigned long long)lib, (unsigned long long)d2u(out));
        out = 0; setpayloadsig(&out, pv); lib = msf64_set_payload_signaling(pb); g_checked++;
        if (pb != 0x8000000000000000ull && lib != d2u(out)) REPORT("msf64_set_payload_signaling %llx lib=%llx glibc=%llx", (unsigned long long)pb, (unsigned long long)lib, (unsigned long long)d2u(out));
        float xf = u2f((uint32_t)gen_cmp(&FM32, 0, 0)), rf = getpayloadf(&xf);
        uint32_t lf = msf32_get_payload(f2u(xf)); g_checked++;
        if (lf != f2u(rf)) REPORT("msf32_get_payload %x lib=%x glibc=%x", f2u(xf), lf, f2u(rf));
        float pf = (float)((rnd() & 1) ? (double)(rnd() % (1u << 23)) : pv), of = 0; setpayloadf(&of, pf);
        lf = msf32_set_payload(f2u(pf)); g_checked++;
        if (f2u(pf) == 0x80000000u) negz++; else if (lf != f2u(of)) REPORT("msf32_set_payload %x lib=%x glibc=%x", f2u(pf), lf, f2u(of));
        of = 0; setpayloadsigf(&of, pf); lf = msf32_set_payload_signaling(f2u(pf)); g_checked++;
        if (f2u(pf) != 0x80000000u && lf != f2u(of)) REPORT("msf32_set_payload_signaling %x lib=%x glibc=%x", f2u(pf), lf, f2u(of));
    }
    printf("[payload] checked=%ld mism=%ld (setPayload(-0) differences excluded: %ld)\n", g_checked, g_mism, negz); fflush(stdout);

    /* remainder, nextUp/Down, logB: f64 & f32 random, f16 exhaustive-ish */
    printed = 0;
    for (long k = 0; k < 300000 * scale; k++) {
        for (int w = 32; w <= 64; w += 32) {
            const Fmt *f = FMT(w);
            uint64_t a = gen_cmp(f, 0, 0), b = (rnd() & 1) ? gen_rel(f, a) : gen_cmp(f, 0, 0);
            msf_flags_t fl = 0; uint64_t got;
            int an = b_isnan(f, a), bn = b_isnan(f, b);
            /* remainder */
            got = (w == 64) ? msf64_remainder(a, b, &fl) : msf32_remainder((msf32_t)a, (msf32_t)b, &fl);
            g_checked++;
            if (an || bn) {
                uint32_t efl = (b_issnan(f, a) || b_issnan(f, b)) ? MSF_FLAG_INVALID : 0;
                if (!b_isnan(f, got) || fl != efl) REPORT("remainder%d %llx %llx -> %llx fl=%02x (NaN expected fl=%02x)", w, (unsigned long long)a, (unsigned long long)b, (unsigned long long)got, fl, efl);
            } else {
                double x = b2d(w, a), y = b2d(w, b), r = (w == 64) ? remainder(x, y) : (double)remainderf((float)x, (float)y);
                uint32_t efl = (isinf(x) || y == 0) ? MSF_FLAG_INVALID : 0; uint64_t exp;
                if (efl) exp = b_defnan(f); else exp = (w == 64) ? d2u(r) : f2u((float)r);
                if (got != exp || fl != efl) REPORT("remainder%d %llx %llx -> %llx fl=%02x expected %llx fl=%02x", w, (unsigned long long)a, (unsigned long long)b, (unsigned long long)got, fl, (unsigned long long)exp, efl);
            }
            /* nextUp / nextDown */
            for (int dir = 0; dir < 2; dir++) {
                fl = 0;
                got = (w == 64) ? (dir ? msf64_next_down(a, &fl) : msf64_next_up(a, &fl)) : (dir ? msf32_next_down((msf32_t)a, &fl) : msf32_next_up((msf32_t)a, &fl));
                g_checked++;
                uint32_t efl = b_issnan(f, a) ? MSF_FLAG_INVALID : 0;
                if (an) { if (got != b_nanconv(f, f, a) || fl != efl) REPORT("next%s%d %llx -> %llx fl=%02x", dir ? "Down" : "Up", w, (unsigned long long)a, (unsigned long long)got, fl); continue; }
                uint64_t exp = (w == 64) ? d2u(dir ? nextdown(u2d(a)) : nextup(u2d(a))) : f2u(dir ? nextdownf(u2f((uint32_t)a)) : nextupf(u2f((uint32_t)a)));
                if (got != exp || fl != efl) REPORT("next%s%d %llx -> %llx fl=%02x expected %llx", dir ? "Down" : "Up", w, (unsigned long long)a, (unsigned long long)got, fl, (unsigned long long)exp);
            }
            /* logB (result in binary64) */
            fl = 0; got = (w == 64) ? msf64_log_b(a, &fl) : msf32_log_b((msf32_t)a, &fl);
            g_checked++;
            if (an) { if (!b_isnan(&FM64, got) || fl != (b_issnan(f, a) ? MSF_FLAG_INVALID : 0u)) REPORT("logB%d %llx -> %llx fl=%02x", w, (unsigned long long)a, (unsigned long long)got, fl); }
            else {
                double x = b2d(w, a); hw_begin(0); double r = logb(x); uint32_t efl = hw_end() & (MSF_FLAG_DIVISION_BY_ZERO | MSF_FLAG_INVALID);
                if (got != d2u(r) || fl != efl) REPORT("logB%d %llx -> %llx fl=%02x expected %llx fl=%02x", w, (unsigned long long)a, (unsigned long long)got, fl, (unsigned long long)d2u(r), efl);
            }
            /* scaleB with integral binary64 n */
            int64_t n = (rnd() % 4 == 0) ? (int64_t)(rnd() % 4400) - 2200 : (int64_t)(rnd() % 120) - 60;
            if (w == 32 && (n > 400 || n < -400)) n = n % 400;
            for (int m = 0; m < 5; m++) {
                fl = 0;
                got = (w == 64) ? msf64_scale_b(a, d2u((double)n), (msf_rounding_t)m, &fl) : msf32_scale_b((msf32_t)a, d2u((double)n), (msf_rounding_t)m, &fl);
                g_checked++;
                if (an) { if (got != b_nanconv(f, f, a) || fl != (b_issnan(f, a) ? MSF_FLAG_INVALID : 0u)) REPORT("scaleB%d %llx n=%lld -> %llx fl=%02x", w, (unsigned long long)a, (long long)n, (unsigned long long)got, fl); continue; }
                double x = b2d(w, a); uint64_t exp; uint32_t efl;
                if (w == 32) { double v = ldexp(x, (int)n); exp = round_from_double(v, 32, m, &efl); }
                else {
                    int mm = m;
                    if (m == 4) { /* ties-away: tie iff the shifted-out bits are exactly one half */
                        int tie = 0;
                        if (x != 0 && !isinf(x)) {
                            int ex; double fr = frexp(fabs(x), &ex); uint64_t M = (uint64_t)ldexp(fr, 53); int e2 = ex - 53 + (int)n; /* value = M * 2^e2 */
                            int sh = -1074 - e2; if (sh > 0 && sh <= 64) { uint64_t dropped = sh == 64 ? M : (M & ((1ull << sh) - 1)); tie = dropped == (1ull << (sh - 1)); }
                        }
                        mm = tie ? (signbit(x) ? 3 : 2) : 0;
                    }
                    hw_begin(mm); double r = scalbn(x, (int)n); efl = hw_end(); exp = d2u(r);
                }
                if (got != exp || fl != efl) REPORT("scaleB%d %s %llx n=%lld -> %llx fl=%02x expected %llx fl=%02x", w, MN[m], (unsigned long long)a, (long long)n, (unsigned long long)got, fl, (unsigned long long)exp, efl);
            }
        }
    }
    printf("[rem/next/logb/scaleb f32,f64] checked=%ld mism=%ld\n", g_checked, g_mism); fflush(stdout);

    /* class, predicates, sign ops: exhaustive f16, random f32/f64 */
    printed = 0;
    for (long k = 0; k < 65536 + 400000 * scale; k++) {
        int w = k < 65536 ? 16 : (k & 1) ? 32 : 64; const Fmt *f = FMT(w);
        uint64_t a = k < 65536 ? (uint64_t)k : gen_cmp(f, 0, 0), b = gen_cmp(f, 0, 0);
        int nan = b_isnan(f, a), sn = b_issnan(f, a), inf = b_isinf(f, a), zero = b_iszero(f, a);
        int sub = !zero && (a & f->emask) == 0, neg = (a & f->sign) != 0, normal = !nan && !inf && !zero && !sub;
        int cls = sn ? 0 : nan ? 1 : inf ? (neg ? 2 : 9) : normal ? (neg ? 3 : 8) : sub ? (neg ? 4 : 7) : (neg ? 5 : 6);
        int lc, ln, lf, lz, ls, li, lnan, lsig, lcan, lneg, lrad;
        uint64_t cp, ng, ab, cs;
        if (w == 16) { lc = msf16_class(a); ln = msf16_is_normal(a); lf = msf16_is_finite(a); lz = msf16_is_zero(a); ls = msf16_is_subnormal(a); li = msf16_is_infinite(a); lnan = msf16_is_nan(a); lsig = msf16_is_signaling(a); lcan = msf16_is_canonical(a); lneg = msf16_is_sign_minus(a); lrad = msf16_radix(a); cp = msf16_copy(a); ng = msf16_negate(a); ab = msf16_abs(a); cs = msf16_copy_sign(a, b); }
        else if (w == 32) { lc = msf32_class(a); ln = msf32_is_normal(a); lf = msf32_is_finite(a); lz = msf32_is_zero(a); ls = msf32_is_subnormal(a); li = msf32_is_infinite(a); lnan = msf32_is_nan(a); lsig = msf32_is_signaling(a); lcan = msf32_is_canonical(a); lneg = msf32_is_sign_minus(a); lrad = msf32_radix(a); cp = msf32_copy(a); ng = msf32_negate(a); ab = msf32_abs(a); cs = msf32_copy_sign(a, b); }
        else { lc = msf64_class(a); ln = msf64_is_normal(a); lf = msf64_is_finite(a); lz = msf64_is_zero(a); ls = msf64_is_subnormal(a); li = msf64_is_infinite(a); lnan = msf64_is_nan(a); lsig = msf64_is_signaling(a); lcan = msf64_is_canonical(a); lneg = msf64_is_sign_minus(a); lrad = msf64_radix(a); cp = msf64_copy(a); ng = msf64_negate(a); ab = msf64_abs(a); cs = msf64_copy_sign(a, b); }
        g_checked++;
        if (lc != cls || !!ln != normal || !!lf != (!nan && !inf) || !!lz != zero || !!ls != sub || !!li != inf || !!lnan != nan || !!lsig != sn || lcan != 1 || !!lneg != neg || lrad != 2)
            REPORT("class/pred f%d %llx: class %d/%d", w, (unsigned long long)a, lc, cls);
        if (cp != a || ng != ((a ^ f->sign) & f->all) || ab != (a & ~f->sign & f->all) || cs != ((a & ~f->sign & f->all) | (b & f->sign)))
            REPORT("signops f%d %llx %llx", w, (unsigned long long)a, (unsigned long long)b);
    }
    printf("[class/pred/signops] checked=%ld mism=%ld\n", g_checked, g_mism);
    printf("version predicates: msf_1985=%d msf_2008=%d msf_2019=%d f16(1985,2008,2019)=%d,%d,%d\n", msf_is754version1985(), msf_is754version2008(), msf_is754version2019(), msf16_is754version1985(), msf16_is754version2008(), msf16_is754version2019());
    printf("TOTAL checked=%ld mismatches=%ld\n", g_checked, g_mism);
    return g_mism != 0;
}
