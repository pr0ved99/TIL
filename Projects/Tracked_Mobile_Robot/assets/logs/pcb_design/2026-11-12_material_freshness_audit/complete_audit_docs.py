"""Reconcile derived-report guidance and remaining current-status documents."""
from pathlib import Path
import json
import shutil

A = Path(__file__).resolve().parent
P = next(p for p in A.parents if p.name == 'Tracked_Mobile_Robot')
changed = json.loads((A/'document_changes.json').read_text(encoding='utf-8'))


def edit(rel, fn):
    f=P/rel
    s=f.read_text(encoding='utf-8-sig')
    out=fn(s)
    if s==out:return
    dest=A/'before'/rel
    dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():shutil.copy2(f,dest)
    f.write_text(out,encoding='utf-8',newline='\n')
    if rel not in changed:changed.append(rel)
    (A/'document_changes.json').write_text(json.dumps(changed,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def line(s,prefix,new):
    rows=s.splitlines(keepends=True)
    matches=[i for i,l in enumerate(rows) if l.startswith(prefix)]
    assert len(matches)==1,(prefix,matches)
    rows[matches[0]]=new+'\n'
    return ''.join(rows)


def shield(s):
    s=line(s,'| ERC |','| ERC | 11/12 새 추출: 40부품 회로도 오류 0/경고 0, 기존 무시 규칙 4개 유지 |')
    s=line(s,'| DRC |','| DRC | 11/12 저장 PCB 검사: 배치 위반 0, 회로도 대조 21건(미반영 부품18 + net 충돌3), 미배선32. **전체 DRC PASS가 아님** |')
    s=line(s,'현재 연결 근거는','현재 연결·ERC·PCB 대조·BOM은 [기본 보고서 안내](reports/README.md)와 [검사 결과](reports/design_review.json)를 따른다. 기본 `netlist.xml`/ERC/DRC/부품 목록과 `check_design.py`를 40부품 회로도 기준으로 갱신했다. 계산 기록과 초기 템플릿 근거는 적용 시점을 별도로 표시한다. ERC/DRC는 입력 보호·ADC 성능·실물 간섭의 검증을 대신하지 않는다.')
    s=line(s,'KiCad CLI로 `sch export netlist', 'KiCad에 포함된 Python으로 [check_design.py](check_design.py)를 실행하면 현재 저장 원본에서 `reports/netlist.xml`, `reports/erc.json`, `reports/drc_unrouted.json`을 먼저 재생성한다. 이어 11/7 검토본과 부품/전체 net·핀 타입, BOM, 초기 헤더 위치를 대조하고 [현재 부품 목록](reports/design_parts.json)과 [검사 결과](reports/design_review.json)를 갱신한다. 회로도·PCB·프로젝트·심벌 원본 해시 보존을 검사한다. PCB의 미반영/충돌/미배선은 별도 OPEN으로 보고하며 스크립트 종료0은 전체 DRC/제작 PASS가 아니다. 회로가 바뀌면 검토를 거쳐 비교 기준을 갱신해야 하며 자동으로 새 회로를 승인하지 않는다.')
    return s
edit('09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/README.md',shield)

edit('docs/handoff/NEXT_SESSION_START_PROMPT.md',lambda s:s.replace('Shield40부품+플래그2개/ERC0/0(무시4개)은 이전 회로도 검사이며 PCB는22풋프린트/배선·영역 없음이다. IDE applied.pdf는11/6 과거 스냅샷이다.', '11/12 자료 감사에서 Shield40부품+플래그2개/ERC0/0(기존 무시4규칙)을 재확인했다. PCB는22풋프린트/배선·영역0이며 회로도 대조21건(부품18+net3), 미배선32가 남는다. 기본 PDF는09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/exports/TMR_Monitor_Shield_RevA_schematic.pdf, 현재 검사 결과는같은프로젝트reports/README.md다. IDE applied.pdf는11/6 과거 스냅샷이다.',1))

edit('docs/handoff/CURRENT_SESSION_CONTEXT.md',lambda s:s.replace('## 현재 재개점 — 41-1 포트·GND 목록','## 현재 재개점 — 41-1 완료 자료 / 다음 41-2\n\n- **11/12 전체 자료 감사:** [점검 결과](../../assets/logs/pcb_design/2026-11-12_material_freshness_audit/README.md). 구매/수령·기구 확인·주행/거리·펌웨어/포트폴리오·현재 재개 안내의 누락을 근거와 대조해 수정했다. Shield 기본 netlist/ERC/DRC/부품 목록·검사기를 갱신했고 40부품/BOM40행/91net/ERC0/0을 확인했다. PCB 대조21건(부품18+net3), 미배선32/구리0은 남은 설계 단계다. CAD·MCU 소스와 기존 무관 변경은 보존했고 새 실물·빌드/플래시는 없다. 아래 41-1/내보내기 작업의 “새 ERC/DRC 없음”은 해당 선행 작업 범위이며 이번 감사의 재검사와 구분한다. 외부 게시 완료 범위는 기존 마감 영수증을 유지한다.',1))

edit('docs/progress/README.md',lambda s:line(s,'**현재 · 2026-11-12 후속:**','**현재 · 2026-11-12 후속:** [41-1 포트·GND 자료와 전체 자료 최신화 점검](2026-11-12_progress.md). 기본 PDF/netlist/ERC/DRC·부품 목록, 수령/기구/주행 근거와 현재 안내를 맞췄다. 다음 41-2 정상 입력·공급 조건표다. 새 실물/MCU 실행은 없고 후속분은 새 외부 게시 전이다. [자료 감사](../../assets/logs/pcb_design/2026-11-12_material_freshness_audit/README.md). 아래는 이전 진행/게시 이력이다.'))

edit('09_Electrical_Design/20_Analog_6Ch_Contract_and_Stage2_Review_2026-10-23_ko.md',lambda s:s.replace('## 채널과 커넥터 계약 제안','## 현재 저장 CAD와의 차이 — 2026-11-12\n\n아래 표는 10/23 제안이며 현재 커넥터 배선 지시가 아니다. 실제 저장본은 전류 J3/J4의 **1=STM_3V3, 2=GND, 3=OUT**, NTC J5/J6의 **1=NTC 노드, 2=GND**, 전압 J7/J8의 **1=GND, 2=RAW**다. 별도 EXP_3V3 LDO는 현재 CAD에 없으며 J1-16이 전류/NTC 공급, J2-7 STM_AVDD가 TPS/TMUX 공급이다. [현재 연결 표](../assets/logs/pcb_design/2026-11-12_port_inventory/README.md). 제품/키/하네스 대조 후 제안과 구현을 최종 계약으로 맞추며 이번에 핀을 자동 변경하지 않았다.\n\n전압 환산은 아래 무부하 분압식만 적용하지 않는다. 현재 47kΩ 방전 부하·1kΩ·TMUX RON을 포함한 명목 계산은 K≈6.747204이며 [학습21의36~39절](../07_Embedded_Learning_Notes/01_Concept_Notes/21_Voltage_ADC_Tolerance_Isolation_and_Discharge_Lab_ko.md)을 따른다. 실물 보정 계수 확정은 아니다.\n\n## 채널과 커넥터 계약 제안',1))

edit('01_System_Architecture/06_MCU_Pin_Allocation_Candidate_ko.md',lambda s:line(s,'> 문서 역할·상태 대조:','> 문서 역할·상태 대조: **2026-11-12** — 현재 Shield 회로도에는 전류 PC0/1, 온도 PC2/3, 전압 PA4/PB0의 6채널이 연결되어 있다. [현재 CAD 포트/핀 대조](../assets/logs/pcb_design/2026-11-12_port_inventory/README.md). 이는 센서 실물 배선·ADC 설정 완료가 아니다. PC0/1의 Nucleo solder bridge와 기존 PB8/PB9 IMU 보존 조건은 검증 전이다. 아래 날짜별 제안/초기 핀 표를 실물 확인으로 확대하지 않는다.'))

edit('docs/plans/2026-10-22_Motor_Current_Temperature_Monitoring_and_Procurement_ko.md',lambda s:s.replace('이어 **아직 모두 배송 대기**라고 확인했다. 실물 구성·결제액·납기는 미확인이다.', '10/22에는 배송 대기였으나 11/4 #5241·103JT-025·UT210E 수령을 보고했고 11/5 GM1312 모델·두 열전대와 UT210E 사용을 확인했다. [최신 보유 상태](../../00_Project_Charter/02_Component_Inventory.md) · [제한 관측](../../assets/logs/mvp_measurements/2026-11-05_external_current_temperature_air_run01/README.md). 실물 센서 상세·결제액/납기·교정/정량 정확도는 별도다.',1))
edit('docs/plans/2026-10-22_NTC_Temperature_Input_Design_ko.md',lambda s:s.replace('센서·측정기는 모두 배송 대기다.', '11/4 센서/UT210E 수령 보고와 11/5 외부 계측 관측이 있으며 [부품 대장](../../00_Project_Charter/02_Component_Inventory.md)을 따른다. NTC/ADC 정량 시험 완료는 아니다.',1).replace('| 103JT-025 | 1 | 2 | 구매 완료, 배송 대기 |','| 103JT-025 | 1 | 2 | 수령 사용자 보고(11/4), 개별 구성·저항/ADC 정량 시험 미검증 |'))

edit('09_Electrical_Design/21_External_Project_Monitoring_Architecture_Review_2026-10-27_ko.md',lambda s:s.replace('## 1. 평가 기준과 현재 프로젝트','**11/12 적용 범위 대조:** 아래 CAD22부품/전압 미추가 평가는 10/27 당시 비교다. 현재 회로도는 전압2채널·TPS/TMUX 포함40부품이며 PCB는22풋프린트로 남아 있다. [최신 도면·기본 검사](KiCAD/TMR_Monitor_Shield_RevA/README.md). 외부 사례를 근거로 성능/보호를 승인하지 않는 비교 원칙은 유지한다.\n\n## 1. 평가 기준과 현재 프로젝트',1))

def portfolio(s):
    s=s.replace('현재 단계에서는 `UART MVP + safety gate + PC dashboard`가 가장 강한 증거다.', '2026-11-12 대조 기준으로 `Wi-Fi/UART 제어 → STM 출력·정지 → 엔코더/1m 거리 기록 → 통합 시연`이 가장 강한 근거다. 전류/온도/전압 Shield 설계·시뮬레이션은 제작/정량 검증과 구분한다.')
    start=s.index('## 아직 포트폴리오에서 약한 부분')
    return s[:start]+'''## 확보한 증거와 현재 남은 범위 — 2026-11-12

| 영역 | 확보한 근거 | 남은 범위 |
| --- | --- | --- |
| 실제 모터·주행 | 단일 모터 PWM/DIR·정지 관측, 지상 전후진·양방향 회전과 149초 시연 | 전체 하중/노면·정밀 정지 시간/거리·장시간 정격 수용 |
| 엔코더 | 신호 조정부·count/CPS·부호, 10/23 지상1m 실제/추정 거리와 오차 기록 | 일반화 가능한 정확도/직진성·슬립·외부 기준 속도 검증 |
| 요구사항 추적 | 요구사항·검증 매트릭스 및 원본 증거 연결 | 전체 MUST 인수 PARTIAL/OPEN, T005A PARTIAL/T007 BLOCKED |
| 소개·시연 | 구조·담당 역할·근거·한계가 있는 README와 149초 통합 영상 | 문서 최신성 유지, 검증 범위를 넘는 표현 방지 |
| 모니터링 회로 | 전류/NTC/전압6채널 Shield40부품·ERC, RC/공차/정착 학습 | PCB22풋프린트·미배선, 포트 보호/기구·제작·ADC 잡음/보정 실측 |

[검증 매트릭스](../verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md) · [거리·MVP 판정](../verification/41_MVP_Acceptance_Disposition_2026-10-24_ko.md) · [통합 영상](../../assets/logs/wifi_link/2026-10-24_carpet_s0_demo_run01/README.md) · [11/5 외부 계측](../../assets/logs/mvp_measurements/2026-11-05_external_current_temperature_air_run01/README.md).

기존의 “엔코더 증거 없음”, “첫 모터 시험 전”, “요구사항 검증표 없음”, “전체 약30%” 평가는 초기 상태에 머문 표현이라 철회한다. 근거가 다른 구현·실물·문서 작업을 하나의 완료율로 합산하지 않는다.

## 다음 보강 순서

1. 현재 41-2 포트 정상 입력·공급 조건부터 전원 조합·고장/차단·복귀·보호 검증 기준을 정리한다.
2. 필요한 회로 변경을 판단한 뒤 기구·풋프린트/PCB·제작 검토로 진행한다. CAD/ERC를 실물 성능으로 표현하지 않는다.
3. 준비된 범위에서 사용자 조립·ADC 구현·독립 기준 비교로 잡음/보정 잔차·정확도·응답/보호 근거를 확보한다.
4. CAN·STM FreeRTOS/LL·ROS2/AI는 별도 후속 단계로 관리한다. 이미 완료한 첫 구동·1m 기록·시연을 다시 선행 과제로 나열하지 않는다.

## 포트폴리오 설명 문장

> STM32F446RE와 ESP32-S3를 연결한 궤도형 로봇의 하위 구동 플랫폼을 개발했습니다. Wi-Fi/UART 명령·최종 출력 안전 판단·PWM/DIR·엔코더를 통합하고, 저속 지상 주행·정지와 1m 실제/추정 거리 기록 및 시연을 남겼습니다. 현재는 전류·온도·전압 측정 Shield의 회로/보호 조건을 검토하고 있으며 정량 ADC·전체 하드웨어 인수는 진행 중입니다.

소유 범위는 사용자 설계·코드 입력·배선/조립·빌드/플래시·실측과 Codex의 검토·분석/문서 지원을 구분한다. 최신 재개점은 [현재 인수인계](../handoff/CURRENT_SESSION_CONTEXT.md)를 따른다.
'''
edit('docs/portfolio/02_Tracked_Mobile_Robot_Portfolio_Strengths_and_Next_Additions_ko.md',portfolio)

for rel in ['04_PC_Serial_Control/README.md','04_PC_Serial_Control/web_serial_dashboard/README.md','04_PC_Serial_Control/docs/05_UART_MVP_Runbook_ko.md']:
    depth=1 if rel=='04_PC_Serial_Control/README.md' else 2
    prefix='../'*depth
    def note(s,prefix=prefix):
        title,rest=s.split('\n',1)
        return title+'\n\n> **현재 용도 대조 · 2026-11-12:** 이 도구/절차는 초기 PC 직결 UART bench 경로다. 현재 로봇의 production 명령 입구는 ESP Wi-Fi이고 STM USART2는 bench logger다. 최신 펌웨어에 초기 runbook을 그대로 적용하지 않는다. [현재 운용 절차]('+prefix+'docs/handoff/CURRENT_MVP_OPERATION_RUNBOOK_ko.md)와 [현재 앱]('+prefix+'03_Firmware/README.md)을 따른다.\n'+rest
    edit(rel,note)

edit('docs/handoff/CURRENT_MVP_OPERATION_RUNBOOK_ko.md',lambda s:s.replace('## 1. 현재 구성과 연결','**11/12 현재 상태 대조:** 이 절차의 원래 구성 기준일은 10/24다. 후속 11/5 외부 전류·온도 제한 관측과 종료 전원 분리 보고는 [회차 기록](../../assets/logs/mvp_measurements/2026-11-05_external_current_temperature_air_run01/README.md)을 따른다. 지금은 PCB 학습이며 이 문서 점검이 새 전원 인가/시험 요청은 아니다.\n\n## 1. 현재 구성과 연결',1))

print('Cumulative changed documents:',len(changed))
