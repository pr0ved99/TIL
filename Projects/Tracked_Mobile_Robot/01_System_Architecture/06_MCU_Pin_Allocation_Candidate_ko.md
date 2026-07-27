# STM32F446RE 핀 배정 후보

## 목적

이 문서는 NUCLEO-F446RE 기반 궤도형 모바일 로봇 MVP를 위한 첫 번째 핀 배정
후보를 제안한다.

이 문서는 전체 최종 핀맵이 아니다. 후보안에서 시작했으며, 현재 CubeMX와 bench에서
확인된 항목은 표와 각 절에 `validated`로 구분해 표시한다.

- STM32F446xC/E 데이터시트
- UM1724 STM32 Nucleo-64 boards user manual
- 이전 MCU 주변장치 분석 문서

아직 `Candidate`인 항목은 해당 펌웨어 구현 전에 CubeMX와 실제 NUCLEO-F446RE
회로도를 기준으로 검증해야 한다.

## 설계 목표

핀 배정은 다음 기능을 지원해야 한다.

- 좌/우 모터 PWM
- 좌/우 모터 direction GPIO
- 선택적 motor power gate 또는 brake GPIO 후보
- 좌/우 quadrature encoder A/B 입력
- PC command/debug serial link
- 선택적 ESP32-S3 serial link
- BNO08x IMU용 I2C
- 3S LiPo 배터리 전압 감시용 ADC
- 향후 CAN 확장
- SWD debugging 보존

## 사용한 자료

| 자료 | 사용 목적 |
| --- | --- |
| `assets/stm32f446mc.pdf` | STM32F446RE 패키지 핀과 alternate function 확인. |
| `UM1724 STM32 Nucleo-64 boards user manual` | NUCLEO-F446RE의 Arduino connector와 ST morpho connector 매핑 확인. |

UM1724에서 사용한 중요한 사실:

- NUCLEO-F446RE는 STM32F446RET6, LQFP64 package를 사용한다.
- Arduino D1/D0는 PA2/PA3이며 USART2_TX/USART2_RX에 대응한다.
- Arduino D15/D14는 PB8/PB9이며 I2C1_SCL/I2C1_SDA에 대응한다.
- Arduino A0/A1/A2/A3는 PA0/PA1/PA4/PB0 ADC 가능 핀에 대응한다.
- PA13과 PA14는 ST-LINK에 연결된 SWD signal을 공유하므로 개발 중 보존해야 한다.

## 배정 전략

첫 핀 배정은 다음 원칙을 따른다.

1. PA13/PA14는 SWD용으로 보존한다.
2. 첫 PC serial link에는 USART2 PA2/PA3를 사용한다.
3. BNO08x IMU에는 I2C1 PB8/PB9를 사용한다.
4. 양쪽 모터 엔코더에는 hardware timer encoder mode를 사용한다.
5. 모터 속도 제어에는 timer PWM output을 사용한다.
6. LiPo 전압은 저항 분배 후 ADC로 측정한다.
7. 가능하면 같은 timer를 PWM과 encoder에 동시에 쓰지 않는다.
8. Arduino header 또는 ST morpho header로 접근 가능한 핀을 우선한다.

## 1차 핀 후보표

