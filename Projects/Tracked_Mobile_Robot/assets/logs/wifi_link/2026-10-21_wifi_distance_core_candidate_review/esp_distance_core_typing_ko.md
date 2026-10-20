# ESP 목표 거리 명령 — 공통 계약·UART 전송 입력

## 목적과 이번 범위

`TK-MVP-03-06`: 브라우저에서5·10·15·20cm를 선택하여 명령하고, STM이 엔코더 count로 좌우 출력을 각각 차단한 뒤 공중 궤도의 링크 이동량을 실측한다. 이번에는 그 명령을 운반할 ESP 공통 계층을 준비한다. **검토 후보이며 아직 생산 소스에 적용하지 않았다.**

대상은 `03_Firmware/esp32_wifi_link/main`의 `wifi_control_contract.h/.c`, `wifi_control_executor.c`3개 파일/5개 교체 구간이다. 사용자 직접 입력·저장 후 실제 저장본 검사가 필요하다. 브라우저 입력·완료 표시는 다음 묶음이며 지금 새 보드 빌드/flash/구동을 하지 않는다.

## 상태와 데이터 흐름

1. 거리 명령도 기존 `CMD,boot_id=...,request_id=...,control_id=...,ticket=...,vx_mmps=100,w_mradps=0` 뒤에 `,distance_mm=50/100/150/200`만 추가한다. 단위는 mm다. 일반 CMD에는 이 필드가 없고 구조체 값은0이다.
2. parser는 성공한 경우에만 임시 구조체를 out으로 복사한다. 잘못된 거리·방향·필드 순서·중복·overflow·개행은 거부한다. 명시적 `distance_mm=0`도 거부한다. zero 정지 CMD는 거리 필드를 **생략**한다.
3. `wifi_control_request_allows()`는 값/모드 정책을 담당한다. ARM에 거리 필드를 허용하지 않고 zero-only 모드도 거리 명령을 거부한다. parser 성공은 제어 허가가 아니다.
4. 기존 executor가 부팅·owner·control ID·ticket·만료·ACTIVE 조건을 확인한다. ARM 직후 첫 CMD는 기존처럼 zero다. 큐에서 전송할 때도 상태/유효기한을 검사한다. 새 우회 경로를 만들지 않는다.
5. UART에는 `CMD,seq=...,vx_mmps=100,w_mradps=0,timeout_ms=300,distance_mm=...`을 보낸다. STM은 현재 ARM의 목표/시작점을 고정하고, 같은 목표 반복은 keepalive로 처리한다. 도달 이후 반복으로 재시작하지 않는다.
6. 버튼 해제의 zero CMD는 suffix를 생략하여 STM 거리 동작을 취소한다. 목표 변경/일반 주행으로의 전환은 STM의 거리 latch를 우회하지 못한다. 다음 시도는 DISARM과 새 ARM을 사용한다.

ESP는 전송·수명·제어권을 관리하고 **거리 판정·좌우 PWM 차단·최종 안전 정지는 STM 책임**으로 유지한다. 동일 명령 종류를 확장하여 기존 ACK/ERR·ticket·owner/state 검증을 재사용한다. 새로운 MOVE 명령이나 별도 UART 송신 경로를 추가하지 않는다.

## 실패와 증거 경계

잘못된 요청은 UART 출력 전에 거부한다. 기존 queue 만료·연결 종료·short TX·ACK timeout·STM ERR는 기존 STOPPING과 부분 줄 취소/DISARM 경로를 유지한다. 유효한 거리 요청의 UART ACK는 접수 근거이며 실제 거리 도달/기계적 정지 PASS가 아니다. count 차단 뒤 관성 이동량도 이후 실측에 포함한다.

Web 최대 ID 조합의 거리 CMD는123byte로 기존128byte 제한 안이다. STM UART 최대 seq의 목표 CMD도 기존96byte 버퍼 안이다. 제한이나 PWM gain/cap을 늘릴 필요가 없다. `vx=100`은 현재 매퍼의 요청값이며 실측100mm/s를 뜻하지 않는다.

PC PASS 기준: 기존 일반 주행·zero-only 회귀,4개 목표의 parser→ticket/owner/state→정확한 UART 필드 보존, invalid/overflow/방향 오류 거부, 첫 zero 강제, 잘못된 owner/boot/control/ticket·만료 거부, 전송 실패 정지, 의도적으로 거리 필드명을 바꾼 오류 주입 검출. PC 모의 검사는 실제 ESP build·FreeRTOS/UART 주기·STM 정지거리 검증을 대체하지 않는다.

아래5개 구간을 순서대로 교체한다. 기존 정책 함수나 전송 함수를 남겨 중복 정의하지 않는다.

## 1. `wifi_control_contract.h` — 요청 구조체의 속도 필드 구간 교체

찾을 기존 구간:

```c
    int32_t vx_mmps;
    int32_t w_mradps;
```

위 기존 구간을 삭제하고 아래 전체 블록으로 교체한다. 추가로 붙이지 않는다.

```c
    int32_t vx_mmps;
    int32_t w_mradps;
    uint32_t distance_mm; /* 0: ordinary CMD; 50/100/150/200: forward goal. */
```

## 2. `wifi_control_contract.h` — 정책 함수 전체 교체와 거리 검사 helper 추가

교체 시작: `/* Value/mode policy only; owner, ticket, phase and time checks are separate. */`

기존 정책 주석부터 `wifi_control_request_allows()` 닫는 중괄호까지 교체한다. 마지막 `#endif`는 유지한다.

위 기존 구간을 삭제하고 아래 전체 블록으로 교체한다. 추가로 붙이지 않는다.

