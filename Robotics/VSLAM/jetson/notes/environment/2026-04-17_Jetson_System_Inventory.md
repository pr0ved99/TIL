# 2026-04-17 Jetson 시스템 인벤토리

## 결론

- 현재 작업 장비는 `NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super`다.
- `Ubuntu 22.04.5 LTS`, `Linux 5.15.185-tegra`, `aarch64` 환경으로 확인됐다.
- `L4T R36.5.0`, `ROS 2 Humble`, `Docker 29.4.0`이 이미 준비되어 있다.
- `lsusb` 기준 `Intel RealSense D435i`가 실제 연결된 상태다.

## 시스템 기본 정보

- hostname: `ubuntu`
- architecture: `arm64` / `aarch64`
- OS: `Ubuntu 22.04.5 LTS`
- kernel: `5.15.185-tegra`
- hardware model: `NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super`

## Jetson / L4T 정보

- `/etc/nv_tegra_release`
  - `R36 (release), REVISION: 5.0`
  - 해석: `L4T R36.5.0`

## ROS 2 정보

- distro: `humble`
- `ros2 doctor --report` 실행 가능
- middleware: `rmw_fastrtps_cpp`

## Docker 정보

- Docker version: `29.4.0`
- Docker Compose version: `v5.1.2`
- docker.service: `active (running)`

## 저장공간 / 메모리

- root filesystem: `233G` 중 `21G` 사용, `200G` 여유
- memory: `7.4Gi` 중 `2.9Gi` 사용, `4.2Gi` available
- swap: `3.7Gi`

## 연결 장치

- `lsusb` 기준 확인된 주요 장치:
  - `Intel RealSense D435i`
  - `Realtek 4-Port USB 3.0 Hub`

## 작업 경로

- home: `/home/jetson`
- main workspace: `/home/jetson/yh_ws`
- TIL repo: `/home/jetson/yh_ws/TIL`

## 현재 판단

- `Jetson` 기본 환경은 이미 많이 준비된 상태다.
- 지금 우선순위는 설치보다 `D435i native bring-up 재현`과 `RTAB-Map baseline 재현`이다.
