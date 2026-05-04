# Mari Nav2 Map Filtering Design

## 결론

Nav2가 쓸 저장 맵은 RGB-D 전체 point cloud를 그대로 2D로 누르는 방식보다, 얇은 `/scan` 기반으로 만들고 저장 후 작은 점 노이즈를 한 번 더 제거하는 방식이 더 안정적이다.

## 목표

```text
깨끗한 바닥은 free
실제 장애물은 occupied
바닥/원거리 depth noise는 제거
Nav2 global costmap은 저장된 map + live /scan 조합으로 사용
```

## 필터링 3단계

### 1. 입력 필터

`depthimage_to_laserscan`에서 depth image 전체가 아니라 얇은 가로 band만 `/scan`으로 변환한다.

기본값:

```text
scan_height=4
range_min=0.35
range_max=3.00
scan_frame=camera_link
```

의도:

- 낮은 카메라가 보는 바닥면을 줄인다.
- 차체/카메라 박스 근처의 자기 장애물성 점을 버린다.
- 먼 거리 depth noise를 줄인다.

### 2. RTAB-Map occupancy 생성 필터

`mari_nav2_map_builder.launch.py`는 RTAB-Map의 2D occupancy grid를 `/scan` 기준으로 만든다.

핵심 파라미터:

```text
Grid/Sensor=0
Grid/3D=false
Grid/RayTracing=true
Grid/Scan2dUnknownSpaceFilled=true
Grid/RangeMin=0.35
Grid/RangeMax=3.00
Grid/CellSize=0.05
```

의도:

- 전체 depth cloud 대신 `/scan`으로 2D map을 만든다.
- sensor와 obstacle 사이의 공간은 free로 지운다.
- 2D 주행에 불필요한 3D occupancy 비용을 줄인다.

### 3. 저장 맵 후처리

`Tools/filter_nav2_saved_map.py`는 저장된 YAML/PGM map에서 작은 occupied 점 노이즈를 제거한다.

기본 명령:

```bash
python3 Tools/filter_nav2_saved_map.py \
  assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap.yaml \
  --output-prefix assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap_filtered \
  --min-occupied-neighbors 1 \
  --min-obstacle-pixels 12
```

더 강한 필터:

```bash
python3 Tools/filter_nav2_saved_map.py \
  assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap.yaml \
  --output-prefix assets/2026-05-01_mari_nav2_saved_map_smoke/stage2_obstacles_rtabmap_filtered \
  --min-occupied-neighbors 2 \
  --min-obstacle-pixels 20
```

주의:

- 너무 강하게 필터링하면 작은 실제 장애물도 지워질 수 있다.
- 필터링 전후 RViz에서 `Map` display만 켜고 비교한다.
- 저장 맵을 고친 뒤에도 live obstacle은 `/scan` obstacle layer가 다시 감지한다.

## 권장 실행 순서

1. Stage 2 Gazebo 실행
2. `mari_nav2_map_builder.launch.py` 실행
3. teleop으로 천천히 주행하며 `/rtabmap/map` 생성
4. `map_saver_cli`로 YAML/PGM 저장
5. `filter_nav2_saved_map.py`로 저장 맵 후처리
6. `mari_nav2_saved_map.launch.py map:=...filtered.yaml` 실행
7. RViz `2D Pose Estimate` 후 `Nav2 Goal`

## 판단 기준

- `Map`만 켰을 때 빈 바닥에 검은 점이 많으면 map 생성/후처리 문제다.
- `Map`은 깨끗한데 costmap만 지저분하면 Nav2 obstacle/inflation 설정 문제다.
- 실제 장애물이 사라졌으면 후처리 강도를 낮춘다.
