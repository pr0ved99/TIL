# ARM/CMD 세 번째 입력 블록 — 제어 연결의 소유권 기록

작성일: **2026-10-11**. 상태: **사용자 저장본 실제 PC9 PASS / owner 포함 ESP 전체 빌드 성공 사용자 확인**.
선행 결과: parser 실제PC15 PASS·ticket 실제PC12 PASS, ticket 포함 ESP 전체 빌드 성공 사용자 확인.
기준: [초기 제어 계약](2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md).

사용자 `.h/.c`와 CMake 등록을 검토했다. 안내와 기능이 일치하고 실제 파일 PC 검사9개가 모두 PASS다.
공백·끝줄 차이는 기능에 영향이 없다. 아래 블록은 입력 참고용으로 유지하며 추가 수정은 필요 없다.

## 왜 별도 owner가 필요한가

현재 W5의 `s_wifi_command_owner_session_id`는 PING/DISARM 요청 한 개가 끝나면 해제된다.
ARM/CMD 제어에서는 첫 명령의 응답을 받은 뒤에도 같은 브라우저가 계속 제어해야 한다.
따라서 **현재 제어를 예약한 연결과 이번 ARM 시도 번호를 계속 기억하는 기록**을 별도로 둔다.

| 모듈/번호 | 맡는 일 |
| --- | --- |
| parser | 문자열을 ARM/CMD 요청 구조체로 읽음 |
| ticket | 특정 연결·용도·세대에 발급한 번호인지,150ms 안인지,미사용인지 검사 |
| owner — 이번 블록 | 한 제어 연결 예약·새 control ID 발급·소유권 대조·취소 |
| `ws_session_id` | 어떤 WebSocket 연결인지. ESP가 실제 연결에서 채움 |
| `control_id` | 그 연결이 몇 번째 제어 시도를 하는지. ARM을 다시 접수할 때 새 번호 |
| 상태 관리 — 다음 블록 | ARM ACK·zero ACK/TEL·시간 제한·정지 확인에 따라 다음 동작 결정 |

예를 들어 session2가 처음 ARM하면 control1을 예약한다. ticket 한 개가 소비돼도 owner는 유지한다.
제어 취소 후 같은 session2가 다시 ARM하면 control2다. 이전 control1의 CMD/응답은 새 소유권과 일치하지 않는다.
새 session3으로 재접속해도 번호 공급기는1부터 다시 시작하지 않는다.

```text
부팅 때 한 번 초기화 → 소유권 없음
  → 조건을 모두 통과한 수동 ARM 접수에서 연결·새 control ID 예약
  → ticket 소비/개별 응답 이후에도 소유권 기록 유지
  → 연결 유실/정지/만료 때 현재 연결·control ID 제거
  → 상태 관리에서 정지 확인 후 새 수동 ARM → 다음 control ID
```

**예약 성공과 `matches()==true`는 식별 번호가 맞다는 뜻이다. ARM 허가나 UART 송신 허가가 아니다.**
이번 모듈은 READY/TEL/FAULT·ticket·요청 번호·zero-only·시간·ACK를 검사하지 않는다.
전체 `IDLE→ARM_PENDING→ZERO_PENDING→ACTIVE→STOPPING/BLOCKED` 전이는 다음 블록이다.

## 정확한 입력 범위

ESP 프로젝트 `03_Firmware/esp32_wifi_link/main`에서 다음 범위만 입력한다.

1. `wifi_control_owner.h` 새 파일 전체: 아래 header 블록.
2. `wifi_control_owner.c` 새 파일 전체: 아래 source 블록.
3. `CMakeLists.txt`: source 네 개가 등록되도록 아래 전체 블록 사용.
   ESP-IDF 확장이 `.c`를 자동 등록했다면 source 네 개와 기존 의존성만 확인한다. 나열 순서는 달라도 된다.

기존 parser/ticket·main C·STM 소스는 이번 입력 대상이 아니다.

### main/wifi_control_owner.h — 새 파일 전체

