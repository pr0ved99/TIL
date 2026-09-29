# Current Session Context

Last updated: 2026-09-30 — 진행 기록 요약·공통 형식·최신 위치 정리로 문서 개편 4단계 마감.

## 바로 이어갈 작업

**현재 사용자는 노트북만 있으며, 합의한 문서 개편 4단계를 마쳤다. 새 물리 시험은 없다.**
1단계로 [최종 MVP 검증 매트릭스](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)를 최신 보고서 25~31과 대조해 정리했다.
2단계로 [전체 실행 계획](../plans/00_Project_Master_Plan_To_Final_MVP_ko.md)의 현재 단계·남은 작업·완료 조건을 정리했다.
3단계로 [프로젝트 README](../../README.md)의 대표 성과 요약·현재 상태·근거 링크와 빌드 진입점을 정리했다.
4단계로 [진행 기록 작성 방법·템플릿](../progress/README.md#공통-템플릿)과 [9/30 기록](../progress/2026-09-30_progress.md)을 작성하고 9/29에 당시 요약만 추가했다.
향후 기록은 목표·기준점·결과·결정·다음 행동을 앞에 두고 상세 관측·이력은 보존한다. 이번 문서 개편의 필수 작업은 마감했다.
로컬 README의 기존 개요·사진·설계 판단·대표 사례·문서 안내 구조를 유지했다. 문서 개편 후 사용자가 Git 최신화를 요청했으며, 저장 대상은 현재 작업 브랜치 agent/dual-encoder-bringup이다.
대표 성과는 표로 요약하고 기존 방법·한계 설명을 접기 영역에 보존했다. 실제 보드 전원과 T004/T005A의 검증 범위를 분리했다.

검증 매트릭스는 현재 현황·요구사항 표를 앞에 두고 기존 측정·판정 이력을 뒤의 접기 영역에 보존했다.
MVP-005/006은 단일 모터 구동 근거로 PLANNED→PARTIAL, REQ-ESTOP-009는 감지/PWM·rail DMM 증거를 반영해 BLOCKED→PARTIAL로 정리했다.
구동 중 S0 정지(T-ESTOP-007)는 여전히 BLOCKED이고 전체 T005A도 PARTIAL이다. 새로운 물리 시험·PASS를 추가한 것은 아니다.
전체 실행 계획은 최신 단계 표·작업별 완료 조건을 앞에 두고 상세 Gate와 과거 시간·측정 이력을 접기 영역에 보존했다.
G0는 기존 매트릭스의 물리 E-stop MVP-013을 범위에 포함시켰다. 단일 모터·전력단·주행의 수용 기준을 완화하지 않았다.
총 잔여시간은 미산정이며 과거 26~52시간을 오늘의 예상 시간으로 사용하지 않는다.

**하드웨어 재개 지점은 A/M1 양수 명령의 실제 전진 방향 확인이다.**
앞선 복습 자료는 [STM·ESP 코드 구조와 함수 지도](../../07_Embedded_Learning_Notes/01_Concept_Notes/09_STM32_ESP32_Source_Structure_and_Function_Map_ko.md) →
[단일 모터 시험 해설](../../07_Embedded_Learning_Notes/01_Concept_Notes/08_Single_Motor_Bench_Dataflow_and_Evidence_Review_ko.md) 순서다.
사용자는 코드 구조와 스스로 목표·역할·인터페이스·작업 순서·통과 기준을 잡는 방법을 복습했다. 이해 완료로 판정하지 않는다.

ESP 소스는 `03_Firmware/esp32_uart_bridge/main/uart_bridge_main.c`로 이름을 변경했다.
기존 hello_world_main.c와 내용·SHA-256이 같고 app_main()과 시험 설정도 유지했다.
CMake·Python 검사 경로·문서 링크를 갱신했다. 과거 증거 manifest의 경로·해시는 당시 기록으로 보존한다.

문서 마감은 [9/30 진행 기록](../progress/2026-09-30_progress.md)에 있다.
장비 재개 시 [9/29 모터 시험 기록](../progress/2026-09-29_progress.md)과
[휴식 후 계획](../plans/2026-09-29_Next_Session_M1_Direction_and_Bench_Closeout_ko.md)에서 해당 조건을 확인한다.
세부 증거는 [report31](../verification/31_Single_Motor_Pulse_Cross_Test_and_Right_DIR_Correction_2026-09-29_ko.md)과
[원본12개](../../assets/logs/motor_output/2026-09-29_single_motor_bench/README.md)에 있다.

- ESP 수동 콘솔은 완성·사용자 빌드/플래시·실제 구동까지 진행했다. 9/27 빈 함수/오타 WIP를 다시 시작하지 않는다.
- 현재 ESP는 **M2 역방향10%/300ms 시험 이미지**다. M2_PULSE → CMD(-50,-250,300), 기대PWM0/−100.
  BRIDGE_M2_PULSE_TEST_ENABLED=1U, 기존 자동 hook 네 개=0U.
- 성공·실패·STOP 뒤 BENCH_FINISHED로 잠기며 RESET_ESTOP도 거부한다.
  새 시도는 ESP 재부팅이 필요하다. STM의 ESTOP latch와 별개다.
- 다음 M1 양수 시험은 코드/HELP/검사 조건을 사용자 입력으로 바꾼 뒤 사용자 ESP 빌드·플래시를 해야 한다.
  현재 이미지로 M1_PULSE를 보내거나 M2_PULSE를 M1 시험으로 간주하지 않는다.
- 재개 준비의 부팅~READY/안정 TEL 로그에서err 기준과 증가 여부도 남긴다.
  마지막 정방향err=0, 역방향err=1439는 각각 일정했고 첨부 사이 증가 원인은 미확정이다.

## 완료한 범위

| 항목 | 확인 결과 |
| --- | --- |
| A/M1 +5%/300ms | 소리·떨림만, CPS0. 실제 회전 달성 안 됨 |
| A/M1 ±10%/300ms | 회전·CPS 부호·timeout 후0 복귀. +명령의 실제 전진 방향은 사용자가 보지 못함 |
| 교차시험 | A를M2에서, B를M1에서 구동 확인. 이때 엔코더도 각 교차 입력 채널로 관측 |
| B/M2 최초 | 소리만 있고 회전 없음. 원래 연결 복원 뒤 회전하여 재현 안 됨; 원인은 미확정 |
| B/M2 DIR 보정 후 +10% | 실제 전진 후 정지·A 무동작, right_cps 양수→0 유지8.9초 |
| B/M2 DIR 보정 후 −10% | 실제 역회전·A 무동작, right_cps 음수→0 유지4.1초;49TEL/4.8초 |
| 검사 | 정적31개 중30 PASS, 시험hook=0 요구1개 FAIL(현재1U). 공백 검사 PASS |

종료 부근의 소수 반대 부호CPS 샘플은 report31에 보존했다. 원인을 역회전/노이즈로 단정하지 않는다.
100ms TEL로 정확한 PWM 차단 지연이나 물리 정지 시간을 주장하지 않는다.
B 양방향 확인을 A 전진 방향, 부하·주행·전체 물리 E-stop PASS로 확대하지 않는다.

## 현재 연결과 코드

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

## 마감 상태와 경계

- 최종 로그는 DISARMED/DISARM, PWM/CPS0이며 ESP는1회 시험 잠금 상태다.
- S0 잠금/S1 OFF/LiPo·두 보드 USB 분리를 안내했다. **최종 전원 분리 완료 응답은 아직 없다.**
- 수동 시험1U를 유지했으며 all-hooks0 safe/default 이미지 복구는 하지 않았다.
- T004 기존 PASS, 전체 T005A PARTIAL 유지. 직접 rail 수용 기준·구동 중 S0 차단·부하/전류/노이즈·기구/주행은 별도다.
  과거 전압·배터리·S1 순간CPS 결과는 [report30](../verification/30_Actual_Encoder_and_Power_Bench_Closeout_2026-09-27_ko.md)에 보존한다.
- 소스는 사용자 입력, STM/ESP 빌드·플래시와 물리 작업도 사용자 수행. Codex는 실제 파일 검토·설명·Python 검사·문서화.
- 완료 검사는 변경·실패 없이 반복하지 않는다. progress는 마감 때 묶어서 갱신한다.
  사용자 요청 없이 subagent나 전체 과거 대화 아카이브를 사용하지 않는다.
- 저장소 C:/Users/eyh12/workspace/TIL, 브랜치 agent/dual-encoder-bringup.
  9/30 사용자 요청으로 64d51ad 이후 수동 콘솔·오른쪽 DIR 보정·소스 이름 변경·시험 증거·문서 개편을 마감 커밋에 포함한다.
  원격 대상은 origin/agent/dual-encoder-bringup이며 main 병합은 범위에 포함하지 않는다. 재개 시 git status와 최신 커밋으로 동기화 상태를 확인한다.
  Git 마감 전 Python 검사를 다시 실행해 30 PASS/1 FAIL을 확인했다. 기존 M2 시험 hook=1U에 따른 실패이며 설정은 유지했다.
