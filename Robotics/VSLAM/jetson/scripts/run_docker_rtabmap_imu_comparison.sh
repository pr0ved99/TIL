#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JETSON_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BENCH_ROOT="${JETSON_DIR}/assets/benchmarks"
source "${SCRIPT_DIR}/lib_jetson_docker.sh"
source "${SCRIPT_DIR}/lib_jetson_benchmark.sh"

MODE="${1:-both}"
PRESET_REF="${2:-light}"
DURATION="${3:-}"
KEEP_RUNNING="${4:-false}"

case "${MODE}" in
  off | on | both) ;;
  *)
    echo "[ERROR] mode must be one of: off, on, both"
    echo "[ERROR] usage: $0 [off|on|both] [preset] [duration_seconds] [keep_running]"
    exit 1
    ;;
esac

jetson_docker_ensure_access
jetson_docker_prepare_env_file
jetson_docker_load_preset "${PRESET_REF}"
jetson_docker_export_defaults

if [[ -z "${DURATION}" ]]; then
  DURATION="${JETSON_BENCHMARK_DURATION}"
fi

set +u
source /opt/ros/humble/setup.bash
set -u

RUN_STAMP="$(date +%Y-%m-%d_%H-%M-%S)"
RUNTIME_LOG_DIR="$(mktemp -d "${TMPDIR:-/tmp}/jetson_imu_runtime_logs_${RUN_STAMP}.XXXXXX")"
mkdir -p "${RUNTIME_LOG_DIR}"

owned_pids=()
OFF_DIR=""
ON_DIR=""

cleanup() {
  if [[ "${KEEP_RUNNING}" != "true" ]]; then
    jetson_docker_compose stop jetson-vslam-camera jetson-vslam-rtabmap >/dev/null 2>&1 || true
  fi
  for pid in "${owned_pids[@]}"; do
    if kill -0 "${pid}" >/dev/null 2>&1; then
      kill "${pid}" >/dev/null 2>&1 || true
    fi
  done
}
trap cleanup EXIT

ros_node_exists() {
  local node_name="$1"
  ros2 node list 2>/dev/null | grep -qx "${node_name}"
}

process_exists() {
  local pattern="$1"
  pgrep -f "${pattern}" >/dev/null 2>&1
}

ensure_imu_runtime() {
  if ros_node_exists "/bno08x_imu_publisher" || process_exists "[b]no08x_ros2_imu_publisher.py"; then
    echo "[INFO] Existing BNO08x IMU publisher detected."
  else
    echo "[INFO] Starting BNO08x IMU publisher for IMU ON benchmark."
    "${SCRIPT_DIR}/run_bno08x_ros2_imu_publisher.sh" > "${RUNTIME_LOG_DIR}/bno08x_publisher.log" 2>&1 &
    owned_pids+=("$!")
    sleep 4
  fi

  if process_exists "[s]tatic_transform_publisher.*camera_link.*imu_link"; then
    echo "[INFO] Existing camera_link -> imu_link static TF publisher detected."
  else
    echo "[INFO] Starting camera_link -> imu_link static TF for IMU ON benchmark."
    "${SCRIPT_DIR}/run_camera_to_imu_static_tf.sh" > "${RUNTIME_LOG_DIR}/camera_to_imu_static_tf.log" 2>&1 &
    owned_pids+=("$!")
    sleep 2
  fi

  if ! timeout 8s ros2 topic echo /imu/data --once > "${RUNTIME_LOG_DIR}/imu_sample.txt" 2>&1; then
    echo "[ERROR] /imu/data was not readable. Check BNO08x wiring, venv, and I2C address."
    echo "[ERROR] If another BNO08x process is running but no /imu/data appears, stop the stale process first."
    echo "[ERROR] See ${RUNTIME_LOG_DIR}/bno08x_publisher.log"
    exit 1
  fi
}

capture_common_metrics() {
  local bench_dir="$1"

  jetson_docker_compose ps > "${bench_dir}/00_compose_ps.txt"
  ros2 node list > "${bench_dir}/01_nodes.txt"
  ros2 topic list > "${bench_dir}/02_topics.txt"
  timeout 10s ros2 topic echo /rtabmap/odom_info --once > "${bench_dir}/03_odom_info.txt" || true
  timeout 5s ros2 topic echo /tf_static --once > "${bench_dir}/04_tf_static.txt" || true
  timeout 5s ros2 topic echo /imu/data --once > "${bench_dir}/05_imu_sample.txt" || true
}

