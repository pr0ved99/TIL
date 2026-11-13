# Shield 검사·계산 보고서 안내

## 현재 저장본에서 다시 생성한 자료 — 2026-11-12

| 파일 | 적용 범위 |
| --- | --- |
| [netlist.xml](netlist.xml) | 현재 40부품, 전체91net/활성22net. J7/J8과 TPS/TMUX 포함 |
| [erc.json](erc.json) | 현재 회로도 오류0/경고0, 기존 무시 규칙4개 유지 |
| [drc_unrouted.json](drc_unrouted.json) | PCB22풋프린트. 배치 위반0, 회로도 대조21건(부품18+net3), 미배선32 |
| [design_review.json](design_review.json) | 위 결과·원본/보고서 해시·11/7 검토본 연결 및 BOM 대조. 전체 DRC PASS 아님 |
| [design_parts.json](design_parts.json) | schema v2: 현재40부품의 식별/값/풋프린트/핀-net 목록. 예전22부품의 배치 좌표표를 대체 |

KiCad에 포함된 Python으로 [check_design.py](../check_design.py)를 실행하면 위 자료를 현재 저장본에서 재생성한다. 회로도/PCB/프로젝트/심벌을 수정하지 않는다. 회로가 바뀌면 11/7 기준과의 차이를 검토해야 하며 자동 승인하지 않는다. PCB 차이를 없애기 위한 회로/배치 편집은 이번 자료 점검 범위가 아니다.

## 당시 조건을 보존하는 계산·템플릿 자료

| 파일 | 해석 기준 |
| --- | --- |
| [current_circuit_walkthrough.json](current_circuit_walkthrough.json) | 10/23의 전류·NTC 초기22부품 설명/계산. 전체 최신 연결 목록은 위 netlist 사용 |
| [current_adc_acquisition.json](current_adc_acquisition.json) | 전류 채널 취득 시간의 명목 비교 계산. 실제 ADC 설정/성능 검증 아님 |
| [current_sampling_cadence_review.json](current_sampling_cadence_review.json) | 10/25의 DC 시험 수집률 비교. 이후 2kHz/평균 A/B 비교는 학습21의40장과11/12 기록 참고 |
| [template_provenance.json](template_provenance.json) | 초기 Morpho 템플릿·22풋프린트 배치의 출처. 40부품 PCB 구현 근거 아님 |

[전체 자료 감사](../../../../assets/logs/pcb_design/2026-11-12_material_freshness_audit/README.md)에 교체 전 보고서를 보존했다. 현재 부품 후보 BOM40행은 회로도와 일치하지만 풋프린트16개 미지정·제품/실물 대조는 후속이다. [BOM](../bom_candidates.csv)은 구매 명령이나 제작 승인 목록이 아니다.
