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

Gazebo launch는 `trashbot_description/config/gazebo_ros.yaml`을 gzserver에 전달한다.
이 파일은 `/clock` publish rate를 `100 Hz`로 올린다.
`robot_localization` EKF가 `use_sim_time=true`로 동작하면 `/clock` 주기에 영향을 받으므로, 후보 B(`/odometry/local`) 실험 전에는 Gazebo를 재시작해야 한다.

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

### 실시간 우선 모드

RTAB-Map이 끊겨 보이면 먼저 렌더링 부하를 줄인다.
매핑 품질을 보는 동안 Mari STL 외형과 Gazebo camera visualization은 필수 입력이 아니다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

ros2 launch trashbot_description gazebo_mari.launch.py \
  use_mesh_visual:=false \
  sim_camera_width:=424 \
  sim_camera_height:=240 \
  sim_camera_update_rate:=10 \
  sim_camera_visualize:=false \
  world:=$(pwd)/trashbot_description/worlds/mari_camera_test.world
```

RTAB-Map도 GUI 없이 먼저 돌려서 backend가 밀리는지 확인한다.

```bash
ros2 launch trashbot_description mari_rtabmap.launch.py \
  rtabmap_viz:=false \
  rviz:=false \
  detection_rate:=3 \
  topic_queue_size:=10 \
  sync_queue_size:=10
```

위 조합이 부드럽게 동작하면 그 다음 `rtabmap_viz:=true`를 켠다.
실시간 확인용으로는 후보 A(`/odom`)를 먼저 쓰고, 후보 B(`/odometry/local`)는 별도 비교 run에서 검증한다.

### RealSense Light 동일 조건

실제 D435i + Jetson Docker baseline에서 쓰던 `light` preset은 아래 조합이다.

```text
camera: 424x240x15
RTAB-Map DetectionRate: 2
queue: 15
rtabmap_viz: true
```

Gazebo에서도 같은 조건으로 맞춘 전용 launch를 추가했다.
실제 데모에서는 지도 생성 화면이 필요하므로 이 wrapper는 `rtabmap_viz=true`를 기본값으로 둔다.
순수 성능 benchmark만 할 때 `rtabmap_viz:=false`로 끈다.

터미널 1:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

ros2 launch trashbot_description gazebo_mari_realsense_light.launch.py
```

터미널 2:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

ros2 launch trashbot_description mari_rtabmap_realsense_light.launch.py
```

터미널 3:

```bash
python3 Tools/teleop_mari_keyboard.py \
  --rate 60 \
  --linear-accel 0.15 \
  --angular-accel 0.45 \
  --key-timeout 1.2
```

터미널 4:

```bash
python3 Tools/check_mari_rtabmap_topics.py \
  --duration 20 \
  --label realsense_light_matched \
  --output-json assets/2026-04-29_mari_rtabmap_odom_mode_compare/04_realsense_light_matched_rtabmap_check.json \
  --output-md assets/2026-04-29_mari_rtabmap_odom_mode_compare/04_realsense_light_matched_rtabmap_check.md
