# Concept Notes

**현재 · 2026-11-13 마감:** 41-1~41-5 포트·정상조건·전원 전이·고장/오접속 설명 자료와 기본 도면·보고서/자료 최신화 누락 수정을 마감한다. 사용자 수기/이해 완료는 미보고이며 ADC 구현·실측/보호 PASS와 구분한다. 다음은41-6 보호 경로·검증 기준이다. [마감 기록](../../docs/progress/2026-11-13_progress.md). 아래는 당시 이력이며 실제 게시 상태는 마감 영수증을 따른다.

[실적·다음 작업](../../docs/progress/2026-11-12_progress.md). 아래 날짜별 재개점은 당시 이력이다.

**11/8 재개점:** [학습21](21_Voltage_ADC_Tolerance_Isolation_and_Discharge_Lab_ko.md)의14장·37-2 정량 관측을 보완했고, [Notion37-2 완료 필기](../../assets/logs/pcb_design/2026-11-08_learning_closeout/37_2_Notion_Completed.md)에 두 커패시터와a,b 유도를 정리했다. 작성 완료와 이해 완료는 다르다. 다음은 C2 제외 근사/포함 모델 → VADC 전류식 복습이다. 아래 학습 순서는 당시 이력이다.

## 현재 위치 — 11/5 학습·11/6 마감

[학습21](21_Voltage_ADC_Tolerance_Isolation_and_Discharge_Lab_ko.md)의39-1~39-3 설명 자료를 작성했다. 최종 판단은±0.10V 목표·현재 분압/보호/내장 ADC 구조를 유지하고39-2 기준으로 전압2채널 회로도 초안을 구체화하는 것이다.39-3에 분석/실측 예산 구분,합격·실패·보류 기준,두 채널 연결과ERC 인계를 모았다. 자료 작성과 사용자 필기/이해·실측 완료는 구분하며 필기 완료 보고는36-19까지다. 설명은 필기 형식으로 대화에도 직접 제공한다.

**다음 첫 작업:** 기존 TMR_Monitor_Shield_RevA 초안과 전압2채널 계약을 대조해 반영 범위·연결표를 작성한다. 이후 배터리측 한 채널→모터 공급측/공통 제어→ERC 순서로 사용자와 진행한다.39절 소챕터는 세 개로 마쳤으며 새 계측 장비 확보를 문서/회로 초안 단계의 완료 조건으로 강제하지 않는다. 실제CAD 편집/ERC 실행·펌웨어 구현·정확도/보호 PASS는 이번 자료 작성 범위에 포함하지 않는다.

CN10-7/AVDD는 공식 보드 문서에서 식별한 공급 후보다. 실제 보드 상태·부하/잡음·전원 과도·무전원 보호·ADC 유효화·정확도·제작 쉴드 반영은 미검증이다. 저항0.1%는39-2에서 제작용 선정 기준으로 제안했으며 실제 부품 채택/보유 사양은 아니다.100pF와고정30µs는 이전 학습 가정이다. 새 SPICE/MCU 빌드·플래시/실물/구매 변경 없이 기존 MVP PARTIAL/OPEN을 유지한다.

[11/5 학습 이력](../../docs/progress/2026-11-05_progress.md) · [11/6 마감·다음 재개](../../docs/progress/2026-11-06_progress.md). 이번37-4~39-3의실제게시상태는11/6영수증을따르며이전11/5게시범위와구분한다.

아래 날짜별 다음 작업은 당시 이력이며 현재 재개점은 위 내용을 따른다.

## 이전 실습 — 10/28 학습·10/29 마감

