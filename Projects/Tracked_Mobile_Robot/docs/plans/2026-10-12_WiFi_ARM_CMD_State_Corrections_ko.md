# ARM/CMD state 실제 저장본 수정 안내 — 2026-10-12

실제 저장한 `.h/.c`를 읽고 원래 안내와 대조했다. CMake의 다섯 source 등록과 의존성은 맞다.
현재 저장본 PC 검사는 첫 `statc`에서 컴파일 실패해 **0 tests / ERROR1**이다. 이는 27개 동작 검사 실패가 아니라 실행 전 컴파일 실패다.
안내의 C 블록은 앞서 PC27 PASS였던 snapshot과 byte 내용이 같음을 확인했다. 사용자 수정본의 PASS는 저장 후 별도로 검사한다.

## 한 번에 수정할 곳

줄 번호는 최초 저장본 기준이며 수정하면 달라질 수 있다. 표의 변경을 한 번에 반영하거나, 아래 두 완성본으로 전체 교체하면 된다. CMake는 유지한다.

| 파일·줄 | 현재 내용·누락 | 올바른 내용·이유 |
| --- | --- | --- |
| h 92~93 | `stop_ack` 없음 | `zero_ack` 다음 `bool stop_ack;` 추가. DISARM ACK 수신을 기억 |
| h 96 | `uint32_t confirm_tel_generation` | `uint64_t confirm_tel_generation`. `tel_generation`과 같은 폭으로 비교 |
| h 129~131 | `wifi_control_state_stop` 선언 없음 | 아래 header의 stop 선언 추가. 다른 파일에서 명시적으로 정지를 요청하는 공개 API |
| c 3 | `statc` | `static` |
| c 26·28 | `staic`, `wifhin` | `static`, `within` |
| c 128 | `deadline(s, now)` | `deadlines(s, now)` |
| c 136 | `.initialized = true;` | `.initialized = true,` — 구조체 초기화 항목 구분 |
| c 153~156 | `satrtup_ready`, `requeset_live` | `startup_ready`, `request_live` |
| c 154 | TEL 상태에 `WIFI_CONTROL_ARM` 대조, zero·요청 종류 검사 누락 | 아래 `begin_arm` 조건 전체 사용. TEL은 `WIFI_CONTROL_STM_DISARMED`, 요청은 `WIFI_CONTROL_ARM`으로 각각 확인하고 `!zero(&s->tel)`도 검사 |
| c 181 | `*!event_time` | `!event_time` — 앞의 `*` 제거 |
| c 268 | `wiif_control_op_t` | `wifi_control_op_t` |
| c 351 | `contirm_tel_generation` | `confirm_tel_generation` |
| c 359 | `WIFI_CONTRIL_STM_ARMED` | `WIFI_CONTROL_STM_ARMED` |
| c 389 | `WIFI_CONTROL_ACTION_DISARM` | `WIFI_CONTROL_ACTION_SEND_DISARM` |

들여쓰기·중괄호 줄바꿈·주석 `field/fields`·끝줄 차이는 이번 기능 문제에 해당하지 않는다.

## 왜 세 가지 ARM 조건이 필요한가

`s->tel.state`는 STM이 알려준 보드 상태이고, `r->type`은 브라우저에서 받은 요청 종류다.
두 enum의 첫 값이 지금 모두 0이어도 같은 뜻의 필드가 아니다. 보드는 DISARMED여야 하고 요청은 ARM이어야 한다.
`zero(&s->tel)`은 명령과 PWM이 모두 0인지 확인한다. 상태 이름 하나만 보고 새 제어를 예약하지 않도록 한다.

상태 흐름은 `IDLE → ARM_PENDING → ZERO_PENDING → ACTIVE`다. ARM ACK 뒤 새 zero CMD의 ACK와 이후 TEL을 확인해야 ACTIVE가 된다.
만료·끊김·FAULT는 `STOPPING`으로 보내고 owner를 취소한다. DISARM ACK와 이후 zero/non-ARMED TEL을 확인해야 IDLE로 돌아가며, 확인 실패는 BLOCKED다.
ACK만으로 상태를 완료하지 않고 TEL 세대를 같이 확인하는 이유는 이전 TEL을 새 명령의 결과로 오인하지 않기 위해서다.
시간 경계에서는 만료 검사가 먼저다. 늦은 ACK/TEL과 재접속으로 기존 허가를 자동 복구하지 않는다.