```

방금 추가한 `424x240x10 + DetectionRate 3 + queue 10` 모드와 비교하면 다음과 같다.

| 항목 | 직전 실시간 우선 모드 | RealSense light 동일 조건 | 해석 |
| --- | ---: | ---: | --- |
| camera resolution | 424x240 | 424x240 | 동일 |
| camera FPS | 10 Hz | 15 Hz | RealSense light가 카메라 부하는 1.5배 큼 |
| camera pixel rate | 약 1.02 Mpx/s | 약 1.53 Mpx/s | Gazebo camera 생성/전송 부하는 직전 모드가 더 가벼움 |
| RTAB-Map DetectionRate | 3 Hz | 2 Hz | RealSense light가 RTAB-Map backend 부하는 더 낮음 |
| queue | 10 | 15 | RealSense light가 timestamp 흔들림에 더 여유 있음 |
| GUI | off 권장 | on 기본 | RealSense light wrapper는 데모 가시성을 우선 |

판정:

- Gazebo camera 자체가 병목이면 `424x240x10` 모드가 더 실시간적이다.
- RTAB-Map 계산이 병목이면 RealSense light 동일 조건이 더 안정적일 수 있다.
- 실제 D435i baseline과 비교 가능한 조건을 원하면 RealSense light 동일 조건을 사용한다.
- 순수 성능 측정에서는 `mari_rtabmap_realsense_light.launch.py rtabmap_viz:=false`로 GUI만 끈다.
- 가장 부드러운 Gazebo 주행/매핑만 원하면 직전 `424x240x10` 모드가 더 보수적인 저부하 조건이다.

### Park Test World

기존 `mari_camera_test.world`는 RGB-D topic과 RTAB-Map 입력 확인용으로는 좋지만,
환경이 단순해서 실제 공원 주행에 가까운 map 품질을 보기 어렵다.
공원형 검증에는 잔디, 보행로, 나무, 벤치, 표지판, 낮은 벽이 있는
`mari_park_test.world`를 사용한다.

더 긴 주행, 재방문, 회전 누적, 지도 확장 느낌을 보고 싶으면
`mari_large_park_test.world`를 사용한다.
이 world는 기존 공원 world보다 넓고, 산책로 루프, 광장, 나무 군집,
벤치, 표지판, 놀이터 블록, 화단, 돌, 경계 펜스를 더 많이 포함한다.

터미널 1:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

ros2 launch trashbot_description gazebo_mari_park_realsense_light.launch.py
```

큰 공원 world로 실행하려면 터미널 1만 아래 명령으로 바꾼다.

```bash
ros2 launch trashbot_description gazebo_mari_large_park_realsense_light.launch.py
```

터미널 2:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

ros2 launch trashbot_description mari_rtabmap_realsense_light.launch.py \
  detection_rate:=3 \
  queue_size:=20 \
  approx_sync_max_interval:=0.08 \
  rtabmap_viz:=true
```

터미널 3:

```bash
python3 Tools/teleop_mari_keyboard.py \
  --rate 60 \
  --linear-speed 0.08 \
  --angular-speed 0.45 \
  --linear-accel 0.12 \
  --angular-accel 0.35 \
  --key-timeout 1.2
```

확인 기준:

- RGB 화면에 잔디만 보이지 않고 보행로/표지판/나무/벤치가 함께 잡힌다.
- Depth PointCloud가 평면 하나가 아니라 서로 다른 높이의 구조물을 만든다.
- RTAB-Map 3D Map에서 경로 주변 landmark가 누적된다.
- 큰 공원 world에서는 시작점 주변뿐 아니라 전방 루프 경로와 양쪽 landmark까지 누적되는지 본다.
- 복잡도가 올라간 만큼 stutter가 생기면 먼저 `detection_rate:=2`로 낮춘다.

### RealSense Light + Local Odom 후보

위치 기반 Gazebo `/odom` baseline이 잘 동작하면, 다음은 odom 입력만
`/odometry/local`로 바꿔서 센서 기반 구조를 검증한다.

이 launch는 아래 경로를 한 번에 실행한다.

```text
Gazebo /odom
-> /motor/encoder_ticks
-> /wheel/odometry
-> /odometry/local
-> RTAB-Map
```

주의할 점:

- 아직 fake encoder tick은 Gazebo `/odom`에서 만든 값이다.
- 따라서 완전한 실제 센서 odom은 아니지만, ROS2 topic 구조는 실차 구조와 같아진다.
- 비교 목적상 camera/RTAB-Map 세팅은 잘 된 smooth baseline과 맞춘다.
- Gazebo IMU의 gyro covariance가 매우 작아 회전 보정이 과해질 수 있으므로,
  이 후보의 기본 EKF는 `ekf_local_gazebo_encoder_only.yaml`을 사용한다.
- IMU fusion을 시험할 때는 raw Gazebo IMU를 바로 쓰지 말고
  `/imu/data_bno08x_like` covariance republisher를 거치는 전용 launch를 쓴다.
- fake encoder tick은 Gazebo `/odom.twist`가 아니라 `/odom.pose` 변화량에서 만든다.
  `twist` 적분은 회전 중/정지 직후 yaw를 덜 반영할 수 있어서 local odom이 덜 도는 것처럼 보일 수 있다.

터미널 1:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

ros2 launch trashbot_description gazebo_mari_realsense_light.launch.py
```