```c
/* Distance is optional: zero means an ordinary CMD, not a zero-length move. */
static inline bool wifi_control_distance_goal_valid(uint32_t distance_mm)
{
    return distance_mm == 50U || distance_mm == 100U ||
        distance_mm == 150U || distance_mm == 200U;
}

/* Value/mode policy only; owner, ticket, phase and time checks are separate. */
static inline bool wifi_control_request_allows(
    const wifi_control_request_t *request)
{
    if (request == NULL) {
        return false;
    }
    const bool is_zero = request->vx_mmps == 0 && request->w_mradps == 0;
    if (request->type == WIFI_CONTROL_ARM) {
        return is_zero && request->distance_mm == 0U;
    }
    if (request->type != WIFI_CONTROL_CMD ||
        request->vx_mmps < WIFI_CONTROL_VX_MIN_MMPS ||
        request->vx_mmps > WIFI_CONTROL_VX_MAX_MMPS ||
        request->w_mradps < WIFI_CONTROL_W_MIN_MRADPS ||
        request->w_mradps > WIFI_CONTROL_W_MAX_MRADPS) {
        return false;
    }
    if (request->distance_mm != 0U &&
        (!wifi_control_distance_goal_valid(request->distance_mm) ||
         request->vx_mmps != 100 || request->w_mradps != 0)) {
        return false;
    }
    return WIFI_CONTROL_ZERO_ONLY == 0U ||
        (is_zero && request->distance_mm == 0U);
}
```

## 3. `wifi_control_contract.c` — wifi_control_parse 함수 전체 교체

교체 시작: `wifi_control_parse_status_t wifi_control_parse(`

해당 함수의 선언부터 닫는 중괄호까지 전체 교체한다. 다음 함수는 유지한다.

위 기존 구간을 삭제하고 아래 전체 블록으로 교체한다. 추가로 붙이지 않는다.

```c
wifi_control_parse_status_t wifi_control_parse(
    const char *text, size_t length,
    wifi_control_request_t *out)
{
    if (text == NULL || out == NULL || length == 0U ||
        length > WIFI_CONTROL_MAX_FRAME_SIZE) {
        return WIFI_CONTROL_PARSE_BAD_FORMAT;
    }

    /* 공백, 개행, 중간, NUL, 비ASCII를 복사 전에 거부한다. */
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
        if (*cursor != '\0') {
            if (!control_take_literal(&cursor, ",distance_mm=") ||
                !control_read_u32(&cursor, &parsed.distance_mm) || *cursor != '\0') {
                return WIFI_CONTROL_PARSE_BAD_FORMAT;
            }
            if (!wifi_control_distance_goal_valid(parsed.distance_mm) ||
                parsed.vx_mmps != 100 || parsed.w_mradps != 0) {
                return WIFI_CONTROL_PARSE_OUT_OF_RANGE;
            }
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
```

## 4. `wifi_control_contract.c` — wifi_control_zero_only_allows 함수 전체 교체

교체 시작: `bool wifi_control_zero_only_allows(`

해당 함수의 선언부터 닫는 중괄호까지 전체 교체한다. 다음 함수는 유지한다.

위 기존 구간을 삭제하고 아래 전체 블록으로 교체한다. 추가로 붙이지 않는다.

```c
bool wifi_control_zero_only_allows(
    const wifi_control_request_t *request)
{
    return request != NULL &&
        (request->type == WIFI_CONTROL_ARM ||
            request->type == WIFI_CONTROL_CMD) &&
        request->vx_mmps == 0 && request->w_mradps == 0 &&
        request->distance_mm == 0U;
}
```

## 5. `wifi_control_executor.c` — wifi_control_executor_take_tx 함수 전체 교체

교체 시작: `bool wifi_control_executor_take_tx(`

해당 함수의 선언부터 닫는 중괄호까지 전체 교체한다. 다음 함수는 유지한다.

위 기존 구간을 삭제하고 아래 전체 블록으로 교체한다. 추가로 붙이지 않는다.

```c
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
        if (e->request.distance_mm != 0U) {
            n = snprintf(tx.bytes, sizeof(tx.bytes),
                "CMD,seq=%" PRIu32 ",vx_mmps=%" PRIi32
                ",w_mradps=%" PRIi32 ",timeout_ms=%" PRIu32
                ",distance_mm=%" PRIu32 "\n",
                seq, e->request.vx_mmps,
                e->request.w_mradps, (uint32_t)WIFI_CONTROL_STM_TIMEOUT_MS,
                e->request.distance_mm);
        } else {
            n = snprintf(tx.bytes, sizeof(tx.bytes),
                "CMD,seq=%" PRIu32 ",vx_mmps=%" PRIi32
                ",w_mradps=%" PRIi32 ",timeout_ms=%" PRIu32 "\n",
                seq, e->request.vx_mmps, e->request.w_mradps,
                (uint32_t)WIFI_CONTROL_STM_TIMEOUT_MS);
        }
    } else {
        /* Full UART writes do not prove that STM received every byte. */
        n = snprintf(tx.bytes, sizeof(tx.bytes), "%s%s,seq=%" PRIu32 "\n",
            op == WIFI_CONTROL_OP_DISARM ? WIFI_CONTROL_UART_CANCEL : "",
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
```

## 입력 후 확인

3개 파일의5개 구간을 함께 저장한 뒤 `확인해`라고 알려준다. Codex가 실제 저장본과 `--saved` native 검사를 대조한다. 이 단계에서 ESP/STM 빌드·flash·구동은 진행하지 않는다. 다음 입력 묶음에서 브라우저 거리 선택·정지 대기·누르는 동안만 실행·완료 표시를 연결한다.
