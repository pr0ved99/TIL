# TMR 2D 목표 도달 환경과 주행 정책

Python과 NumPy로 만든 4 × 4 m 방에서 로봇에 선속도와 각속도를 준다. 한 번의 `step()`은 가상 시간 0.1초를 진행하고 새 관측, 보상, 종료 여부를 돌려준다. 독립 CPU 환경이므로 터미널에서 바로 실험할 수 있다.

## 명령을 직접 바꿔 보기

현재 노트북에는 `~/.venvs/tmr-rl`에 의존성이 설치돼 있다. 새 Ubuntu 환경에서는 아래 작업 디렉터리에서 `python3 -m venv ~/.venvs/tmr-rl`과 `~/.venvs/tmr-rl/bin/python -m pip install -r requirements.txt`를 한 번 실행한다.

```bash
cd ~/workspace/github-repos/TIL/Projects/Tracked_Mobile_Robot/05_ROS2_Integration/rl
~/.venvs/tmr-rl/bin/python tmr_env.py --linear 0.10 --angular 0 --steps 10
~/.venvs/tmr-rl/bin/python tmr_env.py --linear 0 --angular 0.39 --steps 10
~/.venvs/tmr-rl/bin/python tmr_env.py --scenario blocked --linear 0.10 --steps 800
~/.venvs/tmr-rl/bin/python check_env.py
```

각 명령은 초기 위치에서 시작한다. 첫 두 명령은 1초 동안 전진과 제자리 좌회전을 적용한다. 세 번째는 정면에 기둥을 둔다. `dx`·`dy`는 방 좌표계에서의 변위이고 `yaw_change`는 시작 방향을 기준으로 ±180° 범위에 표시한 최종 각도다. `front_scan`은 차체 앞쪽에 있는 센서에서 물체 표면까지의 거리다. 실행 결과에는 실제 벽시계 시간과 독립적인 가상 시간이 표시된다.

## 관측과 보상

| 항목 | 구현한 규칙 |
|---|---|
| 방과 시작 조건 | 정사각형 방 중앙에 반지름 0.30 m의 기둥 하나를 둔다. 기본 `reset(seed=...)`은 바깥쪽 자유 지점 8개에서 서로 다른 출발점·목표를 고르고 시작 방향을 뽑는다. `straight`와 `blocked`는 초기 자세를 고정한 수동 검사용이다. |
| 관측 29개 | 처음 24개는 정면부터 반시계 방향으로 15° 간격의 거리(m)다. 나머지는 목표까지의 거리(m), 상대 방향의 cos·sin, 현재 선속도(m/s), 현재 각속도(rad/s)다. 검사용 절대 자세와 목표 좌표는 `info`에서만 제공한다. |
| 행동 2개 | 코드의 `step([전후진, 회전])`은 각각 −1~1을 받아 ±0.10 m/s와 ±0.39 rad/s로 환산한다. 터미널의 `--linear`와 `--angular`에는 물리 단위를 직접 준다. 양의 선속도는 전진, 양의 각속도는 좌회전이다. |
| 운동과 충돌 | 매 스텝 방향을 먼저 갱신하고 그 방향으로 이동한다. 발자국 네 꼭짓점을 감싸는 반지름 약 0.190 m의 원으로 차체를 근사한다. 이동 구간에서 원이 기둥이나 벽에 닿으면 직전 자세에서 속도를 0으로 두고 종료한다. |
| 거리 스캔 | 센서 원점은 차체 중심에서 앞쪽으로 0.065 m다. 측정 거리를 0.10~8.0 m로 제한한다. 방과 기둥은 고정이며 거리·자세에 잡음을 넣지 않았다. |
| 보상 | 한 스텝마다 줄어든 목표 거리(m)에서 시간 비용 0.001과 회전 비용 `0.0005 × abs(정규화 회전 명령)`을 뺀다. 도착 시 +5, 충돌 시 −5를 더한다. 출발 위치로 왕복하면 거리 보상의 합은 0이고 시간 비용이 남는다. |
| 에피소드 종료 | 중심이 목표 0.15 m 이내면 `goal`, 접촉하면 `collision`이며 둘 다 `terminated=True`다. 기본 800스텝(80초)을 소진하면 `timeout, truncated=True`다. 마지막 스텝에 도착하거나 충돌하면 그 결과가 우선한다. |

