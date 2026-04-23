# 2026-04-16 작업 일지

## 결론

- 노트북 부팅 때 반복되던 `Files(nautilus)` 크래시 팝업은 `ding@rastersoft.com` 확장 비활성화 후 재부팅했을 때 재발하지 않아, 원인을 `DING` 확장으로 판단했다.
- Jetson Docker 환경에서 `x11-apps`, `RTAB-Map`, `realsense2_camera`가 포함된 이미지를 만들고, `X11`, `RTAB-Map`, 원격 실행용 스크립트까지 정리했다.
- Jetson 컨테이너 내부에서는 `D435i` color/depth 토픽이 정상이고, depth 주기도 약 `30 Hz`로 안정적이었다.
- 하지만 **노트북에서 Jetson 토픽을 받아 RTAB-Map GUI를 띄우는 cross-machine ROS 2 경로는 현재 학교 Wi-Fi에서 DDS discovery가 막혀 실패했다.**
- 대신 **노트북에 D435i를 직접 연결한 RTAB-Map 경로에서는 발표용 3D 맵 생성과 `rtabmap.db` 저장까지 완료했다.**
- 다음 작업의 1순위는 **Jetson과 노트북을 아이폰 핫스팟 같은 다른 네트워크로 옮겨서 `ping -> SSH -> ROS 2 토픽 발견 -> 노트북 RTAB-Map GUI`를 다시 확인하는 것**이다.

## 오늘 작업 한 줄 요약

- 노트북 `nautilus` 팝업 원인을 분리해서 해결했고, Jetson Docker에서 `X11 -> RTAB-Map -> 노트북 원격 RTAB-Map` 경로를 단계별로 정리했다.
- 동시에 노트북 직결 `D435i + RTAB-Map` 경로로 발표용 3D 맵 데모를 한 번 확보했다.
- 왜 이 작업을 먼저 했는가?
  - 어제까지는 Jetson 컨테이너 내부 카메라 토픽 확인까지만 끝났고, 오늘은 `GUI`, `RTAB-Map`, `장비 간 ROS 2 통신`처럼 실제 사용 단계에서 막히는 부분을 분리해야 했기 때문이다.

## 시간순 기록

### 09:00

- 노트북 부팅 시 뜨던 `The application Files has closed unexpectedly` 팝업 원인을 먼저 확인했다.
- 이전에 남은 `nautilus` crash 파일을 삭제하고, `nautilus`를 재설치한 뒤 `DING` 확장 유무를 확인했다.
- `ding@rastersoft.com` 확장이 켜져 있는 것을 확인했고, 이 확장이 `nautilus`와 충돌할 가능성이 높다고 판단했다.

```bash
sudo rm -f /var/crash/_usr_bin_nautilus.1000.crash
sudo apt update
sudo apt install --reinstall nautilus
gnome-extensions list | grep -i ding
```

### 09:20

- `DING` 확장을 끄고 재부팅했다.
- 재부팅 후 `DING`이 더 이상 enabled 상태가 아니었고, `/var/crash`에 `nautilus` crash 파일도 다시 생기지 않았다.
- 따라서 반복 팝업 문제는 현재 해결된 것으로 판단했다.

```bash
gnome-extensions disable ding@rastersoft.com
reboot
gnome-extensions list --enabled | grep -i ding
ls -lah /var/crash | grep nautilus
```

### 10:30

- Jetson Docker에서 `X11`과 `RTAB-Map`을 같이 보기 위한 자산을 추가했다.
- `Dockerfile`에 `x11-apps`, `mesa-utils`, `ros-humble-rtabmap*` 패키지를 넣고, `X11 허용`, `X11 테스트`, `컨테이너 내부 RTAB-Map 실행` 스크립트를 만들었다.
- 이 단계의 목표는 `Jetson에서 GUI를 띄우는 경로`가 가능한지 확인하는 것이었다.

### 11:10

- Jetson SSH 세션에서 `enable_x11_for_docker.sh`를 실행했더니 `xhost: unable to open display :0`가 나왔다.
- 여기서 `X11`은 **Jetson 로컬 화면** 기준이고, 단순 SSH 텍스트 세션에서는 `DISPLAY`와 `XAUTHORITY` 권한이 맞지 않는다는 점을 확인했다.
- 이 결과를 바탕으로 `Jetson에서 꼭 GUI를 띄우지 않아도 된다`는 방향으로 설계를 바꿨다.

```bash
cd ~/VSLAM
bash Tools/enable_x11_for_docker.sh
bash Tools/test_x11_in_container.sh
```

### 11:40

