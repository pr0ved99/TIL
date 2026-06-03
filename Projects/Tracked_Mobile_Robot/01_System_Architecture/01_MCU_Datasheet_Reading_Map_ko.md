# STM32F446RE 데이터시트 읽기 지도

## 목적

이 문서는 궤도형 모바일 로봇 프로젝트를 위해 STM32F446xC/E 데이터시트를
어떤 순서와 관점으로 읽을지 기록한다.

목표는 MCU의 모든 기능을 요약하는 것이 아니다. 목표는 NUCLEO-F446RE를
모터 제어, 엔코더 입력, 배터리 전압 감시, 센서 인터페이스, PC/ESP32 통신을
담당하는 하위 제어기로 사용할 수 있는지에 대한 공학적 근거를 뽑아내는 것이다.

## 출처

- 데이터시트: `assets/stm32f446mc.pdf`
- 대상 디바이스 계열: STM32F446xC/E
- 프로젝트 보드: NUCLEO-F446RE
- 현재 읽기 단계: 목차(Contents)와 표 목록(List of tables)

## 데이터시트 읽는 방법

데이터시트는 교과서처럼 처음부터 끝까지 읽는 문서가 아니라, 필요한 정보를
찾기 위한 기준 문서로 읽어야 한다.

이 프로젝트의 1차 읽기에서는 다음 질문에 답해야 한다.

1. MCU가 PWM과 엔코더 입력에 필요한 타이머를 충분히 가지고 있는가?
2. UART, I2C, 향후 CAN까지 고려했을 때 통신 인터페이스가 충분한가?
3. 선택한 센서와 모터 드라이버 신호를 MCU에 안전하게 연결할 수 있는가?
4. ADC를 사용해 LiPo 배터리 전압을 감시할 수 있는가?
5. 보드를 손상시키지 않기 위해 지켜야 하는 전기적 한계는 무엇인가?

## 목차 구조

| 절 | 의미 | 프로젝트 관련성 |
| --- | --- | --- |
| 1. Introduction | 이 데이터시트가 다루는 디바이스 계열을 정의한다. | STM32F446RE가 이 데이터시트 범위에 포함되는지 확인한다. |
| 2. Description | 코어, 메모리, 주변장치 구성을 요약한다. | MCU가 프로젝트에 적절한지 판단하는 첫 근거다. |
| 3. Functional overview | MCU 내부 블록과 주변장치를 설명한다. | 타이머, ADC, UART, I2C, CAN, GPIO, DMA, watchdog 분석의 핵심 장이다. |
| 4. Pinout and pin description | 패키지 핀과 핀의 대체 기능을 나열한다. | 모터, 엔코더, 센서, 통신 핀을 배치할 때 사용한다. |
| 5. Memory mapping | Flash, SRAM, 주변장치 레지스터의 주소 배치를 보여준다. | 저수준 디버깅과 레지스터 수준 이해에 나중에 유용하다. |
| 6. Electrical characteristics | 전압, 전류, 타이밍, 동작 한계를 정의한다. | 안전한 배선과 인터페이스 설계에 매우 중요하다. |
| 7. Package information | 칩 패키지 치수와 열 특성을 제공한다. | NUCLEO 보드 사용 중에는 우선순위가 낮고, 추후 커스텀 PCB에서 중요하다. |
| 8. Part numbering | STM32 부품명 규칙을 설명한다. | 정확한 MCU 변형, Flash 크기, 패키지 옵션을 확인할 때 사용한다. |
| Appendix A | USB 응용 블록 다이어그램을 제공한다. | 초기 로봇 MVP에서는 우선순위가 낮다. |
| Revision history | 데이터시트 변경 이력을 기록한다. | 문서 버전을 비교할 때만 필요하다. |

## 프로젝트 기준 읽기 우선순위

### 먼저 반드시 읽을 부분

- Section 2: Description
- Section 3: Functional overview
- Section 4: Pinout and pin description
- Section 6: Electrical characteristics

이 절들은 아키텍처, 배선, 펌웨어 설계, 안전성과 직접 연결된다.

### 필요할 때 읽을 부분

- Section 5: Memory mapping
- Section 7: Package information
- Section 8: Part numbering
- Appendix A

이 부분들도 유용하지만, 초기 MVP에서 가장 먼저 막히는 지점은 아니다.

## Functional Overview에서 집중할 항목

Section 3은 범위가 넓기 때문에, 실제 로봇 기능으로 연결되는 주변장치에
집중해야 한다.

