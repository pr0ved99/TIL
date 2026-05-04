# Trashbot Description

## Purpose

This package contains the draft `URDF/xacro` model for the trash-collecting robot.
It is the starting point for Sprint 3 robot-modeling tasks:

- link/joint structure draft
- `base_link`, wheels, `D435i`, GPS, and IMU frames
- `robot_state_publisher` and RViz2 display check

## Current Main Model

- [`urdf/trashbot.urdf.xacro`](./urdf/trashbot.urdf.xacro)
- [`urdf/mari.urdf.xacro`](./urdf/mari.urdf.xacro)
- [`urdf/duri.urdf.xacro`](./urdf/duri.urdf.xacro)

The dimensions are placeholders until the real chassis is measured. Keep the frame
names stable first, then update the numeric offsets later.

`mari.urdf.xacro` currently uses the measured/exported chassis bounds below.

```text
base_length = 0.1776 m
base_width  = 0.1580 m
base_height = 0.0504 m
base_link_z = 0.0252 m
```

Current Mari status:

- `mari.urdf.xacro` renders with `xacro`.
- `check_urdf` parses the rendered URDF.
- RViz2 displays the Mari visual mesh and sensor frames after the visual mesh yaw/z-offset correction.
- The TF tree is verified as `base_footprint -> base_link -> chassis_link/camera_link/imu_link/gps_link`.
- `Tools/test_mari_moving_tf.py` can publish a visual motion check with `map -> odom -> base_footprint` and `/odom`.
- Gazebo Classic can create the `mari` entity with `gazebo_mari.launch.py`.
- Gazebo GUI displays both the debug box visual and the full Mari STL visual.
- Gazebo keeps four collision-only virtual track contact links for stable support,
  but `/cmd_vel` control now uses `libgazebo_ros_planar_move.so` instead of
  skid-steer wheel friction.
- `libgazebo_ros_planar_move.so` publishes `/odom` and `odom -> base_footprint`;
  real encoder and IMU topic validation should still use the hardware ROS topics
  directly.
- Gazebo publishes simulated sensor topics for the first VSLAM input baseline:
  `/imu/data`, `/gps/fix`, `/camera/camera/color/image_raw`,
  `/camera/camera/aligned_depth_to_color/image_raw`, matching
  `camera_info` topics, and `/camera/camera/depth/color/points`.
- `base_footprint -> base_link` stays at `z=0.0252 m`, the RViz2-verified
  STL chassis-center baseline. Apparent mesh alignment is handled by the
  visual offset formula `chassis_mesh_z = -base_link_z - chassis_mesh_min_z`,
  not by lowering `base_link`.

The latest Mari visual assets are tracked separately:

- `assets/robot_model_exports/Mari.step`
- `assets/robot_model_exports/mari_visual_mesh.stl`
- `assets/robot_model_exports/onshape_urdf_exports/`
- `trashbot_description/meshes/mari_visual_mesh.stl`

## Frame Draft

- `base_footprint`: ground projection of the robot
- `base_link`: main body frame
- `left_front_virtual_track_wheel_link`, `right_front_virtual_track_wheel_link`: Gazebo front contact/support approximation frames
- `left_rear_virtual_track_wheel_link`, `right_rear_virtual_track_wheel_link`: Gazebo rear contact/support approximation frames
- `left_wheel_link`, `right_wheel_link`: legacy/simple differential drive wheel frame names
- `front_caster_link`: support caster placeholder
- `camera_link`: D435i body frame
- `camera_color_optical_frame`: D435i color optical frame
- `camera_depth_optical_frame`: D435i depth optical frame
- `imu_link`: external BNO08x frame
- `gps_link`: GPS antenna/receiver placeholder frame

## Build

Install runtime dependencies if needed:

```bash
sudo apt update
sudo apt install -y \
  ros-humble-xacro \
  ros-humble-joint-state-publisher \
  ros-humble-joint-state-publisher-gui
```

Build from the VSLAM directory:

```bash
cd ~/yh_ws/TIL/Robotics/VSLAM
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select trashbot_description
source install/setup.bash
```

## Check

Render the xacro and inspect the frame tree:

```bash
xacro ~/yh_ws/TIL/Robotics/VSLAM/trashbot_description/urdf/trashbot.urdf.xacro > /tmp/trashbot.urdf
check_urdf /tmp/trashbot.urdf
```

Open RViz2:

```bash
ros2 launch trashbot_description display.launch.py
```

Open the Mari model in RViz2:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_description display.launch.py \
  model:=$(pwd)/trashbot_description/urdf/mari.urdf.xacro
