# 감지 분기 보호 비교 계산 — 2026-11-13

[설계30 조건표·판단](../../../../09_Electrical_Design/30_Voltage_Sense_Branch_Protection_Comparison_2026-11-13_ko.md) · [계산](calculate.py) · [결과](comparison.json).

Rp=0/100/1000/2200Ω의 정상16V/TMUX ON/RON2Ω DC 전달비, Rp 뒤 감지선의GND단락 전류·전력, C1 지배 근사와 추가Rp 공차를 계산한다. 독립2노드KCL로 정상 전압8개를 대조한다. 실행은 이 폴더의calculate.py이며 결과comparison.json을 재생성한다.

2.2kΩ은 우선 검토값이며 채택/제작/실측 결과가 아니다. 저항이 정상이고 공급16V인 지속 고장을 가정했다. 과도·외부 이상 입력·저항 자체 고장은 포함하지 않았다. 소스 해시는 계산 시 확인한 원본을 가리키며 CAD 변경 없음. 새SPICE/빌드/플래시·실물 시험 없음.
