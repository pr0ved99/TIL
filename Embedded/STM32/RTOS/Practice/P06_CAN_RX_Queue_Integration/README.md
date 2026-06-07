# R06 CAN RX Queue Integration

## 목표

CAN RX interrupt에서 받은 frame을 queue로 넘기고, parser task에서 command/telemetry 구조로 해석한다.

## 구조

```text
CAN RX ISR
-> can_rx_queue
-> can_parser_task
-> command_queue
-> motor_control_task
```

## frame struct 후보

```c
typedef struct {
    uint32_t id;
    uint8_t dlc;
    uint8_t data[8];
    uint32_t rx_tick;
} can_frame_t;
```

## ISR 예시

```c
void HAL_CAN_RxFifo0MsgPendingCallback(CAN_HandleTypeDef *hcan)
{
    BaseType_t higher_priority_task_woken = pdFALSE;
    CAN_RxHeaderTypeDef header;
    can_frame_t frame = {0};

    HAL_CAN_GetRxMessage(hcan, CAN_RX_FIFO0, &header, frame.data);

    frame.id = header.StdId;
    frame.dlc = header.DLC;
    frame.rx_tick = xTaskGetTickCountFromISR();

    xQueueSendFromISR(can_rx_queue, &frame, &higher_priority_task_woken);
    portYIELD_FROM_ISR(higher_priority_task_woken);
}
```

## parser task

```c
void CanParserTask(void *argument)
{
    can_frame_t frame;

    for (;;) {
        if (xQueueReceive(can_rx_queue, &frame, portMAX_DELAY) == pdPASS) {
            switch (frame.id) {
            case 0x100:
                // heartbeat
                break;
            case 0x110:
                // motion command parse
                break;
            case 0x130:
                // estop
                break;
            default:
                break;
            }
        }
    }
}
```

## 완료 기준

- CAN RX callback에서 frame을 queue로 넘긴다.
- parser task가 ID별로 분기한다.
- invalid DLC frame을 무시한다.
- queue overflow count를 기록한다.
- parser task가 PWM을 직접 쓰지 않는다.
