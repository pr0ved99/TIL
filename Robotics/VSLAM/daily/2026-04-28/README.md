# 2026-04-28 작업 일지

## 결론

- 오늘의 핵심 결과는 Mari를 Gazebo에 올려야 하는 이유를 별도 문서로 정리하고, Gazebo Classic에서 Mari를 반복 spawn할 수 있는 실행 baseline을 추가한 것이다.
- `mari.urdf.xacro`에 `use_mesh_visual` 옵션을 추가해, 무거운 STL visual과 안정적인 box debug visual을 전환할 수 있게 했다.
- `gazebo_mari.launch.py`를 추가해 Gazebo server/client, `robot_state_publisher`, `spawn_entity.py`를 한 번에 실행할 수 있게 했다.
- `mari_empty.world`를 추가해 Gazebo 기본 world가 온라인 model database에 의존하지 않도록 했다.
- headless 검증에서 `use_mesh_visual:=false`와 `use_mesh_visual:=true` 모두 `SpawnEntity: Successfully spawned entity [mari]`까지 확인했다.
- 추가로 `gz model -m mari -i`에서 `mari` entity와 debug box visual geometry가 Gazebo world에 들어간 것을 확인했다.
- GUI 확인에서 `use_mesh_visual:=true` 기준 full STL Mari visual이 Gazebo 화면에 정상 표시되는 것을 확인했다.
- 앞/뒤 좌우 총 4개 collision-only virtual track wheel을 추가해 전진/정지/후진 시 pitch가 크게 생기는 문제를 줄였다.
- 다만 GUI 직접 조종에서 궤도형 skid-steer 회전이 접촉 마찰에 따라 끊기는 느낌이 있어, Gazebo 주행 제어를 `libgazebo_ros_planar_move.so`로 전환했다.
- 이제 `/cmd_vel` 회전은 바퀴 접지 마찰에 의존하지 않고 Gazebo 평면 pose를 직접 갱신한다.
- 격리 검증에서 회전 명령 후 yaw가 `-0.002597 -> 0.978302 rad`로 변했고, roll/pitch는 대략 `1e-4 rad` 이하로 유지됐다.
- `/odom` topic과 `odom -> base_footprint` TF publish도 `mari_planar_move` 기준으로 확인했다.
- `Tools/teleop_mari_keyboard.py`를 추가했다. Gazebo 창이 아니라 teleop 터미널에서 키 입력을 받아 `/cmd_vel`을 publish하는 방식으로 정리했다.
- 조종이 뚝뚝 끊겨 보이는 문제를 줄이기 위해 teleop 기본 publish rate를 `50 Hz`로 올리고, 선형/각속도 가속도 제한을 추가했다.
- Gazebo 가상 IMU/RGB-D sensor plugin을 추가해 `/imu/data`, RGB image, depth image, camera_info topic 수신까지 1차 확인했다.
- `Tools/check_mari_gazebo_sensor_topics.py`를 추가해 Gazebo 센서 토픽 수신 여부를 자동으로 확인할 수 있게 했다.
- RViz2 진행 기록을 재확인한 결과, `base_link`를 낮추는 방식은 잘못된 보정으로 판단해 되돌렸다.
- 현재 기준은 `base_footprint -> base_link = 0.0252 m` 유지와 `chassis_mesh_z = -base_link_z - chassis_mesh_min_z` visual offset 보정이다.
- RViz2/Gazebo 장착 높이를 맞추기 위해 `camera_z`를 `0.122174 m`에서 `0.112174 m`로 `10 mm` 낮췄다.
- 다음 실제 개발 단계는 이 가상 센서 baseline을 RTAB-Map 또는 VSLAM smoke test에 연결한 뒤, 실제 hardware encoder/odom, IMU, D435i topic과 맞춰보는 것이다.

## 오늘 작업 한 줄 요약