물리 속도 한계·차체 치수·목표 거리 허용치는 TMR Nav2 설정에 맞췄다. 센서 위치·거리 한계·주기는 가상 LiDAR 모델에서 가져왔다. 방 형태, 원형 충돌 모델, 24개 빔, 보상 계수와 시간 한도는 첫 실험에서 정한 값이다. 궤도 슬립, 가속 지연, 위치추정 오차는 이 모델의 평가 범위 밖이다. [Nav2 설정](../src/tmr_sim/config/nav2_params.yaml) · [가상 LiDAR 모델](../src/tmr_description/urdf/tmr.urdf.xacro) · [Gymnasium 환경 API](https://gymnasium.farama.org/api/env/)

## 검증과 다음 실험

Gymnasium 환경 검사와 별개로 스캔의 방향·거리, 전후진과 양방향 회전량, 목표·기둥·벽·시간 제한, 정지·제자리 회전·왕복의 보상 및 같은 시드 재생을 검사한다. 시드 32개를 두 환경에 각각 넣어 총 640개 행동에서 결과가 일치했다. 위 검사의 고정 명령은 동작 확인용이다. [검증 출력](../../assets/logs/ros2/2026-11-24_tmr_rl01/checks.txt) · [환경 검사 API](https://gymnasium.farama.org/api/utils/)

## RL-02 규칙 제어기

같은 방에서 제어기가 0.1초마다 24방향 스캔과 목표의 상대 거리·방향을 읽어 선속도와 각속도를 정한다. 위 작업 디렉터리에서 기둥 앞 주행과 정식 평가를 재현할 수 있다.

```bash
~/.venvs/tmr-rl/bin/python evaluate_baseline.py --demo blocked
~/.venvs/tmr-rl/bin/python evaluate_baseline.py
```

첫 명령은 1초 간격으로 `front(m)`(정면 거리), `v(m/s)`(전진 명령), `w(rad/s)`(회전 명령)를 보여준다. 첫 줄은 정면 0.635 m, 전진 0, 좌회전 +0.390 rad/s다. 2초 줄에서는 전진 0.089 m/s로 바뀐다. 고정 전진은 5.1초에 충돌했고 이 규칙은 왼쪽으로 우회해 25.0초에 도착했다. [경로 그림](../../assets/logs/ros2/2026-11-24_tmr_rl02/blocked_paths.png) · [0.1초 간격 좌표와 명령](../../assets/logs/ros2/2026-11-24_tmr_rl02/blocked_trace.csv)

### 속도를 정하는 규칙

1. 라이다가 측정한 점들을 차체 좌표계로 옮긴다. 목표 방향으로 최대 0.75 m 길이의 선분을 긋고, 측정점이 선분에서 차체 반경 + 0.09 m 이내에 들어오는지 살핀다. 목표가 가까우면 선분을 목표 거리까지만 검사한다.
2. 그 통로가 비어 있으면 목표를 향한다. 막혀 있으면 15° 간격으로 다른 방향의 통로를 검사한다. 필요한 우회각이 비슷할 때는 왼쪽을 먼저 고른다. 예제 개발 중 좌우 선택이 반복되어, 우측 후보에 빔 한 칸보다 약간 큰 16°의 비용을 주었다. 고정 기둥 예제의 도착 시간이 이 변경 전 38.6초에서 25.0초로 줄었다.
3. 선택한 방향까지의 각도에 비례해 회전한다. 각도 차가 40° 이상이면 제자리에서 돌고, 정면에 가까워질수록 최대 0.10 m/s까지 전진한다. 모든 후보가 막히면 두 명령 모두 0이다. 제어기에 들어가는 데이터는 현재 관측 한 건이다. [규칙 코드](rule_policy.py)

### 평가 조건과 결과

- **조건**은 RL-01 기본 방과 중앙 기둥, 목표 반경 0.15 m, 800스텝(80초)이다. 시드 22000~22019 각각에 대해 `reset(seed=..., options={"scenario": "random"})`을 1회 수행해 출발점·목표·초기 방향을 고정했다. 20회에 서로 다른 출발점·목표 쌍은 16개였다.
- **분모**는 위 20회다. `straight`·`blocked` 고정 예제 2개와 개발 확인 시드 0~11은 별도다. 이후 PPO 파일럿에서도 평가 세트는 학습과 파라미터 선택에서 제외한다. 비교할 때는 같은 환경과 관측을 쓰고 같은 시드로 재설정한다.
- **결과**는 도착 20/20, 충돌 0, 시간 초과 0이다. 평균 가상 시간은 23.4초(11.8~36.3초), 평균 차체 중심 경로 길이는 1.909 m였다. 같은 조건을 다시 실행해 20행 전체가 일치했다. 각 회차는 `goal`·`collision`·`timeout` 중 하나로 집계한다. [회차별 결과](../../assets/logs/ros2/2026-11-24_tmr_rl02/episodes.csv) · [평가 코드](evaluate_baseline.py)
- **적용 범위**는 잡음이 없는 방 한 개와 고정 기둥 한 개다. 새 지도에 대한 평가는 RL-04에서 다룬다.

## RL-03 CPU PPO 파일럿

PPO는 스캔·상대 목표·현재 속도 29개를 입력으로 받아 전후진과 회전 명령 두 개를 낸다. 학습 때는 명령을 샘플링하고 그 결과로 받은 보상을 사용해 신경망의 가중치를 갱신한다. 평가 때는 매번 정책이 정한 대표 명령을 사용한다. [학습 코드](train_ppo.py) · [Stable-Baselines3의 PPO 설명](https://stable-baselines3.readthedocs.io/en/v2.7.1/modules/ppo.html)

초기 조건을 먼저 고정했다. 은닉층 64개 유닛 두 층, 학습 시드 3101, 환경 한 개에서 65,536스텝이다. 1,024스텝씩 동작을 모은 뒤 배치 64개, 6에폭으로 갱신한다. `device="cpu"`, PyTorch 연산 스레드 1개로 실행한다. 학습 시간 180초와 프로세스 최대 상주 메모리 2,048 MiB를 중단 기준으로 뒀다. RL-01과 같은 관측·보상·속도·시간 한도를 사용하며 학습 환경에는 RL-02 평가 시드를 지정하지 않는다.

### 저장한 정책으로 주행해 보기

위 실습 디렉터리에서 실행한다. 첫 명령은 기둥 앞에서의 속도 결정을 1초 간격으로 보여준다. 두 번째는 RL-02의 고정 시드 20개를 전부 평가한다. `--ppo`를 생략하면 같은 조건에서 규칙 제어기를 실행한다.

```bash
model=../../assets/logs/ros2/2026-11-24_tmr_rl03/ppo.zip
~/.venvs/tmr-rl/bin/python evaluate_baseline.py --ppo "$model" --demo blocked
~/.venvs/tmr-rl/bin/python evaluate_baseline.py --ppo "$model"
```

별도 환경을 준비할 때는 기존 TMR 가상환경에 아래 첫 줄로 CPU 패키지를 설치한다. 두 번째 명령은 새 결과 디렉터리에 학습 기록과 모델을 만든다. 설치와 실행은 ROS 환경 변수에 의존하지 않는다.

```bash
env -u PYTHONPATH ~/.venvs/tmr-rl/bin/python -m pip install -r requirements-ppo.txt
env -u PYTHONPATH OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 ~/.venvs/tmr-rl/bin/python train_ppo.py ~/tmr-ppo-replay
```

### 첫 파일럿 결과

아래의 각 행은 같은 방에서 동일한 초기 상태 20개(시드 22000~22019)로 시작했다. 성공은 목표 반경 0.15 m 이내 도달, 시간 초과는 가상 시간 80초다. 평균 최종 거리는 실패한 회차도 포함한다.

| 정책 | 도착 | 충돌 | 시간 초과 | 평균 최종 목표 거리 |
|---|---:|---:|---:|---:|
| PPO 학습 전 | 0 | 0 | 20 | 1.912 m |
| PPO 65,536스텝 후 | 2 | 2 | 16 | 0.960 m |
| 규칙 제어 | 20 | 0 | 0 | 0.145 m |

학습에 35.189초가 걸렸고 프로세스 시작부터 학습 종료까지 최대 상주 메모리는 348.59 MiB였다. 모델 초기화·규칙과 학습 전후 평가·저장을 포함한 계측 구간은 45.163초였다. 학습 중 끝난 89회는 도착 5회, 충돌 13회, 시간 초과 71회였으며 별도의 평가 분모에서 제외했다. 새로운 프로세스에서 체크포인트를 재생해 학습 후 평가 20행이 전부 일치했고 규칙 제어 20행도 RL-02 결과와 일치했다. [버전·설정·시간·메모리](../../assets/logs/ros2/2026-11-24_tmr_rl03/run.json) · [학습 에피소드 원본](../../assets/logs/ros2/2026-11-24_tmr_rl03/train.monitor.csv) · [평가 60행](../../assets/logs/ros2/2026-11-24_tmr_rl03/evaluation.csv)

별도 기둥 예제에서 규칙 제어는 25초에 도착했다. 학습된 정책은 가상 시간 80초간 총 2.026 m를 움직였고 목표까지 1.652 m가 남았다. 이 모델의 평가 범위는 방 하나와 학습 시드 하나다. 다음 RL-04에서 다른 학습 시드와 미학습 지도를 평가한다. [목표 거리 변화 그림](../../assets/logs/ros2/2026-11-24_tmr_rl03/blocked_goal_distance.png) · [저장 모델](../../assets/logs/ros2/2026-11-24_tmr_rl03/ppo.zip)

## RL-04 독립 평가

중앙에 반지름 0.30 m 기둥 하나가 있는 방에서만 PPO를 학습했다. 3101은 RL-03에서 저장한 모델을 사용했고, 3102와 3103은 같은 설정으로 각각 65,536스텝을 새로 학습했다. 평가 전에 두 번째 방의 기둥 중심을 (−0.55, 0.35) m와 (0.55, −0.35) m, 반지름을 각각 0.26 m로 고정했다. 방 크기·경유점 후보·센서·보상·속도·도착 조건·시간 한도는 두 방에서 같다.

시드 24000~24019가 정한 20개 출발 자세와 목표를 두 방과 네 제어기에 공통 적용했다. 이전 파일럿의 22000~22019와 구분한 평가 세트다. 평가에는 훈련을 끝낸 모델의 결정론적 명령을 사용했다. 기존 규칙 제어기도 같은 조건에서 실행했다. [사전에 고정한 조건과 모델 위치](../../assets/logs/ros2/2026-11-24_tmr_rl04/protocol.json) · [평가 코드](evaluate_holdout.py)

| 방 | 제어기 / 학습 시드 | 도착 | 충돌 | 시간 초과 | 평균 시간(s) | 평균 경로(m) |
|---|---|---:|---:|---:|---:|---:|
| single | 규칙 | 20 | 0 | 0 | 20.34 | 1.617 |
| single | PPO 3101 | 1 | 3 | 16 | 67.55 | 1.619 |
| single | PPO 3102 | 1 | 2 | 17 | 70.83 | 1.708 |
| single | PPO 3103 | 0 | 0 | 20 | 80.00 | 1.223 |
| staggered | 규칙 | 18 | 0 | 2 | 27.34 | 1.496 |
| staggered | PPO 3101 | 3 | 6 | 11 | 53.32 | 1.576 |
| staggered | PPO 3102 | 1 | 4 | 15 | 61.77 | 1.733 |
| staggered | PPO 3103 | 0 | 11 | 9 | 41.48 | 0.704 |

각 행은 20회이며 평균에는 충돌과 80초 시간 초과도 들어간다. 짧은 시간·경로에는 일찍 충돌해 끝난 주행이 포함될 수 있다. 새 방에서 규칙 제어기는 18/20 도착했고 두 시간 초과 시드 24000, 24012에서는 각각 가상 시간 7.8초, 3.2초부터 끝까지 전진·회전 명령이 모두 0이었다. 같은 출발 조건 20개를 세 PPO에 적용했을 때 새 방에서 합계 60회 중 도착 4회, 충돌 21회, 시간 초과 35회였다. 이 짧은 학습 예산과 두 방의 결과로는 PPO 전환을 뒷받침하지 않는다. [요약 CSV](../../assets/logs/ros2/2026-11-24_tmr_rl04/results/summary.csv) · [전체 160회 CSV](../../assets/logs/ros2/2026-11-24_tmr_rl04/results/evaluation.csv)

시드 24019는 출발·목표의 연결선이 새 방의 두 기둥을 지나는 경로여서 대표 그림으로 미리 골랐다. 새 방에서 규칙은 35.2초에 도착했고 PPO 3101·3103은 충돌, 3102는 시간 초과였다. 환경 검사에서 두 기둥 각각의 정면 거리와 접촉 시점, 출발 후보의 여유 공간을 확인했다. 원래 방에서 파일럿 시드의 규칙·PPO 3101 평가 40행이 이전 원본과 일치했다. 독립 평가를 새 프로세스에서 다시 돌려 회차별 결과·요약·대표 궤적 CSV가 바이트 단위로 일치하는 것도 확인했다. [대표 경로 그림](../../assets/logs/ros2/2026-11-24_tmr_rl04/example_paths.png) · [스텝별 좌표](../../assets/logs/ros2/2026-11-24_tmr_rl04/results/example_trajectory.csv)

위 실습 디렉터리에서 저장된 모델로 표를 다시 계산하거나 한 회만 재생할 수 있다.

```bash
rl04=../../assets/logs/ros2/2026-11-24_tmr_rl04
~/.venvs/tmr-rl/bin/python evaluate_holdout.py "$rl04/protocol.json"
~/.venvs/tmr-rl/bin/python evaluate_baseline.py --layout staggered --seed 24019
~/.venvs/tmr-rl/bin/python evaluate_baseline.py --layout staggered --seed 24019 --ppo "$rl04/train_3102/ppo.zip"
```

추가 모델을 독립적으로 학습하려면 기존 RL-03 학습 명령에 `--seed 3102` 또는 `--seed 3103`과 새 출력 폴더를 지정한다. 정식 판정의 범위는 가벼운 2D 모델과 미학습 배치 한 개다. 이후 RL-05에서 Gazebo의 스캔·목표·속도·제어 주기를 대조하고 실제 시뮬레이터 주행까지 확인했다. 실제 주행 성능은 이 결과로 판정할 수 없다.

## RL-05 Gazebo 주행

정면 P01에는 시범 주행으로 초기화한 PPO가 직접 도착했다. 벽 뒤 P05에서는 같은 정책에 A* 중간 목표와 AMCL의 지도 기준 위치를 연결해 두 번 도착했다. 정책은 전후진과 회전 속도를 매 스텝 결정한다. 실제 최종 오차는 8.49 cm와 8.10 cm였다. [9회 비교·재현 절차](../../docs/verification/48_Simulation_Gate02_2026-11-24_ko.md) · [실험 파일](../../assets/logs/ros2/2026-11-24_tmr_rl05/README.md)

| 읽는 순서 | 코드에서 확인할 것 |
|---|---|
| [train_guided.py](train_guided.py) | 규칙 시범에서 배우는 단계, PPO 업데이트, 학습과 분리한 2D 검증 |
| [numpy_actor.py](numpy_actor.py) | 저장한 신경망의 행렬과 편향을 내보내고 시스템 NumPy에서 같은 속도를 계산하는 과정 |
| [grid_route.py](grid_route.py) | 점유 지도에서 우회 경로와 로봇이 따라갈 다음 지점을 얻는 과정 |
| [gazebo_goal.py](gazebo_goal.py) | ROS 스캔·위치·속도를 29개 입력으로 만들고 정책 출력을 Twist로 발행하는 루프, 정지·검증 |
| [run_gazebo_goal.py](run_gazebo_goal.py) | 고정 월드와 시험 조건 검사, headless Gazebo·ROS 브리지·선택한 위치 추정 노드·bag 구성 |

저장된 모델로 재주행할 때는 위 검증 보고서의 명령을 사용한다. 학습부터 다시 해보려면 이 디렉터리에서 아래를 실행한다. 새 모델은 새 폴더에 저장하며 Gazebo 재현 명령은 실험 당시 고정한 가중치를 읽는다.

```bash
train_dir=$(mktemp -d)
env -u PYTHONPATH OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ~/.venvs/tmr-rl/bin/python train_guided.py "$train_dir/model"
env -u PYTHONPATH ~/.venvs/tmr-rl/bin/python numpy_actor.py "$train_dir/model/ppo.zip" "$train_dir/model/actor.npz"
```
