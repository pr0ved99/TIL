#!/usr/bin/env bash

set -euo pipefail

X="${1:-0}"
Y="${2:-0}"
Z="${3:-0}"
ROLL="${4:-0}"
PITCH="${5:-0}"
YAW="${6:-0}"
PARENT="${7:-camera_link}"
CHILD="${8:-imu_link}"

if [[ -f /opt/ros/humble/setup.bash ]]; then
  # shellcheck disable=SC1091
  set +u
  source /opt/ros/humble/setup.bash
  set -u
fi

echo "[INFO] Starting static TF publisher"
echo "[INFO] ${PARENT} -> ${CHILD}"
echo "[INFO] xyz=(${X}, ${Y}, ${Z}) rpy=(${ROLL}, ${PITCH}, ${YAW})"

exec ros2 run tf2_ros static_transform_publisher \
  "${X}" "${Y}" "${Z}" "${ROLL}" "${PITCH}" "${YAW}" "${PARENT}" "${CHILD}"
