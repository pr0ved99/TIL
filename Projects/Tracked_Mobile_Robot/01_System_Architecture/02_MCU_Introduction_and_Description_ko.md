# STM32F446RE Introduction and Description 분석

## 목적

이 문서는 STM32F446xC/E 데이터시트의 다음 범위를 읽고, NUCLEO-F446RE가
궤도형 모바일 로봇의 하위 제어기로 적절한지 1차 판단한 기록이다.

- Section 1: Introduction
- Section 2: Description
- Table 2: STM32F446xC/E features and peripheral counts

## 1. Introduction에서 확인한 것

데이터시트의 Introduction은 짧지만 중요한 전제를 준다.

STM32F446xC/E 데이터시트는 Arm Cortex-M4 코어 기반 제품군의 설명 문서다.
하지만 이 문서만으로 펌웨어를 전부 구현할 수는 없다. 데이터시트는 주로
스펙, 핀, 전기적 한계를 설명하고, 주변장치를 실제로 어떻게 설정하는지는
별도 문서를 함께 봐야 한다.

필요한 문서는 다음처럼 역할이 나뉜다.

| 문서 | 역할 | 프로젝트에서의 사용 |
| --- | --- | --- |
| Datasheet | 칩의 기능, 핀, 전기적 한계, 패키지 정보를 제공한다. | MCU 적합성 판단, 핀 선정, 전압/전류 한계 확인. |
| RM0390 Reference Manual | 타이머, ADC, UART 등 주변장치 레지스터와 동작 방식을 설명한다. | 실제 STM32 펌웨어 설계와 디버깅. |
| PM0214 Cortex-M4 Programming Manual | Cortex-M4 코어, 명령어, 예외, 인터럽트 구조를 설명한다. | 인터럽트, SysTick, 저수준 디버깅 이해. |

### 해석

이 프로젝트에서는 처음부터 Reference Manual 전체를 정독할 필요는 없다.
하지만 Timer, ADC, UART, I2C, CAN을 실제로 사용할 때는 데이터시트만으로
부족하므로 RM0390을 함께 확인해야 한다.

## 2. Description 핵심 요약

STM32F446xC/E는 최대 180 MHz로 동작하는 Arm Cortex-M4 32-bit MCU 계열이다.
NUCLEO-F446RE에 들어가는 STM32F446RE도 이 계열에 속한다.

데이터시트의 Description에서 프로젝트와 직접 관련 있는 문장은 다음과 같다.

- 최대 180 MHz Cortex-M4 CPU
- 단정밀도 FPU 포함
- DSP instruction 지원
- MPU 포함
- Flash 최대 512 KB
- SRAM 최대 128 KB
- Backup SRAM 4 KB
- 12-bit ADC 3개
- 일반 목적 16-bit timer 12개
- 모터 제어용 PWM timer 2개
- 일반 목적 32-bit timer 2개
- I2C 최대 4개
- USART 4개 + UART 2개
- CAN 2개
- 동작 전압 범위는 보통 1.8 V ~ 3.6 V로 봐야 함

## 주요 용어 정리

### Cortex-M4

Cortex-M4는 Arm이 만든 MCU용 CPU 코어다. 쉽게 말하면 STM32 안에서 명령어를
실행하는 중심 연산 장치다.

프로젝트 의미:

- PWM 제어 루프를 주기적으로 실행한다.
- 엔코더 값을 읽고 속도를 계산한다.
- PID 제어, odometry 계산, IMU 데이터 처리를 수행한다.

### FPU

FPU는 Floating Point Unit의 약자다. 실수 연산을 하드웨어로 빠르게 처리하는
장치다.

프로젝트 의미:

- 속도 계산에서 `m/s`, `rad/s` 같은 실수 값을 다룰 때 유리하다.
- PID 계산, IMU yaw rate 처리, odometry 계산이 쉬워진다.

주의할 점:

- FPU가 있다고 해서 모든 코드를 float로 작성해도 된다는 뜻은 아니다.
- 제어 주기가 짧아지면 고정소수점 또는 정수 기반 계산이 더 안정적일 수 있다.
- 초기 구현은 가독성을 위해 float를 쓰고, 성능 문제가 생기면 최적화하는 방식이 현실적이다.

### DSP instructions

DSP instruction은 곱셈, 누산, 포화 연산 같은 신호 처리 연산을 빠르게 처리하기
위한 명령어다.

프로젝트 의미:

- 필터링, 센서 데이터 처리, 제어 알고리즘에서 유리하다.
- 예를 들어 엔코더 속도값에 이동 평균 필터를 적용하거나 IMU 데이터를 필터링할 때 도움이 된다.

초기 MVP에서는 직접 DSP 명령어를 의식해서 쓸 가능성은 낮다. 하지만 CMSIS-DSP
같은 라이브러리를 쓰게 되면 이 기능의 이점을 받을 수 있다.

### MPU

MPU는 Memory Protection Unit의 약자다. 메모리 영역별 접근 권한을 제한할 수
있는 장치다.

프로젝트 의미:

