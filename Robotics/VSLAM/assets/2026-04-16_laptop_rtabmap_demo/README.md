# 2026-04-16 Laptop RTAB-Map Demo

## 결론

- 이 폴더는 **노트북에 D435i를 직접 연결해 `RTAB-Map`으로 생성한 발표용 3D 맵 DB**를 보관하는 폴더다.
- 목적은 `Jetson -> 노트북` 원격 GUI 경로가 학교 Wi-Fi에서 막혀도, **발표 자료용 3D 맵 결과물은 별도로 확보**하는 것이다.

## 파일 목록

### 01. RTAB-Map database

- 파일: [rtabmap_demo_map.db](./rtabmap_demo_map.db)
- 의미:
  - 노트북 로컬 환경에서 `D435i + RTAB-Map` 경로로 누적한 맵 데이터베이스
  - `rtabmap_viz`에서 보이던 3D 포인트클라우드와 키프레임 정보가 포함된 결과물
- 보관 정책:
  - 파일 크기가 커서 GitHub에는 올리지 않고 로컬 보관한다.
  - 저장 위치는 이 폴더를 유지하되, README와 캡처만 버전 관리한다.

## 생성 방법

노트북에서 아래 스크립트를 순서대로 실행해 맵을 생성했다.

```bash
cd /home/ssafy/my_ws/git_hub/Robotics/VSLAM
bash 06_Debugging/run_d435i_rgbd_mapping_camera.sh
bash 06_Debugging/run_d435i_rtabmap_light.sh
```

맵 저장:

```bash
mkdir -p /home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-16_laptop_rtabmap_demo
cp ~/.ros/rtabmap.db /home/ssafy/my_ws/git_hub/Robotics/VSLAM/assets/2026-04-16_laptop_rtabmap_demo/rtabmap_demo_map.db
```

## 정리 메모

- 이 증빙은 **노트북 직결 경로는 정상적으로 3D 맵을 만들 수 있다**는 점을 보여준다.
- 따라서 현재 학교 Wi-Fi에서 막힌 문제는 `RTAB-Map` 자체가 아니라 **cross-machine ROS 2 네트워크 계층**으로 보는 것이 맞다.
- 이후 발표용 이미지는 `rtabmap_viz` 오른쪽 `3D Map` 뷰를 중심으로 별도 캡처해 추가하면 된다.
