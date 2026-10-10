# ARM/CMD 첫 입력 블록 — 요청 구조체와 parser

작성일: **2026-10-10**. 단계: **parser 저장본 PC15 PASS / ESP 전체 빌드 성공 사용자 확인**.
기준: [제어 설계안](2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md).

이번에는 **문자열을 읽어 요청 구조체에 담는 부분**을 만든다.
제어 owner·ticket 발급/소비·시간 검사·UART 송신·브라우저 버튼은 다음 연결 블록이다.
기존 `wifi_link_main.c`의 W5 parser와 enum을 확장하지 않는다.

## 저장본 검토와 이번 교체 범위

사용자가 수정한 세 파일을 다시 읽었다. CMake 등록과 header 선언은 맞으며,
앞서 찾은 source 오류5곳도 모두 수정됐다. 실제 저장본 PC 검사15개가 모두 통과했다.
**현재 기능상 추가 수정은 필요하지 않다. ESP 전체 빌드 성공을 사용자가 확인했다.**
다음은 [ticket 입력 블록](2026-10-10_WiFi_ARM_CMD_Ticket_Code_Guide_ko.md)이다.
아래 표와 교체 범위는 최초 검토 당시의 오류·수정 안내 이력이다.
줄 번호는 당시 `main/wifi_control_contract.c` 기준이다.

| 줄 | 최초 입력 | 수정된 내용 | 최초 오류의 영향 |
| --- | --- | --- | --- |
| 29 | `*pos > '9'` | `*pos <= '9'` | 숫자0~9에서 반복문에 진입하지 않아 정상 요청도 거부됨 |
| 49 | `const boll negative` | `const bool negative` | 존재하지 않는 자료형으로 컴파일 오류 |
| 64 | `meganitude` | `magnitude` | 선언되지 않은 변수명으로 컴파일 오류 |
| 70 | `megnitude` | `magnitude` | 선언되지 않은 변수명으로 컴파일 오류 |
| 85 | `wifi_control_request_t *out);` | `wifi_control_request_t *out)` | 함수 정의 앞의 세미콜론 때문에 뒤의 본문이 함수에 연결되지 않음 |

**당시 교체 범위:** `main/wifi_control_contract.c`의 전체 내용(1~169줄)을
아래 **`main/wifi_control_contract.c — 새 파일 전체`**의 완결된 C 블록으로 교체하도록 안내했다.
현재 수정본을 다시 입력할 필요는 없다. header 주석의 `파실`은
`파싱`의 오타지만 기능·컴파일에는 영향이 없다.

숫자를 읽는 조건은 `'0' 이상이면서 '9' 이하`다. header의 함수 **선언**에는 `;`가 필요하지만,
source에서 `{ ... }`를 붙이는 함수 **정의**에는 닫는 괄호 뒤 `;`를 넣지 않는다.
최초 저장본 PC 검사는49줄에서 컴파일이 멈춰 **0 tests / ERROR1**이었다.
이후 수정·저장본을 직접 컴파일·실행해 **15 tests / PASS**를 확인했다.
아래 안내 후보의15 PASS 및 ESP 전체 빌드·보드 결과와 구분한다.

## 입력 순서와 정확한 범위

ESP 프로젝트 `03_Firmware/esp32_wifi_link`의 `main` 폴더에서 진행한다.

1. `main/wifi_control_contract.h`를 새로 만들고 아래 header 블록 전체를 입력한다.
2. `main/wifi_control_contract.c`를 새로 만들고 아래 source 블록 전체를 입력한다.
3. `main/CMakeLists.txt`의 **전체 내용**을 아래 CMake 블록으로 교체한다.

세 파일을 저장하면 이 입력 묶음이 끝난다. 이번 단계에서 `wifi_link_main.c`와 STM 파일을 수정할 필요는 없다.
새 `.c`를 CMake의 SRCS에 등록하지만 아직 WebSocket handler에서 호출하지 않으므로,
프로그램의 PING/DISARM 동작과 UART 입력 허용 범위는 현재 상태를 유지한다.
외부 함수로 정의해서 아직 caller가 없다는 이유로 static unused-function 경고를 만들지 않는다.

### main/wifi_control_contract.h — 새 파일 전체

