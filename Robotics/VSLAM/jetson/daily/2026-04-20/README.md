# 2026-04-20 Jetson 작업 일지

## 결론

- `Jetson`에서 `Docker` 안 `D435i + rgbd_odometry + rtabmap` backend는 계속 두고, `host`에서 `rtabmap_viz`만 띄우는 구조가 현재 가장 실용적이라는 것은 여전히 맞다.
- 다만 `Docker` 안 `rtabmap_viz`도 원인 분석 끝에 `video/render` 그룹 누락과 image-only IMU remap 버그를 고친 뒤 다시 시작과 parameter binding까지 정상 확인했다.
- 즉, 현재 `Jetson` 기준 운영 구조는 **기본은 `Docker backend + host frontend`**, 필요하면 **`Docker 내부 GUI도 재시도 가능한 상태`**로 보는 편이 맞다.

## 오늘 작업 한 줄 요약

- `Docker` 안 `RTAB-Map` 계산은 유지하고, `host`에서 `rtabmap_viz`를 직접 붙여 누적 map이 실제로 보이는지 확인했다.
- 왜 이 작업을 했는가?
  - `Docker` 안 GUI가 OpenGL 문제로 막히는 상황에서도, backend 자체가 실제로 쓸 만한지 먼저 확인해야 했기 때문이다.

## 현재 작업 형태

- `Docker`는 센서 입력과 맵 계산에 집중한다.
- `host`는 시각화만 담당한다.
- 즉, 같은 Jetson 안에서 `backend`와 `frontend`를 역할 분리하는 방식으로 정리했다.

## 시간순 기록

### Docker GUI 검정 화면 재확인

- `run_rtabmap_baseline_in_docker.sh 2 relaxed true 15`로 다시 시도했을 때, 창은 뜨지만 내부는 여전히 검정 화면에 가깝다는 관찰이 이어졌다.
- 이 상태는 기존에 남아 있던 `Docker` 안 `rtabmap_viz`의 OpenGL 문제와 같은 방향으로 보는 편이 자연스럽다.

### host rtabmap_viz 단독 연결 재시도

- `host`에서 `rtabmap_viz`를 직접 띄워 `Docker`가 publish한 `/camera/camera/*`, `/rtabmap/*` topic을 읽게 했다.
- 처음에는 아래 증상이 있었다.

```text
Can't call rtabmap parameters service, is the node running?
rtabmap_viz: Did not receive data since 5 seconds!
```

- 이때는 `viewer`가 `/rtabmap` namespace와 service에 완전히 맞게 붙지 못한 가능성이 컸다.

### backend topic 재확인

- 이후 `host`에서 아래를 다시 확인했다.
  - `/camera/camera/color/image_raw`
  - `/camera/camera/aligned_depth_to_color/image_raw`
  - `/rtabmap/odom`
  - `/rtabmap/odom_info`
  - `/rtabmap/mapData`
  - `/rtabmap/cloud_map`
  - `/rtabmap/grid_prob_map`
- image topic은 약 `15 Hz`로 실제로 올라오고 있었다.
- 따라서 이 시점에는 "`backend가 안 돈다`"보다 "`viewer 연결 문맥이 완전하지 않다`" 쪽이 더 유력했다.

### camera TF 설정 되돌림

- 오늘 중간에 `Docker` camera wrapper를 경량화하면서 `publish_tf:=false`를 넣었던 부분이 있었다.
- 이 상태는 `rgbd_odometry`가 필요한 camera TF를 못 받게 만들어, node는 살아 있어도 실제 odom/map이 안 나오는 쪽으로 이어질 수 있다.
- 그래서 `run_realsense_color_depth_in_docker.sh`에서 `publish_tf:=false`, `tf_publish_rate:=0.0`를 제거해 camera TF를 다시 켜는 쪽으로 되돌렸다.

### Docker backend + host frontend 성공

- 이후 `host`에서 `rtabmap_viz`를 `/rtabmap` namespace 기준으로 다시 붙였고, 현재 구조에서는 누적 map이 실제로 보인다는 점을 확인했다.
- 이 결과로 해석을 다시 정리하면 아래와 같다.
  - `Docker backend`: 정상
  - `Docker GUI`: 당시에는 OpenGL/NvRm 권한 문제로 실패
  - `host GUI`: 같은 ROS graph에서 topic을 읽어 시각화 가능

### Docker 내부 GUI 원인 재분석 및 수정

- 이후 내부 GUI 문제를 따로 다시 좁혀봤다.
- 처음 가설은 `GLX/EGL` 부재였지만, 실제로는 Qt `xcb`와 `GLX` integration 자체는 컨테이너 안에서 정상 초기화됐다.
- 결정적인 로그는 아래였다.

