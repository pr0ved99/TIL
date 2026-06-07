# P08 Nav2 Basics

## 목표

TurtleBot3 simulation으로 Nav2의 기본 입력과 출력 구조를 확인한다.

## 설치

필요하면 다음 package를 설치한다.

```bash
sudo apt install -y \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-turtlebot3 \
  ros-humble-turtlebot3-gazebo
```

## 실행

통합 simulation launch를 먼저 사용한다.

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch nav2_bringup tb3_simulation_launch.py headless:=False
```

RViz2에서:

- `2D Pose Estimate`로 초기 위치 지정
- `Nav2 Goal`로 목표 지점 지정

## 확인할 topic

```bash
ros2 topic list | grep -E 'cmd_vel|odom|scan|tf|map|costmap'
ros2 node list | grep nav2
```

## 확인 기준

- Nav2 goal을 주면 `/cmd_vel`이 publish된다.
- Gazebo 안의 TurtleBot3가 목표 지점으로 이동한다.
- RViz2에서 local/global costmap이 보인다.

## 프로젝트 연결

Nav2는 결국 우리 로봇의 `/cmd_vel`을 생성하는 상위 제어기다. 우리 robot base가 Nav2와 연결되려면 `/odom`, `/tf`, `/scan`, footprint, parameter가 맞아야 한다.
