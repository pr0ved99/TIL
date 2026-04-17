# 2026-04-17 RTAB-Map Viz XCB Display Error

## 증상

- `Jetson`에서 `RTAB-Map` launch는 올라오지만 `rtabmap_viz`가 아래 오류와 함께 종료된다.

```text
qt.qpa.xcb: could not connect to display
Could not load the Qt platform plugin "xcb"
```

## 현재까지 확인된 것

- `/rtabmap/rgbd_odometry`, `/rtabmap/rtabmap` 노드와 관련 topic은 살아 있다.
- 즉, 현재 문제는 `RTAB-Map` 전체 실패가 아니라 GUI display context 문제에 가깝다.

## 현재 판단

- 비GUI shell이나 `SSH` 성격의 shell에서는 `rtabmap_viz`를 바로 띄우기 어렵다.
- GUI 확인은 `Jetson`에 직접 연결한 그래픽 세션에서 다시 보는 편이 맞다.

## 임시 운영 원칙

- 비GUI shell에서는 node/topic/log 기준으로 baseline 성공 여부를 본다.
- 직접 연결한 화면에서는 `rtabmap_viz`, `rqt_image_view`, `RViz`를 다시 확인한다.