- Gazebo가 필요한 이유를 문서화하고, Mari Gazebo spawn/full STL visual/`planar_move` 주행 baseline과 키보드 직접 조종 스크립트를 실행 가능한 형태로 만들었다.

## 배경

- RViz2에서는 Mari visual mesh와 센서 TF가 정상적으로 보이는 상태였다.
- 하지만 Gazebo Classic에서는 `mari` entity는 생성되지만 full STL visual이 안정적으로 보이지 않는 blocker가 남아 있었다.
- 바로 diff-drive plugin을 붙이면 visual 문제와 주행 문제가 섞이므로, 먼저 Gazebo spawn/visual baseline을 분리하기로 했다.

## 만든 문서

- [Why_Mari_Gazebo_Baseline_Is_Needed.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/progress/Why_Mari_Gazebo_Baseline_Is_Needed.md)

정리한 핵심:

- Gazebo는 예쁜 3D 모델을 보기 위한 도구가 아니라, `/cmd_vel -> 로봇 이동 -> /odom -> TF -> 센서/Nav2/VSLAM` 흐름을 실제 하드웨어 전에 검증하기 위한 시뮬레이터다.
- RViz2는 좌표계와 모델 확인용이고, Gazebo는 물리 이동과 충돌, 주행 명령, odom 생성을 확인하는 단계다.
- 오늘 목표는 full STL 고집이 아니라, Gazebo에서 Mari entity와 visual baseline을 안정적으로 띄우는 것이다.

## 구현 내용

### 1. `mari.urdf.xacro` visual 전환 옵션 추가

- `use_mesh_visual` xacro argument를 추가했다.
- 기본값은 `true`로 유지해 RViz2 기존 동작을 보존했다.
- Gazebo launch에서는 기본값을 `false`로 넘겨 debug box visual을 먼저 띄운다.

```bash
xacro trashbot_description/urdf/mari.urdf.xacro use_mesh_visual:=false > /tmp/mari_box.urdf
xacro trashbot_description/urdf/mari.urdf.xacro use_mesh_visual:=true > /tmp/mari_mesh.urdf
```

### 2. Gazebo 전용 launch 추가

- [gazebo_mari.launch.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/launch/gazebo_mari.launch.py)

실행:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_description gazebo_mari.launch.py
```

기본값:

```text
gui              = true
use_mesh_visual  = false
verbose          = true
world            = trashbot_description/worlds/mari_empty.world
entity_name      = mari
```

full STL visual 재시험:

```bash
ros2 launch trashbot_description gazebo_mari.launch.py use_mesh_visual:=true
```

### 3. 로컬 Gazebo world 추가

- [mari_empty.world](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/worlds/mari_empty.world)
- `sun`과 `ground_plane`을 `model://` include가 아니라 world 파일 내부에 직접 정의했다.
- Gazebo 기본 world가 온라인 model database 조회로 지연되거나 경고를 내는 문제를 줄이기 위한 기준 world다.

### 4. Gazebo virtual track support + planar_move 추가

- `left_front`, `right_front`, `left_rear`, `right_rear` 총 4개 collision-only virtual track wheel을 추가했다.
- 이 링크들은 실제 궤도 벨트 구동을 재현하는 용도가 아니라, Gazebo에서 Mari가 한 점 바퀴처럼 앞뒤로 들리지 않도록 접지 지지점을 늘리는 용도다.
- `track_width = 0.137553 m`, `effective_track_radius = 0.021 m`를 contact geometry 기준값으로 사용했다.
- 차체 collision box가 바닥에 닿아 가상 접지 링크를 방해하지 않도록 `collision_z = 0.012 m`로 주행용 collision을 살짝 띄웠다.
- GUI 직접 조종에서 skid-steer 방식 회전이 마찰에 따라 되다 말다 하는 현상이 보여, 실제 이동 제어는 `libgazebo_ros_planar_move.so`로 바꿨다.
- `planar_move`는 `/cmd_vel`을 받아 Gazebo 평면 pose를 직접 갱신하고, `/odom`과 `odom -> base_footprint` TF를 publish한다.