| 로봇 기능 | MCU 핀 | 주변장치/기능 | 보드 접근 | 상태 |
| --- | --- | --- | --- | --- |
| PC serial TX | PA2 | USART2_TX | Arduino D1 / ST morpho CN10 pin 35 | Primary |
| PC serial RX | PA3 | USART2_RX | Arduino D0 / ST morpho CN10 pin 37 | Primary |
| IMU I2C SCL | PB8 | I2C1_SCL | Arduino D15 / ST morpho CN10 pin 3 | Primary |
| IMU I2C SDA | PB9 | I2C1_SDA | Arduino D14 / ST morpho CN10 pin 5 | Primary |
| 왼쪽 모터 PWM | PB6 | TIM4_CH1 | Arduino D10 / ST morpho CN10 pin 17 | Candidate |
| 오른쪽 모터 PWM | PB7 | TIM4_CH2 | ST morpho CN7 pin 21 | Candidate |
| Encoder channel 1 A | PB4 | TIM3_CH1 | Arduino D5 / ST morpho CN10 pin 27 | Motor-power-off validated |
| Encoder channel 1 B | PB5 | TIM3_CH2 | Arduino D4 / ST morpho CN10 pin 29 | Motor-power-off validated |
| Encoder channel 2 A | PA0 | TIM5_CH1 | Arduino A0 / ST morpho CN7 pin 28 | Motor-power-off validated |
| Encoder channel 2 B | PA1 | TIM5_CH2 | Arduino A1 / ST morpho CN7 pin 30 | Motor-power-off validated |
| 배터리 전압 ADC | PA4 | ADC12_IN4 | Arduino A2 / ST morpho CN7 pin 32 | Candidate |
| 왼쪽 모터 direction | PC8 | GPIO output | ST morpho CN10 pin 2 | Candidate |
| 오른쪽 모터 direction | PC9 | GPIO output | ST morpho CN10 pin 1 | Candidate |
| 왼쪽 선택적 power gate/brake | PC6 | GPIO output | ST morpho CN10 pin 4 | Optional |
| 오른쪽 선택적 power gate/brake | PC5 | GPIO output | ST morpho CN10 pin 6 | Optional |
| 선택적 ESP32 TX | PA9 | USART1_TX | Arduino D8 / ST morpho CN10 pin 21 | Reserve |
| 선택적 ESP32 RX | PA10 | USART1_RX | Arduino D2 / ST morpho CN10 pin 33 | Reserve |
| 향후 CAN RX | PA11 | CAN1_RX | ST morpho CN10 pin 14 | Reserve |
| 향후 CAN TX | PA12 | CAN1_TX | ST morpho CN10 pin 12 | Reserve |
| SWDIO | PA13 | SWDIO | ST-LINK / ST morpho CN7 pin 13 | Preserve |
| SWCLK | PA14 | SWCLK | ST-LINK / ST morpho CN7 pin 15 | Preserve |

## 하위 시스템별 근거

### PC Serial Link

PA2와 PA3는 USART2에 배정한다. UM1724에서 이 핀들은 Arduino D1/D0와
USART2_TX/USART2_RX로 매핑되어 있다.

용도:

- PC command input
- Debug log output
- 초기 serial protocol 검증

위험:

- Solder bridge 설정과 ST-LINK virtual COM routing에 따라 USART2가 이미 onboard
  ST-LINK 경로에 연결되어 있을 수 있다.

확인:

- 간단한 UART echo test로 USART2 PA2/PA3 동작을 확인한다.

### IMU I2C

PB8/PB9는 I2C1_SCL/I2C1_SDA에 배정한다. UM1724에서 이 핀들은 Arduino D15/D14,
즉 일반적인 Arduino I2C 핀으로 매핑되어 있다.

용도:

- BNO08x IMU 첫 interface 후보

위험:

- I2C는 배선 길이와 모터 noise에 민감하다.

확인:

- Pull-up 전압과 I2C bus 안정성을 100 kHz 또는 400 kHz에서 확인한다.

### Motor PWM

PB6/PB7은 TIM4_CH1/TIM4_CH2에 배정한다.

이유:

- 두 핀이 같은 timer의 channel이다.
- 좌/우 모터에 같은 PWM frequency와 resolution을 설정하기 쉽다.
- PB6은 Arduino D10과 ST morpho에서 접근 가능하다.
- PB7은 ST morpho에서 접근 가능하다.

위험:

- PB6은 많은 STM32 설계에서 I2C1 후보이기도 하다. 하지만 이 배정에서는
  I2C를 PB8/PB9로 사용하므로 PB6은 TIM4로 남길 수 있다.

확인:

- CubeMX에서 TIM4_CH1과 TIM4_CH2가 충돌 없이 설정되는지 확인한다.

### Encoders

첫 번째 encoder input은 PB4/PB5의 TIM3_CH1/TIM3_CH2를 사용한다.

