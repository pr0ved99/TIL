# STM32F446RE 타이머와 Watchdog 분석

## 목적

이 문서는 궤도형 모바일 로봇 프로젝트를 위해 STM32F446xC/E 데이터시트의
타이머와 watchdog 부분을 분석한다.

범위:

- Section 3.21: Timers and watchdogs
- Section 3.21.1: Advanced-control timers
- Section 3.21.2: General-purpose timers
- Section 3.21.3: Basic timers
- Section 3.21.4: Independent watchdog
- Section 3.21.5: Window watchdog
- Section 3.21.6: SysTick timer
- Table 6: Timer feature comparison

목표는 어떤 타이머 자원을 모터 PWM, 엔코더 입력, 고정 주기 제어 루프,
fail-safe 동작에 사용할 수 있는지 이해하는 것이다.

## 1. 이 로봇에서 타이머가 중요한 이유

타이머는 이 프로젝트에서 가장 중요한 MCU 주변장치 중 하나다.

타이머에 의존하는 로봇 기능:

- 모터 속도 제어를 위한 PWM 생성
- 바퀴 속도 추정을 위한 엔코더 counting
- 고정 주기 control loop 실행
- 필요 시 input capture 또는 output compare
- 주기적인 ADC sampling 또는 diagnostic timing
- 펌웨어 이상 시 watchdog reset

타이머를 잘못 배정하면 코드는 컴파일되고 로봇도 움직일 수 있지만, 제어가
불안정하거나 jitter가 커지고 디버깅이 어려워질 수 있다.

## 2. STM32F446RE의 타이머 그룹

데이터시트는 타이머를 다음 그룹으로 나눈다.

| 타이머 그룹 | 타이머 | 핵심 의미 |
| --- | --- | --- |
| Advanced-control timers | TIM1, TIM8 | 모터 제어형 PWM에 적합한 고기능 타이머. |
| Full-featured general-purpose timers | TIM2, TIM3, TIM4, TIM5 | PWM, input capture, output compare, encoder signal에 쓰는 범용 타이머. |
| Simpler general-purpose timers | TIM9, TIM10, TIM11, TIM12, TIM13, TIM14 | 단순 PWM, output compare, input capture, time-base 작업에 유용한 타이머. |
| Basic timers | TIM6, TIM7 | 단순 16-bit time-base 타이머. DAC trigger나 주기 이벤트에 사용. |
| Watchdog timers | IWDG, WWDG | 펌웨어가 정상적으로 refresh하지 못하면 MCU를 reset하는 안전 타이머. |
| SysTick | Cortex-M system timer | OS tick이나 단순 주기 interrupt에 자주 쓰는 24-bit downcounter. |

## 3. Table 6 요약

Table 6은 타이머별 기능 차이를 비교한다.

중요한 관찰:

- TIM1과 TIM8은 16-bit advanced-control timer다.
- TIM1과 TIM8은 complementary output과 DMA request generation을 지원한다.
- TIM2와 TIM5는 32-bit general-purpose timer다.
- TIM3과 TIM4는 16-bit full-featured general-purpose timer다.
- TIM2, TIM3, TIM4, TIM5는 각각 4개 capture/compare channel을 가진다.
- TIM2, TIM3, TIM4, TIM5는 quadrature incremental encoder signal을 처리할 수 있다.
- TIM6과 TIM7은 capture/compare channel이 없으므로 time-base timer로 보는 것이 적절하다.
- TIM9/TIM12는 2개 channel을 가진다.
- TIM10/TIM11/TIM13/TIM14는 1개 channel을 가진다.
- 모든 timer counter는 debug mode에서 freeze할 수 있다.

## 4. Advanced-Control Timers: TIM1과 TIM8

TIM1과 TIM8은 advanced-control timer다.

데이터시트상 기능:

- 16-bit counter
- Up, down, up/down counting
- 4개 독립 channel
- Input capture
- Output compare
- PWM generation
- One-pulse mode
- Complementary PWM output
- Programmable dead time
- DMA request generation
- 다른 timer와 Timer Link synchronization 가능

### 프로젝트 의미

TIM1과 TIM8은 모터 PWM 생성의 강한 후보군이다.

이 궤도 로봇의 모터 드라이버는 대체로 다음 신호가 필요할 가능성이 높다.

- 왼쪽 모터 PWM
- 오른쪽 모터 PWM
- 왼쪽 방향 제어 GPIO
- 오른쪽 방향 제어 GPIO
- 선택적으로 enable 또는 brake GPIO

모터 드라이버가 모터 하나당 PWM 하나만 요구한다면 TIM1 또는 TIM8은 충분히
여유 있는 PWM channel을 제공한다.

### Complementary Output과 Dead Time

Complementary PWM은 서로 짝이 되는 PWM 출력을 만드는 기능이다. 보통
half-bridge 또는 3상 모터 제어 회로에서 사용한다.

Dead time은 서로 보완 관계인 transistor가 동시에 켜지지 않도록 짧은 지연을
넣는 기능이다.

프로젝트 결정:

- 완성된 DC motor driver module을 사용한다면 complementary PWM과 dead time은
  보통 필요 없다.
