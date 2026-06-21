# UART Interrupt and Ring Buffer

## 핵심 개념

UART RX interrupt는 byte가 도착했을 때 CPU가 ISR로 진입하게 하는 방식이다.

ISR에서는 오래 걸리는 parsing을 하지 않고, 받은 byte를 ring buffer에 넣은 뒤 즉시 빠져나오는 것이 기본이다.

```text
UART byte 도착
-> RXNE flag set
-> NVIC가 USART IRQ 전달
-> ISR 실행
-> DR 읽기
-> ring buffer push
-> main loop 또는 task에서 frame parsing
```

## ISR의 역할

ISR에서 해도 되는 일:

- 수신 레지스터 읽기
- byte를 ring buffer에 저장
- overflow counter 증가
- 짧은 flag set
- 다음 interrupt 수신 준비

ISR에서 피해야 할 일:

- 긴 문자열 parsing
- `printf`
- `delay`
- blocking I2C/SPI call
- 동적 메모리 할당
- 긴 CRC 계산이나 command 처리

## HAL 방식의 1-byte 수신 패턴

```c
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART2) {
        ring_buffer_push(&rx_buf, rx_byte);
        HAL_UART_Receive_IT(&huart2, &rx_byte, 1);
    }
}
```

의미:

- `ring_buffer_push`: 방금 받은 1 byte를 임시 저장한다.
- `HAL_UART_Receive_IT`: 다음 1 byte 수신 interrupt를 다시 건다.

HAL에서는 `HAL_UART_Receive_IT(..., 1)`이 1 byte 완료 후 끝나므로, callback에서 다시 호출해야 다음 byte를 받을 수 있다.

## Direct Register 방식의 개념 대응

```c
void USART2_IRQHandler(void)
{
    if (USART2->SR & USART_SR_RXNE) {
        uint8_t b = (uint8_t)USART2->DR;
        if (!rb_put(&rx_rb, b)) {
            drop_count++;
        }
    }
}
```

여기서 `DR`을 읽으면 RXNE flag가 clear된다.

## Ring Buffer가 필요한 이유

UART byte arrival timing과 application parsing timing은 다르다.

```text
생산자: ISR, byte가 들어올 때마다 저장
소비자: main loop 또는 comm_task, 자기 주기에 맞춰 꺼내서 parsing
```

ring buffer는 이 둘을 분리한다.

## 이 프로젝트에서의 사용

첫 UART protocol은 command와 telemetry를 분리한다.

예시:

```text
CMD,<seq>,<vx_mmps>,<w_mradps>,<crc>\n
TEL,<seq>,<state>,<left_cps>,<right_cps>,<fault>,<crc>\n
```

UART는 safety authority가 아니라 command request와 telemetry path다.
최종 motor permission은 STM32 state machine이 가진다.

## 디버깅 포인트

- ISR이 실제로 들어오는가?
- RXNE flag가 clear되는가?
- ring buffer overflow가 발생하는가?
- frame delimiter를 기준으로 parser가 안정적으로 동작하는가?
- invalid frame이 active command를 덮어쓰지 않는가?
- command timeout이 motor output을 zero로 만드는가?

## 포트폴리오 설명

> UART RX interrupt에서는 수신 byte를 ring buffer에 저장하는 최소 작업만 수행하고, frame parsing과 command validation은 main loop 또는 communication task에서 처리했다. 이를 통해 ISR latency를 줄이고, command timeout과 invalid frame 처리를 safety state machine과 연결했다.
