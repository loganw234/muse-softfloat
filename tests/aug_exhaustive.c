/* aug_exhaustive.c - host differential harness for the
 * Clause 9.5 augmented bundle at binary16 (SF-2 Step 4;
 * NOT part of the shipped library, never linked into it).
 *
 * The reference here is an independent exact-integer
 * restatement for binary16 only: operands decode to
 * (sign, mag, exp) over host unsigned __int128, the exact
 * sum/difference/product is formed at a common scale (the
 * binary16 span is at most 40 bits, so no window argument
 * is needed), the head is rounded by an integer
 * grid-division implementation of roundTiesTowardZero
 * written for this file, the tail is the exact integer
 * residual (or its own grid rounding in the mul
 * below-step cell), and flags follow the ratified table
 * (pin P1 = R2: an exact tiny residual raises nothing).
 * It shares no code with src/msf_aug.c.
 *
 * Modes:
 *   pool               every binary16 first operand x the
 *                      boundary pool below, all three ops
 *                      (standing leg, run by standard)
 *   pairs OP LO HI     op in add|sub|mul, first operands
 *                      in [LO, HI), every second operand
 *                      (the one-time 2^32-per-name run is
 *                      256 shards of this shape per op)
 * Counts are printed by reference kind; any mismatch
 * prints the case and the run exits nonzero. The harness
 * allocates nothing (O(1) memory) and lowers its own
 * priority class on Windows (shared-machine courtesy).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#ifdef _WIN32
#include <windows.h>
#endif
#include "../include/muse_softfloat.h"

typedef unsigned __int128 u128;

enum { K_SNAN, K_QNAN, K_INVALID, K_INF, K_OVERFLOW,
       K_ZERO, K_EXACT, K_PAIR, K_TINY, K_MULINEXACT, K_N };
static const char *const KIND_NAMES[K_N] = {
    "snan", "qnan", "invalid", "inf-exact", "overflow",
    "exact-zero", "exact", "pair-exact", "tiny-exact",
    "mul-inexact-tail"
};

#define F16_SIGN 0x8000u
#define F16_INF 0x7c00u
#define F16_QBIT 0x0200u
#define F16_QNAN 0x7e00u
#define P16 11
#define EMIN16 (-14)
#define EMAX16 15
#define U0E16 (-24)

static int blen128(u128 x)
{
    int n = 0;
    while (x != 0) {
        n++;
        x >>= 1;
    }
    return n;
}

struct dec { int cls; /*0 zero 1 finite 2 inf 3 qnan 4 snan*/
             int sign; uint64_t mag; int exp; };

static struct dec dec16(uint32_t bits)
{
    struct dec d;
    uint32_t e = (bits >> 10) & 0x1fu, f = bits & 0x3ffu;
    d.sign = (bits & F16_SIGN) != 0;
    if (e == 0x1fu) {
        d.mag = f; d.exp = 0;
        d.cls = f == 0 ? 2 : ((f & F16_QBIT) ? 3 : 4);
    } else if (e == 0) {
        d.mag = f; d.exp = U0E16; d.cls = f == 0 ? 0 : 1;
    } else {
        d.mag = 0x400u | f; d.exp = (int)e - 15 - 10; d.cls = 1;
    }
    return d;
}

/* Encode (-1)^sign * mag * 2^exp exactly, or -1. */
static long encode128(int sign, u128 mag, int exp)
{
    int top, step, sh;
    uint64_t m;
    if (mag == 0) {
        return sign ? F16_SIGN : 0;
    }
    top = exp + blen128(mag) - 1;
    if (top > EMAX16) {
        return -1;
    }
    step = top - P16 + 1 > U0E16 ? top - P16 + 1 : U0E16;
    sh = step - exp;
    if (sh > 0) {
        if (mag & (((u128)1 << sh) - 1)) {
            return -1;
        }
        m = (uint64_t)(mag >> sh);
    } else {
        m = (uint64_t)(mag << (-sh));
    }
    if (m >= (1u << P16)) {
        return -1;
    }
    if (m < (1u << (P16 - 1))) {
        return step == U0E16 ? (long)((sign ? F16_SIGN : 0) | m) : -1;
    }
    while (m < (1u << (P16 - 1))) {
        m <<= 1;
    }
    return (long)((sign ? F16_SIGN : 0)
                  | ((uint32_t)(top + 15) << 10) | (m - 0x400u));
}

/* RTTZ rounding by grid division. Returns bits, or -1 for
 * overflow (magnitude strictly above the 9.5 threshold). */