## 정확한 교체 범위와 완성본

`03_Firmware/esp32_wifi_link/main/wifi_control_state.h`의 전체 내용을 다음 블록으로 교체한다.

```c
#ifndef WIFI_CONTROL_STATE_H
#define WIFI_CONTROL_STATE_H

#include "wifi_control_owner.h"

#define WIFI_CONTROL_QUEUE_MS 50U
#define WIFI_CONTROL_ACK_MS 150U
#define WIFI_CONTROL_FIRST_CMD_MS 250U
#define WIFI_CONTROL_SOURCE_MS 200U
#define WIFI_CONTROL_TEL_MS 250U
#define WIFI_CONTROL_STM_TIMEOUT_MS 300U
#define WIFI_CONTROL_STOP_SEND_MS 150U
#define WIFI_CONTROL_STOP_CONFIRM_MS 300U
#define WIFI_CONTROL_STM_CLOCK_SLOP_MS 250U

typedef enum {
    WIFI_CONTROL_IDLE,
    WIFI_CONTROL_ARM_PENDING,
    WIFI_CONTROL_ZERO_PENDING,
    WIFI_CONTROL_ACTIVE,
    WIFI_CONTROL_STOPPING,
    WIFI_CONTROL_BLOCKED
} wifi_control_phase_t;

typedef enum {
    WIFI_CONTROL_OP_NONE,
    WIFI_CONTROL_OP_ARM,
    WIFI_CONTROL_OP_CMD,
    WIFI_CONTROL_OP_DISARM
} wifi_control_op_t;

typedef enum {
    WIFI_CONTROL_REASON_NONE,
    WIFI_CONTROL_REASON_MANUAL_STOP,
    WIFI_CONTROL_REASON_OWNER_CLOSED,
    WIFI_CONTROL_REASON_INPUT_EXPIRED,
    WIFI_CONTROL_REASON_BAD_INPUT,
    WIFI_CONTROL_REASON_STARTUP,
    WIFI_CONTROL_REASON_TEL_STALE,
    WIFI_CONTROL_REASON_STM_FAULT,
    WIFI_CONTROL_REASON_STM_STATE,
    WIFI_CONTROL_REASON_STM_CLOCK,
    WIFI_CONTROL_REASON_CLOCK_BACKWARD,
    WIFI_CONTROL_REASON_ACK_TIMEOUT,
    WIFI_CONTROL_REASON_FIRST_CMD_TIMEOUT,
    WIFI_CONTROL_REASON_SOURCE_TIMEOUT,
    WIFI_CONTROL_REASON_STM_ERR,
    WIFI_CONTROL_REASON_TX_FAILED,
    WIFI_CONTROL_REASON_STOP_UNCONFIRMED
} wifi_control_reason_t;

typedef enum {
    WIFI_CONTROL_STM_DISARMED,
    WIFI_CONTROL_STM_ARMED,
    WIFI_CONTROL_STM_FAULT
} wifi_control_stm_state_t;

/* Validated TEL fields. CPS is not an output-stop confirmation. */
typedef struct {
    wifi_control_stm_state_t state;
    uint32_t t_ms;
    uint32_t last_seq;
    uint32_t command_age_ms;
    int32_t vx_mmps;
    int32_t w_mradps;
    int32_t left_pwm;
    int32_t right_pwm;
} wifi_control_tel_t;

#define WIFI_CONTROL_ACTION_INVALIDATE_INPUTS 1U
#define WIFI_CONTROL_ACTION_SEND_DISARM 2U

/* One instance per ESP boot; one serialized caller, no internal locks. */
typedef struct {
    bool initialized;
    bool startup_ready;
    wifi_control_owner_t owner;
    wifi_control_phase_t phase;
    wifi_control_reason_t reason;
    wifi_control_op_t pending;
    uint32_t pending_seq;
    uint64_t last_now_ms;
    uint64_t pending_sent_ms;
    uint64_t arm_accepted_ms;
    uint64_t arm_expires_ms;
    uint64_t arm_sent_ms;
    uint64_t last_cmd_sent_ms;
    uint64_t stop_started_ms;
    uint64_t stop_ack_ms;
    bool arm_sent;
    bool have_cmd;
    bool zero_ack;
    bool stop_ack;
    bool need_disarm;
    uint32_t confirm_seq;
    uint32_t confirm_stm_ms;
    uint64_t confirm_tel_generation;
    bool have_tel;
    wifi_control_tel_t tel;
    uint64_t tel_received_ms;
    uint64_t tel_generation;
    uint64_t stm_progress_ms;
} wifi_control_state_t;

void wifi_control_state_init(wifi_control_state_t *state, uint32_t boot_id);

/* Parser/ticket/request-id checks precede admission. out changes on success only. */
bool wifi_control_state_begin_arm(
    wifi_control_state_t *state, const wifi_control_request_t *request,
    bool startup_ready, bool uart_idle, uint64_t now_ms,
    uint32_t *out_control_id);

/* Immediately before TX; caller also checks live connection/ticket queue data. */
bool wifi_control_state_arm_sent(
    wifi_control_state_t *state, uint32_t ws_session_id,
    uint32_t control_id, uint32_t seq, uint64_t now_ms);
bool wifi_control_state_cmd_sent(
    wifi_control_state_t *state, const wifi_control_request_t *request,
    uint32_t seq, uint64_t now_ms);
bool wifi_control_state_disarm_sent(
    wifi_control_state_t *state, uint32_t seq, uint64_t now_ms);

/* Use receive time, never a browser timestamp. reply t_ms comes from STM. */
bool wifi_control_state_reply(
    wifi_control_state_t *state, wifi_control_op_t op,
    uint32_t seq, bool ok, uint32_t stm_t_ms, uint64_t now_ms);
void wifi_control_state_tel(
    wifi_control_state_t *state, const wifi_control_tel_t *tel,
    uint64_t now_ms);
void wifi_control_state_poll(
    wifi_control_state_t *state, bool startup_ready, uint64_t now_ms);
void wifi_control_state_stop(
    wifi_control_state_t *state, wifi_control_reason_t reason,
    uint64_t now_ms);
void wifi_control_state_owner_closed(
    wifi_control_state_t *state, uint32_t ws_session_id, uint64_t now_ms);
void wifi_control_state_tx_failed(wifi_control_state_t *state, uint64_t now_ms);

/* Level flags: revoke inputs first, then dispatch one DISARM. No automatic retry. */
uint32_t wifi_control_state_actions(const wifi_control_state_t *state);

#endif
```

