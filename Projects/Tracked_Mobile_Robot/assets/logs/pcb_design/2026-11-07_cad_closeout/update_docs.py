"""One-time documentation closeout for the Nov 6 work block, closed Nov 7 KST."""
from pathlib import Path
import csv
import importlib.util
import io
import json
import sys

OUT=Path(__file__).resolve().parent
P=next(p for p in OUT.parents if p.name=='Tracked_Mobile_Robot')
E='assets/logs/pcb_design/2026-11-07_cad_closeout'
REPORT='29_MVP_Drawing_Identity_Reconciliation_2026-11-07_ko.md'

def read(rel):return (P/rel).read_text(encoding='utf-8-sig')
def write(rel,text):(P/rel).write_text(text.rstrip()+'\n',encoding='utf-8',newline='\n')
def prepend(rel,block):
    s=read(rel);i=s.index('\n')+1;write(rel,s[:i]+'\n'+block.strip()+'\n\n'+s[i:].lstrip())
def replace_first_section(rel,block):
    s=read(rel);start=s.index('\n## ');end=s.index('\n## ',start+1)
    write(rel,s[:start]+'\n\n'+block.strip()+'\n'+s[end:])

report='''# MVP 기능 회로도 — 실제 부품 기록과 과거 Candidate 표기 대조

2026-11-07 마감. 11/6 작업 후 사용자가 앞서 보류했던 과거 회로도 최신화를 명시적으로 위임했다. 대상은 기존 MVP 기능 회로도 `Tracked_Mobile_Robot_Wiring_RevB`이며, 새로운 실물 작업 없이 저장된 관측·구매·조립 기록을 도면에 반영했다.

## 1. 반영 결과

**확인된 부품명/값 12개와 XL4015 #1 출력 net 이름, 상태표·핀 대응·제목란을 갱신했다.** 48부품·전체35net(활성33+명시적 미연결2)의 핀 구성과 전기적 연결은 유지했다. net 이름은 `XL4015_1_5V_OUT_CANDIDATE`에서 `XL4015_1_5V_OUT`으로 바꿨고 연결된 핀 집합은 동일하다.

| Ref | 이전 표기 | 현재 표기 | 근거와 경계 |
| --- | --- | --- | --- |
| S0 | A22NE-M-PD02-N_CANDIDATE | SF2ER-E2R2B | report19 실물 body. 주문 -A 접미사 사진 확인은 별도 |
| S2 | REENABLE_MOMENTARY_NO_CANDIDATE | ABW110G | report19/24 입고·조립·제한 동작 |
| K1 | 12V_COIL_POWER_RELAY_TBD | V23134J1052D642 | 선정26/report24. 정격·단자 release와 구분 |
| K2 | TX2-12V_CANDIDATE | TX2-12V | report18/24. 기능 핀과 실물 핀은 아래 대응 |
| F1 | FUSE_TBD | Littelfuse_10A | report30 사용자 확인. report18의257 각인과287 주문 차이는 OPEN |
| F2 | 0.5A_TIME_DELAY_CANDIDATE | Littelfuse_1A | report30 사용자 확인. exact SKU/시간-전류 coordination은 OPEN |
| U1 | VO617A-3_CANDIDATE | VO617A-3 | report19 입고/report25 conditioned 경로 |
| R13 | 680R_CANDIDATE | 680R | report18 측정670.1Ω. 명목값을 측정값으로 교체하지 않음 |
| R14 | 10k_CANDIDATE | 10k | report18 측정9.97kΩ, report25 conditioned 경로 |
| J13 | XL4015_1_OUT_CANDIDATE | XL4015_1_OUT | report25 전원 경로. 기능 인터페이스 핀 순서는 유지 |
| J17 | K1_COIL_INTERFACE_TBD | K1_COIL_INTERFACE | 기능 접속점, 실제 하네스 품번 확정으로 해석하지 않음 |
| J19 | K1_MAIN_CONTACT_INTERFACE_TBD | K1_MAIN_CONTACT_INTERFACE | 주전류 외부 인터페이스. 단자 정격 release 미완료 |

## 2. K2 기능 핀과 실물 핀 대응

KiCad의 `Relay:Relay_DPDT` 기능 심벌을 유지했다. 아래 실물 번호는 기존 report24·선정26에 기록된 TX2 **BOTTOM VIEW** 기준이며 새 배선 지시가 아니다.

| 회로도 기능 핀 | 실물 핀 | 역할 |
| --- | --- | --- |
| A1 | 1 (+) | K2_COIL_P |
| A2 | 12 (-) | GND |
| 11 → 14 | 9 COM → 8 NO | 자기유지, 8은 K2_COIL_P |
| 21 → 24 | 4 COM → 5 NO | K1 허가, 5는 K1_COIL_P |
| 12 / 22 | 여기서 실물 번호로 사용하지 않음 | 기능 심벌의 미사용 NC 접점 |

회로도의 `12` NC 표기를 실물 coil pin12와 혼동하지 않는다. 일반 릴레이 심벌에 실제 PCB 풋프린트를 바로 배정하면 안 된다. K1 `85–86` 병렬 P6KE16CA 설치 기록은 주석에 반영했으며 clamp 소자를 이번 기능 netlist에 새로 추가하지 않았다. 실제 조립 경로는 VeroRoute와 report24/25를 함께 따른다.

## 3. 검증과 문서 경계

- KiCad10.0.5, 기존 프로젝트 설정: 적용 후 ERC 오류0·경고0. 기존 무시 규칙4개 유지, 새 제외 추가 없음.
- 변경 전후 모든 net의 ref/pin/pinfunction/pintype는 이름 변경1건을 대응시키면 동일하다. 내장 심벌·배선·접합점·미연결 표시도 동일하다.
- 부품 메타데이터는 표의 Value 12건 외 동일하다. 원본8월 checkpoint 상태표는 새 현재 문서 상태표로 교체하고 이전 원본/PDF에 보존했다.
- 엔코더/기능 커넥터 원래 토폴로지는 유지했다. 실물과의 전면 대조를 마친 as-built 도면이나 부품 정격 승인으로 확대하지 않는다.
- Shield R1/R2의 `12k candidate`와 미선정 풋프린트는 현재 설계 미결이므로 유지했다. 역사적 RevA/RevC·8월 exports와11/6 applied.pdf를 최신 도면으로 덮어쓰지 않았다.

[현재 MVP PDF](../assets/logs/pcb_design/2026-11-07_cad_closeout/mvp_current.pdf) · [현재 Shield PDF](../assets/logs/pcb_design/2026-11-07_cad_closeout/shield_current.pdf) · [백업·재현·검증](../assets/logs/pcb_design/2026-11-07_cad_closeout/README.md).

## 4. 원본 근거

- [부품 선정26](../01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md)
- [report18: F1 각인·K2·저항](../docs/verification/18_Physical_EStop_PC7_Direct_Runtime_and_Component_Incoming_Precheck_2026-08-24_ko.md)
- [report19: S0·S2·VO617·F2·TVS 입고](../docs/verification/19_Physical_EStop_Received_Component_Incoming_Precheck_2026-08-28_ko.md)
- [report24: 조립·K2 극성·clamp](../docs/verification/24_Physical_EStop_RevC_Assembly_and_Control_Path_Bench_Test_Report_2026-09-05_ko.md)
- [report25: XL4015·conditioned sense](../docs/verification/25_XL4015_Logic_Power_and_Physical_EStop_Conditioned_Sense_Test_Report_2026-09-08_ko.md)
- [report30: F1/F2 제조사·정격 보고](../docs/verification/30_Actual_Encoder_and_Power_Bench_Closeout_2026-09-27_ko.md)

새 실물·빌드·플래시 없음. 전체 MVP PARTIAL/OPEN, T005A PARTIAL/T007 BLOCKED 유지.
'''
write('09_Electrical_Design/'+REPORT,report)

