# STM32F446RE 통신 및 I/O 주변장치 분석

## 목적

이 문서는 궤도형 모바일 로봇 프로젝트를 위해 STM32F446xC/E 데이터시트의
통신, GPIO, ADC, 디버그 관련 주변장치를 분석한다.

범위:

- Section 3.22: I2C
- Section 3.23: USART/UART
- Section 3.24: SPI
- Section 3.32: bxCAN
- Section 3.36: GPIO
- Section 3.37: ADC
- Section 3.40: SWJ-DP

목표는 STM32F446RE가 BNO08x IMU, PC, ESP32-S3, 모터 드라이버, 배터리 감시
회로, 향후 CAN 확장과 어떻게 연결될 수 있는지 판단하는 것이다.

## 1. 프로젝트 I/O 요구사항

초기 궤도 로봇 MVP에는 다음 MCU 인터페이스가 필요하다.

| 로봇 기능 | 예상 MCU 주변장치 |
| --- | --- |
| PC 명령과 debug log | USART/UART 또는 ST-LINK virtual COM port 경로 |
| ESP32-S3 보조 컨트롤러 연결 | USART/UART |
| BNO08x IMU | I2C 우선, SPI/UART 대안 |
| 모터 드라이버 방향/enable/brake | GPIO |
| 모터 속도 명령 | Timer PWM, 타이머 문서에서 배정 |
| 엔코더 입력 | Timer encoder mode, 타이머 문서에서 배정 |
| 3S LiPo 전압 감시 | 저항 분배 후 ADC |
| 향후 견고한 로봇 내부 버스 | bxCAN + 외부 CAN transceiver |
| 펌웨어 업로드/디버깅 | ST-LINK를 통한 SWD |

## 2. I2C

I2C는 SCL과 SDA 두 선을 사용하는 직렬 버스다. 센서 연결에 자주 쓰인다.

데이터시트 핵심:

- I2C bus interface 4개
- Multimaster와 slave mode 지원
- I2C 3개는 standard mode 최대 100 kHz, fast mode 최대 400 kHz 지원
- I2C 1개는 standard, fast, fast mode plus 최대 1 MHz 지원
- 7-bit, 10-bit addressing 지원
- Slave mode에서 7-bit dual addressing 지원
- Hardware CRC generation/verification
- DMA 지원
- SMBus 2.0 / PMBus 지원
- Programmable analog/digital noise filter 지원

### 프로젝트 용도

첫 번째 후보 용도는 BNO08x IMU 연결이다.

장점:

- 배선이 단순하다: SCL, SDA, 전원, GND
- IMU 하나를 연결하기에 interface 수량이 충분하다
- Noise filter 지원이 실제 배선 안정성에 도움이 될 수 있다

위험:

- I2C는 pull-up 저항, 선 길이, capacitance, noise에 민감하다.
- 모터 배선과 스위칭 noise가 센서 통신을 방해할 수 있다.
- I2C는 shared bus라 불안정한 장치 하나가 bus 전체에 영향을 줄 수 있다.

설계 메모:

- I2C 선은 짧게 유지한다.
- I2C 배선은 모터 전원선과 떨어뜨린다.
- 올바른 logic voltage로 pull-up을 건다.
- 더 빠른 mode를 시도하기 전에 100 kHz 또는 400 kHz부터 시작한다.

초기 결정:

- BNO08x의 첫 interface 후보는 I2C로 둔다.
- I2C 안정성 문제가 생기면 SPI 또는 UART를 fallback으로 검토한다.

## 3. USART / UART

USART는 Universal Synchronous/Asynchronous Receiver Transmitter의 약자다.
UART는 Universal Asynchronous Receiver Transmitter의 약자다.

간단한 차이:

- UART는 비동기 serial communication을 지원한다.
- USART는 비동기 serial communication에 더해 동기 mode도 지원할 수 있다.
- 이 프로젝트에서는 USART도 대부분 UART 방식의 TX/RX mode로 사용할 것이다.

데이터시트 핵심:

- Table 8 기준 serial interface 6개:
  - USART1
  - USART2
  - USART3
  - UART4
  - UART5
  - USART6
