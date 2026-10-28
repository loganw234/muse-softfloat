/* explog_exhaustive.c - host differential harness for the
 * exp2/exp2m1 bundle (SF-2 Step 3a gates; NOT part of the
 * shipped library and never linked into it). The decider
 * is tests/explog_decider.c (MPFR bracket, five modes,
 * adaptive precision), included below. The kernel is
 * invoked on the original encoding in every mode; bits
 * and flags are compared.
 *
 * Modes:
 *   f16                    exhaustive binary16 sweep (all
 *                          65536 encodings, both functions)
 *   f32 LO HI [FN]         binary32 encodings in [LO, HI)
 *                          (hex), FN: 0 exp2, 1 exp2m1,
 *                          2 both (default)
 *   f64seed SEED COUNT     seeded finite binary64 patterns
 *   f32seed SEED COUNT     seeded finite binary32 patterns
 *   wc exp2|exp2m1 FILE    binary64 inputs from a .wc file
 *                          (mechanical first-token parse;
 *                          token must be an exact binary64;
 *                          optional env EXPLOG_WC_DUMP=path
 *                          dumps decided input encodings)
 *   decide                 stdin "msf64_exp2 hexbits";
 *                          stdout bits+flags te tz tp tn ta
 *                          (for tests/gen_vectors_explog.py)
 *   one FMT FN HEX         single-input verbose check
 * Exit status is nonzero on any mismatch, decider-
 * undecided input, audit failure, or final-undecided
 * kernel hit (counters build).
 */
#include "explog_decider.c"

#ifdef MSF_EXPLOG_TEST_COUNTERS
extern uint64_t msf_explog_stage_hits[3];
extern uint64_t msf_explog_final_undecided;
#endif

static uint64_t g_checked, g_mismatch;

static uint64_t x_kernel_call(int fi, int is_m1, uint64_t bits, int rm,
                              msf_flags_t *fl)
{
    *fl = 0u;
    switch (fi) {
    case 0:
        return is_m1 ? msf16_exp2m1((msf16_t)bits, (msf_rounding_t)rm, fl)
                     : msf16_exp2((msf16_t)bits, (msf_rounding_t)rm, fl);
    case 1:
        return is_m1 ? msf32_exp2m1((msf32_t)bits, (msf_rounding_t)rm, fl)
                     : msf32_exp2((msf32_t)bits, (msf_rounding_t)rm, fl);
    default:
        return is_m1 ? msf64_exp2m1(bits, (msf_rounding_t)rm, fl)
                     : msf64_exp2(bits, (msf_rounding_t)rm, fl);
    }
}

static void check_one_x(int fi, int is_m1, uint64_t bits, long p0)
{
    const xfmt_t *f = &XFMTS[fi];
    uint64_t rb[5];
    uint32_t rf[5];
    int rm;
    if (explog_expected(fi, is_m1, bits, p0, rb, rf) != 0) {
        if (g_x_undecided <= 20) {
            printf("UNDECIDED %s %s %016llx\n", f->name,
                   is_m1 ? "exp2m1" : "exp2",
                   (unsigned long long)bits);
        }
        return;
    }
    for (rm = 0; rm < 5; rm++) {
        msf_flags_t fl;
        uint64_t got = x_kernel_call(fi, is_m1, bits, rm, &fl);
        g_checked++;
        if (got != rb[rm] || (uint32_t)fl != rf[rm]) {
            g_mismatch++;
            if (g_mismatch <= 20) {
                printf("MISMATCH %s %s %s in=%016llx got=%016llx/%02x "
                       "want=%016llx/%02x\n",
                       f->name, is_m1 ? "exp2m1" : "exp2", XRM_NAME[rm],
                       (unsigned long long)bits,
                       (unsigned long long)got, (unsigned)fl,
                       (unsigned long long)rb[rm], (unsigned)rf[rm]);
            }
        }
    }
}

static int x_summary(const char *what)
{
    int bad = g_mismatch != 0 || g_x_undecided != 0 || g_x_audit_fail != 0;
#ifdef MSF_EXPLOG_TEST_COUNTERS
    printf("counters: stage hits %llu/%llu/%llu final_undecided=%llu\n",
           (unsigned long long)msf_explog_stage_hits[0],
           (unsigned long long)msf_explog_stage_hits[1],
           (unsigned long long)msf_explog_stage_hits[2],
           (unsigned long long)msf_explog_final_undecided);
    if (msf_explog_final_undecided != 0) {
        bad = 1;
    }
#endif
    printf("%s: checked=%llu mismatches=%llu undecided=%llu "
           "escalations=%llu specials=%llu shortcuts=%llu "
           "audits=%llu audit_fail=%llu -> %s\n",
           what,
           (unsigned long long)g_checked,
           (unsigned long long)g_mismatch,
           (unsigned long long)g_x_undecided,
           (unsigned long long)g_x_escal,
           (unsigned long long)g_x_special,
           (unsigned long long)g_x_shortcut,
           (unsigned long long)g_x_audit,
           (unsigned long long)g_x_audit_fail,
           bad ? "FAIL" : "PASS");
    return bad ? 1 : 0;
}

