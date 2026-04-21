#!/usr/bin/env bash

set -euo pipefail

DETECTION_RATE="${1:-2}"
ODOM_PROFILE="${2:-relaxed}"
IMU_TOPIC="${3:-/imu/data}"

if [[ -f /opt/ros/humble/setup.bash ]]; then
  # shellcheck disable=SC1091
  set +u
  source /opt/ros/humble/setup.bash
  set -u
fi

case "${ODOM_PROFILE}" in
  relaxed)
    ODOM_ARGS="--Vis/CorType 0 --Vis/MinInliers 10 --Vis/MaxFeatures 1500"
    ;;
  feature)
    ODOM_ARGS="--Vis/CorType 0 --Vis/MinInliers 15 --Vis/MaxFeatures 1200"
    ;;
  *)
    echo "[ERROR] Unsupported odom profile: ${ODOM_PROFILE}"
    echo "[ERROR] Supported profiles: relaxed, feature"
    exit 1
    ;;
esac

echo "[INFO] Starting RTAB-Map with external IMU"
echo "[INFO] DetectionRate=${DETECTION_RATE} Hz"
echo "[INFO] Odometry profile=${ODOM_PROFILE}"
echo "[INFO] IMU topic=${IMU_TOPIC}"
echo "[INFO] frame_id=camera_link"
echo "[INFO] Make sure D435i color/depth is already running"
echo "[INFO] Make sure /imu/data publisher and static TF camera_link->imu_link are already running"

exec ros2 launch rtabmap_launch rtabmap.launch.py \
  rgb_topic:=/camera/camera/color/image_raw \
  depth_topic:=/camera/camera/aligned_depth_to_color/image_raw \
  camera_info_topic:=/camera/camera/color/camera_info \
  imu_topic:="${IMU_TOPIC}" \
  wait_imu_to_init:=true \
  frame_id:=camera_link \
  approx_sync:=true \
  approx_sync_max_interval:=0.05 \
  qos_image:=2 \
  qos_camera_info:=2 \
  topic_queue_size:=30 \
  sync_queue_size:=30 \
  queue_size:=30 \
  odom_args:="${ODOM_ARGS}" \
  rtabmap_viz:=true \
  rviz:=false \
  rtabmap_args:="--delete_db_on_start --Rtabmap/DetectionRate ${DETECTION_RATE}"
