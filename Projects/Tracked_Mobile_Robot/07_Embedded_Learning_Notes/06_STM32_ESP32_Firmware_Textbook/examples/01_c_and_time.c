/* PC lesson: values, output pointers, wrap and expiry boundaries. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

typedef struct {
    uint32_t seq;
    int32_t vx_mmps;
} command_t;

static bool make_zero(uint32_t seq, command_t *out)
{
    if (out == NULL) return false;
    *out = (command_t){.seq = seq, .vx_mmps = 0};
    return true;
}

static bool elapsed_at_least(uint32_t now, uint32_t then, uint32_t budget)
{
    return (uint32_t)(now - then) >= budget;
}

int main(void)
{
    command_t a = {0};
    assert(make_zero(7U, &a));
    assert(!make_zero(7U, NULL));
    command_t copy = a;
    a.seq = 8U;
    assert(copy.seq == 7U);
    printf("value copy: original=%lu copy=%lu\n",
           (unsigned long)a.seq, (unsigned long)copy.seq);

    uint32_t then = UINT32_MAX - 9U, now = 20U;
    assert((uint32_t)(now - then) == 30U);
    printf("wrap elapsed=%lu ms\n", (unsigned long)(now - then));
    assert(!elapsed_at_least(1299U, 1000U, 300U));
    assert(elapsed_at_least(1300U, 1000U, 300U));
    puts("timeout: 1299=not expired, 1300=expired");
    puts("PASS 01: C values and time");
    return 0;
}
