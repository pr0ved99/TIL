# Trashbot Description

## Purpose

This package contains the draft `URDF/xacro` model for the trash-collecting robot.
It is the starting point for Sprint 3 robot-modeling tasks:

- link/joint structure draft
- `base_link`, wheels, `D435i`, GPS, and IMU frames
- `robot_state_publisher` and RViz2 display check

## Current Main Model

- [`urdf/trashbot.urdf.xacro`](./urdf/trashbot.urdf.xacro)

The dimensions are placeholders until the real chassis is measured. Keep the frame
names stable first, then update the numeric offsets later.

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

If the terminal does not know the local display, run:

```bash
DISPLAY="${DISPLAY:-:1}" XAUTHORITY="${XAUTHORITY:-/run/user/1000/gdm/Xauthority}" \
ros2 launch trashbot_description display.launch.py
```

## Next Edits

- Replace placeholder chassis dimensions with measured values.
- Measure `base_link -> camera_link`.
- Measure `base_link -> imu_link`.
- Decide whether `gps_link` represents receiver body or antenna phase center.
