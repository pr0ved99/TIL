/* PC lesson: real pure-C mapper/encoder, no HAL or motor output linked. */
#include "drive_command_mapper.h"
#include "encoder_speed.h"
#include <assert.h>
#include <stdio.h>

static void mapping(int32_t vx, int32_t w, int left, int right)
{
    drive_command_request_t request;
    assert(drive_command_map(vx, w, 100U, &request));
    assert(request.left_signed_permille == left);
    assert(request.right_signed_permille == right);
    printf("vx=%ld w=%ld -> PWM request=%d/%d permille\n",
           (long)vx, (long)w, left, right);
}

int main(void)
{
    mapping(0, 0, 0, 0);
    mapping(50, 0, 50, 50);
    mapping(0, 250, -50, 50);
    mapping(100, 500, 0, 100);
    drive_command_request_t bad;
    assert(!drive_command_map(101, 0, 100U, &bad));

    encoder_speed_t speed;
    assert(encoder_speed_init(&speed, ENCODER_COUNTER_WIDTH_16, 65530U, 0U, 100U));
    assert(!encoder_speed_update(&speed, 5U, 99U));
    assert(encoder_speed_update(&speed, 5U, 100U));
    assert(speed.delta_count == 11 && speed.counts_per_second == 110);
    puts("16-bit wrap 65530 -> 5 in 100 ms: delta=11, CPS=110");
    assert(encoder_speed_update(&speed, 65530U, 200U));
    assert(speed.delta_count == -11 && speed.counts_per_second == -110);
    puts("reverse wrap 5 -> 65530 in 100 ms: delta=-11, CPS=-110");
    int32_t mrpm;
    assert(encoder_speed_cps_to_millirpm(780, 1560U, &mrpm));
    assert(mrpm == 30000);
    printf("780 CPS / 1560 counts per rev -> %ld millirpm\n", (long)mrpm);
    assert(!encoder_speed_cps_to_millirpm(780, 0U, &mrpm));
    puts("PASS 03: math only, no hardware output");
    return 0;
}
