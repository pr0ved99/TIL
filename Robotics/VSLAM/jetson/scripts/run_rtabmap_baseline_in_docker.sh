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
ENABLE_VIZ="${3:-${JETSON_RTABMAP_ENABLE_VIZ}}"
QUEUE_SIZE="${4:-${JETSON_RTABMAP_QUEUE_SIZE}}"

export JETSON_RTABMAP_DETECTION_RATE="${DETECTION_RATE}"
export JETSON_RTABMAP_ODOM_PROFILE="${ODOM_PROFILE}"
export JETSON_RTABMAP_QUEUE_SIZE="${QUEUE_SIZE}"
export JETSON_RTABMAP_ENABLE_VIZ="${ENABLE_VIZ}"
export JETSON_RTABMAP_WAIT_IMU_TO_INIT="false"
export JETSON_RTABMAP_IMU_TOPIC="/imu/disabled"
export JETSON_RTABMAP_ODOM_ARGS="$(jetson_docker_resolve_odom_args "${ODOM_PROFILE}")"

if ! jetson_docker_service_is_running "jetson-vslam-camera"; then
  echo "[WARN] jetson-vslam-camera is not running."
  echo "[WARN] start run_realsense_color_depth_in_docker.sh first, or use run_docker_rtabmap_stack.sh."
fi

jetson_docker_compose up --no-deps --force-recreate jetson-vslam-rtabmap
