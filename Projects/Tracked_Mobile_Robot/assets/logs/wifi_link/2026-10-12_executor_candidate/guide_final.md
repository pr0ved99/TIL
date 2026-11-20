# UART 실행 모듈 입력 안내 — 2026-10-12

상태: **안내 후보 C의 PC17 PASS / 사용자 executor 파일 미입력 / main 연결 미실행**.
선행: parser PC15·ticket PC12·owner PC9·state PC27 실제 저장본 PASS, state 포함 ESP 전체 빌드 성공 사용자 확인.
기준은 [제어 계약](2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md), 앞선 판단 모듈은 [state 안내](2026-10-11_WiFi_ARM_CMD_State_Code_Guide_ko.md)다.

## 이번 입력의 목적과 범위

**state는 진행/중단을 판단하고, executor는 그 판단을 대기 요청과 UART 송신 계획으로 연결한다.**
현재 main의 W5는 응답500ms와 요청별 소유권을 사용한다. 제어의 응답150ms·지속 소유권·priority DISARM과 다른 경로라서 executor를 별도로 둔다.
이 모듈은 기존 parser/ticket/owner/state를 함께 사용하고 SDK·네트워크 호출을 포함하지 않는다.
파일이 추가되지만 입력 소비·한 개 큐·송신 전 검사·취소 순서를 실제 C로 함께 검사할 수 있다.

이번에 입력할 대상은 **새 header 전체·새 C 전체·CMake 전체 등록 블록**이다. 기존 main 변경은 다음 연결 블록이다.
이 입력/빌드만으로 브라우저 ARM/CMD나 UART 제어가 활성화되지는 않는다.
현재 보드 조건은 사용자 보고의 STM/ESP 만능기판 장착·USB 공급·XL4015 분리다. 분리 지점·LiPo/모터 전원·PC7 sense는 미보고이며 소프트웨어 입력에 필요한 값으로 추정하지 않는다.

## 값이 지나가는 순서

```text
서버가 확인한 요청 + 해당 연결의 ticket
  → submit: ticket 검사·소비, ARM이면 owner 예약, 요청을 값으로 복사
  → 대기 슬롯 하나
  → take_tx: 마감/owner/phase 재검사, pending 등록, UART 문자열 생성
  → 다음 main 연결에서 uart_write_bytes 호출
  → tx_complete: 실제 쓰기 반환값 보고
  → matching ACK/ERR와 TEL을 executor에 전달
  → state 전환 + 결과 슬롯 하나
```

ticket의 사본을 검사해 접수가 성공할 때만 실제 ticket 소비를 확정한다. 접수 시각은 전달받은 ESP 단조 시각으로, 만료 시각은 ticket에서 가져온다.
ARM 접수 뒤 요청의 control_id에는 예약된 새 제어 번호를 저장한다. 이후 ACK로 owner를 해제하지 않는다.
request/payload/ticket 객체의 포인터를 보관하지 않으므로 호출 뒤 원래 요청 값을 바꿔도 큐의 요청은 바뀌지 않는다.
ticket 번호 공급기는 기존 pool이 ESP 부팅 동안 관리한다. 연결 종료 때 pool이나 executor를 초기화하지 않는다.

## 함수와 자료의 역할

| 함수/자료 | 역할 |
| --- | --- |
| init | ESP 부팅 때 한 번. 내부 state와 대기/결과 슬롯을 준비 |
| submit | 서버에서 검사한 ARM/CMD 요청을 ticket과 함께 접수. 한 슬롯을 확보할 때 소비 확정 |
| take_tx | 단일 UART 담당이 새 seq를 주면 송신 계획을 반환. 성공 뒤 즉시 실제 쓰기·tx_complete 필요 |
| tx_complete | uart_write_bytes의 정확한 반환값을 보고. 불완전 송신은 취소와 줄 동기화 요구 |
| reply/tel/poll | STM 응답·정상 TEL·주기 시각을 state로 전달하고 취소된 대기 작업을 정리 |
| stop/owner_closed | 수동 정지나 해당 owner의 연결 종료. 다른 연결 종료는 owner를 취소하지 않음 |
| needs_invalidation/inputs_cleared | 외부 ticket/미송신 입력 폐기를 요청하고 실제 폐기 뒤 확인받음 |
| take_result | 완료 결과 한 개를 값으로 꺼냄. 포인터 수명은 status의 정적 문자열만 사용 |
| allows_ping | IDLE/BLOCKED이며 executor 송신/응답 대기가 없을 때만 진단 허용. startup/W5 검사도 별도로 필요 |
| result.has_seq | 결과의 seq가 할당됐는지 표시. seq=0도 유효하며 이 값은 물리 TX 완료 증거가 아님 |

