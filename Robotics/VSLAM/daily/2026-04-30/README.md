# 2026-04-30 작업 일지

## 결론

- 오늘의 핵심 결과는 Mari Gazebo 환경을 단순 카메라 테스트 world에서 공원형 RTAB-Map 검증 world로 확장한 것이다.
- `mari_park_test.world`를 추가해 잔디, 보행로, 나무, 벤치, 표지판, 낮은 벽, 돌이 있는 환경에서 RGB-D mapping을 확인할 수 있게 했다.
- `gazebo_mari_park_realsense_light.launch.py`를 추가해 기존 RealSense-light 저부하 카메라 조건으로 공원 world를 바로 실행할 수 있게 했다.
- 공원 world에서 RTAB-Map 3D map이 기존 단순 world보다 풍부하게 생성되는 것을 화면으로 확인했다.
- 현재 성공한 map은 Gazebo 위치 기반 `/odom`을 RTAB-Map 입력으로 사용한 baseline이다.
- 실제 encoder + IMU 기반 odometry 검증은 아직 아니며, 다음 비교 대상은 같은 공원 world에서 `/odometry/local` 입력을 쓰는 run이다.
- 추가로 encoder adapter에 좌우 거리 scale, tick jump reject, 속도 제한, encoder gap 감지를 추가해 실제 encoder bring-up 전 1차 방어 구조를 만들었다.

## 오늘 작업 한 줄 요약

- RTAB-Map이 보기 좋은 구조물을 더 많이 포함하도록 Gazebo 공원형 world를 추가하고, `/odom` 기반 mapping baseline 증빙 경로를 만들었다.

## 배경

- 기존 `mari_camera_test.world`는 RGB-D topic 수신과 RTAB-Map 입력 확인에는 충분했다.
- 하지만 환경이 색상 패널, 박스, 기둥 중심이라 실제 공원 주행과는 차이가 컸다.
- RTAB-Map은 카메라가 보는 구조물의 모양, 색, 깊이 변화가 많을수록 map 확인이 쉬우므로, 공원형 landmark가 필요했다.

## 오늘 만든/수정한 파일

- [mari_park_test.world](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/worlds/mari_park_test.world)
- [gazebo_mari_park_realsense_light.launch.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/launch/gazebo_mari_park_realsense_light.launch.py)
- [05-02_Mari_Gazebo_Run_Guide.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/learning/05-02_Mari_Gazebo_Run_Guide.md)
- [trashbot_description README](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/README.md)
- [park world RTAB-Map baseline README](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-30_mari_park_world_rtabmap_baseline/README.md)
- [encoder_ticks_to_wheel_odom.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_localization/scripts/encoder_ticks_to_wheel_odom.py)
- [mock_motor_encoder_ticks.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_localization/scripts/mock_motor_encoder_ticks.py)
- [encoder_odom.yaml](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_localization/config/encoder_odom.yaml)
- [encoder_odom_gazebo.yaml](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_localization/config/encoder_odom_gazebo.yaml)
- [mari_encoder_odom_mock.launch.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_localization/launch/mari_encoder_odom_mock.launch.py)
- [trashbot_localization README](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_localization/README.md)

## 실행 명령

빌드:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
colcon build --symlink-install --packages-select trashbot_description && source ~/.bashrc
```

Gazebo:

```bash
ros2 launch trashbot_description gazebo_mari_park_realsense_light.launch.py
```

RTAB-Map:

```bash
ros2 launch trashbot_description mari_rtabmap_realsense_light.launch.py \
  detection_rate:=3 \
  queue_size:=20 \
  approx_sync_max_interval:=0.08 \
  rtabmap_viz:=true
```

Teleop:

```bash
python3 Tools/teleop_mari_keyboard.py \
  --rate 60 \
  --linear-speed 0.08 \
  --angular-speed 0.45 \
  --linear-accel 0.12 \
  --angular-accel 0.35 \
  --key-timeout 1.2