```text
NvRmMemInitNvmap failed with Permission denied
libnvrm_gpu.so: NvRmGpuLibOpen failed
qt.qpa.backingstore: composeAndFlush: makeCurrent() failed
```

- 원인 확인 결과:
  - 컨테이너 사용자 `jetson`은 `i2c`만 보조 그룹으로 받고 있었고
  - Jetson GPU 쪽 장치인 `/dev/nvmap`, `/dev/nvhost-gpu`, `/dev/nvhost-ctrl-gpu`는 `root:video 660`이었다
  - 즉, `rtabmap_viz`가 Tegra GPU 메모리 경로를 열 때 권한이 막히는 구조였다

- 수정:
  - `compose.yaml`에 `HOST_VIDEO_GID`, `HOST_RENDER_GID`를 `group_add`로 추가
  - `lib_jetson_docker.sh`가 host의 `video/render` group id를 `.env`에 자동 반영하게 수정

- 추가로 함께 찾은 버그:
  - image-only baseline에서도 `rtabmap_launch` 기본값 때문에 `/imu/data` remap이 숨어서 붙고 있었다
  - 그래서 image-only 경로는 명시적으로 `imu_topic:=/imu/disabled`를 넘기게 바꿨다

- 재검증 결과:
  - container 안에서 사용자가 `video(44)`, `render(104)`를 실제로 받는 것 확인
  - 내부 `rtabmap_viz` 재기동 시 예전 `NvRmMemInitNvmap failed with Permission denied` 로그가 사라짐
  - `Parameters read = 387`, `Parameters successfully read.`, `rtabmap_viz started.`까지 확인

- 현재 해석:
  - Docker 내부 GUI 문제의 핵심은 `GLX/EGL 부재`보다 `Jetson GPU device 권한`이었다
  - 현재는 고쳐진 상태지만, 운영 기준으로는 여전히 `Docker backend + host GUI`가 더 단순하고 반복 가능하다

### Docker baseline 경량화 정리

- 오늘 기준으로 Docker wrapper 쪽 기본값도 조금 더 정리했다.
  - camera preset: `424x240x15 + IMU OFF`
  - RTAB-Map queue size: `15`
  - compose: `init`, `tmpfs /tmp`, `MALLOC_ARENA_MAX=2` 반영
- 이건 지금 목표가 "`최대한 예쁜 설정`"이 아니라 "`Jetson에서 반복 가능한 baseline`"이기 때문이다.

### Docker 구조 최적화 2차 정리

- 기존에는 `compose run --rm jetson-vslam-dev bash -lc ...` 형태의 일회성 실행이 중심이었다.
- 오늘은 이 구조를 아래처럼 다시 나눴다.
  - `jetson-vslam-dev`
  - `jetson-vslam-camera`
  - `jetson-vslam-rtabmap`
- 또 이미지도 아래처럼 나눴다.
  - `Dockerfile`: 개발용 이미지
  - `Dockerfile.runtime`: camera/rtabmap 실행용 경량 이미지

### tmpfs DB / ROS log 적용

- 반복 baseline에서 디스크 I/O를 줄이기 위해 아래 경로를 `/tmp` 기반으로 고정했다.
  - `ROS_HOME=/tmp/ros`
  - `ROS_LOG_DIR=/tmp/ros/log`
  - `rtabmap.db=/tmp/rtabmap/rtabmap.db`
- compose에는 `/tmp`, `/var/tmp` `tmpfs`도 같이 추가했다.

### preset 파일 분리

- `Docker` baseline 설정이 명령 인자에만 흩어지지 않도록 preset 파일을 추가했다.
  - `light`
  - `medium`
  - `compare`
- 지금 기본 운영 기준은 여전히 `light`다.

### monitoring 자동화 추가

- 반복 실험 때 "가벼워졌는지"를 숫자로 보기 위해 benchmark 스크립트를 추가했다.
- 이 스크립트는 한 번에 아래를 수집한다.
  - `tegrastats`
  - `/camera/...` `topic hz`
  - `/rtabmap/odom`, `/rtabmap/mapData` `topic hz`
  - `camera / rtabmap` Docker log

### benchmark 결과 자동 요약/인덱스 추가

- benchmark가 끝날 때마다 각 결과 폴더에 아래 파일이 자동으로 생기게 정리했다.
  - `90_summary.env`
  - `91_summary.md`
- 또 root benchmark 폴더의 아래 파일도 자동 갱신되게 만들었다.
  - `docker_benchmark_index.csv`
  - `assets/benchmarks/README.md`