- Jetson Docker 내부 `RTAB-Map` 실행은 유지하되, GUI는 노트북에서 띄우는 구조로 방향을 바꿨다.
- 즉, **Jetson은 D435i 카메라 토픽만 publish**하고, **노트북은 그 토픽을 받아 RTAB-Map GUI를 실행**하는 구조를 선택했다.
- 이 구조가 더 실용적인 이유는 Jetson X11을 억지로 붙들 필요가 없고, 노트북 화면에서 시각화가 더 편하기 때문이다.

### 12:10

- 노트북에서 Jetson 토픽을 확인하고 RTAB-Map을 실행하는 스크립트를 추가했다.
- `check_remote_jetson_camera_topics.sh`는 노트북에서 `/camera/camera/*` 토픽이 보이는지 확인하는 용도다.
- `launch_rtabmap_remote_from_laptop.sh`는 노트북에서 Jetson 카메라 토픽을 구독해 `rtabmap_viz`를 띄우는 용도다.
- `Jetson_Docker_Camera_to_Laptop_RTABMap_Guide.md`도 같이 정리했다.

### 13:00

- Jetson 쪽 `run_ros2_d435i_container.sh`가 `/workspace/VSLAM`를 마운트하고, `DISPLAY`, `ROS_DOMAIN_ID`, `ROS_LOCALHOST_ONLY`, `RMW_IMPLEMENTATION`, `ROS_DISCOVERY_SERVER`, `ROS_SUPER_CLIENT`를 컨테이너에 넘기도록 수정했다.
- 그 결과 Jetson 컨테이너 안에서 최신 스크립트와 환경변수가 제대로 보이는지 확인했다.

```bash
docker exec -it ros2-d435i bash -lc "ls /workspace && ls /workspace/VSLAM && ls /workspace/VSLAM/Tools"
docker exec -it ros2-d435i bash -lc "env | grep -E 'ROS_DOMAIN_ID|ROS_LOCALHOST_ONLY|RMW_IMPLEMENTATION|ROS_DISCOVERY_SERVER|ROS_SUPER_CLIENT'"
```

### 13:30

- Jetson 컨테이너 안에서 `realsense2_camera`를 다시 실행하고, 카메라 노드와 토픽이 정상인지 확인했다.
- `aligned_depth_to_color` 토픽까지 확인했고, 노드는 `/camera/camera`로 정상 동작했다.

```bash
export ROS_DOMAIN_ID=14
export ROS_LOCALHOST_ONLY=0
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_DISCOVERY_SERVER=192.168.100.62:11811
export ROS_SUPER_CLIENT=TRUE

cd ~/VSLAM
bash Tools/run_ros2_d435i_container.sh
bash Tools/launch_realsense_rgbd.sh

docker exec -it ros2-d435i bash -lc "source /opt/ros/humble/setup.bash && ros2 daemon stop || true && ros2 daemon start && sleep 2 && echo '==== nodes ====' && ros2 node list && echo '==== topics ====' && ros2 topic list | grep '^/camera/camera'"
```

### 14:00

- depth 주기를 다시 측정했다.
- `/camera/camera/depth/image_rect_raw`는 약 `29.98 ~ 30.00 Hz`로 매우 안정적이었다.
- 즉, 카메라 경로 자체는 `RTAB-Map` 입력으로 쓰기에 충분한 수준이라고 판단했다.

```bash
docker exec -it ros2-d435i bash -lc "source /opt/ros/humble/setup.bash && ros2 topic hz /camera/camera/depth/image_rect_raw"
```

### 14:30

- 노트북에서 Jetson 토픽을 보려고 했지만, 처음에는 `AMENT_TRACE_SETUP_FILES: unbound variable` 오류가 났다.
- 원인은 스크립트의 `set -u`와 ROS 2 `setup.bash`의 내부 변수가 충돌했기 때문이었다.
- 노트북용 스크립트에서 `setup.bash`를 읽을 때만 `set +u`로 바꿔 해결했다.

### 15:00

- 노트북과 Jetson 사이의 `ROS_DOMAIN_ID` 불일치를 의심해 양쪽을 `14`로 맞췄다.
- 하지만 노트북에서는 여전히 Jetson 카메라 토픽이 보이지 않았다.
- 이 시점부터는 `카메라 문제`가 아니라 `cross-machine ROS 2 discovery` 문제로 판단을 좁혔다.

### 15:30

- `ros2 multicast receive/send` 테스트를 통해 현재 Wi-Fi에서 멀티캐스트 기반 discovery가 실패한다는 점을 확인했다.
- 따라서 현재 학교 Wi-Fi는 ROS 2 장비 간 자동 발견에 적합하지 않다고 판단했다.
- 우회책으로 `Fast DDS Discovery Server` 경로를 준비했다.

