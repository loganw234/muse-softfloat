/* runner.c - host vector runner (SF-0 Section 5.1 front door body).
 *
 * Modes:
 *   msf_runner verify [--manifest M] [--expect-counts E] VEC...
 *   msf_runner hash VEC...     whole-run SHA-256 over canonical results
 *   msf_runner unit            flag-state machine, versions, SHA KATs
 *
 * Vector format: tests/VECTORS.md. Inventory is printed BEFORE any
 * verdict: compiler identity, op-surface counts, per-file and
 * per-provenance vector counts, skips by name with reasons, and the
 * semantics in force (tininess after rounding, SF-0 NaN matrix).
 * A green run that cannot name its vectors is a failed run.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../include/muse_softfloat.h"
#include "../src/msf_internal.h"
#include "msf_dispatch.h"
#include "sha256.h"

#ifndef MSF_BUILD_ID
#define MSF_BUILD_ID "unknown-build"
#endif

static void die(const char *msg)
{
    fprintf(stderr, "runner: %s\n", msg);
    exit(2);
}

static const msf_op_desc_t *find_op(const char *name)
{
    size_t i;
    for (i = 0; i < MSF_OP_COUNT; i++) {
        if (strcmp(MSF_OPS[i].name, name) == 0) {
            return &MSF_OPS[i];
        }
    }
    return NULL;
}

static int kind_width(uint8_t kind)
{
    switch (kind) {
    case MSF_AK_F16: case MSF_AK_I16: case MSF_AK_U16: return 16;
    case MSF_AK_F32: case MSF_AK_I32: case MSF_AK_U32: return 32;
    case MSF_AK_F64: case MSF_AK_I64: case MSF_AK_U64: return 64;
    case MSF_AK_I8: case MSF_AK_U8: return 8;
    default: return 64;
    }
}

typedef uint64_t (*fn_un_u)(uint64_t);
typedef uint32_t (*fn_un_u32)(uint32_t);
typedef uint16_t (*fn_un_u16)(uint16_t);
typedef int (*fn_un_i)(uint64_t);
typedef int (*fn_un_i32)(uint32_t);
typedef int (*fn_un_i16)(uint16_t);
typedef uint64_t (*fn_bin_u)(uint64_t, uint64_t);
typedef uint32_t (*fn_bin_u32)(uint32_t, uint32_t);
typedef uint16_t (*fn_bin_u16)(uint16_t, uint16_t);
typedef int (*fn_null_i)(void);

/* P0-implemented signature shapes only. A vector naming another shape
 * is a hard error (counted, never skipped silently). */
static int call_op(const msf_op_desc_t *op, const uint64_t *args,
                   uint64_t *result)
{
    int w = op->nargs > 0 ? kind_width(op->argkinds[0]) : 64;
    if (op->sig == MSF_SIG_VERSION_OP) {
        *result = (uint64_t)((fn_null_i)op->fn)();
        return 0;
    }
    if (op->nargs == 1 && op->retkind == op->argkinds[0]) {
        if (w == 16) { *result = ((fn_un_u16)op->fn)((uint16_t)args[0]); return 0; }
        if (w == 32) { *result = ((fn_un_u32)op->fn)((uint32_t)args[0]); return 0; }
        *result = ((fn_un_u)op->fn)(args[0]);
        return 0;
    }
    if (op->nargs == 1 && (op->sig == MSF_SIG_CLASSIFY || op->sig == MSF_SIG_CLASS_OP
                           || op->sig == MSF_SIG_RADIX_OP)) {
        if (w == 16) { *result = (uint64_t)((fn_un_i16)op->fn)((uint16_t)args[0]); return 0; }
        if (w == 32) { *result = (uint64_t)((fn_un_i32)op->fn)((uint32_t)args[0]); return 0; }
        *result = (uint64_t)((fn_un_i)op->fn)(args[0]);
        return 0;
    }
    if (op->nargs == 2 && op->sig == MSF_SIG_SIGN_BIN) {
        if (w == 16) { *result = ((fn_bin_u16)op->fn)((uint16_t)args[0], (uint16_t)args[1]); return 0; }
        if (w == 32) { *result = ((fn_bin_u32)op->fn)((uint32_t)args[0], (uint32_t)args[1]); return 0; }
        *result = ((fn_bin_u)op->fn)(args[0], args[1]);
        return 0;
    }
    return -1;
}

