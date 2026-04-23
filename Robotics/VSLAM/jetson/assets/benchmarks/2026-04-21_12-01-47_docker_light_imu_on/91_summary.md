# 2026-04-21_12-01-47 Docker light Benchmark Summary

## 자동 요약

- preset: `light`
- IMU: mode `on`, topic `/imu/data`, hz `69.225`
- duration: `20s`
- profiles: `424x240x15` / `424x240x15`
- detection rate / queue: `2` / `15`
- image hz: color `14.989`, depth `14.992`
- odom/mapData hz: `9.539` / `1.768`
- odom quality: avg `57.1`, min-max `0~84`
- odom delay: avg `0.1592s`, min-max `0.0884~0.4586s`
- RTAB-Map delay: avg `0.1680s`
- VDD_IN: avg `9128mW`, min-max `8780~9477mW`
- odom_info: matches `119`, inliers `63`, features `119`, local map `356`

## 참고 파일

- [`README.md`](./README.md): 실행 조건과 산출물 설명
- [`10_tegrastats.txt`](./10_tegrastats.txt): Jetson 자원 사용량 원본
- [`11_camera.log`](./11_camera.log): camera service log
- [`12_rtabmap.log`](./12_rtabmap.log): rtabmap service log
- [`20_color_hz.txt`](./20_color_hz.txt): color hz 원본
- [`21_aligned_depth_hz.txt`](./21_aligned_depth_hz.txt): depth hz 원본
- [`22_odom_hz.txt`](./22_odom_hz.txt): odom hz 원본
- [`23_mapdata_hz.txt`](./23_mapdata_hz.txt): mapData hz 원본
