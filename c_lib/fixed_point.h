#ifndef FIXED_POINT_H
#define FIXED_POINT_H

#include <stdint.h>

struct Format{
    int a;
    int b;
} typedef Format;

typedef int8_t fp8_t;
typedef int16_t fp16_t;
typedef int32_t fp32_t;
typedef int64_t fp64_t;

static inline fp8_t fp8_add(fp8_t v1, fp8_t v2){
    return v1 + v2;
}
static inline fp8_t fp8_mul(fp8_t v1, fp8_t v2){
    fp16_t prod = (fp16_t)v1 * (fp16_t)v2;
    return (fp8_t)(prod >> 8);
}

static inline fp16_t fp16_add(fp16_t v1, fp16_t v2);
static inline fp16_t fp16_mul(fp16_t v1, fp16_t v2);

static inline fp32_t fp32_add(fp32_t v1, fp32_t v2);
static inline fp32_t fp32_mul(fp32_t v1, fp32_t v2);



#endif