### 16:00

- 노트북에서 `Fast DDS Discovery Server`를 띄우고, Jetson 컨테이너와 노트북 양쪽에 `ROS_DISCOVERY_SERVER`와 `ROS_SUPER_CLIENT`를 넣어 다시 시도했다.
- 이때 Jetson 컨테이너 쪽 환경변수와 카메라 노드는 정상적으로 보였다.
- 하지만 노트북에서는 여전히 `/camera/camera/*` 토픽을 보지 못했다.
- 따라서 문제는 현재 네트워크에서의 DDS 전달/발견 자체라고 결론 내렸다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
bash Tools/start_fastdds_discovery_server.sh

export ROS_DOMAIN_ID=14
export ROS_LOCALHOST_ONLY=0
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_DISCOVERY_SERVER=192.168.100.62:11811
export ROS_SUPER_CLIENT=TRUE

bash Tools/check_remote_jetson_camera_topics.sh
```

### 16:40

- 네트워크 자체를 바꿔보는 방향으로 전환했다.
- 아이폰 핫스팟을 Jetson에서 스캔했을 때 `pr0ved’s iPhone` SSID가 정상적으로 보이는 것까지 확인했다.
- 즉, 다음 실험은 **Jetson과 노트북을 둘 다 아이폰 핫스팟에 붙여서 `ping -> SSH -> ROS 2 토픽 발견 -> 노트북 RTAB-Map`을 다시 보는 것**으로 정리했다.

```bash
sudo nmcli device wifi rescan
nmcli device wifi list
```

### 17:20

- 학교 Wi-Fi 기반 cross-machine 경로가 바로 풀리지 않았기 때문에, 발표 자료용 3D 맵은 우선 **노트북 직결 D435i + RTAB-Map** 경로로 확보하기로 했다.
- 노트북에서 아래 두 스크립트를 순서대로 실행해 `RGB-D 카메라 노드 -> RTAB-Map GUI` 경로를 올렸다.
- 이 경로는 Jetson 네트워크 상태와 무관하게 로컬에서 바로 맵을 쌓을 수 있다는 장점이 있었다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
bash 06_Debugging/run_d435i_rgbd_mapping_camera.sh
bash 06_Debugging/run_d435i_rtabmap_light.sh
```

### 17:45

- `rtabmap_viz`에서 실제 포인트클라우드 기반 3D 맵이 누적되는 것을 확인했다.
- 발표 슬라이드용으로는 `3D Map` 오른쪽 뷰를 중심으로 캡처하고, 분석용으로는 `rtabmap.db`를 따로 저장하는 방식이 가장 실용적이라고 정리했다.
- 최종적으로 노트북 로컬 맵 DB를 아래 경로에 저장했다.

```bash
mkdir -p /home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-16_laptop_rtabmap_demo
cp ~/.ros/rtabmap.db /home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-16_laptop_rtabmap_demo/rtabmap_demo_map.db
```

## 오늘 관찰한 핵심 현상

- 노트북 부팅 팝업 문제는 `DING` 확장을 끄자 재발하지 않았다.
- Jetson SSH 텍스트 세션에서 `X11`을 직접 붙이는 방식은 `DISPLAY` 권한 문제로 바로 막혔다.
- Jetson 컨테이너 안 `realsense2_camera`는 안정적으로 올라오고, `aligned_depth_to_color` 토픽까지 정상 생성된다.
- `depth/image_rect_raw` 주기는 약 `30 Hz`로 매우 안정적이었다.
- 노트북에서 Jetson 토픽이 안 보이는 문제는 `ROS_DOMAIN_ID`, `ROS_DISCOVERY_SERVER`, `ROS_SUPER_CLIENT`까지 맞춰도 현재 Wi-Fi에서는 해결되지 않았다.
- `ros2 multicast`가 안 되었고, Discovery Server까지 써도 노트북에서 토픽 발견이 실패했으므로, 현재 병목은 **카메라가 아니라 네트워크 계층**이다.
- 아이폰 핫스팟은 Jetson에서 스캔 가능했다.
- 반면 **노트북 직결 D435i + RTAB-Map 경로는 즉시 3D 맵 생성이 가능했고, 발표용 데모 확보에는 이 경로가 가장 빠르다.**

## 원인 가설

