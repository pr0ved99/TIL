# UART MVP Screenshots

이 폴더는 UART MVP 실습의 화면 증거를 모아 두는 곳이다.

가이드 문서에 이미지를 넣을 때는 실제 스크린샷 파일이 존재하는지 먼저 확인한다.
아직 파일이 없으면 Markdown 이미지 링크를 만들지 않는다. 깨진 이미지 링크를 남기지 않기 위해서다.

## Recommended Captures

- STM32CubeMX `Board Selector`에서 `NUCLEO-F446RE`를 선택한 화면
- STM32CubeMX USART2 `Mode` / `Parameter Settings` 화면
- STM32CubeMX USART2 `NVIC Settings` 화면
- STM32CubeMX `Project Manager`와 `GENERATE CODE` 화면
- STM32CubeIDE import/open 화면
- STM32CubeIDE build success 화면
- Windows Device Manager COM port evidence
- Web Serial dashboard `PING/PONG`, `ACK`, `ERR`, `TEL` logs

## Filename Rule

파일명은 날짜, 순서, 화면 성격이 드러나게 저장한다.

```text
YYYY-MM-DD_01_cubemx_board_selector.png
YYYY-MM-DD_02_usart2_mode_async.png
YYYY-MM-DD_03_usart2_parameter_settings.png
YYYY-MM-DD_04_usart2_pinout_pa2_pa3.png
YYYY-MM-DD_05_usart2_nvic_settings.png
YYYY-MM-DD_06_project_manager_toolchain.png
YYYY-MM-DD_07_generate_code_success.png
YYYY-MM-DD_08_cubeide_import_project.png
YYYY-MM-DD_09_cubeide_build_success.png
YYYY-MM-DD_10_device_manager_com_port.png
YYYY-MM-DD_11_web_serial_ping_ack_tel.png
```

## Guide Mapping

`04_PC_Serial_Control/docs/06_STM32_UART_MVP_Detailed_Implementation_ko.md`에 이미지를 넣을 때는 아래 기준으로 배치한다.

| Screenshot keyword | Guide section |
| --- | --- |
| `cubemx_board_selector` | `1.2 Board 선택` |
| `usart2_mode_async` | `2.1 USART2 Mode 선택` |
| `usart2_parameter_settings` | `2.2 USART2 Parameter Settings` |
| `usart2_pinout` or `pa2_pa3` | `2.3 USART2 Pin 확인` |
| `usart2_nvic_settings` | `2.4 USART2 NVIC 설정` |
| `project_manager` or `toolchain` | `3.1 Project` / `3.2 Code Generator` |
| `generate_code_success` | `3.3 Code Generate` |
| `cubeide_import_project` | `4.2 CubeIDE에서 import` |
| `cubeide_build_success` | `5. 생성 직후 Build 확인` |
| `device_manager_com_port` | `22.4 PC에서 COM port가 안 보임` 또는 `25. Evidence 정리` |
| `web_serial` | `23. PC Web Dashboard 검증` |

## Captured Screenshots

현재 문서에 반영된 파일:

| File | Meaning | Guide section |
| --- | --- | --- |
| `2026-06-22_01_cubemx_initial_pinout_nucleo_f446re.png` | NUCLEO-F446RE board project가 열린 초기 pinout 화면 | `1.3 Board 선택 후 바로 확인할 것` |
| `2026-06-22_03_usart2_parameter_settings.png` | USART2 Asynchronous mode와 115200 8N1 parameter 확인 화면 | `2.2 USART2 Parameter Settings` |
| `2026-06-22_04_usart2_pinout_pa2_pa3.png` | PA2/PA3가 USART TX/RX로 잡힌 pinout 확인 화면 | `2.3 USART2 Pin 확인` |
| `2026-06-22_05_usart2_nvic_settings.png` | USART2 global interrupt가 enabled 된 NVIC 설정 화면 | `2.4 USART2 NVIC 설정` |
| `2026-06-22_06_project_manager_toolchain.png` | Project name/location과 STM32CubeIDE toolchain 설정 화면 | `3.1 Project` |
| `2026-06-22_07_code_generator_peripheral_files.png` | peripheral별 `.c/.h` 분리 생성과 user code 보존 설정 화면 | `3.2 Code Generator` |
| `2026-06-22_09_cubeide_build_success.png` | STM32CubeIDE 기본 생성 코드 build success 화면 | `5. 생성 직후 Build 확인` |

`06` 가이드에서 이 폴더의 이미지를 참조할 때는 다음 상대 경로를 사용한다.

```text
../../assets/screenshots/uart_mvp/<actual-screenshot-file-name>.png
```

Markdown 이미지 링크는 실제 파일이 존재할 때만 추가한다.

## Notes

- Windows가 자동으로 만드는 `desktop.ini`는 Git에 포함하지 않는다.
- 같은 단계에서 여러 장을 캡처했다면 `a`, `b` suffix를 붙인다.
- 예: `YYYY-MM-DD_03a_usart2_parameter_basic.png`, `YYYY-MM-DD_03b_usart2_parameter_advanced.png`
