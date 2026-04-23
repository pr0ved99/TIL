#!/usr/bin/env bash

set -euo pipefail

container_name="ros2-d435i"
image_name="ros2-d435i:humble"
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
display_value="${DISPLAY:-:0}"
x11_socket="/tmp/.X11-unix"
ros_domain_id="${ROS_DOMAIN_ID:-0}"
ros_localhost_only="${ROS_LOCALHOST_ONLY:-0}"
rmw_implementation="${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}"
ros_discovery_server="${ROS_DISCOVERY_SERVER:-}"
ros_super_client="${ROS_SUPER_CLIENT:-}"

docker_args=(
  -d
  --name "${container_name}"
  --network host
  --privileged
  --runtime nvidia
  -e "ROS_DOMAIN_ID=${ros_domain_id}"
  -e "ROS_LOCALHOST_ONLY=${ros_localhost_only}"
  -e "RMW_IMPLEMENTATION=${rmw_implementation}"
  -v /dev:/dev
  -v "${repo_root}:/workspace/VSLAM"
)

if [[ -n "${ros_discovery_server}" ]]; then
  docker_args+=(
    -e "ROS_DISCOVERY_SERVER=${ros_discovery_server}"
  )
fi

if [[ -n "${ros_super_client}" ]]; then
  docker_args+=(
    -e "ROS_SUPER_CLIENT=${ros_super_client}"
  )
fi

if [[ -d "${x11_socket}" ]]; then
  docker_args+=(
    -e "DISPLAY=${display_value}"
    -v "${x11_socket}:${x11_socket}"
  )
fi

if docker ps -a --format '{{.Names}}' | grep -qx "${container_name}"; then
  echo "[INFO] Removing existing container: ${container_name}"
  docker rm -f "${container_name}" >/dev/null
fi

docker run "${docker_args[@]}" "${image_name}" sleep infinity

echo "[OK] Container started: ${container_name}"
echo "[INFO] ROS_DOMAIN_ID=${ros_domain_id}"
echo "[INFO] ROS_LOCALHOST_ONLY=${ros_localhost_only}"
echo "[INFO] RMW_IMPLEMENTATION=${rmw_implementation}"
if [[ -n "${ros_discovery_server}" ]]; then
  echo "[INFO] ROS_DISCOVERY_SERVER=${ros_discovery_server}"
fi
if [[ -n "${ros_super_client}" ]]; then
  echo "[INFO] ROS_SUPER_CLIENT=${ros_super_client}"
fi
echo "Next:"
echo "  bash Tools/exec_ros2_d435i_container.sh"
echo "  bash Tools/check_ros2_graph_in_container.sh"
