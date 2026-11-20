/* Synthetic PC checks of the real candidate C. No robot or serial connection. */
#include "distance_move.h"
#include <assert.h>
#include <limits.h>
#include <stddef.h>
#include <stdio.h>

static unsigned scenarios;

static distance_move_sample_t sample(int64_t left, int64_t right, uint32_t ms)
{
    distance_move_sample_t s = {left, right, ms, true};
    return s;
}

static void outputs(distance_move_t *m, bool left, bool right)
{
    distance_move_output_t o = distance_move_output(m);
    assert(o.left_run == left && o.right_run == right);
}

static void aborted(distance_move_t *m, distance_move_reason_t reason)
{
    assert(m->phase == DISTANCE_MOVE_ABORTED && m->reason == reason);
    outputs(m, false, false);
}

static void begin(distance_move_t *m, int64_t left, int64_t right, uint32_t ms)
{
    distance_move_sample_t s = sample(left, right, ms);
    distance_move_init(m);
    outputs(m, false, false);
    assert(distance_move_start(m, 50U, &s, ms, true));
    assert(m->target_counts == 578U);
    outputs(m, true, true);
}

static void tick(distance_move_t *m, int64_t left, int64_t right, uint32_t ms)
{
    distance_move_sample_t s = sample(left, right, ms);
    distance_move_update(m, &s, ms, true);
}