터미널 2:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

ros2 launch trashbot_description mari_rtabmap_realsense_light_local_odom.launch.py
```

IMU까지 포함한 기존 EKF를 다시 비교하려면 아래처럼 실행한다.

```bash
ros2 launch trashbot_description mari_rtabmap_realsense_light_local_odom.launch.py \
  ekf_config:=$(ros2 pkg prefix trashbot_localization)/share/trashbot_localization/config/ekf_local.yaml
```

터미널 3:

```bash
python3 Tools/teleop_mari_keyboard.py \
  --rate 60 \
  --linear-speed 0.08 \
  --angular-speed 0.45 \
  --linear-accel 0.12 \
  --angular-accel 0.35 \
  --key-timeout 1.2
```

터미널 4:

```bash
python3 Tools/check_mari_rtabmap_topics.py \
  --duration 20 \
  --label local_odom_realsense_light_smooth \
  --odom-topic /odometry/local \
  --output-json assets/2026-04-29_mari_rtabmap_odom_mode_compare/06_local_odom_realsense_light_smooth_check.json \
  --output-md assets/2026-04-29_mari_rtabmap_odom_mode_compare/06_local_odom_realsense_light_smooth_check.md
```

비교 기준:

```text
/odom baseline:
05_odom_realsense_light_smooth_driving_check.*

/odometry/local 후보:
06_local_odom_realsense_light_smooth_check.*
```

### RealSense Light + Encoder/IMU Local Odom 후보

encoder-only local odom이 동작하면 다음은 `/wheel/odometry`와 IMU yaw/yaw-rate를 EKF에서 함께 쓰는 후보를 비교한다.
이 후보는 Gazebo `/imu/data`를 그대로 쓰지 않고, BNO08x-like covariance를 입힌 `/imu/data_bno08x_like`를 사용한다.
기본 실행은 yaw covariance가 과하게 커지지 않도록 `ekf_local_encoder_imu_bno08x_yaw_tuned.yaml`을 쓴다.

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

터미널 1:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

ros2 launch trashbot_description gazebo_mari_park_realsense_light.launch.py
```

터미널 2:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

ros2 launch trashbot_description mari_rtabmap_realsense_light_encoder_imu.launch.py
```

터미널 3:

```bash
python3 Tools/teleop_mari_keyboard.py \
  --rate 60 \
  --linear-speed 0.08 \
  --angular-speed 0.45 \
  --linear-accel 0.12 \
  --angular-accel 0.35 \
  --key-timeout 1.2
```

터미널 4:

```bash
python3 Tools/check_mari_rtabmap_topics.py \
  --duration 20 \
  --label large_park_encoder_imu_local_odom_yaw_tuned \
  --odom-topic /odometry/local \
  --output-json assets/2026-05-01_mari_large_park_rtabmap/03_large_park_encoder_imu_local_odom_yaw_tuned_check.json \
  --output-md assets/2026-05-01_mari_large_park_rtabmap/03_large_park_encoder_imu_local_odom_yaw_tuned_check.md
```

비교 기준:

```text
/odom baseline:
01_mari_park_world_rtabmap_odom_baseline.png
02_park_odom_baseline_rtabmap_check.*

encoder-only /odometry/local:
03_park_local_odom_rtabmap_check.*

encoder+IMU /odometry/local:
02_large_park_encoder_imu_local_odom_check.*

encoder+IMU yaw-tuned /odometry/local:
03_large_park_encoder_imu_local_odom_yaw_tuned_check.*
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
현재 Mari Gazebo 기본값은 작은 테스트 world에서 생기는 graph optimization 경고를 줄이기 위해 아래처럼 보수적으로 잡아뒀다.