progress='''# 2026-11-07 진행 기록 — 11/6 CAD 작업 마감·MVP 도면 최신화

## 범위와 날짜

11/6에 사용자 직접 Shield 회로도 작성과 ERC 확인을 진행했고, 자정을 넘긴11/7에 사용자가 과거 MVP 도면 최신화와 다섯 항목 정리를 요청했다. 실제 수면·작업 시작/종료 시각은 추정하지 않는다. 이전11/6 학습 마감의 게시 영수증과 이번 CAD 마감을 구분한다.

## 완료 결과

- 사용자 직접 TPS3840PL30DBV/TMUX1511PW 심벌, 전압2채널과 공통 제어·전원/미사용 핀 처리를 작성했다. 40부품+PWR_FLAG2개, 활성22net·의도적 미연결69net다. PA4/J1-32, PB0/J1-34, AVDD/J2-7과 설계27 연결표를 대조했다. 전류/NTC 기존 연결은 유지했다.
- 사용자 ERC 화면0/0과 실제 저장본 CLI ERC0/0을 확인했다. 이전 검토 스냅샷의18건→전원 표현2건→PWR_FLAG 추가 후0건을 구분한다. 기존 무시4규칙은 유지했다.
- Codex는 위임받은 MVP 도면의 확인된 부품 Value12건·net 이름1건과 K2 실물 대응·상태표를 갱신했다. 48부품·전체35net의 핀 연결/타입을 유지하고 ERC0/0을 확인했다. [부품별 근거·한계](../../09_Electrical_Design/29_MVP_Drawing_Identity_Reconciliation_2026-11-07_ko.md).
- Shield의 TO BE ADDED/전압 예약 공간/CN10 미사용 등 오래된 주석을 수정했다. 회로 값과 연결은 변경하지 않았다. 열린 KiCad 편집기에는 이전 내용이 남을 수 있어 다음 작업은 디스크의 최신 회로도를 다시 열어 시작한다.
- 최신 PDF/ERC/netlist/백업·검증은 [이번 CAD 마감 폴더](../../assets/logs/pcb_design/2026-11-07_cad_closeout/README.md)에 저장했다. 기존 applied.pdf는24부품 스냅샷이며 보존했다. Shield 후보 BOM은40부품으로 맞추되 실제 구매/풋프린트 확정으로 승격하지 않았다.
- [제품 검토28](../../09_Electrical_Design/28_Product_Design_Noise_and_Robustness_Review_2026-11-06_ko.md)의 기본 회로 유지 판단과 보완 우선순위를 검토했다. 100Hz·10개 평균은 첫 DC 비교용이며 모터 운용의 alias 억제 완료가 아니다. 12kΩ 누설·접지/하네스·외부 포트 보호·전원 전이가 후속 설계 항목이다.
- 이전 로컬 후속인 프로젝트 전체 진행 그래프·연결표·심벌/배치 검토·MVP 정돈·제품 분석도 이번 선택 게시 범위에 포함한다. 진행 그래프는 선정 성과의 날짜별 집계이며 완료율/투입시간으로 해석하지 않는다.

## 다음 재개점 — 11/7 수면 후

**기본 분압·TPS/TMUX·STM32 내장 ADC 구조를 유지하고 두 설계표부터 작성한다.**

1. 수집·필터 표: 채널별 측정 목적 → 원시 수집률 → 아날로그/디지털 필터 → 출력 주기·응답 시간. 첫 DC 비교용100Hz/10개와 모터 운용 조건을 분리하고 채널 수·취득 시간을 계산한다.
2. 포트·전원 조건표: 정상 범위 → 고려할 오접속/단락/전원 상태 → 보호 방법 → 확인 기준. 감지선 출발점의 에너지 제한과 센서 GND 귀환을 포함한다.

두 표를 설명·검토한 뒤 필요한 회로/BOM 변경, 기구·풋프린트, PCB 배치·배선으로 진행한다. 준비된 측정 없이 잡음·보정 잔차를0으로 채우거나 새 구매/물리 시험을 시작하지 않는다.11/9·10휴무를 유지하며 앞당겨 완료한 회로도/ERC를 이후 일정에서 반복하지 않는다.

## 유지하는 검증 경계

자료39-3까지 작성 / 사용자 필기 완료 보고36-19까지 / 실제 ADC 설정·평균 구현 및 잡음·보정 계수·독립점 잔차 측정 전. Shield PCB는 기존22풋프린트·트랙/비아/구리 영역0이고 새16부품 풋프린트는 미지정이다. 실제 전원OFF 보호·정확도·제작 승인 전이다.

실물은11/5 전원 분리 완료 보고 상태다. 새 MCU 빌드·플래시·실물 조작 없음. NotebookLM은 별도이며 최종 영상 완료를 추정하지 않는다. 기존 MVP PARTIAL/OPEN·T005A PARTIAL/T007 BLOCKED 유지.

## 게시 확인

문서·현재 재개점/README/메모리/계획을 갱신했다. Git·Calendar·Notion의 실제 반영과 보존 검증은 [게시 영수증](../../assets/logs/pcb_design/2026-11-07_cad_closeout/publication.json)을 따른다. 게시 완료 문구는 재조회 이후에 갱신한다.
'''
write('docs/progress/2026-11-07_progress.md',progress)
prepend('docs/progress/2026-11-06_progress.md','''**후속 작업 마감 · 2026-11-07:** 11/6 사용자 CAD 작성은 전압2채널/공통 제어와 ERC0/0까지 완료했다. 이후 위임받은 MVP 부품 표기·문서 최신화와 게시 범위는 [11/7 마감 기록](2026-11-07_progress.md)을 따른다. 아래 최초 학습 마감과 중간 배치/검토 상태는 각 시점의 이력이다.''')

