# P06 Gazebo Diff Drive

## 목표

Gazebo classic에서 differential-drive 기반 로봇을 띄우고 `/cmd_vel`, `/odom`, `/tf` 흐름을 확인한다.

## 환경 확인

```bash
which gazebo
gazebo --version
ros2 pkg list | grep -E 'gazebo_ros|gazebo_msgs|gazebo_plugins'
```

## 실행 순서

1. Gazebo 빈 world 실행

```bash
gazebo --verbose
```

2. 로봇 URDF spawn launch 작성
3. diff-drive plugin 추가
4. `/cmd_vel` publish

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.1}, angular: {z: 0.0}}" -r 5
```

5. odometry 확인

```bash
ros2 topic echo /odom
ros2 topic echo /tf
```

## 확인 기준

- Gazebo에 로봇이 보인다.
- `/cmd_vel`에 따라 로봇이 움직인다.
- `/odom`이 publish된다.
- RViz2에서 TF와 RobotModel이 함께 보인다.

## 프로젝트 연결

실제 tracked robot physics를 처음부터 완벽히 재현하지 않는다. 먼저 virtual diff-drive로 ROS 2 interface를 검증한 뒤 실제 hardware bridge로 넘어간다.
