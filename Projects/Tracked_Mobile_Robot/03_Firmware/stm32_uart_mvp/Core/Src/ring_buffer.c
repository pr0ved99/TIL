#include "ring_buffer.h"

static uint16_t rb_next(uint16_t index)
{
  return (uint16_t)((index + 1u) % RB_SIZE);
}

void rb_init(ring_buffer_t *rb)
{
  rb->head = 0u;
  rb->tail = 0u;
}

int rb_put(ring_buffer_t *rb, uint8_t byte)
{
  uint16_t next = rb_next(rb->head);

  if (next == rb->tail) {
    return 0;
  }

  rb->buf[rb->head] = byte;
  rb->head = next;
  return 1;
}

int rb_get(ring_buffer_t *rb, uint8_t *out)
{
  if (rb->head == rb->tail) {
    return 0;
  }

  *out = rb->buf[rb->tail];
  rb->tail = rb_next(rb->tail);
  return 1;
}

uint16_t rb_count(const ring_buffer_t *rb)
{
  if (rb->head >= rb->tail) {
    return (uint16_t)(rb->head - rb->tail);
  }

  return (uint16_t)(RB_SIZE - rb->tail + rb->head);
}
