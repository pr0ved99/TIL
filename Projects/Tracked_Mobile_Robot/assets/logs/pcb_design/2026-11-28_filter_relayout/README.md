# 전류·온도 필터 재배치와 접지면

2026-11-28 모니터 쉴드 RevA의 기존 배선 완료본과 새 배치를 같은 패드 쌍으로 비교했다. 실물 결합 위치가 정해진 J1~J8, 장착 홀, 전압 감지부 및 오른쪽 온도 C4는 유지했다. R1~R6, C1~C3, TP3~TP6의 위치 또는 방향을 바꿨다. [기능별 배치와 전후 도면](../../../../09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/exports/TMR_Monitor_Shield_RevA_functional_placement_review.pdf)

| 패드 중심 간 구리 길이 (mm) | 이전 | 적용 | 이유 |
| --- | ---: | ---: | --- |
| C3.1 → CN7-35 | 51.03 | 21.91 | 왼쪽 온도 필터를 ADC 헤더 쪽으로 이동 |
| R4.2 → C3.1 | 6.38 | 4.33 | 직렬 저항 출력과 커패시터를 함께 이동 |
| J3.3 → R1.1 / C1.1 → CN7-38 | 42.66 / 43.52 | 19.69 / 34.85 | 왼쪽 전류의 원신호와 필터 출력 동선을 모두 단축 |
| J4.3 → R2.1 / C2.1 → CN7-36 | 42.66 / 44.31 | 25.85 / 25.75 | 오른쪽 전류의 원신호와 필터 출력 동선을 모두 단축 |
| R6.2 → C4.1 / C4.1 → CN7-37 | 29.43 / 8.66 | 24.09 / 8.66 | C4에서 ADC까지의 짧은 배선을 보존 |
| R3.2 → R4.1 / C3.1 → TP5.1 | 5.38 / 5.00 | 22.31 / 8.29 | 왼쪽 온도의 필터 전단 일부와 시험점 경로는 길어짐 |

왼쪽 전류 채널의 첫 개선안은 C1.1 → CN7-38이 33.38 mm였고, 반대층의 전단 분압선과 5.99 mm 구간에서 투영 구리가 겹쳤다. 같은 부품 위치에서 대각선 좌표를 여섯 가지로 바꿔 간격과 연결을 대조했다. 선택한 경로는 34.85 mm이고, 기존에 겹친 긴 구간의 투영 구리 간격은 약 1.48 mm다. 두 네트 사이 투영 간격 1 mm 이내에서 측정한 최장 평행 단일 선분 구간은 0.39 mm다. 1 mm는 기하 검색 기준이다. [두 신호의 확대도와 검사 범위](../../../../09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/exports/TMR_Monitor_Shield_RevA_quality_audit.pdf)

아랫면에 공통 GND 면을 채우고 H1~H3에 와셔용 구리 금지 영역을 두었다. C8.2와 U2.7은 각 핀 근처의 별도 비아로 접지면과 이어진다. 28개 GND 패드가 연결되고 면의 채움 면적은 약 2,894 mm²다. C3.2 → CN7-20은 예전 폭이 정해진 배선을 따라 103.27 mm였다. 새 보드에서는 B.Cu 접지면과 접지 패드·비아 구리를 0.0625 mm 격자로 샘플링해 8방향 최단 경로 예시 42.58 mm를 얻었다. 다른 네트를 가로지르는 대각선 모서리 이동은 허용하지 않았다. 실제 귀환 전류 분포, 임피던스, ADC 오차는 이 거리만으로 정해지지 않는다.

KiCad 10.0.8에서 저장본에 프로젝트 규칙을 적용했다. 활성 22개 네트의 94개 패드가 연결됐으며, 회로도 ERC 오류·경고, DRC 위반, 미배선, 회로도 대조 오류가 모두 0건이다. 제조 전에는 실물 1:1 간섭, 초안 실크, 제조사 규칙과 Gerber·드릴 출력을 확인한다. 전압 감시·보호 동작과 센서 간 영향은 조립 후 실측한다. 별도 CAN 모듈의 전기·기구 통합은 다음 설계 범위다.

- [58쌍의 전후 길이·부품 좌표·평행 배선 비교](comparison.json) · [현재 좌표·간격 원본](geometry.json) · [KiCad 전체 DRC](drc_all.json)
- [재배치 전 PCB](before/TMR_Monitor_Shield_RevA.kicad_pcb) · [이전 PDF 여섯 개](before/exports) · [이전 패드 길이](before/reports/functional_placement_paths.csv)
- [현재 PCB](../../../../09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/TMR_Monitor_Shield_RevA.kicad_pcb) · [현재 검사표와 재현 방법](../../../../09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/reports/README.md)

## 11월 28일 마감 대조

정식 CAD 입력의 보고서 해시, 기본 경로 PDF 7개, 재배치 전후 원본, 현재 PCB의 DRC·ERC 재실행 결과, 관련 문서의 로컬 링크 대상 217개를 대조했다. 일자별 계획·마일스톤·간트 차트에서 미지정 풋프린트와 배선 예정으로 남아 있던 현재 상태를 수정했다. 최종 제작용 Gerber·드릴과 실물 적층은 후속 검토 범위다. [검사 수치와 해시](closeout_checks.json) · [독립 검토 자료](external_review/README.md)