```c
#ifndef WIFI_CONTROL_CONTRACT_H
#define WIFI_CONTROL_CONTRACT_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define WIFI_CONTROL_MAX_FRAME_SIZE 128U
#define WIFI_CONTROL_ZERO_ONLY 1U
#define WIFI_CONTROL_VX_MIN_MMPS (-100)
#define WIFI_CONTROL_VX_MAX_MMPS 100
#define WIFI_CONTROL_W_MIN_MRADPS (-500)
#define WIFI_CONTROL_W_MAX_MRADPS 500

typedef enum {
    WIFI_CONTROL_ARM,
    WIFI_CONTROL_CMD
} wifi_control_type_t;

typedef enum {
    WIFI_CONTROL_PARSE_OK,
    WIFI_CONTROL_PARSE_BAD_FORMAT,
    WIFI_CONTROL_PARSE_OUT_OF_RANGE
} wifi_control_parse_status_t;

typedef struct {
    wifi_control_type_t type;
    uint32_t expected_boot_id;
    uint32_t request_id;
    uint32_t control_id;
    uint32_t ticket;
    int32_t vx_mmps;
    int32_t w_mradps;

    /* ESP가 나중에 채울 값. 브라우저 문자열에서 읽지 않는다. */
    uint32_t ws_session_id;
    uint64_t accepted_ms;
    uint64_t expires_ms;
} wifi_control_request_t;

/* 성공할 때만 out에 복사한다. 실패하면 이전 out을 사용하지 않는다. */
wifi_control_parse_status_t wifi_control_parse(
    const char *text, size_t length,
    wifi_control_request_t *out);

/* 파싱 성공 요청의 zero-only 적합성만 확인한다. 제어 허가가 아니다. */
bool wifi_control_zero_only_allows(
    const wifi_control_request_t *request);

#endif
```

### main/wifi_control_contract.c — 새 파일 전체

```c
#include "wifi_control_contract.h"

#include <string.h>

/* 일치한 문자열만큼 cursor를 이동한다. */
static bool control_take_literal(
    const char **cursor, const char *literal)
{
    const size_t length = strlen(literal);

    if (strncmp(*cursor, literal, length) != 0) {
        return false;
    }

    *cursor += length;
    return true;
}

/* u32 overflow를 곱셈 전에 검사한다. */
static bool control_read_u32(const char **cursor, uint32_t *out)
{
    const char *pos = *cursor;
    uint32_t value = 0U;

    if (*pos < '0' || *pos > '9') {
        return false;
    }

    while (*pos >= '0' && *pos <= '9') {
        const uint32_t digit = (uint32_t)(*pos - '0');

        if (value > (UINT32_MAX - digit) / 10U) {
            return false;
        }

        value = value * 10U + digit;
        ++pos;
    }

    *cursor = pos;
    *out = value;
    return true;
}

/* 부호와 magnitude를 따로 읽어 INT32_MIN도 안전하게 처리한다. */
static bool control_read_i32(const char **cursor, int32_t *out)
{
    const char *pos = *cursor;
    const bool negative = *pos == '-';
    uint32_t magnitude = 0U;

    if (negative) {
        ++pos;
    }

    if (!control_read_u32(&pos, &magnitude)) {
        return false;
    }

    const uint32_t limit = negative
        ? (uint32_t)INT32_MAX + 1U
        : (uint32_t)INT32_MAX;

    if (magnitude > limit) {
        return false;
    }

    int32_t value;

    if (negative && magnitude == limit) {
        value = INT32_MIN;
    } else if (negative) {
        value = -(int32_t)magnitude;
    } else {
        value = (int32_t)magnitude;
    }

    *cursor = pos;
    *out = value;
    return true;
}

wifi_control_parse_status_t wifi_control_parse(
    const char *text, size_t length,
    wifi_control_request_t *out)
{
    if (text == NULL || out == NULL || length == 0U ||
        length > WIFI_CONTROL_MAX_FRAME_SIZE) {
        return WIFI_CONTROL_PARSE_BAD_FORMAT;
    }

    /* 공백·개행·중간 NUL·비ASCII를 복사 전에 거부한다. */
    for (size_t i = 0U; i < length; ++i) {
        const uint8_t byte = (uint8_t)text[i];

        if (byte < 0x21U || byte > 0x7eU) {
            return WIFI_CONTROL_PARSE_BAD_FORMAT;
        }
    }

    char buffer[WIFI_CONTROL_MAX_FRAME_SIZE + 1U];
    memcpy(buffer, text, length);
    buffer[length] = '\0';

    const char *cursor = buffer;
    wifi_control_request_t parsed = {0};

    if (control_take_literal(&cursor, "ARM,")) {
        parsed.type = WIFI_CONTROL_ARM;
    } else if (control_take_literal(&cursor, "CMD,")) {
        parsed.type = WIFI_CONTROL_CMD;
    } else {
        return WIFI_CONTROL_PARSE_BAD_FORMAT;
    }

    if (!control_take_literal(&cursor, "boot_id=") ||
        !control_read_u32(&cursor, &parsed.expected_boot_id) ||
        !control_take_literal(&cursor, ",request_id=") ||
        !control_read_u32(&cursor, &parsed.request_id) ||
        parsed.request_id == 0U) {
        return WIFI_CONTROL_PARSE_BAD_FORMAT;
    }

    if (parsed.type == WIFI_CONTROL_CMD) {
        if (!control_take_literal(&cursor, ",control_id=") ||
            !control_read_u32(&cursor, &parsed.control_id) ||
            parsed.control_id == 0U) {
            return WIFI_CONTROL_PARSE_BAD_FORMAT;
        }
    }

    if (!control_take_literal(&cursor, ",ticket=") ||
        !control_read_u32(&cursor, &parsed.ticket) ||
        parsed.ticket == 0U) {
        return WIFI_CONTROL_PARSE_BAD_FORMAT;
    }

    if (parsed.type == WIFI_CONTROL_CMD) {
        if (!control_take_literal(&cursor, ",vx_mmps=") ||
            !control_read_i32(&cursor, &parsed.vx_mmps) ||
            !control_take_literal(&cursor, ",w_mradps=") ||
            !control_read_i32(&cursor, &parsed.w_mradps)) {
            return WIFI_CONTROL_PARSE_BAD_FORMAT;
        }
    }

    if (*cursor != '\0') {
        return WIFI_CONTROL_PARSE_BAD_FORMAT;
    }

    if (parsed.vx_mmps < WIFI_CONTROL_VX_MIN_MMPS ||
        parsed.vx_mmps > WIFI_CONTROL_VX_MAX_MMPS ||
        parsed.w_mradps < WIFI_CONTROL_W_MIN_MRADPS ||
        parsed.w_mradps > WIFI_CONTROL_W_MAX_MRADPS) {
        return WIFI_CONTROL_PARSE_OUT_OF_RANGE;
    }

    *out = parsed;
    return WIFI_CONTROL_PARSE_OK;
}

bool wifi_control_zero_only_allows(
    const wifi_control_request_t *request)
{
    return request != NULL &&
        (request->type == WIFI_CONTROL_ARM ||
         request->type == WIFI_CONTROL_CMD) &&
        request->vx_mmps == 0 && request->w_mradps == 0;
}
```

