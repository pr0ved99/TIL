# Current Session Context

Last updated: **2026-10-24 통합 시연149초 제작·검증 완료 및 다섯 항목 마감**.

## 현재 MVP 재개점

- **완성본:** [통합 시연149초](../../assets/logs/wifi_link/2026-10-24_carpet_s0_demo_run01/edit/TMR_MVP_Final_2026-10-24.mp4). 기존65초 탁상 시연 전체 + 카펫 전진/선회 + 두 번째 S0·래치 유지·S2·STM reset·새 ARM·재주행을 같은 디자인으로 연결했다.1080p30/H.264/무음, 전체4470프레임 디코딩 오류0·21표본 검토·원본 보존/바탕화면 사본 해시 동일. [명세·한계](../../assets/logs/wifi_link/2026-10-24_carpet_s0_demo_run01/README.md).
- 새 두 영상은 화면=카메라+0.5초의 시연용 근사 정렬이다. 공통 시계가 없어 지연 계측·정확한 동기를 주장하지 않는다. 카펫100×150cm/1m 이상은 사용자 보고, 원시 TEL JSON 없음.145.6초 종료 화면은 DISARM3625 OK·IDLE/DISARMED·요청/PWM/CPS0·count239/4215. 리셋 전후 count를 합산하지 않는다. 최종 전원 분리·셀 전압은 미보고다.
- 사용자가 ESP 플래시 성공·새 UI 정상·배터리 단독을 확인했다. PAGE 밖/기존 제어 JS 보존과 PC105검사·Chrome4너비 검증은 저장되어 있다. 보드 이미지 readback과 새 UI 실시간 비용은 미확인. 이전 v5.2 앱최대0.6/0.6/0.8ms는 UI 수정 전 근거다.
- **완료:** v5.2 IDLE/속도0/전진 분석, 운용 문서, README 정보 요구사항 MVP-012, 대표 영상 제작. **유지:** 전체 MUST/T-DOC-001 미완료, T005A PARTIAL/T007 BLOCKED, 과거 통신/UI 원인OPEN. rail-off 제조사 검토는10/17 수행·후속 제외됐으므로 반복하지 않는다.
- 사용자 “영상까지 끝나면 정리”에 따라 문서·진행·해당 Git·기존 Calendar/Notion을 마감한다. 실제 게시 결과는 [오늘 마감](../progress/2026-10-24_progress.md)과 closeout 영수증을 따른다. 이전 전원 마감 영수증을 이번 게시 증거로 사용하지 않는다.
- **다음:** 영상은 바탕화면 `TMR_MVP_Final_2026-10-24.mp4`로 바로 재생할 수 있다. 추가 촬영·완료 시험 재실행 없이 새 대화에서 보류한 PCB 상세 검토 또는 후속 작업을 선택한다. 아래 PCB 재개점은 설계 후보 상태다.
- control200ms/TEL250ms/STM300ms, cap150/200‰·gain960/930·k1687/19500 유지. MCU 빌드·플래시/실물 조작은 사용자. 사용자 요청 없이 subagent 사용 금지.

## 보류한 노트북 PCB 작업

