# ARM/CMD 네 번째 입력 블록 — 상태·시간 제한·응답과 정지 확인

작성일: **2026-10-11**. 갱신: **2026-10-12**. 상태: **최종 사용자 저장본 PC27 PASS / state 포함 ESP 전체 빌드 성공 사용자 확인**.
다음은 main의 제어 실행 adapter 연결이다. 새 플래시·보드 ARM/CMD 결과는 미확인이다.
10/12 최종 `.h/.c`와 CMake를 대조하고 실제 저장본 27 tests/PASS를 확인했다. [최종 근거](../../assets/logs/wifi_link/2026-10-12_state_review/saved_revision_4/manifest.json)와 [진행 기록](../progress/2026-10-12_progress.md)을 따른다. 아래 최초 컴파일 실패·미입력 설명은 입력 당시 이력이다.
10/12 실제 `.h/.c`와 CMake를 검토했다. CMake 등록은 맞으며 실제 저장본은 0 tests/ERROR1이다. [일괄 수정 안내](2026-10-12_WiFi_ARM_CMD_State_Corrections_ko.md)를 먼저 따른다. 아래 C 블록은 검사했던 후보와 동일하다.
선행: parser PC15·ticket PC12·owner PC9 실제 저장본 PASS, owner 포함 ESP 빌드 성공 사용자 확인.
기준: [초기 계약](2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md).

오늘 두 보드 UART 재연결 뒤 DISARM ACK·PONG·STARTUP READY, TEL과 PWM0/0·drop/err0/0을 제공 로그에서 확인했다.
후속 사용자가 핀의 바닥 접촉 때문에 CPS가 튀었고 보드를 띄우니 현상이 사라졌다고 확인했다. 해소 후 정확한 수치는 미보고다.
엔코더 미연결 조건의 CPS는 실제 속도/정지 증거가 아니다. 이번 모듈의 TEL 정지 확인은 command/PWM0이며 CPS를 사용하지 않는다.

## 이번 블록이 맡는 일

parser는 요청을 읽고, ticket은 요청의 유효시간/일회성을 검사하고, owner는 연결·제어 번호를 기억한다.
이번 state는 **다음 동작을 허용할 단계인지, 기다림이 끝났는지, 정지를 확인했는지**를 결정한다.

```text
IDLE → 수동 ARM 접수/예약 → ARM_PENDING
  → 실제 ARM 송신 + 같은 seq/type의 ACK → ZERO_PENDING
  → 새 zero CMD 송신 + ACK + ACK 이후 ARMED/zero TEL → ACTIVE
  → 끊김/만료/FAULT/오류 → STOPPING (owner 제거·입력 폐기 요구)
  → DISARM ACK + ACK 이후 non-ARMED/zero TEL → IDLE
  → 정지 확인 실패 → BLOCKED → 새 수동 DISARM으로만 다시 확인
```

ARM ACK만으로 ACTIVE로 바꾸지 않는다. DISARM ACK만으로 IDLE로 바꾸지도 않는다.
송신마다 pending 한 개를 기록하고 seq와 종류를 함께 대조한다. 만료를 먼저 검사하므로 경계/늦은 ACK는 허가를 복원하지 않는다.
첫 CMD/후속 입력 시각은 UART 송신 시점이며 PING·TEL·ACK 수신으로 연장하지 않는다.

| 조건 | 시간·동작 |
| --- | --- |
| ARM/CMD 큐·ticket | accepted부터50ms 미만, expires 이전. ticket 발급/소비 자체는 기존 모듈/후속 adapter |
| ARM/CMD/DISARM 응답 | 송신부터150ms 미만. 기한 도달은 만료 |
| 첫 zero CMD | ARM 송신부터250ms 미만 |
| 후속 새 CMD | 마지막 CMD 송신부터200ms 미만 |
| 제어 TEL | 마지막 정상 수신부터250ms 미만 |
| STM CMD timeout | 후속 UART adapter가300ms 고정값으로 생성. 이번 모듈은 UART 문자열을 생성하지 않음 |
| stop 송신 대기 | **추가 로컬 규칙:** 취소 뒤150ms까지 송신 기록이 없으면 BLOCKED. 무한 STOPPING 대기 방지이며 실제 정지 시간 보장이 아님 |
| stop ACK 후 TEL 확인 | 300ms 미만, ACK 이후 TEL·STM 시각·seq·non-ARMED·명령/PWM0 필요 |
| STM 시각 대조 | **초기 보수적 규칙:** u32 delta와 ESP 경과의 차이250ms 초과 또는 STM 시각250ms 정체 시 취소. wrap 허용, 재기동/노이즈 확정 판별 아님 |

