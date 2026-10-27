/* sha256.h - test-only SHA-256 (FIPS 180-4) for whole-run hashes.
 * Shared by the host runner and the board harness so both sides hash
 * result streams identically (SF-0 Section 6 item 7). Never linked
 * into the library. Correctness is gated by known-answer tests in
 * the runner's unit mode against published digests.
 */
#ifndef MSF_TEST_SHA256_H
#define MSF_TEST_SHA256_H

#include <stddef.h>
#include <stdint.h>

typedef struct msf_sha256 {
    uint32_t h[8];
    uint64_t len;
    uint8_t buf[64];
    size_t buflen;
} msf_sha256_t;

void msf_sha256_init(msf_sha256_t *s);
void msf_sha256_update(msf_sha256_t *s, const void *data, size_t n);
void msf_sha256_final(msf_sha256_t *s, uint8_t out[32]);

#endif /* MSF_TEST_SHA256_H */
