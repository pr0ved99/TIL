# 2026-04-18 Jetson 작업 일지

## 결론

- `Jetson` 로컬 그래픽 세션에서 `D435i` 카메라 노드와 `rtabmap_viz` GUI를 실제로 띄우는 데 성공했다.
- 전날 확인했던 `xcb` 오류는 `SSH/비GUI shell` 문제였고, `Jetson` 화면에서 직접 연 터미널에서는 `RTAB-Map GUI` 확인이 가능했다.
- 현재 기준선은 가이드 5 기본값인 `424x240x15 + DetectionRate 2 + IMU OFF`로 보는 편이 맞다.

## 오늘 작업 한 줄 요약

- `05_Jetson_Local_RTABMap_GUI_Check_Guide.md` 순서대로 `Jetson`에서 직접 `카메라 노드 + rtabmap_viz`를 확인했다.
- 왜 이 작업을 먼저 했는가?
  - `Jetson`에서 실제로 GUI가 뜨는지 확인돼야 이후 맵 누적, 체감 속도, 화면 증빙을 계속 쌓을 수 있기 때문이다.

## 현재 작업 형태

- `Jetson`에 `모니터 + 키보드 + 마우스`를 직접 연결한 상태에서 진행했다.
- 이번 작업은 `SSH`가 아니라 `Jetson` 바탕화면에서 직접 연 터미널이 필요했다.

## 시간순 기록

### 00:15

- `Jetson` 로컬 그래픽 세션에서 `rtabmap_viz` 창이 실제로 열린 상태를 확인했다.
- 스크린샷 기준으로 좌측에는 특징점이 표시된 입력 영상과 odometry 뷰가 보이고, 우측에는 `3D Map`과 trajectory가 정상적으로 그려졌다.
- 사용자 메모상 해상도는 `424x240x15`였을 가능성이 높고, 가이드 5 기본값 기준으로는 `DetectionRate 2`, `IMU OFF` 조합으로 기록하는 편이 자연스럽다.

### 01:09

- `06_Jetson_Baseline_Benchmark_Guide.md` 기준으로 benchmark 산출물을 실제로 만들었다.
- `01_camera_launch.log`, `02_rtabmap_launch.log`, `06_color_hz.txt`, `07_aligned_depth_hz.txt`, `12_tegrastats.txt`, `13_rtabmap_viz.png`까지 저장된 상태다.
- `quality / delay`는 `02_rtabmap_launch.log`에서 실제로 충분히 뽑을 수 있었다.
  - 전체 log 기준 `quality 0~299`, 평균 `174.2`
  - 대부분은 약 `95~205`
  - `delay 0.099~0.270s`, 평균 `0.150s`
- color와 aligned depth는 둘 다 대체로 `15 Hz` 근처로 유지됐다.
- 다만 이번 run에서는 guide가 `/odom_info`, `/odom`으로 적혀 있어 `05_odom_info.txt`, `08_odom_hz.txt`는 실제 데이터가 비었다.
  실제 topic은 `/rtabmap/odom_info`, `/rtabmap/odom`이었고, 가이드는 이후 수정했다.

### 02:10

- `Jetson`의 Docker 상태를 실제로 다시 점검했다.
- 확인 결과 `Docker CE 29.4.0`, `Docker Compose v5.1.2`, `nvidia-container-toolkit 1.16.2`가 이미 설치돼 있었다.
- `/etc/docker/daemon.json`에도 `nvidia` runtime이 등록돼 있어, 시스템 레벨 설치 자체는 거의 끝난 상태로 보는 편이 맞다.
- 다만 `jetson` 사용자는 아직 `docker` 그룹에 포함되지 않아 `docker info`가 `permission denied`로 막혔다.
- 이 상태를 반영해 `Jetson`용 `VSLAM` Docker 뼈대와 enablement 가이드를 새로 만들었다.

### 14:10

- 외부 `GY-BNO08x` IMU를 `Jetson`에 연결한 뒤, 1차 값 확인 준비를 시작했다.
- 재스캔 결과 `i2c-1`에서 `0x4B`가 실제로 보였고, 외부 `BNO08x`의 I2C 인식 자체는 성공한 상태로 정리했다.
- Python 쪽도 `pip`, `venv`, `adafruit_bno08x`, `board`, `busio`가 없어 바로 값 읽기 스크립트를 돌릴 수는 없었다.
- 그래서 먼저 `BNO08x` bus scan 스크립트와 `I2C/UART` 겸용 값 확인 스크립트, 그리고 Jetson용 bring-up 가이드를 추가했다.
- 이후 host `venv`에서 `accel / gyro / mag / quaternion` 값이 실제로 출력되는 것까지 확인했다.
- 다만 프로젝트 운영 기준은 결국 `Docker`이므로, 이 host `venv`는 센서/배선 검증용 1회 확인 수단으로만 두고, 이후는 Docker 이미지 안에 의존성을 포함시키는 방향으로 정리했다.
- Docker 컨테이너 안 첫 재시험에서는 `/dev/i2c-1`에 `Permission denied`가 발생했다.
- 원인은 host 장치가 `root:i2c`(`gid 116`)이고, 컨테이너 사용자에 그 보조 그룹이 없었던 점이었다.
- 이를 반영해 `compose.yaml`에 host `i2c` group(`116`)을 추가했다.

