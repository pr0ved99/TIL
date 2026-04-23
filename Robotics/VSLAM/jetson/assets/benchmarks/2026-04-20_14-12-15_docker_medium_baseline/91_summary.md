# 2026-04-20_14-12-15 Docker medium Benchmark Summary

## 자동 요약

- preset: `medium`
- IMU: mode `n/a`, topic `n/a`, hz `n/a`
- duration: `20s`
- profiles: `640x360x15` / `640x360x15`
- detection rate / queue: `2` / `20`
- image hz: color `14.300`, depth `14.983`
- odom/mapData hz: `5.310` / `1.522`
- odom quality: avg `325.2`, min-max `0~494`
- odom delay: avg `0.2020s`, min-max `0.1007~0.5248s`
- RTAB-Map delay: avg `0.2749s`
- VDD_IN: avg `7103mW`, min-max `6705~8661mW`
- odom_info: matches `448`, inliers `335`, features `801`, local map `892`

## 참고 파일

- [`README.md`](./README.md): 실행 조건과 산출물 설명
- [`10_tegrastats.txt`](./10_tegrastats.txt): Jetson 자원 사용량 원본
- [`11_camera.log`](./11_camera.log): camera service log
- [`12_rtabmap.log`](./12_rtabmap.log): rtabmap service log
- [`20_color_hz.txt`](./20_color_hz.txt): color hz 원본
- [`21_aligned_depth_hz.txt`](./21_aligned_depth_hz.txt): depth hz 원본
- [`22_odom_hz.txt`](./22_odom_hz.txt): odom hz 원본
- [`23_mapdata_hz.txt`](./23_mapdata_hz.txt): mapData hz 원본
