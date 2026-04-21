#!/usr/bin/env bash

set -euo pipefail

JETSON_DOCKER_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JETSON_DOCKER_DIR="$(cd "${JETSON_DOCKER_SCRIPT_DIR}/../docker" && pwd)"
JETSON_DOCKER_ENV_FILE="${JETSON_DOCKER_DIR}/.env"
JETSON_DOCKER_ENV_EXAMPLE="${JETSON_DOCKER_DIR}/.env.example"
JETSON_DOCKER_TIL_ROOT="$(cd "${JETSON_DOCKER_SCRIPT_DIR}/../../../.." && pwd)"
JETSON_DOCKER_WS_ROOT="$(dirname "${JETSON_DOCKER_TIL_ROOT}")"

jetson_docker_upsert_env_key() {
  local key="$1"
  local value="$2"
  local file="$3"
  if grep -q "^${key}=" "${file}"; then
    sed -i "s|^${key}=.*|${key}=${value}|" "${file}"
  else
    printf '%s=%s\n' "${key}" "${value}" >> "${file}"
  fi
}

jetson_docker_ensure_access() {
  if ! docker info >/dev/null 2>&1; then
    echo "[ERROR] docker daemon access is not ready."
    echo "[ERROR] run guides/08_Jetson_Docker_Enablement_Guide.md first."
    exit 1
  fi
}

jetson_docker_prepare_env_file() {
  if [[ ! -f "${JETSON_DOCKER_ENV_FILE}" ]]; then
    cp "${JETSON_DOCKER_ENV_EXAMPLE}" "${JETSON_DOCKER_ENV_FILE}"
  fi

  local i2c_gid="116"
  if getent group i2c >/dev/null 2>&1; then
    i2c_gid="$(getent group i2c | cut -d: -f3)"
  fi
  local video_gid="44"
  if getent group video >/dev/null 2>&1; then
    video_gid="$(getent group video | cut -d: -f3)"
  fi
  local render_gid="104"
  if getent group render >/dev/null 2>&1; then
    render_gid="$(getent group render | cut -d: -f3)"
  fi

  jetson_docker_upsert_env_key "UID" "$(id -u)" "${JETSON_DOCKER_ENV_FILE}"
  jetson_docker_upsert_env_key "GID" "$(id -g)" "${JETSON_DOCKER_ENV_FILE}"
  jetson_docker_upsert_env_key "USER_NAME" "$(id -un)" "${JETSON_DOCKER_ENV_FILE}"
  jetson_docker_upsert_env_key "DISPLAY" "${DISPLAY:-:0}" "${JETSON_DOCKER_ENV_FILE}"
  jetson_docker_upsert_env_key "HOST_TIL_ROOT" "${JETSON_DOCKER_TIL_ROOT}" "${JETSON_DOCKER_ENV_FILE}"
  jetson_docker_upsert_env_key "HOST_WS_ROOT" "${JETSON_DOCKER_WS_ROOT}" "${JETSON_DOCKER_ENV_FILE}"
  jetson_docker_upsert_env_key "HOST_I2C_GID" "${i2c_gid}" "${JETSON_DOCKER_ENV_FILE}"
  jetson_docker_upsert_env_key "HOST_VIDEO_GID" "${video_gid}" "${JETSON_DOCKER_ENV_FILE}"
  jetson_docker_upsert_env_key "HOST_RENDER_GID" "${render_gid}" "${JETSON_DOCKER_ENV_FILE}"
  jetson_docker_upsert_env_key "ROS_DISTRO" "humble" "${JETSON_DOCKER_ENV_FILE}"
  jetson_docker_upsert_env_key "ROS_DOMAIN_ID" "${ROS_DOMAIN_ID:-0}" "${JETSON_DOCKER_ENV_FILE}"
  jetson_docker_upsert_env_key "COMPOSE_PROJECT_NAME" "jetson-vslam" "${JETSON_DOCKER_ENV_FILE}"
  jetson_docker_upsert_env_key "JETSON_DEFAULT_PRESET" "light" "${JETSON_DOCKER_ENV_FILE}"
  jetson_docker_upsert_env_key "JETSON_TMPFS_TMP_SIZE" "1024m" "${JETSON_DOCKER_ENV_FILE}"
  jetson_docker_upsert_env_key "JETSON_TMPFS_VAR_SIZE" "256m" "${JETSON_DOCKER_ENV_FILE}"
  jetson_docker_upsert_env_key "JETSON_RTABMAP_IMU_TOPIC" "/imu/disabled" "${JETSON_DOCKER_ENV_FILE}"
}

