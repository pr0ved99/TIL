# UR-02 수동 주입 입력 전 후보

2026-10-16. 실제 펌웨어는 수정하지 않고 `uart_partial_test_candidate.py`로 만든 후보다.

- [검토용 C 전체](wifi_link_main.c): 기본 `WIFI_UART_PARTIAL_TEST_MODE=0U`.
- [PC 출력](pc_results.txt): native TCC `-Wall -Werror`, 기본 비활성 및 W5/main 42개 회귀 검사,
  임시 mode1/2 실제 STM 파서 연결과 실패 경로, LF-only 반례 검출.
- [manifest](source_manifest.json): 원본 펌웨어·검사 파일·후보 SHA256, 원본 미변경 확인.
- [사용자 입력 가이드](../../../../docs/plans/2026-10-16_UART_Partial_Command_Test_Code_Guide_ko.md).

가이드의 설정·PAGE 머리·5개 함수·시험 블록을 원본에 적용했을 때 검토 후보와 전체 문자열이
일치함을 확인했다. UTF-8/LF 정규화 후보 SHA256:
`215cd704f66ccb15a520a0397675d3a553ebf61be887d797dfa96a2b972302b7`.
Windows 저장 파일의 실제 바이트 해시는 manifest에 별도로 기록한다.

PC mock은 SDK 전체 빌드·RTOS 태스크 실경합·선로 수신·전기 출력 증거가 아니다.
사용자 입력, 실제 저장본 검토, 사용자 보드 빌드/플래시, 부분 CMD/ARM 실물 캡처는 미완료다.
UR-02 전체 및 AC-S는 PARTIAL을 유지한다.
