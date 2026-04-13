# VSLAM Study

Visual SLAM(VSLAM)은 카메라 영상으로 자신의 위치를 추정하고 주변 지도를 만드는 기술이다.

## 결론

- 이 폴더는 `주제별 문서 + 날짜별 작업 기록` 구조로 정리한다.
- 개념, 계획, 트러블슈팅 같은 참고 문서는 `docs/` 아래에서 관리한다.
- 실제로 하루 동안 무엇을 했는지는 `daily/YYYY-MM-DD/README.md`에 시간순으로 기록한다.
- 증빙 이미지와 캡처는 `assets/` 아래에서 관리한다.

## Structure

- `00_Basics`: 좌표계, 카메라 모델, 에피폴라 기하, 선형대수 기초
- `01_Calibration`: 카메라 보정, 왜곡 파라미터, 외부 파라미터, 시간 동기화
- `02_Feature_Tracking`: 특징점 검출, 디스크립터, 추적, 매칭, 이상치 제거
- `03_Visual_Odometry`: 프레임 간 상대 자세 추정, PnP, 삼각측량, 스케일 이슈
- `04_Backend_Optimization`: 번들 조정, 비선형 최적화, 노이즈 모델, 수치 안정성
- `05_Loop_Closure`: 장소 인식, 재방문 검출, 포즈 그래프 보정
- `06_Debugging`: 좌표계 오류, timestamp sync 문제, scale drift, 추적 실패 점검
- `07_Evaluation`: ATE, RPE, FPS, latency, 메모리/연산량 평가

## Note

학습 자료는 각 폴더 안에 Markdown 문서와 예제 코드로 정리한다.

## Documents

### learning

- [`docs/learning/D435i_Jetson_Docker_Prerequisites.md`](./docs/learning/D435i_Jetson_Docker_Prerequisites.md): D435i와 Jetson Docker를 시작하기 전에 알아야 할 선수지식 정리
- [`docs/learning/D435i_IMU_Topics_and_Enable_Guide.md`](./docs/learning/D435i_IMU_Topics_and_Enable_Guide.md): D435i IMU 토픽을 켜고 확인하는 방법 정리
- [`docs/learning/D435i_IMU_Axis_Interpretation.md`](./docs/learning/D435i_IMU_Axis_Interpretation.md): D435i IMU의 `x/y/z` 축이 실제 회전 동작과 어떻게 대응되는지 정리
- [`docs/learning/D435i_Odometry_Accuracy_Comparison.md`](./docs/learning/D435i_Odometry_Accuracy_Comparison.md): `D435i 단독`, `D435i + IMU`, `wheel encoder + 외부 IMU` 조합의 odom 정확도 비교표
- [`docs/learning/How_realsense2_camera_converts_D435i_to_ROS2_Topics.md`](./docs/learning/How_realsense2_camera_converts_D435i_to_ROS2_Topics.md): `realsense2_camera`가 D435i 데이터를 ROS2 토픽으로 바꾸는 과정 정리

### progress

