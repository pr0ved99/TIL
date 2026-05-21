# Duri RTAB-Map Nav2 학습 자료

## 결론

이 문서는 GitHub TIL에 남기는 학습 자료다. 실제 코드와 실행 명령은 팀 프로젝트 경로인 `/home/ssafy/my_ws/git_lab/S14P31C205` 기준으로 정리한다.

지금 Duri 쪽 진행은 아래 흐름으로 이해하면 된다.

```text
Duri Gazebo
-> RGB-D camera topic
-> RTAB-Map mapping
-> Nav2용 saved map
-> AMCL localization + Nav2 goal driving
-> 실제 하드웨어 전환을 위한 motor/sensor bridge
```

현재 확인한 팀 프로젝트 repo 기준으로는 Duri Gazebo, RGB-D topic, RTAB-Map mapping, saved-map Nav2 launch, RViz 확인, depth 기반 scan/pointcloud filter, `/cmd_vel` motor bridge, encoder/GPS/IMU 확인 스크립트가 있다. 다만 실제 로봇에서 자율주행까지 완전히 연결하려면 실제 D435i, wheel odom, IMU, encoder topic, motor bridge를 하나의 bringup으로 묶는 작업이 더 필요하다.

## 먼저 알아야 할 말

- `topic`: ROS2에서 노드끼리 데이터를 주고받는 이름 있는 통로다. 예를 들어 `/cmd_vel`, `/odom`, `/camera/...`가 topic이다.
- `TF`: `map`, `odom`, `base_link`, `camera_link` 같은 좌표계 사이의 위치 관계다. 좌표계가 끊기면 RViz와 Nav2가 로봇 위치를 제대로 못 본다.
- `RTAB-Map`: RGB-D 카메라와 odometry를 이용해 주변 지도를 만드는 SLAM/VSLAM 계열 도구다.
- `Nav2`: ROS2에서 goal을 찍으면 경로를 만들고 로봇 속도 명령 `/cmd_vel`을 내는 자율주행 stack이다.
- `costmap`: Nav2가 장애물과 이동 가능 영역을 계산하는 2D 격자 지도다.
- `AMCL`: 이미 만든 2D 지도 위에서 로봇이 현재 어디 있는지 추정하는 Nav2 localization 노드다.

## 실행 위치

TIL 문서는 GitHub 경로에 있지만, 아래 명령은 팀 프로젝트 경로에서 실행한다.

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
```

작업을 헷갈리지 않으려면 이렇게 구분한다.

```text
/home/ssafy/my_ws/git_hub/Robotics/VSLAM
-> 학습 기록, TIL, 개념 정리

/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson
-> 팀 프로젝트 실제 실행 코드
```

## 현재 진행 상황

### 1. Duri Gazebo와 RGB-D camera

Duri 모델은 Gazebo에서 RGB-D 카메라 topic을 낸다.

관련 파일:

```text
edge/jetson/ros2_ws/src/trashbot_description/launch/gazebo_duri_realsense_light.launch.py
edge/jetson/ros2_ws/src/trashbot_description/launch/gazebo_duri.launch.py
edge/jetson/ros2_ws/src/trashbot_description/urdf/duri.urdf.xacro
```

중요 topic:

```text
/cmd_vel
/odom
/imu/data
/camera/camera/color/image_raw
/camera/camera/aligned_depth_to_color/image_raw
/camera/camera/color/camera_info
/camera/camera/depth/color/points
```

실행 명령:

```bash
ros2 launch trashbot_description gazebo_duri_realsense_light.launch.py \
  gui:=true \
  verbose:=false
