#!/usr/bin/env bash

set -euo pipefail

docker exec -it ros2-d435i bash -lc \
  "set +u && \
   source /opt/ros/humble/setup.bash && \
   set -u && \
   ros2 launch realsense2_camera rs_launch.py \
   enable_color:=true \
   enable_depth:=true \
   align_depth.enable:=true \
   enable_gyro:=false \
   enable_accel:=false"
