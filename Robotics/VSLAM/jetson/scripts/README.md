# Jetson Scripts

## 결론

- 이 폴더는 `Jetson`에서 직접 실행하는 스크립트만 따로 모아두는 공간이다.
- 기존 `06_Debugging/` 스크립트는 공통 실험용으로 두고, 여기에는 `Jetson` 전용 wrapper, launch helper, 성능 측정 스크립트를 둔다.

## 넣을 대상

- `Jetson` 전용 launch wrapper
- `CPU`, `memory`, `temperature` 측정 스크립트
- `D435i + RTAB-Map` 한 번에 올리는 실행 스크립트
- `Jetson` 현장 점검용 빠른 체크 스크립트

## 원칙

- 공통 스크립트와 중복 복사하지 않는다.
- `Jetson`에서만 필요한 옵션이나 경로가 있을 때만 이 폴더에 둔다.
