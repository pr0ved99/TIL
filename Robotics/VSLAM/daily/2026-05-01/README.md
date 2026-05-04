# 2026-05-01 작업 일지

## 결론

- 오늘의 핵심 결과는 encoder-only local odom 다음 단계로 encoder+IMU EKF 후보를 추가한 것이다.
- Gazebo raw `/imu/data`를 바로 EKF에 넣지 않고, BNO08x-like covariance를 입힌 `/imu/data_bno08x_like`를 쓰도록 했다.
- `/wheel/odometry`는 위치와 전진속도, `/imu/data_bno08x_like`는 yaw-rate를 담당하는 local EKF profile을 추가했다.
- 공원형 Gazebo world에서 이 encoder+IMU `/odometry/local` 후보를 RTAB-Map으로 바로 비교할 수 있는 launch를 추가했다.
- 더 긴 주행과 현실적인 landmark 분포 확인을 위해 큰 공원형 Gazebo world를 추가했다.
- Mari Gazebo + RTAB-Map 결과를 Nav2에 연결하기 위한 `trashbot_navigation` 1차 smoke-test 구조를 추가했다.
- Nav2 초기 디버깅을 위해 Stage 0~3 단계별 훈련 world를 추가했다.
- Nav2 stage troubleshooting 캡처를 정리했고, 평지를 장애물로 오인해 map이 지저분하게 따지는 문제와 해결 상태를 기록했다.
- 저장된 RTAB-Map occupancy map을 Nav2 static map으로 다시 불러오는 `map_server + AMCL` saved-map profile을 추가했다.
- Stage 2 장애물 world에서 clean saved map을 다시 만들고, 저장 맵 기반 Nav2가 `/plan`과 `/cmd_vel`을 publish하는 것까지 확인했다.
- 현재 Nav2는 "경로 생성과 속도 명령 발행" 단계까지 통과했고, 다음 검증은 여러 goal에 대한 실제 도착/우회/recovery 기록이다.
- 아직 실제 BNO08x 하드웨어 입력은 아니며, Gazebo IMU를 실제 센서 구조에 가깝게 다루기 위한 중간 검증 단계다.

## 오늘 작업 한 줄 요약

- Gazebo fake encoder와 Gazebo IMU를 실제 encoder/BNO08x 구조처럼 연결해 `/odometry/local`을 만들고, 큰 공원형 world까지 준비했다.
- 이어서 `/odom` baseline 기준 Nav2 1차 자율주행 smoke-test 절차를 만들었다.
- 저장 맵 기반 Nav2에서 AMCL localization, global plan, `/cmd_vel` 발행까지 확인했다.

## 배경

- 이전 단계에서는 `/wheel/odometry`를 만들고 encoder-only EKF로 `/odometry/local`을 publish하는 구조를 확인했다.
- 하지만 실제 로봇에서는 회전 안정화를 위해 encoder만 쓰기보다 IMU yaw-rate도 함께 쓰는 편이 일반적이다.
- 문제는 Gazebo IMU covariance가 너무 작으면 EKF가 IMU를 과하게 믿을 수 있다는 점이다.
- 그래서 raw `/imu/data`를 직접 넣지 않고, BNO08x-like covariance를 입힌 topic을 별도로 만들었다.

## 오늘 만든/수정한 파일

