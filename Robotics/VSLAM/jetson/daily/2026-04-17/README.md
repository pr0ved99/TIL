# 2026-04-17 Jetson 작업 일지

## 결론

- 현재 `VSLAM` 작업은 `Jetson`에서 실제 실행 환경을 검증하는 단계로 넘어왔다.
- `Jetson` 접속은 `SSH`로 시작했지만, 지금은 `모니터 + 키보드 + 마우스`를 직접 연결한 상태에서 작업 중이다.
- 앞으로 `Jetson` 현장 진행 기록은 이 폴더 아래에서 분리 관리한다.

## 오늘 작업 한 줄 요약

- `Jetson`에서 `VSLAM`을 돌리기 위한 작업 흐름을 `원격 접속`에서 `직접 연결 기반 작업`까지 확장했다.
- 왜 이 작업을 먼저 했는가?
  - `D435i`, `RTAB-Map`, `GUI`, `장치 권한`, `USB 연결 상태`는 `Jetson` 현장에서 직접 보는 편이 훨씬 빠르기 때문이다.

## 현재 작업 형태

- 시작 형태:
  - `SSH` 접속으로 기본 환경 접근
- 현재 형태:
  - `Jetson`에 `모니터`, `키보드`, `마우스`를 직접 연결한 상태
- 의미:
  - 이제 `Jetson`은 단순 원격 대상이 아니라, `VSLAM` 실제 실행 장비로 다루기 시작한 상태다.

## 시간순 기록

### 현재 시점

- `Jetson`에서 `VSLAM`을 직접 돌리기 위한 작업 공간을 사용하기 시작했다.
- 기존 `PC` 중심 기록과 분리해서 `Jetson` 전용 폴더를 만들기로 정리했다.
- 이후 `Jetson`에서의 실행 로그, GUI 확인, 장치 문제, 성능 체감은 이 폴더 아래에 계속 누적한다.

### 기준선 확인

- `Jetson` 시스템 인벤토리 확인을 먼저 진행했다.
- 현재 장비는 `NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super`로 확인됐다.
- OS는 `Ubuntu 22.04.5 LTS`, 커널은 `5.15.185-tegra`, 아키텍처는 `aarch64`다.
- `L4T`는 `R36.5.0` 기준으로 보인다.
- `ROS 2 Humble`이 정상 설치되어 있고, `ros2 doctor --report`도 실행 가능했다.
- `Docker 29.4.0`, `Docker Compose v5.1.2`가 설치되어 있고 daemon도 `active (running)` 상태다.
- 루트 디스크는 `233G` 중 `21G` 사용, 메모리는 `7.4Gi` 중 `2.9Gi` 사용 상태였다.
- `lsusb` 기준으로 `Intel RealSense D435i`가 실제 연결된 상태도 확인했다.

### D435i native bring-up 재현

- `Jetson` native ROS 2 환경에서 `realsense2_camera rs_launch.py`를 다시 실행했다.
- `/camera/camera` 노드가 올라왔고, color/depth 관련 topic은 정상적으로 확인됐다.
- launch 로그에서 `Device USB type: 3.2`가 보여, 물리 연결 대역폭은 정상으로 보였다.
- 다만 같은 로그에서 아래 메시지가 함께 확인됐다.
  - `No HID info provided, IMU is disabled`
  - `HID Motion Sensor Failure! bad optional access`
- 현재 `Jetson`에서는 `D435i` 내장 IMU topic이 뜨지 않았고, 기준선은 우선 `IMU OFF`로 보는 편이 맞다.

### RTAB-Map baseline 1차 기동

- `Jetson` 기준 첫 안정 후보로 `424x240x15`, `DetectionRate=2`, `IMU OFF` 조합을 다시 실행했다.
- 카메라 launch와 `RTAB-Map` 경량 launch는 정상적으로 올라왔다.
- `/rtabmap/rgbd_odometry`, `/rtabmap/rtabmap` 노드와 관련 topic이 실제로 확인됐다.
- `rgbd_odometry` 품질값은 시작 직후 `0`에서 올라온 뒤, 대체로 `60~160`, 안정 구간에서는 `120~150` 정도로 관찰됐다.
- 즉, `Jetson`에서도 `D435i + RTAB-Map` baseline은 `IMU` 없이 1차 동작하는 상태다.

### GUI 실행 조건 확인

- 현재 `Codex/SSH` 성격의 shell에서는 `rtabmap_viz`가 `qt.qpa.xcb: could not connect to display` 오류로 열리지 않았다.
- 따라서 GUI 확인은 `Jetson`에 직접 연결한 그래픽 세션에서 해야 하고, 비GUI shell에서는 node/topic/log 위주로 확인하는 편이 맞다.

### IMU HID 1차 진단

- 사용자 확인상 `D435i`는 `SS USB` 케이블로 `Jetson`에 직결된 상태다.
- 다만 `lsusb -t` 기준 USB 토폴로지에서는 upstream에 `4-Port USB 3.0 Hub` 장치가 보이고, `D435i`는 그 경로 아래 `5000M`으로 매달린 형태로 보인다.
- USB 계층에서는 `Video` 인터페이스들과 함께 `Human Interface Device` 인터페이스도 `usbhid`로 보였다.
- 커널 로그 기준 `hidraw0`는 생성됐지만, `/sys/bus/iio/devices`는 비어 있어 IMU용 `IIO` 센서 노드가 올라오지 않았다.
- 같은 커널 로그에서 `Failed to query (GET_CUR) UVC control 1 on unit 3: -32`와 `Non-zero status (-71)`가 반복 확인됐다.
- 현재 1차 해석은 "`HID 인터페이스는 보이지만 sensor node가 안 뜬다` + `USB control 경로가 안정적이지 않을 수 있다`" 쪽이다.
- 따라서 현재는 `외부 허브 사용`을 원인으로 단정하지 않고, `IIO/HID sensor node` 문제와 `USB control` 경로 문제를 중심으로 본다.

