#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include "muse_softfloat.h"
#include "softfloat.h"

#define N 1000000
static uint64_t a64[N], b64[N], c64[N], r64[N];
static uint32_t a32[N], b32[N], c32[N], r32[N];

static uint64_t rng = 0x9E3779B97F4A7C15ull;
static uint64_t nx(void){ rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17; return rng; }
/* operands in a moderate exponent range so results are normal */
static uint64_t mk64(void){ uint64_t m = nx() & 0x000FFFFFFFFFFFFFull; uint64_t e = 1023 - 20 + (nx() % 40); return ((nx()&1)<<63) | (e<<52) | m; }
static uint32_t mk32(void){ uint32_t m = (uint32_t)nx() & 0x7FFFFF; uint32_t e = 127 - 20 + (uint32_t)(nx() % 40); return (uint32_t)(((nx()&1)<<31) | (e<<23) | m); }

static double now(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec + t.tv_nsec*1e-9; }

#define BENCH(label, body) do { double best=1e9; for (int rep=0; rep<5; rep++){ double t0=now(); body; double t1=now(); if (t1-t0<best) best=t1-t0; } printf("%-26s %8.2f ns/op\n", label, best*1e9/N); } while(0)

int main(void){
    for (int i=0;i<N;i++){ a64[i]=mk64(); b64[i]=mk64(); c64[i]=mk64(); a32[i]=mk32(); b32[i]=mk32(); c32[i]=mk32(); }
    msf_flags_t fl = 0; volatile uint64_t sink = 0;
    softfloat_roundingMode = softfloat_round_near_even;
    float64_t x, y, z; float32_t p, q, r;
    printf("(host x86-64, %d ops per timing, best of 5; msf = this library, bf = Berkeley SoftFloat 3e)\n", N);
    BENCH("msf64_add",  for(int i=0;i<N;i++) r64[i]=msf64_add(a64[i],b64[i],MSF_ROUND_TIES_TO_EVEN,&fl));
    BENCH("bf f64_add", for(int i=0;i<N;i++){ x.v=a64[i]; y.v=b64[i]; z=f64_add(x,y); r64[i]=z.v; });
    BENCH("msf64_mul",  for(int i=0;i<N;i++) r64[i]=msf64_mul(a64[i],b64[i],MSF_ROUND_TIES_TO_EVEN,&fl));
    BENCH("bf f64_mul", for(int i=0;i<N;i++){ x.v=a64[i]; y.v=b64[i]; z=f64_mul(x,y); r64[i]=z.v; });
    BENCH("msf64_div",  for(int i=0;i<N;i++) r64[i]=msf64_div(a64[i],b64[i],MSF_ROUND_TIES_TO_EVEN,&fl));
    BENCH("bf f64_div", for(int i=0;i<N;i++){ x.v=a64[i]; y.v=b64[i]; z=f64_div(x,y); r64[i]=z.v; });
    BENCH("msf64_sqrt", for(int i=0;i<N;i++) r64[i]=msf64_sqrt(a64[i]&0x7FFFFFFFFFFFFFFFull,MSF_ROUND_TIES_TO_EVEN,&fl));
    BENCH("bf f64_sqrt",for(int i=0;i<N;i++){ x.v=a64[i]&0x7FFFFFFFFFFFFFFFull; z=f64_sqrt(x); r64[i]=z.v; });
    BENCH("msf64_fma",  for(int i=0;i<N;i++) r64[i]=msf64_fma(a64[i],b64[i],c64[i],MSF_ROUND_TIES_TO_EVEN,&fl));
    BENCH("bf f64_mulAdd",for(int i=0;i<N;i++){ x.v=a64[i]; y.v=b64[i]; z.v=c64[i]; z=f64_mulAdd(x,y,z); r64[i]=z.v; });
    BENCH("msf32_add",  for(int i=0;i<N;i++) r32[i]=msf32_add(a32[i],b32[i],MSF_ROUND_TIES_TO_EVEN,&fl));
    BENCH("bf f32_add", for(int i=0;i<N;i++){ p.v=a32[i]; q.v=b32[i]; r=f32_add(p,q); r32[i]=r.v; });
    BENCH("msf32_mul",  for(int i=0;i<N;i++) r32[i]=msf32_mul(a32[i],b32[i],MSF_ROUND_TIES_TO_EVEN,&fl));
    BENCH("bf f32_mul", for(int i=0;i<N;i++){ p.v=a32[i]; q.v=b32[i]; r=f32_mul(p,q); r32[i]=r.v; });
    BENCH("msf32_div",  for(int i=0;i<N;i++) r32[i]=msf32_div(a32[i],b32[i],MSF_ROUND_TIES_TO_EVEN,&fl));
    BENCH("bf f32_div", for(int i=0;i<N;i++){ p.v=a32[i]; q.v=b32[i]; r=f32_div(p,q); r32[i]=r.v; });
    BENCH("msf64_sin_pi", for(int i=0;i<N/10;i++) r64[i]=msf64_sin_pi(a64[i],MSF_ROUND_TIES_TO_EVEN,&fl));
    BENCH("msf64_exp2",   for(int i=0;i<N/10;i++) r64[i]=msf64_exp2(a64[i],MSF_ROUND_TIES_TO_EVEN,&fl));
    BENCH("msf64_log2",   for(int i=0;i<N/10;i++) r64[i]=msf64_log2(a64[i]&0x7FFFFFFFFFFFFFFFull,MSF_ROUND_TIES_TO_EVEN,&fl));
    for (int i=0;i<16;i++) sink += r64[i] + r32[i];
    return (int)(sink & 1) * 0 + (int)(fl == 0xdead);
}
