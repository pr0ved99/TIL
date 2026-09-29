# 진행 기록

이 폴더에는 날짜별 수행 내용·관측·결정·다음 행동을 남긴다. 문서 상단의 **한눈에 보기**로 재개 지점을 파악하고, 필요할 때 상세 기록과 원본 증거를 읽는다.
날짜가 지난 기록의 ‘현재’와 ‘다음’은 당시 상태다. 프로젝트 최신 상태는 [현재 인수인계](../handoff/CURRENT_SESSION_CONTEXT.md), 판정과 증거는 [검증 매트릭스](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)에서 확인한다.

## 최신 기록

**[2026-09-30 진행 기록](2026-09-30_progress.md)** — 날짜별 요약·공통 템플릿과 인수인계를 정리해 문서 개편 4단계를 마감했다.
[전체 실행 계획](../plans/00_Project_Master_Plan_To_Final_MVP_ko.md)과 [프로젝트 README](../../README.md)의 개편 결과를 유지하며, 새 물리 시험은 하지 않았다.

마지막 모터 시험은 [9/28 기록](2026-09-28_progress.md)·[9/29 기록](2026-09-29_progress.md)·[report 31](../verification/31_Single_Motor_Pulse_Cross_Test_and_Right_DIR_Correction_2026-09-29_ko.md)에 있다.
ESP 수동 콘솔은 완성·실행됐고 마지막 이미지는 M2 역방향 10%/300 ms 시험 hook=1U다. 장비 재개 목표는 A/M1 실제 전진 방향 확인이며, [휴식 후 계획](../plans/2026-09-29_Next_Session_M1_Direction_and_Bench_Closeout_ko.md)을 따른다.
현재는 노트북만 있는 상태로, 장비의 전원 분리 완료를 새로 확인한 것은 아니다.

기존 측정·연결 기준도 다음 문서에 보존한다.

- [report 29](../verification/29_Vehicle_Side_Mapping_Correction_and_Hand_Rotation_Check_2026-09-26_ko.md): A=left/M1/TIM3, B=right/M2/TIM5.
- [report 30](../verification/30_Actual_Encoder_and_Power_Bench_Closeout_2026-09-27_ko.md): 입력 전압·손회전·warm reset 169 TEL, S1 전환 순간 CPS ±10 후 즉시 0 복귀. T004 기존 PASS·전체 T005A PARTIAL 유지.
- [9/8 진행 기록](2026-09-08_progress.md)·[report 25](../verification/25_XL4015_Logic_Power_and_Physical_EStop_Conditioned_Sense_Test_Report_2026-09-08_ko.md): 보드 전원 공급 기준. 9/5 K2/K1 control-only 결과를 전체 Physical E-stop PASS로 확대하지 않는다.

## 작성 방법

1. 아래 템플릿을 복사해 `YYYY-MM-DD_progress.md`를 만들고, 첫 요약의 다섯 항목을 짧게 채운다.
2. 같은 날짜의 다른 작업 묶음은 상세 기록에 추가한다. 기존 측정·결정 이력을 보존하고 상단에는 그날의 마감 상태를 요약한다.
3. 하드웨어 시험 중에는 결과를 모아 작업 묶음 마감 때 기록한다. 사용자의 즉시 문서화 요청이나 잘못된 현재 지시를 바로잡아야 할 때는 그 시점에 갱신한다.
4. 작업일과 문서화일이 다르면 둘 다 적는다. 과거 기록에 나중에 요약을 추가하면 추가 날짜를 밝히고 당시 판정을 바꾸지 않는다.
5. 기준점에는 확인한 커밋·미커밋 상태와 시험 설정을 적는다. 소스 해시·바이너리·배선·전압이 미기록이면 추정해서 채우지 않는다.
6. 코드 검사·빌드·보드 동작·전기적 계측·사용자 보고의 범위를 구분한다. 문서만 정리한 날은 해당 사실을 명시한다.
7. 요약과 상세에 같은 긴 로그를 복제하지 않고 원본 보고서·파일에 연결한다. 다음 행동은 1~3개와 완료 조건으로 제한한다.
8. 사용하지 않은 템플릿 항목은 삭제하거나 ‘해당 없음/미실행/미기록’으로 표시한다. 이전 날짜 전체를 일괄 재작성할 필요는 없다.
9. 기록을 마감하면 아래 색인과 현재 인수인계의 최신 위치를 갱신한다. 계획은 실행 계획에, 최신 판정은 검증 매트릭스에 반영한다.