jetson_docker_is_preset_ref() {
  local ref="${1:-}"
  [[ -n "${ref}" ]] && {
    [[ -f "${ref}" ]] || [[ -f "${JETSON_DOCKER_DIR}/presets/${ref}.env" ]]
  }
}

jetson_docker_load_preset() {
  local ref="${1:-light}"
  local preset_file="${ref}"

  if [[ ! -f "${preset_file}" ]]; then
    preset_file="${JETSON_DOCKER_DIR}/presets/${ref}.env"
  fi

  if [[ ! -f "${preset_file}" ]]; then
    echo "[ERROR] preset file not found: ${ref}"
    echo "[ERROR] available presets: light, medium, compare"
    exit 1
  fi

  # shellcheck disable=SC1090
  source "${preset_file}"
  export JETSON_ACTIVE_PRESET="$(basename "${preset_file}" .env)"
}

jetson_docker_resolve_odom_args() {
  local profile="${1:-relaxed}"
  case "${profile}" in
    relaxed)
      printf '%s' "--Vis/CorType 0 --Vis/MinInliers 10 --Vis/MaxFeatures 1500"
      ;;
    feature)
      printf '%s' "--Vis/CorType 0 --Vis/MinInliers 15 --Vis/MaxFeatures 1200"
      ;;
    flow)
      printf '%s' "--Vis/CorType 0 --Vis/MinInliers 10 --Vis/MaxFeatures 1500"
      ;;
    *)
      echo "[ERROR] Unsupported odom profile: ${profile}" >&2
      echo "[ERROR] Supported profiles: relaxed, feature, flow" >&2
      exit 1
      ;;
  esac
}

jetson_docker_export_defaults() {
  export JETSON_CAMERA_COLOR_PROFILE="${JETSON_CAMERA_COLOR_PROFILE:-424x240x15}"
  export JETSON_CAMERA_DEPTH_PROFILE="${JETSON_CAMERA_DEPTH_PROFILE:-${JETSON_CAMERA_COLOR_PROFILE}}"
  export JETSON_CAMERA_ENABLE_GYRO="${JETSON_CAMERA_ENABLE_GYRO:-false}"
  export JETSON_CAMERA_ENABLE_ACCEL="${JETSON_CAMERA_ENABLE_ACCEL:-false}"
  export JETSON_CAMERA_EXTRA_ARGS="${JETSON_CAMERA_EXTRA_ARGS:-}"

  export JETSON_RTABMAP_DETECTION_RATE="${JETSON_RTABMAP_DETECTION_RATE:-2}"
  export JETSON_RTABMAP_ODOM_PROFILE="${JETSON_RTABMAP_ODOM_PROFILE:-relaxed}"
  export JETSON_RTABMAP_QUEUE_SIZE="${JETSON_RTABMAP_QUEUE_SIZE:-15}"
  export JETSON_RTABMAP_ENABLE_VIZ="${JETSON_RTABMAP_ENABLE_VIZ:-false}"
  export JETSON_RTABMAP_WAIT_IMU_TO_INIT="${JETSON_RTABMAP_WAIT_IMU_TO_INIT:-false}"
  export JETSON_RTABMAP_IMU_TOPIC="${JETSON_RTABMAP_IMU_TOPIC:-/imu/disabled}"
  export JETSON_RTABMAP_APPROX_SYNC_MAX_INTERVAL="${JETSON_RTABMAP_APPROX_SYNC_MAX_INTERVAL:-0.05}"
  export JETSON_RTABMAP_EXTRA_ARGS="${JETSON_RTABMAP_EXTRA_ARGS:-}"
  export JETSON_RTABMAP_ODOM_ARGS="${JETSON_RTABMAP_ODOM_ARGS:-$(jetson_docker_resolve_odom_args "${JETSON_RTABMAP_ODOM_PROFILE}")}"

  export JETSON_BENCHMARK_DURATION="${JETSON_BENCHMARK_DURATION:-20}"
}

jetson_docker_compose() {
  (cd "${JETSON_DOCKER_DIR}" && docker compose --env-file "${JETSON_DOCKER_ENV_FILE}" "$@")
}

jetson_docker_service_is_running() {
  local service="$1"
  jetson_docker_compose ps --status running --services | grep -qx "${service}"
}
