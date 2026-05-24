# Ubuntu Laptop Git Preservation Review

Date: 2026-05-24
Host: `ssafy-960XGL`
Target archive repo: `https://github.com/pr0ved99/TIL.git`

## Conclusion

노트북 정리 과정에서 GitLab 프로젝트에는 더 이상 커밋하지 않는다.
대신 개인 GitHub TIL repo에 정리 판단, 남겨야 할 경로, 외부 백업 후보를 문서로 남긴다.

이번 문서는 삭제/이동/커밋/푸시 전에 만든 보존 판단 기록이다.
GitLab 작업트리는 그대로 두고, 이 문서만 GitHub 개인 계정에 푸시한다.

## Current Policy

- GitLab repo에는 새 commit을 만들지 않는다.
- GitHub TIL에는 보존 판단 문서만 남긴다.
- 대용량 `.usd`, `.usda`, `.pt`, `.db`, 영상 파일은 GitHub에 직접 올리지 않는다.
- GitLab의 미추적 파일이나 local branch는 사용자가 확인하기 전 삭제하지 않는다.
- `.git-credentials` 같은 인증 파일은 읽거나 복사하지 않는다.

## Priority Repos

| Priority | Path | State | Decision |
|---|---|---|---|
| P0 | `/home/ssafy/my_ws/git_lab/S14P31C205` | modified/untracked files exist | GitLab commit 없이 보존 후보만 기록 |
| P0 | `/home/ssafy/my_ws/git_lab/S14P21C206` | code changes plus large Isaac assets | Git과 외부 백업 후보를 분리 |
| P1 | `/home/ssafy/my_ws/git_lab/labs/projects/petner/main` | `portfolio_petner.md` untracked | GitHub/portfolio 문서로 옮길지 별도 판단 |
| P1 | `/home/ssafy/1. skeleton01` | many deleted files, no upstream | 실습 자료 보존 여부 확인 후 archive/delete |
| P2 | `/home/ssafy/my_ws/git_hub` | personal TIL repo | cleanup docs만 commit/push |

## S14P31C205 Notes

Path: `/home/ssafy/my_ws/git_lab/S14P31C205`

Observed branch:

```text
S14P31C205-1329-feat-hardware-action-final
```

Observed changed files:

| File or path | Meaning | Keep? |
|---|---|---|
| `edge/jetson/ros2_ws/src/trashbot_description/CMakeLists.txt` | teleop scripts install target added | yes |
| `edge/jetson/ros2_ws/src/trashbot_description/scripts/teleop_mari_keyboard.py` | incremental key teleop option added | yes |
| `edge/jetson/ros2_ws/src/trashbot_localization/scripts/cmd_vel_to_motor.py` | duplicated motor scale declaration removed | yes |
| `edge/jetson/ros2_ws/src/trashbot_navigation/rviz/duri_nav2_presentation.rviz` | presentation RViz layout | yes |
| `edge/jetson/assets/presentation_nav2_rviz/` | Nav2 goal smoke/local-goal evidence text files | yes |

Follow-up review:

- `cmd_vel_to_motor.py` staged diff removes duplicated declarations only.
- `left_motor_scale` and `right_motor_scale` validation/application logic remains.
- The RViz/evidence files are small enough to preserve somewhere, but current policy is not to commit them to GitLab.

Evidence captured in the local GitLab checkout:

- `20260520_152847_goal_smoke/05_odom_after_goal.txt`: odom x about `0.4057 m`
- `20260520_154142_local_goal/05_odom_after_goal.txt`: odom x about `0.4039 m`
- `/cmd_vel` evidence shows ramping from `0.03` to `0.12`

Recommended handling:

- Do not commit this to GitLab.
- If the project evidence is still needed later, copy it into a separate archive folder or external drive.
- Keep this GitHub note as the index pointing back to the original local path.

## S14P21C206 Notes

Path: `/home/ssafy/my_ws/git_lab/S14P21C206`

Changed code candidates:

- `sim/arm/scripts/3_rebuild_RL/0_2_logging_location_simulation_env_v1.py`
- `sim/arm/scripts/3_rebuild_RL/0_5_place_rolltainer_moving_box_simulation_env_v1.py`

Large/non-Git candidates:

| Path | Approx size | Handling |
|---|---:|---|
| `sim/arm/assets/maps` | `9.3G` | external backup candidate |
| `sim/arm/assets/smart_flow_env_v1_arm6.usda` | `1.8G` | external backup candidate |
| `sim/arm/assets/smart_flow_env_v2_arm6.usda` | `1.8G` | external backup candidate |
| `sim/arm/assets/simulation_env_v1.usd` | `506M` | external backup or LFS only |
| `sim/arm/logs` | `55M` | keep selected logs only |
| `sim/arm/docs/videos` | `26M` | keep if portfolio evidence |

Recommended handling:

- Do not add assets/models/logs directly to GitHub TIL.
- If preserving this work, create a compact README-style evidence summary in GitHub and put binary artifacts in external storage.

## PetNer Notes

Path: `/home/ssafy/my_ws/git_lab/labs/projects/petner/main`

- Untracked file: `portfolio_petner.md`
- Approx size: `12K`

Recommended handling:

- Decide whether this is a portfolio document worth moving into GitHub TIL.
- Avoid committing inside the GitLab mirror unless the project repo itself needs it.

## GitHub TIL Notes

Path: `/home/ssafy/my_ws/git_hub`

Current repo purpose:

- 개인 학습/TIL 기록
- 노트북 정리 판단 문서 저장
- GitLab 작업 결과의 큰 바이너리 대신 작은 요약과 경로 인덱스 보존

Not included in this cleanup commit:

- `Projects/Tracked_Mobile_Robot/`
- GitLab project source files
- large binary assets
- credential files

## Next Actions

1. Push this cleanup note to GitHub TIL.
2. Decide whether `Projects/Tracked_Mobile_Robot/` should be included in a separate GitHub commit.
3. Review `S14P21C206` large assets and choose external backup target.
4. Review Desktop and Downloads after Git/GitHub preservation is done.

