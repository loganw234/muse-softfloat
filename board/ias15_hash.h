/* ias15_hash.h - IAS15FH1 field hashes for the board glue.
 *
 * Implements the hash specification of scratch/ias15/report.md
 * Sec.3 (our own spec) over the opaque ias15x accessors, streaming
 * into the repo's test SHA-256 (tests/sha256.c, the same source the
 * board harness links). Integer-only: every binary64 enters as its
 * bit pattern, little-endian by construction.
 */
#ifndef IAS15_HASH_H
#define IAS15_HASH_H

#include <stdint.h>
#include "ias15_api.h"

/* Compute both digests for `step`. If nonfinite_inout is non-NULL,
 * add the count of non-finite hashed fields (particle fields plus,
 * when allocated, the internal arrays) exactly as the reference
 * driver counts them, so a NaN reaching hashed state can never
 * pass silently. */
void ias15_hash_pair(ias15x_t *sim, uint64_t step,
                     uint8_t h_state[32], uint8_t h_full[32],
                     uint64_t *nonfinite_inout);

#endif /* IAS15_HASH_H */
