# GPIO Alternate Function and CubeMX

## 핵심 개념

STM32의 핀은 단순 GPIO뿐 아니라 UART, I2C, SPI, Timer channel 같은 peripheral 신호로도 사용할 수 있다.

핀을 peripheral에 연결하려면 두 단계를 설정한다.

1. `GPIOx->MODER`에서 해당 핀을 alternate function mode로 설정한다.
2. `GPIOx->AFR[]`에서 어떤 alternate function 번호를 쓸지 선택한다.

예를 들어 NUCLEO-F446RE에서 USART2를 PC serial로 쓸 때 일반 후보는 다음과 같다.

```text
PA2 -> USART2_TX -> AF7
PA3 -> USART2_RX -> AF7
```

## Direct Register 관점

PA2, PA3를 USART2로 쓰려면 개념적으로 다음 설정이 필요하다.

```c
RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
RCC->APB1ENR |= RCC_APB1ENR_USART2EN;

GPIOA->MODER &= ~((3u << (2 * 2)) | (3u << (3 * 2)));
GPIOA->MODER |=  ((2u << (2 * 2)) | (2u << (3 * 2)));

GPIOA->AFR[0] &= ~((0xFu << (2 * 4)) | (0xFu << (3 * 4)));
GPIOA->AFR[0] |=  ((7u   << (2 * 4)) | (7u   << (3 * 4)));
```

의미:

- `MODER = 10`: alternate function mode
- `AFR = 7`: AF7, USART2 연결
- `RCC`: GPIOA와 USART2 peripheral clock enable

## CubeMX/HAL 관점

CubeMX에서 `.ioc`에 `PA2 = USART2_TX`, `PA3 = USART2_RX`로 설정하면 보통 다음 흐름이 생성된다.

```text
main.c
  -> MX_GPIO_Init()
  -> MX_USART2_UART_Init()

stm32f4xx_hal_msp.c
  -> HAL_UART_MspInit()
     -> __HAL_RCC_GPIOA_CLK_ENABLE()
     -> __HAL_RCC_USART2_CLK_ENABLE()
     -> HAL_GPIO_Init(GPIOA, AF7 USART2)
```

CubeMX는 초기화 코드를 만들어주지만, ring buffer, protocol parser, fault handling 같은 application logic은 직접 작성해야 한다.

## 이 프로젝트에서의 사용

현재 후보:

- PC serial: `PA2 / PA3`, USART2
- ESP32 UART: `PA9 / PA10`, USART1
- IMU I2C: `PB8 / PB9`, I2C1
- motor PWM: `PB6 / PB7`, TIM4_CH1/CH2
- encoder: `PB4/PB5`, TIM3 and `PA0/PA1`, TIM5

## 디버깅 포인트

- GPIO clock을 켰는가?
- peripheral clock을 켰는가?
- MODER가 alternate function mode인가?
- AFR 번호가 맞는가?
- 해당 핀이 보드 header에 실제로 노출되어 있는가?
- ST-LINK, SWD, Arduino header 기능과 충돌하지 않는가?

## 포트폴리오 설명

> CubeMX로 핀맵을 먼저 검증한 뒤, GPIO alternate function이 실제로 `MODER`와 `AFR` 레지스터를 통해 peripheral에 연결된다는 것을 확인했다. UART, I2C, Timer PWM, Timer encoder 입력이 서로 충돌하지 않도록 STM32F446RE 핀 후보를 정리했다.
