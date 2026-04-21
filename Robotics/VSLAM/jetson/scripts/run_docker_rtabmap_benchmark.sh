#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JETSON_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BENCH_ROOT="${JETSON_DIR}/assets/benchmarks"
source "${SCRIPT_DIR}/lib_jetson_docker.sh"
source "${SCRIPT_DIR}/lib_jetson_benchmark.sh"

PRESET_REF="${1:-light}"
DURATION="${2:-}"
KEEP_RUNNING="${3:-false}"

jetson_docker_ensure_access
jetson_docker_prepare_env_file
jetson_docker_load_preset "${PRESET_REF}"
jetson_docker_export_defaults

if [[ -z "${DURATION}" ]]; then
  DURATION="${JETSON_BENCHMARK_DURATION}"
fi

export JETSON_RTABMAP_ODOM_ARGS="$(jetson_docker_resolve_odom_args "${JETSON_RTABMAP_ODOM_PROFILE}")"

STAMP="$(date +%Y-%m-%d_%H-%M-%S)"
BENCH_DIR="${BENCH_ROOT}/${STAMP}_docker_${JETSON_ACTIVE_PRESET}_baseline"
mkdir -p "${BENCH_DIR}"

cleanup() {
  if [[ "${KEEP_RUNNING}" != "true" ]]; then
    jetson_docker_compose stop jetson-vslam-camera jetson-vslam-rtabmap >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

set +u
source /opt/ros/humble/setup.bash
set -u

echo "[INFO] Starting detached Docker stack for benchmark"
jetson_docker_compose up -d --force-recreate jetson-vslam-camera
sleep 4
jetson_docker_compose up -d --force-recreate --no-deps jetson-vslam-rtabmap
sleep 6

jetson_docker_compose ps > "${BENCH_DIR}/00_compose_ps.txt"
ros2 node list > "${BENCH_DIR}/01_nodes.txt"
ros2 topic list > "${BENCH_DIR}/02_topics.txt"
timeout 10s ros2 topic echo /rtabmap/odom_info --once > "${BENCH_DIR}/03_odom_info.txt" || true

echo "[INFO] Capturing logs and metrics for ${DURATION}s"

timeout "${DURATION}s" tegrastats --interval 1000 > "${BENCH_DIR}/10_tegrastats.txt" &
pid_tegrastats=$!
timeout "${DURATION}s" bash -lc "cd '${JETSON_DOCKER_DIR}' && docker compose --env-file '${JETSON_DOCKER_ENV_FILE}' logs -f jetson-vslam-camera" > "${BENCH_DIR}/11_camera.log" &
pid_camera_log=$!
timeout "${DURATION}s" bash -lc "cd '${JETSON_DOCKER_DIR}' && docker compose --env-file '${JETSON_DOCKER_ENV_FILE}' logs -f jetson-vslam-rtabmap" > "${BENCH_DIR}/12_rtabmap.log" &
pid_rtabmap_log=$!
timeout "${DURATION}s" ros2 topic hz /camera/camera/color/image_raw > "${BENCH_DIR}/20_color_hz.txt" &
pid_color=$!
timeout "${DURATION}s" ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw > "${BENCH_DIR}/21_aligned_depth_hz.txt" &
pid_depth=$!
timeout "${DURATION}s" ros2 topic hz /rtabmap/odom > "${BENCH_DIR}/22_odom_hz.txt" &
pid_odom=$!
timeout "${DURATION}s" ros2 topic hz /rtabmap/mapData > "${BENCH_DIR}/23_mapdata_hz.txt" &
pid_mapdata=$!

wait "${pid_tegrastats}" "${pid_camera_log}" "${pid_rtabmap_log}" "${pid_color}" "${pid_depth}" "${pid_odom}" "${pid_mapdata}" || true

cat > "${BENCH_DIR}/README.md" <<EOF
# ${STAMP} Docker ${JETSON_ACTIVE_PRESET} Baseline Benchmark

## 목적

- \`Docker\` 분리 서비스 구조에서
- 현재 preset으로 \`D435i color/depth + RTAB-Map\` backend가 얼마나 가볍게 도는지
- \`tegrastats\`, \`topic hz\`, service log 기준으로 남긴다.

## 이번 실행 조건

- preset: \`${JETSON_ACTIVE_PRESET}\`
- duration: \`${DURATION}s\`
- color profile: \`${JETSON_CAMERA_COLOR_PROFILE}\`
- depth profile: \`${JETSON_CAMERA_DEPTH_PROFILE}\`
- detection rate: \`${JETSON_RTABMAP_DETECTION_RATE}\`
- odom profile: \`${JETSON_RTABMAP_ODOM_PROFILE}\`
- queue size: \`${JETSON_RTABMAP_QUEUE_SIZE}\`
- tmpfs DB/log: \`enabled\`

## 생성 파일

- \`00_compose_ps.txt\`: benchmark 당시 compose 서비스 상태
- \`01_nodes.txt\`: host에서 본 ROS node 목록
- \`02_topics.txt\`: host에서 본 ROS topic 목록
- \`03_odom_info.txt\`: 시작 시점 odom_info 샘플
- \`10_tegrastats.txt\`: Jetson 자원 사용량
- \`11_camera.log\`: camera service log
- \`12_rtabmap.log\`: rtabmap service log
- \`20_color_hz.txt\`: color image topic hz
- \`21_aligned_depth_hz.txt\`: aligned depth topic hz
- \`22_odom_hz.txt\`: /rtabmap/odom hz
- \`23_mapdata_hz.txt\`: /rtabmap/mapData hz
- \`90_summary.env\`: 자동 생성된 핵심 숫자 요약
- \`91_summary.md\`: 사람이 읽기 쉬운 자동 요약
EOF

benchmark_write_summary_env "${BENCH_DIR}" > "${BENCH_DIR}/90_summary.env"
benchmark_render_summary_markdown "${BENCH_DIR}/90_summary.env" > "${BENCH_DIR}/91_summary.md"
"${SCRIPT_DIR}/update_docker_benchmark_index.sh" >/dev/null

echo "[INFO] Benchmark saved to ${BENCH_DIR}"
echo "[INFO] Summary files:"
echo "  ${BENCH_DIR}/90_summary.env"
echo "  ${BENCH_DIR}/91_summary.md"
if [[ "${KEEP_RUNNING}" == "true" ]]; then
  echo "[INFO] Services are still running because KEEP_RUNNING=true."
fi
