# 2026-04-18 Jetson 작업 일지

## 결론

- `Jetson` 로컬 그래픽 세션에서 `D435i` 카메라 노드와 `rtabmap_viz` GUI를 실제로 띄우는 데 성공했다.
- 전날 확인했던 `xcb` 오류는 `SSH/비GUI shell` 문제였고, `Jetson` 화면에서 직접 연 터미널에서는 `RTAB-Map GUI` 확인이 가능했다.
- 현재 기준선은 가이드 5 기본값인 `424x240x15 + DetectionRate 2 + IMU OFF`로 보는 편이 맞다.

## 오늘 작업 한 줄 요약

- `05_Jetson_Local_RTABMap_GUI_Check_Guide.md` 순서대로 `Jetson`에서 직접 `카메라 노드 + rtabmap_viz`를 확인했다.
- 왜 이 작업을 먼저 했는가?
  - `Jetson`에서 실제로 GUI가 뜨는지 확인돼야 이후 맵 누적, 체감 속도, 화면 증빙을 계속 쌓을 수 있기 때문이다.

## 현재 작업 형태

- `Jetson`에 `모니터 + 키보드 + 마우스`를 직접 연결한 상태에서 진행했다.
- 이번 작업은 `SSH`가 아니라 `Jetson` 바탕화면에서 직접 연 터미널이 필요했다.

## 시간순 기록

### 00:15

- `Jetson` 로컬 그래픽 세션에서 `rtabmap_viz` 창이 실제로 열린 상태를 확인했다.
- 스크린샷 기준으로 좌측에는 특징점이 표시된 입력 영상과 odometry 뷰가 보이고, 우측에는 `3D Map`과 trajectory가 정상적으로 그려졌다.
- 사용자 메모상 해상도는 `424x240x15`였을 가능성이 높고, 가이드 5 기본값 기준으로는 `DetectionRate 2`, `IMU OFF` 조합으로 기록하는 편이 자연스럽다.

## 오늘 관찰한 핵심 현상

- `rtabmap_viz`는 비GUI shell에서 실패했지만, `Jetson` 로컬 그래픽 세션에서는 정상적으로 표시됐다.
- 즉, 현재 병목은 "`RTAB-Map GUI가 안 되는가`"가 아니라 "`어떤 세션에서 실행했는가`"에 더 가깝다.
- GUI 기준으로도 `RTAB-Map`이 실제 맵과 trajectory를 그리고 있다는 증빙을 확보했다.

## 원인 가설

- 기존에는 `rtabmap_viz` 오류가 Jetson 성능이나 패키지 문제일 수도 있다고 봤다.
- 하지만 이번 결과로 보면 핵심 원인은 `DISPLAY/xcb`가 없는 비GUI shell에서 실행했던 점에 더 가깝다.

## 해결 방법

- `Jetson` 바탕화면에서 직접 연 터미널에서 가이드 5 순서대로 실행하는 방식을 기준 절차로 삼는다.
- `SSH`나 원격 IDE 터미널에서는 GUI 확인을 하지 않고, node/topic/log 확인용으로만 쓴다.

## 오늘 만든/수정한 파일

- [2026-04-18 Jetson 작업 일지](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/daily/2026-04-18/README.md)
- [Current_Progress_and_Open_Issues.md](/home/jetson/yh_ws/TIL/Robotics/VSLAM/docs/progress/Current_Progress_and_Open_Issues.md)

## 증빙 자료

- [Jetson RTAB-Map GUI screenshot](/home/jetson/yh_ws/TIL/Robotics/VSLAM/jetson/assets/screenshots/2026-04-18_jetson_rtabmap_viz_gui_baseline_424x240x15_detectionrate2_imuoff.png)

## 남은 문제

- `D435i` 내장 IMU는 여전히 `HID Motion Sensor Failure`로 살아나지 않아 별도 진단이 필요하다.
- 이번 캡처는 GUI 성공 증빙이므로, 다음에는 `quality`, `delay`, `체감 부드러움`까지 같이 남겨야 한다.
- `424x240x15` 설정은 사용자 메모 기준으로는 유력하지만, 다음 기록에서는 실행 직후 설정값을 같이 캡처하거나 로그로 남기는 편이 더 정확하다.

## 다음 액션

1. `Jetson` 로컬 그래픽 세션에서 가이드 5 기준으로 `quality`와 `delay`를 같이 기록한다.
2. 같은 조건에서 짧은 실내 경로를 움직이며 trajectory와 맵 누적 상태를 비교한다.
3. `IMU OFF` 기준 baseline을 먼저 고정한 뒤, `D435i IMU HID` 진단을 따로 이어간다.

## 한 줄 회고

- `Jetson`에서 `rtabmap_viz` GUI가 실제로 떴다는 증빙을 확보하면서, 이제 GUI 실행 여부가 아니라 baseline 품질 비교로 넘어갈 수 있게 됐다.
