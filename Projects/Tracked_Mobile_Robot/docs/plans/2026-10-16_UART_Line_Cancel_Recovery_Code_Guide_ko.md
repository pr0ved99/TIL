# UART 재연결 첫 DISARM 복구 코드 가이드

작성: **2026-10-16**. 후속 상태: 사용자 4개 파일 입력·저장본 PC513조합+executor17+main42·양쪽 보드 빌드/플래시·재연결 관측 완료. 부분 명령 폐기의 실물 수용은 미완료이며 [보고서36](../verification/36_UART_Line_Cancel_Recovery_2026-10-16_ko.md)을 따른다. 아래 교체 블록은 입력 당시 이력으로, 현재 파일에 다시 적용하지 않는다. 입력 전 후보 manifest의 guide hash에 해당하는 [원본 안내 snapshot](../../assets/logs/wifi_link/2026-10-16_uart_cancel_candidate/code_guide_snapshot.txt)을 보존했다.

## 해결할 문제와 현재 증거

STM은 LF가 도착할 때 한 줄을 파싱한다. `CMD,seq=`가 남은 상태에서 `DISARM,seq=123\n`이 붙으면 한 줄 `CMD,seq=DISARM,seq=123`으로 해석해 첫 정지 요청을 잃는다. PC에서 이 결합을 재현했다. 반대로 LF만 먼저 보내면 완성된 `ARM,seq=99` 뒤에 LF가 붙어 오래된 ARM이 실행될 수 있다.

실물 UR-01 run01에서는 CMD와 자동 DISARM이 통째로 유실됐고, 재연결 첫 DISARM 2760658648은 성공했다. 이 성공은 부분 명령 실패가 고쳐졌다는 증거가 아니다. [실물 관측](../../assets/logs/wifi_link/2026-10-16_ur01_uart_reconnect_run01/observations.json)과 [기존 실패 보고](../verification/35_WiFi_Zero_Control_Fault_Recovery_2026-10-15_ko.md)를 구분한다.

## 수신과 송신의 책임

ESP는 모든 DISARM 앞에 **ASCII CAN 0x18과 LF 0x0A** 두 바이트를 붙인다. CAN은 이 UART 프로토콜의 줄 폐기 표식이며, 이후 계획된 CAN 통신 버스와는 별개다. 정상 ARM·CMD·PING 형식은 그대로다. 부팅의 초기 동기화와 DISARM 재시도, 기존 PING/DISARM 송신 경로도 같은 규칙을 사용한다.

STM은 CAN을 만나면 현재 줄의 길이와 overflow 상태를 지우고, 다음 LF까지 수신 바이트를 폐기한다. 그 LF로 기존 줄을 실행하지 않는다. 다음 새 DISARM은 원래 파서와 정지 처리기를 통과해 모터 정지, seq 갱신, ACK 송신을 수행한다. **CAN 자체는 ARM 허가나 DISARM 확인 응답이 아니다.**

```text
남은 CMD 조각 → CAN → LF → DISARM,seq=새번호 → LF
                │     │                         │
           줄 폐기 시작  새 줄 수집 시작       정지 처리와 ACK
```

수신 상태는 COLLECT(줄 수집), DISCARD_CANCEL(의도적인 폐기), DISCARD_ERROR(HAL/RX 오류 뒤 폐기) 셋이다. 의도적인 폐기는 err를 늘리지 않는다. 기존 HAL/RX 오류가 먼저 발생했다면 CAN이 오류 상태를 덮어쓰지 않으며, LF에서 RX_DESYNC를 보고한 다음 새 줄을 받는다. 정상 LF/CRLF와 프레임 길이 제한은 그대로다.

ESP의 STOPPING→IDLE 조건도 그대로다. 정확한 DISARM seq/type의 ACK와, ACK 이후 수신 세대의 정지 TEL을 확인한다. TEL의 STM 시각은 ACK보다 이전이면 안 된다. 응답 누락·short write·확인 시간 초과는 BLOCKED이며, 자동 ARM·CMD 재시도는 없다. 기존 short-write 전용 need_line_sync 플래그는 모든 DISARM에 폐기 표식을 넣으므로 제거한다.

