#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JETSON_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BENCH_ROOT="${JETSON_DIR}/assets/benchmarks"
source "${SCRIPT_DIR}/lib_jetson_benchmark.sh"

INDEX_FILE="${BENCH_ROOT}/docker_benchmark_index.csv"
ROOT_README="${BENCH_ROOT}/README.md"

tmp_index="$(mktemp)"
trap 'rm -f "${tmp_index}"' EXIT

printf '%s\n' 'stamp,preset,imu_mode,imu_topic,imu_hz,color_profile,depth_profile,detection_rate,queue_size,color_hz,depth_hz,odom_hz,mapdata_hz,odom_quality_avg,odom_quality_min,odom_quality_max,odom_delay_avg_s,rtabmap_delay_avg_s,vdd_in_avg_mw,odom_info_matches,odom_info_inliers,odom_info_features,odom_info_local_map_size,bench_dir' > "${tmp_index}"

mapfile -t bench_dirs < <(find "${BENCH_ROOT}" -maxdepth 1 -mindepth 1 -type d -name '*_docker_*' | sort -r)

for bench_dir in "${bench_dirs[@]}"; do
  if [[ ! -f "${bench_dir}/README.md" || ! -f "${bench_dir}/12_rtabmap.log" ]]; then
    continue
  fi

  summary_env="${bench_dir}/90_summary.env"
  summary_md="${bench_dir}/91_summary.md"

  benchmark_write_summary_env "${bench_dir}" > "${summary_env}"
  benchmark_render_summary_markdown "${summary_env}" > "${summary_md}"

  (
    set -a
    # shellcheck disable=SC1090
    source "${summary_env}"
    set +a
    printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
      "${STAMP}" \
      "${PRESET}" \
      "${IMU_MODE}" \
      "${IMU_TOPIC}" \
      "${IMU_HZ}" \
      "${COLOR_PROFILE}" \
      "${DEPTH_PROFILE}" \
      "${DETECTION_RATE}" \
      "${QUEUE_SIZE}" \
      "${COLOR_HZ}" \
      "${DEPTH_HZ}" \
      "${ODOM_HZ}" \
      "${MAPDATA_HZ}" \
      "${ODOM_QUALITY_AVG}" \
      "${ODOM_QUALITY_MIN}" \
      "${ODOM_QUALITY_MAX}" \
      "${ODOM_DELAY_AVG}" \
      "${RTABMAP_DELAY_AVG}" \
      "${VDD_IN_AVG_MW}" \
      "${ODOM_INFO_MATCHES}" \
      "${ODOM_INFO_INLIERS}" \
      "${ODOM_INFO_FEATURES}" \
      "${ODOM_INFO_LOCAL_MAP_SIZE}" \
      "${BENCH_NAME}" \
      >> "${tmp_index}"
  )
done

mv "${tmp_index}" "${INDEX_FILE}"

{
  cat <<'EOF'
# Jetson Benchmarks

## 결론

- 이 폴더는 `Jetson`에서 실제로 돌려본 baseline과 후보 세팅의 측정 결과를 저장하는 공간이다.
- `2026-04-20`부터는 `Docker` benchmark 결과가 실행 직후 자동으로 요약되고, root 인덱스도 함께 갱신된다.

## 권장 구조

- 날짜별 실험 폴더를 만든다.
- 예시:
  - `2026-04-18_rtabmap_baseline/`
  - `2026-04-18_detectionrate3_candidate/`
  - `2026-04-19_candidate_compare/`
  - `2026-04-20_14-10-57_docker_light_baseline/`

## 권장 파일

- `01_camera_launch.log`
- `02_rtabmap_launch.log`
- `05_odom_info.txt`
- `06_color_hz.txt`
- `07_aligned_depth_hz.txt`
- `08_odom_hz.txt`
- `12_tegrastats.txt`
- `13_rtabmap_viz.png`
- `README.md`
- `90_summary.env`
- `91_summary.md`

## 원칙

- 같은 실험의 로그, 숫자, 스크린샷은 한 폴더에 모은다.
- 나중에 비교할 수 있게 파일명은 숫자 접두어로 정렬되게 쓴다.
- 실험마다 마지막에 `README.md` 한 장으로 결론을 남긴다.
- `Docker` benchmark는 요약 파일과 root 인덱스를 자동 갱신한다.

## Docker Benchmark Index

- CSV 인덱스: [`docker_benchmark_index.csv`](./docker_benchmark_index.csv)
- 각 benchmark 폴더의 `91_summary.md`를 같이 보면 빠르게 비교할 수 있다.

| Timestamp | Preset | IMU | Color Hz | Odom Hz | MapData Hz | Odom Quality Avg | Odom Delay Avg | VDD_IN Avg | Summary |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
EOF

  for bench_dir in "${bench_dirs[@]}"; do
    if [[ ! -f "${bench_dir}/README.md" || ! -f "${bench_dir}/12_rtabmap.log" ]]; then
      continue
    fi

    summary_env="${bench_dir}/90_summary.env"
    (
      set -a
      # shellcheck disable=SC1090
      source "${summary_env}"
      set +a
      printf '| `%s` | `%s` | `%s` | `%s` | `%s` | `%s` | `%s` | `%ss` | `%smW` | [%s](./%s/91_summary.md) |\n' \
        "${STAMP}" \
        "${PRESET}" \
        "${IMU_MODE}" \
        "${COLOR_HZ}" \
        "${ODOM_HZ}" \
        "${MAPDATA_HZ}" \
        "${ODOM_QUALITY_AVG}" \
        "${ODOM_DELAY_AVG}" \
        "${VDD_IN_AVG_MW}" \
        "${BENCH_NAME}" \
        "${BENCH_NAME}"
    )
  done
} > "${ROOT_README}"

echo "[INFO] Docker benchmark index updated: ${INDEX_FILE}"
echo "[INFO] Benchmarks README updated: ${ROOT_README}"
