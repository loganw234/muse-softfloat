/* ias15_api.h - opaque interface from the (MIT) board glue to the
 * IAS15 workload. The workload itself is GPL-3.0-or-later REBOUND
 * code and lives OUTSIDE this repository (scratch/ias15/extract in
 * the workspace, supplied at build time via -DIAS15_EXTRACT_DIR);
 * this header is our own interface definition - no upstream struct,
 * type, or source appears here. Values cross the boundary only as
 * integer bit patterns or read-only double arrays the glue bit-casts
 * itself; the glue performs no floating-point arithmetic.
 *
 * Field order for particles is x y z vx vy vz ax ay az m r (11
 * binary64 values), matching the IAS15FH1 field-hash specification
 * in scratch/ias15/report.md Sec.3. Internal-array indices:
 * flat (length N3=3N): 0=at 1=x0 2=v0 3=a0 4=csx 5=csv 6=csa0;
 * dp7 (length 7*N3, storage order): 0=g 1=b 2=csb 3=e 4=br 5=er.
 * Table indices for ias15x_table_bits: 0=h 1=rr 2=c 3=d (the step's
 * Gauss-Radau coefficient tables; w is MEGNO-only and unused here).
 */
#ifndef IAS15_API_H
#define IAS15_API_H

#include <stddef.h>
#include <stdint.h>

#ifndef IAS15X_NMAX
#define IAS15X_NMAX 16 /* demo runs N=3; arena scales 1176+88 bytes/body */
#endif
/* Caller-owned static arena handed to ias15x_init. The workload
 * carves its whole workspace from it once (formula in README of
 * the extract); 32 KiB covers NMAX=16 with headroom, and init
 * fails loudly if it ever does not. */
#ifndef IAS15X_ARENA_BYTES
#define IAS15X_ARENA_BYTES (32u * 1024u)
#endif

typedef struct ias15x_handle ias15x_t; /* opaque, owned by the workload */

/* Initialise (or reset) the workload in the given 8-byte-aligned
 * arena. Returns 0 on success, nonzero on arena/capacity failure. */
int ias15x_init(unsigned char *arena, size_t arena_bytes, ias15x_t **out);
void ias15x_shutdown(ias15x_t *sim);

void ias15x_set_scalars(ias15x_t *sim,
                        uint64_t g_bits, uint64_t dt_bits, uint64_t t_bits,
                        uint64_t epsilon_bits, uint64_t min_dt_bits,
                        uint32_t adaptive_mode);
/* Appends one particle from its 11 field bit patterns. 0 ok. */
int ias15x_add_particle(ias15x_t *sim, const uint64_t field_bits[11]);
/* Advance one accepted step (upstream steps(sim,1) semantics). */
void ias15x_step(ias15x_t *sim);

size_t ias15x_particle_count(const ias15x_t *sim);
size_t ias15x_n3(const ias15x_t *sim);            /* 3 * (N + N_var); N_var=0 */
int ias15x_allocated(const ias15x_t *sim);        /* IAS15FH1 'allocated' byte */
uint64_t ias15x_t_bits(const ias15x_t *sim);
uint64_t ias15x_dt_bits(const ias15x_t *sim);
uint64_t ias15x_dt_last_done_bits(const ias15x_t *sim);
uint64_t ias15x_g_bits(const ias15x_t *sim);
uint64_t ias15x_epsilon_bits(const ias15x_t *sim);
uint64_t ias15x_min_dt_bits(const ias15x_t *sim);
uint32_t ias15x_adaptive_mode(const ias15x_t *sim);
uint64_t ias15x_iterations_max_exceeded(const ias15x_t *sim);
uint64_t ias15x_steps_done(const ias15x_t *sim);
uint32_t ias15x_warnings(const ias15x_t *sim);
uint32_t ias15x_errors(const ias15x_t *sim);
uint64_t ias15x_particle_field_bits(const ias15x_t *sim, size_t particle,
                                    size_t field); /* field 0..10 */
const double *ias15x_flat_array(const ias15x_t *sim, int which);
const double *ias15x_dp7_array(const ias15x_t *sim, int which);
uint64_t ias15x_table_bits(int which, size_t i);
size_t ias15x_table_len(int which);

#endif /* IAS15_API_H */
