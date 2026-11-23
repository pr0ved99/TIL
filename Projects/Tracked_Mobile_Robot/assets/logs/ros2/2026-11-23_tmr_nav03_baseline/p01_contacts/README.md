# P01 직진과 Gazebo 접촉 계측

원점에서 지도 좌표 (0.60 m, 0 m), 방향 0°를 목표로 보냈다. 각 회차는 도메인 86의 새 headless 월드에서 시작했다. P02~P05와 같은 후보 설정인 도착 허용치 0.15 m·0.12 rad, 진행 확인기 0.50 m·10초, MPPI 목표 방향 비용 적용 거리 0.15 m·가중치 3.0을 읽어 확인했다.

| Gazebo 시드 | 도착 시간 | 정지 후 월드 x | 위치 오차 | 방향 오차 | 복구 | 바닥 접촉 레코드 | 장애물 접촉 횟수 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3102 | 4.74초 | 0.462 m | 13.82 cm | 0.97° | 0 | 21,791 | 0 |
| 3103 | 4.70초 | 0.460 m | 14.06 cm | 1.21° | 0 | 21,773 | 0 |

두 액션 모두 성공했다. 마지막 속도 명령과 정지 후 약 2.01초간 오도메트리 60표본의 속도 여섯 성분이 0이었다. 접촉 집계 창은 목표 전송 직전의 최신 오도메트리 시각부터 정지 관측 종료까지 각각 7.344 시뮬레이션 초였다. 양쪽 바퀴와 앞뒤 지지부에서 바닥을 검출했다. 두 회차 모두 서로 다른 물리 시각 7,345개에 바닥 접촉이 있었고, 연속 시각 사이 최장 간격은 1 ms였다. [측정 요약](p01_summary.json) · [Nav2 액션 로그](p01_events.txt) · [주행 시계열](p01_navigation.json.gz) · [3102 접촉 원자료](contact-3102.json.gz) · [3103 접촉 원자료](contact-3103.json.gz)

## 접촉을 세는 방법