```c
#ifndef WIFI_CONTROL_OWNER_H
#define WIFI_CONTROL_OWNER_H

#include "wifi_control_contract.h"

/* ESP 부팅당 하나. 취소 때 next_control_id를 초기화하지 않는다. */
typedef struct {
    uint32_t boot_id;
    uint64_t next_control_id;
    uint32_t ws_session_id;
    uint32_t control_id;
} wifi_control_owner_t;

typedef enum {
    WIFI_OWNER_OK,
    WIFI_OWNER_BAD_ARGUMENT,
    WIFI_OWNER_BUSY,
    WIFI_OWNER_EXHAUSTED
} wifi_control_owner_status_t;

void wifi_control_owner_init(
    wifi_control_owner_t *owner, uint32_t boot_id);

/* 호출자는 IDLE 및 나머지 ARM 접수 조건을 먼저 확인한다. */
wifi_control_owner_status_t wifi_control_owner_reserve(
    wifi_control_owner_t *owner, uint32_t ws_session_id,
    uint32_t *out_control_id);

/* 식별 번호만 대조한다. 제어 상태/시간/출력 허가 검사가 아니다. */
bool wifi_control_owner_matches(
    const wifi_control_owner_t *owner, uint32_t boot_id,
    uint32_t ws_session_id, uint32_t control_id);

void wifi_control_owner_revoke(wifi_control_owner_t *owner);

#endif
```

### main/wifi_control_owner.c — 새 파일 전체

```c
#include "wifi_control_owner.h"

void wifi_control_owner_init(
    wifi_control_owner_t *owner, uint32_t boot_id)
{
    if (owner != NULL) {
        *owner = (wifi_control_owner_t){
            .boot_id = boot_id,
            .next_control_id = 1U
        };
    }
}

wifi_control_owner_status_t wifi_control_owner_reserve(
    wifi_control_owner_t *owner, uint32_t ws_session_id,
    uint32_t *out_control_id)
{
    if (owner == NULL || ws_session_id == 0U || out_control_id == NULL) {
        return WIFI_OWNER_BAD_ARGUMENT;
    }

    if (owner->ws_session_id != 0U || owner->control_id != 0U) {
        return WIFI_OWNER_BUSY;
    }

    if (owner->next_control_id == 0U || owner->next_control_id > UINT32_MAX) {
        return WIFI_OWNER_EXHAUSTED;
    }

    owner->ws_session_id = ws_session_id;
    owner->control_id = (uint32_t)owner->next_control_id++;
    *out_control_id = owner->control_id;
    return WIFI_OWNER_OK;
}

bool wifi_control_owner_matches(
    const wifi_control_owner_t *owner, uint32_t boot_id,
    uint32_t ws_session_id, uint32_t control_id)
{
    return owner != NULL && ws_session_id != 0U && control_id != 0U &&
        owner->boot_id == boot_id &&
        owner->ws_session_id == ws_session_id &&
        owner->control_id == control_id;
}

void wifi_control_owner_revoke(wifi_control_owner_t *owner)
{
    if (owner != NULL) {
        owner->ws_session_id = 0U;
        owner->control_id = 0U;
    }
}
```

### main/CMakeLists.txt — 전체 등록 블록

```cmake
idf_component_register(
    SRCS "wifi_link_main.c" "wifi_control_contract.c"
         "wifi_control_ticket.c" "wifi_control_owner.c"
    INCLUDE_DIRS "."
    PRIV_REQUIRES
        esp_wifi esp_event esp_netif esp_http_server
        esp_timer esp_system esp_hw_support nvs_flash freertos
        esp_driver_uart
)
```

## 각 함수와 실패 경로

| 함수 | 정상 처리 | 실패/유지 조건 |
| --- | --- | --- |
| `init()` | 현재 boot·다음 번호1·소유권 없음 | ESP 부팅당 한 번만 호출. 같은 부팅의 재접속/취소 때 호출 금지 |
| `reserve()` | 한 연결 예약·새 control ID 발급, 성공 때만 out 기록 | 이미 예약돼 있으면 BUSY. 번호 소진은 EXHAUSTED. 실패 때 owner/out 유지 |
| `matches()` | boot·연결·control ID 세 값이 모두 같은지 확인 | 소유권 없음/0번호/다른 연결/이전 세대면 false. 읽기만 함 |
| `revoke()` | 현재 연결·control ID만0으로 만듦 | boot와 다음 번호 유지. 두 번 취소해도 번호는 되돌아가지 않음 |

`next_control_id`는 내부64bit다. 마지막u32 번호를 발급한 다음에는 `UINT32_MAX+1`로 남아
다음 예약을 거부한다. 같은 ESP 부팅에서 번호 소진을 `init()`으로 복구하지 않는다.
NULL 인자는 예약 BAD_ARGUMENT/대조 false, 초기화·취소는 아무 동작도 하지 않는다.

이 작은 기록을 UART pending에 넣으면 ACK 처리 때 함께 지워질 수 있어 전역 제어 상태가 따로 보관한다.
ACK 처리는 pending만 정리하며 owner에 `revoke()`를 호출하지 않아야 한다.
`revoke()`에는 UART 송신이 없다. 실제 정지는 다음 상태 관리에서 priority DISARM과 ACK/새 TEL로 확인한다.

## 다음 연결 블록이 반드시 지킬 순서