```

Open the Mari model in Gazebo Classic with the stable debug visual:

Full Gazebo execution steps are collected in
[05-02_Mari_Gazebo_Run_Guide.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/learning/05-02_Mari_Gazebo_Run_Guide.md).

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch trashbot_description gazebo_mari.launch.py
```

Open the Gazebo sensor debug view in RViz2:

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
rviz2 -d trashbot_description/rviz/mari_sensor_debug.rviz
```

This RViz2 config uses `odom` as the fixed frame. If RViz2 is manually opened
with `Fixed Frame = map`, RobotModel will show transform errors until a mapping
or localization node publishes the `map` frame.
The Gazebo launch also starts `joint_state_publisher` so the four
`*_virtual_track_wheel_link` contact frames have default joint states in RViz2.

The default Gazebo launch uses `use_mesh_visual:=false`, so `chassis_link` is shown
as a simple box. This is intentional: it proves that Gazebo, spawn, TF, and the
model body are visible before debugging the heavy STL visual.

The launch uses `worlds/mari_empty.world`, which keeps the sun and ground plane
local instead of depending on Gazebo's online model database. It also gives
`spawn_entity.py` a longer service timeout to reduce startup flakiness.

The Gazebo launch passes `config/gazebo_ros.yaml` to `gzserver`. This raises
Gazebo's `/clock` publish rate from the default low-rate behavior so
`robot_localization` timers using `use_sim_time=true` are not capped near
10 Hz during `/odometry/local` tests.

Gazebo motion is intentionally controlled by `libgazebo_ros_planar_move.so`.
This makes `/cmd_vel` rotation independent from intermittent skid-steer contact
friction, while the four virtual track wheels remain collision-only support
links for the visible tracked chassis.

Retry the full Mari STL visual:

```bash
ros2 launch trashbot_description gazebo_mari.launch.py use_mesh_visual:=true
```

Use the camera test world when RGB/depth image topics are hard to inspect in an
empty scene:

```bash
ros2 launch trashbot_description gazebo_mari.launch.py \
  use_mesh_visual:=true \
  world:=$(pwd)/trashbot_description/worlds/mari_camera_test.world
```

Use the real-time-first Gazebo profile when RTAB-Map processing is stuttering.
This keeps the camera useful for RGB-D mapping, but reduces render and image
transport load:

```bash
ros2 launch trashbot_description gazebo_mari.launch.py \
  use_mesh_visual:=false \
  sim_camera_width:=424 \
  sim_camera_height:=240 \
  sim_camera_update_rate:=10 \
  sim_camera_visualize:=false \
  world:=$(pwd)/trashbot_description/worlds/mari_camera_test.world
```

Use the RealSense-light matched profile when comparing Gazebo against the
previous D435i RTAB-Map baseline:

```bash
ros2 launch trashbot_description gazebo_mari_realsense_light.launch.py
ros2 launch trashbot_description mari_rtabmap_realsense_light.launch.py
```

That profile uses `424x240x15`, `DetectionRate=2`, queue size `15`, and
`rtabmap_viz=true` for visible mapping feedback. Use `rtabmap_viz:=false`
only for pure backend benchmarking.

Use the park world when the camera test world is too simple for RTAB-Map
inspection:

```bash
ros2 launch trashbot_description gazebo_mari_park_realsense_light.launch.py
ros2 launch trashbot_description mari_rtabmap_realsense_light.launch.py \
  detection_rate:=3 \
  queue_size:=20 \
  approx_sync_max_interval:=0.08 \
  rtabmap_viz:=true
```

The park world keeps the low-load RealSense-light camera profile but replaces
the simple test targets with grass, walking paths, trees, benches, signs, low
walls, and rocks.

Use the larger park world when checking longer teleop paths, loop-like walking
routes, and richer landmark coverage:

```bash
ros2 launch trashbot_description gazebo_mari_large_park_realsense_light.launch.py
```

The larger world keeps the same low-load camera defaults, but expands the scene
with a wider ground plane, longer paths, a small plaza, tree rows, benches,
colored signs, playground blocks, flower beds, rocks, and boundary fences.

## Nav2 Training Worlds

Use these worlds before running Nav2 in the larger park. They keep the same
Mari Gazebo base launch and RealSense-light camera profile, but reduce the
environment complexity so navigation failures can be isolated.

```bash
# Stage 0: basic /cmd_vel smoke test
ros2 launch trashbot_description gazebo_mari_nav2_stage0_empty.launch.py

# Stage 1: straight path tracking
ros2 launch trashbot_description gazebo_mari_nav2_stage1_straight_path.launch.py

