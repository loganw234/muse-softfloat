/* glue.c - WebAssembly surface for the demo site.
 *
 * The library sources under src/ are compiled unmodified; this file is
 * the only site-owned C. It reuses the repository's generated dispatch
 * table (tests/msf_dispatch.h - the same table tests/runner.c drives)
 * so the browser runs exactly the instantiations the host gate replays.
 *
 * Exported surface (all values cross the boundary as 32-bit words):
 *   msf_op_count()      number of dispatch entries
 *   msf_run(idx, rm, a_lo, a_hi, b_lo, b_hi, c_lo, c_hi)
 *                       run dispatch entry idx; rm is an msf_rounding_t
 *                       value (0..4) or -1 for ops without an attribute;
 *                       operands are raw bit patterns, low word first
 *   msf_result_lo/hi()  result bits of the last msf_run
 *   msf_result_flags()  flag delta (MSF_FLAG_* bits) of the last run
 *   msf_result_ok()     1 if the entry is runnable, 0 otherwise
 *
 * Entries whose trampoline is 0 in the dispatch table (the character
 * conversions and flag-management ops, which are not hex-drivable)
 * report ok=0 and are excluded from the page's op list by
 * build_data.py.
 */
#include <stddef.h>
#include <stdint.h>

#include "../tests/msf_dispatch.h"

#define EXPORT __attribute__((visibility("default")))

/* Freestanding wasm32: the compiler may still emit calls to these for
 * aggregate copies (the library's 128-bit values are structs). */
void *memcpy(void *dst, const void *src, size_t n) {
    unsigned char *d = (unsigned char *)dst;
    const unsigned char *s = (const unsigned char *)src;
    for (size_t i = 0; i < n; i++) d[i] = s[i];
    return dst;
}
void *memmove(void *dst, const void *src, size_t n) {
    unsigned char *d = (unsigned char *)dst;
    const unsigned char *s = (const unsigned char *)src;
    if (d < s) {
        for (size_t i = 0; i < n; i++) d[i] = s[i];
    } else {
        for (size_t i = n; i > 0; i--) d[i - 1] = s[i - 1];
    }
    return dst;
}
void *memset(void *dst, int v, size_t n) {
    unsigned char *d = (unsigned char *)dst;
    for (size_t i = 0; i < n; i++) d[i] = (unsigned char)v;
    return dst;
}

static uint64_t g_result;
static uint32_t g_flags;
static uint32_t g_ok;

EXPORT int msf_op_count(void) {
    return (int)(sizeof(MSF_OPS) / sizeof(MSF_OPS[0]));
}

EXPORT void msf_run(int idx, int rm,
                    uint32_t a_lo, uint32_t a_hi,
                    uint32_t b_lo, uint32_t b_hi,
                    uint32_t c_lo, uint32_t c_hi) {
    g_result = 0;
    g_flags = 0;
    g_ok = 0;
    if (idx < 0 || idx >= msf_op_count()) return;
    const msf_op_desc_t *op = &MSF_OPS[idx];
    if (op->call == 0) return;
    uint64_t args[3];
    args[0] = ((uint64_t)a_hi << 32) | (uint64_t)a_lo;
    args[1] = ((uint64_t)b_hi << 32) | (uint64_t)b_lo;
    args[2] = ((uint64_t)c_hi << 32) | (uint64_t)c_lo;
    msf_flags_t flags = 0;
    g_result = op->call(args, rm, &flags);
    g_flags = (uint32_t)flags;
    g_ok = 1;
}

EXPORT uint32_t msf_result_lo(void) { return (uint32_t)(g_result & 0xffffffffu); }
EXPORT uint32_t msf_result_hi(void) { return (uint32_t)(g_result >> 32); }
EXPORT uint32_t msf_result_flags(void) { return g_flags; }
EXPORT uint32_t msf_result_ok(void) { return g_ok; }
