# 배터리측 전압 채널 배치 확인 — 2026-11-06

**최신 도면 안내 · 2026-11-07:** 이 폴더는 당시 배치 스냅샷으로 보존한다. 현재 회로도와 ERC·부품 표기 최신화 결과는 [11/7 CAD 마감](../2026-11-07_cad_closeout/README.md)을 따른다.

사용자가 Monitor Shield에 J7/R7~R11/C5의7개 부품을 직접 추가했다. 최초 검토 [placement.pdf](placement.pdf)와 [review.json](review.json)은 위치 조정 전 기록이다.

이후 실제 저장 파일에서 다음 이동을 확인했다. Codex가 이 회로도를 수정한 것은 아니다.

| 부품 | 확인한 기준점(mm) | 판단 |
| --- | --- | --- |
| J7 | x50.8, y184.15 | 위100mil 이동.2번 핀이 y186.69의 R7/R8/R10 신호선과 정렬됨 |
| R9 | x127, y194.31 | 아래300mil 이동. 분압 분기로 배치됨 |
| C5 | x152.4, y194.31 | 아래300mil 이동. 필터 분기로 배치됨 |

[위치 조정 후 PDF](aligned.pdf) · [저장 파일 해시·확인 결과](alignment_check.json).

총31부품이다. 새7부품의14핀은 아직 미연결이며, 다음은 [설계27](../../../../09_Electrical_Design/27_Voltage_2Ch_Schematic_Contract_Comparison_2026-11-06_ko.md)의 전단 분압·필터 배선이다. 위치 확인과 배선/ERC 완료를 구분한다.
