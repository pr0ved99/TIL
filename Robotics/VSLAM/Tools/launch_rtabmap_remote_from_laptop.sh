#!/usr/bin/env bash

set -euo pipefail

set +u
source /opt/ros/humble/setup.bash
set -u

export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}"
export ROS_LOCALHOST_ONLY=0
export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}"
if [[ -n "${ROS_DISCOVERY_SERVER:-}" ]]; then
  export ROS_SUPER_CLIENT="${ROS_SUPER_CLIENT:-TRUE}"
fi

DETECTION_RATE="${DETECTION_RATE:-3}"
ODOM_PROFILE="${ODOM_PROFILE:-relaxed}"
ENABLE_IMU="${ENABLE_IMU:-false}"

case "${ODOM_PROFILE}" in
  flow)
    echo "[WARN] 'flow' profile is treated as a backward-compatible alias."
    echo "[WARN] OdometryF2M does not support Vis/CorType=1, so relaxed matching is used."
    ODOM_ARGS='--Vis/CorType 0 --Vis/MinInliers 10 --Vis/MaxFeatures 1500'
    ;;
  relaxed)
    ODOM_ARGS='--Vis/CorType 0 --Vis/MinInliers 10 --Vis/MaxFeatures 1500'
    ;;
  feature)
    ODOM_ARGS='--Vis/CorType 0 --Vis/MinInliers 15 --Vis/MaxFeatures 1200'
    ;;
  *)
    echo "[ERROR] Unsupported odom profile: ${ODOM_PROFILE}"
    exit 1
    ;;
esac

if [[ "${ENABLE_IMU}" == "true" ]]; then
  IMU_ARGS='imu_topic:=/camera/camera/imu wait_imu_to_init:=true'
else
  IMU_ARGS='wait_imu_to_init:=false'
fi

echo "[INFO] ROS_DOMAIN_ID=${ROS_DOMAIN_ID}"
echo "[INFO] ROS_LOCALHOST_ONLY=${ROS_LOCALHOST_ONLY}"
echo "[INFO] RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION}"
if [[ -n "${ROS_DISCOVERY_SERVER:-}" ]]; then
  echo "[INFO] ROS_DISCOVERY_SERVER=${ROS_DISCOVERY_SERVER}"
  echo "[INFO] ROS_SUPER_CLIENT=${ROS_SUPER_CLIENT}"
fi
echo "[INFO] Starting RTAB-Map on laptop using Jetson camera topics"
echo "[INFO] Detection rate=${DETECTION_RATE} Hz"
echo "[INFO] Odometry profile=${ODOM_PROFILE}"
echo "[INFO] IMU enabled=${ENABLE_IMU}"
echo "[INFO] First make sure Jetson Docker container is already publishing D435i topics"

if ! ros2 topic list | grep -q '^/camera/camera'; then
  echo "[ERROR] No Jetson camera topics are visible from this laptop."
  echo "[HINT] Run Tools/check_remote_jetson_camera_topics.sh first."
  exit 1
fi

eval ros2 launch rtabmap_launch rtabmap.launch.py \
  rgb_topic:=/camera/camera/color/image_raw \
  depth_topic:=/camera/camera/aligned_depth_to_color/image_raw \
  camera_info_topic:=/camera/camera/color/camera_info \
  frame_id:=camera_link \
  approx_sync:=true \
  approx_sync_max_interval:=0.05 \
  ${IMU_ARGS} \
  qos_image:=2 \
  qos_camera_info:=2 \
  topic_queue_size:=30 \
  sync_queue_size:=30 \
  queue_size:=30 \
  odom_args:="${ODOM_ARGS}" \
  rtabmap_viz:=true \
  rviz:=false \
  rtabmap_args:="--delete_db_on_start --Rtabmap/DetectionRate ${DETECTION_RATE}"