checkpoint='''## 현재 재개점

- **날짜:**11/6 CAD 작업을11/7에 마감했다. 사용자는 자고 일어나11/7에 이어간다. 실제 시각/수면은 추정하지 않는다. [11/7 마감](../progress/2026-11-07_progress.md)과 게시 영수증을 우선한다.
- **Shield 완료:** 사용자 직접 전압2채널·공통 TPS/TMUX·C7/C8·미사용 핀 처리·PWR_FLAG2개 작성. 현재40부품+플래그2개, 설계27 연결표 일치, 기존 설정의 ERC 오류0/경고0(무시4규칙 유지). Codex는 마감 시 오래된 주석/날짜만 수정했고 연결/값은 보존했다. [최신 도면·근거](../../assets/logs/pcb_design/2026-11-07_cad_closeout/README.md). 기존 IDE의11/6 applied.pdf는24부품 과거 스냅샷이다. 다음에는 KiCad를 디스크 최신본으로 다시 연다.
- **MVP 도면 최신화:** 앞서 보류한 Candidate 갱신을 사용자 명시 위임으로 완료했다. [설계29](../../09_Electrical_Design/29_MVP_Drawing_Identity_Reconciliation_2026-11-07_ko.md): 부품 Value12개·출력 net 이름1개·K2 기능/실물 핀 대응·상태표,48부품/전체35net 연결 보존/ERC0/0. F1 257/287·F2 exact SKU/정격 release 등은 OPEN이다. 기존 실물의 전면 as-built 승인으로 확대하지 않는다.
- **다음 첫 작업:** [제품 검토28](../../09_Electrical_Design/28_Product_Design_Noise_and_Robustness_Review_2026-11-06_ko.md)을 바탕으로 **수집·필터 표**부터 작성한다. 측정 목적→원시 수집률→아날로그/디지털 필터→출력 주기·응답 시간. 이어 **포트·전원 조건표**(정상→고장/전원 상태→보호→확인 기준). 검토 결과에 필요한 회로 변경을 정한 뒤 기구/풋프린트→PCB 배치/배선이다. 완료한 회로 작성/ERC를 반복하지 않는다.
- **설계 방향:** 기존 분압·TPS3840PL30/TMUX1511·STM 내장ADC와 전압±0.10V/10Hz 목표 유지.14MHz/480cycles·100Hz/유효10개는 첫 DC 비교용이며 미구현이다. 모터 운용의 샘플링/필터 확정값이 아니다.12kΩ 누설·접지/하네스·포트 보호·전원 전이를 검토하며 실제 잡음/계수/잔차를0으로 가정하지 않는다.
- **학습:** 자료39-3까지 / 사용자 필기 완료 보고36-19까지. 결론→목적·원리→가정/계산→설계 판단→검증 순서로 대화에 필기 본문을 제공한다. 데이터시트 판본/쪽/절·표·행/조건을 제시한다. 자료 작성과 이해·실측을 구분한다.
- **작업 경계:**11/5 실물 전원 분리 완료 사용자 보고 유지. 새 MCU 빌드/플래시·실물·구매 없음. CAD 회로 추가와 펌웨어는 기본적으로 사용자가 직접 한다. NotebookLM은 별도이고 최종 영상 완료 미확인. 전체MVP PARTIAL/OPEN, T005A PARTIAL/T007 BLOCKED 및11/9·10휴무 유지.
- **정리/게시:** 문서·진행/메모리·선택Git·Calendar·Notion 다섯 항목. [이번 게시 영수증](../../assets/logs/pcb_design/2026-11-07_cad_closeout/publication.json)을 확인한다. 무관한 기존19파일을 보존한다. subagent는 사용자가 명시 요청할 때만 사용한다.
'''
s=read('docs/handoff/CURRENT_SESSION_CONTEXT.md');old=s[s.index('## 현재 재개점'):]
old=old.replace('## 현재 재개점','## 이전 11/6 진행 중 상태 — 당시 기록',1)
write('docs/handoff/CURRENT_SESSION_CONTEXT.md','# Current Session Context\n\nLast updated: **2026-11-07 — 11/6 CAD/ERC 마감·MVP 부품 표기 최신화, 다음 수집/필터·포트/전원 조건표**.\n\n'+checkpoint+'\n'+old)

