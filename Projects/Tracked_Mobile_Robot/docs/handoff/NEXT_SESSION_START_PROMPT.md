# Next Session Start Prompt

새 Codex 대화창에서 작업을 이어갈 때 아래 내용을 그대로 붙여넣는다.

```text
Tracked_Mobile_Robot 프로젝트를 이어서 진행한다.

먼저 다음 파일을 읽고 현재 상태를 파악해라.

1. Projects/Tracked_Mobile_Robot/README.md
2. Projects/Tracked_Mobile_Robot/PROJECT_MEMORY.md
3. Projects/Tracked_Mobile_Robot/AGENTS.md
4. Projects/Tracked_Mobile_Robot/docs/handoff/README.md
5. Projects/Tracked_Mobile_Robot/docs/progress/2026-08-03_progress.md
6. Projects/Tracked_Mobile_Robot/docs/handoff/2026-08-03_uart_strict_parser_regression_handoff.md
7. Projects/Tracked_Mobile_Robot/docs/verification/08_ESP32_STM32_UART_Strict_Parser_Normal_Sequence_Test_Report_2026-08-03_ko.md
8. Projects/Tracked_Mobile_Robot/docs/verification/07_STM32_Motor_Output_Waveform_and_Direction_Timing_Test_Report_2026-08-03_ko.md
9. Projects/Tracked_Mobile_Robot/02_Hardware_Validation/09_Motor_Output_Waveform_and_Shutdown_Latency_Test.md
10. Projects/Tracked_Mobile_Robot/docs/progress/2026-07-31_progress.md
11. Projects/Tracked_Mobile_Robot/docs/handoff/2026-07-28_kicad_reva_wiring_handoff.md
12. Projects/Tracked_Mobile_Robot/09_Electrical_Design/README.md
13. Projects/Tracked_Mobile_Robot/02_Hardware_Validation/04_Encoder_Signal_Safety_Test.md
14. Projects/Tracked_Mobile_Robot/assets/captures/logic_analyzer/README.md
15. Projects/Tracked_Mobile_Robot/docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md
16. Projects/Tracked_Mobile_Robot/docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md
17. Projects/Tracked_Mobile_Robot/01_System_Architecture/21_Physical_EStop_Architecture_ko.md
18. Projects/Tracked_Mobile_Robot/docs/verification/06_Physical_EStop_Requirements_and_Verification_Plan_ko.md
19. Projects/Tracked_Mobile_Robot/03_Firmware/tests/README.md
20. Projects/Tracked_Mobile_Robot/03_Firmware/tools/README.md

현재 상태:

- ESP32-S3 ESP-IDF v6.0.2 환경 bring-up은 완료됐다.
- ESP32 project는 Projects/Tracked_Mobile_Robot/03_Firmware/esp32_uart_bridge 이다.
- ESP32 target은 esp32s3, serial port는 COM4, OpenOCD config는 board/esp32s3-builtin.cfg 이다.
- ESP32 hello_world build, flash, monitor는 성공했다.
- ESP32 bring-up evidence는 assets/screenshots/esp32_uart_bridge 와 002_ESP32_IDF_Environment_Bringup_ko.md 에 있다.
- ESP32 UART1은 GPIO17 TX / GPIO18 RX / 115200 8N1이다.
- GPIO17-GPIO18 loopback은 PASS했다.
- ESP32 GPIO17 TX -> STM32 PA10 RX, ESP32 GPIO18 RX <- STM32 PA9 TX, GND 공통으로 연결했다.
- ESP32가 PING을 보내고 STM32 PONG을 받는 왕복 통신은 PASS했다.
- ESP32가 STM32 TEL telemetry를 수신하는 경로도 PASS했다.
- ESP32 parser는 TEL, PONG, ACK, ERR, UNKNOWN을 구분한다.
- TEL의 t_ms, state, last_seq, vx_mmps, w_mradps, left_cps, right_cps, err 구조화는 실제 STM32 link에서 PASS했다.
- structured TEL parser evidence는 assets/screenshots/esp32_uart_bridge/2026-07-18_13_esp32_structured_tel_parser_success.png 이다.
- ESP32 scripted CMD before ARM -> ARM -> valid CMD -> invalid CMD -> DISARM sequence는 PASS했다.
- STM32 NOT_ARMED, ARM/CMD ACK, OUT_OF_RANGE, DISARM ACK와 최종 DISARMED telemetry를 확인했다.
- valid CMD 이후 약 300 ms 뒤 vx=0, w=0으로 복귀하는 STM32 timeout-zero를 확인했다.
- bridge 최종 evidence는 assets/screenshots/esp32_uart_bridge/2026-07-20_esp32_stm32_scripted_safety_sequence_pass.png 와 assets/logs/esp32_uart_bridge/2026-07-20_scripted_safety_sequence_pass.txt 이다.
- ESP32-STM32 board-only UART bridge의 2026-07-20 historical baseline은 완료됐다.
- 2026-07-31 strict-parser board-only 회귀에서 stale ARMED session, startup PING 유실과 ESP reset 중 UART desync를 관찰했다. Parser는 오염 frame을 fail-closed로 버리고 다음 frame부터 복구했다.
- 2026-08-03에는 `500 ms settle -> LF -> 100 ms -> PING` controlled preamble로 current parser의 PING/PONG, NOT_ARMED, ARM/valid CMD, timeout-zero, OUT_OF_RANGE와 final DISARMED를 다시 PASS했다. Raw evidence는 `assets/logs/esp32_uart_bridge/2026-08-03_strict_parser_normal_sequence_pass.txt`다.
- 이 결과는 정상 시퀀스 하위 시험 PASS다. Matching `DISARM ACK`와 bounded-retry `PING/PONG`을 확인하는 startup state machine, handshake 실패 시 ARM/CMD 차단과 malformed-frame fail-closed/recovery injection은 남아 있어 current strict-parser release는 `PARTIAL`이다.
- 현재 ESP32 source의 `BRIDGE_SCRIPTED_TEST_ENABLED`는 `0U`다. 다만 마지막 ESP32 board flash는 test macro `1U` image일 수 있으므로 다음 safe reflash 전까지 두 board USB와 battery/MDD10A power를 분리한다.
- STM32 `.ioc` init list는 `MX_TIM5_Init`를 명시적으로 보존한다.
- 2026-07-30 laptop-only preflight에서 firmware safety contract `12/12`와 isolated STM32 Debug + ESP32-S3 clean build가 통과했다. 이 결과는 board flash/runtime 또는 전기 파형 검증이 아니다.
- STM32 project는 Projects/Tracked_Mobile_Robot/03_Firmware/stm32_uart_mvp 이다.
- STM32 NUCLEO-F446RE는 ESP bridge용으로 USART1 PA9 TX / PA10 RX를 사용한다.
- STM32 ST-LINK VCP는 COM3, ESP32-S3 serial port는 COM4로 구분한다.
- STM32 protocol path는 uart_mvp_init(&huart1) 사용과 실제 PING/PONG/TEL runtime을 확인했다.
- STM32 motor bench mapping은 PB6/TIM4_CH1 -> PWM1, PC8 -> DIR1, PB7/TIM4_CH2 -> PWM2, PC9 -> DIR2, common GND다.
- STM32 pin-only DMM과 MDD10A powered/no-motor 6-step LED routing은 2026-07-26에 통과했고, 2026-07-29 direction-change 수정 뒤 같은 sequence와 final all-off를 재통과했다. Test macro는 다시 0U다.
- 현재 motor-output source는 `PWM zero -> 1 ms PWM-zero settle -> DIR -> 1 ms post-DIR settle -> PWM` 순서다. 2026-08-03 로직 분석기에서 두 PWM은 각각 약 `20.1005 kHz`, duty 약 `10.05%`였고, DIR 변경 전후 PWM-zero 간격은 채널별 모두 `1 ms` 이상으로 PASS했다.
- 2026-07-29 motor-disconnected 10%-limited UART hook에서 active timeout과 별도 active `DISARM`이 MDD10A M1A/M2A LED를 all-off로 만드는 기능 시험을 통과했다. Hook은 `0U`로 복구했고 default scripted sequence 전체 all-off도 확인했다.
- 2026-07-30 motor-disconnected software fault-injection에서 M1A/M2A limited active 뒤 `Error_Handler()`를 주입했다. All motor LEDs off, `PB6/PB7/PC8/PC9=0 V`, reset 전 B1 재활성화 차단을 확인했다. 두 test macro는 `0U`로 복구했고 B1 무출력을 재확인했다.
- 2026-08-03 raw `.sr`/`.pvs`와 측정 screenshot은 STM32 핀 파형과 방향 전환 timing 증거다. Active DISARM/timeout/software-fault shutdown latency, physical E-stop, production velocity-to-PWM mapping과 실제 motor stop은 아직 증명하지 않는다.
- 두 encoder motor는 MG540-A/B로 식별하며 encoder-side mapping은 MG540-A=motor A=vehicle right/TIM5, MG540-B=motor B=vehicle left/TIM3로 확정했다. MDD10A powered channel-to-side mapping은 아직 미확정이다.
- MG540-A raw encoder A/B는 shaft 위치에 따라 약 0/5 V였다. Raw direct STM32 연결은 금지한다.
- 최종 motor-off conditioning은 각 A/B에서 `1 kΩ series -> STM32 input node`, 그 node에서 `15 kΩ -> common GND`다. STM32 GND, encoder GND와 XL4015 OUT-를 공통으로 묶는다.
- PB4/PB5 분리 상태의 conditioned HIGH는 MG540-A A/B 3.06 V, MG540-B A/B 3.06~3.07 V였다.
- TIM3 `PB4/CH1=A`, `PB5/CH2=B`, encoder TI12 x4 조건에서 두 motor의 motor-off hand-count를 순차 검증했다.
- 2026-07-26 1회전 시험 당시 output-shaft-end view 기준 MG540-A는 CW +1560, CCW -1560~-1570, MG540-B는 CW +1562, CCW -1560이었고 `1560 counts/output rev`를 잠정값으로 사용했다.
- 저장 raw log는 MG540-A의 부분 양방향 증감만 담고 있으며, 전체 1회전 수치와 MG540-B 결과는 같은 session의 별도 작업자 기록이다.
- 2026-07-30 방향별 50회전 손보정에서 MG540-A absolute count는 `77,998 / 78,001`, MG540-B는 `78,000 / 78,000`이었다. `1559.96~1560.02 counts/output rev`로 수렴했으므로 현재 firmware 상수는 `1560`으로 확정했다. 이 작업자 측정은 아래 mRPM raw log와 별도 증거다.
- TIM5 PA0/PA1과 TIM3 PB4/PB5에 두 encoder를 동시에 연결한 motor-off 독립 count/sign은 통과했다.
- 2026-07-29 production `encoder_speed` module에서 TIM3 16-bit/TIM5 32-bit modular delta, wrap-safe int64 누적 count와 nominal 100 ms counts/s를 구현했다. Synthetic wrap, stationary와 dual hand-rotation bench log를 통과했다.
- 2026-07-30 signed CPS -> mRPM conversion과 invalid/range self-test를 추가했다. `ENC_SELF_TEST,wrap=PASS,millirpm=PASS`와 305-row dual hand-rotation log에서 610 sample formula mismatch 0, direction mismatch 0과 stop-to-zero를 확인했다. mRPM은 USART2 bench field이고 production `TEL`은 CPS를 유지한다.
- 2026-07-29 end-to-end retest에서 MG540-A -> TIM5 -> `right_cps`, MG540-B -> TIM3 -> `left_cps`, output-shaft-end raw CW `+` / CCW `-`, inactive field zero를 production `TEL`과 ESP32 parser에서 확인했다.
- 2026-07-30 encoder-side vehicle mapping은 A=right/TIM5, B=left/TIM3로 확정했다. Right/A의 CW와 left/B의 CCW가 physical forward이므로 production CPS에서 TIM3/left만 부호 반전하고 TIM5/right는 유지한다. USART2 `ENC3/ENC5` bench log는 raw sign을 유지한다.
- Exact LOW/A-B phase timing, powered-motor noise, external tachometer 기준 RPM 정확도와 wheel-speed scale은 아직 미검증이다.
- KiCad 10.0 `Tracked_Mobile_Robot_Wiring_RevA` 기능 회로도 초안을 09_Electrical_Design에 보존했다.
- RevA에는 battery -> FUSE_TBD -> switch -> MDD10A/XL4015 x2 병렬 분배, MDD10A logic/output, dual encoder 1 kΩ + MCU-side 15 kΩ conditioning, XL4015 #2 encoder 5 V와 STM32–ESP32 UART를 기록했다.
- Dated ERC는 0 errors / 0 warnings이고 review PDF도 보존했다. 이는 물리 배선, 전류 용량, noise, footprint 또는 제조 적합성 검증이 아니다.
- XL4015 #1 출력 destination/USB backfeed, fuse rating, BNO085 power/I2C와 physical harness는 TBD다.
- 어댑터 플레이트 Rev A 외곽은 174 x 208.93379 mm이고, 제작 후보 재료는 아크릴 3T로 결정했다.
- 소형 체결 홀은 M3 여유 홀 후보인 지름 3.3 mm로 설계했다.
- 만능기판은 150 x 100 mm, 홀 배열은 55 x 37이다.
- XL4015 x2와 MDD10A는 상단 전력부, NUCLEO-F446RE와 ESP32-S3 및 GY-BNO085는 만능기판 영역에 배치했다.
- ESP32-S3는 USB 접근성을 위해 가로 방향을 유지하고, GY-BNO085는 차량 중심에 가깝게 배치했다.
- Rev A 2D 형상을 DXF, DWG, PDF로 내보내 release 폴더에 보존했다.
- A4 1:1 출력물을 실물 셰시와 대조했고 사용자가 적합 판정을 내렸다(USER-CONFIRMED PASS).
- 멀티메이커 450 x 300 mm 양식에 Rev A 벡터를 중앙 배치했다.
- 최종 주문용 PDF는 1페이지, 벡터 경로 39개, 래스터 이미지 0개, 텍스트 0개이다.
- 원본 Onshape PDF 대비 최종 주문 PDF의 형상 크기 차이는 X -0.001055 mm, Y -0.000840 mm로 검증됐다.
- 최종 주문 파일은 08_Mechanical_Design/releases/revA/2026-07-24_adapter_plate_revA_multimaker_order.pdf 이다.
- 멀티메이커 원본 작업 양식은 08_Mechanical_Design/references/vendor_templates 에 보존했다.
- 멀티메이커 사이트 업로드는 서버의 wp-content/uploads/2026/07 디렉터리 쓰기 권한 오류로 0%에서 실패했다.
- 따라서 현재 상태는 RELEASE FILES PREPARED / ORDER NOT SUBMITTED 이다.
- 최초 입력으로 사용한 R3 셰시 홀 패턴 DWG 원본은 08_Mechanical_Design/source/chassis 에 SHA-256과 함께 보존했다.
- 캡처의 Assembly 트리에 남은 빨간 참조 표시는 사용자 지시에 따라 이번 Rev A 2D 발주 범위에서 제외했다.
- mechanical-layout 증거는 assets/screenshots/mechanical_layout 에 있다.
- 체결 나사·스페이서의 최종 규격과 제작품 수령 후 실물 fit은 아직 검증하지 않았다.

중요 규칙:

- 작업 전 반드시 git status --short Projects/Tracked_Mobile_Robot 를 실행한다.
- 사용자 변경사항과 CubeMX generated changes를 되돌리지 않는다.
- STM32는 parser, safety gate, timeout owner, final drivetrain authority 이다.
- ESP32는 command source, relay, logger, future wireless bridge 후보이다.
- UART 연결은 TX/RX 교차, GND 공통이다.
- USB로 두 보드를 각각 전원 공급 중이면 5V/VBUS/VIN끼리는 연결하지 않는다.
- ESP-IDF monitor가 COM4를 점유하면 flash 전에 Ctrl+]로 monitor를 종료한다.
- main/hello_world_main.c는 사용자가 직접 학습하며 작성 중이므로 요청 없이 대신 완성하지 않는다.
- `BRIDGE_SCRIPTED_TEST_ENABLED`는 기본 `0U`다. Motor-disconnected controlled bench 외에는 활성화하지 않는다.
- CubeMX 재생성 뒤 TIM5 init 보존 여부와 static contract test를 먼저 확인한다.
- Raw encoder A/B를 STM32에 직접 연결하지 않는다. 제한 시험 조건은 채널별 `1 kΩ series + MCU-side 15 kΩ pull-down`, common GND와 motor power disconnected다.
- USART2 encoder 출력은 병행 검증용 bench logger이며 mRPM도 여기에서만 출력한다. 내부 count는 int64지만 newlib-nano `%lld` 제약 때문에 현재 짧은 bench log는 `(long)`/`%ld`를 사용한다. CPS는 production UART `TEL`에도 연결되어 ESP32 parser까지 PASS했다.
- 실제 motor test 전에는 active DISARM/timeout/software-fault shutdown latency와 physical E-stop gate를 확인한다. PB6/PB7 PWM과 exact direction timing 하위 게이트는 2026-08-03 PASS했다.
- XL4015 #1 candidate 5 V는 USB backfeed 정책이 확정되기 전 STM32/ESP32에 연결하지 않는다.
- KiCad의 `FUNCTIONAL` connector block은 관련 신호를 묶은 표기이며 물리적으로 연속된 header를 뜻하지 않는다.
- ERC PASS를 실물 배선, 전류 용량, noise, footprint 또는 제조 검증으로 확대 해석하지 않는다.
- Physical E-stop은 NC hardware motor-energy cut와 독립 3.3 V auxiliary sense의 두 경로로 설계한다. Release만으로 auto-arm/restart하지 않으며 direct-contact/contactor 선택, DC interrupt rating, sense pin, KiCad와 firmware는 아직 TBD다.

다음 목표:

1. MDD10A/Battery power OFF와 motor path 분리를 확인하고, ESP32/STM32의 네 test macro가 모두 `0U`인지 확인한다.
2. ESP32에 `500 ms settle -> newline sync -> DISARM/ACK bounded retry -> PING/PONG bounded retry` startup state machine을 구현한다. READY 전에는 ARM/CMD를 송신하지 않는다.
3. Motor power OFF에서 startup과 정상 scripted sequence를 다시 검증하고 raw log를 저장한다.
4. DISARMED 상태에서 malformed PING, field-order violation CMD, unknown frame을 주입하고 마지막 정상 PING/PONG 복구까지 확인한다.
5. UART 회귀가 끝나면 ESP test macro를 `0U`로 복구하고 contract test/clean build 뒤 safe ESP image를 재플래시한다.
6. Motor-disconnected 10%-limited 조건에서 active `DISARM`, command timeout, software-fault의 event-to-PWM inactive latency를 순서대로 측정한다.
7. Latency 시험 뒤 STM32 test hook을 모두 `0U`로 복구하고 tests/build/safe reflash를 수행한 다음, 외부 reset marker를 포함한 PB6/PC8/PB7/PC9 all-inactive boot 회귀를 캡처한다.
8. Board power/back-power 선행 조건과 Physical E-stop `T-ESTOP-001~006`을 닫는다.
9. 위 안전 gate 통과 뒤 first lifted/no-load motor test에서 MDD10A channel-to-side mapping, encoder false count/noise와 input filter를 확인한다.
10. 영구 만능기판·하네스는 KiCad schematic-to-hardware continuity review 후 조성한다.
11. 멀티메이커에 서버 업로드 오류를 알리고 아크릴 3T, 외곽 174 x 208.93379 mm, 지름 3.3 mm 홀, 1개 제작의 대체 제출·견적을 확인한다.
12. 주문 접수 시 order ID와 제출 revision을 기록한다.
13. 제작품 수령 후 `02_Hardware_Validation/08_Adapter_Plate_Fit_Check.md`로 실물 fit을 검증한다.

완료된 historical UART bridge와 current normal-sequence 하위 시험은 다시 구현하지 말고 evidence를 참조한다. 다음 세션의 첫 종료선은 아직 남은 response-gated startup과 malformed-frame recovery를 닫는 것이다.
```

## Minimal First Command

새 세션에서 실제 작업을 시작하기 전 아래 명령을 먼저 실행한다.

```powershell
git status --short Projects/Tracked_Mobile_Robot
```

## Firmware Preflight Commands

저장소 루트 `TIL`에서 실행한다.

```powershell
python -m unittest discover `
  -s Projects/Tracked_Mobile_Robot/03_Firmware/tests `
  -p "test_*.py" `
  -v

Push-Location Projects/Tracked_Mobile_Robot/03_Firmware/tools
.\Build-Firmware.ps1
Pop-Location
```
