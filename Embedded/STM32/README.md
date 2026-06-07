# STM32

NUCLEO-F446RE 기반 MCU, peripheral, firmware architecture 학습 기록을 정리하는 공간이다.

## Baseline

- Board: NUCLEO-F446RE
- MCU: STM32F446RE
- IDE: STM32CubeIDE, STM32CubeMX, VS Code STM32 extension
- Initial driver: HAL
- Deepening path: LL, FreeRTOS, CAN

## Structure

- `Theory`: STM32 기본 개념, 보드 구성, HAL/LL/CAN/RTOS 방향 문서
- `Practice`: GPIO, interrupt, PWM 등 기본 실습 기록
- `CAN`: NUCLEO-F446RE bxCAN 학습과 robot command/telemetry bus 설계
- `RTOS`: FreeRTOS task, queue, priority, safety-oriented firmware architecture
- `STM32_ws`: STM32CubeIDE 실습 프로젝트
- `assets`: 보드 이미지, 케이블, 참고 자료

## Core Learning Maps

- [`CAN/00_A_to_Z/01_NUCLEO_F446RE_CAN_A_to_Z_Learning_Map.md`](./CAN/00_A_to_Z/01_NUCLEO_F446RE_CAN_A_to_Z_Learning_Map.md): NUCLEO-F446RE CAN A-to-Z 학습 지도
- [`RTOS/00_A_to_Z/01_NUCLEO_F446RE_FreeRTOS_A_to_Z_Learning_Map.md`](./RTOS/00_A_to_Z/01_NUCLEO_F446RE_FreeRTOS_A_to_Z_Learning_Map.md): NUCLEO-F446RE FreeRTOS A-to-Z 학습 지도
- [`Theory/05_STM32_CAN_LL_FreeRTOS_Roadmap.md`](./Theory/05_STM32_CAN_LL_FreeRTOS_Roadmap.md): CAN, LL, FreeRTOS 통합 로드맵

## Practice Index

- [`CAN/Practice/README.md`](./CAN/Practice/README.md): CAN 실습 경로
- [`RTOS/Practice/README.md`](./RTOS/Practice/README.md): FreeRTOS 실습 경로
- [`Practice/01_F446RE_Blinky_Tutorial.md`](./Practice/01_F446RE_Blinky_Tutorial.md): F446RE GPIO blinky
- [`Practice/03_F446RE_EXTI_Button_Interrupt.md`](./Practice/03_F446RE_EXTI_Button_Interrupt.md): EXTI button interrupt
- [`Practice/04_F446RE_PWM_Tutorial.md`](./Practice/04_F446RE_PWM_Tutorial.md): PWM 기본 실습
