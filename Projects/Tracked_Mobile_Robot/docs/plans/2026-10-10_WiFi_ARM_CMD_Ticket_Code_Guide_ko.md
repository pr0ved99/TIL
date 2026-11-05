# ARM/CMD 두 번째 입력 블록 — 일회용 ticket

작성일: **2026-10-10**. 갱신일: **2026-10-11**. 상태: **사용자 수정본 실제 PC12 PASS / ticket 포함 ESP 전체 빌드 성공 사용자 확인**.
선행 결과: [parser 안내](2026-10-10_WiFi_ARM_CMD_Parser_Code_Guide_ko.md)의 실제 저장본 PC15 PASS,
ESP 전체 빌드 성공은 사용자 확인이다. 새 플래시·보드 실행은 확인하지 않았다.
기준: [제어 설계안](2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md).

## 만드는 이유와 이번 범위

parser는 `ticket=9`를 숫자9로 바꿀 뿐, ESP가 발급한 번호인지 확인하지 않는다.
이번 모듈은 **ESP가 어떤 연결에 어떤 용도로 언제 발급했는지**를 보관하고 실제 요청과 대조한다.
ticket은 암호나 로그인 인증이 아니다. 오래 대기한 입력과 재사용 입력을 거부하는 번호다.

```text
ESP pool에서 새 번호 발급
  → 해당 연결의 ticket에 boot·session·용도·control ID·만료시각 저장
  → 이미 parser를 통과한 요청과 대조
  → 만료 전 한 번 소비
  → 같은 ticket을 다시 보내면 거부
```

- ARM ticket의 `control_id`는0이다. 아직 ARM을 접수해 제어 세대를 예약하기 전이기 때문이다.
- CMD ticket은 owner/state 코드에서 정한 양수 `control_id`에 묶인다.
- `ws_session_id`는 ESP가 확인한 연결 ID다. 브라우저 payload에서 받지 않는다.
- 발급 pool은 ESP 부팅당 한 번 초기화한다. 연결 종료·DISARM 때 pool을 초기화하지 않는다.
- 유효한 ticket을 중간에 새 번호로 바꾸지 않는다. 만료/소비 후 다음 번호를 발급한다.
- `now_ms >= expires_ms`이면 만료다.150ms는 ESP 발급 시점 기준이며 브라우저 수신 때 다시 시작하지 않는다.

이번에는 HTTP·UART에서 호출하지 않는 독립 모듈을 등록한다. owner 선택, control ID 발급,
READY/TEL/FAULT 조건, 속도/zero-only, 요청 번호·최소 간격, 큐 용량과 정지 상태는 다음 연결 블록이다.
ticket 성공을 ARM 수락이나 STM ACK로 표시하면 안 된다.

## 최초 저장본 검토와 수정 확인 — 2026-10-10

사용자가 저장한 `.h/.c`와 CMake를 읽었다. header 선언과 CMake의 세 source 등록은 맞다.
최초 source에는 아래 컴파일 오류 두 곳이 있었으며 후속 사용자 저장본에서 모두 수정됐다.

| 최초 source 줄 | 최초 저장된 값 | 수정 확인한 값 | 쓰는 이유 |
| --- | --- | --- | --- |
| 46 | `UINT32_NAX` | `UINT32_MAX` | u32 ticket 번호의 최댓값을 넘어가면 발급을 잠금 |
| 74 | `ticket->puepose` | `ticket->purpose` | ARM/CMD 용도가 발급 기록과 같은지 확인 |

최초 저장본 PC 검사는46줄의 미정의 이름에서 멈춰 **0 tests / ERROR1**이었다.
수정본을 다시 읽고 실제 파일을 컴파일·실행해 **12 tests / PASS**를 확인했다.
header8줄의 `떄`는 주석 오타로 기능에 영향이 없다.

## 입력 범위와 후속 수정 이력

ESP 프로젝트 `03_Firmware/esp32_wifi_link/main/wifi_control_ticket.c`의
**최초1~87줄 전체 교체 블록**으로 아래 source를 제공했다. 사용자 수정본은 두 오류가 해결됐으며
공백을 제외하면 아래 source와 일치한다. 추가 재입력은 필요 없다.
header/CMake 블록은 비교용으로 유지한다. CMake의 source 나열 순서는 달라도 된다.

이번 수정은 ticket source의 두 오타이며 기존 parser와 main C는 앞선 hash를 유지한다.

### main/wifi_control_ticket.h — 확인된 선언, 비교용