## 공통 템플릿

문서 작업과 보드 시험에 같은 첫 요약을 사용한다. 아래는 작성 틀이며 실제 결과가 아니다.

```md
# YYYY-MM-DD 진행 기록

## 한눈에 보기

| 항목 | 내용 |
| --- | --- |
| 목표 | 오늘 확인하거나 정리할 대상과 관련 요구사항·Test ID(해당할 때) |
| 작업·시험 기준점 | 마지막 커밋과 미커밋 여부, 사용한 소스/문서. 하드웨어 시험이면 보드·배선·전원·시험 설정도 기록 |
| 결과 | 완료·부분 완료·미실행을 범위와 함께 요약. 실제 관측과 사용자 보고를 구분 |
| 결정과 영향 | 바꾼 이유, 영향받는 코드·배선·문서와 유지한 조건 |
| 다음 행동 | 바로 실행할 작업 1~3개와 각 완료 조건. 장비가 필요한 일은 구분 |

## 결과와 근거

| 항목 | 판정·확인한 범위 | 근거 | 미확인·남은 조건 |
| --- | --- | --- | --- |
| 작업/시험 이름 | PASS·PARTIAL·미실행 등과 구체적인 범위 | 보고서·로그·사진·측정표 또는 변경 파일 | 전체 완료로 확대할 수 없는 범위 |

## 결정과 미완료

- 결정과 이유:
- 영향받는 항목:
- 미확인 사항·진행을 막는 조건:

## 다음 행동

1. 다음 작업 — 선행 조건과 완료 기준.
2. 필요한 경우에만 추가. 이미 통과한 검사를 반복하려면 변경·실패 근거를 기록.

## 상세 작업 기록

### 작업 묶음 이름

- 문제/목적과 실제 수행 내용.
- 관측값·단위·조건·사용자 보고·해석을 구분하고 원본에 연결.
- 문서 작업만 했다면 변경 내용과 확인 방법을 기록. 새 빌드·플래시·물리 시험을 수행한 것으로 쓰지 않음.

## 변경 파일과 검증

- 변경 파일:
- 수행한 검사와 결과:
- 실행하지 않은 검증(결과 해석에 필요할 때):
```

## 날짜별 기록