- 초기 bare-metal 또는 HAL 기반 펌웨어에서는 거의 사용하지 않는다.
- RTOS를 쓰거나 안전성이 중요한 구조로 확장할 때 의미가 커진다.

현재 판단:

- 초기 MVP에서는 후순위다.

### APB, AHB, Multi-AHB bus matrix

APB와 AHB는 MCU 내부에서 CPU, 메모리, 주변장치가 데이터를 주고받는 내부 버스다.

쉽게 말하면:

- AHB: 빠른 내부 고속도로
- APB: 타이머, UART, I2C 같은 주변장치로 가는 도로
- Multi-AHB bus matrix: 여러 장치가 동시에 접근할 수 있게 해주는 내부 연결 구조

프로젝트 의미:

- Timer, ADC, UART, DMA 같은 주변장치가 CPU와 어떻게 연결되는지의 기반이다.
- 초기에는 CubeMX/HAL이 대부분 처리하므로 깊게 몰라도 된다.
- DMA와 고속 ADC/UART를 동시에 쓰기 시작하면 중요해진다.

## 3. Table 2에서 F446RE만 추출한 결과

NUCLEO-F446RE는 STM32F446RE 계열로 보면 된다. Table 2 기준으로 F446RE의
핵심 스펙은 다음과 같이 정리할 수 있다.

| 항목 | STM32F446RE 기준 | 프로젝트 판단 |
| --- | --- | --- |
| Flash | 512 KB | 하위 제어 펌웨어, UART 프로토콜, IMU 처리까지 충분하다. |
| System SRAM | 128 KB, 구조상 112 KB + 16 KB | 모터 제어, 엔코더, ADC, IMU 버퍼에는 충분하다. |
| Backup SRAM | 4 KB | 초기 MVP에서는 거의 사용하지 않는다. |
| General-purpose timers | 10개 | PWM, 엔코더, 주기 타이머 구성에 충분하다. |
| Advanced-control timers | 2개 | 모터 제어용 PWM에 적합한 고급 타이머다. |
| Basic timers | 2개 | 주기적 이벤트나 DAC 트리거 등에 사용 가능하다. |
| SPI / I2S | SPI 4개 / I2S 3개 | SPI 센서를 추가할 여유가 있다. I2S는 초기에는 불필요하다. |
| I2C | 4개, FMP+ 1개 | BNO08x IMU 연결에 충분하다. |
| USART / UART | USART 4개 + UART 2개 | PC, ESP32, 디버그용 통신을 나눌 수 있다. |
| USB OTG FS | 지원 | NUCLEO 보드에서는 ST-LINK 가상 COM 포트와 구분해서 봐야 한다. |
| USB OTG HS | 지원 | 초기 MVP에서는 우선순위 낮다. |
| CAN | 2개 | CAN을 나중으로 미루더라도 확장 여지가 있다. |
| SDIO | 지원 | 초기에는 불필요하다. |
| QuadSPI | 제한 기능 가능 | 초기에는 불필요하다. |
| Camera interface | 지원 | 초기에는 불필요하다. |
| GPIO | F446RE 패키지 기준 약 50개 | 모터, 엔코더, UART, I2C, ADC 배치에 충분할 가능성이 높다. |
| 12-bit ADC | ADC 3개, F446RE 패키지 기준 채널 16개 | 배터리 전압, 전류 센서 후보, 아날로그 입력에 충분하다. |
| 12-bit DAC | 2채널 | 초기 MVP에서는 불필요하다. |
| Maximum CPU frequency | 180 MHz | 하위 제어기로 충분히 여유 있다. |
| Operating voltage | 1.8 V ~ 3.6 V | 실제 보드 운용은 3.3 V 기준으로 설계해야 한다. |
| Package | LQFP64 | NUCLEO-F446RE의 핀 수 제약을 고려해야 한다. |

## 4. 우리 로봇 요구사항과의 매칭

### 모터 PWM 제어

요구사항:

- 좌/우 모터 PWM 출력
- 방향 제어 GPIO
- direction GPIO와 선택적 power gate/brake 제어 GPIO

Table 2 기준 판단:

- Advanced-control timer 2개와 general-purpose timer 10개가 있으므로 PWM 자원은 충분하다.
- 실제 사용 가능 여부는 Table 11의 Alternate function과 NUCLEO 보드 핀맵으로 확인해야 한다.

### 엔코더 입력

요구사항:

- 좌/우 모터 엔코더 A/B 채널
- 가능하면 Timer encoder mode 사용

Table 2 기준 판단:

- Timer 수량은 충분하다.
- 어떤 timer가 encoder mode를 지원하는지는 Table 6과 RM0390에서 확인해야 한다.
- 핀 배치는 Table 11에서 `TIMx_CH1`, `TIMx_CH2` 쌍이 같은 timer로 나오는지 확인해야 한다.

### 배터리 전압 감시

요구사항:

- 3S LiPo 전압을 저항 분배 후 ADC로 측정
- 저전압 기준 도달 시 모터 출력 제한 또는 정지

Table 2 기준 판단:

- 12-bit ADC 3개와 F446RE 기준 16개 ADC 채널은 충분하다.
- 단, 3S LiPo 전압은 MCU에 직접 넣으면 안 된다.
- 반드시 저항 분배로 ADC 입력을 3.3 V 이하로 낮춰야 한다.
- 실제 입력 조건은 Table 76 ADC characteristics와 Section 6 전기적 특성에서 확인해야 한다.

### BNO08x IMU 연결

요구사항:

- I2C 또는 UART/SPI 연결 후보

Table 2 기준 판단:

- I2C 4개가 있으므로 I2C 연결 여유가 있다.
- SPI도 4개라 SPI 연결도 가능하다.
- 초기에는 배선이 단순한 I2C가 유리하지만, 통신 안정성 문제가 생기면 SPI도 후보가 된다.

### PC / ESP32 통신

요구사항:

- PC에서 속도 명령 수신
- ESP32-S3와 보조 통신 가능성
- 디버그 로그 출력

Table 2 기준 판단:

- USART 4개 + UART 2개는 충분하다.
- 예를 들어 PC debug, ESP32 link, 외부 serial module을 분리할 수 있다.
- 실제로 어떤 UART가 NUCLEO 커넥터에 잘 나오는지는 보드 회로도와 핀맵을 같이 봐야 한다.

### CAN 확장

요구사항:

- 초기 MVP에서는 제외
- 추후 견고한 내부 통신 버스로 검토

Table 2 기준 판단:

- CAN 2개가 있으므로 MCU 자체는 CAN 확장을 지원한다.
- 단, STM32의 CAN 컨트롤러만으로는 버스에 직접 연결할 수 없다.
- 실제 CAN 통신에는 별도 CAN transceiver가 필요하다.

## 5. 중요한 주의점

### 1. MCU 동작 전압과 보드 전원은 구분해야 한다

Table 2에는 operating voltage가 1.8 V ~ 3.6 V로 나온다. 하지만 NUCLEO 보드와
일반적인 STM32 GPIO 설계는 3.3 V 기준으로 생각해야 한다.

주의:

- 3S LiPo를 STM32에 직접 연결하면 안 된다.
- 5 V 신호도 모든 핀에 넣을 수 있는 것이 아니다.
- 5 V tolerant 여부는 핀별로 Table 10, Table 11, Section 6에서 확인해야 한다.

### 2. F446RE는 F446 계열 전체 중 핀 수가 적은 편이다

F446RE는 LQFP64 패키지다. 같은 F446 계열의 더 큰 패키지보다 GPIO 수와 ADC
채널 수가 적다.

의미:

- MCU 내부 주변장치 수는 충분해도, 실제 보드 밖으로 나온 핀이 부족할 수 있다.
- CubeMX에서 peripheral conflict가 발생할 수 있다.
- 모터 PWM, 엔코더, UART, I2C, ADC를 동시에 배치하는 핀맵 검토가 필요하다.

### 3. 데이터시트는 충분조건이 아니다

Table 2에서 timer 수가 충분하다고 해서 바로 엔코더 입력이 된다는 뜻은 아니다.

추가로 확인해야 하는 것:

- 해당 timer가 encoder mode를 지원하는가?
- 필요한 채널이 같은 timer의 CH1/CH2로 나오는가?
- 그 핀이 NUCLEO 보드에서 사용 가능한가?
- ST-LINK, Arduino header, Morpho header와 충돌하지 않는가?

## 6. 1차 판단

STM32F446RE는 이 프로젝트의 초기 하위 제어기로 적절하다.

근거:

1. 180 MHz Cortex-M4와 FPU가 있어 모터 제어와 기본 odometry 계산에 충분하다.
2. 512 KB Flash와 128 KB SRAM은 초기 펌웨어 규모에 충분하다.
3. Timer 수량이 많아 PWM, 엔코더, 주기 타이머 구성이 가능하다.
4. 12-bit ADC 3개와 여러 ADC 채널을 통해 배터리 전압 감시가 가능하다.
5. USART/UART 수량이 충분해 PC, ESP32, 디버그 통신을 분리할 수 있다.
6. I2C와 SPI가 모두 있어 BNO08x IMU 연결 방식을 선택할 수 있다.
7. CAN 2개가 있어 초기에는 쓰지 않더라도 확장성이 있다.

단, 적절성 판단이 최종 확정되려면 다음 검증이 필요하다.

- 실제 NUCLEO-F446RE 핀맵에서 PWM/엔코더/UART/I2C/ADC가 충돌 없이 배치되는지
- 모터 드라이버 입력 전압과 STM32 GPIO 출력 전압이 호환되는지
- 엔코더 출력 전압이 STM32 입력 한계를 넘지 않는지
- ADC 배터리 전압 측정 회로가 전기적 한계를 만족하는지

## 다음 단계

다음에는 Section 3 Functional overview 중 프로젝트에 직접 필요한 항목을
순서대로 읽는다.

우선순위:

1. Cortex-M4 / FPU / Flash / SRAM
2. DMA
3. NVIC / EXTI
4. Clocks and startup
5. Timers and watchdogs
6. I2C
7. USART/UART
8. bxCAN
9. GPIO
10. ADC

이후 Table 6, Table 10, Table 11을 사용해 실제 핀 배치 후보를 만든다.
