#!/usr/bin/env bash

set -euo pipefail

benchmark_extract_readme_value() {
  local readme_file="$1"
  local label="$2"
  if [[ ! -f "${readme_file}" ]]; then
    printf '%s' "n/a"
    return
  fi
  awk -F'`' -v label="${label}" 'index($0, label) {print $2; found=1; exit} END {if(!found) print "n/a"}' "${readme_file}"
}

benchmark_last_average_rate() {
  local metric_file="$1"
  if [[ ! -f "${metric_file}" ]]; then
    printf '%s' "n/a"
    return
  fi
  awk '/average rate:/ {rate=$3} END {if(rate != "") print rate; else print "n/a"}' "${metric_file}"
}

benchmark_write_odom_stats_env() {
  local log_file="$1"
  if [[ ! -f "${log_file}" ]]; then
    cat <<'EOF'
ODOM_SAMPLE_COUNT=0
ODOM_QUALITY_AVG=n/a
ODOM_QUALITY_MIN=n/a
ODOM_QUALITY_MAX=n/a
ODOM_DELAY_AVG=n/a
ODOM_DELAY_MIN=n/a
ODOM_DELAY_MAX=n/a
ODOM_UPDATE_AVG=n/a
ODOM_UPDATE_MIN=n/a
ODOM_UPDATE_MAX=n/a
EOF
    return
  fi
  awk '
    BEGIN {
      count = 0
      qsum = 0
      dsum = 0
      usum = 0
    }
    match($0, /quality=[0-9]+/) {
      quality = substr($0, RSTART + 8, RLENGTH - 8) + 0
      count++
      qsum += quality
      if (count == 1 || quality < qmin) qmin = quality
      if (count == 1 || quality > qmax) qmax = quality
    }
    match($0, /delay=[0-9.]+s/) {
      delay = substr($0, RSTART + 6, RLENGTH - 7) + 0
      dsum += delay
      if (count == 1 || delay < dmin) dmin = delay
      if (count == 1 || delay > dmax) dmax = delay
    }
    match($0, /update time=[0-9.]+s/) {
      update_time = substr($0, RSTART + 12, RLENGTH - 13) + 0
      usum += update_time
      if (count == 1 || update_time < umin) umin = update_time
      if (count == 1 || update_time > umax) umax = update_time
    }
    END {
      if (count > 0) {
        printf "ODOM_SAMPLE_COUNT=%d\n", count
        printf "ODOM_QUALITY_AVG=%.1f\n", qsum / count
        printf "ODOM_QUALITY_MIN=%d\n", qmin
        printf "ODOM_QUALITY_MAX=%d\n", qmax
        printf "ODOM_DELAY_AVG=%.4f\n", dsum / count
        printf "ODOM_DELAY_MIN=%.4f\n", dmin
        printf "ODOM_DELAY_MAX=%.4f\n", dmax
        printf "ODOM_UPDATE_AVG=%.4f\n", usum / count
        printf "ODOM_UPDATE_MIN=%.4f\n", umin
        printf "ODOM_UPDATE_MAX=%.4f\n", umax
      } else {
        print "ODOM_SAMPLE_COUNT=0"
        print "ODOM_QUALITY_AVG=n/a"
        print "ODOM_QUALITY_MIN=n/a"
        print "ODOM_QUALITY_MAX=n/a"
        print "ODOM_DELAY_AVG=n/a"
        print "ODOM_DELAY_MIN=n/a"
        print "ODOM_DELAY_MAX=n/a"
        print "ODOM_UPDATE_AVG=n/a"
        print "ODOM_UPDATE_MIN=n/a"
        print "ODOM_UPDATE_MAX=n/a"
      }
    }
  ' "${log_file}"
}

