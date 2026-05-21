# 2026-05-16 Duri Gazebo Sensor Fusion Dry-Run Handoff

이 문서는 다른 Codex 대화창에서 Duri 센서퓨전 시뮬레이션 작업을 바로 이어받기 위한 기록이다.

## 결론

하드웨어를 잠깐 사용할 수 없는 상태에서 진행도를 올리기 위해, GitLab `S14P31C205`에 **Duri 전용 Gazebo sensor-fusion dry-run 경로**를 준비했다.

목표 흐름은 아래와 같다.

```text
Gazebo Duri
-> fake encoder tick
-> /wheel/odometry
-> encoder + IMU EKF
-> /odometry/local
-> RTAB-Map external odom
-> optional Nav2 goal smoke test
```

이 작업은 센서퓨전 계획의 Stage 2~4에 해당한다.

- Stage 2: Duri encoder odom 분리
- Stage 3: encoder + IMU local EKF
- Stage 4: RTAB-Map external odom 전환

## 경로 구분

중요하다. 두 checkout을 섞으면 안 된다.

```text
GitLab product repo:
/home/ssafy/my_ws/git_lab/S14P31C205

GitLab ROS2 workspace:
/home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws

GitHub TIL / 기록 repo:
/home/ssafy/my_ws/git_hub/Robotics/VSLAM
```

이 문서는 GitHub TIL에 있는 기록 문서다.
실제 launch/config 산출물은 GitLab에 있다.

## 현재 GitLab 작업트리 상태

이 handoff 작성 시점에 GitLab에는 이미 다른 변경도 섞여 있다.
다음 Codex는 절대 임의로 되돌리면 안 된다.

```text
 M edge/jetson/ros2_ws/src/trashbot_navigation/launch/duri_real_robot_bringup.launch.py
 M edge/jetson/ros2_ws/src/trashbot_navigation/rviz/duri_real_localization_monitor.rviz
?? edge/jetson/maps/
?? edge/jetson/ros2_ws/src/trashbot_localization/config/ekf_local_duri_encoder_imu.yaml
?? edge/jetson/ros2_ws/src/trashbot_localization/config/encoder_odom_gazebo_duri.yaml
?? edge/jetson/ros2_ws/src/trashbot_localization/launch/duri_ekf_local.launch.py
?? edge/jetson/ros2_ws/src/trashbot_localization/launch/duri_gazebo_encoder_odom.launch.py
?? edge/jetson/ros2_ws/src/trashbot_navigation/launch/duri_gazebo_sensor_fusion_rtabmap.launch.py
?? edge/jetson/ros2_ws/src/trashbot_navigation/scripts/check_laptop_duri_mapping_stack.sh
?? edge/jetson/ros2_ws/src/trashbot_navigation/scripts/start_duri_real_mapping_stack.sh
```

주의:

- `duri_real_robot_bringup.launch.py`, RViz, `edge/jetson/maps/`, mapping helper scripts는 이번 dry-run 기록의 핵심 수정 범위가 아니다.
- 이번 작업에서 직접 확인한 1순위 dry-run 산출물은 아래 5개 파일이다.

## 1순위 dry-run 산출물

### 1. Duri Gazebo encoder config

GitLab path:

```text
edge/jetson/ros2_ws/src/trashbot_localization/config/encoder_odom_gazebo_duri.yaml
```

역할:

```text
Gazebo /odom
-> gazebo_odom_to_encoder_ticks.py
-> /motor/encoder_ticks
-> encoder_ticks_to_wheel_odom.py
-> /wheel/odometry
```

핵심 내용:

- `integration_source: pose`
- `ticks_per_revolution: 1560.0`
- `effective_wheel_radius_m: 0.021`
- `track_width_m: 0.219716`
- `publish_tf: false`

`track_width_m: 0.219716`은 Duri URDF의 track center `+/-0.109858 m`에서 나온 Gazebo dry-run용 값이다.
실제 Duri wheel/track calibration 값으로 확정하면 안 된다.

### 2. Duri encoder + IMU EKF config

