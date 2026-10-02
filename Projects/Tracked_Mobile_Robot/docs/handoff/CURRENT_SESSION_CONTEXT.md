# Current Session Context

Last updated: **2026-10-03 — Wi-Fi 설정 확인·ESP 예제 검토와 문서 최신화. 현재는 Wi-Fi 코드 이해를 위한 기초 학습, 이후 ESP 단독 WebSocket 상태 전송**.

## 바로 이어갈 작업

현재 사용자는 Wi-Fi 코드 이해를 위해 별도 IDE와 `03_Firmware/esp32_examples`를 만들었다. [10/3 검토 기록](../progress/2026-10-03_progress.md)을 따른다. 코드가 있는 것은 01 Hello World이며 02~05는 빈 폴더다. 예제 README에는 01 빌드 성공이 기록돼 있으나 실행 로그는 미확인이다. 먼저 로그·태스크·이벤트의 역할을 익히며 기존 WebSocket 전체 코드 입력을 완료했다고 가정하지 않는다. 예제 README에 실행 안내를 추가했고 생성 파일 Git 제외와 설정 재현은 남아 있다.

A의 실제 전진 방향, A active DISARM, A 물리 S0의 PWM/엔코더 관측, A/B 각각10%·3초 제한 구동을 완료했다.
**이 시험들을 처음부터 반복하지 않는다.** 10/1에는 노트북·ESP로 Wi-Fi를 검증했고, 10/2에는 로봇 배선을 재연결한 뒤 기본 전원·접점 점검을 진행했다.

- 먼저 [10/2 진행 기록](../progress/2026-10-02_progress.md)을 따른다. 6핀 방수커넥터/JESTOP 유지, F1→S1→Bar+와 K1 30/F2 분기를 사용자 확인했다.
- 지속 단락음 없음, 연결 도통과 S0/S2 접점 정상 보고. Bar+ 12.11V, XL4015 #1/#2 5.02V/4.95V. MDD는 S0 잠금0.50V→해제만0.48V→S2 후12.11V→S0 잠금5초1.0V/30초0.57V였다.
- S1 OFF 10초 후 **Bar 0.67V**, S0 해제/S1 재투입/S2 미조작 5초 후 **MDD 0.52V**. 낮은 전압 관측을 0V·전체 rail-off PASS로 확대하지 않는다. 잔류 원인/최종 수용 기준은 미확정이다.
- 최종 S1 OFF·S0 잠금·LiPo 분리 안내 뒤 사용자가 "분리했고"라고 답해 전원 분리 완료를 확인했다. 같은 마감 질문을 반복하지 않는다.
- 바탕화면 `전선정리` 사진5장을 확인했다. 배선 정리1차 마무리로 판단하며 금속 슬롯/노출 S1 단자 보호, 현가·궤도 간섭과 홀더 고정은 조립 마감 때 확인한다. 사진상 모터는 섀시 장착, 궤도·STM/ESP 본체는 미장착이다. 자세한 범위는 당일 기록을 따른다.
- 아래 Wi-Fi/PCB 계획과 9/30 모터 성과는 보존한다. 이번에 새 모터 구동·펌웨어 변경·UART 통합 검증은 하지 않았다.

1. [10/1 마감 기록](../progress/2026-10-01_progress.md)과 [report32](../verification/32_Single_Motor_Run_DISARM_S0_and_Encoder_Evidence_2026-09-30_ko.md)에서 완료 범위를 확인한다.
2. 전류·온도는 미측정이다. 저가 계측 구성은 정확도/판매품 확인이 부족해 구매 확정하지 않았다.
   현재10% 무부하의 작은 공급전류를 20A/50mV 션트+XL830L로 정밀하게 잴 수 있다고 단정하지 않는다.
