# 2026-04-23 작업 일지

## 결론

- 오늘 가장 중요한 결과는 `turtle_CAD` 자료의 중국어 파일명/폴더명을 영어로 정리하고, 구매한 것으로 보이는 `R3` 궤도형 섀시 후보 자료만 따로 분리해 비교 가능한 상태로 만든 것이다.
- 오늘 작업은 Jetson에서 센서나 Docker를 실행한 것이 아니라, **노트북 로컬에서 CAD 자료 정리, 3D 모델 확인 환경 준비, URDF/Xacro 작성을 위한 사전 준비**를 진행한 것이다.
- `mari.stl`의 Onshape import 오류는 단위 문제보다 메쉬 결함 가능성이 크다는 점을 확인했고, 발표용/시각화용 STL과 설계용 STEP을 구분해서 써야 한다는 기준을 정리했다.
- 다음 작업의 1순위는 **분리한 궤도형 섀시 CAD를 기준으로 `base_link`, `camera_link`, `imu_link` 위치 후보를 정리하고 URDF/Xacro 초안을 시작하는 것**이다.

## 오늘 작업 한 줄 요약

- 노트북에서 WHEELTEC 섀시 CAD 자료를 정리하고, 궤도형 후보 섀시 자료만 따로 복제해 비교 가능한 작업 폴더를 만들었다.
- 왜 이 작업을 먼저 했는가?
  - 자율주행과 VSLAM에 필요한 센서 장착 위치를 정의하려면 먼저 실제 섀시 형상, 브라켓 위치, 부품별 구조를 확인할 수 있어야 하기 때문이다.

## 시간순 기록

### 10:00

- `/home/ssafy/Desktop/turtle_CAD` 폴더 전체를 분석해 어떤 종류의 섀시 자료가 들어 있는지 확인했다.
- 주요 대상이 `WHEELTEC R1/R3/R3X/TT` 계열 섀시 자료라는 점을 확인했고, 설치 영상, 3D 모델, CAD 도면이 섞여 있는 구조라는 점을 파악했다.
- 이후 검색과 비교가 가능하도록 중국어 파일명/폴더명을 영어로 정리하기로 결정했다.

```bash
find /home/ssafy/Desktop/turtle_CAD -maxdepth 5 -type d
find /home/ssafy/Desktop/turtle_CAD -type f | sed -n '1,200p'
```

### 10:40

- 중국어 파일명/폴더명을 영어로 rename했다.
- rename 과정에서 원본 경로와 최종 경로를 나중에 추적할 수 있도록 manifest를 만들었다.
- 결과적으로 중국어 파일명이 남지 않도록 정리했다.

```bash
python3 -m pip install --user deep-translator
python3 - <<'PY'
# 중국어 파일명/폴더명 번역 및 rename 실행
PY
```

### 11:20

- rename 이후 결과를 검증했다.
- 중국어 파일명이 남아 있는지, 비ASCII 이름이 남아 있는지 확인했다.
- 검증 결과 `remaining_cjk_paths = 0`, `non_ascii_filenames = 0`이었다.

```bash
python3 - <<'PY'
from pathlib import Path
import re
root=Path('/home/ssafy/Desktop/turtle_CAD')
cjk=re.compile(r'[\u4e00-\u9fff]')
hits=[p for p in root.rglob('*') if cjk.search(p.name)]
print('remaining_cjk_paths', len(hits))
PY
```

### 12:00

- 현재 구매한 섀시가 무엇인지 추정하기 위해 `R1`, `R3`, `R3X`, `TT`, `Tracked`, `Ackermann`, `Mecanum`, `Omni`, `Differential` 관련 경로를 분리해 조사했다.
- 그 결과 궤도형 섀시 관련 자료는 `Tracked` 키워드 아래 정리되어 있다는 점을 확인했다.
- 특히 `R3_Standard_Version_Tracked_Robot_Car`와 `R3_High_Config_Version_Tracked_Robot_Car`가 실제 구매 후보로 보인다는 결론에 도달했다.

```bash
find /home/ssafy/Desktop/turtle_CAD -type d -iname '*Tracked*' | sort
find /home/ssafy/Desktop/turtle_CAD -type f \( -iname '*Tracked*' -o -iname '*Track*' \) | sort
```

### 13:00

- 구매 후보로 보이는 두 궤도형 섀시 자료만 따로 복제해 별도 비교 폴더를 만들었다.
- 이렇게 분리해두면 원본 자료 전체를 뒤질 필요 없이, 실제 후보 섀시에 필요한 `.stp`, `.dwg`, `.pdf`, `.mp4`만 빠르게 비교할 수 있다.
- 복제본은 Jetson용이 아니라 **로컬 설계/검토용 작업 폴더**라는 점을 명확히 했다.

