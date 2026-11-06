# 2026-11-06 전압 2채널 CAD 대조 근거

사용자의 “오늘 계획 진행” 요청으로 기존 제작 쉴드와 전압2채널 설계 계약을 대조했다. [설계27 결과·연결표](../../../../09_Electrical_Design/27_Voltage_2Ch_Schematic_Contract_Comparison_2026-11-06_ko.md)를 따른다.

## 확인 결과

- 실제 `.kicad_sch`에서 KiCad CLI10.0.5로 netlist/PDF를 새로 내보냈다. 원본의 generator_version9.0·RevA.0-DRAFT를10.0 형식으로 다시 저장하지 않았다.
- 22부품·10개 활성 net는 이전 netlist와 같았다. J1-32/J1-34/J2-7은 실제 no-connect 표시와 미연결 net를 모두 확인했다.
- 설치된 표준 심벌 폴더의 이름 검색에서 TPS3840/TMUX1511 일치 항목은 없었다. 라이브러리 검색 범위와 명령은 JSON에 남겼다.
- CAD/기존보고7파일과 무관한19파일의 실행 전후 해시가 같았다. 새 ERC/DRC·펌웨어·실물 작업은 하지 않았다.
- ST UM1724 Rev17 p59 Table29와 저장된 TMUX1511 Rev.B p3 이미지를 시각 대조했다. TPS3840 핀 표는 기존 학습32의 검토 결과를 승계하며 이번에 새 원문 검토를 했다고 기록하지 않는다.

| 파일 | 내용 |
| --- | --- |
| [audit.json](audit.json) | 실제 부품·net·핀 상태, 명령 결과, 입력 해시·보존 확인 |
| [current_netlist.xml](current_netlist.xml) | 현재 저장 회로도에서 새로 추출한 실제 연결 |
| [current_schematic.pdf](current_schematic.pdf) / [PNG](current_schematic.png) | 현재 초안의 읽기용 출력 |
| [제안 net CSV](proposed_voltage_nets.csv) | **PROPOSED_NOT_APPLIED**. 이후 편집의 비교 대상 |
| [UM1724 p59 PNG](UM1724_Rev17_p59_Table29.png) / [텍스트](UM1724_Rev17_p59_Table29.txt) | CN7-32/34·CN10-7·GND의 원문 표 |
| [audit_schematic.py](audit_schematic.py) | 로컬 CLI로 읽기용 산출물을 재생성하고 입력 보존·연결을 확인한 코드 |

스크립트는 현재22부품 초안을 대상으로 한다. 이후 회로도를 변경하면 같은 결과를 기대해 재실행하지 말고 새 회차의 비교 기준을 작성한다. 제안 CSV의 GND는 기존 GND에 추가할 핀 목록이며, NO_CONNECT 행은 두 독립 핀의 표시를 뜻한다. 물리 배선·제작 승인이나 측정 성능 PASS 근거가 아니다. 이번 결과는 로컬 후속이며 앞선 Git·Calendar·Notion 마감 게시에 포함되지 않는다.
