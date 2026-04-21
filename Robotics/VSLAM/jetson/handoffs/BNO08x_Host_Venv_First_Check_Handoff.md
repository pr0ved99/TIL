# BNO08x Host Venv First Check Handoff

## 목적

- 외부 `GY-BNO08x` IMU를 `Jetson` host 환경에서 다시 읽어보는 절차를 팀원에게 그대로 넘긴다.
- 이번 단계의 목표는 `ROS 2`나 `Docker`가 아니라, **I2C 인식과 raw IMU 값 출력이 실제로 되는지 재현**하는 것이다.
- 즉, `accel / gyro / mag / quaternion`이 보이면 이번 단계는 성공이다.

## 현재 상태

- 하드웨어: `GY-BNO08x`
- 연결 방식: `I2C`
- 현재 확인된 bus / address: `i2c-1 / 0x4B`
- host 기준 1차 값 확인: 성공
- `Docker` 기준 1차 값 확인: 의존성은 넣었고, 컨테이너 장치 그룹 권한 재확인 단계

## 현재 고정한 배선

- `VCC -> Jetson pin 17 (3.3V)`
- `GND -> Jetson pin 30 (GND)`
- `SDA -> Jetson pin 27`
- `SCL -> Jetson pin 28`

주의:

- `5V`는 쓰지 않는다.
- `PS0 / PS1 / CS / ADO / INT / RST`는 이번 단계에서 연결하지 않는다.

## 이 핸드오프 문서가 다루는 범위

1. `i2c-1 / 0x4B`가 다시 보이는지 확인
2. host `venv`에서 `accel / gyro / mag / quat`가 실제로 출력되는지 확인
3. 성공하면 결과를 붙여넣고 `Docker` 또는 `ROS 2 publisher` 단계로 넘김

## 바로 실행할 문서 묶음

1. [11_Jetson_BNO08x_First_Value_Check_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/11_Jetson_BNO08x_First_Value_Check_Guide.md:1)
2. [scan_bno08x_buses.sh](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/scan_bno08x_buses.sh:1)
3. [bno08x_value_check.py](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/scripts/bno08x_value_check.py:1)
4. [13_Jetson_BNO08x_Live_Plot_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/13_Jetson_BNO08x_Live_Plot_Guide.md:1)
5. [14_Jetson_BNO08x_Aircraft_Viewer_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/14_Jetson_BNO08x_Aircraft_Viewer_Guide.md:1)
6. [12_Jetson_BNO08x_Docker_Check_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/12_Jetson_BNO08x_Docker_Check_Guide.md:1)
7. [2026-04-18 Jetson 작업 일지](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/daily/2026-04-18/README.md:1)

## 가장 짧은 실행 순서

### 1. 시스템 패키지 준비

```bash
sudo apt update
sudo apt install -y python3-pip python3-dev python3-venv python3-smbus i2c-tools
```

### 2. host `venv` 준비

```bash
python3 -m venv ~/venvs/bno08x
source ~/venvs/bno08x/bin/activate
pip install --upgrade pip
pip install adafruit-blinka adafruit-circuitpython-bno08x adafruit-extended-bus pyserial smbus2
```

### 3. I2C 주소 재확인

```bash
cd ~/yh_ws/TIL
./Robotics/VSLAM/jetson/scripts/scan_bno08x_buses.sh
sudo i2cdetect -y -r 1
```

기대:

- `i2c-1`에서 `0x4B`가 보여야 한다.

### 4. 값 읽기 실행

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_value_check.py --interface i2c --bus 1 --address 0x4b --rate 5 --samples 20
```

## 기대 출력

- 첫 줄에 `opened BNO08x over I2C bus=1 address=0x4b`
- 이후 줄마다
  - `accel=(...)`
  - `gyro=(...)`
  - `mag=(...)`
  - `quat=(...)`

정지 상태에서 기대하는 특징:

- `gyro`는 대체로 `0` 근처
- `accel` 크기는 대략 중력값 근처
- `quat`는 첫 샘플이 `0`일 수 있지만, 이후 정상값으로 들어오면 큰 문제로 보지 않는다

## 실제로 이미 확인된 상태

- host `venv` 기준으로 위 명령이 성공했다.
- 센서를 움직였을 때 `gyro`, `accel`, `quat` 변화가 실제로 확인됐다.
- 따라서 현재 병목은 배선이나 센서 불량보다는, 이후 단계의 `Docker` 또는 `ROS 2` 통합 쪽이다.

## 실패하면 먼저 볼 것

1. `sudo i2cdetect -y -r 1`에서 여전히 `0x4B`가 보이는지
2. `VCC / GND / SDA / SCL` 배선이 그대로 유지됐는지
3. `3.3V`에 연결했는지
4. `venv`가 활성화됐는지
5. pip 패키지 이름을 `adafruit-extended-bus`로 넣었는지

## 이번 단계의 완료 조건

- `i2c-1 / 0x4B` 확인
- host `venv`에서 `accel / gyro / mag / quat` 출력 확인
- 센서를 움직였을 때 값 변화 확인

## 완료 후 다음 단계

1. [13_Jetson_BNO08x_Live_Plot_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/13_Jetson_BNO08x_Live_Plot_Guide.md:1) 기준으로 그래프에서 축 반응과 bias를 확인
2. [14_Jetson_BNO08x_Aircraft_Viewer_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/14_Jetson_BNO08x_Aircraft_Viewer_Guide.md:1) 기준으로 자세 변화를 비행기 모델로 확인
3. [12_Jetson_BNO08x_Docker_Check_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/12_Jetson_BNO08x_Docker_Check_Guide.md:1) 기준으로 같은 값을 컨테이너 안에서 재현
4. [16_Jetson_BNO08x_ROS2_IMU_Publisher_Guide.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/guides/16_Jetson_BNO08x_ROS2_IMU_Publisher_Guide.md:1) 기준으로 `sensor_msgs/Imu` publisher 실행
5. `/imu/data`와 `/imu/mag` publish 확인
6. `imu_link` frame 정리 후 `RTAB-Map` 또는 `robot_localization` 연계 검토

## 한 줄 인계

- `BNO08x`는 Jetson host `venv`에서 이미 살아 있다. 팀원은 먼저 같은 host 명령으로 raw 값 재현부터 하고, 그 다음에만 `Docker`와 `ROS 2` 단계로 넘어가면 된다.