- USART1과 USART6은 APB2에 매핑되어 더 높은 최대 baud rate를 지원한다.
- USART2, USART3, UART4, UART5는 APB1에 매핑된다.
- 모든 interface는 asynchronous communication을 지원한다.
- IrDA, multiprocessor communication, single-wire half-duplex, LIN, DMA를 지원한다.
- USART1, USART2, USART3, USART6은 CTS/RTS, Smart Card mode, SPI-like communication도 지원한다.

### 프로젝트 용도

주요 용도:

- PC에서 속도 명령 수신
- Debug log 출력
- ESP32-S3와 통신
- 향후 ROS2 또는 PC-side tool로 이어지는 serial bridge

초기 권장 사용:

- 먼저 PC command와 debug용 serial channel 하나만 사용한다.
- ESP32-S3용 두 번째 serial channel은 필요가 분명해진 뒤 추가한다.

일반적인 초기 설정:

- 115200 baud
- 8 data bits
- No parity
- 1 stop bit
- No flow control

이를 흔히 `115200 8N1`이라고 쓴다.

### 설계 메모

Logic-level UART와 RS-232를 혼동하면 안 된다.

- STM32 UART 핀은 보통 3.3 V logic-level 신호다.
- RS-232 전압 레벨을 STM32 핀에 직접 연결하면 안 된다.
- USB-to-serial adapter는 3.3 V logic 호환인지 확인해야 한다.

처음에는 interrupt 방식으로 시작한다.

- Interrupt 기반 수신은 DMA보다 단순하다.
- Serial protocol이 고속화되거나 byte 손실이 확인되면 DMA 수신을 추가한다.

Protocol 권장:

- 처음에는 단순 text command protocol로 시작한다.
- 기본 주행 테스트가 된 뒤 binary packet과 CRC를 검토한다.

## 4. SPI

SPI는 clock line, data line, chip select signal을 사용하는 동기식 serial
interface다.

데이터시트 핵심:

- SPI 최대 4개
- Master/slave mode 지원
- Full-duplex와 simplex communication 지원
- SPI1, SPI4는 최대 45 Mbit/s
- SPI2, SPI3는 최대 22.5 Mbit/s
- 8-bit 또는 16-bit frame format
- Hardware CRC generation/verification
- DMA 지원

### 프로젝트 용도

SPI는 첫 MVP에 필수는 아니지만, 대체 센서 interface로 유용하다.

후보 용도:

- 모듈이 지원한다면 BNO08x IMU fallback interface
- 향후 고속 센서
- Display 또는 external storage

I2C와 SPI 비교:

- I2C는 선이 적고 저속 센서에 단순하다.
- SPI는 선이 더 많지만 일부 모듈에서는 더 빠르고 안정적일 수 있다.

초기 결정:

- IMU breakout 또는 sensor module이 SPI를 더 쉽게 만들지 않는 한 SPI를 먼저 쓰지 않는다.
- SPI는 확장 interface로 남긴다.

## 5. bxCAN

bxCAN은 STM32의 CAN controller다. CAN은 차량과 산업 시스템에서 자주 쓰는
차동 multi-node bus다.

데이터시트 핵심:

- CAN controller 2개
- CAN 2.0A와 2.0B active 지원
- 최대 bitrate 1 Mbit/s
- 11-bit standard identifier
- 29-bit extended identifier
- CAN별 transmit mailbox 3개
- 3단 receive FIFO 2개
- shared scalable filter bank 28개
- CAN별 SRAM 256 bytes 할당

### 프로젝트 용도

CAN은 MVP에서는 명시적으로 후순위지만, MCU는 향후 확장을 지원한다.

가능한 미래 용도:

- STM32와 다른 controller 사이의 견고한 link
- 분산 motor controller 또는 sensor node
- multi-node robot electronics의 배선 정리

중요한 하드웨어 메모:

- STM32에는 CAN controller가 들어 있지만, 완전한 물리 CAN interface가 들어 있는 것은 아니다.
- 실제 CAN bus에 연결하려면 CAN transceiver가 필요하다.
- 실제 CAN 배선에는 적절한 bus termination이 필요하다.

초기 결정:

- 첫 MVP에서는 CAN을 사용하지 않는다.
- UART 기반 MVP가 검증될 때까지 CAN은 architecture 확장 경로로만 남긴다.

## 6. GPIO

