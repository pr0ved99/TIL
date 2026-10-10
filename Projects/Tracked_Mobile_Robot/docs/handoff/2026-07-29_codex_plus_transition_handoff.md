# 2026-07-29 Codex Plus Transition Handoff

## Purpose

사용자 제공 일정 기준으로 2026-08-06 이후 ChatGPT Pro에서 Plus로 전환할 때, `Tracked_Mobile_Robot` 프로젝트를 과도한 Codex 사용량 없이 계속 진행하기 위한 설정 및 운용 절차다.

Plus에서도 Codex를 사용할 수 있다. 다만 Pro보다 사용 여유가 작으므로, 기본 작업은 가벼운 설정으로 수행하고 복잡한 판단이 필요한 순간에만 모델과 추론 강도를 올리는 방식으로 전환한다.

> 상태: 전환 준비 문서만 작성했다. 아래 Plus 설정은 아직 적용하지 않았다.

## Current State Before Transition

2026-07-29 기준 사용자 전역 설정 파일은 다음 경로에 있다.

```text
C:\Users\eyh12\.codex\config.toml
```

현재 성능 관련 핵심값은 다음과 같다.

```toml
model = "gpt-5.6-sol"
model_reasoning_effort = "low"
service_tier = "priority"
```

- `gpt-5.6-sol`: 복잡하고 개방적인 작업에 적합한 최상위 모델
- `low`: 현재 추론 강도는 이미 낮게 설정되어 있음
- `priority`: Plus 전환 후 기본 사용량 절약을 위해 제거할 항목
- Windows sandbox, trusted project, plugin, MCP 설정은 Plus 전환과 무관하므로 그대로 유지한다.
- `openaiDeveloperDocs` MCP는 2026-07-29 공식 문서 확인을 위해 등록했다. Plus 전환 필수 항목은 아니며 삭제할 필요도 없다.

## Target Plus Baseline

Plus 전환 후 전역 설정의 성능 관련 부분은 아래를 기준으로 한다.

```toml
model = "gpt-5.6-terra"
model_reasoning_effort = "low"

[agents]
max_concurrent_threads_per_session = 1
default_subagent_model = "gpt-5.6-luna"
default_subagent_reasoning_effort = "low"
```

적용 원칙:

- 기존 `service_tier = "priority"` 줄은 삭제한다.
- `[features].fast_mode = true`가 나중에 추가되어 있다면 삭제하거나 `false`로 바꾼다.
- 기존 `[windows]`, `[projects...]`, `[plugins...]`, `[mcp_servers...]` 블록은 삭제하지 않는다.
- `gpt-5.6-terra` 또는 `gpt-5.6-luna`가 당시 모델 선택기에 보이지 않으면 강제로 사용하지 말고, 사용 가능한 권장 모델을 확인한 뒤 이 문서를 갱신한다.

이 기준을 택한 이유:

- Terra는 일상적인 코드 작성, 파일 검사, 문서화와 Git 작업에 적합하다.
- Luna는 명확하고 반복적인 로그 정리나 요약에 적합하다.
- Low reasoning은 범위가 명확한 작업의 기본값으로 사용한다.
- 동시 서브에이전트를 1개로 제한하면 불필요한 병렬 사용을 줄일 수 있다.
- GPT-5.6 Fast 모드는 속도가 약 1.5배지만 Standard 대비 크레딧을 2.5배 사용하므로 Plus의 상시 기본값으로 두지 않는다.

## Transition-Day Procedure

### 1. 현재 설정 백업

PowerShell에서 실행한다.

```powershell
Copy-Item "$env:USERPROFILE\.codex\config.toml" `
  "$env:USERPROFILE\.codex\config.pro-2026-08-06.toml" -Force
