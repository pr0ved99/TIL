#include "ring_buffer.h"

static uint16_t ring_buffer_next(uint16_t index)
{
    return (uint16_t)((index + 1u) % RING_BUFFER_SIZE);
}

void ring_buffer_init(ring_buffer_t *rb)
{
    if(rb == NULL){
        return;
    }

    rb->head = 0;
    rb->tail = 0;
    rb->drop_count = 0;
}

int ring_buffer_push(ring_buffer_t *rb, uint8_t data){
    if (rb == NULL){
        return 0;
    }

    uint16_t next_head = ring_buffer_next(rb->head);

    if(next_head == rb->tail){
        rb->drop_count++;
        return 0;
    }

    rb->buffer[rb->head] = data;
    rb->head =  next_head;

    return 1;
}

int ring_buffer_pop(ring_buffer_t *rb, uint8_t *data){
    if(rb == NULL || data == NULL){
        return 0;
    }
    if(rb->head == rb->tail){
        return 0;
    }
    *data = rb->buffer[rb->tail];
    rb->tail = ring_buffer_next(rb->tail);
    return 1;
}

void ring_buffer_discard_all(ring_buffer_t *rb){
    if(rb == NULL){
        return;
    }

    rb->tail = rb->head;
}

uint16_t ring_buffer_available(const ring_buffer_t *rb){
    if(rb == NULL){
        return 0;
    }

    if(rb->head >= rb->tail){
        return (uint16_t)(rb->head - rb->tail);
    }

    return (uint16_t)(RING_BUFFER_SIZE - rb->tail + rb->head);
}

uint32_t ring_buffer_dropped(const ring_buffer_t *rb){
    if(rb == NULL){
        return 0;
    }
    return rb->drop_count;
}