GPIO는 General-Purpose Input/Output의 약자다. 디지털 입력, 디지털 출력,
아날로그 입력, peripheral alternate function으로 설정할 수 있는 핀이다.

데이터시트 핵심:

- Output mode: push-pull 또는 open-drain
- Pull-up 또는 pull-down 선택 가능
- Input mode: floating 또는 pull-up/pull-down
- Peripheral alternate function mode
- 많은 GPIO가 digital 또는 analog alternate function과 공유됨
- GPIO speed selection 가능
- I/O configuration lock 가능
- 최대 90 MHz까지 빠른 I/O toggling 가능

### 프로젝트 용도

GPIO는 다음에 필요하다.

- 모터 드라이버 direction pin
- 모터 드라이버 enable 또는 brake pin
- 가능하다면 driver fault input
- User button 또는 emergency-stop signal
- Status LED
- SPI device의 chip-select signal
- 선택적 power control signal

중요한 경고:

- GPIO가 high-current-capable이라고 해서 모터를 직접 구동할 수 있다는 뜻은 아니다.
- STM32 GPIO pin은 logic signal용이지 motor power용이 아니다.
- 모터는 반드시 motor driver 또는 power stage를 통해 구동해야 한다.

### 안전한 모터 드라이버 제어

모터 관련 GPIO는 안전한 기본 상태를 가지도록 설계해야 한다.

권장 접근:

- Motor enable pin은 reset 중 기본적으로 disabled가 되도록 한다.
- 필요에 따라 pull-down 또는 pull-up 저항을 사용한다.
- 펌웨어는 startup 중 motor output을 명시적으로 disable해야 한다.
- PWM은 direction과 enable pin이 알려진 상태가 된 뒤 시작한다.

## 7. ADC

ADC는 Analog-to-Digital Converter의 약자다. 아날로그 전압을 디지털 값으로
바꾸는 장치다.

데이터시트 핵심:

- 12-bit ADC 3개
- 각 ADC는 최대 16개 external channel 공유
- Single-shot 또는 scan mode
- 선택한 analog input group에 대한 automatic scan conversion
- Simultaneous sample and hold
- Interleaved sample and hold
- DMA 지원
- Analog watchdog 지원
- 변환 전압이 설정 threshold 밖으로 나가면 interrupt 생성 가능
- ADC conversion은 TIM1, TIM2, TIM3, TIM4, TIM5, TIM8로 trigger 가능

### 프로젝트 용도

첫 번째 ADC 용도는 3S LiPo 전압 감시다.

중요 규칙:

- 3S LiPo 전압은 STM32 ADC pin에 절대 직접 연결하면 안 된다.
- 반드시 저항 분배 회로로 battery voltage를 ADC input range 아래로 낮춰야 한다.

가능한 ADC 입력:

- 배터리 pack voltage
- Motor driver current sense가 있다면 전류 감지
- 저항 분배를 통한 regulated 5 V rail monitor
- 온도 또는 기타 analog diagnostics

### Analog Watchdog

Analog watchdog은 ADC 값이 설정한 threshold 범위를 벗어나면 interrupt를
생성할 수 있다.

프로젝트 용도:

- 저전압 감지
- Warning state 진입
- PWM 제한 또는 모터 정지

초기 결정:

- 먼저 주기적 ADC sampling과 software threshold check로 시작한다.
- Battery monitoring logic에 더 강한 hardware support가 필요해지면 analog watchdog을 검토한다.

### Timer-Triggered ADC

ADC는 timer로 trigger할 수 있다.

프로젝트 용도:

- 고정 주기로 battery voltage를 sampling한다.
- Main loop timing 변화 때문에 sampling이 불규칙해지는 것을 줄인다.

초기 결정:

- MVP에서는 software-triggered 또는 단순 periodic sampling으로 충분하다.
- Control loop와 telemetry 구조가 정리되면 timer-triggered ADC를 추가한다.

## 8. SWJ-DP: SWD/JTAG Debug Port

SWJ-DP는 Serial Wire Debug와 JTAG debug access를 결합한 debug port다.

데이터시트 핵심:

- SWD와 JTAG 지원
- SWD는 JTAG보다 적은 pin 사용
- SWDIO와 SWCLK 두 pin만으로 debug 가능
- 적절한 경우 JTAG pin은 alternate function GPIO로 재사용 가능