[Notion 상세 실습 노트](https://app.notion.com/p/407a7326f87b81298703fecc5a17ab48). 학습18절·원본그래프5개와계산/관측값·다음작업을저장하고본문및기존목차/프로젝트/작업/기술목차연결을재조회했다.

[20 KiCad 전류RC·NTC·전압 분압 실습](20_KiCad_Current_NTC_Voltage_Simulation_Lab_ko.md)은18절로AC1V·dB·A0/상대−3dB·시정수/99%·온도별등가저항·VDD/VDDA·전원차단/다이오드·전압/전류/전력과실제확인값을연결한다. [설계 판단24](../../09_Electrical_Design/24_Monitoring_Input_Simulation_and_Design_Review_2026-10-28_ko.md) · [마감](../../docs/progress/2026-10-29_progress.md). 기존2장은2-6,3장은3-4그대로이며별도실습노트다. 다음은전압오차예산·보호조건,아래이전학습재개안은당시이력이다.

이 폴더는 보드 실습 전에 개념을 분해해서 이해하는 곳이다.

각 파일은 다음 관점으로 작성한다.

- 개념의 역할
- STM32F446RE peripheral 관점
- CubeMX/HAL 설정과 direct register 대응
- 이 프로젝트에서의 사용 위치
- 실수, 고장, 디버깅 포인트
- 포트폴리오/면접 설명 문장

## 실제 설계 작업으로 연결

2026-10-27에 [전류 검증 명세22](../../09_Electrical_Design/22_Current_Channel_Verification_Spec_2026-10-27_ko.md)·[온도 검증 명세23](../../09_Electrical_Design/23_Temperature_Channel_Verification_Spec_2026-10-27_ko.md)를 작성했다. 학습3-1~3-4를 다시 쓰지 않고 시험 조건·오차 배분·장비·보정/독립점·판정을 구체화한 설계 산출물이다. 시험 NOT_RUN.

## Index

현재 STM·ESP 구조가 먼저 필요하면 [09 코드 구조와 함수 지도](09_STM32_ESP32_Source_Structure_and_Function_Map_ko.md)를 읽고,
이후 [08 단일 모터 시험 해설](08_Single_Motor_Bench_Dataflow_and_Evidence_Review_ko.md)에서 실제 시험 흐름과 연결한다.

| File | Topic |
| --- | --- |
| `01_GPIO_Alternate_Function_and_CubeMX_ko.md` | GPIO mode, alternate function, CubeMX code generation |
| `02_UART_Interrupt_Ring_Buffer_ko.md` | UART RX interrupt, ISR, ring buffer, parser split |
| `03_Timer_Encoder_Mode_ko.md` | A/B quadrature, timer encoder mode, hardware counting |
| `04_DMA_Interrupt_Timer_Comparison_ko.md` | DMA, interrupt, timer hardware role differences |
| `05_HAL_LL_Direct_Register_ko.md` | HAL, LL, direct register 접근 전략 |
| `06_I2C_SPI_IMU_Interface_Choice_ko.md` | BNO08x IMU에서 I2C 우선, SPI fallback 판단 |
| `07_CubeMX_Generated_Code_and_User_Code_Boundary_ko.md` | CubeMX 생성 파일, HAL 초기화 코드, 사용자 protocol 코드 경계 |
| [08 단일 모터 시험 해설](08_Single_Motor_Bench_Dataflow_and_Evidence_Review_ko.md) | PC→ESP→STM→모터→엔코더 흐름, 상태·timeout·DIR 보정, 실제 로그와 자기 점검 |
| [09 STM·ESP 코드 구조와 함수 지도](09_STM32_ESP32_Source_Structure_and_Function_Map_ko.md) | 파일별 역할, 초기화·반복문·UART 인터럽트 호출 흐름, 핵심 모듈 함수 사전 |
| [10 Wi-Fi·WebSocket 타이밍과 W4 데이터 흐름](10_ESP32_WiFi_WebSocket_Timing_and_W4_Dataflow_ko.md) | 주기·지연·보장, 실제 TEL/CPS 설정, 배터리 자리표시자, 모의 데이터와 실제 UART의 검증 범위 |
| [11 측정 요구·NTC·RC·ADC 샘플링](11_Monitoring_ADC_Requirements_RC_and_Sampling_ko.md) | R4/C3, 기준 전압 추종, 63%, 19kHz 감쇠, 누설과 내부/외부 C의 계산·가정 |
| [12 ADC 수집 주기·평균·PWM](12_ADC_Sampling_Cadence_Averaging_and_PWM_ko.md) | 1회 획득/반복/결과 주기 구분, 100Hz·1kHz 비교, C 회복·PWM alias 검토 |
| [13 측정 오차 예산과 보정](13_Current_Measurement_Error_Budget_and_Calibration_ko.md) | 필기2-5: 전체 전압 환산 예산, 영점·감도 보정, 보정 후 잔차와 누설/분해능/리플 구분 |
| [14 R·C와 ADC 후보 종합 판단](14_Current_RC_ADC_Candidate_Decision_ko.md) | 필기2-6: 필터·누설·센서 부하·획득·수집·응답을 연결한 후보 판단, DC 시험 시작 조건 제안 |
| [3-1 검증 대상과 합격 기준](15_Verification_Targets_and_Acceptance_ko.md) | 검증 경계·읽음값 기준·기준 계기 불확도·합격/보류 예시 |
| [3-2 정확도와 보정 검증](16_DC_Accuracy_and_Calibration_Verification_ko.md) | 입력계/센서 구분·전압 대입·영점/감도 보정·독립 검증점 |
| [3-3 PWM·수집 조건과 응답 검증](17_PWM_Sampling_and_Response_Verification_ko.md) | 평균/RMS·alias·수집률 비교·300ms 응답과 시각 불확도 |
| [3-4 이상 상태와 최종 판정](18_Fault_Validity_and_Final_Decision_ko.md) | VALID/STALE/INVALID·검출 한계·8항목 시험표·범위별 판정 |
| [3-1 보충: 전체 측정 정확도와 입력계 정확도](19_Total_Measurement_vs_Input_Chain_Accuracy_ko.md) | 센서 포함/제외 시험의 시작점·단위·오차 예산·보정·가상 예시, 온도/전압의 시험 경계 |

## 기존 모니터링 학습 목차와 당시 진행 순서

2장은 2-6까지, 3장은 **3-1~3-4 총 네 편**이다. 11번은 측정 요구·NTC/RC·ADC 획득의 상세 배경, 12번은 수집 주기·평균·PWM, 13/14번은 2-5/2-6 자료다.

3장 네 편은 자료 작성 완료다. 다음 대화에서는 **3-1부터 함께 읽고** 요구 수치·입력계 오차 배분·기준 계기·연결 조건의 미정을 채운다. 자료 준비를 사용자 학습 완료나 실물 PASS로 기록하지 않는다. 3-4의 MON-L01~08은 후속 시험안이며 모두 NOT_RUN이다.

10/25 학습 회차의 추가 자료를 10/26에 정리했다. [최신 마감 기록](../../docs/progress/2026-10-26_progress.md)을 따른다.

## Notion 복습 자료

10/27 추가: [전체 측정 정확도와 입력 회로 정확도 구분](https://app.notion.com/p/406a7326f87b81d0a897f34791e226c8). 센서 포함 전류 비교와 센서 대신 전압을 대입하는 입력계 비교를 풀어쓴 **3-1 보충 자료**다. 13개 절/예시 저장을 재조회했으며 기존 시작점·3-1 페이지에 연결했다. 새 3-5장이 아니고 실제 시험은 NOT_RUN이다.

10/26에 비공개 독립 페이지로 저장하고 본문·절·표를 재조회했다. 기존 [학습 노트 시작점](https://app.notion.com/p/403a7326f87b816f8115fbe2c995f8f0)과 프로젝트·기술 자료 목차에서도 연결된다.

- [2장 수집 주기·평균·오차 예산·후보 판단](https://app.notion.com/p/404a7326f87b81ddb7fddd0c2aa08d02)
- [3-1. 검증 대상과 합격 기준](https://app.notion.com/p/404a7326f87b81b7bf78c03a54178726)
- [3-2. 정확도와 보정 검증](https://app.notion.com/p/404a7326f87b81e9adeed4f4edd952d1)
- [3-3. PWM·수집 조건과 응답 검증](https://app.notion.com/p/404a7326f87b81999772cb0d058633b4)
- [3-4. 이상 상태와 최종 판정](https://app.notion.com/p/404a7326f87b815dbeaac47e98012307)
