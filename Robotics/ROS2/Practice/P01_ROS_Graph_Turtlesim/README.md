# P01 ROS Graph With Turtlesim

## 목표

`turtlesim`으로 node, topic, message, teleop, ROS graph를 직접 확인한다.

## 실행

터미널 1:

```bash
ros2 run turtlesim turtlesim_node
```

터미널 2:

```bash
ros2 run turtlesim turtle_teleop_key
```

터미널 3:

```bash
ros2 node list
ros2 topic list -t
ros2 topic echo /turtle1/cmd_vel
ros2 topic hz /turtle1/pose
rqt_graph
```

## 확인 기준

- 방향키로 turtle이 움직인다.
- `/turtle1/cmd_vel`에 `geometry_msgs/msg/Twist`가 흐른다.
- `/turtle1/pose` rate를 확인할 수 있다.
- `rqt_graph`에서 teleop node와 turtlesim node 연결이 보인다.

## 프로젝트 연결

`/turtle1/cmd_vel`은 실제 로봇의 `/cmd_vel`과 같은 개념이다. 나중에는 teleop 또는 Nav2가 `/cmd_vel`을 publish하고, base bridge가 이를 받아 STM32로 보낸다.
