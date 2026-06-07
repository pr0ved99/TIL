# ROS 2 Project A-to-Z Learning Map

## 목적

이 문서는 현재 진행하려는 로봇 프로젝트에 필요한 ROS 2 학습 범위를 A-to-Z로 정리한 로드맵이다.

단순히 ROS 2 명령어를 외우는 것이 아니라, 아래 흐름을 실제 시스템으로 연결하는 것을 목표로 한다.

```text
STM32 하부제어
-> 상위 컴퓨터 ROS 2
-> cmd_vel / odom / tf
-> URDF / RViz2 / Gazebo
-> 센서 토픽
-> Nav2 자율주행
-> 실제 하드웨어 bring-up
```

## 프로젝트 기준 가정

현재 학습 기준 프로젝트는 다음 구조를 가진 모바일 로봇이다.

- 하부 제어기: STM32 기반 모터 제어, 엔코더, 안전 상태, telemetry
- 상위 컴퓨터: Ubuntu 22.04 + ROS 2 Humble
- 이동 방식: tracked drivetrain을 differential-drive로 1차 근사
- 제어 입력: `/cmd_vel`
- 상태 출력: `/odom`, `/tf`, motor telemetry, battery telemetry
- 시각화: RViz2
- 시뮬레이션: Gazebo classic 11
- 자율주행 확장: Nav2, SLAM 또는 GPS/IMU/encoder fusion
- 센서 확장: LiDAR, RealSense D435i, IMU, GPS

## 실습 태그 인덱스

학습 본문에서 `[Pxx]` 태그가 보이면 아래 실습 문서로 이동한다.

| 태그 | 실습 경로 | 목적 |
| --- | --- | --- |
| `[P00]` | [`Practice/P00_Environment_Check`](../Practice/P00_Environment_Check/README.md) | ROS 2 Humble 환경과 GUI 도구 확인 |
| `[P01]` | [`Practice/P01_ROS_Graph_Turtlesim`](../Practice/P01_ROS_Graph_Turtlesim/README.md) | ROS graph, topic, teleop 감각 익히기 |
| `[P02]` | [`Practice/P02_Package_PubSub`](../Practice/P02_Package_PubSub/README.md) | ROS 2 package와 pub/sub 직접 만들기 |
| `[P03]` | [`Practice/P03_CmdVel_Odom_Model`](../Practice/P03_CmdVel_Odom_Model/README.md) | `/cmd_vel`과 differential odometry 모델 이해 |
| `[P04]` | [`Practice/P04_TF2_RViz`](../Practice/P04_TF2_RViz/README.md) | TF tree와 RViz2 디버깅 |
| `[P05]` | [`Practice/P05_URDF_Xacro`](../Practice/P05_URDF_Xacro/README.md) | URDF/xacro와 robot_state_publisher |
| `[P06]` | [`Practice/P06_Gazebo_Diff_Drive`](../Practice/P06_Gazebo_Diff_Drive/README.md) | Gazebo classic에서 differential-drive 시뮬레이션 |
| `[P07]` | [`Practice/P07_Serial_Bridge`](../Practice/P07_Serial_Bridge/README.md) | ROS 2와 STM32 serial bridge 설계 |
| `[P08]` | [`Practice/P08_Nav2_Basics`](../Practice/P08_Nav2_Basics/README.md) | Nav2 기본 구조와 TurtleBot3 실습 |
| `[P09]` | [`Practice/P09_Sensor_Pipeline`](../Practice/P09_Sensor_Pipeline/README.md) | LiDAR, camera, IMU, GPS 토픽 확인 |
| `[P10]` | [`Practice/P10_Bringup_Debugging`](../Practice/P10_Bringup_Debugging/README.md) | 실제 bring-up과 디버깅 루틴 |

## 전체 학습 순서

