# TMR ROS 2 시뮬레이션 인터페이스

SIM-01에서 정한 토픽과 TF 기준, SIM-02에서 작성한 첫 [TMR 모델](src/tmr_description/urdf/tmr.urdf.xacro)을 담고 있다. 첫 TMR 모델은 좌우 궤도를 차동 구동으로 근사한다. Gazebo에서 기본 주행을 확인했다. 가상 LiDAR, 고정 지도와 AMCL 초기화·전진 후 위치 갱신을 확인했다. NAV-02에서 Gazebo 오도메트리로 목표 도착·취소 후 정지·추가 벽 우회를 확인했다. 가상 IMU의 좌·우회전 각속도와 정지를 확인했다. 별도 EKF로 직진·회전을 비교했다. EKF 모드 패키지 런처로 Nav2 연결과 P05 도착을 확인했다. [EKF 주행 근거](../assets/logs/ros2/2026-11-23_tmr_nav_ekf/README.md) [EKF 측정](../assets/logs/ros2/2026-11-23_tmr_ekf_comparison/README.md) [IMU 측정 결과](../assets/logs/ros2/2026-11-23_tmr_imu_turns/result.json) [시뮬레이션 로드맵](../docs/plans/2026-11-17_Ubuntu_Nav2_Simulation_and_RL_Roadmap_ko.md)

## 첫 모델의 기준점과 치수

평평한 바닥에서 가상 구동축 중앙을 바닥에 내린 점을 `base_footprint` 원점으로 잡았다. `base_link`는 수평 좌표를 공유하고, 현재 모델에서 바닥보다 50mm 높다. 몸체와 센서의 위치는 `base_link`를 기준으로 기록한다. 좌우 바퀴 축은 모두 `+Y` 방향이며, 바퀴 중심을 반지름만큼 들어 올려 충돌 실린더의 최하점이 바닥에 닿게 했다. [모델 원본](src/tmr_description/urdf/tmr.urdf.xacro)

