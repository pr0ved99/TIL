# 12 Jetson BNO08x Docker Check Guide

## 목적

- 이미 host에서 확인한 `BNO08x i2c-1 / 0x4B` 값을 이번에는 Docker 컨테이너 안에서 다시 읽어본다.
- 즉, 앞으로 실제 운영 기준인 `Docker` 환경에서도 `accel / gyro / quaternion`이 그대로 보이는지 검증한다.

## 전제

- host에서 `BNO08x`가 `i2c-1 / 0x4B`로 잡힌 상태여야 한다.
- [`09_Jetson_VSLAM_Docker_Bringup_Guide.md`](./09_Jetson_VSLAM_Docker_Bringup_Guide.md) 기준으로 개발 컨테이너 build가 끝나 있어야 한다.
- `compose.yaml`은 이미 `/dev`를 마운트하므로, 컨테이너 안에서도 I2C 장치 접근이 가능해야 한다.
- `compose.yaml`에는 host `i2c` 그룹(`gid 116`)도 추가해, 컨테이너 사용자로 `/dev/i2c-1`에 접근할 수 있게 한다.

## 1. host에서 주소 재확인

```bash
sudo i2cdetect -y -r 1
```

기대:

- `0x4B`가 보여야 한다.

## 2. 컨테이너 진입

```bash
xhost +local:docker
cd ~/yh_ws/TIL
cd ~/yh_ws/TIL/Robotics/VSLAM/jetson/docker
docker compose --env-file .env build
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/run_jetson_vslam_docker.sh
```

## 3. 컨테이너 안에서 기본 확인

```bash
python3 --version
python3 - <<'PY'
import board
import adafruit_bno08x
from adafruit_extended_bus import ExtendedI2C
print("imports ok")
print("ExtendedI2C ok:", ExtendedI2C)
PY
```

## 4. 컨테이너 안에서 BNO08x 값 읽기

```bash
cd /workspace/TIL
python3 ./Robotics/VSLAM/jetson/scripts/bno08x_value_check.py --interface i2c --bus 1 --address 0x4b --rate 5 --samples 20
```

## 5. 기대 결과

- host에서 보였던 것처럼 `accel`, `gyro`, `mag`, `quat`가 출력된다.
- 센서를 움직이면 값이 바뀐다.
- 이 단계가 성공하면 이후 ROS2 publisher도 Docker 안에서 바로 만들 수 있다.

## 6. 안 되면 볼 것

- host에서 여전히 `0x4B`가 보이는지
- 컨테이너 안에서 `/dev/i2c-1`가 보이는지
- 컨테이너 이미지가 최신으로 rebuild 됐는지

```bash
ls -l /dev/i2c-1
```

## 7. 다음 단계

- `sensor_msgs/Imu` publisher 작성
- `/imu/data` 또는 `/imu/data_raw` publish
- `imu_link` frame과 quaternion 해석 정리
