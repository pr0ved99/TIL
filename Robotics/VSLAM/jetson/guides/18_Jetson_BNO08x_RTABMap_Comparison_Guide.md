# 18 Jetson BNO08x RTAB-Map Comparison Guide

## 목적

- `RTAB-Map IMU OFF`와 `BNO08x IMU ON`을 **지금 기준 운영 구조**에서 비교한다.
- 현재 운영 구조는 `Docker backend + host rtabmap_viz frontend`다.
- 지금 단계 목표는 "`완전한 센서 융합`"이 아니라, **외부 IMU를 넣었을 때 맵 기울기와 자세 안정성에 큰 차이가 있는지 먼저 보는 것**이다.

## 현재 전제

- `D435i` 내장 IMU는 현재 Jetson에서 막혀 있다.
- 따라서 `IMU ON` 비교는 외부 `BNO08x` 기준으로 진행한다.
- 실험 중에는 `BNO08x`가 `D435i`에 **임시로 단단히 고정**되어 있어야 한다.
- 현재 Docker 기본 preset은 `light`로 확정된 상태다.

먼저 끝내야 하는 것:

- [17_Jetson_BNO08x_Temporary_Mount_and_TF_Guide.md](./17_Jetson_BNO08x_Temporary_Mount_and_TF_Guide.md)
- [16_Jetson_BNO08x_ROS2_IMU_Publisher_Guide.md](./16_Jetson_BNO08x_ROS2_IMU_Publisher_Guide.md)
- [21_Jetson_Docker_RTABMap_Baseline_Guide.md](./21_Jetson_Docker_RTABMap_Baseline_Guide.md)
- [22_Jetson_Docker_Backend_Host_RTABMapViz_Guide.md](./22_Jetson_Docker_Backend_Host_RTABMapViz_Guide.md)

## 비교 원칙

- preset, 해상도, DetectionRate, queue는 그대로 둔다.
- `IMU`만 바꿔서 비교한다.
- 가능한 한 같은 짧은 경로를 다시 움직인다.

현재 비교 기준:

- preset: `light`
- `424x240x15`
- `DetectionRate`: `2`
- `odom profile`: `relaxed`
- queue: `15`

## 빠른 결론

- `2026-04-21` 기준 자동 benchmark에서는 `IMU ON`이 odometry quality를 크게 끌어올리지는 않았다.
- 같은 `light`, `20s` 조건에서 `IMU OFF` quality avg는 `56.4`, `IMU ON` quality avg는 `57.1`이었다.
- 대신 사용자가 직접 본 RTAB-Map 화면에서는 IMU를 추가했을 때 맵 자세가 더 안정적으로 느껴졌다.
- 따라서 현재 결론은 **성능 숫자 개선보다는 회전/기울기 상황에서 자세 안정성 보조 효과가 있는 후보**로 보는 것이 맞다.

결과 문서:

- [`2026-04-21_12-00-54_docker_light_imu_on_off_comparison.md`](../assets/benchmarks/2026-04-21_12-00-54_docker_light_imu_on_off_comparison.md)

## 빠른 실행 명령어

이 섹션은 실제 비교할 때 바로 복붙하는 명령어 모음이다.

### 숫자 benchmark 비교

이 명령은 화면을 보지 않고 `IMU OFF -> IMU ON`을 같은 `light` 조건으로 연속 측정한다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_imu_comparison.sh both light 20
```

### 화면 비교 1: IMU OFF

이 명령은 `BNO08x`를 끄고 `D435i color/depth`만으로 Docker RTAB-Map backend를 띄운 뒤 host `rtabmap_viz`로 화면을 본다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/stop_docker_rtabmap_stack.sh
pkill -f '[r]tabmap_viz' || true
pkill -f '[b]no08x_ros2_imu_publisher.py' || true
pkill -f '[s]tatic_transform_publisher.*imu_link' || true

./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack.sh light
DISPLAY="${DISPLAY:-:1}" XAUTHORITY="${XAUTHORITY:-/run/user/1000/gdm/Xauthority}" \
./Robotics/VSLAM/jetson/scripts/run_rtabmap_viz_from_host_for_docker.sh
```

### 화면 비교 2: IMU ON

`IMU ON`은 센서값 publisher, `camera_link -> imu_link` TF, Docker RTAB-Map backend가 모두 필요하다. 아래 3개 터미널을 각각 열어 실행한다.

터미널 1:

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/stop_docker_rtabmap_stack.sh
pkill -f '[r]tabmap_viz' || true
pkill -f '[b]no08x_ros2_imu_publisher.py' || true
pkill -f '[s]tatic_transform_publisher.*imu_link' || true

./Robotics/VSLAM/jetson/scripts/run_bno08x_ros2_imu_publisher.sh
```

터미널 2:

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_camera_to_imu_static_tf.sh
```

터미널 3:

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack_with_external_imu.sh light 2 relaxed /imu/data 15
DISPLAY="${DISPLAY:-:1}" XAUTHORITY="${XAUTHORITY:-/run/user/1000/gdm/Xauthority}" \
./Robotics/VSLAM/jetson/scripts/run_rtabmap_viz_from_host_for_docker.sh
```

비교할 때는 `IMU OFF`와 `IMU ON`에서 같은 경로, 같은 속도, 같은 회전으로 움직인다.

## A. IMU OFF run

### 1. 기존 stack과 viewer 정리

이 단계는 이전 run이 남아 있어 비교가 섞이지 않게 정리하는 단계다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/stop_docker_rtabmap_stack.sh
pkill -f '[r]tabmap_viz' || true
```

