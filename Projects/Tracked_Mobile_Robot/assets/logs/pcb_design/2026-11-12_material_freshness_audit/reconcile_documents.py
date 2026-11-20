"""Apply the evidence-backed 2026-11-12 documentation audit; preserve pre-edit copies."""
from pathlib import Path
import json
import re
import shutil

A = Path(__file__).resolve().parent
P = next(p for p in A.parents if p.name == 'Tracked_Mobile_Robot')
changed = []


def edit(rel, transform):
    f = P/rel
    old = f.read_text(encoding='utf-8-sig')
    new = transform(old)
    if new == old:
        return
    backup = A/'before'/rel
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists():
        shutil.copy2(f, backup)
    f.write_text(new, encoding='utf-8', newline='\n')
    changed.append(rel)
    (A/'document_changes.json').write_text(json.dumps(changed, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')


def line(text, prefix, replacement):
    rows = text.splitlines(keepends=True)
    matches = [i for i, row in enumerate(rows) if row.startswith(prefix)]
    assert len(matches) == 1, (prefix, matches)
    rows[matches[0]] = replacement+'\n'
    return ''.join(rows)


def block(text, start, end, replacement):
    i = text.index(start)
    j = text.index(end, i)
    return text[:i]+replacement.rstrip()+'\n\n'+text[j:]


current = '**현재 · 2026-11-12 후속:** 41-1 외부 포트·기준 GND 목록 작성과 저장 CAD 대조를 마쳤다. 다음은 **41-2 정상 입력·공급 조건표**다. 수집·필터 A/B는 구현 전 비교안이며 실제 잡음·정확도·보호 검증과 사용자 수기/이해 완료는 별도다. 기본 도면 PDF와 검사 보고서는 11/12 자료 점검에서 최신 저장본에 맞췄다. 아래 날짜별 재개점은 당시 이력이다.'
for rel in ['docs/handoff/README.md', 'docs/plans/README.md', '07_Embedded_Learning_Notes/README.md', '07_Embedded_Learning_Notes/01_Concept_Notes/README.md']:
    edit(rel, lambda s: line(s, '**현재 · 2026-11-12 마감:**', current))

edit('README.md', lambda s: line(s, '- **최신 학습 ·', '- **현재 학습 · 11/12 후속:** 41-1 포트·GND 목록과 현재 CAD 연결을 대조했다. 다음은 41-2 정상 입력·공급 조건표다. [현재 재개점](docs/handoff/CURRENT_SESSION_CONTEXT.md) · [최신 도면 기본 경로](09_Electrical_Design/README.md) · [전체 자료 점검](assets/logs/pcb_design/2026-11-12_material_freshness_audit/README.md). 자료 작성·수기/이해·실제 ADC 구현과 잡음/보호 검증을 구분한다.'))

def memory(s):
    s=line(s, 'Last updated:', 'Last updated: 2026-11-12 (41-1 port inventory and material freshness audit; next: 41-2 normal input/supply conditions).')
    s=s.replace('## Current Checkpoint — 2026-11-12 sampling/filter closeout', '## Current Checkpoint — 2026-11-12 port inventory and material audit', 1)
    s=s.replace('- 40-2의 블록 평균', '- 41-1 포트·GND 자료와 최신 CAD 대조 완료. 다음은 41-2 정상 입력·공급 조건표다. 사용자 수기/이해 완료는 미보고다. Shield/MVP 기본 PDF·Shield netlist/ERC/DRC/부품 목록과 현재 안내 문서의 누락을 수정했다. [점검 결과](assets/logs/pcb_design/2026-11-12_material_freshness_audit/README.md).\n- 11/12 Shield 재검사: 40부품/91net(활성22), BOM40행 일치, 기존 설정 ERC0/0·무시4규칙 유지. PCB22풋프린트/회로도 대조21건/미배선32/구리0은 남은 설계 단계이며 전체 DRC PASS가 아니다.\n- 40-2의 블록 평균',1)
    s=s.replace('**다음은 포트·전원 조건표**이며', '**해당 마감 뒤 포트·전원 조건표를 시작했으며 현재 다음은 41-2**다. 이후에도',1)
    return s
edit('PROJECT_MEMORY.md', memory)

edit('docs/README.md', lambda s: s.replace('## 기획과 요구사항', '최신 도면은 [전기 설계 기본 PDF 안내](../09_Electrical_Design/README.md), 이번 자료 정합성 결과는 [11/12 점검 기록](../assets/logs/pcb_design/2026-11-12_material_freshness_audit/README.md)을 따른다. 날짜별 로그 PDF와 초기 검사는 현재 회로/실물 판정으로 재사용하지 않는다.\n\n## 기획과 요구사항',1))

def plan(s):
    s=line(s, '**최신 조정 · 2026-11-12:**', '**최신 조정 · 2026-11-12 후속:** 40-2·40-3 비교 뒤 41-1 포트·GND 자료와 CAD 대조를 마쳤다. 다음은 41-2 정상 입력·공급 조건표다. 기본 도면·검사 보고서와 현재 안내의 최신화 누락을 수정했다. A/B는 비교안이며 새 FFT/PWM 실습·회로 편집을 자동 추가하지 않는다. 아래 최초 회로 목표는 이미 완료한 11/6 기본 연결을 반복하라는 지시가 아니다.')
    s=s.replace('| 11/12 | alias 검토 목적·온도 B안 이해 연결, 문서·Git·Notion·Calendar 마감 |','| 11/12 | alias·온도 B안 학습과 다섯 항목 마감. 이후 별도 로컬 후속으로 41-1 포트 대조·NotebookLM 업로드 보고·자료 최신화 점검. 후속분은 새 외부 게시 전 |')
    s=s.replace('| 11/13 | 재개 후보: 포트·전원 조건표의 정상 입력/기준 GND/전원 상태부터 |','| 11/13 | 재개 후보: 41-2 정상 입력·공급 범위부터. 41-1 완료 자료를 재작성하지 않고 전원 상태 조합으로 연결 |')
    s=s.replace('완료RC/공차/두 점 보정 실습은 반복하지 않는다.', '완료한 RC·공차 관측과 14장/37-2 실습은 반복하지 않는다. 38장의 보정 자료 작성은 실제 두 점 보정 실습 완료와 다르며, 실제 보정 계수·잔차는 미확보다.')
    return s
edit('docs/plans/2026-11-04_to_15_PCB_Laptop_Work_Plan_ko.md', plan)

def master(s):
    s=line(s, '갱신:', '갱신: **2026-11-12 자료 점검**. 10/24 통합 시연149초와 10/23 거리 기록, 11/5 외부 전류·온도 제한 관측을 반영한다. 전체 MUST 인수는 미완료다. 현재는 PCB 학습 41-2 정상 입력·공급 조건표가 다음 작업이다.')
    s=line(s, '**적용 범위:**', '**적용 범위:** 기존 MG540 유지. 온도 `MVP-015 / REQ-THERM-001 / T-LOAD-001 / ST-MVP-04`의 정식 장시간 열적 수용은 DEFERRED / NOT_RUN이다. 11/5 짧은 공중 외부 계측 관측은 수행했지만 이를 정식 수용으로 확대하지 않는다. 전류/ADC도 후속이며 장비 배송·열 기준을 MVP 선행으로 복원하지 않는다. 10/17 사용자 제외한 정격/도면 조사를 재개하지 않는다.')
    s=line(s, '**다음:**', '**다음:** 41-1 포트·GND 자료를 이어 41-2 정상 입력·공급 범위 → 전원 조합/고장·차단·복귀 → 보호 경로·검증 기준을 정리한다. 필요한 회로 변경은 조건 검토 뒤 판단하고 기구·풋프린트 → PCB로 진행한다. [현행 계획](2026-11-04_to_15_PCB_Laptop_Work_Plan_ko.md). 시연149초 제작·거리 기록·기존 기능 시험을 자동 반복하지 않는다. 새 실물·MCU 빌드/플래시 지시가 아니다.')
    s=s.replace('[오늘 기록](../progress/2026-10-24_progress.md)이 재개점이다.', '[최신 진행 기록](../progress/2026-11-12_progress.md)이 재개점이다.',1)
    return s
edit('docs/plans/00_Project_Master_Plan_To_Final_MVP_ko.md', master)

def inventory(s):
    s=line(s, '부품 본문 기준:', '부품 본문 기준: **2026-09-23**, 센서/계측기 상태는 **11/4 수령 보고·11/5 외부 관측을 11/12 대조**했다. 보유·사용 여부와 정량 검증 완료 여부는 구분한다.')
    s=s.replace('## 계측 장비와 센서 구매 — 2026-10-22', '## 계측 장비와 센서 — 11/4~5 후속 반영',1)
    s=line(s, '사용자가 **온도센서', '10/22 구매·배송 대기 이후, 11/4 사용자가 #5241·103JT-025·UT210E 수령을 보고했다. 11/5 GM1312 실물 모델·두 열전대 사용과 UT210E 표시 관측을 확인했다. [수령 보고](../docs/progress/2026-11-04_progress.md) · [외부 관측·한계](../assets/logs/mvp_measurements/2026-11-05_external_current_temperature_air_run01/README.md). 센서 설치·ADC 정량 시험 완료와는 별개다.')
    s=s.replace('구매 완료 / 배송 대기. 좌우 모터 케이스 관측. SEMITEC `103JT-025`, 사용자 구매 모델 확인; 실물 구성 확인 대기','수령 사용자 보고(11/4). SEMITEC `103JT-025`; 개별 실물 수량/구성·저항/ADC 정량 시험 미검증')
    s=s.replace('구매 완료 / 배송 대기. 좌우 모터 개별 전류 관측. Pololu `#5241 / ACS71240KEXBLT-030B3` ±30A·3.3V, 사용자 구매 모델 확인; 실물 구성 확인 대기','수령 사용자 보고(11/4). Pololu `#5241 / ACS71240KEXBLT-030B3` ±30A·3.3V; 센서 출력/ADC 정확도 시험 미검증')
    s=s.replace('구매 완료 / 배송 대기. 이전 주문 재고 취소 뒤 최종 구매 보고. 실제 K형 프로브·건전지·부속 구성 확인 대기','보유 및 GM1312 모델·두 열전대 사용 확인(11/5). 모터별 짧은 관측 수행; 부속 전체·교정/정확도 검증은 별도')
    s=s.replace('구매 완료 / 배송 대기. 외부 DC 클램프 전류 관측. 최종 판매처·가격·납기는 미확인','수령 사용자 보고(11/4), 외부 DC 클램프 표시 관측(11/5). 교정/정확도 검증·최종 결제 정보는 별도')
    return s
edit('00_Project_Charter/02_Component_Inventory.md', inventory)

def architecture(s):
    s=line(s, '상태 대조일:', '상태 대조일: **2026-11-12**. 기존 코드·시험 기록·현재 CAD를 대조한 문서 갱신이며 새 실물 시험 결과가 아니다.')
    s=s.replace('현재 작업은 PCB 3-1 학습 재개다.', '현재 PCB 학습은 41-1 포트·GND 자료 작성 뒤 41-2 정상 입력·공급 조건표로 이어진다.')
    s=line(s, '| Wi-Fi·제어 준비 |', '| Wi-Fi·제어 | 현재 앱 `esp32_wifi_link`의 ARM/CMD·owner/state/executor·UART·브라우저 연결. 10/18 지상 주행, 10/20 유실/timeout 기능, 10/24 새 UI·통합 시연 근거 | 전체 오류 조합/시간 수용과 이미지 식별은 각 시험 범위대로 남김 |')
    s=line(s, '| 모터 매핑 |', '| 모터 매핑 | A=왼쪽/M1/JENC_1/TIM3, B=오른쪽/M2/JENC_2/TIM5. 지상 전·후진/양방향 회전 및 10/23 1m 실측·추정 기록 확보 | 정밀도·직진성·다양한 하중/노면 수용 |')
    s=line(s, '| 엔코더 |', '| 엔코더 | PB4/PB5·PA0/PA1, 1kΩ 직렬+15kΩ 풀다운. CPS/count 및 10/23 지상1m 기록, k=1687/19500mm/count | 외부 기준 속도·노면/하중별 정확도·전체 구동 잡음 검증 |')
    s=line(s, '| 전원 |', '| 전원 | F1→S1→+버스바에서 K1·두 XL4015·F2 제어 분기. K1 87→MDD B+, MDD B−→GND. 11/5 종료 후 전원 분리 보고 | 정격·열·단자/전원 전이 등 기존 인수 미결. 사용자 제외한 rail-off 조사를 새 선행으로 복원하지 않음 |')
    s=line(s, '| CAN |', '| CAN | STM PA11 RX/PA12 TX 예약, MCU-230 및 CANable V2.0 Pro 보유 보고. 현재 운영은 UART | 실제 모듈·전원·종단·버스/펌웨어 검증, ESP GPIO4/5는 제안 |')
    s=line(s, '| ADC·적층 |', '| ADC·Shield | 전류2·온도2·PA4/PB0 전압2의 40부품 회로도, TPS/TMUX 포함. 기본 PDF/연결 목록 최신화 | PCB22풋프린트로 18부품 미반영·미배선. 보호·핀/하네스·기구·ADC/잡음/보정 검증. 자동 저전압은 후속 |')
    s=block(s, '**마지막 보드 실행:**', '**9/30 로봇 시험 이력:**', '**최근 실물 회차:** 11/5 기존 로봇의 짧은 공중 전진·후진에서 외부 전류/온도를 관측했고 전원 분리 완료를 사용자가 보고했다. [관측·한계](../assets/logs/mvp_measurements/2026-11-05_external_current_temperature_air_run01/README.md). 최신 ESP 앱은 `esp32_wifi_link`이며 10/24 UI 플래시 사용자 보고가 있다. STM/ESP 새 빌드·플래시를 이번 문서 점검에서 수행하지 않았다.')
    s=line(s, '| 무선 제어 다음 구현 |', '| 무선 제어 구현 이해 | [초기 계약](../docs/plans/2026-10-10_WiFi_ARM_CMD_Control_Contract_ko.md), [현재 실행 경로](../03_Firmware/README.md#armcmd-모듈과-실행-경로) | 현재 모듈은 연결되어 있다. 초기 입력 지시를 최신 코드에 덮어쓰지 않고 구현/관측 범위를 대조 |')
    return s
edit('01_System_Architecture/README.md', architecture)

def firmware(s):
    s=line(s, '상태 대조:', '상태 대조: **2026-11-12**. 10/23 지상1m 거리 기록, 10/24 새 UI 플래시 사용자 보고와 통합 시연, 11/5 외부 전류·온도 관측을 연결한다. 현재 앱은 STM `stm32_uart_mvp`와 ESP `esp32_wifi_link`이며 이번 점검에서 MCU 소스·빌드/플래시는 변경하지 않았다. ADC 수집/평균은 아직 설계 비교안이다. [현재 판정](../docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md).')
    s=s.replace('**최신 전원 재설정 후 관측:**', '**10/23 전원 재설정 후 관측 이력:**',1)
    s=line(s, '| [stm32_uart_mvp]', '| [stm32_uart_mvp](stm32_uart_mvp/) | [main.c](stm32_uart_mvp/Core/Src/main.c)와 [UART 프로토콜](stm32_uart_mvp/Core/Src/uart_mvp_protocol.c). 명령·timeout·출력 안전 판단 | Wi-Fi 경유 지상 주행·정지·count 거리 및 10/24 시연 근거. 전체 인수·ADC 구현과 별개 |')
    s=s.replace('10/23 지상1m count/수동 DISARM 확인. 반응형 PAGE·복사 기능 적용, 실제 배포 이미지 신원은 별도', '10/23 지상1m·10/24 새 UI 플래시/시연·11/5 외부 계측 회차. 보드 이미지 해시 확인은 별도')
    s=line(s, '과거 W5 시험은', '과거 W5는 두 보드 USB·LiPo 미연결 시험이었다. 이후 배터리 단독 운용을 확인했고 최근 11/5 회차 종료의 전원 분리 완료를 사용자가 보고했다. [근거](../assets/logs/mvp_measurements/2026-11-05_external_current_temperature_air_run01/README.md).')
    s=s.replace('최신 main C42·기존 PAGE67·거리/복사28 PC PASS; 10/21 거리 TEL 관측은 원본과 연결', 'main C42의 기존 기록과 10/24 PAGE 중복 제외105 PC 검사 기록. 현재 검사 범위는 tests README를 따름')
    s=line(s, '학습은 [교과서 단위 1]', '현재 프로젝트 다음 작업은 [인수인계](../docs/handoff/CURRENT_SESSION_CONTEXT.md)의 41-2 정상 입력·공급 조건표다. 펌웨어 기초를 별도로 복습할 때 [교과서 단위 1](../07_Embedded_Learning_Notes/06_STM32_ESP32_Firmware_Textbook/README.md#study-route)을 사용한다. 완료한 지상 거리·유실/timeout 시험을 자동 반복하지 않으며 전체 안전·정량 ADC 수용과 구분한다.')
    return s
edit('03_Firmware/README.md', firmware)

edit('03_Firmware/esp32_wifi_link/README.md', lambda s: s.replace('아래10/23 전원 관측은 이전 회차이며 새 전압/종료 전원 분리는 미보고다.', '아래10/23 전원 관측은 이전 회차다. 후속 11/5 외부 계측 회차에서는 전원 분리 완료를 사용자가 보고했다. [해당 관측](../../assets/logs/mvp_measurements/2026-11-05_external_current_temperature_air_run01/README.md). 새 전압·보드 이미지 해시 검증과 구분한다.',1))

edit('02_Hardware_Validation/README.md', lambda s: block(s, '**상태 대조:', '시스템 아키텍처 문서가', '**상태 대조: 2026-11-12.** 10/18 지상 주행·10/20 유실/timeout 기능·10/23 1m 거리 기록·10/24 시연과 11/5 외부 전류/온도 관측까지 [최신 검증표](../docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)에 연결한다. 아래 단계별 체크리스트는 초기 시험과 각 회차 기록이다. 완료 시험을 자동 반복하지 않는다.\n\n11/5 전원 분리 보고 이후 새 실물 실행은 없다. 전체 MVP PARTIAL/OPEN, T005A PARTIAL/T007 BLOCKED와 정식 열적 수용 미완료를 유지한다. [재개점](../docs/handoff/CURRENT_SESSION_CONTEXT.md)을 따른다.'))

edit('02_Hardware_Validation/05_First_Motor_No_Load_Test.md', lambda s: s.replace('> **2026-09-26 연결 정정:**', '> **현재 안내 대조 · 2026-11-12:** 아래 9/26~27의 동력선 분리·코드 WIP·구동 미검증은 당시 이력이다. 후속 단일 구동은 [report32](../docs/verification/32_Single_Motor_Run_DISARM_S0_and_Encoder_Evidence_2026-09-30_ko.md), 지상 주행·거리와 현재 판정은 [검증표](../docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)를 따른다. 이 초기 시험을 현재 재개 지시로 사용하지 않는다.\n>\n> **2026-09-26 연결 정정:**',1))

edit('docs/verification/README.md', lambda s: line(s, '최신 통합 관측:', '최신 관측 대조: **2026-11-12**. 10/23 지상1m 실제/추정 거리·오차 기록, 10/24 149초 통합 시연, 11/5 짧은 공중 외부 전류·온도 표시 관측과 종료 전원 분리 보고를 반영한다. [검증 매트릭스](05_Final_MVP_Requirements_and_Verification_Matrix_ko.md) · [최근 외부 관측](../../assets/logs/mvp_measurements/2026-11-05_external_current_temperature_air_run01/README.md). 정밀도·장시간 열적 수용·전체 MUST 인수 완료는 아니다.'))

edit('docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md', lambda s: s.replace('## 최신 판정 — 2026-10-24 잔여 인수 항목 대조', '## 현재 근거 대조 — 2026-11-12\n\n11/5 외부 계기의 짧은 공중 전류·온도 관측과 전원 분리 보고를 확보했다. [값·조건·한계](../../assets/logs/mvp_measurements/2026-11-05_external_current_temperature_air_run01/README.md). 정식 T-LOAD-001 열적 수용과 ACS71240/NTC/ADC 정량 검증을 완료한 것은 아니며 전체 MUST·T005A PARTIAL·T007 BLOCKED 판정은 유지한다. Shield CAD/ERC·학습 자료 완료를 실물 요구사항 PASS로 옮기지 않는다. 아래 날짜별 수치와 당시 미보고 상태는 원래 회차 기록이다.\n\n## 2026-10-24 잔여 인수 항목 대조',1))

def mechanical(s):
    s=s.replace('**상태 대조: 2026-10-11.** 플레이트 revision 동일성·fit은 계속 미확인이다.\n10/2 배선 사진의 모터 섀시 장착 모습과 하네스 조립 관측을 정식 기구 release로 확대하지 않는다.', '**상태 대조: 2026-11-12.** 10/17 가조립·고정·절연 간격·접근성, 10/20 배선 경로는 사용자 보고 범위 PASS다. [검사 기록](../02_Hardware_Validation/08_Adapter_Plate_Fit_Check.md). 제작 revision·재료/치수·홀 패턴 동일성은 여전히 미확인이고 정식 기구 release가 아니다.')
    s=s.replace('`PC PLATE USER-REPORTED RECEIVED / REVISION IDENTITY AND FIT PENDING`','`USER-REPORTED MOUNTING/ACCESS CHECKS PASS; SOURCE-TO-PART IDENTITY OPEN`')
    s=s.replace('`USER-REPORTED RECEIVED` - 2026-08-26, 실물 fit은 `NOT TESTED`','수령 보고(8/26), 가조립·고정·간격·접근성 확인 보고(10/17), 배선 경로 확인 보고(10/20). 도면-실물 치수 동일성 미검증')
    return s
edit('08_Mechanical_Design/README.md', mechanical)

edit('09_Electrical_Design/VeroRoute/README.md', lambda s: s.replace('실제 엔코더 케이블과 신호 검증은 미완료다. 과거 CTRL/addIMU 파일은 이력으로 보존한다.', '후속 엔코더 케이블·손회전/신호 관측은 [report30](../../docs/verification/30_Actual_Encoder_and_Power_Bench_Closeout_2026-09-27_ko.md), 구동·거리 기록은 [최신 검증표](../../docs/verification/05_Final_MVP_Requirements_and_Verification_Matrix_ko.md)를 따른다. 이 VRT/PDF는 9/23 제작 기록이며 최종 실물 전체의 as-built 도면 승인은 아니다. 과거 CTRL/addIMU 파일은 이력으로 보존한다.',1))

print('Updated', len(changed), 'documents; original copies preserved under before/')
