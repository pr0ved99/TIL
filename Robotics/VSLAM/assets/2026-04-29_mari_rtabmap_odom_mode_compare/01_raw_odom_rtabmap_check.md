# Mari RTAB-Map Check - raw_odom

## Summary

- checked_at: `2026-04-29T13:17:20.926951+00:00`
- duration_sec: `20.0`
- odom_topic: `/odom`
- rtabmap_namespace: `/rtabmap`

## Topics

| status | label | topic | count | rate_hz | summary |
| --- | --- | --- | ---: | ---: | --- |
| OK | odom input | `/odom` | 998 | 49.88 | frame=odom child=base_footprint x=1.747 y=-0.033 |
| OK | rgb image input | `/camera/camera/color/image_raw` | 159 | 7.95 | frame=camera_color_optical_frame size=640x480 encoding=rgb8 |
| OK | depth image input | `/camera/camera/aligned_depth_to_color/image_raw` | 93 | 4.66 | frame=camera_color_optical_frame size=640x480 encoding=32FC1 |
| OK | rgb camera info input | `/camera/camera/color/camera_info` | 300 | 15.00 | frame=camera_color_optical_frame size=640x480 |
| OK | rtabmap info output | `/rtabmap/info` | 44 | 2.22 | frame=map ref_id=160 loop=0 wm=14 stats=106 |
| OK | rtabmap map data output | `/rtabmap/mapData` | 44 | 2.22 | frame=map nodes=1 poses=14 links=159 |
| OK | rtabmap cloud map output | `/rtabmap/cloud_map` | 14 | 0.68 | frame=map size=3899x1 points=3899 |
| OBS | rtabmap map graph output | `/rtabmap/mapGraph` | 14 | 0.68 | frame=map poses=14 links=158 |
| OBS | rtabmap path output | `/rtabmap/mapPath` | 44 | 2.22 | frame=map poses=14 |
| OBS | rtabmap occupancy map output | `/rtabmap/map` | 14 | 0.68 | frame=map size=132x161 resolution=0.050 |
| OBS | tf | `/tf` | 1599 | 79.90 | transforms=1 first=map->odom |

## RTAB-Map Info

- ref_id: `160`
- loop_closure_id: `0`
- proximity_detection_id: `0`
- working_memory_size: `14`
- local_path_size: `0`
- odom_cache_poses: `0`
- stats_count: `106`

## Selected Stats

| key | value |
| --- | ---: |
| `Keypoint/Index_memory_usage/KB` | 78952 |
| `Loop/Accepted_hypothesis_id/` | 0 |
| `Loop/Angular_variance/` | 0 |
| `Loop/Distance_since_last_loc/m` | 4.29492 |
| `Loop/Highest_hypothesis_id/` | 127 |
| `Loop/Highest_hypothesis_value/` | 0.0780035 |
| `Loop/Hypothesis_ratio/` | 0 |
| `Loop/Hypothesis_reactivated/` | 1 |
| `Loop/Id/` | 0 |
| `Loop/Landmark_detected/` | 0 |
| `Loop/Landmark_detected_node_ref/` | 0 |
| `Loop/Last_id/` | 0 |
| `Loop/Linear_variance/` | 0 |
| `Loop/MapToBase_lin_std/m` | 0.0591608 |
| `Loop/MapToBase_lin_var/m2` | 0.0035 |
| `Loop/MapToBase_pitch/deg` | 0 |
| `Loop/MapToBase_roll/deg` | 0 |
| `Loop/MapToBase_x/m` | 1.6602 |
| `Loop/MapToBase_y/m` | -0.032876 |
| `Loop/MapToBase_yaw/deg` | -0.122179 |
