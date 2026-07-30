# Firmware Safety Contract Tests

이 디렉터리의 테스트는 STM32와 ESP32 펌웨어 사이에서 이미 확정한 핀,
UART, timer, encoder sign, motor-output safety 설정이 소스 변경이나 CubeMX
재생성으로 조용히 달라지는 것을 막는 정적 preflight 검사다.

## 실행

저장소 루트에서 다음 명령을 실행한다.

```powershell
python -m unittest discover `
  -s Projects/Tracked_Mobile_Robot/03_Firmware/tests `
  -p "test_*.py" `
  -v
```

외부 Python 패키지는 필요하지 않다. 실패가 발생하면 firmware build나 flash를
진행하기 전에 변경된 `.ioc`, generated source, user-code contract를 확인한다.

## 범위와 한계

- CubeMX `.ioc` pin/peripheral 설정과 generated C source의 일치 여부
- STM32-ESP32 UART1 `115200 8-N-1`, GPIO17/18와 PA9/PA10 계약
- TIM3/TIM5 encoder, TIM4 nominal 20 kHz PWM와 left/right mapping
- 모든 bench-only output/test hook의 기본 비활성 상태
- boot, DISARM, timeout, Error Handler의 source-level output-zero 경로

이 검사는 컴파일 성공이나 실제 전기 신호를 증명하지 않는다. STM32/ESP32 build,
로직 분석기 PWM·direction·shutdown latency 측정, E-stop 및 powered-motor 검증은
별도 verification gate로 계속 수행해야 한다.
