# 2026-04-19 Jetson 작업 일지

## 결론

- 현재 `Jetson`에서는 `D435i` 내장 IMU가 아직 직접 시각화 가능한 상태는 아니지만, IMU topic만 살아나면 바로 `비행기 viewer`로 볼 수 있게 `ROS 2 IMU topic -> aircraft viewer` 경로를 준비했다.
- 즉, 오늘은 `D435i IMU`가 바로 동작한 날이 아니라, **`D435i IMU`가 살아났을 때 바로 확인할 수 있는 준비 절차를 만든 날**로 보는 편이 맞다.
- 다음 1순위는 여전히 `D435i IMU HID` 문제를 먼저 좁히는 것이다.

## 오늘 작업 한 줄 요약

- `D435i` 내장 IMU를 `BNO08x`처럼 비행기 시각화에 바로 쓸 수 있는지 검토했고, 현재 Jetson 상태를 고려해 `ROS 2 IMU viewer` 스크립트와 가이드를 먼저 준비했다.
- 왜 이 작업을 먼저 했는가?
  - IMU topic만 살아나면 바로 시각화로 넘어가도록 준비해두면, 이후 진단과 확인 속도가 훨씬 빨라지기 때문이다.

## 현재 작업 형태

- 문서/스크립트 준비 작업은 `SSH`에서도 가능하지만, 실제 viewer 확인은 `Jetson` 로컬 그래픽 세션이 필요하다.
- 따라서 오늘은 `준비 작업은 shell`, `실제 GUI 확인은 이후 IMU 복구 후 로컬 세션`이라는 기준으로 정리했다.

## 시간순 기록

### 현재 시점

- 사용자 질문은 "`D435i`의 IMU로도 비행기 시각화를 해볼 수 있는가?"였다.
- 현재 판단은 "`가능은 하지만 지금 바로는 아니고, D435i IMU topic이 살아나야 한다`" 쪽이다.
- 이유는 `Jetson` 실측 기준으로 아직 `D435i` IMU가 `HID Motion Sensor Failure` 상태이기 때문이다.

### 14:33

- 실제로 `realsense2_camera rs_launch.py`를 `enable_gyro:=true`, `enable_accel:=true`, `unite_imu_method:=1`로 다시 올려 `D435i IMU` topic이 살아나는지 확인했다.
- launch 자체는 성공했고 `D435i` color/depth는 정상으로 올라왔다.
- 하지만 launch 로그에서 아래가 다시 확인됐다.

```text
No HID info provided, IMU is disabled
Intel RealSense D435I #116622071600 - HID Motion Sensor Failure! bad optional access
```

- 이어서 `ros2 topic echo /camera/camera/imu --once`를 실행했지만, `/camera/camera/imu` topic은 실제로 publish되지 않았다.
- 즉, `2026-04-19` 시점에도 `Jetson`에서 `D435i` 내장 IMU는 아직 viewer 입력으로 쓸 수 없는 상태다.

### 14:36

- 이번에는 "`정말 권한 문제인가?`"를 분리해서 확인했다.
- 먼저 `lsusb -t` 기준으로 `D435i`의 `Human Interface Device` 인터페이스 자체는 보였다.
- 특히 `/sys/class/hidraw/hidraw2`는 아래 경로로 연결돼 있어, 현재 `D435i`의 HID 노드가 실제로 생성되는 것까지는 확인했다.

```text
/sys/devices/platform/bus@0/3610000.usb/usb2/2-1/2-1.2/2-1.2:1.5/0003:8086:0B3A.0007
HID_NAME=Intel(R) RealSense(TM) Depth Camera 435i Intel(R) RealSense(TM) Depth Camera 435i
```

- 하지만 `hidraw` 디바이스 권한은 아래처럼 전부 `root:root`, mode `600`이었다.

```text
crw------- 1 root root ... /dev/hidraw2
```

