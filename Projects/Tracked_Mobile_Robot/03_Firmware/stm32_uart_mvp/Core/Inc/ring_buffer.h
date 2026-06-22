#ifndef RING_BUFFER_H
#define RING_BUFFER_H

#include <stdint.h>

#define RB_SIZE 512u

typedef struct {
  volatile uint8_t buf[RB_SIZE];
  volatile uint16_t head;
  volatile uint16_t tail;
} ring_buffer_t;

void rb_init(ring_buffer_t *rb);
int rb_put(ring_buffer_t *rb, uint8_t byte);
int rb_get(ring_buffer_t *rb, uint8_t *out);
uint16_t rb_count(const ring_buffer_t *rb);

#endif /* RING_BUFFER_H */