주행용 Xacro를 Gazebo SDF로 변환한 다음 차체, 앞·뒤 지지부, 좌·우 바퀴의 충돌 형상 다섯 개에 접촉 센서를 하나씩 붙였다. 두 P01 주행과 아래 교정 실험에서 같은 센서 모델을 사용했다. 생성한 SDF에서 센서 요소 다섯 개를 제거하면 변환 직후 원본과 XML 구조가 일치했다. 기존 월드의 Contact 시스템이 물리 엔진의 접촉 쌍을 Gazebo Transport로 발행한다. 센서에 접촉이 있을 때만 해당 토픽에 메시지가 생긴다. [센서 생성 도구](instrument_sdf.py) · [토픽 목록](topics.json) · [Gazebo Harmonic Contact 구현](https://github.com/gazebosim/gz-sim/blob/gz-sim8/src/systems/contact/Contact.cc)

기록기는 시뮬레이션 시각, 센서 토픽, 양쪽 충돌 형상의 전체 이름을 저장한다. 로봇과 `ground_plane::ground::collision` 쌍은 바닥, 로봇 내부끼리는 자체 접촉, 로봇과 다른 모델은 장애물로 분류한다. 이름을 식별할 수 없는 쌍은 별도 집계한다. 동일 장애물 모델에 여러 로봇 부위가 닿아도 하나의 접촉 구간으로 합치며, 마지막 접촉 후 **100 ms를 초과하는** 시뮬레이션 시간 공백이 있으면 다음 접촉으로 센다. 100 ms는 이 평가의 집계 규칙이다. 더 짧은 간격으로 떨어졌다 다시 닿으면 한 구간에 포함된다. 센서가 작동하는지는 토픽 목록과 바닥 접촉 시각의 연속성, 벽 접촉 양성 대조로 확인했다. [기록·집계 코드](contacts.py)

## 실제 벽 접촉 양성 대조

Nav2 주행과 분리된 Gazebo 파티션 `tmr-nav03-contact-inspect`에서 동일 규격의 정적 벽을 (+0.38, 0, 0.20) m에 배치했다. 시드 3102로 시작한 가상 로봇에 +0.08 m/s로 접근, −0.08 m/s로 후진, 분리 상태에서 정지, 재접근, 후진, 정지 순서로 명령했다. 장애물 레코드 2,435개 모두 차체와 `contact_cal_wall`의 접촉이었고, 기록기는 이를 두 구간으로 집계했다. 최초 바닥 대기, 두 접촉 사이 분리 정지, 마지막 정지 구간에는 바닥만 관측됐다.

| 접촉 구간 | 첫 시각 (sim s) | 마지막 시각 (sim s) | 관측된 물리 시각 수 |
| --- | ---: | ---: | ---: |
| 벽에 첫 접근 | 134.233 | 135.364 | 1,132 |
| 후진 후 재접근 | 139.879 | 141.181 | 1,303 |

이 검증은 차체와 한 고정 벽의 반복 접촉에 대한 양성 대조다. 과거 P02~P05 주행에는 이 관측기가 없었다. 당시 충돌 횟수는 미계측으로 유지한다. [단계별 결과](calibration.json) · [교정 접촉 원자료](calibration_contacts.json.gz) · [Gazebo 교정 동작](calibrate.py)

아래 재현 절차를 새 월드에서 다시 실행했다. 두 번째 실행에서도 장애물 레코드 2,991개를 벽 접촉 두 구간으로 집계했다. [재실행 접촉 원자료](calibration_replay_contacts.json.gz)

## 재현

저장된 세 접촉 파일은 이 폴더에서 아래 명령으로 다시 집계할 수 있다.

```bash
source /opt/ros/jazzy/setup.bash
python3 contacts.py contact-3102.json.gz
python3 contacts.py contact-3103.json.gz
python3 contacts.py calibration_contacts.json.gz
```

교정 실험을 다시 실행하려면 첫 터미널에서 아래 명령으로 별도 검증 월드를 연다.

```bash
source /opt/ros/jazzy/setup.bash
project_dir=~/workspace/github-repos/TIL/Projects/Tracked_Mobile_Robot
export GZ_PARTITION=tmr-nav03-contact-inspect ROS_DOMAIN_ID=87 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
gz sim -r -s --headless-rendering --seed 3102 "$project_dir/05_ROS2_Integration/src/tmr_sim/worlds/drive.sdf"
```

두 번째 터미널에서 해당 파티션에 로봇과 검증 벽을 생성하고 교정을 실행한다. 새 기록은 임시 디렉터리에 저장된다. 교정이 끝나면 첫 터미널에서 Ctrl+C로 월드를 종료한다.

```bash
source /opt/ros/jazzy/setup.bash
project_dir=~/workspace/github-repos/TIL/Projects/Tracked_Mobile_Robot
evidence_dir="$project_dir/assets/logs/ros2/2026-11-23_tmr_nav03_baseline/p01_contacts"
export GZ_PARTITION=tmr-nav03-contact-inspect ROS_DOMAIN_ID=87 ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
work_dir=$(mktemp -d)
cd "$work_dir"
xacro "$project_dir/05_ROS2_Integration/src/tmr_description/urdf/tmr.urdf.xacro" gazebo_drive:=true > base.urdf
gz sdf -p base.urdf > base.sdf
python3 "$evidence_dir/instrument_sdf.py" base.sdf measured.sdf topics.json
ros2 run ros_gz_sim create -world empty -name tmr -file "$work_dir/measured.sdf" -z 0.02
ros2 run ros_gz_sim create -world empty -name contact_cal_wall -file "$project_dir/assets/logs/ros2/2026-11-22_tmr_lidar_amcl/scan_test_wall.sdf" -x 0.38 -z 0.20
python3 "$evidence_dir/calibrate.py"
```

정식 주행에서는 동일한 센서 SDF를 TMR로 한 번 생성하고 기존 URDF 기반 상태 발행기·브리지·Nav2를 사용한다. 도달 액션을 보내기 전에 다섯 토픽과 바닥 접촉 수신을 확인하고, 목표 전송부터 정지 확인까지 같은 시뮬레이션 시각 창으로 집계한다.
