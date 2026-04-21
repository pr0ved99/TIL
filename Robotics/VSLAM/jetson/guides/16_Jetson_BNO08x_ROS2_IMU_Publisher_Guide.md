# 16 Jetson BNO08x ROS2 IMU Publisher Guide

## 목적

- `GY-BNO08x`를 Jetson host에서 읽어 `ROS 2 sensor_msgs/Imu`로 바로 publish한다.
- 즉, 지금 목표는 "`raw 값은 이미 나오니, 이제 `/imu/data`를 실제 ROS 2 topic으로 띄우자`"이다.

## 중요한 현재 상태

- host `venv` 기준으로 `BNO08x` raw 값 확인은 이미 성공했다.
- `D435i` 내장 IMU는 현재 `Jetson`에서 막혀 있으므로, 실제 IMU 비교 실험은 우선 외부 `BNO08x` 기준으로 진행하는 편이 맞다.
- 이 가이드는 `host venv + ROS 2`를 같이 쓰는 경로다.

## 실행 전 확인

- 먼저 아래가 이미 되는 상태여야 한다.
  - [11_Jetson_BNO08x_First_Value_Check_Guide.md](./11_Jetson_BNO08x_First_Value_Check_Guide.md)
  - [13_Jetson_BNO08x_Live_Plot_Guide.md](./13_Jetson_BNO08x_Live_Plot_Guide.md) 또는 [14_Jetson_BNO08x_Aircraft_Viewer_Guide.md](./14_Jetson_BNO08x_Aircraft_Viewer_Guide.md)
- 현재 실측 기준 기본값은 아래다.
  - `interface=i2c`
  - `bus=1`
  - `address=0x4b`

## 1. 터미널 1에서 publisher 실행

중요:

- `source /opt/ros/humble/setup.bash`를 먼저 하고
- 그다음 `source ~/venvs/bno08x/bin/activate`를 한다

```bash
cd ~/yh_ws/TIL
source /opt/ros/humble/setup.bash
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_ros2_imu_publisher.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b \
  --topic /imu/data \
  --mag-topic /imu/mag \
  --frame-id imu_link \
  --rate 50
```

기대:

- 첫 줄에 `opened BNO08x over I2C...`
- 이어서 `publishing IMU on /imu/data ...`
- 그다음 `first sample: ...`

## 2. 터미널 2에서 topic 확인

```bash
source /opt/ros/humble/setup.bash
ros2 topic list | grep -E '^/imu'
ros2 topic echo /imu/data --once
ros2 topic hz /imu/data
ros2 topic echo /imu/mag --once
```

기대:

- `/imu/data`
- `/imu/mag`
- `header.frame_id: imu_link`
- `orientation`, `angular_velocity`, `linear_acceleration`가 실제 값으로 채워짐

## 3. 터미널 3에서 ROS 2 비행기 viewer 연결

이 단계는 선택이지만, 현재 흐름에서는 바로 같이 보는 편이 좋다.

```bash
source /opt/ros/humble/setup.bash
python3 /home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/ros2_imu_aircraft_viewer.py --topic /imu/data --rate 20
```

이제는 `BNO08x` quaternion이 이미 `/imu/data` 안 orientation으로 들어가므로, viewer는 보통 `message_quaternion` 모드로 동작하는 쪽이 자연스럽다.

## 4. 지금 단계에서 확인할 것

1. 센서를 평평하게 두고 시작했을 때 자세가 크게 튀지 않는지
2. 앞뒤 기울임에서 `pitch`가 자연스럽게 바뀌는지
3. 좌우 기울임에서 `roll`이 자연스럽게 바뀌는지
4. 천천히 회전했을 때 `yaw`도 대체로 따라오는지
5. `/imu/data` topic rate가 설정한 값 근처로 유지되는지

## 5. 안 되면 먼저 볼 것

1. [11_Jetson_BNO08x_First_Value_Check_Guide.md](./11_Jetson_BNO08x_First_Value_Check_Guide.md) 기준 raw 값이 아직 나오는지
2. `source /opt/ros/humble/setup.bash`를 먼저 했는지
3. `source ~/venvs/bno08x/bin/activate`를 했는지
4. `rclpy` import 에러가 나는지
5. `opened BNO08x...`는 뜨는데 topic이 안 보이면 publisher 터미널 로그를 다시 확인

## 6. 다음 단계

- `/imu/data` publish 성공
- `ros2_imu_aircraft_viewer.py`로 자세 반응 확인
- 그다음 `imu_link` frame 정리
- 이후 `RTAB-Map IMU OFF`와 `BNO08x IMU ON` 비교 실험으로 넘어감
