/* interval_host.c - host runner for the Step 1c interval
 * workload. Reads tests/interval_catalogue.tsv, classifies every
 * ray at every stage through board/interval_workload.c, prints
 * one RAY line per row plus a deterministic SHA-256 (the hash the
 * later board run must match). Host-only file: stdio is used for
 * the catalogue and the report, never inside the workload core.
 *
 * Hash layout IW1: the 3 bytes "IW1", then per catalogue row in
 * file order little-endian fields:
 *   sphere: id u32, kind u8=0, s1 cls u8, s1 lo u32, s1 hi u32,
 *           s1 ops u64, s2 cls u8, s2 lo u64, s2 hi u64, s2 ops
 *           u64, s3 cls u8, s3 ops u64, final cls u8
 *   box:    id u32, kind u8=1, cls u8, tmin u64, tmax u64, ops u64
 *   torus:  id u32, kind u8=2, cls u8, br lo u64, br hi u64,
 *           ops u64, evals u64, max depth u32, cap hit u8
 * Endpoint bits are the library minimum/maximum convention bits
 * from the workload core (frozen in interval_workload.h).
 *
 * Usage: interval_host CATALOGUE.tsv [--tol-half] [--cap N]
 * --tol-half halves the torus tolerance (monotonicity gate);
 * --cap overrides the per-ray torus op cap (default 4000000).
 */
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "interval_workload.h"
#include "../tests/sha256.h"

static iw_ctx_t ctx;
static msf_sha256_t hash;

static void h_u8(unsigned v)
{
    uint8_t b = (uint8_t)v;
    msf_sha256_update(&hash, &b, 1);
}

static void h_u32(uint32_t v)
{
    uint8_t b[4] = {(uint8_t)v, (uint8_t)(v >> 8),
                    (uint8_t)(v >> 16), (uint8_t)(v >> 24)};
    msf_sha256_update(&hash, b, 4);
}

static void h_u64(uint64_t v)
{
    uint8_t b[8];
    int i;
    for (i = 0; i < 8; i++) b[i] = (uint8_t)(v >> (8 * i));
    msf_sha256_update(&hash, b, 8);
}

static const char *cls_name(iw_class_t c)
{
    return c == IW_HIT ? "HIT" : (c == IW_MISS ? "MISS" : "UNCERTAIN");
}

static iw_class_t staged_final(iw_class_t s1, iw_class_t s2, iw_class_t s3)
{
    if (s3 != IW_UNCERTAIN) return s3;
    if (s2 != IW_UNCERTAIN) return s2;
    return s1;
}

#define NF 19
static char line[16384];
static char *fields[NF];

static int split_fields(char *s)
{
    int n = 0;
    char *p = s;
    fields[n++] = p;
    while (*p) {
        if (*p == '\t') {
            *p = '\0';
            if (n < NF) fields[n] = p + 1;
            n++;
        } else if (*p == '\n' || *p == '\r') {
            *p = '\0';
            break;
        }
        p++;
    }
    return n;
}

static msf64_t hex64(const char *s)
{
    return (msf64_t)strtoull(s, NULL, 16);
}