```text
0. 환경과 작업공간
1. ROS graph 기본
2. package / workspace / launch
3. message와 interface 설계
4. 이동 로봇 kinematics와 odometry
5. TF2와 좌표계
6. URDF/xacro와 robot_state_publisher
7. RViz2 시각화
8. Gazebo 시뮬레이션
9. STM32 bridge와 ros2_control 방향
10. 센서 토픽과 perception pipeline
11. Nav2와 자율주행 stack
12. bring-up, test, safety
```

## 0. 환경과 작업공간

### 0.1 ROS 2 배포판과 OS

현재 기준은 Ubuntu 22.04와 ROS 2 Humble이다.

프로젝트에서 중요한 것은 "내 터미널이 ROS 2 환경을 제대로 보고 있는가"다. ROS 2에서는 같은 명령을 입력해도 shell setup이 안 되어 있으면 package, message, launch file을 찾지 못한다.

확인할 것:

- `ROS_DISTRO=humble`
- `/opt/ros/humble/setup.bash` source 여부
- `ros2`, `colcon`, `rosdep` 사용 가능 여부
- RViz2와 Gazebo GUI 실행 가능 여부

연결 실습: `[P00]`

### 0.2 ROS 2 workspace

ROS 2 코드는 보통 workspace 단위로 관리한다.

권장 연습 workspace:

```text
/home/proved/my_ws/ros2_ws
```

기본 구조:

```text
ros2_ws/
├── src/
├── build/
├── install/
└── log/
```

규칙:

- 직접 작성하는 package는 `src/` 아래에 둔다.
- `colcon build`는 workspace root에서 실행한다.
- 빌드 후에는 `source install/setup.bash`를 해야 새 package가 보인다.
- 여러 workspace를 겹쳐 쓸 때는 source 순서가 중요하다.

## 1. ROS Graph 기본

### 1.1 Node

Node는 ROS 2에서 실행되는 최소 기능 단위다.

프로젝트 예시:

- `base_bridge_node`: STM32와 serial/CAN 통신
- `robot_state_publisher`: URDF 기준 TF publish
- `sensor_driver_node`: LiDAR, camera, IMU driver
- `nav2_controller`: path를 따라 `/cmd_vel` 생성
- `mission_manager_node`: 순찰, 탐지, 접근, 복귀 상태 관리

### 1.2 Topic

Topic은 지속적으로 흐르는 데이터 통로다.

프로젝트에서 반드시 익숙해져야 할 topic:

| Topic | Message | 의미 |
| --- | --- | --- |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | 상위 제어기가 하부 구동계에 주는 속도 명령 |
| `/odom` | `nav_msgs/msg/Odometry` | encoder/IMU 기반 로봇 위치 추정 |
| `/tf` | `tf2_msgs/msg/TFMessage` | 시간에 따라 변하는 좌표계 관계 |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | 고정된 좌표계 관계 |
| `/joint_states` | `sensor_msgs/msg/JointState` | wheel joint 상태 |
| `/scan` | `sensor_msgs/msg/LaserScan` | 2D LiDAR scan |
| `/imu/data` | `sensor_msgs/msg/Imu` | IMU orientation/angular velocity/acceleration |
| `/camera/color/image_raw` | `sensor_msgs/msg/Image` | RGB camera image |
| `/camera/depth/image_rect_raw` | `sensor_msgs/msg/Image` | depth image |

연결 실습: `[P01]`, `[P02]`

### 1.3 Service

Service는 요청과 응답이 명확한 1회성 작업에 사용한다.

프로젝트 예시:

- motor enable/disable
- encoder reset
- calibration start
- map save
- mission start/stop

지속적인 제어 명령을 service로 보내면 안 된다. 예를 들어 주행 속도 명령은 service가 아니라 topic인 `/cmd_vel`로 보내야 한다.

### 1.4 Action

Action은 시간이 오래 걸리고 중간 feedback과 cancel이 필요한 작업에 사용한다.

프로젝트 예시:

- Nav2의 `NavigateToPose`
- 특정 지점까지 이동
- docking
- pickup sequence

### 1.5 Parameter

Parameter는 node 실행 중 바꿀 수 있는 설정값이다.

프로젝트 예시:

- wheel radius
- track width
- serial port
- baudrate
- control loop rate
- timeout threshold
- Nav2 costmap inflation radius

### 1.6 QoS

QoS는 ROS 2 통신 품질 설정이다. ROS 2는 DDS 기반이라 QoS가 맞지 않으면 topic 이름이 같아도 통신이 안 될 수 있다.

기본 감각:

- 센서 데이터: 최신 값이 중요하므로 best effort를 쓰는 경우가 많다.
- 제어 명령: 안정적인 delivery와 timeout 설계가 중요하다.
- map, parameter, static TF: 늦게 구독해도 마지막 값을 받아야 할 수 있다.

## 2. Package, Workspace, Launch

### 2.1 Package 역할 분리

프로젝트가 커지면 package를 역할 기준으로 나눠야 한다.

권장 package 구조:

```text
tracked_robot_description     # URDF/xacro, meshes, RViz config
tracked_robot_bringup         # 실제 로봇 launch 모음
tracked_robot_base_bridge     # STM32 serial/CAN bridge
tracked_robot_simulation      # Gazebo world, spawn launch
tracked_robot_navigation      # Nav2 params, map, navigation launch
tracked_robot_sensors         # camera/LiDAR/IMU/GPS bring-up
tracked_robot_msgs            # 꼭 필요할 때만 custom msg/srv/action
```

처음부터 모든 package를 만들 필요는 없다. 하지만 역할 경계는 위처럼 생각하고 시작하는 편이 좋다.

연결 실습: `[P02]`

### 2.2 Launch

Launch file은 여러 node를 한 번에 실행하는 entrypoint다.

프로젝트 launch는 보통 다음처럼 나뉜다.

```text
description.launch.py     # robot_state_publisher, joint_state_publisher
sim.launch.py             # Gazebo, spawn_entity, simulated sensors
bringup.launch.py         # real robot base bridge, sensors, TF
navigation.launch.py      # Nav2 stack
view.launch.py            # RViz2 visualization
```

좋은 launch file은 하드코딩을 줄이고 parameter와 argument로 환경 차이를 처리한다.

## 3. Message와 Interface 설계

### 3.1 표준 message 우선

ROS 2에서는 표준 message를 우선 사용해야 한다.

프로젝트에서 우선 사용할 표준 message:

- 속도 명령: `geometry_msgs/msg/Twist`
- 위치 추정: `nav_msgs/msg/Odometry`
- IMU: `sensor_msgs/msg/Imu`
- Laser: `sensor_msgs/msg/LaserScan`
- Image: `sensor_msgs/msg/Image`
- Battery: `sensor_msgs/msg/BatteryState`
- Joint: `sensor_msgs/msg/JointState`
- Diagnostic: `diagnostic_msgs`

Custom message는 표준 message로 표현하기 어려운 firmware telemetry나 fault code가 명확해진 뒤 만든다.

### 3.2 STM32 interface 계약

상위 ROS 2와 STM32 사이에는 명확한 interface contract가 필요하다.

최소 command:

```text
linear_x_mps
angular_z_radps
enable
sequence
```

최소 telemetry:

```text
left_encoder_count
right_encoder_count
left_speed_mps
right_speed_mps
battery_voltage
fault_flags
firmware_state
timestamp_or_sequence
```

안전 규칙:

- `/cmd_vel`이 일정 시간 끊기면 STM32가 자체적으로 정지한다.
- ROS 2 bridge가 죽어도 모터가 계속 돌면 안 된다.
- 통신 parsing 실패는 무시하거나 safe state로 보내야 한다.
- enable 상태와 speed command는 분리한다.

연결 실습: `[P03]`, `[P07]`

## 4. 이동 로봇 Kinematics와 Odometry

### 4.1 Differential-drive 근사

Tracked drivetrain은 slip이 있지만 첫 모델은 differential-drive로 근사한다.

기본 식:

```text
v = (v_r + v_l) / 2
w = (v_r - v_l) / B

v_l = v - (w * B / 2)
v_r = v + (w * B / 2)
```

