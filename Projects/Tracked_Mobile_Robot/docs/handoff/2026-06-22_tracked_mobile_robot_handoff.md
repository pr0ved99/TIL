# Tracked Mobile Robot Handoff - 2026-06-22

## Purpose

This handoff is the current continuation note for future Codex sessions and manual work.

The older `2026-06-04_tracked_mobile_robot_handoff.md` is historical and describes a pre-MDD10A/BTS7960 planning state. For current work, use this file together with `PROJECT_MEMORY.md`, `AGENTS.md`, and the latest progress log.

## Read First

1. `PROJECT_MEMORY.md`
2. `AGENTS.md`
3. `README.md`
4. `docs/progress/2026-06-22_progress.md`
5. `04_PC_Serial_Control/docs/06_STM32_UART_MVP_Detailed_Implementation_ko.md`

## Current State

- Active low-level board: `NUCLEO-F446RE`
- Active motor driver path: `MDD10A`
- Superseded motor driver path: `BTS7960`
- First communication path: PC/ESP32 command source to STM32 over UART line frames
- First PC validation path: ST-LINK Virtual COM Port / USART2
- Current firmware task: STM32 UART MVP, without MDD10A, motors, or LiPo main power connected

## Important Decisions

- STM32 is the final safety authority for command timeout and motor output permission.
- PC and ESP32 use the same UART MVP application frames.
- The first UART MVP uses `ACK` for accepted commands and `ERR` for rejected commands or parse failures.
- A separate `NACK` frame is not used.
- Timeout first drives output zero while staying armed; later auto-disarm behavior is documented as lab default in the firmware guide.
- Browser dashboard uses Web Serial directly from localhost. WebSocket is optional and not part of the first MVP.
- AI-assisted log diagnosis is optional and cannot become the primary motor safety authority.

## Current Tooling

PC-side tools:

- `04_PC_Serial_Control/tools/UartMvpTool.ps1`: Windows PowerShell UART MVP tool
- `04_PC_Serial_Control/tools/uart_mvp_tool.sh`: Ubuntu/Linux Bash UART MVP tool
- `04_PC_Serial_Control/tools/uart_mvp_tool.py`: Python UART MVP tool, not the first path on this Windows machine
- `04_PC_Serial_Control/web_serial_dashboard`: browser Web Serial dashboard
- `04_PC_Serial_Control/tools/ServeWebDashboard.ps1`: Windows localhost server
- `04_PC_Serial_Control/tools/serve_web_dashboard.sh`: Ubuntu/Linux localhost server

Firmware guide:

- `04_PC_Serial_Control/docs/06_STM32_UART_MVP_Detailed_Implementation_ko.md`

This guide now assumes a STM32CubeMX-first workflow.

## CubeMX-First Firmware Workflow

Do not start from `STM32CubeIDE Empty Project`.

Use this flow:

```text
STM32CubeMX 설치/실행
-> Board Selector에서 NUCLEO-F446RE 선택
-> USART2 PA2/PA3, 115200 8N1 설정
-> USART2 global interrupt enable
-> 03_Firmware/stm32_uart_mvp 아래로 code generation
-> STM32CubeIDE에서 open/import
-> ring_buffer.* / uart_mvp_protocol.* 추가
-> build / flash
-> PC dashboard 또는 terminal tool로 PING/ACK/ERR/TEL 검증
```

Expected firmware project location:

```text
C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\03_Firmware\stm32_uart_mvp
```

## Next Actions

1. Create the STM32CubeMX project for `NUCLEO-F446RE` under `03_Firmware/stm32_uart_mvp`.
2. Configure USART2 PA2/PA3 at 115200 8N1 and enable `USART2 global interrupt`.
3. Generate code and open/import it in STM32CubeIDE.
4. Add `ring_buffer.*` and `uart_mvp_protocol.*` following the detailed guide.
5. Build and flash the firmware with no motor power connected.
6. Run the Web Serial dashboard or terminal scripted test.
7. Save UART logs and screenshots as evidence.
8. Update `docs/progress/YYYY-MM-DD_progress.md` with results and blockers.

## Validation Target

The first firmware validation is complete when these are visible from PC logs:

```text
PING -> PONG
CMD before ARM -> ERR,code=NOT_ARMED
ARM -> ACK
valid CMD -> ACK
out-of-range CMD -> ERR,code=OUT_OF_RANGE
timeout -> TEL with left_pwm=0,right_pwm=0
DISARM -> ACK and TEL,state=DISARMED
```

## Do Not Do Yet

- Do not connect MDD10A to motor power for this UART MVP firmware test.
- Do not connect DC motors.
- Do not connect the 3S LiPo main power path.
- Do not start CAN or FreeRTOS migration before the UART MVP evidence is captured.
