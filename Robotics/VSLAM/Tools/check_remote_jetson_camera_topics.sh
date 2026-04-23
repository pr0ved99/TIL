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

echo "[INFO] ROS_DOMAIN_ID=${ROS_DOMAIN_ID}"
echo "[INFO] ROS_LOCALHOST_ONLY=${ROS_LOCALHOST_ONLY}"
echo "[INFO] RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION}"
if [[ -n "${ROS_DISCOVERY_SERVER:-}" ]]; then
  echo "[INFO] ROS_DISCOVERY_SERVER=${ROS_DISCOVERY_SERVER}"
  echo "[INFO] ROS_SUPER_CLIENT=${ROS_SUPER_CLIENT}"
fi
echo "[INFO] Checking remote Jetson camera topics from this laptop"

ros2 daemon stop || true
ros2 daemon start
sleep 2

echo "==== nodes ===="
ros2 node list || true

echo "==== camera topics ===="
ros2 topic list | grep '^/camera/camera' || {
  echo "[ERROR] No /camera/camera* topics are visible from this laptop."
  echo "[HINT] Check Jetson camera node status, network reachability, ROS_DOMAIN_ID, and ROS_LOCALHOST_ONLY."
  exit 1
}
