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
| `2026-04-21_12-01-47` | `light` | `on` | `14.989` | `9.539` | `1.768` | `57.1` | `0.1592s` | `9128mW` | [2026-04-21_12-01-47_docker_light_imu_on](./2026-04-21_12-01-47_docker_light_imu_on/91_summary.md) |
| `2026-04-21_12-00-54` | `light` | `off` | `14.976` | `10.410` | `1.828` | `56.4` | `0.1459s` | `9018mW` | [2026-04-21_12-00-54_docker_light_imu_off](./2026-04-21_12-00-54_docker_light_imu_off/91_summary.md) |
| `2026-04-20_14-12-51` | `compare` | `n/a` | `14.986` | `7.783` | `2.490` | `186.9` | `0.1960s` | `7399mW` | [2026-04-20_14-12-51_docker_compare_baseline](./2026-04-20_14-12-51_docker_compare_baseline/91_summary.md) |
| `2026-04-20_14-12-15` | `medium` | `n/a` | `14.300` | `5.310` | `1.522` | `325.2` | `0.2020s` | `7103mW` | [2026-04-20_14-12-15_docker_medium_baseline](./2026-04-20_14-12-15_docker_medium_baseline/91_summary.md) |
| `2026-04-20_14-10-57` | `light` | `n/a` | `14.989` | `14.991` | `1.874` | `198.7` | `0.1270s` | `6777mW` | [2026-04-20_14-10-57_docker_light_baseline](./2026-04-20_14-10-57_docker_light_baseline/91_summary.md) |
