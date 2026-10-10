# T-ESTOP-005A 증거 보존

[보고서 27](../../../../docs/verification/27_T_ESTOP_005A_Motor_Disconnected_Rail_and_Safe_Restore_Report_2026-09-23_ko.md)의 근거다.

- 원본: [logic_analyzer](../../../captures/logic_analyzer/)의 `2026-09-22_T_ESTOP_005A_run01`~`run06` `.sr/.pvs`.
- [manifest.json](manifest.json): 프로젝트 루트 기준 파일 경로·크기·SHA-256.
- `runNN_summary.json`: 당시 저장된 raw bit/UART 분석과 명령·응답 대조. 마감 시 6개 원본 hash 일치를 확인했다.
- `runNN_D4.txt`, `runNN_D4_lines.json`: **STM→ESP** TEL/ACK/ERR.
- `runNN_D5.txt`, `runNN_D5_lines.json`: **ESP→STM** 명령. 이전 T004의 D4/D5 역할과 반대다.
- run05/06 `boot_details.json`: 부팅 전이·invalid-stop 후보를 정상 프레임과 구분한 보조 분석.
- [decode_sr.py](decode_sr.py): 당시 사용한 기본 decoder. 저장된 summary의 수동 보강 항목까지
  자동 생성하는 도구는 아니다. `python decode_sr.py <capture.sr>`는 별도 임시 폴더에 파생 파일을 쓴다.
- [safe_restore_artifacts.json](safe_restore_artifacts.json): 현재 소스/ELF/BIN 식별과 증거 경계.

원본 `.sr`을 재검토 기준으로 삼는다. `.pvs`는 화면/decoder 설정이며 분석 결과 자체가 아니다.
DMM 수치는 사용자 대화 보고로 보고서에 보존하며 디지털 파형에서 유도한 값으로 취급하지 않는다.
run03은 ESP 유실 자극이 성립하지 않은 시험으로 보존한다. 전체 T005A는 PARTIAL이다.
