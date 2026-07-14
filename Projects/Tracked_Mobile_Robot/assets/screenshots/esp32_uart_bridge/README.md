# ESP32 UART Bridge Screenshots

이 폴더는 ESP32-S3와 NUCLEO-F446RE를 UART로 연결해 command bridge를 검증할 때 나온 스크린샷과 사진을 저장한다.

권장 파일명:

| No. | Filename | Content |
| --- | --- | --- |
| 01 | `2026-07-14_01_esp32_idf_project_settings.png` | `esp32s3`, `COM4`, `board/esp32s3-builtin.cfg` 설정 화면 |
| 02 | `2026-07-14_02_esp32_idf_build_success.png` | ESP-IDF build 성공 또는 memory usage summary |
| 03 | `2026-07-14_03_esp32_idf_flash_done.png` | `Flash Done` 로그 |
| 04 | `2026-07-14_04_esp32s3_monitor_hello_world.png` | ESP32-S3 `hello_world` monitor 로그 |
| 05 | `2026-07-14_05_stm32_esp32_uart_wiring.jpg` | STM32와 ESP32의 GND/TX/RX 배선 사진 |
| 06 | `2026-07-14_06_esp32_uart_loopback_log.png` | ESP32 단독 UART loopback 성공 로그 |
| 07 | `2026-07-14_07_esp32_ping_pong_log.png` | ESP32가 `PING`을 보내고 STM32 `PONG`을 받은 로그 |
| 08 | `2026-07-14_08_esp32_arm_cmd_disarm_log.png` | ESP32 scripted `ARM -> CMD -> DISARM` 결과 |
| 09 | `2026-07-14_09_esp32_telemetry_relay_log.png` | STM32 `TEL` frame이 ESP32에서 수신되는 장면 |

이미지는 검증 리포트에서 바로 렌더링될 수 있도록 Markdown 상대 경로로 링크한다.
