# 진행 기록

- [10/23 세션 마감·전압 추가 관측·다음 재개점](2026-10-23_progress.md#세션-마감과-다음-재개점): 거리/알람 기록 완료, 자동 DISARM 수신 지연 구간은 OPEN. 기존 제한값 유지, 수면 후 조사.

**[2026-10-23 전진·좌회전 자동 DISARM](2026-10-23_progress.md#전진좌회전-중-자동-disarm의-실제-지연-관측)** — TEL250ms/control200ms freshness 조건에 따른 보호 정지 확인. 수신 공백·묶음 도착의 원인은 미결, 다음은 기존 제한 유지하 지연 구간 조사.

**[2026-10-23 DISARM PC 검토 마감](2026-10-23_progress.md#disarm-버튼-현상-pc-검토-마감)** — 추가24·기존67검사 PASS, 원본4개 대조. 과거 원인 미확정/미재현 유지, MCU 수정·추가 실물 시험 없음. 다음은 최종 인수 범위 대조.

**[2026-10-23 리포 알람 과거 경고음 확인](2026-10-23_progress.md#리포-알람-실제-경고-동작의-과거-관측-확인)** — 과거 주행 중 셀 전압이 설정값 아래로 내려가 경고음이 울렸고 전원을 껐다는 사용자 보고 확인. REQ-POWER-004/T-PWR-004 PASS — USER-REPORTED 감독하 운영 범위. 반복 시험 요구 없음.

**[2026-10-23 지상1m 비교·DISARM 관찰 마감](2026-10-23_progress.md#지상-1m-거리-비교와-disarm-관찰-마감)** — run03/04 실측1002mm, 평균1002.640333/1000.953333mm. T-ODO-001은 거리/오차 기록 범위 PASS. 관찰기v5.1·수동 DISARM 경로 확인, run02 기록 누락/간헐 UI 원인은 OPEN. 전체 MVP 인수는 잔여 경계 대조 중.

**[2026-10-23 기존 모터 유지·온도 검증 후속 분리](2026-10-23_progress.md#기존-모터-유지와-온도-검증-후속-분리)** — 사용자 결정으로 외부 온도는 DEFERRED / NOT_RUN. 온도계·열 기준 대기를 지상1m/MVP 선행에서 제외하고 열 미검증을 한계로 남긴다. 기존 출력/정지/셀 알람 운영 유지.

**[2026-10-23 JGB37-520 교체 후보 조사](2026-10-23_progress.md)** — XYT/ASLONG 제조사 원문·도면 보관. 세부 모델별 성능 차이와 동작 환경 온도 확인, 케이스/권선 한계·연속 운전 조건은 미확보. AliExpress 상품과 자료의 동일성 미확인, 구매·교체 미확정.

**[2026-10-22 모터 모니터링4채널 확장 연결안](2026-10-22_progress.md#모터-모니터링-4채널-확장-연결안)** — 기존 기판 유지·별도 신호 기판, 후보4접점 Net0/기준4핀 대조·CN7 bridge 조건 반영. 전류12kΩ/100nF 계산안과커넥터 초안 준비, 실물/제작 미확정. 다음은 독립 회로도·보호/누설/전원·ADC 검토다.

**[2026-10-22 NTC 온도2채널 입력 계산](2026-10-22_progress.md#배송-대기-중-ntc-온도-입력-회로-계산)** — 채널별10kΩ±0.1%·1kΩ·100nF, 제조사21점 분압 표·자가발열/ADC 획득 계산과 유효성 처리 준비. 실제84MHz PCLK2 기반14MHz/480cycles 후보, 미구현/미실측. 다음은 전류 필터·ADC/영점과전체3.3V 부하다.

**[2026-10-22 구매 모델·전 품목 배송 대기·계측 양식 준비](2026-10-22_progress.md)** — 온도103JT-025·전류Pololu#5241 모델 확인. 네 품목 모두 배송 대기. 외부 전류 양식/CSV와 기존 온도 기록 연결 준비, 실제 설치·수치 기준 확정·실측은 미실시.

**[2026-10-22 구매 마감 후 재개 — 펌웨어 기준점 대조](2026-10-22_progress.md)** — 핵심 소스13·기존 PC 입력35개 hash 일치. STM 거리/비동기 TX 함수 포함, ESP ELF/BIN 식별·현재 PAGE 일치,10·15cm 원본 보존 확인. 보드 실행 hash는 미확인. 다음은 실제 주문 모델/수령 구성과 계측 준비다.

**[2026-10-22 센서·측정기 구매 완료와 세션 마감](2026-10-22_progress.md)** — 온도센서2·전류센서2·GM-1312·UT210E 구매 완료(사용자 보고). 수령·SKU/구성·실측은 미확인. 다음은 수령 확인과 계측 준비이며 오늘 새 펌웨어/물리 시험 없음.

**[2026-10-21 문서·Git·Notion·캘린더 마감](2026-10-21_progress.md#세션-마감--문서gitnotion캘린더-최신화)** — 공중5·10·15cm 결과/한계·20cm 미실시를 정합화했다. Notion6페이지·Calendar12개 기존 시간대 보존을 재조회했고 실제 저장본 STM/ESP 회귀·거리 분석45개 PASS. Git 게시 결과는 오늘 최종 게시 항목을 따른다.

**[2026-10-21 공중 거리 실측 정리 — 20cm 미실시](2026-10-21_progress.md#공중-거리-실측-정리--20cm-미실시)** — 5cm 좌우52mm, 10cm 좌102/우101~102mm, 15cm 좌우151~152mm. 10·15cm 원본에서 목표 도달·정지 확인. 20cm는 사용자 요청으로 미실시, 계수/출력 유지. 각 목표 단일 공중 회차이며 반복 정밀도·지상 거리 검증은 별도다.

**[2026-10-21 ESP 상태 페이지 반응형 레이아웃 적용](2026-10-21_progress.md#esp-상태-페이지-반응형-레이아웃-적용)** — 넓은 화면 2열·좁은 화면 1열, 거리 기록 복사 유지. 기존 기능 회귀와 Chrome 다섯 화면 폭 검사 PASS. 사용자 ESP 재빌드·플래시 후 화면/복사 확인 대기. 좌우52mm 사용자 보고가 있으나 제공된 거리 JSON은 빈 회차여서 count 대조는 미완료다.

**[2026-10-21 거리 버튼 교정 직접 적용·저장본 PASS](2026-10-21_progress.md#거리-버튼-교정-직접-적용저장본-pass)** — 사용자 위임으로 실제 main PAGE5개 함수 교정, 저장본 거리23·기존 브라우저67 등 PC PASS. 다음은 사용자 ESP 재빌드/flash 후 정지 중 버튼 안정성 확인이며 실제 거리 구동은 이후다.

**[2026-10-21 STM 빌드·Run 성공 보고](2026-10-21_progress.md#stm-빌드run-성공-사용자-보고)** — 사용자 STM 빌드·Run 성공 보고. 다음은 ESP 프로젝트의 사용자 빌드이며 실제 거리·정지 검증은 이후다.

**[2026-10-21 브라우저 거리 제어 실제 저장본 PASS](2026-10-21_progress.md#브라우저-거리-제어-실제-저장본-pass)** — PAGE 단일 정의·후보 정확 일치와 실제 저장본 PC 검사 통과. 기존 브라우저67·거리16·main adapter/C initializer 검증. 다음은 사용자 STM 빌드(distance_move.c 포함 확인)이며 보드 flash·물리 거리 검증은 별도다.

**[2026-10-21 ESP 거리 공통 계층 실제 저장본 PASS](2026-10-21_progress.md#esp-거리-명령-공통-계층-실제-저장본-pass)** — 현재 빌드 대상 executor 수정 확인,3개 실제 파일 native 컴파일·거리 전달/제어권·정지 회귀 통과. 다음은 브라우저 거리 선택/정지 대기/hold-to-run 연결이다.

**[2026-10-21 STM 거리 명령 실제 저장본 PASS](2026-10-21_progress.md#stm-거리-명령-실제-저장본-pass)** — 헤더 오타 교정 확인, 실제 저장본 native 컴파일·거리 제어/타이밍 회귀 통과. 다음은 ESP/브라우저 거리 명령 연결이며 보드·실물 거리 검증은 별도다.

**[2026-10-21 타이밍 실제 저장본 PASS](2026-10-21_progress.md#타이밍-실제-저장본-최종-pass)** — 중복 제거·오타 교정 완료, 실제 C native 검사 통과. 다음은 목표 거리 명령·PWM 차단·ESP UI 연결이며 보드 검증은 별도다. 아래 FAIL은 이전 검토 이력이다.

**[2026-10-21 타이밍 저장본 교정 대기](2026-10-21_progress.md#타이밍-저장본-오류와-교정-후보)** — 저장본6문제/구조 검사 FAIL,3개 파일의4개 전체 교정 블록 준비. 교정 후보 native PASS이며 실제 파일에는 미적용이다. 사용자 교정 후 저장본 재검사가 다음이다.

**[2026-10-21 빠른 count·비동기 UART 후보 PASS](2026-10-21_progress.md#빠른-count와-비동기-uart-입력-준비)** —5ms 목표 count/100ms CPS·고정 버퍼 IT 송신·응답 우선/포화 정지 후보와5개 파일 전체 입력 묶음 준비. native 후보 회귀 PASS, 사용자 입력 대기. 실제 목표 명령/PWM 연결·보드 검증은 다음 단계다.

**[2026-10-21 목표 거리 모듈 저장본 PASS](2026-10-21_progress.md)** — 사용자 입력 `distance_move.h/.c`는 후보와 일치하며 실제 저장본 native PC25개 시나리오 묶음/합성120회 통과. 다음은 빠른 encoder/정지 판정·송신 구조와 출력 경로 연결이다. STM 보드 빌드/실물 거리 검증은 별도다.

**[2026-10-20 공중 목표 거리 정지 모듈 준비](2026-10-20_progress.md)** — 사용자가 원하는5·10·15·20cm 명령→자동 정지→좌우 링크 실측으로 범위 정정. 독립 C 후보25개 시나리오 묶음/합성120회 PASS, 사용자 새 파일 입력 대기. 생산 펌웨어 연결/빠른 샘플·송신 구조/실험은 아직 미완료.

**[2026-10-20 현재 보정값 거리 검증 준비](2026-10-20_progress.md#현재-보정값-기준-거리-검증과-실측-비교-도구)** — PC 분석기에 실측 변위·명시적 ARM 구간을 연결하는 오차 계산 추가, 관련45검사 PASS. 현재 gain/출력·거리 계수 유지. 실제 지상1m는 기본 온도 판정 대기이며 새 측정값 없음.

**[2026-10-20 ESP·배선·BX100 마감](2026-10-20_progress.md#esp-복원배선-경로bx100-확인-마감)** — ESP 복원·배선 경로 사용자 확인 완료. BX100 조작 후 설정3.40V/셀, 셀 표시4.05/4.09/4.06V 기록. 알람·주전원 분리 완료. 1m 기록표 준비, 실제 온도/1m는 장비·선행 판정 대기.

**[2026-10-20 장비 대기 중 잔여 증거 정리](2026-10-20_progress.md#장비-대기-중-tk-mvp-05-02-증거-대조)** — 기존 이미지/원본 확인, 기구 장착의 오래된 미시험 표기 정정과 count·정지 근거 연결. 05-02 실행 목록 준비 후 위 사용자 확인을 추가했다. 실제 알람 경고·열·거리 등 미결은 유지한다.

**[2026-10-20 외부 온도 문서 준비](2026-10-20_progress.md#외부-온도-계획과-기록-양식-준비)** — 모터/드라이버/전원부의 2채널 측정 쌍, 고정 후보, 짧은 주행 프로파일·세션/CSV 양식 준비. 이후 GM-1312 주문 완료 보고, 10/21~22 수령 예상(미확정). 실제 부착·수치 기준은 미확정, T-LOAD-001은 PLANNED 유지. 다음은 수령/프로브 확인과 기준 확정.

**[2026-10-20 후속: UART 단절·timeout 정지와 복구](2026-10-20_progress.md#공중-uart-명령선-단절timeout-정지재연결-복구-완료)** — GPIO17 단절 뒤 STM CMD_TIMEOUT·실제 정지(S0 미사용), 재연결 후3초 실제 정지 유지, 수동 DISARM/IDLE 복구 확인. REQ-DRIVE-003/T-DRIVE-001의 기능 범위 PASS, ST-MVP-02 완료. 원본2건·분석 보존; 정확한 차단 시간/전체 MVP 수용과 구분. 다음은 전원 종료 상태 확인·GM-1312 외부 온도 준비다.

**[2026-10-20 count 실물·14톱니 모델 정정](2026-10-20_progress.md)** — 실물 톱니 **14개** 확인. 연속6개 링크 동일 형상1→6의5간격48.1~48.3mm에서 피치9.62~9.66mm, 대표값9.64mm. 기존 실측1560counts/output rev 유지 →134.96mm/rev, 좌우 공통 초기 k=1687/19500≈0.08651282mm/count. 대표값은 측정 범위 중간값이며 수동 checkpoint 회귀 보정값이 아니다. 분석기36·CLI3·거부2 PASS. 수동 참조는 윗쪽 직선 궤도 이동이며 지상 차체 거리 정확도는 미검증. 다음은 인수 이미지 기준점 대조·고정.

**[2026-10-19 계측 검토·MVP 부하 범위 재판단](2026-10-19_progress.md)** — 실제 궤도 하중의 기본 동작과 GM-1312 외부 온도는 MVP, 정량 전류 측정·전류/전압 ADC/브라우저는 post-MVP로 정리했다. MVP-014는 DEFERRED, MVP-015 외부 온도는 PLANNED. IMU 첫 후속 순서와 기존 실물 판정 유지. 구매·코드/배선·새 실측 없음.

이 폴더에는 날짜별 수행 내용·관측·결정·다음 행동을 남긴다. 문서 상단의 **한눈에 보기**로 재개 지점을 파악하고, 필요할 때 상세 기록과 원본 증거를 읽는다.
10/19에 [스토리·태스크 백로그](../plans/README.md#스토리태스크-백로그)를 추가하고 `TK-MVP-05-01` [미결 감사](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md#tk-mvp-05-01-감사-결과--2026-10-19)를 완료했다. 과거 기구 확인 근거를 정합화하고 활성 미결·제외 조사·후속을 구분했다. 현재 `TK-MVP-03-01` 거리 모델/원시 count 계약 진행 중이며 기존 누적기를 생산 TEL/브라우저 로그로 연결할 설계를 준비한다. 새 firmware/실물 시험은 없다.
같은 날 [일자별 실행안](../plans/README.md#일자별-실행안--2026-10-19-시작)을 추가했다. 하루 약2시간 가정으로10/28 인수 검토·10/29~30 보완 기간, 이후 조건부 IMU 첫 세션을 배치했다. 온도계 납기·사용 가능 시간·기존 미결에 따라 이동하는 목표 일정이며 실적/완료 판정이 아니다.
날짜가 지난 기록의 ‘현재’와 ‘다음’은 당시 상태다. 프로젝트 최신 상태는 [현재 인수인계](../handoff/CURRENT_SESSION_CONTEXT.md), 판정과 증거는 [검증 매트릭스](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)에서 확인한다.

## 최신 기록

**[2026-10-18 배터리 단독 지상 수동 주행·1차 직진 보정 완료](2026-10-18_progress.md)** — 일반15%/회전20%, 직진 왼쪽 gain960/930. 전진→좌회전→전진→우회전→후진과 매 동작 사이 zero/PWM/CPS0·최종 DISARM 확인. 사용자 휨 감소·방향 전환/놓음 정지 문제없음 확인. [최종 회차](../../assets/logs/wifi_link/2026-10-18_ground_combined_trim_run01/observations.json). 전체 MVP·정밀 주행·장시간 신뢰성 수용은 별도.

**[2026-10-17 AC-S·nonzero NZ-01~04 마감](2026-10-17_progress.md)** — Wi-Fi nonzero core/PAGE 통합·mode0 사용자 빌드/플래시와 NZ-01~04 모터 분리 UART/DIR/PWM 시험을 완료했다. 방향 입력·놓음 zero·출력 중 DISARM·창 전환 정지/자동 재무장 방지의 선택 시나리오 PASS다. 실제 모터 부하·주행은 다음 별도 회차다. [보고서38](../verification/38_WiFi_Nonzero_Disconnected_Motor_Bench_Closeout_2026-10-17_ko.md) 참조. 최신 DISARM436 OK/IDLE/DISARMED, 이번 종료 전원 분리는 미보고.

**[2026-10-16 UART 줄 폐기·부분 명령 실물 시험·일반 이미지 복원](2026-10-16_progress.md)** — UR-02 재연결·부분 CMD·LF 없는 ARM 폐기 및 첫 DISARM 복구 PASS. mode0 복원 뒤 boot3996125447, 시험 배너 없음·READY/IDLE 확인. D1 단발 샘플 차이 원인·전체 AC-S는 미완료. 다음은 UR-03 잔여 항목. [보고서36](../verification/36_UART_Line_Cancel_Recovery_2026-10-16_ko.md).

**[2026-10-15 zero-only 정지·리셋·두 연결·UART 단절](2026-10-15_progress.md)** — 기능 관측을 [보고서35](../verification/35_WiFi_Zero_Control_Fault_Recovery_2026-10-15_ko.md)에 보존. 마지막 DISARM24 OK/IDLE이나 첫 복구 DISARM23 실패는 OPEN. 전체 AC-S 및 실제 PWM 측정 미완료. 문서화10/16.

**[2026-10-13 zero-only 통합·교과서·Git 정리](2026-10-13_progress.md)** — 사용자 빌드/플래시와 ARM/zero·정지 관측, 최신 저장 main C42·PAGE JS46 PASS. STM·ESP 교과서와 예제 5개, 12개 학습 단위 완료. 전체 AC-B/S·nonzero 구동은 미완료이며 종료 전원 상태는 미보고다.

**[2026-10-12 state 저장본·ESP 빌드 확인](2026-10-12_progress.md)** — 최종 실제 .h/.c 안내 일치·PC27 PASS、ESP 전체 빌드 성공 사용자 확인. STM·ESP는 만능기판 장착·USB 공급·XL4015 분리 사용자 보고다. 다음은 main의 제어 실행 adapter 연결이다.

**[2026-10-11 owner PC·ESP 빌드 확인과 문서 정합성 마감](2026-10-11_progress.md)** — 실제 parser PC15·ticket PC12·owner PC9 PASS, owner 포함 ESP 전체 빌드 성공 사용자 확인. 프로젝트/앱/분야 목차·Memory의 현재 요약을 대조하고 펌웨어 목차·증거 보존 절차를 추가했다. 다음은 phase/기한·ACK/TEL·취소/정지 흐름이다. 큐/UART 연결과 새 보드 동작은 미실행이다.

**[2026-10-10 W5 마감·ARM/CMD 초기 설계](2026-10-10_progress.md)** — W5 왕복·거부·timeout/복구·결과/버튼·재접속 마감과 Git 반영. JS57·C21은 별도 증거, 두 USB 분리 완료 사용자 확인. 후속 [ARM/CMD 계약·검증 계획](../plans/2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md)을 작성했고 다음은 ESP 데이터/입력 검사 구현이다. 새 제어 송신·보드 시험은 미실행이다. [보고서34](../verification/34_W5_PING_DISARM_WebSocket_and_Response_Matching_2026-10-10_ko.md).

**[2026-10-08 W4 실제 TEL·WebSocket·STARTUP 마감](2026-10-08_progress.md)** — 실제 TEL 전달·stale/복구·WS 재접속·ACK/PONG 제한 실패·READY/FAILED 독립 표시 PASS. PA10 pull-up과 리셋 err의 관측·해석 한계를 보존했다. 마지막 READY/fresh 복원, 다음 W5는 비구동 PING/DISARM부터다. [보고서33](../verification/33_W4_STM_UART_WebSocket_and_Startup_Status_2026-10-08_ko.md).

**[2026-10-06 HTTP·WebSocket 학습과 W4 준비](2026-10-06_progress.md)** — 사용자 보고로 04 `/hello` 응답과 05 두 탭 브로드캐스트를 확인했다. 실제 앱은 HTTP 폴링이며 W4/W5는 남아 있다. TEL 100ms·CPS·배터리 자리표시자를 실제 소스와 대조하고 모의 제안·시간 보장 설명을 정리했다. 집에서 실제 UART를 연결해 재개한다.

**[2026-10-04 FreeRTOS 예제 구조 검토](2026-10-04_progress.md)** — 02 저장본의 fast/slow/main 역할과 공유 카운터·Mutex·대기 흐름을 확인했다. 로컬 SDK로 스택 단위와 main 태스크 진입 구조를 대조했으며, 빌드·보드 실행 로그는 미확인이다.

**[2026-10-03 Wi-Fi 설정 확인·ESP 예제 검토](2026-10-03_progress.md)** — 당시 검토에서는 실제 앱이 HTTP 폴링이며 01 빌드 성공 기록과 02~05 빈 폴더를 안내했다. 이후 저장본·실행 결과는 10/4·10/6 기록을 따른다. 설정 재현과 빌드 생성 파일 Git 제외는 후속 보완 대상이다.

**[2026-10-02 재배선 점검](2026-10-02_progress.md)** — 6핀/JESTOP 유지, 전원 분배와 접점 도통 확인. Bar 12.11V, XL4015 출력5.02V/4.95V, S0/S2 및 S1 재투입에 따른 전압 변화를 사용자 보고로 기록했다.
최종 전원 분리 완료를 사용자 확인했고 바탕화면 배선 사진5장을 검토했다. 배선 정리1차는 마무리, 보호·고정·현가/궤도 간섭은 조립 마감 때 확인한다. 낮은 차단 후 전압을 전체 rail-off PASS로 확대하지 않으며, 새 모터 구동·펌웨어 변경은 없다.
사진 원본은 10/3에 [프로젝트 배선 사진 폴더](../../assets/photos/wiring/README.md)로 이름 변경·이동했다.

**[2026-10-01 마감 기록](2026-10-01_progress.md)** — 9/30 단일 모터 시험 결과와 계측 구매 검토·PCB 검토 의견을 정리했다.
[report32](../verification/32_Single_Motor_Run_DISARM_S0_and_Encoder_Evidence_2026-09-30_ko.md)에 A 전진 방향·active DISARM·S0 관측과 A/B 각각10%·3초 구동을 보존했다.
현재 휴대한 ESP에는 별도 Wi-Fi 앱을 플래시했다. M2_RUN 시험1U는 로봇 UART bridge의 마지막 시험 설정이며 전류/온도·정상모드 복구·최종 전원 분리 확인은 당시 미완료다.
재개는 [현재 인수인계](../handoff/CURRENT_SESSION_CONTEXT.md)를 따른다. 이전 계획의 A 방향 확인부터 반복하지 않는다.

같은 날 후속으로 노트북·ESP만 있는 환경의 [Wi-Fi·PCB·문서 이해 계획](../plans/2026-10-01_Laptop_ESP_WiFi_PCB_and_Project_Review_Plan_ko.md)을 마련했다.
이후 사용자 빌드·플래시와 AP HTTP 접속·상태 갱신·연결 해제 표시·재접속 복구를 확인했다.
STA·WebSocket·STM 통합/무선 명령과 PCB CAD는 남아 있다. 앞선 낡은 현재 안내3곳의 수정 이력도 같은 날 기록에 보존했다.

9/30 전반부 문서 개편·확장 기판 분석은 [9/30 기록](2026-09-30_progress.md), 이전 시험은 report25~31에 있다.

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
| 2026-10-12 | [2026-10-12_progress.md](2026-10-12_progress.md) | state 실제PC27 PASS·ESP 전체 빌드 성공 사용자 확인, 보드 장착·USB/XL4015 조건 기록 |
| 2026-10-11 | [2026-10-11_progress.md](2026-10-11_progress.md) | owner 실제PC9 PASS·owner 포함 ESP 전체 빌드 성공 사용자 확인, 제어 UART 미연결 |
| 2026-10-10 | [2026-10-10_progress.md](2026-10-10_progress.md) | W5 마감·Git 반영 / ARM/CMD 설계·parser/ticket 실제 PC 검사와 parser 빌드 확인, 제어 UART 미연결 |
| 2026-10-08 | [2026-10-08_progress.md](2026-10-08_progress.md) | 10/7~8 W4 통합·리셋 진단·부팅/TEL 상태 분리·정상 복원 마감 |
| 2026-10-01 | [2026-10-01_progress.md](2026-10-01_progress.md) | 9/30 모터 시험 증거 마감·계측 구매 한계·PCB 전환 의견 |
| 2026-09-30 | [2026-09-30_progress.md](2026-09-30_progress.md) | 전반부 문서 개편·공간 분석; 후반부 모터 시험은10/1 기록과 report32로 마감 |
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
