# ESP32 UART Bridge Screenshots

이 폴더는 ESP32-S3와 NUCLEO-F446RE를 UART로 연결해 command bridge를 검증할 때 나온 스크린샷과 사진을 저장한다.

확보한 evidence:

| No. | Filename | Content |
| --- | --- | --- |
| 01 | `2026-07-14_01_esp32_idf_project_settings.png` | `esp32s3`, `COM4`, `board/esp32s3-builtin.cfg` 설정 화면 |
| 02 | `2026-07-14_02_esp32_idf_build_success.png` | ESP-IDF build 성공 또는 memory usage summary |
| 03 | `2026-07-14_03_esp32_idf_flash_done.png` | `Flash Done` 로그 |
| 04 | `2026-07-14_04_esp32s3_monitor_hello_world.png` | ESP32-S3 `hello_world` monitor 로그 |
| 05 | `2026-07-14_05_esp32_basic_loop_monitor.png` | ESP32-S3 기본 loop firmware가 주기 로그를 출력하는 장면 |
| 06 | `2026-07-14_06_esp32_uart1_init_monitor.png` | ESP32 UART1이 `TX=GPIO17`, `RX=GPIO18`, `115200`으로 초기화된 로그 |
| 07 | `2026-07-14_07_esp32_uart1_ping_tx_initial.png` | ESP32 UART1에서 `PING,seq=...` 송신이 처음 동작한 로그 |
| 08 | `2026-07-14_08_esp32_uart1_ping_tx_continuous.png` | ESP32 UART1 `PING` 송신이 주기적으로 유지되는 로그 |
| 09 | `2026-07-14_09_esp32_uart1_loopback_ping_rx.png` | ESP32 GPIO17-TX와 GPIO18-RX loopback으로 `PING` 송수신을 검증한 로그 |
| 10 | `2026-07-14_10_esp32_stm32_uart_overflow_before_stm32_flash.png` | STM32가 최신 USART1 firmware로 실행되지 않았을 때 나타난 RX overflow/깨진 수신 증상 |
| 11 | `2026-07-14_11_esp32_stm32_uart_ping_pong_tel_success.png` | STM32 USART1과 ESP32 UART1 연결 후 `TEL`, `PING`, `PONG`이 정상 왕복된 최종 성공 로그 |
| 12 | `2026-07-14_12_esp32_uart_parser_tel_pong_classification_success.png` | ESP32 수신 파서가 STM32 `TEL`과 `PONG` frame을 구분하고 count를 증가시키는 로그 |
| 13 | `2026-07-18_13_esp32_structured_tel_parser_success.png` | ESP32가 `TEL`의 `state`, `last_seq`, `vx`, `w`, `err`를 구조화하고 실제 STM32 link에서 반복 출력한 로그 |

이미지는 검증 리포트에서 바로 렌더링될 수 있도록 Markdown 상대 경로로 링크한다.

다음 evidence 권장 파일명:

| No. | Filename | Content |
| --- | --- | --- |
| 14 | `YYYY-MM-DD_14_esp32_scripted_command_ack_err.png` | `CMD before ARM`, `ARM`, valid/invalid `CMD`, `DISARM` ACK/ERR |
| 15 | `YYYY-MM-DD_15_esp32_timeout_zero_telemetry.png` | command 중단 후 STM32 timeout-zero telemetry |