```bash
mkdir -p /home/ssafy/Desktop/R3_Tracked_Chassis_Selected_20260423
python3 - <<'PY'
# Standard / High_Config tracked chassis 자료 복제
PY
```

### 14:00

- FreeCAD와 Onshape를 기준으로 `.stp`, `.dwg`, `.stl` 파일을 어떻게 볼지 정리했다.
- 설계 구조 보존과 URDF/Xacro 추출 가능성을 고려하면 `.stp/.step`이 주 경로이고, `.stl`은 시각화나 메쉬 용도라는 기준을 세웠다.
- Onshape import 옵션은 assembly 구조 보존을 위해 `Split into multiple documents`를 유지하는 방향으로 정리했다.

```bash
freecad
xdg-open "/home/ssafy/Desktop/R3_Tracked_Chassis_Selected_20260423"
```

### 15:00

- `mari.stl`를 Onshape에 import할 때 발생한 오류 원인을 분석했다.
- 파일 자체를 검사한 결과, 단위 선택 문제가 아니라 `non-manifold edge`, `duplicate face` 같은 메쉬 결함이 주요 원인으로 보였다.
- 따라서 설계 목적에는 STL보다 STEP을 우선 사용해야 한다는 판단을 정리했다.

```bash
python3 - <<'PY'
# binary STL 구조, triangle 수, non-manifold edge, duplicate face 분석
PY
freecadcmd -c "import Mesh; m=Mesh.Mesh('/home/ssafy/Desktop/turtle_CAD/mari.stl'); print(m.CountFacets)"
```

### 15:40

- Onshape 업로드 테스트용으로 `mari.stl`의 수리본을 별도로 만들었다.
- 이 수리본은 시각화 테스트용으로는 의미가 있지만, CAD 편집 기준의 정확한 원본 대체물은 아니라는 점도 같이 정리했다.
- 메쉬 수리와 CAD 원본 유지의 차이를 구분해서 다루기로 했다.

```bash
freecadcmd -c "import Mesh; src='/home/ssafy/Desktop/turtle_CAD/mari.stl'; dst='/home/ssafy/Desktop/turtle_CAD/mari_repaired_for_onshape.stl'; m=Mesh.Mesh(src); m.removeDuplicatedFacets(); m.removeDuplicatedPoints(); m.removeNonManifolds(); m.fixSelfIntersections(); m.write(dst)"
```

### 16:20

- 자율주행/VSLAM 관점에서 지금 해야 할 일이 단순히 3D 파일을 보는 것이 아니라, **센서의 실제 위치를 좌표계로 정의하고 URDF/Xacro에 반영하는 사전 준비 작업**이라는 점을 다시 정리했다.
- 즉, 지금 CAD를 보는 목적은 섀시 위에 `D435i`, `IMU`, `Jetson`이 어디에 올라갈지 결정하고, 나중에 `base_link -> camera_link -> imu_link` 관계를 정의하기 위한 것이다.
- 따라서 오늘 CAD 정리는 VSLAM과 직접 연결되는 준비 단계라고 판단했다.

## 오늘 관찰한 핵심 현상

- `turtle_CAD` 자료는 단순히 한 개의 섀시가 아니라 `R1`, `R3`, `R3X`, `TT` 계열 전체가 섞인 대형 벤더 패키지였다.
- 파일명을 영어로 정리한 뒤 경로 탐색 속도가 크게 좋아졌고, 후보 섀시를 빠르게 좁힐 수 있었다.
- 궤도형 자료는 `R3_Chassis` 아래 `Tracked` 관련 경로로 모여 있었다.
- `mari.stl`는 파일 크기나 triangle 수 자체보다 메쉬 위상 문제가 import 오류에 더 큰 영향을 주고 있었다.
- 설계용 CAD와 시각화용 mesh는 목적이 다르므로 확장자를 구분해서 써야 한다는 점이 분명해졌다.

## 원인 가설

- 처음에는 Onshape import 오류가 `meter/mm` 단위 선택 문제라고 생각했다.
- 하지만 메쉬를 직접 확인한 결과, 핵심 원인은 STL 자체의 메쉬 결함 가능성이 더 높다고 판단했다.
- 처음에는 파일 확장자만 맞으면 URDF/Xacro 준비가 가능하다고 생각할 수 있었지만, 실제로는 **assembly 구조 유지 여부와 센서 장착 위치 확인 가능성**이 더 중요했다.