### main/CMakeLists.txt — 기존 파일 전체 교체

```cmake
idf_component_register(
    SRCS "wifi_link_main.c" "wifi_control_contract.c"
    INCLUDE_DIRS "."
    PRIV_REQUIRES
        esp_wifi esp_event esp_netif esp_http_server
        esp_timer esp_system esp_hw_support nvs_flash freertos
        esp_driver_uart
)
```

## 읽는 흐름과 각 변수의 역할

```text
WebSocket TEXT와 실제 바이트 길이
  → length/ASCII 검사
  → 로컬 buffer에 복사하고 끝에 NUL 추가
  → cursor로 명령/필드를 차례로 읽기
  → 임시 parsed에 숫자 저장
  → 끝/범위 검사 성공
  → 호출자의 out에 한 번 복사
```

- `text`: 입력 배열을 가리키는 주소다. 입력이 NUL로 끝난다고 가정하지 않고 `length`만큼만 읽는다.
- `buffer`: parser 내부의128+1byte 배열이다. 마지막1byte는 `\0`용이며 허용 payload 길이는128byte다.
- `cursor`: **buffer 안에서 지금 읽을 위치**를 가리키는 포인터다. 문자열을 새로 저장하는 배열이 아니다.
- helper의 `const char **cursor`: 호출자의 cursor 자체를 이동시키려고 포인터의 주소를 받는다.
  예를 들어 `control_take_literal(&cursor, "boot_id=")`는 일치한8글자 다음으로 caller의 cursor를 옮긴다.
- `parsed`: 아직 검사 중인 임시 요청이다. 중간 실패에서 caller에게 일부 필드만 전달되지 않도록 사용한다.
- `out`: caller가 만든 요청 구조체의 주소다. `*out = parsed`에서 구조체 내용을 복사한다.
- `ws_session_id/accepted_ms/expires_ms`: parser 성공 때0이다. 나중에 **ESP가** 연결 ID·접수 시각·실제 마감을 채운다.
  브라우저가 문자열에 이 필드를 넣으면 추가 필드로 거부한다.

