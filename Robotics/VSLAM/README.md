# VSLAM Study

Visual SLAM(VSLAM)은 카메라 영상으로 자신의 위치를 추정하고 주변 지도를 만드는 기술이다.

## 결론

- 이 폴더는 `주제별 문서 + 날짜별 작업 기록` 구조로 정리한다.
- 개념, 계획, 트러블슈팅 같은 참고 문서는 `docs/` 아래에서 관리한다.
- 실제로 하루 동안 무엇을 했는지는 `daily/YYYY-MM-DD/README.md`에 시간순으로 기록한다.
- `Jetson`에서 직접 진행하는 실행/성능/GUI 검증은 `jetson/` 아래에서 별도로 기록한다.
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
- `jetson`: `Jetson` 현장 실행 기록, GUI 검증, 장치/성능 이슈 분리 관리

## Note

학습 자료는 각 폴더 안에 Markdown 문서와 예제 코드로 정리한다.

## Documents

### learning

- [`docs/learning/D435i_RTABMap_VSLAM_Manual.md`](./docs/learning/D435i_RTABMap_VSLAM_Manual.md): D435i RGB-D 입력으로 RTAB-Map VSLAM을 실행하고 확인하는 운영 매뉴얼
- [`docs/learning/D435i_Jetson_Docker_Prerequisites.md`](./docs/learning/D435i_Jetson_Docker_Prerequisites.md): D435i와 Jetson Docker를 시작하기 전에 알아야 할 선수지식 정리
- [`docs/learning/Jetson_Docker_Host_Checklist.md`](./docs/learning/Jetson_Docker_Host_Checklist.md): Jetson에서 Docker 작업 시작 전 호스트 상태를 점검하는 체크리스트
- [`docs/learning/Jetson_Orin_Nano_Power_Mode_Guide.md`](./docs/learning/Jetson_Orin_Nano_Power_Mode_Guide.md): `25W`, `Balanced`, `nvpmodel`, `jetson_clocks` 관계와 RTAB-Map 관점에서의 점검 순서 정리
- [`docs/learning/Jetson_Docker_Camera_to_Laptop_RTABMap_Guide.md`](./docs/learning/Jetson_Docker_Camera_to_Laptop_RTABMap_Guide.md): Jetson Docker 컨테이너에서 D435i 토픽을 publish하고 노트북에서 RTAB-Map GUI를 띄우는 절차 정리
- [`docs/learning/D435i_IMU_Topics_and_Enable_Guide.md`](./docs/learning/D435i_IMU_Topics_and_Enable_Guide.md): D435i IMU 토픽을 켜고 확인하는 방법 정리
- [`docs/learning/D435i_IMU_Axis_Interpretation.md`](./docs/learning/D435i_IMU_Axis_Interpretation.md): D435i IMU의 `x/y/z` 축이 실제 회전 동작과 어떻게 대응되는지 정리
- [`docs/learning/D435i_Odometry_Accuracy_Comparison.md`](./docs/learning/D435i_Odometry_Accuracy_Comparison.md): `D435i 단독`, `D435i + IMU`, `wheel encoder + 외부 IMU` 조합의 odom 정확도 비교표
- [`docs/learning/How_realsense2_camera_converts_D435i_to_ROS2_Topics.md`](./docs/learning/How_realsense2_camera_converts_D435i_to_ROS2_Topics.md): `realsense2_camera`가 D435i 데이터를 ROS2 토픽으로 바꾸는 과정 정리
- [`docs/learning/Mari_URDF_Xacro_Preparation_Checklist.md`](./docs/learning/Mari_URDF_Xacro_Preparation_Checklist.md): Mari URDF/Xacro 작성을 위한 좌표계, 궤도, 구동축, collision, 센서 위치 체크리스트

### progress

