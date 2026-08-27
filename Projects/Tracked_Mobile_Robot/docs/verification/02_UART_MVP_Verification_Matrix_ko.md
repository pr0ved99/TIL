# UART MVP Verification Matrix

## 목적

이 문서는 UART MVP 요구사항과 실제 검증 증거를 연결한다.

검증 기준:

- PASS: 실제 STM32 보드와 Web Serial dashboard로 확인했고 증거 파일이 존재한다.
- PARTIAL: 일부 조건만 확인했거나 증거가 부족하다.
- PLANNED: 아직 검증하지 않았다.

## Evidence Set

| Evidence ID | File | Meaning |
| --- | --- | --- |
| EV-CSV-20260709 | [`../../04_PC_Serial_Control/logs/2026-07-09_uart_mvp_validation_session.csv`](../../04_PC_Serial_Control/logs/2026-07-09_uart_mvp_validation_session.csv) | 전체 UART TX/RX 세션 로그 |
| EV-IMG-01 | [`../../assets/screenshots/uart_mvp/2026-07-09_01_web_dashboard_connected_idle.png`](../../assets/screenshots/uart_mvp/2026-07-09_01_web_dashboard_connected_idle.png) | connected idle + periodic TEL |
| EV-IMG-02 | [`../../assets/screenshots/uart_mvp/2026-07-09_02_ping_pong_response.png`](../../assets/screenshots/uart_mvp/2026-07-09_02_ping_pong_response.png) | PING/PONG response |
| EV-IMG-03 | [`../../assets/screenshots/uart_mvp/2026-07-09_03_cmd_before_arm_not_armed_error.png`](../../assets/screenshots/uart_mvp/2026-07-09_03_cmd_before_arm_not_armed_error.png) | CMD before ARM rejected |
| EV-IMG-04 | [`../../assets/screenshots/uart_mvp/2026-07-09_04_arm_ack_state_armed.png`](../../assets/screenshots/uart_mvp/2026-07-09_04_arm_ack_state_armed.png) | ARM ACK and ARMED state |
| EV-IMG-05 | [`../../assets/screenshots/uart_mvp/2026-07-09_05_valid_cmd_ack_armed.png`](../../assets/screenshots/uart_mvp/2026-07-09_05_valid_cmd_ack_armed.png) | valid CMD ACK and velocity reflected |
| EV-IMG-06 | [`../../assets/screenshots/uart_mvp/2026-07-09_06_cmd_timeout_output_zero.png`](../../assets/screenshots/uart_mvp/2026-07-09_06_cmd_timeout_output_zero.png) | timeout output zero |
| EV-IMG-07 | [`../../assets/screenshots/uart_mvp/2026-07-09_07_bad_range_out_of_range_error.png`](../../assets/screenshots/uart_mvp/2026-07-09_07_bad_range_out_of_range_error.png) | velocity range rejection |
| EV-IMG-08 | [`../../assets/screenshots/uart_mvp/2026-07-09_08_disarm_ack_state_disarmed.png`](../../assets/screenshots/uart_mvp/2026-07-09_08_disarm_ack_state_disarmed.png) | DISARM ACK and DISARMED state |

## Visual Evidence

### EV-IMG-01: connected idle + periodic TEL

![EV-IMG-01 connected idle](../../assets/screenshots/uart_mvp/2026-07-09_01_web_dashboard_connected_idle.png)

### EV-IMG-02: PING/PONG response

![EV-IMG-02 ping pong](../../assets/screenshots/uart_mvp/2026-07-09_02_ping_pong_response.png)

### EV-IMG-03: CMD before ARM rejected

![EV-IMG-03 not armed](../../assets/screenshots/uart_mvp/2026-07-09_03_cmd_before_arm_not_armed_error.png)

### EV-IMG-04: ARM ACK and ARMED state

![EV-IMG-04 armed](../../assets/screenshots/uart_mvp/2026-07-09_04_arm_ack_state_armed.png)

### EV-IMG-05: valid CMD ACK and velocity reflected

![EV-IMG-05 valid cmd](../../assets/screenshots/uart_mvp/2026-07-09_05_valid_cmd_ack_armed.png)

### EV-IMG-06: timeout output zero

![EV-IMG-06 timeout zero](../../assets/screenshots/uart_mvp/2026-07-09_06_cmd_timeout_output_zero.png)

### EV-IMG-07: bad range rejected

![EV-IMG-07 bad range](../../assets/screenshots/uart_mvp/2026-07-09_07_bad_range_out_of_range_error.png)

### EV-IMG-08: DISARM ACK and DISARMED state

![EV-IMG-08 disarmed](../../assets/screenshots/uart_mvp/2026-07-09_08_disarm_ack_state_disarmed.png)

## Matrix