static int parse_rm(const char *tok, int *rm)
{
    if (strcmp(tok, "te") == 0) { *rm = MSF_IROUND_TIES_TO_EVEN; return 0; }
    if (strcmp(tok, "tz") == 0) { *rm = MSF_IROUND_TOWARD_ZERO; return 0; }
    if (strcmp(tok, "tp") == 0) { *rm = MSF_IROUND_TOWARD_POSITIVE; return 0; }
    if (strcmp(tok, "tn") == 0) { *rm = MSF_IROUND_TOWARD_NEGATIVE; return 0; }
    if (strcmp(tok, "ta") == 0) { *rm = MSF_IROUND_TIES_TO_AWAY; return 0; }
    if (strcmp(tok, "-") == 0) { *rm = -1; return 0; }
    return -1;
}

static int hex_u128(const char *s, msf_u128_t *out)
{
    msf_u128_t r = msf_u128_from_u64(0u);
    if (strlen(s) > 32u) {
        return -1;
    }
    for (; *s; s++) {
        unsigned v;
        if (*s >= '0' && *s <= '9') { v = (unsigned)(*s - '0'); }
        else if (*s >= 'a' && *s <= 'f') { v = (unsigned)(*s - 'a') + 10u; }
        else if (*s >= 'A' && *s <= 'F') { v = (unsigned)(*s - 'A') + 10u; }
        else { return -1; }
        r = msf_u128_shl(r, 4u);
        r.w[0] |= v;
    }
    *out = r;
    return 0;
}

struct stats {
    unsigned long total, passed, failed, skipped_planned, malformed;
};

#define MAX_PROV 32
static char prov_names[MAX_PROV][64];
static unsigned long prov_counts[MAX_PROV];
static int prov_n = 0;

static void count_prov(const char *prov)
{
    int i;
    for (i = 0; i < prov_n; i++) {
        if (strcmp(prov_names[i], prov) == 0) {
            prov_counts[i]++;
            return;
        }
    }
    if (prov_n < MAX_PROV) {
        strncpy(prov_names[prov_n], prov, 63);
        prov_counts[prov_n] = 1u;
        prov_n++;
    }
}

static msf_sha256_t g_hash;
static int g_hash_mode = 0;

static void hash_result(const char *opname, const uint64_t *args, int nargs,
                        uint64_t result, uint32_t flags)
{
    char line[256];
    int n = 0, i;
    n += snprintf(line + n, sizeof(line) - (size_t)n, "%s", opname);
    for (i = 0; i < nargs; i++) {
        n += snprintf(line + n, sizeof(line) - (size_t)n, " %016llx",
                      (unsigned long long)args[i]);
    }
    n += snprintf(line + n, sizeof(line) - (size_t)n, " -> %016llx %02x\n",
                  (unsigned long long)result, (unsigned)flags);
    msf_sha256_update(&g_hash, line, (size_t)n);
}

static void fail_line(const char *file, unsigned long lno, const char *raw,
                      const char *why, struct stats *st)
{
    st->failed++;
    printf("FAIL %s:%lu %s | %s\n", file, lno, why, raw);
}

