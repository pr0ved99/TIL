# 26 Jetson BNO08x Motion Trace Viewer Guide

## 목적

- `BNO08x`의 `linear acceleration`을 짧게 적분해서, `X/Y/Z` 축 위에서 점이 어떻게 움직이는지 본다.
- 즉, 지금 목표는 "`진짜 위치 추정`이 아니라 `짧은 순간 움직임 방향과 누적 경향`을 점 이동으로 보자`"이다.

## 먼저 꼭 알아둘 점

- 이 viewer는 `pseudo-position`이다.
- `linear acceleration`을 짧게 적분한 결과라서, 오래 두면 drift가 커진다.
- 따라서 이 viewer는
  - `어느 방향으로 움직이기 시작했는지`
  - `짧은 순간 어떤 축으로 가속이 걸렸는지`
  - `손으로 흔들었을 때 점이 어떻게 튀는지`
  를 보는 용도에 가깝다.
- 화면 아래 안내처럼 `r` 키를 누르면 trace를 원점으로 reset할 수 있다.

## 1. host `venv` 활성화

```bash
source ~/venvs/bno08x/bin/activate
```

## 2. 기본 실행

이 단계는 `linear acceleration + quaternion` 기준으로 `X/Y/Z` 축 위 점 이동 viewer를 여는 단계다.

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_motion_trace_viewer.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b
```

## 3. 더 부드럽게 보기

이 단계는 센서는 더 자주 읽고, 화면은 적당한 속도로만 그려서 움직임 trace를 더 안정적으로 보는 단계다.

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_motion_trace_viewer.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b \
  --sensor-rate 100 \
  --rate 30
```

## 4. 민감도 조정

이 단계는 점이 너무 쉽게 흔들리거나, 반대로 너무 둔할 때 deadband와 damping을 조정하는 단계다.

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_motion_trace_viewer.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b \
  --accel-deadband 0.20 \
  --velocity-damping 1.8 \
  --speed-floor 0.03
```

## 5. trail 길이와 화면 범위 조정

이 단계는 더 긴 trace를 보고 싶거나, 화면 축 범위를 넓히고 싶을 때 쓰는 단계다.

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_motion_trace_viewer.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b \
  --trail-length 250 \
  --radius 0.8
```

## 6. 화면에서 무엇을 볼지

- 3D 축
  - `X/Y/Z` world 축 기준으로 점이 어디로 움직이는지 본다.
- 파란 점
  - 현재 pseudo-position
- 파란 선
  - 최근 trail
- 아래 정보 줄
  - `pos`
  - `vel`
  - `lin_world`
  - `lin_body`

## 7. 해석 기준

- 정지 상태
  - 점이 원점 근처에 머무는 편이 자연스럽다.
  - 아주 천천히 drift하는 건 어느 정도 정상이다.
- 손으로 특정 방향으로 밀기
  - 그 방향 축으로 점이 먼저 튀는 경향이 보여야 자연스럽다.
- 흔들기
  - trail이 불규칙하게 퍼질 수 있다.
- 오래 두기
  - 진짜 위치가 아니라 drift가 누적될 수 있다.

## 8. reset

- 창이 떠 있는 상태에서 `r` 키를 누르면
  - 현재 trace
  - velocity
  - pseudo-position
  을 원점 기준으로 다시 초기화한다.

## 9. 안 되면 먼저 볼 것

1. [11_Jetson_BNO08x_First_Value_Check_Guide.md](./11_Jetson_BNO08x_First_Value_Check_Guide.md) 기준으로 raw 값이 먼저 나오는지
2. [25_Jetson_BNO08x_All_In_One_Viewer_Guide.md](./25_Jetson_BNO08x_All_In_One_Viewer_Guide.md)에서 `Linear` 값이 먼저 자연스럽게 보이는지
3. 현재 터미널이 `Jetson` 로컬 GUI 터미널인지
4. `source ~/venvs/bno08x/bin/activate`가 되어 있는지

## 10. 다음 단계

- 이 viewer로 짧은 순간 이동 방향 감이 잡히면
  - `all-in-one viewer`의 `Move` 힌트와 같이 보고
  - `BNO08x` 장착 방향/축 해석을 더 확신한 다음
  - `RTAB-Map IMU ON/OFF` 비교로 넘어간다.
