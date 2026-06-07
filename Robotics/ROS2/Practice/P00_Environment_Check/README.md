# P00 Environment Check

## 목표

현재 노트북에서 ROS 2 Humble, RViz2, Gazebo classic이 정상 동작하는지 확인한다.

## 실행

```bash
echo $ROS_DISTRO
which ros2
ros2 doctor
which rviz2
which gazebo
gazebo --version
```

GUI 확인:

```bash
rviz2
gazebo --verbose
```

## 확인 기준

- `ROS_DISTRO`가 `humble`로 출력된다.
- `ros2 doctor`가 큰 오류 없이 통과한다.
- RViz2 창이 열린다.
- Gazebo classic 11 창이 열린다.

## 기록할 것

- ROS 2 버전
- Gazebo 버전
- GUI 실행 여부
- 오류 로그가 있으면 원문과 원인 가설
