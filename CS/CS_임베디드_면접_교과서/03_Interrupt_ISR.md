# Interrupt와 ISR

## 분야

- 임베디드 시스템
- MCU 주변장치 제어
- 실시간 입력 처리

## 관련 면접 질문

- interrupt와 polling의 차이는?
- 센서 입력 처리에서 interrupt를 쓰는 경우는?
- ISR 안에서 주의할 점은?

## 선수지식

- CPU가 명령을 순차적으로 실행한다는 개념
- GPIO, UART 같은 주변장치
- 함수 호출
- flag 변수
- `volatile`

## 핵심 개념

Interrupt는 CPU가 메인 코드를 실행하고 있다가, 외부 이벤트나 주변장치 이벤트가 발생했을 때 현재 흐름을 잠시 멈추고 정해진 처리 루틴을 실행하는 방식입니다. 이때 실행되는 함수가 ISR입니다.

```text
main loop 실행
     |
     | UART 수신 발생
     v
ISR 실행
     |
     v
main loop 복귀
```

## Interrupt가 필요한 상황

Interrupt는 이벤트가 언제 들어올지 모르는 경우에 유용합니다.

- UART 데이터 수신
- 버튼 입력
- 외부 센서의 data ready 신호
- timer overflow
- encoder pulse

예를 들어 UART 수신은 데이터가 언제 들어올지 모르기 때문에 CPU가 계속 확인하는 것보다 interrupt로 받는 편이 효율적입니다.

## ISR에서 주의할 점

ISR은 짧고 빠르게 끝나야 합니다.

ISR 안에서 오래 걸리는 일을 하면 다음 문제가 생깁니다.

- 다른 interrupt 처리가 늦어집니다.
- main loop나 RTOS task 실행이 밀립니다.
- 제어 주기가 흔들립니다.
- 디버깅이 어려워집니다.

좋은 방식은 ISR에서 최소한의 일만 하고, 실제 처리는 main loop나 task에서 하는 것입니다.

```c
volatile bool uart_rx_ready = false;

void USART_IRQHandler(void)
{
    // 받은 byte를 buffer에 저장
    uart_rx_ready = true; // 처리할 일이 생겼다는 flag만 세움
}

int main(void)
{
    while (1) {
        if (uart_rx_ready) {
            uart_rx_ready = false;
            // 실제 parsing 처리
        }
    }
}
```

## `volatile`이 필요한 이유

ISR과 main loop가 같은 변수를 공유할 때 compiler가 최적화로 값을 잘못 가정하지 않도록 `volatile`을 붙입니다.

```c
volatile bool button_pressed = false;
```

`volatile`은 "이 변수는 코드 흐름 밖에서 바뀔 수 있으니 매번 메모리에서 읽어라"라는 의미입니다.

단, `volatile`은 동시성 문제를 완전히 해결하지 않습니다. 여러 byte 변수나 복잡한 구조체를 공유하면 critical section이나 mutex가 필요할 수 있습니다.

## Interrupt Priority

MCU에서는 interrupt마다 우선순위를 줄 수 있습니다. 더 중요한 interrupt가 덜 중요한 interrupt보다 먼저 처리됩니다.

예를 들어 motor control timer interrupt는 높은 우선순위를, debug UART interrupt는 낮은 우선순위를 줄 수 있습니다.

## 면접 답변으로 연결

### 30초 답변

> Interrupt는 이벤트가 발생했을 때 CPU가 현재 작업을 멈추고 ISR을 실행하는 방식입니다. UART 수신, 버튼 입력, encoder pulse처럼 언제 발생할지 모르는 입력에 적합합니다. 다만 ISR 안에서 오래 걸리는 parsing이나 연산을 하면 다른 작업이 밀릴 수 있으므로, ISR에서는 buffer 저장이나 flag 설정만 하고 실제 처리는 main loop나 RTOS task에서 하는 것이 좋습니다.

## 내 프로젝트로 연결하는 문장

> STM32에서 UART 수신을 처리한다면 RX interrupt나 DMA를 사용해 수신 데이터를 buffer에 넣고, main loop나 통신 task에서 delimiter 기준으로 parsing하는 구조가 적절하다고 설명할 수 있습니다.

