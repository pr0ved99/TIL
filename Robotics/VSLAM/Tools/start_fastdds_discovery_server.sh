#!/usr/bin/env bash

set -euo pipefail

set +u
source /opt/ros/humble/setup.bash
set -u

server_id="${FASTDDS_SERVER_ID:-0}"
listen_ip="${FASTDDS_SERVER_IP:-0.0.0.0}"
listen_port="${FASTDDS_SERVER_PORT:-11811}"

echo "[INFO] Starting Fast DDS Discovery Server"
echo "[INFO] server_id=${server_id}"
echo "[INFO] listen_ip=${listen_ip}"
echo "[INFO] listen_port=${listen_port}"
echo "[INFO] Use this value on both laptop and Jetson:"
echo "  export ROS_DISCOVERY_SERVER=192.168.100.62:${listen_port}"

exec fastdds discovery -i "${server_id}" -l "${listen_ip}" -p "${listen_port}"