### 프로젝트 용도

NUCLEO 보드는 ST-LINK를 사용하며, firmware upload와 debugging은 이 debug
interface에 의존한다.

프로젝트 결정:

- 개발 중에는 SWD pin을 보존한다.
- 초기 개발 단계에서는 SWD pin을 로봇 기능에 배정하지 않는다.
- MVP 단계에서는 pin 몇 개를 아끼는 것보다 debug access를 유지하는 것이 더 가치 있다.

## 9. MVP에서 우선순위가 낮은 주변장치

다음 주변장치들은 일반적으로 유용하지만 첫 로봇 MVP의 중심은 아니다.

- I2S / SAI / SPDIF-RX: audio interface
- HDMI-CEC: consumer electronics control
- SDIO: SD/MMC card interface
- USB OTG FS/HS: 유용할 수 있지만 ST-LINK virtual COM과 UART가 첫 단계에서는 더 단순함
- DCMI: camera parallel interface
- DAC: analog output

결정:

- 첫 pin allocation에는 포함하지 않는다.
- 특정 기능이 필요해질 때만 다시 검토한다.

## 10. 예비 주변장치 배정

이것은 최종 pinout이 아니다. Table 10, Table 11, NUCLEO schematic, CubeMX를
확인하기 전의 기능 배정이다.

| 로봇 기능 | 주변장치 후보 | 첫 결정 |
| --- | --- | --- |
| PC command/debug | USART/UART | 먼저 단순 serial link 하나만 사용. |
| ESP32-S3 link | USART/UART | PC serial control이 동작한 뒤 추가. |
| BNO08x IMU | I2C 우선, SPI/UART fallback | I2C로 단순하게 시작. |
| Motor driver direction | GPIO | 안전한 기본 상태 사용. |
| Motor driver enable/brake | GPIO | Reset 시 disabled가 기본. |
| Battery voltage monitor | ADC | 저항 분배와 software threshold부터 사용. |
| Future CAN bus | bxCAN + transceiver | UART MVP 이후로 연기. |
| Firmware debug | ST-LINK를 통한 SWD | 개발 중 보존. |

## 11. 위험 요소와 확인 사항

### Voltage Compatibility

필수 확인:

- Motor driver logic input threshold
- Encoder output voltage
- IMU logic voltage
- ESP32-S3 UART voltage
- ADC input maximum voltage

### Pin Conflict

필수 확인:

- USART pin이 PWM/encoder pin과 충돌하지 않는가?
- I2C pin이 사용 가능하고 pull-up이 적절한가?
- ADC pin이 timer 또는 communication 기능과 충돌하지 않는가?
- SWD pin이 유지되는가?

### Noise

모터 시스템은 noise가 크다.

대응:

- Motor power wire를 I2C/UART wire와 떨어뜨린다.
- 공통 GND 기준을 의도적으로 구성한다.
- Filtering이나 shielding은 실제 문제를 측정하거나 관찰한 뒤 추가한다.
- ADC divider impedance와 filtering을 적절히 잡는다.

## 12. 1차 설계 결정

STM32F446RE는 초기 궤도 로봇 MVP에 필요한 통신 및 I/O 자원이 충분하다.

추천 방향:

1. PC command와 debug에는 USART/UART 경로 하나를 먼저 사용한다.
2. BNO08x IMU의 첫 interface 후보는 I2C로 둔다.
3. Motor direction과 enable/brake는 안전한 기본 상태를 가진 GPIO로 제어한다.
4. LiPo 전압 감시는 저항 분배 후 ADC로 수행한다.
5. SWD는 debugging을 위해 보존한다.
6. CAN은 UART 기반 MVP가 검증될 때까지 미룬다.

## 13. 다음 단계

다음 architecture 문서는 첫 pin allocation candidate를 만들어야 한다.

필요한 입력:

- Table 10: Pin and ball descriptions
- Table 11: Alternate function
- NUCLEO-F446RE user manual and schematic
- CubeMX pinout conflict check

Pin allocation은 다음을 포함해야 한다.

- 좌/우 motor PWM
- 좌/우 encoder A/B
- Motor direction과 enable GPIO
- PC용 UART
- ESP32-S3용 optional UART
- IMU용 I2C
- Battery voltage용 ADC
- SWD debug 보존