static void process_pack_line(char **tok, int ntok, const char *file,
                              unsigned long lno, const char *raw,
                              struct stats *st)
{
    /* internal.pack64 rm sign exp2 sig128 sticky -> result flags prov */
    int rm, sign, sticky;
    long exp2;
    msf_u128_t sig;
    msf_flags_t flags = 0u, expect_flags;
    uint64_t expect, got;
    if (ntok != 10 || strcmp(tok[6], "->") != 0
        || parse_rm(tok[1], &rm) != 0 || rm < 0
        || hex_u128(tok[4], &sig) != 0) {
        st->malformed++;
        fail_line(file, lno, raw, "malformed pack64 line", st);
        return;
    }
    sign = atoi(tok[2]);
    exp2 = atol(tok[3]);
    sticky = atoi(tok[5]);
    expect = strtoull(tok[7], NULL, 16);
    expect_flags = (msf_flags_t)strtoul(tok[8], NULL, 16);
    got = msf_pack_f64(sign, (int32_t)exp2, sig, sticky, rm, &flags);
    st->total++;
    count_prov(tok[9]);
    if (g_hash_mode) {
        uint64_t args[3];
        args[0] = msf_u128_to_u64_trunc(sig);
        args[1] = msf_u128_to_u64_trunc(msf_u128_shr(sig, 64u));
        args[2] = (uint64_t)(uint32_t)exp2;
        hash_result(tok[0], args, 3, got, flags);
    }
    if (got != expect || flags != expect_flags) {
        char why[128];
        snprintf(why, sizeof(why), "got %016llx/%02x want %016llx/%02x",
                 (unsigned long long)got, (unsigned)flags,
                 (unsigned long long)expect, (unsigned)expect_flags);
        fail_line(file, lno, raw, why, st);
        return;
    }
    st->passed++;
}

static void process_line(char *line, const char *file, unsigned long lno,
                         struct stats *st)
{
    char raw[512];
    char *tok[16];
    int ntok = 0;
    char *p;
    const msf_op_desc_t *op;
    uint64_t args[3] = {0u, 0u, 0u};
    uint64_t expect = 0u, got = 0u;
    int arrow = -1, i;

    strncpy(raw, line, sizeof(raw) - 1u);
    raw[sizeof(raw) - 1u] = '\0';
    for (p = strtok(line, " \t\r\n"); p && ntok < 16; p = strtok(NULL, " \t\r\n")) {
        tok[ntok++] = p;
    }
    if (ntok == 0 || tok[0][0] == '#') {
        return;
    }
    if (strcmp(tok[0], "internal.pack64") == 0) {
        process_pack_line(tok, ntok, file, lno, raw, st);
        return;
    }
    op = find_op(tok[0]);
    if (op == NULL) {
        st->malformed++;
        fail_line(file, lno, raw, "unknown op", st);
        return;
    }
    if (op->status == 0) {
        st->skipped_planned++;
        st->total++;
        printf("SKIP %s:%lu %s not implemented (planned wave %d)\n",
               file, lno, op->name, op->wave);
        return;
    }
    for (i = 0; i < ntok; i++) {
        if (strcmp(tok[i], "->") == 0) {
            arrow = i;
        }
    }
    /* shape: op rm args... -> result flags prov : 2+nargs+1+3 tokens */
    if (arrow < 0 || ntok != 2 + op->nargs + 1 + 3 || arrow != 2 + op->nargs) {
        st->malformed++;
        fail_line(file, lno, raw, "malformed token count", st);
        return;
    }
    {
        int rm = -2;
        if (parse_rm(tok[1], &rm) != 0
            || (op->has_rm && rm < 0) || (!op->has_rm && rm != -1)) {
            st->malformed++;
            fail_line(file, lno, raw, "rounding token mismatch", st);
            return;
        }
    }
    for (i = 0; i < op->nargs; i++) {
        args[i] = strtoull(tok[2 + i], NULL, 16);
    }
    expect = strtoull(tok[arrow + 1], NULL, 16);
    if (!op->has_flags && strcmp(tok[arrow + 2], "--") != 0) {
        st->malformed++;
        fail_line(file, lno, raw, "flags given for flagless op", st);
        return;
    }
    if (call_op(op, args, &got) != 0) {
        fail_line(file, lno, raw, "runner has no call shape for this op yet", st);
        st->total++;
        return;
    }
    {
        int w = kind_width((uint8_t)op->retkind);
        uint64_t mask = w >= 64 ? ~0ULL : ((1ULL << w) - 1u);
        got &= mask;
        expect &= mask;
    }
    st->total++;
    count_prov(tok[arrow + 3]);
    if (g_hash_mode) {
        hash_result(op->name, args, op->nargs, got, 0u);
    }
    if (got != expect) {
        char why[128];
        snprintf(why, sizeof(why), "got %016llx want %016llx",
                 (unsigned long long)got, (unsigned long long)expect);
        fail_line(file, lno, raw, why, st);
        return;
    }
    st->passed++;
}

