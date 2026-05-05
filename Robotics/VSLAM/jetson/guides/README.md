# Jetson Guides

## 결론

- 이 폴더는 `Jetson`에서 직접 따라 입력할 수 있게 만든 `진행 방법 파일` 모음이다.
- 계획 문서가 "무엇을 할지"를 설명한다면, 여기 문서는 **"지금 무엇을 어떤 순서로 입력할지"**를 바로 보여준다.

## 원칙

- 각 가이드는 복붙 가능한 명령만 위에서 아래 순서대로 배치한다.
- GUI가 필요한 경우 `터미널 1`, `터미널 2`처럼 나눠서 적는다.
- 한 가이드는 한 목적만 가진다.
- 새로운 단계가 시작되면 그 단계용 가이드를 먼저 만든다.

## 현재 가이드

- [`00_Jetson_Session_Start_Guide.md`](./00_Jetson_Session_Start_Guide.md): 작업 시작 전에 기본 세션 정리
- [`01_Jetson_System_Inventory_Guide.md`](./01_Jetson_System_Inventory_Guide.md): 시스템 기준선 확인
- [`02_Jetson_D435i_Native_Bringup_Guide.md`](./02_Jetson_D435i_Native_Bringup_Guide.md): `D435i` native bring-up
- [`03_Jetson_RTABMap_Baseline_Guide.md`](./03_Jetson_RTABMap_Baseline_Guide.md): `RTAB-Map` baseline 실행
- [`04_Jetson_D435i_IMU_Diagnosis_Guide.md`](./04_Jetson_D435i_IMU_Diagnosis_Guide.md): `D435i IMU HID` 이슈 진단
- [`05_Jetson_Local_RTABMap_GUI_Check_Guide.md`](./05_Jetson_Local_RTABMap_GUI_Check_Guide.md): Jetson 화면에서 `카메라 노드 + rtabmap_viz` 직접 확인
- [`06_Jetson_Baseline_Benchmark_Guide.md`](./06_Jetson_Baseline_Benchmark_Guide.md): baseline의 `quality / delay / tegrastats / screenshot` 기록
- [`07_Jetson_DetectionRate_Comparison_Guide.md`](./07_Jetson_DetectionRate_Comparison_Guide.md): `DetectionRate 2 vs 3` 후보 비교
- [`08_Jetson_Docker_Enablement_Guide.md`](./08_Jetson_Docker_Enablement_Guide.md): 이미 설치된 Docker를 `jetson` 사용자 기준으로 실제 사용 가능 상태로 전환
- [`09_Jetson_VSLAM_Docker_Bringup_Guide.md`](./09_Jetson_VSLAM_Docker_Bringup_Guide.md): Jetson용 `VSLAM` 개발 컨테이너 빌드 및 진입
- [`10_Jetson_Korean_Input_Guide.md`](./10_Jetson_Korean_Input_Guide.md): Jetson에 한국어 입력기 설정
- [`11_Jetson_BNO08x_First_Value_Check_Guide.md`](./11_Jetson_BNO08x_First_Value_Check_Guide.md): 외부 `GY-BNO08x` IMU 값 1차 확인
- [`12_Jetson_BNO08x_Docker_Check_Guide.md`](./12_Jetson_BNO08x_Docker_Check_Guide.md): `BNO08x` 값을 Docker 컨테이너 안에서 재확인
- [`13_Jetson_BNO08x_Live_Plot_Guide.md`](./13_Jetson_BNO08x_Live_Plot_Guide.md): host `venv`에서 `BNO08x` 값을 실시간 그래프로 확인
- [`14_Jetson_BNO08x_Aircraft_Viewer_Guide.md`](./14_Jetson_BNO08x_Aircraft_Viewer_Guide.md): 비행기 모양 3D 모델로 `BNO08x` 자세를 직관적으로 확인
- [`15_Jetson_D435i_IMU_Aircraft_Viewer_Guide.md`](./15_Jetson_D435i_IMU_Aircraft_Viewer_Guide.md): `D435i` IMU topic을 비행기 viewer로 확인하기 위한 준비 가이드
- [`16_Jetson_BNO08x_ROS2_IMU_Publisher_Guide.md`](./16_Jetson_BNO08x_ROS2_IMU_Publisher_Guide.md): `BNO08x`를 `/imu/data`로 publish하고 ROS 2 viewer와 연결
- [`17_Jetson_BNO08x_Temporary_Mount_and_TF_Guide.md`](./17_Jetson_BNO08x_Temporary_Mount_and_TF_Guide.md): `BNO08x`를 `D435i`에 임시 고정하고 `camera_link -> imu_link` static TF 준비
- [`18_Jetson_BNO08x_RTABMap_Comparison_Guide.md`](./18_Jetson_BNO08x_RTABMap_Comparison_Guide.md): 현재 `Docker backend + host rtabmap_viz` 구조에서 `RTAB-Map IMU OFF`와 `BNO08x IMU ON` 비교
- [`19_Jetson_BNO08x_Compass_Viewer_Guide.md`](./19_Jetson_BNO08x_Compass_Viewer_Guide.md): `BNO08x` 방향을 나침반 형태로 직관적으로 확인
- [`20_Jetson_Docker_RTABMap_With_BNO08x_Guide.md`](./20_Jetson_Docker_RTABMap_With_BNO08x_Guide.md): host `BNO08x`와 Docker `RTAB-Map`을 현재 wrapper 기준으로 함께 실행하는 절차
- [`21_Jetson_Docker_RTABMap_Baseline_Guide.md`](./21_Jetson_Docker_RTABMap_Baseline_Guide.md): `IMU OFF` 기준 Docker image-only baseline 실행 절차
- [`22_Jetson_Docker_Backend_Host_RTABMapViz_Guide.md`](./22_Jetson_Docker_Backend_Host_RTABMapViz_Guide.md): `Docker`에서 계산하고 host에서 `rtabmap_viz`만 띄우는 우회 절차
- [`23_Jetson_Docker_Preset_and_Benchmark_Guide.md`](./23_Jetson_Docker_Preset_and_Benchmark_Guide.md): `light / medium / compare` preset과 detached benchmark 절차
- [`24_Jetson_BNO08x_Level_Viewer_Guide.md`](./24_Jetson_BNO08x_Level_Viewer_Guide.md): `BNO08x`를 전자 수평계처럼 보고 `roll / pitch`로 수평 판단
- [`25_Jetson_BNO08x_All_In_One_Viewer_Guide.md`](./25_Jetson_BNO08x_All_In_One_Viewer_Guide.md): `나침반 + 수평계 + 기울기 + 회전`을 한 화면에서 동시에 확인
- [`26_Jetson_BNO08x_Motion_Trace_Viewer_Guide.md`](./26_Jetson_BNO08x_Motion_Trace_Viewer_Guide.md): `linear acceleration`을 짧게 적분한 `pseudo-position`을 `X/Y/Z` 축 위 점 이동으로 확인
- [`27_Jetson_BNO08x_Calibration_Guide.md`](./27_Jetson_BNO08x_Calibration_Guide.md): `BNO08x`의 `accelerometer / gyroscope / magnetometer` 보정 절차를 Jetson에서 직접 수행
- [`28_Jetson_Trashbot_URDF_RViz_Guide.md`](./28_Jetson_Trashbot_URDF_RViz_Guide.md): `base_link`, 바퀴, `D435i`, `BNO08x`, GPS frame을 가진 `trashbot_description` 모델을 RViz2에서 확인
- [`29_Jetson_GPS_ROS2_Bringup_Guide.md`](./29_Jetson_GPS_ROS2_Bringup_Guide.md): GPS raw 값 확인부터 `/gps/fix` ROS 2 topic publish까지 진행