- 처음에는 `nautilus` 패키지 자체 문제라고 생각했지만, 실제로는 `DING` 확장이 로그인 시점에 충돌을 일으킨 가능성이 높았다.
- 처음에는 Jetson X11 설정 문제라고 생각했지만, 실제로는 `SSH 텍스트 세션에서 로컬 GUI를 직접 제어하려는 접근`이 잘못된 가정이었다.
- 처음에는 `ROS_DOMAIN_ID` 불일치가 핵심 원인이라고 봤지만, 그 값을 맞춘 뒤에도 실패했으므로 원인이 더 아래 계층에 있다고 판단했다.
- 현재 가장 강한 가설은 **학교 Wi-Fi에서 DDS 멀티캐스트 또는 장비 간 discovery/전달이 막히고 있다는 것**이다.

## 확인 방법

- `gnome-extensions list --enabled | grep -i ding`, `ls -lah /var/crash | grep nautilus`로 노트북 팝업 원인을 확인했다.
- Jetson에서는 `docker exec ... ros2 node list`, `ros2 topic list`로 컨테이너 내부 카메라 노드와 토픽을 확인했다.
- `ros2 topic hz /camera/camera/depth/image_rect_raw`로 실제 주기를 수치로 확인했다.
- `ros2 multicast receive/send`로 멀티캐스트 discovery 가능 여부를 분리했다.
- `Fast DDS Discovery Server`를 띄워 discovery server 우회 경로도 테스트했다.
- `nmcli device wifi rescan`, `nmcli device wifi list`로 아이폰 핫스팟 노출 여부를 확인했다.

## 해결 방법

- 노트북 팝업 문제는 `DING` 비활성화로 해결했다.
- Jetson Docker 쪽은 `X11`, `RTAB-Map`, `원격 RTAB-Map`, `Discovery Server` 관련 스크립트를 추가해 이후 재현성을 높였다.
- `run_ros2_d435i_container.sh`를 수정해 `ROS_DOMAIN_ID`, `ROS_LOCALHOST_ONLY`, `RMW_IMPLEMENTATION`, `ROS_DISCOVERY_SERVER`, `ROS_SUPER_CLIENT`를 컨테이너에 넘기도록 했다.
- 노트북용 원격 실행 스크립트는 `set -u`와 `setup.bash` 충돌을 피하도록 수정했다.
- 다만 cross-machine ROS 2는 아직 해결된 것이 아니라, **현재 네트워크에서는 실패 원인을 분리한 상태**다.
- 발표용 결과물 확보는 **노트북 직결 RTAB-Map** 경로로 우선 해결했고, `rtabmap_demo_map.db`를 따로 저장했다.

## 오늘 배운 것

- `X11`은 GUI 창을 띄우는 용도이지, 카메라 노드나 RTAB-Map 실행 자체에 항상 필수는 아니다.
- `Jetson은 센서 publish`, `노트북은 GUI/시각화` 구조가 현재 프로젝트에 더 실용적이다.
- `ROS_DOMAIN_ID`를 맞추는 것만으로는 부족하고, 실제 네트워크가 DDS discovery를 허용하는지도 봐야 한다.
- `ros2 multicast`가 실패하면, 카메라나 launch 파일보다 먼저 네트워크를 의심하는 게 맞다.
- 아이폰 핫스팟처럼 다른 네트워크로 바꾸는 테스트는 cross-machine ROS 2 문제를 분리하는 데 유효하다.

## 오늘 만든/수정한 파일

- `Tools/check_remote_jetson_camera_topics.sh`
- `Tools/launch_rtabmap_remote_from_laptop.sh`
- `Tools/start_fastdds_discovery_server.sh`
- `Tools/run_ros2_d435i_container.sh`
- `Tools/enable_x11_for_docker.sh`
- `Tools/test_x11_in_container.sh`
- `Tools/launch_rtabmap_light_in_container.sh`
- `Tools/launch_realsense_rgbd.sh`
- `docker/jetson_ros2_d435i/Dockerfile`
- `docs/learning/Jetson_Docker_Camera_to_Laptop_RTABMap_Guide.md`

## 증빙 자료

- 오늘 새로 확보한 정리 대상은 아래 두 종류다.
  - Jetson 네트워크/원격 RTAB-Map 실패 원인 분리 화면
  - 노트북 직결 RTAB-Map 3D 맵 생성 결과와 DB 파일
- 현재 노트북 직결 맵 DB는 아래 경로에 저장해 두었다.

```text
/home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-16_laptop_rtabmap_demo/rtabmap_demo_map.db
```

