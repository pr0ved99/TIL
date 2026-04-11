#!/usr/bin/env bash

set -eo pipefail

DETECTION_RATE="${1:-3}"

if [[ -f /opt/ros/humble/setup.bash ]]; then
  # shellcheck disable=SC1091
  source /opt/ros/humble/setup.bash
fi

set -u

echo "[INFO] Starting lightweight RTAB-Map launch"
echo "[INFO] GUI: rtabmap_viz only"
echo "[INFO] RViz is disabled to reduce load"
echo "[INFO] Image QoS is set to Best Effort"
echo "[INFO] Rtabmap/DetectionRate=${DETECTION_RATE} Hz"
echo "[INFO] Make sure D435i RGB-D launch is already running"
echo "[INFO] Approximate sync is enabled to reduce RGB/Depth timestamp mismatch drops"
echo "[INFO] Larger queues are enabled for more robust RGB-D synchronization"

exec ros2 launch rtabmap_launch rtabmap.launch.py \
  rgb_topic:=/camera/camera/color/image_raw \
  depth_topic:=/camera/camera/aligned_depth_to_color/image_raw \
  camera_info_topic:=/camera/camera/color/camera_info \
  frame_id:=camera_link \
  approx_sync:=true \
  approx_sync_max_interval:=0.02 \
  wait_imu_to_init:=false \
  qos_image:=2 \
  qos_camera_info:=2 \
  topic_queue_size:=30 \
  sync_queue_size:=30 \
  queue_size:=30 \
  rtabmap_viz:=true \
  rviz:=false \
  rtabmap_args:="--delete_db_on_start --Rtabmap/DetectionRate ${DETECTION_RATE}"
