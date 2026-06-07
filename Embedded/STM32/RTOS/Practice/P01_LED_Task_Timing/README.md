# R01 LED Task Timing

## 목표

`vTaskDelayUntil()`을 사용해서 LED task를 일정 주기로 실행한다.

## 구현 과제

PA5 user LED를 500 ms 주기로 toggle한다.

```c
void LedTask(void *argument)
{
    TickType_t last_wake = xTaskGetTickCount();

    for (;;)
    {
        HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);
        vTaskDelayUntil(&last_wake, pdMS_TO_TICKS(500));
    }
}
```

## 확인 기준

- LED가 일정한 주기로 깜빡인다.
- `vTaskDelay()`와 `vTaskDelayUntil()`의 차이를 설명할 수 있다.
- task 안에서 `HAL_Delay()`를 쓰지 않는다.

## 프로젝트 연결

`motor_control_task`도 같은 방식으로 100 Hz 주기 실행을 목표로 한다.
