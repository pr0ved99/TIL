# D435i와 Jetson Docker 선수지식

## 결론

지금까지 진행한 작업 기준으로, 먼저 알고 있으면 좋은 선수지식은 크게 두 묶음이다.

1. `D435i + ROS2`를 다루기 위한 선수지식
2. `Jetson + Docker`를 다루기 위한 선수지식

초보자 기준으로는 아래 순서로 이해하는 것이 가장 실용적이다.

1. 센서가 어떤 데이터를 내보내는지 이해
2. ROS2에서 토픽과 노드가 어떻게 연결되는지 이해
3. Jetson이 일반 PC와 왜 다른지 이해
4. Docker가 왜 필요한지 이해
5. 실제 명령어와 검증 포인트를 연결해서 이해

---

## 1. 왜 이 선수지식이 필요한가

직관:
지금 프로젝트는 "카메라만 켜기"나 "Docker만 설치하기" 수준이 아니다.  
나중에는 `D435i`, `Jetson`, `ROS2`, `Docker`, `Nav2`, `VSLAM`이 서로 연결된다.  
그래서 각 부품이 무슨 역할을 하는지 모르면 디버깅할 때 어디를 봐야 할지 금방 헷갈린다.

핵심:

- `D435i`는 단순 웹캠이 아니라 `RGB + Depth + IMU` 센서다.
- `ROS2`는 데이터를 `토픽(topic)` 으로 주고받는다.
- `Jetson`은 `arm64` 기반이라 일반 PC와 Docker 이미지 호환성이 다르다.
- `Docker`는 개발환경을 고정해주는 도구지만, Jetson에서는 `GPU runtime`과 장치 접근까지 같이 생각해야 한다.

---

## 2. D435i를 다루기 위한 선수지식

### 2-1. D435i가 무엇인지

- `RGB 카메라`: 일반 컬러 영상
- `Depth 카메라`: 픽셀마다 거리값을 주는 카메라
- `IMU`: 가속도계와 자이로 센서

중요:
지금 프로젝트에서는 D435i를 `전역 위치추정`보다는 `근거리 장애물 확인`, `쓰레기 탐지`, `마지막 정밀 접근` 쪽에 더 유용하게 쓸 가능성이 크다.

### 2-2. ROS2 기본 개념

- `노드(Node)`: 데이터를 보내거나 받는 실행 단위다.
- `토픽(Topic)`: 노드끼리 데이터를 주고받는 채널이다.
- `launch`: 여러 노드를 한 번에 실행하는 방식이다.

지금 D435i를 띄울 때 쓴 명령:

```bash
ros2 launch realsense2_camera rs_launch.py enable_color:=true enable_depth:=true
```

이 명령이 하는 일:

- RealSense ROS 드라이버 노드를 실행한다
- color 스트림과 depth 스트림을 켠다

### 2-3. 꼭 알아야 하는 D435i 토픽

지금 확인했던 핵심 토픽:

```text
/camera/camera/color/image_raw
/camera/camera/depth/image_rect_raw
/camera/camera/color/camera_info
/camera/camera/depth/camera_info
```

의미:

- `image_raw`: 실제 영상 데이터
- `camera_info`: 카메라 내부 파라미터 정보

중요:
나중에 `VSLAM`, `3D 위치 계산`, `point cloud`, `장애물 회피`를 하려면 `camera_info`도 같이 중요하다.

### 2-4. depth 영상이 왜 흑백처럼 보이는가

- `raw depth`는 색깔 영상이 아니라 `거리값` 영상이다.
- 그래서 `rqt_image_view`에서 보면 회색조처럼 보이는 것이 정상이다.
- 사람이 보기 쉽게 하려면 컬러맵(colormap)을 씌운 시각화용 토픽을 따로 만들면 된다.

현재 추가한 시각화용 스크립트:

- [depth_colormap_publisher.py](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/06_Debugging/depth_colormap_publisher.py)

### 2-5. USB 3.x가 왜 중요한가

- `USB 2.x`로 연결되면 대역폭이 부족할 수 있다.
- 그러면 프레임 저하, 해상도 제한, depth 성능 저하가 생길 수 있다.

지금까지 관찰한 점:

- 초기에 `USB type 2.1`이 한 번 보였다
- 이후 저장된 증빙 기준으로는 `USB type 3.2`가 확인됐다

즉, 포트와 케이블 상태를 계속 점검해야 한다.

### 2-6. D435i에서 최소한 알아야 하는 디버깅 포인트

1. 카메라가 실제로 인식됐는가
2. `ros2 topic list`에 depth 토픽이 보이는가
3. `rqt_image_view`에서 depth가 실제로 나오는가
4. USB 타입이 3.x로 잡히는가
5. 토픽 이름과 `frame_id`가 예상과 맞는가

---

## 3. Jetson에서 Docker를 쓰기 위한 선수지식

### 3-1. Jetson이 일반 PC와 다른 이유

- Jetson은 보통 `arm64(aarch64)` 아키텍처를 쓴다.
- 일반 데스크탑은 보통 `x86_64`다.