두 번째 encoder input 후보는 PA0/PA1의 TIM5_CH1/TIM5_CH2다.

2026-07-26 motor-power-off hand-rotation 시험에서 `PB4 = TIM3_CH1/A`,
`PB5 = TIM3_CH2/B`, `TIM_ENCODERMODE_TI12` x4 quadrature 구성을
MG540-A/B에 순차 적용해 count 증감과 정지 안정성을 확인했다. 이 결과는
TIM3 bench input을 검증한 것이며 차량 left/right assignment를 확정하지 않는다.

시험한 각 A/B 입력은 다음 조건을 사용했다.

```text
encoder signal -> 1 kΩ series -> MCU input node
MCU input node -> 15 kΩ -> common GND
```

이유:

- Encoder mode는 보통 같은 timer의 CH1과 CH2가 필요하다.
- TIM3과 TIM5는 full-featured general-purpose timer다.
- TIM5는 32-bit라 encoder counting에 유리하다.
- PB4/PB5와 PA0/PA1은 보드 header에서 접근 가능하다.

위험:

- PB4/PB5는 일부 STM32 설정에서 debug/JTAG 관련 이력이 있을 수 있다.
  SWD 자체는 주로 PA13/PA14를 사용하지만, CubeMX에서 반드시 확인해야 한다.
- PA0/PA1은 편리한 ADC 핀이기도 하므로, encoder에 배정하면 배터리 전압 측정은 PA4로 이동한다.

확인:

- `PASS`: PB4/PB5에서 TIM3 TI12 x4 encoder mode motor-power-off 확인
- `PENDING`: PA0/PA1에서 TIM5 encoder mode 확인
- STM32에 연결하기 전에 encoder signal voltage 확인

### Battery Voltage ADC

PA4는 ADC12_IN4에 배정한다.

이유:

- PA0/PA1은 오른쪽 encoder 후보로 예약한다.
- PA4는 Arduino A2로 접근 가능하고 ADC 기능이 있다.

중요 규칙:

- 3S LiPo는 절대 PA4에 직접 연결하면 안 된다.
- 저항 분배 회로가 필수다.

확인:

- 최대 배터리 전압에서도 ADC 입력 범위 아래가 되도록 divider 값을 정한다.
- STM32에 연결하기 전에 멀티미터로 분압 전압을 측정한다.

### Motor Direction and Optional Power Gate GPIO

PC8, PC9를 MDD10A direction GPIO output으로 배정한다. PC6, PC5는 MDD10A 기본
logic input에는 필요하지 않지만, 나중에 별도 motor power gate, brake, relay, interlock 회로를
추가할 때를 위한 optional GPIO 후보로 남긴다.

이유:

- 이 핀들은 ST morpho에서 접근 가능하다.
- 첫 serial, I2C, encoder, PWM, ADC, SWD 배정과 충돌하지 않는다.
- MDD10A는 motor당 `PWM + DIR` 구조이므로 첫 MVP에는 PWM 2개와 DIR GPIO 2개면 충분하다.

안전 요구사항:

- Motor DIR pin은 PWM이 0인 상태에서만 방향 전환되도록 firmware에서 강제한다.
- Optional power gate/brake pin을 실제 회로에 연결한다면 reset 중 안전한 off 상태가 되어야 한다.
- 회로 요구사항에 맞춰 외부 pull-down 또는 pull-up 저항을 사용한다.

확인:

- Motor driver input logic level 확인
- STM32 reset 또는 boot 중 PWM output이 0 상태인지 확인

### Optional ESP32 Serial

PA9/PA10은 USART1_TX/USART1_RX 후보로 reserve한다.

이유:

- USART1은 ESP32-S3와 연결할 수 있는 깔끔한 optional serial link다.
- PC serial MVP가 동작한 뒤 추가하면 된다.

확인:

- STM32와 ESP32-S3의 3.3 V UART logic 호환성 확인
- 공통 GND 연결

### Future CAN

PA11/PA12는 CAN1_RX/CAN1_TX 후보로 reserve한다.

이유:

