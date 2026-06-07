# R04 UART Log Mutex

## 목표

여러 task가 UART log를 동시에 출력할 때 문자열이 섞이지 않도록 보호한다.

## 구조

```text
task A ----+
          +-> uart_log_mutex -> HAL_UART_Transmit()
task B ----+
```

## 구현 방향

간단한 실습에서는 mutex로 UART 출력 구간을 보호한다.

```c
if (xSemaphoreTake(uart_mutex, pdMS_TO_TICKS(10)) == pdTRUE) {
    HAL_UART_Transmit(&huart2, data, len, 100);
    xSemaphoreGive(uart_mutex);
}
```

## 확인 기준

- 여러 task 로그가 한 줄 안에서 섞이지 않는다.
- mutex timeout을 둔다.
- ISR에서 mutex를 사용하지 않는다.

## 프로젝트 연결

실제 firmware에서는 telemetry/log 전용 task를 두고 다른 task가 queue로 log event를 보내는 구조가 더 안전하다.
