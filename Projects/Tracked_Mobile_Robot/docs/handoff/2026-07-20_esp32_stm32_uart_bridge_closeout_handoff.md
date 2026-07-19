# ESP32-STM32 UART Bridge Closeout Handoff - 2026-07-20

## Current Checkpoint

ESP32-S3와 NUCLEO-F446RE 사이의 board-only UART bridge MVP는 PASS했다.

```text
ESP32 UART1 GPIO17/GPIO18
<-> STM32 USART1 PA10/PA9
<-> PING/PONG + ARM/CMD/DISARM + ACK/ERR/TEL
```

ESP32는 command source / relay / logger 역할을 수행하고, STM32는 parser, safety gate, command timeout, 최종 output authority를 유지한다.

## Completed

- ESP-IDF v6.0.2 build / flash / COM4 monitor
- ESP32 UART1 GPIO17/GPIO18 loopback
- ESP32 `PING` -> STM32 `PONG`
- STM32 `TEL` -> ESP32 relay
- `PONG`, `TEL`, `ACK`, `ERR`, `UNKNOWN` frame classification
- structured `TEL` parsing: `t_ms`, `state`, `last_seq`, `vx_mmps`, `w_mradps`, `err`
- common UART frame sender
- `ARM`, `CMD`, `DISARM` frame builders
- one-shot scripted safety sequence
- `NOT_ARMED`, valid command ACK, `OUT_OF_RANGE`, DISARM 검증
- valid CMD 이후 약 300 ms timeout-zero 검증

## Final Runtime Result

```text
CMD,seq=2 before ARM -> ERR,code=NOT_ARMED
ARM,seq=3            -> ACK,type=ARM -> TEL,state=ARMED
CMD,seq=4,vx=50      -> ACK,type=CMD -> TEL,vx=50 -> timeout -> vx=0
CMD,seq=5,vx=9999    -> ERR,code=OUT_OF_RANGE, last_seq=4 유지
DISARM,seq=6         -> ACK,type=DISARM -> TEL,state=DISARMED,vx=0,w=0
```

첫 실행은 STM32가 기존 `ARMED` 상태였기 때문에 `CMD before ARM` precondition을 만족하지 못했다. `DISARMED` 상태를 확인한 뒤 재실행한 최종 로그가 PASS evidence다.

## Evidence

- [`../../assets/screenshots/esp32_uart_bridge/2026-07-20_esp32_stm32_scripted_safety_sequence_pass.png`](../../assets/screenshots/esp32_uart_bridge/2026-07-20_esp32_stm32_scripted_safety_sequence_pass.png)
- [`../../assets/logs/esp32_uart_bridge/2026-07-20_scripted_safety_sequence_pass.txt`](../../assets/logs/esp32_uart_bridge/2026-07-20_scripted_safety_sequence_pass.txt)
- [`../progress/2026-07-20_progress.md`](../progress/2026-07-20_progress.md)
- [`../verification/04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md`](../verification/04_ESP32_STM32_UART_Bridge_Verification_Plan_ko.md)

## Preserved Baseline

- ESP32: `UART_NUM_1`, GPIO17 TX, GPIO18 RX, 115200 8N1
- STM32: USART1 PA9 TX, PA10 RX, `uart_mvp_init(&huart1)`
- wiring: TX/RX crossed, common GND
- USB로 두 보드를 각각 공급할 때 5V/VBUS/VIN끼리는 연결하지 않는다.
- `hello_world_main.c`는 사용자가 직접 타이핑하며 학습한 source이므로 이후에도 요청 없이 대체 작성하지 않는다.

## Next Concrete Start

UART bridge를 반복 구현하지 않는다. 다음 세션은 아래 순서로 시작한다.

1. `git status --short Projects/Tracked_Mobile_Robot`
2. `02_Hardware_Validation/03_MDD10A_Logic_Input_Test.md` 확인
3. STM32 PWM/DIR 후보 핀과 MDD10A channel mapping 확인
4. motor와 3S LiPo main power 없이 logic input test 준비
5. PWM/DIR logic 검증 후 UART command state와 output path 연결

## Not Yet Validated

- MDD10A PWM/DIR input
- actual DC motor motion
- encoder feedback
- UART command와 physical motor output 연결
- closed-loop speed control
- CAN / FreeRTOS / ROS 2 integration
