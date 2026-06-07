# STM32 FreeRTOS Practice

FreeRTOS A-to-Z 학습 문서와 연결되는 실습 경로다.

## 실습 목록

| 태그 | 경로 | 주제 |
| --- | --- | --- |
| `[R00]` | [`P00_CubeMX_FreeRTOS_Setup`](./P00_CubeMX_FreeRTOS_Setup/README.md) | CubeMX FreeRTOS 설정 |
| `[R01]` | [`P01_LED_Task_Timing`](./P01_LED_Task_Timing/README.md) | LED task timing |
| `[R02]` | [`P02_Button_ISR_Queue`](./P02_Button_ISR_Queue/README.md) | ISR to queue |
| `[R03]` | [`P03_Task_Priority_Stack`](./P03_Task_Priority_Stack/README.md) | priority, stack, heap |
| `[R04]` | [`P04_UART_Log_Mutex`](./P04_UART_Log_Mutex/README.md) | UART log mutex |
| `[R05]` | [`P05_Motor_Control_Task_Skeleton`](./P05_Motor_Control_Task_Skeleton/README.md) | robot task skeleton |
| `[R06]` | [`P06_CAN_RX_Queue_Integration`](./P06_CAN_RX_Queue_Integration/README.md) | CAN RX queue integration |

## 권장 STM32CubeIDE workspace

```text
/home/proved/my_ws/github/pr0ved99/TIL/Embedded/STM32/STM32_ws
```

실습 프로젝트 후보:

```text
F446RE_FreeRTOS_LED_Task
F446RE_FreeRTOS_Button_Queue
F446RE_FreeRTOS_Robot_Skeleton
F446RE_CAN_FreeRTOS_Queue
```
