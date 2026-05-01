# Trashbot Localization

## 결론

- 이 패키지는 Mari의 localization 구조를 미리 고정하기 위한 패키지다.
- 실제 encoder 하드웨어가 없어도 `/motor/encoder_ticks -> /wheel/odometry` 변환 구조를 먼저 검증할 수 있다.
- Gazebo `/odom`을 mock `/wheel/odometry`로 바꾸는 경로도 유지하지만, 최종 계약은 motor encoder raw topic을 기준으로 둔다.
- 실제 하드웨어가 연결되면 motor driver가 `/motor/encoder_ticks`를 publish하고, adapter가 `/wheel/odometry`를 publish한다.

## 용어

- `odometry`: 로봇이 직전 상태에서 지금까지 얼마나 움직였는지 추정한 값이다.
- `wheel odometry`: 바퀴 또는 궤도 encoder 기반 이동량이다.
- `encoder tick`: 모터축이나 바퀴가 회전할 때 encoder가 세는 누적 카운트다.
- `EKF`: 여러 센서의 위치/속도/회전 추정값을 하나로 섞어 더 안정적인 상태를 만드는 필터다.

## 현재 구조

```text
Real motor driver ------------------> /motor/encoder_ticks
                                      std_msgs/Int64MultiArray
                                      data[0] = left cumulative ticks
                                      data[1] = right cumulative ticks

/motor/encoder_ticks ---------------> encoder_ticks_to_wheel_odom
                                      -> /wheel/odometry

/wheel/odometry + /imu/data --------> robot_localization EKF
                                      -> /odometry/local
```

Gazebo-only 구조는 아래처럼 별도 mock 경로로 둔다.

```text
Gazebo /odom -----------------------> /wheel/odometry
Gazebo /imu/data -------------------> /imu/data

/wheel/odometry + /imu/data --------> robot_localization EKF
                                      -> /odometry/local
```

현재 Gazebo에서는 `/odom`과 `odom -> base_footprint` TF를 `planar_move` plugin이 publish한다.
그래서 mock EKF config의 `publish_tf` 기본값은 `false`다.
실제 하드웨어에서 EKF가 `odom -> base_footprint`를 책임지는 단계가 되면 `publish_tf`를 `true`로 바꿔야 한다.

## Encoder Topic 계약

실제 motor driver는 아래 topic을 publish하는 것을 기본 계약으로 둔다.

```text
topic: /motor/encoder_ticks
type:  std_msgs/msg/Int64MultiArray
data:  [left_ticks, right_ticks]
unit:  cumulative signed ticks
rate:  권장 30 Hz 이상
```

규칙:

- tick은 매 메시지마다 0으로 초기화하지 않고 누적값으로 보낸다.
- 전진할 때 좌우 tick이 같은 부호로 증가하도록 맞춘다.
- 부호가 반대면 `left_ticks_sign`, `right_ticks_sign` 파라미터로 보정한다.
- 좌우 이동 거리 차이가 일정하게 나면 `left_distance_scale`, `right_distance_scale`로 보정한다.
- 실제 거리 환산은 `ticks_per_revolution`, `effective_wheel_radius_m`, `track_width_m`로 계산한다.
- 비현실적인 tick jump, 속도, 회전속도, 긴 수신 gap은 adapter에서 1차로 reject한다.

## Mari MG513 초기 가설값

아직 정식 데이터시트와 실측값이 없으므로 아래 값은 topic pipeline 검증용 초기값이다.
거리 정확도를 보장하는 calibration 값이 아니다.

```text
motor: MG513P30_12V 가정
encoder: 13-line Hall encoder 가정
gear ratio: 1:30 가정
decode: x4 quadrature count 가정

ticks_per_revolution = 13 * 30 * 4 = 1560
effective_wheel_radius_m = 0.021
track_width_m = 0.137553
```

주의:

- motor driver가 단일 채널 pulse만 세면 `ticks_per_revolution`은 `390`일 수 있다.
- motor driver가 A/B 양쪽 rising edge만 세면 `780`일 수 있다.
- 실제 Mari에서는 구동축/궤도 1회전 tick과 1m 직진 실측으로 반드시 보정해야 한다.

## Encoder 보정/방어 파라미터

`encoder_ticks_to_wheel_odom.py`는 실제 encoder bring-up에서 `/wheel/odometry`가 한 번에 크게 튀는 것을 막기 위해 1차 보정/방어 파라미터를 가진다.

