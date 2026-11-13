# 10/28 시뮬레이션 학습 — 10/29 마감 근거

학습 회차2026-10-28, 정리2026-10-29(Asia/Seoul). 사용자가 KiCad GUI에서 실행·저장한 원본과 대화 보고를 정리한다. 실제 수행 시각이나 Calendar 시간으로 추정하지 않는다.

| 파일 | 근거 |
| --- | --- |
| [manifest.json](manifest.json) | 저장된 실습 회로·PNG/CSV/워크북·이전 직접 실행 결과의 경로/크기/SHA256 |
| [user_reported_op.txt](user_reported_op.txt) | NTC 두 조건과 전압 세 조건의 사용자 OP 출력 원문 전사 |
| [saved_connectivity.json](saved_connectivity.json) | 최종 저장된 4개 회로의 소자 값·노드, CSV 당시 모든 조건을 대표하지는 않음 |
| `netlists/` | 현재 회로에서 내보낸 읽기 검토용 KiCad XML. 시뮬레이션은 실행하지 않음 |
| [audit_saved_results.py](audit_saved_results.py) | 사용자 CSV/이론식 대조·최종 연결·원래 쉴드 및 무관한 변경의 보존 검사 |
| [validation.json](validation.json) | AC4개×1201점과 전류TRAN15023점의 대조, 수치 표현·보존 결과 |
| [baseline.json](baseline.json) | 마감 시작 시 무관한17개 변경과 제작 쉴드3개 파일의 해시 |

AC CSV의 dB 출력과 이론식 차이는 모두0.000082dB 미만이었다. 전류 계단 CSV와 유한 에지 해석해의 최대 차이는 약16.3µV다. 대조 기준0.002dB/20µV는 CSV 반올림·수치 결과를 확인하는 기준이며 측정 성능 요구나 실물 합격 기준이 아니다.

사용자 PNG/CSV는 [Simulation](../../../../09_Electrical_Design/KiCAD/Simulation/README.md)의 각 폴더 루트에 있다. `01_Current_RC/reports/`는 앞서 Codex가 직접 DLL로 실행한 별도 이력이다. 기존 보고서의 `gui_run: NOT_RUN`은 그 이전 실행의 당시 상태로 보존하고, 사용자 GUI 완료는 이번 근거로 추가한다.

워크북은 설정이며 데이터 자체의 대체물이 아니다. NTC 최종 모델은4147Ω,25°C CSV는10kΩ 조건이다. 사용자가 붙인 커서의 화면 값과 원본 CSV 보간값은 표시 정밀도로 약간 다를 수 있다. 대화 화면 캡처를 별도 로컬 원본 파일로 저장했다고 주장하지 않는다.

[학습 노트20](../../../../07_Embedded_Learning_Notes/01_Concept_Notes/20_KiCad_Current_NTC_Voltage_Simulation_Lab_ko.md) · [설계 판단24](../../../../09_Electrical_Design/24_Monitoring_Input_Simulation_and_Design_Review_2026-10-28_ko.md) · [10/29 마감](../../../../docs/progress/2026-10-29_progress.md).

문서/게시 결과는 별도 publication.json에 기록한다. 원래 쉴드·MCU·실물 변경 및 새 시뮬레이션 실행은 없다. 다음은 전압 오차 예산·보정과 보호 조건이며, 완성 PCB나 전체 MVP의 합격을 뜻하지 않는다.

## 외부 게시 확인

[Notion 학습 노트](https://app.notion.com/p/407a7326f87b81298703fecc5a17ab48)의18절·마지막절·원본그림5개와기존4페이지연결/속성을재조회했다. 기존Calendar시간/제목/알림/반복불변도확인했다. [publication.json](publication.json)에확인응답과내용커밋을저장한다. 노션게시원문은[notion_learning_payload.json](notion_learning_payload.json)이다.
