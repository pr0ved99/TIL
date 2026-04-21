# Jetson Assets

## 결론

- 이 폴더는 `Jetson`에서 실제로 관찰한 증빙 자료를 종류별로 분리 저장하는 공간이다.
- 화면 캡처, 로그, 성능 측정 결과를 섞지 않고 나누어 보관한다.

## 구조

- `screenshots/`
  - `Jetson` 화면, `RViz`, `rtabmap_viz`, `realsense-viewer` 캡처
- `videos/`
  - `Jetson` 작업과 직접 연결된 동영상 증빙, 시각화 참고 영상
- `logs/`
  - launch 로그, 재시험 로그, 오류 로그
- `benchmarks/`
  - CPU, memory, temperature, FPS, topic rate 같은 성능 측정 결과

## 규칙

- 파일명은 `날짜 + 도구 + 무엇을 증명하는지`가 드러나게 쓴다.
- 같은 실험의 캡처와 로그는 가능하면 같은 날짜 하위 폴더로 묶는다.
- 영상은 원본 파일명을 `README.md`에 남기고, 보관본 이름은 실험 맥락이 드러나게 정리한다.