GitLab path:

```text
edge/jetson/ros2_ws/src/trashbot_localization/config/ekf_local_duri_encoder_imu.yaml
```

역할:

```text
/wheel/odometry
+ /imu/data_bno08x_like
-> robot_localization ekf_node
-> /odometry/local
```

핵심 내용:

- `frequency: 30.0`
- `two_d_mode: true`
- `publish_tf: false`
- `world_frame: odom`
- `odom0: /wheel/odometry`
- `imu0: /imu/data_bno08x_like`

`publish_tf: false`인 이유:

- Gazebo `planar_move` plugin이 이미 `odom -> base_footprint` TF를 publish한다.
- dry-run에서 EKF까지 같은 TF를 publish하면 TF owner가 중복된다.
- 실제 하드웨어에서는 EKF가 `odom -> base_footprint`를 맡도록 별도 실차 profile에서 바꾸는 것이 맞다.

### 3. Duri Gazebo encoder bridge launch

GitLab path:

```text
edge/jetson/ros2_ws/src/trashbot_localization/launch/duri_gazebo_encoder_odom.launch.py
```

역할:

```text
gazebo_odom_to_encoder_ticks.py
+ encoder_ticks_to_wheel_odom.py
```

기본 topic:

```text
input:  /odom
middle: /motor/encoder_ticks
output: /wheel/odometry
```

검증 포인트:

```bash
ros2 topic echo /motor/encoder_ticks --once
ros2 topic echo /wheel/odometry --once
```

### 4. Duri local EKF launch

GitLab path:

```text
edge/jetson/ros2_ws/src/trashbot_localization/launch/duri_ekf_local.launch.py
```

역할:

```text
/imu/data
-> imu_covariance_republisher.py
-> /imu/data_bno08x_like

/wheel/odometry + /imu/data_bno08x_like
-> robot_localization ekf_node
-> /odometry/local
```

검증 포인트:

```bash
ros2 topic echo /imu/data_bno08x_like --once
ros2 topic echo /odometry/local --once
```

### 5. Duri Gazebo sensor-fusion RTAB-Map launch

GitLab path:

```text
edge/jetson/ros2_ws/src/trashbot_navigation/launch/duri_gazebo_sensor_fusion_rtabmap.launch.py
```

역할:

```text
Gazebo Duri
+ Duri fake encoder bridge
+ Duri encoder+IMU EKF
+ RTAB-Map external odom
+ optional Nav2 smoke test
```

기본값:

```text
start_gazebo:=true
start_encoder_bridge:=true
start_ekf:=true
start_rtabmap:=true
start_nav2:=false
camera_pitch:=0.436332
local_odom_topic:=/odometry/local
```

RTAB-Map 연결 기준:

```text
visual_odometry:=false
odom_topic:=/odometry/local
odom_frame_id:=odom
frame_id:=base_footprint
```

## 이번 대화에서 실제로 보정한 부분

처음 확인했을 때 1순위 산출물 대부분은 이미 untracked 상태로 존재했다.
이번 대화에서는 기존 산출물을 덮어쓰지 않고 검토한 뒤, 통합 launch 하나를 실행 안정성 기준으로 보정했다.

수정 파일:

```text
edge/jetson/ros2_ws/src/trashbot_navigation/launch/duri_gazebo_sensor_fusion_rtabmap.launch.py
```

수정 내용:

1. `PythonExpression` import 추가
2. `delete_db_on_start` launch argument 추가
3. RTAB-Map args에 조건부 `--delete_db_on_start` 반영
4. `odom_frame_id` launch argument 추가
5. RTAB-Map include에 `odom_frame_id:=odom` 명시
6. 기본 `camera_pitch`를 `0.0`에서 `0.436332`로 변경

보정 이유:

- 현재 Mari/Duri Gazebo RTAB-Map 검증 기준은 카메라 pitch 25도다.
- RTAB-Map external odom 모드에서 odom frame을 명시해야 `/odometry/local`과 `odom` frame 계약이 분명해진다.
- mapping dry-run은 매번 DB를 지우는 것이 재현성에 좋고, localization 모드에서는 DB를 유지해야 하므로 `delete_db_on_start`를 인자로 열어두는 것이 좋다.

