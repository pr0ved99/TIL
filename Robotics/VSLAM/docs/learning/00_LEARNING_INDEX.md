# VSLAM Learning Index

## 결론

이 인덱스는 VSLAM 학습 문서를 읽을 순서대로 묶어 둔 목차다.
처음에는 `D435i RGB-D + RTAB-Map baseline`을 이해하고, 그 다음 Jetson 실행 구조, 외부 IMU, GPS 순서로 확장한다.

## 1. VSLAM 기본 실행 흐름

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 1-1 | [D435i_RTABMap_VSLAM_Manual.md](./D435i_RTABMap_VSLAM_Manual.md) | D435i RGB-D와 RTAB-Map baseline 흐름을 잡는다. |
| 1-2 | [How_realsense2_camera_converts_D435i_to_ROS2_Topics.md](./How_realsense2_camera_converts_D435i_to_ROS2_Topics.md) | D435i 데이터가 ROS 2 topic으로 바뀌는 과정을 이해한다. |

## 2. D435i IMU와 odometry 이해

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 2-1 | [D435i_IMU_Topics_and_Enable_Guide.md](./D435i_IMU_Topics_and_Enable_Guide.md) | D435i IMU topic을 언제 켜고 어떻게 확인할지 본다. |
| 2-2 | [D435i_IMU_Axis_Interpretation.md](./D435i_IMU_Axis_Interpretation.md) | IMU 축과 실제 회전 방향을 연결한다. |
| 2-3 | [D435i_Odometry_Accuracy_Comparison.md](./D435i_Odometry_Accuracy_Comparison.md) | camera, IMU, wheel encoder 조합의 odometry 차이를 비교한다. |

## 3. Jetson Docker 준비

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 3-1 | [D435i_Jetson_Docker_Prerequisites.md](./D435i_Jetson_Docker_Prerequisites.md) | D435i와 Jetson Docker 작업 전 선수 지식을 정리한다. |
| 3-2 | [Jetson_Docker_Host_Checklist.md](./Jetson_Docker_Host_Checklist.md) | Jetson host 상태를 실행 전 점검한다. |
| 3-3 | [Jetson_Orin_Nano_Power_Mode_Guide.md](./Jetson_Orin_Nano_Power_Mode_Guide.md) | Jetson 전력 모드와 RTAB-Map 성능 관계를 이해한다. |
| 3-4 | [Jetson_Docker_Camera_to_Laptop_RTABMap_Guide.md](./Jetson_Docker_Camera_to_Laptop_RTABMap_Guide.md) | Jetson camera와 laptop RTAB-Map GUI 분리 구조를 이해한다. |

## 4. Jetson 현장 운영과 멀티세션

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 4-1 | [Jetson_RTABMap_Multi_Session_Workflow_Guide.md](./Jetson_RTABMap_Multi_Session_Workflow_Guide.md) | `camera`, `RTAB-Map backend`, `topic 확인`, `host GUI`를 세션별로 나누는 이유를 이해한다. |
| 4-2 | [RTABMap_MultiSession_DB_Reuse_Learning_Guide.md](./RTABMap_MultiSession_DB_Reuse_Learning_Guide.md) | RTAB-Map DB를 새로 만들고 삭제하지 않고 다시 여는 multi-session reuse 흐름을 이해한다. |

## 5. 외부 IMU 확장

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 5-1 | [BNO08x_IMU_Placement_Guide.md](./BNO08x_IMU_Placement_Guide.md) | 외부 BNO08x IMU를 어디에 어떻게 장착할지 이해한다. |
| 5-2 | [BNO08x_RTABMap_IMU_Comparison_Learning_Guide.md](./BNO08x_RTABMap_IMU_Comparison_Learning_Guide.md) | BNO08x IMU OFF/ON 비교를 어떤 조건으로 보고 어떻게 해석할지 이해한다. |

## 6. 야외 자율주행용 GPS 확장

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 6-1 | [Jetson_GPS_UART_ROS2_Bringup_Learning_Guide.md](./Jetson_GPS_UART_ROS2_Bringup_Learning_Guide.md) | GPS UART raw NMEA 확인부터 ROS 2 `/gps/fix` 전 단계까지 이해한다. |

## 7. 로봇 모델과 응용 연결

| 순서 | 문서 | 목적 |
| --- | --- | --- |
| 7-1 | [Mari_URDF_Xacro_Preparation_Checklist.md](./Mari_URDF_Xacro_Preparation_Checklist.md) | Mari URDF/Xacro 작성을 위한 좌표계와 센서 frame 준비 기준을 잡는다. |
| 7-2 | [D435i_Ubuntu_YOLO_Depth_Handoff.md](./D435i_Ubuntu_YOLO_Depth_Handoff.md) | D435i depth와 인식 결과를 응용 작업으로 넘기는 기준을 정리한다. |

## 8. 현재 추천 학습 순서

VSLAM과 야외 자율주행을 처음부터 이어서 공부한다면 아래 순서가 가장 실용적이다.

1. [D435i_RTABMap_VSLAM_Manual.md](./D435i_RTABMap_VSLAM_Manual.md)
2. [How_realsense2_camera_converts_D435i_to_ROS2_Topics.md](./How_realsense2_camera_converts_D435i_to_ROS2_Topics.md)
3. [Jetson_RTABMap_Multi_Session_Workflow_Guide.md](./Jetson_RTABMap_Multi_Session_Workflow_Guide.md)
4. [RTABMap_MultiSession_DB_Reuse_Learning_Guide.md](./RTABMap_MultiSession_DB_Reuse_Learning_Guide.md)
5. [BNO08x_RTABMap_IMU_Comparison_Learning_Guide.md](./BNO08x_RTABMap_IMU_Comparison_Learning_Guide.md)
6. [Jetson_GPS_UART_ROS2_Bringup_Learning_Guide.md](./Jetson_GPS_UART_ROS2_Bringup_Learning_Guide.md)
7. [Mari_URDF_Xacro_Preparation_Checklist.md](./Mari_URDF_Xacro_Preparation_Checklist.md)
