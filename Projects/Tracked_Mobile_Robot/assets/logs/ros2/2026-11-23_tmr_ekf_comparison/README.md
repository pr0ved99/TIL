# SIM-05 바퀴 오도메트리와 IMU의 첫 EKF 비교

TMR 기본 `drive.launch.py headless:=true`로 빈 월드를 열고 별도 ROS 도메인 73에서 Jazzy `robot_localization` 3.8.4의 `ekf_node`를 실행했다. 바퀴 전진 속도와 IMU의 Z축 각속도를 넣어 평면 위치·방향을 추정했다. Gazebo 월드 자세는 비교에만 사용했다. 원래의 바퀴 자세와 IMU 절대 방향은 입력에서 껐다. IMU 메시지의 공분산은 미지정이며 이번 시험은 최적 가중치나 실물 잡음을 검증하지 않았다. [실행한 설정](ekf.yaml)

| 동작 | Gazebo 월드 | 바퀴 오도메트리 | EKF |
| --- | ---: | ---: | ---: |
| 직진 평면 변위 | 19.83 cm | 19.87 cm | 20.04 cm |
| 좌회전 방향 변화 | +50.24° | +44.66° | +50.10° |
| 우회전 방향 변화 | −50.34° | −44.73° | −50.49° |

`forward_stop`, `turn_stop left`, `turn_stop right`를 순서대로 각각 한 번 실행했다. 각 동작 전후 정지한 0.5초 구간에서 위치·방향의 중앙값을 구해 방향 변화와 평면 이동 거리를 계산했다. 좌·우회전의 월드 대비 방향 변화 오차는 바퀴 5.57°·5.61°, EKF 0.13°·0.15°였다. 직진 거리 오차는 바퀴 약 0.4 mm, EKF 약 2.1 mm였다. [결과와 시각 구간](result.json) · [월드·바퀴·EKF·IMU 원자료](samples.json.gz) · [ROS bag](bag/metadata.yaml)

실행 중 EKF 파라미터를 읽어 두 입력 마스크와 `publish_tf: false`를 확인했다. EKF 출력은 `/odometry/filtered`, 원래 입력은 `/odom`이며 두 오도메트리의 프레임은 `odom`과 `base_footprint`였다. Jazzy EKF가 ROS 그래프에 `/tf` 발행자로 등록되는 것과 특정 변환을 실제 송신하는 것을 구분했다. 수신한 `odom → base_footprint`의 DDS 발행자 ID를 노드와 대조하니 브리지 하나에서만 왔다. 예비 실행에서 그래프의 발행자 목록만으로 판정하다 검증이 중단돼, 이 기록은 송신자를 직접 계측한 재실행 결과로 작성했다. [변환 송신 기록](tf_origin.log)

같은 로컬 ROS 도메인과 `GZ_PARTITION`을 쓰는 터미널에서 먼저 `ros2 launch tmr_sim drive.launch.py headless:=true`를 시작한다. 다른 터미널에서 이 폴더의 설정으로 다음 명령을 실행한 뒤, 별도 터미널에서 각 동작 사이 정지를 두고 세 주행 명령을 실행한다.

```bash
ros2 run robot_localization ekf_node --ros-args -r __node:=ekf_filter_node --params-file "$PWD/ekf.yaml"
```

사용자가 설정을 `src/tmr_sim/config/ekf.yaml`에 저장했다. 기본 Nav2로 전환할 때는 바퀴 원본과 EKF 출력 토픽을 분리하고, 동적 `odom → base_footprint` 송신을 EKF 한 곳으로 넘기는 단계가 남아 있다.

## 패키지 설정으로 좌회전 재현

패키지에 저장한 YAML과 비교용 파일이 일치했다. 새 파일을 설치 경로에 등록하려고 ROS 워크스페이스에서 `colcon build --packages-select tmr_sim --symlink-install`을 실행했다. 새 로컬 도메인 74의 기본 주행 시뮬레이션에서 다음 명령으로 EKF를 실행하고 `ros2 run tmr_sim turn_stop left`를 한 번 실행했다.

```bash
ros2 run robot_localization ekf_node --ros-args -r __node:=ekf_filter_node --params-file "$(ros2 pkg prefix --share tmr_sim)/config/ekf.yaml"
```

회전 명령 중 안정 구간의 각속도 중앙값은 바퀴 +0.3927, IMU와 EKF 모두 +0.4420 rad/s였다. 동작 전후 0.5초 정지 구간의 중앙값으로 계산한 회전각은 Gazebo 월드 +50.26°, 바퀴 +44.68°, EKF +50.52°였다. 정지 후 두 오도메트리의 각속도는 사실상 0이었다. `publish_tf: false`를 실행 중 읽고 실제 `odom → base_footprint` 송신자는 브리지 하나인 것을 확인했다. [각속도와 회전각 그림](package_left/left_turn.png) · [측정값과 구간](package_left/result.json) · [원표본](package_left/samples.json.gz) · [ROS bag](package_left/bag/metadata.yaml)
