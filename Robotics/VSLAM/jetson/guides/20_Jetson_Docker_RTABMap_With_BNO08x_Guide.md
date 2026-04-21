# 20 Jetson Docker RTAB-Map With BNO08x Guide

## 목적

- `BNO08x`는 host에서 `/imu/data`로 publish하고,
- `D435i color/depth`와 `RTAB-Map`은 Docker 안에서 실행해서,
- `Jetson` 기준의 실제 `Docker + 외부 IMU` 실행 경로를 고정한다.

## 현재 전제

- `jetson-vslam:humble` 이미지는 이미 build 완료
- `docker` 그룹 권한 반영 완료
- host에서 `BNO08x` raw 값과 `/imu/data` publish가 이미 성공
- `D435i` 내장 IMU는 현재 Jetson 커널 이슈로 사용하지 않음

## 먼저 알면 좋은 점

- 지금 단계에서는 `BNO08x publisher`를 굳이 Docker 안으로 넣지 않는다.
- 이유는 host에서 이미 안정적으로 `/imu/data`가 확인됐고, `Docker`는 `host network`를 쓰므로 컨테이너에서도 그 topic을 바로 읽을 수 있기 때문이다.
- 현재 Docker backend는 `camera`, `rtabmap`, `dev-shell` service로 분리돼 있다.
- 따라서 운영 기준은 아래처럼 잡는다.
  - host: `BNO08x publisher`, `static TF`
  - Docker: `D435i color/depth`, `RTAB-Map`

## 0. GUI 접근 허용

이 단계는 Docker 컨테이너가 Jetson의 현재 X11 세션에 접근할 수 있게 만드는 단계다.

Jetson 로컬 GUI 터미널에서 한 번만:

```bash
xhost +local:docker
```

## 1. 터미널 1: host BNO08x publisher

이 단계는 외부 `BNO08x`를 host에서 읽어 `/imu/data`와 `/imu/mag`로 publish하는 단계다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_bno08x_ros2_imu_publisher.sh
```

## 2. 터미널 2: host static TF

이 단계는 `camera_link`와 `imu_link` 사이 고정 관계를 먼저 만들어 `RTAB-Map`이 IMU를 해석할 수 있게 하는 단계다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_camera_to_imu_static_tf.sh
```

## 3. 터미널 3: Docker D435i color/depth

이 단계는 Docker 안에서 `D435i` color/depth topic만 가볍게 publish하는 단계다.

```bash
cd ~/yh_ws/TIL
chmod +x ./Robotics/VSLAM/jetson/scripts/run_realsense_color_depth_in_docker.sh
./Robotics/VSLAM/jetson/scripts/run_realsense_color_depth_in_docker.sh light
```

## 4. 터미널 4: Docker RTAB-Map with external IMU

이 단계는 Docker 안 `RTAB-Map`이 host에서 이미 올라온 `/imu/data`를 읽게 만드는 단계다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack_with_external_imu.sh light 2 relaxed /imu/data 15
```

## 5. 실험 전에 빠르게 확인할 것

이 단계는 IMU topic이 host와 Docker 양쪽에서 실제로 보이는지 빠르게 확인하는 단계다.

새 터미널에서 host 또는 Docker 둘 중 편한 쪽으로 아래를 확인한다.

host:

```bash
source /opt/ros/humble/setup.bash
ros2 topic echo /imu/data --once
```

Docker:

```bash
cd ~/yh_ws/TIL/Robotics/VSLAM/jetson/docker
docker compose --env-file .env run --rm jetson-vslam-dev bash -lc 'source /opt/ros/humble/setup.bash && ros2 topic echo /imu/data --once'
```

## 6. 지금 단계에서 기대할 것

- Docker 안에서 `realsense2_camera`가 color/depth를 publish
- Docker 안에서 `RTAB-Map`이 `/imu/data`를 받아 `wait_imu_to_init:=true` 상태로 시작
- Docker backend 기준으로 `RTAB-Map`이 실제로 IMU topic을 읽고 동작함
- GUI가 필요하면 현재는 Docker 안 `rtabmap_viz`보다 host viewer 우회 구조를 먼저 보는 편이 더 안전함

## 7. 해석 기준

- 잘 된다:
  - Docker 안에서도 `BNO08x` IMU 입력이 실제로 연결된 것
  - 이제 `IMU OFF vs IMU ON` 비교 실험을 Docker 기준으로 반복할 수 있다

- `/imu/data`가 Docker에서 안 보인다:
  - host publisher가 꺼졌는지
  - `ROS_DOMAIN_ID`가 다르지 않은지
  - host network로 컨테이너가 뜨는지 먼저 다시 본다

- `RTAB-Map`이 IMU 대기에서 멈춘다:
  - `/imu/data` publish와 `camera_link -> imu_link` static TF가 둘 다 살아 있는지 먼저 확인한다

## 8. 다음 단계

- 이 경로가 실제로 올라오면
  - `IMU OFF`와 `IMU ON`을 같은 Docker 기준으로 비교
  - 맵 기울기, trajectory 안정성, 회전 구간 흔들림 비교
  - 이후 필요하면 launch 파일 수준으로 더 고정
