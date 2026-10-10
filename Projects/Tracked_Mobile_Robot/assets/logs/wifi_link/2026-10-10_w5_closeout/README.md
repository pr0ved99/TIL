# W5 마감 증거 — 2026-10-10

[보고서34](../../../../docs/verification/34_W5_PING_DISARM_WebSocket_and_Response_Matching_2026-10-10_ko.md)에서 시험 ID·판정·한계를 확인한다.

| 파일 | 출처와 의미 |
| --- | --- |
| [manifest.json](manifest.json) | 저장소 기준점·snapshot/기록 파일 SHA256. source hash는 플래시 binary hash가 아님 |
| [user_log_excerpts.md](user_log_excerpts.md) | 사용자가 대화에 붙인 serial 로그의 선택 발췌. 전체 원본 capture 아님 |
| [observations.json](observations.json) | 화면의 선택 필드와 사용자 정정/확인 전사. 원본 PNG 아님 |
| [test_validation.json](test_validation.json) | 이 작업에서 실행한 JS57·C21 결과 전사. 전체 콘솔 원본 아님 |
| `source_snapshot/` | 마감 때 저장된 공개 소스·설정·검사 파일의 byte copy. 개인 Wi-Fi header와 binary 제외 |

정확한 날짜가 없는 개별 로그는 ESP uptime으로 날짜를 추정하지 않았다. 실제 보드 관측·PC 함수 검사·사용자 build/flash 보고·미실행 전기/구동 검증을 구분한다. 두 보드 USB 분리 완료는 사용자 확인이다.
