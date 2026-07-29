# Drivetrain Kinematics and Odometry Plan

## 목적

이 문서는 궤도형 모바일 로봇의 첫 kinematics와 odometry 계획을 정의한다.

로봇은 left/right tracked drivetrain을 사용한다. Low-speed control과 첫 odometry에서는 differential-drive
robot처럼 다룰 수 있다. 즉 left track과 right track의 속도 차이로 전진과 회전을 만든다.

이 문서는 다음 질문에 답한다.

- Command velocity가 left/right track command로 어떻게 바뀌는가
- Encoder count가 distance와 speed estimate로 어떻게 바뀌는가
- Odometry를 시간에 따라 어떻게 적분하는가
- IMU data는 나중에 어디에 추가되는가
- Tracked vehicle odometry의 한계는 무엇인가
- Odometry model이 쓸 만하다는 것을 어떤 test로 증명하는가

## Architecture Decision

첫 tracked drivetrain model은 differential-drive approximation을 사용한다.

Initial command variables:

```text
vx_mmps   : forward velocity in mm/s
w_mradps : yaw rate in millirad/s
```

Initial output variables:

```text
left_track_speed
right_track_speed
left_motor_pwm
right_motor_pwm
```

핵심 결정:

```text
Encoder-based differential odometry를 먼저 사용한다.
Drivetrain과 encoder sign이 안정된 뒤 IMU yaw-rate correction을 추가한다.
```

## 1. 용어

| Term | 이 프로젝트에서의 의미 |
| --- | --- |
| Kinematics | Robot motion과 left/right track motion 사이의 관계 |
| Odometry | Wheel 또는 track encoder data로 robot movement를 추정하는 것 |
| Track width | Left/right contact line 사이의 effective distance |
| Encoder count | Motor 또는 wheel encoder에서 측정한 tick count |
| Counts per revolution | Shaft 또는 output 1회전에 해당하는 encoder count |
| Distance per count | Encoder count 1개가 나타내는 linear travel estimate |
| Yaw | Vertical axis 주변 heading angle |
| Slip | Track이 움직였지만 실제 ground movement로 변환되지 않은 현상 |

## 2. Coordinate Convention

일반 mobile robot body convention을 사용한다.

```text
x axis: forward
y axis: left
z axis: up
positive yaw: 위에서 봤을 때 counter-clockwise turn
```

Robot pose:

```text
x_m     : position x in meters
y_m     : position y in meters
yaw_rad : heading in radians
```

Command convention:

```text
positive vx -> robot moves forward
positive w  -> robot turns left
```

Encoder sign은 이 convention이 성립하도록 조정해야 한다.

### Bench encoder sign convention

2026-07-26 motor-power-off 시험에서는 output shaft end를 정면에서 본 기준으로
clockwise 회전 시 TIM3 count가 증가하고 counter-clockwise 회전 시 감소했다.
이 부호는 `PB4 = CH1/A`, `PB5 = CH2/B`인 bench wiring 결과일 뿐이며,
차량 forward와 left/right encoder sign은 motor 장착 후 별도로 확정한다.

## 3. Differential Drive Approximation

정의:

```text
v     = robot forward velocity
w     = robot yaw rate
B     = effective track width
v_l   = left track linear velocity
v_r   = right track linear velocity
```

Forward model:

```text
v = (v_r + v_l) / 2
w = (v_r - v_l) / B
```

Inverse model:

```text
v_l = v - (w * B / 2)
v_r = v + (w * B / 2)
```

Project interpretation:

- Left/right speed가 같으면 직진.
- Right가 left보다 빠르면 left turn.
- Left가 right보다 빠르면 right turn.
- 부호가 반대면 제자리 회전 후보.

## 4. Encoder Distance Model

각 side에 대해:

```text
distance_per_count = output_circumference / counts_per_output_rev
distance = delta_count * distance_per_count
```

여기서:

- `output_circumference`는 effective sprocket 또는 track driving circumference다.
- Encoder가 motor shaft에 있다면 `counts_per_output_rev`에는 encoder resolution과 gearbox ratio가 포함되어야 한다.

측정해야 할 open parameters:

| Parameter | How to obtain |
| --- | --- |
| Encoder counts per output revolution | Motor/encoder datasheet와 반복 bench/주행 measurement |
| Gear ratio | Motor model datasheet 또는 manual count test |
| Output sprocket circumference | 직접 측정 또는 track movement로 추정 |
| Effective track width | Chassis 측정, rotation test로 tune |
| Encoder sign | Bench sign과 별개로 low-speed vehicle-forward command에서 확인 |