```

명령어 구성:

- `ros2 launch`: ROS2 launch 파일을 실행한다.
- `trashbot_description`: Duri URDF, Gazebo launch가 들어 있는 package 이름이다.
- `gazebo_duri_realsense_light.launch.py`: Duri 모델과 RealSense 형태의 RGB-D 카메라를 Gazebo에 띄우는 launch 파일이다.
- `gui:=true`: Gazebo 화면을 띄운다.
- `verbose:=false`: Gazebo 로그를 줄인다.

왜 실행했는가:

- Duri 모델이 Gazebo에 정상 spawn되는지 확인하기 위해서다.
- RGB-D camera topic, `/odom`, `/imu/data`, `/cmd_vel` 흐름이 생성되는지 보기 위해서다.
- 이후 RTAB-Map과 Nav2가 쓸 입력을 먼저 확보해야 하기 때문이다.

확인 명령:

```bash
ros2 topic list -t | sort | grep -E 'cmd_vel|odom|imu|camera|tf'
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
ros2 topic hz /camera/camera/depth/color/points
```

명령어 구성:

- `ros2 topic list -t`: 현재 살아 있는 topic과 message type을 함께 본다.
- `sort`: topic 목록을 보기 좋게 정렬한다.
- `grep -E '...'`: 필요한 topic만 필터링한다.
- `ros2 topic hz`: 해당 topic이 초당 몇 번 들어오는지 본다.

왜 실행했는가:

- RViz에 보이기 전에 실제 ROS2 topic이 살아 있는지 확인하기 위해서다.
- depth image와 pointcloud가 멈춰 있으면 RTAB-Map mapping도 진행되지 않는다.

### 2. Duri RTAB-Map mapping

RTAB-Map은 depth image와 odom을 받아 map을 만든다. 여기서 중요한 점은 depth topic이 곧바로 Nav2 map이 되는 것이 아니라는 점이다.

```text
RGB image + aligned depth image + camera info + /odom
-> RTAB-Map
-> /rtabmap/map
```

관련 파일:

```text
edge/jetson/ros2_ws/src/trashbot_description/launch/duri_rtabmap_realsense_light.launch.py
edge/jetson/ros2_ws/src/trashbot_navigation/launch/duri_rtabmap_mapping.launch.py
edge/jetson/ros2_ws/src/trashbot_navigation/launch/duri_nav2_map_builder.launch.py
edge/jetson/docs/navigation/Duri_RTABMap_To_Nav2_Map_Guide.md
```

실행 명령:

```bash
ros2 launch trashbot_navigation duri_nav2_map_builder.launch.py \
  gui:=true \
  launch_rviz:=true \
  rtabmap_viz:=true \
  camera_pitch:=0.1745 \
  verbose:=false
```

명령어 구성:

- `trashbot_navigation`: mapping, Nav2, costmap 관련 launch와 config가 들어 있는 package다.
- `duri_nav2_map_builder.launch.py`: Gazebo Duri와 RTAB-Map mapping, RViz 확인을 한 번에 묶은 launch다.
- `launch_rviz:=true`: RViz를 같이 띄운다.
- `rtabmap_viz:=true`: RTAB-Map 전용 시각화도 켠다.
- `camera_pitch:=0.1745`: 카메라가 아래쪽을 보는 각도를 radian 단위로 준다. `0.1745 rad`는 약 10도다.

왜 실행했는가:

- depth camera 기반으로 실제 2D map이 만들어지는지 확인하기 위해서다.
- 카메라가 정면만 보면 바닥/장애물 관측이 부족하므로 pitch 값을 줘서 depth 관측 방향을 맞춘다.
- mapping 단계와 navigation 단계를 분리해서 디버깅하기 위해서다.

mapping 중에는 천천히 움직여야 한다.

```bash
python3 src/trashbot_description/scripts/teleop_mari_keyboard.py \
  --cmd-vel-topic /cmd_vel \
  --rate 60 \
  --linear-speed 0.08 \
  --angular-speed 0.45 \
  --key-timeout 1.2
```

명령어 구성:

- `python3 ...teleop_mari_keyboard.py`: 키보드로 로봇 속도 명령을 보내는 script다.
- `--cmd-vel-topic /cmd_vel`: 속도 명령을 보낼 topic을 지정한다.
- `--rate 60`: 초당 60번 명령을 publish한다.
- `--linear-speed 0.08`: 전진/후진 속도를 낮게 둔다.
- `--angular-speed 0.45`: 회전 속도를 낮게 둔다.
- `--key-timeout 1.2`: 키 입력이 끊기면 1.2초 뒤 정지하도록 한다.

왜 실행했는가:

- RTAB-Map은 빠르게 움직이면 feature tracking이 깨지거나 depth matching이 불안정해진다.
- 키 입력이 끊겼을 때 계속 움직이는 상황을 막기 위해 timeout을 둔다.

정상 확인:

```bash
ros2 topic list -t | grep -E 'rtabmap|camera|odom|tf'
ros2 topic echo --once /rtabmap/map
```

### 3. RTAB-Map map을 Nav2 map으로 저장

Nav2는 보통 `map_server`가 읽을 수 있는 `.yaml`과 `.pgm` map을 쓴다. 그래서 RTAB-Map 결과를 저장해야 한다.

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205
mkdir -p edge/jetson/configs/maps

ros2 run nav2_map_server map_saver_cli \
  -f /home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/configs/maps/duri_rtabmap_gazebo \
  --ros-args \
  -r map:=/rtabmap/map \
  -p map_subscribe_transient_local:=true
```

