# VSLAM Study

Visual SLAM(VSLAM)은 카메라 영상으로 자신의 위치를 추정하고 주변 지도를 만드는 기술이다.

## Structure

- `00_Basics`: 좌표계, 카메라 모델, 에피폴라 기하, 선형대수 기초
- `01_Calibration`: 카메라 보정, 왜곡 파라미터, 외부 파라미터, 시간 동기화
- `02_Feature_Tracking`: 특징점 검출, 디스크립터, 추적, 매칭, 이상치 제거
- `03_Visual_Odometry`: 프레임 간 상대 자세 추정, PnP, 삼각측량, 스케일 이슈
- `04_Backend_Optimization`: 번들 조정, 비선형 최적화, 노이즈 모델, 수치 안정성
- `05_Loop_Closure`: 장소 인식, 재방문 검출, 포즈 그래프 보정
- `06_Debugging`: 좌표계 오류, timestamp sync 문제, scale drift, 추적 실패 점검
- `07_Evaluation`: ATE, RPE, FPS, latency, 메모리/연산량 평가

## Note

학습 자료는 각 폴더 안에 Markdown 문서와 예제 코드로 정리한다.