핵심 흐름:

```text
/cmd_vel
-> libgazebo_ros_planar_move.so
-> Gazebo planar pose update
-> /odom
-> odom -> base_footprint TF
```

### 5. Gazebo 가상 IMU/RGB-D sensor topic 추가

- `imu_link`에 `libgazebo_ros_imu_sensor.so` 기반 IMU sensor를 추가했다.
- `camera_link`에 `libgazebo_ros_camera.so` 기반 depth camera sensor를 추가했다.
- Gazebo depth camera 하나에서 RGB image, depth image, camera_info, pointcloud를 publish하도록 구성했다.
- 실제 D435i 토픽 구조에 맞추기 위해 RGB-D topic 이름은 `/camera/camera/...` 형태로 맞췄다.
- IMU message의 `frame_id`는 `imu_link`, RGB-D message의 `frame_id`는 `camera_color_optical_frame`으로 확인했다.

기대 토픽:

```text
/odom
/imu/data
/camera/camera/color/image_raw
/camera/camera/aligned_depth_to_color/image_raw
/camera/camera/color/camera_info
/camera/camera/aligned_depth_to_color/camera_info
/camera/camera/depth/color/points
```

검증 스크립트:

- [check_mari_gazebo_sensor_topics.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/Tools/check_mari_gazebo_sensor_topics.py)

실행:

```bash
python3 Tools/check_mari_gazebo_sensor_topics.py
```

### 6. RViz2 기준 `base_link`/mesh offset 재확인

- Progress 문서의 RViz2 검증 기록을 다시 확인한 결과, 링크 좌표계는 유지하고 visual mesh만 yaw/z offset으로 맞추는 방식이 올바른 기준이다.
- 따라서 `base_link_z=0.021 m`로 낮추는 시도는 되돌렸고, 현재는 RViz2에서 검증했던 `base_link_z=0.0252 m`를 유지한다.
- `0.021 m` 값은 가상 궤도 접지 반지름 후보로는 계속 사용하지만, `base_footprint -> base_link` 높이 기준으로는 쓰지 않는다.
- visual mesh 최저점은 `chassis_mesh_z = -base_link_z - chassis_mesh_min_z` 계산식으로 `base_footprint` 기준 `z=0`에 맞춘다.
- 카메라 높이는 RViz2/Gazebo 공통 기준으로 `camera_z=0.112174 m`를 적용한다.

렌더링된 TF 높이:

```text
base_footprint -> base_link   z=0.025200
base_footprint -> camera_link z=0.137374
base_footprint -> imu_link    z=0.043594
base_footprint -> gps_link    z=0.063143
virtual_track_wheel_link      z=0.021000
```

## 검증 결과

### xacro / URDF 검증

```bash
source /opt/ros/humble/setup.bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

xacro trashbot_description/urdf/mari.urdf.xacro use_mesh_visual:=false > /tmp/mari_box.urdf
check_urdf /tmp/mari_box.urdf

xacro trashbot_description/urdf/mari.urdf.xacro use_mesh_visual:=true > /tmp/mari_mesh.urdf
check_urdf /tmp/mari_mesh.urdf
```

결과:

```text
Successfully Parsed XML
root Link: base_footprint
```

### colcon build

```bash
source /opt/ros/humble/setup.bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
colcon build --symlink-install --packages-select trashbot_description
```

결과:

```text
1 package finished
```

### Gazebo headless spawn 검증

debug box visual 기준:

```bash
ros2 launch trashbot_description gazebo_mari.launch.py gui:=false use_mesh_visual:=false verbose:=true
```

full STL visual 기준:

```bash
ros2 launch trashbot_description gazebo_mari.launch.py gui:=false use_mesh_visual:=true verbose:=true
```

결과:

```text
Spawn status: SpawnEntity: Successfully spawned entity [mari]
```

### Gazebo model state 확인

