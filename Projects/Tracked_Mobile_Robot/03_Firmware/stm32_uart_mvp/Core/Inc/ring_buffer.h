#ifndef RING_BUFFER_H
#define RING_BUFFER_H

#include <stdint.h>
#include <stddef.h>

#define RING_BUFFER_SIZE 256u

typedef struct{
    uint8_t buffer[RING_BUFFER_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
    volatile uint32_t drop_count;
} ring_buffer_t;

void ring_buffer_init(ring_buffer_t *rb);
int ring_buffer_push(ring_buffer_t *rb, uint8_t data);
int ring_buffer_pop(ring_buffer_t *rb, uint8_t *data);
uint16_t ring_buffer_available(const ring_buffer_t *rb);
uint32_t ring_buffer_dropped(const ring_buffer_t *rb);

#endif // RING_BUFFER_H