`state`와 나머지 공개 필드는 관찰용이다. main/HTTP에서 owner·phase·pending을 직접 덮어쓰지 않는다.
ARM/CMD 접수 거부 상태는 BAD_INPUT/BOOT_MISMATCH/TICKET_REJECTED/NOT_READY/BUSY/OUTPUT_PENDING으로 반환한다.
최신 owner의 잘못된 입력/ticket은 취소로 이어질 수 있으며, 다른 연결이나 이전 control ID의 요청은 최신 owner를 취소하지 않는다.
기존 결과를 아직 꺼내지 않았으면 새 요청을 OUTPUT_PENDING으로 거부한다. 거부가 source 기한을 연장하지 않으며 자동 재시도하지 않는다.

## 중단과 우선 DISARM

```text
만료/FAULT/끊김/수동 정지
  → state STOPPING, owner 취소
  → executor의 미송신 요청/응답 대기 취소, 해당 결과 확정
  → needs_invalidation=true
  → 다음 main에서 모든 관련 ticket·미송신 ingress 작업 폐기
  → 실제 폐기 뒤 inputs_cleared 호출
  → 다음 take_tx는 ARM/CMD 대신 DISARM
  → DISARM ACK + 이후 non-ARMED/zero TEL이면 IDLE
  → 송신/ACK/정지 확인 실패면 BLOCKED, 새 수동 DISARM 필요
```

외부 폐기 확인 전에는 DISARM 계획을 반환하지 않는다. inputs_cleared는 외부 작업이 끝났다는 호출자의 확인이므로 실제 RTOS 큐/WS ticket이 폐기됐는지를 이 함수 자체가 측정하지는 않는다.
외부 폐기를 완료하지 못하거나 송신/응답이 지연되면 state의 기존 시간 제한에 따라 BLOCKED로 간다. 정지 확인 실패를 물리 출력 정지로 기록하지 않는다.
준비된 프레임 한 개의 실제 쓰기가 끝나기 전에는 다음 프레임을 준비하지 않는다. 그 사이 취소되면 이전 응답은 허가를 복원하지 않으며, 이미 쓰기 중인 프레임을 회수할 수는 없다.
부분 송신 이후 DISARM 문자열 앞에 LF를 붙여 이전 불완전 줄의 경계 복원을 시도한다. PC 검사는 이 문자열을 확인한 범위이며 실제 STM 수신/복구는 후속 보드 검증이다.
정지 처리는 결과 표시나 네트워크 송신을 기다리지 않는다. 결과를 외부 메시지 큐/owner에게 전달하지 못하면 main은 stop(TX_FAILED)를 전달한다.

## 다음 main 연결에서 지켜야 할 조건

