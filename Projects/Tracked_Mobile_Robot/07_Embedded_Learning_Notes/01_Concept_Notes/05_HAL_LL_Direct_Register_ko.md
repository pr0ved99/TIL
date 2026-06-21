# HAL, LL, Direct Register 접근 전략

## 세 계층

STM32 firmware는 보통 다음 계층으로 접근할 수 있다.

| 방식 | 예시 | 특징 |
| --- | --- | --- |
| HAL | `HAL_UART_Init()` | 추상화 높음, bring-up 빠름 |
| LL | `LL_USART_Enable()` | 레지스터에 가까운 ST low-layer API |
| Direct Register | `USART2->CR1 |= ...` | 레지스터를 직접 제어 |

## HAL

장점:

- CubeMX와 잘 맞는다.
- clock, GPIO, peripheral 초기화 실수가 줄어든다.
- 빠르게 보드 bring-up하기 좋다.

단점:

- 내부 레지스터 동작이 덜 보인다.
- 일부 hot path에서는 오버헤드가 크다.

## LL

LL은 HAL보다 얇은 ST 제공 low-layer API다.

```c
LL_GPIO_SetPinMode(GPIOA, LL_GPIO_PIN_2, LL_GPIO_MODE_ALTERNATE);
LL_USART_EnableIT_RXNE(USART2);
```

레지스터를 직접 만지는 것보다 안전하고, HAL보다 명시적이다.

## Direct Register

```c
GPIOA->MODER |= ...
USART2->CR1 |= ...
TIM4->CCR1 = duty;
GPIOC->BSRR = GPIO_BSRR_BS8;
```

장점:

- 어떤 bit를 바꾸는지 명확하다.
- ISR 또는 motor output hot path에서 빠르고 예측 가능하다.
- reference manual 학습에 좋다.

주의:

- clock enable, reset state, reserved bit, read-modify-write 위험을 직접 책임져야 한다.
- 모든 기능을 direct register로 쓰면 유지보수가 어려울 수 있다.

## 이 프로젝트의 권장 전략

```text
Phase 1: CubeMX/HAL로 peripheral bring-up
Phase 2: 동작 확인 후 timing-critical path만 LL 또는 direct register로 전환
Phase 3: 전환 이유, 측정값, 유지할 HAL 영역을 문서화
```

우선 전환 후보:

- `TIMx->CNT` encoder read
- `TIMx->CCR` PWM duty update
- `GPIOx->BSRR` DIR pin set/reset
- UART RX ISR의 최소 처리
- safety stop 시 motor output zero

HAL 유지 후보:

- 초기 clock tree
- 복잡한 I2C sensor bring-up
- 첫 ADC/UART 검증
- FreeRTOS integration 초기 단계

## 포트폴리오 설명

> 초기 bring-up은 CubeMX/HAL로 안정적으로 진행하고, 이후 제어 주기와 안전 응답성이 중요한 motor output, encoder counter read, UART RX ISR은 LL 또는 direct register 접근으로 분리했다. 이를 통해 개발 속도와 실시간성을 균형 있게 가져갔다.
