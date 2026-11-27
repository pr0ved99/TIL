# Shield 검사·계산 보고서 안내

## 2026-11-28 쉴드 회로도와 PCB 검사

| 파일 | 적용 범위 |
| --- | --- |
| [netlist.xml](netlist.xml) | 현재 40부품, 전체91net/활성22net. J7/J8과 TPS/TMUX 포함 |
| [erc.json](erc.json) | 현재 회로도 오류0/경고0, 기존 무시 규칙4개 유지 |
| [drc_unrouted.json](drc_unrouted.json) | 회로 부품 40개와 기구 홀 3개. 배치·배선 위반 0건, 회로도 대조 오류 0건, 미배선 0건 |
| [design_review.json](design_review.json) | 회로도·BOM·풋프린트·헤더 및 기구 홀 대조. 활성 22개 네트의 94개 패드 전부에 대한 구리 연결, 네트별 층별 길이·비아 수, 프로젝트 규칙 검사와 원본 해시 |
| [design_parts.json](design_parts.json) | schema v2: 현재40부품의 식별/값/풋프린트/핀-net 목록. 예전22부품의 배치 좌표표를 대체 |

쉴드 프로젝트 폴더에서 Ubuntu의 `/usr/bin/python3 check_design.py` 또는 Windows의 KiCad 번들 Python으로 다시 검사할 수 있다. 11/28에 KiCad 10.0.8로 검사했다. 11/7 검토본에서 C7을 220 nF로 바꾸고 J7·J8, C1~C8, R7~R16의 풋프린트를 변경했다. C1~C8과 R7~R16에는 제조사·품번·데이터시트도 기록했다. 91개 네트의 핀 연결과 40행 BOM을 대조했다. [검사 스크립트](../check_design.py) · [11/22 당시 검사](../../../../docs/progress/2026-11-22_progress.md#프로젝트-자료-점검)

[58개 패드 쌍의 측정표](functional_placement_paths.csv)에서 `copper_path_mm`는 패드 중심 사이의 배선 중심선 길이이며 층 전환의 수직 길이를 제외한다. 접지면으로 이어져 이 열이 비는 경우 `bottom_ground_grid_mm`에 B.Cu 구리 위에서 계산한 0.0625 mm 격자 최단 경로가 있다. `straight_line_mm`는 패드 중심 사이 직선거리다. 실제 전류 분포와 ADC 오차는 시제품에서 확인한다.

## 당시 조건을 보존하는 계산·템플릿 자료

| 파일 | 해석 기준 |
| --- | --- |
| [current_circuit_walkthrough.json](current_circuit_walkthrough.json) | 10/23의 전류·NTC 초기22부품 설명/계산. 전체 최신 연결 목록은 위 netlist 사용 |
| [current_adc_acquisition.json](current_adc_acquisition.json) | 전류 채널 취득 시간의 명목 비교 계산. 실제 ADC 설정/성능 검증 아님 |
| [current_sampling_cadence_review.json](current_sampling_cadence_review.json) | 10/25의 DC 시험 수집률 비교. 이후 2kHz/평균 A/B 비교는 학습21의40장과11/12 기록 참고 |
| [template_provenance.json](template_provenance.json) | 초기 Morpho 템플릿·22풋프린트 배치의 출처. 40부품 PCB 구현 근거 아님 |

[전체 자료 감사](../../../../assets/logs/pcb_design/2026-11-12_material_freshness_audit/README.md)에 교체 전 보고서를 보존했다. 현재 BOM 40행은 회로도와 일치한다. 회로 부품 40개와 기구 홀 3개를 배치했고, 활성 22개 네트의 모든 패드를 배선했다. 공통 GND의 28개 패드와 STM_3V3의 6개 패드도 각각 하나로 이어진다. 재배치 후 구리 선분은 194개, 관통 비아는 12개다. B.Cu의 GND 영역 1개와 장착 홀 금지 영역 3개는 별도로 센다. 다음은 제작 전 검토이며 보호 동작, ADC 성능과 기구 실측은 별도로 검증한다. [전체 배선 검토 PDF](../exports/TMR_Monitor_Shield_RevA_routing_review.pdf) · [BOM](../bom_candidates.csv)
