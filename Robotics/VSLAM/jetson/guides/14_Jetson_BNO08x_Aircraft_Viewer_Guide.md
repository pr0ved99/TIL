# 14 Jetson BNO08x Aircraft Viewer Guide

## 목적

- `BNO08x`의 quaternion을 단순 그래프가 아니라 `비행기 모양 3D 모델`로 본다.
- 센서를 손으로 기울이거나 회전할 때, 비행기 모델이 같은 방향으로 기울고 도는지 직관적으로 확인한다.

## 언제 쓰는가

- [11_Jetson_BNO08x_First_Value_Check_Guide.md](./11_Jetson_BNO08x_First_Value_Check_Guide.md) 기준으로 raw 값 출력이 이미 성공했을 때
- [13_Jetson_BNO08x_Live_Plot_Guide.md](./13_Jetson_BNO08x_Live_Plot_Guide.md)로 시계열은 확인했고, 자세 변화를 더 직관적으로 보고 싶을 때

## 먼저 알면 좋은 점

- 이 뷰어는 `Jetson` 로컬 바탕화면 터미널에서 실행하는 편이 좋다.
- 내부적으로는 `quaternion -> rotation matrix`로 바꿔 간단한 비행기 와이어프레임을 회전시킨다.
- 현재 버전은 **첫 유효 quaternion을 시작 자세 기준**으로 잡는다.
- 즉, 프로그램을 켠 직후 센서를 어떻게 두었는지가 회색 기준 비행기 자세가 된다.
- 현재 버전은 `센서 polling`과 `화면 redraw`를 분리했다.
- 그래서 센서는 더 자주 읽고, 화면은 상대적으로 가볍게 그릴 수 있다.
- 처음에는 축 방향이 직감과 조금 다르게 보일 수 있다. 그럴 때는 센서 실물 방향과 화면 기준을 같이 메모하는 게 중요하다.

## 1. host `venv` 활성화

```bash
source ~/venvs/bno08x/bin/activate
```

## 2. `matplotlib` 설치 확인

```bash
pip install matplotlib
```

## 3. 비행기 뷰어 실행

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_aircraft_viewer.py --interface i2c --bus 1 --address 0x4b --rate 20
```

지연이 거슬리면 이렇게 실행하는 편이 좋다.

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_aircraft_viewer.py \
  --interface i2c \
  --bus 1 \
  --address 0x4b \
  --sensor-rate 100 \
  --rate 30
```

- `--sensor-rate`
  - 백그라운드에서 `BNO08x`를 읽는 속도
- `--rate`
  - 비행기 화면을 다시 그리는 속도

즉, 지금은 `--sensor-rate`를 높여 최신 자세를 더 자주 받고, `--rate`는 `20~30` 정도로 두는 쪽이 보통 더 부드럽다.

## 4. 화면에서 무엇을 볼지

- 파란색 와이어프레임
  - 센서의 **현재 자세**를 비행기 모양으로 표현한다.
- 회색 점선 와이어프레임
  - 프로그램 시작 순간의 **기준 자세**다.
- 빨간색 / 초록색 / 주황색 실선 축
  - 비행기 **body x / y / z**가 현재 어떻게 회전했는지 보여준다.
- 빨간색 / 초록색 / 주황색 점선 축
  - 고정된 **world x / y / z** 기준 방향이다.
- 아래 텍스트
  - `roll / pitch / yaw`
  - 현재 `accel`
  - 현재 `gyro`
  - `body: +X nose / +Y left wing / +Z up`

## 5. 현재 구현 기준 좌표 해석

- `+X`
  - 비행기 코 방향
- `+Y`
  - 비행기 왼쪽 날개 방향
- `+Z`
  - 비행기 위쪽 방향

즉, 지금 뷰어의 body frame은 아래처럼 보면 된다.

- `X`: forward
- `Y`: left
- `Z`: up

## 6. 추천 확인 동작

1. 센서를 평평하게 두고 시작
2. 앞쪽을 들고 내리면서 `pitch` 반응 확인
3. 왼쪽/오른쪽으로 기울이며 `roll` 반응 확인
4. 바닥면에서 천천히 돌려 `yaw` 반응 확인

## 7. 해석 기준

- 실물을 앞뒤로 기울였을 때 비행기 코가 같이 들리거나 내려가면 `pitch` 반응이 자연스럽다.
- 좌우로 기울였을 때 비행기 날개가 같이 기울면 `roll` 반응이 자연스럽다.
- 평면에서 돌렸을 때 비행기 머리가 돌아가면 `yaw` 반응이 자연스럽다.

## 8. 안 되면 먼저 볼 것

1. [11_Jetson_BNO08x_First_Value_Check_Guide.md](./11_Jetson_BNO08x_First_Value_Check_Guide.md) 기준 raw 값이 아직 나오는지
2. [13_Jetson_BNO08x_Live_Plot_Guide.md](./13_Jetson_BNO08x_Live_Plot_Guide.md) 기준 그래프가 먼저 뜨는지
3. 현재 터미널이 `Jetson` 로컬 GUI 터미널인지
4. `source ~/venvs/bno08x/bin/activate`가 되어 있는지

## 9. 다음 단계

- 이 비행기 뷰어에서 자세 변화가 자연스럽게 보이면
  - `imu_link` 축 해석 정리
  - `sensor_msgs/Imu` publisher 작성
  - `RViz2` 화살표/축 또는 `PlotJuggler`로 `ROS 2` 시각화
  로 넘어간다.
