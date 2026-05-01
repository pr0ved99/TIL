# 2026-04-29 Mari Sensor Visualization Evidence

## 결론

- 이 폴더는 Gazebo Mari의 가상 센서 topic을 RViz2에서 통합 시각화한 증빙을 보관한다.
- 이번 캡처는 `RobotModel`, `TF`, `/odom`, `/wheel/odometry`, RGB image, depth image, depth point cloud가 같은 RViz2 화면에서 표시되는 것을 확인한 기록이다.

## 파일 목록

| 파일 | 설명 |
| --- | --- |
| `01_rviz_mari_rgbd_pointcloud_odom_visualization_ok.png` | RViz2에서 Mari robot model, odometry, RGB image, depth image, point cloud 통합 표시가 정상인 장면 |

## 실행 흐름

```text
Gazebo Mari
-> /robot_description, /tf, /odom
-> RGB-D camera topics
-> Gazebo encoder bridge
-> /motor/encoder_ticks
-> /wheel/odometry
-> RViz2 mari_sensor_debug.rviz
```

## 확인 명령

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

ros2 launch trashbot_description gazebo_mari.launch.py \
  use_mesh_visual:=true \
  world:=$(pwd)/trashbot_description/worlds/mari_camera_test.world
```

다른 터미널:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_localization mari_gazebo_encoder_odom.launch.py
```

다른 터미널:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
rviz2 -d trashbot_description/rviz/mari_sensor_debug.rviz
```

## 판정

- RViz2 `Global Status`가 `OK`인 상태에서 Mari robot model과 주요 TF가 표시된다.
- RGB image와 depth 기반 point cloud가 같은 장면의 테스트 물체들을 표시한다.
- `/odom`과 `/wheel/odometry`가 RViz2 display에 추가되어, Gazebo odom과 fake encoder odometry를 함께 볼 수 있다.
- 왼쪽 depth image 패널이 검게 보일 수 있지만, `32FC1` depth image의 표시 스케일 문제일 수 있다. 같은 시점의 point cloud가 정상 표시되므로 depth 데이터 수신 자체는 정상으로 본다.