여기서:

- `v`: 로봇 전진 속도
- `w`: yaw rate
- `v_l`: left track 속도
- `v_r`: right track 속도
- `B`: effective track width

### 4.2 `/cmd_vel` 해석

`/cmd_vel`의 `linear.x`와 `angular.z`만 먼저 사용한다.

```text
linear.x  > 0 : 전진
linear.x  < 0 : 후진
angular.z > 0 : 좌회전
angular.z < 0 : 우회전
```

초기에는 `linear.y`, `linear.z`, `angular.x`, `angular.y`는 무시한다.

### 4.3 Encoder odometry

Encoder count는 distance로 바뀌고, distance delta는 pose로 적분된다.

```text
distance_per_count = output_circumference / counts_per_output_rev
d_l = delta_left_count * distance_per_count
d_r = delta_right_count * distance_per_count
d_center = (d_r + d_l) / 2
d_yaw = (d_r - d_l) / B
```

Pose update:

```text
yaw_mid = yaw + d_yaw / 2
x = x + d_center * cos(yaw_mid)
y = y + d_center * sin(yaw_mid)
yaw = yaw + d_yaw
```

연결 실습: `[P03]`

### 4.4 Odometry의 한계

Tracked robot은 회전 시 slip이 크다. Encoder-only odometry는 short-term estimate로 보고, 장기 위치 정확도는 IMU, LiDAR SLAM, GPS, visual odometry 중 하나와 결합해야 한다.

## 5. TF2와 좌표계

### 5.1 필수 frame

모바일 로봇에서 먼저 고정할 frame:

```text
map
└── odom
    └── base_footprint
        └── base_link
            ├── left_track_link
            ├── right_track_link
            ├── imu_link
            ├── gps_link
            ├── lidar_link
            └── camera_link
```

의미:

- `map`: 전역 좌표. SLAM/Nav2가 관리한다.
- `odom`: local odometry 좌표. 연속적이지만 drift가 있다.
- `base_footprint`: 지면에 투영된 로봇 중심.
- `base_link`: 로봇 본체 기준 좌표.
- sensor link: 실제 센서 장착 위치.

### 5.2 Static TF와 Dynamic TF

Static TF:

- `base_link -> camera_link`
- `base_link -> imu_link`
- `base_link -> lidar_link`
- `base_link -> gps_link`

Dynamic TF:

- `odom -> base_footprint`
- wheel joint
- SLAM/Nav2가 제공하는 `map -> odom`

TF가 틀리면 센서 데이터, RViz2, Nav2가 모두 틀어진다. 따라서 TF는 시뮬레이션 전 단계에서 반드시 검증한다.

연결 실습: `[P04]`

## 6. URDF/xacro와 Robot State Publisher

### 6.1 URDF의 역할

URDF는 로봇의 link와 joint 구조를 표현한다.

최소 구성:

- `base_link`
- left/right track 또는 virtual wheel link
- sensor link
- fixed joint
- wheel continuous joint
- visual geometry
- collision geometry
- inertial 정보

### 6.2 xacro의 역할

xacro는 URDF를 parameter와 macro로 관리하기 위한 도구다.

반복되는 wheel, sensor mount, material, inertial block은 xacro macro로 빼는 것이 좋다.

### 6.3 Robot State Publisher

`robot_state_publisher`는 URDF와 `/joint_states`를 받아 TF를 publish한다.

프로젝트에서 검증해야 할 것:

- RViz2에서 RobotModel이 보이는가
- TF tree가 끊기지 않았는가
- sensor frame 위치가 실제 장착 위치와 맞는가
- `base_link`와 `base_footprint`의 관계가 명확한가

연결 실습: `[P05]`

## 7. RViz2 시각화와 디버깅

### 7.1 RViz2의 목적

RViz2는 물리 시뮬레이터가 아니라 ROS 2 데이터 시각화 도구다.

프로젝트에서 RViz2로 볼 것:

- TF tree
- RobotModel
- Odometry
- Path
- LaserScan
- PointCloud2
- Camera image
- Marker
- Nav2 costmap

### 7.2 Fixed Frame

RViz2에서 가장 먼저 확인할 것은 Fixed Frame이다.

권장:

- TF/URDF 검증: `base_link` 또는 `odom`
- odometry 검증: `odom`
- navigation 검증: `map`

Fixed Frame이 없거나 TF가 연결되지 않으면 RViz2에 데이터가 있어도 보이지 않는다.

연결 실습: `[P04]`, `[P05]`

## 8. Gazebo 시뮬레이션

### 8.1 Gazebo classic과 newer Gazebo 구분

현재 Humble 학습 기준은 Gazebo classic 11이다.

명령:

```bash
gazebo --verbose
```

`gz sim`은 newer Gazebo 계열이므로 현재 classic 기반 실습과 구분한다.

### 8.2 시뮬레이션에서 먼저 검증할 것

Gazebo에서 바로 전체 자율주행을 붙이지 않는다.

순서:

1. 빈 world 실행
2. 로봇 URDF spawn
3. visual/collision/inertial 확인
4. diff-drive plugin 연결
5. `/cmd_vel`로 이동
6. `/odom`과 `/tf` 확인
7. Laser/Camera/IMU plugin 추가
8. Nav2 연결

연결 실습: `[P06]`

### 8.3 실제 tracked robot과 가상 diff-drive

Gazebo에서 실제 track contact physics를 처음부터 정확히 재현하려고 하면 복잡도가 급격히 올라간다.

초기 전략:

- visual은 tracked robot처럼 표현한다.
- 주행 물리는 virtual left/right wheel 기반 diff-drive로 먼저 검증한다.
- 실제 slip과 track 특성은 하드웨어 실험에서 튜닝한다.

## 9. STM32 Bridge와 ros2_control 방향

### 9.1 첫 단계는 단순 bridge

처음부터 `ros2_control` hardware interface를 구현하지 않는다.

초기 bridge node 책임:

- `/cmd_vel` subscribe
- linear/angular velocity를 left/right target으로 변환
- STM32로 command packet 전송
- STM32 telemetry 수신
- `/odom` publish
- `odom -> base_footprint` TF publish
- diagnostics publish

연결 실습: `[P07]`

### 9.2 ros2_control은 후속 단계

`ros2_control`은 controller와 hardware interface를 표준화하는 프레임워크다.

도입 가치:

- wheel controller 표준화
- simulation과 real hardware interface 통일
- controller switching
- joint state 관리

도입 시점:

- serial/CAN command와 telemetry format이 안정된 뒤
- odometry 계산 기준이 정리된 뒤
- Gazebo와 real robot의 interface를 맞추고 싶을 때

## 10. 센서 토픽과 Perception Pipeline

### 10.1 LiDAR

LiDAR는 Nav2 local costmap과 obstacle detection에 중요하다.

확인할 것:

- `/scan` publish 여부
- frame id
- range min/max
- scan rate
- RViz2 LaserScan 표시

### 10.2 RealSense D435i

D435i는 RGB, depth, IMU를 제공할 수 있다.

확인할 것:

- color image
- depth image
- camera info
- aligned depth
- IMU topic
- frame tree

### 10.3 IMU

IMU는 yaw-rate, orientation, localization 보정에 사용한다.

주의:

- IMU frame 방향
- covariance
- mounting orientation
- timestamp
- magnetometer 사용 여부

### 10.4 GPS

실외 공터 주행을 고려하면 GPS는 전역 위치 추정 후보가 된다.

확인할 것:

- `/fix`
- covariance
- update rate
- antenna 위치 frame
- `robot_localization` 연동 가능성

연결 실습: `[P09]`

## 11. Nav2와 자율주행 Stack

### 11.1 Nav2가 요구하는 것

Nav2를 붙이려면 최소한 아래가 필요하다.

- `map -> odom -> base_link` TF
- `/odom`
- `/cmd_vel` 수신 가능한 base
- obstacle source: `/scan` 또는 point cloud
- robot footprint
- costmap parameter
- planner/controller parameter