```text
ticks_per_revolution       output shaft 또는 궤도 1회전당 tick 수
effective_wheel_radius_m   tick을 거리로 바꿀 때 쓰는 유효 반지름
track_width_m              좌우 궤도 중심 간 유효 거리
left_ticks_sign            왼쪽 tick 부호 보정
right_ticks_sign           오른쪽 tick 부호 보정
left_distance_scale        왼쪽 거리 scale 보정
right_distance_scale       오른쪽 거리 scale 보정
reject_outlier_samples     이상 샘플 reject 활성화
max_tick_delta             한 샘플에서 허용할 최대 tick 변화량
max_linear_velocity_mps    encoder로 계산한 최대 허용 선속도
max_angular_velocity_radps encoder로 계산한 최대 허용 회전속도
max_encoder_gap_sec        encoder 메시지 사이 최대 허용 시간 간격
```

Reject 동작:

- `max_tick_delta`를 넘는 누적 tick jump가 오면 해당 샘플을 버린다.
- 계산된 `linear.x` 또는 `angular.z`가 제한값을 넘으면 해당 샘플을 버린다.
- encoder 메시지 간격이 `max_encoder_gap_sec`보다 길면 누적 tick baseline을 재설정한다.
- reject 시 pose는 그대로 유지하고, zero velocity odom을 한 번 publish한다.
- 이후 다음 정상 tick부터 다시 적분한다.

이 방어는 잘못된 encoder 값을 완전히 복구하는 기능이 아니라, 한 번의 이상값이 EKF와 RTAB-Map trajectory를 크게 흔들지 않도록 막는 1차 안전장치다.

## IMU covariance republisher

Gazebo IMU는 covariance가 너무 작게 들어올 수 있다.
Covariance는 "이 센서값을 얼마나 믿을지"를 나타내는 값이므로, 너무 작으면 EKF가 IMU yaw-rate를 과하게 믿는다.

`imu_covariance_republisher.py`는 raw `/imu/data`를 받아 같은 IMU 값에 BNO08x-like covariance를 입힌 뒤 `/imu/data_bno08x_like`로 다시 publish한다.

```text
/imu/data
-> imu_covariance_republisher.py
-> /imu/data_bno08x_like
```

기본값:

```text
orientation_covariance: 0.01
angular_velocity_covariance: 0.001
linear_acceleration_covariance: 0.01
```

이 값은 실제 BNO08x 최종 보정값이 아니라, Gazebo IMU의 near-zero covariance를 피하기 위한 1차 보수값이다.

## Encoder + IMU EKF profile

첫 encoder+IMU fusion profile은 아래 역할 분리를 기준으로 했다.

```text
/wheel/odometry        x/y position, forward velocity
/imu/data_bno08x_like  angular_velocity.z
-> /odometry/local
```

이 yaw-rate-only profile은 보수적이지만 yaw pose 자체를 직접 관측하지 않아
시간이 지나며 EKF yaw covariance가 커질 수 있다.
RTAB-Map 비교용 기본 profile은 yaw covariance를 낮추기 위해 아래처럼 조정했다.

```text
/wheel/odometry        x/y/yaw pose, forward velocity, yaw-rate
/imu/data_bno08x_like  yaw orientation, yaw-rate
-> /odometry/local
```

설정 파일은 아래에 있다.

- `config/ekf_local_encoder_imu_bno08x_like.yaml`
- `config/ekf_local_encoder_imu_bno08x_yaw_tuned.yaml`
- `config/imu_covariance_bno08x_like.yaml`

## 실행

하드웨어 없이 raw encoder topic과 odom 변환을 같이 테스트한다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_localization mari_encoder_odom_mock.launch.py
ros2 topic echo /motor/encoder_ticks --once
ros2 topic echo /wheel/odometry --once
```

제자리 회전 mock:

```bash
ros2 launch trashbot_localization mari_encoder_odom_mock.launch.py \
  linear_velocity_mps:=0.0 \
  angular_velocity_radps:=0.5
```

큰 tick jump 방어 확인:

```bash
ros2 launch trashbot_localization mari_encoder_odom_mock.launch.py \
  tick_jump_after_sec:=2.0 \
  tick_jump_left:=20000 \
  tick_jump_right:=20000
