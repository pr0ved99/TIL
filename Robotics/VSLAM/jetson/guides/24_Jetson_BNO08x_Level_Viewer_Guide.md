# 24 Jetson BNO08x Level Viewer Guide

## 목적

- `BNO08x`의 `roll / pitch`를 이용해 `수평(level)` 상태를 전자 수평계처럼 직관적으로 본다.
- 즉, 지금 목표는 "`나침반`이나 `자세` 확인을 넘어서, 지금 얼마나 평평한지 바로 보자`"이다.

## 언제 쓰는가

- [11_Jetson_BNO08x_First_Value_Check_Guide.md](./11_Jetson_BNO08x_First_Value_Check_Guide.md) 기준으로 raw 값이 이미 성공했을 때
- [14_Jetson_BNO08x_Aircraft_Viewer_Guide.md](./14_Jetson_BNO08x_Aircraft_Viewer_Guide.md)로 자세 변화는 확인했고, 수평 여부만 더 단순하게 보고 싶을 때

## 먼저 알면 좋은 점

- 이 viewer는 `yaw`보다 `roll / pitch`를 중심으로 본다.
- 화면 가운데에 점이 있으면 수평에 가깝고, 원 바깥쪽으로 갈수록 더 기울어진 상태다.
- 기본값은 **실제 roll / pitch**를 그대로 보여준다.
- 만약 현재 자세를 임시 기준 수평으로 삼고 싶으면 `--zero-on-start`를 쓸 수 있다.
- 센서 장착이 약간 비뚤어졌다면 `--roll-offset`, `--pitch-offset`으로 수동 보정할 수 있다.

## 1. host `venv` 활성화

```bash
source ~/venvs/bno08x/bin/activate
```

## 2. `matplotlib` 설치 확인

```bash
pip install matplotlib
```

## 3. 기본 실행

이 단계는 실제 `roll / pitch`를 그대로 전자 수평계처럼 보는 단계다.

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_level_viewer.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b
```

## 4. 더 부드럽게 보기

이 단계는 센서는 더 자주 읽고 화면은 적당한 속도로만 그려 체감 반응을 더 부드럽게 만드는 단계다.

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_level_viewer.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b \
  --sensor-rate 100 \
  --rate 30
```

## 5. 시작 자세를 임시 수평 기준으로 쓰기

이 단계는 센서를 현재 둔 자세를 `0점`으로 보고 싶을 때 쓰는 단계다.

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_level_viewer.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b \
  --zero-on-start
```

## 6. 장착 오차 수동 보정

이 단계는 센서가 물리적으로 조금 비뚤게 붙어 있어서, 정지 상태인데도 `roll / pitch`가 0 근처가 아닐 때 쓰는 단계다.

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_level_viewer.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b \
  --roll-offset 1.5 \
  --pitch-offset -0.8
```

## 7. 화면에서 무엇을 볼지

- 가운데 점
  - 현재 `roll / pitch`가 0에 가까운지 보여준다.
- 초록색 원 안
  - `level threshold` 안쪽이다.
  - 기본값으로는 `2도` 이내를 수평으로 본다.
- 상태 텍스트
  - `LEVEL` 또는 `TILTED`
  - 현재 `roll / pitch`
- 아래 상세 텍스트
  - raw `roll / pitch`
  - `yaw`
  - 가속도 크기 `|a|`
  - 현재 threshold
  - `zero-on-start`를 썼다면 시작 기준값

## 8. 해석 기준

- 정지 상태에서 점이 중앙 근처에 머물면 수평에 가깝다.
- 앞뒤로 기울이면 점이 위/아래로 움직이고, 좌우로 기울이면 점이 좌/우로 움직여야 자연스럽다.
- 가속도 크기 `|a|`가 대략 `9.8 m/s²` 근처면 정지 상태 해석이 더 믿을 만하다.
- 빠르게 흔들거나 이동 중이면 순간적으로 점이 더 튈 수 있다.

## 9. 안 되면 먼저 볼 것

1. [11_Jetson_BNO08x_First_Value_Check_Guide.md](./11_Jetson_BNO08x_First_Value_Check_Guide.md) 기준 raw 값이 먼저 나오는지
2. [14_Jetson_BNO08x_Aircraft_Viewer_Guide.md](./14_Jetson_BNO08x_Aircraft_Viewer_Guide.md) 기준 quaternion viewer가 먼저 자연스럽게 뜨는지
3. 현재 터미널이 `Jetson` 로컬 GUI 터미널인지
4. `source ~/venvs/bno08x/bin/activate`가 되어 있는지

## 10. 다음 단계

- 이 viewer로 수평 판단이 자연스럽게 보이면
  - `BNO08x` 장착 기준면 정리
  - `imu_link` 축 정리
  - `RTAB-Map IMU ON/OFF` 비교
  로 넘어간다.