- [imu_covariance_republisher.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_localization/scripts/imu_covariance_republisher.py)
- [imu_covariance_bno08x_like.yaml](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_localization/config/imu_covariance_bno08x_like.yaml)
- [ekf_local_encoder_imu_bno08x_like.yaml](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_localization/config/ekf_local_encoder_imu_bno08x_like.yaml)
- [ekf_local_encoder_imu_bno08x_yaw_tuned.yaml](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_localization/config/ekf_local_encoder_imu_bno08x_yaw_tuned.yaml)
- [mari_ekf_local.launch.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_localization/launch/mari_ekf_local.launch.py)
- [mari_rtabmap_realsense_light_local_odom.launch.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/launch/mari_rtabmap_realsense_light_local_odom.launch.py)
- [mari_rtabmap_realsense_light_encoder_imu.launch.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/launch/mari_rtabmap_realsense_light_encoder_imu.launch.py)
- [mari_large_park_test.world](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/worlds/mari_large_park_test.world)
- [gazebo_mari_large_park_realsense_light.launch.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_description/launch/gazebo_mari_large_park_realsense_light.launch.py)
- [trashbot_localization README](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_localization/README.md)
- [05-02_Mari_Gazebo_Run_Guide.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/learning/05-02_Mari_Gazebo_Run_Guide.md)
- [trashbot_navigation](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_navigation)
- [mari_nav2_rtabmap.launch.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_navigation/launch/mari_nav2_rtabmap.launch.py)
- [mari_nav2_rtabmap_params.yaml](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_navigation/config/mari_nav2_rtabmap_params.yaml)
- [mari_nav2_saved_map.launch.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_navigation/launch/mari_nav2_saved_map.launch.py)
- [mari_nav2_map_builder.launch.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_navigation/launch/mari_nav2_map_builder.launch.py)
- [mari_nav2_saved_map_params.yaml](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/trashbot_navigation/config/mari_nav2_saved_map_params.yaml)
- [filter_nav2_saved_map.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/Tools/filter_nav2_saved_map.py)
- [05-03_Mari_Nav2_Map_Filtering_Design.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/learning/05-03_Mari_Nav2_Map_Filtering_Design.md)
- [check_mari_nav2_topics.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/Tools/check_mari_nav2_topics.py)
- [05-04_Mari_Nav2_Run_Guide.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/learning/05-04_Mari_Nav2_Run_Guide.md)
- [2026-05-01_mari_nav2_stage_troubleshooting](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-05-01_mari_nav2_stage_troubleshooting)
- [2026-05-01_mari_nav2_saved_map_smoke](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-05-01_mari_nav2_saved_map_smoke)
- `mari_nav2_stage0_empty.world`, `mari_nav2_stage1_straight_path.world`, `mari_nav2_stage2_obstacles.world`, `mari_nav2_stage3_small_loop.world`
- `gazebo_mari_nav2_stage0_empty.launch.py`, `gazebo_mari_nav2_stage1_straight_path.launch.py`, `gazebo_mari_nav2_stage2_obstacles.launch.py`, `gazebo_mari_nav2_stage3_small_loop.launch.py`

## 구조

```text
Gazebo /odom
-> /motor/encoder_ticks
-> /wheel/odometry

Gazebo /imu/data
-> /imu/data_bno08x_like

/wheel/odometry + /imu/data_bno08x_like
-> /odometry/local
-> RTAB-Map
```

Nav2 1차 smoke-test 구조:

```text
Gazebo /odom
RTAB-Map map->odom TF and /rtabmap/map
RGB-D depth image -> depthimage_to_laserscan -> /scan
Nav2 -> /cmd_vel
Mari planar move
```

저장된 맵 기반 Nav2 구조:

```text
depth image -> depthimage_to_laserscan -> /scan
RTAB-Map grid from /scan -> /rtabmap/map
-> nav2_map_server map_saver_cli
-> saved YAML/PGM map
-> map_server + AMCL
-> Nav2 static global costmap + live /scan obstacle layer
-> /cmd_vel
```

## 실행 명령

빌드:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
colcon build --symlink-install --packages-select trashbot_localization trashbot_description && source ~/.bashrc
```

터미널 1, Gazebo:

```bash
ros2 launch trashbot_description gazebo_mari_park_realsense_light.launch.py
```

큰 공원 world로 실행:

```bash
ros2 launch trashbot_description gazebo_mari_large_park_realsense_light.launch.py
```

터미널 2, RTAB-Map + encoder/IMU local odom:

```bash
ros2 launch trashbot_description mari_rtabmap_realsense_light_encoder_imu.launch.py
```

터미널 3, Teleop:

```bash
python3 Tools/teleop_mari_keyboard.py \
  --rate 60 \
  --linear-speed 0.08 \
  --angular-speed 0.45 \
  --linear-accel 0.12 \
  --angular-accel 0.35 \
  --key-timeout 1.2
