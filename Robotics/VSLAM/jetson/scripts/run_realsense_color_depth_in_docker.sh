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

COLOR_PROFILE="${JETSON_CAMERA_COLOR_PROFILE}"
DEPTH_PROFILE="${JETSON_CAMERA_DEPTH_PROFILE}"

if [[ $# -gt 0 && "$1" != *":="* ]]; then
  COLOR_PROFILE="$1"
  shift
fi

if [[ $# -gt 0 && "$1" != *":="* ]]; then
  DEPTH_PROFILE="$1"
  shift
fi

EXTRA_ARGS=("$@")

export JETSON_CAMERA_COLOR_PROFILE="${COLOR_PROFILE}"
export JETSON_CAMERA_DEPTH_PROFILE="${DEPTH_PROFILE}"
export JETSON_CAMERA_EXTRA_ARGS="${EXTRA_ARGS[*]:-}"

jetson_docker_compose up --force-recreate jetson-vslam-camera
