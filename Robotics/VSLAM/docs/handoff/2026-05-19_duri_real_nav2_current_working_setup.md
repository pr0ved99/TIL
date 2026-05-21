# 2026-05-19 Duri Real Nav2 Current Working Setup

## 결론

현재 Duri 실물 Nav2는 다음 3개 프로세스를 분리해서 실행하는 구성이 가장 안정적이다.

```text
1. RTAB-Map localization
2. Nav2
3. cmd_vel_to_motor bridge
```

중요한 원칙은 `RTAB-Map launch`에서 Nav2를 같이 켜지 않는 것이다.
Nav2는 `duri_nav2_real_bringup.launch.py` 하나로만 실행해야 한다.

## 현재 네트워크 / 공통 환경

현재 사용 중인 Jetson 접속 대상:

```text
jetson@172.30.1.48
```

공통 ROS2 환경:

```bash
cd /home/jetson/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=14
export ROS_LOCALHOST_ONLY=0
export FASTDDS_BUILTIN_TRANSPORTS=UDPv4
```

노트북 GitLab workspace:

```text
/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws
```

Jetson ROS2 workspace:

```text
/home/jetson/S14P31C205/edge/jetson/ros2_ws
```

Jetson RTAB-Map DB 위치:

```text
/home/jetson/.ros/rtabmap/duri_mapping_*.db
```

Jetson saved map 위치:

```text
/home/jetson/S14P31C205/edge/jetson/maps/duri_rtabmap_*.yaml
/home/jetson/S14P31C205/edge/jetson/maps/duri_rtabmap_refined_*.yaml
```

## 현재 잘 되는 조건

현재까지 실물에서 비교적 잘 동작한 조건은 다음과 같다.

```text
카메라 각도:
  camera_pitch:=0.436332
  약 25도. 카메라를 다시 올렸을 때 위치추정이 좋아졌음.

RTAB-Map:
  localization mode 사용
  기존 DB를 사용해 /odom, /rtabmap/map, map->base_footprint 추정 유지

Nav2:
  saved map 사용
  Nav2 launch는 한 번만 실행
  robot_radius는 0.45
  inflation_radius는 0.35

motor bridge:
  /cmd_vel 구독
  너무 빠른 회전을 피하기 위해 낮은 출력 범위 사용
```

용어:

```text
inflation:
  장애물 주변에 회색 비용 영역을 퍼뜨려서 로봇이 너무 가까이 가지 않게 하는 Nav2 costmap 기능

costmap:
  Nav2가 주행 가능/불가능 공간을 판단하는 2D 비용 지도

BT:
  Behavior Tree. Nav2가 계획, 주행, 복구 행동을 순서대로 판단하는 흐름
```

## 금지 조합

아래 조합은 Nav2 노드를 중복으로 띄우기 쉬우므로 피한다.

```text
duri_real_robot_bringup.launch.py start_nav2:=true
+
duri_nav2_real_bringup.launch.py

또는

duri_nav2_real_bringup.launch.py
+
nav2_bringup navigation_launch.py 직접 실행
```

중복 상태에서 보이는 증상:

```text
3 /bt_navigator
2 /controller_server
/navigate_to_pose Action servers: 3
/follow_path Action servers: 2
```

이 상태에서는 goal이 어느 action server로 들어가는지 꼬일 수 있으므로 goal 테스트를 하지 않는다.

## 실행 순서

### 0. 기존 Nav2 정리

Jetson에서 실행한다.

```bash
cd /home/jetson/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=14
export ROS_LOCALHOST_ONLY=0
export FASTDDS_BUILTIN_TRANSPORTS=UDPv4

ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{}" || true

printf '1\n' | sudo -S pkill -INT -f 'duri_nav2_real_bringup.launch.py|navigation_launch.py|controller_server|planner_server|bt_navigator|velocity_smoother|behavior_server|waypoint_follower|smoother_server|lifecycle_manager_navigation|map_server|lifecycle_manager_map_server|map_to_odom_static_tf|static_transform_publisher' || true
sleep 4

printf '1\n' | sudo -S pkill -9 -f 'duri_nav2_real_bringup.launch.py|navigation_launch.py|controller_server|planner_server|bt_navigator|velocity_smoother|behavior_server|waypoint_follower|smoother_server|lifecycle_manager_navigation|map_server|lifecycle_manager_map_server|map_to_odom_static_tf|static_transform_publisher' || true
sleep 3

ros2 daemon stop
ros2 daemon start
```

노트북에서도 graph cache를 갱신한다.

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=14
export ROS_LOCALHOST_ONLY=0
export FASTDDS_BUILTIN_TRANSPORTS=UDPv4

ros2 daemon stop
ros2 daemon start
```

정리 확인:

```bash
ros2 node list | sort | uniq -c | grep -E 'bt_navigator|controller_server|planner_server|velocity_smoother|map_server|costmap' || echo "Nav2 cleared"
```

### 1. RTAB-Map localization 실행

Jetson 터미널 1.

```bash
cd /home/jetson/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=14
export ROS_LOCALHOST_ONLY=0
export FASTDDS_BUILTIN_TRANSPORTS=UDPv4

