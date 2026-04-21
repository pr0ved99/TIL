# 15 Jetson D435i IMU Aircraft Viewer Guide

## 목적

- `D435i`의 IMU topic을 받아 `비행기 모양 3D viewer`로 자세 변화를 본다.
- `BNO08x` viewer와 달리, 이 가이드는 `ROS 2 sensor_msgs/Imu` topic을 입력으로 쓴다.

## 중요한 현재 상태

- 현재 `Jetson` 실측 기준으로 `D435i` 내장 IMU는 아직 바로 쓰기 어렵다.
- 즉, 이 가이드는 **지금 당장 100% 재현 완료된 절차**라기보다, `D435i IMU` topic이 살아나는 순간 바로 시도할 수 있게 준비한 viewer 절차다.
- 현재 blocker는 [04_Jetson_D435i_IMU_Diagnosis_Guide.md](./04_Jetson_D435i_IMU_Diagnosis_Guide.md)에서 보는 `HID Motion Sensor Failure`다.

## 이 viewer가 하는 일

- `sensor_msgs/Imu` 메시지에 orientation quaternion이 있으면 그 값을 그대로 사용한다.
- orientation이 비어 있으면, `gyro + accel`로 간단한 complementary filter를 돌려 대략적인 `roll / pitch / yaw`를 추정한다.

주의:

- `D435i`는 magnetometer가 없으므로 `yaw`는 드리프트할 수 있다.
- 따라서 이 viewer는 `정밀 orientation 측정기`라기보다, `IMU topic이 살아 있고 회전 반응이 대체로 맞는지` 보는 확인 도구에 가깝다.

## 1. 먼저 D435i IMU가 살아 있는지 확인

가이드:

- [02_Jetson_D435i_Native_Bringup_Guide.md](./02_Jetson_D435i_Native_Bringup_Guide.md)
- [04_Jetson_D435i_IMU_Diagnosis_Guide.md](./04_Jetson_D435i_IMU_Diagnosis_Guide.md)

IMU topic 예시:

- `/camera/camera/imu`

## 2. 터미널 1에서 D435i launch

```bash
source /opt/ros/humble/setup.bash
ros2 launch realsense2_camera rs_launch.py \
  enable_color:=true \
  enable_depth:=true \
  enable_gyro:=true \
  enable_accel:=true \
  unite_imu_method:=1 \
  enable_sync:=true \
  align_depth.enable:=true
```

## 3. 터미널 2에서 IMU topic이 실제로 보이는지 확인

```bash
source /opt/ros/humble/setup.bash
ros2 topic list | grep -E 'imu|gyro|accel'
ros2 topic echo /camera/camera/imu --once
```

## 4. viewer 실행

```bash
source /opt/ros/humble/setup.bash
python3 /home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/ros2_imu_aircraft_viewer.py --topic /camera/camera/imu --rate 20
```

## 5. 화면에서 무엇을 볼지

- 파란 비행기
  - 현재 IMU 자세
- 회색 점선 비행기
  - viewer 시작 순간 기준 자세
- 실선 축
  - 현재 body `X / Y / Z`
- 점선 축
  - 고정 world `X / Y / Z`
- 아래 텍스트
  - `mode=...`
  - `frame=...`
  - `roll / pitch / yaw`

## 6. `mode` 해석

- `message_quaternion`
  - IMU 메시지 안 quaternion을 그대로 쓰는 상태
- `estimated_from_gyro_accel`
  - orientation이 비어 있어, viewer 안에서 `gyro + accel`로 자세를 추정하는 상태

현재 `D435i`라면 보통 두 번째 쪽이 더 현실적이다.

## 7. 추천 확인 동작

1. 카메라를 평평하게 두고 시작
2. 앞쪽을 들고 내리면서 `pitch` 반응 확인
3. 좌우로 기울이며 `roll` 반응 확인
4. 천천히 회전시키며 `yaw`가 어느 정도 따라오는지 확인

## 8. 안 되면 먼저 볼 것

1. `/camera/camera/imu` topic이 실제로 존재하는지
2. launch 로그에 아래가 뜨지 않는지

```text
No HID info provided, IMU is disabled
HID Motion Sensor Failure! bad optional access
```

3. GUI가 있는 `Jetson` 로컬 세션에서 실행 중인지
4. `source /opt/ros/humble/setup.bash`를 했는지

## 9. 다음 단계

- 이 viewer가 실제로 회전 반응을 보이면
  - `D435i IMU`의 frame 해석 정리
  - baseline 대비 `IMU ON/OFF` 비교
  - 필요하면 `imu_filter_madgwick` 같은 필터 도입 검토
  순서로 넘어간다.