nextprompt='''# 다음 세션 시작 프롬프트 — 2026-11-07 수면 후 재개

Tracked_Mobile_Robot 프로젝트의11/6 CAD 작업을11/7에 마감했다. 작업 폴더는 C:\\Users\\eyh12\\workspace\\TIL이다.

1. 루트/프로젝트 AGENTS.md.
2. docs/handoff/CURRENT_SESSION_CONTEXT.md의 현재 재개점.
3. docs/progress/2026-11-07_progress.md와 assets/logs/pcb_design/2026-11-07_cad_closeout/publication.json.
4. 09_Electrical_Design/28_Product_Design_Noise_and_Robustness_Review_2026-11-06_ko.md. 상단 최신 상태와 본문의 이전 스냅샷을 구분한다.

Shield는40부품+PWR_FLAG2개, 전압2채널·공통 제어 연결표 대조와 기존 설정 ERC0/0까지 완료했다. MVP 기능 도면의 Candidate 최신화도 완료했고 설계29에 부품별 근거가 있다. 예전 applied.pdf를 최신 도면으로 사용하지 않는다. KiCad를 디스크 최신본으로 다시 연다.

**첫 작업은 수집·필터 표**다. 기존 측정 목적·응답 목표를 읽고 채널별 원시 수집률→아날로그/디지털 필터→출력 주기를 설명/계산한다.100Hz·10개 평균은 첫 DC 비교용이며 모터 운용 확정값이 아니다. 이어 포트·전원 조건표(정상→고장/전원 상태→보호→확인 기준)를 작성한다. 기본 분압/TPS/TMUX/STM 내장ADC 구조는 유지하고 필요한 변경을 판단한 후 풋프린트/PCB로 진행한다.

목적→용어/원리→가정/계산→설계 판단→남은 검증의 번호 있는 필기 형식을 유지한다. 결론을 먼저 제시하고 데이터시트 판본·쪽·절/표/행·조건을 알려준다. 자료39-3 작성과 사용자 필기 보고36-19·실측 완료를 구분한다.

기존 Git 변경을 확인하고 무관한 변경을 보존한다. 실물은11/5전원 분리 보고 상태이며 새 빌드/플래시·실물·구매를 시작하지 않는다. NotebookLM은 별도. 전체MVP PARTIAL/OPEN, T005A PARTIAL/T007 BLOCKED와11/9·10휴무 유지. 완료한 회로도 작성/ERC·이전 시험을 자동 반복하지 않는다.
'''
write('docs/handoff/NEXT_SESSION_START_PROMPT.md',nextprompt)