- 실제로 `jetson` 사용자로 `/dev/hidraw0`, `/dev/hidraw1`, `/dev/hidraw2`를 열어보면 모두 `PermissionError: [Errno 13] Permission denied`가 났다.
- 반면 color/depth용 `/dev/video*`는 `root:video`로 열려 있어서 일반 사용자 접근이 가능했다.
- 즉 현재 상태는 "`카메라 비디오 스트림은 user 권한으로 접근 가능하지만, HID 쪽은 user 권한으로 막혀 있음`"에 가깝다.

### 14:38

- `udev` 쪽도 같이 확인했다.
- 현재 시스템의 `/etc/udev/rules.d`에는 `realsense`용 규칙 파일이 없었고, 설치된 `ros-humble-librealsense2`, `ros-humble-realsense2-camera` 패키지 목록에도 `99-realsense-libusb.rules` 같은 파일은 포함돼 있지 않았다.
- 따라서 현재 `Jetson` 상태에서는 `D435i` HID 디바이스가 생성되더라도, 일반 사용자가 읽을 수 있도록 permissions/group을 열어주는 규칙이 빠져 있을 가능성이 높다.
- `rs-enumerate-devices -s`도 일반 사용자로 실행 시 동일하게 `HID Motion Sensor Failure! bad optional access`를 출력했다.

### 14:39

- 임시로 `sudo chmod 666 /dev/hidraw2`를 준 뒤 `realsense2_camera`를 다시 올려 봤다.
- 하지만 결과는 같았다.

```text
No HID info provided, IMU is disabled
Intel RealSense D435I #116622071600 - HID Motion Sensor Failure! bad optional access
```

- 즉, `hidraw` 권한 하나만 풀어준다고 바로 IMU가 살아나는 문제는 아니었다.
- 이후 `99-realsense-hidraw.rules`를 직접 추가했고, 현재 `/dev/hidraw2`는 실제로 아래처럼 바뀌었다.

```text
crw-rw---- 1 root plugdev ... /dev/hidraw2
```

- `jetson` 사용자는 이미 `plugdev` 그룹에 들어가 있으므로, **지금 시점에서는 최소한 `hidraw` 파일 권한 자체는 1차 정리된 상태**다.
- 그런데도 `IMU` topic은 여전히 뜨지 않았으므로, 원인은 단순 user permission보다 더 아래 단계에 있을 가능성이 높다.

### 14:41

- 추가로 확인한 결과 `/sys/bus/iio/devices` 아래에는 여전히 아무 장치도 없었다.
- `industrialio` 코어는 보이지만, `hid_sensor_hub` / `hid_sensor_accel_3d` / `hid_sensor_gyro_3d` 같은 커널 쪽 흔적은 현재 사용자 수준 확인 결과 보이지 않았다.
- 따라서 현재 가설은 아래처럼 정리된다.
  - `hidraw` 권한 문제는 일부 있었고 지금은 어느 정도 해소됨
  - 하지만 핵심 blocker는 여전히 `Jetson` 커널/HID/IIO 경로 쪽일 가능성이 더 큼

### 14:42

- 마지막으로 `root` 권한으로도 같은 launch를 다시 올려 봤다.
- 하지만 `root`에서도 결과는 완전히 같았다.

```text
No HID info provided, IMU is disabled
Intel RealSense D435I #116622071600 - HID Motion Sensor Failure! bad optional access
```

- 이어서 `sudo -E bash -lc 'source /opt/ros/humble/setup.bash && ros2 topic list | grep imu'`까지 확인했지만, `imu` 관련 topic은 여전히 나타나지 않았다.
- 이 결과로 인해 현재 판단은 더 명확해졌다.
  - **일반 사용자 권한 부족은 더 이상 핵심 원인으로 보기 어렵다**
  - 실제 blocker는 `Jetson` 쪽 `HID sensor / IIO / kernel path`에 더 가깝다

### 커널 blocker 확인

- 이후 `Jetson` 커널 config를 직접 확인했다.
- 현재 실측 결과는 아래와 같았다.

```text
CONFIG_HIDRAW=y
# CONFIG_HID_SENSOR_HUB is not set
CONFIG_IIO=y
```

