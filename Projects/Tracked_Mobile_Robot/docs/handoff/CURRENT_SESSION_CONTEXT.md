# Current Session Context

Last updated: 2026-09-23 — encoder conditioning electrical checks complete; actual encoder next.

## 현재 종료 지점

**엔코더 입력 조정부 실제 납땜 완료 사용자 보고. 저항 8곳, 전원 연결·단락 6곳 PASS.
JENC_1/2 모두 +5.05V. 실제 엔코더 연결부터 다음 세션으로 보류했다.**

먼저 [9/23 progress](../progress/2026-09-23_progress.md)와 필요한 부분의
[report 28](../verification/28_Encoder_Conditioning_Assembly_and_Electrical_Check_Report_2026-09-23_ko.md)을 읽는다.
완료한 저항·도통·5.05V 검사는 배선 변경이나 실패가 없으면 반복하지 않는다.

## 바로 다음 작업

1. 실제 무전원 상태와 엔코더 4선 케이블 준비 여부·제품 핀 방향을 확인한다.
   마지막 케이블 준비 질문은 사용자가 작업을 미루어 미답변이다. 준비됐다고 가정하지 않는다.
2. 무전원에서 GND/B/A/5V를 JENC에 연결한다. 모터 동력선 2개는 계속 분리한다.
3. STM32 분리 상태로 실제 엔코더의 A/B LOW/HIGH를 JDBG_ENC에서 측정한다.
   축을 조금씩 돌려 멈추며 측정한다. 연속 회전 중 DMM 평균을 HIGH로 해석하지 않는다.
4. 입력 전압 적합성 확인 후 보드를 복원하고 새 배선의 수동 회전·양방향·정지·독립성을 검증한다.

최종 안내는 S1 OFF→LiPo 분리였다. 사용자의 마지막 별도 분리 완료 보고는 없으므로
전원이 꺼졌다고 문서만으로 판단하지 않는다. 이번 종료에는 실제 엔코더를 연결하지 않았다.

## 새 도면과 실물 검사

- 현재 VRT: `09_Electrical_Design/VeroRoute/Tracked_Mobile_Robot_Perfboard_RevC_Estop_Logic_Power_UART_Debug_ENC_Conditioning_WIP.vrt`.
  182,515 bytes; SHA-256 `09c1546d04eeaf581bc55ea9717965a56fd6dac742b565f9796924bdf8fbef78`.
- exports의 동일 이름 PDF: 02:36 저장, 172,045 bytes; 새 연결 반영 확인.
- 저장 Net/Flying Wire Pad 19개와 Broken Nets 0개 확인. 전체 좌표·Net은 report 28에 있다.
- JENC_1=C50/R11~14, JENC_2=C54/R5~8. 위→아래 Pin1 GND, Pin2 B raw, Pin3 A raw, Pin4 AUX_5V.
- 왼쪽 PB4/A=R2 1k+R6 15k, PB5/B=R1+R5. 오른쪽 PA0/A=R4+R8, PA1/B=R3+R7.
  직렬저항 뒤 MCU 노드에 풀다운과 JDBG를 연결한다. AUX는 R13 앞 J3 Pin1에서 분기한다.
- 실제 납땜 완료 및 두 보드 장착 monitor 사용자 보고. 이후 저항 검사 8곳 모두 정상;
  직렬 최솟값 0.98kΩ, 풀다운 한 값 14.69kΩ. JENC 전원 6검사 및 두 +5.05V PASS.
- 1k+15k는 범용 5V→3.3V 분압기가 아니다. 실제 엔코더 연결 후 새 배선의 입력 전압 검증이 남았다.
- 커넥터 실물 제품/케이블과 부품 높이·고정 상태를 도면만으로 확정하지 않는다.

## 로그의 확인 범위

