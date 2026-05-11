# Git Branch Strategy Guide

> Git Flow 기반 + GitLab MR 워크플로우

## 결론

- `main`은 배포된 안정 버전만 유지한다.
- 일상 개발은 `dev`로 통합하고, 실제 작업은 `feat/*`, `fix/*`, `refactor/*` 브랜치에서 진행한다.
- 직접 push 대신 `issue -> branch -> commit -> push -> MR -> squash merge` 흐름을 기본으로 사용한다.
- 이 문서에서는 원문에 섞여 있던 표기를 정리해, 실제 운영 브랜치 이름을 `dev`, `feat/*`, `fix/*`, `refactor/*`, `hotfix/*`, `release/*`로 통일한다.

## 1. 브랜치 구조

```text
main ← 배포 완료된 안정 버전
 └── release/* ← 배포 준비 (QA, 핫픽스)
      └── dev ← 통합 개발 브랜치
           ├── feat/* ← 기능 개발
           ├── fix/* ← 버그 수정
           ├── refactor/* ← 리팩토링
           └── hotfix/* ← 긴급 수정 (main에서 분기)
```

### 브랜치 역할

| 브랜치 | 용도 | 보호 | 머지 대상 |
| --- | --- | --- | --- |
| `main` | 배포된 안정 코드 | Protected (직접 push 금지) | `release/* -> main` |
| `release/*` | 배포 전 QA 및 안정화 | Protected | `dev -> release/*`, `release/* -> main` |
| `dev` | 통합 개발 브랜치 | Protected (MR only) | `feat/*`, `fix/*`, `refactor/*` |
| `feat/*` | 기능 개발 | - | `dev` |
| `fix/*` | 버그 수정 | - | `dev` |
| `refactor/*` | 리팩토링 | - | `dev` |
| `hotfix/*` | 긴급 배포 수정 | - | `main`, `dev` |

## 2. 파트 구성 및 Prefix

| 파트 | Prefix | 예시 |
| --- | --- | --- |
| Frontend | `[FE]` | `[FE] feat: 홈 대시보드 UI 구현` |
| Backend | `[BE]` | `[BE] feat: 쓰레기 데이터 API 설계` |
| Embedded | `[EM]` | `[EM] feat: 흡입 모듈 모터 제어` |
| AI/ML | `[AI]` | `[AI] feat: 쓰레기 인식 모델 학습` |
| Infra | `[INFRA]` | `[INFRA] feat: CI/CD 파이프라인 구축` |
| 공통/기타 | `[ALL]` | `[ALL] docs: README 업데이트` |

## 3. 이슈 타이틀 컨벤션

### 형식

```text
[파트] type: 제목
```

### type 종류

| type | 용도 |
| --- | --- |
| `feat` | 기능 개발 |
| `fix` | 버그 해결 |
| `refactor` | 리팩토링 |

### 예시

```text
[FE] feat: qr 인터랙션 페이지 구현
[BE] feat: 쓰레기 데이터 수집 api 설계
[EM] fix: 흡입 모터 pwm 신호 오류 수정
[AI] feat: yolov8 기반 담배꽁초 인식 모델 학습
[INFRA] refactor: docker compose 구조 개선
[ALL] docs: readme 업데이트
```

## 4. 브랜치 네이밍 컨벤션

### 형식

```text
{이슈번호}-{type}-{간단설명}
```

- 띄어쓰기는 하이픈(`-`) 사용
- 케밥 케이스를 사용
- 이슈 번호를 앞에 두어 GitLab 이슈, 브랜치, MR 연결을 쉽게 유지

### type 종류

| type | 용도 |
| --- | --- |
| `feat` | 새 기능 |
| `fix` | 버그 수정 |
| `refactor` | 리팩토링 |
| `hotfix` | 긴급 수정 |

### 예시

```text
42-feat-trash-detection-model
58-fix-motor-calibration
71-refactor-api-response-structure
99-hotfix-sensor-timeout
```

