# UR-02 첫 사용자 저장본 검토 — PAGE 복원 필요

2026-10-16. 사용자 복사·저장 후 실제 파일을 읽었다. 이번 저장본은 **전체 확인 미통과**다.

- [첫 저장본 스냅샷](wifi_link_main.c), [해시](source_manifest.json): 기본0U와 시험 8개 블록은 포함됐다.
  후보 대비 기능상 문제는 기존 PAGE JavaScript 전체와 종결 세미콜론의 주석 처리다.
  STATUS_JSON_SIZE 선언 위치·빈 줄·설명 주석 위치 차이는 기능에 영향을 주지 않는다.
- [adapter 검사](adapter_results.txt): 함수만 추출하는 기존 42개와 mode1/2 통과.
  PAGE 선언을 컴파일하지 않는 범위의 PASS이며 전체 소스 PASS가 아니다.
- [PAGE C 실패](page_compile_failure.txt): native C로 실제 주석·매크로·PAGE 초기화 구문을
  컴파일하자 `unexpected end of file`. ESP SDK 빌드는 실행하지 않았다.
- [수정 검토 사본](page_fix_review/wifi_link_main.c), [검사 출력](page_fix_review/pc_results.txt),
  [manifest](page_fix_review/source_manifest.json): PAGE 범위만 완전한 블록으로 교체한 별도 사본.
  mode0/1/2 PAGE C·HTML 확인, mode0 비활성+42개, mode1/2 STM 파서·경합·실패 검사 PASS.

[가이드 4-2](../../../../docs/plans/2026-10-16_UART_Partial_Command_Test_Code_Guide_ko.md)는
`static const char PAGE[] =`부터 `static int status_json(...)` 직전까지 전체 교체하도록 보완했다.
마지막 JavaScript·HTML 종결과 세미콜론까지 포함하며 다른 7개 블록을 재입력할 필요는 없다.

**실제 펌웨어는 Codex가 수정하지 않았다.** 사용자가 PAGE를 복원한 뒤 저장본 재검토가 필요하다.
보드 빌드·플래시·실물 주입은 미완료다.