- 첫 UART/I2C/PWM/ADC 배정을 건드리지 않고 향후 CAN 경로를 남길 수 있다.

중요:

- CAN transceiver가 필요하다.
- CAN bus termination은 별도로 설계해야 한다.

## 충돌 검토

| 자원 | 충돌 상태 |
| --- | --- |
| USART2 PA2/PA3 | TIM2/TIM5 CH3/CH4 대체 기능과 겹치지만 이번 배정에서는 사용하지 않는다. |
| I2C1 PB8/PB9 | TIM4_CH3/CH4 대체 기능과 겹치지만 PWM은 TIM4_CH1/CH2를 사용한다. |
| TIM4 PB6/PB7 PWM | PB6은 I2C1_SCL 또는 USART1_TX 후보이기도 하지만 이번 배정에서는 사용하지 않는다. |
| TIM3 PB4/PB5 encoder | CubeMX 구성과 motor-power-off hand rotation에서 TI12 x4 동작을 확인했다. SWD는 PA13/PA14에 유지한다. |
| TIM5 PA0/PA1 encoder | A0/A1 ADC 가능 핀을 사용한다. TI12 motor-off hand-count와 TIM3 동시 독립 동작을 확인했다. |
| PA4 ADC | USART2_CK/SPI 기능도 있지만 이번 배정에서는 필요 없다. |
| PA13/PA14 | SWD용으로 보존하고 로봇 기능에 배정하지 않는다. |

## 검증 체크리스트

현재 검증 상태:

1. `[x]` STM32F446RETx 기준 CubeMX project 생성
2. `[x]` USART2 PA2/PA3 활성화와 PC UART 사용
3. `[ ]` I2C1 PB8/PB9 활성화와 BNO08x 확인
4. `[x]` TIM4 PWM PB6/PB7 활성화와 static motor-output 시험
5. `[x]` TIM3 encoder mode PB4/PB5 활성화와 motor-off hand-count
6. `[x]` TIM5 encoder mode PA0/PA1 활성화와 두 번째 channel 시험
7. `[ ]` PA4 ADC 활성화와 divider 시험
8. `[x]` PC8/PC9 MDD10A DIR GPIO 설정과 static routing 시험
9. `[ ]` 필요 시 PC6/PC5 optional power gate/brake 회로 결정
10. `[x]` PA13/PA14 SWD 유지
11. `[ ]` 남은 후보까지 포함한 최종 warning/pin-conflict review
12. `[x]` 현재 검증 범위의 `.ioc` 생성 및 Git 추적

벤치 검증 순서:

1. GPIO output toggle test
2. USART2 echo test
3. I2C scan 또는 BNO08x identity read
4. PWM output 측정
5. 손으로 모터를 돌리며 encoder count test
6. 배터리 대신 bench voltage로 ADC divider 측정
7. 모터 전원은 분리한 상태에서 MDD10A PWM/DIR logic safety test

## 1차 결정

이 후보안의 USART/PWM/DIR/TIM3/TIM5 범위는 CubeMX와 제한 bench 시험까지 진행했고,
I2C1/ADC와 차량 최종 mapping은 아직 후보 상태다.

가장 중요한 설계 선택:

- PC serial: USART2 PA2/PA3
- IMU: I2C1 PB8/PB9
- 좌/우 PWM: TIM4 PB6/PB7
- 엔코더: TIM3 PB4/PB5, TIM5 PA0/PA1
- 배터리 전압 ADC: PA4
- SWD: PA13/PA14 보존

## 다음 단계

다음 단계는 남은 후보를 순서대로 검증하는 것이다.

1. TIM3/TIM5 count sampling을 wrap-safe delta와 speed module로 분리한다.
2. I2C1 `PB8/PB9`와 PA4 ADC가 기존 확정 핀과 충돌하지 않는지 CubeMX에서 확인한다.
3. 각 검증 결과와 `.ioc`를 함께 업데이트한다.
4. 차량 장착 후 encoder channel left/right와 vehicle-forward sign을 확정한다.
5. 탈락한 후보는 decision log에 남긴다.