> GitLab 이슈에서 `Create branch`를 사용하면 이슈 번호 포함 브랜치를 만들기 쉽다.
> 이 규칙을 따르면 이슈 ↔ 브랜치 ↔ MR 추적이 쉬워진다.

## 5. 커밋 메시지 컨벤션

### 규칙

- 한 커밋에는 한 가지 문제만 담는다.
- 제목은 소문자 사용, 끝에 `.` 금지
- 제목은 한글 기준 25자 이내, 영문 기준 50자 이내 권장
- 본문은 필요할 때만 작성
- 나누기 어렵다면 파일 단위로 커밋

### 형식

```text
type: 간단한 설명
```

### 예시

```text
feat: qr 인터랙션 페이지 구현
fix: 쓰레기 위치 좌표 변환 오류 수정
refactor: 모터 드라이버 코드 구조 개선
feat: yolov8 기반 담배꽁초 인식 모델 추가
chore: docker 이미지 경량화
```

### 핵심 type

| type | 설명 |
| --- | --- |
| `feat` | 새로운 기능 추가 |
| `fix` | 버그 수정 |
| `refactor` | 코드 리팩토링 (기능 변화 없음) |
| `chore` | 빌드 설정, 패키지 매니저 수정, 기타 설정 변경 |
| `docs` | 문서 관련 |
| `style` | formatting, 세미콜론 수정 등 동작 변화 없는 수정 |

### 확장 type

| type | 설명 |
| --- | --- |
| `test` | 테스트 코드 추가/수정 |
| `perf` | 성능 개선 |
| `design` | UI 디자인 변경 |
| `comment` | 주석 추가/변경 |
| `init` | 프로젝트 초기 파일 생성 |
| `rename` | 파일/폴더 이름 변경만 수행 |
| `remove` | 파일 삭제만 수행 |
| `!BREAKING CHANGE` | 큰 API 변경 |
| `!HOTFIX` | 치명적 긴급 수정 |

## 6. MR 타이틀 / Description 규칙

MR 타이틀은 Jira 키를 포함해 작성한다. Squash Merge를 사용하면 `dev` 브랜치 로그에서 어떤 Jira 이슈의 작업인지 바로 추적할 수 있다.

```text
[파트] S14P31C205-<이슈번호>/ type: 제목
```

예시:

```text
[EM] S14P31C205-678/ feat: RTAB-Map 멀티세션 기반 지도 재사용 검증
```

MR Description은 아래 형식을 사용한다.

```markdown
## ⭐ Jira Ticket Number

- Closes #S14P31C205-<이슈번호>

## ✨ 작업 내용
- 작업 내용 1
- 작업 내용 2

## 🖥 스크린샷
- 관련 캡처, 영상, 문서 경로

## ✅ 체크리스트
- [ ] 브랜치 방향 확인 (`S14P31C205-<이슈번호>-<type>-<slug>` → `dev`)
- [ ] 최신 `dev` 내용 반영
- [ ] 로컬에서 정상 작동 확인 (Build & Run)
- [ ] 불필요한 주석 및 콘솔 출력 제거 확인
- [ ] 커밋 메시지 컨벤션 준수 확인
- [ ] 셀프 코드 리뷰 완료
```

실제 작성 예시:

```markdown
## ⭐ Jira Ticket Number

- Closes #S14P31C205-678

## ✨ 작업 내용
- RTAB-Map 멀티세션 DB 신규 생성/재사용 절차 정리
- `delete_db_on_start:=true/false` 기준에 따라 record/reuse 스크립트 분리
- Mari Gazebo 기반 RTAB-Map launch에 DB 경로 및 재사용 옵션 반영
- `databaseViewer` 기반 DB 저장/재사용 확인 결과와 캡처 자료 정리

## 🖥 스크린샷
- `edge/jetson/assets/2026-05-06_rtabmap_multisession_db_reuse/01_mari_rtabmap_multisession_db_viewer_nodes.png`

## ✅ 체크리스트
- [x] 브랜치 방향 확인 (`S14P31C205-678-feat-rtabmap-multisession-map-reuse` → `dev`)
- [x] 최신 `dev` 내용 반영
- [x] 로컬에서 RTAB-Map DB 생성/재사용 결과 확인
- [x] 불필요한 주석 및 콘솔 출력 제거 확인
- [x] 커밋 메시지 컨벤션 준수 확인
- [x] 셀프 코드 리뷰 완료
```