STM 시각 차이 허용값은 실측 전 설계값이며 제어를 끊는 방향으로 사용한다. 이미 UART에 보낸 프레임은 회수하지 못한다.
BLOCKED는 정지가 증명되지 않았다는 뜻이며 물리 출력이 반드시 멈췄다는 뜻이 아니다.

## 모듈의 경계와 후속 연결

- owner를 내부에 보관하며 번호 공급기는 취소 후 유지한다. state의 공개 필드는 관찰용이고 adapter가 임의로 phase/시간/owner를 덮어쓰지 않는다.
- ticket/request ID/실제 WebSocket 생존·UART 사용 가능·값 복사 큐/우선순위는 **후속 실행 adapter**가 담당한다. parser 성공/사용자 입력과 서버 수신 시각을 바탕으로 `request.accepted_ms/expires_ms/ws_session_id`를 채운다.
- ARM 접수 전에 해당 ticket이 발급/미소비 상태인지 검사하고, 큐 확보/예약 성공 때 소비한다. 실패 후에는 owner·ticket을 함께 폐기한다. 이 순서의 원자성/RTOS mutex는 이번 순수 C 검사로 증명하지 않는다.
- `arm_sent/cmd_sent/disarm_sent`는 실제 UART 쓰기 **직전** 최종 검사와 pending 등록이다. 성공 반환 이후 실제 쓰기가 실패/부분 완료면 즉시 `tx_failed`를 전달한다. 단순 함수 호출을 물리 TX 증거로 기록하지 않는다.
- `actions()`의 INVALIDATE_INPUTS는 모든 관련 ticket·미송신 ARM/CMD를 즉시 폐기하라는 요구다. 그 뒤 SEND_DISARM을 UART 담당이 우선 처리한다. level flag이므로 폐기는 반복해도 안전하게 구현하며, DISARM pending 등록 뒤 SEND 비트는 사라진다.
- STOPPING의 반복 stop은 기한을 늘리지 않는다. BLOCKED에서 재시도는 새 수동 DISARM만 허용한다. 자동 ARM/CMD/DISARM retry 없음.
- 다른/이전 owner의 대기 CMD는 송신 거부하며 현재 owner를 되살리거나 바꾸지 않는다. 입력 접수 단계에서 현재 owner의 잘못된 요청은 adapter가 stop으로 연결한다.
- ZERO_PENDING에서는 ARM 이전 DISARMED TEL을 완료 증거로 쓰지 않는다. ARMED/zero 확인 전에는 zero CMD만 반복하며 source/ACK/TEL 감시를 유지한다.
- 정상 ACK 뒤 새 TEL 수신 이벤트와 STM ACK t_ms 이후 조건을 함께 확인한다. ACTIVE 이후 비ARMED/FAULT·명령/PWM 비영점·command age300ms 이상이면 취소한다.
- 모든 호출은 **하나의 직렬화된 실행 문맥**에서 한다. monotonic ESP uint64 ms를 넘기며 브라우저 시각을 사용하지 않는다. UART watchdog 점검20ms 목표·네트워크/큐 경합은 다음 연결에서 검증한다.
- 제어 중 일반 PING은 후속 adapter가 CONTROL_ACTIVE로 거부한다. 기존 W5의500ms 응답 대기를 제어 UART 처리에 끼워 넣지 않는다. 이 모듈에는 PING 이벤트나 lease 연장 API가 없다.
- 이번 입력은 기존 main/STM/브라우저를 연결하지 않는다. 낱개 보드 PC7 FAULT를 우회하지 않으며 AC-B/AC-S는 새 실행 경로를 만든 뒤 진행한다.

owner를 별도 모듈로 둔 상태에서 state가 owner를 포함하는 방식을 선택했다.
state 안에서 예약/취소를 함께 처리하면 STOPPING/BLOCKED에서 새 owner를 예약하는 실수를 줄일 수 있다.
콜백/태스크별로 별도 state를 만들거나, W5의 요청별 owner를 이 owner로 재사용하지 않는다.

## 정확한 입력 범위

읽는 순서는 다음과 같다. 아래 호출 흐름은 후속 adapter의 연결 기준이며 현재 main이 호출하고 있다는 뜻이 아니다.