# Stage 2: simple obstacle/costmap test
ros2 launch trashbot_description gazebo_mari_nav2_stage2_obstacles.launch.py

# Stage 3: small loop park integration test
ros2 launch trashbot_description gazebo_mari_nav2_stage3_small_loop.launch.py

# Stage 4: close-obstacle repeat-course test
ros2 launch trashbot_description gazebo_mari_nav2_stage4_repeat_course.launch.py
```

The larger park remains the demo/final validation world:

```bash
ros2 launch trashbot_description gazebo_mari_large_park_realsense_light.launch.py
```

Use the local-odom variant when checking the sensor-style odometry path with the
same real-time mapping profile:

```bash
ros2 launch trashbot_description gazebo_mari_realsense_light.launch.py
ros2 launch trashbot_description mari_rtabmap_realsense_light_local_odom.launch.py
```

This keeps Gazebo `/odom` only as the mock encoder source, then feeds RTAB-Map
with `/odometry/local`. The default Gazebo local-odom EKF uses
`ekf_local_gazebo_encoder_only.yaml` to avoid over-trusting the simulated IMU
gyro covariance during rotation. The mock encoder bridge derives ticks from
Gazebo pose deltas so yaw follows the visible Gazebo rotation more closely than
twist-only integration.

Drive Mari directly from the keyboard:

```bash
python3 Tools/teleop_mari_keyboard.py
```

Run Gazebo and teleop in separate terminals. Keep the teleop terminal focused
while pressing keys; Gazebo is the visual feedback window. Use `w/s/a/d` or the
arrow keys to move, `q/e/z/c` for arc turns, `space` or `x` to stop, `r/f` to
change linear speed, and `t/g` to change angular speed. The script publishes
`geometry_msgs/Twist` to `/cmd_vel` and automatically sends zero velocity if no
movement key is received for a short timeout.

If the Gazebo window has keyboard focus, Gazebo consumes the key events before
this script can read them. Click or focus the teleop terminal before driving.

For smoother visual motion, use a higher publish rate with lower acceleration:

```bash
python3 Tools/teleop_mari_keyboard.py \
  --rate 60 \
  --key-timeout 1.2
```

The keyboard teleop defaults to step command mode, so movement keys publish the
target velocity immediately. Add `--smooth --linear-accel ... --angular-accel ...`
only when a ramped command is desired.

Drive Mari in Gazebo with `/cmd_vel`:

```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.12}, angular: {z: 0.0}}"
```

Rotate Mari in Gazebo:

```bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.5}}"
```

Stop command:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

Check odom:

```bash
ros2 topic echo /odom --once
ros2 run tf2_ros tf2_echo odom base_footprint
```

Check Gazebo simulated sensor topics:

```bash
python3 Tools/check_mari_gazebo_sensor_topics.py
```

Start RTAB-Map with the Mari Gazebo defaults:

```bash
ros2 launch trashbot_description mari_rtabmap.launch.py
```

This wraps the longer generic `rtabmap_launch` command with Mari's RGB-D,
`/odom`, `base_footprint`, simulation time, QoS, and `DetectionRate=5`
defaults. It also uses a Gazebo-stable mapping profile by default:
`Optimizer/Strategy=1` (`g2o`), planar 3DoF registration, no gravity constraint,
and no spatial proximity links. Override values only when a specific experiment
needs it:

```bash
ros2 launch trashbot_description mari_rtabmap.launch.py detection_rate:=3
ros2 launch trashbot_description mari_rtabmap.launch.py optimizer_strategy:=2
```

Check RTAB-Map input and output topics:

```bash
python3 Tools/check_mari_rtabmap_topics.py
python3 Tools/check_mari_rtabmap_topics.py --all-stats --max-stats 80
```

Start RTAB-Map with the local EKF odometry input:

```bash
ros2 launch trashbot_description mari_rtabmap_local_odom.launch.py
```

This starts the Gazebo encoder bridge, local EKF, and RTAB-Map together after
Gazebo is already running. RTAB-Map consumes `/odometry/local` instead of raw
Gazebo `/odom`.

```bash
python3 Tools/check_mari_rtabmap_topics.py --odom-topic /odometry/local
```

Start RTAB-Map with the encoder + BNO08x-like IMU local EKF candidate:

```bash
ros2 launch trashbot_description mari_rtabmap_realsense_light_encoder_imu.launch.py
```

This keeps the RealSense-light RTAB-Map profile, but changes the local EKF path:

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

`/imu/data_bno08x_like` is still simulated data. It exists to avoid over-trusting
Gazebo's near-zero IMU covariance before the real BNO08x is connected.

After EKF/Gazebo clock tuning, save the retest with a new report name instead
of overwriting the first local-odom baseline:

```bash
python3 Tools/check_mari_rtabmap_topics.py \
  --duration 20 \
  --label local_odom_tuned \
  --odom-topic /odometry/local \
  --output-json assets/2026-04-29_mari_rtabmap_odom_mode_compare/03_local_odom_tuned_rtabmap_check.json \
  --output-md assets/2026-04-29_mari_rtabmap_odom_mode_compare/03_local_odom_tuned_rtabmap_check.md
