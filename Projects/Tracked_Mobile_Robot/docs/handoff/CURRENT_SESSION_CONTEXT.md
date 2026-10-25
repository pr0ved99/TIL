# Current Session Context

Last updated: **2026-10-26 — 10/25 학습 회차·3-1~3-4 자료 마감**.

## 현재 재개점 — 모니터링 입력 설계

- **사용자 요청:** “3-X 학습노트를 전부 만들어놓은 다음 정리”. [학습 목차](../../07_Embedded_Learning_Notes/01_Concept_Notes/README.md)에 3-1~3-4 네 편(15~18번)을 작성했다. 12~14번 수집·평균·PWM·오차 예산·후보 판단도 함께 마감한다. 모든 숫자 예시는 명목 계산/가상 예시로 구분했다.
- **복습 자료:** [16절 학습 노트](../../07_Embedded_Learning_Notes/01_Concept_Notes/11_Monitoring_ADC_Requirements_RC_and_Sampling_ko.md), [Notion 비공개 학습 노트](https://app.notion.com/p/403a7326f87b816f8115fbe2c995f8f0). 식의 목적·값의 출처·단위·예시·가정을 생략하지 않는다. 문서 작성으로 사용자의 이해도나 설계 승인 여부를 추정하지 않는다.
- **목표/진행:** 신뢰할 수 있는 모니터링 입력 설계. 2장은 2-6, 3장은 3-4에서 끝낸다. 시험 범위·합격/보류·보정 독립점·PWM/시간·유효성·MON-L01~08 시험표를 작성했으며 실제 시험은 NOT_RUN이다. 요구 채택·입력계 예산·장비/연결 조건·부품 확정은 남았다.
- **다음 한 묶음:** [3-1 검증 대상과 합격 기준](../../07_Embedded_Learning_Notes/01_Concept_Notes/15_Verification_Targets_and_Acceptance_ko.md)부터 사용자와 함께 읽는다. 자료 작성으로 사용자 학습 완료를 추정하지 않는다. 미정 기준을 검토한 뒤 실행 가능한 시험 한 그룹을 정하며 지금 실물 조작/새 시험을 자동 시작하지 않는다.
- **NTC 결론:** R3/NTC 분압, 공통 여기/기준 전압의 비율 상쇄, R4+(R3||NTC) 필터를 설명했다. NTC STM 공급 B안과 10k/1k/100nF는 추천 후보다. PC2 FT의 무전원 도통을 일반 다이오드 그림으로 확정하지 않는다. R4는 전류 제한·필터의 일부이며 역급전 차단 보증이 아니다. C3의 NTC 쪽 방전 경로와 ADC 쪽 국소 경로를 구분한다.
- **수집 후보:** 채널별100Hz·100ms 블록10개 평균은 첫 DC 비교 조건 제안,1kHz와 비교한다. 최종 운용 설정이 아니다. 2-5 예산 배분도 설명용 미채택이다. PWM/alias·보정 후 정확도·전체 응답은 미검증이다.
- **전류 결론:** #5241 nonratiometric, 44mV/A. 12k/100nF 이상 모델은 fc132.63Hz·1% 잔차5.53ms·19kHz 진폭비0.00698. 누설1µA 한계 모델은 12mV/0.273A이지만 실측·보정 후 오차가 아니다. 이 때문에 필터 성능만으로 부품을 확정하지 않는다.
- **ADC 결론:** [계산 JSON](../../09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/reports/current_adc_acquisition.json). 외부 C 없는 모델의 0.25LSB 유효 획득1.23086µs와 외부100nF의 단일 전하 공유0.230984mV/0.2867LSB·회복τ1.2ms는 별개 모델이다. 14MHz/480cycles는 후보, 6채널210.86µs는 트리거/소프트웨어 제외 계산이다. 긴 획득 시간으로 DC 누설 오차를 없앨 수 없다.
- **CAD/범위:** [쉴드 README](../../09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/README.md). 현재 22부품·미배선32개, 전류2/온도2만 있다. 실제 J1-16 STM_3V3 공통 공급, J3/4=1전원2GND3출력, J5/6=1NTC노드2GND. 전체 목표 ADC6+CAN과 별도 EXP 공급/커넥터 계약은 미적용 부분이 있다. CAN·전압2·LDO·보호 설계/기구 적합성 미완료, 제작용 아님.
- **작업 경계:** CAD/BOM·펌웨어·MCU 빌드/플래시·실물 조작 없음. 사용자는 기존 진행 순서 유지와 공간 검토 후속을 지정했다. IMU 기존 위치/배선을 유지하며 쉴드 완성을 MVP 선행으로 추가하지 않는다. MCU 코드 입력·빌드/플래시/실물은 사용자, subagent는 명시 요청 없이 사용하지 않는다.
- **마감 근거:** [이번 10/26 마감](../progress/2026-10-26_progress.md), [10/25 학습 이력](../progress/2026-10-25_progress.md), [이번 게시·검사 영수증](../../assets/logs/pcb_design/2026-10-25_chapter3_closeout/publication.json). 과거 미게시 문구와 이전 영수증은 당시 이력이다.

## 완료한 MVP 시연과 유지할 판정

- **완성본:** [통합 시연149초](../../assets/videos/wifi_mvp/2026-10-24/final/TMR_MVP_Final_2026-10-24.mp4). 기존65초 탁상 시연 전체 + 카펫 전진/선회 + 두 번째 S0·래치 유지·S2·STM reset·새 ARM·재주행을 같은 디자인으로 연결했다.1080p30/H.264/무음, 전체4470프레임 디코딩 오류0·21표본 검토·원본 보존/바탕화면 사본 해시 동일. [명세·한계](../../assets/logs/wifi_link/2026-10-24_carpet_s0_demo_run01/README.md).
- 카펫 동기 수정 완료: 새 두 영상은 화면=카메라−0.7667초이며 기존 편집보다 화면을1.2667초 늦췄다. 원본9구간18전이·출력5구간10전이 대조, 출력 표본 잔차 최대약0.133초다. 공통 시계가 없어 지연 계측·정확한 동기를 주장하지 않는다. 카펫100×150cm/1m 이상은 사용자 보고, 원시 TEL JSON 없음.145.6초 종료 화면은 DISARM3625 OK·IDLE/DISARMED·요청/PWM/CPS0·count239/4215. 리셋 전후 count를 합산하지 않는다. 최종 전원 분리·셀 전압은 미보고다.
- 사용자가 ESP 플래시 성공·새 UI 정상·배터리 단독을 확인했다. PAGE 밖/기존 제어 JS 보존과 PC105검사·Chrome4너비 검증은 저장되어 있다. 보드 이미지 readback과 새 UI 실시간 비용은 미확인. 이전 v5.2 앱최대0.6/0.6/0.8ms는 UI 수정 전 근거다.
- **완료:** v5.2 IDLE/속도0/전진 분석, 운용 문서, README 정보 요구사항 MVP-012, 대표 영상 제작. **유지:** 전체 MUST/T-DOC-001 미완료, T005A PARTIAL/T007 BLOCKED, 과거 통신/UI 원인OPEN. rail-off 제조사 검토는10/17 수행·후속 제외됐으므로 반복하지 않는다.
- 사용자 “영상까지 끝나면 정리”에 따라 문서·진행·해당 Git·기존 Calendar3일정/Notion2페이지를 마감했다. 영상·관련194파일 커밋9bc2499의 원격 일치와 외부 재조회를 확인했다. 실제 게시 결과는 [오늘 마감](../progress/2026-10-24_progress.md)과 closeout 영수증을 따른다. 이전 전원 마감 영수증을 이번 게시 증거로 사용하지 않는다.
- control200ms/TEL250ms/STM300ms, cap150/200‰·gain960/930·k1687/19500 유지. MCU 빌드·플래시/실물 조작은 사용자. 사용자 요청 없이 subagent 사용 금지.

## 이전 전원 조정 회차 참고

- 전원 재설정 후 두 보드 연결 전압5.02V, 로봇 최종 실측 중량3.25kg(사용자 보고). 새 로그153.124초/전·후진·좌우회전16개 비영 명령 구간에서 집중·버튼 유지 중 지연성 DISARM0건, TEL 최대126.3ms(비영 명령120ms), 제어 상태 최대80.1ms다. 이전 전진/좌회전 정지 근처 TEL287.9/219.2ms보다 긴 공백이 줄었지만 재부팅도 동반되어 전압 인과관계는 OPEN이다.
- [비교 보고서](../../assets/logs/wifi_link/2026-10-23_power_adjusted_drive_run01/comparison_ko.md)와 [비교 JSON](../../assets/logs/wifi_link/2026-10-23_power_adjusted_drive_run01/comparison.json)을 먼저 읽는다. TEL2553개/153.124초, 제어·송신 이력114.752초(초반history3600개 삭제). 전진6·후진3·좌회전3·우회전4 구간이다. 물리 이동시간/거리 인수 회차로 확대하지 않는다.
- 이전 전원 조정 회차는 boot2737441136/session2. DISARM1710/seq770061694 OK, IDLE·DISARMED/DISARM·요청/PWM/CPS0, count31912/37642 고정2.9초였다. 해당 마지막 정지는 motion=null인 window blur 경로다. 재접속/trace error0, drop/err0. 이번 귀가 후 최신 회차와 소급 혼합하지 않는다.
- 전원 기록: 조정 전 무부하5.03V/보드 연결4.96V; 목표5.10V 제시 후 최종 보드 연결5.02V. 최종 실제 무부하 값은 미보고다. USB 저항 부하에서 USB4.85~4.87V/0.93A·XL OUT5.00V·제공된 배치도 기준 CC LED꺼짐. 정확한 전류 제한A/순간 파형·두 보드 각각의 입력/3.3V는 미확인이다. 모터 전류/열적 적합성 검증이 아니다.
- 중량 최종3.25kg은 사용자 실측 보고이며 앞선3.2/3.1kg을 대체한다. 저울/불확도·구성품별 내역은 미보고다. 과거 회차에 소급 배정하지 않는다.

## 보존할 재개 조건과 이전 미결

- **노트북 재개:** 상단의 3-1 학습 노트 검토부터 진행한다. **집/MVP:** 기존 인수 판정과 사용자 제외 범위를 유지하며 새 물리 작업 시각은 추정하지 않는다.

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
- [현재 마감 기록](../progress/2026-10-25_progress.md), [다음 대화 프롬프트](NEXT_SESSION_START_PROMPT.md), branch `agent/dual-encoder-bringup`. 직전 전원 조정 마감에서는28파일을b81034a로commit/push·원격일치 확인했고 Notion4페이지/Calendar7일정을 재조회했다. 그 게시 영수증은 `assets/logs/wifi_link/2026-10-23_power_adjusted_closeout/`이며 이번 귀가 후/노트북 작업의 추가 게시 증거가 아니다. 이전1차 마감66b321f/c27c250와도 구분한다.
- HelloWorld build·LA Session2·과거 source_snapshot·10/18 monitorlogs의 별도 변경17개를 보존한다. 전체 일괄 stage하지 않는다. 서브에이전트는 사용자 요청 없이 사용하지 않는다.