명령어 구성:

- `ros2 run nav2_map_server map_saver_cli`: Nav2 map 저장 도구를 실행한다.
- `-f .../duri_rtabmap_gazebo`: 저장할 파일 prefix를 지정한다.
- `--ros-args`: 뒤쪽 인자를 ROS2 remap/parameter로 해석한다.
- `-r map:=/rtabmap/map`: 기본 `/map` 대신 `/rtabmap/map`을 저장 대상으로 쓴다.
- `-p map_subscribe_transient_local:=true`: 이미 publish된 map을 늦게 구독해도 받을 수 있게 한다.

왜 실행했는가:

- RTAB-Map이 만든 map을 Nav2가 다시 읽을 수 있는 파일로 남기기 위해서다.
- mapping과 navigation을 분리하면 저장 map 품질을 먼저 확인할 수 있다.

저장 결과:

```text
edge/jetson/configs/maps/duri_rtabmap_gazebo.yaml
edge/jetson/configs/maps/duri_rtabmap_gazebo.pgm
```

map에 검은 점이나 노이즈가 많으면 후처리 스크립트를 쓴다.

```bash
python3 edge/jetson/scripts/filter_nav2_saved_map.py \
  edge/jetson/configs/maps/duri_rtabmap_gazebo.yaml \
  --output-prefix edge/jetson/configs/maps/duri_rtabmap_gazebo_filtered \
  --min-occupied-neighbors 1 \
  --min-obstacle-pixels 12
```

왜 실행했는가:

- RTAB-Map 결과에 작은 점 노이즈가 많으면 Nav2가 장애물로 오해할 수 있다.
- 후처리로 너무 작은 장애물 조각을 제거해 costmap을 안정화한다.

### 4. 저장 map 기반 Nav2

저장 map을 Nav2에 넣고, AMCL로 현재 위치를 맞춘 뒤 goal을 찍는 흐름이다.

관련 파일:

```text
edge/jetson/ros2_ws/src/trashbot_navigation/launch/duri_nav2_saved_map.launch.py
edge/jetson/ros2_ws/src/trashbot_navigation/launch/duri_nav2_bringup.launch.py
edge/jetson/ros2_ws/src/trashbot_navigation/config/nav2_duri_gazebo.yaml
edge/jetson/ros2_ws/src/trashbot_navigation/rviz/duri_nav2_view.rviz
```

실행 명령:

```bash
ros2 launch trashbot_navigation duri_nav2_saved_map.launch.py \
  map:=/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/configs/maps/duri_rtabmap_gazebo_filtered.yaml \
  start_gazebo:=true \
  gui:=true \
  launch_rviz:=true \
  camera_pitch:=0.1745 \
  verbose:=false
```

명령어 구성:

- `map:=...yaml`: Nav2가 읽을 저장 map을 지정한다.
- `start_gazebo:=true`: Gazebo simulation도 같이 시작한다.
- `launch_rviz:=true`: RViz에서 map, robot, costmap, path를 확인한다.
- `camera_pitch:=0.1745`: Gazebo camera TF와 depth 관측 방향을 맞춘다.

왜 실행했는가:

- mapping 결과를 가지고 실제 Nav2 goal driving까지 되는지 확인하기 위해서다.
- RTAB-Map mapping 문제인지, Nav2 localization/planning 문제인지 분리해서 보기 위해서다.

RViz에서는 바로 `Nav2 Goal`을 찍지 말고 먼저 `2D Pose Estimate`로 시작 위치를 맞춘다. 그 다음 `Localization: active`, `Navigation: active`를 확인하고 goal을 찍는다.

