# 2026-04-27 작업 일지

## 결론

- 오늘 가장 중요한 결과는 Gazebo에서 막힌 Mari 모델을 RViz2 기준으로 먼저 검증해, URDF/Xacro의 링크 구조와 센서 TF가 정상적으로 보이는 상태까지 확인한 것이다.
- `mari_visual_mesh.stl`의 회전과 z offset을 보정해, 거북이 외형과 `base_link`, `camera_link`, `imu_link`, `gps_link`가 서로 맞는 상태로 정리했다.
- `map -> odom -> base_footprint -> base_link` 구조의 동적 TF 테스트 스크립트를 추가해, RViz2에서 Mari가 원형 경로로 움직이는지 확인할 수 있게 했다.
- Gazebo visual mesh 표시 문제는 아직 남아 있지만, RViz2 기준 모델/TF 검증은 진행 완료로 볼 수 있다.

## 오늘 작업 한 줄 요약

- Mari URDF/Xacro를 RViz2에서 검증하고, TF tree와 동적 이동 테스트까지 확인했다.

## 시간순 기록

### 11:00

- `mari.urdf.xacro`를 렌더링하고 `check_urdf`로 링크 구조를 확인했다.
- `display.launch.py`에서 `robot_description` 파라미터가 YAML로 잘못 파싱되는 문제를 수정했다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

xacro trashbot_description/urdf/mari.urdf.xacro > /tmp/mari.urdf
check_urdf /tmp/mari.urdf
```

### 12:00

- `joint_state_publisher_gui`가 없을 때 launch가 실패하는 문제를 확인했다.
- 기본 실행은 GUI joint slider 없이 `joint_state_publisher`로 뜨도록 정리했다.

```bash
sudo apt update
sudo apt install ros-humble-joint-state-publisher-gui
```

### 14:00

- RViz2에서 Mari visual mesh가 90도 틀어져 보이는 문제를 확인했다.
- ROS 링크 좌표계는 유지하고, visual mesh만 yaw 방향으로 90도 회전하도록 보정했다.
- STL bounds 기준으로 mesh의 최저점이 지면에 맞도록 z offset을 조정했다.

```xml
<xacro:property name="chassis_mesh_yaw" value="${pi / 2.0}"/>
<xacro:property name="chassis_mesh_min_z" value="-0.021884"/>
<xacro:property name="chassis_mesh_z" value="${-base_link_z - chassis_mesh_min_z}"/>
```

### 15:00

- RViz2에서 `base_footprint`, `base_link`, `camera_link`, `imu_link`, `gps_link`가 표시되는지 확인했다.
- `tf2_tools view_frames`로 TF tree PDF를 생성하고 `mari_view` 증빙 폴더에 보관했다.

```bash
ros2 run tf2_tools view_frames
```

### 16:00

- RViz2에서 Mari가 움직이는지 확인하기 위해 `Tools/test_mari_moving_tf.py`를 추가했다.
- 처음에는 `map -> base_footprint`를 직접 움직였으나, 실제 자율주행 구조에 가깝게 `map -> odom -> base_footprint` 구조로 수정했다.
- `/odom` 토픽도 같이 publish하도록 보강했다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

python3 Tools/test_mari_moving_tf.py
```

### 17:00

- 리얼센스 장착 높이가 `(80 - 65.44216) mm = 14.55784 mm` 높아진 것을 반영했다.
- `mari.urdf.xacro`의 `camera_z`를 기존 `0.107616 m`에서 `0.122174 m`로 갱신했다.
- `05-01_Mari_URDF_Xacro_Preparation_Checklist.md`에도 현재 적용 기준값을 동일하게 맞췄다.

### 17:30

- 원형 TF 테스트 다음 단계로 `/cmd_vel` 기반 odom 테스트 스크립트를 추가했다.
- `Tools/test_mari_cmd_vel_odom.py`는 `/cmd_vel`을 subscribe하고, 2D pose를 적분해 `/odom`과 `odom -> base_footprint` TF를 publish한다.
- 이 단계는 아직 실제 바퀴/엔코더 기반 odom은 아니지만, Nav2와 자율주행에서 쓰는 명령-주행-odom 흐름에 더 가까운 검증이다.

```bash
python3 Tools/test_mari_cmd_vel_odom.py
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.15}, angular: {z: 0.0}}"
```

## 오늘 관찰한 핵심 현상

- RViz2에서는 Mari visual mesh와 센서 TF가 정상적으로 표시된다.
- Gazebo Classic에서는 여전히 visual mesh 표시가 불안정하므로, Gazebo 문제는 별도 blocker로 유지한다.
- RViz2에서 움직임을 보려면 `Fixed Frame`과 `Target Frame`을 `map`으로 맞춰야 한다.
- 현재 동적 테스트는 실제 바퀴 물리가 아니라 TF를 직접 발행하는 시각 검증용이다.
- `/cmd_vel` 기반 테스트는 실제 물리/엔코더는 아니지만, 명령 속도를 받아 `/odom`과 TF를 만드는 구조를 확인하는 용도다.