- [`docs/progress/AI_Assisted_Algorithm_Switching_Workflow.md`](./docs/progress/AI_Assisted_Algorithm_Switching_Workflow.md): AI로 논문 후보를 조사하고, baseline과 비교해 알고리즘 전환 여부를 결정하는 절차
- [`docs/progress/Current_Progress_and_Open_Issues.md`](./docs/progress/Current_Progress_and_Open_Issues.md): 현재 프로젝트 위치, 완료된 것, 남은 문제, 다음 액션을 한 번에 보는 상태 문서
- [`docs/progress/D435i_VSLAM_A_to_Z_Plan.md`](./docs/progress/D435i_VSLAM_A_to_Z_Plan.md): D435i 기반 VSLAM 구현 전체 계획 문서
- [`docs/progress/Jira_Tasks_From_Screenshot_2026-04-13.md`](./docs/progress/Jira_Tasks_From_Screenshot_2026-04-13.md): Jira 스크린샷 기준 Sprint/Backlog 정리
- [`docs/progress/RTABMap_Tuning_Experiment_Plan.md`](./docs/progress/RTABMap_Tuning_Experiment_Plan.md): RTAB-Map 세팅 비교 실험 계획과 평가 기준
- [`docs/progress/Turtle_Trash_Picking_VSLAM_Roadmap.md`](./docs/progress/Turtle_Trash_Picking_VSLAM_Roadmap.md): 쓰레기 수거 로봇용 VSLAM 기반 자율주행 단계별 계획
- [`docs/progress/Outdoor_Autonomous_Trash_Robot_Development_Roadmap.md`](./docs/progress/Outdoor_Autonomous_Trash_Robot_Development_Roadmap.md): 공터 환경 기준 전체 자율주행 개발 로드맵
- [`docs/progress/PreArrival_Sensor_Fusion_Architecture.md`](./docs/progress/PreArrival_Sensor_Fusion_Architecture.md): `IMU / wheel encoder / GPS`가 도착하기 전 미리 고정해둘 ROS2 토픽, TF, EKF 구조 설계
- [`docs/progress/Simulation_First_Outdoor_Trash_Robot_Procedure.md`](./docs/progress/Simulation_First_Outdoor_Trash_Robot_Procedure.md): URDF/시뮬레이션 선검증 기준 실제 개발 절차
- [`docs/progress/Sprint_Only_Execution_and_Backlog_Reference.md`](./docs/progress/Sprint_Only_Execution_and_Backlog_Reference.md): 스프린트 실행 기준과 백로그 문서화 정리
- [`docs/progress/Why_Mari_Gazebo_Baseline_Is_Needed.md`](./docs/progress/Why_Mari_Gazebo_Baseline_Is_Needed.md): Mari를 Gazebo에 띄우는 이유와 오늘 개발 성공 기준 정리

### process

- [`docs/process/Jira_Convention_Guide.md`](./docs/process/Jira_Convention_Guide.md): Jira 에픽/스토리/태스크 작성 규칙과 스프린트 운영 컨벤션
- [`docs/process/Git_Branch_Strategy_Guide.md`](./docs/process/Git_Branch_Strategy_Guide.md): Git Flow 기반 브랜치 전략, 커밋/MR 규칙, GitLab MR 워크플로우 정리

### troubleshooting

- [`docs/troubleshooting/D435i_RealTime_Troubleshooting_History.md`](./docs/troubleshooting/D435i_RealTime_Troubleshooting_History.md): D435i 실시간성 문제를 실제로 어떻게 분리하고 해결했는지 전체 기록 정리
- [`docs/troubleshooting/D435i_RealSense_Viewer_Triage_Checklist.md`](./docs/troubleshooting/D435i_RealSense_Viewer_Triage_Checklist.md): RealSense Viewer 기준으로 D435i 실시간성 문제를 분리 진단하는 체크리스트
- [`docs/troubleshooting/Why_RealSense_Viewer_Looks_RealTime_But_RTABMap_Does_Not.md`](./docs/troubleshooting/Why_RealSense_Viewer_Looks_RealTime_But_RTABMap_Does_Not.md): 왜 `realsense-viewer`는 부드럽고 `RTAB-Map`은 더 무겁고 실패하기 쉬운지 정리