- `Optimizer/Strategy=1`: `g2o` optimizer 사용. 기본 `GTSAM`보다 작은 synthetic world에서 덜 민감하다.
- `Reg/Force3DoF=true`, `RGBD/ForceOdom3DoF=true`: 지상 로봇이므로 `x/y/yaw` 평면 이동만 쓰게 한다.
- `Optimizer/GravitySigma=0`: 현재는 IMU/VIO gravity constraint를 쓰지 않는다.
- `RGBD/ProximityBySpace=false`: 좁은 테스트 world에서 불필요한 근접 loop link를 줄인다.

필요하면 처리 주기만 바꿔서 비교한다.

```bash
ros2 launch trashbot_description mari_rtabmap.launch.py detection_rate:=3
```

GTSAM 기본 동작과 비교하고 싶을 때만 아래처럼 바꾼다.

```bash
ros2 launch trashbot_description mari_rtabmap.launch.py optimizer_strategy:=2
```

RTAB-Map raw parameter를 추가로 실험해야 하면 `rtabmap_args_extra`에 붙인다.

```bash
ros2 launch trashbot_description mari_rtabmap.launch.py \
  rtabmap_args_extra:="--Vis/MinInliers 30 --Kp/MaxFeatures 700"
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
checker는 `/odom` covariance와 `/rtabmap/info` 진단값도 함께 출력한다.
RTAB-Map 내부 통계를 더 많이 보고 싶으면 아래처럼 실행한다.

```bash
python3 Tools/check_mari_rtabmap_topics.py --all-stats --max-stats 80
```

### `/odometry/local` 입력 비교

기본 RTAB-Map은 Gazebo가 직접 만든 `/odom`을 입력으로 쓴다.
local EKF 결과를 비교하려면 `/wheel/odometry + /imu/data -> /odometry/local`을 먼저 만들고, RTAB-Map의 `odom_topic`을 `/odometry/local`로 바꾼다.
아래 launch는 Gazebo가 켜져 있다는 전제에서 fake encoder bridge, local EKF, RTAB-Map을 한 번에 실행한다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

ros2 launch trashbot_description mari_rtabmap_local_odom.launch.py
```

RTAB-Map topic check도 local odom 입력 기준으로 실행한다.

```bash
python3 Tools/check_mari_rtabmap_topics.py --odom-topic /odometry/local
```

정상 기준:

```text
[OK] odom input: /odometry/local
[OK] rtabmap info output: /rtabmap/info
[OK] rtabmap map data output: /rtabmap/mapData
[OK] rtabmap cloud map output: /rtabmap/cloud_map
```

이미 `mari_gazebo_encoder_odom.launch.py`나 `mari_ekf_local.launch.py`를 따로 실행 중이면 중복 node를 피하기 위해 필요한 항목만 끈다.

```bash
ros2 launch trashbot_description mari_rtabmap_local_odom.launch.py \
  start_encoder_bridge:=false \
  start_ekf:=false
```

비교 실험에서는 같은 world와 비슷한 teleop 경로에서 아래 두 run을 따로 본다.

```bash
# Raw Gazebo odom baseline
ros2 launch trashbot_description mari_rtabmap.launch.py
python3 Tools/check_mari_rtabmap_topics.py \
  --duration 20 \
  --label raw_odom \
  --output-json assets/2026-04-29_mari_rtabmap_odom_mode_compare/01_raw_odom_rtabmap_check.json \
  --output-md assets/2026-04-29_mari_rtabmap_odom_mode_compare/01_raw_odom_rtabmap_check.md

# Local EKF odom baseline
ros2 launch trashbot_description mari_rtabmap_local_odom.launch.py
python3 Tools/check_mari_rtabmap_topics.py \
  --duration 20 \
  --label local_odom \
  --odom-topic /odometry/local \
  --output-json assets/2026-04-29_mari_rtabmap_odom_mode_compare/02_local_odom_rtabmap_check.json \
  --output-md assets/2026-04-29_mari_rtabmap_odom_mode_compare/02_local_odom_rtabmap_check.md
```