### 16:05

- 외부 `BNO08x`는 host `venv`에서 이미 재현 가능한 상태이므로, 팀원이 바로 실행할 수 있게 별도 핸드오프 문서를 만들었다.
- 이번 핸드오프는 "`host에서 I2C 주소 확인 -> raw IMU 값 확인 -> 그 다음에만 Docker 단계로 이동`" 흐름을 고정하는 데 목적이 있다.
- 관련 실행 문서를 `handoffs/` 아래에 따로 묶어, 현재 상태와 필요한 가이드를 한 번에 볼 수 있게 정리했다.

### 16:35

- raw 값이 숫자로만 보이면 축 반응을 해석하기 불편하므로, host `venv` 기준 `BNO08x` live plot 스크립트와 가이드를 추가했다.
- 이번 시각화는 `accel / gyro / mag` 시계열과 `roll / pitch / yaw`를 함께 보는 방식으로 잡았다.
- 목적은 `ROS 2`로 가기 전에 정지 시 gyro bias, 기울임 방향, yaw 반응을 빠르게 눈으로 확인하는 것이다.

### 16:55

- 그래프만으로는 자세 변화를 직관적으로 읽기 어려울 수 있어, quaternion을 바로 `비행기 모양 3D viewer`에 반영하는 스크립트를 추가했다.
- 이번 viewer는 정교한 CAD 모델이 아니라, `roll / pitch / yaw` 반응을 빠르게 검증하기 위한 단순 와이어프레임 형태다.
- 목적은 실물을 기울였을 때 화면의 비행기가 같은 방향으로 기울고 회전하는지 확인하는 것이다.

### 17:05

- `Downloads`에 있던 `IMG_1660.MOV`를 `Jetson assets` 아래로 복제해, 현재 `BNO08x` 시각화 흐름과 연결되는 참고 영상으로 정리했다.
- 단순 파일 보관이 아니라, `assets/videos/2026-04-18_bno08x_visualization_reference/` 폴더를 만들고 설명용 `README.md`를 같이 두는 방식으로 정리했다.
- 이렇게 해두면 이후 팀원이나 미래의 내가 영상을 다시 볼 때 "이게 왜 저장됐는지"를 바로 이해할 수 있다.

## 오늘 관찰한 핵심 현상

- `rtabmap_viz`는 비GUI shell에서 실패했지만, `Jetson` 로컬 그래픽 세션에서는 정상적으로 표시됐다.
- 즉, 현재 병목은 "`RTAB-Map GUI가 안 되는가`"가 아니라 "`어떤 세션에서 실행했는가`"에 더 가깝다.
- GUI 기준으로도 `RTAB-Map`이 실제 맵과 trajectory를 그리고 있다는 증빙을 확보했다.
- 숫자 로그 기준으로도 현재 baseline은 실제로 반복 기록 가능한 수준까지 왔다.

## 원인 가설

- 기존에는 `rtabmap_viz` 오류가 Jetson 성능이나 패키지 문제일 수도 있다고 봤다.
- 하지만 이번 결과로 보면 핵심 원인은 `DISPLAY/xcb`가 없는 비GUI shell에서 실행했던 점에 더 가깝다.

## 해결 방법

- `Jetson` 바탕화면에서 직접 연 터미널에서 가이드 5 순서대로 실행하는 방식을 기준 절차로 삼는다.
- `SSH`나 원격 IDE 터미널에서는 GUI 확인을 하지 않고, node/topic/log 확인용으로만 쓴다.
- baseline 숫자 기록이 필요하므로, 다음부터는 `06_Jetson_Baseline_Benchmark_Guide.md` 기준으로 로그와 `tegrastats`까지 같이 남긴다.
- `/rtabmap` namespace를 반영하도록 benchmark 가이드를 수정했다.
- Docker 쪽은 재설치가 아니라 기존 설치 상태를 활용하는 방향으로 정리했다.
- 즉, 먼저 `docker` 그룹 권한만 열고, 그 다음 `compose`로 `Jetson VSLAM` 개발 컨테이너를 띄우는 흐름이 자연스럽다.
- 외부 `BNO08x`는 아직 값 확인 성공 전 단계이므로, 현재는 "`연결 방식 식별 -> Python 환경 준비 -> 1차 값 확인`" 순서로 가는 것이 맞다.
- 지금은 연결 방식 식별이 끝났고, 실제로는 "`Python 환경 준비 -> 1차 값 확인`" 단계로 바로 넘어가면 된다.

## 오늘 만든/수정한 파일

