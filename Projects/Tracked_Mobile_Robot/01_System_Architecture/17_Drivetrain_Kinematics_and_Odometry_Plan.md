# Drivetrain Kinematics and Odometry Plan

## Purpose

This document defines the first kinematics and odometry plan for the tracked
mobile robot.

The robot uses a left/right tracked drivetrain. For low-speed control and first
odometry, it can be treated like a differential-drive robot: left and right
tracks move at different speeds to create forward motion and rotation.

This document answers:

- How a command velocity becomes left/right track commands
- How encoder counts become distance and speed estimates
- How odometry is integrated over time
- Where IMU data can be added later
- What limitations exist for tracked vehicle odometry
- What tests prove the odometry model is usable

## Architecture Decision

Use a differential-drive approximation for the first tracked drivetrain model.

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

Core decision:

```text
Use encoder-based differential odometry first.
Add IMU yaw-rate correction later after the drivetrain and encoder signs are stable.
```

## 1. Terms

| Term | Meaning in this project |
| --- | --- |
| Kinematics | Relationship between robot motion and left/right track motion |
| Odometry | Estimating robot movement from wheel or track encoder data |
| Track width | Effective distance between left and right contact lines |
| Encoder count | Tick count measured from motor or wheel encoder |
| Counts per revolution | Encoder counts for one shaft or output revolution |
| Distance per count | Linear travel estimate represented by one encoder count |
| Yaw | Robot heading angle around the vertical axis |
| Slip | Track movement that does not become actual ground movement |

## 2. Coordinate Convention

Use the common mobile robot body convention:

```text
x axis: forward
y axis: left
z axis: up
positive yaw: counter-clockwise turn when viewed from above
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

Encoder sign must be adjusted so this convention is true.

## 3. Differential Drive Approximation

Let:

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

- Same left/right speed -> straight motion.
- Right faster than left -> left turn.
- Left faster than right -> right turn.
- Opposite signs -> in-place rotation candidate.

## 4. Encoder Distance Model

For each side:

```text
distance_per_count = output_circumference / counts_per_output_rev
distance = delta_count * distance_per_count
```

Where:

- `output_circumference` is the effective sprocket or track driving
  circumference.
- `counts_per_output_rev` must include encoder resolution and gearbox ratio if
  the encoder is on the motor shaft.

Open parameters to measure:

| Parameter | How to obtain |
| --- | --- |
| Encoder counts per motor revolution | Motor/encoder datasheet or bench measurement |
| Gear ratio | Motor model datasheet or manual count test |
| Output sprocket circumference | Measure or infer from track movement |
| Effective track width | Measure from chassis, tune with rotation test |
| Encoder sign | Confirm by low-speed forward command |

Do not assume the nominal motor label gives enough information for accurate
odometry.

## 5. Speed Estimation

At each control period:

```text
delta_count = current_count - previous_count
distance_m = delta_count * distance_per_count_m
speed_mps = distance_m / dt_s
```

Initial filtering:

- Use raw speed first during bench validation.
- Add simple moving average or low-pass filtering only after confirming sign
  and scale.
- Keep filtered and raw values visible in debug logs if possible.

Why filtering matters:

- Encoder counts are discrete.
- Low-speed motion may produce sparse ticks.
- Motor and track vibration can create noisy speed estimates.

## 6. Odometry Integration

At each odometry update:

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

Use radians internally.

Initial update rate:

```text
50 Hz to 100 Hz
```

The same 100 Hz motor loop can compute basic odometry, or odometry can be a
separate lower-priority task after FreeRTOS is introduced.

## 7. Tracked Vehicle Limitations

Tracked robots have more slip than ideal wheeled differential-drive robots.

Common error sources:

- Track slip during turns
- Track deformation
- Uneven floor friction
- Different left/right motor response
- Encoder mounted before gearbox
- Backlash or mechanical looseness
- Load-dependent current and speed changes

Implication:

Encoder-only odometry is useful for short-term motion estimation, but it should
not be treated as globally accurate position.

## 8. IMU Fusion Path

BNO08x IMU can improve heading behavior later.

First IMU uses:

- Compare encoder yaw rate with IMU yaw rate.
- Detect large slip during turns.
- Use IMU yaw as a heading correction candidate.
- Publish yaw or yaw-rate telemetry.

Do not start with complex sensor fusion.

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

Only use this after time alignment, axis convention, and IMU orientation are
verified.

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

- Start with open-loop low PWM.
- Use encoder counts only for observation.
- Add speed estimation.
- Add proportional control after encoder signs and scale are reliable.
- Add PID only after P control behavior is understood.

## 10. Calibration Tests

### Test 1: Encoder Sign Test

Procedure:

- Lift tracks.
- Command low forward speed.
- Check left and right encoder count direction.

Expected:

- Both sides increase for forward command.

### Test 2: Distance Scale Test

Procedure:

- Mark floor start position.
- Command a short straight motion.
- Measure actual travel distance.
- Compare with encoder-estimated distance.

Expected:

- Scale error is measured and documented.

### Test 3: Rotation Scale Test

Procedure:

- Command slow in-place rotation.
- Measure actual yaw change.
- Compare with odometry yaw.

Expected:

- Effective track width can be tuned.

### Test 4: Straight-Line Drift Test

Procedure:

- Command straight motion.
- Record left/right encoder speeds.
- Observe whether robot veers left or right.

Expected:

- Motor mismatch and track friction are identified.

### Test 5: IMU Comparison Test

Procedure:

- Rotate slowly.
- Compare encoder yaw rate and IMU yaw rate.

Expected:

- IMU axis and sign are validated before fusion.

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

These fields are useful for plotting and debugging.

## 12. ROS2 Expansion Path

After firmware odometry is validated, a higher-level bridge can publish:

- `nav_msgs/Odometry`
- `tf`: `odom -> base_link`
- optional `sensor_msgs/Imu`

Important:

- Do not publish ROS2 odometry until frame convention and units are consistent.
- ROS2 integration should preserve the STM32 safety ownership model.
- ROS2 may request velocity, but STM32 still owns command timeout and motor
  safety.

## 13. Evidence Targets

Portfolio-quality evidence:

| Evidence | What it proves |
| --- | --- |
| Encoder sign table | Correct left/right direction convention |
| Distance scale test | Encoder counts converted into distance |
| Rotation test | Effective track width tuned or measured |
| Speed plot | Encoder speed estimate works |
| Straight-line drift record | Mechanical and control mismatch recognized |
| IMU comparison plot | Sensor fusion path is grounded in data |
| Odometry formula document | Engineering model is explicit |

## Final Decision

Use encoder-based differential-drive odometry as the first model.

Treat it as a practical local estimate, not a perfect position source.

Add IMU yaw comparison and correction only after encoder direction, scale, and
control behavior are validated.
