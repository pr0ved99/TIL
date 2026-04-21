# 25 Jetson BNO08x All-In-One Viewer Guide

## 목적

- `BNO08x`의 `나침반`, `수평계`, `기울기`, `회전`을 한 화면에서 동시에 본다.
- 즉, 지금 목표는 "`방향`, `수평`, `자세`, `회전 속도`를 따로따로 실행하지 말고 한 번에 보자`"이다.

## 언제 쓰는가

- [11_Jetson_BNO08x_First_Value_Check_Guide.md](./11_Jetson_BNO08x_First_Value_Check_Guide.md) 기준으로 raw 값이 이미 성공했을 때
- `aircraft`, `compass`, `level` viewer를 각각 따로 돌리는 게 번거로울 때
- `RTAB-Map IMU ON/OFF` 비교 전에, 센서 상태를 한 화면에서 빠르게 점검하고 싶을 때

## 먼저 알면 좋은 점

- 왼쪽은 `3D 자세(기울기)`다.
- 오른쪽 위는 `나침반(heading)`이다.
- 오른쪽 아래는 `수평계(level)`다.
- 아래 텍스트에는 `roll / pitch / yaw`, `gyro`, `accel`, `mag`, `turn rate`가 같이 나온다.
- diagnostics 확장판에서는 `gravity`, `linear acceleration`, `calibration status`도 같이 나온다.
- 또 `linear acceleration` 기준으로 `Move` 힌트도 같이 나온다.
- 하단 정보 패널은 항목 이름 위치를 고정하고, 각 값만 갱신되게 정리했다.
- 그래서 숫자가 바뀌어도 문장 전체가 계속 흔들리는 느낌은 이전보다 덜하다.
- 즉, 이 viewer 하나로
  - `나침반`
  - `수평`
  - `기울기`
  - `회전`
  을 한 번에 본다.
- heading 기준 축은 `--forward-axis x`가 기본이다. 지금 보드 기준으로도 이 값이 가장 자연스러운 쪽이었다.

## 1. host `venv` 활성화

```bash
source ~/venvs/bno08x/bin/activate
```

## 2. `matplotlib` 설치 확인

```bash
pip install matplotlib
```

## 3. 기본 실행

이 단계는 기본 heading 축 `+X` 기준으로 통합 viewer를 띄우는 단계다.

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_all_in_one_viewer.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b \
  --forward-axis x
```

## 4. 더 부드럽게 보기

이 단계는 센서는 더 자주 읽고, 화면은 적당한 속도로만 그려서 반응을 부드럽게 보는 단계다.

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

## 5. 수평 기준을 현재 자세로 두기

이 단계는 지금 센서를 둔 자세를 임시 `0점`으로 보고 싶을 때 쓰는 단계다.

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_all_in_one_viewer.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b \
  --forward-axis x \
  --zero-on-start
```

## 6. heading이나 수평 오차 보정

이 단계는 실제 북쪽이나 장착 기준이 약간 돌아가 있을 때 쓰는 단계다.

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_all_in_one_viewer.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b \
  --forward-axis x \
  --heading-offset 12 \
  --roll-offset 1.0 \
  --pitch-offset -0.5
```

## 7. 화면에서 무엇을 볼지

- 왼쪽 3D 자세
  - 비행기 모양으로 `기울기`와 `자세`를 본다.
- 오른쪽 위 나침반
  - `+X`가 현재 어느 방향을 보는지 본다.
- 오른쪽 아래 수평계
  - `roll / pitch`가 0에 가까운지 본다.
- 위 상태 줄
  - `Heading`, `Roll`, `Pitch`, `Yaw`, `Turn`
- 그 아래 상태 줄
  - `State`, `Move`
- 아래 상세 줄
  - `Gyro`, `Accel`, `Mag`
- 추가 diagnostics 줄
  - `Gravity`, `Linear`, `Calib`
- 가장 아래 안내 줄
  - `relative heading`
  - `zero ref`
  - `|a|`
  - `|B|`
  - `|g|`
  - `|lin|`

## 8. 해석 기준

- 평평하게 두었을 때
  - 수평계 점이 중앙 근처
  - `roll`, `pitch`가 0 근처
  - 상태가 `LEVEL`
- 좌우/앞뒤로 기울이면
  - 3D 비행기 자세와 수평계 점이 같이 변해야 자연스럽다.
- 평면에서 돌리면
  - 나침반 heading과 `yaw`가 같이 변해야 자연스럽다.
- 빠르게 돌리면
  - `turn_rate`가 커져야 한다.
- 정지 상태면
  - `Gravity` 크기는 대체로 `9.8 m/s²` 근처여야 한다.
  - `Linear`는 `0` 근처여야 자연스럽다.
- `Move`는
  - `linear acceleration` 기준으로 `forward/back/left/right/up/down/still` 같은 힌트를 보여준다.
  - 위치 추정이 아니라, "지금 어느 방향으로 가속이 걸리고 있나"를 빠르게 읽기 위한 보조 정보다.
- `Calib`는
  - `0 unreliable`
  - `1 low`
  - `2 medium`
  - `3 high`
  정도로 보면 된다.

## 8-1. 이동 힌트 민감도 조정

이 단계는 `Move`가 너무 예민하거나 둔할 때 threshold를 조정하는 단계다.

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_all_in_one_viewer.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b \
  --forward-axis x \
  --move-threshold 0.25 \
  --vertical-threshold 0.30
```

## 9. 안 되면 먼저 볼 것

1. [11_Jetson_BNO08x_First_Value_Check_Guide.md](./11_Jetson_BNO08x_First_Value_Check_Guide.md) 기준 raw 값이 먼저 나오는지
2. [14_Jetson_BNO08x_Aircraft_Viewer_Guide.md](./14_Jetson_BNO08x_Aircraft_Viewer_Guide.md), [19_Jetson_BNO08x_Compass_Viewer_Guide.md](./19_Jetson_BNO08x_Compass_Viewer_Guide.md), [24_Jetson_BNO08x_Level_Viewer_Guide.md](./24_Jetson_BNO08x_Level_Viewer_Guide.md)가 각각 먼저 뜨는지
3. 현재 터미널이 `Jetson` 로컬 GUI 터미널인지
4. `source ~/venvs/bno08x/bin/activate`가 되어 있는지

## 10. 다음 단계

- 이 통합 viewer가 자연스럽게 보이면
  - `BNO08x` 장착 기준면 정리
  - `imu_link` 축 정리
  - `RTAB-Map IMU ON/OFF` 비교
  로 넘어간다.