brief='''## 현재 위치 — 11/6 CAD 완료·11/7 마감

Shield 전압2채널·공통 제어는40부품+PWR_FLAG2개로 연결 대조/ERC0/0까지 완료했다. MVP 도면의 실제 부품 표기·K2 핀 대응을 갱신했고 기능 연결/ERC0/0을 보존했다. **다음은 수면 후11/7 수집·필터 표 → 포트·전원 조건표**다. 기본 구조를 유지하고 필요한 회로 변경을 정한 뒤 기구/풋프린트/PCB로 진행한다.

자료39-3 / 필기 보고36-19 / ADC 구현·정확도·보호 실측은 별도다. 실물 전원 분리·MVP PARTIAL/OPEN·11/9·10휴무·NotebookLM 별도를 유지한다.

[마감·게시 근거](../progress/2026-11-07_progress.md) · [현재 인수인계](CURRENT_SESSION_CONTEXT.md) · [다음 시작 프롬프트](NEXT_SESSION_START_PROMPT.md).
'''
replace_first_section('docs/handoff/README.md',brief)
s=read('docs/progress/README.md');i=s.index('**11/5 마감 후 학습 재개:**')
write('docs/progress/README.md','# 진행 기록\n\n**최신 마감 · 2026-11-07:** [11/6 Shield 연결/ERC0/0·MVP 도면 최신화·다섯 항목 마감](2026-11-07_progress.md). 다음은 수집·필터 표와 포트·전원 조건표다. 실제 게시 결과는 마감 기록의 영수증을 따른다. 기존19개 무관한 변경과 MVP/실물 검증 경계를 유지한다.\n\n아래는 각 시점의 이전 이력이다.\n\n'+s[i:])