| 함수 | 언제 부르는가·무엇을 기억하는가 |
| --- | --- |
| init | ESP 부팅 때 한 번. owner 번호 공급기와 IDLE을 준비 |
| tel | 검증된 새 STM TEL 수신. 상태/명령/PWM·시각·수신 세대를 기억 |
| begin_arm | 수동 ARM 접수 조건/ticket 확인 후. 연결을 예약하고 ARM_PENDING |
| arm_sent / cmd_sent | UART 쓰기 직전. 기한/소유권을 재검사하고 기다릴 seq/type·송신 시각 등록 |
| reply | STM ACK/ERR 수신. 만료/seq/type을 확인하고 ZERO_PENDING 또는 TEL 확인 대기로 이동 |
| poll | UART 루프의 시간 점검. 입력/응답/TEL 기한이 끝나면 STOPPING/BLOCKED |
| stop / owner_closed / tx_failed | 수동 정지·owner 종료·실제 UART 쓰기 실패. 허가를 지우고 정지 요구 |
| actions / disarm_sent | 입력을 먼저 폐기한 뒤 우선 DISARM 송신. ACK와 새 TEL까지 기다림 |

`pending`은 한 UART 응답 대기, `phase`는 제어 전체 단계다. ACK를 받으면 pending은 끝나도 owner/phase는 유지될 수 있다.
`reason`은 취소/확인 실패의 이유, `tel_generation`은 ACK 전후 TEL을 구분하는 ESP 수신 순번이다.

`03_Firmware/esp32_wifi_link/main`에 다음 두 새 파일을 입력하고 CMake source 다섯 개를 확인한다.

1. `wifi_control_state.h`: 아래 header 전체.
2. `wifi_control_state.c`: 아래 source 전체.
3. `CMakeLists.txt`: 아래 CMake 블록 전체. 기존 main/parser/ticket/owner를 보존한다.

### main/wifi_control_state.h — 새 파일 전체

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

### main/wifi_control_state.c — 새 파일 전체

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

### main/CMakeLists.txt — 전체 교체

```cmake
idf_component_register(
    SRCS "wifi_link_main.c" "wifi_control_contract.c"
         "wifi_control_ticket.c" "wifi_control_owner.c"
         "wifi_control_state.c"
    INCLUDE_DIRS "."
    PRIV_REQUIRES
        esp_wifi esp_event esp_netif esp_http_server
        esp_timer esp_system esp_hw_support nvs_flash freertos
        esp_driver_uart
)
```

## 검사와 다음 행동

PC 검사는 [test_wifi_control_state.py](../../03_Firmware/tests/test_wifi_control_state.py)와
[실제 C fixture](../../03_Firmware/tests/wifi_control_state_host_fixture.c)를 사용한다.
GUIDE 환경 변수로는 **안내 후보 C**, 제거 후에는 **사용자 저장본 C**를 각각 실행한다.
의존성은 실제 저장된 owner C이며 UART/브라우저/보드의 실행을 대신하지 않는다.

```powershell
# TCC/GCC/Clang 경로는 현재 PC에 있는 도구로 지정한다.
$env:WIFI_CONTROL_HOST_CC = 'C:/path/to/tcc.exe'
# 사용자가 입력한 파일 검사: 후보 환경 변수를 제거한다.
Remove-Item Env:WIFI_CONTROL_STATE_GUIDE -ErrorAction SilentlyContinue
python -m unittest discover -s Projects/Tracked_Mobile_Robot/03_Firmware/tests -p test_wifi_control_state.py -v
```

안내의 C 두 블록을 실제 저장된 owner C와 TCC `-Wall -Werror`로 컴파일·실행해 **27 tests / PASS**를 확인했다.
사용자 state 파일이 없는 기본 실행은 **0 tests / SKIP1**이며 실제 저장본/ESP 빌드/보드 결과가 아니다.
[검사 원본 출력·후보 C snapshot·재연결 로그](../../assets/logs/wifi_link/2026-10-11_state_candidate/README.md)를 보존했다.

PASS는 정상 ARM→zero ACK/TEL→ACTIVE와 정지 확인, 시간 경계·owner/seq/type·미송신 만료·늦은 응답·FAULT/clock/zero-only의
**후보 또는 실제 state C 판단 결과**다. AC-H 전체의 UART TX0·브라우저·큐/mutex 경합 PASS가 아니다.
다음은 사용자 입력 → 실제 저장본 검토/PC 검사 → 사용자 ESP 전체 빌드 → 실행 adapter 설계/입력이다.
이번 파일 등록만으로 보드에서 ARM/CMD를 시험하지 않는다.