`03_Firmware/esp32_wifi_link/main/wifi_control_state.c`의 전체 내용을 다음 블록으로 교체한다.

```c
#include "wifi_control_state.h"

static bool live(const wifi_control_state_t *s)
{
    return s != NULL && s->initialized;
}

static bool controlling(const wifi_control_state_t *s)
{
    return s->phase == WIFI_CONTROL_ARM_PENDING ||
        s->phase == WIFI_CONTROL_ZERO_PENDING ||
        s->phase == WIFI_CONTROL_ACTIVE;
}

static bool within(uint64_t now, uint64_t then, uint32_t budget)
{
    return now >= then && now - then < budget;
}

static bool zero(const wifi_control_tel_t *tel)
{
    return tel->vx_mmps == 0 && tel->w_mradps == 0 &&
        tel->left_pwm == 0 && tel->right_pwm == 0;
}

static bool fresh(const wifi_control_state_t *s, uint64_t now)
{
    return s->have_tel && within(now, s->tel_received_ms, WIFI_CONTROL_TEL_MS);
}

static bool request_live(const wifi_control_request_t *r, uint64_t now)
{
    return r->expires_ms > r->accepted_ms &&
        r->expires_ms - r->accepted_ms <= 150U &&
        now < r->expires_ms && within(now, r->accepted_ms, WIFI_CONTROL_QUEUE_MS);
}

static void blocked(wifi_control_state_t *s, wifi_control_reason_t reason)
{
    wifi_control_owner_revoke(&s->owner);
    s->phase = WIFI_CONTROL_BLOCKED;
    s->reason = reason;
    s->pending = WIFI_CONTROL_OP_NONE;
    s->need_disarm = false;
    s->zero_ack = false;
    s->stop_ack = false;
}

static void stop_now(
    wifi_control_state_t *s, wifi_control_reason_t reason, uint64_t now)
{
    if (s->phase == WIFI_CONTROL_STOPPING ||
        (s->phase == WIFI_CONTROL_BLOCKED &&
         reason != WIFI_CONTROL_REASON_MANUAL_STOP)) {
        return;
    }
    wifi_control_owner_revoke(&s->owner);
    s->phase = WIFI_CONTROL_STOPPING;
    s->reason = reason;
    s->pending = WIFI_CONTROL_OP_NONE;
    s->need_disarm = true;
    s->stop_started_ms = now;
    s->zero_ack = false;
    s->stop_ack = false;
    s->arm_sent = false;
    s->have_cmd = false;
}

static bool clock_accept(wifi_control_state_t *s, uint64_t now)
{
    if (now < s->last_now_ms) {
        if (controlling(s)) {
            stop_now(s, WIFI_CONTROL_REASON_CLOCK_BACKWARD, s->last_now_ms);
        } else if (s->phase == WIFI_CONTROL_STOPPING) {
            blocked(s, WIFI_CONTROL_REASON_CLOCK_BACKWARD);
        }
        return false;
    }
    s->last_now_ms = now;
    return true;
}

static void deadlines(wifi_control_state_t *s, uint64_t now)
{
    if (s->phase == WIFI_CONTROL_STOPPING) {
        if ((s->need_disarm &&
             !within(now, s->stop_started_ms, WIFI_CONTROL_STOP_SEND_MS)) ||
            (s->pending == WIFI_CONTROL_OP_DISARM &&
             !within(now, s->pending_sent_ms, WIFI_CONTROL_ACK_MS)) ||
            (s->stop_ack &&
             !within(now, s->stop_ack_ms, WIFI_CONTROL_STOP_CONFIRM_MS))) {
            blocked(s, WIFI_CONTROL_REASON_STOP_UNCONFIRMED);
        }
        return;
    }
    if (!controlling(s)) {
        return;
    }
    wifi_control_reason_t reason = WIFI_CONTROL_REASON_NONE;
    if (!s->startup_ready) {
        reason = WIFI_CONTROL_REASON_STARTUP;
    } else if (!fresh(s, now)) {
        reason = WIFI_CONTROL_REASON_TEL_STALE;
    } else if (s->phase == WIFI_CONTROL_ARM_PENDING && !s->arm_sent &&
        (now >= s->arm_expires_ms ||
         !within(now, s->arm_accepted_ms, WIFI_CONTROL_QUEUE_MS))) {
        reason = WIFI_CONTROL_REASON_INPUT_EXPIRED;
    } else if (s->pending != WIFI_CONTROL_OP_NONE &&
        !within(now, s->pending_sent_ms, WIFI_CONTROL_ACK_MS)) {
        reason = WIFI_CONTROL_REASON_ACK_TIMEOUT;
    } else if (s->arm_sent && !s->have_cmd &&
        !within(now, s->arm_sent_ms, WIFI_CONTROL_FIRST_CMD_MS)) {
        reason = WIFI_CONTROL_REASON_FIRST_CMD_TIMEOUT;
    } else if (s->have_cmd &&
        !within(now, s->last_cmd_sent_ms, WIFI_CONTROL_SOURCE_MS)) {
        reason = WIFI_CONTROL_REASON_SOURCE_TIMEOUT;
    }
    if (reason != WIFI_CONTROL_REASON_NONE) {
        stop_now(s, reason, now);
    }
}

static bool event_time(wifi_control_state_t *s, uint64_t now)
{
    if (!live(s) || !clock_accept(s, now)) {
        return false;
    }
    deadlines(s, now);
    return true;
}

void wifi_control_state_init(wifi_control_state_t *s, uint32_t boot_id)
{
    if (s != NULL) {
        *s = (wifi_control_state_t) {
            .initialized = true,
            .phase = WIFI_CONTROL_IDLE
        };
        wifi_control_owner_init(&s->owner, boot_id);
    }
}

bool wifi_control_state_begin_arm(
    wifi_control_state_t *s, const wifi_control_request_t *r,
    bool startup_ready, bool uart_idle, uint64_t now,
    uint32_t *out_control_id)
{
    if (!live(s) || r == NULL || out_control_id == NULL) {
        return false;
    }
    s->startup_ready = startup_ready;
    if (!event_time(s, now) || s->phase != WIFI_CONTROL_IDLE ||
        !startup_ready || !uart_idle || !fresh(s, now) ||
        s->tel.state != WIFI_CONTROL_STM_DISARMED || !zero(&s->tel) ||
        r->type != WIFI_CONTROL_ARM || r->expected_boot_id != s->owner.boot_id ||
        r->ws_session_id == 0U || r->control_id != 0U ||
        !request_live(r, now)) {
        return false;
    }
    uint32_t id;
    if (wifi_control_owner_reserve(&s->owner, r->ws_session_id, &id) != WIFI_OWNER_OK) {
        return false;
    }
    s->phase = WIFI_CONTROL_ARM_PENDING;
    s->reason = WIFI_CONTROL_REASON_NONE;
    s->arm_accepted_ms = r->accepted_ms;
    s->arm_expires_ms = r->expires_ms;
    s->arm_sent = false;
    s->have_cmd = false;
    s->zero_ack = false;
    s->stop_ack = false;
    s->need_disarm = false;
    s->pending = WIFI_CONTROL_OP_NONE;
    *out_control_id = id;
    return true;
}

bool wifi_control_state_arm_sent(
    wifi_control_state_t *s, uint32_t session, uint32_t id,
    uint32_t seq, uint64_t now)
{
    if (!event_time(s, now) || s->phase != WIFI_CONTROL_ARM_PENDING ||
        s->arm_sent ||
        !wifi_control_owner_matches(&s->owner, s->owner.boot_id, session, id)) {
        return false;
    }
    if (s->tel.state != WIFI_CONTROL_STM_DISARMED || !zero(&s->tel)) {
        stop_now(s, WIFI_CONTROL_REASON_STM_STATE, now);
        return false;
    }
    s->arm_sent = true;
    s->arm_sent_ms = now;
    s->pending = WIFI_CONTROL_OP_ARM;
    s->pending_seq = seq;
    s->pending_sent_ms = now;
    return true;
}

bool wifi_control_state_cmd_sent(
    wifi_control_state_t *s, const wifi_control_request_t *r,
    uint32_t seq, uint64_t now)
{
    if (r == NULL || !event_time(s, now) ||
        (s->phase != WIFI_CONTROL_ZERO_PENDING && s->phase != WIFI_CONTROL_ACTIVE) ||
        !wifi_control_owner_matches(&s->owner, r->expected_boot_id,
                                    r->ws_session_id, r->control_id)) {
        return false;
    }
    /* Old queue identity cannot cancel a newer owner; a live owner's bad data can. */
    if (r->type != WIFI_CONTROL_CMD || r->vx_mmps != 0 || r->w_mradps != 0) {
        stop_now(s, WIFI_CONTROL_REASON_BAD_INPUT, now);
        return false;
    }
    if (!request_live(r, now)) {
        stop_now(s, WIFI_CONTROL_REASON_INPUT_EXPIRED, now);
        return false;
    }
    if (s->pending != WIFI_CONTROL_OP_NONE) {
        return false;
    }
    s->pending = WIFI_CONTROL_OP_CMD;
    s->pending_seq = seq;
    s->pending_sent_ms = now;
    s->last_cmd_sent_ms = now;
    s->have_cmd = true;
    return true;
}

void wifi_control_state_poll(
    wifi_control_state_t *s, bool startup_ready, uint64_t now)
{
    if (live(s)) {
        s->startup_ready = startup_ready;
        (void)event_time(s, now);
    }
}

void wifi_control_state_stop(
    wifi_control_state_t *s, wifi_control_reason_t reason, uint64_t now)
{
    if (live(s) && clock_accept(s, now)) {
        stop_now(s, reason == WIFI_CONTROL_REASON_NONE ?
                 WIFI_CONTROL_REASON_MANUAL_STOP : reason, now);
    }
}

void wifi_control_state_owner_closed(
    wifi_control_state_t *s, uint32_t session, uint64_t now)
{
    if (live(s) && session != 0U && s->owner.ws_session_id == session) {
        wifi_control_state_stop(s, WIFI_CONTROL_REASON_OWNER_CLOSED, now);
    }
}

bool wifi_control_state_disarm_sent(
    wifi_control_state_t *s, uint32_t seq, uint64_t now)
{
    if (!event_time(s, now) || s->phase != WIFI_CONTROL_STOPPING || !s->need_disarm) {
        return false;
    }
    s->need_disarm = false;
    s->pending = WIFI_CONTROL_OP_DISARM;
    s->pending_seq = seq;
    s->pending_sent_ms = now;
    return true;
}

bool wifi_control_state_reply(
    wifi_control_state_t *s, wifi_control_op_t op,
    uint32_t seq, bool ok, uint32_t stm_t_ms, uint64_t now)
{
    if (!event_time(s, now) || op == WIFI_CONTROL_OP_NONE ||
        op != s->pending || seq != s->pending_seq) {
        return false;
    }
    if (!ok) {
        if (op == WIFI_CONTROL_OP_DISARM) {
            blocked(s, WIFI_CONTROL_REASON_STM_ERR);
        } else {
            stop_now(s, WIFI_CONTROL_REASON_STM_ERR, now);
        }
        return true;
    }
    s->pending = WIFI_CONTROL_OP_NONE;
    if (op == WIFI_CONTROL_OP_ARM) {
        s->phase = WIFI_CONTROL_ZERO_PENDING;
    } else {
        s->confirm_seq = seq;
        s->confirm_stm_ms = stm_t_ms;
        s->confirm_tel_generation = s->tel_generation;
        if (op == WIFI_CONTROL_OP_CMD) {
            s->zero_ack = true;
        } else {
            s->stop_ack = true;
            s->stop_ack_ms = now;
        }
    }
    return true;
}

static bool stm_clock_bad(
    const wifi_control_state_t *s, const wifi_control_tel_t *tel, uint64_t now)
{
    if (!s->have_tel) {
        return false;
    }
    const uint64_t delta = (uint32_t)(tel->t_ms - s->tel.t_ms);
    const uint64_t elapsed = now - s->tel_received_ms;
    const uint64_t difference = delta > elapsed ? delta - elapsed : elapsed - delta;
    return difference > WIFI_CONTROL_STM_CLOCK_SLOP_MS ||
        (delta == 0U && !within(now, s->stm_progress_ms, WIFI_CONTROL_TEL_MS));
}

void wifi_control_state_tel(
    wifi_control_state_t *s, const wifi_control_tel_t *tel, uint64_t now)
{
    if (tel == NULL || !event_time(s, now)) {
        return;
    }
    if (tel->state != WIFI_CONTROL_STM_DISARMED &&
        tel->state != WIFI_CONTROL_STM_ARMED &&
        tel->state != WIFI_CONTROL_STM_FAULT) {
        if (controlling(s)) {
            stop_now(s, WIFI_CONTROL_REASON_STM_STATE, now);
        }
        return;
    }
    const bool bad_clock = stm_clock_bad(s, tel, now);
    if (!s->have_tel || tel->t_ms != s->tel.t_ms) {
        s->stm_progress_ms = now;
    }
    s->have_tel = true;
    s->tel = *tel;
    s->tel_received_ms = now;
    if (s->tel_generation == UINT64_MAX) {
        blocked(s, WIFI_CONTROL_REASON_STM_CLOCK);
        return;
    }
    ++s->tel_generation;
    if (controlling(s)) {
        if (bad_clock) {
            stop_now(s, WIFI_CONTROL_REASON_STM_CLOCK, now);
        } else if (tel->state == WIFI_CONTROL_STM_FAULT) {
            stop_now(s, WIFI_CONTROL_REASON_STM_FAULT, now);
        } else if (!zero(tel) ||
            (s->phase == WIFI_CONTROL_ACTIVE &&
             (tel->state != WIFI_CONTROL_STM_ARMED ||
              tel->command_age_ms >= WIFI_CONTROL_STM_TIMEOUT_MS))) {
            stop_now(s, WIFI_CONTROL_REASON_STM_STATE, now);
        }
    }
    const bool after_ack = s->tel_generation > s->confirm_tel_generation &&
        (uint32_t)(tel->t_ms - s->confirm_stm_ms) < UINT32_C(0x80000000);
    if (s->phase == WIFI_CONTROL_ZERO_PENDING && s->zero_ack && after_ack &&
        tel->last_seq == s->confirm_seq && tel->state == WIFI_CONTROL_STM_ARMED &&
        zero(tel) && tel->command_age_ms < WIFI_CONTROL_STM_TIMEOUT_MS) {
        s->phase = WIFI_CONTROL_ACTIVE;
    } else if (s->phase == WIFI_CONTROL_STOPPING && s->stop_ack && after_ack &&
        tel->last_seq == s->confirm_seq) {
        if (bad_clock || tel->state == WIFI_CONTROL_STM_ARMED || !zero(tel)) {
            blocked(s, WIFI_CONTROL_REASON_STOP_UNCONFIRMED);
        } else {
            s->phase = WIFI_CONTROL_IDLE;
            s->reason = WIFI_CONTROL_REASON_NONE;
            s->stop_ack = false;
            s->zero_ack = false;
        }
    }
}

void wifi_control_state_tx_failed(wifi_control_state_t *s, uint64_t now)
{
    if (!event_time(s, now)) {
        return;
    }
    if (s->phase == WIFI_CONTROL_STOPPING) {
        blocked(s, WIFI_CONTROL_REASON_TX_FAILED);
    } else if (controlling(s)) {
        stop_now(s, WIFI_CONTROL_REASON_TX_FAILED, now);
    }
}

uint32_t wifi_control_state_actions(const wifi_control_state_t *s)
{
    if (!live(s) ||
        (s->phase != WIFI_CONTROL_STOPPING && s->phase != WIFI_CONTROL_BLOCKED)) {
        return 0U;
    }
    return WIFI_CONTROL_ACTION_INVALIDATE_INPUTS |
        (s->need_disarm ? WIFI_CONTROL_ACTION_SEND_DISARM : 0U);
}
```

## 저장 후 확인

두 파일을 저장한 뒤 실제 저장본으로 PC27 검사를 다시 수행한다. 정상 전환·시간 경계·seq/type/owner·늦은 응답·FAULT·정지 확인·자동 복구 금지의 27개가 모두 PASS여야 한다.
그 뒤 사용자가 ESP 전체 빌드를 한다. 이번 등록만으로 main/UART/브라우저 ARM/CMD 실행은 연결되지 않으며 PC PASS를 보드 시험 결과로 확대하지 않는다.
Codex가 사용자 펌웨어를 직접 수정하거나 ESP 빌드·플래시·Git 반영을 수행하지 않았다.

[최초 저장본·컴파일 실패 원본](../../assets/logs/wifi_link/2026-10-12_state_review/manifest.json) · [기존 후보27 PASS](../../assets/logs/wifi_link/2026-10-11_state_candidate/pc_state_candidate.txt)

