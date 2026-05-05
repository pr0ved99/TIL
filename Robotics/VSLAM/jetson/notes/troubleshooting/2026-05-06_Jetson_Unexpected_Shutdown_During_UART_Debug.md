# 2026-05-06 Jetson Unexpected Shutdown During UART Debug

## 증상

- `Jetson Orin Nano`에서 GPS UART bring-up과 40핀 header UART loopback을 진행하는 중, 갑자기 Jetson이 shutdown되는 현상이 있었다.
- 아직 shutdown 시점의 정확한 로그와 원인은 확인하지 않았다.
- 이 문제는 `R36.5 UART DMA/DTB` 이슈와 별도 항목으로 분리해 추적한다.

## 당시 작업 맥락

- GPS 모듈 `GY-GPS6MV2 / NEO-6M`을 Jetson 40핀 header UART에 직접 연결하는 작업 중이었다.
- `pin 8 <-> pin 10` loopback, Jetson-IO 설정 확인, DTB 수정, PIO mode 우회 검증을 진행했다.
- 이후 PIO mode에서 `/dev/ttyTHS1` loopback과 GPS NMEA 수신은 성공했다.

## 가능한 원인 후보

### 전원 계통

- Jetson 전원 어댑터 또는 케이블의 순간 전류 부족
- USB 주변장치, GPS, 팬, NVMe 등 주변장치 부하 변화
- 배선 작업 중 순간적인 전원/GND 접촉 불안정

### 열 또는 부하

- 장시간 작업 중 온도 상승
- 팬 동작 문제 또는 통풍 문제
- GPU/CPU 부하는 낮아도 케이스 내부 열이 쌓이는 상황

### 커널/드라이버 fault

- UART DMA/DTB 문제로 `SMMU/IOMMU fault`와 memory controller error가 반복된 상태였다.
- 이 fault가 shutdown의 직접 원인인지는 아직 확인하지 않았다.
- PIO mode 적용 후 동일 현상이 재현되는지 분리 확인이 필요하다.

### 물리 배선

- 40핀 header 작업 중 점퍼선이 인접 핀과 순간 접촉했을 가능성
- GPS 전원선과 UART 신호선 작업 중 전원 ON 상태에서 배선을 만졌을 가능성
- `3.3V`, `5V`, `GND`, `TX/RX` 접촉 실수 가능성

## 확인 명령

shutdown 직후 다음 부팅에서 확인한다.

```bash
last -x | head -n 30
journalctl --list-boots
journalctl -b -1 -p warning..alert --no-pager | tail -n 120
journalctl -b -1 --no-pager | grep -iE 'shutdown|reboot|power|thermal|overtemp|watchdog|panic|oops|fault|smmu|tegra' | tail -n 160
```

현재 부팅 상태에서 온도와 부하를 확인한다.

```bash
uptime
tegrastats --interval 1000
```

`tegrastats`는 10초 정도 관찰한 뒤 `Ctrl+C`로 종료한다.

## 다음에 재현되면 기록할 것

- 정확한 시각
- 전원이 툭 꺼졌는지, 정상 shutdown 메시지가 보였는지
- 배선 변경 중이었는지, 명령 실행 중이었는지
- 연결된 장치 목록
- 전원 어댑터 종류와 전원 입력 방식
- 재부팅 후 `journalctl -b -1` 결과
- 재부팅 후 `dmesg`의 thermal, watchdog, panic, SMMU fault 여부

## 임시 안전 원칙

- 40핀 header 배선 변경은 가능한 전원 OFF 상태에서 진행한다.
- 전원 ON 상태에서는 `3.3V`, `5V`, `GND` 주변 점퍼선을 움직이지 않는다.
- GPS UART 테스트는 현재 성공한 `JetsonIO-UARTA-PIO` boot entry에서 계속한다.
- 같은 shutdown이 다시 나오면 GPS/ROS 2 진행보다 전원과 커널 로그 확인을 우선한다.

## 현재 판단

- 아직 원인 미확정이다.
- 다만 UART DMA 문제는 PIO mode로 우회되어 loopback과 NMEA 수신이 정상화됐다.
- 따라서 이후 shutdown이 다시 발생하면 UART DMA보다는 전원, 열, 물리 접촉, 다른 kernel fault를 우선 확인한다.