Motor label의 nominal 정보만으로 정확한 odometry가 가능하다고 가정하지 않는다.

2026-07-26 TIM3 TI12 x4 hand-rotation에서 얻은 provisional 값은 다음과 같다.

| Bench motor | Shaft-end-view CW | Shaft-end-view CCW | Provisional counts/output rev |
| --- | ---: | ---: | ---: |
| MG540-A | 약 +1560 | 약 -(1560~1570) | 약 1560 |
| MG540-B | +1562 | -1560 | 약 1560 |

`1560 counts/output rev`는 motor-power-off 1회전 수동 측정의 provisional scale이다.
Powered/noise 조건, 반복 측정, TIM5와 실제 drivetrain scale 검증 전에는 final
odometry constant로 고정하지 않는다. Raw serial log는 MG540-A의 정지 안정성과
방향별 count 증감만 직접 보여 주며, 위 1회전 수치와 MG540-B 결과는 같은 bench
session의 별도 측정 보고다. Evidence는
[`../assets/logs/encoder/README.md`](../assets/logs/encoder/README.md)에 정리한다.

### 2026-07-30 50-Revolution Calibration

위 2026-07-26 provisional scale을 보완하기 위해 표시한 출력축을 motor별·방향별
50회전시켰다.

| Bench motor | Direction | Absolute total count | Counts/output rev |
| --- | --- | ---: | ---: |
| MG540-A | CW | 77,998 | 1559.96 |
| MG540-A | CCW | 78,001 | 1560.02 |
| MG540-B | CW | 78,000 | 1560.00 |
| MG540-B | CCW | 78,000 | 1560.00 |

현재 STM32 quadrature x4 기준 firmware 변환 상수는 `1560 counts/output rev`로
확정한다. Signed CPS -> mRPM은 `trunc(CPS * 60000 / 1560)`으로 계산하며 boot
self-test와 305-row dual hand-rotation log에서 계산·방향·정지 복귀가 통과했다.

이 결정은 count-to-output-revolution scale을 닫은 것이다. Track odometry의
`distance_per_count`는 effective sprocket/track travel, track slip과 실제 차량
forward sign을 측정하기 전까지 확정하지 않는다. External tachometer 기반 절대
RPM 정확도와 powered-motor noise도 별도 시험 대상이다. 상세 evidence는
[`../assets/logs/encoder/2026-07-30_encoder_output_shaft_calibration_and_millirpm_verification.md`](../assets/logs/encoder/2026-07-30_encoder_output_shaft_calibration_and_millirpm_verification.md)에 있다.

## 5. Speed Estimation

각 control period마다:

```text
delta_count = current_count - previous_count
distance_m = delta_count * distance_per_count_m
speed_mps = distance_m / dt_s
```

Initial filtering:

- Bench validation 중에는 raw speed부터 사용한다.
- Sign과 scale을 확인한 뒤 simple moving average 또는 low-pass filtering을 추가한다.
- 가능하면 filtered value와 raw value를 모두 debug log에 남긴다.

Filtering이 필요한 이유:

- Encoder count는 discrete하다.
- Low-speed motion에서는 tick이 드물게 발생할 수 있다.
- Motor와 track vibration이 speed estimate noise를 만들 수 있다.

## 6. Odometry Integration

각 odometry update마다:

```text
d_l = left_distance_delta
d_r = right_distance_delta
d_center = (d_r + d_l) / 2
d_yaw = (d_r - d_l) / B
```

Pose update:

```text
yaw_mid = yaw + d_yaw / 2
x = x + d_center * cos(yaw_mid)
y = y + d_center * sin(yaw_mid)
yaw = yaw + d_yaw
```

내부 계산은 radians를 사용한다.

Initial update rate:

```text
50 Hz to 100 Hz
```

같은 100 Hz motor loop에서 basic odometry를 계산할 수 있고, FreeRTOS 도입 이후 별도 lower-priority task로
분리할 수도 있다.

## 7. Tracked Vehicle Limitations

Tracked robot은 ideal wheeled differential-drive robot보다 slip이 크다.

Common error sources:

- Track slip during turns
- Track deformation
- Uneven floor friction
- Different left/right motor response
- Encoder mounted before gearbox
- Backlash 또는 mechanical looseness
- Load-dependent current and speed changes

Implication:

Encoder-only odometry는 short-term motion estimation에는 유용하지만, globally accurate position으로
취급하면 안 된다.

## 8. IMU Fusion Path