### 11.2 Nav2 구성요소

핵심 구성:

- Planner server: global path 생성
- Controller server: path tracking
- Behavior tree navigator: navigation task orchestration
- Costmap: 장애물과 inflation 관리
- Lifecycle manager: Nav2 node lifecycle 관리
- AMCL 또는 SLAM/localization: `map -> odom` 제공

연결 실습: `[P08]`

### 11.3 프로젝트 자율주행 방향

프로젝트 단계별 방향:

1. Gazebo에서 TurtleBot3로 Nav2 개념 학습
2. 자체 URDF diff-drive 모델로 Nav2 연결
3. 실제 base bridge에서 `/cmd_vel`, `/odom`, `/tf` 연결
4. LiDAR 또는 depth 기반 obstacle source 연결
5. mission manager로 순찰/탐지/복귀 상태 관리

## 12. Bring-up, Test, Safety

### 12.1 Bring-up 순서

실제 로봇에서 권장 실행 순서:

```text
1. 전원/퓨즈/스위치 확인
2. STM32 firmware 단독 motor disabled 상태 확인
3. serial/CAN 연결 확인
4. base bridge 실행
5. telemetry 수신 확인
6. motor enable 전 timeout 동작 확인
7. 낮은 속도 `/cmd_vel` 테스트
8. `/odom`, `/tf` 확인
9. RViz2에서 RobotModel/Odom/TF 확인
10. 센서 driver 실행
11. rosbag 기록
12. Nav2 또는 mission logic 연결
```

연결 실습: `[P10]`

### 12.2 안전 규칙

최소 안전 규칙:

- 바퀴를 띄운 상태에서 첫 구동 테스트를 한다.
- `/cmd_vel` timeout을 firmware와 ROS 2 bridge 양쪽에 둔다.
- enable과 speed command를 분리한다.
- emergency stop 경로를 둔다.
- battery voltage fault를 telemetry와 firmware state에 반영한다.
- launch file 하나로 바로 motor enable이 되게 만들지 않는다.

### 12.3 기록 규칙

실험마다 남길 것:

- 실행한 launch/command
- topic list
- TF tree
- rosbag 또는 log
- RViz2/Gazebo screenshot
- 성공 기준
- 실패 원인 가설
- 다음 action

## 마일스톤

| Milestone | 목표 | 완료 기준 |
| --- | --- | --- |
| M0 | Humble 환경 고정 | `ros2 doctor`, RViz2, Gazebo 실행 |
| M1 | ROS graph 이해 | topic/service/action/param CLI 사용 가능 |
| M2 | Package 작성 | 직접 만든 node가 pub/sub 수행 |
| M3 | Robot model | URDF가 RViz2에서 TF와 함께 표시 |
| M4 | Sim base | Gazebo에서 `/cmd_vel`로 이동하고 `/odom` publish |
| M5 | Base bridge | STM32 또는 simulator와 command/telemetry 송수신 |
| M6 | Sensor pipeline | LiDAR/camera/IMU/GPS topic을 RViz2에서 확인 |
| M7 | Nav2 simulation | goal pose로 이동 성공 |
| M8 | Real bring-up | 낮은 속도 실제 주행, odom/TF/telemetry 기록 |

## 다음에 쌓을 세부 문서

이 A-to-Z 문서는 전체 지도다. 이후에는 아래 문서를 순서대로 분리해서 작성한다.

- `01_Core_Concepts/01_ROS_Graph_Node_Topic_Service_Action.md`
- `01_Core_Concepts/02_QoS_and_DDS_Basics.md`
- `01_Core_Concepts/03_TF2_Frame_Design_For_Mobile_Robot.md`
- `02_Tools/01_ROS2_CLI_Debugging_Guide.md`
- `03_Simulation/01_Gazebo_Classic_Diff_Drive_Workflow.md`
- `99_Troubleshooting/01_ROS2_Package_And_Source_Troubleshooting.md`