## 원인 가설

- RViz2에서 90도 틀어져 보였던 원인은 Onshape/STL export 축과 ROS 기준 축이 달랐기 때문으로 판단했다.
- `base_link`가 아래로 주저앉아 보인 원인은 mesh 최저점과 `base_footprint` 기준 높이 보정이 맞지 않았기 때문이다.
- Gazebo에서 보이지 않는 문제는 아직 RViz2 문제와 별개이며, Gazebo mesh loader 또는 visual resource path 문제일 가능성이 남아 있다.

## 확인 방법

- `xacro` 렌더링으로 XML 생성 여부를 확인했다.
- `check_urdf`로 URDF 링크 트리가 깨지지 않는지 확인했다.
- RViz2 `RobotModel`, `TF`, `Ground Grid`를 켜서 visual mesh와 TF 위치를 확인했다.
- `view_frames`로 TF tree를 PDF로 저장했다.
- `test_mari_moving_tf.py`로 `map -> odom -> base_footprint` 이동 구조를 시각 확인했다.

## 해결 방법

- `display.launch.py`에서 `robot_description`을 `ParameterValue(..., value_type=str)`로 넘겨 YAML 파싱 오류를 해결했다.
- `mari.urdf.xacro`에서 visual mesh의 yaw 회전과 z offset을 보정했다.
- `camera_link` box 크기를 D435i 실제 방향에 맞게 `x=0.025`, `y=0.09`, `z=0.025`로 정리했다.
- `Tools/test_mari_moving_tf.py`를 추가해 RViz2 이동 검증 절차를 만들었다.

## 오늘 배운 것

- `TF`는 ROS에서 좌표계 사이의 위치와 회전 관계를 알려주는 시스템이다.
- `map -> odom -> base_footprint` 구조는 실제 자율주행에서 흔히 쓰는 기본 구조다.
- `map`은 전역 기준, `odom`은 짧은 시간 동안 부드럽게 이어지는 로컬 이동 기준, `base_footprint`는 로봇 바닥 중심 기준이다.
- RViz2에서 모델이 잘 보이는 것과 Gazebo에서 물리 시뮬레이션이 잘 되는 것은 별개의 단계다.

## 오늘 만든/수정한 파일

- [mari.urdf.xacro](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/urdf/mari.urdf.xacro)
- [display.launch.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/launch/display.launch.py)
- [test_mari_moving_tf.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/Tools/test_mari_moving_tf.py)
- [test_mari_cmd_vel_odom.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/Tools/test_mari_cmd_vel_odom.py)
- [trashbot_description README](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/README.md)
- [Current Progress and Open Issues](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/progress/Current_Progress_and_Open_Issues.md)

## 증빙 자료

- [01_mari_urdf_rviz_mesh_tf_alignment_check.png](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/robot_model_exports/mari_view/01_mari_urdf_rviz_mesh_tf_alignment_check.png)
- [02_mari_tf_tree_view_frames.pdf](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/robot_model_exports/mari_view/02_mari_tf_tree_view_frames.pdf)
- [03_mari_rviz_dynamic_tf_motion_check.webm](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/robot_model_exports/mari_view/03_mari_rviz_dynamic_tf_motion_check.webm)

## 남은 문제

- Gazebo Classic에서 Mari visual mesh가 아직 안정적으로 표시되지 않는다.
- 현재 RViz2 이동 검증은 실제 바퀴, encoder 기반 odom이 아니라 TF/명령 기반 테스트다.
- 다음 단계에서 virtual wheel 기반 diff-drive 모델과 `/cmd_vel -> /odom -> TF` 흐름을 추가해야 한다.

## 다음 액션

1. `Tools/test_mari_cmd_vel_odom.py`로 `/cmd_vel -> /odom -> odom -> base_footprint` 흐름을 RViz2에서 확인한다.
2. `left_virtual_drive_wheel_link`, `right_virtual_drive_wheel_link`를 xacro에 추가한다.
3. RViz2에서 virtual wheel TF가 base 기준으로 원하는 위치에 있는지 확인한다.
4. 이후 Gazebo 또는 대체 시뮬레이터에서 같은 `/cmd_vel`, `/odom`, `odom -> base_footprint` 흐름을 연결한다.

## 한 줄 회고

- Gazebo가 막혀도 RViz2에서 URDF, TF, 센서 frame을 먼저 검증해 다음 주행 모델 작업의 기준선을 확보했다.