```

백업 확인:

```powershell
Get-Item "$env:USERPROFILE\.codex\config.pro-2026-08-06.toml"
```

### 2. 설정 파일 편집

```powershell
notepad "$env:USERPROFILE\.codex\config.toml"
```

다음 작업만 수행한다.

1. `model`을 `gpt-5.6-terra`로 변경한다.
2. `model_reasoning_effort`를 `low`로 유지한다.
3. `service_tier = "priority"`를 삭제한다.
4. 파일 끝에 `[agents]` 블록을 추가한다.
5. 다른 trust, Windows, plugin, MCP 설정은 보존한다.

### 3. Codex 재시작

- 열려 있는 Codex 데스크톱 앱과 IDE 확장을 완전히 닫았다가 다시 연다.
- 기존 대화는 이전 모델 선택을 유지할 수 있으므로 새 대화에서 검증한다.
- 2026-07-29 등록한 `openaiDeveloperDocs` MCP도 재시작 후 새 세션에서 인식되는지 확인한다.

### 4. 모델과 속도 확인

- 앱 또는 IDE의 모델 선택기에서 기본값이 Terra/Low인지 확인한다.
- CLI에서는 `/model`로 현재 모델과 reasoning을 확인하거나 변경한다.
- CLI에서 `/fast status`를 실행한다.
- Fast가 켜져 있으면 `/fast off`를 실행한다.
- 사용량은 Codex 설정의 Usage 화면 또는 표시되는 limit banner에서 확인한다.

### 5. 프로젝트 smoke test

TIL 저장소 루트에서 다음을 실행한다.

```powershell
Set-Location C:\Users\eyh12\workspace\TIL
git status --short -- Projects/Tracked_Mobile_Robot
```

그 다음 새 대화에서 다음처럼 요청한다.

```text
Tracked_Mobile_Robot의 최신 handoff와 최신 progress만 먼저 읽고,
현재 상태와 다음 한 가지 작업을 요약해줘. 파일은 수정하지 마.
```

다음 조건이면 전환 검증 통과다.

- 저장소와 최신 문서를 정상적으로 읽는다.
- 기존 사용자 수정 파일을 임의로 되돌리지 않는다.
- 현재 프로젝트 상태와 다음 작업을 짧게 정확히 설명한다.
- 단순 상태 확인에 전체 저장소나 모든 architecture 문서를 읽지 않는다.

## Model and Reasoning Rules

| Work | Default | Raise only when |
| --- | --- | --- |
| 파일 확인, Markdown, Git 상태, 짧은 코드 수정 | Terra + Low | 여러 파일의 동작 관계를 추론해야 할 때 |
| STM32 기능 구현, encoder 속도 계산, 상태 머신 | Terra + Medium | 문제 원인이 불명확하거나 안전 판단이 얽힐 때 |
| 시스템 구조, 복합 디버깅, 중요한 설계 검토 | Sol + Medium | 한 번의 분석 정확도가 사용량보다 중요할 때 |
| 로그 분류, 표 변환, 반복 요약 | Luna + Low | 결과가 계속 부정확할 때 Terra로 변경 |
| 전원·모터 안전 판단 | Terra 또는 Sol + Medium | Luna에 맡기지 않음 |

운용 규칙:

- 우선 Low로 시작하고 결과가 부족할 때만 Medium으로 올린다.
- High, Extra High, Max는 일반 진행에 사용하지 않는다.
- Ultra는 둘 이상의 독립 작업을 실제로 병렬화할 가치가 있을 때만 사용한다.
- 복잡한 작업을 마치면 다음 새 대화부터 Terra + Low로 돌아온다.
- Fast는 긴급하게 응답 시간을 줄여야 하는 짧은 세션에서만 일시적으로 켠다.

## Project Context Rules For Plus

Plus에서 가장 중요한 절약 방법은 매 요청마다 프로젝트 전체를 다시 읽지 않게 하는 것이다.

### New session minimum read set

기본적으로 다음만 읽는다.

1. `PROJECT_MEMORY.md`의 현재 상태와 다음 작업
2. `docs/progress/`의 최신 progress 1개
3. `docs/handoff/`의 최신 작업 handoff 1개
4. 이번 작업과 직접 관련된 firmware, verification 또는 design 문서

다음 자료는 필요할 때만 읽는다.

- 전체 프로젝트 `README.md`
- 모든 architecture 문서
- 오래된 progress/handoff
- 전체 로그 원문
- 현재 작업과 무관한 firmware tree

### Session discipline

- 한 대화에는 한 가지 검증 목표를 둔다.
- 먼저 `rg` 또는 파일 목록으로 후보를 좁힌 뒤 필요한 파일만 연다.
- 긴 로그는 원본 전체 대신 실패 전후 구간과 저장 경로를 제공한다.
- 사용자가 직접 타이핑하는 학습 방식이면 한 단계씩 안내하고, 완료 후 해당 부분만 검사한다.
- 작업 종료 시 progress와 handoff를 갱신해 다음 세션의 재탐색을 줄인다.
- 단순 작업에는 서브에이전트를 사용하지 않는다.
- 서로 독립적인 조사나 검증이 두 개 이상일 때만 서브에이전트 1개를 사용한다.

### Recommended later cleanup

Plus 전환 시 프로젝트 `AGENTS.md`의 `Read First`를 위 minimum read set 중심으로 축소하는 별도 작업을 진행한다. 이 변경은 프로젝트 작업 방식에 영향을 주므로 이 문서 작성 시점에는 적용하지 않았다.

## Usage Warning Signs

다음 상황이 반복되면 설정과 작업 범위를 다시 줄인다.

- 짧은 작업인데도 Usage가 빠르게 감소한다.
- 매 대화 시작 때 동일한 대형 문서를 전부 읽는다.
- 상태 확인만 요청했는데 다수의 서브에이전트가 생성된다.
- 간단한 문서 작업에 Sol 또는 High 이상이 계속 선택된다.
- Fast가 항상 켜져 있다.
- 하나의 대화에서 하드웨어, 펌웨어, CAD, 문서화를 모두 이어서 수행한다.

Plus의 정확한 사용량은 고정된 메시지 수가 아니다. 공식 안내상 작업 크기와 복잡도, 모델, 실행 위치, 긴 세션 여부에 따라 달라지며 Codex 외 일부 agentic 기능과 같은 사용량 풀을 공유할 수 있다. 숫자를 문서에 고정하지 말고 당시 Usage 화면을 기준으로 판단한다.

## Rollback

설정 변경 후 모델 접근 오류나 작업 품질 문제가 생기면 백업을 복원한다.

```powershell
Copy-Item "$env:USERPROFILE\.codex\config.pro-2026-08-06.toml" `
  "$env:USERPROFILE\.codex\config.toml" -Force
```