```bash
gz model -m mari -i
```

확인한 내용:

- `name: "mari"`
- `is_static: false`
- `mari::base_footprint`
- debug box visual geometry가 `type: BOX`로 들어감

### Gazebo GUI visual 확인

debug box visual 기준:

```bash
ros2 launch trashbot_description gazebo_mari.launch.py
```

full STL visual 기준:

```bash
ros2 launch trashbot_description gazebo_mari.launch.py use_mesh_visual:=true
```

확인한 내용:

- `use_mesh_visual:=false` 기준으로 Gazebo GUI에서 단순 box body, camera box, IMU/GPS visual이 표시됐다.
- `use_mesh_visual:=true` 기준으로 Gazebo GUI에서 Mari full STL visual이 정상 표시됐다.
- 따라서 기존 blocker였던 "Gazebo Classic에서 Mari visual mesh가 보이지 않음"은 현재 실행 경로 기준으로 해소됐다.

증빙 이미지 저장 경로:

- [01_mari_gazebo_debug_box_visual_baseline.png](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/robot_model_exports/mari_gazebo/01_mari_gazebo_debug_box_visual_baseline.png)
- [02_mari_gazebo_full_stl_visual_success.png](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/robot_model_exports/mari_gazebo/02_mari_gazebo_full_stl_visual_success.png)

### Gazebo planar_move 주행 검증

문제 상황:

- `num_wheel_pairs=2` 기반 skid-steer 근사는 headless 수치상 전진/회전이 가능했다.
- 하지만 GUI에서 직접 조종할 때 회전이 접촉 마찰에 따라 되다 말다 하는 느낌이 있었다.
- 현재 목표는 실제 궤도 물리 재현이 아니라 encoder/IMU/RGB-D topic 검증 전 `/cmd_vel -> /odom -> TF` 흐름을 안정화하는 것이다.

해결:

- 구동 plugin을 `libgazebo_ros_diff_drive.so`에서 `libgazebo_ros_planar_move.so`로 바꿨다.
- 4개 virtual track wheel은 계속 collision-only 접지/지지 링크로 유지했다.
- virtual track wheel 마찰은 `mu1=0.2`, `mu2=0.2`로 낮춰, 평면 이동 중 불필요한 회전 저항을 줄였다.

실제 encoder/IMU/RGB-D topic 검증과의 관계:

- 이번 변경은 Gazebo 제어 안정화를 위한 시뮬레이션 전용 구성이다.
- 실제 encoder 값은 하드웨어 노드가 publish하는 ROS topic을 보면 되므로, Gazebo virtual track wheel joint와 직접 연결하지 않는다.
- 나중에 simulated encoder가 꼭 필요하면 별도 encoder simulator node를 추가해서 `/joint_states` 또는 `/odom` 기반으로 만들면 된다.

격리 headless full STL visual 검증:

```bash
ROS_DOMAIN_ID=78 GAZEBO_MASTER_URI=http://127.0.0.1:11347 \
ros2 launch trashbot_description gazebo_mari.launch.py gui:=false use_mesh_visual:=true verbose:=false
```

plugin 로그:

```text
mari_planar_move: Subscribed to [/cmd_vel]
mari_planar_move: Advertise odometry on [/odom]
mari_planar_move: Publishing odom transforms between [odom] and [base_footprint]
```

회전 테스트:

```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.5}}"
```

확인 결과:

```text
before pose:       x=-0.000015, y=-0.012129, roll=0.000000,  pitch=0.000002, yaw=-0.002597
after rotate pose: x=0.000467,  y=-0.027608, roll=-0.000062, pitch=0.000031, yaw=0.978302
```

전진 테스트:

```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.12}, angular: {z: 0.0}}"
```

확인 결과:

```text
after forward pose: x=0.252227, y=0.293961, roll=0.000024, pitch=0.000037, yaw=0.936806
/odom pose:         x=0.255596, y=0.291474, orientation.z=0.446298, orientation.w=0.894885
```