- 즉, 이제는 결과 폴더만 쌓이는 게 아니라 "최근 Docker benchmark를 어디서 빨리 비교할지"까지 같이 남는 구조다.

### preset benchmark 비교

- `light`, `medium`, `compare` preset으로 각각 `20s` benchmark를 남겼다.
- 저장 위치:
  - [`2026-04-20_14-10-57_docker_light_baseline`](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-20_14-10-57_docker_light_baseline)
  - [`2026-04-20_14-12-15_docker_medium_baseline`](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-20_14-12-15_docker_medium_baseline)
  - [`2026-04-20_14-12-51_docker_compare_baseline`](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-20_14-12-51_docker_compare_baseline)

관찰 요약:

- `light`
  - color/depth 약 `15 Hz`, odom 약 `15 Hz`, mapData 약 `1.87 Hz`
  - odom delay 대체로 `0.10~0.11s`
  - 전력은 대체로 `6.6~6.8W`
  - 현재 세 preset 중 가장 실시간성이 좋다.
- `medium`
  - color 약 `14.3 Hz`, depth 약 `15 Hz`, odom 약 `5.3 Hz`, mapData 약 `1.52 Hz`
  - odom quality는 높아졌지만 delay와 추정 시간이 커졌다.
  - 전력은 대체로 `6.8~7.3W`
  - 현재 Jetson baseline으로 쓰기엔 무겁다.
- `compare`
  - color/depth 약 `15 Hz`, odom 약 `7.8 Hz`, mapData 약 `2.49 Hz`
  - `DetectionRate=3` 영향으로 mapData는 더 자주 나오지만 odom은 `light`보다 느리다.
  - 전력은 대체로 `7.2~7.3W`
  - 품질/누적감은 좋아질 여지가 있지만 baseline보다는 비교용 후보에 가깝다.

현재 판단:

- 기본 preset은 여전히 `light`가 가장 적합하다.
- `compare`는 누적 map 빈도와 품질 후보를 볼 때 비교용으로 유지할 가치가 있다.
- `medium`은 현재 기준으로는 실시간성 대비 이득이 애매하다.
- `BNO08x` 쪽 시각화는 `aircraft`, `compass`에 이어 `level viewer`까지 추가해, 이제 방향/기울기/수평을 각각 따로 볼 수 있게 됐다.
- 여기에 더해 `all-in-one viewer`도 추가해서, 이제 방향/수평/기울기/회전을 한 화면에서 동시에 점검할 수 있게 됐다.
- `all-in-one viewer` 하단 정보 패널도 라벨 위치를 고정하고 값만 갱신되게 바꿔, 숫자 변화가 덜 산만하게 보이도록 정리했다.
- 이후 `all-in-one viewer`를 diagnostics 확장판으로 키워 `gravity`, `linear acceleration`, `calibration status`까지 같이 보이게 정리했다.
- 여기에 `linear acceleration` 기반 `Move` 힌트도 넣어, 위치 추정은 아니지만 현재 어떤 방향으로 가속이 걸리고 있는지 빠르게 읽을 수 있게 했다.
- 또 `linear acceleration`을 짧게 적분한 `motion trace viewer`도 추가해, `X/Y/Z` 축 위에서 점이 어떻게 이동하는지 `pseudo-position` 형태로 확인할 수 있게 했다.
- 또 `Sensor-Calibration-Procedure-v1.1.pdf`를 참고해 Jetson용 `BNO08x calibration guide`도 새로 정리했다.

## 오늘 만든/수정한 파일

