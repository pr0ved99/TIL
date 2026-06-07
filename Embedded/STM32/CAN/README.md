# STM32 CAN Study

NUCLEO-F446RE 기준 CAN 통신 학습과 프로젝트 적용 기록을 정리하는 공간이다.

## Baseline

- Board: NUCLEO-F446RE
- MCU: STM32F446RE
- CAN peripheral: bxCAN
- Initial API: STM32 HAL CAN
- Physical layer: external CAN transceiver required
- Project target: tracked mobile robot command/telemetry bus

## Structure

- `00_A_to_Z`: NUCLEO-F446RE 기준 CAN 전체 학습 지도
- `Practice`: A-to-Z 문서와 연결되는 번호별 실습 경로

## Documents

- [`00_A_to_Z/01_NUCLEO_F446RE_CAN_A_to_Z_Learning_Map.md`](./00_A_to_Z/01_NUCLEO_F446RE_CAN_A_to_Z_Learning_Map.md): CAN 기본기부터 robot command/telemetry 설계까지의 학습 지도
- [`Practice/README.md`](./Practice/README.md): CAN 실습 경로 인덱스

## Related Project Documents

- [`../../../Projects/Tracked_Mobile_Robot/01_System_Architecture/14_CAN_Bus_Integration_Plan_ko.md`](../../../Projects/Tracked_Mobile_Robot/01_System_Architecture/14_CAN_Bus_Integration_Plan_ko.md): tracked mobile robot CAN 통합 계획
- [`../Theory/05_STM32_CAN_LL_FreeRTOS_Roadmap.md`](../Theory/05_STM32_CAN_LL_FreeRTOS_Roadmap.md): STM32 CAN, LL, FreeRTOS 통합 학습 로드맵