후보 B 조정 후에는 기존 `02_local_odom...` 결과와 구분하기 위해 새 이름으로 저장한다.

```bash
python3 Tools/check_mari_rtabmap_topics.py \
  --duration 20 \
  --label local_odom_tuned \
  --odom-topic /odometry/local \
  --output-json assets/2026-04-29_mari_rtabmap_odom_mode_compare/03_local_odom_tuned_rtabmap_check.json \
  --output-md assets/2026-04-29_mari_rtabmap_odom_mode_compare/03_local_odom_tuned_rtabmap_check.md
```

비교 기준:

```text
depth image rate
rtabmap info/cloud_map rate
poses/links 증가
graph optimization warning
teleop 중 체감 끊김
```

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

RViz2로 robot model, TF, odom, camera image, depth point cloud를 같이 보고 싶으면 아래 설정 파일로 실행한다.
이 설정은 `Fixed Frame = odom`으로 저장되어 있다.

```bash
rviz2 -d trashbot_description/rviz/mari_sensor_debug.rviz
```

수동으로 RViz2를 열었을 때 `Global Status: Error`와 `Frame [map] does not exist`가 보이면,
왼쪽 `Global Options -> Fixed Frame`을 `map`에서 `odom`으로 바꾼다.
Gazebo 기본 TF는 `odom -> base_footprint -> base_link -> camera_link/...`이므로, `map` frame은 RTAB-Map이나 별도 localization node가 publish하기 전까지 없다.
Gazebo launch는 `joint_state_publisher`도 함께 실행하므로, 네 개의 `*_virtual_track_wheel_link` 접촉 프레임도 RViz2에서 기본 joint state를 받는다.

RViz2 수동 설정:

```text
Fixed Frame = odom
Add -> RobotModel
Add -> TF
Add -> Odometry, Topic = /odom
Add -> Odometry, Topic = /wheel/odometry
Add -> By topic -> /camera/camera/color/image_raw -> Image
Add -> By topic -> /camera/camera/aligned_depth_to_color/image_raw -> Image
Add -> By topic -> /camera/camera/depth/color/points -> PointCloud2
```

## 3-3. 실제 encoder 후보 topic 확인

Gazebo의 `/odom`은 `planar_move` plugin이 만든 가상 odom이다.
실제 Mari 하드웨어에서는 motor driver 또는 encoder driver가 다른 topic을 낼 수 있으므로, 먼저 후보 topic을 찾아야 한다.

현재 기본 encoder topic 계약은 아래처럼 잡는다.

```text
topic: /motor/encoder_ticks
type:  std_msgs/msg/Int64MultiArray
data:  [left_ticks, right_ticks]
unit:  cumulative signed ticks
```

실제 Mari 또는 Jetson bring-up 환경에서 아래를 실행한다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

python3 Tools/check_mari_encoder_topics.py
```

이 스크립트는 이름이나 타입에 `encoder`, `wheel`, `motor`, `joint`, `odom`, `tick`, `count`, `rpm`이 들어간 topic을 찾고, 지원하는 타입이면 rate와 마지막 값을 같이 보여준다.
`/wheel/odometry`가 이미 `nav_msgs/Odometry`로 나오면 이후 local EKF의 wheel input 후보가 된다.
`/joint_states`나 raw tick/count만 보이면, 다음 단계는 이 값을 `/wheel/odometry`로 변환하는 adapter를 만드는 것이다.

후보가 안 보이면 전체 topic을 보면서 다시 좁힌다.

```bash
python3 Tools/check_mari_encoder_topics.py --all-topics --duration 3
```

## 3-4. Motor encoder tick을 `/wheel/odometry`로 변환

하드웨어가 없어도 raw encoder topic 계약을 mock으로 먼저 테스트할 수 있다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_localization mari_encoder_odom_mock.launch.py
```

확인:

```bash
ros2 topic echo /motor/encoder_ticks --once
ros2 topic echo /wheel/odometry --once
ros2 topic hz /wheel/odometry
```

실제 motor driver가 `/motor/encoder_ticks`를 publish하고 있으면 adapter만 실행한다.

