# Mari RTAB-Map Check - local_odom

## Summary

- checked_at: `2026-04-29T13:20:02.349764+00:00`
- duration_sec: `20.0`
- odom_topic: `/odometry/local`
- rtabmap_namespace: `/rtabmap`

## Topics

| status | label | topic | count | rate_hz | summary |
| --- | --- | --- | ---: | ---: | --- |
| OK | odom input | `/odometry/local` | 200 | 9.99 | frame=odom child=base_footprint x=1.744 y=-0.267 |
| OK | rgb image input | `/camera/camera/color/image_raw` | 166 | 8.31 | frame=camera_color_optical_frame size=640x480 encoding=rgb8 |
| OK | depth image input | `/camera/camera/aligned_depth_to_color/image_raw` | 88 | 4.46 | frame=camera_color_optical_frame size=640x480 encoding=32FC1 |
| OK | rgb camera info input | `/camera/camera/color/camera_info` | 298 | 14.90 | frame=camera_color_optical_frame size=640x480 |
| OK | rtabmap info output | `/rtabmap/info` | 43 | 2.12 | frame=map ref_id=81 loop=0 wm=15 stats=106 |
| OK | rtabmap map data output | `/rtabmap/mapData` | 39 | 1.92 | frame=map nodes=1 poses=15 links=80 |
| OK | rtabmap cloud map output | `/rtabmap/cloud_map` | 15 | 0.72 | frame=map size=3826x1 points=3826 |
| OBS | rtabmap map graph output | `/rtabmap/mapGraph` | 15 | 0.72 | frame=map poses=15 links=79 |
| OBS | rtabmap path output | `/rtabmap/mapPath` | 43 | 2.12 | frame=map poses=15 |
| OBS | rtabmap occupancy map output | `/rtabmap/map` | 15 | 0.72 | frame=map size=131x176 resolution=0.050 |
| OBS | tf | `/tf` | 1597 | 79.85 | transforms=1 first=odom->base_footprint |

## RTAB-Map Info

- ref_id: `81`
- loop_closure_id: `0`
- proximity_detection_id: `0`
- working_memory_size: `15`
- local_path_size: `0`
- odom_cache_poses: `0`
- stats_count: `106`

## Selected Stats

| key | value |
| --- | ---: |
| `Keypoint/Index_memory_usage/KB` | 92960 |
| `Loop/Accepted_hypothesis_id/` | 0 |
| `Loop/Angular_variance/` | 0 |
| `Loop/Distance_since_last_loc/m` | 3.28744 |
| `Loop/Highest_hypothesis_id/` | 52 |
| `Loop/Highest_hypothesis_value/` | 0.0603926 |
| `Loop/Hypothesis_ratio/` | 0 |
| `Loop/Hypothesis_reactivated/` | 1 |
| `Loop/Id/` | 0 |
| `Loop/Landmark_detected/` | 0 |
| `Loop/Landmark_detected_node_ref/` | 0 |
| `Loop/Last_id/` | 0 |
| `Loop/Linear_variance/` | 0 |
| `Loop/MapToBase_lin_std/m` | 1.45032 |
| `Loop/MapToBase_lin_var/m2` | 2.10343 |
| `Loop/MapToBase_pitch/deg` | 0 |
| `Loop/MapToBase_roll/deg` | 0 |
| `Loop/MapToBase_x/m` | 1.71266 |
| `Loop/MapToBase_y/m` | -0.0100557 |
| `Loop/MapToBase_yaw/deg` | -2.78241 |