| 날짜 | 기록 | 당시 작업 요약 |
| --- | --- | --- |
| 2026-09-30 | [2026-09-30_progress.md](2026-09-30_progress.md) | 진행 기록 요약·공통 템플릿·인수인계 정리로 문서 개편 4단계 마감; 새 물리 시험 없음 |
| 2026-09-29 | [2026-09-29_progress.md](2026-09-29_progress.md) | B 교차시험·오른쪽 DIR 보정·양방향 구동/정지, 노트북 복습·파일명 정리·문서 개편 1~3단계; M2 역방향 시험 이미지 유지 |
| 2026-09-28 | [2026-09-28_progress.md](2026-09-28_progress.md) | 수동 콘솔·COM5·ESP 세 가닥 연장, A/M1 ±10% 회전, 초기 B/M2 미회전과 A 교차시험 |
| 2026-09-27 | [2026-09-27_progress.md](2026-09-27_progress.md) | 실제 엔코더·warm reset·좌우 정정·전력단 관측 보존; ESP M1 수동 콘솔 사용자 입력 WIP, 다음 상태 변수 설명 |
| 2026-09-23 | [2026-09-23_progress.md](2026-09-23_progress.md) | 엔코더 영구 조정부 납땜/저항/전원 검사와 +5.05V PASS; 정지 TEL400 CPS0, 실제 엔코더 연결 다음; T005A 6캡처 마감 |
| 2026-09-22 | [2026-09-22_progress.md](2026-09-22_progress.md) | T004 conditioned PWM/latch/reset/wire-open 및 hook0 복구 PASS; left encoder 임시 pull-down, 30/30, 다음은 T005A 준비 |
| 2026-09-19 | [2026-09-19_progress.md](2026-09-19_progress.md) | 측정 배선·무전원 검사·마감 사용자 보고 PASS; CTRL/ENC 각 3핀 두 개, T004 사용자 빌드부터 재개 |
| 2026-09-15 | [2026-09-15_progress.md](2026-09-15_progress.md) | README 162줄 개편, 상세 색인 보존, 9/15 도면 검토와 이후 저장본 경계 정리; 기존 배선 도면 잔여 검토부터 재개 |
| 2026-09-10 | [`2026-09-10_progress.md`](2026-09-10_progress.md) | Daily UART/debug-header plan; carried-forward scheduler correction and hook-0 30/30 PASS; T004-only 1U confirmed, user build/flash/runtime unreported |
| 2026-09-09 | [`2026-09-09_progress.md`](2026-09-09_progress.md) | Historical initial paused checkpoint; subsequent scheduler/test completion and current resume point are carried forward in 2026-09-10 progress |
| 2026-09-08 | [`2026-09-08_progress.md`](2026-09-08_progress.md) | K2/S0 wire-break, XL4015 #1 dual-board power, #2 AUX path와 conditioned sense 0.06/3.27 V 기능 subset PASS; T004 firmware/PWM NOT RUN |
| 2026-09-07 | [`2026-09-07_progress.md`](2026-09-07_progress.md) | Session/documentation 복원, host 29/29 PASS, K2 VeroRoute/PDF Label 정정 확인 및 R02/R03 재측정 low-Ω PASS; 전체 E-stop PARTIAL |
| 2026-09-05 | [`2026-09-05_progress.md`](2026-09-05_progress.md) | K2 bottom-view/polarity as-built correction 뒤 12.24 V control-only K2/K1/S2/S0/S1 nominal subset와 S0-B contact truth table PASS; MDD10A B+ disconnected, wire-break/T003/full rail gate OPEN |
| 2026-09-03 | [`2026-09-03_progress.md`](2026-09-03_progress.md) | RevC 무전원 검사 IN PROGRESS; rail 0 V와 U1 방향/forward `0.918 V`/reverse-open PASS, 나머지 local continuity/isolation OPEN |
| 2026-09-01 | [`2026-09-01_progress.md`](2026-09-01_progress.md) | RevC E-stop VeroRoute FINAL과 component/solder mirror PDF 고정; R14/U1/K2/D2/JESTOP 및 세 배선 구간 user-reported partial solder, 무전원 실물 continuity/isolation OPEN |
| 2026-08-30 | [`2026-08-30_progress.md`](2026-08-30_progress.md) | P-04B default-`0U` reset closeout harness, current canonical `29/29`과 ESP32 isolated build PASS; reset target runtime OPEN; crimp tool user-reported arrived/unverified, 6P unassembled |
| 2026-08-29 | [`2026-08-29_progress.md`](2026-08-29_progress.md) | P-04A complete, P-04B reason/command-age와 timeout/direct-PC7 active-latch subset PASS, historical checkpoint `28/28`와 hook-0 isolated build PASS, reset/target reflash-runtime pending |
| 2026-08-28 | [`2026-08-28_progress.md`](2026-08-28_progress.md) | K1/S0/S2/VO617A-3/P6KE/F2 unpowered screen, P-03/REQ-SAFE-004 target runtime와 run04 safe restore PASS, 6P/tooling boundary와 next work |
| 2026-08-27 | [`2026-08-27_progress.md`](2026-08-27_progress.md) | P-02B~P-02C-2와 P-03A/P-03B source/static/full-build 완료, 당시 canonical `26/26` PASS, P-03 target runtime pending, Physical E-stop partial arrival와 received-subset 무전원 입고검사 전환 |
| 2026-08-26 | [`2026-08-26_progress.md`](2026-08-26_progress.md) | 2026-09-15까지의 dated pre-arrival schedule, priority/milestone/buffer와 delivery transition rule |
| 2026-08-25 | [`2026-08-25_progress.md`](2026-08-25_progress.md) | Four-chapter remaining-work rebaseline, production CMD mapper/data-path gaps, E-stop `005A/005B` scope split and `P-01~P-09` pre-arrival queue |
| 2026-08-24 | [`2026-08-24_progress.md`](2026-08-24_progress.md) | PC7 direct latch/reset runtime, host contract 20/20, F1/K2 무전원 입고 precheck와 S2 stuck/short no-auto-reenable blocker 확인 |
| 2026-08-18 | [`2026-08-18_progress.md`](2026-08-18_progress.md) | MG540 제조사 수치, nominal 19 kHz final perfboard gate PASS, TE K1 assembly 주문·catalog numerical PASS와 AWG 12 common-path 우선 결정 |
| 2026-08-16 | [`2026-08-16_progress.md`](2026-08-16_progress.md) | VeroRoute `55 x 37` target-hole-area에서 `C1..C55/R1..R37` 전체 포함을 확인하고 PDF export Gate로 전환 |
| 2026-08-15 | [`2026-08-15_progress.md`](2026-08-15_progress.md) | 실사 joint + Onshape 교차검토로 만능기판 예비 좌표/keep-out을 작성하고, 실물 dry placement 전 VeroRoute 2.40 기반 1:1 component/solder-side와 KiCad-net-to-hole Gate 채택 |
| 2026-08-14 | [`2026-08-14_progress.md`](2026-08-14_progress.md) | 실제 만능기판 component-side 정면 사진을 `assets/photos/perfboard`에 보존하고 fixed-header/open-area 확인 및 다음 solder-side/scale 입력 정의 |
| 2026-08-13 | [`2026-08-13_progress.md`](2026-08-13_progress.md) | Physical E-stop RevB 기능 회로도 재배치, 전체 Reference/Value `50/40 mil`, ERC 0/0·넷리스트 120 보존; 기능 흐름 재배치는 학습 후 후속 작업으로 동결 |
| 2026-08-12 | [`2026-08-12_progress.md`](2026-08-12_progress.md) | UART Gate C PASS에 이어 STM32 timeout/fault/reset-boot MCU-pin 시험 완료; reset 부동 HIGH FAIL을 `10 kΩ` pull-down으로 개선·재시험 PASS, all-hooks-`0U`/contract `15/15`/final safe UART PASS |
| 2026-08-11 | [`2026-08-11_progress.md`](2026-08-11_progress.md) | T-BRIDGE-008A partial-frame-name rejection/recovery PASS; all-hooks-`0U`, contract `15/15`, safe full-build/flash와 post-READY TEL 164/164 회귀 PASS; invalid terminator/control next |
| 2026-08-10 | [`2026-08-10_progress.md`](2026-08-10_progress.md) | Engineering Basis·표준 추적성 정본과 E-stop Step 1~7 진행; K2 분리/5 V-opto 보정, S0/S2/K2/opto 후보 선정, K1/F1 motor-data blocked |
| 2026-08-07 | [`2026-08-07_progress.md`](2026-08-07_progress.md) | T-BRIDGE-008A required-`seq` uint32-overflow까지 3개 subvector PASS; all-hooks-`0U`, contract `15/15`, protocol recompile+relink `0/0`, safe flash와 READY 후 14.43 s/TEL 145 회귀 PASS; partial frame-name vector next |
| 2026-08-06 | [`2026-08-06_progress.md`](2026-08-06_progress.md) | Safe baseline 뒤 T-BRIDGE-008A duplicate-required-seq subvector PASS; all-hooks-`0U`, contract `15/15`, safe build/reflash와 READY 후 14.42 s/TEL 150 회귀 PASS; remaining 008A와 008B next |
| 2026-08-04 | [`2026-08-04_progress.md`](2026-08-04_progress.md) | Gate A/B response-gated runtime과 active DISARM 23.50 us PASS; safe source/contract/isolated build PASS, board reflash/run·wrong ACK type·Gate C two-parser recovery pending |
| 2026-08-03 | [`2026-08-03_progress.md`](2026-08-03_progress.md) | USART1/PWM/DIR 로직 분석기 검증, safe STM32 runtime과 strict-parser controlled normal sequence PASS, response-gated startup source·contract `15/15`·ESP build PASS; actual board retry/wrong-response/malformed 회귀는 PARTIAL |
| 2026-07-31 | [`2026-07-31_progress.md`](2026-07-31_progress.md) | Strict UART frame parser fail-closed/recovery board-only 시험과 startup PING/desynchronization 한계 확인 |
| 2026-07-30 | [`2026-07-30_progress.md`](2026-07-30_progress.md) | 1560 counts/rev·mRPM, vehicle-frame sign, software fault latch 검증과 default-off 회귀; firmware safety contract 12/12 및 격리 STM32+ESP32 build PASS |
| 2026-07-29 | [`2026-07-29_progress.md`](2026-07-29_progress.md) | Dual encoder modular delta/CPS와 production TEL -> ESP32 independent CW/CCW PASS, direction 6-step 회귀, timeout/DISARM LED shutdown, Plus 전환 인수인계 |
| 2026-07-28 | [`2026-07-28_progress.md`](2026-07-28_progress.md) | KiCad RevA functional wiring draft, PDF export와 ERC 0/0; XL4015 #1 backfeed·fuse rating·vehicle mapping·BNO085는 TBD |
| 2026-07-27 | [`2026-07-27_progress.md`](2026-07-27_progress.md) | TIM5 PA0/PA1 추가, TIM3/TIM5 dual motor-off 독립 count/sign 및 약 1560 count/rev 재현 PASS; speed·vehicle sign·powered-noise는 PARTIAL |
| 2026-07-26 | [`2026-07-26_progress.md`](2026-07-26_progress.md) | STM32 PWM/DIR·MDD10A 6-step 검증과 swap 교정, MG540-A/B conditioned TIM3 TI12 x4 motor-power-off count/sign PASS; TIM5, powered-noise와 active safety는 PARTIAL |
| 2026-07-24 | [`2026-07-24_progress.md`](2026-07-24_progress.md) | Rev A 제조 사전검증과 주문 blocker, 최신 V-model master plan 및 final MVP traceability matrix 작성 |
| 2026-07-23 | [`2026-07-23_progress.md`](2026-07-23_progress.md) | 209 x 174 mm 알루미늄 어댑터 플레이트와 전장 배치 Draft 캡처; CAD 트리 오류 검증과 제조 release는 미완료 |
| 2026-07-20 | [`2026-07-20_progress.md`](2026-07-20_progress.md) | ESP32 scripted safety sequence, timeout-zero, board-only UART bridge MVP PASS |
| 2026-07-18 | [`2026-07-18_progress.md`](2026-07-18_progress.md) | ESP32 structured `TEL` parser implementation and real STM32 link validation |
| 2026-07-14 | [`2026-07-14_progress.md`](2026-07-14_progress.md) | ESP-IDF setup, UART1 loopback, STM32 `TEL/PING/PONG`, ESP32 TEL/PONG parser classification |
| 2026-07-10 | [`2026-07-10_progress.md`](2026-07-10_progress.md) | MDD10A inspection, fused power path validation, XL4015 #1/#2 no-load calibration, XL4016 scope correction |
| 2026-07-09 | [`2026-07-09_progress.md`](2026-07-09_progress.md) | STM32 UART MVP Web Serial validation, evidence capture, and verification docs |
| 2026-06-22 | [`2026-06-22_progress.md`](2026-06-22_progress.md) | STM32CubeMX-first UART MVP firmware guide and handoff cleanup |
| 2026-06-21 | [`2026-06-21_progress.md`](2026-06-21_progress.md) | MDD10A/BTS7960 document consistency update |
| 2026-06-08 | [`2026-06-08_progress.md`](2026-06-08_progress.md) | Architecture baseline, learning maps, MDD10A update, current next actions |

Related execution plans:

- [`../plans/2026-08-26_Pre_Arrival_Schedule_ko.md`](../plans/2026-08-26_Pre_Arrival_Schedule_ko.md)
- [`../plans/2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md`](../plans/2026-08-25_Final_MVP_Remaining_Work_and_Pre_Arrival_Plan_ko.md)
- [`../plans/2026-06-08_to_2026-06-10_hardware_execution_plan.md`](../plans/2026-06-08_to_2026-06-10_hardware_execution_plan.md)
- [`../plans/2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md`](../plans/2026-07-10_board_only_stm32_esp32_uart_bridge_plan.md)
