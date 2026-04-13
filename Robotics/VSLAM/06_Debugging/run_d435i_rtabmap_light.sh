#!/usr/bin/env bash

set -eo pipefail

DETECTION_RATE="${1:-3}"
ODOM_PROFILE="${2:-relaxed}"
ENABLE_IMU="${3:-false}"

if [[ -f /opt/ros/humble/setup.bash ]]; then
  # shellcheck disable=SC1091
  source /opt/ros/humble/setup.bash
fi

set -u

case "${ODOM_PROFILE}" in
  flow)
    echo "[WARN] 'flow' profile is kept as a backward-compatible alias."
    echo "[WARN] OdometryF2M does not support Vis/CorType=1, so this falls back to relaxed feature matching."
    ODOM_ARGS="--Vis/CorType 0 --Vis/MinInliers 10 --Vis/MaxFeatures 1500"
    ;;
  relaxed)
    # Start-up friendly feature matching profile. This is the most practical
    # default when verifying D435i RGB-D odometry by hand.
    ODOM_ARGS="--Vis/CorType 0 --Vis/MinInliers 10 --Vis/MaxFeatures 1500"
    ;;
  feature)
    ODOM_ARGS="--Vis/CorType 0 --Vis/MinInliers 15 --Vis/MaxFeatures 1200"
    ;;
  *)
    echo "[ERROR] Unsupported odom profile: ${ODOM_PROFILE}"
    echo "[ERROR] Supported profiles: relaxed, feature, flow"
    exit 1
    ;;
esac

echo "[INFO] Starting lightweight RTAB-Map launch"
echo "[INFO] GUI: rtabmap_viz only"
echo "[INFO] RViz is disabled to reduce load"
echo "[INFO] Image QoS is set to Best Effort"
echo "[INFO] Rtabmap/DetectionRate=${DETECTION_RATE} Hz"
echo "[INFO] Odometry profile=${ODOM_PROFILE}"
echo "[INFO] Make sure D435i RGB-D launch is already running"
echo "[INFO] Approximate sync is enabled to reduce RGB/Depth timestamp mismatch drops"
echo "[INFO] Larger queues are enabled for more robust RGB-D synchronization"
echo "[INFO] odom_args=${ODOM_ARGS}"
echo "[INFO] IMU enabled: ${ENABLE_IMU}"

if [[ "${ENABLE_IMU}" == "true" ]]; then
  IMU_ARGS="imu_topic:=/camera/camera/imu wait_imu_to_init:=true"
else
  IMU_ARGS="wait_imu_to_init:=false"
fi

exec ros2 launch rtabmap_launch rtabmap.launch.py \
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