- **하나의 직렬화된 실행 문맥**에서 모든 executor 함수를 호출한다. 내부 mutex/태스크가 없다. HTTP와 UART 태스크가 보호 없이 동시에 호출하지 않는다.
- request_id 증가 검사·같은 연결 CMD 간격50ms·실제 WS 생존·현재 boot·서버 session 식별과 ticket 발급/전달은 외부 adapter가 맡는다. 이 검사가 끝난 요청만 submit에 전달한다.
- ARM 접수 때 startup READY·제어 fresh TEL·DISARMED/zero·UART idle을 확인한다. executor는 state 조건을 다시 검사하며 PC7 FAULT를 우회하지 않는다.
- seq는 현재 startup/W5와 공유하는 단일 UART 담당이 발급한다. 새 독립 seq 공급기를 만들지 않는다. 소진 시 재사용하지 않고 제어를 잠그며 정지 미확인을 처리한다.
- take_tx 직전에도 연결 생존/취소와 외부 큐를 확인한다. UART 쓰기/네트워크 송신 동안 공유 mutex를 잡지 않도록 기존 W5 경로도 함께 조정한다.
- take_tx 성공 뒤 실제 UART 쓰기·tx_complete를 바로 수행하고, 그 다음 응답을 처리한다. tx_complete를 빠뜨리면 새 송신 계획이 나오지 않는다.
- poll은 UART 담당의20ms 목표 점검에서 호출한다. 이 모듈에 자체 타이머는 없다. 응답150ms·큐50ms·source200ms·TEL250ms 등 수치는 state의 초기 설계값이며 물리 시간 보장이 아니다.
- owner의 ZERO_PENDING/ACTIVE 전이와 다음 CMD ticket을 대상 연결에 전달한다. CMD ticket은 ACK 뒤 발급하며 결과/상태/ticket 전달 실패는 취소해야 한다.
- DISARM은 일반 BUSY/rate 제한으로 정지를 막지 않게 기존 W5 입력 경로에서 priority stop으로 연결한다. UART pending과 제어 owner를 혼동하지 않는다.
- 제어 중 PING은 CONTROL_ACTIVE로 거부한다. PING/TEL/ACK로 CMD source 기한을 연장하지 않는다. 재접속 후 자동 ARM/CMD가 없도록 한다.

이 조건들은 다음 main/브라우저 입력 블록의 구현 항목이며 이번 module PC17 결과가 HTTP/RTOS 경합·필수 메시지 전달·실제 UART TX를 증명하지 않는다.

## 정확한 입력 범위

아래 두 파일은 새로 만들고 각 블록 전체를 입력한다. CMake도 마지막 등록 블록으로 전체 교체한다. main 함수 연결은 다음 단계이므로 이번에는 아래 세 입력 범위만 적용한다.

## main/wifi_control_executor.h — 신규 파일 전체 입력

```c
#ifndef WIFI_CONTROL_EXECUTOR_H
#define WIFI_CONTROL_EXECUTOR_H

#include "wifi_control_state.h"
#include "wifi_control_ticket.h"

#define WIFI_CONTROL_UART_FRAME_SIZE 96U

typedef enum {
    WIFI_EXEC_ACCEPTED,
    WIFI_EXEC_BAD_INPUT,
    WIFI_EXEC_BOOT_MISMATCH,
    WIFI_EXEC_TICKET_REJECTED,
    WIFI_EXEC_NOT_READY,
    WIFI_EXEC_BUSY,
    WIFI_EXEC_OUTPUT_PENDING
} wifi_control_submit_status_t;

typedef struct {
    wifi_control_op_t op;
    uint32_t seq;
    char bytes[WIFI_CONTROL_UART_FRAME_SIZE];
    size_t length;
} wifi_control_tx_t;

typedef struct {
    wifi_control_request_t request;
    uint32_t seq;
    bool has_seq; /* Assigned UART seq, including valid zero; not physical TX proof. */
    const char *status; /* Static string; no allocation or borrowed input pointer. */
} wifi_control_executor_result_t;

/* One serialized caller. HTTP/FreeRTOS/network synchronization is external. */
typedef struct {
    wifi_control_state_t state;
    wifi_control_phase_t observed_phase;
    wifi_control_request_t request;
    bool queued;
    bool waiting;
    bool prepared;
    bool inputs_cleared;
    bool need_line_sync;
    wifi_control_op_t prepared_op;
    uint32_t prepared_seq;
    size_t prepared_length;
    uint32_t request_seq;
    bool have_result;
    wifi_control_executor_result_t result;
} wifi_control_executor_t;

void wifi_control_executor_init(wifi_control_executor_t *executor, uint32_t boot_id);

/* request-id ordering, rate limit and real session liveness precede this call. */
wifi_control_submit_status_t wifi_control_executor_submit(
    wifi_control_executor_t *executor, const wifi_control_request_t *request,
    wifi_control_ticket_t *ticket, bool startup_ready, bool uart_idle,
    uint64_t now_ms);

/* Outer actor purges all tickets and unsent ingress work before acknowledging. */
bool wifi_control_executor_needs_invalidation(const wifi_control_executor_t *executor);
void wifi_control_executor_inputs_cleared(wifi_control_executor_t *executor);

/* seq is allocated by the SAME UART owner used for startup/W5. Never reuse it. */
bool wifi_control_executor_take_tx(
    wifi_control_executor_t *executor, uint32_t seq, uint64_t now_ms,
    wifi_control_tx_t *out);
/* Write immediately, then report exact uart_write_bytes return before RX/next TX. */
bool wifi_control_executor_tx_complete(
    wifi_control_executor_t *executor, int written, uint64_t now_ms);

bool wifi_control_executor_reply(
    wifi_control_executor_t *executor, wifi_control_op_t op,
    uint32_t seq, bool ok, uint32_t stm_t_ms, uint64_t now_ms);
void wifi_control_executor_tel(
    wifi_control_executor_t *executor, const wifi_control_tel_t *tel,
    uint64_t now_ms);
void wifi_control_executor_poll(
    wifi_control_executor_t *executor, bool startup_ready, uint64_t now_ms);
void wifi_control_executor_stop(
    wifi_control_executor_t *executor, wifi_control_reason_t reason,
    uint64_t now_ms);
void wifi_control_executor_owner_closed(
    wifi_control_executor_t *executor, uint32_t ws_session_id, uint64_t now_ms);
bool wifi_control_executor_take_result(
    wifi_control_executor_t *executor, wifi_control_executor_result_t *out);
bool wifi_control_executor_allows_ping(const wifi_control_executor_t *executor);

#endif
```