- [2026-04-20 Jetson 작업 일지](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/daily/2026-04-20/README.md)
- [Current_Progress_and_Open_Issues.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/docs/progress/Current_Progress_and_Open_Issues.md)
- [docker/README.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/docker/README.md)
- [Dockerfile.runtime](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/docker/Dockerfile.runtime)
- [docker/presets/README.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/docker/presets/README.md)
- [docker/presets/light.env](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/docker/presets/light.env)
- [docker/presets/medium.env](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/docker/presets/medium.env)
- [docker/presets/compare.env](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/docker/presets/compare.env)
- [20_Jetson_Docker_RTABMap_With_BNO08x_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/20_Jetson_Docker_RTABMap_With_BNO08x_Guide.md)
- [21_Jetson_Docker_RTABMap_Baseline_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/21_Jetson_Docker_RTABMap_Baseline_Guide.md)
- [22_Jetson_Docker_Backend_Host_RTABMapViz_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/22_Jetson_Docker_Backend_Host_RTABMapViz_Guide.md)
- [23_Jetson_Docker_Preset_and_Benchmark_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/23_Jetson_Docker_Preset_and_Benchmark_Guide.md)
- [lib_jetson_docker.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/lib_jetson_docker.sh)
- [run_realsense_color_depth_in_docker.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_realsense_color_depth_in_docker.sh)
- [run_rtabmap_baseline_in_docker.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_rtabmap_baseline_in_docker.sh)
- [run_rtabmap_with_external_imu_in_docker.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_rtabmap_with_external_imu_in_docker.sh)
- [run_docker_rtabmap_stack.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack.sh)
- [stop_docker_rtabmap_stack.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/stop_docker_rtabmap_stack.sh)
- [run_docker_rtabmap_benchmark.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_benchmark.sh)
- [run_rtabmap_viz_from_host_for_docker.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_rtabmap_viz_from_host_for_docker.sh)
- [run_bno08x_ros2_imu_publisher.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_bno08x_ros2_imu_publisher.sh)
- [run_camera_to_imu_static_tf.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_camera_to_imu_static_tf.sh)
- [run_docker_rtabmap_stack_with_external_imu.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack_with_external_imu.sh)
- [bno08x_level_viewer.py](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/bno08x_level_viewer.py)
- [bno08x_all_in_one_viewer.py](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/bno08x_all_in_one_viewer.py)
- [24_Jetson_BNO08x_Level_Viewer_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/24_Jetson_BNO08x_Level_Viewer_Guide.md)
- [25_Jetson_BNO08x_All_In_One_Viewer_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/25_Jetson_BNO08x_All_In_One_Viewer_Guide.md)
- [compose.yaml](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/docker/compose.yaml)
- [guides/README.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/README.md)
- [scripts/README.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/README.md)

## 오늘 관찰한 핵심 현상

- `Docker` 안 `rtabmap_viz`가 안 되던 것은 "`맵 계산 실패`"보다 "`Jetson GPU device 권한이 빠진 GUI 렌더링 실패`"에 더 가까웠다.
- `host`에서 같은 topic을 읽으면 누적 map이 보였으므로, backend 데이터는 실제로 살아 있다.
- `RTAB-Map`은 이미지 자체를 파노라마처럼 계속 붙이는 도구가 아니므로, "`feature는 누적되는데 이미지가 안 쌓인다`"는 느낌은 어느 정도 정상일 수 있다.
- 세 preset 비교 결과, 현재 `Jetson Docker` 기본 운영 preset은 `light`로 유지하는 편이 맞다.
- 다음 `BNO08x IMU ON` 비교도 `light` baseline을 유지한 채 `Docker backend + host rtabmap_viz` 구조에서 반복하는 것이 현재 기준선이다.

## 해결 방법

- 현재 baseline 확인은 `Docker headless`로 본다.
- 누적 map을 눈으로 보고 싶을 때만 `host rtabmap_viz`를 붙인다.
- 즉, 운영 기준은 `Docker backend + host GUI`다.

## 남은 문제

- `Docker` 안 `rtabmap_viz`는 핵심 권한 문제를 수정했고, 내부 GUI 재기동과 parameter binding까지는 재확인했다.
- `D435i` 내장 IMU는 여전히 `Jetson kernel/HID/IIO` blocker 때문에 복구되지 않았다.
- 현재 `BNO08x`는 host 기준으로는 살아 있지만, 아직 정식 장착 전이라 `IMU ON/OFF` 비교는 다음 단계다.

## 다음 액션

1. 지금 구조를 기준선으로 문서화하고 반복 가능한 실행 절차를 고정한다.
2. `compare` preset은 후보로 남기고, `light` 대비 체감 이득이 있는지 필요할 때만 다시 본다.
3. 그 다음에만 `BNO08x`를 다시 붙여 `IMU OFF vs IMU ON`을 비교한다.
4. `Docker` GUI 자체를 꼭 살려야 할 이유가 생기면, 그때 OpenGL/GLX/EGL 이슈를 별도 트랙으로 판다.

## 다음 단계 준비

- `BNO08x IMU ON` 비교를 현재 운영 구조에 맞게 다시 정리했다.
- 기준은 아래처럼 고정한다.
  - `Docker backend + host rtabmap_viz`
  - baseline: `run_docker_rtabmap_stack.sh light`
  - IMU ON: `run_docker_rtabmap_stack_with_external_imu.sh light 2 relaxed /imu/data 15`
- host에서 반복 실행하기 쉽게 아래 wrapper도 추가했다.
  - [run_bno08x_ros2_imu_publisher.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_bno08x_ros2_imu_publisher.sh)
  - [run_camera_to_imu_static_tf.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_camera_to_imu_static_tf.sh)
  - [run_docker_rtabmap_stack_with_external_imu.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack_with_external_imu.sh)
