# Jetson VSLAM Docker

## 결론

- 현재 `Jetson`에는 `Docker CE 29.4.0`, `Docker Compose v5.1.2`, `NVIDIA Container Toolkit 1.16.2`가 이미 설치되어 있다.
- `/etc/docker/daemon.json`에는 `nvidia` runtime도 등록돼 있다.
- 여기 Docker 폴더는 **"시스템 재설치"가 아니라, 기존 설치 상태를 활용해 `Jetson`용 `VSLAM` backend를 반복 가능하게 고정하는 실행 구조**다.
- `2026-04-20` 기준으로는 `camera`, `rtabmap`, `dev-shell`을 서비스로 분리했고, `dev image`와 `runtime image`도 나눠서 관리한다.

## 현재 기준선

- host OS: `Ubuntu 22.04.5 LTS`
- host arch: `aarch64`
- L4T: `R36.5.0`
- ROS 2: `Humble`
- Compose project: `jetson-vslam`
- 현재 운영 기준: `Docker backend + host rtabmap_viz frontend`
- 현재 경량 baseline preset: `light`
  - `424x240x15`
  - `DetectionRate 2`
  - `queue 15`

## 구성 파일

- [`Dockerfile`](./Dockerfile)
  - `ROS 2 Humble` 기반 개발용 이미지
  - `RTAB-Map`, `RViz2`, `rqt_image_view`, `BNO08x` Python 의존성까지 포함
- [`Dockerfile.runtime`](./Dockerfile.runtime)
  - `camera`와 `rtabmap` 서비스가 공통으로 쓰는 실행 전용 이미지
  - `realsense2_camera`, `rtabmap_ros` 중심으로만 구성
- [`compose.yaml`](./compose.yaml)
  - `jetson-vslam-dev`, `jetson-vslam-camera`, `jetson-vslam-rtabmap` 서비스 정의
  - `host network`, `nvidia runtime`, `X11`, `/dev`, `/run/udev`, host `i2c` group 반영
  - `ROS_HOME`, `ROS_LOG_DIR`, `rtabmap.db`를 `tmpfs` 경로(`/tmp`)로 보내는 구조 포함
- [`.env.example`](./.env.example)
  - 사용자/경로/화면 변수 기본값
- [`presets/`](./presets/README.md)
  - `light / medium / compare` preset 파일 모음
  - 해상도, DetectionRate, queue, benchmark duration 기준값 저장

## 사용 순서

1. [`08_Jetson_Docker_Enablement_Guide.md`](../guides/08_Jetson_Docker_Enablement_Guide.md)로 `docker` 그룹 권한과 기본 실행을 먼저 확인한다.
2. Jetson 로컬 GUI 세션에서 `xhost +local:docker`를 실행한다.
3. `docker compose build jetson-vslam-dev jetson-vslam-camera`로 개발/실행 이미지를 만든다.
4. 개발 쉘이 필요하면 `run_jetson_vslam_docker.sh`를 쓴다.
5. baseline backend는 아래처럼 서비스 단위로 띄운다.
   - `run_realsense_color_depth_in_docker.sh light`
   - `run_rtabmap_baseline_in_docker.sh light`
6. 두 서비스를 detached로 한 번에 띄우고 싶으면 `run_docker_rtabmap_stack.sh light`를 쓴다.
7. 성능 로그까지 남기고 싶으면 `run_docker_rtabmap_benchmark.sh light 20`을 쓴다.
8. benchmark가 끝나면 각 폴더의 `90_summary.env`, `91_summary.md`와 root `docker_benchmark_index.csv`가 자동 갱신된다.

## 왜 이렇게 잡았는가

- 지금 프로젝트 기준으로 중요한 건 "`Jetson native baseline`을 유지하면서도, 같은 ROS/RTAB-Map 개발환경을 반복 가능하게 만드는 것"이다.
- 그래서 `Jetson` Docker 구조도 아래처럼 역할을 나눴다.
  - `dev-shell`: 패키지 확인, 디버깅, 개발 작업
  - `camera`: `D435i` color/depth publish
  - `rtabmap`: `rgbd_odometry + rtabmap` backend
- 또 `dev image`와 `runtime image`를 분리해서, baseline 실행 경로에는 `rviz2`, 편집기, `BNO08x` Python 패키지 같은 개발성 의존성을 빼두었다.
- 반복 실험에서는 `rtabmap.db`와 ROS log가 디스크에 쌓이지 않도록 `/tmp` `tmpfs`로 보내서 I/O 부담도 줄였다.

## 주의사항

- `D435i IMU HID` 문제는 native에서도 남아 있으므로, Docker 안에서 바로 해결된다고 가정하면 안 된다.
- `rtabmap_viz`는 현재 Docker 안 OpenGL 문제가 남아 있으므로, `Jetson host`에서 보는 편이 더 안전하다.
- `privileged: true`는 bring-up과 장치 접근을 쉽게 하기 위한 선택이다. 나중에 안정화되면 필요한 장치만 더 좁히는 편이 좋다.
- preset 파일은 기준선 저장용이다.
  - 임시 override는 wrapper 인자로 하되, 기준이 바뀌면 `presets/`를 함께 갱신하는 편이 좋다.
