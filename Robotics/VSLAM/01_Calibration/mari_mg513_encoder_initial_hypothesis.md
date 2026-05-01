# Mari MG513 Encoder Initial Hypothesis

## 결론

현재 값은 실제 calibration 결과가 아니라 `/motor/encoder_ticks -> /wheel/odometry` topic 흐름을 먼저 확인하기 위한 초기 가설값이다.
실제 Mari 하드웨어가 연결되면 반드시 구동축 1회전 tick, 1m 직진 거리, 360도 제자리 회전으로 보정해야 한다.

## 근거

- Mari는 MG513 모터를 사용한다고 확인했다.
- 로컬 WHEELTEC 자료의 CAD/설치 자료에서는 MG513/MG513P30 계열 이름이 확인된다.
- 공개 판매 자료에서는 MG513P30_12V, 13-line Hall encoder, 1:30 gear ratio 조합이 확인된다.
- 다만 이 자료들은 정식 MG513 데이터시트가 아니므로 최종 calibration 값으로 쓰면 안 된다.

## 초기 가설값

```text
motor: MG513P30_12V
encoder: 13-line Hall encoder
gear_ratio: 30
quadrature_decode_factor: 4
ticks_per_revolution: 13 * 30 * 4 = 1560
effective_wheel_radius_m: 0.021
track_width_m: 0.137553
```

`ticks_per_revolution`은 구동축 1회전에 해당하는 encoder tick 수다.
여기서는 motor driver가 A/B quadrature encoder를 x4 decoding해서 누적 tick을 publish한다고 가정했다.

## 틀릴 수 있는 부분

| motor driver tick 방식 | 예상 ticks/rev |
| --- | ---: |
| 단일 채널 1배 pulse count | 390 |
| A/B 2배 edge count | 780 |
| A/B 4배 quadrature count | 1560 |

실제 `/motor/encoder_ticks`를 만든 firmware가 어느 방식으로 count하는지 확인되기 전까지는 `1560`을 topic 검증용 기본값으로만 사용한다.

## 현재 적용 위치

- `trashbot_localization/config/encoder_odom.yaml`
- `trashbot_localization/scripts/encoder_ticks_to_wheel_odom.py`
- `trashbot_localization/scripts/mock_motor_encoder_ticks.py`

## Topic 검증 명령

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
colcon build --packages-select trashbot_localization --symlink-install
source install/setup.bash

ros2 launch trashbot_localization mari_encoder_odom_mock.launch.py
```

다른 터미널에서 확인한다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

python3 Tools/check_mari_encoder_topics.py --duration 6.0
ros2 topic echo /motor/encoder_ticks --once
ros2 topic echo /wheel/odometry --once
```

## 2026-04-29 Mock Topic 검증 결과

결론: 실제 모터 하드웨어 없이도 mock encoder publisher와 adapter 기준으로 `/motor/encoder_ticks -> /wheel/odometry` 변환 pipeline은 직진/회전 모두 통과했다.

### 직진 mock

실행:

```bash
ros2 launch trashbot_localization mari_encoder_odom_mock.launch.py
python3 Tools/check_mari_encoder_topics.py --duration 6.0
```

관찰:

```text
[OK] /motor/encoder_ticks type=std_msgs/msg/Int64MultiArray count=181 rate=30.0 Hz len=2 data=[22227, 22227]
[OK] /wheel/odometry type=nav_msgs/msg/Odometry count=180 rate=30.0 Hz frame=odom child=base_footprint x=1.867 y=0.000 yaw=0.000 vx=0.101 wz=0.000
```

해석:

- 좌/우 tick이 같은 방향으로 증가하므로 직진 입력으로 해석된다.
- `/wheel/odometry.twist.twist.linear.x`가 약 `0.10 m/s`로 mock 설정값과 맞는다.
- 회전 속도 `wz`는 `0.000`으로 직진 상태에 맞다.

### 제자리 회전 mock

실행:

```bash
ros2 launch trashbot_localization mari_encoder_odom_mock.launch.py \
  linear_velocity_mps:=0.0 \
  angular_velocity_radps:=0.5

python3 Tools/check_mari_encoder_topics.py --duration 6.0
```

관찰:

```text
[OK] /motor/encoder_ticks type=std_msgs/msg/Int64MultiArray count=181 rate=30.0 Hz len=2 data=[-5041, 5041]
[OK] /wheel/odometry type=nav_msgs/msg/Odometry count=180 rate=30.0 Hz frame=odom child=base_footprint x=0.000 y=0.000 yaw=-0.166 vx=0.000 wz=0.519
```

해석:

- 좌/우 tick이 반대 방향으로 변하므로 제자리 회전 입력으로 해석된다.
- `/wheel/odometry.twist.twist.angular.z`가 약 `0.52 rad/s`로 mock 설정값 `0.5 rad/s`와 가깝다.
- `x`, `y`, `vx`가 0 근처이므로 직진 이동 없이 회전 odometry가 생성된다.
- `yaw` 값은 각도 정규화 구간에 따라 음수로 보일 수 있으나, 핵심 검증값은 `wz`와 좌우 tick 부호다.

### 현재 판정

- `[완료]` `/motor/encoder_ticks` topic 계약 검증
- `[완료]` 직진 tick을 `/wheel/odometry`로 변환
- `[완료]` 회전 tick을 `/wheel/odometry`로 변환
- `[남음]` 실제 MG513 motor driver가 publish하는 tick count 방식 확인
- `[남음]` 실제 Mari에서 `ticks_per_revolution`, `effective_wheel_radius_m`, `track_width_m` 보정

## 실차 보정 순서

1. 전원을 끄거나 로봇을 들어 올린 상태에서 한쪽 구동축을 정확히 1회전시켜 tick 증가량을 확인한다.
2. 좌우 구동축 각각 1회전 tick을 확인해 부호와 count 방식이 같은지 확인한다.
3. 바닥에서 1m 직진시켜 `/wheel/odometry.pose.pose.position.x`가 1m에 가까운지 확인한다.
4. 제자리 360도 회전시켜 yaw 변화가 약 6.283 rad인지 확인한다.
5. 오차가 크면 `ticks_per_revolution`, `effective_wheel_radius_m`, `track_width_m` 순서로 보정한다.