## main/wifi_control_executor.c — 신규 파일 전체 입력

```c
#include "wifi_control_executor.h"

#include <inttypes.h>
#include <stdio.h>

static bool live(const wifi_control_executor_t *e)
{
    return e != NULL && e->state.initialized;
}

static const char *cancel_status(const wifi_control_state_t *s, bool queued)
{
    switch (s->reason) {
    case WIFI_CONTROL_REASON_OWNER_CLOSED: return "CONNECTION_CLOSED";
    case WIFI_CONTROL_REASON_INPUT_EXPIRED: return queued ? "QUEUE_EXPIRED" : "TIMEOUT";
    case WIFI_CONTROL_REASON_ACK_TIMEOUT:
    case WIFI_CONTROL_REASON_FIRST_CMD_TIMEOUT:
    case WIFI_CONTROL_REASON_SOURCE_TIMEOUT: return "TIMEOUT";
    case WIFI_CONTROL_REASON_STM_ERR: return "STM_ERROR";
    case WIFI_CONTROL_REASON_TX_FAILED: return "TX_ERROR";
    default: return "CANCELLED";
    }
}

static void result(wifi_control_executor_t *e, const char *status)
{
    e->result = (wifi_control_executor_result_t) {
        .request = e->request, .seq = e->request_seq,
        .has_seq = e->waiting, .status = status
    };
    e->have_result = true;
    e->queued = false;
    e->waiting = false;
}

static void reconcile(wifi_control_executor_t *e)
{
    const wifi_control_phase_t phase = e->state.phase;
    if (phase == WIFI_CONTROL_STOPPING || phase == WIFI_CONTROL_BLOCKED) {
        if (phase != e->observed_phase) {
            e->inputs_cleared = false;
        }
        if (e->queued || e->waiting) {
            result(e, cancel_status(&e->state, e->queued));
        }
    }
    e->observed_phase = phase;
}

static wifi_control_submit_status_t reject(
    wifi_control_executor_t *e, const wifi_control_request_t *r,
    wifi_control_submit_status_t status, wifi_control_reason_t reason,
    uint64_t now)
{
    /* An old generation/other connection cannot cancel a newer owner. */
    if (r->expected_boot_id == e->state.owner.boot_id &&
        r->ws_session_id != 0U && r->ws_session_id == e->state.owner.ws_session_id &&
        (r->control_id == e->state.owner.control_id ||
         (r->type == WIFI_CONTROL_ARM && r->control_id == 0U))) {
        wifi_control_state_stop(&e->state, reason, now);
        reconcile(e);
    }
    return status;
}

void wifi_control_executor_init(wifi_control_executor_t *e, uint32_t boot_id)
{
    if (e != NULL) {
        *e = (wifi_control_executor_t) {0};
        wifi_control_state_init(&e->state, boot_id);
        e->observed_phase = WIFI_CONTROL_IDLE;
    }
}

void wifi_control_executor_poll(
    wifi_control_executor_t *e, bool startup_ready, uint64_t now)
{
    if (live(e)) {
        wifi_control_state_poll(&e->state, startup_ready, now);
        reconcile(e);
    }
}

wifi_control_submit_status_t wifi_control_executor_submit(
    wifi_control_executor_t *e, const wifi_control_request_t *r,
    wifi_control_ticket_t *ticket, bool startup_ready, bool uart_idle,
    uint64_t now)
{
    if (!live(e) || r == NULL || ticket == NULL) {
        return WIFI_EXEC_BAD_INPUT;
    }
    wifi_control_executor_poll(e, startup_ready, now);
    if (r->expected_boot_id != e->state.owner.boot_id) {
        return WIFI_EXEC_BOOT_MISMATCH;
    }
    if (r->request_id == 0U || r->ws_session_id == 0U ||
        (r->type != WIFI_CONTROL_ARM && r->type != WIFI_CONTROL_CMD) ||
        !wifi_control_zero_only_allows(r)) {
        return reject(e, r, WIFI_EXEC_BAD_INPUT, WIFI_CONTROL_REASON_BAD_INPUT, now);
    }
    if (e->queued || e->waiting || e->prepared) {
        return WIFI_EXEC_BUSY;
    }
    if (e->have_result) {
        return WIFI_EXEC_OUTPUT_PENDING;
    }
    wifi_control_ticket_t checked = *ticket;
    wifi_control_request_t accepted = *r;
    accepted.accepted_ms = now;
    accepted.expires_ms = checked.expires_ms;
    const wifi_control_ticket_status_t ticket_status =
        wifi_control_ticket_consume(&checked, &accepted, now);
    if (ticket_status != WIFI_TICKET_OK) {
        if (ticket_status == WIFI_TICKET_EXPIRED) {
            *ticket = checked;
        }
        return reject(e, r, WIFI_EXEC_TICKET_REJECTED,
            ticket_status == WIFI_TICKET_EXPIRED ? WIFI_CONTROL_REASON_INPUT_EXPIRED :
                WIFI_CONTROL_REASON_BAD_INPUT, now);
    }
    if (accepted.type == WIFI_CONTROL_ARM) {
        uint32_t id;
        if (!wifi_control_state_begin_arm(
                &e->state, &accepted, startup_ready, uart_idle, now, &id)) {
            return reject(e, r, WIFI_EXEC_NOT_READY, WIFI_CONTROL_REASON_BAD_INPUT, now);
        }
        accepted.control_id = id;
    } else if (!uart_idle ||
        (e->state.phase != WIFI_CONTROL_ZERO_PENDING && e->state.phase != WIFI_CONTROL_ACTIVE) ||
        !wifi_control_owner_matches(&e->state.owner, accepted.expected_boot_id,
                                   accepted.ws_session_id, accepted.control_id)) {
        return reject(e, r, WIFI_EXEC_NOT_READY, WIFI_CONTROL_REASON_BAD_INPUT, now);
    }
    /* Queue reservation and ticket consumption are one serialized operation. */
    *ticket = checked;
    e->request = accepted;
    e->request_seq = 0U;
    e->queued = true;
    reconcile(e);
    return WIFI_EXEC_ACCEPTED;
}

bool wifi_control_executor_needs_invalidation(const wifi_control_executor_t *e)
{
    return live(e) &&
        (e->state.phase == WIFI_CONTROL_STOPPING || e->state.phase == WIFI_CONTROL_BLOCKED) &&
        !e->inputs_cleared;
}

void wifi_control_executor_inputs_cleared(wifi_control_executor_t *e)
{
    if (wifi_control_executor_needs_invalidation(e)) {
        e->inputs_cleared = true;
    }
}

bool wifi_control_executor_take_tx(
    wifi_control_executor_t *e, uint32_t seq, uint64_t now, wifi_control_tx_t *out)
{
    if (!live(e) || out == NULL) {
        return false;
    }
    wifi_control_executor_poll(e, e->state.startup_ready, now);
    if (e->prepared) {
        return false;
    }
    wifi_control_op_t op;
    if (e->state.phase == WIFI_CONTROL_STOPPING && e->state.need_disarm) {
        if (!e->inputs_cleared) {
            return false;
        }
        op = WIFI_CONTROL_OP_DISARM;
    } else if (e->queued) {
        op = e->request.type == WIFI_CONTROL_ARM ? WIFI_CONTROL_OP_ARM : WIFI_CONTROL_OP_CMD;
    } else {
        return false;
    }
    wifi_control_tx_t tx = {.op = op, .seq = seq};
    int n;
    if (op == WIFI_CONTROL_OP_CMD) {
        n = snprintf(tx.bytes, sizeof(tx.bytes),
            "CMD,seq=%" PRIu32 ",vx_mmps=0,w_mradps=0,timeout_ms=300\n", seq);
    } else {
        n = snprintf(tx.bytes, sizeof(tx.bytes), "%s%s,seq=%" PRIu32 "\n",
            op == WIFI_CONTROL_OP_DISARM && e->need_line_sync ? "\n" : "",
            op == WIFI_CONTROL_OP_ARM ? "ARM" : "DISARM", seq);
    }
    if (n <= 0 || (size_t)n >= sizeof(tx.bytes)) {
        wifi_control_state_stop(&e->state, WIFI_CONTROL_REASON_TX_FAILED, now);
        reconcile(e);
        return false;
    }
    const bool allowed = op == WIFI_CONTROL_OP_ARM ?
        wifi_control_state_arm_sent(&e->state, e->request.ws_session_id,
                                    e->request.control_id, seq, now) :
        op == WIFI_CONTROL_OP_CMD ? wifi_control_state_cmd_sent(&e->state, &e->request, seq, now) :
        wifi_control_state_disarm_sent(&e->state, seq, now);
    reconcile(e);
    if (!allowed) {
        return false;
    }
    tx.length = (size_t)n;
    e->prepared = true;
    e->prepared_op = op;
    e->prepared_seq = seq;
    e->prepared_length = tx.length;
    if (op != WIFI_CONTROL_OP_DISARM) {
        e->queued = false;
        e->waiting = true;
        e->request_seq = seq;
    }
    *out = tx;
    return true;
}

bool wifi_control_executor_tx_complete(wifi_control_executor_t *e, int written, uint64_t now)
{
    if (!live(e) || !e->prepared) {
        return false;
    }
    const bool full = written >= 0 && (size_t)written == e->prepared_length;
    e->prepared = false;
    if (!full) {
        e->need_line_sync = true;
        /* An intervening cancel already revoked an old ARM/CMD pending. */
        if (e->state.pending == e->prepared_op && e->state.pending_seq == e->prepared_seq) {
            wifi_control_state_tx_failed(&e->state, now);
        }
    } else if (e->prepared_op == WIFI_CONTROL_OP_DISARM) {
        e->need_line_sync = false;
    }
    wifi_control_state_poll(&e->state, e->state.startup_ready, now);
    reconcile(e);
    return full;
}

bool wifi_control_executor_reply(
    wifi_control_executor_t *e, wifi_control_op_t op,
    uint32_t seq, bool ok, uint32_t stm_t_ms, uint64_t now)
{
    if (!live(e) || e->prepared) {
        return false;
    }
    const bool matched = wifi_control_state_reply(&e->state, op, seq, ok, stm_t_ms, now);
    if (matched && op != WIFI_CONTROL_OP_DISARM && e->waiting) {
        result(e, ok ? "OK" : "STM_ERROR");
    }
    reconcile(e);
    return matched;
}

void wifi_control_executor_tel(
    wifi_control_executor_t *e, const wifi_control_tel_t *tel, uint64_t now)
{
    if (live(e)) {
        wifi_control_state_tel(&e->state, tel, now);
        reconcile(e);
    }
}

void wifi_control_executor_stop(
    wifi_control_executor_t *e, wifi_control_reason_t reason, uint64_t now)
{
    if (live(e)) {
        wifi_control_state_stop(&e->state, reason, now);
        reconcile(e);
    }
}

void wifi_control_executor_owner_closed(
    wifi_control_executor_t *e, uint32_t session, uint64_t now)
{
    if (live(e)) {
        wifi_control_state_owner_closed(&e->state, session, now);
        reconcile(e);
    }
}

bool wifi_control_executor_take_result(
    wifi_control_executor_t *e, wifi_control_executor_result_t *out)
{
    if (!live(e) || out == NULL || !e->have_result) {
        return false;
    }
    *out = e->result;
    e->have_result = false;
    return true;
}

bool wifi_control_executor_allows_ping(const wifi_control_executor_t *e)
{
    return live(e) && !e->queued && !e->waiting && !e->prepared &&
        e->state.pending == WIFI_CONTROL_OP_NONE &&
        (e->state.phase == WIFI_CONTROL_IDLE || e->state.phase == WIFI_CONTROL_BLOCKED);
}
```