static long round128(int sign, u128 mag, int exp)
{
    int top, step, sh;
    u128 q;
    if (mag == 0) {
        return sign ? F16_SIGN : 0;
    }
    top = exp + blen128(mag) - 1;
    if (top > EMAX16) {
        return -1;
    }
    step = top - P16 + 1 > U0E16 ? top - P16 + 1 : U0E16;
    sh = step - exp;
    if (sh <= 0) {
        q = mag << (-sh);
    } else {
        u128 rem;
        q = mag >> sh;
        rem = mag - (q << sh);
        if (rem > ((u128)1 << (sh - 1))) { /* tie stays */
            q += 1;
            if (blen128(q) > P16 && top >= EMIN16) {
                q >>= 1;
                step++;
                top++;
                if (top > EMAX16) {
                    return -1;
                }
            }
        }
    }
    return encode128(sign, q, step);
}

static void ref_aug(uint32_t abits, uint32_t bbits, int op,
                    uint32_t *head, uint32_t *tail,
                    uint32_t *flags, int *kind)
{
    struct dec da = dec16(abits), db = dec16(bbits);
    int eff_b = db.sign ^ (op == 1);
    int i;
    *flags = 0;
    for (i = 0; i < 2; i++) {
        struct dec d = i == 0 ? da : db;
        uint32_t bits = i == 0 ? abits : bbits;
        if (d.cls == 4) {
            *head = *tail = bits | F16_QBIT;
            *flags = MSF_FLAG_INVALID; *kind = K_SNAN; return;
        }
    }
    for (i = 0; i < 2; i++) {
        struct dec d = i == 0 ? da : db;
        uint32_t bits = i == 0 ? abits : bbits;
        if (d.cls == 3) {
            *head = *tail = bits; *kind = K_QNAN; return;
        }
    }
    {
        int invalid = op == 2
            ? ((da.cls == 0 && db.cls == 2) || (da.cls == 2 && db.cls == 0))
            : (da.cls == 2 && db.cls == 2 && da.sign != eff_b);
        if (invalid) {
            *head = *tail = F16_QNAN;
            *flags = MSF_FLAG_INVALID; *kind = K_INVALID; return;
        }
    }
    if (da.cls == 2 || db.cls == 2) {
        int s = op == 2 ? (da.sign ^ db.sign)
                        : (da.cls == 2 ? da.sign : eff_b);
        *head = *tail = (s ? F16_SIGN : 0) | F16_INF;
        *kind = K_INF; return;
    }
    {
        u128 mag;
        int sign, exp;
        long hb, tb;
        if (op == 2) {
            sign = da.sign ^ db.sign;
            mag = (u128)da.mag * (u128)db.mag;
            exp = da.exp + db.exp;
        } else {
            int e = da.exp < db.exp ? da.exp : db.exp;
            u128 av = (u128)da.mag << (da.exp - e);
            u128 bv = (u128)db.mag << (db.exp - e);
            exp = e;
            if (da.sign == eff_b) {
                mag = av + bv; sign = da.sign;
            } else if (av >= bv) {
                mag = av - bv; sign = da.sign;
            } else {
                mag = bv - av; sign = eff_b;
            }
        }
        if (mag == 0) {
            int zs = op == 2 ? (da.sign ^ db.sign)
                : ((da.cls == 0 && db.cls == 0)
                   ? (da.sign == eff_b ? da.sign : 0) : 0);
            *head = *tail = zs ? F16_SIGN : 0;
            *kind = K_ZERO; return;
        }
        hb = round128(sign, mag, exp);
        if (hb < 0) {
            *head = *tail = (sign ? F16_SIGN : 0) | F16_INF;
            *flags = MSF_FLAG_OVERFLOW | MSF_FLAG_INEXACT;
            *kind = K_OVERFLOW; return;
        }
        *head = (uint32_t)hb;
        {
            struct dec hd = dec16(*head);
            u128 rmag;
            int rsign, rexp, er;
            if (hd.mag == 0) {
                rmag = mag; rsign = sign; rexp = exp;
            } else {
                u128 ev, hv;
                er = exp < hd.exp ? exp : hd.exp;
                ev = mag << (exp - er);
                hv = (u128)hd.mag << (hd.exp - er);
                rexp = er;
                if (ev >= hv) {
                    rmag = ev - hv; rsign = sign;
                } else {
                    rmag = hv - ev; rsign = sign ^ 1;
                }
            }
            if (rmag == 0) {
                *tail = *head & F16_SIGN; *kind = K_EXACT; return;
            }
            tb = encode128(rsign, rmag, rexp);
            if (tb >= 0) {
                int tiny = rexp + blen128(rmag) - 1 < EMIN16;
                *tail = (uint32_t)tb;
                *kind = tiny ? K_TINY : K_PAIR; /* P1: no flag */
                return;
            }
            /* mul below-step cell (asserted by kind count
             * review if it ever appears for add/sub) */
            tb = round128(rsign, rmag, rexp);
            *tail = (uint32_t)tb;
            *flags = MSF_FLAG_UNDERFLOW | MSF_FLAG_INEXACT;
            *kind = K_MULINEXACT;
        }
    }
}

