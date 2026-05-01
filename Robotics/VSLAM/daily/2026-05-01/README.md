# 2026-05-01 작업 일지

## 결론

- 오늘의 핵심 결과는 encoder-only local odom 다음 단계로 encoder+IMU EKF 후보를 추가한 것이다.
- Gazebo raw `/imu/data`를 바로 EKF에 넣지 않고, BNO08x-like covariance를 입힌 `/imu/data_bno08x_like`를 쓰도록 했다.
- `/wheel/odometry`는 위치와 전진속도, `/imu/data_bno08x_like`는 yaw-rate를 담당하는 local EKF profile을 추가했다.
- 공원형 Gazebo world에서 이 encoder+IMU `/odometry/local` 후보를 RTAB-Map으로 바로 비교할 수 있는 launch를 추가했다.
- 더 긴 주행과 현실적인 landmark 분포 확인을 위해 큰 공원형 Gazebo world를 추가했다.
- 아직 실제 BNO08x 하드웨어 입력은 아니며, Gazebo IMU를 실제 센서 구조에 가깝게 다루기 위한 중간 검증 단계다.

## 오늘 작업 한 줄 요약

- Gazebo fake encoder와 Gazebo IMU를 실제 encoder/BNO08x 구조처럼 연결해 `/odometry/local`을 만들고, 큰 공원형 world까지 준비했다.

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
- [Mari_Gazebo_Run_Guide.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/learning/Mari_Gazebo_Run_Guide.md)

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

## 남은 문제

- yaw-tuned encoder+IMU `/odometry/local`은 개선됐지만 `/odom` baseline 수준까지는 아직 내려오지 않았다.
- 현재 fake encoder source는 여전히 Gazebo `/odom`이므로 실제 motor encoder 성능을 증명한 것은 아니다.
- BNO08x 실제 하드웨어 covariance와 yaw-rate scale은 장착 후 재측정해야 한다.

## 다음 액션

1. yaw-tuned `/odometry/local`의 `Loop/MapToBase_lin_std`를 낮추기 위해 EKF covariance와 RTAB-Map odom 신뢰도 설정을 한 번 더 조정한다.
2. 같은 주행 경로로 `/odom` baseline과 yaw-tuned `/odometry/local`을 다시 비교한다.
3. 큰 공원 world에서 긴 loop 주행을 수행해 loop closure가 실제로 accept되는지 확인한다.
4. 실제 encoder/BNO08x 연결 전까지는 fake encoder 기반 결과라는 전제를 문서에 계속 표시한다.

## 한 줄 회고

- 실제 센서가 없어도 encoder와 IMU가 들어왔을 때의 ROS2/EKF/RTAB-Map 연결 방식을 먼저 고정했다.