```

When real Mari hardware is connected, discover likely encoder, wheel, motor,
joint, and odom feedback topics before writing an adapter:

```bash
python3 Tools/check_mari_encoder_topics.py
python3 Tools/check_mari_encoder_topics.py --all-topics --duration 3
```

The intended motor encoder contract is:

```text
/motor/encoder_ticks  std_msgs/Int64MultiArray  [left_ticks, right_ticks]
```

Test the raw encoder contract and `/wheel/odometry` conversion without hardware:

```bash
ros2 launch trashbot_localization mari_encoder_odom_mock.launch.py
ros2 topic echo /motor/encoder_ticks --once
ros2 topic echo /wheel/odometry --once
```

When the real motor driver publishes `/motor/encoder_ticks`, run only the
adapter:

```bash
ros2 launch trashbot_localization mari_encoder_odom.launch.py
```

Before the real encoder is connected, use Gazebo `/odom` as mock wheel odom:

```bash
ros2 launch trashbot_localization mari_wheel_odom_mock.launch.py
ros2 topic echo /wheel/odometry --once
```

If `robot_localization` is installed, the local EKF scaffold can also publish
`/odometry/local`:

```bash
ros2 launch trashbot_localization mari_ekf_local.launch.py
```

Expected first baseline topics:

```text
/odom                                             nav_msgs/Odometry
/imu/data                                         sensor_msgs/Imu
/gps/fix                                          sensor_msgs/NavSatFix
/camera/camera/color/image_raw                    sensor_msgs/Image
/camera/camera/aligned_depth_to_color/image_raw   sensor_msgs/Image
/camera/camera/color/camera_info                  sensor_msgs/CameraInfo
/camera/camera/aligned_depth_to_color/camera_info sensor_msgs/CameraInfo
/camera/camera/depth/color/points                 sensor_msgs/PointCloud2
```

The simulated camera uses `camera_color_optical_frame` as the image frame. The
simulated IMU uses `imu_link` as the IMU frame. The Gazebo GPS plugin currently
publishes `/gps/fix` with `frame_id=base_footprint`; this is enough for value
reception checks, but GPS antenna lever-arm testing needs a later `gps_link`
frame correction or republish.

If the terminal does not know the local display, run:

```bash
DISPLAY="${DISPLAY:-:1}" XAUTHORITY="${XAUTHORITY:-/run/user/1000/gdm/Xauthority}" \
ros2 launch trashbot_description display.launch.py
```

Mari variant with explicit display variables:

```bash
DISPLAY="${DISPLAY:-:1}" XAUTHORITY="${XAUTHORITY:-/run/user/1000/gdm/Xauthority}" \
ros2 launch trashbot_description display.launch.py \
  model:=$(pwd)/trashbot_description/urdf/mari.urdf.xacro
```

Check the current TF tree:

```bash
ros2 run tf2_tools view_frames
```

Run a simple RViz2 motion check:

```bash
python3 Tools/test_mari_moving_tf.py
```

For the motion check, set RViz2 as follows:

```text
Global Options > Fixed Frame = map
Views > Current View > Target Frame = map
```

The script publishes:

```text
map -> odom -> base_footprint -> base_link
/odom
```

Run a `/cmd_vel` based odom check:

```bash
python3 Tools/test_mari_cmd_vel_odom.py
```

In another terminal, publish a forward command:

```bash
source /opt/ros/humble/setup.bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.15}, angular: {z: 0.0}}"
```

Rotation command:

```bash
source /opt/ros/humble/setup.bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.5}}"
```

This test subscribes to `/cmd_vel`, integrates a simple 2D pose, and publishes
`/odom` plus `odom -> base_footprint`.

## Next Edits

- Restart Gazebo, then drive Mari from `Tools/teleop_mari_keyboard.py` in GUI with `use_mesh_visual:=true`.
- Confirm `/odom` and `odom -> base_footprint` stay continuous while using the `planar_move` controller.
- Connect the simulated RGB-D/IMU topics to the next VSLAM smoke test, then validate the matching real hardware ROS topics.
