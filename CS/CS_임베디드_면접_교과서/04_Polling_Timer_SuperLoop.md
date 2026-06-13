# Polling, Timer, Super Loop

## 분야

- 임베디드 펌웨어 구조
- 센서 샘플링
- 주기적 작업 스케줄링

## 관련 면접 질문

- polling은 무엇인가?
- interrupt와 polling 중 센서 입력 처리에 무엇을 선택할 것인가?
- super loop 구조는 무엇인가?

## 선수지식

- while loop
- GPIO read
- timer
- 센서 샘플링 주기

## 핵심 개념

Polling은 CPU가 주기적으로 상태를 확인하는 방식입니다.

```c
while (1) {
    if (button_is_pressed()) {
        handle_button();
    }
}
```

이 코드는 button이 눌렸는지 계속 확인합니다. 이벤트가 없어도 계속 확인한다는 점이 interrupt와 다릅니다.

## Polling의 장점

- 구현이 단순합니다.
- 코드 흐름이 직관적입니다.
- 디버깅이 쉽습니다.
- 주기적 센서 읽기에 적합합니다.

예를 들어 온도 센서나 배터리 전압처럼 빠르게 변하지 않는 값은 100ms 또는 1초마다 polling으로 읽어도 충분할 수 있습니다.

## Polling의 단점

- CPU가 불필요하게 상태를 확인할 수 있습니다.
- 이벤트 발생 시점과 확인 시점 사이에 지연이 생깁니다.
- loop 안의 다른 작업이 길어지면 sampling 주기가 흔들릴 수 있습니다.

## Timer 기반 Polling

단순히 while loop에서 계속 읽는 것보다, timer를 기준으로 주기를 맞추는 것이 좋습니다.

```c
uint32_t last_tick = 0;

while (1) {
    if (millis() - last_tick >= 100) {
        last_tick = millis();
        read_sensor();
    }
}
```

이 구조는 100ms마다 센서를 읽는 형태입니다.

## Super Loop

Super loop는 RTOS 없이 main loop 하나에서 여러 작업을 순서대로 처리하는 구조입니다.

```c
while (1) {
    read_sensor_if_time();
    process_uart_if_received();
    update_motor_control();
    refresh_watchdog();
}
```

작은 MCU 프로젝트에서 흔히 사용합니다. 구조가 단순하지만, 작업 시간이 길어지면 전체 응답성이 떨어질 수 있습니다.

## Interrupt와 Polling 선택 기준

| 상황 | 추천 방식 |
| --- | --- |
| UART 수신 | interrupt 또는 DMA |
| 버튼 입력 | interrupt 또는 debounce polling |
| 온도/거리 센서 주기 측정 | timer 기반 polling |
| encoder pulse | interrupt 또는 timer encoder mode |
| control loop | timer interrupt 또는 RTOS periodic task |

## 면접 답변으로 연결

### 30초 답변

> Polling은 CPU가 주기적으로 상태를 확인하는 방식이고, interrupt는 이벤트가 발생했을 때 CPU에 알려주는 방식입니다. 센서가 일정 주기로 읽어도 되는 값이라면 timer 기반 polling이 적합하고, UART 수신이나 encoder pulse처럼 비동기적이고 놓치면 안 되는 이벤트는 interrupt가 적합합니다. 실제 시스템에서는 둘을 섞어 쓰는 경우가 많습니다.

## 내 프로젝트로 연결하는 문장

> 장비 상태 모니터링용 ADC/GPIO는 100ms timer 주기로 polling하고, UART 수신은 interrupt로 받는 방식처럼 입력 특성에 따라 나누어 설계할 수 있습니다.

