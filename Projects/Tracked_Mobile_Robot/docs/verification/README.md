# Verification Documentation

이 폴더는 Tracked Mobile Robot 프로젝트의 요구사항, 검증 항목, 테스트 증거를 연결해 두는 곳이다.

목표는 개인 프로젝트 규모에 맞는 경량 V-model을 적용하는 것이다. 즉, 큰 조직의 절차 문서를 흉내 내는 것이 아니라 다음 흐름을 작게라도 남긴다.

```text
요구사항
-> 구현 대상
-> 검증 방법
-> 실제 증거
-> 결과와 다음 조치
```

## Current Verification Scope

현재 검증 완료 범위는 PC-first UART MVP, ESP32 board-only UART bridge MVP와
motor-disconnected MDD10A/dual-encoder 하위 시험까지 확장됐다.

```text
PC Web Serial Dashboard
<-> ST-LINK Virtual COM Port
<-> STM32 USART2
<-> UART MVP parser / safety state machine

ESP32 USB Monitor
<-> ESP32-S3 UART1 GPIO17/GPIO18
<-> STM32 USART1 PA10/PA9
<-> PING/PONG/ARM/CMD/DISARM/ACK/ERR/TEL
```

ESP32 bridge는 2026-07-20 release baseline에서 loopback, `PING/PONG`, structured `TEL` parsing, scripted `CMD before ARM -> ARM -> valid CMD -> invalid CMD -> DISARM`, timeout-zero를 모두 PASS했다. 2026-08-03에는 current strict parser에서 `500 ms settle -> LF -> 100 ms -> PING` preamble을 사용한 controlled normal sequence도 다시 PASS했다. 다만 응답 확인형 startup handshake와 malformed-frame board injection은 아직 남아 있으므로, current strict-parser release 전체 판정은 `PARTIAL`이다.

2026-08-03 현재 부분 검증된 추가 범위:

- MDD10A powered/no-motor routing, direction, timeout/DISARM와 software fault shutdown
- STM32 pin-only PWM frequency/duty와 direction-change pre/post zero interval
- Dual encoder conditioned input, TIM3/TIM5 count, CPS/mRPM와 vehicle-frame sign
- Fused/switched LiPo input과 XL4015 bench load

아직 최종 검증에 포함하지 않은 것:

- 실제 DC motor 구동
- Active DISARM/timeout/software-fault shutdown edge latency
- Physical E-stop과 motor-connected stop
- Powered-motor encoder noise와 wheel-speed/odometry
- ROS 2 bridge

따라서 이 검증의 의미는 "로봇 전체가 움직였다"가 아니라, "STM32 하위 제어기가 command/telemetry protocol과 safety gate를 실제 보드에서 수행했다"이다.

## Documents

| Document | Purpose |
| --- | --- |
| [`01_UART_MVP_Requirements_ko.md`](01_UART_MVP_Requirements_ko.md) | UART MVP 요구사항과 acceptance criteria |
| [`02_UART_MVP_Verification_Matrix_ko.md`](02_UART_MVP_Verification_Matrix_ko.md) | 요구사항, 테스트 방법, 증거 파일, 결과 연결 |
| [`03_UART_MVP_Test_Report_2026-07-09_ko.md`](03_UART_MVP_Test_Report_2026-07-09_ko.md) | 2026-07-09 실제 STM32 + Web Serial 검증 리포트 |
| [`04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md`](04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md) | ESP32를 command source / telemetry relay로 붙이는 보드 단독 검증 계획 |
| [`05_Final_MVP_Requirements_and_Verification_Matrix_ko.md`](05_Final_MVP_Requirements_and_Verification_Matrix_ko.md) | 전원·기구·모터·엔코더·주행까지 확장한 최종 MVP 요구사항과 V-model 추적 매트릭스 |
| [`06_Physical_EStop_Requirements_and_Verification_Plan_ko.md`](06_Physical_EStop_Requirements_and_Verification_Plan_ko.md) | MCU와 독립적인 motor-energy 차단, fail-safe sense, latch/reset과 단계별 E-stop 검증 계획 |
| [`07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md`](07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md) | Logic analyzer로 확인한 boot inactive sampled interval, 양 채널 PWM frequency/duty와 direction settle 결과·한계 |
| [`08_ESP32_STM32_UART_Strict_Parser_Normal_Sequence_Test_Report_2026-08-03_ko.md`](08_ESP32_STM32_UART_Strict_Parser_Normal_Sequence_Test_Report_2026-08-03_ko.md) | Current strict parser의 controlled normal sequence PASS 결과와 startup/malformed 잔여 release gate |

