# 2026-04-20_14-12-51 Docker compare Benchmark Summary

## 자동 요약

- preset: `compare`
- duration: `20s`
- profiles: `424x240x15` / `424x240x15`
- detection rate / queue: `3` / `20`
- image hz: color `14.986`, depth `14.980`
- odom/mapData hz: `7.783` / `2.490`
- odom quality: avg `186.9`, min-max `0~312`
- odom delay: avg `0.1960s`, min-max `0.1013~0.2504s`
- RTAB-Map delay: avg `0.2021s`
- VDD_IN: avg `7399mW`, min-max `7210~8820mW`
- odom_info: matches `425`, inliers `186`, features `545`, local map `1389`

## 참고 파일

- [`README.md`](./README.md): 실행 조건과 산출물 설명
- [`10_tegrastats.txt`](./10_tegrastats.txt): Jetson 자원 사용량 원본
- [`11_camera.log`](./11_camera.log): camera service log
- [`12_rtabmap.log`](./12_rtabmap.log): rtabmap service log
- [`20_color_hz.txt`](./20_color_hz.txt): color hz 원본
- [`21_aligned_depth_hz.txt`](./21_aligned_depth_hz.txt): depth hz 원본
- [`22_odom_hz.txt`](./22_odom_hz.txt): odom hz 원본
- [`23_mapdata_hz.txt`](./23_mapdata_hz.txt): mapData hz 원본