해석:

- yaw가 `-0.002597 -> 0.978302 rad`로 변했으므로 회전 명령이 안정적으로 반영됐다.
- roll/pitch가 `1e-4 rad` 이하로 유지됐으므로 앞뒤 들림 문제도 이 검증 경로에서는 사실상 사라졌다.
- Gazebo GUI를 이미 띄워둔 상태라면 URDF plugin 변경이 반영되지 않으므로, Gazebo를 다시 시작해야 한다.

### 키보드 teleoperation smoke test

```bash
source /opt/ros/humble/setup.bash
python3 Tools/teleop_mari_keyboard.py --key-timeout 5.0
```

`w` 입력 후 `/cmd_vel` 확인:

```bash
ros2 topic echo /cmd_vel --once
```

결과:

```text
linear.x: 0.12
angular.z: 0.0
```

`x` 입력 후에는 다음 zero velocity가 확인됐다.

```text
linear.x: 0.0
angular.z: 0.0
```

### Gazebo 가상 센서 topic smoke test

격리 실행:

```bash
ROS_DOMAIN_ID=79 GAZEBO_MASTER_URI=http://127.0.0.1:11348 \
ros2 launch trashbot_description gazebo_mari.launch.py gui:=false use_mesh_visual:=true verbose:=false
```

검증:

```bash
ROS_DOMAIN_ID=79 python3 Tools/check_mari_gazebo_sensor_topics.py --duration 6.0 --min-count 1
```

결과:

```text
[OK] odom: /odom count=301 rate=50.0 Hz frame=odom child=base_footprint
[OK] imu: /imu/data count=600 rate=99.9 Hz frame=imu_link
[OK] rgb image: /camera/camera/color/image_raw count=53 rate=9.2 Hz frame=camera_color_optical_frame size=640x480 encoding=rgb8
[OK] depth image: /camera/camera/aligned_depth_to_color/image_raw count=38 rate=6.8 Hz frame=camera_color_optical_frame size=640x480 encoding=32FC1
[OK] rgb camera info: /camera/camera/color/camera_info count=60 rate=10.1 Hz frame=camera_color_optical_frame size=640x480
[OK] depth camera info: /camera/camera/aligned_depth_to_color/camera_info count=60 rate=10.1 Hz frame=camera_color_optical_frame size=640x480
```

`base_link_z=0.021 m` 보정 시도는 RViz2 기준 문서와 충돌해 폐기했다.
현재 기준은 `base_link_z=0.0252 m` 유지이며, 아래 topic smoke test 결과는
센서 plugin 수신 확인 용도로만 남긴다.

```text
[OK] odom: /odom count=300 rate=50.0 Hz frame=odom child=base_footprint
[OK] imu: /imu/data count=601 rate=99.9 Hz frame=imu_link
[OK] rgb image: /camera/camera/color/image_raw count=24 rate=4.1 Hz frame=camera_color_optical_frame size=640x480
[OK] depth image: /camera/camera/aligned_depth_to_color/image_raw count=20 rate=3.4 Hz frame=camera_color_optical_frame size=640x480
```

## 현재 의미

- 이제 Gazebo에서 Mari entity를 반복 spawn하는 실행 경로가 생겼다.
- full STL visual 렌더링 문제와 Gazebo spawn 문제를 분리했고, 현재 실행 경로 기준으로 full STL visual은 성공했다.
- Gazebo에서 `/cmd_vel -> /odom -> odom -> base_footprint` 주행 baseline도 1차 확인했고, 현재 제어 기준은 `planar_move`다.
- 4개 collision-only virtual track wheel은 구동용이 아니라, full STL 궤도 외형 아래에서 자세를 지지하는 시뮬레이션용 접지 구조다.
- `Tools/teleop_mari_keyboard.py`로 직접 조종하면서 GUI 기준 주행 감각을 확인할 수 있다.
- Gazebo 가상 센서 기준으로 `/odom`, `/imu/data`, RGB image, depth image, camera_info 수신까지 확인했다.
- RViz2 기준 문서를 재확인해 `base_link_z=0.0252 m` 기준선을 복원했고, mesh 바닥 정렬은 visual offset으로 처리한다.
- RViz2/Gazebo 공통으로 `camera_z`를 `0.112174 m`로 조정해 카메라 박스와 camera TF를 `10 mm` 낮췄다.
- 이제 다음 단계는 이 topic 세트를 RTAB-Map 또는 VSLAM smoke test에 연결하고, 실제 하드웨어의 encoder/odom, IMU, RGB/depth topic 입력과 비교하는 것이다.

