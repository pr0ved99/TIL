# VSLAM Learning Index

## 결론

이 폴더의 학습 문서는 `대단원-소단원` 번호로 정렬한다.
파일명 앞의 `01-02`는 `01 대단원`의 `02 소단원`이라는 뜻이다.

지금 VSLAM과 야외 자율주행을 학습할 때는 `01 -> 02 -> 03 -> 04 -> 05 -> 06` 순서로 보면 된다.
다만 처음에는 `01`과 `02`를 먼저 끝내고, 그 다음 `03`부터 실제 실행 환경으로 넘어가는 편이 좋다.

## 01. VSLAM 기초와 용어

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 01-01 | [`01-01_VSLAM_Document_Study_Guide.md`](./01-01_VSLAM_Document_Study_Guide.md) | VSLAM 문서를 어떤 순서로 읽을지 잡는다. |
| 01-02 | [`01-02_VSLAM_Terms_Level1_Guide.md`](./01-02_VSLAM_Terms_Level1_Guide.md) | VSLAM 용어를 한 단계 깊게 이해한다. |

## 02. D435i RGB-D VSLAM Baseline

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 02-01 | [`02-01_D435i_RTABMap_VSLAM_Manual.md`](./02-01_D435i_RTABMap_VSLAM_Manual.md) | D435i RGB-D와 RTAB-Map baseline 흐름을 이해한다. |
| 02-02 | [`02-02_How_realsense2_camera_converts_D435i_to_ROS2_Topics.md`](./02-02_How_realsense2_camera_converts_D435i_to_ROS2_Topics.md) | D435i 데이터가 ROS2 topic으로 변환되는 과정을 이해한다. |
| 02-03 | [`02-03_D435i_IMU_Topics_and_Enable_Guide.md`](./02-03_D435i_IMU_Topics_and_Enable_Guide.md) | D435i IMU topic을 언제 켜고 어떻게 확인할지 본다. |
| 02-04 | [`02-04_D435i_IMU_Axis_Interpretation.md`](./02-04_D435i_IMU_Axis_Interpretation.md) | IMU 축과 실제 회전 방향을 연결한다. |
| 02-05 | [`02-05_D435i_Odometry_Accuracy_Comparison.md`](./02-05_D435i_Odometry_Accuracy_Comparison.md) | camera, IMU, wheel encoder 조합의 odometry 차이를 비교한다. |

## 03. Jetson 실행 환경과 RTAB-Map 운영

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 03-01 | [`03-01_D435i_Jetson_Docker_Prerequisites.md`](./03-01_D435i_Jetson_Docker_Prerequisites.md) | D435i와 Jetson Docker 작업 전 선수 지식을 정리한다. |
| 03-02 | [`03-02_Jetson_Docker_Host_Checklist.md`](./03-02_Jetson_Docker_Host_Checklist.md) | Jetson host 상태를 실행 전 점검한다. |
| 03-03 | [`03-03_Jetson_Orin_Nano_Power_Mode_Guide.md`](./03-03_Jetson_Orin_Nano_Power_Mode_Guide.md) | Jetson 전력 모드와 RTAB-Map 성능 관계를 이해한다. |
| 03-04 | [`03-04_Jetson_Docker_Camera_to_Laptop_RTABMap_Guide.md`](./03-04_Jetson_Docker_Camera_to_Laptop_RTABMap_Guide.md) | Jetson Docker backend와 노트북 RTAB-Map GUI 흐름을 이해한다. |

## 04. 외부 IMU와 센서 장착

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 04-01 | [`04-01_BNO08x_IMU_Placement_Guide.md`](./04-01_BNO08x_IMU_Placement_Guide.md) | 외부 BNO08x IMU를 어디에 어떻게 장착할지 이해한다. |

## 05. 로봇 통합과 야외 자율주행 준비

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 05-01 | [`05-01_Mari_URDF_Xacro_Preparation_Checklist.md`](./05-01_Mari_URDF_Xacro_Preparation_Checklist.md) | 로봇 좌표계와 센서 frame 준비 기준을 잡는다. |
| 05-02 | [`05-02_Mari_Gazebo_Run_Guide.md`](./05-02_Mari_Gazebo_Run_Guide.md) | 시뮬레이션에서 VSLAM 입력을 확인하는 실행 흐름을 본다. |
| 05-03 | [`05-03_Mari_Nav2_Map_Filtering_Design.md`](./05-03_Mari_Nav2_Map_Filtering_Design.md) | RTAB-Map 결과를 Nav2용 map으로 다룰 때의 필터링 기준을 본다. |
| 05-04 | [`05-04_Mari_Nav2_Run_Guide.md`](./05-04_Mari_Nav2_Run_Guide.md) | VSLAM 결과를 자율주행 smoke test로 연결하는 흐름을 이해한다. |

## 06. 응용과 핸드오프

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 06-01 | [`06-01_D435i_Ubuntu_YOLO_Depth_Handoff.md`](./06-01_D435i_Ubuntu_YOLO_Depth_Handoff.md) | D435i depth와 인식 결과를 응용 작업으로 넘기는 기준을 정리한다. |

## 권장 학습 경로

처음 학습 경로:

```text
01-01 -> 01-02 -> 02-01 -> 02-02 -> 02-05
```

센서와 실험 환경까지 확장:

```text
02-03 -> 02-04 -> 03-01 -> 03-02 -> 03-03 -> 03-04
```

야외 자율주행 준비:

```text
04-01 -> 05-01 -> 05-02 -> 05-03 -> 05-04
```
