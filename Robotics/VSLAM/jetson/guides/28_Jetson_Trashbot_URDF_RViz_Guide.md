# 28 Jetson Trashbot URDF RViz Guide

## 목적

- Sprint 3의 `로봇 모델링` 작업을 시작하기 위해 `trashbot_description` 모델을 Jetson에서 확인한다.
- 목표는 실제 치수 완성보다 먼저 `base_link`, 바퀴, `D435i`, `BNO08x`, GPS frame 구조가 RViz2에서 보이는지 확인하는 것이다.

## 현재 전제

- 패키지: `trashbot_description`
- 모델: `trashbot_description/urdf/trashbot.urdf.xacro`
- launch: `trashbot_description/launch/display.launch.py`
- RViz config: `trashbot_description/rviz/trashbot_model.rviz`

## 1. 필요한 ROS 패키지를 설치한다

이 단계는 xacro 렌더링, wheel joint 확인, RViz2 표시를 위해 필요한 실행 패키지를 설치하는 단계다.

```bash
sudo apt update
sudo apt install -y \
  ros-humble-xacro \
  ros-humble-joint-state-publisher \
  ros-humble-joint-state-publisher-gui
```

왜 이 명령을 쓰는가:

- `xacro`가 없으면 `.urdf.xacro`를 실제 URDF로 렌더링할 수 없다.
- `joint_state_publisher_gui`가 없으면 RViz2에서 wheel joint 상태를 쉽게 확인하기 어렵다.

## 2. description package를 build한다

이 단계는 `ros2 launch trashbot_description ...` 형태로 실행할 수 있게 패키지를 install space에 올리는 단계다.

```bash
cd ~/yh_ws/TIL/Robotics/VSLAM
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select trashbot_description
source install/setup.bash
```

왜 이 명령을 쓰는가:

- `FindPackageShare("trashbot_description")`가 launch 파일 안에서 패키지 경로를 찾을 수 있게 한다.
- `--symlink-install`을 쓰면 xacro나 rviz 파일을 수정한 뒤 rebuild 부담이 줄어든다.

## 3. xacro를 URDF로 렌더링해 문법을 확인한다

이 단계는 RViz를 띄우기 전에 모델 자체가 파싱되는지 확인하는 단계다.

```bash
xacro ~/yh_ws/TIL/Robotics/VSLAM/trashbot_description/urdf/trashbot.urdf.xacro > /tmp/trashbot.urdf
check_urdf /tmp/trashbot.urdf
```

기대 결과:

- `robot name is: trashbot`
- link 목록에 `base_link`, `camera_link`, `imu_link`, `gps_link`, wheel link가 보임

## 4. RViz2에서 robot model을 확인한다

이 단계는 `robot_state_publisher`와 RViz2를 같이 띄워 TF tree와 robot model을 확인하는 단계다.

```bash
ros2 launch trashbot_description display.launch.py
```

Jetson 로컬 화면에서 `DISPLAY`가 비어 있으면 아래처럼 실행한다.

```bash
DISPLAY="${DISPLAY:-:1}" XAUTHORITY="${XAUTHORITY:-/run/user/1000/gdm/Xauthority}" \
ros2 launch trashbot_description display.launch.py
```

## 5. 확인할 것

- `base_footprint -> base_link`가 보이는지
- `left_wheel_link`, `right_wheel_link`가 좌우에 배치되어 있는지
- `camera_link`가 전방 상단에 있는지
- `imu_link`가 카메라 근처 상단에 있는지
- `gps_link`가 상단 뒤쪽에 있는지
- `camera_color_optical_frame`, `camera_depth_optical_frame`이 TF에 나타나는지

## 6. 지금 단계에서 인정할 한계

- 실제 로봇 실측값이 아직 반영되지 않았다.
- `base_link -> camera_link`, `base_link -> imu_link`, `base_link -> gps_link`는 임시값이다.
- Gazebo 물리 시뮬레이션용 transmission/plugin은 아직 들어가지 않았다.

## 7. 다음 단계

- 실제 섀시 크기와 바퀴 간격을 측정해 xacro property를 수정한다.
- `D435i`와 `BNO08x`를 실제 장착 위치 기준으로 다시 측정한다.
- RViz 확인이 끝나면 Gazebo diff-drive 시뮬레이션용 plugin을 추가한다.
