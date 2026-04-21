# 21 Jetson Docker RTAB-Map Baseline Guide

## 목적

- `BNO08x`나 다른 IMU 없이,
- `D435i` 이미지 토픽만으로
- `Docker` 안에서 `RTAB-Map` baseline이 실제로 도는지 확인한다.

## 현재 전제

- 목표는 `성능 비교`가 아니라 `Docker에서도 기본 흐름이 뜨는지` 확인하는 것이다.
- 즉, 지금은 가장 단순한 경로만 본다.
  - Docker 안 `realsense2_camera`
  - Docker 안 `RTAB-Map`
  - `IMU OFF`

## 먼저 알면 좋은 점

- 현재 `D435i` 내장 IMU는 Jetson에서 안 되므로, baseline은 무조건 `IMU OFF`다.
- 현재 기본 Docker camera preset은 `light = 424x240x15 + IMU OFF`다.
- 현재 기본 Docker RTAB-Map queue size는 `15`다.
- camera, rtabmap, dev-shell은 이제 `compose` 서비스로 분리돼 있다.
- baseline wrapper는 내부적으로 `compose run --rm`이 아니라 `service up`을 사용한다.
- `RTAB-Map` odometry가 실제로 돌려면 `D435i` camera TF는 끄지 않는 편이 안전하다.
- image-only baseline은 `imu_topic:=/imu/disabled`를 명시적으로 넘겨, launch 기본값 `/imu/data`가 숨어서 붙지 않게 정리했다.
- GUI 확인은 Jetson 로컬 그래픽 세션에서 하는 편이 좋다.
- `2026-04-20` 후반 재검증 기준으로, Docker 안 `rtabmap_viz`의 핵심 blocker는 `GLX/EGL 부재`보다 `video/render` 그룹 누락으로 인한 `NvRmMemInitNvmap failed with Permission denied`였다.
- 현재 `compose`는 `video/render` 그룹을 컨테이너에 추가하도록 수정돼 있고, 내부 GUI도 다시 시작해 parameter/service 연결까지 정상 확인했다.
- 다만 운영 기준으로는 여전히 `Docker backend + host rtabmap_viz`가 더 단순하고 반복하기 쉽다.
- GUI를 다시 시도하려면 먼저 한 번은 아래를 실행해두는 편이 좋다.

이 명령은 Docker 컨테이너가 Jetson의 현재 X11 세션에 접근할 수 있게 만든다.

```bash
xhost +local:docker
```

가능하면 Jetson 성능 모드도 먼저 고정한다.
이 명령은 Jetson이 낮은 전력 모드로 묶이지 않게 해서 baseline이 쓸데없이 흔들리는 것을 줄인다.

```bash
sudo nvpmodel -m 2
sudo jetson_clocks
```

## 1. 터미널 1: Docker D435i color/depth

이 단계는 Docker 안에서 `D435i`의 color/depth topic만 가볍게 올리는 단계다.

```bash
cd ~/yh_ws/TIL
chmod +x ./Robotics/VSLAM/jetson/scripts/run_realsense_color_depth_in_docker.sh
./Robotics/VSLAM/jetson/scripts/run_realsense_color_depth_in_docker.sh light
```

다른 해상도로 시험하려면:

이 명령은 같은 wrapper를 쓰되 color/depth preset만 바꾸는 방식이다.

```bash
./Robotics/VSLAM/jetson/scripts/run_realsense_color_depth_in_docker.sh medium
./Robotics/VSLAM/jetson/scripts/run_realsense_color_depth_in_docker.sh light 640x360x15 640x360x15
```

## 2. 터미널 2: Docker RTAB-Map baseline

이 단계는 Docker 안에서 `rgbd_odometry`와 `rtabmap`을 headless로 실행하는 단계다.

```bash
cd ~/yh_ws/TIL
chmod +x ./Robotics/VSLAM/jetson/scripts/run_rtabmap_baseline_in_docker.sh
./Robotics/VSLAM/jetson/scripts/run_rtabmap_baseline_in_docker.sh light
```

queue size까지 직접 줄이려면:

이 명령은 viewer 없이 queue size만 더 낮춰 메모리와 지연을 조금 더 줄이는 용도다.

```bash
./Robotics/VSLAM/jetson/scripts/run_rtabmap_baseline_in_docker.sh light 2 relaxed false 10
```

`rtabmap_viz`까지 다시 시도하려면:

이 명령은 Docker 안 GUI까지 같이 띄우는 방식이다.
현재는 `video/render` 그룹 누락과 image-only IMU remap 버그를 수정한 뒤 다시 기동과 parameter binding을 확인한 상태다.
그래도 문제가 재현되면 아래를 먼저 본다.
- `xhost +local:docker`
- Jetson 로컬 X11 세션인지
- container group에 `video`, `render`가 실제로 추가됐는지

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_rtabmap_baseline_in_docker.sh light 2 relaxed true 15
```

detached로 한 번에 띄우고 싶다면:

이 명령은 `camera`와 `rtabmap`을 service 단위로 background에서 같이 올리는 방식이다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack.sh light
```

## 3. 빠른 확인

이 단계는 GUI를 보기 전에 backend가 실제로 살아 있는지 확인하는 단계다.

새 터미널에서:

```bash
source /opt/ros/humble/setup.bash
ros2 node list
ros2 topic list | grep -E 'camera|rtabmap|odom'
```

## 4. 기대 결과

- Docker 안에서 `realsense2_camera`가 color/depth를 publish
- Docker 안에서 `RTAB-Map`이 `IMU OFF` 상태로 시작
- `rgbd_odometry`와 `rtabmap` 프로세스가 유지됨
- `quality` 로그가 0에서 시작한 뒤 다시 올라옴
- 반복 비교가 목적이면 [`23_Jetson_Docker_Preset_and_Benchmark_Guide.md`](./23_Jetson_Docker_Preset_and_Benchmark_Guide.md) 기준으로 preset/benchmark 구조를 함께 쓰는 편이 좋다.

## 5. 지금 단계에서 볼 것

- launch가 죽지 않고 유지되는지
- `rgbd_odometry`, `rtabmap`이 실제로 도는지
- 이미지가 들어오면서 map/trajectory가 움직이는지
- `IMU OFF` 기준 baseline이 Docker 안에서도 재현되는지
- Docker 안 GUI가 다시 이상하면, host `rtabmap_viz` 우회 구조를 먼저 본다.
  - 관련 가이드: [`22_Jetson_Docker_Backend_Host_RTABMapViz_Guide.md`](./22_Jetson_Docker_Backend_Host_RTABMapViz_Guide.md)

## 6. 해석 기준

- 잘 된다:
  - 이제 Docker 기준 baseline은 확보된 것
  - 그다음에만 `BNO08x`를 다시 붙여 비교한다

- camera는 뜨는데 RTAB-Map이 안 뜬다:
  - `camera_info`, `aligned_depth_to_color`, `color/image_raw` topic부터 다시 본다

- GUI만 안 뜬다:
  - `xhost +local:docker`
  - `DISPLAY`
  - Jetson 로컬 그래픽 세션인지
  - `video/render` group이 container에 들어갔는지
  - image-only baseline에서 `imu:=/imu/disabled`로 실행되는지
  부터 다시 본다
  - 지금도 운영 기준은 backend 확인과 host GUI 우회가 더 안정적이다

## 7. 다음 단계

- 이 baseline이 Docker 안에서 확인되면
  - 그 다음에만 `BNO08x IMU ON` 실험으로 넘어간다
  - 즉 순서는 `Docker baseline 확보 -> Docker IMU 비교`다
