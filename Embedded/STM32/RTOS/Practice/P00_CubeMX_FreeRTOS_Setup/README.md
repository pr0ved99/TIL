# R00 CubeMX FreeRTOS Setup

## 목표

NUCLEO-F446RE에서 FreeRTOS가 포함된 STM32Cube 프로젝트를 만들고 기본 task가 실행되는지 확인한다.

## CubeMX 설정

```text
Board: NUCLEO-F446RE
Middleware -> FreeRTOS -> Enabled
API: CMSIS-RTOS2 또는 FreeRTOS native 중 하나로 통일
GPIO: PA5 user LED output
UART: log용 USART 설정 후보
```

## 확인 기준

- 프로젝트가 build 된다.
- 보드에 flash 된다.
- default task 또는 LED task가 실행된다.
- debugger에서 scheduler 시작 이후 task가 도는 것을 확인한다.

## 기록할 것

- FreeRTOS API 선택
- heap 설정
- tick rate
- default task stack size
- 사용한 CubeMX/CubeIDE 버전
