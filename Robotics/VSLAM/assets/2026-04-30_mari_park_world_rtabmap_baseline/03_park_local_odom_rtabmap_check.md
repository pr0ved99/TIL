# Mari RTAB-Map Check - park_local_odom

## Summary

- checked_at: `2026-04-30T07:31:10.584678+00:00`
- duration_sec: `20.0`
- odom_topic: `/odometry/local`
- rtabmap_namespace: `/rtabmap`

## Topics

| status | label | topic | count | rate_hz | summary |
| --- | --- | --- | ---: | ---: | --- |
| OK | odom input | `/odometry/local` | 600 | 29.96 | frame=odom child=base_footprint x=1.363 y=-0.001 |
| OK | rgb image input | `/camera/camera/color/image_raw` | 300 | 14.98 | frame=camera_color_optical_frame size=424x240 encoding=rgb8 |
| OK | depth image input | `/camera/camera/aligned_depth_to_color/image_raw` | 300 | 14.98 | frame=camera_color_optical_frame size=424x240 encoding=32FC1 |
| OK | rgb camera info input | `/camera/camera/color/camera_info` | 300 | 14.98 | frame=camera_color_optical_frame size=424x240 |
| OK | rtabmap info output | `/rtabmap/info` | 52 | 2.61 | frame=map ref_id=85 loop=0 wm=12 stats=106 |
| OK | rtabmap map data output | `/rtabmap/mapData` | 52 | 2.61 | frame=map nodes=1 poses=12 links=84 |
| OK | rtabmap cloud map output | `/rtabmap/cloud_map` | 12 | 0.58 | frame=map size=6450x1 points=6450 |
| OBS | rtabmap map graph output | `/rtabmap/mapGraph` | 12 | 0.58 | frame=map poses=12 links=83 |
| OBS | rtabmap path output | `/rtabmap/mapPath` | 52 | 2.61 | frame=map poses=12 |
| OBS | rtabmap occupancy map output | `/rtabmap/map` | 12 | 0.58 | frame=map size=146x145 resolution=0.050 |
| OBS | tf | `/tf` | 1699 | 84.89 | transforms=1 first=odom->base_footprint |

## RTAB-Map Info

- ref_id: `85`
- loop_closure_id: `0`
- proximity_detection_id: `0`
- working_memory_size: `12`
- local_path_size: `0`
- odom_cache_poses: `0`
- stats_count: `106`

## Selected Stats

| key | value |
| --- | ---: |
| `Keypoint/Index_memory_usage/KB` | 102552 |
| `Loop/Accepted_hypothesis_id/` | 0 |
| `Loop/Angular_variance/` | 0 |
| `Loop/Distance_since_last_loc/m` | 3.90907 |
| `Loop/Highest_hypothesis_id/` | 1 |
| `Loop/Highest_hypothesis_value/` | 0.09674 |
| `Loop/Hypothesis_ratio/` | 0 |
| `Loop/Hypothesis_reactivated/` | 1 |
| `Loop/Id/` | 0 |
| `Loop/Landmark_detected/` | 0 |
| `Loop/Landmark_detected_node_ref/` | 0 |
| `Loop/Last_id/` | 0 |
| `Loop/Linear_variance/` | 0 |
| `Loop/MapToBase_lin_std/m` | 1.41609 |
| `Loop/MapToBase_lin_var/m2` | 2.00531 |
| `Loop/MapToBase_pitch/deg` | 0 |
| `Loop/MapToBase_roll/deg` | 0 |
| `Loop/MapToBase_x/m` | 1.30019 |
| `Loop/MapToBase_y/m` | -0.0108101 |
| `Loop/MapToBase_yaw/deg` | -0.0375525 |