```c
#ifndef WIFI_CONTROL_TICKET_H
#define WIFI_CONTROL_TICKET_H

#include "wifi_control_contract.h"

#define WIFI_CONTROL_TICKET_VALID_MS 150U

/* ESP 부팅 전체에서 공유한다. 연결 종료 때 초기화하지 않는다. */
typedef struct {
    uint32_t boot_id;
    uint64_t next_id;
} wifi_control_ticket_pool_t;

/* 연결마다 하나 보관한다. 초기값은 {0}이다. */
typedef struct {
    uint32_t boot_id;
    uint32_t ws_session_id;
    uint32_t control_id;
    wifi_control_type_t purpose;
    uint32_t id;
    uint64_t issued_ms;
    uint64_t expires_ms;
    bool valid;
} wifi_control_ticket_t;

typedef enum {
    WIFI_TICKET_OK,
    WIFI_TICKET_BAD_ARGUMENT,
    WIFI_TICKET_BUSY,
    WIFI_TICKET_EXHAUSTED,
    WIFI_TICKET_MISMATCH,
    WIFI_TICKET_EXPIRED
} wifi_control_ticket_status_t;

void wifi_control_ticket_pool_init(
    wifi_control_ticket_pool_t *pool, uint32_t boot_id);

wifi_control_ticket_status_t wifi_control_ticket_issue(
    wifi_control_ticket_pool_t *pool,
    wifi_control_ticket_t *ticket,
    uint32_t ws_session_id, wifi_control_type_t purpose,
    uint32_t control_id, uint64_t now_ms);

/* 호출자는 parser 성공과 나머지 접수 조건을 먼저 검사한다. */
wifi_control_ticket_status_t wifi_control_ticket_consume(
    wifi_control_ticket_t *ticket,
    const wifi_control_request_t *request, uint64_t now_ms);

void wifi_control_ticket_invalidate(wifi_control_ticket_t *ticket);

#endif
```

### main/wifi_control_ticket.c — 전체 입력 블록, 수정 확인 완료

```c
#include "wifi_control_ticket.h"

void wifi_control_ticket_pool_init(
    wifi_control_ticket_pool_t *pool, uint32_t boot_id)
{
    if (pool != NULL) {
        *pool = (wifi_control_ticket_pool_t){
            .boot_id = boot_id,
            .next_id = 1U
        };
    }
}

void wifi_control_ticket_invalidate(wifi_control_ticket_t *ticket)
{
    if (ticket != NULL) {
        ticket->valid = false;
    }
}

wifi_control_ticket_status_t wifi_control_ticket_issue(
    wifi_control_ticket_pool_t *pool,
    wifi_control_ticket_t *ticket,
    uint32_t ws_session_id, wifi_control_type_t purpose,
    uint32_t control_id, uint64_t now_ms)
{
    if (pool == NULL || ticket == NULL || ws_session_id == 0U ||
        (purpose != WIFI_CONTROL_ARM && purpose != WIFI_CONTROL_CMD) ||
        (purpose == WIFI_CONTROL_ARM && control_id != 0U) ||
        (purpose == WIFI_CONTROL_CMD && control_id == 0U) ||
        now_ms > UINT64_MAX - WIFI_CONTROL_TICKET_VALID_MS) {
        return WIFI_TICKET_BAD_ARGUMENT;
    }

    if (ticket->valid) {
        if (now_ms < ticket->issued_ms) {
            ticket->valid = false;
            return WIFI_TICKET_EXPIRED;
        }
        if (now_ms < ticket->expires_ms) {
            return WIFI_TICKET_BUSY;
        }
        ticket->valid = false;
    }

    if (pool->next_id == 0U || pool->next_id > UINT32_MAX) {
        return WIFI_TICKET_EXHAUSTED;
    }

    *ticket = (wifi_control_ticket_t){
        .boot_id = pool->boot_id,
        .ws_session_id = ws_session_id,
        .control_id = control_id,
        .purpose = purpose,
        .id = (uint32_t)pool->next_id++,
        .issued_ms = now_ms,
        .expires_ms = now_ms + WIFI_CONTROL_TICKET_VALID_MS,
        .valid = true
    };
    return WIFI_TICKET_OK;
}

wifi_control_ticket_status_t wifi_control_ticket_consume(
    wifi_control_ticket_t *ticket,
    const wifi_control_request_t *request, uint64_t now_ms)
{
    if (ticket == NULL || request == NULL) {
        return WIFI_TICKET_BAD_ARGUMENT;
    }

    if (!ticket->valid || ticket->id == 0U ||
        request->expected_boot_id != ticket->boot_id ||
        request->ws_session_id != ticket->ws_session_id ||
        request->type != ticket->purpose ||
        request->control_id != ticket->control_id ||
        request->ticket != ticket->id) {
        return WIFI_TICKET_MISMATCH;
    }

    if (now_ms < ticket->issued_ms || now_ms >= ticket->expires_ms) {
        ticket->valid = false;
        return WIFI_TICKET_EXPIRED;
    }

    ticket->valid = false;
    return WIFI_TICKET_OK;
}
```

### main/CMakeLists.txt — 등록 완료, 비교용

```cmake
idf_component_register(
    SRCS "wifi_link_main.c" "wifi_control_contract.c" "wifi_control_ticket.c"
    INCLUDE_DIRS "."
    PRIV_REQUIRES
        esp_wifi esp_event esp_netif esp_http_server
        esp_timer esp_system esp_hw_support nvs_flash freertos
        esp_driver_uart
)
```

## 함수가 맡는 일과 연결할 때의 순서