### daily

- [`daily/README.md`](./daily/README.md): `VSLAM 공통 일지`와 `Jetson 현장 일지`를 날짜순으로 모아보는 통합 인덱스
- [`daily/_template/README.md`](./daily/_template/README.md): 날짜별 작업 일지를 쓸 때 복사해서 사용하는 질문형 회고 템플릿
- [`daily/2026-04-09/README.md`](./daily/2026-04-09/README.md): 프로젝트 방향, 스프린트 기준, D435i 1차 확인 정리
- [`daily/2026-04-11/README.md`](./daily/2026-04-11/README.md): D435i 권한 문제, IMU 연속성, depth 저해상도 안정화 트러블슈팅 정리
- [`daily/2026-04-13/README.md`](./daily/2026-04-13/README.md): Jira 작업 정리, VSLAM 진행 계획 보강, 발표 자료용 RTAB-Map 3D 맵 구성 정리
- [`daily/2026-04-14/README.md`](./daily/2026-04-14/README.md): RTAB-Map 튜닝 방향, 재실험 로그, 발표용 3D 맵 생성 시도 정리
- [`daily/2026-04-15/README.md`](./daily/2026-04-15/README.md): Jetson 호스트, Docker, ROS 2 Humble, D435i color/depth bring-up 정리
- [`daily/2026-04-16/README.md`](./daily/2026-04-16/README.md): Jetson Docker RTAB-Map/X11, cross-machine ROS 2 실패 원인 분리, 노트북 직결 RTAB-Map 데모 정리
- [`daily/2026-04-23/README.md`](./daily/2026-04-23/README.md): 로컬 CAD 자료 정리, 궤도형 섀시 후보 분리, URDF/Xacro 준비 방향 정리
- [`daily/2026-04-24/README.md`](./daily/2026-04-24/README.md): Mari URDF/Xacro 골격, 센서 배치 준비, 하드웨어/VSLAM 현황 정리
- [`daily/2026-04-25/README.md`](./daily/2026-04-25/README.md): Mari `base_link`, 센서 frame, 궤도/구동축 파라미터 측정
- [`daily/2026-04-26/README.md`](./daily/2026-04-26/README.md): Mari/Duri asset 정리, Onshape URDF/GLTF 보관, Gazebo visual mesh blocker 확인
- [`daily/2026-04-28/README.md`](./daily/2026-04-28/README.md): Mari Gazebo 필요성 문서화와 Gazebo launch/world 기반 headless spawn baseline 확인

### jetson

- [`jetson/README.md`](./jetson/README.md): `Jetson`에서 직접 진행하는 `VSLAM` 실행 기록 관리 기준
- [`jetson/daily/2026-04-17/README.md`](./jetson/daily/2026-04-17/README.md): `SSH` 시작 이후 `모니터 + 키보드 + 마우스`를 직접 연결한 현재 작업 상태 기록
- [`jetson/daily/2026-04-18/README.md`](./jetson/daily/2026-04-18/README.md): `Docker`, `BNO08x`, 핸드오프 문서와 영상 증빙 정리
- [`jetson/daily/2026-04-19/README.md`](./jetson/daily/2026-04-19/README.md): `D435i IMU` 한계 확인과 `BNO08x ROS2 publisher/viewer` 진행 기록
- [`jetson/daily/2026-04-20/README.md`](./jetson/daily/2026-04-20/README.md): `Docker backend + host rtabmap_viz` 구조로 누적 map을 확인한 기록
- [`jetson/daily/2026-04-21/README.md`](./jetson/daily/2026-04-21/README.md): `BNO08x` calibration과 Docker `IMU OFF/ON` 비교 benchmark 기록
- [`jetson/daily/2026-04-22/README.md`](./jetson/daily/2026-04-22/README.md): `trashbot_description` URDF/xacro 초안과 RViz2 확인 구조 추가
- [`jetson/docker/README.md`](./jetson/docker/README.md): `Jetson Docker`의 service 분리, runtime/dev image, preset, tmpfs 구조 정리
- [`jetson/guides/README.md`](./jetson/guides/README.md): `Jetson`에서 바로 따라칠 수 있는 진행 방법 파일 목록
- [`jetson/handoffs/README.md`](./jetson/handoffs/README.md): 팀원 실행용 핸드오프 문서 목록
- [`jetson/progress/Jetson_VSLAM_Project_Goal_and_Roadmap.md`](./jetson/progress/Jetson_VSLAM_Project_Goal_and_Roadmap.md): `Jetson`에서의 최종 목표와 단계별 로드맵
- [`jetson/progress/Jetson_VSLAM_Daily_Execution_Plan.md`](./jetson/progress/Jetson_VSLAM_Daily_Execution_Plan.md): `Jetson` 기준 일일 실행 계획