- 즉, 현재 `Jetson` 커널에서는 `HID sensor hub`가 아예 꺼져 있다.
- `/lib/modules/$(uname -r)` 아래에도 `hid_sensor_hub`, `hid_sensor_accel_3d`, `hid_sensor_gyro_3d` 관련 모듈이 보이지 않았다.
- 반면 사용자가 확인한 바에 따르면, 같은 `D435i` 내장 IMU는 `노트북`에서는 `yaw / pitch / roll`까지 정상 동작했다.
- 이 조합을 같이 보면 현재 결론은 거의 명확하다.
  - `D435i` 센서 자체 불량보다는 `Jetson` 환경 차이
  - 그중에서도 `Jetson kernel/HID/IIO support`가 핵심 blocker

### 공식 RealSense udev rules 재적용 후 재시험

- `realsense-viewer`에서는 "`99-realsense-libusb.rules`가 없거나 오래됐다"는 경고가 떴다.
- 그래서 공식 `RealSense` rules `v1.1` 내용을 `/etc/udev/rules.d/99-realsense-libusb.rules`로 다시 반영한 상태를 기준으로 재시험했다.
- 하지만 결과는 그대로였다.

`rs-enumerate-devices -s`:

```text
Intel RealSense D435I #116622071600 - HID Motion Sensor Failure! bad optional access
```

`realsense2_camera rs_launch.py`:

```text
No HID info provided, IMU is disabled
Intel RealSense D435I #116622071600 - HID Motion Sensor Failure! bad optional access
```

- 즉, `official udev rules`를 맞춘 뒤에도 `D435i` 내장 IMU는 여전히 살아나지 않았다.
- 이 재시험으로 인해 지금은 `udev rules`보다 `Jetson kernel/HID/IIO support`가 핵심 blocker라는 판단이 더 강해졌다.

### 방향 전환

- 따라서 `2026-04-19` 시점부터는 `D435i` 내장 IMU를 계속 파는 것보다, 이미 host에서 살아 있는 외부 `BNO08x`를 `ROS 2 /imu/data`로 연결하는 쪽이 더 우선순위가 높다고 판단했다.
- 즉, `D435i IMU`는 별도 backlog로 두고, 실제 `RTAB-Map IMU ON/OFF` 비교 실험은 우선 `BNO08x`로 진행하는 흐름으로 전환했다.

### 이번에 이어서 만든 것

- `BNO08x`를 바로 `sensor_msgs/Imu`로 publish하는 스크립트를 추가했다.
- 이 스크립트는 host `venv`에서 센서를 읽고, 동시에 아래를 publish한다.
  - `/imu/data`
  - `/imu/mag`
- 같이 `ROS 2` topic 확인과 `ros2_imu_aircraft_viewer.py` 연결까지 한 번에 따라칠 수 있는 가이드도 정리했다.

### BNO08x ROS 2 publisher 스모크 테스트

- 새 publisher를 host `venv + ROS 2` 조합으로 짧게 실행해 봤다.
- 실제 로그 기준으로 아래가 바로 확인됐다.

```text
opened BNO08x over I2C bus=1 address=0x4b
publishing IMU on /imu/data frame_id=imu_link rate=10.0Hz
publishing magnetic field on /imu/mag
first sample: accel=... gyro=... mag=... quat=...
```

- 동시에 별도 터미널에서 `ros2 topic list | grep -E '^/imu'`를 확인했을 때 아래 topic이 실제로 보였다.

```text
/imu/data
/imu/mag
```

- 즉, `2026-04-19` 기준으로 외부 `BNO08x`는 host `venv`에서 raw 값 확인을 넘어서, **이제 실제 `ROS 2` IMU topic publisher로도 동작하는 상태**가 됐다.

### BNO08x ROS 2 viewer 1차 수정

- `/imu/data`를 `ros2_imu_aircraft_viewer.py`에 바로 연결해 보니, viewer 내부에서 빈 topic name으로 임시 subscription을 만드는 버그가 있었다.
- 이 부분을 수정해서, 이제는 viewer가 시작 시 `""` 빈 topic 때문에 죽지 않고 전달된 topic으로 바로 subscribe 하도록 정리했다.
- 비GUI 백엔드 기준 스모크 테스트에서는 더 이상 `InvalidTopicNameException`이 재현되지 않았다.