## 대안과 범위

- LF만 추가: 오래된 ARM을 실행하는 PC 반례가 있어 채택하지 않았다.
- 정지 명령 재전송: 첫 줄을 잃는 문제를 감추고 기존 수동 복구 규칙을 바꾸므로 채택하지 않았다.
- 수신 줄 시간 제한만 추가: 지연된 정상 분할 수신과 시간 경계를 새로 정의해야 하며, 기한 전 정지 요청도 처리해야 한다.
- CAN+LF: 추가 2바이트로 수신 줄을 명시적으로 폐기한다. 115200/8N1에서 이 두 바이트의 선로 시간은 약 174µs이며, 전체 정지 지연 측정값은 아니다.

이번 보완은 폐기 표식과 새 DISARM이 정상 수신될 때의 복구다. 그 도중 추가 단절, HAL 오류, RX ring overflow로 새 DISARM까지 버려지면 성공을 보장하지 않으며 BLOCKED를 유지한다. CAN 이전에 이미 LF까지 도착해 실행된 명령은 소급 취소할 수 없다. UART seq 재생 방지와 물리 PWM 차단 시간은 별도 범위다.

## 입력 순서

현재 READY/IDLE과 MDD10A B+ 분리·절연을 유지한다. 아래 4개 파일의 변경을 **모두 입력·저장**한다. `wifi_link_config.h`와 Wi-Fi 자격 증명은 대상이 아니다. 표기한 줄 번호는 입력 전 저장본 기준이므로 검색할 원문을 우선한다. 각 항목의 기존 블록 전체를 교체 블록 전체로 바꾸고, 삭제 항목은 해당 한 줄만 지운다.

## 1 uart_mvp_protocol.c

[대상 파일](../../03_Firmware/stm32_uart_mvp/Core/Src/uart_mvp_protocol.c)

### 수신 줄 상태 선언

입력 전 70행 부근의 다음 블록을 찾는다.

```c
static uint8_t s_rx_discard_until_lf;
```

다음으로 교체한다.

```c
typedef enum {
    UART_RX_COLLECT = 0,
    UART_RX_DISCARD_ERROR,
    UART_RX_DISCARD_CANCEL
} uart_rx_line_mode_t;

static uart_rx_line_mode_t s_rx_line_mode;
```

### begin_rx_resynchronization 내부

입력 전 245행 부근의 다음 블록을 찾는다.

```c
    s_rx_discard_until_lf = 1u;
```

다음으로 교체한다.

```c
    s_rx_line_mode = UART_RX_DISCARD_ERROR;
```

### uart_mvp_init 내부

입력 전 606행 부근의 다음 블록을 찾는다.

```c
    s_rx_desync_pending = 0u;
    s_rx_discard_until_lf = 0u;
```

다음으로 교체한다.

```c
    s_rx_desync_pending = 0u;
    s_rx_line_mode = UART_RX_COLLECT;
```

### uart_mvp_process의 LF 폐기 분기 전체

입력 전 695행 부근의 다음 블록을 찾는다.

```c
        if(s_rx_discard_until_lf != 0u){
            if(byte == '\n'){
                s_rx_discard_until_lf = 0u;
                uart_sendf("ERR,seq=0,type=RX,code=RX_DESYNC\n");
            }
            continue;
        }
```

다음으로 교체한다.

```c
        /* CAN (0x18) cancels a pending line without executing it.
         * Keep discarding through LF; preserve a prior hardware-error report.
         * This changes framing only. DISARM below still owns the stop/ACK.
         */
        if(byte == 0x18u){
            s_line_len = 0u;
            s_line_overflow = 0u;
            if(s_rx_line_mode == UART_RX_COLLECT){
                s_rx_line_mode = UART_RX_DISCARD_CANCEL;
            }
            continue;
        }

        if(s_rx_line_mode != UART_RX_COLLECT){
            if(byte == '\n'){
                if(s_rx_line_mode == UART_RX_DISCARD_ERROR){
                    uart_sendf("ERR,seq=0,type=RX,code=RX_DESYNC\n");
                }
                s_rx_line_mode = UART_RX_COLLECT;
            }
            continue;
        }
```

