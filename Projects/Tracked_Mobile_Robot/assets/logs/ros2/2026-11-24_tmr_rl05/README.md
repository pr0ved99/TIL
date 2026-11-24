# RL-05 · Gazebo 주행 원본

방 B의 원점에서 정면 P01과 벽 뒤 P05로 이동한 기록이다. 같은 시드 4101로 Gazebo를 매회 다시 실행했다. 원본 위치·속도·접촉으로 재판정한 9회와 수리 과정에서 나온 초기 실행을 아래에서 구분한다. [조건과 결과 해석](../../../../docs/verification/48_Simulation_Gate02_2026-11-24_ko.md) · [조건 원본](protocol.json) · [전체 CSV](results.csv) · [경로 그림](p05_paths.png)

| 확인할 내용 | 파일 |
|---|---|
| 2D 시범 학습·PPO 실행, 검증 시드별 성공 여부 | [학습 설정](guided/run.json), [훈련 에피소드](guided/ppo.monitor.csv), [투입 판정 20회](guided/qualification.csv), [이전 평가 배치 재시험 40회](guided/previous_holdout.csv) |
| 고정 정책과 재생 검산 | [SB3 체크포인트](guided/ppo.zip), [Gazebo용 NumPy 가중치](guided/actor.npz), [실제 명령 재계산](guided/command_replay.json) |
| P01 정면 주행 | [Nav2](nav2_P01/result.json), [규칙](rule_P01/result.json), [직접 PPO](guided_P01_numpy/result.json) |
| P05 벽 우회 | [Nav2 성공](nav2_P05/result.json), [규칙 시간 초과](rule_P05_run/result.json), [직접 PPO 접촉](guided_P05_numpy/result.json), [경로 + 바퀴 odom 오차 초과](guided_map_P05/result.json) |
| P05 지도 경로 + AMCL + PPO | [첫 주행](guided_map_amcl_P05/result.json), [새로 시작한 두 번째 주행](guided_map_amcl_P05_repeat/result.json), [ROS bag](guided_map_amcl_P05_repeat/bag/bag_0.mcap), [역직렬화·명령 대조](guided_map_amcl_P05_repeat/bag_check.json) |

각 정식 회차의 `trace.json.gz`에는 Gazebo 월드 위치·ROS odom·명령이, `contacts.json.gz`에는 시뮬레이터 접촉 관측이 들어 있다. 학습·규칙 주행의 `policy.csv`는 매 스텝의 스캔과 odom 시각, 추정 위치, 29개 입력, 속도 명령, 당시 목표를 담고 있다. 지도 경로를 적용한 세 회차에는 `global_path.json`도 있다. [P05 원시 궤적](guided_map_amcl_P05_repeat/trace.json.gz) · [센서 접촉](guided_map_amcl_P05_repeat/contacts.json.gz) · [정책 입력·출력](guided_map_amcl_P05_repeat/policy.csv)

## 초기 실행 기록

- `rule_P05`에서는 ROS 콜백 등록 단계에서 중단되어 최종 측정 파일이 없다. `rule_P05_retry`와 `guided_P01`은 ROS 시각의 나노초 필드를 Gazebo 필드 이름으로 읽다가 중단됐다. 어댑터가 두 메시지 형식을 구분하도록 수정했다. [수정 전 오류](rule_P05_retry/trial.log)
- `guided_P05`는 시작 시 오래된 입력을 검출해 속도 추론 0회로 정지했다. 연결 수립 후 명령을 발행하지 않는 첫 추론과 최신 스캔·odom 짝 확인을 추가했다. [정지 기록](guided_P05/result.json)
- `guided_P01_run`은 목표에 도달했으나 ROS 확장과 학습 가상환경의 NumPy 버전 경고가 있었다. `guided_P05_run`은 같은 경고가 있었고 유한하지 않은 거리 표본 처리 중 중단됐다. 시스템 Python에서 NumPy 추론을 실행하고 센서의 ±∞와 NaN을 구분한 뒤 P01·P05를 새로 측정했다. 위 CSV에서 사용하는 직접 PPO 결과는 `_numpy` 두 회차다. [P01 초기 로그](guided_P01_run/trial.log) · [P05 초기 로그](guided_P05_run/trial.log)

`verify_results.py`는 원본으로 CSV를 다시 계산한다. `check_bag.py`는 녹화 메시지와 정책 CSV를 대조하고 `plot_paths.py`는 원시 월드 좌표에서 그림을 만든다. 구동 명령과 소프트웨어 버전은 검증 보고서에 있다. [재현 절차](../../../../docs/verification/48_Simulation_Gate02_2026-11-24_ko.md#재현과-증거)

저장본 무결성은 이 폴더에서 `sha256sum --quiet -c measurements.sha256`로 확인한다. [원본·결과·가중치 해시 목록](measurements.sha256)
