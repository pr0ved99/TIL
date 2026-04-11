#!/usr/bin/env bash

set -eo pipefail

DEPTH_PROFILE="${1:-424x240x15}"

if [[ -f /opt/ros/humble/setup.bash ]]; then
  # shellcheck disable=SC1091
  source /opt/ros/humble/setup.bash
fi

set -u

echo "[INFO] Starting D435i depth-only low-bandwidth mode"
echo "[INFO] depth_profile=${DEPTH_PROFILE}"
echo "[INFO] If continuity is still poor, try: 424x240x6"
echo "[INFO] Do not run realsense-viewer or another rs_launch.py at the same time."

exec ros2 launch realsense2_camera rs_launch.py \
  enable_color:=false \
  enable_depth:=true \
  enable_gyro:=false \
  enable_accel:=false \
  pointcloud.enable:=false \
  publish_tf:=false \
  tf_publish_rate:=0.0 \
  depth_module.depth_profile:="${DEPTH_PROFILE}"