```

터미널 4, RTAB-Map topic report:

```bash
python3 Tools/check_mari_rtabmap_topics.py \
  --duration 20 \
  --label large_park_encoder_imu_local_odom_yaw_tuned \
  --odom-topic /odometry/local \
  --output-json assets/2026-05-01_mari_large_park_rtabmap/03_large_park_encoder_imu_local_odom_yaw_tuned_check.json \
  --output-md assets/2026-05-01_mari_large_park_rtabmap/03_large_park_encoder_imu_local_odom_yaw_tuned_check.md
```

Nav2 1차 smoke-test:

```bash
ros2 launch trashbot_description gazebo_mari_nav2_stage0_empty.launch.py
ros2 launch trashbot_description mari_rtabmap_realsense_light.launch.py
ros2 launch trashbot_navigation mari_nav2_rtabmap.launch.py
```

RViz에서 `2D Goal Pose`를 누르고 Mari 앞쪽의 가까운 지점을 찍는다.

Stage를 올릴 때는 Gazebo launch만 `stage1_straight_path`, `stage2_obstacles`, `stage3_small_loop`, `large_park` 순서로 바꾼다.

Nav2 topic 확인:

```bash
python3 Tools/check_mari_nav2_topics.py --duration 8
python3 Tools/check_mari_nav2_topics.py --duration 8 --expect-cmd-vel
```

저장된 맵 기반 Nav2 smoke-test:

```bash
ros2 launch trashbot_navigation mari_nav2_map_builder.launch.py

mkdir -p assets/2026-05-01_mari_nav2_saved_map_smoke
ros2 run nav2_map_server map_saver_cli \
  -t /rtabmap/map \
  -f assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap \
  --fmt pgm \
  --mode trinary \
  --occ 0.65 \
  --free 0.25

ros2 launch trashbot_navigation mari_nav2_saved_map.launch.py \
  map:=/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap.yaml
```

저장 맵 후처리:

```bash
python3 Tools/filter_nav2_saved_map.py \
  assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap.yaml \
  --output-prefix assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap_filtered \
  --min-occupied-neighbors 1 \
  --min-obstacle-pixels 12
```

저장 맵이 지저분하면 map builder를 더 보수적으로 다시 실행한다.

```bash
ros2 launch trashbot_navigation mari_nav2_map_builder.launch.py \
  scan_height:=2 \
  range_min:=0.45 \
  range_max:=2.50 \
  grid_range_min:=0.45 \
  grid_range_max:=2.50 \
  linear_update:=0.15 \
  angular_update:=0.15
```

Nav2 훈련 world 검증:

```text
Stage 0~3 world XML parse: success
gz sdf -k mari_nav2_stage*.world: Check complete
python3 -m py_compile gazebo_mari_nav2_stage*.launch.py: success
colcon build --symlink-install --packages-select trashbot_description trashbot_localization trashbot_navigation: success
ros2 launch trashbot_description gazebo_mari_nav2_stage*.launch.py --show-args: success
Stage 0 gui:=false smoke: world loaded, SpawnEntity successfully spawned mari, /cmd_vel subscribed, /odom advertised
```

Nav2 stage troubleshooting captures:

```text
assets/2026-05-01_mari_nav2_stage_troubleshooting/
01_nav2_costmap_false_wall_before_scan_filter.png
02_nav2_costmap_dense_rtabmap_static_map_issue.png
03_nav2_goal_outside_small_global_costmap.png
04_nav2_scan_only_costmap_obstacle_detection_ok.png
```

대표 캡처:

![평지를 장애물로 오인해 map/costmap이 지저분하게 생성된 상태](../../assets/2026-05-01_mari_nav2_stage_troubleshooting/03_nav2_goal_outside_small_global_costmap.png)

![평지 오인식이 줄고 실제 물체 근처에만 장애물 trace가 남는 해결 후 상태](../../assets/2026-05-01_mari_nav2_stage_troubleshooting/04_nav2_scan_only_costmap_obstacle_detection_ok.png)

저장 맵 기반 Nav2 smoke 결과:

```text
map source:
assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap_filtered.yaml

