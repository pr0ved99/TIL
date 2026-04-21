#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib_jetson_docker.sh"

PRESET_REF="light"
if [[ $# -gt 0 ]] && jetson_docker_is_preset_ref "$1"; then
  PRESET_REF="$1"
  shift
fi

jetson_docker_ensure_access
jetson_docker_prepare_env_file
jetson_docker_load_preset "${PRESET_REF}"
jetson_docker_export_defaults

DETECTION_RATE="${1:-${JETSON_RTABMAP_DETECTION_RATE}}"
ODOM_PROFILE="${2:-${JETSON_RTABMAP_ODOM_PROFILE}}"
IMU_TOPIC="${3:-${JETSON_RTABMAP_IMU_TOPIC}}"
QUEUE_SIZE="${4:-${JETSON_RTABMAP_QUEUE_SIZE}}"

export JETSON_RTABMAP_DETECTION_RATE="${DETECTION_RATE}"
export JETSON_RTABMAP_ODOM_PROFILE="${ODOM_PROFILE}"
export JETSON_RTABMAP_QUEUE_SIZE="${QUEUE_SIZE}"
export JETSON_RTABMAP_ENABLE_VIZ="false"
export JETSON_RTABMAP_WAIT_IMU_TO_INIT="true"
export JETSON_RTABMAP_IMU_TOPIC="${IMU_TOPIC}"
export JETSON_RTABMAP_ODOM_ARGS="$(jetson_docker_resolve_odom_args "${ODOM_PROFILE}")"

echo "[INFO] Starting Docker RTAB-Map stack with external IMU in detached mode"
echo "[INFO] preset=${JETSON_ACTIVE_PRESET}"
echo "[INFO] color_profile=${JETSON_CAMERA_COLOR_PROFILE}"
echo "[INFO] depth_profile=${JETSON_CAMERA_DEPTH_PROFILE}"
echo "[INFO] detection_rate=${JETSON_RTABMAP_DETECTION_RATE}"
echo "[INFO] odom_profile=${JETSON_RTABMAP_ODOM_PROFILE}"
echo "[INFO] imu_topic=${JETSON_RTABMAP_IMU_TOPIC}"
echo "[INFO] queue_size=${JETSON_RTABMAP_QUEUE_SIZE}"

jetson_docker_compose up -d --force-recreate jetson-vslam-camera
sleep 4
jetson_docker_compose up -d --force-recreate --no-deps jetson-vslam-rtabmap

echo "[INFO] Docker backend with IMU is running."
echo "[INFO] Follow logs with:"
echo "  docker compose --env-file ${JETSON_DOCKER_ENV_FILE} logs -f jetson-vslam-camera jetson-vslam-rtabmap"
echo "[INFO] Open host GUI with:"
echo "  ~/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_rtabmap_viz_from_host_for_docker.sh"