## Evidence

- [`assets/2026-04-09_task59_d435i_depth_check/README.md`](./assets/2026-04-09_task59_d435i_depth_check/README.md): `S14P31C205-59` D435i depth 토픽 확인 증빙 정리
- [`assets/2026-04-11_d435i_viewer_and_mapping_check/README.md`](./assets/2026-04-11_d435i_viewer_and_mapping_check/README.md): `realsense-viewer`, IMU 확인, RTAB-Map 3D 맵핑 시도 증빙 정리
- [`assets/2026-04-15_jetson_docker_ros2_d435i_check/README.md`](./assets/2026-04-15_jetson_docker_ros2_d435i_check/README.md): Jetson 호스트, ROS 2 컨테이너, `realsense2_camera` 토픽/주기 확인 증빙 정리
- [`assets/2026-04-16_laptop_rtabmap_demo/README.md`](./assets/2026-04-16_laptop_rtabmap_demo/README.md): 노트북 직결 `D435i + RTAB-Map` 발표용 3D 맵 DB 정리
- [`assets/robot_model_exports/mari_gazebo/README.md`](./assets/robot_model_exports/mari_gazebo/README.md): Mari Gazebo debug box/full STL visual 확인 증빙 정리
- [`01_launch_success.png`](./assets/2026-04-09_task59_d435i_depth_check/01_launch_success.png)
- [`02_device_info_and_usb_type.png`](./assets/2026-04-09_task59_d435i_depth_check/02_device_info_and_usb_type.png)
- [`03_ros2_topic_list.png`](./assets/2026-04-09_task59_d435i_depth_check/03_ros2_topic_list.png)
- [`04_depth_view.png`](./assets/2026-04-09_task59_d435i_depth_check/04_depth_view.png)

## Templates

- [`templates/sensor_fusion_prebuild/README.md`](./templates/sensor_fusion_prebuild/README.md): `robot_localization`과 `navsat_transform` 연동을 미리 준비해두는 템플릿 모음

## Tools

