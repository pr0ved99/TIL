# 19 Jetson BNO08x Compass Viewer Guide

## 목적

- `BNO08x`의 방향을 `나침반` 형태로 직관적으로 확인한다.
- 단순 숫자 대신 `heading`과 `방위(N/NE/E/...)`를 바로 본다.

## 언제 쓰는가

- [11_Jetson_BNO08x_First_Value_Check_Guide.md](./11_Jetson_BNO08x_First_Value_Check_Guide.md) 기준으로 raw 값이 이미 성공했을 때
- [14_Jetson_BNO08x_Aircraft_Viewer_Guide.md](./14_Jetson_BNO08x_Aircraft_Viewer_Guide.md)로 자세는 확인했고, 방향만 더 단순하게 보고 싶을 때

## 먼저 알면 좋은 점

- 이 viewer는 `raw magnetometer` 자체보다는 `BNO08x`가 내부적으로 융합한 `quaternion`을 기준으로 heading을 보여준다.
- 현재 버전은 `yaw` 숫자만 바로 쓰지 않고, `선택한 body axis`를 quaternion으로 실제 회전시켜 그 축이 어디를 보는지 계산한다.
- 즉, `+X`를 heading으로 볼지 `+Y`를 heading으로 볼지 직접 고를 수 있다.
- 그래서 어떤 보드에서는 `--forward-axis x`, 다른 보드에서는 `--forward-axis y`가 더 자연스럽게 보일 수 있다.
- 실사용 관점에서는 더 자연스럽지만, `완전한 절대 북쪽 측정기`처럼 생각하면 안 된다.
- 주변 금속, 모터, 전원선, 자석 영향이 있으면 heading이 흔들릴 수 있다.
- 방향이 약간 돌아가 보이면 `--heading-offset`으로 수동 보정할 수 있다.

## 1. host `venv` 활성화

```bash
source ~/venvs/bno08x/bin/activate
```

## 2. `matplotlib` 설치 확인

```bash
pip install matplotlib
```

## 3. 기본 실행

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_compass_viewer.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b \
  --forward-axis x
```

## 4. 더 부드럽게 보기

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_compass_viewer.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b \
  --forward-axis x \
  --sensor-rate 100 \
  --rate 30
```

만약 화면상으로 보니 실제 `+Y`축이 heading처럼 움직인다면 이렇게 바꿔서 본다.

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_compass_viewer.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b \
  --forward-axis y \
  --sensor-rate 100 \
  --rate 30
```

## 5. 방향이 약간 돌아가 보일 때

예를 들어 전체 나침반이 `15도`쯤 돌아가 보이면:

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_compass_viewer.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b \
  --forward-axis x \
  --heading-offset 15
```

자기편차까지 더하고 싶으면 `--declination`도 쓸 수 있다.

## 6. 화면에서 무엇을 볼지

- 파란 화살표
  - 현재 `heading`
  - 즉, `--forward-axis`로 선택한 body axis가 현재 어느 방향을 보는지
- 회색 점선 화살표
  - 프로그램 시작 시점을 기준으로 한 상대 방향
- 큰 숫자
  - 현재 heading 각도와 방위
  - 어떤 axis를 기준으로 보는지도 같이 표시
- 아래 텍스트
  - `fused yaw`
  - 시작 대비 `relative`
  - 실제로 사용한 `world_axis`
  - 현재 `mag`
  - 자기장 크기 `|B|`

## 7. 해석 기준

- 센서를 평평하게 들고 천천히 좌우로 돌리면 파란 화살표가 같이 돌아야 자연스럽다.
- `+X`가 아니라 `+Y`가 heading처럼 보이면 `--forward-axis y`로 바꿔서 다시 본다.
- 같은 자리에서 값이 너무 심하게 튀면 주변 자기장 간섭을 의심한다.
- `roll/pitch`를 크게 기울인 상태에서도 heading이 크게 요동치면 센서 위치나 주변 금속 환경을 다시 본다.

## 8. 안 되면 먼저 볼 것

1. [11_Jetson_BNO08x_First_Value_Check_Guide.md](./11_Jetson_BNO08x_First_Value_Check_Guide.md) 기준 raw 값이 먼저 나오는지
2. [14_Jetson_BNO08x_Aircraft_Viewer_Guide.md](./14_Jetson_BNO08x_Aircraft_Viewer_Guide.md) 기준 quaternion viewer가 먼저 뜨는지
3. 현재 터미널이 `Jetson` 로컬 GUI 터미널인지
4. `source ~/venvs/bno08x/bin/activate`가 되어 있는지

## 9. 다음 단계

- 이 compass viewer가 자연스럽게 보이면
  - `yaw` 안정성 확인
  - `RTAB-Map IMU ON/OFF` 비교
  - 필요하면 `ROS 2 /imu/data` 기준 compass viewer 또는 heading logger
  로 넘어간다.
