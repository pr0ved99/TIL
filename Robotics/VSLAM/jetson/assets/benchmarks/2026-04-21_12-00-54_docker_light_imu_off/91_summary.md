# 2026-04-21_12-00-54 Docker light Benchmark Summary

## 자동 요약

- preset: `light`
- IMU: mode `off`, topic `/imu/disabled`, hz `n/a`
- duration: `20s`
- profiles: `424x240x15` / `424x240x15`
- detection rate / queue: `2` / `15`
- image hz: color `14.976`, depth `14.990`
- odom/mapData hz: `10.410` / `1.828`
- odom quality: avg `56.4`, min-max `0~86`
- odom delay: avg `0.1459s`, min-max `0.0889~0.4490s`
- RTAB-Map delay: avg `0.1488s`
- VDD_IN: avg `9018mW`, min-max `8805~9437mW`
- odom_info: matches `111`, inliers `51`, features `111`, local map `360`

## 참고 파일

- [`README.md`](./README.md): 실행 조건과 산출물 설명
- [`10_tegrastats.txt`](./10_tegrastats.txt): Jetson 자원 사용량 원본
- [`11_camera.log`](./11_camera.log): camera service log
- [`12_rtabmap.log`](./12_rtabmap.log): rtabmap service log
- [`20_color_hz.txt`](./20_color_hz.txt): color hz 원본
- [`21_aligned_depth_hz.txt`](./21_aligned_depth_hz.txt): depth hz 원본
- [`22_odom_hz.txt`](./22_odom_hz.txt): odom hz 원본
- [`23_mapdata_hz.txt`](./23_mapdata_hz.txt): mapData hz 원본
