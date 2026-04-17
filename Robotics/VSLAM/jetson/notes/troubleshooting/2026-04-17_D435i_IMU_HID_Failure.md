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

## 현재 판단

- 현재 `Jetson` baseline 운영은 우선 `IMU OFF`로 두는 편이 맞다.
- IMU는 `Jetson` 전용 진단 과제로 별도 분리한다.
- 현재 1순위 원인 후보는 `USB control` 경로 문제 또는 `HID sensor node / IIO` 노출 문제다.

## 다음에 바로 볼 항목

- 현재 직결 상태를 유지한 채 같은 가이드 재현
- `04_Jetson_D435i_IMU_Diagnosis_Guide.md` 순서대로 재현
- `journalctl -k -b --no-pager | grep -iE 'realsense|hid|uvc|iio'`
- `/sys/bus/iio/devices` 존재 여부
- launch 중복 실행 또는 `realsense-viewer` 동시 실행 여부