즉:

- x86용 Docker 이미지는 Jetson에서 바로 안 될 수 있다.
- Jetson에서는 `arm64 호환 이미지`, `JetPack/L4T 호환성`, `NVIDIA runtime`을 같이 봐야 한다.

### 3-2. 꼭 알아야 하는 용어

- `JetPack`: Jetson용 소프트웨어 묶음이다.
- `L4T`: Jetson 저수준 Linux 플랫폼 버전이다.
- `Docker Image`: 컨테이너 실행용 파일 묶음이다.
- `Container`: 이미지를 실제로 실행한 상태다.
- `Bind Mount`: 호스트 폴더를 컨테이너와 연결하는 방식이다.
- `NVIDIA runtime`: 컨테이너 안에서 GPU 관련 라이브러리와 장치를 쓸 수 있게 해주는 설정이다.

### 3-3. Docker를 왜 쓰는가

직관:
개발할 때 ROS2, OpenCV, CUDA, TensorRT, Python 버전이 조금만 달라도 환경이 쉽게 깨진다.  
Docker는 이 개발환경을 "컨테이너" 안에 고정해주는 도구다.

실무 장점:

- 팀원마다 환경 차이를 줄일 수 있다
- Jetson 재설치 후에도 환경을 복구하기 쉽다
- 나중에 ROS2/VSLAM 실행 환경을 재현하기 쉽다

### 3-4. Jetson Docker에서 최소로 알아야 하는 것

1. Jetson 보드 정보 확인

```bash
uname -m
cat /etc/nv_tegra_release
```

2. Docker 존재 여부 확인

```bash
docker --version
docker compose version
systemctl status docker --no-pager
```

3. 기본 컨테이너 실행 확인

```bash
docker run hello-world
```

4. 사용자 권한 확인

```bash
groups
```

여기서 `docker` 그룹이 없으면 매번 `sudo docker ...`를 써야 할 수 있다.

### 3-5. Jetson Docker에서 자주 헷갈리는 포인트

- `Docker가 설치됨` 과 `Jetson GPU를 쓸 수 있음` 은 다르다
- `컨테이너가 뜸` 과 `카메라/USB 장치를 쓸 수 있음` 도 다르다
- `일반 Ubuntu 이미지` 와 `Jetson에 맞는 이미지` 는 다를 수 있다

즉, 나중에는 아래를 따로 검증해야 한다.

1. Docker가 뜨는가
2. Jetson용 이미지가 맞는가
3. GPU runtime이 보이는가
4. 컨테이너 안에서 카메라/USB 장치를 읽을 수 있는가

---

## 4. D435i와 Jetson Docker가 만나는 지점

이 둘은 나중에 따로 쓰지 않고 연결된다.

예상 연결 구조:

```text
D435i -> ROS2 topic publish
Jetson -> ROS2 노드 실행
Docker -> ROS2/VSLAM/탐지 환경 고정
```

그래서 나중에는 아래를 같이 이해해야 한다.

- 컨테이너 안에서도 ROS2가 떠야 한다
- 컨테이너 안에서도 D435i 장치 접근이 되어야 한다
- 컨테이너 밖/안의 토픽 확인 방법이 같아야 한다

---

## 5. 지금 단계에서 꼭 알고 있으면 좋은 최소 선수지식

아래만 알아도 지금 스프린트 진행에는 충분하다.

### D435i 쪽

- `realsense2_camera`가 D435i를 ROS2 토픽으로 바꿔준다
- depth 핵심 토픽은 `/camera/camera/depth/image_rect_raw`다
- `rqt_image_view`로 depth 시각화가 가능하다
- raw depth는 회색조처럼 보이는 것이 정상이다
- USB 3.x 여부는 성능에 중요하다

### Jetson Docker 쪽

- Jetson은 `arm64`라서 이미지 호환성을 봐야 한다
- Docker는 개발환경 고정용이다
- `docker --version`, `docker run hello-world`가 1차 확인이다
- Jetson에서는 나중에 `GPU runtime`도 따로 확인해야 한다

---

## 6. 다음 단계로 넘어가기 전 체크리스트

### D435i

- [x] D435i 장치 인식
- [x] depth 토픽 확인
- [x] depth 시각화 확인
- [x] 검증 캡처 정리

### Jetson Docker

- [ ] Jetson 실물 확보
- [ ] JetPack/L4T 버전 확인
- [ ] Docker 설치 여부 확인
- [ ] Docker daemon 상태 확인
- [ ] `hello-world` 실행 확인

---

## 7. 같이 보면 좋은 기존 문서

- [D435i_VSLAM_A_to_Z_Plan.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/docs/progress/D435i_VSLAM_A_to_Z_Plan.md)
- [assets/2026-04-09_task59_d435i_depth_check/README.md](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-09_task59_d435i_depth_check/README.md)
- [01_Jetson_Orin_Nano_Docker_A_to_Z.md](/home/ssafy/my_ws/git_hub/Embedded/Jetson/Theory/01_Jetson_Orin_Nano_Docker_A_to_Z.md)