- [2026-04-18 Jetson 작업 일지](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/daily/2026-04-18/README.md)
- [Current_Progress_and_Open_Issues.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/docs/progress/Current_Progress_and_Open_Issues.md)
- [06_Jetson_Baseline_Benchmark_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/06_Jetson_Baseline_Benchmark_Guide.md)
- [RTABMap_Baseline_Benchmark_Template.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/RTABMap_Baseline_Benchmark_Template.md)
- [2026-04-18 benchmark README](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline/README.md)
- [Jetson Videos README](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/videos/README.md)
- [2026-04-18 BNO08x visualization video README](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/videos/2026-04-18_bno08x_visualization_reference/README.md)
- [Jetson Docker README](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/docker/README.md)
- [08_Jetson_Docker_Enablement_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/08_Jetson_Docker_Enablement_Guide.md)
- [09_Jetson_VSLAM_Docker_Bringup_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/09_Jetson_VSLAM_Docker_Bringup_Guide.md)
- [check_jetson_docker_preflight.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/check_jetson_docker_preflight.sh)
- [run_jetson_vslam_docker.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_jetson_vslam_docker.sh)
- [11_Jetson_BNO08x_First_Value_Check_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/11_Jetson_BNO08x_First_Value_Check_Guide.md)
- [BNO08x Host Venv First Check Handoff](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/handoffs/BNO08x_Host_Venv_First_Check_Handoff.md)
- [scan_bno08x_buses.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/scan_bno08x_buses.sh)
- [bno08x_value_check.py](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/bno08x_value_check.py)
- [13_Jetson_BNO08x_Live_Plot_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/13_Jetson_BNO08x_Live_Plot_Guide.md)
- [bno08x_live_plot.py](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/bno08x_live_plot.py)
- [14_Jetson_BNO08x_Aircraft_Viewer_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/14_Jetson_BNO08x_Aircraft_Viewer_Guide.md)
- [bno08x_aircraft_viewer.py](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/bno08x_aircraft_viewer.py)

## 증빙 자료

- [Jetson RTAB-Map GUI screenshot](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/screenshots/2026-04-18_jetson_rtabmap_viz_gui_baseline_424x240x15_detectionrate2_imuoff.png)
- [2026-04-18 benchmark screenshot](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/benchmarks/2026-04-18_rtabmap_baseline/13_rtabmap_viz.png)
- [2026-04-18 BNO08x visualization reference video](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/videos/2026-04-18_bno08x_visualization_reference/2026-04-18_bno08x_visualization_reference.mov)

## 남은 문제

- `D435i` 내장 IMU는 여전히 `HID Motion Sensor Failure`로 살아나지 않아 별도 진단이 필요하다.
- 이번엔 `quality`, `delay`, `rate`, `tegrastats`까지 확보했지만, 짧은 경로 반복 비교는 아직 더 필요하다.
- `424x240x15` 설정은 이번 benchmark log로 확인됐다.
- `trajectory`와 `체감 부드러움`은 다음 run에서 더 의식적으로 메모를 남겨야 한다.
- Docker는 시스템 설치는 돼 있지만 `jetson` 사용자의 socket 권한이 아직 열리지 않아 실제 `compose build`까지는 바로 검증하지 못했다.
- 외부 `BNO08x`는 현재 `i2c-1 / 0x4B`로 잡혔으므로, 다음 병목은 배선이 아니라 Python 의존성 설치다.
- Python 기본 패키지(`pip`, `venv`)도 아직 없어 bring-up 전에 한 번 설치가 필요하다.
- host `venv`에서는 이미 값 확인에 성공했으므로, 다음 병목은 이제 Docker 이미지 rebuild와 컨테이너 안 재현 여부다.

## 다음 액션

1. `08_Jetson_Docker_Enablement_Guide.md` 기준으로 `docker` 그룹 권한과 `hello-world`를 먼저 확인한다.
2. `09_Jetson_VSLAM_Docker_Bringup_Guide.md` 기준으로 `Jetson VSLAM` 개발 컨테이너를 실제로 빌드한다.
3. 컨테이너 안에서 `realsense2_camera`, `rtabmap_ros`, `rviz2` 패키지 가용성을 먼저 확인한다.
4. 그 다음 native baseline과 Docker baseline을 같은 조건에서 비교한다.
5. 외부 `BNO08x`는 `11_Jetson_BNO08x_First_Value_Check_Guide.md` 기준으로 `i2c-1 / 0x4B`에서 바로 1차 값 확인을 진행한다.
6. 그 다음은 `12_Jetson_BNO08x_Docker_Check_Guide.md` 기준으로 같은 값을 Docker 컨테이너 안에서도 다시 확인한다.

즉시 실행할 때는 `05`로 GUI를 띄운 뒤 `06` 가이드로 로그와 benchmark를 남기는 흐름이 가장 자연스럽다.
후보 비교를 시작할 때는 `07` 가이드로 `DetectionRate 3`를 먼저 보는 편이 가장 깔끔하다.

## 한 줄 회고

- `Jetson`에서 `rtabmap_viz` GUI가 실제로 떴다는 증빙을 확보하면서, 이제 GUI 실행 여부가 아니라 baseline 품질 비교로 넘어갈 수 있게 됐다.