- 나중에 MOSFET bridge를 직접 설계한다면 TIM1/TIM8의 중요도가 크게 올라간다.

## 5. Full-Featured General-Purpose Timers: TIM2, TIM3, TIM4, TIM5

이 타이머들은 엔코더와 일반 제어 작업에서 가장 중요한 후보군이다.

데이터시트상 기능:

- TIM2와 TIM5: 32-bit counter
- TIM3과 TIM4: 16-bit counter
- 16-bit prescaler
- Up, down, up/down counting
- 각 타이머별 4개 독립 channel
- Input capture
- Output compare
- PWM generation
- One-pulse mode
- Timer Link synchronization
- DMA request generation
- Quadrature incremental encoder signal 처리 가능
- Hall sensor digital output 처리 가능

### 프로젝트 의미

모터 엔코더에는 TIM2, TIM3, TIM4, TIM5가 1차 후보군이다.

GPIO interrupt로 엔코더 edge를 직접 세는 방식보다 hardware timer encoder
mode를 우선하는 것이 좋다.

이유:

- CPU interrupt 부담을 줄인다.
- 높은 edge rate를 더 안정적으로 처리한다.
- 속도 추정의 timing이 더 결정적이다.
- NVIC 자원을 통신과 안전 이벤트에 남겨둘 수 있다.

### 32-bit와 16-bit timer 차이

TIM2와 TIM5는 32-bit이고, TIM3과 TIM4는 16-bit다.

쉽게 보면:

- 32-bit timer는 overflow 전까지 훨씬 더 많이 셀 수 있다.
- 16-bit timer는 더 빨리 overflow되므로 sampling 주기와 overflow 처리를 더 신경 써야 한다.

로봇에서의 의미:

- TIM2와 TIM5는 엔코더 counter로 매력적인 후보이다.
- TIM3과 TIM4도 고정 주기로 count 차이를 읽고 wraparound를 처리하면 사용할 수 있다.
- 최종 선택은 timer 기능뿐 아니라 실제 사용 가능한 핀에 의해 결정된다.

## 6. 더 단순한 General-Purpose Timers

TIM9, TIM10, TIM11, TIM12, TIM13, TIM14는 더 단순한 16-bit timer다.

기능:

- TIM9와 TIM12는 2개 channel을 가진다.
- TIM10, TIM11, TIM13, TIM14는 1개 channel을 가진다.
- 타이머에 따라 input capture, output compare, PWM, one-pulse mode, simple
  time-base task에 사용할 수 있다.

프로젝트 후보 용도:

- 추가 PWM 출력
- 상태 LED timing
- 주기적 diagnostic
- 단순 timeout 생성
- 중요도가 낮은 input capture

초기 결정:

- 처음부터 이 타이머들을 우선 배정하지 않는다.
- 모터 PWM, 엔코더, 제어 루프 timing을 배정한 뒤 spare timer로 남긴다.

## 7. Basic Timers: TIM6과 TIM7

TIM6과 TIM7은 basic 16-bit timer다.

데이터시트 핵심:

- 주로 DAC trigger와 waveform generation에 사용
- generic 16-bit time base로도 사용 가능
- DMA request generation 지원
- capture/compare channel 없음

프로젝트 의미:

- 고정 주기 software timing에 좋은 후보이다.
- capture/compare 기능이 필요 없는 control-loop tick에 사용할 수 있다.
- 배터리 전압 sampling이나 diagnostic 같은 주기 작업에도 사용할 수 있다.

초기 후보:

- TIM6: 고정 주기 motor control loop timer
- TIM7: 더 느린 diagnostic 또는 ADC sampling time base

이는 예비 배정일 뿐이다. 최종 선택은 CubeMX, HAL 사용 방식, 라이브러리 충돌을
확인한 뒤 정해야 한다.

## 8. Watchdogs

Watchdog은 안전용 주변장치다. 펌웨어가 정상적으로 동작하지 않을 때 MCU를
reset한다.

### Independent Watchdog: IWDG

Independent watchdog은 다음을 기반으로 한다.

- 12-bit downcounter
- 8-bit prescaler
- 독립 32 kHz internal RC clock
- main system clock과 독립적으로 동작
- Stop mode와 Standby mode에서도 동작 가능
- option bytes를 통해 hardware 또는 software 설정 가능

프로젝트 의미:

- IWDG는 main clock에 의존하지 않기 때문에 더 강한 fail-safe watchdog이다.
- 펌웨어가 멈추면 watchdog이 MCU를 reset할 수 있다.

중요한 안전 주의:

- MCU reset은 로봇을 능동적으로 제동하는 것과 같지 않다.
- Motor driver enable pin은 reset 중에도 출력이 꺼지도록 pull-down 같은 안전 기본 상태를 가져야 한다.
- MCU가 reboot되는 동안 motor power stage가 계속 모터를 구동하면 안 된다.

초기 결정:

- 기본 모터 제어가 안정화된 뒤 IWDG를 추가한다.
- 너무 일찍 켜면 디버깅이 어려워질 수 있다.

### Window Watchdog: WWDG

Window watchdog은 다음을 기반으로 한다.