## 키보드 teleoperation 추가

추가 파일:

- [teleop_mari_keyboard.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/Tools/teleop_mari_keyboard.py)

실행:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_description gazebo_mari.launch.py use_mesh_visual:=true
```

새 터미널에서 teleop 실행:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

python3 Tools/teleop_mari_keyboard.py
```

조작:

```text
w / up        forward
s / down      backward
a / left      rotate left
d / right     rotate right
q, e          forward arc left/right
z, c          backward arc right/left
space, x, k   stop
r / f         linear speed up/down
t / g         angular speed up/down
```

스크립트는 `/cmd_vel`에 `geometry_msgs/Twist`를 publish한다. 기본 publish rate는 `50 Hz`이고, 속도 명령은 가속도 제한으로 ramping되어 시작/회전/정지가 덜 튀게 했다. 일정 시간 이동 키가 들어오지 않으면 자동으로 zero velocity를 보내므로, 터미널 포커스를 잃었을 때 로봇이 계속 움직이는 위험을 줄인다.

더 부드러운 수동 조종 확인:

```bash
python3 Tools/teleop_mari_keyboard.py \
  --rate 60 \
  --linear-accel 0.15 \
  --angular-accel 0.45 \
  --key-timeout 1.2
```

주의할 점은 이 스크립트가 터미널 표준입력으로 키를 읽는다는 것이다. Gazebo 창은 시각 피드백용이고, 실제 조종 키 입력은 teleop 스크립트를 실행한 새 터미널에서 한다.

## 남은 문제

- 현재 켜져 있는 Gazebo에는 이전 URDF plugin이 남아 있을 수 있으므로, 새 모델 반영을 위해 Gazebo를 다시 시작해야 한다.
- `planar_move`는 실제 고무 궤도 벨트 물리가 아니라 센서/topic 검증을 위한 안정화된 시뮬레이션 제어다.
- 실제 encoder 값을 Gazebo wheel joint에서 얻는 구조는 아니다. 실제 encoder 검증은 하드웨어 ROS topic 기준으로 진행한다.
- Gazebo RGB-D publish rate는 설정값 15 Hz보다 낮게 관측됐다. 다음 VSLAM smoke test에서 실제 처리 FPS와 latency 기준으로 다시 봐야 한다.

## 다음 액션

1. Gazebo를 재시작한 뒤 `use_mesh_visual:=true` 상태로 `Tools/teleop_mari_keyboard.py`를 실행해 전진/회전을 직접 확인한다.
2. `/odom`, `odom -> base_footprint`, `base_footprint -> base_link` TF를 RViz2 또는 `tf2_echo`로 재확인한다.
3. `Tools/check_mari_gazebo_sensor_topics.py`로 가상 센서 topic이 계속 들어오는지 확인한다.
4. RTAB-Map 또는 VSLAM smoke test를 Gazebo 가상 RGB-D/IMU topic에 연결한다.
5. 실제 Mari 또는 Jetson bring-up 환경에서 encoder/odom, IMU, D435i RGB/depth image, camera info topic을 확인한다.
6. 주행과 센서 topic이 안정되면 Nav2/VSLAM 연결 전 최소 baseline을 별도 문서로 정리한다.
