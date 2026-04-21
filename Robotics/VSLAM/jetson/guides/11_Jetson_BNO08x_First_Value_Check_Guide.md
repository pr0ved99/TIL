# 11 Jetson BNO08x First Value Check Guide

## 결론

- 지금 목표는 `GY-BNO08x`에서 실제 `accel / gyro / mag / quaternion` 값이 나오는지 먼저 보는 것이다.
- 현재 Jetson 실측 기준으로는 `i2c-1`에서 `0x4B`가 실제로 보였다.
- 즉, **I2C 인식은 이미 성공**했고 지금은 Python으로 값만 읽어보면 되는 단계다.

## 현재 확인 상태

- `i2cdetect -l` 기준 I2C bus는 보인다.
- 재스캔 기준 `i2c-1`에서 `0x4B`가 확인됐다.
- Python 쪽은 `pip`, `venv`, `adafruit_bno08x`, `board`, `busio`가 아직 없다.
- 따라서 지금 남은 핵심은 시스템 패키지와 Python 라이브러리 설치다.

## 1. 시스템 준비

```bash
sudo apt update
sudo apt install -y python3-pip python3-dev python3-venv python3-smbus i2c-tools
```

## 2. Python 환경 준비

```bash
python3 -m venv ~/venvs/bno08x
source ~/venvs/bno08x/bin/activate
pip install --upgrade pip
pip install adafruit-blinka adafruit-circuitpython-bno08x adafruit-extended-bus pyserial smbus2
```

## 3. I2C 연결인지 먼저 확인

```bash
cd ~/yh_ws/TIL
chmod +x ./Robotics/VSLAM/jetson/scripts/scan_bno08x_buses.sh
./Robotics/VSLAM/jetson/scripts/scan_bno08x_buses.sh
```

기대:

- 현재 기대값은 `i2c-1`에 `0x4B`가 보이는 것이다.
- 만약 다시 안 보이면 배선이 흔들렸거나 전원/SDA/SCL 연결 상태를 다시 봐야 한다.

## 4. I2C로 값 읽기

예시:

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_value_check.py --interface i2c --bus 1 --address 0x4b --rate 5 --samples 20
```

현재 실측 기준으로는 그대로 `--bus 1 --address 0x4b`를 쓰면 된다.

## 5. 기대 결과

- `accel`, `gyro`, `mag`, `quat` 값이 주기적으로 출력된다.
- 센서를 움직이면 값이 바뀐다.
- 정지 상태에서는 `gyro`가 대체로 `0` 근처로 보인다.
- `quaternion`이 정상적으로 바뀌면, 이후 `ROS 2 sensor_msgs/Imu` publish 단계로 넘어갈 수 있다.

## 6. UART는 지금은 보조 경로

예시:

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_value_check.py --interface uart --uart-port /dev/ttyTHS1 --baud 3000000 --rate 5 --samples 20
```

주의:

- `GY-BNO08x` breakout마다 UART 기본 baud가 다를 수 있다.
- 데이터시트나 판매 페이지 기준 baud가 다르면 그 값으로 바꾼다.

## 7. 실패 시 확인 우선순위

1. `i2c-1`에서 `0x4B`가 여전히 보이는지 확인
2. `VCC / GND / SDA / SCL` 배선이 handoff 그대로 맞는지 확인
3. `3.3V`로 연결했는지 확인
4. Python 라이브러리가 설치됐는지 확인
5. `board.I2C()` 대신 지금처럼 `ExtendedI2C(1)` 기반 스크립트로 읽는지 확인

## 8. 다음 단계

- 1차 값 확인 성공
- 축 방향과 중력 방향 확인
- quaternion 기준 frame 해석
- 그다음에만 `ROS 2` 노드 또는 `robot_localization` 입력으로 연결