- 7-bit downcounter
- main clock
- early warning interrupt
- debug freeze 지원

프로젝트 의미:

- WWDG는 watchdog refresh가 너무 이르거나 너무 늦은 timing fault를 감지할 수 있다.
- 단순 timeout watchdog보다 더 엄격하다.

초기 결정:

- 초기 MVP에는 WWDG가 필요하지 않다.
- 첫 watchdog으로는 IWDG가 더 단순하고 유용하다.

### SysTick Timer

SysTick은 Cortex-M system timer다.

데이터시트 핵심:

- 24-bit downcounter
- autoreload capability
- counter가 0에 도달하면 maskable interrupt 생성
- programmable clock source
- RTOS나 HAL timing에 자주 사용

프로젝트 의미:

- HAL은 보통 SysTick을 millisecond timing에 사용한다.
- 단순 delay나 scheduling에 사용할 수 있다.
- dedicated hardware timer가 있다면 고품질 motor-control timing의 중심으로 쓰는 것은 피하는 편이 좋다.

초기 결정:

- SysTick은 HAL/system tick 용도로 둔다.
- Motor control loop는 별도 TIMx timer를 사용한다.

## 9. 예비 타이머 배정안

이 배정은 최종안이 아니다. CubeMX와 pinout 검증을 위한 출발점이다.

| 로봇 기능 | 우선 타이머 후보 | 이유 |
| --- | --- | --- |
| 좌/우 모터 PWM | TIM1 또는 TIM8 | Advanced-control timer이며 여러 PWM channel 제공. |
| 왼쪽 엔코더 | TIM2 또는 TIM5 | 32-bit, full-featured, quadrature encoder signal 지원. |
| 오른쪽 엔코더 | TIM5 또는 TIM2 | 32-bit, full-featured, quadrature encoder signal 지원. |
| 엔코더 예비 후보 | TIM3 또는 TIM4 | Encoder-capable full-featured timer, 16-bit. |
| 고정 주기 control loop | TIM6 또는 TIM7 | Time base 용도로 충분한 basic timer. |
| 배터리 sampling tick | TIM7 또는 spare timer | 저속 주기 작업에 적합. |
| 추가 PWM/debug timing | TIM9-TIM14 | 보조 기능용으로 reserve. |
| System millisecond tick | SysTick | 보통 HAL이 사용. |
| 펌웨어 hang recovery | IWDG | 독립 watchdog clock 사용. |

## 10. 위험 요소와 확인 사항

### Pin Conflict

타이머 기능이 있다고 해서 실제 핀을 사용할 수 있다는 뜻은 아니다.

필수 확인:

- 선택한 timer channel이 NUCLEO에서 접근 가능한 핀으로 나오는가?
- ST-LINK, user button, LED, Arduino header, Morpho header 사용과 충돌하지 않는가?
- 좌/우 엔코더 channel이 각각 같은 timer의 CH1/CH2로 구성 가능한가?

### PWM Frequency

PWM frequency는 다음에 의해 결정된다.

- Timer input clock
- Prescaler
- Auto-reload value
- Counting mode

필수 확인:

- 모터 드라이버에 적합한 PWM frequency를 선택한다.
- 가능하면 가청 소음을 피한다.
- Duty-cycle 제어에 충분한 timer resolution을 유지한다.

### Encoder Overflow

Encoder counter는 overflow될 수 있다.

위험:

- 16-bit timer는 32-bit timer보다 훨씬 빨리 overflow된다.

대응:

- 핀이 허용한다면 TIM2/TIM5를 encoder에 우선 사용한다.
- 16-bit timer를 쓴다면 count difference를 자주 읽고 wraparound를 올바르게 처리한다.

### Watchdog Reset Safety

Watchdog reset은 안전한 모터 상태로 이어져야 한다.

필수 확인:

- Motor driver enable pin의 기본 상태가 안전한가?
- PWM pin reset state가 모터를 의도치 않게 구동하지 않는가?
- Firmware initialization 단계에서 control을 켜기 전에 motor를 disable하는가?

## 11. 1차 설계 결정

STM32F446RE의 타이머 자원은 궤도 로봇 MVP에 충분하다.

추천 설계 방향:

1. 고정 주기 control loop에는 전용 hardware timer를 사용한다.
2. 모터 엔코더에는 hardware timer encoder mode를 사용한다.
3. 핀 배치가 허용하면 PWM에는 TIM1 또는 TIM8을 우선 검토한다.
4. SysTick은 HAL/system timing 용도로 둔다.
5. IWDG는 기본 모터 제어가 안정화된 뒤 추가한다.
6. 펌웨어 확정 전에 CubeMX와 NUCLEO-F446RE pinout에서 모든 선택을 검증한다.

## 12. 다음 단계

다음 문서는 communication and I/O peripherals를 분석한다.

- BNO08x IMU용 I2C
- PC와 ESP32 통신용 USART/UART
- 후순위 확장용 bxCAN
- 모터 드라이버와 안전 신호용 GPIO
- 배터리 전압 감시용 ADC

통신과 I/O 분석 이후에는 첫 번째 pin-allocation table을 만들어야 한다.