- **현재는3단계 첫 블록을 실제 회로와 함께 읽는 상세 검토다.** 사용자가 회로가 이미 구성되어 있으니 같이 자세하게 진행하자고 요청했다. 저장 회로도에서 새 netlist를 추출했고 현재10활성 연결은 이전 보고와 같았다. [읽기/명목 계산 기록](../../09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/reports/current_circuit_walkthrough.json), [회로 설명](../../09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/README.md#3단계-함께-검토--현재-회로의-전원과-왼쪽-ntc). 실제 CAD는 여전히 J1-16 STM_3V3가 J3/4 전류센서·R3/5 NTC를 공급하며 EXP LDO/CAN/전압2채널 없음. 현재 J3/4=1전원2GND3출력, J5/6=1NTC노드2GND로20번 계약 제안과 다르며 미적용을 구분한다. 첫 상세 설명은 J5/R3/R4/C3:25°C1.65V/이상2048, 실제RC소스6kΩ·0.6ms·약265Hz. 다음은 NTC도EXP 공급안(A)을 유지할지, NTC 여기만STM 측에 두는 추천 대안(B)을 비교하고 ADC 보호/net수정을 결정한다. B는0.33mA 명목/단락0.66mA 규모지만 VDDA 경로 확인·기존 전원 계약 변경 전에는 채택하지 않는다. 문서만 늘리거나 CAD를 먼저 바꾸지 말고 실제 부품/선 하나씩 설명한다. MCU/실물·CAD/BOM 변경 없음.

- 사용자가 밖에서 노트북만 가진 동안 PCB 설계를 진행하기로 결정했다. [TMR Monitor Shield RevA](../../09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/README.md)에 전류2·온도2채널 독립 회로도와 부품22개 초기 배치를 만들었다. 설치 KiCad Morpho 템플릿의 헤더 좌표·외곽을 출발점으로 쓰며 모든 부품·기구 적합성은 아직 후보이다.
- 사용자가 전체 기능과 기존 IMU 배치를 재확인했다. **현재 CAD는 센서 부분 초안이며 CAN·K1 전단/후단 전압2채널이 빠져 있다.** 전체 주요 검토 범위는 ADC6채널(전류2·온도2·전압2)+CAN이다. IMU는 기존 만능기판 위치·PB8/PB9·PB1/PC4 배선을 유지하며 새 PCB에 중복 실장하지 않는다. LiDAR는 모델·전원/데이터 인터페이스 미정이므로 전원/하네스 조건을 관리하고 부품은 임의 확정하지 않는다.
- ERC0·회로도/PCB 불일치0, 미배선32개는 기존 센서 부분의 결과다. 입력 보호/역급전·전체 전원 여유·ADC 조건·소켓 높이/간섭은 미확정이다. 제작용 파일이나 실물 검사 결과가 아니다. 핀·전원·커넥터 계약은 현재2단계의 후속 작업이고 회로 추가는3단계 이후다. 이번 블록도 작성으로 CAD·BOM은 변경하지 않았다.
- 저녁 이후 집에서 기존 MVP 작업을 재개한다. 쉴드·온도/전류 ADC 완성을 MVP 선행으로 추가하지 않는다. 이번 노트북 작업의 Git/Calendar/Notion 게시는 아직 수행하지 않았으며 아래 게시 내역은 직전 마감 기록이다.

## 이전 전원 조정 회차 참고

- 전원 재설정 후 두 보드 연결 전압5.02V, 로봇 최종 실측 중량3.25kg(사용자 보고). 새 로그153.124초/전·후진·좌우회전16개 비영 명령 구간에서 집중·버튼 유지 중 지연성 DISARM0건, TEL 최대126.3ms(비영 명령120ms), 제어 상태 최대80.1ms다. 이전 전진/좌회전 정지 근처 TEL287.9/219.2ms보다 긴 공백이 줄었지만 재부팅도 동반되어 전압 인과관계는 OPEN이다.
- [비교 보고서](../../assets/logs/wifi_link/2026-10-23_power_adjusted_drive_run01/comparison_ko.md)와 [비교 JSON](../../assets/logs/wifi_link/2026-10-23_power_adjusted_drive_run01/comparison.json)을 먼저 읽는다. TEL2553개/153.124초, 제어·송신 이력114.752초(초반history3600개 삭제). 전진6·후진3·좌회전3·우회전4 구간이다. 물리 이동시간/거리 인수 회차로 확대하지 않는다.
- 이전 전원 조정 회차는 boot2737441136/session2. DISARM1710/seq770061694 OK, IDLE·DISARMED/DISARM·요청/PWM/CPS0, count31912/37642 고정2.9초였다. 해당 마지막 정지는 motion=null인 window blur 경로다. 재접속/trace error0, drop/err0. 이번 귀가 후 최신 회차와 소급 혼합하지 않는다.
- 전원 기록: 조정 전 무부하5.03V/보드 연결4.96V; 목표5.10V 제시 후 최종 보드 연결5.02V. 최종 실제 무부하 값은 미보고다. USB 저항 부하에서 USB4.85~4.87V/0.93A·XL OUT5.00V·제공된 배치도 기준 CC LED꺼짐. 정확한 전류 제한A/순간 파형·두 보드 각각의 입력/3.3V는 미확인이다. 모터 전류/열적 적합성 검증이 아니다.
- 중량 최종3.25kg은 사용자 실측 보고이며 앞선3.2/3.1kg을 대체한다. 저울/불확도·구성품별 내역은 미보고다. 과거 회차에 소급 배정하지 않는다.

## 보존할 재개 조건과 이전 미결

- **밖/노트북:** 채택한 ESP–STM CAN 구성에서 현재 CAD의 J5/R3/R4/C3부터 함께 읽는3단계 상세 검토다. 다음은 NTC EXP/STM 공급안과 ADC 보호를 비교해 실제 수정할 net을 정한다. 기존 IMU 자리를 유지한다. **집/MVP:** 아래 통신 미결·최종 인수 범위를 이어간다. 사용자는 귀가 시각을 지정하지 않았으므로 임의 일정 시간을 만들지 않는다.

- 귀가 후 잔여 인수 대조는 보고서39, 전달 경로/관측 설계는 보고서40에 완료했다. v5.2 구현·PC 검증과 실제 브라우저3조건 관측을10/24 완료했다. 추가 반복 없이 상단의 기존 인수 경계로 복귀한다. 기존200/250/300ms 제한과 완료91 PC 감사·거리/단절 시험 자동 반복 금지를 유지한다.
- 이전 [전진 자동 정지](../../assets/logs/wifi_link/2026-10-23_forward_auto_disarm_run01/observations.json) TEL나이265.2≥250ms, [좌회전 자동 정지](../../assets/logs/wifi_link/2026-10-23_left_auto_disarm_run01/observations.json) control나이204.9≥200ms 및 실제 PAGE PC 재현 PASS를 보존한다. 이전 좌회전 누적 로그는 전진 사건도 포함해 독립 통계로 합산하지 않는다.
- 개선 원인을 전압으로 확정하지 않는다. 재부팅/연결 초기화 동반·Wi-Fi/노트북 조건 미통제·순간전압/brownout 계측 없음. 평소 TEL p95는 전후약90ms로 비슷하다. 장비가 필요한 새 관측은 필요성을 먼저 정리하며 MCU 입력·빌드/플래시와 물리 조작은 사용자 수행이다.

## 완료 범위와 남은 판단

- 지상1m `MVP-011 / REQ-ODO-001 / T-ODO-001` PASS는 거리/오차 기록 범위, ST-MVP-03/TK-MVP-03-05 완료다. run03/04 실측1002mm·평균1002.640333/1000.953333mm. 정밀도·직진성·자동1m 정지 보증이 아니다. run01 개략 기준선, run02 종료 ACK/연속 기록 누락 REJECTED 유지.
- 리포 알람: 과거 주행 중 설정값 아래 셀 전압에서 경고음→수동 전원 차단을10/23 사용자 확인했다. REQ-POWER-004/T-PWR-004 PASS — USER-REPORTED 감독하 운영 범위. 당시 전압·시간 미보고,10/20 BX100설정3.40V와 소급 동일시하지 않는다. 반복 저전압 시험을 요구하지 않는다.
- 전체 MUST/최종 MVP는 미완료다. UART전체 release·전원 전체 수용·엔코더 신호·물리 E-stop 정식 수용 경계는 [검증표](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)를 따른다.10/17 사용자 제외한 정격/도면 재검토를 재개하거나 모든 PARTIAL을 새 물리 숙제로 만들지 않는다.
- run02 수동 DISARM 여러 번 뒤 버튼 활성 보고의 원인은 별개 OPEN이다. v5는 설치 당시 소켓만 구독해 이후 응답을 놓쳤다. v5.1은 재접속/실제 send/클릭/focus loss를 기록한다. PC7검사와 정지 상태/run03/04 정상 수동 클릭 경로 확인을 이전 문제 해결로 확대하지 않는다.
- [DISARM PC 감사](../../assets/logs/wifi_link/2026-10-23_disarm_code_audit/review.json) 추가24+기존67 PASS. 이는 실제 연속 통신 신뢰성 보장이 아니다. 같은 감사·완료한 단절/복구·공중5/10/15cm·로컬 이미지 감사를 자동 반복하지 않는다.20cm는 사용자 요청 미실시로 유지한다.
- 기존 MG540 유지. `MVP-015 / REQ-THERM-001 / T-LOAD-001 / ST-MVP-04` 온도는 DEFERRED/NOT_RUN. 전류/ADC도 후속이며 장비 배송·열 기준을 MVP 선행으로 복원하지 않는다. 장시간/정격·열적 적합성을 주장하지 않는다.

## 고정 구성과 후속

- NUCLEO-F446RE + ESP32-S3 DevKitC + MDD10A. A=왼쪽/M1/JENC1/TIM3 inverted, B=오른쪽/M2/JENC2/TIM5 normal. UART STM PA9→ESP GPIO18, ESP GPIO17→STM PA10,공통GND,115200/8N1.
- 일반 cap150‰·순수 회전200‰·왼쪽gain전진960‰/후진930‰. 요청100mm/s→PWM144/150‰이며 실측 속도가 아니다. ESP ZERO_ONLY0·시험mode0, STM hook0 유지.
- 실물14톱니·대표피치9.64mm·1560counts/output rev, 초기 공통k=1687/19500mm/count, 지상 보정 아님. 궤도 중심 간격 실측약233mm/CAD228.31681mm; 유효 skid-steer 폭은 미보정이다.
- STM최종 출력/300ms timeout, browser CMD80ms·control200ms/TEL250ms, WS TEL50ms 유지. signed64 count문자열·sample/ARM metadata 보존. 새 MCU 변경/빌드/플래시 없음. 현재 로컬 PAGE hash는 이전과 같으며 보드 runtime hash readback의 새 증거는 아니다.
- 마지막 구매/수령 보고:103JT-025×2·Pololu5241×2·GM1312·UT210E 배송 대기, Vishay100nF10개 구매/수령미확인,10k/1k/12k저항보유. 후속4채널/NTC/쉴드 계획 유지. CANableV2Pro·MCU-230보유, 통신미검증. ADS1115/PSU/탑재컴퓨터 추가 구매를 요구하지 않는다. MVP후 첫 기본 검증은 IMU다.

## 정리 규칙과 게시

- **“정리”는 문서화·진행상황·Git·Calendar·Notion 다섯 항목 전체를 뜻한다.** 이번 사용자 명시를 루트/프로젝트 AGENTS와 [workflow](CODEX_CONTEXT_WORKFLOW.md)에 반영했다. 별도 수행 여부를 다시 묻지 않는다.
- [현재 진행 기록](../progress/2026-10-24_progress.md), [다음 대화 프롬프트](NEXT_SESSION_START_PROMPT.md), branch `agent/dual-encoder-bringup`. 직전 전원 조정 마감에서는28파일을b81034a로commit/push·원격일치 확인했고 Notion4페이지/Calendar7일정을 재조회했다. 그 게시 영수증은 `assets/logs/wifi_link/2026-10-23_power_adjusted_closeout/`이며 이번 귀가 후/노트북 작업의 추가 게시 증거가 아니다. 이전1차 마감66b321f/c27c250와도 구분한다.
- HelloWorld build·LA Session2·과거 source_snapshot·10/18 monitorlogs의 별도 변경17개를 보존한다. 전체 일괄 stage하지 않는다. 서브에이전트는 사용자 요청 없이 사용하지 않는다.