- [`docs/progress/AI_Assisted_Algorithm_Switching_Workflow.md`](./docs/progress/AI_Assisted_Algorithm_Switching_Workflow.md): AI로 논문 후보를 조사하고, baseline과 비교해 알고리즘 전환 여부를 결정하는 절차
- [`docs/progress/Current_Progress_and_Open_Issues.md`](./docs/progress/Current_Progress_and_Open_Issues.md): 현재 프로젝트 위치, 완료된 것, 남은 문제, 다음 액션을 한 번에 보는 상태 문서
- [`docs/progress/D435i_VSLAM_A_to_Z_Plan.md`](./docs/progress/D435i_VSLAM_A_to_Z_Plan.md): D435i 기반 VSLAM 구현 전체 계획 문서
- [`docs/progress/Turtle_Trash_Picking_VSLAM_Roadmap.md`](./docs/progress/Turtle_Trash_Picking_VSLAM_Roadmap.md): 쓰레기 수거 로봇용 VSLAM 기반 자율주행 단계별 계획
- [`docs/progress/Outdoor_Autonomous_Trash_Robot_Development_Roadmap.md`](./docs/progress/Outdoor_Autonomous_Trash_Robot_Development_Roadmap.md): 공터 환경 기준 전체 자율주행 개발 로드맵
- [`docs/progress/PreArrival_Sensor_Fusion_Architecture.md`](./docs/progress/PreArrival_Sensor_Fusion_Architecture.md): `IMU / wheel encoder / GPS`가 도착하기 전 미리 고정해둘 ROS2 토픽, TF, EKF 구조 설계
- [`docs/progress/Simulation_First_Outdoor_Trash_Robot_Procedure.md`](./docs/progress/Simulation_First_Outdoor_Trash_Robot_Procedure.md): URDF/시뮬레이션 선검증 기준 실제 개발 절차
- [`docs/progress/Sprint_Only_Execution_and_Backlog_Reference.md`](./docs/progress/Sprint_Only_Execution_and_Backlog_Reference.md): 스프린트 실행 기준과 백로그 문서화 정리

### troubleshooting

- [`docs/troubleshooting/D435i_RealTime_Troubleshooting_History.md`](./docs/troubleshooting/D435i_RealTime_Troubleshooting_History.md): D435i 실시간성 문제를 실제로 어떻게 분리하고 해결했는지 전체 기록 정리
- [`docs/troubleshooting/D435i_RealSense_Viewer_Triage_Checklist.md`](./docs/troubleshooting/D435i_RealSense_Viewer_Triage_Checklist.md): RealSense Viewer 기준으로 D435i 실시간성 문제를 분리 진단하는 체크리스트
- [`docs/troubleshooting/Why_RealSense_Viewer_Looks_RealTime_But_RTABMap_Does_Not.md`](./docs/troubleshooting/Why_RealSense_Viewer_Looks_RealTime_But_RTABMap_Does_Not.md): 왜 `realsense-viewer`는 부드럽고 `RTAB-Map`은 더 무겁고 실패하기 쉬운지 정리

### daily

- [`daily/_template/README.md`](./daily/_template/README.md): 날짜별 작업 일지를 쓸 때 복사해서 사용하는 질문형 회고 템플릿
- [`daily/2026-04-09/README.md`](./daily/2026-04-09/README.md): 프로젝트 방향, 스프린트 기준, D435i 1차 확인 정리
- [`daily/2026-04-11/README.md`](./daily/2026-04-11/README.md): D435i 권한 문제, IMU 연속성, depth 저해상도 안정화 트러블슈팅 정리

## Evidence

- [`assets/2026-04-09_task59_d435i_depth_check/README.md`](./assets/2026-04-09_task59_d435i_depth_check/README.md): `S14P31C205-59` D435i depth 토픽 확인 증빙 정리
- [`assets/2026-04-11_d435i_viewer_and_mapping_check/README.md`](./assets/2026-04-11_d435i_viewer_and_mapping_check/README.md): `realsense-viewer`, IMU 확인, RTAB-Map 3D 맵핑 시도 증빙 정리
- [`01_launch_success.png`](./assets/2026-04-09_task59_d435i_depth_check/01_launch_success.png)
- [`02_device_info_and_usb_type.png`](./assets/2026-04-09_task59_d435i_depth_check/02_device_info_and_usb_type.png)
- [`03_ros2_topic_list.png`](./assets/2026-04-09_task59_d435i_depth_check/03_ros2_topic_list.png)
- [`04_depth_view.png`](./assets/2026-04-09_task59_d435i_depth_check/04_depth_view.png)

## Templates

- [`templates/sensor_fusion_prebuild/README.md`](./templates/sensor_fusion_prebuild/README.md): `robot_localization`과 `navsat_transform` 연동을 미리 준비해두는 템플릿 모음