### BNO08x ROS 2 viewer 지연 원인 정리

- 이후 publisher를 `50 Hz -> 100 Hz`, viewer를 `20 Hz -> 30 Hz`로 올려도 체감 지연이 크게 줄지 않는다는 피드백이 있었다.
- 원인을 다시 보면, 기존 viewer는 화면 갱신 때마다 `rclpy.spin_once()`로 콜백을 하나씩만 소비하는 구조였다.
- 즉, publisher가 더 빨라도 viewer가 backlog를 따라잡지 못하면 체감이 크게 좋아지지 않을 수 있었다.
- 그래서 viewer를 `ROS callback background thread + 최신 값 snapshot` 구조로 바꿔, 화면 갱신 속도와 ROS message 수신을 분리했다.
- 이 수정 후에는 `rate`를 높였을 때 실제로 최신 자세를 더 잘 따라갈 가능성이 커졌다.

### BNO08x host aircraft viewer 지연 완화

- 이후 같은 종류의 지연이 host `bno08x_aircraft_viewer.py`에도 있다는 피드백이 있었다.
- 확인해보니 이 스크립트는 원래 `matplotlib` animation update 안에서 직접 `bno.quaternion`, `bno.acceleration`, `bno.gyro`를 읽고 있었다.
- 즉, `센서 polling`과 `화면 redraw`가 한 루프에 묶여 있어서, redraw가 느리면 최신 자세 반영도 같이 밀릴 수 있는 구조였다.
- 그래서 이 viewer도 아래처럼 구조를 바꿨다.
  - `BNO08x`는 백그라운드 thread에서 계속 polling
  - 화면은 최신 snapshot만 그리기
  - `--sensor-rate`와 `--rate`를 분리
- 이제는 예를 들어 `--sensor-rate 100 --rate 30`처럼 실행해서, 센서는 더 자주 읽고 화면은 적당한 속도로만 그릴 수 있다.

### BNO08x compass viewer 추가

- 이후 "`나침반 기능도 가능한가`"라는 질문이 나왔다.
- 현재 판단은 아래와 같다.
  - `BNO08x`: 가능
  - `D435i` 내장 IMU: 현재 Jetson에서는 사실상 불가
- 그래서 host `venv`에서 바로 띄울 수 있는 `BNO08x compass viewer`를 새로 추가했다.
- 이 viewer는 `raw magnetometer`만 단독으로 쓰기보다, `BNO08x`가 내부 sensor fusion으로 만든 `quaternion yaw`를 중심으로 heading을 보여준다.
- 화면에는 아래를 같이 보여준다.
  - 현재 heading 각도
  - 방위 `N / NE / E / ...`
  - 시작 시점 대비 상대 방향
  - 현재 `mag` 벡터와 자기장 크기
- 필요하면 `--heading-offset`과 `--declination`으로 수동 보정도 할 수 있게 해뒀다.

### Docker + BNO08x + RTAB-Map 실행 경로 확인

- 이후 질문은 "`값 잘 받는 건 확인했으니, 이제 Docker로 RTAB-Map을 진행해보자`"였다.
- 먼저 실제 연결 상태부터 다시 확인했다.
  - `jetson-vslam:humble` 컨테이너 안에서 `realsense2_camera`, `rtabmap_launch`, `rtabmap_ros` 패키지가 실제로 보였다.
  - 컨테이너 안에서도 `/dev/video0`, `/dev/i2c-1`가 마운트된 상태를 확인했다.
- 그다음 host에서 `BNO08x` publisher를 실제로 올린 뒤, 별도 컨테이너에서 아래를 확인했다.

```text
ros2 topic echo /imu/data --once
```

