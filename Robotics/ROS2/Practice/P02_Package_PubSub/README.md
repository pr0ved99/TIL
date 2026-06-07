# P02 Package And Pub/Sub

## 목표

Python 기반 ROS 2 package를 만들고, 직접 publisher/subscriber node를 작성한다.

## 실행

workspace 생성:

```bash
mkdir -p /home/proved/my_ws/ros2_ws/src
cd /home/proved/my_ws/ros2_ws/src
```

package 생성:

```bash
ros2 pkg create ros2_learning_py \
  --build-type ament_python \
  --dependencies rclpy std_msgs geometry_msgs
```

빌드:

```bash
cd /home/proved/my_ws/ros2_ws
colcon build --symlink-install
source install/setup.bash
ros2 pkg list | grep ros2_learning_py
```

## 구현 과제

`ros2_learning_py` 안에 다음 node를 만든다.

- `heartbeat_publisher`: 1초마다 문자열 publish
- `cmd_vel_watcher`: `/cmd_vel`을 subscribe해서 linear/angular 값을 출력

## 확인 기준

- 직접 만든 package가 `ros2 pkg list`에 보인다.
- publisher node가 topic을 만든다.
- subscriber node가 `/cmd_vel` 값을 읽는다.

## 프로젝트 연결

이 실습은 나중에 `tracked_robot_base_bridge` package를 만들기 위한 최소 단위다.
