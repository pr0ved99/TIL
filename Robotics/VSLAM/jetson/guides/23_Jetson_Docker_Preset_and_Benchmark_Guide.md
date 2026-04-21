# 23 Jetson Docker Preset and Benchmark Guide

## 목적

- `Jetson`에서 `Docker` baseline을 반복할 때
- 해상도, DetectionRate, queue 같은 성능 기준을 파일로 고정하고,
- 같은 실행에서 `tegrastats`, `topic hz`, `quality` 로그를 자동으로 남긴다.

## 이 가이드가 필요한 이유

- 지금까지는 명령 인자로 `424x240x15`, `DetectionRate 2`, `queue 15`를 직접 넣는 경우가 많았다.
- 이 방식은 빠르지만, 나중에 "어떤 기준선으로 돌렸는지"가 흐려지기 쉽다.
- 그래서 지금은 아래 두 층으로 나눠서 관리한다.
  - `preset 파일`: baseline 조건 저장
  - `benchmark script`: 실행 중 성능/토픽/log 자동 수집

## 먼저 알면 좋은 점

- preset 파일은 [`docker/presets/`](../docker/presets/README.md)에 있다.
- 현재 기본값은 `light`다.
- detached benchmark는 `camera`와 `rtabmap` 서비스를 background로 띄운 뒤,
  host에서 `ros2 topic hz`와 `tegrastats`를 같이 수집한다.

## 1. preset 파일이 무엇을 하는지 먼저 이해한다

이 단계는 "왜 첫 인자로 `light`, `medium`, `compare`를 넣는지"를 먼저 이해하는 단계다.

- `light`
  - 가장 가벼운 baseline
  - `424x240x15`, `DetectionRate 2`, `queue 15`
- `medium`
  - 조금 더 촘촘한 map 확인
  - `640x360x15`, `DetectionRate 2`, `queue 20`
- `compare`
  - 해상도는 `light`와 같고 `DetectionRate`만 높여 비교
  - `424x240x15`, `DetectionRate 3`, `queue 20`

## 2. detached stack으로 backend만 빠르게 올린다

이 단계는 `camera`와 `rtabmap` 서비스를 foreground 두 터미널 대신 detached로 한 번에 올리는 단계다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack.sh light
```

왜 이 명령을 쓰는가:

- `compose run --rm`보다 서비스 단위가 더 분명하다.
- `camera / rtabmap`을 따로 죽이고 다시 올리기 쉽다.
- 이후 host `rtabmap_viz`를 붙이거나 benchmark를 남길 때도 기준선이 더 흔들리지 않는다.

## 3. benchmark를 자동 수집한다

이 단계는 detached stack을 띄운 뒤, 같은 실행에서 `tegrastats`, `topic hz`, Docker logs를 자동으로 모으는 단계다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_benchmark.sh light 20
```

왜 이 명령을 쓰는가:

- `20초` 동안 baseline을 유지하면서,
  - `tegrastats`
  - `/camera/...` `topic hz`
  - `/rtabmap/odom`, `/rtabmap/mapData` `topic hz`
  - `camera/rtabmap` Docker log
  를 한 번에 남길 수 있다.
- 실행이 끝나면 benchmark 폴더 안에 `90_summary.env`, `91_summary.md`도 같이 생긴다.
- 동시에 [`jetson/assets/benchmarks/README.md`](../assets/benchmarks/README.md)와 `docker_benchmark_index.csv`도 자동으로 갱신된다.

## 4. 더 촘촘한 조건으로 같은 실험을 반복한다

이 단계는 같은 구조를 유지한 채 preset만 바꿔서 비교하는 단계다.

```bash
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_benchmark.sh medium 20
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_benchmark.sh compare 20
```

왜 이 명령을 쓰는가:

- `light`는 실시간 baseline
- `medium`은 map 밀도
- `compare`는 DetectionRate 차이
를 각각 같은 수집 형식으로 남길 수 있다.

## 5. 결과는 어디에 남는가

이 단계는 benchmark 산출물 위치를 먼저 이해하는 단계다.

- 저장 위치:
  - `jetson/assets/benchmarks/YYYY-MM-DD_HH-MM-SS_docker_<preset>_baseline/`
- 기본 파일:
  - `00_compose_ps.txt`
  - `01_nodes.txt`
  - `02_topics.txt`
  - `03_odom_info.txt`
  - `10_tegrastats.txt`
  - `11_camera.log`
  - `12_rtabmap.log`
  - `20_color_hz.txt`
  - `21_aligned_depth_hz.txt`
  - `22_odom_hz.txt`
  - `23_mapdata_hz.txt`
  - `90_summary.env`
  - `91_summary.md`

## 6. 자동 요약 파일은 어떻게 읽는가

이 단계는 benchmark가 끝난 뒤 어디를 먼저 보면 되는지 이해하는 단계다.

- `90_summary.env`
  - 스크립트가 다시 읽기 쉬운 key-value 요약
  - 다른 자동화나 표 생성에 쓰기 좋다
- `91_summary.md`
  - 사람이 바로 읽는 요약
  - preset, hz, odom quality/delay, 전력 요약이 같이 들어 있다
- `docker_benchmark_index.csv`
  - 여러 benchmark를 한 줄씩 비교하는 root 인덱스
- `jetson/assets/benchmarks/README.md`
  - 최근 Docker benchmark를 표로 모아 보여주는 루트 인덱스

## 7. 끝난 뒤 서비스를 정리한다

이 단계는 detached로 띄운 backend를 깔끔하게 내리는 단계다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/stop_docker_rtabmap_stack.sh
```

왜 이 명령을 쓰는가:

- 다음 실험 전에 남아 있는 서비스가 baseline을 섞지 않게 한다.
- Docker backend를 foreground/manual 실행으로 다시 바꾸고 싶을 때도 정리 기준이 생긴다.

## 8. 지금 단계에서 기대할 것

- `Docker` baseline이 "감"이 아니라 숫자로 비교 가능해진다.
- 어떤 설정이 더 가벼운지 `tegrastats`, `topic hz`, `quality` 로그로 판단할 수 있다.
- 이후 `BNO08x IMU ON` 실험도 같은 수집 틀로 확장 가능하다.
