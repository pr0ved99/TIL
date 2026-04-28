# Mari Gazebo Run Guide

## 결론

- Mari를 Gazebo Classic에 띄울 때는 `gazebo_mari.launch.py`를 실행한다.
- full STL Mari를 보고 직접 조종하려면 Gazebo 터미널과 teleop 터미널을 분리한다.
- 키 입력은 Gazebo 창이 아니라 `Tools/teleop_mari_keyboard.py`를 실행한 터미널에서 한다.
- 실행 후 `/odom`, `/imu/data`, RGB image, depth image, `camera_info` topic을 확인한다.

## 용어

- Gazebo: 로봇의 움직임, 충돌, 센서 출력을 가상으로 만들어 주는 시뮬레이터다.
- Topic: ROS2 노드들이 데이터를 주고받는 이름 붙은 통신 채널이다.
- TF: `base_link`, `camera_link` 같은 좌표계 사이의 위치/방향 관계다.
- Teleop: 키보드나 조이스틱으로 로봇에 `/cmd_vel` 이동 명령을 보내는 방식이다.

## 0. 기본 준비

모든 터미널은 아래 경로에서 시작한다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash
```

빌드가 안 되어 있거나 새로 수정한 뒤라면 먼저 빌드한다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash

colcon build --symlink-install --packages-select trashbot_description
source install/setup.bash
```

## 1. Gazebo 실행

### Debug Box Visual

가장 안정적인 기본 실행이다. Gazebo spawn, TF, `/cmd_vel`, `/odom`, sensor plugin 경로를 먼저 확인할 때 쓴다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_description gazebo_mari.launch.py
```

### Full STL Visual

Mari 전체 STL 외형과 카메라 박스가 보이는지 확인할 때 쓴다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_description gazebo_mari.launch.py use_mesh_visual:=true
```

### Camera Test World

카메라 화면이 잘 나오는지 확인할 때는 비어 있는 world 대신 색상 패널, 박스, 기둥이 있는 테스트 world를 쓴다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_description gazebo_mari.launch.py \
  use_mesh_visual:=true \
  world:=$(pwd)/trashbot_description/worlds/mari_camera_test.world
```

현재 증빙 이미지는 아래에 보관한다.

- [01_mari_gazebo_debug_box_visual_baseline.png](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/robot_model_exports/mari_gazebo/01_mari_gazebo_debug_box_visual_baseline.png)
- [02_mari_gazebo_full_stl_visual_success.png](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/robot_model_exports/mari_gazebo/02_mari_gazebo_full_stl_visual_success.png)

## 2. 키보드 조종

Gazebo는 켜 둔 상태에서 새 터미널을 연다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

python3 Tools/teleop_mari_keyboard.py
```

더 부드럽게 움직임을 보고 싶으면 아래처럼 publish rate를 높이고 가속도를 낮춘다.

```bash
python3 Tools/teleop_mari_keyboard.py \
  --rate 60 \
  --linear-accel 0.15 \
  --angular-accel 0.45 \
  --key-timeout 1.2
```

키 입력은 이 teleop 터미널에서 한다. Gazebo 창을 클릭한 상태에서는 Gazebo가 키 입력을 가져갈 수 있다.

기본 조작:

```text
w / up       forward
s / down     backward
a / left     rotate left
d / right    rotate right
q, e          forward arc left/right
z, c          backward arc right/left
space, x, k   stop
r / f         linear speed up/down
t / g         angular speed up/down
h             help
Ctrl-C, Esc   stop and exit
```

## 3. Topic 자동 확인

Gazebo가 켜진 상태에서 새 터미널을 연다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

python3 Tools/check_mari_gazebo_sensor_topics.py
```

정상 기준은 아래 topic들이 `[OK]`로 나오는 것이다.

```text
/odom
/imu/data
/camera/camera/color/image_raw
/camera/camera/aligned_depth_to_color/image_raw
/camera/camera/color/camera_info
/camera/camera/aligned_depth_to_color/camera_info
```

## 3-1. RTAB-Map 실행과 topic 확인

Gazebo와 teleop이 켜진 상태에서 새 터미널을 연다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_description mari_rtabmap.launch.py
```

위 launch는 범용 `rtabmap_launch`에 Mari Gazebo 기본값을 넣어둔 wrapper다.
필요하면 처리 주기만 바꿔서 비교한다.

```bash
ros2 launch trashbot_description mari_rtabmap.launch.py detection_rate:=3
```