static uint64_t g_total = 0, g_bad = 0;
static uint64_t g_kind[K_N];
static uint64_t g_tail_minnorm = 0, g_tail_zero_opp = 0;

static void run_case(uint32_t a, uint32_t b, int op)
{
    uint32_t rh, rt, rf;
    int kind;
    msf_flags_t fl = 0;
    msf16_pair_t r;
    ref_aug(a, b, op, &rh, &rt, &rf, &kind);
    r = op == 0 ? msf16_augmented_add((msf16_t)a, (msf16_t)b, &fl)
      : op == 1 ? msf16_augmented_sub((msf16_t)a, (msf16_t)b, &fl)
                : msf16_augmented_mul((msf16_t)a, (msf16_t)b, &fl);
    g_total++;
    g_kind[kind]++;
    if (kind == K_MULINEXACT) {
        if ((rt & 0x7fffu) == 0x0400u) {
            g_tail_minnorm++;
        }
        if ((rt & 0x7fffu) == 0 && ((rt ^ rh) & F16_SIGN) != 0) {
            g_tail_zero_opp++;
        }
    }
    if ((uint32_t)r.head != rh || (uint32_t)r.tail != rt
        || (uint32_t)fl != rf) {
        if (g_bad < 20) {
            printf("MISMATCH op=%d a=%04x b=%04x got %04x %04x/%02x"
                   " want %04x %04x/%02x kind=%s\n", op, a, b,
                   (uint32_t)r.head, (uint32_t)r.tail, (uint32_t)fl,
                   rh, rt, rf, KIND_NAMES[kind]);
        }
        g_bad++;
    }
    if (kind == K_MULINEXACT && op != 2) {
        printf("REF BUG: inexact tail for add/sub a=%04x b=%04x\n", a, b);
        g_bad++;
    }
}

static int report(const char *mode)
{
    int i;
    printf("aug_exhaustive %s: total=%llu mismatches=%llu\n", mode,
           (unsigned long long)g_total, (unsigned long long)g_bad);
    for (i = 0; i < K_N; i++) {
        printf("  kind %-16s %llu\n", KIND_NAMES[i],
               (unsigned long long)g_kind[i]);
    }
    printf("  inexact-tail-to-min-normal %llu\n",
           (unsigned long long)g_tail_minnorm);
    printf("  inexact-tail-zero-opposite-head %llu\n",
           (unsigned long long)g_tail_zero_opp);
    printf("VERDICT: %s\n", g_bad == 0 ? "PASS" : "FAIL");
    return g_bad == 0 ? 0 : 1;
}

int main(int argc, char **argv)
{
#ifdef _WIN32
    SetPriorityClass(GetCurrentProcess(), BELOW_NORMAL_PRIORITY_CLASS);
#endif
    if (argc >= 2 && strcmp(argv[1], "pool") == 0) {
        static const uint32_t pool[] = {
            0x0000, 0x8000, 0x0001, 0x8001, 0x0002, 0x0003,
            0x03ff, 0x83ff, 0x0400, 0x8400, 0x0401, 0x0800,
            0x3c00, 0xbc00, 0x3c01, 0x3fff, 0x4000, 0x7bff,
            0xfbff, 0x7c00, 0xfc00, 0x7e00, 0xfe01, 0x7c01,
            0x3555, 0xb555, 0x2e66, 0x7800
        };
        uint32_t a;
        size_t i;
        int op;
        for (a = 0; a < 65536u; a++) {
            for (i = 0; i < sizeof(pool) / sizeof(pool[0]); i++) {
                for (op = 0; op < 3; op++) {
                    run_case(a, pool[i], op);
                }
            }
        }
        return report("pool");
    }
    if (argc == 5 && strcmp(argv[1], "pairs") == 0) {
        int op = strcmp(argv[2], "add") == 0 ? 0
               : strcmp(argv[2], "sub") == 0 ? 1
               : strcmp(argv[2], "mul") == 0 ? 2 : -1;
        uint32_t lo, hi, a, b;
        char mode[64];
        if (op < 0) {
            fprintf(stderr, "bad op\n");
            return 2;
        }
        lo = (uint32_t)strtoul(argv[3], NULL, 0);
        hi = (uint32_t)strtoul(argv[4], NULL, 0);
        for (a = lo; a < hi; a++) {
            for (b = 0; b < 65536u; b++) {
                run_case(a, b, op);
            }
        }
        snprintf(mode, sizeof(mode), "pairs %s %u %u", argv[2], lo, hi);
        return report(mode);
    }
    fprintf(stderr, "usage: pool | pairs add|sub|mul LO HI\n");
    return 2;
}

