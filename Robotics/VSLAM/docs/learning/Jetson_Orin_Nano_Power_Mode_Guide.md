# Jetson Orin Nano 전력 모드 정리

## 결론

- Jetson 우상단에 보이는 `25W`와 `Balanced`는 **같은 설정이 아니다**.
- `25W`는 `nvpmodel` 기준 **Jetson 전력 모드**이고, `Balanced`는 Ubuntu 쪽 **일반 전원 프로필 표시**다.
- 따라서 `Balanced`를 `Performance`로 못 바꾼다고 해서, Jetson이 저성능 모드로 고정됐다고 바로 판단하면 안 된다.
- 지금 실무적으로 더 중요한 것은 아래 2가지다.
  1. 현재 `nvpmodel`이 실제로 몇 W 모드인지 확인
  2. `jetson_clocks`로 CPU / GPU / 메모리 클럭을 최대 고정할지 결정

## 용어 한 줄 설명

- `nvpmodel`: Jetson의 전력 예산과 성능 모드를 정하는 NVIDIA 도구다.
- `jetson_clocks`: CPU, GPU, 메모리 클럭을 가능한 높은 값으로 고정하는 도구다.
- `Balanced`: Ubuntu 데스크톱의 일반 전원 프로필 표시다.
- `Performance`: Ubuntu GUI에서 보이는 일반 성능 프로필 이름이다.
- `MAXN`: Jetson에서 가능한 최대 성능 쪽 모드를 뜻한다.

## 왜 헷갈리기 쉬운가

직관:
우상단에 `25W`도 보이고 `Balanced`도 보이니, 둘이 같은 성능 설정처럼 보인다.

핵심:

1. `25W`는 NVIDIA가 Jetson 하드웨어에 적용한 전력 모드다.
2. `Balanced`는 Ubuntu 전원 UI다.
3. 따라서 `Balanced`가 그대로여도, 실제 Jetson은 이미 `25W` 고성능 모드일 수 있다.

즉, `Balanced` 문구만 보고 성능이 낮다고 판단하면 안 된다.

## 지금 먼저 확인할 것

Jetson 터미널에서 아래 명령을 본다.

```bash
sudo nvpmodel -q --verbose
sudo jetson_clocks --show
```

### 1. `nvpmodel` 확인

목적:
- 현재 Jetson이 실제로 어떤 전력 모드로 동작하는지 확인

예시:

```bash
sudo nvpmodel -q --verbose
```

여기서 봐야 하는 것:
- 현재 mode ID
- 현재 power mode 이름
- 최대 전력 예산

### 2. `jetson_clocks` 확인

목적:
- CPU / GPU / EMC 클럭이 최대 고정인지 확인

예시:

```bash
sudo jetson_clocks --show
```

이 명령은 지금 클럭 설정을 보여준다.

## RTAB-Map 관점에서 가장 실용적인 설정

`RTAB-Map`은 RGB-D 입력, 특징 추출, 오도메트리, 시각화를 동시에 하므로 CPU / 메모리 대역폭 영향을 많이 받는다.

따라서 가장 먼저 해볼 만한 설정은 아래다.

```bash
sudo jetson_clocks
```

이유:
- `Balanced` GUI를 건드리는 것보다
- 실제 연산 클럭을 최대 고정하는 것이
- `RTAB-Map`, `realsense2_camera`, `rtabmap_viz` 성능에 더 직접적이다.

## 권장 점검 순서

1. 현재 `nvpmodel` 확인
2. `jetson_clocks --show` 확인
3. `sudo jetson_clocks` 적용
4. 그 뒤에 `ros2 topic hz`, `CPU 사용량`, `RTAB-Map 체감 부드러움` 재확인

즉, GUI의 `Balanced`를 먼저 의심하지 말고, **실제 Jetson 하드웨어 모드와 클럭 상태를 먼저 확인**하는 게 맞다.

## 자주 하는 오해

### 오해 1. `Balanced`면 Jetson이 무조건 저성능이다

- 아니다.
- `Balanced`는 Ubuntu 전원 UI일 수 있고, 실제 Jetson은 `25W` 모드일 수 있다.

### 오해 2. `Performance` 버튼이 안 보이면 성능을 못 올린다

- 아니다.
- Jetson은 `nvpmodel`과 `jetson_clocks`가 더 중요하다.

### 오해 3. RTAB-Map이 느리면 무조건 전력 모드 문제다

- 아니다.
- 실제 병목은 아래일 수도 있다.
  - `realsense2_camera` 해상도/FPS
  - `rtabmap_viz` GUI 부하
  - Docker 오버헤드
  - X11 렌더링
  - RGB-D 동기화

## 실무 추천

현재 Jetson에서 `RTAB-Map`을 보려는 상황이라면 아래 조합이 가장 실용적이다.

```bash
sudo nvpmodel -q --verbose
sudo jetson_clocks
sudo jetson_clocks --show
```

그 다음 아래를 다시 본다.

```bash
docker exec -it ros2-d435i bash -lc 'set +u; source /opt/ros/humble/setup.bash; set -u; ros2 topic hz /camera/camera/aligned_depth_to_color/image_raw'
```

그리고 실제 체감은 아래로 본다.

- `rtabmap_viz`가 버벅이는지
- 맵 누적이 끊기는지
- CPU/GPU 사용량이 과하게 치솟는지

## 한 줄 요약

`Balanced`를 `Performance`로 못 바꾸는 것보다, **현재 `25W`가 실제 Jetson 전력 모드인지 확인하고 `sudo jetson_clocks`를 적용하는 것이 RTAB-Map 성능 점검에 더 중요하다.**

## 참고 자료

- NVIDIA Jetson Linux Developer Guide  
  https://docs.nvidia.com/jetson/
- Jetson Orin Nano / Orin NX / AGX Orin Power and Performance  
  https://docs.nvidia.com/jetson/archives/r36.4.4/DeveloperGuide/SD/PlatformPowerAndPerformance/JetsonOrinNanoSeriesJetsonOrinNxSeriesAndJetsonAgxOrinSeries.html