| 모델 입력 | 첫 모델 값 | 근거 |
| --- | --- | --- |
| 조립 질량 | 3.25kg | 사용자 실측 보고를 사용했다. 모델의 질량은 차체 3.05kg와 가상 바퀴 각 0.10kg으로 배분하고, 관성은 직육면체와 실린더로 근사했다. [운용 기준](../docs/handoff/CURRENT_MVP_OPERATION_RUNBOOK_ko.md) |
| 구동부 중심 간격 | 233mm | 양 궤도를 한 링크씩 단축한 실물의 사용자 실측값을 초기 간격으로 사용했다. 중심 위치는 좌 `+116.5mm`, 우 `−116.5mm`다. 회전 오차 보정에 쓰는 유효 궤간은 주행 실측에서 따로 정한다. [구동부 기록](../docs/progress/2026-10-23_progress.md) |
| 가상 구동 바퀴 반지름 | 21.48mm | 톱니 14개와 링크 피치 대표값 9.64mm로 한 바퀴당 궤도 진행량 134.96mm를 구했다. 같은 진행량을 갖는 원의 반지름 `134.96 ÷ (2π)`를 사용했다. [궤도 기하 기록](../assets/logs/wifi_link/2026-10-20_track_geometry_14t_revision/geometry_model.json) |
| 차체와 궤도 외형 | 차체 209 × 174 × 60mm, 하단 높이 20mm, 궤도 외형 각 약 270 × 35 × 50mm | 차체 길이·폭은 어댑터 도면을 참고해 배치한 근사값이다. 궤도 길이는 61링크의 피치선 둘레를 직선 두 구간과 같은 반지름의 양 끝 호로 근사했다. 차체 높이·하단 간격과 궤도 폭·높이는 초기 가정이다. [어댑터 도면 치수](../08_Mechanical_Design/README.md) · [궤도 기하 기록](../assets/logs/wifi_link/2026-10-20_track_geometry_14t_revision/geometry_model.json) |
| 센서 위치 | `laser_frame`은 차체 기준 앞 65mm·위 45mm, `imu_link`는 차체 중심 위 35mm | LiDAR는 가상 센서 배치 가정이다. IMU는 기존 중심 근처 배치 원칙을 적용했고 높이와 축 정렬은 초기 모델 가정이다. [IMU 배치 기준](../08_Mechanical_Design/01_Adapter_Plate_and_Electronics_Layout_ko.md#placement-decisions) |

회색 궤도는 표시용 형상이다. Gazebo의 평지 주행 근사에는 좌우 구동 바퀴와 차체 앞뒤의 구형 지지 접점을 사용한다. 지지 접점은 차체 중앙에서 앞뒤로 각각 90mm, 반지름 10mm다. 수평일 때 접점 아래로 0.2mm를 비워 중앙 바퀴가 먼저 바닥에 닿게 했다. 이 값들은 시뮬레이션 가정이다. 20mm 높이에서 놓은 뒤 60초 시점에 앞뒤 기울기가 기존 모델 약 11.05°, 수정본 약 0.13°였다. 주행 중 마찰과 회전 거동은 구동부를 연결한 뒤 확인한다. [정지 자세 검증](../docs/progress/2026-11-21_progress.md)

## RViz에서 모델 열기

TIL 저장소 루트의 Bash 터미널에서 실행한다. 이 노트북의 새 Bash는 `/opt/ros/jazzy/setup.bash`와 빌드된 작업공간의 `install/local_setup.bash`를 자동으로 불러온다. 기본 `ROS_DOMAIN_ID=84`, 탐색 범위는 `LOCALHOST`다. RViz는 `base_footprint`를 기준으로 차체를 보여준다. 도메인 85는 예제 TurtleBot3 실습의 도메인 84와 분리해 모델을 확인하기 위한 값이다.

```bash
cd Projects/Tracked_Mobile_Robot/05_ROS2_Integration
source /opt/ros/jazzy/setup.bash
colcon build --base-paths src --symlink-install --packages-select tmr_description
source install/setup.bash
ROS_DOMAIN_ID=85 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST ros2 launch tmr_description display.launch.py
```

RViz에서 **파란 차체, 좌우 회색 궤도, 전방 주황색 LiDAR 표시**를 확인한다. 왼쪽 `TF` 항목을 켜면 원점과 센서 프레임을 볼 수 있다. RViz 창을 닫으면 미리보기 노드도 함께 종료된다. 화면 없이 토픽과 TF만 확인할 때는 launch에 `rviz:=false`를 붙인다.

## Gazebo에서 전진과 정지 확인

정지 자세를 확인한 모델을 평지에서 짧게 주행한다. 처음 설치할 때 이 작업공간에서 `colcon build --base-paths src --symlink-install --packages-up-to tmr_sim`을 실행하고 작업공간 환경을 불러온다. 주행용 터미널에서 다음 명령으로 Gazebo 창을 하나 연다.

```bash
ROS_DOMAIN_ID=85 ros2 launch tmr_sim drive.launch.py
```

새 월드에는 `ground_plane`과 구동 가능한 `tmr`이 있다. 도메인 85는 TurtleBot3 예제의 도메인 84와 분리된다. 앞 절에서 도메인 85로 연 모델 미리보기는 창을 닫고 주행 런치를 실행한다. 두 런치 모두 같은 로봇의 TF를 발행한다. Gazebo Transport의 기본 파티션 이름은 `<호스트명>-<사용자명>-tmr-drive-<ROS 도메인 ID>`이며, 환경변수 `GZ_PARTITION`으로 지정할 수 있다. 주행 월드를 열어 둔 상태에서 다른 터미널에서 다음 명령을 한 번 실행한다.

```bash
ROS_DOMAIN_ID=85 ros2 run tmr_sim forward_stop
```

이 실습 명령은 시뮬레이션 시간 2초 동안 약 10Hz로 `linear.x = 0.10 m/s`를 보내고 이어서 0을 보낸다. 한 번 실행할 때 목표 이동량은 약 20cm다. `/cmd_vel`을 받은 Gazebo 차동 구동 플러그인이 좌우 바퀴를 구동한다. ROS에서 받는 `/odom`은 바퀴의 회전량을 적분한 값이다. 검증할 때 Gazebo 월드가 보고하는 위치와 각각 비교했다. [브리지 연결](src/tmr_sim/config/drive_bridge.yaml) · [전진·정지 측정 기록](../docs/progress/2026-11-21_progress.md#sim-03-평지-전진과-정지)

같은 월드에서 후진을 확인할 때는 다음 명령을 사용한다. 회전 속도는 0이고, 시뮬레이션 시간 2초 동안 `linear.x = −0.10 m/s`를 보낸 뒤 정지한다.

```bash
ROS_DOMAIN_ID=85 ros2 run tmr_sim reverse_stop
```

회전 명령에서 `left`와 `right`는 각각 양수와 음수의 `angular.z`를 선택한다. 현재 사용자가 저장한 값은 ±π/8 rad/s이고, `drive_step.py`가 시뮬레이션 시간을 기준으로 2초를 지시한 뒤 0을 발행한다. 명령상 회전량은 ±45°다. 월드와 바퀴 오도메트리에서 관측한 회전량은 [좌우 회전 실습 기록](../docs/progress/2026-11-21_progress.md#sim-03-제자리-회전-실습)에 있다.

```bash
ROS_DOMAIN_ID=85 ros2 run tmr_sim turn_stop left
ROS_DOMAIN_ID=85 ros2 run tmr_sim turn_stop right
ROS_DOMAIN_ID=85 ros2 run tf2_ros tf2_echo base_link laser_frame
```

## 가상 2D LiDAR와 고정 지도

`drive.launch.py`는 Sensors 플러그인이 있는 [drive.sdf](src/tmr_sim/worlds/drive.sdf)를 열고 `/model/tmr/scan`을 ROS `/scan`으로 연결한다. 가상 LiDAR는 `laser_frame`을 측정 원점으로 수평 1° 간격 360개를 10Hz로 측정한다. 실습 범위는 0.10~8.0m다. 센서 설치 위치는 임시값이다. 실물 장착 때 측정 원점까지의 `xyz/rpy`를 반영해 다시 검증한다.

가상 벽 정면 1.000m를 0.999870m로 읽었다. 고정 지도를 로드하고 AMCL을 초기화했다. 약 0.396m 전진 후 지도 기준 위치의 평면 차이는 Gazebo 대비 약 6.3mm였다. RViz에서 `Fixed Frame=map`, `Map`의 `/map`은 `Transient Local`, `LaserScan`은 `/scan`으로 두고 벽 정렬을 확인했다. [11/22 결과와 실행 순서](../assets/logs/ros2/2026-11-22_tmr_lidar_amcl/README.md)

고정 지도와 AMCL을 실행한 뒤 `ros2 launch tmr_sim navigation.launch.py`로 TMR의 Nav2를 실행한다. NAV-03 예비 주행은 별도 도메인 86에서 `drive.launch.py headless:=true seed:=3101` 등으로 새 월드를 열고 5개 경로를 비교한다. [예비 주행 절차](../assets/logs/ros2/2026-11-23_tmr_nav03_baseline/README.md) · [정식 평가 결과](../assets/logs/ros2/2026-11-23_tmr_nav03_evaluation/README.md)

바퀴 모드는 `ros2 launch tmr_sim drive.launch.py`, EKF 모드는 `ros2 launch tmr_sim drive_ekf.launch.py`로 선택한다. EKF 모드는 바퀴 원본 `/wheel/odom`에서 전진 속도를, `/imu/data`에서 차체의 Z축 각속도를 받아 평면 자세를 추정한다. 두 모드 모두 Nav2가 구독하는 토픽은 `/odom`이다.

## SIM-06 모의 배터리 전압 한 표본

`/tmr/sim/battery_voltage`에서 `diagnostic_msgs/msg/DiagnosticArray` 한 건을 발행하고 별도 ROS 구독자로 수신했다. 기존 [TEL 예제](../01_System_Architecture/07_ESP32S3_Features_and_Project_Role_ko.md)의 `batt_mv=11820`을 11.82 V로 환산한 모의값이다. `status[0].values`의 문자열 쌍에 `voltage`, `unit`, `source=SIM`, `valid=true`를 넣고 `header.stamp`는 모의 측정 생성 시각으로 쓴다. 이번 시험은 ROS 시스템 시각을 사용했다. `age`는 수신 측에서 현재 시각과 마지막 측정 시각의 차이로 계산한다.

Jazzy 환경의 첫 번째 터미널에서 구독을 먼저 시작한다.

```bash
ROS_DOMAIN_ID=77 ros2 topic echo --no-daemon /tmr/sim/battery_voltage diagnostic_msgs/msg/DiagnosticArray --once
```

두 번째 터미널에서 다음 명령으로 한 번 발행한다.

```bash
cd ~/workspace/github-repos/TIL/Projects/Tracked_Mobile_Robot/assets/logs/ros2/2026-11-23_tmr_sim06_battery
ROS_DOMAIN_ID=77 ros2 topic pub --once /tmr/sim/battery_voltage diagnostic_msgs/msg/DiagnosticArray "$(cat sample.yaml)"
```

구독 메시지에서 전압 11.82, 단위 V, 출처 SIM, 유효 표시 true, 0보다 큰 측정 시각을 확인한다. [발행 입력](../assets/logs/ros2/2026-11-23_tmr_sim06_battery/sample.yaml) · [수신 표본](../assets/logs/ros2/2026-11-23_tmr_sim06_battery/received.yaml) · [시각 비교](../assets/logs/ros2/2026-11-23_tmr_sim06_battery/receipt.json)

### 발행 중단과 재개 확인

ROS Jazzy를 불러온 두 터미널에서 각각 위의 `sample.yaml` 폴더로 이동한다. 첫 번째 터미널에서 감시기를 실행한다.

```bash
ROS_DOMAIN_ID=77 /usr/bin/python3 watch_voltage_age.py
```

두 번째 터미널에서 0.5초 간격으로 네 번 발행한다. 첫 번째 터미널에 `STALE`이 뜨면 같은 발행 명령을 한 번 더 실행한다.

```bash
ROS_DOMAIN_ID=77 ros2 topic pub --rate 2 --times 4 -w 1 \
  /tmr/sim/battery_voltage diagnostic_msgs/msg/DiagnosticArray "$(cat sample.yaml)"
```

감시기는 표본을 기다리는 동안 `WAITING`을 표시한다. 표본이 들어오면 0.1초마다 현재 시각에서 가장 최근 표본의 `header.stamp`를 빼서 경과 시간을 구한다. 실습 기준인 1.5초 미만이면 `FRESH`, 1.5초 이상이면 `STALE`을 표시한다. 전압이 계속 11.82 V여도 새 시각의 표본이 들어오면 다시 `FRESH`가 된다. 상태가 바뀔 때만 출력하며, `Ctrl+C`로 종료한다. [감시기 코드](../assets/logs/ros2/2026-11-23_tmr_sim06_battery/watch_voltage_age.py) · [전환 기록](../assets/logs/ros2/2026-11-23_tmr_sim06_battery/freshness_transitions.log)

사용자 회차에서 마지막 표본은 0.002초에 `FRESH`, 1.502초에 `STALE`이었다. 현재 감시기는 시각만 검사한다. 다음은 같은 표본에 담긴 `valid`도 읽어서 표시하는 것이다. [사용자 관찰 기록](../docs/progress/2026-11-23_progress.md)

## 주행과 센서 토픽

Gazebo의 차동 구동 플러그인은 속도 명령을 받아 좌우 구동 관절에 적용하고, 그 관절의 운동을 바탕으로 오도메트리를 계산한다. `ros_gz_bridge`가 명령을 ROS에서 Gazebo로 보내고, 오도메트리와 센서 데이터는 Gazebo에서 ROS로 가져온다. 기본 주행에서는 수동 조종 노드가 `/cmd_vel`을 보낸다. 목표 이동에서는 Nav2의 최종 출력이 같은 역할을 맡는다. 한 주행 회차에는 한 명령 경로가 구동부를 제어한다. [Gazebo DiffDrive](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1DiffDrive.html) · [ROS와 Gazebo 메시지 변환](https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md)

| ROS 토픽 | 메시지 | 발행 주체와 수신 주체 | 값과 좌표계 | 사용 시점 |
| --- | --- | --- | --- | --- |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | 수동 조종 또는 Nav2 최종 출력 → `ros_gz_bridge` → Gazebo 차동 구동 | 로봇 기준 `linear.x`는 m/s, `angular.z`는 rad/s. 앞쪽과 좌회전이 양수. 나머지 네 성분은 `0` | 기본 주행 |
| `/odom` | `nav_msgs/msg/Odometry` | 바퀴 모드는 `tmr_drive_bridge`, EKF 모드는 `ekf_filter_node` → RViz·Nav2 | `header.frame_id=odom`, `child_frame_id=base_footprint`. `pose`는 `odom` 기준 위치(m)·방향, `twist`는 `base_footprint` 기준 선속도(m/s)·각속도(rad/s) | 기본 주행 |
| `/clock` | `rosgraph_msgs/msg/Clock` | Gazebo 월드 → `ros_gz_bridge` → 시뮬레이션 노드 | 월드에서 진행된 시뮬레이션 시간. ROS의 `/clock`에 월드 하나를 연결 | 모델 실행 |
| `/joint_states` | `sensor_msgs/msg/JointState` | Gazebo 관절 상태 플러그인 → `ros_gz_bridge` → `robot_state_publisher` | 관절 이름은 URDF와 일치. 회전 관절 위치 rad, 속도 rad/s | 구동 관절 표시 |
| `/scan` | `sensor_msgs/msg/LaserScan` | Gazebo 2D LiDAR → `ros_gz_bridge` → RViz·AMCL·Nav2 costmap | `header.frame_id=laser_frame`. 거리 m, 각도 rad. 센서가 측정한 시각을 유지 | LiDAR 연결 |
| `/imu/data` | `sensor_msgs/msg/Imu` | Gazebo IMU → `ros_gz_bridge` → 기록·EKF | `header.frame_id=imu_link`. 각속도 rad/s, 선가속도 m/s². 좌회전 Z 양수·우회전 Z 음수, 정지 시 Z 가속도 약 +9.8 m/s², 첫 표본 공분산 미지정 | 시뮬레이션에서 발행 및 EKF 각속도 입력 확인 |
| `/map` | `nav_msgs/msg/OccupancyGrid` | `map_server` → RViz·AMCL·Nav2 costmap | `header.frame_id=map`. 해상도는 셀당 m. 첫 목표 이동에는 고정 지도를 사용 | 지도 연결 |

설치된 Jazzy 예제에서 `/cmd_vel`의 `Twist`, `/odom`의 `odom`·`base_footprint`와 bridge의 메시지 전달을 확인했다. 초기 TMR bridge는 예제의 RELIABLE/VOLATILE을 출발점으로 삼는다. 지도 `/map`과 고정 변환 `/tf_static`은 RELIABLE/TRANSIENT_LOCAL로 발행해 늦게 접속한 RViz도 받을 수 있게 한다. `/imu/data`와 `laser_frame`은 TMR에서 사용할 이름이다. bridge에서 ROS와 Gazebo 양쪽 토픽 이름을 명시하고, 센서 메시지의 `frame_id`를 실제 TF 프레임과 대조한다. [예제 실행 기록](../docs/progress/2026-11-20_progress.md#ubuntu-ros-2-환경과-turtlebot3-목표-이동-확인) · [Jazzy Odometry 메시지 정의](https://github.com/ros2/common_interfaces/blob/jazzy/nav_msgs/msg/Odometry.msg)

## 좌표계와 발행 주체

`base_footprint`는 로봇을 바닥 평면에 투영한 주행 기준이고, `base_link`는 차체와 함께 움직이는 기준이다. 두 프레임의 축은 앞 `+X`, 왼쪽 `+Y`, 위 `+Z`로 잡는다. 첫 평면 월드에서는 둘 사이를 고정 조인트로 두고, 높이와 센서 설치 위치는 모델을 작성할 때 정한다. `odom → base_link`는 `base_footprint`를 거쳐 얻는다. 이 구조는 프로젝트의 실물 ROS bridge 구상에도 적혀 있는 `odom → base_footprint`와 맞는다. [ROS 좌표계 규약](https://github.com/ros-infrastructure/rep/blob/master/rep-0105.rst#coordinate-frames) · [프로젝트 ROS bridge 경로](../01_System_Architecture/11_System_Block_Diagram_and_Interface_Map_ko.md#future-ros2-bridge-path)

```text
map
└── odom                AMCL
    └── base_footprint  Gazebo 차동 구동과 ros_gz_bridge
        └── base_link   robot_state_publisher
            ├── laser_frame
            └── imu_link
```

| TF | 발행 주체 | 사용 시점 |
| --- | --- | --- |
| `odom → base_footprint` | 바퀴 모드는 `tmr_drive_bridge`, EKF 모드는 `ekf_filter_node`가 `/tf`에 전달 | EKF 모드에서 브리지의 원래 차체 변환은 별도 토픽 `/wheel/tf`로 전달 |
| `base_footprint → base_link`, `base_link → laser_frame`, `base_link → imu_link` | `robot_state_publisher`가 URDF 고정 조인트를 `/tf_static`에 발행 | 차체·센서 모델을 띄울 때 |
| `map → odom` | AMCL이 LiDAR 스캔과 지도로 계산해 `/tf`에 발행 | 고정 지도와 자기 위치 추정을 연결할 때 |

각 자식 프레임에는 부모 하나를 지정하고, 같은 변환은 발행 주체 하나가 담당한다. 구동 관절의 동적 변환은 `robot_state_publisher`가 `/joint_states`를 받아 갱신한다.

기본 주행에서 RViz의 Fixed Frame은 `odom`을 쓴다. 고정 지도 주행에서는 `map`으로 전환하고, AMCL의 `base_frame_id`는 `base_footprint`, Nav2의 `robot_base_frame`은 `base_link`를 사용한다. Nav2의 로봇 외곽 다각형은 차체 치수를 정한 뒤 `base_link` 기준으로 작성한다. [Nav2 AMCL 변환 발행](https://github.com/ros-navigation/navigation2/blob/jazzy/nav2_amcl/src/amcl_node.cpp#L953)

## 시간과 데이터 확인

- 시뮬레이션 노드는 `use_sim_time: true`로 `/clock`을 사용한다. Gazebo에서 생성한 `/odom`, `/scan`, `/imu/data`, 동적 TF의 시각을 bridge가 유지한다. 센서 검증에서는 프레임 이름과 측정 시각을 확인하고, 이용 가능한 TF로 측정 시점의 좌표를 변환할 수 있는지 확인한다. 월드를 재시작해 시간이 역행하면 새 시험으로 기록한다.
- `/cmd_vel`의 `Twist`는 헤더가 없는 메시지다. 첫 주행 시험은 유한한 속도 입력과 명시적인 0 명령을 사용한다. 입력 유실에 따른 정지는 후속 시험에서 마지막 명령을 수신한 시각을 기준으로 검증한다. 수신 간격과 속도 상한은 주행 모델과 시험 조건을 정할 때 기록한다.
- Gazebo가 보고하는 오도메트리는 Nav2와 RViz에 사용한다. Gazebo 월드에서 읽은 모델 위치는 주행 결과를 평가할 때 사용한다. 센서의 발행률, 공분산과 지연은 해당 센서를 연결한 뒤 측정한다.
- 시뮬레이션 런치는 전용 ROS 도메인과 Gazebo Transport 파티션에서 실행한다. 실물 연동 런치는 실물 센서와 주행 브리지를 별도 구성으로 실행한다. 이 인터페이스의 속도 단위와 프레임 이름은 상위 계층을 연결할 때 재사용한다.

## 단계별 확인 기준

| 단계 | 확인 결과 |
| --- | --- |
| SIM-02 모델 | RViz에서 `base_footprint`, `base_link`와 센서 프레임이 연결된다. 센서 위치·차체 치수·관성의 근거와 가정을 기록한다. |
| SIM-03 기본 주행 | 전진·후진·좌우 회전에서 `/cmd_vel`의 부호와 모델의 움직임이 일치한다. 0 명령 후 시뮬레이터에서 정지하며 `/odom` 속도가 0으로 수렴한다. `/odom`의 두 프레임과 동적 TF의 일치를 확인한다. |
| 센서·지도 연결 | RViz에서 LiDAR 스캔이 지도와 맞고, 초기 위치 지정 후 AMCL의 `map → odom`과 전체 TF 경로가 연결된다. |
| 첫 Nav2 목표 이동 | RViz에서 찍은 한 목표가 `SUCCEEDED`로 끝나고 모델이 정지한다. 목표·종료 좌표, 최종 위치 오차, 정지 여부를 저장한다. 목표 허용 오차는 Nav2 설정에서 기록한다. |

`tmr_description`은 Jazzy에서 빌드했고 `check_urdf`로 링크 구조를 확인했다. 설치된 launch를 도메인 85에서 실행해 `/robot_description`, 좌우 `/joint_states`, `base_footprint` 기준 다섯 TF의 위치와 RViz의 모델 렌더링을 확인했다. [검증 진행 기록](../docs/progress/2026-11-20_progress.md#tmr-첫-차체-모델-sim-02)