RViz state:
Navigation active
Localization active
Feedback active

topic check:
/scan: OK, 15.0 Hz, frame=camera_link
/global_costmap/costmap: OK, 0.7 Hz, frame=map, resolution=0.050
/local_costmap/costmap: OK, 2.7 Hz, frame=odom, resolution=0.050
/plan: OK, 1.0 Hz, frame=map, poses=37
/cmd_vel: OK, 137.8 Hz, linear_x=0.111, angular_z=0.396

plan echo:
frame_id=map
path pose가 x=4.025, y=0.230 부근에서 x=4.170, y=0.765 부근까지 연속적으로 생성됨
final orientation quaternion z=0.533, w=0.846
```

해석:

- 저장 맵 기반 `map_server + AMCL + Nav2` pipeline은 연결됐다.
- `/plan`이 `map` frame 기준으로 생성되고 `/cmd_vel`도 발행됐으므로, Nav2가 목표를 받아 실제 제어 명령까지 내고 있다.
- `check_mari_nav2_topics.py`에서 `/map` count가 0으로 나온 것은 sample window 동안 새 `/map` 메시지가 잡히지 않은 현상이다. RViz map 표시, AMCL active 상태, global costmap과 plan 생성을 기준으로 저장 맵 자체는 사용 중인 것으로 본다.
- 아직 남은 판정은 여러 목표점에서 실제 goal reach, 장애물 우회, recovery 횟수, path 품질을 반복 기록하는 것이다.

## 검증 결과

```text
python3 -m py_compile imu_covariance_republisher.py mari_ekf_local.launch.py mari_rtabmap_realsense_light_local_odom.launch.py mari_rtabmap_realsense_light_encoder_imu.launch.py: success
imu_covariance_bno08x_like.yaml / ekf_local_encoder_imu_bno08x_like.yaml parse: success
colcon build --symlink-install --packages-select trashbot_localization trashbot_description: success
ros2 launch trashbot_description mari_rtabmap_realsense_light_encoder_imu.launch.py --show-args: success
OK XML: trashbot_description/worlds/mari_large_park_test.world
gz sdf -k trashbot_description/worlds/mari_large_park_test.world: Check complete
python3 -m py_compile gazebo_mari_large_park_realsense_light.launch.py: success
colcon build --symlink-install --packages-select trashbot_description: success
ros2 launch trashbot_description gazebo_mari_large_park_realsense_light.launch.py --show-args: success
gui:=false launch smoke: large park world loaded and SpawnEntity successfully spawned mari
```

큰 공원 world 비교 결과:

```text
/odom baseline:
odom rate=49.96 Hz, mapData poses=13 links=114, cloud=5631 points, Loop/MapToBase_lin_std=0.068 m

encoder+IMU /odometry/local:
odom rate=29.97 Hz, mapData poses=13 links=103, cloud=5659 points, Loop/MapToBase_lin_std=1.737 m
```

후속 조정:

```text
ekf_local_encoder_imu_bno08x_yaw_tuned.yaml 추가
mari_rtabmap_realsense_light_encoder_imu.launch.py 기본 EKF config를 yaw-tuned profile로 변경
headless smoke /odometry/local pose_cov_yaw=0.00194

