# 2026-04-29 Mari Encoder Odom Smoke Evidence

## 결론

- 이 폴더는 Gazebo에서 Mari를 움직일 때 encoder tick과 wheel odometry topic이 실시간으로 변하는 증빙을 보관한다.
- 이번 영상은 왼쪽에 Gazebo, 오른쪽에 terminal `ros2 topic echo /motor/encoder_ticks`를 띄워 tick 값이 실시간으로 증가하는 것을 확인한 기록이다.

## 파일 목록

| 파일 | 설명 |
| --- | --- |
| `01_gazebo_mari_realtime_encoder_ticks.webm` | Gazebo Mari 주행 중 `/motor/encoder_ticks` 값이 실시간으로 변화하는 영상 |

## 실행 흐름

```text
Gazebo /odom
-> gazebo_odom_to_encoder_ticks
-> /motor/encoder_ticks
-> encoder_ticks_to_wheel_odom
-> /wheel/odometry
```

## 확인 명령

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
ros2 launch trashbot_description gazebo_mari.launch.py use_mesh_visual:=true
ros2 launch trashbot_localization mari_gazebo_encoder_odom.launch.py
python3 Tools/teleop_mari_keyboard.py
ros2 topic echo /motor/encoder_ticks
```

## 판정

- Gazebo에서 Mari가 움직일 때 `/motor/encoder_ticks`가 실시간으로 변하는 것을 육안 확인했다.
- 이 값은 실제 하드웨어 encoder가 아니라 Gazebo `/odom`으로부터 만든 fake encoder tick이다.
- 실제 하드웨어에서는 motor driver가 `/motor/encoder_ticks`를 직접 publish해야 한다.