## Evidence Files

주요 증거 파일:

| Evidence | Path |
| --- | --- |
| Web Serial screenshots | [`../../assets/screenshots/uart_mvp`](../../assets/screenshots/uart_mvp) |
| UART validation CSV | [`../../04_PC_Serial_Control/logs/2026-07-09_uart_mvp_validation_session.csv`](../../04_PC_Serial_Control/logs/2026-07-09_uart_mvp_validation_session.csv) |
| ESP32-STM32 UART bridge screenshots | [`../../assets/screenshots/esp32_uart_bridge`](../../assets/screenshots/esp32_uart_bridge) |
| ESP32-STM32 UART bridge raw logs | [`../../assets/logs/esp32_uart_bridge`](../../assets/logs/esp32_uart_bridge) |
| Encoder calibration, CPS/mRPM and vehicle-sign evidence | [`../../assets/logs/encoder`](../../assets/logs/encoder) |
| Motor-output fault evidence | [`../../assets/logs/motor_output`](../../assets/logs/motor_output) |
| Logic-analyzer raw/session captures | [`../../assets/captures/logic_analyzer`](../../assets/captures/logic_analyzer) |
| Logic-analyzer measurement screenshots | [`../../assets/screenshots/logic_analyzer`](../../assets/screenshots/logic_analyzer) |

## Result Summary

2026-08-03 기준 추가 하드웨어/firmware subtest:

- A=right/TIM5, B=left/TIM3 encoder-side vehicle mapping과 forward-positive production CPS subtest PASS
- 방향별 50회전 `1560 counts/output rev`, CPS-to-mRPM self-test와 dynamic calculation PASS
- Motor-disconnected software fault injection 뒤 MDD10A all-off, `PB6/PB7/PC8/PC9=0 V`와 reset 전 latch PASS
- Button output/fault test macro를 모두 `0U`로 복구한 뒤 B1 no-output regression PASS
- D0=DIR1, D1=PWM1, D2=DIR2, D3=PWM2 실제 mapping에서 양 PWM 20.1005 kHz, high 5.00 us, 약 10.05% PASS
- Direction-change PWM-zero interval은 CH1 pre/post 1.994/2.03875 ms, CH2 pre/post 1.54725/~2.040 ms로 모두 최소 1 ms PASS
- Current strict parser의 controlled normal sequence는 startup `PING/PONG`, `NOT_ARMED`, ARM/CMD ACK, timeout-zero, `OUT_OF_RANGE`, final DISARMED까지 PASS
- UART current release는 response-gated `DISARM/ACK -> PING/PONG` bounded-retry startup과 malformed-frame fail-closed/recovery injection이 남아 `PARTIAL`
- Active shutdown edge latency, reset-marker를 포함한 final hook-off boot capture, physical E-stop과 motor-connected stop은 계속 `PARTIAL/NOT TESTED`
- MDD10A powered channel 1/2와 실제 좌우 motor 대응은 아직 `PARTIAL`

2026-07-20 기준 ESP32-STM32 board-only UART bridge MVP는 다음 항목을 실제 보드에서 확인했다.