- [`Tools/check_jetson_host_docker.sh`](./Tools/check_jetson_host_docker.sh): Jetson 호스트에서 `JetPack / Docker / NVIDIA runtime / D435i` 상태를 점검하는 스크립트
- [`Tools/run_ros2_d435i_container.sh`](./Tools/run_ros2_d435i_container.sh): Jetson에서 `ros2-d435i:humble` 컨테이너를 실행하는 스크립트
- [`Tools/exec_ros2_d435i_container.sh`](./Tools/exec_ros2_d435i_container.sh): 실행 중인 `ros2-d435i` 컨테이너에 들어가는 스크립트
- [`Tools/launch_realsense_rgbd.sh`](./Tools/launch_realsense_rgbd.sh): 컨테이너 안에서 D435i color/depth 노드를 실행하는 스크립트
- [`Tools/check_ros2_graph_in_container.sh`](./Tools/check_ros2_graph_in_container.sh): 컨테이너 안 ROS 2 노드/토픽 상태를 재확인하는 스크립트
- [`Tools/check_remote_jetson_camera_topics.sh`](./Tools/check_remote_jetson_camera_topics.sh): 노트북에서 Jetson D435i 토픽이 보이는지 확인하는 스크립트
- [`Tools/launch_rtabmap_remote_from_laptop.sh`](./Tools/launch_rtabmap_remote_from_laptop.sh): 노트북에서 Jetson D435i 토픽을 받아 RTAB-Map GUI를 실행하는 스크립트
- [`Tools/start_fastdds_discovery_server.sh`](./Tools/start_fastdds_discovery_server.sh): 멀티캐스트가 막힌 네트워크에서 노트북을 Fast DDS Discovery Server로 띄우는 스크립트
- [`Tools/enable_x11_for_docker.sh`](./Tools/enable_x11_for_docker.sh): Jetson 로컬 GUI 세션에서 Docker 컨테이너가 X11 창을 띄울 수 있게 허용하는 스크립트
- [`Tools/test_x11_in_container.sh`](./Tools/test_x11_in_container.sh): 컨테이너 안에서 `xeyes`를 실행해 X11 GUI 전달을 확인하는 스크립트
- [`Tools/launch_rtabmap_light_in_container.sh`](./Tools/launch_rtabmap_light_in_container.sh): 컨테이너 안에서 경량 RTAB-Map launch를 실행하는 스크립트
- [`Tools/teleop_mari_keyboard.py`](./Tools/teleop_mari_keyboard.py): Gazebo의 Mari를 `/cmd_vel`로 직접 조종하는 키보드 teleoperation 스크립트
- [`Tools/check_mari_gazebo_sensor_topics.py`](./Tools/check_mari_gazebo_sensor_topics.py): Mari Gazebo의 `/odom`, IMU, RGB-D topic 수신을 확인하는 스크립트
- [`Tools/check_mari_rtabmap_topics.py`](./Tools/check_mari_rtabmap_topics.py): Mari Gazebo 입력 topic과 RTAB-Map map output topic을 함께 확인하는 스크립트
- [`Tools/test_mari_cmd_vel_odom.py`](./Tools/test_mari_cmd_vel_odom.py): `/cmd_vel`을 받아 `/odom`과 `odom -> base_footprint` TF를 publish하는 Mari RViz2 이동 검증 스크립트
- [`Tools/test_mari_moving_tf.py`](./Tools/test_mari_moving_tf.py): `map -> odom -> base_footprint` 동적 TF와 `/odom`을 publish하는 Mari RViz2 시각 검증 스크립트

## Docker

- [`docker/jetson_ros2_d435i/README.md`](./docker/jetson_ros2_d435i/README.md): Jetson에서 `ROS 2 Humble + D435i` 환경을 재현하는 컨테이너 사용 가이드
- [`docker/jetson_ros2_d435i/Dockerfile`](./docker/jetson_ros2_d435i/Dockerfile): `realsense2_camera`와 장치 확인 도구를 포함한 Jetson용 기본 이미지 정의

## Description

- `trashbot_description/urdf/trashbot.urdf.xacro`: 자율주행 로봇 초안 URDF/xacro (`base_link`, 좌우 바퀴, `D435i`, `BNO08x`, GPS frame 포함)
- `trashbot_description/launch/display.launch.py`: `robot_state_publisher`, `joint_state_publisher`, RViz2 기반 모델 확인 launch
- `trashbot_description/urdf/duri.urdf.xacro`: Duri 기준 기본 URDF (센서 링크 포함)
- `trashbot_description/urdf/mari.urdf.xacro`: Mari 기준 기본 URDF (센서 링크 포함)