## 2 wifi_control_executor.h

[대상 파일](../../03_Firmware/esp32_wifi_link/main/wifi_control_executor.h)

### UART 프레임 크기 정의 바로 아래

입력 전 7행 부근의 다음 블록을 찾는다.

```c
#define WIFI_CONTROL_UART_FRAME_SIZE 96U
```

다음으로 교체한다.

```c
#define WIFI_CONTROL_UART_FRAME_SIZE 96U
/* ASCII CAN + LF: discard the pending STM line before a new stop command. */
#define WIFI_CONTROL_UART_CANCEL "\x18\n"
```

### executor 구조체의 폐기된 조건 플래그

입력 전 42행 부근의 다음 블록을 찾는다.

```c
    bool need_line_sync;
```

위 한 줄을 삭제한다.

## 3 wifi_control_executor.c

[대상 파일](../../03_Firmware/esp32_wifi_link/main/wifi_control_executor.c)

### take_tx의 ARM DISARM 포맷 분기

입력 전 183행 부근의 다음 블록을 찾는다.

```c
    } else {
        n = snprintf(tx.bytes, sizeof(tx.bytes), "%s%s,seq=%" PRIu32 "\n",
            op == WIFI_CONTROL_OP_DISARM && e->need_line_sync ? "\n" : "",
            op == WIFI_CONTROL_OP_ARM ? "ARM" : "DISARM", seq);
    }
```

다음으로 교체한다.

```c
    } else {
        /* Full UART writes do not prove that STM received every byte. */
        n = snprintf(tx.bytes, sizeof(tx.bytes), "%s%s,seq=%" PRIu32 "\n",
            op == WIFI_CONTROL_OP_DISARM ? WIFI_CONTROL_UART_CANCEL : "",
            op == WIFI_CONTROL_OP_ARM ? "ARM" : "DISARM", seq);
    }
```

### tx_complete의 short write 처리

입력 전 223행 부근의 다음 블록을 찾는다.

```c
    if (!full) {
        e->need_line_sync = true;
        /* An intervening cancel already revoked an old ARM/CMD pending. */
        if (e->state.pending == e->prepared_op && e->state.pending_seq == e->prepared_seq) {
            wifi_control_state_tx_failed(&e->state, now);
        }
    } else if (e->prepared_op == WIFI_CONTROL_OP_DISARM) {
        e->need_line_sync = false;
    }
```

다음으로 교체한다.

```c
    if (!full) {
        /* Every DISARM now cancels a partial line, including after short TX. */
        if (e->state.pending == e->prepared_op && e->state.pending_seq == e->prepared_seq) {
            wifi_control_state_tx_failed(&e->state, now);
        }
    }
```

## 4 wifi_link_main.c

[대상 파일](../../03_Firmware/esp32_wifi_link/main/wifi_link_main.c)

### stm_startup_send_request의 snprintf

입력 전 1306행 부근의 다음 블록을 찾는다.

```c
        frame, sizeof(frame),
        "%s,seq=%" PRIu32 "\n", command, seq);
```

다음으로 교체한다.

```c
        frame, sizeof(frame),
        "%s%s,seq=%" PRIu32 "\n",
        ping ? "" : WIFI_CONTROL_UART_CANCEL, command, seq);
```

### stm_startup_step SETTLE의 단독 LF 송신

입력 전 1365행 부근의 다음 블록을 찾는다.

```c
        if (uart_write_bytes(STM_UART_PORT, "\n", 1) != 1) {
            stm_startup_fail("line sync TX failed");
            break;
        }

        ESP_LOGI(TAG, "STARTUP: line sync sent");
```

다음으로 교체한다.

```c
        if (uart_write_bytes(STM_UART_PORT, WIFI_CONTROL_UART_CANCEL, 2) != 2) {
            stm_startup_fail("line cancel TX failed");
            break;
        }

        ESP_LOGI(TAG, "STARTUP: line cancel sent");
```

### wifi_command_step의 PING DISARM 포맷

입력 전 1655행 부근의 다음 블록을 찾는다.

```c
        line, sizeof(line),
        "%s,seq=%" PRIu32 "\n", command, s_wifi_uart_pending.seq);
```