- `CMD before ARM` -> `ERR,code=NOT_ARMED`
- `ARM` -> `ACK,type=ARM`, `TEL,state=ARMED`
- valid `CMD` -> `ACK,type=CMD`, `TEL,vx_mmps=50`
- command timeout 이후 `vx_mmps=0`, `w_mradps=0`
- invalid range command -> `ERR,code=OUT_OF_RANGE`, 이전 `last_seq` 유지
- `DISARM` -> `ACK,type=DISARM`, `TEL,state=DISARMED`
- evidence: [`screenshot`](../../assets/screenshots/esp32_uart_bridge/2026-07-20_esp32_stm32_scripted_safety_sequence_pass.png), [`raw log`](../../assets/logs/esp32_uart_bridge/2026-07-20_scripted_safety_sequence_pass.txt)

2026-08-03 current strict-parser controlled run은 [`raw log`](../../assets/logs/esp32_uart_bridge/2026-08-03_strict_parser_normal_sequence_pass.txt)와 [test report](08_ESP32_STM32_UART_Strict_Parser_Normal_Sequence_Test_Report_2026-08-03_ko.md)로 보존했다. 이 시험의 fixed-delay preamble은 startup reliability의 최종 구현이 아니다. Release gate에는 explicit `DISARM`의 matching ACK, bounded-retry `PING/PONG`, handshake 실패 시 ARM/CMD 차단과 malformed-frame hardware injection이 남아 있다. RX desync는 오염 frame을 버리고 다음 line boundary에서 복구하지만 즉시 motor stop을 실행하지 않으며, 현재 최대 500 ms command timeout이 fallback이다.

2026-07-09 기준 PC-first UART MVP는 다음 항목을 실제 보드에서 확인했다.

- Web Serial dashboard와 ST-LINK VCP 연결
- periodic `TEL` 수신
- `PING` -> `PONG`
- `CMD` before `ARM` -> `ERR,code=NOT_ARMED`
- `ARM` -> `ACK,type=ARM`, `TEL,state=ARMED`
- valid `CMD` -> `ACK,type=CMD`
- command timeout 이후 `vx_mmps=0`, `w_mradps=0`
- invalid command range -> `ERR,code=OUT_OF_RANGE`
- invalid timeout range -> `ERR,code=TIMEOUT_OUT_OF_RANGE`
- `DISARM` -> `ACK,type=DISARM`, `TEL,state=DISARMED`

## Visual Summary

아래 이미지는 2026-07-09 검증 세션의 핵심 장면이다. 전체 8개 스크린샷은 [`03_UART_MVP_Test_Report_2026-07-09_ko.md`](03_UART_MVP_Test_Report_2026-07-09_ko.md)에 순서대로 포함되어 있다.

### 1. Connected idle

![Connected idle](../../assets/screenshots/uart_mvp/2026-07-09_01_web_dashboard_connected_idle.png)

### 2. CMD before ARM rejected

![CMD before ARM rejected](../../assets/screenshots/uart_mvp/2026-07-09_03_cmd_before_arm_not_armed_error.png)

### 3. Valid CMD accepted

![Valid CMD accepted](../../assets/screenshots/uart_mvp/2026-07-09_05_valid_cmd_ack_armed.png)

### 4. Timeout output zero

![Timeout output zero](../../assets/screenshots/uart_mvp/2026-07-09_06_cmd_timeout_output_zero.png)

## Next Verification Areas

다음 단계 검증 순서:

1. MDD10A/Battery power OFF에서 matching `DISARM ACK`와 bounded-retry `PING/PONG` startup state machine 검증
2. Malformed PING/CMD/unknown frame의 fail-closed 거부와 마지막 정상 PING/PONG 복구 검증
3. ESP test macro `0U`, contract test/clean build와 safe ESP32 image reflash/run
4. Active DISARM/timeout/software-fault event와 PWM edge를 함께 캡처해 실제 shutdown latency 계측
5. STM32 temporary hook `0U` 복구, tests/build/safe reflash와 external reset marker 포함 boot no-output 회귀 캡처
6. Physical E-stop architecture/component review 뒤 입력·latch·reset 구현 및 motor-disconnected 검증
7. Board power/back-power와 fabricated plate fit 검증
8. 첫 motor lifted/no-load low-duty 및 powered encoder noise 시험
9. Left/right drivetrain과 wheel travel/odometry 검증
10. Final fault/stop acceptance와 traceability audit