static void process_file(const char *path, struct stats *st)
{
    FILE *f = fopen(path, "r");
    char buf[512];
    unsigned long lno = 0u, before = st->total;
    if (!f) {
        fprintf(stderr, "runner: cannot open %s\n", path);
        st->failed++;
        return;
    }
    while (fgets(buf, sizeof(buf), f)) {
        lno++;
        process_line(buf, path, lno, st);
    }
    fclose(f);
    printf("file %s: %lu vectors\n", path, st->total - before);
}

static void sha256_file_hex(const char *path, char out[65])
{
    FILE *f = fopen(path, "rb");
    msf_sha256_t s;
    uint8_t dig[32], chunk[4096];
    size_t n;
    int i;
    if (!f) {
        die("manifest: cannot open listed file");
    }
    msf_sha256_init(&s);
    while ((n = fread(chunk, 1u, sizeof(chunk), f)) > 0u) {
        msf_sha256_update(&s, chunk, n);
    }
    fclose(f);
    msf_sha256_final(&s, dig);
    for (i = 0; i < 32; i++) {
        snprintf(out + 2 * i, 3u, "%02x", dig[i]);
    }
    out[64] = '\0';
}

/* Manifest lines: "<sha256hex>  <path>". Any mismatch refuses the run
 * (stale-binary / tampered-vector control, SF-0 5.2). */
static void check_manifest(const char *path)
{
    FILE *f = fopen(path, "r");
    char buf[1024];
    unsigned long lno = 0u;
    if (!f) {
        die("manifest: cannot open");
    }
    while (fgets(buf, sizeof(buf), f)) {
        char want[65], got[65], file[768];
        lno++;
        if (buf[0] == '#' || buf[0] == '\n' || buf[0] == '\r') {
            continue;
        }
        if (sscanf(buf, "%64s %767s", want, file) != 2) {
            fprintf(stderr, "runner: manifest line %lu malformed\n", lno);
            exit(2);
        }
        sha256_file_hex(file[0] == '*' ? file + 1 : file, got);
        if (strcmp(want, got) != 0) {
            fprintf(stderr, "runner: MANIFEST MISMATCH for %s (want %s got %s) - refusing\n",
                    file, want, got);
            exit(2);
        }
    }
    fclose(f);
    printf("manifest %s: all entries match\n", path);
}

static int check_expect_counts(const char *path)
{
    FILE *f = fopen(path, "r");
    char buf[256];
    int bad = 0;
    if (!f) {
        die("expect-counts: cannot open");
    }
    while (fgets(buf, sizeof(buf), f)) {
        char prov[64];
        unsigned long want, got = 0u;
        int i;
        if (buf[0] == '#' || buf[0] == '\n' || buf[0] == '\r') {
            continue;
        }
        if (sscanf(buf, "%63s %lu", prov, &want) != 2) {
            continue;
        }
        for (i = 0; i < prov_n; i++) {
            if (strcmp(prov_names[i], prov) == 0) {
                got = prov_counts[i];
            }
        }
        if (got != want) {
            printf("COUNT MISMATCH provenance %s: ran %lu, expected %lu\n",
                   prov, got, want);
            bad = 1;
        }
    }
    fclose(f);
    return bad;
}

static int g_unit_fail = 0;

#define UNIT_CHECK(cond) do { \
    if (!(cond)) { \
        printf("UNIT FAIL line %d: %s\n", __LINE__, #cond); \
        g_unit_fail++; \
    } \
} while (0)

