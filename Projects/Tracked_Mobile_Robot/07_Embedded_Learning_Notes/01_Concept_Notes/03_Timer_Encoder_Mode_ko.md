# Timer Encoder Mode

## 핵심 개념

STM32 Timer Encoder Mode는 A/B quadrature encoder 신호를 CPU interrupt로 직접 세지 않고, timer hardware가 자동으로 count하게 하는 기능이다.

```text
Encoder A -> TIMx_CH1
Encoder B -> TIMx_CH2
          -> input filter
          -> edge detector
          -> quadrature decoder
          -> TIMx->CNT 증가/감소
```

CPU는 매 edge마다 개입하지 않고, 주기적으로 `CNT` 값을 읽어 속도와 이동량을 계산한다.

## A/B Quadrature 원리

정방향 예시:

```text
AB: 00 -> 10 -> 11 -> 01 -> 00
```

역방향 예시:

```text
AB: 00 -> 01 -> 11 -> 10 -> 00
```

Timer 내부 decoder는 이전 A/B 상태와 현재 A/B 상태의 전이 순서를 보고 방향을 판단한다.

## 왜 GPIO Interrupt보다 좋은가

- encoder edge rate가 높아도 CPU interrupt 부담이 작다.
- 방향 판단을 hardware가 처리한다.
- control loop는 일정 주기로 count delta만 읽으면 된다.
- NVIC 자원을 UART, timer tick, safety event에 남겨둘 수 있다.

## 속도 계산

```text
current_count = TIMx->CNT
delta_count = current_count - previous_count
counts_per_second = delta_count / sample_time
rpm = counts_per_second / counts_per_rev * 60
```

제어 loop가 10 ms라면 10 ms마다 count delta를 계산한다.

## 이 프로젝트에서의 후보

```text
Left encoder A/B:
PB4 / PB5 -> TIM3_CH1 / TIM3_CH2

Right encoder A/B:
PA0 / PA1 -> TIM5_CH1 / TIM5_CH2
```

TIM5는 32-bit라 overflow 여유가 크다.
TIM3은 16-bit라 sampling 주기와 wraparound 처리를 신경 써야 한다.

## 디버깅 포인트

- encoder output voltage가 STM32 input limit 안에 있는가?
- A/B 상이 반대로 연결되지 않았는가?
- forward command에서 count sign이 기대와 맞는가?
- timer counter overflow 또는 wraparound를 처리했는가?
- input filter 설정이 너무 강해서 정상 pulse를 놓치지 않는가?
- 모터 noise가 encoder line에 들어오지 않는가?

## 포트폴리오 설명

> 좌우 모터의 A/B quadrature 신호를 STM32 timer encoder mode로 하드웨어 카운팅하고, 10 ms 제어 주기마다 count delta를 읽어 속도와 odometry 입력으로 변환했다. GPIO interrupt 방식 대신 timer hardware를 사용해 CPU 부하와 edge loss 가능성을 줄였다.