## 검증 완료한 것

### Python 문법 검사

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205

python3 -m py_compile \
  edge/jetson/ros2_ws/src/trashbot_localization/launch/duri_gazebo_encoder_odom.launch.py \
  edge/jetson/ros2_ws/src/trashbot_localization/launch/duri_ekf_local.launch.py \
  edge/jetson/ros2_ws/src/trashbot_navigation/launch/duri_gazebo_sensor_fusion_rtabmap.launch.py
```

결과:

```text
pass
```

### YAML parse 검사

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205

python3 - <<'PY'
from pathlib import Path
import yaml

paths = [
    Path('edge/jetson/ros2_ws/src/trashbot_localization/config/encoder_odom_gazebo_duri.yaml'),
    Path('edge/jetson/ros2_ws/src/trashbot_localization/config/ekf_local_duri_encoder_imu.yaml'),
]

for path in paths:
    with path.open() as f:
        yaml.safe_load(f)
    print(f'OK {path}')
PY
```

결과:

```text
OK edge/jetson/ros2_ws/src/trashbot_localization/config/encoder_odom_gazebo_duri.yaml
OK edge/jetson/ros2_ws/src/trashbot_localization/config/ekf_local_duri_encoder_imu.yaml
```

### colcon build

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash

colcon build --symlink-install \
  --packages-select trashbot_description trashbot_localization trashbot_navigation \
  --allow-overriding trashbot_description trashbot_localization trashbot_navigation
```

결과:

```text
Summary: 3 packages finished
```

### launch argument 해석

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_localization duri_gazebo_encoder_odom.launch.py --show-args
ros2 launch trashbot_localization duri_ekf_local.launch.py --show-args
ros2 launch trashbot_navigation duri_gazebo_sensor_fusion_rtabmap.launch.py --show-args
```

확인된 핵심 기본값:

```text
duri_gazebo_encoder_odom.launch.py:
  gazebo_odom_topic:=/odom
  encoder_topic:=/motor/encoder_ticks
  wheel_odom_topic:=/wheel/odometry
  publish_tf:=false

duri_ekf_local.launch.py:
  raw_imu_topic:=/imu/data
  filtered_imu_topic:=/imu/data_bno08x_like
  output_odom_topic:=/odometry/local

duri_gazebo_sensor_fusion_rtabmap.launch.py:
  camera_pitch:=0.436332
  local_odom_topic:=/odometry/local
  odom_frame_id:=odom
  start_nav2:=false
```

### no-op launch 확인

아래 명령으로 launch 파일이 모든 하위 include를 찾고 인자를 해석하는지 확인했다.

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

timeout 8 ros2 launch trashbot_navigation duri_gazebo_sensor_fusion_rtabmap.launch.py \
  start_gazebo:=false \
  start_encoder_bridge:=false \
  start_ekf:=false \
  start_rtabmap:=false \
  start_nav2:=false
```

결과:

```text
launch startup succeeded; timeout exit 124 because no nodes were started
```

이 `124`는 실패가 아니라 `timeout`이 빈 launch를 8초 뒤 종료한 결과다.

## 2026-05-16 2순위 Gazebo EKF 검증 업데이트

2순위 목표는 RTAB-Map/Nav2까지 가기 전에 아래 체인이 Gazebo에서 실제로 이어지는지 보는 것이다.

```text
/cmd_vel
-> Gazebo Duri movement
-> /odom
-> /motor/encoder_ticks
-> /wheel/odometry
-> /imu/data_bno08x_like
-> /odometry/local
```

실행한 명령:

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash

colcon build --symlink-install \
  --packages-select trashbot_description trashbot_localization trashbot_navigation \
  --allow-overriding trashbot_description trashbot_localization trashbot_navigation
source install/setup.bash

ros2 launch trashbot_navigation duri_gazebo_sensor_fusion_rtabmap.launch.py \
  gui:=false \
  verbose:=false \
  start_rtabmap:=false \
  start_nav2:=false
```

