# 2026-04-29 Mari RTAB-Map Local Odom Smoke Evidence

## 결론

- 이 폴더는 RTAB-Map이 raw Gazebo `/odom` 대신 local EKF output인 `/odometry/local`을 입력으로 받아 map output을 만든 증빙을 보관한다.
- 이번 smoke test는 `/wheel/odometry + /imu/data -> /odometry/local -> RTAB-Map` 경로가 실제 ROS2 graph에서 동작함을 확인했다.

## 실행 흐름

```text
Gazebo /odom
-> gazebo_odom_to_encoder_ticks
-> /motor/encoder_ticks
-> encoder_ticks_to_wheel_odom
-> /wheel/odometry
-> robot_localization EKF + /imu/data
-> /odometry/local
-> RTAB-Map RGB-D mapping
```

## 확인 명령

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
python3 Tools/check_mari_rtabmap_topics.py --odom-topic /odometry/local
```

## 확인 결과 요약

| 항목 | 결과 |
| --- | --- |
| `/odometry/local` input | `[OK]`, `nav_msgs/Odometry`, 약 `10.0 Hz`, `frame=odom`, `child=base_footprint` |
| RGB image input | `[OK]`, 약 `6.7 Hz`, `640x480`, `rgb8` |
| Depth image input | `[OK]`, 약 `2.5 Hz`, `640x480`, `32FC1` |
| Camera info input | `[OK]`, 약 `15.0 Hz` |
| `/rtabmap/info` | `[OK]`, 약 `1.4 Hz`, `frame=map`, `ref_id=467`, `wm=89` |
| `/rtabmap/mapData` | `[OK]`, `nodes=1`, `poses=89`, `links=466` |
| `/rtabmap/cloud_map` | `[OK]`, `points=27973` |
| `/rtabmap/map` | `[OBS]`, `245x261`, `resolution=0.050` |

## 판정

- `/odometry/local`이 RTAB-Map odometry input으로 정상 사용됐다.
- RTAB-Map은 `/rtabmap/info`, `/rtabmap/mapData`, `/rtabmap/cloud_map`, `/rtabmap/mapPath`, `/rtabmap/map`을 publish했다.
- `poses=89`, `links=466`으로 graph가 생성됐고, cloud map도 만들어졌다.
- 따라서 `/odometry/local` 기반 RTAB-Map smoke test는 통과로 판정한다.

## 남은 확인

- Depth image rate가 약 `2.5 Hz`, RTAB-Map info rate가 약 `1.4 Hz`라서 실시간성은 추가 점검이 필요하다.
- 다음 비교는 같은 world와 비슷한 teleop 경로에서 raw `/odom` 입력 run과 `/odometry/local` 입력 run을 나눠 실행한다.
- 비교 기준은 depth image rate, RTAB-Map info/cloud_map rate, poses/links 증가, graph optimization warning, 체감 끊김이다.