다음으로 교체한다.

```c
        line, sizeof(line),
        "%s%s,seq=%" PRIu32 "\n",
        request.type == WIFI_COMMAND_DISARM ? WIFI_CONTROL_UART_CANCEL : "",
        command, s_wifi_uart_pending.seq);
```

### wifi_command_step의 TX_ERROR 분기

입력 전 1679행 부근의 다음 블록을 찾는다.

```c
    } else if (written != length) {
        xSemaphoreTake(s_stm_lock, portMAX_DELAY);
        s_control.need_line_sync = true;
        xSemaphoreGive(s_stm_lock);
        wifi_command_finish("TX_ERROR");
```

다음으로 교체한다.

```c
    } else if (written != length) {
        wifi_command_finish("TX_ERROR");
```

## 검증 결과와 저장 후 순서

후보를 임시 디렉터리에서 실제 STM stream/parser/ring/mapper, ESP executor/state와 함께 PC 실행했다. HAL·모터·IRQ·UART/RTOS는 mock이다. main의 실제 부팅 함수도 추출해 검사했다.

- 513개 prefix/state 조합: 빈 prefix와 모든 비어 있지 않은 부분 줄, IDLE·ARMED·timeout 뒤 상태. ARM, zero/nonzero CMD, DISARM, PING, ESTOP_RESET과 CRLF를 포함한다. 첫 새 DISARM ACK, 오래된 ARM/CMD 실행 없음, 의도적 취소로 ERR 증가 없음.
- 분할 수신, 한 번에 큐에 넣은 데이터, 반복 CAN, ring wrap, 최대 길이 CRLF와 line/ring overflow, HAL 오류 뒤 복구 통과.
- 299/300ms watchdog 경계, CMD-only 재ARM 거부, E-stop latch 유지, 정확한 ACK와 새 TEL 확인, short write의 BLOCKED 유지 통과.
- 부팅의 CAN+LF, 정지 재시도, PING/PONG, TX 실패 처리 통과.
- 기존 executor 17개와 main 어댑터 42개 검사 통과. 프레임 앞 2바이트에 대한 기대값만 새 계약에 맞추며 기존 시나리오는 유지한다.

원본 출력: [candidate_pc.txt](../../assets/logs/wifi_link/2026-10-16_uart_cancel_candidate/candidate_pc.txt). 입력/후보 식별: [source_manifest.json](../../assets/logs/wifi_link/2026-10-16_uart_cancel_candidate/source_manifest.json). 후보 검사는 현재 펌웨어를 덮어쓰지 않는다.

```powershell
python Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_uart_recovery.py --candidate
# 사용자가 4개 파일을 저장한 뒤 실제 저장본 검사
python Projects/Tracked_Mobile_Robot/03_Firmware/tests/test_uart_recovery.py --saved
```

컴파일러는 기존처럼 WIFI_CONTROL_HOST_CC에 PC용 TCC/GCC 경로를 지정한다. 두 실행은 PC 검사이며 STM/ESP 대상 보드 빌드는 사용자가 수행한다. 기존 reproduce_uart_reconnect.py는 수정 전 실패를 기대하는 진단이므로 수정 뒤 성공 판정에 사용하지 않는다.

**이 안내의 입력·저장본 검사·양쪽 빌드/플래시 단계는 완료됐다.** 현재는 `--saved`를 사용한다. `--candidate`는 수정 전 baseline에만 적용되는 변환이다. 다음은 UR-02 통제된 부분 명령 주입 경로의 설계/PC 검토이며 아직 해당 시험 코드는 없다.

이후 실물 PASS 기준은 CAN+LF와 새 DISARM이 D3/D1 양끝에서 확인되고, 정확한 ACK 및 새 정지 TEL 뒤 IDLE, 자동 재ARM 없음이다. 무작위 손 분리에서 부분 CMD가 생기지 않으면 정상 복구 관측으로만 기록한다. 의도적인 부분 줄 주입은 별도 통제 시험으로 안내한다. 현재 UART 4채널만으로 물리 PWM·전력 차단 PASS를 선언하지 않는다.