빌드 결과:

```text
Summary: 3 packages finished
```

실행 중 확인된 것:

```text
Gazebo gzserver started
Duri spawn succeeded
Gazebo planar_move subscribed to /cmd_vel
Gazebo planar_move advertised /odom
gazebo_odom_to_encoder_ticks.py started
encoder_ticks_to_wheel_odom.py started
imu_covariance_republisher.py started
robot_localization ekf_node started
```

확인 명령:

```bash
ros2 topic list -t | sort | grep -E 'cmd_vel|encoder|wheel|odom|imu|tf|clock|camera'
ros2 topic echo /motor/encoder_ticks --once
ros2 topic echo /wheel/odometry --once
ros2 topic echo /imu/data_bno08x_like --once
ros2 topic echo /odometry/local --once
timeout 5 ros2 run tf2_ros tf2_echo odom base_footprint
```

통과한 항목:

- `/cmd_vel` topic 존재
- `/odom` topic 존재
- `/motor/encoder_ticks` publish 확인
- `/wheel/odometry` publish 확인
- `/imu/data_bno08x_like` publish 확인
- `/odometry/local` publish 확인
- Gazebo camera/depth pointcloud topic 존재 확인

확인된 핵심 frame 계약:

```text
/wheel/odometry:
  header.frame_id: odom
  child_frame_id: base_footprint

/odometry/local:
  header.frame_id: odom
  child_frame_id: base_footprint
```

## 2026-05-16 2순위에서 수정한 버그

처음 검증했을 때 `/wheel/odometry`가 아래처럼 잘못 나왔다.

```text
header.frame_id: base_footprint
child_frame_id: base_footprint
```

원인:

- parent launch인 `duri_gazebo_sensor_fusion_rtabmap.launch.py`에 RTAB-Map용 `frame_id` launch argument가 있다.
- child launch인 `duri_gazebo_encoder_odom.launch.py`에도 wheel odometry용 `frame_id` launch argument가 있다.
- parent include에서 child `frame_id`를 명시하지 않아서 parent의 `frame_id:=base_footprint`가 child로 전파됐다.
- 결과적으로 `/wheel/odometry`의 기준 frame이 `odom`이 아니라 `base_footprint`가 됐다.

수정 파일:

```text
edge/jetson/ros2_ws/src/trashbot_navigation/launch/duri_gazebo_sensor_fusion_rtabmap.launch.py
```

수정 내용:

```python
encoder_bridge = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
        PathJoinSubstitution(
            [
                FindPackageShare("trashbot_localization"),
                "launch",
                "duri_gazebo_encoder_odom.launch.py",
            ]
        )
    ),
    condition=IfCondition(start_encoder_bridge),
    launch_arguments={
        "use_sim_time": use_sim_time,
        "encoder_config": encoder_config,
        "gazebo_odom_topic": gazebo_odom_topic,
        "encoder_topic": encoder_topic,
        "wheel_odom_topic": wheel_odom_topic,
        "frame_id": "odom",
        "child_frame_id": "base_footprint",
        "publish_tf": "false",
    }.items(),
)
```

수정 후 `/wheel/odometry`와 `/odometry/local`의 frame 계약은 정상으로 돌아왔다.

## 2순위 검증의 현재 한계

현재 ROS graph에 기존 monitor stack이 남아 있었다.

```text
/usr/bin/python3 /opt/ros/humble/bin/ros2 launch trashbot_navigation duri_real_laptop_monitor.launch.py
```

이 프로세스 때문에 아래 노드가 dry-run과 별개로 계속 보였다.

```text
/duri_keyboard_teleop
/robot_state_publisher
/rtabmap/rgbd_odometry
/rtabmap/rtabmap
```

그래서 `tf2_echo odom base_footprint`에서는 transform은 나오지만 `TF_OLD_DATA` 경고가 섞였다.
이번 검증에서는 이 기존 monitor stack을 임의로 종료하지 않았다.

