# 2026-04-17 D435i IMU HID Failure

## 증상

- `Jetson`에서 `realsense2_camera rs_launch.py`를 실행하면 color/depth는 올라오지만 IMU topic이 보이지 않는다.
- launch 로그에서 아래 문구가 확인됐다.

```text
No HID info provided, IMU is disabled
HID Motion Sensor Failure! bad optional access
```

## 현재까지 확인된 것

- `lsusb` 기준 `Intel RealSense D435i`는 연결되어 있다.
- launch 로그 기준 `Device USB type: 3.2`가 확인됐다.
- `/camera/camera` 노드는 올라오고 color/depth topic은 정상이다.
- 문제는 현재 `Jetson`에서 `D435i` 내장 IMU만 비활성화된 상태라는 점이다.
- 사용자 확인상 물리 연결은 `SS USB` 케이블로 `Jetson` 직결 상태다.
- 다만 `lsusb -t` 기준 USB 토폴로지에서는 `D435i`가 upstream `4-Port USB 3.0 Hub` 경로 아래 `5000M`으로 보인다.
- USB 계층에서는 `Human Interface Device` 인터페이스가 `usbhid`로 보였고, 커널 로그에는 `hidraw0` 생성도 확인됐다.
- 하지만 `/sys/bus/iio/devices`는 비어 있어 IMU용 `IIO` 센서 노드는 생성되지 않았다.
- 커널 로그에는 `Failed to query (GET_CUR) UVC control 1 on unit 3: -32`와 `Non-zero status (-71)`도 반복 확인됐다.
- 이후 `udev` 규칙을 추가해 `/dev/hidraw2`를 `root:plugdev 660`까지 정리했고, `sudo`로 `realsense2_camera`를 실행해도 결과는 같았다.
- 즉, `hidraw` 권한만의 문제는 아니었다.
- 그리고 `Jetson` 현재 커널 config를 직접 확인했을 때 아래가 나왔다.

```text
# CONFIG_HID_SENSOR_HUB is not set
```

- `/lib/modules/$(uname -r)` 아래에도 `hid_sensor_hub`, `hid_sensor_accel_3d`, `hid_sensor_gyro_3d` 관련 모듈이 보이지 않았다.
- 반면 사용자가 확인한 바에 따르면, 같은 `D435i` IMU는 `노트북`에서는 `yaw / pitch / roll`까지 정상 동작했다.

## 현재 판단

- 현재 `Jetson` baseline 운영은 우선 `IMU OFF`로 두는 편이 맞다.
- IMU는 `Jetson` 전용 진단 과제로 별도 분리한다.
- 현재 1순위 원인 후보는 더 구체적으로 `Jetson kernel의 HID sensor hub / IIO support 부재`다.
- 즉, 이 문제는 `노트북에서는 되고 Jetson에서는 안 되는 환경 차이`로 보는 편이 맞다.

## 다음에 바로 볼 항목

- `04_Jetson_D435i_IMU_Diagnosis_Guide.md` 순서대로 재현
- `check_d435i_imu_kernel_support.sh` 실행으로 현재 Jetson 커널 지원 상태를 다시 확인
- 노트북과 Jetson 간 `kernel / librealsense / ROS driver / HID/IIO support` 차이 비교
- 정말 `D435i IMU`를 Jetson에서 써야 한다면, `CONFIG_HID_SENSOR_HUB`가 켜진 커널 경로를 준비
