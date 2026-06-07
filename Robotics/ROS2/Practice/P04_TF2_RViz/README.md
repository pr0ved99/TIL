# P04 TF2 And RViz2

## 목표

TF tree가 RViz2 시각화와 Nav2의 기준이라는 것을 확인한다.

## 실행

static transform publish:

```bash
ros2 run tf2_ros static_transform_publisher \
  0 0 0.10 0 0 0 base_link camera_link
```

다른 터미널:

```bash
ros2 run tf2_ros tf2_echo base_link camera_link
rviz2
```

RViz2에서:

- Fixed Frame: `base_link`
- Add -> TF
- Add -> Axes

## 확인 기준

- RViz2에서 `base_link`와 `camera_link` frame이 보인다.
- `tf2_echo`에서 transform 값이 계속 출력된다.

## 프로젝트 연결

실제 로봇에서는 `base_link -> camera_link`, `base_link -> imu_link`, `base_link -> lidar_link`가 모두 정확해야 한다. 센서 frame이 틀리면 obstacle, point cloud, camera 좌표가 모두 틀어진다.