다음 Codex가 TF까지 깨끗하게 검증하려면 먼저 기존 monitor stack을 끄고 ROS graph를 정리한 뒤 다시 실행해야 한다.

```bash
# 사용자에게 확인 후 실행하는 것이 안전하다.
pkill -INT -f 'duri_real_laptop_monitor.launch.py|rtabmap|rgbd_odometry|duri_keyboard_teleop'
ros2 daemon stop
ros2 daemon start
```

그 다음 다시 아래 launch를 실행한다.

```bash
ros2 launch trashbot_navigation duri_gazebo_sensor_fusion_rtabmap.launch.py \
  gui:=false \
  verbose:=false \
  start_rtabmap:=false \
  start_nav2:=false
```

아직 미완료인 항목:

- 깨끗한 ROS graph에서 `odom -> base_footprint` TF 재검증
- Gazebo에서 `/cmd_vel`을 줬을 때 `/motor/encoder_ticks`, `/wheel/odometry`, `/odometry/local` 값이 연속적으로 변하는지 확인
- RTAB-Map이 `/odometry/local`을 받아 `/rtabmap/map`, `/rtabmap/info`, `map -> odom`을 만드는지 확인
- optional Nav2 smoke test

## 다음 Codex가 바로 실행할 명령

### 1. 작업트리 먼저 확인

```bash
git -C /home/ssafy/my_ws/git_lab/S14P31C205 status --short
git -C /home/ssafy/my_ws/git_hub status --short
```

기존 변경을 되돌리지 말고, 새 작업 범위만 분리해서 진행한다.

### 2. build 재확인

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash

colcon build --symlink-install \
  --packages-select trashbot_description trashbot_localization trashbot_navigation \
  --allow-overriding trashbot_description trashbot_localization trashbot_navigation
source install/setup.bash
```

### 3. Gazebo + sensor fusion + RTAB-Map dry-run 실행

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_navigation duri_gazebo_sensor_fusion_rtabmap.launch.py \
  gui:=true \
  start_nav2:=false
```

GUI가 부담되면:

```bash
ros2 launch trashbot_navigation duri_gazebo_sensor_fusion_rtabmap.launch.py \
  gui:=false \
  start_nav2:=false
```

### 4. topic/TF 확인

다른 터미널:

```bash
cd /home/ssafy/my_ws/git_lab/S14P31C205/edge/jetson/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 topic list -t | sort | grep -E 'encoder|wheel|odom|imu|tf|rtabmap|camera'
ros2 topic echo /motor/encoder_ticks --once
ros2 topic echo /wheel/odometry --once
ros2 topic echo /imu/data_bno08x_like --once
ros2 topic echo /odometry/local --once
timeout 5 ros2 run tf2_ros tf2_echo odom base_footprint
```

RTAB-Map 확인:

```bash
ros2 topic echo /rtabmap/info --once
ros2 topic echo /rtabmap/map --once --field info
timeout 5 ros2 run tf2_ros tf2_echo map odom
```

### 5. Gazebo에서 움직임 주기

RTAB-Map은 움직임이 있어야 의미 있는 map node가 생긴다.

```bash
timeout 3 ros2 topic pub -r 5 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.05}, angular: {z: 0.0}}"

ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist '{}'
```

회전은 천천히 시작한다.

```bash
timeout 3 ros2 topic pub -r 5 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.15}}"

ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist '{}'
```

## 성공 판정

아래가 모두 확인되면 1순위 dry-run은 성공이다.

```text
/motor/encoder_ticks publish
/wheel/odometry publish
/imu/data_bno08x_like publish
/odometry/local publish
odom -> base_footprint TF 유지
RTAB-Map visual_odometry false 상태에서 /odometry/local 입력 사용
/rtabmap/map 또는 /rtabmap/info publish
map -> odom TF publisher가 하나만 존재
```

## 실패 시 우선 확인

### `/motor/encoder_ticks`가 안 나옴

- `/odom`이 먼저 나오는지 확인한다.
- Gazebo Duri가 spawn됐는지 확인한다.
- `duri_gazebo_odom_to_encoder_ticks` node가 떠 있는지 확인한다.