| 데이터시트 항목 | 쉬운 의미 | 로봇에서의 용도 |
| --- | --- | --- |
| Cortex-M4 / FPU | CPU 코어와 부동소수점 연산 장치. | 제어 루프와 속도/odometry 계산을 수행한다. |
| Flash / SRAM | 프로그램 저장 메모리와 실행 중 사용하는 메모리. | 펌웨어와 실행 중 변수들을 저장한다. |
| DMA | CPU 대신 데이터를 옮기는 하드웨어 장치. | 나중에 ADC, UART, SPI 데이터를 효율적으로 처리할 때 유용하다. |
| NVIC / EXTI | 인터럽트 제어기와 외부 인터럽트 라인. | 엔코더 에지, 비상 입력, 시간 민감 이벤트 처리에 사용한다. |
| Clocks | MCU의 시간 기준과 주파수 구조. | PWM 주파수, UART baud rate, 제어 루프 주기에 영향을 준다. |
| Boot modes | 전원이 켜질 때 어떤 방식으로 시작할지 정하는 기능. | 펌웨어 업로드 실패 시 복구와 디버깅에 필요하다. |
| Timers | 하드웨어 카운터와 파형 생성기. | PWM 출력, 엔코더 모드, 주기적 제어 루프에 사용한다. |
| Watchdogs | 펌웨어가 멈췄을 때 리셋하는 안전 장치. | 로봇 정지/복구용 fail-safe에 사용한다. |
| I2C | 두 선으로 통신하는 센서 버스. | BNO08x IMU 연결 후보 인터페이스다. |
| USART/UART | 직렬 통신 장치. | PC, ESP32, 디버그 콘솔, 명령 프로토콜에 사용한다. |
| bxCAN | CAN 통신 컨트롤러. | 향후 더 견고한 로봇 내부 버스로 확장할 때 사용한다. |
| GPIO | 디지털 입력/출력 핀. | 모터 드라이버 방향/enable, 스위치, 상태 입력에 사용한다. |
| ADC | 아날로그 전압을 디지털 값으로 바꾸는 장치. | 저항 분배 회로를 통한 LiPo 전압 감시에 사용한다. |
| SWD/JTAG | 디버깅과 프로그래밍 인터페이스. | ST-LINK 디버깅과 펌웨어 업로드에 사용한다. |

## 초기 MVP에서 우선순위가 낮은 기능

다음 기능들은 MCU가 제공하는 유효한 기능이지만, 초기 궤도 로봇 MVP의
핵심은 아니다.

- FMC, PSRAM, SDRAM, QuadSPI
- I2S, SAI, SPDIF-RX, audio PLL
- HDMI CEC
- SDIO
- USB OTG HS
- DCMI camera interface
- DAC
- RTC calendar 기능

프로젝트 범위가 확장될 때만 다시 검토한다.

## 중요한 표

표 목록은 중요하다. 설계 결정은 설명 문장뿐 아니라 숫자 근거를 바탕으로
해야 하기 때문이다.

| 표 | 중요한 이유 |
| --- | --- |
| Table 2. STM32F446xC/E features and peripheral counts | 타이머, ADC, UART, I2C, CAN, 메모리 크기, 패키지 옵션의 개수를 확인한다. |
| Table 6. Timer feature comparison | 어떤 타이머를 PWM, 입력 캡처, 출력 비교, 엔코더 관련 기능에 쓸 수 있는지 판단한다. |
| Table 7. Comparison of I2C analog and digital filters | IMU 배선에서 I2C 통신 안정성을 검토할 때 유용하다. |
| Table 8. USART feature comparison | PC, ESP32, 디버그 링크에 사용할 UART/USART를 고를 때 참고한다. |
| Table 10. Pin and ball descriptions | 물리 핀과 사용 가능한 신호를 매핑한다. |
| Table 11. Alternate function | 각 핀에 어떤 주변장치 기능을 배정할 수 있는지 보여준다. |
| Table 13. Voltage characteristics | 넘기면 안 되는 전압 한계를 정의한다. |
| Table 14. Current characteristics | 넘기면 안 되는 전류 한계를 정의한다. |
| Table 16. General operating conditions | 정상 동작 전압과 온도 조건을 정의한다. |
| Table 56. I/O static characteristics | 로직 레벨 기준과 5V tolerant I/O 동작을 확인한다. |
| Table 60. TIMx characteristics | 타이머 관련 타이밍 한계를 확인한다. |
| Table 61. I2C characteristics | I2C 장치의 전기적/타이밍 제약을 확인한다. |
| Table 63. SPI dynamic characteristics | 나중에 SPI 센서, 디스플레이, 저장장치를 추가할 경우 유용하다. |
| Table 76. ADC characteristics | 배터리 전압 측정 정확도와 ADC 입력 조건을 검토할 때 중요하다. |
| Table 86. VBAT monitoring characteristics | 나중에 VBAT 관련 감시가 필요해질 경우 참고한다. |

## 이 단계의 읽기 결과

목차와 표 목록을 보면 데이터시트는 프로젝트 중심 순서로 읽어야 한다.

1. MCU 기본 능력 확인: Section 2와 Table 2.
2. 로봇 관련 주변장치 확인: Section 3과 Tables 6, 7, 8.
3. 실제 핀 배치: Section 4와 Tables 10, 11.
4. 전기적 안전 검증: Section 6과 Tables 13, 14, 16, 56, 60, 61, 76.

이 정도면 다음 읽기 단계로 넘어갈 수 있다.

## 다음 읽기 단계

다음 대상:

- Section 1: Introduction
- Section 2: Description
- Table 2: STM32F446xC/E features and peripheral counts

다음 단계에서 답해야 할 질문:

1. STM32F446RE가 이 보드의 정확한 대상 부품인가?
2. 사용 가능한 Flash와 SRAM은 어느 정도인가?
3. 이 로봇에 필요한 주변장치가 충분한 수량으로 제공되는가?
4. 지금 유용한 기능과 나중으로 미룰 기능은 무엇인가?
5. STM32F446RE를 하위 제어기로 사용하는 근거는 무엇인가?
