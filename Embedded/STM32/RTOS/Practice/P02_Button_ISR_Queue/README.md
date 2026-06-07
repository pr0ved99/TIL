# R02 Button ISR To Queue

## 목표

버튼 interrupt에서 직접 처리하지 않고, queue를 통해 task로 event를 넘긴다.

## 구조

```text
Button EXTI ISR
-> xQueueSendFromISR()
-> button_event_task
-> LED toggle 또는 log
```

## ISR 예시

```c
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    if (GPIO_Pin == GPIO_PIN_13) {
        BaseType_t higher_priority_task_woken = pdFALSE;
        uint32_t event = 1;

        xQueueSendFromISR(button_queue, &event, &higher_priority_task_woken);
        portYIELD_FROM_ISR(higher_priority_task_woken);
    }
}
```

## 확인 기준

- 버튼을 누르면 task가 event를 받는다.
- ISR 안에서 오래 걸리는 처리를 하지 않는다.
- queue overflow 여부를 확인할 수 있다.

## 프로젝트 연결

CAN RX interrupt, UART RX interrupt, emergency stop input도 같은 방식으로 task에 넘길 수 있다.