### 2. 터미널 1: Docker baseline backend 시작

이 단계는 `D435i color/depth + rgbd_odometry + rtabmap`을 Docker 안에서 baseline 설정으로 올리는 단계다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack.sh light
```

### 3. 터미널 2: host rtabmap_viz 실행

이 단계는 Docker가 publish한 topic을 host에서 읽어 누적 map을 눈으로 확인하는 단계다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_rtabmap_viz_from_host_for_docker.sh
```

### 관찰 항목

- 맵이 기울어지는지
- 회전할 때 trajectory가 흔들리는지
- `rtabmap_viz` 체감 부드러움
- 짧은 경로 누적이 자연스러운지

## B. IMU ON run with BNO08x

### 1. 기존 stack과 viewer 정리

이 단계는 `IMU OFF` run과 완전히 분리해 비교할 수 있게 정리하는 단계다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/stop_docker_rtabmap_stack.sh
pkill -f '[r]tabmap_viz' || true
pkill -f '[b]no08x_ros2_imu_publisher.py' || true
pkill -f '[s]tatic_transform_publisher.*imu_link' || true
```

### 2. 터미널 1: host BNO08x publisher

이 단계는 외부 `BNO08x`를 host에서 읽어 `/imu/data`, `/imu/mag`로 publish하는 단계다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_bno08x_ros2_imu_publisher.sh
```

### 3. 터미널 2: host camera_link -> imu_link static TF

이 단계는 `camera_link`와 `imu_link`의 고정 관계를 먼저 만들어 `RTAB-Map`이 IMU를 해석할 수 있게 하는 단계다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_camera_to_imu_static_tf.sh
```

### 4. 터미널 3: Docker backend with external IMU

이 단계는 baseline과 같은 Docker 구조를 유지하면서, `RTAB-Map`만 `/imu/data`를 읽게 바꾸는 단계다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_stack_with_external_imu.sh light 2 relaxed /imu/data 15
```

### 5. 터미널 4: host rtabmap_viz 실행

이 단계는 `IMU ON` 상태의 누적 map을 같은 host viewer에서 보는 단계다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_rtabmap_viz_from_host_for_docker.sh
```

## C. 비교할 것

### 숫자 benchmark를 먼저 남긴다

이 단계는 수동 GUI 비교와 별도로, 같은 preset에서 `IMU OFF`와 `IMU ON`을 연속 측정해 로그를 남기는 단계다.

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_docker_rtabmap_imu_comparison.sh both light 20
```

왜 이 명령을 쓰는가:

- `IMU OFF`와 `IMU ON`이 같은 `light` preset으로 측정된다.
- `topic hz`, `odom quality`, `delay`, `tegrastats`, Docker logs가 같은 형식으로 저장된다.
- 결과는 `jetson/assets/benchmarks/` 아래에 `imu_off`, `imu_on`, `imu_on_off_comparison.md`로 남는다.
- `BNO08x`는 I2C 장치라 동시에 두 publisher가 읽으면 오류가 날 수 있으므로, 실행 전에는 기존 publisher 중복을 정리하는 것이 안전하다.

### GUI에서 체감 비교를 한다

아래만 보면 된다.

1. 맵 기울기
2. 처음 자세 안정화 시간
3. 천천히 회전할 때 흔들림
4. 같은 짧은 경로에서 trajectory 형태
5. `rtabmap_viz` 체감

## D. 지금 단계에서의 해석 기준

- `IMU ON`이 더 낫다:
  - 맵이 덜 기울고
  - 회전 구간이 덜 흔들리고
  - trajectory가 더 차분하다

- 차이가 거의 없다:
  - 지금 RTAB-Map baseline은 시각 정보만으로도 충분한 환경일 수 있다
  - 또는 임시 장착/TF가 아직 거칠 수 있다

- 오히려 나빠진다:
  - `BNO08x` 축 정렬이 틀렸을 가능성
  - 임시 고정이 약해서 카메라-IMU 상대 자세가 흔들렸을 가능성
  - `camera_link -> imu_link`를 0으로 둔 단순화가 아직 너무 거칠었을 가능성

## E. 이번 단계에서 인정할 한계

- 아직 로봇 본체 기준 정식 장착이 아니다.
- `camera_link -> imu_link`도 임시 0 transform 가정이다.
- 따라서 지금 결과는 **정식 센서 융합 최종판**이 아니라, "`외부 IMU가 대략 도움 되는 방향인가`"를 보는 1차 실험이다.

## F. 다음 단계

- 이번 비교에서 `IMU ON`이 긍정적으로 보이면
  - `BNO08x` 정식 장착 위치 논의
  - 실제 `imu_link` 기준 정리
  - 필요하면 `robot_localization` 전 단계 준비

- 차이가 애매하면
  - 임시 고정 품질과 축 정렬을 먼저 다시 본다