```bash
ros2 node list | grep -E 'duri|encoder|gazebo'
ros2 topic echo /odom --once
```

### `/wheel/odometry`가 안 나옴

- `/motor/encoder_ticks` 메시지 형식이 `std_msgs/msg/Int64MultiArray`인지 확인한다.
- `encoder_odom_gazebo_duri.yaml`이 install path에 들어갔는지 확인한다.

```bash
ros2 topic info /motor/encoder_ticks -v
ros2 node list | grep wheel
```

### `/odometry/local`이 안 나옴

- `robot_localization` 설치 여부를 확인한다.
- `/wheel/odometry`와 `/imu/data_bno08x_like`가 둘 다 들어오는지 확인한다.

```bash
ros2 pkg prefix robot_localization
ros2 topic echo /wheel/odometry --once
ros2 topic echo /imu/data_bno08x_like --once
```

### RTAB-Map이 안 뜸

- camera topic과 `/odometry/local`이 먼저 들어오는지 확인한다.
- `visual_odometry:=false`, `odom_topic:=/odometry/local`, `odom_frame_id:=odom`인지 확인한다.
- camera info topic은 Duri Gazebo URDF 기준 `/camera/camera/color/camera_info`다.

```bash
ros2 topic echo /camera/camera/color/image_raw --once
ros2 topic echo /camera/camera/aligned_depth_to_color/image_raw --once
ros2 topic echo /camera/camera/color/camera_info --once
ros2 topic echo /odometry/local --once
```

### TF 충돌 의심

Gazebo dry-run에서는 EKF와 wheel odom이 TF를 publish하지 않는 것이 의도다.

```text
encoder_odom_gazebo_duri.yaml:
  publish_tf: false

ekf_local_duri_encoder_imu.yaml:
  publish_tf: false
```

`odom -> base_footprint`는 Gazebo `planar_move`가 맡는다.
실차에서는 이 구조를 그대로 쓰면 안 되고, EKF가 TF를 맡는 별도 real profile이 필요하다.

## optional Nav2 smoke test

RTAB-Map과 `/odometry/local`이 안정적일 때만 Nav2를 켠다.

```bash
ros2 launch trashbot_navigation duri_gazebo_sensor_fusion_rtabmap.launch.py \
  gui:=true \
  start_nav2:=true
```

주의:

- 이 launch는 Nav2 include에 `start_map_to_odom_tf:=false`를 넘긴다.
- 이유는 RTAB-Map이 `map -> odom`을 publish해야 하기 때문이다.
- static `map -> odom`과 RTAB-Map `map -> odom`이 동시에 나오면 안 된다.

짧은 goal:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "
pose:
  header:
    frame_id: map
  pose:
    position:
      x: 0.3
      y: 0.0
      z: 0.0
    orientation:
      w: 1.0
" --feedback
```

## 이번 작업의 한계

하드웨어가 없으므로 아래는 확정하지 않았다.

- 실제 Duri wheel radius
- 실제 Duri track width
- encoder tick sign
- left/right distance scale
- motor response
- 실제 IMU covariance
- 실제 GPS/NavSatFix
- 실차에서 EKF가 `odom -> base_footprint` TF를 맡는 최종 profile

즉, 이번 작업은 **실차 calibration**이 아니라 **시뮬레이션 배선과 launch 구조 고정**이다.

## 다음 구현 권장 순서

1. Gazebo full run으로 `/motor/encoder_ticks`, `/wheel/odometry`, `/odometry/local` 확인
2. RTAB-Map이 `/odometry/local` external odom으로 map을 만드는지 확인
3. map/odom TF owner가 하나인지 확인
4. Nav2는 `start_nav2:=true`로 아주 짧은 goal만 smoke test
5. 성공하면 GitHub TIL `docs/progress/` 또는 `daily/2026-05-16/`에 실행 결과와 캡처를 추가
6. 그 다음에 depth obstacle layer와 GPS mock global EKF로 넘어간다