s=read('PROJECT_MEMORY.md');s=s.replace('Last updated: 2026-11-06 (closing Nov 5 PCB learning through 39-3; resume after sleep with existing shield CAD versus two-channel contract review).','Last updated: 2026-11-07 (Nov 6 Shield wiring/ERC complete; MVP recorded component identities reconciled).')
start=s.index('## Current Checkpoint');end=s.index('## Previous Checkpoint',start)
write('PROJECT_MEMORY.md',s[:start]+'''## Current Checkpoint — 2026-11-07 closeout / 11-06 CAD

- Shield40部품+PWR_FLAG2개. 전압2채널/공통 제어 연결표 대조 및 기존 설정 ERC0/0 완료. 새 PCB 배치/배선·실물 정확도/보호 PASS는 아니다.
- MVP 기능 회로도48부품/전체35net 유지, 부품 Value12건과net 이름1건·실물 K2 대응/상태표 갱신/ERC0/0. [설계29](09_Electrical_Design/29_MVP_Drawing_Identity_Reconciliation_2026-11-07_ko.md). 기존19개 무관한 변경 보존.
- 다음은 수집·필터 표 → 포트·전원 조건표. 기본 분압/TPS/TMUX/STM내장ADC와±0.10V/10Hz 목표 유지.100Hz/10개는 첫 DC 비교안이며 모터 운용 확정값·펌웨어 구현이 아니다.
- 자료39-3 / 사용자 필기 보고36-19 / 실제 잡음·계수·잔차 미측정. 목적·근거·계산을 설명하고 결론부터 전달한다.
- 실물11/5전원 분리 보고 유지. 새 MCU빌드/플래시·실물·구매 없음. NotebookLM별도, MVP PARTIAL/OPEN·T005A PARTIAL/T007 BLOCKED·11/9·10휴무 유지.
- [마감/게시](docs/progress/2026-11-07_progress.md) · [현재 재개점](docs/handoff/CURRENT_SESSION_CONTEXT.md).

'''+s[end:])

for rel,heading,body in [
 ('09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/README.md','**현재 재개점 · 2026-11-07:**','전압2채널·공통 제어와PWR_FLAG2개까지 사용자 작성 완료,40부품·활성22net·기존 설정 ERC0/0이다. Codex가 마감 시 오래된 주석/제목란만 갱신했다. [최신 PDF·검증](../../../assets/logs/pcb_design/2026-11-07_cad_closeout/README.md). 다음은 수집·필터 표와 포트·전원 조건표이며 풋프린트/기구·PCB는 그 뒤다. 후보 BOM은40부품으로 갱신했으나 구매/제작 승인은 아니다. 아래는 당시 이력이다.'),
 ('09_Electrical_Design/KiCAD/Tracked_Mobile_Robot_Wiring_RevB/README.md','## 2026-11-07 부품 표기·상태 최신화','[설계29](../../29_MVP_Drawing_Identity_Reconciliation_2026-11-07_ko.md)에 따라 S0/S2/K1/K2/F1/F2/U1/R13/R14/J13/J17/J19와출력net 이름을 갱신했다. [최신 PDF·변경 전 백업·검증](../../../assets/logs/pcb_design/2026-11-07_cad_closeout/README.md).48부품·전체35net의핀 연결/타입 보존·ERC0/0. K2 기능 핀과 실물 핀 대응을 표시했다. F1 series/F2 exact SKU/정격 release는OPEN. 과거8월 export와하위RevC는역사적자료로보존하며 현재 실물 전면 as-built 승인은 아니다.'),
 ('09_Electrical_Design/27_Voltage_2Ch_Schematic_Contract_Comparison_2026-11-06_ko.md','**최신 적용 확인 · 2026-11-07 마감:**','아래 연결표의 전압2채널/공통 회로가 실제 CAD에 반영됐다.40부품+PWR_FLAG2개,PA4/PB0/AVDD와MR/CT 개방·미사용 채널GND를대조했고기존설정ERC0/0이다. [적용 연결표·PDF/ERC](../assets/logs/pcb_design/2026-11-07_cad_closeout/README.md). 아래 최초22부품/24부품·PROPOSED_NOT_APPLIED 기록은 당시 스냅샷이다.'),
 ('09_Electrical_Design/28_Product_Design_Noise_and_Robustness_Review_2026-11-06_ko.md','**최신 상태 · 2026-11-07 마감:**','공통RESET→SEL·미사용 핀·PWR_FLAG 처리까지 완료해현재40부품/기존설정ERC0/0이다. 아래공통미완성·오류18건은11/6 22:14 추출시점이력이다. [최신CAD/ERC](../assets/logs/pcb_design/2026-11-07_cad_closeout/README.md). 회로 구조는 유지하고 다음은 수집·필터 표 → 포트·전원 조건표를 작성해 필요한 변경을 정한다.100Hz/10개는첫DC비교용,12kΩ은비교대상유지이며모터운용/정확도보증으로승격하지않는다. 실제잡음·전원전이·정확도검증은남는다.'),
 ('09_Electrical_Design/26_Voltage_ADC_Component_Conditions_and_Control_Draft_2026-10-31_ko.md','**최신 CAD 결과 · 2026-11-07 마감:**','설계27의전압2채널·공통제어가반영되어40부품/기존설정ERC0/0을확인했다. [최신도면·검증](../assets/logs/pcb_design/2026-11-07_cad_closeout/README.md). 다음은 [제품검토28](28_Product_Design_Noise_and_Robustness_Review_2026-11-06_ko.md)의수집·필터/포트·전원조건표다. 아래심벌준비/배선예정은과거이력이다.'),
 ('01_System_Architecture/26_Physical_EStop_Component_and_Rating_Selection_ko.md','**도면 동기화 · 2026-11-07:**','이 문서와report18/19/24/25/30에기록된부품정체성을MVP RevB기능도면에반영했다. [설계29 대조표](../09_Electrical_Design/29_MVP_Drawing_Identity_Reconciliation_2026-11-07_ko.md). 새부품선정/실물/정격판정변경은없으며기능핀과실물핀의차이를유지한다.')]:
    prepend(rel,heading+'\n\n'+body)

