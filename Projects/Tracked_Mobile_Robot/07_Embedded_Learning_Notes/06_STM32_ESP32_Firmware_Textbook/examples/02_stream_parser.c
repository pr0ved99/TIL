/* PC lesson: real STM ring/parser, simplified foreground line collector.
 * No ISR/UART. This collector deliberately omits production error recovery. */
#include "ring_buffer.h"
#include "uart_frame_parser.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static ring_buffer_t rb;
static char line[128];
static size_t length;
static unsigned lines;

static void drain(void)
{
    uint8_t byte;
    while (ring_buffer_pop(&rb, &byte)) {
        if (byte == '\n') {
            uart_frame_t frame;
            assert(uart_frame_parse(line, length, &frame) == UART_FRAME_PARSE_OK);
            printf("frame %u: %s seq=%lu\n", ++lines,
                   uart_frame_type_name(frame.type), (unsigned long)frame.seq);
            length = 0;
        } else {
            assert(length < sizeof(line));
            line[length++] = (char)byte;
        }
    }
}

static void feed(const char *chunk)
{
    while (*chunk != '\0') {
        assert(ring_buffer_push(&rb, (uint8_t)*chunk++));
    }
    drain();
}

int main(void)
{
    ring_buffer_init(&rb);
    feed("AR");
    assert(lines == 0U);
    feed("M,seq=7");
    assert(lines == 0U);
    feed("\nPING,seq=8\n");
    assert(lines == 2U);

    uart_frame_t frame;
    const char *extra = "ARM,seq=7,extra=1";
    const char *overflow = "ARM,seq=4294967296";
    const char *range = "CMD,seq=9,vx_mmps=101,w_mradps=0,timeout_ms=300";
    assert(uart_frame_parse(extra, strlen(extra), &frame) == UART_FRAME_PARSE_EXTRA_DATA);
    assert(uart_frame_parse(overflow, strlen(overflow), &frame) == UART_FRAME_PARSE_INVALID_SEQ);
    /* Parsing an int32 succeeds; handle_cmd must reject the operational range. */
    assert(uart_frame_parse(range, strlen(range), &frame) == UART_FRAME_PARSE_OK);
    assert(frame.vx_mmps == 101);
    puts("vx=101: syntax valid; STM handle_cmd must reject the speed range");

    ring_buffer_init(&rb);
    for (unsigned i = 0; i < RING_BUFFER_SIZE - 1U; ++i) {
        assert(ring_buffer_push(&rb, 'X'));
    }
    assert(!ring_buffer_push(&rb, 'Y'));
    assert(ring_buffer_available(&rb) == 255U && ring_buffer_dropped(&rb) == 1U);
    puts("capacity=255, rejected byte count=1");
    puts("PASS 02: byte chunks, strict parser and ring capacity");
    return 0;
}
