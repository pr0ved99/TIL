# ESP32-S3 Study

ESP32-S3 DevKitC-1 기반 임베디드 실습을 정리하는 공간이다.

현재 기준 보드는 HG ESP32-S3 DevKitC-1이며, 실습은 보드 단독으로 가능한 내용부터 진행한다. 외부 센서나 모터가 필요한 실습은 별도 준비물이 생긴 뒤 분리해서 기록한다.

## Structure

- `Practice`: 실습 절차, 명령어, 결과 로그, 트러블슈팅
- `Theory`: ESP-IDF, FreeRTOS, GPIO, Wi-Fi, BLE, USB/JTAG 개념 정리
- `assets`: 회로도 캡처, 보드 사진, 실행 결과 이미지
- `docs`: 진행 기록, 환경 메모, 이어받기용 문서

## Current Board

- Board: HG ESP32-S3 DevKitC-1
- Connection: USB hub 경유 연결
- Detected device: `Espressif USB JTAG/serial debug unit`
- Serial port: `/dev/ttyACM0`
- Stable path: `/dev/serial/by-id/usb-Espressif_USB_JTAG_serial_debug_unit_20:6E:F1:B4:B5:5C-if00`
- Flash: 실제 감지 `16MB`

## Current Status

- 2026-05-22: ESP-IDF `v5.4.4` 설치 완료
- 2026-05-22: `~/esp/hello_world` build/flash/monitor 성공
- 2026-05-22: `~/esp/esp32s3_rgb_led` build/flash 성공 및 내장 RGB LED 점멸 확인
- 2026-05-22: 다음 실습 후보는 BOOT 버튼 입력 처리

## Practice Index

- `Practice/00_ESP32S3_DevKitC1_Setup.md`: 보드 연결 확인과 ESP-IDF 첫 실습 준비
- `Practice/01_ESP32S3_RGB_LED.md`: 내장 RGB LED 제어와 `GPIO38` 확인

## First Goal

1. ESP-IDF 환경을 준비한다.
2. `hello_world` 예제를 ESP32-S3 대상으로 빌드한다.
3. `/dev/ttyACM0`로 flash/monitor를 실행한다.
4. 내장 RGB LED, BOOT 버튼, FreeRTOS 태스크 순서로 보드 단독 실습을 확장한다.