benchmark_write_rtabmap_stats_env() {
  local log_file="$1"
  if [[ ! -f "${log_file}" ]]; then
    cat <<'EOF'
RTABMAP_SAMPLE_COUNT=0
RTABMAP_DELAY_AVG=n/a
RTABMAP_DELAY_MIN=n/a
RTABMAP_DELAY_MAX=n/a
RTABMAP_TIME_AVG=n/a
RTABMAP_TIME_MIN=n/a
RTABMAP_TIME_MAX=n/a
EOF
    return
  fi
  awk '
    BEGIN {
      count = 0
      dsum = 0
      tsum = 0
    }
    /rtabmap\.rtabmap/ {
      has_delay = match($0, /delay=[0-9.]+s/)
      if (has_delay) {
        delay = substr($0, RSTART + 6, RLENGTH - 7) + 0
      }
      has_time = match($0, /RTAB-Map=[0-9.]+s/)
      if (has_time) {
        map_time = substr($0, RSTART + 9, RLENGTH - 10) + 0
      }
      if (has_delay && has_time) {
        count++
        dsum += delay
        tsum += map_time
        if (count == 1 || delay < dmin) dmin = delay
        if (count == 1 || delay > dmax) dmax = delay
        if (count == 1 || map_time < tmin) tmin = map_time
        if (count == 1 || map_time > tmax) tmax = map_time
      }
    }
    END {
      if (count > 0) {
        printf "RTABMAP_SAMPLE_COUNT=%d\n", count
        printf "RTABMAP_DELAY_AVG=%.4f\n", dsum / count
        printf "RTABMAP_DELAY_MIN=%.4f\n", dmin
        printf "RTABMAP_DELAY_MAX=%.4f\n", dmax
        printf "RTABMAP_TIME_AVG=%.4f\n", tsum / count
        printf "RTABMAP_TIME_MIN=%.4f\n", tmin
        printf "RTABMAP_TIME_MAX=%.4f\n", tmax
      } else {
        print "RTABMAP_SAMPLE_COUNT=0"
        print "RTABMAP_DELAY_AVG=n/a"
        print "RTABMAP_DELAY_MIN=n/a"
        print "RTABMAP_DELAY_MAX=n/a"
        print "RTABMAP_TIME_AVG=n/a"
        print "RTABMAP_TIME_MIN=n/a"
        print "RTABMAP_TIME_MAX=n/a"
      }
    }
  ' "${log_file}"
}

benchmark_write_power_stats_env() {
  local metric_file="$1"
  if [[ ! -f "${metric_file}" ]]; then
    cat <<'EOF'
VDD_IN_SAMPLE_COUNT=0
VDD_IN_AVG_MW=n/a
VDD_IN_MIN_MW=n/a
VDD_IN_MAX_MW=n/a
EOF
    return
  fi
  awk '
    BEGIN {
      count = 0
      sum = 0
    }
    {
      if (match($0, /VDD_IN [0-9]+mW\/[0-9]+mW/)) {
        power_field = substr($0, RSTART + 7, RLENGTH - 7)
        split(power_field, parts, "/")
        gsub(/mW/, "", parts[1])
        power = parts[1] + 0
        count++
        sum += power
        if (count == 1 || power < min) min = power
        if (count == 1 || power > max) max = power
      }
    }
    END {
      if (count > 0) {
        printf "VDD_IN_SAMPLE_COUNT=%d\n", count
        printf "VDD_IN_AVG_MW=%.0f\n", sum / count
        printf "VDD_IN_MIN_MW=%d\n", min
        printf "VDD_IN_MAX_MW=%d\n", max
      } else {
        print "VDD_IN_SAMPLE_COUNT=0"
        print "VDD_IN_AVG_MW=n/a"
        print "VDD_IN_MIN_MW=n/a"
        print "VDD_IN_MAX_MW=n/a"
      }
    }
  ' "${metric_file}"
}

benchmark_write_odom_info_env() {
  local info_file="$1"
  if [[ ! -f "${info_file}" ]]; then
    cat <<'EOF'
ODOM_INFO_MATCHES=n/a
ODOM_INFO_INLIERS=n/a
ODOM_INFO_FEATURES=n/a
ODOM_INFO_LOCAL_MAP_SIZE=n/a
ODOM_INFO_ESTIMATION_TIME=n/a
EOF
    return
  fi
  awk '
    /^matches: / {matches=$2}
    /^inliers: / {inliers=$2}
    /^features: / {features=$2}
    /^local_map_size: / {local_map_size=$2}
    /^time_estimation: / {estimation_time=$2}
    END {
      printf "ODOM_INFO_MATCHES=%s\n", matches ? matches : "n/a"
      printf "ODOM_INFO_INLIERS=%s\n", inliers ? inliers : "n/a"
      printf "ODOM_INFO_FEATURES=%s\n", features ? features : "n/a"
      printf "ODOM_INFO_LOCAL_MAP_SIZE=%s\n", local_map_size ? local_map_size : "n/a"
      printf "ODOM_INFO_ESTIMATION_TIME=%s\n", estimation_time ? estimation_time : "n/a"
    }
  ' "${info_file}"
}