BNO08x IMU는 나중에 heading behavior 개선에 사용할 수 있다.

First IMU uses:

- Encoder yaw rate와 IMU yaw rate 비교.
- Turn 중 큰 slip 감지.
- IMU yaw를 heading correction 후보로 사용.
- Yaw 또는 yaw-rate telemetry publish.

처음부터 복잡한 sensor fusion을 시작하지 않는다.

Recommended progression:

```text
encoder-only odometry
    -> compare encoder yaw with IMU yaw
    -> simple complementary heading correction
    -> later ROS2 odometry message and TF integration
```

Simple complementary idea:

```text
yaw_est = alpha * yaw_encoder + (1 - alpha) * yaw_imu
```

이 방식은 time alignment, axis convention, IMU orientation을 확인한 뒤에만 사용한다.

## 9. Command to Motor Output

Command path:

```text
vx_mmps, w_mradps
        |
        v
convert to v_l, v_r
        |
        v
apply speed limits
        |
        v
apply acceleration/ramp limits
        |
        v
open-loop PWM or speed controller
        |
        v
MDD10A PWM + DIR output
```

Initial control mode:

- Low PWM open-loop으로 시작한다.
- Encoder count는 처음에는 observation용으로만 사용한다.
- Speed estimation을 추가한다.
- Encoder sign과 scale이 안정된 뒤 proportional control을 추가한다.
- P control behavior를 이해한 뒤 PID를 추가한다.

## 10. Calibration Tests

### Test 1: Encoder Sign Test

Procedure:

- Track을 들어 올린다.
- Low forward speed를 command한다.
- Left/right encoder count direction을 확인한다.

Expected:

- Forward command에서 양쪽 count가 증가한다.

### Test 2: Distance Scale Test

Procedure:

- Floor start position을 표시한다.
- 짧은 직선 motion을 command한다.
- 실제 이동 거리를 측정한다.
- Encoder-estimated distance와 비교한다.

Expected:

- Scale error가 측정되고 문서화된다.

### Test 3: Rotation Scale Test

Procedure:

- Slow in-place rotation을 command한다.
- 실제 yaw change를 측정한다.
- Odometry yaw와 비교한다.

Expected:

- Effective track width를 tune할 수 있다.

### Test 4: Straight-Line Drift Test

Procedure:

- Straight motion을 command한다.
- Left/right encoder speed를 기록한다.
- Robot이 left/right로 치우치는지 관찰한다.

Expected:

- Motor mismatch와 track friction이 식별된다.

### Test 5: IMU Comparison Test

Procedure:

- 천천히 회전한다.
- Encoder yaw rate와 IMU yaw rate를 비교한다.

Expected:

- Fusion 전에 IMU axis와 sign이 검증된다.

## 11. Telemetry Fields

Recommended odometry telemetry:

```text
left_count
right_count
left_delta
right_delta
left_speed_mmps
right_speed_mmps
vx_est_mmps
w_est_mradps
odom_x_mm
odom_y_mm
odom_yaw_mrad
imu_yaw_mrad
imu_yaw_rate_mradps
```

이 field들은 plotting과 debugging에 유용하다.

## 12. ROS2 Expansion Path

Firmware odometry가 검증된 뒤 higher-level bridge는 다음을 publish할 수 있다.

- `nav_msgs/Odometry`
- `tf`: `odom -> base_link`
- optional `sensor_msgs/Imu`

중요:

- Frame convention과 unit이 일관되기 전에는 ROS2 odometry를 publish하지 않는다.
- ROS2 integration은 STM32 safety ownership model을 유지해야 한다.
- ROS2는 velocity를 요청할 수 있지만 STM32는 command timeout과 motor safety를 계속 소유한다.

## 13. Evidence Targets

Portfolio-quality evidence:

| Evidence | What it proves |
| --- | --- |
| Encoder sign table | Left/right direction convention이 맞음 |
| Distance scale test | Encoder count를 distance로 변환했음 |
| Rotation test | Effective track width를 tune 또는 측정했음 |
| Speed plot | Encoder speed estimate가 동작함 |
| Straight-line drift record | Mechanical/control mismatch를 인식했음 |
| IMU comparison plot | Sensor fusion path가 data 기반임 |
| Odometry formula document | Engineering model이 명시적임 |

## Final Decision

첫 model은 encoder-based differential-drive odometry를 사용한다.

이를 완벽한 position source가 아니라 practical local estimate로 취급한다.

Encoder direction, scale, control behavior가 검증된 뒤 IMU yaw comparison과 correction을 추가한다.