## 확인 방법

- `find`, `du`, `file`, Python 스크립트로 CAD 자료 구조와 용량을 먼저 확인했다.
- `Tracked` 키워드 기준으로 궤도형 섀시 자료만 따로 필터링했다.
- FreeCAD와 Onshape 사용 흐름을 비교해 `.stp`와 `.stl`의 용도 차이를 정리했다.
- `freecadcmd`, Python STL 파싱 스크립트로 triangle 수, 중복 면, 비매니폴드 여부를 확인했다.

## 해결 방법

- 중국어 파일명은 영어 파일명으로 정리해 검색 가능성을 높였다.
- 구매 후보 섀시는 별도 폴더로 복제해 원본 자료와 분리했다.
- Onshape import는 `.stp/.step` 중심으로 가져가고, assembly 구조를 유지하는 옵션을 우선 적용하기로 했다.
- STL 오류는 단위 조정보다 메쉬 수리 또는 STEP 원본 사용이 우선이라는 기준을 정했다.

## 오늘 배운 것

- VSLAM용 로봇 모델링에서 CAD를 보는 목적은 단순 시각화가 아니라 **센서 위치와 좌표계 정의를 준비하는 것**이다.
- `.stp/.step`은 설계와 구조 유지에 유리하고, `.stl`은 메쉬 기반 시각화에 더 가깝다.
- Onshape에서 URDF 쪽으로 이어가려면 부품이 한 덩어리로 합쳐진 형태보다 assembly 구조가 살아 있는 import가 유리하다.
- CAD 정리 작업도 결국 `base_link`, `camera_link`, `imu_link` 설계로 이어지는 VSLAM 준비 작업의 일부라는 점을 이해했다.

## 오늘 만든/수정한 파일

- [2026-04-23 작업 일지](/home/ssafy/my_ws/git_hub/Robotics/VSLAM/daily/2026-04-23/README.md)
- [rename manifest](/home/ssafy/Desktop/turtle_CAD/rename_manifest_20260423.tsv)
- [rename final manifest](/home/ssafy/Desktop/turtle_CAD/rename_manifest_final_20260423.tsv)
- [tracked chassis selected README](/home/ssafy/Desktop/R3_Tracked_Chassis_Selected_20260423/README.md)
- [Mari repaired STL](/home/ssafy/Desktop/turtle_CAD/mari_repaired_for_onshape.stl)

## 증빙 자료

- [R3 tracked chassis selected folder README](/home/ssafy/Desktop/R3_Tracked_Chassis_Selected_20260423/README.md)
- [Standard tracked 3D model](/home/ssafy/Desktop/R3_Tracked_Chassis_Selected_20260423/Standard_Version/R3_Standard_Version_Tracked_Robot_Car/R3_Standard_Version_Tracked_Vehicle_Customer_3D_Model/Standard_Version_Small_Tracked_Robot_Car_-3D_Model.stp)
- [High config tracked 3D model](/home/ssafy/Desktop/R3_Tracked_Chassis_Selected_20260423/High_Config_Version/R3_High_Config_Version_Tracked_Robot_Car/R3_High_Config_Version_Tracked_Vehicle_Customer_3D_Model/High_Config_Tracked_Vehicle_-3D_Model.stp)

## 남은 문제

- 아직 실제 구매 섀시가 `Standard tracked`인지 `High config tracked`인지 최종 확정하지 않았다.
- 센서 위치를 정의하려면 실제 섀시 실물과 CAD를 대조해서 `camera`, `imu`, `jetson` 장착 위치를 측정해야 한다.
- URDF/Xacro 초안은 아직 작성하지 않았다.
- Onshape에서 STEP import 후 assembly 구조가 원하는 수준으로 유지되는지 실제 확인이 더 필요하다.

## 다음 액션

1. `R3_Standard_Version_Tracked_Robot_Car`와 `R3_High_Config_Version_Tracked_Robot_Car`의 차이를 실물 사진과 비교해 실제 구매품을 확정한다.
2. 확정된 섀시를 기준으로 `base_link`, `camera_link`, `imu_link` 후보 위치를 표로 정리한다.
3. Onshape 또는 FreeCAD에서 센서 장착 위치를 확인한 뒤 URDF/Xacro 초안을 시작한다.

## 한 줄 회고

- 오늘 작업을 한 문장으로 요약하면, **Jetson 실험 대신 로컬 CAD 자료를 정리해 VSLAM용 로봇 모델과 센서 좌표계 설계를 시작할 준비를 끝낸 날**이었다.