benchmark_write_summary_env() {
  local bench_dir="$1"
  local bench_name
  local stamp
  local preset
  local readme_file="${bench_dir}/README.md"

  bench_name="$(basename "${bench_dir}")"
  stamp="${bench_name%%_docker_*}"
  preset="${bench_name#*_docker_}"
  preset="${preset%_baseline}"

  cat <<EOF
BENCH_NAME=${bench_name}
BENCH_DIR=${bench_dir}
STAMP=${stamp}
PRESET=${preset}
DURATION_SECONDS=$(benchmark_extract_readme_value "${readme_file}" "duration:")
COLOR_PROFILE=$(benchmark_extract_readme_value "${readme_file}" "color profile:")
DEPTH_PROFILE=$(benchmark_extract_readme_value "${readme_file}" "depth profile:")
DETECTION_RATE=$(benchmark_extract_readme_value "${readme_file}" "detection rate:")
ODOM_PROFILE=$(benchmark_extract_readme_value "${readme_file}" "odom profile:")
QUEUE_SIZE=$(benchmark_extract_readme_value "${readme_file}" "queue size:")
COLOR_HZ=$(benchmark_last_average_rate "${bench_dir}/20_color_hz.txt")
DEPTH_HZ=$(benchmark_last_average_rate "${bench_dir}/21_aligned_depth_hz.txt")
ODOM_HZ=$(benchmark_last_average_rate "${bench_dir}/22_odom_hz.txt")
MAPDATA_HZ=$(benchmark_last_average_rate "${bench_dir}/23_mapdata_hz.txt")
EOF
  benchmark_write_odom_stats_env "${bench_dir}/12_rtabmap.log"
  benchmark_write_rtabmap_stats_env "${bench_dir}/12_rtabmap.log"
  benchmark_write_power_stats_env "${bench_dir}/10_tegrastats.txt"
  benchmark_write_odom_info_env "${bench_dir}/03_odom_info.txt"
}

benchmark_render_summary_markdown() {
  local summary_env="$1"
  (
    set -a
    # shellcheck disable=SC1090
    source "${summary_env}"
    set +a
    cat <<EOF
# ${STAMP} Docker ${PRESET} Benchmark Summary

## 자동 요약

- preset: \`${PRESET}\`
- duration: \`${DURATION_SECONDS}\`
- profiles: \`${COLOR_PROFILE}\` / \`${DEPTH_PROFILE}\`
- detection rate / queue: \`${DETECTION_RATE}\` / \`${QUEUE_SIZE}\`
- image hz: color \`${COLOR_HZ}\`, depth \`${DEPTH_HZ}\`
- odom/mapData hz: \`${ODOM_HZ}\` / \`${MAPDATA_HZ}\`
- odom quality: avg \`${ODOM_QUALITY_AVG}\`, min-max \`${ODOM_QUALITY_MIN}~${ODOM_QUALITY_MAX}\`
- odom delay: avg \`${ODOM_DELAY_AVG}s\`, min-max \`${ODOM_DELAY_MIN}~${ODOM_DELAY_MAX}s\`
- RTAB-Map delay: avg \`${RTABMAP_DELAY_AVG}s\`
- VDD_IN: avg \`${VDD_IN_AVG_MW}mW\`, min-max \`${VDD_IN_MIN_MW}~${VDD_IN_MAX_MW}mW\`
- odom_info: matches \`${ODOM_INFO_MATCHES}\`, inliers \`${ODOM_INFO_INLIERS}\`, features \`${ODOM_INFO_FEATURES}\`, local map \`${ODOM_INFO_LOCAL_MAP_SIZE}\`

## 참고 파일

- [\`README.md\`](./README.md): 실행 조건과 산출물 설명
- [\`10_tegrastats.txt\`](./10_tegrastats.txt): Jetson 자원 사용량 원본
- [\`11_camera.log\`](./11_camera.log): camera service log
- [\`12_rtabmap.log\`](./12_rtabmap.log): rtabmap service log
- [\`20_color_hz.txt\`](./20_color_hz.txt): color hz 원본
- [\`21_aligned_depth_hz.txt\`](./21_aligned_depth_hz.txt): depth hz 원본
- [\`22_odom_hz.txt\`](./22_odom_hz.txt): odom hz 원본
- [\`23_mapdata_hz.txt\`](./23_mapdata_hz.txt): mapData hz 원본
EOF
  )
}
