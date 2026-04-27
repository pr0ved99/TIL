# 2026-04-22 Jetson 작업 일지

## 결론

- 스프린트 3의 `로봇 모델링` 흐름에 맞춰 `trashbot_description` 초안 모델을 추가했다.
- 새 모델은 `base_footprint`, `base_link`, 좌우 바퀴, caster, `D435i`, `BNO08x`, GPS frame을 포함한다.
- `robot_state_publisher`와 RViz2로 확인할 수 있는 `display.launch.py`와 RViz 설정을 추가했다.
- 현재 Jetson에는 `xacro`, `joint_state_publisher` 패키지가 아직 설치되어 있지 않아, xacro 렌더링 검증은 설치 후 진행해야 한다.

## 오늘 작업 한 줄 요약

- `S14P31C205-85` 로봇 링크/조인트 구조 초안 작성 진행
- `S14P31C205-86` `base_link`, 휠, `D435i`, GPS, IMU xacro 작성 진행
- `S14P31C205-87` RViz2 display launch 및 `robot_state_publisher` 설정 초안 작성 진행

## 현재 작업 형태

- 기존 `trashbot_description` 패키지를 확장했다.
- 기존 `duri`, `mari` xacro는 보존했다.
- 실제 치수는 아직 확정되지 않았으므로 새 `trashbot.urdf.xacro`는 placeholder dimension 기준이다.

## 시간순 기록

### 로봇 모델 초안 추가

- `trashbot_description/urdf/trashbot.urdf.xacro` 추가
- 포함 frame:
  - `base_footprint`
  - `base_link`
  - `left_wheel_link`
  - `right_wheel_link`
  - `front_caster_link`
  - `camera_link`
  - `camera_color_optical_frame`
  - `camera_depth_optical_frame`
  - `imu_link`
  - `gps_link`

### RViz 확인 구조 추가

- `trashbot_description/launch/display.launch.py` 추가
- `trashbot_description/rviz/trashbot_model.rviz` 추가
- `package.xml`에 `joint_state_publisher`, `joint_state_publisher_gui`, `rviz2`, `xacro` 실행 의존성 반영
- `CMakeLists.txt`에 `launch`, `rviz`, `urdf`, `meshes` install 반영

## 실행 명령

필요 패키지 설치:

```bash
sudo apt update
sudo apt install -y \
  ros-humble-xacro \
  ros-humble-joint-state-publisher \
  ros-humble-joint-state-publisher-gui
```

빌드:

```bash
cd ~/yh_ws/TIL/Robotics/VSLAM
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select trashbot_description
source install/setup.bash
```

URDF 확인:

```bash
xacro ~/yh_ws/TIL/Robotics/VSLAM/trashbot_description/urdf/trashbot.urdf.xacro > /tmp/trashbot.urdf
check_urdf /tmp/trashbot.urdf
```

RViz 확인:

```bash
DISPLAY="${DISPLAY:-:1}" XAUTHORITY="${XAUTHORITY:-/run/user/1000/gdm/Xauthority}" \
ros2 launch trashbot_description display.launch.py
```

## 검증 결과

- `colcon build --symlink-install --packages-select trashbot_description` 성공
- `trashbot.urdf.xacro` XML well-formed 확인
- `display.launch.py` Python syntax 확인
- `xacro` 명령은 현재 미설치 상태라 렌더링 검증은 패키지 설치 후 진행 필요

## 오늘 만든/수정한 파일

- [trashbot.urdf.xacro](/home/jetson/yh_ws/TIL/Robotics/VSLAM/trashbot_description/urdf/trashbot.urdf.xacro)
- [display.launch.py](/home/jetson/yh_ws/TIL/Robotics/VSLAM/trashbot_description/launch/display.launch.py)
- [trashbot_model.rviz](/home/jetson/yh_ws/TIL/Robotics/VSLAM/trashbot_description/rviz/trashbot_model.rviz)
- [trashbot_description README](/home/jetson/yh_ws/TIL/Robotics/VSLAM/trashbot_description/README.md)
- [28_Jetson_Trashbot_URDF_RViz_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/28_Jetson_Trashbot_URDF_RViz_Guide.md)

## 남은 문제

- 실제 로봇 치수와 바퀴 간격을 측정해 xacro property를 수정해야 한다.
- `base_link -> camera_link`, `base_link -> imu_link`, `base_link -> gps_link` 위치/각도를 실측해야 한다.
- Gazebo diff-drive plugin과 transmission은 아직 추가하지 않았다.

## 다음 액션

1. `xacro`, `joint_state_publisher` 패키지 설치
2. `check_urdf`로 렌더링 검증
3. RViz2에서 TF tree와 model 표시 확인
4. 실제 치수 반영
5. Gazebo diff-drive 시뮬레이션으로 이동

## 한 줄 회고

- 오늘은 RTAB-Map baseline 이후 자율주행으로 넘어가기 위한 첫 로봇 모델링 뼈대를 만들었다.
