# ESP32 UART Bridge Screenshots

이 폴더는 ESP32-S3와 NUCLEO-F446RE를 UART로 연결해 command bridge를 검증할 때 나온 스크린샷과 사진을 저장한다.

권장 파일명:

| No. | Filename | Content |
| --- | --- | --- |
| 01 | `2026-07-10_01_stm32_esp32_uart_wiring.jpg` | STM32와 ESP32의 GND/TX/RX 배선 사진 |
| 02 | `2026-07-10_02_esp32_uart_loopback_log.png` | ESP32 단독 UART loopback 성공 로그 |
| 03 | `2026-07-10_03_esp32_ping_pong_log.png` | ESP32가 `PING`을 보내고 STM32 `PONG`을 받은 로그 |
| 04 | `2026-07-10_04_esp32_arm_cmd_disarm_log.png` | ESP32 scripted `ARM -> CMD -> DISARM` 결과 |
| 05 | `2026-07-10_05_esp32_telemetry_relay_log.png` | STM32 `TEL` frame이 ESP32에서 수신되는 장면 |

이미지는 검증 리포트에서 바로 렌더링될 수 있도록 Markdown 상대 경로로 링크한다.
