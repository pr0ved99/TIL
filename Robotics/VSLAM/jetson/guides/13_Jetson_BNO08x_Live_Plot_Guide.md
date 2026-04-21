# 13 Jetson BNO08x Live Plot Guide

## 목적

- `BNO08x` raw 값을 숫자로만 보지 않고, `Jetson` 로컬 GUI에서 실시간 그래프로 확인한다.
- 이번 단계의 핵심은 `축 방향`, `노이즈`, `정지 시 gyro bias`, `기울기 변화`를 빠르게 눈으로 읽는 것이다.

## 언제 이 가이드를 쓰는가

- [11_Jetson_BNO08x_First_Value_Check_Guide.md](./11_Jetson_BNO08x_First_Value_Check_Guide.md) 기준으로 host `venv`에서 값 출력이 이미 성공했을 때
- `ROS 2` publisher 전에 센서 품질과 축 반응을 직관적으로 확인하고 싶을 때

## 먼저 알면 좋은 점

- 이 가이드는 `Jetson` 로컬 바탕화면 터미널에서 실행하는 편이 좋다.
- `SSH` 터미널에서도 `X11 forwarding`이 되면 가능할 수 있지만, 지금 기준 절차는 로컬 GUI다.
- 시각화는 `matplotlib`를 사용한다.

## 1. host `venv` 활성화

```bash
source ~/venvs/bno08x/bin/activate
```

## 2. `matplotlib` 설치

```bash
pip install matplotlib
```

## 3. live plot 실행

```bash
cd ~/yh_ws/TIL
source ~/venvs/bno08x/bin/activate
python ./Robotics/VSLAM/jetson/scripts/bno08x_live_plot.py --interface i2c --bus 1 --address 0x4b --rate 10 --history 20
```

## 4. 화면에서 무엇을 볼지

- `Acceleration`
  - 센서를 가만히 두면 한 축에 중력값이 크게 잡힌다.
  - 센서를 눕히거나 세우면 큰 축이 바뀐다.
- `Gyroscope`
  - 정지 상태에서는 거의 `0` 근처여야 한다.
  - 천천히 돌리면 해당 축 그래프가 부드럽게 반응해야 한다.
- `Magnetometer`
  - 주변 금속이나 방향 변화에 따라 값이 달라진다.
  - 이번 단계에서는 절대값보다 변화 양상만 먼저 본다.
- `Orientation (roll / pitch / yaw)`
  - quaternion을 사람이 읽기 쉬운 `roll / pitch / yaw`로 바꿔서 보여준다.
  - 센서를 앞뒤로 기울이면 `pitch`
  - 좌우로 기울이면 `roll`
  - 평면에서 돌리면 `yaw`
  가 주로 변해야 자연스럽다.

## 5. 같이 보는 숫자

- 창 아래 상태줄에는 아래 값이 같이 표시된다.
  - `|a|`
  - `|g|`
  - `|q|`
- 정지 상태에서
  - `|a|`는 대략 중력값 근처
  - `|g|`는 작아야 함
  - `|q|`는 대략 `1.0` 근처
  로 보는 편이 자연스럽다.

## 6. 추천 확인 동작

1. 센서를 평평하게 두고 5초 정지
2. 앞뒤로 천천히 기울이기
3. 좌우로 천천히 기울이기
4. 평면 위에서 yaw 방향으로 천천히 회전
5. 다시 정지해서 gyro가 0 근처로 돌아오는지 확인

## 7. 안 되면 먼저 볼 것

1. 현재 터미널이 `Jetson` 로컬 GUI 터미널인지
2. `source ~/venvs/bno08x/bin/activate`를 했는지
3. `pip install matplotlib`가 끝났는지
4. [11_Jetson_BNO08x_First_Value_Check_Guide.md](./11_Jetson_BNO08x_First_Value_Check_Guide.md) 기준 raw 값 출력이 아직 되는지

## 8. 다음 단계

- live plot에서 축과 반응이 자연스러우면
  - `sensor_msgs/Imu` publisher 작성
  - `/imu/data` publish
  - `RViz2` 또는 `PlotJuggler` 기반 `ROS 2` 시각화
  순서로 넘어간다.