- 결과적으로 `Docker` 컨테이너 안에서 host가 publish한 `/imu/data`를 실제로 읽을 수 있었다.
- 이어서 `Docker` 안에서 `realsense2_camera rs_launch.py enable_color:=true enable_depth:=true ...`를 짧게 다시 올려 본 결과, color/depth 기준 bring-up도 정상으로 재현됐다.
- 즉, 현재 가장 현실적인 운영 기준은 아래처럼 정리된다.
  - host: `BNO08x publisher`, `static TF`
  - Docker: `D435i color/depth`, `RTAB-Map`
- 이 흐름을 반복 실행하기 쉽게 하기 위해 아래 wrapper와 가이드를 추가했다.
  - `run_realsense_color_depth_in_docker.sh`
  - `run_rtabmap_with_external_imu_in_docker.sh`
  - `20_Jetson_Docker_RTABMap_With_BNO08x_Guide.md`

### Docker baseline을 IMU 없이 다시 확인

- 이후 목표를 다시 정리했다.
- 지금 바로 필요한 것은 `IMU ON` 비교가 아니라, **`D435i` 이미지 토픽만으로 Docker 안에서 `RTAB-Map` baseline이 실제로 도는지 확인하는 것**이다.
- 그래서 `BNO08x`는 잠시 빼고, 아래 경로만 다시 확인했다.
  - Docker 안 `realsense2_camera`
  - Docker 안 `RTAB-Map`
  - `IMU OFF`
- 이 확인을 쉽게 하기 위해 아래 wrapper와 가이드를 추가했다.
  - `run_rtabmap_baseline_in_docker.sh`
  - `21_Jetson_Docker_RTABMap_Baseline_Guide.md`
- 실제 재시험 결과:
  - Docker 안 `realsense2_camera`는 color/depth 기준으로 정상 기동
  - Docker 안 `rgbd_odometry`, `rtabmap`도 정상 기동
  - `quality`는 초기 `0` 이후 바로 `640~700`대까지 올라감
- 즉, **backend 관점에서는 Docker 안 `D435i image-only RTAB-Map baseline`이 실제로 재현됐다**고 봐도 된다.
- 다만 `rtabmap_viz`는 Docker 안에서 여전히 아래 계열의 OpenGL/NvRm 오류가 보였다.

```text
QOpenGLWidget: Failed to create context
NvRmMemInitNvmap failed with Permission denied
qt.qpa.backingstore: composeAndFlush: makeCurrent() failed
```

- 따라서 현재 운영 기준은 이렇게 정리한다.
  - baseline 확인: Docker `headless` 기준
  - GUI 문제: 별도 이슈로 추적

### Docker GUI software rendering 재시험

- 혹시 `rtabmap_viz`를 software rendering으로라도 띄울 수 있는지 추가로 다시 시도했다.
- 아래 환경 변수를 넣고 `rtabmap_viz:=true`로 Docker 안 실행을 재시험했다.

```text
LIBGL_ALWAYS_SOFTWARE=1
QT_OPENGL=software
QT_XCB_GL_INTEGRATION=none
MESA_LOADER_DRIVER_OVERRIDE=llvmpipe
QT_QUICK_BACKEND=software
```

- 하지만 결과는 여전히 아래와 같았다.

```text
QXcbIntegration: Cannot create platform OpenGL context, neither GLX nor EGL are enabled
QOpenGLWidget: Failed to create context
qt.qpa.backingstore: composeAndFlush: QOpenGLContext creation failed
qt.qpa.backingstore: composeAndFlush: makeCurrent() failed
```

- 즉, `2026-04-19` 기준으로는 Docker 안 `RTAB-Map backend`는 재현됐지만, `rtabmap_viz GUI`는 GPU 경로와 software rendering 우회 모두 아직 실패한 상태다.

### 임시 고정 실험 준비

- 이후 질문은 "`BNO08x`가 아직 정식 장착된 상태는 아닌데, `D435i`와 같이 잡고 `RTAB-Map` 비교 실험을 해도 되는가?"였다.
- 현재 판단은 "`손으로 같이 드는 건 비추천이고, 최소한 D435i 몸체에 임시로 단단히 고정해야 한다`" 쪽이다.
- 그래서 다음 단계용으로 아래 두 갈래를 정리했다.
  - `BNO08x`를 `D435i`에 임시 고정하고 `camera_link -> imu_link` static TF를 준비하는 가이드
  - 그 상태로 `RTAB-Map IMU OFF`와 `BNO08x IMU ON`을 비교하는 가이드
