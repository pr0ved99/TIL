#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib_jetson_docker.sh"

jetson_docker_ensure_access
jetson_docker_prepare_env_file

echo "[INFO] Stopping Docker RTAB-Map services"
jetson_docker_compose stop jetson-vslam-camera jetson-vslam-rtabmap