| Requirement | Test Method | Evidence | Result | Notes |
| --- | --- | --- | --- | --- |
| REQ-UART-001 | Web dashboard connect 후 periodic `TEL` 확인 | EV-IMG-01, EV-CSV-20260709 | PASS | `CONNECTED`, `TEL,state=DISARMED` 반복 수신 |
| REQ-UART-002 | `PING,seq=1` 전송 후 `PONG,seq=1` 확인 | EV-IMG-02, EV-CSV-20260709 | PASS | CSV에 TX `PING,seq=1`, RX `PONG,seq=1` 존재 |
| REQ-UART-003 | `ARM`, valid `CMD`, `DISARM` 각각 ACK 확인 | EV-IMG-04, EV-IMG-05, EV-IMG-08, EV-CSV-20260709 | PASS | `ACK,type=ARM`, `ACK,type=CMD`, `ACK,type=DISARM` 확인 |
| REQ-UART-004 | invalid command에 대해 ERR 확인 | EV-IMG-03, EV-IMG-07, EV-CSV-20260709 | PASS | `NOT_ARMED`, `OUT_OF_RANGE`, `TIMEOUT_OUT_OF_RANGE` 확인 |
| REQ-SAFE-001 | DISARMED 상태에서 `CMD` 전송 | EV-IMG-03, EV-CSV-20260709 | PASS | `ERR,seq=2,type=CMD,code=NOT_ARMED` |
| REQ-SAFE-002 | `ARM,seq=3` 전송 | EV-IMG-04, EV-CSV-20260709 | PASS | `ACK,seq=3,type=ARM`, 이후 `TEL,state=ARMED` |
| REQ-SAFE-003 | ARMED 상태에서 `CMD,seq=20,vx_mmps=50,w_mradps=0,timeout_ms=500` 전송 | EV-IMG-05, EV-CSV-20260709 | PASS | `ACK,seq=20,type=CMD`, 이후 `TEL,last_seq=20,vx_mmps=50` |
| REQ-SAFE-004 | valid `CMD` 후 추가 command 없이 timeout 대기 | EV-IMG-06, EV-CSV-20260709 | PARTIAL — historical timeout-zero only | 2026-07-09 증거는 seq 20 기준 `vx_mmps=50` -> `vx_mmps=0`만 확인했다. 새 요구사항의 `DISARMED`, CMD-only 거부와 ARM+CMD 복구는 P-03 target runtime pending |
| REQ-SAFE-005 | `CMD`에 `vx_mmps=9999` 전송 | EV-IMG-07, EV-CSV-20260709 | PASS | `ERR,seq=25,type=CMD,code=OUT_OF_RANGE` |
| REQ-SAFE-006 | `CMD`에 `timeout_ms=3000` 전송 | EV-CSV-20260709 | PASS | `ERR,code=TIMEOUT_OUT_OF_RANGE`; 스크린샷은 별도 저장하지 않음 |
| REQ-SAFE-007 | `DISARM,seq=26` 전송 | EV-IMG-08, EV-CSV-20260709 | PASS | `ACK,seq=26,type=DISARM`, 이후 `TEL,state=DISARMED` |

## CSV Evidence Highlights

검증 세션 CSV에서 확인한 주요 이벤트:

```text
TX PING,seq=1
RX PONG,seq=1,t_ms=497650

TX CMD,seq=2,vx_mmps=0,w_mradps=0,timeout_ms=300
RX ERR,seq=2,type=CMD,code=NOT_ARMED

TX ARM,seq=3
RX ACK,seq=3,type=ARM

TX CMD,seq=20,vx_mmps=50,w_mradps=0,timeout_ms=500
RX ACK,seq=20,type=CMD
RX TEL,...last_seq=20,vx_mmps=50...
RX TEL,...last_seq=20,vx_mmps=0...

TX CMD,seq=25,vx_mmps=9999,w_mradps=0,timeout_ms=300
RX ERR,seq=25,type=CMD,code=OUT_OF_RANGE

TX DISARM,seq=26
RX ACK,seq=26,type=DISARM
RX TEL,...state=DISARMED,last_seq=26,vx_mmps=0,w_mradps=0...
```

## Residual Risk

- `LAST CODE` display는 마지막 error code를 유지하므로 정상 ACK 화면에서도 이전 error가 남아 보일 수 있다. 이는 firmware behavior라기보다 dashboard display policy에 가깝다.
- CSV에는 periodic `TEL`이 많이 포함되어 파일 크기가 커진다. 이후에는 test session 단위로 log trimming 또는 summary export를 추가할 수 있다.
- 이번 검증은 motor output 없이 command variable과 telemetry만 확인했다. 실제 PWM/DIR 출력 검증은 별도 hardware validation에서 수행해야 한다.
