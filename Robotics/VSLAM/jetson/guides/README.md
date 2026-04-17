# Jetson Guides

## 결론

- 이 폴더는 `Jetson`에서 직접 따라 입력할 수 있게 만든 `진행 방법 파일` 모음이다.
- 계획 문서가 "무엇을 할지"를 설명한다면, 여기 문서는 **"지금 무엇을 어떤 순서로 입력할지"**를 바로 보여준다.

## 원칙

- 각 가이드는 복붙 가능한 명령만 위에서 아래 순서대로 배치한다.
- GUI가 필요한 경우 `터미널 1`, `터미널 2`처럼 나눠서 적는다.
- 한 가이드는 한 목적만 가진다.
- 새로운 단계가 시작되면 그 단계용 가이드를 먼저 만든다.

## 현재 가이드

- [`00_Jetson_Session_Start_Guide.md`](./00_Jetson_Session_Start_Guide.md): 작업 시작 전에 기본 세션 정리
- [`01_Jetson_System_Inventory_Guide.md`](./01_Jetson_System_Inventory_Guide.md): 시스템 기준선 확인
- [`02_Jetson_D435i_Native_Bringup_Guide.md`](./02_Jetson_D435i_Native_Bringup_Guide.md): `D435i` native bring-up
- [`03_Jetson_RTABMap_Baseline_Guide.md`](./03_Jetson_RTABMap_Baseline_Guide.md): `RTAB-Map` baseline 실행
- [`04_Jetson_D435i_IMU_Diagnosis_Guide.md`](./04_Jetson_D435i_IMU_Diagnosis_Guide.md): `D435i IMU HID` 이슈 진단
- [`05_Jetson_Local_RTABMap_GUI_Check_Guide.md`](./05_Jetson_Local_RTABMap_GUI_Check_Guide.md): Jetson 화면에서 `카메라 노드 + rtabmap_viz` 직접 확인