[9/23 monitor](../../assets/logs/encoder/2026-09-23_perfboard_conditioning/README.md):
STM t_ms=4200~44100, TEL 400개/39.9초, left/right CPS 모두 0, TEL 100ms 연속.
FAULT/ESTOP_ACTIVE 유지, PWM 보고값 0, err=7 고정. RX_DESYNC 1회 뒤 DISARM ACK/PONG/READY.
첫 4.2초가 없어 과거 300/400ms 부팅 튐 해결은 미확인이다. 로그 촬영 때 임시 빵판 저항 제거와
엔코더 케이블 상태는 별도 보고되지 않았다. 이후 무전원 검사에는 STM/임시 저항 분리를 안내했다.
CPS 계산을 변경하지 않는다. 새 실제 엔코더 경로 전체 PASS로 확대하지 않는다.

## T005A와 현재 전력단

[report 27](../verification/27_T_ESTOP_005A_Motor_Disconnected_Rail_and_Safe_Restore_Report_2026-09-23_ko.md):
9/22 run01~06과 파생 증거 보존 완료. **T005A 전체 PARTIAL**, T004 PASS는 유지한다.

- 두 커버형 버스바 사용. +는 S1 OUT→XL1/XL2 IN+, K1 30, F2/6P Pin1 분기.
  −는 LiPo−/XL1·XL2 IN−/MDD B−. MDD B+=K1 87, B−=GND 16 AWG. K1 주선 14 AWG.
- MDD 5P 제어 하네스 연결, 두 모터는 분리. BNO 모듈은 미연결.
- run03 오른쪽 RESET 표기 버튼은 ESP 송신을 멈추지 않았다.
  실제 HG-ESP32-S3-DevkitC-1은 **왼쪽 BOOT 표기 버튼이 EN LOW**를 만든다.
  run04에서 마지막 CMD 끝→PWM 정지 498.635ms와 CMD_TIMEOUT 관측.
- run05/06 all-hooks-0U 복구 후 25초 두 PWM HIGH0, 자동 ARM/CMD/RESET 없음.
  right_cps=10 한 번씩(t_ms=300/400)이 남아 이번 입력 조정부 작업으로 이어졌다.
- DMM 잔류 0.45~1.6V를 임의 rail-off PASS로 처리하지 않는다. V_RAIL_OFF_MAX/판정 시점,
  F1 257/287 식별, F2 식별, K1 단자-선재 release 항목은 report 27을 따른다.
- T005A D4=STM TX/TEL, D5=ESP TX/명령. 이전 T004와 채널 역할이 반대다.

## 전원·펌웨어·작업 방식

- XL4015 #1 OUT에서 별도 2P 두 갈래로 NUCLEO/ESP32에 공급한다. 중간 4P는 없다.
  #2는 AUX_5V이며 두 buck의 OUT+는 분리, GND 공통.
- 독립 전원 운전: USB 제거, NUCLEO JP5=E5V, JP1=OPEN.
  USB 개발: S1 OFF/LiPo 분리/잔류전압 확인 후 #1 두 2P 분리, JP5=U5V/JP1=OPEN,
  두 보드 각각 USB 공급. USB와 buck을 동시 공급하지 않는다.
- ESP controlled hook 네 개 모두 0U, STM unchanged. 복구 사용자 빌드·플래시 및 당시 static 30/30 PASS.
  source SHA `ecc304898b7f61ba1c28a8f01fa69b2fe9b11eb196bfaf02fb911d003ef000e4`,
  ELF SHA 시작 `3c5b64553806`; 9/23 monitor의 `3c5b64553...`와 일치. flash readback은 아니다.
- 사용자가 펌웨어 입력, STM/ESP 빌드·플래시와 하드웨어 조작을 수행한다. Codex가 대신 진행하지 않는다.
- 코드 안내는 연결된 블록 전체와 정확한 교체 범위·이유를 제공한다. bench는 한 측정 묶음씩 진행한다.
- progress는 사용자 작업 마감 때 한 번에 갱신. 하위 PASS를 전체로 확대하지 않는다.
- 사용자 요청 없이 subagent/전체 대화 아카이브 검색을 실행하지 않는다.
- repo `C:\Users\eyh12\workspace\TIL`, branch `agent/dual-encoder-bringup`.
  사용자가 이번 문서·증거·도면의 Git 커밋/푸시를 요청했다. 현재 commit/원격 상태는 Git에서 확인한다.
