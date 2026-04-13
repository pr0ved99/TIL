#!/usr/bin/env bash

set -eo pipefail

COLOR_PROFILE="${1:-640x480x15}"
DEPTH_PROFILE="${2:-640x480x15}"
ENABLE_IMU="${3:-false}"

if [[ -f /opt/ros/humble/setup.bash ]]; then
  # shellcheck disable=SC1091
  source /opt/ros/humble/setup.bash
fi

set -u

echo "[INFO] Starting D435i RGB-D camera for mapping"
echo "[INFO] color_profile=${COLOR_PROFILE}"
echo "[INFO] depth_profile=${DEPTH_PROFILE}"
echo "[INFO] IMU enabled: ${ENABLE_IMU}"
echo "[INFO] Do not run realsense-viewer or another rs_launch.py at the same time."
echo "[INFO] For odometry stability, prefer higher FPS over very low FPS."

exec ros2 launch realsense2_camera rs_launch.py \
  enable_color:=true \
  enable_depth:=true \
  enable_gyro:="${ENABLE_IMU}" \
  enable_accel:="${ENABLE_IMU}" \
  unite_imu_method:=1 \
  enable_sync:=true \
  align_depth.enable:=true \
  pointcloud.enable:=false \
  rgb_camera.color_profile:="${COLOR_PROFILE}" \
  depth_module.depth_profile:="${DEPTH_PROFILE}"