정상 확인:

```bash
ros2 topic list -t | sort | grep -E 'map|amcl|particle|scan|costmap|plan|cmd_vel|odom|tf'
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 lifecycle get /controller_server
ros2 lifecycle get /planner_server
```

## Depth를 Nav2에 쓰는 두 가지 방식

### 방식 A: RTAB-Map으로 map을 만든 뒤 저장해서 사용

이 방식은 지금 Duri 작업의 기본 방향이다.

```text
depth camera
-> RTAB-Map
-> /rtabmap/map
-> map_saver_cli
-> saved map yaml/pgm
-> Nav2 map_server
```

장점:

- Nav2가 안정적으로 쓸 수 있는 정적 map을 만들 수 있다.
- mapping과 navigation을 분리해서 디버깅하기 쉽다.

주의:

- 저장 map이 지저분하면 Nav2도 지저분한 map을 그대로 믿는다.
- map 저장 후에는 AMCL이 `map -> odom`을 맡는다.

### 방식 B: depth pointcloud를 local costmap obstacle로 사용

이 방식은 실시간 장애물 회피에 필요하다.

```text
/camera/camera/depth/color/points
-> pointcloud_height_filter.py
-> /duri/filtered_depth_points
-> Nav2 local_costmap obstacle layer
```

관련 파일:

```text
edge/jetson/ros2_ws/src/trashbot_navigation/scripts/pointcloud_height_filter.py
edge/jetson/ros2_ws/src/trashbot_navigation/config/nav2_duri_gazebo.yaml
```

장점:

- 저장 map에 없는 새 장애물을 피할 수 있다.

주의:

- 바닥이 장애물처럼 들어오면 `min_z`, `camera_pitch`, `range_min`을 조정해야 한다.
- 너무 강하게 필터링하면 낮은 장애물까지 사라질 수 있다.

## 실제 하드웨어 쪽 연결

### 모터 제어

현재 `/cmd_vel`을 실제 좌우 모터 속도로 바꾸는 브리지 패키지가 있다.

관련 파일:

```text
edge/jetson/ros2_ws/src/trashbot_hardware/scripts/cmd_vel_motor_bridge.py
edge/jetson/ros2_ws/src/trashbot_hardware/launch/cmd_vel_motor_bridge.launch.py
edge/jetson/libs/control/drivers/mdd10a.py
```

흐름:

```text
/cmd_vel
-> cmd_vel_motor_bridge
-> left/right normalized speed
-> MDD10A PWM/DIR
```

실제 Jetson에서 실행:

```bash
ros2 launch trashbot_hardware cmd_vel_motor_bridge.launch.py \
  edge_root:=/home/jetson/S14P31C205/edge
```

처음에는 GPIO를 건드리지 않는 dry-run으로 변환만 본다.

```bash
ros2 launch trashbot_hardware cmd_vel_motor_bridge.launch.py dry_run:=true
```

### Encoder, GPS, IMU 확인

관련 파일:

```text
edge/jetson/tests/manual/encoder/encoder_console.py
edge/jetson/tests/manual/gps/gps_console.py
edge/jetson/tests/manual/gps/gps_nmea_uart_console.py
edge/jetson/tests/manual/imu/imu_console.py
edge/jetson/tests/integration/sensor_monitor/sensor_monitor.py
```

확인 명령:

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205/edge