아래는 이번 모듈을 안전하게 호출할 조건이다. 이번 입력으로 이 연결 코드까지 구현한 것은 아니다.

1. ARM은 parser 성공·실제 연결 ID·boot/요청 번호·ticket·READY·fresh DISARMED/zero TEL·IDLE·큐 여유를 먼저 검사한다.
2. 같은 mutex 안에서 번호 공급기 여유를 확인하고 ticket 소비·owner 예약·ARM_PENDING 전이·큐 값 복사를 완료한다.
   실패 시 접수를 취소하고 소비한 ticket을 복원하지 않는다. 부분 예약/큐 실패는 정지 경로로 넘긴다.
3. CMD는 owner 식별 번호뿐 아니라 현재 phase·ticket·zero-only·간격/기한도 확인한다.
4. owner 연결의 종료/만료는 같은 mutex 안에서 STOPPING 설정·ticket 무효화·owner 취소·미송신 요청 폐기·stop flag 설정을 수행한다.
   다른 탭의 종료는 현재 owner 연결과 다르면 owner를 취소하지 않는다. 현재 boot의 유효한 수동 DISARM은 다른 탭도 가능하다.
5. owner가 없어졌어도 STOPPING/BLOCKED에서는 `reserve()`를 호출하지 않는다.
   matching DISARM ACK와 이후 fresh non-ARMED/zero TEL을 확인해야 IDLE로 복귀한다.
6. UART 송신 직전에도 세 값·phase·기한·연결 생존·stop flag를 다시 확인한다.
   늦은 ACK는 matching pending/seq·제어 세대·기한을 모두 통과해야 하며 owner 대조만으로 상태를 복원하지 않는다.

이 모듈 안에는 mutex나 시간 감시가 없다. 모든 읽기/예약/취소는 caller가 같은 lock으로 보호한다.
예약의 `out_control_id`에는 owner 내부 필드가 아닌 별도u32 변수의 주소를 전달한다.
각 필드를 개별 수정하거나 `next_control_id`를 되돌리는 경로를 만들지 않는다.
이전 ticket도 취소해야 하므로 owner 취소만으로 ticket 소비가 자동 차단되는 것은 아니다.

## PC 검사와 완료 경계

PC fixture는 실제 owner 함수를 호출하고 한 연결만 예약, 실패 시 상태/out 유지,
boot/session/control 대응, 취소 뒤 같은/다른 연결의 새 세대, 재사용 없음·번호 소진을 검사한다.
별도로 **현재 저장된 ticket 모듈**에서 CMD ticket을 발급·소비한 뒤 owner가 계속 유지되는지도 검사한다.
이 검사는 실제 ACK 수신/태스크 경합/미송신 큐·UART TX0를 증명하지 않는다.

후보 코드 PC 검사 → 사용자 세 파일 입력/저장 → 실제 저장본 PC 검사 → 사용자 ESP 전체 빌드 순서다.
이번에도 HTTP/UART에서 owner를 호출하지 않으며 새 플래시는 필요하지 않다.
AC-H02의 소유권 식별 기록 부분만 준비한다. 전체 AC-H02/H03·FSM·보드 안전은 미완료다.

10/11 준비 검사: 위 두 C 블록을 임시 폴더로 추출해 TCC `-Wall -Werror`로 컴파일·실행한
**후보9 PASS**다. `test_wifi_control_owner.py`와 fixture가 owner 후보와 실제 저장된 ticket C 함수를 호출했다.
입력 전 owner 파일이 없던 기본 실행은 **0 tests / SKIP1**이었다.
후속 사용자 저장본은 후보 선택 환경 변수를 제거하고 TCC `-Wall -Werror`로 검사한 **실제9 PASS**다.
모드는 `SAVED OWNER AND TICKET C ONLY`다. owner header SHA256은
`3797e5d06fe9a2a1ff954dd8f99c3c9c801aac7a566ae3b4f074de26a34209af`, source는
`707cd4d02ffe83faf8580cab3bf200b03f4e18ceec6251b4fd0124083a80e3bd`다.
10/11 owner 포함 ESP 전체 빌드 성공을 사용자가 확인했다. 원본 로그/바이너리 hash는 미제공이다.
다음은 제어 phase·기한·ACK/TEL·취소/정지 흐름의 입력 블록이다. 새 UART 연결·플래시·보드 결과로 확대하지 않는다.
검사한 후보 C 블록의 LF 끝줄 포함 SHA256은 header
`2b417380410a36ddb0cbdc3161c093686daaa9f175d024f822cfb51f4b8635d3`, source
`74cf280c391060b26bee6f105ebd3568749c6d1eef79d27203af9f482e930710`이다.
