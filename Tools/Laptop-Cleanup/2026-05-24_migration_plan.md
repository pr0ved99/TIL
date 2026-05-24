# Laptop Return Migration Plan

Date: 2026-05-24
Host: `ssafy-960XGL`
Purpose: 노트북 반납 전 필요한 자료를 GitHub 또는 Google Drive로 이전하기 위한 실행 계획

## Conclusion

자료 이전 기준은 다음과 같다.

- GitHub: 코드, Markdown 문서, 작은 설정 파일, 프로젝트 인덱스
- Google Drive: 영상, 발표자료, CAD, RTAB-Map DB, 시뮬레이션 asset, 설치파일, 개인 금융/제출 서류
- Local only or discard: 재생성 가능한 cache, build output, IDE database, package cache

현재 Google Drive는 로컬 마운트가 확인되지 않았고 `rclone`도 설치되어 있지 않다.
따라서 먼저 GitHub에 올릴 자료를 푸시하고, Google Drive 대상은 목록을 확정한 뒤 브라우저 또는 Drive client로 업로드한다.

## GitHub Upload Targets

These files are small and useful as source-controlled project records.

| Status | Path | Reason |
|---|---|---|
| upload now | `Tools/Laptop-Cleanup/2026-05-24_git_preservation_review.md` | GitLab/GitHub 보존 판단 기록 |
| upload now | `Tools/Laptop-Cleanup/2026-05-24_migration_plan.md` | 노트북 반납 전 이전 계획 |
| upload now | `Projects/Tracked_Mobile_Robot/` | 개인 궤도 로봇 프로젝트 문서 워크스페이스 |
| already tracked | `Embedded/ESP32-S3/` | ESP32-S3 실습 기록 |
| already tracked | `Embedded/STM32/` | STM32/F446RE 실습 기록 |
| already tracked | `Robotics/VSLAM/` | VSLAM/ROS2 학습 기록 |

Do not upload to GitHub:

- GitLab project source trees as-is
- `.git-credentials`
- `.ssh`
- personal finance files
- raw videos
- `.db` map databases
- `.usd`, `.usda`, `.pt`, collected simulation assets
- installer archives

## Google Drive Upload Targets

### High Priority

| Path | Approx size | Reason |
|---|---:|---|
| `/home/ssafy/Desktop/Send Anywhere (2026-05-20 21-44-56).zip` | 5.4G | transferred phone/video bundle |
| `/home/ssafy/Desktop/Send Anywhere (2026-05-20 21-44-56)/` | 5.1G | extracted bundle, likely duplicate of zip |
| `/home/ssafy/Desktop/IMG_1880.mov` | 1.8G | raw phone/video evidence |
| `/home/ssafy/Desktop/echo_turtle.pptx` | 105M | presentation source |
| `/home/ssafy/Desktop/Echo Trutle 반 발표.pdf` | 99M | presentation export |
| `/home/ssafy/Desktop/Echo Turtle Project.pdf` | 117M | presentation/export material |
| `/home/ssafy/Desktop/turtle_CAD/` | 6.1G | chassis/CAD/reference materials |
| `/home/ssafy/rtabmap_maps/` | 1.9G | RTAB-Map result DBs |
| `/home/ssafy/duri_rtabmap_db/` | 1.6G | Duri RTAB-Map DB/export |
| `/home/ssafy/Videos/Screencasts/` | 2.9G total under Videos | demo/evidence recordings |

### Project-Specific Large Assets

| Path | Approx size | Reason |
|---|---:|---|
| `/home/ssafy/my_ws/git_lab/S14P21C206/sim/arm/assets/maps` | 9.3G | Isaac/SmartFactory collected assets |
| `/home/ssafy/my_ws/git_lab/S14P21C206/sim/arm/assets/smart_flow_env_v1_arm6.usda` | 1.8G | simulation scene asset |
| `/home/ssafy/my_ws/git_lab/S14P21C206/sim/arm/assets/smart_flow_env_v2_arm6.usda` | 1.8G | simulation scene asset |
| `/home/ssafy/my_ws/git_lab/S14P21C206/sim/arm/assets/simulation_env_v1.usd` | 506M | simulation scene asset |
| `/home/ssafy/my_ws/git_lab/S14P21C206/sim/arm/docs/videos` | 26M | portfolio/demo evidence |

### Personal or Administrative Files

Upload manually and keep private.

| Path | Reason |
|---|---|
| `/home/ssafy/Desktop/현대카드_소비패턴_분석.md` | personal finance analysis |
| `/home/ssafy/Desktop/보조배터리_가격별_6월까지_지출계획.md` | personal finance planning |
| `/home/ssafy/Desktop/토스뱅크_거래내역.xlsx` | personal bank statement |
| `/home/ssafy/Desktop/최근 이용 내역-현대카드.pdf` | personal card statement |
| `/home/ssafy/Downloads/*동의서*.docx` | SSAFY administrative document |
| `/home/ssafy/Downloads/*진료확인서*` | personal medical/admin document |

## Probably Discard or Recreate

Review once before deleting, but these are not migration priorities.

| Path | Reason |
|---|---|
| `/home/ssafy/.cache/ov` | Omniverse cache, large and reproducible |
| `/home/ssafy/.cache/pip` | pip package cache |
| `/home/ssafy/.vscode/browse.vc.db` | VSCode browse database |
| `/home/ssafy/Desktop/.vscode/browse.vc.db` | VSCode browse database |
| `/home/ssafy/my_ws/.vscode/browse.vc.db` | VSCode browse database |
| `/var/log/journal` | system logs |
| `/home/ssafy/Downloads/code_*.deb` | VS Code installers, re-downloadable |
| `/home/ssafy/Downloads/stm32cubemx-*.zip` | installer, re-downloadable |
| `/home/ssafy/Downloads/st-stm32cubeide_*.sh*` | installer, re-downloadable |
| `/home/ssafy/cuda-repo-ubuntu2204-13-1-local_*.deb` | CUDA local installer, re-downloadable if version is recorded |

## Recommended Folder Structure on Google Drive

```text
Laptop_Return_Backup_2026-05/
  01_Project_Evidence/
    Duri_RTABMap/
    S14P21C206_SmartFactory/
    Echo_Turtle_Presentation/
  02_CAD_and_Hardware_Refs/
    turtle_CAD/
    WHEELTEC/
  03_Videos/
    Desktop_SendAnywhere/
    Screencasts/
  04_Personal_Private/
    Finance/
    SSAFY_Admin/
  05_Installers_Optional/
```

## Execution Order

1. Push GitHub targets first.
2. Create the Google Drive folder structure.
3. Upload high-priority project evidence and CAD files.
4. Upload private/admin files manually.
5. After upload, verify file count and size.
6. Only after verification, delete local cache and duplicated archives.

## Verification Checklist

- GitHub `main` contains the cleanup plan and project workspace.
- Google Drive has the expected top-level folders.
- At least one large uploaded file is downloaded or previewed successfully.
- Sensitive files are in a private Drive folder, not public GitHub.
- Local deletion happens only after upload verification.