static int run_wc_x(int is_m1, const char *path)
{
    FILE *fh = fopen(path, "r");
    FILE *dump = NULL;
    const char *dump_path = getenv("EXPLOG_WC_DUMP");
    char line[512];
    uint64_t nline = 0, ntok = 0, nfin = 0, nnonfinite = 0;
    uint64_t nunparsed = 0, ninexact = 0;
    int rc;
    if (fh == NULL) {
        fprintf(stderr, "wc: cannot open %s\n", path);
        return 2;
    }
    if (dump_path != NULL) {
        dump = fopen(dump_path, "w");
        if (dump == NULL) {
            fprintf(stderr, "wc: cannot open dump %s\n", dump_path);
            fclose(fh);
            return 2;
        }
    }
    printf("wc %s from %s (mechanical parse; MPFR re-decides)\n",
           is_m1 ? "exp2m1" : "exp2", path);
    while (fgets(line, sizeof line, fh) != NULL) {
        char *hash = strchr(line, '#');
        char tok[256];
        nline++;
        if (hash != NULL) {
            *hash = '\0';
        }
        if (sscanf(line, "%255s", tok) != 1) {
            continue;
        }
        ntok++;
        {
            mpfr_t v;
            char *end = NULL;
            uint64_t rb;
            uint32_t rf;
            mpfr_init2(v, 4096);
            mpfr_strtofr(v, tok, &end, 0, MPFR_RNDN);
            if (end == tok || *end != '\0') {
                nunparsed++; /* counted only; token never printed */
                mpfr_clear(v);
                continue;
            }
            if (mpfr_nan_p(v) || mpfr_inf_p(v)) {
                nnonfinite++;
                mpfr_clear(v);
                continue;
            }
            x_narrow(&XFMTS[2], v, 0, &rb, &rf);
            mpfr_clear(v);
            if (rf != 0u) {
                ninexact++; /* token is not an exact binary64 */
                continue;
            }
            if (((rb >> 52) & 0x7ffu) == 0x7ffu) {
                nnonfinite++;
                continue;
            }
            nfin++;
            if (dump != NULL) {
                fprintf(dump, "%016llx\n", (unsigned long long)rb);
            }
            check_one_x(2, is_m1, rb, 320);
        }
    }
    fclose(fh);
    if (dump != NULL) {
        fclose(dump);
    }
    printf("wc lines=%llu tokens=%llu finite_checked_inputs=%llu "
           "nonfinite_skipped=%llu unparsed=%llu inexact_tokens=%llu\n",
           (unsigned long long)nline, (unsigned long long)ntok,
           (unsigned long long)nfin,
           (unsigned long long)nnonfinite,
           (unsigned long long)nunparsed,
           (unsigned long long)ninexact);
    rc = x_summary(is_m1 ? "wc exp2m1 f64" : "wc exp2 f64");
    if (ninexact != 0u) {
        printf("wc: inexact tokens present - coverage strictness FAIL\n");
        rc = 1;
    }
    return rc;
}

static int x_fmt_from_op(const char *op, int *fi, int *is_m1)
{
    if (strncmp(op, "msf16_", 6) == 0) { *fi = 0; }
    else if (strncmp(op, "msf32_", 6) == 0) { *fi = 1; }
    else if (strncmp(op, "msf64_", 6) == 0) { *fi = 2; }
    else { return 0; }
    if (strcmp(op + 6, "exp2") == 0) { *is_m1 = 0; }
    else if (strcmp(op + 6, "exp2m1") == 0) { *is_m1 = 1; }
    else { return 0; }
    return 1;
}

