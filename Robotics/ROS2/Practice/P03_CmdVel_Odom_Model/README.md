# P03 CmdVel And Odometry Model

## 목표

`/cmd_vel`을 left/right track speed로 바꾸고, encoder delta를 `/odom`으로 바꾸는 계산 흐름을 이해한다.

## 핵심 식

```text
v_l = v - (w * B / 2)
v_r = v + (w * B / 2)
```

```text
d_center = (d_r + d_l) / 2
d_yaw = (d_r - d_l) / B
```

## 실행 과제

Python으로 다음 함수를 작성한다.

```python
def twist_to_tracks(v_mps, w_radps, track_width_m):
    left = v_mps - (w_radps * track_width_m / 2.0)
    right = v_mps + (w_radps * track_width_m / 2.0)
    return left, right
```

테스트 입력:

```text
track_width_m = 0.137553
v_mps = 0.10
w_radps = 0.0

v_mps = 0.00
w_radps = 0.50

v_mps = 0.10
w_radps = -0.30
```

## ROS 2 연결 과제

`/cmd_vel`을 subscribe해서 left/right target speed를 출력하는 node를 만든다.

확인용 publish:

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.1}, angular: {z: 0.3}}" -r 5
```

## 확인 기준

- 직진 명령에서 left/right speed가 같다.
- 좌회전 명령에서 right speed가 left보다 크다.
- 우회전 명령에서 left speed가 right보다 크다.

## 프로젝트 연결

이 로직은 STM32로 보낼 command packet 생성 직전에 들어간다. 실제 하드웨어에서는 여기에 속도 제한, acceleration limit, deadband, timeout 처리가 추가된다.
