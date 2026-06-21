# Web Serial UART MVP Dashboard

## Purpose

이 문서는 UART MVP 검증을 위한 웹 대시보드 실행 방법을 정리한다.

이번 웹 대시보드는 WebSocket 서버를 만들지 않는다.
브라우저의 Web Serial API를 사용해서 다음 경로로 직접 통신한다.

```text
Chrome / Edge
<-> Web Serial API
<-> ST-LINK Virtual COM Port
<-> STM32 USART2
```

그래서 복잡도는 다음 정도로 제한된다.

```text
Static HTML/CSS/JS + local static file server
```

## Scope

지원 기능:

- Serial connect/disconnect
- `PING`, `ARM`, `DISARM`, `CMD`, raw frame 전송
- `ACK`, `ERR`, `PONG`, `TEL` 수신 표시
- telemetry field display
- fake telemetry mode
- zero-CMD keepalive
- scripted MVP test
- raw log display
- CSV download

지원하지 않는 것:

- WebSocket server
- backend serial bridge
- AI diagnosis
- ROS 2 bridge
- browser가 motor safety authority가 되는 구조

STM32가 여전히 최종 safety authority다.

## Files

```text
04_PC_Serial_Control/
  web_serial_dashboard/
    index.html
    styles.css
    app.js
    README.md
  tools/
    ServeWebDashboard.ps1
    serve_web_dashboard.sh
```

## Browser Requirement

Web Serial API는 일반적으로 desktop Chrome 또는 Edge에서 사용한다.

중요:

- `file://`로 직접 열지 않는다.
- `http://localhost:8765/`처럼 localhost에서 실행한다.
- 브라우저에서 `Connect`를 누르면 serial port 권한 창이 뜬다.
- STM32 firmware가 아직 없으면 `Fake TEL`, raw parse, TX dry-run 성격의 UI 확인만 가능하다.

## Windows Run

PowerShell:

```powershell
cd C:\Users\eyh12\workspace\TIL\Projects\Tracked_Mobile_Robot\04_PC_Serial_Control
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ServeWebDashboard.ps1
```

브라우저에서 연다.

```text
http://localhost:8765/
```

다른 port를 쓰고 싶으면:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ServeWebDashboard.ps1 -Port 8770
```

## Ubuntu Run

```bash
cd ~/workspace/TIL/Projects/Tracked_Mobile_Robot/04_PC_Serial_Control
bash tools/serve_web_dashboard.sh
```

브라우저에서 연다.

```text
http://localhost:8765/
```

다른 port:

```bash
bash tools/serve_web_dashboard.sh 8770
```

## Test Flow

STM32 firmware가 준비된 뒤 다음 순서로 확인한다.

1. 웹 대시보드를 localhost로 연다.
2. baud rate를 `115200`으로 둔다.
3. `Connect`를 누르고 ST-LINK Virtual COM Port를 선택한다.
4. `PING`을 보내 `PONG`을 확인한다.
5. `CMD`를 먼저 보내 `ERR,code=NOT_ARMED`를 확인한다.
6. `ARM`을 보내 `ACK,type=ARM`을 확인한다.
7. valid `CMD`를 보내 `ACK,type=CMD`를 확인한다.
8. `Bad Range`를 보내 `ERR,code=OUT_OF_RANGE`를 확인한다.
9. `Keepalive`를 켰다가 끄고 timeout 후 telemetry 변화를 확인한다.
10. `DISARM`을 보내 `TEL,state=DISARMED`를 확인한다.
11. 필요하면 CSV를 다운로드한다.

## Fake Telemetry

STM32 firmware가 아직 없어도 `Fake TEL`을 켜면 UI display와 CSV download 흐름을 먼저 볼 수 있다.

이 기능은 UI 검증용이다.
실제 UART 검증 evidence는 STM32와 연결한 뒤 raw log와 CSV로 남긴다.

## Troubleshooting

### Connect 버튼이 비활성화됨

가능한 원인:

- Chrome/Edge가 아님
- `file://`로 열었음
- localhost가 아닌 insecure origin에서 열었음

해결:

```text
http://localhost:8765/
```

으로 다시 연다.

### Serial port가 목록에 안 보임

- NUCLEO USB cable이 data cable인지 확인한다.
- STM32CubeProgrammer, serial monitor, 다른 terminal tool이 port를 잡고 있으면 닫는다.
- Windows에서는 Device Manager에서 ST-LINK Virtual COM Port를 확인한다.
- Ubuntu에서는 `/dev/ttyACM0`와 `dialout` 권한을 확인한다.

### TX만 보이고 RX가 없음

- STM32 USART2 firmware가 아직 구현되지 않았을 수 있다.
- STM32가 response 끝에 `\n`을 붙이는지 확인한다.
- baud rate 115200 8N1을 확인한다.

## Portfolio Framing

> PC web dashboard에서 Web Serial API로 STM32 UART MVP frame을 직접 송수신하고, STM32의 ACK/ERR/TEL 응답을 telemetry panel과 raw log/CSV로 검증했다. WebSocket 서버 없이 browser-local serial monitoring으로 시작해 복잡도를 낮췄고, motor safety authority는 STM32 state machine에 유지했다.