- 실행 부담을 줄이기 위해 외부 IMU topic을 넣어 `RTAB-Map`을 올리는 helper 스크립트도 같이 추가했다.

### 준비한 것

- `sensor_msgs/Imu` topic을 바로 받아 비행기 viewer로 보여주는 스크립트를 추가했다.
- 이 viewer는 두 경로를 모두 지원한다.
  - 메시지에 quaternion이 있으면 그대로 사용
  - quaternion이 없으면 `gyro + accel`로 간단한 complementary filter를 돌려 대략적인 자세를 추정

### 같이 정리한 것

- `D435i IMU`용 비행기 viewer 가이드도 새로 만들었다.
- 현재 blocker와 실행 순서를 같이 적어, `IMU` topic이 살아났을 때 바로 따라칠 수 있게 만들었다.
- 그리고 `BNO08x -> /imu/data` publisher 경로도 추가해, 이제는 외부 IMU 기준으로 실제 `ROS 2` 연동을 바로 시작할 수 있게 됐다.

## 오늘 관찰한 핵심 현상

- `BNO08x`는 quaternion을 바로 주기 때문에 비행기 시각화로 연결하기 쉬웠다.
- 반면 `D435i IMU`는 현재 `Jetson`에서 topic 자체가 불안정하고, orientation도 바로 오지 않을 수 있어 중간 추정 단계가 필요하다.
- 오늘 재시험 기준으로도 `D435i`는 color/depth는 정상이나 IMU topic은 실제로 publish되지 않았다.
- 오늘 권한 진단 기준으로는, 단순 launch 옵션 문제가 아니라 `hidraw` 접근 권한과 `udev rules` 부재가 실제 원인 후보로 더 강해졌다.
- 다만 실제 재시험 후에는 "`권한만 고치면 해결`" 수준은 아니고, 권한 문제 뒤에 `커널/HID/IIO` 쪽 blocker가 더 남아 있는 상태로 보는 편이 맞다.
- 특히 `root`로도 재현됐기 때문에, 현재는 권한 이슈보다 `Jetson`의 커널/HID/IIO 경로를 더 우선 원인 후보로 본다.
- 따라서 실험 우선순위는 `D435i IMU 복구`보다 `BNO08x ROS 2 publish -> viewer -> RTAB-Map 비교`로 옮겨가는 편이 더 효율적이다.
- 따라서 지금은 "`시각화 불가`"가 아니라 "`시각화 경로는 준비됐고, 입력 topic이 아직 안 살아 있다`"가 더 정확한 표현이다.

## 원인 가설

- 현재 `D435i IMU`가 바로 viewer로 안 가는 핵심 원인은 시각화 코드 부재가 아니라, `Jetson`에서의 `HID / IIO` 문제다.
- 그중에서도 오늘 재확인 결과로는 `hidraw` 권한과 `realsense`용 `udev` 규칙 부재가 가장 먼저 의심된다.
- 다만 `hidraw` 권한을 실제로 열어 본 뒤에도 증상이 유지됐으므로, 현재는 `hidraw` 권한보다 `커널의 HID sensor/IIO 초기화 경로`를 더 우선 원인 후보로 본다.
- `root`로도 같은 증상이 재현됐기 때문에, 지금은 `sudo로 해결되는 권한 문제`라고 보기는 어렵다.
- 즉, viewer보다 먼저 해결해야 할 건 `IMU bring-up`이다.

## 해결 방법

- `D435i`용 `ROS 2 IMU aircraft viewer` 스크립트를 만들었다.
- 가이드에는 현재 blocker와 함께, IMU topic이 살아났을 때 바로 실행할 명령을 순서대로 정리했다.
- 실제 재시험 결과까지 봤으므로, 당분간은 `D435i IMU`를 바로 쓰기보다 `04_Jetson_D435i_IMU_Diagnosis_Guide.md` 기준 진단과 외부 `BNO08x` 경로를 병행하는 편이 맞다.