- 아래 화면은 오늘 작업을 설명하는 데 가치가 있다.
  - `DING` 비활성화 후 `gnome-extensions list --enabled | grep -i ding`와 `ls -lah /var/crash | grep nautilus` 결과
  - Jetson 컨테이너 안에서 `env | grep ...` 결과
  - Jetson 컨테이너 안에서 `/camera/camera*` 토픽 목록
  - 노트북에서 `check_remote_jetson_camera_topics.sh` 실패 화면
  - Jetson에서 `nmcli device wifi list`로 `pr0ved’s iPhone`가 보이는 화면
  - 노트북에서 `rtabmap_viz`로 생성한 발표용 3D 맵 화면

## 추천 스크린샷

### 1. `01_nautilus_popup_fix_check.png`

- 추천 화면:
  - `gnome-extensions list --enabled | grep -i ding`
  - `ls -lah /var/crash | grep nautilus`
- 의미:
  - 노트북 부팅 팝업 문제 원인 분리와 해결 결과를 보여준다.

### 2. `02_jetson_container_env_and_camera_topics.png`

- 추천 화면:
  - `docker exec -it ros2-d435i bash -lc "env | grep -E 'ROS_DOMAIN_ID|ROS_LOCALHOST_ONLY|RMW_IMPLEMENTATION|ROS_DISCOVERY_SERVER|ROS_SUPER_CLIENT'"`
  - `docker exec -it ros2-d435i bash -lc "source /opt/ros/humble/setup.bash && ros2 node list && ros2 topic list | grep '^/camera/camera'"`
- 의미:
  - Jetson 컨테이너 내부 카메라 publish 경로가 정상이라는 점을 증명한다.

### 3. `03_depth_30hz_check.png`

- 추천 화면:
  - `docker exec -it ros2-d435i bash -lc "source /opt/ros/humble/setup.bash && ros2 topic hz /camera/camera/depth/image_rect_raw"`
- 의미:
  - RTAB-Map 입력으로 쓰는 depth 경로가 약 `30 Hz`로 안정적임을 보여준다.

### 4. `04_remote_topic_discovery_failure_on_school_wifi.png`

- 추천 화면:
  - 노트북에서 `bash Tools/check_remote_jetson_camera_topics.sh`
  - 가능하면 노트북에서 `ros2 multicast receive` 대기 후, 아무 것도 안 보이는 상황
- 의미:
  - 현재 학교 Wi-Fi에서 cross-machine ROS 2 discovery가 실패한다는 점을 보여준다.

### 5. `05_iphone_hotspot_visible_on_jetson.png`

- 추천 화면:
  - `sudo nmcli device wifi rescan`
  - `nmcli device wifi list`
  - 여기서 `pr0ved’s iPhone`가 보이는 상태
- 의미:
  - 다음 실험용 대체 네트워크 후보가 실제로 준비됐음을 보여준다.

### 6. `06_laptop_rtabmap_demo_map.png`

- 추천 화면:
  - 노트북에서 `rtabmap_viz` 오른쪽 `3D Map` 뷰만 크게 보이도록 정리한 화면
- 의미:
  - Jetson 원격 경로와 별개로, 발표용 3D 맵은 노트북 직결 경로에서 이미 확보했다는 점을 보여준다.

## 남은 문제

- 노트북에서 Jetson 카메라 토픽을 바로 받아 RTAB-Map GUI를 띄우는 cross-machine ROS 2 경로는 아직 성공하지 못했다.
- 현재 학교 Wi-Fi에서 DDS discovery 또는 장비 간 전달이 막히는 것으로 보인다.
- Jetson에서 `D435i IMU(HID)` 경고는 여전히 남아 있어, IMU 기반 RTAB-Map 경로는 아직 보류 상태다.
- 발표 자료용 3D 맵은 확보했지만, 이 결과를 Jetson publish -> 노트북 GUI 구조로 재현하는 검증은 아직 남아 있다.

## 다음 액션

1. Jetson과 노트북을 둘 다 아이폰 핫스팟에 연결한다.
2. `ping -> SSH -> bash Tools/check_remote_jetson_camera_topics.sh -> bash Tools/launch_rtabmap_remote_from_laptop.sh` 순서로 다시 검증한다.
3. 핫스팟에서도 실패하면, ROS 2 talker/listener 최소 예제로 cross-machine 통신을 분리 테스트한다.
4. 발표 자료에는 노트북 직결 RTAB-Map 경로에서 확보한 3D 맵 화면과 DB를 우선 사용한다.

## 한 줄 회고

- 오늘 작업을 한 문장으로 요약하면, **Jetson 내부는 정상화했지만 cross-machine ROS 2는 현재 Wi-Fi에서 막혀 있고, 다음 실험은 아이폰 핫스팟으로 네트워크를 바꿔 재검증하는 단계까지 정리한 날**이었다.
