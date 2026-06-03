#ifndef FIXED_POINT_H
#define FIXED_POINT_H

#include <stdint.h>

static inline void print_binary(int value, int n_bits) {
    for (int i = n_bits - 1; i >= 0; i--) {
        printf("%d", (value >> i) & 1);
    }
    printf(" (%d) ", value);
}

/* Fixed-point storage types */
typedef int8_t fp8_t;
typedef int16_t fp16_t;
typedef int32_t fp32_t;
typedef int64_t fp64_t;


/* Fixed-point arithmetic operations */
static inline fp8_t fp8_add(fp8_t v1, fp8_t v2){
    // Addition : operands must use the same format, so we can directly add them
    return v1 + v2;
}
static inline fp8_t fp8_mul(fp8_t v1, fp8_t v2, int shift){
    // Multiplication : intermediate result uses 16 bits then shifted right to restore scaling
    fp16_t prod = (fp16_t)v1 * (fp16_t)v2;

    if(shift > 0)
        return (fp8_t)(prod >> shift);
    else if(shift < 0)
        return (fp8_t)(prod << (-shift));

    return (fp8_t)prod;
}

static inline fp16_t fp16_add(fp16_t v1, fp16_t v2){
    // Addition : operands must use the same format, so we can directly add them
    return v1 + v2;
}
static inline fp16_t fp16_mul(fp16_t v1, fp16_t v2, int shift){
    // Multiplication : intermediate result uses 32 bits then shifted right to restore scaling
    fp32_t prod = (fp32_t)v1 * (fp32_t)v2;

    if(shift > 0)
        return (fp16_t)(prod >> shift);
    else if(shift < 0)
        return (fp16_t)(prod << (-shift));

    return (fp16_t)prod;
}

static inline fp32_t fp32_add(fp32_t v1, fp32_t v2){
    // Addition : operands must use the same format, so we can directly add them
    return v1 + v2;
}
static inline fp32_t fp32_mul(fp32_t v1, fp32_t v2, int shift){
    // Multiplication : intermediate result uses 64 bits then shifted right to restore scaling
    fp64_t prod = (fp64_t)v1 * (fp64_t)v2;
    
    if(shift > 0)
        return (fp32_t)(prod >> shift);
    else if(shift < 0)
        return (fp32_t)(prod << (-shift));

    return (fp32_t)prod;
}

#endif