DB=$(ls -t /home/jetson/.ros/rtabmap/duri_mapping_*.db | head -n1)
echo "DB=$DB"

ros2 launch trashbot_navigation duri_real_robot_bringup.launch.py \
  start_camera:=true \
  start_robot_tf:=true \
  start_rtabmap:=true \
  rtabmap_localization:=true \
  database_path:="$DB" \
  start_map_server:=false \
  start_nav2:=false \
  start_motor_bridge:=false \
  color_profile:=424x240x15 \
  depth_profile:=424x240x15 \
  camera_preset:=light \
  camera_pitch:=0.436332 \
  detection_rate:=1 \
  max_features:=800 \
  topic_queue_size:=30 \
  sync_queue_size:=30 \
  approx_sync_max_interval:=0.20 \
  log_level:=info
```

중요:

```text
start_nav2:=false
start_map_server:=false
start_motor_bridge:=false
```

RTAB-Map launch는 위치추정과 TF만 담당한다.

### 2. Nav2 실행

Jetson 터미널 2.

```bash
cd /home/jetson/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=14
export ROS_LOCALHOST_ONLY=0
export FASTDDS_BUILTIN_TRANSPORTS=UDPv4

MAP=$(ls -t /home/jetson/S14P31C205/edge/jetson/maps/duri_rtabmap_refined_*.yaml /home/jetson/S14P31C205/edge/jetson/maps/duri_rtabmap_*.yaml 2>/dev/null | head -n1)
PARAM=/home/jetson/S14P31C205/edge/jetson/ros2_ws/src/trashbot_navigation/config/nav2_duri_real.yaml

echo "MAP=$MAP"

ros2 launch trashbot_navigation duri_nav2_real_bringup.launch.py \
  map:="$MAP" \
  params_file:="$PARAM" \
  start_map_to_odom_tf:=true \
  start_map_server:=true \
  start_nav2:=true \
  autostart:=true \
  log_level:=info
```

현재 운용상 `start_map_to_odom_tf:=true`를 사용하고 있다.
다만 RTAB-Map이 map->odom을 안정적으로 소유하는 구조로 바꾸면 이 옵션은 다시 검토해야 한다.

### 3. motor bridge 실행

Jetson 터미널 3.

최근 비교적 부드럽게 사용한 낮은 출력 설정:

```bash
cd /home/jetson/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=14
export ROS_LOCALHOST_ONLY=0
export FASTDDS_BUILTIN_TRANSPORTS=UDPv4

printf '1\n' | sudo -S -E bash -lc '
cd /home/jetson/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=14
export ROS_LOCALHOST_ONLY=0
export FASTDDS_BUILTIN_TRANSPORTS=UDPv4

ros2 run trashbot_localization cmd_vel_to_motor.py \
  --ros-args \
  -p cmd_vel_topic:=/cmd_vel \
  -p min_motor_speed:=0.11 \
  -p max_motor_speed:=0.18 \
  -p max_linear_speed_mps:=0.05 \
  -p max_angular_speed_radps:=0.08 \
  -p cmd_timeout_s:=0.4
'
```

주의:

```text
웹 조종기와 cmd_vel_to_motor.py는 동시에 켜지 않는다.
둘 다 GPIO를 잡으면 Device or resource busy가 날 수 있다.
```

### 4. RViz 실행

노트북 터미널.

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=14
export ROS_LOCALHOST_ONLY=0
export FASTDDS_BUILTIN_TRANSPORTS=UDPv4

rviz2 -d install/trashbot_navigation/share/trashbot_navigation/rviz/duri_real_localization_monitor.rviz
```

RViz에서 헷갈리면 `RTAB Live Map`은 끄고 `Saved Map`, `Global Costmap`, `Local Costmap`, `Nav2 Global Plan`, `Nav2 Local Plan` 중심으로 본다.

## 현재 Nav2 파라미터 운영값

현재 성공 가능성이 높았던 costmap 여유 설정:

```text
robot_radius: 0.45
inflation_radius: 0.35
```

실행 중 확인:

```bash
ros2 param get /local_costmap/local_costmap robot_radius
ros2 param get /global_costmap/global_costmap robot_radius
ros2 param get /local_costmap/local_costmap inflation_layer.inflation_radius
ros2 param get /global_costmap/global_costmap inflation_layer.inflation_radius
```

설정 파일에 반영:

```bash
PARAM=/home/jetson/S14P31C205/edge/jetson/ros2_ws/src/trashbot_navigation/config/nav2_duri_real.yaml

cp "$PARAM" "${PARAM}.bak_inflation_$(date +%Y%m%d_%H%M%S)"

sed -i 's/^\([[:space:]]*robot_radius:\).*/\1 0.45/' "$PARAM"
sed -i 's/^\([[:space:]]*inflation_radius:\).*/\1 0.35/' "$PARAM"

grep -nE 'robot_radius|inflation_radius' "$PARAM"
```