## 형식 검사와 제어 허가는 다르다

| 입력 | parser 결과 | zero-only 적합성 | 의미 |
| --- | --- | --- | --- |
| `ARM,boot_id=7,request_id=1,ticket=9` | OK | true | 숫자/형식만 정상. 실제 boot/ticket/FAULT 확인 전에는 ARM을 보낼 수 없음 |
| `CMD,boot_id=7,request_id=2,control_id=1,ticket=10,vx_mmps=0,w_mradps=0` | OK | true | zero CMD 형식 정상. 제어 owner·ticket/마감 검사는 아직 필요 |
| 같은 CMD의 `vx_mmps=50` | OK | false | 표현 가능한 속도 요청이지만 첫 zero-only 모드에서는 거부해야 함 |
| 같은 CMD의 `vx_mmps=101` | OUT_OF_RANGE | 검사하지 않음 | 현재 STM 범위 초과 |
| `request_id=0`, `ticket=0`, CMD의 `control_id=0` | BAD_FORMAT | 검사하지 않음 | 유효 식별 번호가 아님 |
| 추가 필드·필드 순서 오류·공백·개행·u32 overflow | BAD_FORMAT | 검사하지 않음 | 모호한 입력을 실행 경로로 넘기지 않음 |

`PARSE_OK`는 수락 notice나 STM ACK가 아니다. `zero_only_allows=true`도 제어권을 부여하지 않는다.
앞으로 caller는 먼저 parse 결과를 확인하고, 실패하면 `out`의 이전 내용을 사용하지 않고 즉시 거부해야 한다.
숫자가 있어도 아직 ticket이 발급되거나 검증된 것이 아니므로 이 예시를 브라우저에서 실제 송신하지 않는다.

단순 `atoi()` 대신 범위를 검사하며 숫자를 읽는다. `4294967296`이0으로 바뀌거나 signed overflow가 생기는 것을 막는다.
`INT32_MIN`을 처리하는 코드는 음수 변환 과정의 overflow 방지이며, 실제 허용 속도는 마지막 검사에서 더 작게 제한한다.
`+1`은 거부하고 `-0`/앞자리0은 기존 십진수 해석처럼 허용한다. 숫자로 변환한 값으로 비교할 예정이다.

## 저장 후 검사와 이 단계의 완료 기준

1. Codex가 실제 세 파일을 다시 읽고 안내 블록·위치·CMake 연결을 확인한다.
2. 실제 저장된 `.h/.c`로 PC C 검사를 실행한다. 형식/숫자 경계·실제 길이·오염된 바이트·실패 시 출력 유지·zero-only 구분을 확인한다.
3. 필요하면 사용자가 ESP 빌드를 수행한다. 이번 입력만으로 플래시나 보드 전원 연결은 필요하지 않다.

**PASS 범위:** AC-H01의 parser와 zero-only helper 자체. 허가 세대·ticket 만료·태스크 경합·UART 송신·보드 동작은 다음 단계다.
안내 블록을 임시 PC 파일로 컴파일한 결과는 입력 후보 검사다. 실제 저장본 검사나 ESP 전체 빌드로 표시하지 않는다.

10/10 준비 당시: 위 두 C 블록을 임시 폴더에 추출해 TCC `-Wall -Werror`로 컴파일한 **후보15 PASS**.
Codex가 `test_wifi_control_parser.py`와 fixture를 준비했고, 사용자 파일이 없던 기본 실행은 **SKIP1/0 tests**였다.
최초 사용자 저장본 검사는 source49줄의 `boll`에서 컴파일이 멈춰 **0 tests / ERROR1**이었다.
이후5곳이 수정된 저장본을 다시 읽고 TCC `-Wall -Werror`로 실제 모듈을 컴파일·실행해
**15 tests / PASS**를 확인했다. 형식/숫자 경계·실제 길이·오염된 바이트·출력 유지·zero-only 구분의 결과다.
이후 ESP 전체 빌드 성공을 사용자가 확인했다. 빌드 로그·바이너리 hash는 미제공이며,
Codex가 ESP 빌드를 실행하거나 새 플래시·보드 동작을 확인한 것은 아니다.
기존 `wifi_link_main.c` hash는 W5 마감과 동일하다. parser는 아직 WebSocket/UART 실행 경로에 연결되지 않았다.
