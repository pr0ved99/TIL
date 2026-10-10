# 시험·빌드 증거 보존 절차

작성: **2026-10-11**. 다음 시험부터 원본과 판정의 연결을 남기기 위한 기록 방법이다.
시험 동작·허가 조건은 해당 plan/report를 따른다. 이 문서 작성은 시험 실행·빌드·플래시 완료를 뜻하지 않는다.

## 현재 보존 상태와 한계

- [W5 보고서34](34_W5_PING_DISARM_WebSocket_and_Response_Matching_2026-10-10_ko.md): 소스 byte snapshot·사용자 로그 발췌·화면/확인 전사·PC 결과 전사를 보존했다. 원본 PNG·전체 serial capture·플래시 바이너리 hash는 미기록이다.
- [10/11 기록](../progress/2026-10-11_progress.md): parser/ticket/owner 실제 저장본 PC15/12/9 PASS와 사용자 ESP 빌드 성공을 기록했다. 원본 빌드 로그·바이너리 hash·새 플래시/보드 실행은 미확인이다.
- 과거 원본을 확보하지 못하면 `미보존/미제공`으로 유지한다. 발췌·재작성·후속 재실행을 과거 원본으로 대체하지 않는다. 증거 보완만을 위해 변경 없는 완료 시험을 다시 요구하지 않는다.

## 기록 순서

1. **시험 전:** Test ID, 목적/PASS 기준, 실제 연결·전원/모터 조건, hook 설정, 저장소 branch/HEAD와 미커밋 변경 여부를 기록한다. PC 검사인지 보드/전기/기계 시험인지 구분한다.
2. **빌드:** 사용자가 수행한 전체 빌드 출력과 성공/실패를 저장한다. 앱/target/도구 버전, 실제 소스 hash와 산출물 BIN/ELF hash를 기록한다. 빌드가 없었던 시험에는 `빌드 미실행`이라고 적는다.
3. **플래시:** 사용자가 수행한 대상 보드·포트·파일·성공/verify 출력을 저장한다. 기록한 산출물과 실제 flash 파일이 같은지 확인한다. 단순 성공 메시지나 소스 hash만 있으면 바이너리 동일성은 미확인으로 남긴다.
4. **실행:** 시험 전 상태부터 요청·응답·종료/복구까지 시리얼 출력을 가능한 한 연속 보존한다. ESP `boot_id`/uptime와 STM `t_ms`를 각각 기록한다. 모니터 실행이 리셋을 유발했는지도 관측으로 남기며 uptime을 실제 날짜로 환산하지 않는다.
5. **화면/계측:** 원본 PNG·사진·로직 캡처를 저장하고 채널/프로브 지점·단위·샘플레이트·도구/모드·배선 조건을 적는다. 분석 JSON이나 요약은 원본과 별도 파일로 남긴다.
6. **마감:** 관측한 수치와 PASS/PARTIAL/FAIL/미실행의 범위를 적는다. 최종 출력·전원 분리 등 물리 동작은 사용자 확인 또는 관측이 있을 때만 기록한다. 다음 조치와 미확인 증거를 명시한다.

전체 시리얼 로그가 없으면 제공된 구간만 `발췌`로 저장한다. PC 결과도 실행 대상/모드·검사 수·SKIP/ERROR·종료값을 함께 남긴다.
비밀번호·토큰이 포함된 원본은 공개 저장소에 올리지 않고, 공개용 발췌에는 제외 범위와 원본 hash를 기록한다. 개인 설정 header는 기존 Git 제외 규칙을 유지한다.

## 폴더와 파일 구성

실제 시험이 생기면 `assets/logs/<영역>/YYYY-MM-DD_<test_id>_<run>/`에 README·로그·manifest를 보존한다.
PNG/사진과 계측 원본은 기존 `assets/screenshots/`, `assets/photos/`, `assets/captures/`에 두고 상대 링크로 연결해도 된다.
시도별 파일을 덮어쓰지 않으며 실패/제외 시도도 유효 시도와 구분한다.

| 파일/필드 | 남길 내용 |
| --- | --- |
| `README.md` | Test ID·날짜/시간대·목적·조건·판정·증거 링크·한계·다음 조치 |
| `build_console.txt`, `flash_console.txt` | 실제 수행했을 때의 전체 출력. 보드/app/산출물 대응 |
| `serial_raw.txt` | 보존한 연속 구간과 시작/끝 상태. 발췌인 경우 별도 이름과 범위 |
| 원본 화면·사진·캡처 | 이름·출처·측정 설정. 전사/가공본과 분리 |
| `manifest.json` | 원본/파생 구분·파일 경로·byte 수·SHA256, 소스/산출물/플래시 연결의 확인 수준 |
| progress/report | 해당 증거가 뒷받침하는 범위와 미확인 조건. 과거 날짜 기록에 소급 적용하지 않음 |

아래는 **미실행 기록용 틀**이다. 실제 관측한 항목만 채우고 알 수 없는 값은 null/미확인으로 둔다.

```json
{
  "test_id": "AC-B01",
  "run": "run01",
  "observed_at": null,
  "timezone": "Asia/Seoul",
  "status": "NOT_RUN",
  "git_branch": null,
  "git_head": null,
  "working_tree_dirty": null,
  "app": null,
  "power_and_wiring": null,
  "source_sha256": null,
  "built_binary_sha256": null,
  "flashed_binary_identity": "unconfirmed",
  "files": [],
  "evidence_limits": []
}
```

## hash 기록 예시

사용자가 ESP Wi-Fi 앱을 빌드한 뒤 **`03_Firmware/esp32_wifi_link` 폴더**에서 산출물을 확인할 때의 예시다.
이 명령은 파일 식별값만 읽으며 빌드/플래시를 수행하지 않는다.

```powershell
Get-FileHash -LiteralPath .\build\esp32_wifi_link.bin -Algorithm SHA256
Get-FileHash -LiteralPath .\build\esp32_wifi_link.elf -Algorithm SHA256
git rev-parse HEAD
git status --short
```

STM32도 실제 빌드가 생성한 ELF/BIN 파일의 경로를 확인해 hash를 기록한다. 파일이 없거나 어느 파일을 플래시했는지 모르면 값을 추정하지 않는다.
현재 작업본 hash, 보존된 source snapshot hash, 빌드 산출물 hash와 flash/runtime 동일성은 각각 별개의 사실이다.

## 문서 마감 확인

진행/판정이 바뀌면 현재 인수인계·진행 색인·관련 plan/report와 함께 프로젝트/앱/분야 README·Memory의 현재 요약도 대조한다.
과거 기록은 날짜를 유지하고, 오래된 ‘현재/다음’을 새 재개 지시로 읽지 않도록 후속 기준을 연결한다.
상대 링크·섹션 앵커·보존 파일 hash를 확인하고 개인 설정·생성 빌드 파일을 문서 커밋과 구분한다.
