# 27 Jetson BNO08x Calibration Guide

## 목적

- `BNO08x`의 `accelerometer`, `gyroscope`, `magnetometer`를 Jetson에서 직접 보정한다.
- 즉, 지금 목표는 "`heading / level / tilt`를 더 믿을 수 있게 만들기 위해 기본 보정 절차를 실제로 수행하자`"이다.

## 언제 쓰는가

- [11_Jetson_BNO08x_First_Value_Check_Guide.md](./11_Jetson_BNO08x_First_Value_Check_Guide.md) 기준으로 raw 값은 이미 나올 때
- [25_Jetson_BNO08x_All_In_One_Viewer_Guide.md](./25_Jetson_BNO08x_All_In_One_Viewer_Guide.md)에서 `Calib`가 낮거나 `heading`이 흔들릴 때
- 센서를 새로 연결했거나, 장착 위치/주변 환경이 바뀌었을 때

## 참고 문서

- 이 가이드는 Jetson 로컬에 있는 [Sensor-Calibration-Procedure-v1.1.pdf](/home/jetson/Downloads/Sensor-Calibration-Procedure-v1.1.pdf)를 참고해 정리했다.
- 문서 핵심은 아래와 같다.
  - `accelerometer`: `4~6`개의 서로 다른 자세로 약 `1초`씩 유지
  - `gyroscope`: 완전히 정지한 상태로 `2~3초`
  - `magnetometer`: `roll / pitch / yaw` 축으로 약 `180도` 회전했다가 원위치
  - `magnetometer accuracy`가 `2` 또는 `3`이 될 때까지 반복

## 먼저 알면 좋은 점

- 현재 `all-in-one viewer`의 `Calib`는 실질적으로 `magnetometer accuracy`를 보는 값이다.
- 보통 아래처럼 해석하면 된다.
  - `0`: unreliable
  - `1`: low
  - `2`: medium
  - `3`: high
- `heading / compass`가 중요하면 `Calib 2` 이상을 목표로 보는 편이 좋다.
- 금속 책상, 스피커, 모터, 전원선 근처에서는 자기장 보정이 잘 안 될 수 있다.

## 1. host `venv` 활성화

```bash
source ~/venvs/bno08x/bin/activate
```

## 2. 보정 상태를 볼 viewer 띄우기

이 단계는 보정이 실제로 좋아지는지 눈으로 보기 위해 `all-in-one viewer`를 먼저 여는 단계다.

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_all_in_one_viewer.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b \
  --forward-axis x \
  --sensor-rate 100 \
  --rate 30
```

## 3. calibration 시작

이 단계는 `BNO08x` 내부 self-calibration 루틴을 시작하는 단계다.

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python - <<'PY'
from adafruit_extended_bus import ExtendedI2C
from adafruit_bno08x.i2c import BNO08X_I2C

i2c = ExtendedI2C(1)
bno = BNO08X_I2C(i2c, address=0x4B)
bno.begin_calibration()
print("BNO08x calibration started.")
PY
```

## 4. accelerometer 보정

이 단계는 서로 다른 `4~6`개 자세로 센서를 옮겨 `accelerometer`를 보정하는 단계다.

### 동작 방법

- 센서를 `앞`, `뒤`, `왼쪽`, `오른쪽`, `위`, `아래` 같은 서로 다른 방향으로 옮긴다.
- 완벽하게 직각일 필요는 없고, 서로 충분히 다른 자세면 된다.
- 각 자세에서 약 `1초` 정도 가만히 둔다.

### 간단 기준

- `4`개 자세만 해도 시작은 가능하다.
- 가능하면 `6`개 자세에 가깝게 해보는 편이 좋다.

## 5. gyroscope 보정

이 단계는 센서를 완전히 멈춘 상태로 두어 `gyroscope bias`를 잡는 단계다.

### 동작 방법

- 센서를 책상 위에 가만히 둔다.
- 약 `2~3초` 동안 건드리지 않는다.

## 6. magnetometer 보정

이 단계는 `heading / compass` 품질에 가장 직접적으로 영향을 주는 `magnetometer`를 보정하는 단계다.

### 동작 방법

- 아래 세 축 방향 회전을 반복한다.
  - `roll` 축으로 약 `180도` 회전했다가 원위치
  - `pitch` 축으로 약 `180도` 회전했다가 원위치
  - `yaw` 축으로 약 `180도` 회전했다가 원위치
- 각 축은 대략 `2초` 정도에 걸쳐 천천히 움직이면 충분하다.
- viewer의 `Calib`가 `2` 또는 `3`이 될 때까지 반복한다.

### 목표

- 최소 목표: `Calib = 2`
- 권장 목표: `Calib = 3`

## 7. calibration 저장

이 단계는 현재 보정 결과를 `DCD` 형태로 센서 쪽에 저장하는 단계다.

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python - <<'PY'
from adafruit_extended_bus import ExtendedI2C
from adafruit_bno08x.i2c import BNO08X_I2C

i2c = ExtendedI2C(1)
bno = BNO08X_I2C(i2c, address=0x4B)
bno.save_calibration_data()
print("BNO08x calibration data saved.")
PY
```

## 8. 저장 후 다시 확인

이 단계는 저장이 끝난 뒤 `heading`, `Calib`, `level`이 더 안정적으로 보이는지 다시 확인하는 단계다.

### 체크 포인트

- `Calib`가 `2`나 `3`으로 유지되는지
- `heading`이 전보다 덜 흔들리는지
- 정지 상태에서 `Move`가 거의 `still`에 가깝게 나오는지
- `level`과 `tilt`가 자연스러운지

## 9. 환경 바뀌면 다시 해야 하는가

- `heading / compass`를 중요하게 쓸 거면 다시 하는 게 좋다.
- 특히 아래 경우는 다시 해볼 가치가 크다.
  - 다른 방으로 옮겼을 때
  - 금속 구조물/모터/배터리 근처 배치가 달라졌을 때
  - 장착 위치가 바뀌었을 때

## 10. 안 되면 먼저 볼 것

1. [11_Jetson_BNO08x_First_Value_Check_Guide.md](./11_Jetson_BNO08x_First_Value_Check_Guide.md) 기준으로 raw 값이 먼저 나오는지
2. [25_Jetson_BNO08x_All_In_One_Viewer_Guide.md](./25_Jetson_BNO08x_All_In_One_Viewer_Guide.md)에서 `Calib` 값이 실제로 보이는지
3. 너무 자성이 강한 환경인지
4. 센서 전원/배선이 불안정하지 않은지

## 11. 다음 단계

- calibration이 끝나면
  - `heading-offset`
  - `roll / pitch offset`
  - `BNO08x IMU ON / OFF` 비교
  로 넘어간다.