static int run_decide_x(void)
{
    char op[64], hex[32];
    while (scanf("%63s %31s", op, hex) == 2) {
        int fi = 0, is_m1 = 0, rm;
        uint64_t bits, rb[5];
        uint32_t rf[5];
        if (!x_fmt_from_op(op, &fi, &is_m1)) {
            printf("BADOP %s\n", op);
            return 2;
        }
        bits = strtoull(hex, NULL, 16);
        if (explog_expected(fi, is_m1, bits, 640, rb, rf) != 0) {
            printf("UNDECIDED %s %s\n", op, hex);
            return 1;
        }
        printf("%s %s", op, hex);
        for (rm = 0; rm < 5; rm++) {
            printf(" %llx %x", (unsigned long long)rb[rm],
                   (unsigned)rf[rm]);
        }
        printf("\n");
    }
    return 0;
}

/* splitmix64, harness-local seeded streams */
static uint64_t g_rng;
static uint64_t rng_next(void)
{
    uint64_t z = (g_rng += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}

int main(int argc, char **argv)
{
    if (argc >= 2 && strcmp(argv[1], "f16") == 0) {
        uint64_t b;
        int fn;
        for (fn = 0; fn < 2; fn++) {
            for (b = 0; b < 65536ULL; b++) {
                check_one_x(0, fn, b, 160);
            }
        }
        return x_summary("f16 exhaustive exp2+exp2m1");
    }
    if (argc >= 4 && strcmp(argv[1], "f32") == 0) {
        uint64_t lo = strtoull(argv[2], NULL, 16);
        uint64_t hi = strtoull(argv[3], NULL, 16);
        int fn = argc >= 5 ? atoi(argv[4]) : 2;
        uint64_t b;
        int f0 = fn == 2 ? 0 : fn, f1 = fn == 2 ? 1 : fn, f;
        for (f = f0; f <= f1; f++) {
            for (b = lo; b < hi; b++) {
                check_one_x(1, f, b & 0xffffffffULL, 160);
            }
        }
        printf("f32 range [%016llx,%016llx) fn=%d inputs_per_fn=%llu\n",
               (unsigned long long)lo, (unsigned long long)hi, fn,
               (unsigned long long)(hi - lo));
        return x_summary("f32 range");
    }
    if (argc >= 4 && (strcmp(argv[1], "f64seed") == 0
                      || strcmp(argv[1], "f32seed") == 0)) {
        int fi = argv[1][1] == '6' ? 2 : 1;
        uint64_t count = strtoull(argv[3], NULL, 10);
        uint64_t i;
        int fn;
        g_rng = strtoull(argv[2], NULL, 10) * 0x2545f4914f6cdd1dULL + 1u;
        for (fn = 0; fn < 2; fn++) {
            for (i = 0; i < count; i++) {
                uint64_t b = rng_next();
                if (fi == 1) {
                    b &= 0xffffffffULL;
                    if (((b >> 23) & 0xffu) == 0xffu) {
                        continue;
                    }
                } else if (((b >> 52) & 0x7ffu) == 0x7ffu) {
                    continue;
                }
                check_one_x(fi, fn, b, fi == 2 ? 192 : 160);
            }
        }
        return x_summary(argv[1]);
    }
    if (argc >= 4 && strcmp(argv[1], "wc") == 0) {
        int is_m1;
        if (strcmp(argv[2], "exp2") == 0) { is_m1 = 0; }
        else if (strcmp(argv[2], "exp2m1") == 0) { is_m1 = 1; }
        else { fprintf(stderr, "wc: bad fn\n"); return 2; }
        return run_wc_x(is_m1, argv[3]);
    }
    if (argc >= 2 && strcmp(argv[1], "decide") == 0) {
        return run_decide_x();
    }
    if (argc >= 5 && strcmp(argv[1], "one") == 0) {
        int fi = atoi(argv[2]), is_m1 = atoi(argv[3]), rm;
        uint64_t bits = strtoull(argv[4], NULL, 16);
        uint64_t rb[5];
        uint32_t rf[5];
        if (explog_expected(fi, is_m1, bits, 640, rb, rf) != 0) {
            printf("UNDECIDED\n");
            return 1;
        }
        for (rm = 0; rm < 5; rm++) {
            msf_flags_t fl;
            uint64_t got = x_kernel_call(fi, is_m1, bits, rm, &fl);
            printf("%s got=%016llx/%02x want=%016llx/%02x %s\n",
                   XRM_NAME[rm], (unsigned long long)got, (unsigned)fl,
                   (unsigned long long)rb[rm], (unsigned)rf[rm],
                   (got == rb[rm] && (uint32_t)fl == rf[rm]) ? "ok" : "BAD");
        }
        return 0;
    }
    fprintf(stderr,
            "usage: f16 | f32 LO HI [FN] | f64seed S N | f32seed S N | "
            "wc exp2|exp2m1 FILE | decide | one FI FN HEX\n");
    return 2;
}