```

## 검증 결과

```text
OK XML: trashbot_description/worlds/mari_park_test.world
gz sdf -k trashbot_description/worlds/mari_park_test.world: Check complete
colcon build --symlink-install --packages-select trashbot_description: success
ros2 launch trashbot_description gazebo_mari_park_realsense_light.launch.py --show-args: success
```

Encoder adapter 검증:

```text
python3 -m py_compile encoder_ticks_to_wheel_odom.py mock_motor_encoder_ticks.py: success
encoder_odom.yaml / encoder_odom_gazebo.yaml parse: success
colcon build --symlink-install --packages-select trashbot_localization: success
ros2 launch trashbot_localization mari_encoder_odom_mock.launch.py --show-args: success
```

직진 mock:

```text
[OK] /motor/encoder_ticks count=121 rate=30.0 Hz data=[13872, 13872]
[OK] /wheel/odometry count=120 rate=30.0 Hz x=1.153 y=0.000 yaw=0.000 vx=0.102 wz=0.000
```

제자리 회전 mock:

```text
[OK] /motor/encoder_ticks count=121 rate=30.0 Hz data=[-5014, 5014]
[OK] /wheel/odometry count=120 rate=30.0 Hz x=0.000 y=0.000 yaw=-0.199 vx=0.000 wz=0.516
```

큰 tick jump 방어:

```text
tick_jump_after_sec:=2.0 tick_jump_left:=20000 tick_jump_right:=20000
Rejected encoder sample #1: encoder tick jump exceeded limit ...
/wheel/odometry x=1.307 y=0.000 yaw=0.000 vx=0.101 wz=0.000
```

## 오늘 관찰한 핵심 현상

- Gazebo 좌측 model tree에 `park_ground`, `walking_paths`, `front_park_landmarks`, `left_bench`, `tree_cluster_left`, `tree_cluster_right`, `flower_beds_and_rocks`, `park_boundary_cues`, `mari`가 표시됐다.
- RTAB-Map GUI에서 Gazebo camera view, rejected loop hypothesis panel, odometry view, 3D map이 함께 표시됐다.
- 3D map에는 보행로, 나무, 벤치, 표지판, 낮은 벽이 point cloud와 RGB color로 누적됐다.
- 현재 결과는 `/odom` 기반 baseline이므로 map이 잘 나온 이유에는 Gazebo 위치 기반 odometry가 안정적이라는 점도 포함된다.
- encoder adapter는 큰 tick jump를 `/wheel/odometry` pose jump로 바로 반영하지 않고 reject할 수 있게 됐다.

## 증빙 자료

- [assets/2026-04-30_mari_park_world_rtabmap_baseline](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-30_mari_park_world_rtabmap_baseline)
- 추천 파일명: `01_mari_park_world_rtabmap_odom_baseline.png`

## 남은 문제

- 같은 공원 world에서 `/odometry/local` 입력으로 RTAB-Map을 돌렸을 때 map 정렬과 회전량이 `/odom` baseline만큼 안정적인지 아직 비교하지 않았다.
- 현재 `/odometry/local`은 구조상 encoder pipeline을 거치지만, Gazebo에서는 fake encoder source가 여전히 Gazebo `/odom`이다.
- 실제 encoder + BNO08x IMU 기반 odometry는 하드웨어 연결 후 별도 검증해야 한다.
- encoder adapter의 1차 방어는 들어갔지만, 좌우 scale과 covariance 값은 아직 실제 주행 실측으로 보정되지 않았다.

## 다음 액션

1. 공원 world에서 `/odometry/local` 입력 RTAB-Map run을 실행한다.
2. `/odom` baseline과 `/odometry/local` run을 같은 world, 비슷한 teleop 경로로 비교한다.
3. `Tools/check_mari_rtabmap_topics.py --odom-topic /odometry/local` 결과를 JSON/Markdown으로 저장한다.
4. 회전량이 맞지 않으면 fake encoder `track_width_m`, pose-delta tick 생성, EKF covariance를 순서대로 확인한다.
5. 실제 encoder 연결 전에는 `max_tick_delta`, `max_linear_velocity_mps`, `max_angular_velocity_radps` 기본값이 Mari 주행 속도 범위를 과하게 제한하지 않는지 추가 확인한다.

## 한 줄 회고

- 단순 topic 확인용 world에서 벗어나, 실제 공원형 VSLAM 데모에 가까운 Gazebo mapping baseline을 확보했다.