3. [10/1 노트북·ESP 작업 계획](../plans/2026-10-01_Laptop_ESP_WiFi_PCB_and_Project_Review_Plan_ko.md)을 마련했다.
   먼저 ESP 단독 접속·HTTP 상태 표시, 이어서 STM TEL 통합과 무선 명령을 단계별로 검증한다.
   AP·공유기 STA·노트북 핫스폿 가능성을 모두 유지한다.
   `03_Firmware/esp32_wifi_link` scaffold와 [앱 입력 안내](../plans/2026-10-01_ESP_Standalone_WiFi_HTTP_Code_Guide_ko.md)를 준비했다.
   입력본 검토 뒤 사용자가 오타/누락을 수정하고 빌드·플래시했다. 10/1 AP HTTP 시험 뒤 10/2에는 개인 설정을 STA로 변경하고 사용자가 연결 완료를 보고했다. 현재 소스도 `WIFI_LINK_USE_AP=0`이며 HTTP 폴링을 사용한다.
   W1 접속·JSON 수신, W2 반복 갱신, W3 연결 해제 표시·재접속 자동 복구를 확인했다. 재플래시 뒤 boot_id는 바뀌며 같은 부팅의 해제·재접속에서는 유지된다.
   [AP 실측 결과](../progress/2026-10-01_progress.md#wi-fi-ap-실측--w1w2w3-결과)와 [STA 연결 보고](../progress/2026-10-02_progress.md#공유기-sta-연결-확인)를 구분한다. STA 접속 IP/로그는 미수집이며 STA 재접속·WebSocket·STM 통합·무선 명령과 새 PCB CAD는 미검증/미실행이다.
   [WebSocket 입력 안내](../plans/2026-10-02_ESP_Standalone_WebSocket_Code_Guide_ko.md)에 전체 코드·설정·함수 설명·WS-1~4 기준을 준비했다. 안내 코드의 브라우저 모의 검사 11개 PASS이며 실제 C 소스는 HTTP 폴링 상태다. 사용자는 `CONFIG_HTTPD_WS_SUPPORT=y` 활성화를 확인했다. 기초 예제 학습 후 사용자 입력 → 저장 파일 검토 → 사용자 빌드·플래시 → 실제 WS 검증으로 진행한다. 실제 STM TEL 통합(W4)과 무선 명령(W5)은 이후 별도로 진행한다. 비밀번호는 출력하지 않는다.
   PCB는 ADC/CAN 확장 회로와 인터페이스부터 설계한다. 10/2 전원 재점검과 STM TEL 통합·모터 시험은 별도 범위다.

10/2 점검 종료 뒤 전원 분리 완료는 **사용자 확인**이다. 재개 시 새 전원 연결/배선 변경이 있으면 그 상태를 기준으로 진행한다.

## 현재 실행 이미지와 코드

- 마지막으로 연결 완료가 보고된 ESP 앱은 `esp32_wifi_link`, HTTP 상태 페이지, STM 통합 없음이다. 10/1 AP는 COM5/115200 부팅 로그로 확인했다. 10/2 전원 점검 마감 뒤 STA 설정/USB COM4 사용으로 전환하고 사용자가 연결 완료를 보고했다. STA 로그는 미수집이며 UART bridge 복원 보고는 없다. 이후 예제 Hello World의 플래시·실행 로그는 미확인이다.
- 아래는 **9/30 로봇 시험용 `esp32_uart_bridge` 소스/마지막 실행 이력**이다. 현재 ESP에서 M2_RUN 앱이 실행 중이라는 뜻이 아니다. 로봇 시험 재개 전 대상 앱과 설정을 확인하고 사용자가 빌드·플래시한다.
- UART bridge: BRIDGE_M2_RUN_TEST_ENABLED=1U, 이전 자동 hook4개=0U.
- HELP: RESET_ESTOP, M2_RUN, STOP. M2 양수10%, 3초 제한, 500 ms STM watchdog, 100 ms CMD 재전송.
- CMD(50,+250,500)→left0/right100 permille. 3초 절대 종료 시각은 재전송으로 연장하지 않는다.
- TEL stale250 ms·응답200 ms·무회전500 ms 감시, DISARM 뒤600 ms 정지 관측.
- 부팅당1회, 성공/실패/STOP 뒤 잠금. 자동 ARM/구동 없음. all-hooks0 정상 이미지 복구는 미실행.
- 사용자가 M1→M2 전환만 이번 한 번 Codex 직접 수정을 허용했다. 이후 펌웨어는 기본 사용자 입력 방식.
- 마지막 계약 검사30 PASS/1 FAIL(default-off 검사, 수동 hook1U). 마감 중 소스 수정·빌드·플래시 없음.
- 현재 소스/캡처 해시는 [manifest](../../assets/logs/motor_output/2026-09-30_single_motor_run/manifest.json).
  소스 해시는 마감 작업본이며 각 시험의 바이너리 해시를 대신하지 않는다.

## 완료한 범위

| 항목 | 관측과 경계 |
| --- | --- |
| A 양수10%/300 ms | A 실제 전진 후 정지, B 정지. 이전 A 전진 관찰 공백 완료 |
| A active DISARM | 실제 전진/정지, UART frame end→마지막 PWM 하강364.44 μs. 기계 정지 시간이 아님 |
| A 물리 S0 | PC7 활성 이후 PWM 재발 없음, FAULT/ESTOP_ACTIVE·CPS0. 정밀 rail/기계 정지 시간·거리 미검증 |
| A 3초 | PWM2.99828925 s, 약19.059 kHz/10%; 원시1432 ticks=CPS 적분, B 정지 |
| B 3초 | PWM2.988788 s, 약19.040 kHz/10%; 원시1384 ticks=CPS 적분, A 정지 |
| 범위 | 두 모터 섀시 분리, 각각 단독. 주행·동시 구동·전류/열·폐루프 정속은 미검증 |

B의 구동 중 CPS 상승을 정속 PASS로 쓰지 않는다. A/B 3초 원시 전이에는 반대/동시2비트 전이가 없었다.
S0 시험의 마지막 엔코더 전이는 PC7 최초 HIGH 후127.32 ms이며 분해능 내 관측이다.
500 ms 안에 사람이 S0을 누르도록 한 절차는 짧았다는 사용자 지적을 반영했다. 다음 수동 개입 시험은 충분한 조작 시간을 둔다.
기존 T004 PASS·전체 T005A/T-MOTOR-003 PARTIAL, 정식 T-ESTOP-007 BLOCKED 유지.
기존 기준을 충족한 것으로 소급하지 않으며 관측 범위만 report32에 보존한다.

## 9/30 로봇 시험 연결 기준 — 10/2 전원 점검 조건은 당일 기록 참고

| 항목 | 기준 |
| --- | --- |
| 왼쪽 | A / M1 / JENC_1 / TIM3 PB4(A)·PB5(B) / left; Motor+→M1A, Motor−→M1B |
| 오른쪽 | B / M2 / JENC_2 / TIM5 PA0(A)·PA1(B) / right; Motor+→M2A, Motor−→M2B |
| STM 방향 정의 | 왼쪽 forward LOW/reverse HIGH 유지; **오른쪽 forward HIGH/reverse LOW로 보정 후 양방향 확인** |
| PWM / DIR | M1 PB6/PC8, M2 PB7/PC9 |
| 엔코더 | JENC Pin1~4=GND/B/A/AUX5V; 네 채널1kΩ 직렬+15kΩ 풀다운; TIM3 부호 반전/TIM5 유지;1560 counts/rev |
| 보드 배치 | STM은 만능기판 장착. ESP는 UART USB 간섭 때문에 기판 밖 |
| ESP 연장 / 콘솔 | GPIO17·18·GND만 대응 ESP 헤더로 연장. UART 표기 USB 하나로 공급·UART0 콘솔, 현재COM5/115200 |
| USB 전원 조건 | XL4015 #1 보드용2P 두 개 분리·절연, STM JP5=U5V/JP1=OPEN, #2 AUX5V와 공통GND |
| 전력단 | 두 버스바, MDD B+=K1 87/B−=GND16AWG, K1주선14AWG; Littelfuse F1/F2=10A/1A |

두 모터는 섀시에서 분리한 상태다. 교차 연결은 원래 A/M1·B/M2로 복원했다.
실제 ESP의 왼쪽 BOOT 표기=EN, 오른쪽 RESET 표기=GPIO0였으므로 보통 보드의 버튼 이름으로 재부팅을 단정하지 않는다.
도면·완료한 조정부 검사는 [report28](../verification/28_Encoder_Conditioning_Assembly_and_Electrical_Check_Report_2026-09-23_ko.md),
손회전 방향은 [report29](../verification/29_Vehicle_Side_Mapping_Correction_and_Hand_Rotation_Check_2026-09-26_ko.md)를 따른다.


## 남은 선택과 사용자 선호

- 전류/온도 구매 후보는 저가 구성의 정확도 문제를 확인해 조건부/보류로 정정했다. 구매·측정 없음.
- Wi-Fi·PCB·문서 이해를 이번 작업 대상으로 선택했다. ESP 단독 AP HTTP 실측과 STA 연결 사용자 확인은 완료했다. STA 재접속·WebSocket·STM 통합과 PCB CAD는 남아 있다.
- 무선 제어는 별도 입력/유효시간/연결 유실 검증이 필요하다. PC 명령 유실 시 과거 명령을 계속 재송신하지 않도록 설계.
- 기존 최상층 만능기판·납땜 부품 유지 선호. ADC/CAN 소형 PCB 설계 범위를 정리했으며 외곽/실측/제작 결정은 아직 미확정.
- 확장 PCB 후보는 회로/커넥터/실측이 확정된 부분부터. 전체 MCU 캐리어 교체와 모터 주전류 PCB 통합은 별도 후속 범위.
- 소스 입력·두 보드 빌드·플래시·물리 작업은 사용자. Codex는 설명·저장 파일 검토·Python 검사·문서 보조.
- 결과는 작업 마감 때 묶어 기록. 사용자 요청 없이 subagent/전체 대화 아카이브를 열지 않는다.

## 저장소

- branch agent/dual-encoder-bringup, HEAD69ca538. 이후 아키텍처47개·확장 검토·ESP 시험 코드·이번 증거/문서가 미커밋.
- 마지막 푸시 이후 새 commit/push는 이번 대화 마감에 포함되지 않았다. 기존 사용자 변경을 보존했다.
- 완료한 문서 개편과 과거 핀/전력 이력은 [9/30 기록](../progress/2026-09-30_progress.md), report25~31에 보존돼 있다.