s=read('09_Electrical_Design/README.md');start=s.index('## 현재 위치');end=s.index('## 전류·온도',start)
write('09_Electrical_Design/README.md',s[:start]+'''## 현재 위치 — 11/6 Shield 연결/ERC 완료·11/7 도면 마감

Shield40부품+PWR_FLAG2개, 전압2채널/공통 연결표 대조와기존설정ERC0/0완료. MVP48부품기능도면은기록된부품명·K2실물대응·상태표를최신화했고연결/ERC0/0을보존했다.

[최신 Shield/MVP PDF·검증](../assets/logs/pcb_design/2026-11-07_cad_closeout/README.md) · [설계29 부품별 대조](29_MVP_Drawing_Identity_Reconciliation_2026-11-07_ko.md) · [제품 검토28](28_Product_Design_Noise_and_Robustness_Review_2026-11-06_ko.md).

**다음은 수집·필터 표 → 포트·전원 조건표**다. 기본 분압/TPS/TMUX/STM내장ADC 구조를 유지하고 필요한 회로 변경을 판단한 뒤기구/풋프린트/PCB로진행한다.100Hz/10개는첫DC비교용이며실제구현/모터운용확정값이아니다. ShieldPCB는기존22풋프린트/구리배선없음,정확도/전원보호/제작승인전이다.

[11/7 마감·게시](../docs/progress/2026-11-07_progress.md). 아래 날짜별 다음 작업은 당시 이력이다.

'''+s[end:])

s=read('README.md');lines=s.splitlines();lines=[('- **모니터링 설계 · 11/6 작업/11/7 마감:** 사용자 직접 전압2채널·공통제어 작성과기존설정ERC0/0완료. Shield40부품+플래그2개. MVP부품표기·K2실물대응도갱신했다. [최신도면·검증](assets/logs/pcb_design/2026-11-07_cad_closeout/README.md). 다음은수집·필터표/포트·전원조건표다. 자료39-3/필기보고36-19와ADC구현·정확도/보호실측을구분한다. [마감·게시](docs/progress/2026-11-07_progress.md). NotebookLM별도,11/9·10휴무유지.') if l.startswith('- **모니터링 설계 · 11/5') else l for l in lines];write('README.md','\n'.join(lines))

prepend('docs/plans/2026-11-04_to_15_PCB_Laptop_Work_Plan_ko.md','''**현재 계획 갱신 · 2026-11-07:** 전압2채널/공통 회로와기존설정ERC0/0을11/6에앞당겨완료했다. 수면 후11/7은 수집·필터 표와 포트·전원 조건표부터 진행한다.11/8 및11/11~15는 남은 조건/필요한 회로 변경·풋프린트/기구 검토를 위한 여유로 사용하고 완료한 회로 작성을 반복하지 않는다. 후속 단계는 검토 결과에 따라 정하며 제작/실물 완료를 약속하지 않는다.11/9·10휴무와기존종일일정경계를유지한다. [11/7마감](../progress/2026-11-07_progress.md). 아래 날짜별 표는 최초 계획/중간 이력이다.''')
s=read('docs/plans/README.md');start=s.index('**현재 위치');end=s.index('## 10/19 시작점')
write('docs/plans/README.md',s[:start]+'''**현재 위치 · 11/7 마감:** Shield전압2채널/공통연결과ERC0/0완료. MVP기능도면의실제부품표기최신화완료. **다음은수집·필터표→포트·전원조건표**이며검토후필요한회로변경/기구/풋프린트로진행한다. [마감·게시](../progress/2026-11-07_progress.md) · [현재맥락](../handoff/CURRENT_SESSION_CONTEXT.md).

실물전원분리·MVP PARTIAL/OPEN·NotebookLM별도·11/9/10휴무유지. AI계획은기존문서후속이며현재PCB순서를대체하지않는다. 아래는당시이력이다.

'''+s[end:])

