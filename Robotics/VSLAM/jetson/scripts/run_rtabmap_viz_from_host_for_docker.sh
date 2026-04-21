#!/usr/bin/env bash

set -euo pipefail

FRAME_ID="${1:-camera_link}"
QUEUE_SIZE="${2:-30}"
SYNC_QUEUE_SIZE="${3:-30}"

if [[ -f /opt/ros/humble/setup.bash ]]; then
  # shellcheck disable=SC1091
  set +u
  source /opt/ros/humble/setup.bash
  set -u
fi

echo "[INFO] Starting host rtabmap_viz for Docker backend"
echo "[INFO] frame_id=${FRAME_ID}"
echo "[INFO] topic_queue_size=${QUEUE_SIZE}"
echo "[INFO] sync_queue_size=${SYNC_QUEUE_SIZE}"
echo "[INFO] This viewer expects Docker backend topics on the host ROS graph"

exec ros2 run rtabmap_viz rtabmap_viz --ros-args \
  -r __ns:=/rtabmap \
  -p frame_id:="${FRAME_ID}" \
  -p subscribe_rgb:=true \
  -p subscribe_depth:=true \
  -p subscribe_odom_info:=true \
  -p approx_sync:=true \
  -p topic_queue_size:="${QUEUE_SIZE}" \
  -p sync_queue_size:="${SYNC_QUEUE_SIZE}" \
  -p qos_image:=2 \
  -p qos_camera_info:=2 \
  -r rgb/image:=/camera/camera/color/image_raw \
  -r depth/image:=/camera/camera/aligned_depth_to_color/image_raw \
  -r rgb/camera_info:=/camera/camera/color/camera_info \
  -r odom:=/rtabmap/odom \
  -r odom_info:=/rtabmap/odom_info