| 함수 | 역할 | 성공/실패 때 남는 값 |
| --- | --- | --- |
| `pool_init()` | 부팅의 번호 공급기를1부터 시작 | 연결마다 호출하지 않음. 같은 부팅의 번호 재사용 방지 |
| `issue()` | 대상 연결·용도의 ticket 발급 | 유효한 ticket이 남으면 BUSY, 새 번호를 쓰지 않음 |
| `consume()` | 요청과 발급 기록 비교 후 한 번 소비 | 성공하면 valid=false. 다른 연결/용도/번호는 MISMATCH |
| `invalidate()` | 종료/정지 때 ticket 취소 | valid=false. 번호 공급기는 유지 |

`pool`은 부팅 전체의 번호 공급기이고 `ticket`은 한 연결에 준 발급 기록이다.
예를 들어 session2에 ticket9를 줬으면 session3이9를 보내도 거부한다.
session2가9를 정상 사용하면 이후에는 같은 session2에서도9를 다시 쓸 수 없다.
두 연결에 ARM ticket이 있어도 제어 owner를 두 개 허용한다는 뜻은 아니다.
owner/state 코드는 한 ARM만 예약하고 나머지를 거부해야 한다.

이 모듈은 시계를 직접 읽지 않는다. caller가 `esp_timer_get_time()` 기준의 ms를 전달하고,
PC 검사에서는149/150ms 같은 경계를 직접 전달한다. 시각이 발급 시각보다 작으면 거부한다.
번호는 내부64bit로 올리므로 마지막u32 번호를 사용한 뒤에도0으로 돌아가지 않는다.
소진은 제어 잠금으로 처리하고 같은 부팅에서 `pool_init()`으로 복구하지 않는다.

접수 연결 시 caller의 순서는 아래와 같아야 한다.

1. parser 성공 확인, ESP가 실제 연결의 `ws_session_id`를 request에 채움.
2. 현재 boot, owner/control ID, 상태/FAULT, zero-only, 요청 번호·간격과 큐 여유 검사.
3. **같은 mutex 안에서** ticket 소비와 제어 예약·큐 값 복사를 완료.
4. 큐 실패·메시지 실패는 제어 취소로 처리. 소비한 ticket을 복원하지 않음.
5. UART 송신 직전 연결 생존·세대·stop flag와 저장한 ticket/큐 deadline을 다시 검사.

`consume()`은 request의 시간 metadata를 바꾸지 않는다. caller는 **소비 전 기록에서** ticket 만료시각을 읽고
접수 시각을 기록해야 한다. CMD의 송신 마감은 ticket 만료와 접수+50ms 중 빠른 값이다.
ticket이 이미 소비됐으므로 UART 담당이 `consume()`을 다시 호출하지 않는다.
이 모듈 안에는 mutex가 없다. 번호 공급기와 연결 ticket의 읽기·쓰기는 caller가 같은 lock으로 보호한다.
유효한 CMD ticket은 matching ARM ACK/zero 상태에서만, 다음 CMD ticket은 직전 matching CMD ACK 뒤에만 발급한다.
ACK 전 발급, 자동 ARM, ticket만 보고 UART 송신하는 호출 경로는 만들지 않는다.

## 검사와 완료 경계

- 번호/boot/session/purpose/control ID 대응,149/150ms 경계, 한 번 소비와 취소, 번호 소진을 native C로 검사한다.
- 후보 Markdown 블록 검사와 사용자가 저장한 실제 파일 검사를 구분한다.
- AC-H02/H03의 ticket 자체 검사다. UART TX0·큐 경합·owner/state·실측 시간/정지는 아직 증명하지 않는다.
- 사용자 입력/저장 → 실제 파일 검토·PC 검사 → 사용자 ESP 전체 빌드 순서다. 이번에도 플래시는 필요하지 않다.

10/10 준비 검사: 위 두 C 블록을 임시 폴더로 추출해 TCC `-Wall -Werror`로 컴파일·실행한
**후보12 PASS**다. `test_wifi_control_ticket.py`와 fixture가 실제 module 함수를 호출한다.
입력 전 파일이 없던 기본 실행은 **0 tests / SKIP1**이었다.
최초 사용자 저장본은 위 오타 때문에 **0 tests / ERROR1**이었다.
후속 수정본은 후보 선택 환경 변수를 제거하고 TCC `-Wall -Werror`로 검사한 **실제 PC12 PASS**다.
ticket header SHA256은 `ad2dc0c8e622204365cd6817ae92f41f898b0a184b246b37a48376afb781afea`,
source는 `415b4d1d7a234b6280ae37c4320c69fe8562baaa4f74d0eca8f2c96497a4ce94`다.
10/11 ticket 포함 ESP 전체 빌드 성공을 사용자가 확인했다. 원본 로그/바이너리 hash는 미제공이다.
다음은 제어 소유권/control ID·상태/기한 관리다. 새 플래시·UART 연결·보드 결과는 미확인이다.
후보/저장본 PC 결과를 ESP 전체 빌드·UART 송신·보드 결과로 합치지 않는다.
검사 의존 header는 현재 저장된 `wifi_control_contract.h`이며 SHA256은
`9fd0156335c1b8bfcdfc76e09f90c3868182bf99b46bc8512dd986092b8d3ac8`이다.