```bash
ros2 launch trashbot_localization mari_encoder_odom.launch.py
```

거리 환산 파라미터는 `trashbot_localization/config/encoder_odom.yaml`에 있다.
실제 주행거리와 encoder count가 맞지 않으면 아래 값을 먼저 보정한다.

```text
ticks_per_revolution
effective_wheel_radius_m
track_width_m
left_ticks_sign
right_ticks_sign
```

현재 Mari MG513 초기 가설값은 `ticks_per_revolution=1560`이다.
이는 `13-line Hall encoder * 1:30 gear ratio * x4 quadrature decoding`을 가정한 값이며, 실측 전까지는 topic pipeline 검증용으로만 사용한다.
자세한 근거와 실차 보정 순서는 `01_Calibration/mari_mg513_encoder_initial_hypothesis.md`에 있다.

## 3-5. Gazebo `/odom`을 mock wheel odom으로 사용

`EKF`는 여러 센서의 추정값을 섞어 하나의 안정적인 odom을 만드는 필터다.
지금은 실제 encoder가 없으므로 Gazebo `/odom`을 `/wheel/odometry`로 복사해서 이후 구조를 먼저 확인한다.

Gazebo 움직임을 fake encoder tick으로 바꾸고, 기존 encoder adapter까지 같이 확인하려면 아래 경로를 쓴다.
이 방식은 Gazebo `/odom`을 직접 복사하지 않고 `/motor/encoder_ticks`를 한 번 거친다.

```text
Gazebo /odom
-> gazebo_odom_to_encoder_ticks
-> /motor/encoder_ticks
-> encoder_ticks_to_wheel_odom
-> /wheel/odometry
```

Gazebo가 켜진 상태에서 새 터미널을 연다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_localization mari_gazebo_encoder_odom.launch.py
```

다른 터미널에서 Gazebo 움직임에 맞춰 encoder tick과 wheel odom이 나오는지 확인한다.

```bash
python3 Tools/check_mari_encoder_topics.py --duration 6.0
ros2 topic echo /motor/encoder_ticks --once
ros2 topic echo /wheel/odometry --once
```

단순히 Gazebo `/odom`을 `/wheel/odometry`로 복사만 하려면 아래 bridge를 쓴다.

```bash
ros2 launch trashbot_localization mari_wheel_odom_mock.launch.py
```

다른 터미널에서 mock wheel odom이 나오는지 확인한다.

```bash
ros2 topic echo /wheel/odometry --once
ros2 topic hz /wheel/odometry
```

`robot_localization`이 설치되어 있으면 local EKF까지 실행한다.

```bash
ros2 launch trashbot_localization mari_ekf_local.launch.py
ros2 topic echo /odometry/local --once
```

현재 PC에 `robot_localization`이 없으면 아래 패키지가 필요하다.

```bash
sudo apt install ros-humble-robot-localization
```

`robot_localization` 없이 bridge만 테스트하려면 아래처럼 실행한다.

```bash
ros2 launch trashbot_localization mari_ekf_local.launch.py start_ekf:=false
```

실제 encoder 하드웨어가 연결되면 `start_gazebo_odom_bridge:=false`로 실행하고, 실제 driver 또는 adapter가 `/wheel/odometry`를 publish하게 바꾼다.

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

Gazebo 장착 센서 전체를 한 번에 확인한다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM

python3 Tools/check_mari_gazebo_sensor_topics.py --duration 8.0
```

확인 대상:

```text
/odom
/imu/data
/gps/fix
/camera/camera/color/image_raw
/camera/camera/aligned_depth_to_color/image_raw
/camera/camera/color/camera_info
/camera/camera/aligned_depth_to_color/camera_info
/camera/camera/depth/color/points
```

주의:

- Gazebo GPS plugin은 현재 `/gps/fix`의 `frame_id`를 `base_footprint`로 publish한다.
- 값 수신 검증은 가능하지만, GPS 안테나 위치 오프셋까지 정확히 쓰려면 이후 `gps_link` frame 보정 또는 republish가 필요하다.

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