복원 후 Codex 앱과 IDE 확장을 완전히 재시작한다.

백업 전체를 복원하지 않고 품질만 보완하려면 다음 순서로 한 단계씩 올린다.

1. Terra + Low 유지, 요청 범위를 더 명확히 작성
2. Terra + Medium
3. Sol + Low 또는 Medium
4. 필요한 작업 한 번만 Fast 또는 더 높은 reasoning 사용

## Do Not Do

- Plus 전환 전에 현재 Pro 설정을 미리 낮추지 않는다.
- `config.toml`의 trust, sandbox, plugin, MCP 블록을 통째로 덮어쓰지 않는다.
- 토큰, GitHub 인증 정보 또는 비밀값을 handoff 문서에 복사하지 않는다.
- 하드웨어 안전 검증을 Luna 요약 결과만으로 확정하지 않는다.
- Usage 절약을 이유로 빌드, 계측, 로그와 회로 연속성 검증을 생략하지 않는다.

## Official References

2026-07-29 확인 기준이며, 전환 당일 다시 확인한다.

- [ChatGPT plans and Plus/Pro feature comparison](https://chatgpt.com/pricing/)
- [Using Codex with your ChatGPT plan](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan)
- [Codex models](https://developers.openai.com/codex/models)
- [Codex speed and Fast mode](https://developers.openai.com/codex/speed)
- [Codex configuration reference](https://developers.openai.com/codex/config-reference)

## Next Action

2026-08-06 또는 실제 Pro 종료 직후 이 문서의 Transition-Day Procedure를 실행한다. 전환 smoke test가 통과한 뒤, 별도 커밋으로 프로젝트 `AGENTS.md`의 기본 읽기 범위를 축소한다.
