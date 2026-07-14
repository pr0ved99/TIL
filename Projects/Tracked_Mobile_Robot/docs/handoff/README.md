# Handoff Notes

이 폴더는 `Tracked_Mobile_Robot` 프로젝트를 다른 Codex 세션이나 사람이 이어받을 때 필요한 인수인계 문서를 저장한다.

## How To Use

새 대화창에서 작업을 이어갈 때는 아래 순서로 읽는다.

1. [`../../README.md`](../../README.md)
2. [`../../PROJECT_MEMORY.md`](../../PROJECT_MEMORY.md)
3. [`../../AGENTS.md`](../../AGENTS.md)
4. [`NEXT_SESSION_START_PROMPT.md`](NEXT_SESSION_START_PROMPT.md)
5. [`2026-07-14_esp32_stm32_uart_bridge_handoff.md`](2026-07-14_esp32_stm32_uart_bridge_handoff.md)
6. [`../progress/2026-07-14_progress.md`](../progress/2026-07-14_progress.md)

그 다음 현재 작업 주제에 맞는 verification, firmware, learning note를 읽는다.

## Current Handoff

| Date | File | Use |
| --- | --- | --- |
| 2026-07-14 | [`2026-07-14_esp32_stm32_uart_bridge_handoff.md`](2026-07-14_esp32_stm32_uart_bridge_handoff.md) | ESP32-S3 ESP-IDF bring-up 이후 STM32 USART1 bridge 작업을 이어가기 위한 최신 인수인계 |

## Historical Handoff

| Date | File | Note |
| --- | --- | --- |
| 2026-06-22 | [`2026-06-22_tracked_mobile_robot_handoff.md`](2026-06-22_tracked_mobile_robot_handoff.md) | STM32CubeMX-first UART MVP 구현 전후 상태 |
| 2026-06-04 | [`2026-06-04_tracked_mobile_robot_handoff.md`](2026-06-04_tracked_mobile_robot_handoff.md) | 초기 프로젝트 상태, 현재와 다른 결정이 포함될 수 있음 |

## Rules For Future Handoff

- 새 handoff는 날짜 prefix를 붙인다: `YYYY-MM-DD_topic_handoff.md`.
- 최신 handoff는 이 README의 `Current Handoff`에 추가한다.
- handoff에는 반드시 다음을 포함한다.
  - 현재 목표
  - 완료된 것
  - 다음 작업
  - 건드리면 안 되는 파일/결정
  - hardware wiring safety
  - evidence 위치
  - 첫 번째로 실행할 확인 명령
- 새 세션은 `git status --short Projects/Tracked_Mobile_Robot`를 먼저 실행한 뒤 작업한다.

