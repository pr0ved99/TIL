# STM32F446RE 코어, 메모리, 인터럽트, 클럭 분석

## 목적

이 문서는 STM32F446xC/E 데이터시트의 Section 3 Functional overview 중
프로젝트와 먼저 연결되는 앞부분을 분석한다.

범위:

- Section 3.1: Arm Cortex-M4 with FPU and embedded Flash/SRAM
- Section 3.2: ART Accelerator
- Section 3.3: MPU
- Section 3.4: Embedded Flash memory
- Section 3.5: CRC calculation unit
- Section 3.6: Embedded SRAM
- Section 3.7: Multi-AHB bus matrix
- Section 3.8: DMA controller
- Section 3.9: FMC
- Section 3.10: QuadSPI
- Section 3.11: NVIC
- Section 3.12: EXTI
- Section 3.13: Clocks and startup
- Section 3.14: Boot modes

목표는 모터 제어 타이머, 통신 주변장치, GPIO, ADC를 분석하기 전에 MCU의
기본 구조를 이해하는 것이다.

## 1. 코어와 연산 성능

### Cortex-M4 with FPU

STM32F446RE는 단정밀도 FPU가 포함된 Arm Cortex-M4 CPU 코어를 사용한다.

데이터시트 핵심:

- 32-bit RISC processor
- 임베디드 시스템용으로 설계됨
- 빠른 인터럽트 응답
- DSP instruction 지원
- 단정밀도 부동소수점 하드웨어 지원
- Cortex-M3와 바이너리 호환

프로젝트 의미:

- 초기 하위 로봇 제어기로 충분한 CPU 성능을 가진다.
- 속도, yaw rate, PID, odometry 계산에 부동소수점 연산을 사용할 수 있다.
- DSP 지원은 추후 필터링과 센서 처리 최적화 여지를 준다.

실무적 해석:

- 초기에는 읽기 쉬운 부동소수점 코드를 사용한다.
- 실제 loop time을 측정한 뒤에만 최적화한다.
- CPU가 빠르더라도 시간에 민감한 interrupt handler는 짧게 유지한다.

### FPU

FPU는 Floating Point Unit의 약자다. `m/s`, `rad/s`, PID 항, odometry 추정값
같은 실수 계산을 빠르게 처리하는 하드웨어다.

로봇에서의 용도:

- 엔코더 tick을 바퀴 속도로 변환
- 각속도 계산
- IMU yaw rate와 엔코더 기반 yaw 추정 비교
- 읽기 쉬운 수식 형태의 PID 제어 구현

주의점:

- FPU는 성능을 도와주지만, 제어 주기의 결정성을 보장해주지는 않는다.
- 제어 루프는 여전히 고정 주기로 실행되어야 한다.

### DSP Instructions

DSP instruction은 곱셈-누산, 포화 연산처럼 신호 처리에서 자주 쓰는 패턴을
빠르게 처리하기 위한 CPU 명령어다.

로봇에서의 후보 용도:

- 엔코더 속도 smoothing
- IMU 신호 필터링
- 전류 또는 전압 측정값 필터링
- 추후 CMSIS-DSP 기반 필터링

초기 결정:

- MVP 단계에서는 DSP instruction을 전제로 설계하지 않는다.
- 추후 최적화 여지로 남긴다.

### MPU

MPU는 Memory Protection Unit의 약자다. 메모리 영역 접근 권한을 제한해서
한 task가 다른 보호 영역을 실수로 망가뜨리지 못하게 하는 장치다.

데이터시트 핵심:

- 최대 8개 보호 영역
- 각 영역은 하위 영역으로 나눌 수 있음
- 보호 영역 크기는 32 bytes부터 전체 4 GB 주소 공간까지 가능
- 보통 RTOS가 관리함
- 선택 기능이며 필요 없으면 우회 가능

프로젝트 결정:

- 초기 bare-metal 또는 HAL 기반 MVP에서는 우선순위가 낮다.
- RTOS 기반 펌웨어나 더 강한 안전 분리 구조로 확장할 때 다시 검토한다.