# Bring the candidate BOM up to the actual schematic without choosing unverified packages.
sp=OUT.parent/'2026-11-06_schematic_layout_review/rearrange_schematic.py'
spec=importlib.util.spec_from_file_location('tmr_parser_docs',sp);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
comps,nets=m.net_signature(OUT/'shield_current.xml')
rel='09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/bom_candidates.csv'
rows=list(csv.DictReader(io.StringIO(read(rel))));existing={r['Reference'] for r in rows}
for ref,c in comps.items():
    if ref not in existing:
        rows.append({'Reference':ref,'Value':c['value'],'Footprint_candidate':c['footprint'] or '',
          'Status':'SCHEMATIC_DRAFT_FOOTPRINT_REVIEW_PENDING' if c['footprint'] else 'SCHEMATIC_DRAFT_FOOTPRINT_UNASSIGNED',
          'Notes':'Connected and ERC checked 2026-11-07; not a purchase order or fabrication approval'})
buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=rows[0].keys(),lineterminator='\n');w.writeheader();w.writerows(rows);write(rel,buf.getvalue())

# Preserve the original proposed table; create a separate applied evidence table.
rows=list(csv.DictReader(io.StringIO(read('assets/logs/pcb_design/2026-11-06_voltage_schematic_audit/proposed_voltage_nets.csv'))))
for row in rows:row['status']='APPLIED_AND_NETLIST_VERIFIED_2026_11_07'
buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=rows[0].keys(),lineterminator='\n');w.writeheader();w.writerows(rows);(OUT/'applied_voltage_nets.csv').write_text(buf.getvalue(),encoding='utf-8')
write(E+'/README.md','''# 11/6 CAD 작업 — 11/7 마감 근거

사용자 직접 Shield 작성/검사와 Codex 위임 도면 최신화를 구분한다. 이번은 문서/CAD 마감이며 새 실물·MCU 빌드/플래시는 없다.

| 최신 결과 | 파일 |
| --- | --- |
| Shield 전압2채널/공통 완성본 | [PDF](shield_current.pdf) · [netlist](shield_current.xml) · [ERC](shield_current.erc.json) |
| MVP 기록 부품 최신화 | [PDF](mvp_current.pdf) · [netlist](mvp_current.xml) · [ERC](mvp_current.erc.json) |
| 전압 연결표 적용 근거 | [적용 표](applied_voltage_nets.csv) |
| 변경·보존 검증 | [validation.json](validation.json) · [원본 작업 상태/무관19파일](baseline.json) |
| 게시 영수증 | [publication.json](publication.json) |
| 재현 코드 | [update_cad.py](update_cad.py) · [update_docs.py](update_docs.py) |

Shield40부품+PWR_FLAG2개, 전체91net(활성22+의도적미연결69). MVP48부품·전체35net(활성33+미연결2). 두 도면 모두기존설정ERC0/0이며무시4규칙은유지했다. 새제외없음. `*_before.kicad_sch`/PDF/netlist/ERC는이번수정직전백업, `*_candidate.*`는검토본, `*_current.*`는원본반영후재추출이다. candidates폴더는복사한설정/라이브러리로재현검사한중간본이다.

MVP값12건/이름1건외핀연결·전기타입·심벌정의는보존했다. [설계29](../../../../09_Electrical_Design/29_MVP_Drawing_Identity_Reconciliation_2026-11-07_ko.md)에원본관측과확정/미결을대조했다. Shield는전기내용그대로주석/제목란을갱신했고후보BOM40행으로맞췄다.

이전 `2026-11-06_schematic_layout_review/applied.pdf`는24부품과거스냅샷이다. [새진행/재개](../../../../docs/progress/2026-11-07_progress.md)를따른다. 열린KiCad편집기에이전내용이남아있으면덮어저장하지말고디스크최신본으로다시연다.

다음은수집·필터표와포트·전원조건표다. 기본구조유지/ADC구현전/정확도·보호실측전/MVP PARTIAL·OPEN/11월9·10일휴무/NotebookLM별도를유지한다.
''')

for rel in ['assets/logs/pcb_design/2026-11-06_schematic_layout_review/README.md','assets/logs/pcb_design/2026-11-06_mvp_schematic_layout_review/README.md','assets/logs/pcb_design/2026-11-06_voltage_upstream_placement/README.md']:
    prepend(rel,'**최신 도면 안내 · 2026-11-07:** 이 폴더는 당시 배치 스냅샷으로 보존한다. 현재 회로도와 ERC·부품 표기 최신화 결과는 [11/7 CAD 마감](../2026-11-07_cad_closeout/README.md)을 따른다.')

print('Documentation and candidate BOM reconciled; publication still pending.')
