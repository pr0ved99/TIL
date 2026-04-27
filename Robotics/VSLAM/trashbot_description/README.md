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
- Gazebo Classic can create the `mari` entity, but the full visual mesh is not visible yet.
- Treat the current Gazebo issue as a visual mesh loading/display blocker before adding diff-drive plugins.

The latest Mari visual assets are tracked separately:

- `assets/robot_model_exports/Mari.step`
- `assets/robot_model_exports/mari_visual_mesh.stl`
- `assets/robot_model_exports/onshape_urdf_exports/`
- `trashbot_description/meshes/mari_visual_mesh.stl`

## Frame Draft

- `base_footprint`: ground projection of the robot
- `base_link`: main body frame
- `left_wheel_link`, `right_wheel_link`: differential drive wheel frames
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

- Add virtual wheel links after the RViz2 TF baseline is stable.
- Verify the test path as `/cmd_vel -> /odom -> odom -> base_footprint`.
- Debug why Gazebo Classic does not display `mari_visual_mesh.stl` even though the `mari` entity is created.
- Check `gzclient --verbose` for mesh URI or resource path errors.
- Compare the Mari STL with a simple visible test mesh to separate path issues from scale/origin issues.
- Add Gazebo diff-drive plugin only after the visual baseline is visible or a simplified simulation visual is chosen.
