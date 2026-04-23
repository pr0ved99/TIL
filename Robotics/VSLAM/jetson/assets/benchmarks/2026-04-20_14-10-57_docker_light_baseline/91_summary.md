# 2026-04-20_14-10-57 Docker light Benchmark Summary

## 자동 요약

- preset: `light`
- IMU: mode `n/a`, topic `n/a`, hz `n/a`
- duration: `20s`
- profiles: `424x240x15` / `424x240x15`
- detection rate / queue: `2` / `15`
- image hz: color `14.989`, depth `14.989`
- odom/mapData hz: `14.991` / `1.874`
- odom quality: avg `198.7`, min-max `0~254`
- odom delay: avg `0.1270s`, min-max `0.0852~0.1855s`
- RTAB-Map delay: avg `0.1581s`
- VDD_IN: avg `6777mW`, min-max `6586~8385mW`
- odom_info: matches `245`, inliers `214`, features `398`, local map `394`

## 참고 파일

- [`README.md`](./README.md): 실행 조건과 산출물 설명
- [`10_tegrastats.txt`](./10_tegrastats.txt): Jetson 자원 사용량 원본
- [`11_camera.log`](./11_camera.log): camera service log
- [`12_rtabmap.log`](./12_rtabmap.log): rtabmap service log
- [`20_color_hz.txt`](./20_color_hz.txt): color hz 원본
- [`21_aligned_depth_hz.txt`](./21_aligned_depth_hz.txt): depth hz 원본
- [`22_odom_hz.txt`](./22_odom_hz.txt): odom hz 원본
- [`23_mapdata_hz.txt`](./23_mapdata_hz.txt): mapData hz 원본