## 7. 전체 워크플로우

```text
① 이슈 생성 (템플릿 선택)
    ↓
② 이슈에서 브랜치 생성 (네이밍 컨벤션 준수)
    ↓
③ 로컬에서 작업 + 커밋 (커밋 컨벤션 준수)
    ↓
④ 원격으로 push
    ↓
⑤ MR 생성 (템플릿 선택, Jira 키 포함 타이틀 사용)
    ↓
⑥ 코드 리뷰 + Approve (최소 1명)
    ↓
⑦ Squash Merge → dev
    ↓
⑧ 이슈 자동 Close (MR 템플릿의 Closes # 활용)
```

### 실행 시 체크포인트

1. 이슈 생성
   - Title은 `[파트] type: 제목` 형식 사용
   - Template, Assignee, Label 선택
2. 이슈에서 브랜치 생성
   - `{이슈번호}-{type}-{간단설명}` 형식 준수
3. 작업 후 커밋
   - 커밋 메시지 컨벤션 준수
4. 원격 push
5. MR 생성
   - source branch 선택
   - target branch는 `dev`
   - Title은 `[파트] S14P31C205-<이슈번호>/ type: 제목` 형식 사용
   - MR 템플릿 선택
   - Description의 `Closes #S14P31C205-<이슈번호>` 확인
   - `Assign to me`, Label 지정
   - `Squash commits when merge` 활성화

## 8. Release 플로우

```text
① dev에서 release/v1.0.0 브랜치 분기
    ↓
② QA 진행 → 발견된 버그는 release 브랜치에서 직접 수정
    ↓
③ QA 완료 → main으로 Merge + 태그 생성 (v1.0.0)
    ↓
④ main → dev로 역머지 (release 수정사항 반영)
    ↓
⑤ release 브랜치 삭제
```

## 9. Hotfix 플로우

```text
① main에서 hotfix/이슈번호-hotfix-설명 브랜치 분기
    ↓
② 긴급 수정 후 MR → main 머지 + 태그 (v1.0.1)
    ↓
③ main → dev로 역머지
    ↓
④ hotfix 브랜치 삭제
```

## 10. 이슈 & MR 템플릿 목록

### 이슈 템플릿

| 템플릿 | 용도 |
| --- | --- |
| `✨_기능개발` | 새로운 기능 개발 |
| `🐛_버그수정` | 버그 리포트 및 수정 |
| `🔄_리팩토링` | 코드 개선 |
| `🔧_인프라` | CI/CD, 배포, 환경 설정 |
| `📝_문서` | 문서 작성 및 수정 |

### MR 템플릿

| 템플릿 | 용도 |
| --- | --- |
| `🤩_Merge_Request` | 일반 MR (`dev` 머지용) |
| `🚀_Release` | 릴리즈 MR (`main` 머지용) |
| `🔥_Hotfix` | 긴급 수정 MR (`main` 직접 머지용) |

## 11. Label 체계

| Label | 색상 | 용도 |
| --- | --- | --- |
| `FE` | 파랑 | Frontend |
| `BE` | 초록 | Backend |
| `EM` | 주황 | Embedded |
| `AI` | 보라 | AI/ML |
| `INFRA` | 회색 | Infra |
| `bug` | 빨강 | 버그 |
| `enhancement` | 노랑 | 기능 개선 |
| `urgent` | 빨강 | 긴급 |