## 오늘 관찰한 핵심 현상

- 이 장비는 문서상 가정이 아니라 실제 `Jetson Orin Nano` 실기 환경이 맞다.
- `ROS 2`, `Docker`, `D435i` 기본 요소가 이미 살아 있어서, 다음 단계는 설치보다 bring-up 재현에 집중하는 편이 맞다.
- 현재 기준으로 가장 중요한 사실은 `D435i`가 `lsusb`에서 바로 보이고 있다는 점이다.
- `Jetson` native 기준으로 `D435i color/depth`와 `RTAB-Map` baseline은 실제로 다시 재현됐다.
- 현재 가장 실용적인 `Jetson` baseline 후보는 `424x240x15 + DetectionRate 2 + IMU OFF`다.
- 지금 남은 핵심 이슈는 `D435i IMU HID failure`와 `GUI display context`다.
- IMU 진단 1차 결과로는 `HID` 인터페이스 자체는 보이지만 `IIO` 센서 노드가 비어 있었다.
- 사용자 확인상 물리 연결은 이미 직결 상태이므로, 다음 우선순위는 `IIO/HID sensor node`와 `udev / kernel log` 관점의 진단이다.

추가로, `Jetson` 작업은 `SSH`만으로 끝나지 않고 직접 화면을 보며 진행해야 하는 구간이 분명히 존재한다.
특히 아래 항목은 `Jetson` 현장에서 직접 확인하는 편이 유리하다.

- `realsense-viewer`
- `RViz`
- `rtabmap_viz`
- `USB/장치 인식`
- `GUI 체감 속도`

## 원인 가설

- 기존에는 `PC` 기준 로그와 설정만으로도 충분히 다음 단계로 갈 수 있다고 봤다.
- 하지만 실제 `Jetson`에서 `VSLAM`을 돌리려면 장치 상태와 GUI 조건을 같이 확인해야 하므로, 전용 진행 축이 필요하다고 판단했다.

## 해결 방법

- `Jetson` 전용 진행 기록 폴더를 새로 만들었다.
- 전체 진행상황 문서에는 현재 작업 환경이 `Jetson` 현장 검증 단계로 넘어왔다는 점을 반영했다.

## 오늘 만든/수정한 파일

- [Current_Progress_and_Open_Issues.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/docs/progress/Current_Progress_and_Open_Issues.md)
- [jetson/README.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/README.md)
- [jetson/daily/2026-04-17/README.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/daily/2026-04-17/README.md)
- [notes/environment/2026-04-17_Jetson_System_Inventory.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/notes/environment/2026-04-17_Jetson_System_Inventory.md)
- [guides/02_Jetson_D435i_Native_Bringup_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/02_Jetson_D435i_Native_Bringup_Guide.md)
- [guides/03_Jetson_RTABMap_Baseline_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/03_Jetson_RTABMap_Baseline_Guide.md)
- [guides/04_Jetson_D435i_IMU_Diagnosis_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/04_Jetson_D435i_IMU_Diagnosis_Guide.md)
- [notes/troubleshooting/2026-04-17_D435i_IMU_HID_Failure.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/notes/troubleshooting/2026-04-17_D435i_IMU_HID_Failure.md)
- [notes/troubleshooting/2026-04-17_RTABMap_Viz_XCB_Display_Error.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/notes/troubleshooting/2026-04-17_RTABMap_Viz_XCB_Display_Error.md)

## 남은 문제

- `Jetson`에서 실제 `D435i + RTAB-Map` 기준으로 어느 정도 해상도와 `DetectionRate`가 가장 실용적인지 더 검증이 필요하다.
- 현재 `D435i` 내장 IMU는 `HID Motion Sensor Failure`로 살아나지 않아, 별도 진단이 필요하다.
- USB 토폴로지상 upstream hub 장치는 보이지만, 사용자 확인상 물리 연결은 직결 상태다.
- 현재는 커널 로그의 `GET_CUR -32`, `status -71`와 `IIO` 노드 부재를 중심으로 보는 편이 맞다.
- `rtabmap_viz`는 non-GUI shell에서 열리지 않으므로, 직접 연결한 그래픽 세션에서 다시 확인해야 한다.
- `Jetson` 기준 `CPU`, `memory`, `GUI` 체감 속도는 이후 benchmark 기록으로 채워야 한다.

## 다음 액션

1. 현재 직결 상태에서 `04_Jetson_D435i_IMU_Diagnosis_Guide.md` 기준으로 `IIO/HID sensor node`와 커널 로그를 다시 확인한다.
2. 직접 연결한 그래픽 세션에서 `rtabmap_viz`와 `rqt_image_view`를 다시 확인한다.
3. 현재 baseline인 `424x240x15 + DetectionRate 2 + IMU OFF` 조합의 재현 로그와 benchmark를 쌓는다.

## 한 줄 회고

- 시스템 기준선과 `Jetson` baseline이 둘 다 확인됐으니, 이제부터는 설치보다 `IMU 진단`, `GUI 확인`, `baseline 고정`에 집중하면 된다.