## main/CMakeLists.txt — 전체 교체

```cmake
idf_component_register(
    SRCS "wifi_link_main.c" "wifi_control_contract.c"
         "wifi_control_ticket.c" "wifi_control_owner.c"
         "wifi_control_state.c" "wifi_control_executor.c"
    INCLUDE_DIRS "."
    PRIV_REQUIRES
        esp_wifi esp_event esp_netif esp_http_server
        esp_timer esp_system esp_hw_support nvs_flash freertos
        esp_driver_uart
)
```

## 검사 결과와 PASS 기준

안내 후보 C 두 블록과 실제 저장된 parser/ticket/owner/state C를 TCC `-Wall -Werror`로 컴파일·실행해 **17 tests/PASS**다.
executor 실제 파일이 없는 기본 검사 모드는 **0 tests/SKIP1**이며 사용자 저장본 PASS가 아니다.
[검사 원본과 검사 대상 snapshot](../../assets/logs/wifi_link/2026-10-12_executor_candidate/README.md)을 보존했다.

검사한 범위는 정상 ARM→zero ACK/TEL→ACTIVE→정지 확인, ARM/TEL/startup/진단 busy gate, ticket·큐·응답의 시간 경계,
폐기 확인 전 DISARM 계획 없음, 요청 값 복사, 결과 역압, owner 식별, 준비/쓰기 중 취소, 부분 송신 LF,
source 감시·BLOCKED 수동 복구·ticket 재사용·startup 유실·늦은 쓰기 완료·유효 UART seq0이다.
프레임 출력은 UART 계획 값이며 보드에서 해당 byte가 송신됐다는 증거가 아니다. AC-H 전체·AC-B/S는 미완료다.

```powershell
# 사용자가 저장한 파일로 검사할 때 후보 선택을 제거한다.
Remove-Item Env:WIFI_CONTROL_EXECUTOR_GUIDE -ErrorAction SilentlyContinue
$env:WIFI_CONTROL_HOST_CC = 'C:/path/to/tcc.exe'
python -m unittest discover -s Projects/Tracked_Mobile_Robot/03_Firmware/tests -p test_wifi_control_executor.py -v
```

Codex가 새 입력을 다시 읽고 실제 파일 검사17 PASS를 확인하면 사용자가 ESP 전체 빌드를 수행한다.
그 뒤 다음 main 연결 블록에서 태스크/큐/close flag·공통 seq·ACK/ERR/TEL·주기 감시·결과와 ticket/브라우저를 연결한다.
이번 모듈 입력만으로 플래시나 ARM/CMD 보드 시험을 진행하지 않는다.