int main(int argc, char **argv)
{
    FILE *f;
    int i, rows = 0;
    int n_sphere = 0, n_box = 0, n_torus = 0;
    int unc1 = 0, unc2 = 0, unc3 = 0;
    msf64_t tol = IW_TORUS_TOL_BITS;
    uint64_t cap = 4000000u;
    uint8_t dig[32];

    if (argc < 2) {
        fprintf(stderr, "usage: interval_host CAT.tsv [--tol-half] [--cap N]\n");
        return 2;
    }
    for (i = 2; i < argc; i++) {
        if (strcmp(argv[i], "--tol-half") == 0) {
            tol = (msf64_t)0x3F40000000000000ULL; /* 2^-11 */
        } else if (strcmp(argv[i], "--cap") == 0 && i + 1 < argc) {
            cap = strtoull(argv[++i], NULL, 10);
        } else {
            fprintf(stderr, "unknown argument: %s\n", argv[i]);
            return 2;
        }
    }
    f = fopen(argv[1], "r");
    if (f == NULL) {
        fprintf(stderr, "cannot open %s\n", argv[1]);
        return 2;
    }
    iw_ctx_init(&ctx);
    msf_sha256_init(&hash);
    msf_sha256_update(&hash, "IW1", 3);

    while (fgets(line, sizeof(line), f) != NULL) {
        msf64_t O[3], D[3], g[6];
        uint32_t id;
        if (line[0] == '#' || line[0] == '\n' || line[0] == '\0') continue;
        if (split_fields(line) != NF) {
            fprintf(stderr, "bad catalogue line: %s\n", line);
            fclose(f);
            return 1;
        }
        rows++;
        id = (uint32_t)strtoul(fields[0], NULL, 10);
        for (i = 0; i < 3; i++) O[i] = hex64(fields[4 + i]);
        for (i = 0; i < 3; i++) D[i] = hex64(fields[7 + i]);
        for (i = 0; i < 6; i++) g[i] = hex64(fields[10 + i]);

        if (strcmp(fields[2], "sphere") == 0) {
            msf32_t lo1, hi1;
            msf64_t lo2, hi2;
            uint64_t o1, o2, o3;
            iw_class_t s1 = iw_sphere_stage1_f32(&ctx, O, D, g, g[3],
                                                 &lo1, &hi1, &o1);
            iw_class_t s2 = iw_sphere_stage2_f64(&ctx, O, D, g, g[3],
                                                 &lo2, &hi2, &o2);
            iw_class_t s3 = iw_sphere_stage3_exact(&ctx, O, D, g, g[3], &o3);
            iw_class_t fin = staged_final(s1, s2, s3);
            n_sphere++;
            if (s1 == IW_UNCERTAIN) unc1++;
            if (s2 == IW_UNCERTAIN) unc2++;
            if (s3 == IW_UNCERTAIN) unc3++;
            printf("RAY id=%" PRIu32 " fam=%s kind=sphere s1=%s "
                   "s1lo=%08" PRIx32 " s1hi=%08" PRIx32 " s1ops=%" PRIu64
                   " s2=%s s2lo=%016" PRIx64 " s2hi=%016" PRIx64
                   " s2ops=%" PRIu64 " s3=%s s3ops=%" PRIu64 " final=%s\n",
                   id, fields[1], cls_name(s1), lo1, hi1, o1,
                   cls_name(s2), lo2, hi2, o2, cls_name(s3), o3,
                   cls_name(fin));
            h_u32(id); h_u8(0);
            h_u8((unsigned)s1); h_u32(lo1); h_u32(hi1); h_u64(o1);
            h_u8((unsigned)s2); h_u64(lo2); h_u64(hi2); h_u64(o2);
            h_u8((unsigned)s3); h_u64(o3);
            h_u8((unsigned)fin);
        } else if (strcmp(fields[2], "box") == 0) {
            msf64_t tmin, tmax;
            uint64_t ops;
            iw_class_t cls = iw_box(&ctx, O, D, g, g + 3, &tmin, &tmax, &ops);
            n_box++;
            printf("RAY id=%" PRIu32 " fam=%s kind=box dec=%s "
                   "tmin=%016" PRIx64 " tmax=%016" PRIx64 " ops=%" PRIu64 "\n",
                   id, fields[1], cls_name(cls), tmin, tmax, ops);
            h_u32(id); h_u8(1);
            h_u8((unsigned)cls); h_u64(tmin); h_u64(tmax); h_u64(ops);
        } else if (strcmp(fields[2], "torus") == 0) {
            iw_torus_result_t tr;
            iw_torus_first_hit(&ctx, O, D, tol, cap, &tr);
            n_torus++;
            printf("RAY id=%" PRIu32 " fam=%s kind=torus dec=%s "
                   "brlo=%016" PRIx64 " brhi=%016" PRIx64 " ops=%" PRIu64
                   " evals=%" PRIu64 " maxdepth=%" PRIu32 " caphit=%d\n",
                   id, fields[1], cls_name(tr.cls), tr.br_lo, tr.br_hi,
                   tr.ops, tr.evals, tr.max_depth, tr.cap_hit);
            h_u32(id); h_u8(2);
            h_u8((unsigned)tr.cls); h_u64(tr.br_lo); h_u64(tr.br_hi);
            h_u64(tr.ops); h_u64(tr.evals); h_u32(tr.max_depth);
            h_u8((unsigned)tr.cap_hit);
        } else {
            fprintf(stderr, "unknown kind: %s\n", fields[2]);
            fclose(f);
            return 1;
        }
    }
    fclose(f);
    msf_sha256_final(&hash, dig);
    printf("SUMMARY rows=%d sphere=%d box=%d torus=%d "
           "sphere_uncertain s1=%d s2=%d s3=%d total_ops=%" PRIu64 "\n",
           rows, n_sphere, n_box, n_torus, unc1, unc2, unc3, ctx.ops);
    printf("HOST_SHA256 ");
    for (i = 0; i < 32; i++) printf("%02x", dig[i]);
    printf("\n");
    return rows > 0 ? 0 : 1;
}
