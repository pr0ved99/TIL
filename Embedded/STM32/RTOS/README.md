# STM32 RTOS Study

NUCLEO-F446RE 기준 FreeRTOS 학습과 tracked mobile robot firmware 구조화를 정리하는 공간이다.

## Baseline

- Board: NUCLEO-F446RE
- MCU: STM32F446RE
- RTOS: FreeRTOS
- Configuration entry: STM32CubeMX / STM32CubeIDE
- First target: motor control, safety, communication, telemetry task separation

## Structure

- `00_A_to_Z`: NUCLEO-F446RE 기준 FreeRTOS 전체 학습 지도
- `Practice`: A-to-Z 문서와 연결되는 번호별 실습 경로

## Documents

- [`00_A_to_Z/01_NUCLEO_F446RE_FreeRTOS_A_to_Z_Learning_Map.md`](./00_A_to_Z/01_NUCLEO_F446RE_FreeRTOS_A_to_Z_Learning_Map.md): FreeRTOS 기본기부터 robot firmware task architecture까지의 학습 지도
- [`Practice/README.md`](./Practice/README.md): FreeRTOS 실습 경로 인덱스

## Related Project Documents

- [`../../../Projects/Tracked_Mobile_Robot/01_System_Architecture/13_FreeRTOS_Task_Architecture_ko.md`](../../../Projects/Tracked_Mobile_Robot/01_System_Architecture/13_FreeRTOS_Task_Architecture_ko.md): tracked mobile robot FreeRTOS task architecture
- [`../Theory/05_STM32_CAN_LL_FreeRTOS_Roadmap.md`](../Theory/05_STM32_CAN_LL_FreeRTOS_Roadmap.md): STM32 CAN, LL, FreeRTOS 통합 학습 로드맵