yaw-tuned encoder+IMU /odometry/local:
odom rate=29.95 Hz, RGB/Depth=14.98 Hz, mapData poses=19 links=76, cloud=7314 points
pose_cov_yaw=0.00175, Loop/MapToBase_lin_std=1.253 m
screen capture: assets/2026-05-01_mari_large_park_rtabmap/03_large_park_encoder_imu_local_odom_yaw_tuned_rtabmap.png
```

IMU covariance republisher smoke:

```text
/test/imu/raw -> /test/imu/bno08x_like
frame_id: imu_link
orientation_covariance diag: 0.01
angular_velocity_covariance diag: 0.001
linear_acceleration_covariance diag: 0.01
```

## 오늘 관찰한 핵심 현상

- `/imu/data_bno08x_like`는 IMU 값 자체를 바꾸는 것이 아니라 covariance와 frame을 실험용으로 정리한다.
- EKF는 `/wheel/odometry`에서 위치/전진속도를 받고, `/imu/data_bno08x_like`에서 yaw-rate만 받는다.
- 이 구조는 실제 BNO08x가 연결됐을 때 topic 이름과 covariance만 교체하면 같은 EKF 구조를 재사용하기 위한 준비다.
- `mari_large_park_test.world`는 기존 공원 world보다 넓고 landmark가 더 분산되어 있어, 짧은 화면 증빙보다 긴 주행/재방문/누적 map 품질 확인에 더 적합하다.
- yaw-rate-only EKF는 화면상 map을 깨지는 않았지만 yaw covariance가 커져 RTAB-Map 내부 불확실도가 높게 나왔다.
- yaw-tuned EKF는 wheel yaw와 BNO08x-like IMU yaw orientation을 함께 넣어 `/odometry/local`의 yaw pose를 직접 관측하게 만든다.
- yaw-tuned EKF 재검증에서는 yaw covariance가 크게 낮아지고 map point 누적도 증가했지만, `Loop/MapToBase_lin_std`는 아직 `/odom` baseline보다 크다.
- Stage 2 saved-map Nav2에서는 저장 맵, AMCL, global planner, controller, `/cmd_vel`까지 이어지는 기본 자율주행 pipeline이 확인됐다.
- 지금부터는 "실행은 되는가"보다 "여러 goal에서 안정적으로 도착하는가"를 검증해야 한다.

## 남은 문제

- yaw-tuned encoder+IMU `/odometry/local`은 개선됐지만 `/odom` baseline 수준까지는 아직 내려오지 않았다.
- 현재 fake encoder source는 여전히 Gazebo `/odom`이므로 실제 motor encoder 성능을 증명한 것은 아니다.
- BNO08x 실제 하드웨어 covariance와 yaw-rate scale은 장착 후 재측정해야 한다.
- 저장 맵 기반 Nav2는 plan/cmd_vel 생성까지 확인됐지만, 여러 goal에 대한 도착률과 장애물 우회 안정성은 아직 정량 기록이 부족하다.
- `/cmd_vel` 발행 주기가 높게 나오는 상태이므로, 실제 주행 화면에서 움직임이 과하게 떨리거나 recovery가 반복되는지도 별도 관찰해야 한다.

## 다음 액션

1. Stage 2 saved map에서 가까운 goal, 장애물 우회 goal, 먼 goal을 각각 3회 이상 찍어 goal reach 여부와 recovery 횟수를 기록한다.
2. `/cmd_vel`, `/plan`, global/local costmap, RViz 화면을 함께 캡처해 Nav2 주행 증빙을 남긴다.
3. saved-map 주행이 안정화되면 Stage 3 small loop world에서도 같은 map 생성/저장/주행 절차를 반복한다.
4. 그 다음 yaw-tuned `/odometry/local` 기반 Nav2 profile로 바꿔 Gazebo `/odom` baseline과 차이를 비교한다.
5. 실제 encoder/BNO08x 연결 전까지는 fake encoder 기반 결과라는 전제를 문서에 계속 표시한다.

## 한 줄 회고

- 실제 센서가 없어도 encoder와 IMU가 들어왔을 때의 ROS2/EKF/RTAB-Map 연결 방식을 먼저 고정했다.