python jetson/tests/manual/encoder/encoder_console.py --poll
python jetson/tests/manual/gps/gps_nmea_uart_console.py -p /dev/ttyTHS1 --raw
python jetson/tests/manual/gps/gps_console.py
python jetson/tests/manual/imu/imu_console.py
python jetson/tests/integration/sensor_monitor/sensor_monitor.py
```

현재 주의할 점:

- encoder count를 직접 읽는 코드는 있지만, 실제 encoder 값을 ROS topic `/motor/encoder_ticks`로 publish하는 실기 publisher는 별도 확인 또는 구현이 필요하다.
- GPS는 raw UART 확인과 gpsd 확인 경로가 분리되어 있다.
- BNO085/BNO08x IMU는 I2C 기본값이 `bus=1`, `address=0x4B`다.

## 지금 헷갈리기 쉬운 지점

### Depth topic과 map은 다르다

`/camera/camera/aligned_depth_to_color/image_raw`는 카메라가 보는 깊이 이미지다. 이 자체가 Nav2 map은 아니다. RTAB-Map이나 costmap layer가 이 데이터를 해석해야 쓸 수 있다.

### `/odom`과 `map`은 다르다

`/odom`은 짧은 시간에는 부드럽지만 장시간 누적 오차가 생긴다. `map`은 전역 기준이다. Nav2에서는 보통 아래 연결이 필요하다.

```text
map -> odom -> base_footprint -> base_link -> camera_link
```

### RViz에서 보인다고 Nav2가 쓰는 것은 아니다

RViz는 topic을 시각화하는 도구다. RViz에서 pointcloud가 보인다고 Nav2 costmap이 그 pointcloud를 사용한다는 뜻은 아니다. Nav2 config에 obstacle source가 연결되어 있어야 한다.

### Gazebo 성공과 실제 로봇 성공은 다르다

Gazebo에서는 `/odom`, `/imu/data`, camera topic이 깔끔하게 나온다. 실제 로봇에서는 encoder 방향, IMU 좌표계, GPS fix, D435i frame, timestamp sync를 따로 맞춰야 한다.

## 추천 학습 순서

1. `ros2 topic list`, `ros2 topic echo`, `ros2 topic hz`로 topic 확인에 익숙해진다.
2. RViz에서 `TF`, `RobotModel`, `Image`, `PointCloud2`, `Map`, `Costmap` display가 각각 무엇을 보여주는지 구분한다.
3. Duri Gazebo에서 `/cmd_vel -> /odom -> TF -> camera topic` 흐름을 확인한다.
4. RTAB-Map을 띄워 `/rtabmap/map`, `/rtabmap/mapData`, `/rtabmap/mapGraph`가 생기는지 확인한다.
5. RTAB-Map map을 `map_saver_cli`로 저장하고, RViz에서 저장 map이 깨끗한지 본다.
6. 저장 map으로 Nav2를 띄우고, `2D Pose Estimate -> Nav2 Goal` 순서로 주행한다.
7. encoder, IMU, GPS 수동 스크립트를 각각 실행해 실제 센서 값이 들어오는지 확인한다.
8. 마지막에 `/cmd_vel` motor bridge를 dry-run으로 검증한 뒤 실제 모터로 넘긴다.

## 디버깅 체크리스트

### Topic

```bash
ros2 topic list -t | sort
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
ros2 topic hz /odom
ros2 topic echo --once /rtabmap/map
```

### TF

```bash
ros2 run tf2_ros tf2_echo map odom
ros2 run tf2_ros tf2_echo odom base_footprint
ros2 run tf2_ros tf2_echo base_link camera_link
```

### Nav2 lifecycle

```bash
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
ros2 lifecycle get /controller_server
ros2 lifecycle get /planner_server
ros2 lifecycle get /bt_navigator
```

### 센서

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205/edge

python jetson/tests/manual/encoder/encoder_console.py --poll
python jetson/tests/manual/imu/imu_console.py
python jetson/tests/manual/gps/gps_nmea_uart_console.py -p /dev/ttyTHS1 --raw
```

## 다음에 구현해야 할 것

1. Duri 실제 encoder 값을 `/motor/encoder_ticks`로 publish하는 ROS2 node를 만든다.
2. `/motor/encoder_ticks -> /wheel/odometry -> EKF -> /odometry/local` 흐름을 Duri 기준으로 맞춘다.
3. 실제 D435i topic과 Gazebo topic 이름 차이를 정리한다.
4. 실제 IMU frame과 `base_link` 사이 TF를 검증한다.
5. Nav2 obstacle layer가 `/duri/filtered_depth_points`를 안정적으로 쓰는지 확인한다.
6. 실제 모터 bridge를 Nav2 `/cmd_vel`과 연결하기 전에 낮은 속도와 짧은 timeout으로 테스트한다.

## 한 줄 요약

Duri는 지금 Gazebo 기준으로 RGB-D mapping과 saved-map Nav2까지 가는 학습/검증 경로가 만들어지고 있고, 실제 로봇으로 넘어가려면 encoder odom, IMU TF, D435i topic, motor bridge를 같은 ROS2 bringup 안에 묶는 단계가 남아 있다.