목표 판정은 필요하면 아래처럼 느슨하게 한다.

```bash
ros2 param set /controller_server general_goal_checker.xy_goal_tolerance 0.25
ros2 param set /controller_server general_goal_checker.yaw_goal_tolerance 1.57
```

의미:

```text
xy_goal_tolerance 0.25:
  목표점 25cm 이내면 도착으로 인정

yaw_goal_tolerance 1.57:
  최종 방향은 약 90도까지 허용
```

## 정상 상태 확인 명령

Nav2 중복 확인:

```bash
ros2 node list | sort | uniq -c | grep -E 'bt_navigator|controller_server|planner_server|velocity_smoother|map_server|costmap'
ros2 action info /navigate_to_pose
ros2 action info /follow_path
```

정상 기준:

```text
1 /bt_navigator
1 /controller_server
1 /planner_server
1 /velocity_smoother
1 /map_server
1 /global_costmap/global_costmap
1 /local_costmap/local_costmap

/navigate_to_pose Action servers: 1
/follow_path Action servers: 1
```

RTAB-Map 위치추정 확인:

```bash
ros2 topic echo /rtabmap/odom_info --once | grep -E 'lost|matches|inliers|features|local_map_size'
timeout 5 ros2 run tf2_ros tf2_echo map base_footprint
```

좋은 상태:

```text
lost: false
inliers: 100 이상이면 비교적 양호
map -> base_footprint TF가 연속 출력됨
```

cmd_vel 연결 확인:

```bash
ros2 topic info /cmd_vel -v | grep -E 'Publisher count|Subscription count|Node name|Topic type'
ros2 topic info /cmd_vel_nav -v | grep -E 'Publisher count|Subscription count|Node name|Topic type'
```

정상 흐름:

```text
controller_server -> /cmd_vel_nav -> velocity_smoother -> /cmd_vel -> cmd_vel_to_motor
```

## 목표 취소 명령

goal이 꼬였거나 새 goal이 안 먹으면 먼저 cancel한다.

```bash
ros2 service call /navigate_to_pose/_action/cancel_goal action_msgs/srv/CancelGoal \
"{goal_info: {goal_id: {uuid: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, stamp: {sec: 0, nanosec: 0}}}"

ros2 service call /follow_path/_action/cancel_goal action_msgs/srv/CancelGoal \
"{goal_info: {goal_id: {uuid: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, stamp: {sec: 0, nanosec: 0}}}"

ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{}"
```

상태 코드:

```text
2 = EXECUTING
4 = SUCCEEDED
5 = CANCELED
6 = ABORTED
```

## 현재 관찰된 문제와 해결 방향

### 1. Nav2 중복 실행

증상:

```text
3 /bt_navigator
2 /controller_server
Action servers가 여러 개
```

원인:

```text
RTAB launch에서 start_nav2:=true를 켰거나,
Nav2 launch를 여러 터미널에서 반복 실행했거나,
navigation_launch.py를 별도로 같이 실행했을 가능성
```

해결:

```text
RTAB launch는 start_nav2:=false
Nav2는 duri_nav2_real_bringup.launch.py 한 번만 실행
```

### 2. 장애물 앞에서 후진 후 대기하다 실패

증상:

```text
goal을 찍으면 장애물 앞에서 후진
대기 시간이 길어짐
최종 status 6 ABORTED
```

가능한 원인:

```text
inflation이 너무 두꺼워 local controller가 이동 가능 공간을 좁게 판단
goal이 costmap의 회색/검은 영역에 걸림
local controller가 FollowPath를 abort
```

대응:

```text
inflation_radius 0.35로 축소
RViz에서 /global_costmap/costmap, /local_costmap/costmap 확인
목표는 흰색 free space 안쪽, 현재 위치에서 0.3~0.5m 앞쪽부터 테스트
```

### 3. 실시간 장애물 회피는 아직 완성 아님

현재 Nav2 설정은 저장된 map과 inflation 중심이다.
local_costmap에 depth 기반 obstacle layer가 본격적으로 붙은 상태는 아니다.

즉 현재 가능한 것은:

```text
저장 맵 기반 주행
저장 맵 장애물 주변 inflation 회피
```

아직 미완성인 것은:

```text
새로 등장한 사람/물체를 depth camera로 local costmap에 실시간 반영
```

후속 작업:

```text
depth image 또는 pointcloud -> obstacle_layer 연결
local_costmap plugins에 obstacle_layer 추가
RPP use_collision_detection 재검토
```

## 다음 재현 절차 요약

```text
1. Jetson 172.30.1.48 접속
2. 기존 Nav2 정리
3. RTAB-Map localization 실행, start_nav2:=false 확인
4. Nav2 launch 한 번만 실행
5. bridge 실행
6. RViz 실행
7. node/action 중복 확인
8. costmap inflation 0.35 확인
9. 2D Goal Pose를 가까운 흰색 free space에 찍기
```