int main(void)
{
    distance_move_t m;
    distance_move_sample_t s;
    uint32_t n;
    unsigned i;
    const uint32_t distances[] = {50, 100, 150, 200};
    const uint32_t expected[] = {578, 1156, 1734, 2312};

    for (i = 0; i < 4; ++i) {
        assert(distance_move_target_counts(distances[i], &n));
        assert(n == expected[i]);
        /* Nearest count: doubled distance error <= one count's numerator. */
        {
            int64_t error = (int64_t)n * 1687 - (int64_t)distances[i] * 19500;
            if (error < 0) error = -error;
            assert(2 * error <= 1687);
        }
    }
    scenarios++;

    for (i = 0; i <= 201; ++i) {
        bool allowed = i == 50 || i == 100 || i == 150 || i == 200;
        n = 123;
        assert(distance_move_target_counts(i, &n) == allowed);
        if (!allowed) assert(n == 0);
    }
    assert(!distance_move_target_counts(UINT32_MAX, &n) && n == 0);
    assert(!distance_move_target_counts(50, NULL));
    scenarios++;

    distance_move_init(NULL);
    distance_move_cancel(NULL);
    distance_move_update(NULL, NULL, 0, false);
    outputs(NULL, false, false);
    assert(!distance_move_start(NULL, 50, NULL, 0, true));
    scenarios++;

    distance_move_init(&m);
    s = sample(0, 0, 0);
    assert(!distance_move_start(&m, 51, &s, 0, true));
    aborted(&m, DISTANCE_MOVE_REASON_BAD_TARGET);
    scenarios++;

    distance_move_init(&m);
    assert(!distance_move_start(&m, 50, &s, 0, false));
    aborted(&m, DISTANCE_MOVE_REASON_NOT_PERMITTED);
    scenarios++;

    distance_move_init(&m);
    assert(!distance_move_start(&m, 50, NULL, 0, true));
    aborted(&m, DISTANCE_MOVE_REASON_BAD_SAMPLE);
    distance_move_init(&m);
    s.valid = false;
    assert(!distance_move_start(&m, 50, &s, 0, true));
    aborted(&m, DISTANCE_MOVE_REASON_BAD_SAMPLE);
    scenarios++;

    distance_move_init(&m);
    s = sample(0, 0, 0);
    assert(!distance_move_start(&m, 50, &s, 21, true));
    aborted(&m, DISTANCE_MOVE_REASON_STALE_SAMPLE);
    distance_move_init(&m);
    assert(!distance_move_start(&m, 50, &s, UINT32_MAX, true));
    aborted(&m, DISTANCE_MOVE_REASON_STALE_SAMPLE); /* Future timestamp. */
    scenarios++;

    begin(&m, 10000, -2000, 0);
    tick(&m, 10577, -1423, 10);
    outputs(&m, true, true);
    tick(&m, 10578, -1423, 20);
    outputs(&m, false, true);
    tick(&m, 10580, -1422, 30);
    assert(m.phase == DISTANCE_MOVE_TARGET_REACHED);
    outputs(&m, false, false);
    /* Coasting/continuing updates do not re-enable outputs. */
    tick(&m, 10600, -1400, 40);
    outputs(&m, false, false);
    s = sample(10600, -1400, 40);
    assert(!distance_move_start(&m, 100, &s, 40, true));
    scenarios++;

    begin(&m, 0, 0, 0);
    tick(&m, 577, 590, 10);
    outputs(&m, true, false);
    tick(&m, 600, 590, 20);
    assert(m.phase == DISTANCE_MOVE_TARGET_REACHED);
    outputs(&m, false, false);
    scenarios++;

    begin(&m, -100, -100, 0);
    tick(&m, 478, 478, 10);
    assert(m.phase == DISTANCE_MOVE_TARGET_REACHED);
    outputs(&m, false, false);
    scenarios++;

    begin(&m, 0, 0, 0);
    s = sample(1, 1, 10);
    assert(!distance_move_start(&m, 200, &s, 10, true));
    assert(m.target_counts == 578 && m.started_ms == 0 && m.start_left == 0);
    tick(&m, 578, 578, 10);
    assert(m.phase == DISTANCE_MOVE_TARGET_REACHED);
    scenarios++;

    begin(&m, 0, 0, 0);
    distance_move_cancel(&m);
    aborted(&m, DISTANCE_MOVE_REASON_CANCELLED);
    s = sample(0, 0, 10);
    assert(!distance_move_start(&m, 50, &s, 10, true));
    tick(&m, 1, 1, 10);
    aborted(&m, DISTANCE_MOVE_REASON_CANCELLED);
    /* Explicit reset is possible; caller must enforce a new stopped run. */
    distance_move_init(&m);
    assert(distance_move_start(&m, 50, &s, 10, true));
    scenarios++;

    begin(&m, 0, 0, 0);
    s = sample(578, 578, 10);
    distance_move_update(&m, &s, 10, false);
    aborted(&m, DISTANCE_MOVE_REASON_NOT_PERMITTED);
    scenarios++;

    begin(&m, 0, 0, 0);
    distance_move_update(&m, NULL, 10, true);
    aborted(&m, DISTANCE_MOVE_REASON_BAD_SAMPLE);
    begin(&m, 0, 0, 0);
    s = sample(1, 1, 10);
    s.valid = false;
    distance_move_update(&m, &s, 10, true);
    aborted(&m, DISTANCE_MOVE_REASON_BAD_SAMPLE);
    scenarios++;

    begin(&m, 0, 0, 0);
    s = sample(0, 0, 0);
    distance_move_update(&m, &s, 20, true);
    outputs(&m, true, true); /* Age exactly 20 ms is allowed. */
    distance_move_update(&m, &s, 21, true);
    aborted(&m, DISTANCE_MOVE_REASON_STALE_SAMPLE);
    scenarios++;

    begin(&m, 0, 0, 0);
    tick(&m, 1, 1, 20);
    outputs(&m, true, true); /* Poll gap exactly 20 ms is allowed. */
    tick(&m, 2, 2, 41);
    aborted(&m, DISTANCE_MOVE_REASON_POLL_GAP);
    scenarios++;

    begin(&m, 0, 0, 0);
    tick(&m, 1, 1, 10);
    s = sample(1, 1, 10);
    distance_move_update(&m, &s, 15, true);
    outputs(&m, true, true); /* Identical snapshot may be polled again. */
    s.left_count = 2;
    distance_move_update(&m, &s, 16, true);
    aborted(&m, DISTANCE_MOVE_REASON_BAD_SAMPLE);
    scenarios++;

    begin(&m, 0, 0, 100);
    tick(&m, 1, 1, 110);
    s = sample(2, 2, 109);
    distance_move_update(&m, &s, 111, true);
    aborted(&m, DISTANCE_MOVE_REASON_BAD_SAMPLE);
    scenarios++;

    begin(&m, 0, 0, 0);
    tick(&m, 10, 10, 10);
    tick(&m, 9, 11, 20);
    aborted(&m, DISTANCE_MOVE_REASON_COUNT_REVERSED);
    begin(&m, 0, 0, 0);
    tick(&m, 1, -1, 10);
    aborted(&m, DISTANCE_MOVE_REASON_COUNT_REVERSED);
    scenarios++;

    begin(&m, INT64_MIN, INT64_MIN, 0);
    tick(&m, INT64_MIN + 578, INT64_MIN + 578, 10);
    assert(m.phase == DISTANCE_MOVE_TARGET_REACHED);
    begin(&m, INT64_MAX - 578, INT64_MAX - 578, 0);
    tick(&m, INT64_MAX, INT64_MAX, 10);
    assert(m.phase == DISTANCE_MOVE_TARGET_REACHED);
    begin(&m, INT64_MIN, 0, 0);
    tick(&m, INT64_MAX, 0, 10);
    aborted(&m, DISTANCE_MOVE_REASON_COUNT_RANGE);
    begin(&m, 0, INT64_MIN, 0);
    tick(&m, 0, INT64_MAX, 10);
    aborted(&m, DISTANCE_MOVE_REASON_COUNT_RANGE);
    scenarios++;

    begin(&m, 0, 0, 0);
    for (i = 10; i <= 500; i += 10) {
        tick(&m, 0, i / 10, i);
        if (i < 500) outputs(&m, true, true);
    }
    aborted(&m, DISTANCE_MOVE_REASON_NO_PROGRESS);
    begin(&m, 0, 0, 0);
    for (i = 10; i <= 500; i += 10) tick(&m, i / 10, 0, i);
    aborted(&m, DISTANCE_MOVE_REASON_NO_PROGRESS);
    scenarios++;

    begin(&m, 0, 0, 0);
    for (i = 10; i <= 600; i += 10) tick(&m, 578, i / 10, i);
    outputs(&m, false, true); /* Reached side is exempt from stall check. */
    scenarios++;

    begin(&m, 0, 0, 0);
    for (i = 10; i <= 3000; i += 10) {
        tick(&m, i / 10, i / 10, i);
        if (i < 3000) outputs(&m, true, true);
    }
    aborted(&m, DISTANCE_MOVE_REASON_RUN_TIMEOUT);
    scenarios++;

    begin(&m, 0, 0, UINT32_MAX - 9U);
    tick(&m, 1, 1, UINT32_MAX);
    tick(&m, 578, 578, 9);
    assert(m.phase == DISTANCE_MOVE_TARGET_REACHED);
    scenarios++;

    /* Replay policy across all targets and many distinct initial counts. */
    for (i = 0; i < 4; ++i) {
        unsigned run;
        for (run = 0; run < 30; ++run) {
            unsigned t;
            int64_t l0 = (int64_t)run * 123 - 2000;
            int64_t r0 = -(int64_t)run * 99 + 100;
            distance_move_init(&m);
            s = sample(l0, r0, 0);
            assert(distance_move_start(&m, distances[i], &s, 0, true));
            for (t = 10; t <= 2500 && m.phase == DISTANCE_MOVE_RUNNING; t += 10) {
                unsigned ld = t * (10 + run % 3) / 10;
                unsigned rd = t * (12 + run % 4) / 10;
                tick(&m, l0 + ld, r0 + rd, t);
                {
                    distance_move_output_t o = distance_move_output(&m);
                    assert(o.left_run == (ld < expected[i]));
                    assert(o.right_run == (rd < expected[i]));
                }
            }
            assert(m.phase == DISTANCE_MOVE_TARGET_REACHED);
        }
    }
    scenarios++;
    printf("PASS %u scenario groups including 120 synthetic target runs\n", scenarios);
    return 0;
}