RTAB-Map이 켜진 뒤 다른 터미널에서 입력과 출력 topic을 확인한다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

python3 Tools/check_mari_rtabmap_topics.py
```

`/odom`, RGB image, depth image, camera info가 입력이고,
`/rtabmap/info`, `/rtabmap/mapData`, `/rtabmap/cloud_map`이 RTAB-Map output이다.

## 3-2. 카메라 화면 확인

Gazebo camera test world를 켠 상태에서 새 터미널을 연다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run rqt_image_view rqt_image_view
```

RGB 화면은 아래 topic을 고른다.

```text
/camera/camera/color/image_raw
```

Depth 화면은 아래 topic을 고른다. `32FC1` depth image라서 RGB처럼 보이지 않을 수 있지만, 색상 패널/박스/기둥과 거리 차이가 보이면 정상이다.

```text
/camera/camera/aligned_depth_to_color/image_raw
```

RViz2로 보고 싶으면 아래처럼 실행한다.

```bash
rviz2
```

RViz2 설정:

```text
Fixed Frame = camera_color_optical_frame
Add -> By topic -> /camera/camera/color/image_raw -> Image
Add -> By topic -> /camera/camera/aligned_depth_to_color/image_raw -> Image
```

## 4. 수동 Topic 확인

전체 topic 목록에서 핵심 topic만 확인한다.

```bash
ros2 topic list | grep -E 'odom|imu|camera|cmd_vel|tf|clock'
```

`/odom`이 들어오는지 한 번 확인한다.

```bash
ros2 topic echo /odom --once
```

IMU가 들어오는지 한 번 확인한다.

```bash
ros2 topic echo /imu/data --once
```

RGB image와 depth image가 publish되는지 확인한다.

```bash
ros2 topic hz /camera/camera/color/image_raw
ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw
```

## 5. TF 확인

`odom -> base_footprint`가 이어지는지 확인한다.

```bash
ros2 run tf2_ros tf2_echo odom base_footprint
```

`base_footprint -> base_link`가 `z=0.0252 m` 기준인지 확인한다.

```bash
ros2 run tf2_ros tf2_echo base_footprint base_link
```

카메라 frame이 연결되는지 확인한다.

```bash
ros2 run tf2_ros tf2_echo base_link camera_link
ros2 run tf2_ros tf2_echo base_link camera_color_optical_frame
```

## 6. `/cmd_vel` 직접 publish

teleop 없이 명령만 보내고 싶을 때 사용한다.

전진:

```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.12}, angular: {z: 0.0}}"
```

회전:

```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.5}}"
```

정지:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

## 7. 현재 기대 상태

- Gazebo GUI에서 debug box visual과 full STL visual 모두 표시된다.
- full STL visual에서는 카메라 박스가 Mari 상단 위치에 맞게 표시된다.
- `mari_camera_test.world`에서는 전방 색상 패널, 좌우 박스, 기둥이 카메라 화면에 보여야 한다.
- 현재 `camera_link` 높이는 `base_link` 기준 `z=0.112174 m`다.
- `planar_move` plugin이 `/cmd_vel`을 받아 Gazebo 평면 pose를 갱신한다.
- `/odom`과 `odom -> base_footprint` TF가 publish된다.
- Gazebo 가상 IMU/RGB-D sensor topic이 publish된다.

## 8. 흔한 실수

- Gazebo 창을 클릭한 뒤 키를 누르면 teleop이 아니라 Gazebo가 키 입력을 가져갈 수 있다.
- `source install/setup.bash`를 안 하면 새 launch 파일이나 package resource를 못 찾을 수 있다.
- URDF/Xacro를 수정한 뒤에는 `colcon build --symlink-install --packages-select trashbot_description`를 다시 실행한다.
- Gazebo가 이미 켜져 있으면 이전 URDF/plugin 상태가 남아 있을 수 있으므로 재시작한다.
- `base_link_z`는 현재 `0.0252 m` 기준이고, `0.021 m`는 가상 궤도 접지 반지름 후보로만 본다.
- 기본 `mari_empty.world`는 일부러 비어 있으므로 카메라 화면 확인에는 `mari_camera_test.world`를 쓴다.
- 로봇 움직임이 튀면 teleop의 `--linear-accel`, `--angular-accel` 값을 낮춘다.
- RTAB-Map 화면이 튀면 teleop보다 camera FPS, Gazebo FPS, `Rtabmap/DetectionRate`, CPU/GPU 부하를 같이 봐야 한다.