```

정상이라면 adapter 로그에 아래와 같은 warning이 한 번 나온다.

```text
Rejected encoder sample #1: encoder tick jump exceeded limit ...
Resetting encoder baseline and publishing zero velocity.
```

실제 motor driver가 `/motor/encoder_ticks`를 publish하고 있으면 adapter만 실행한다.

```bash
ros2 launch trashbot_localization mari_encoder_odom.launch.py
ros2 topic echo /wheel/odometry --once
```

Gazebo 움직임을 fake encoder tick으로 바꾼 뒤 기존 adapter까지 통과시킨다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_localization mari_gazebo_encoder_odom.launch.py
ros2 topic echo /motor/encoder_ticks --once
ros2 topic echo /wheel/odometry --once
```

이 launch의 기본 encoder 변환 설정은 `config/encoder_odom_gazebo.yaml`이다.
이 파일은 Gazebo `/odom`에서 만든 fake encoder odom 전용 covariance를 사용한다.
실제 motor encoder의 거리 보정용 기본값은 `config/encoder_odom.yaml`에 남겨둔다.

이 경로는 아래처럼 동작한다.

```text
Gazebo /odom
-> gazebo_odom_to_encoder_ticks
-> /motor/encoder_ticks
-> encoder_ticks_to_wheel_odom
-> /wheel/odometry
```

이 방식은 실제 motor driver가 생기기 전까지 Gazebo 주행과 encoder odometry pipeline을 함께 확인하기 위한 bridge다.
실제 하드웨어에서는 `gazebo_odom_to_encoder_ticks`를 쓰지 않고 motor driver가 `/motor/encoder_ticks`를 직접 publish해야 한다.

Gazebo가 켜진 상태에서 mock wheel odom만 확인한다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_localization mari_wheel_odom_mock.launch.py
ros2 topic echo /wheel/odometry --once
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

RTAB-Map이 local EKF output을 쓰게 비교하려면 Gazebo를 먼저 켠 뒤 아래 launch를 실행한다.

```bash
ros2 launch trashbot_description mari_rtabmap_local_odom.launch.py
python3 Tools/check_mari_rtabmap_topics.py --odom-topic /odometry/local
```

이 경로는 `/wheel/odometry + /imu/data -> /odometry/local`을 만든 뒤,
RTAB-Map의 odom input을 기존 `/odom` 대신 `/odometry/local`로 바꾼다.
현재 Gazebo 비교에서는 raw `/odom` 입력을 기본 매핑 baseline으로 두고,
`/odometry/local` 입력은 실제 encoder/IMU 구조 전환을 위한 후보 B로 분리한다.

Encoder + BNO08x-like IMU covariance profile을 바로 비교하려면 Gazebo를 먼저 켠 뒤 아래 launch를 실행한다.
이 launch의 기본 EKF config는 `ekf_local_encoder_imu_bno08x_yaw_tuned.yaml`이다.

```bash
ros2 launch trashbot_description mari_rtabmap_realsense_light_encoder_imu.launch.py
python3 Tools/check_mari_rtabmap_topics.py --odom-topic /odometry/local
```

이 launch는 아래 경로를 실행한다.

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

후보 B 조정 후 재검증 결과는 아래 이름으로 저장한다.

```bash
python3 Tools/check_mari_rtabmap_topics.py \
  --duration 20 \
  --label large_park_encoder_imu_local_odom_yaw_tuned \
  --odom-topic /odometry/local \
  --output-json assets/2026-05-01_mari_large_park_rtabmap/03_large_park_encoder_imu_local_odom_yaw_tuned_check.json \
  --output-md assets/2026-05-01_mari_large_park_rtabmap/03_large_park_encoder_imu_local_odom_yaw_tuned_check.md
```

## 실제 encoder 연결 시 전환

1. motor driver가 `/motor/encoder_ticks`를 publish하게 맞춘다.
2. `Tools/check_mari_encoder_topics.py`로 topic type/rate/값 변화를 확인한다.
3. `mari_encoder_odom.launch.py`를 실행해 `/wheel/odometry`가 나오는지 확인한다.
4. 직진 시 `/wheel/odometry.pose.pose.position.x`가 증가하는지 확인한다.
5. 제자리 회전 시 yaw와 `twist.twist.angular.z` 부호가 기대와 맞는지 확인한다.
6. `/wheel/odometry`가 안정적으로 나오면 `start_gazebo_odom_bridge:=false`로 EKF를 실행한다.
7. Gazebo가 아닌 실차에서는 EKF가 TF를 담당하도록 `ekf_local.yaml`의 `publish_tf`를 `true`로 바꾼다.