## 오늘 만든/수정한 파일

- [ros2_imu_aircraft_viewer.py](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/ros2_imu_aircraft_viewer.py)
- [15_Jetson_D435i_IMU_Aircraft_Viewer_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/15_Jetson_D435i_IMU_Aircraft_Viewer_Guide.md)
- [bno08x_ros2_imu_publisher.py](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/bno08x_ros2_imu_publisher.py)
- [16_Jetson_BNO08x_ROS2_IMU_Publisher_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/16_Jetson_BNO08x_ROS2_IMU_Publisher_Guide.md)
- [run_rtabmap_with_external_imu.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_rtabmap_with_external_imu.sh)
- [17_Jetson_BNO08x_Temporary_Mount_and_TF_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/17_Jetson_BNO08x_Temporary_Mount_and_TF_Guide.md)
- [18_Jetson_BNO08x_RTABMap_Comparison_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/18_Jetson_BNO08x_RTABMap_Comparison_Guide.md)
- [bno08x_compass_viewer.py](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/bno08x_compass_viewer.py)
- [19_Jetson_BNO08x_Compass_Viewer_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/19_Jetson_BNO08x_Compass_Viewer_Guide.md)
- [run_realsense_color_depth_in_docker.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_realsense_color_depth_in_docker.sh)
- [run_rtabmap_with_external_imu_in_docker.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_rtabmap_with_external_imu_in_docker.sh)
- [20_Jetson_Docker_RTABMap_With_BNO08x_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/20_Jetson_Docker_RTABMap_With_BNO08x_Guide.md)
- [run_rtabmap_baseline_in_docker.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/run_rtabmap_baseline_in_docker.sh)
- [21_Jetson_Docker_RTABMap_Baseline_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/21_Jetson_Docker_RTABMap_Baseline_Guide.md)
- [guides/README.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/README.md)
- [scripts/README.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/README.md)

## 남은 문제

- `D435i` 내장 IMU는 여전히 `Jetson`에서 `No HID info provided, IMU is disabled`, `HID Motion Sensor Failure` 문제를 해결하지 못했다.
- 현재 `/dev/hidraw2`는 `root:plugdev 660`까지 정리됐지만, IMU topic은 여전히 publish되지 않는다.
- 시스템에 `realsense`용 `udev` rules 파일은 직접 추가했지만, 그것만으로는 해결되지 않았다.
- `root`로 재시험해도 `/camera/camera/imu`가 뜨지 않는다.
- `/sys/bus/iio/devices`가 비어 있어 `IIO` 경로가 아직 안 살아 있다.
- 따라서 새 viewer는 아직 end-to-end 실기 검증 전이다.
- `yaw`는 magnetometer가 없는 D435i 특성상 드리프트할 수 있다.
- `unite_imu_method:=1`를 줘도 IMU stream 자체가 안 살아 있으므로, 현재 문제는 viewer나 launch 옵션보다 `HID / IIO` 경로 쪽이다.

## 다음 액션

1. [17_Jetson_BNO08x_Temporary_Mount_and_TF_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/17_Jetson_BNO08x_Temporary_Mount_and_TF_Guide.md) 기준으로 `BNO08x`를 `D435i`에 임시 고정한다.
2. [16_Jetson_BNO08x_ROS2_IMU_Publisher_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/16_Jetson_BNO08x_ROS2_IMU_Publisher_Guide.md) 기준으로 `/imu/data`를 유지한다.
3. [18_Jetson_BNO08x_RTABMap_Comparison_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/18_Jetson_BNO08x_RTABMap_Comparison_Guide.md) 기준으로 `IMU OFF`와 `IMU ON`을 비교한다.
4. `D435i IMU`는 별도 backlog로 유지하고, 필요할 때만 다시 커널/HID/IIO 진단을 이어간다.

## 한 줄 회고

- 오늘은 `D435i IMU`를 바로 시각화한 날은 아니지만, `IMU`만 살아나면 즉시 확인할 수 있는 준비 경로를 만들어 둔 날이다.