static void unit_sha256_kat(void)
{
    static const struct { const char *msg; const char *hex; } kat[] = {
        { "", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" },
        { "abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad" },
        { "abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
          "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1" }
    };
    size_t i;
    for (i = 0; i < sizeof(kat) / sizeof(kat[0]); i++) {
        msf_sha256_t s;
        uint8_t dig[32];
        char got[65];
        int j;
        msf_sha256_init(&s);
        msf_sha256_update(&s, kat[i].msg, strlen(kat[i].msg));
        msf_sha256_final(&s, dig);
        for (j = 0; j < 32; j++) {
            snprintf(got + 2 * j, 3u, "%02x", dig[j]);
        }
        got[64] = '\0';
        UNIT_CHECK(strcmp(got, kat[i].hex) == 0);
    }
    printf("unit sha256: %u known-answer tests\n", (unsigned)(sizeof(kat) / sizeof(kat[0])));
}

static void unit_flags_and_versions(void)
{
    msf_flags_t st = 0u;
    msf_saved_flags_t saved;
    unsigned cases = 0u;
    uint32_t subset, start;
    /* exhaustive state machine over all 32 flag words x 32 groups:
     * lower/raise/test semantics from 5.7.4 (any-of-group tests). */
    for (start = 0u; start < 32u; start++) {
        for (subset = 0u; subset < 32u; subset++) {
            st = start;
            msf_lower_flags(&st, subset);
            UNIT_CHECK(st == (start & ~subset));
            st = start;
            msf_raise_flags(&st, subset);
            UNIT_CHECK(st == (start | subset));
            st = start;
            UNIT_CHECK(msf_test_flags(&st, subset) == ((start & subset) != 0u));
            UNIT_CHECK(st == start);
            saved = msf_save_all_flags(&st);
            UNIT_CHECK(msf_test_saved_flags(saved, subset) == ((start & subset) != 0u));
            st = 0x1fu - start; /* some other state (still within 5 bits) */
            {
                msf_flags_t other = st;
                msf_restore_flags(&st, saved, subset);
                UNIT_CHECK(st == ((other & ~subset) | (start & subset)));
            }
            cases++;
        }
    }
    /* stray bits above the five flags are ignored, not stored */
    st = 0u;
    msf_raise_flags(&st, 0xffffffe0u);
    UNIT_CHECK(st == 0u);
    msf_raise_flags(&st, MSF_FLAGS_ALL | 0xffffffe0u);
    UNIT_CHECK(st == MSF_FLAGS_ALL);
    printf("unit flags: %u exhaustive state/group cases\n", cases);

    UNIT_CHECK(msf_is754version1985() == 0);
    UNIT_CHECK(msf_is754version2008() == 0);
    UNIT_CHECK(msf_is754version2019() == 1);
    UNIT_CHECK(msf16_is754version2019() == 1 && msf32_is754version2008() == 0
               && msf64_is754version1985() == 0);
    printf("unit versions: global + per-format predicates\n");
}

static void unit_wide(void)
{
    msf_u128_t a = msf_u128_mul_u64_u64(0xffffffffffffffffULL, 0xffffffffffffffffULL);
    msf_u128_t b;
    uint32_t carry = 0u, borrow = 0u;
    /* (2^64-1)^2 = 2^128 - 2^65 + 1 */
    UNIT_CHECK(a.w[0] == 1u && a.w[1] == 0u && a.w[2] == 0xfffffffeu && a.w[3] == 0xffffffffu);
    /* a + (2^64-1) = 2^128 - 2^64; minus 1 borrows across two limbs */
    b = msf_u128_add(a, msf_u128_from_u64(0xffffffffffffffffULL), &carry);
    UNIT_CHECK(carry == 0u && b.w[0] == 0u && b.w[1] == 0u
               && b.w[2] == 0xffffffffu && b.w[3] == 0xffffffffu);
    b = msf_u128_sub(b, msf_u128_from_u64(1u), &borrow);
    UNIT_CHECK(borrow == 0u && b.w[0] == 0xffffffffu && b.w[1] == 0xffffffffu
               && b.w[2] == 0xfffffffeu && b.w[3] == 0xffffffffu);
    b = msf_u128_shr_jam(msf_u128_from_u64(0x10u), 5u, 0);
    UNIT_CHECK(msf_u128_to_u64_trunc(b) == 1u); /* jam keeps tail evidence */
    b = msf_u128_shr(msf_u128_from_u64(0x10u), 5u);
    UNIT_CHECK(msf_u128_to_u64_trunc(b) == 0u);
    UNIT_CHECK(msf_u128_clz(msf_u128_from_u64(1u)) == 127);
    UNIT_CHECK(msf_u128_clz(a) == 0);
    UNIT_CHECK(msf_u128_clz(msf_u128_from_u64(0u)) == 128);
    printf("unit wide: mul/add/sub/jam/clz spot identities\n");
}

static void print_inventory(const char *mode)
{
    size_t i;
    unsigned impl = 0u;
    for (i = 0; i < MSF_OP_COUNT; i++) {
        if (MSF_OPS[i].status == 1) {
            impl++;
        }
    }
    printf("== muse-softfloat runner: %s ==\n", mode);
    printf("build: %s\n", MSF_BUILD_ID);
#if defined(__VERSION__)
    printf("compiler: %s\n", __VERSION__);
#endif
#if defined(__FLT_EVAL_METHOD__)
    printf("FLT_EVAL_METHOD=%d\n", __FLT_EVAL_METHOD__);
#endif
    printf("semantics: IEEE 754-2019; tininess %s; NaN matrix SF-0 2.5; H=%d\n",
           MSF_TININESS_AFTER_ROUNDING ? "after rounding" : "BEFORE ROUNDING (control build)",
           MSF_DECIMAL_H);
    printf("op surface: %u instantiations (%u implemented, %u planned)\n",
           (unsigned)MSF_OP_COUNT, impl, (unsigned)MSF_OP_COUNT - impl);
}

int main(int argc, char **argv)
{
    struct stats st;
    const char *manifest = NULL, *expect = NULL;
    int i, rc = 0;
    memset(&st, 0, sizeof(st));
    if (argc < 2) {
        die("usage: verify|hash|unit ...");
    }
    if (strcmp(argv[1], "unit") == 0) {
        print_inventory("unit");
        unit_sha256_kat();
        unit_flags_and_versions();
        unit_wide();
        printf("unit: %s (%d failures)\n", g_unit_fail == 0 ? "PASS" : "FAIL", g_unit_fail);
        return g_unit_fail == 0 ? 0 : 1;
    }
    if (strcmp(argv[1], "hash") != 0 && strcmp(argv[1], "verify") != 0) {
        die("usage: verify|hash|unit ...");
    }
    g_hash_mode = strcmp(argv[1], "hash") == 0;
    print_inventory(argv[1]);
    if (g_hash_mode) {
        msf_sha256_init(&g_hash);
    }
    for (i = 2; i < argc; i++) {
        if (strcmp(argv[i], "--manifest") == 0 && i + 1 < argc) {
            manifest = argv[++i];
        } else if (strcmp(argv[i], "--expect-counts") == 0 && i + 1 < argc) {
            expect = argv[++i];
        }
    }
    if (manifest) {
        check_manifest(manifest);
    }
    for (i = 2; i < argc; i++) {
        if (strcmp(argv[i], "--manifest") == 0
            || strcmp(argv[i], "--expect-counts") == 0) {
            i++;
        } else {
            process_file(argv[i], &st);
        }
    }
    if (expect) {
        rc |= check_expect_counts(expect);
    }
    printf("-- provenance --\n");
    for (i = 0; i < prov_n; i++) {
        printf("prov %s %lu\n", prov_names[i], prov_counts[i]);
    }
    printf("-- summary --\n");
    printf("total %lu passed %lu failed %lu malformed %lu skipped-planned %lu\n",
           st.total, st.passed, st.failed, st.malformed, st.skipped_planned);
    if (g_hash_mode) {
        uint8_t dig[32];
        msf_sha256_final(&g_hash, dig);
        printf("whole-run-sha256 ");
        for (i = 0; i < 32; i++) {
            printf("%02x", dig[i]);
        }
        printf("\n");
    }
    if (st.failed > 0u || st.malformed > 0u || rc != 0) {
        printf("VERDICT: FAIL\n");
        return 1;
    }
    if (st.total == 0u) {
        printf("VERDICT: FAIL (no vectors ran)\n");
        return 1;
    }
    printf("VERDICT: PASS\n");
    return 0;
}
