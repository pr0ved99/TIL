# P10 Bringup Debugging

## 목표

실제 로봇 또는 시뮬레이션을 실행할 때 문제를 빠르게 분리하는 기본 루틴을 만든다.

## 기본 점검 순서

```bash
echo $ROS_DISTRO
ros2 node list
ros2 topic list -t
ros2 service list
ros2 action list
ros2 param list
```

## Topic 확인

```bash
ros2 topic info /cmd_vel
ros2 topic echo /cmd_vel --once
ros2 topic hz /odom
```

## TF 확인

필요하면 `tf2_tools`를 설치한다.

```bash
sudo apt install -y ros-humble-tf2-tools
```

```bash
ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_tools view_frames
```

생성된 `frames.pdf`를 열어 TF tree가 끊기지 않았는지 확인한다.

## Launch 문제 확인

```bash
ros2 launch <package_name> <launch_file.py> --show-args
ros2 launch <package_name> <launch_file.py> --debug
```

## Gazebo 문제 확인

```bash
gazebo --verbose
```

확인할 것:

- mesh load error
- plugin load error
- package URI resolve error
- `/clock` publish 여부
- `use_sim_time` 설정 여부

## 실제 하드웨어 안전 확인

- 바퀴를 띄운 상태에서 첫 테스트를 한다.
- motor enable 전 telemetry만 먼저 확인한다.
- `/cmd_vel` timeout을 확인한다.
- emergency stop 경로를 확인한다.
- battery voltage와 fault flag를 확인한다.

## 확인 기준

- 문제가 node, topic, TF, launch, Gazebo, hardware 중 어디에 있는지 분리할 수 있다.
- 실패 로그와 재현 명령을 기록할 수 있다.