run_one_benchmark() {
  local imu_mode="$1"
  local imu_topic="/imu/disabled"
  local wait_imu="false"

  if [[ "${imu_mode}" == "on" ]]; then
    ensure_imu_runtime
    imu_topic="/imu/data"
    wait_imu="true"
  fi

  export JETSON_RTABMAP_IMU_TOPIC="${imu_topic}"
  export JETSON_RTABMAP_WAIT_IMU_TO_INIT="${wait_imu}"
  export JETSON_RTABMAP_ENABLE_VIZ="false"
  export JETSON_RTABMAP_ODOM_ARGS="$(jetson_docker_resolve_odom_args "${JETSON_RTABMAP_ODOM_PROFILE}")"

  local stamp
  stamp="$(date +%Y-%m-%d_%H-%M-%S)"
  local bench_dir="${BENCH_ROOT}/${stamp}_docker_${JETSON_ACTIVE_PRESET}_imu_${imu_mode}"
  mkdir -p "${bench_dir}"

  echo "[INFO] Starting Docker RTAB-Map benchmark: preset=${JETSON_ACTIVE_PRESET}, imu=${imu_mode}, duration=${DURATION}s"
  jetson_docker_compose up -d --force-recreate jetson-vslam-camera
  sleep 4
  jetson_docker_compose up -d --force-recreate --no-deps jetson-vslam-rtabmap
  sleep 8

  capture_common_metrics "${bench_dir}"

  echo "[INFO] Capturing metrics for ${DURATION}s into ${bench_dir}"
  timeout "${DURATION}s" tegrastats --interval 1000 > "${bench_dir}/10_tegrastats.txt" &
  local pid_tegrastats=$!
  timeout "${DURATION}s" bash -lc "cd '${JETSON_DOCKER_DIR}' && docker compose --env-file '${JETSON_DOCKER_ENV_FILE}' logs -f jetson-vslam-camera" > "${bench_dir}/11_camera.log" &
  local pid_camera_log=$!
  timeout "${DURATION}s" bash -lc "cd '${JETSON_DOCKER_DIR}' && docker compose --env-file '${JETSON_DOCKER_ENV_FILE}' logs -f jetson-vslam-rtabmap" > "${bench_dir}/12_rtabmap.log" &
  local pid_rtabmap_log=$!
  timeout "${DURATION}s" ros2 topic hz /camera/camera/color/image_raw > "${bench_dir}/20_color_hz.txt" &
  local pid_color=$!
  timeout "${DURATION}s" ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw > "${bench_dir}/21_aligned_depth_hz.txt" &
  local pid_depth=$!
  timeout "${DURATION}s" ros2 topic hz /rtabmap/odom > "${bench_dir}/22_odom_hz.txt" &
  local pid_odom=$!
  timeout "${DURATION}s" ros2 topic hz /rtabmap/mapData > "${bench_dir}/23_mapdata_hz.txt" &
  local pid_mapdata=$!

  local pid_imu=""
  if [[ "${imu_mode}" == "on" ]]; then
    timeout "${DURATION}s" ros2 topic hz /imu/data > "${bench_dir}/24_imu_hz.txt" &
    pid_imu=$!
  else
    printf 'IMU disabled for this run.\n' > "${bench_dir}/24_imu_hz.txt"
  fi

  if [[ -n "${pid_imu}" ]]; then
    wait "${pid_tegrastats}" "${pid_camera_log}" "${pid_rtabmap_log}" "${pid_color}" "${pid_depth}" "${pid_odom}" "${pid_mapdata}" "${pid_imu}" || true
  else
    wait "${pid_tegrastats}" "${pid_camera_log}" "${pid_rtabmap_log}" "${pid_color}" "${pid_depth}" "${pid_odom}" "${pid_mapdata}" || true
  fi

  cat > "${bench_dir}/README.md" <<EOF
# ${stamp} Docker ${JETSON_ACTIVE_PRESET} IMU ${imu_mode} Benchmark

## 목적

- 같은 Docker light 계열 RTAB-Map baseline에서
- BNO08x IMU를 끈 상태와 켠 상태를 같은 방식으로 비교한다.
- 체감 안정성 판단을 보조하기 위해 \`topic hz\`, odometry quality, delay, 전력 로그를 남긴다.

## 이번 실행 조건

- preset: \`${JETSON_ACTIVE_PRESET}\`
- imu mode: \`${imu_mode}\`
- imu topic: \`${imu_topic}\`
- wait imu to init: \`${wait_imu}\`
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
- \`04_tf_static.txt\`: static TF 샘플
- \`05_imu_sample.txt\`: IMU 샘플 또는 비활성 상태 확인용 출력
- \`10_tegrastats.txt\`: Jetson 자원 사용량
- \`11_camera.log\`: camera service log
- \`12_rtabmap.log\`: rtabmap service log
- \`20_color_hz.txt\`: color image topic hz
- \`21_aligned_depth_hz.txt\`: depth hz
- \`22_odom_hz.txt\`: /rtabmap/odom hz
- \`23_mapdata_hz.txt\`: /rtabmap/mapData hz
- \`24_imu_hz.txt\`: /imu/data hz
- \`90_summary.env\`: 자동 생성된 핵심 숫자 요약
- \`91_summary.md\`: 사람이 읽기 쉬운 자동 요약
EOF

  benchmark_write_summary_env "${bench_dir}" > "${bench_dir}/90_summary.env"
  benchmark_render_summary_markdown "${bench_dir}/90_summary.env" > "${bench_dir}/91_summary.md"

  if [[ "${imu_mode}" == "off" ]]; then
    OFF_DIR="${bench_dir}"
  else
    ON_DIR="${bench_dir}"
  fi
}

summary_value() {
  local summary_env="$1"
  local key="$2"
  awk -F= -v key="${key}" '$1 == key {sub($1 "=", ""); print; found=1; exit} END {if(!found) print "n/a"}' "${summary_env}"
}

write_comparison() {
  if [[ -z "${OFF_DIR}" || -z "${ON_DIR}" ]]; then
    return
  fi

  local comparison_file="${BENCH_ROOT}/${RUN_STAMP}_docker_${JETSON_ACTIVE_PRESET}_imu_on_off_comparison.md"
  local off_summary="${OFF_DIR}/90_summary.env"
  local on_summary="${ON_DIR}/90_summary.env"

  cat > "${comparison_file}" <<EOF
# ${RUN_STAMP} Docker ${JETSON_ACTIVE_PRESET} IMU ON/OFF Comparison

## 결론 작성 기준

- 같은 preset과 같은 duration에서 \`IMU OFF\`와 \`IMU ON\`을 연속 측정했다.
- 숫자는 자동 수집값이고, 실제 맵 안정성 평가는 같은 경로를 손으로 움직여 보며 함께 판단한다.
- BNO08x는 \`/imu/data\`, TF는 \`camera_link -> imu_link\` 기준이다.

| Mode | Odom Hz | MapData Hz | IMU Hz | Odom Quality Avg | Odom Delay Avg | RTAB-Map Delay Avg | VDD_IN Avg | Summary |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| OFF | \`$(summary_value "${off_summary}" ODOM_HZ)\` | \`$(summary_value "${off_summary}" MAPDATA_HZ)\` | \`$(summary_value "${off_summary}" IMU_HZ)\` | \`$(summary_value "${off_summary}" ODOM_QUALITY_AVG)\` | \`$(summary_value "${off_summary}" ODOM_DELAY_AVG)s\` | \`$(summary_value "${off_summary}" RTABMAP_DELAY_AVG)s\` | \`$(summary_value "${off_summary}" VDD_IN_AVG_MW)mW\` | [$(basename "${OFF_DIR}")](./$(basename "${OFF_DIR}")/91_summary.md) |
| ON | \`$(summary_value "${on_summary}" ODOM_HZ)\` | \`$(summary_value "${on_summary}" MAPDATA_HZ)\` | \`$(summary_value "${on_summary}" IMU_HZ)\` | \`$(summary_value "${on_summary}" ODOM_QUALITY_AVG)\` | \`$(summary_value "${on_summary}" ODOM_DELAY_AVG)s\` | \`$(summary_value "${on_summary}" RTABMAP_DELAY_AVG)s\` | \`$(summary_value "${on_summary}" VDD_IN_AVG_MW)mW\` | [$(basename "${ON_DIR}")](./$(basename "${ON_DIR}")/91_summary.md) |

## 해석 메모

- \`Odom Quality Avg\`가 높을수록 시각 odometry에서 잡힌 특징점 기반 추정 품질이 좋다고 볼 수 있다.
- \`Odom Delay Avg\`와 \`RTAB-Map Delay Avg\`가 낮을수록 실시간성이 좋다.
- IMU ON이 항상 숫자를 극적으로 좋게 만들지는 않는다. 대신 급격한 회전, 기울어진 주행, feature가 적은 구간에서 자세 추정 안정성에 도움이 되는지 확인하는 것이 핵심이다.
EOF

  echo "[INFO] IMU comparison saved to ${comparison_file}"
}

case "${MODE}" in
  off)
    run_one_benchmark "off"
    ;;
  on)
    run_one_benchmark "on"
    ;;
  both)
    run_one_benchmark "off"
    run_one_benchmark "on"
    write_comparison
    ;;
esac

"${SCRIPT_DIR}/update_docker_benchmark_index.sh" >/dev/null

echo "[INFO] Benchmark index updated."
if [[ -n "${OFF_DIR}" ]]; then
  echo "[INFO] IMU OFF benchmark: ${OFF_DIR}"
fi
if [[ -n "${ON_DIR}" ]]; then
  echo "[INFO] IMU ON benchmark: ${ON_DIR}"
fi
if [[ "${KEEP_RUNNING}" == "true" ]]; then
  echo "[INFO] Services are still running because KEEP_RUNNING=true."
fi