## 2. 프로그램 메모리와 데이터 메모리

### Embedded Flash Memory

데이터시트는 이 디바이스가 프로그램과 데이터를 저장하기 위한 512 KB Flash
memory를 내장한다고 설명한다.

로봇에서의 용도:

- 메인 펌웨어 이미지
- 제어 로직
- Serial protocol 코드
- Flash에 저장하는 calibration constant

초기 판단:

- 512 KB는 초기 모터 제어 펌웨어에 충분하다.
- UART protocol 처리, IMU parsing, 기본 diagnostic logging 코드까지도 충분할 가능성이 높다.

### ART Accelerator

ART는 Adaptive Real-Time memory accelerator의 약자다. CPU가 높은 주파수에서
Flash에 있는 코드를 실행할 때 생기는 대기 시간을 줄여주는 장치다.

데이터시트 핵심:

- Cortex-M4에 최적화됨
- instruction prefetch와 branch cache 사용
- Flash에서 실행해도 CPU 성능을 높게 유지하도록 도움
- 데이터시트는 CoreMark 계열 성능 기준으로 180 MHz에서 Flash 실행이 0 wait state에 준하는 성능을 낼 수 있다고 설명함

프로젝트 의미:

- 펌웨어를 내부 Flash에서 일반적으로 실행해도 된다.
- 제어 루프 코드를 특별히 RAM으로 옮겨 실행하는 복잡한 구조는 초기에는 필요 없다.

실무적 주의:

- ART가 있다고 해서 timing 검증이 필요 없어지는 것은 아니다.
- 제어 루프 주기는 GPIO toggle, timer capture, debug/trace 도구 등으로 실제 측정해야 한다.

### Embedded SRAM

STM32F446xC/E는 다음 SRAM을 포함한다.

- 최대 128 KB system SRAM
- 4 KB backup SRAM
- System SRAM은 CPU clock speed에서 0 wait state로 접근 가능
- Backup SRAM은 Standby 또는 VBAT mode에서 유지 가능

로봇에서의 용도:

- 실행 중 변수
- 엔코더 카운터와 속도 추정값
- UART 수신 버퍼
- ADC 샘플 버퍼
- IMU 데이터 버퍼
- 제어 상태값

초기 판단:

- 128 KB는 초기 로봇 MVP에 충분하다.
- 그래도 불필요하게 큰 버퍼는 피해야 한다.
- Backup SRAM은 초기에는 필요 없다.

## 3. 데이터 무결성과 데이터 이동

### CRC Calculation Unit

CRC는 Cyclic Redundancy Check의 약자다. 데이터가 전송 또는 저장 중 손상됐는지
확인하기 위한 짧은 검증 코드다.

데이터시트 핵심:

- 32-bit data word와 고정 polynomial로 CRC 생성
- 데이터 전송 또는 저장 무결성 확인에 사용 가능
- 런타임 소프트웨어 signature 계산에도 활용 가능

로봇에서의 후보 용도:

- 추후 serial command packet 검증
- 저장된 calibration data 검증
- 더 성숙한 안전 설계에서 firmware integrity check

초기 결정:

- 첫 모터 제어 MVP에는 필수는 아니다.
- Serial protocol이 구조화되면 유용해질 수 있다.

### DMA Controller

DMA는 Direct Memory Access의 약자다. CPU가 모든 바이트를 직접 복사하지 않아도
메모리와 주변장치 사이에서 데이터를 옮겨주는 하드웨어다.

데이터시트 핵심:

- DMA1, DMA2 두 개의 general-purpose dual-port DMA
- 각 DMA는 8개 stream 보유
- memory-to-memory, peripheral-to-memory, memory-to-peripheral 전송 지원
- circular buffer management 지원
- double buffering 지원
- SPI/I2S, I2C, USART, timer, DAC, SDIO, DCMI, ADC, SAI, SPDIF, QuadSPI와 사용 가능

로봇에서의 용도:

- UART 수신 버퍼를 안정적으로 유지
- 배터리 전압 ADC 샘플링
- 필요 시 SPI 또는 I2C 센서 전송
- 더 고급 설계에서 timer 관련 데이터 전송

초기 결정:

- 처음에는 interrupt 기반 UART와 단순 ADC polling/interrupt 방식으로 시작한다.
- 데이터 손실, CPU 부담, timing jitter가 실제로 측정되면 DMA로 넘어간다.

중요한 설계 원칙:

- DMA는 효율을 높이지만 디버깅 난이도도 올린다.
- 단순한 방식의 한계가 확인된 뒤에 사용한다.

## 4. 내부 버스 구조

### Multi-AHB Bus Matrix

Multi-AHB bus matrix는 CPU, DMA, USB HS 같은 master와 Flash, RAM, QuadSPI,
FMC, AHB peripheral, APB peripheral 같은 slave를 연결한다.

쉽게 해석하면:

- CPU, DMA, 주변장치가 내부 도로를 공유한다.
- Bus matrix는 여러 고속 블록이 동시에 동작할 수 있도록 돕는다.

프로젝트 의미:

- DMA가 데이터를 옮기는 동안 CPU가 제어 로직을 계속 실행할 수 있는 기반이다.
- UART, ADC, timer, sensor interface가 동시에 동작하기 시작하면 중요해진다.

초기 결정:

- 이 단계에서 직접 작성할 펌웨어 코드는 없다.
- 추후 성능 디버깅을 위한 배경 지식으로 둔다.

## 5. 외부 메모리 기능

### FMC

FMC는 Flexible Memory Controller의 약자다. SRAM, PSRAM, NOR Flash, NAND Flash,
SDRAM 같은 외부 메모리와 연결하기 위한 장치다.

프로젝트 결정:

- 초기 로봇 MVP에서는 필요 없다.
- 외부 메모리나 병렬 LCD가 필요한 미래 설계에서만 다시 검토한다.

### QuadSPI

QuadSPI는 외부 SPI Flash memory를 위한 고속 인터페이스다. 외부 Flash를
memory-mapped 방식으로 접근할 수도 있다.

프로젝트 결정:

- 초기 로봇 MVP에서는 필요 없다.
- 하위 제어기에는 내부 Flash로 충분하다.

## 6. 인터럽트와 이벤트 처리

### NVIC

NVIC는 Nested Vectored Interrupt Controller의 약자다. 인터럽트 우선순위를
관리하고 CPU를 올바른 interrupt handler로 보내는 장치다.

데이터시트 핵심:

- 16 priority levels
- 최대 91개 maskable interrupt channel
- Cortex-M4 core interrupt line 16개
- low-latency interrupt processing
- 늦게 도착한 더 높은 우선순위 interrupt 처리 지원
- tail chaining 지원
- processor state 자동 저장/복구

로봇에서의 용도:

- 제어 루프용 주기 timer interrupt
- 명령 수신용 USART receive interrupt
- 비상 버튼 또는 저속 외부 신호용 EXTI interrupt
- DMA를 쓰지 않는 경우 ADC interrupt

설계 원칙:

- Interrupt handler는 짧게 유지한다.
- Interrupt handler 안에서 긴 계산, blocking delay, 무거운 printing을 하지 않는다.
- 플래그 설정이나 작은 버퍼 저장만 수행하고, 실제 처리는 main loop 또는 주기 task에서 한다.

### EXTI

EXTI는 External Interrupt/Event Controller의 약자다. 외부 핀의 edge를 감지해
interrupt 또는 event request를 만든다.

데이터시트 핵심:

- 23개 edge-detector line
- rising edge, falling edge, both edge trigger 선택 가능
- line별 독립 mask 가능
- pending register로 요청 상태 유지
- 전체 디바이스 계열 기준 최대 114 GPIO가 16개 external interrupt line에 연결 가능

로봇에서의 용도:

- 비상 정지 버튼
- 사용자 버튼
- limit switch
- 모터 드라이버의 저속 fault input

엔코더 관련 주의:

- EXTI로 edge를 세는 것도 가능하지만, 고속 모터 엔코더는 보통 timer encoder mode가 더 적합하다.
- Timer encoder mode는 CPU interrupt 부담을 줄이고 모터 제어에서 더 안정적이다.

## 7. 클럭과 시작 동작

### 기본 클럭

Reset 후에는 16 MHz internal RC oscillator가 기본 CPU clock으로 선택된다.
데이터시트는 이 oscillator가 25도에서 1% 정확도로 factory-trimmed 되어 있다고
설명한다.

프로젝트 의미:

- 외부 clock 없이도 MCU가 시작할 수 있다.
- 초기 부팅과 간단한 펌웨어 테스트는 내부 oscillator로도 가능하다.

### 외부 클럭과 PLL

애플리케이션은 다음 중 하나를 system clock으로 선택할 수 있다.

- Internal RC oscillator
- External 4 MHz ~ 26 MHz clock source

외부 clock은 실패 여부를 감시할 수 있다. 실패가 감지되면 system은 internal RC
oscillator로 자동 복귀할 수 있고, 설정했다면 software interrupt도 발생시킬 수 있다.

PLL은 주파수를 최대 180 MHz까지 올릴 수 있다.

버스 주파수 한계:

- AHB maximum: 180 MHz
- APB2 maximum: 90 MHz
- APB1 maximum: 45 MHz

프로젝트 의미:

- PWM 주파수, UART baud rate, timer tick rate, control-loop period가 모두 clock 설정에 의존한다.
- Clock 설정이 틀리면 UART baud rate 또는 PWM timing이 틀어질 수 있다.

초기 결정:

- 먼저 CubeMX가 생성한 clock configuration을 사용한다.
- 실제 system clock, APB1, APB2 frequency를 펌웨어 문서에 기록한다.
- UART baud rate와 PWM frequency는 실제 테스트로 검증한다.

## 8. Boot Modes

디바이스는 다음 세 위치에서 boot할 수 있다.

1. User Flash
2. System memory
3. Embedded SRAM

Bootloader는 system memory에 위치하며, 다음 serial communication interface를
통해 Flash memory를 다시 programming할 수 있다.

- UART
- I2C
- CAN
- SPI
- USB

프로젝트 의미:

- 일반 펌웨어는 user Flash에서 boot한다.
- System bootloader는 일반 debug 경로가 막혔을 때 복구 또는 programming에 유용하다.
- SRAM boot는 특수 디버깅에 유용하지만 초기에는 필요 없다.

초기 결정:

- 일반 NUCLEO ST-LINK programming flow를 사용한다.
- Boot mode는 복구용 지식으로만 남긴다.

## 9. 이 로봇 아키텍처에 주는 영향

Section 3.1~3.14를 읽은 결과는 다음 초기 아키텍처 판단을 뒷받침한다.

1. STM32F446RE는 하위 제어에 충분한 연산 여유가 있다.
2. 초기 PID와 odometry 작업에서 부동소수점 연산을 사용해도 된다.
3. Interrupt는 시간 민감 이벤트를 조정하는 데 쓰되, handler는 짧게 유지해야 한다.
4. DMA는 유용하지만 실제 필요가 확인된 뒤 도입한다.
5. 모터 엔코더 counting은 EXTI보다 timer encoder mode를 우선 검토한다.
6. Timer와 USART는 clock 설정에 의존하므로 clock configuration을 기록해야 한다.
7. Bootloader 지식은 복구에는 유용하지만 MVP 설계의 중심은 아니다.

## 10. 다음 단계의 질문

다음 분석은 timers and watchdogs에 집중한다.

질문:

1. 어떤 timer가 PWM output을 지원하는가?
2. 어떤 timer가 encoder mode를 지원하는가?
3. 어떤 timer channel이 NUCLEO-F446RE에서 실제 사용 가능한 핀으로 나오는가?
4. 고정 주기 control loop는 어떤 timer로 실행할 것인가?
5. fail-safe recovery에는 어떤 watchdog을 사용할 것인가?
6. control-loop timing은 어떻게 측정하고 검증할 것인가?
