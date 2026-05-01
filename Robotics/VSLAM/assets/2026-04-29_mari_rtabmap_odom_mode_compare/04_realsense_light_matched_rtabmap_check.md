# Mari RTAB-Map Check - realsense_light_matched

## Summary

- checked_at: `2026-04-30T05:11:59.399460+00:00`
- duration_sec: `20.0`
- odom_topic: `/odom`
- rtabmap_namespace: `/rtabmap`

## Topics

| status | label | topic | count | rate_hz | summary |
| --- | --- | --- | ---: | ---: | --- |
| OK | odom input | `/odom` | 999 | 49.94 | frame=odom child=base_footprint x=-0.000 y=-0.010 |
| OK | rgb image input | `/camera/camera/color/image_raw` | 300 | 14.98 | frame=camera_color_optical_frame size=424x240 encoding=rgb8 |
| OK | depth image input | `/camera/camera/aligned_depth_to_color/image_raw` | 300 | 14.99 | frame=camera_color_optical_frame size=424x240 encoding=32FC1 |
| OK | rgb camera info input | `/camera/camera/color/camera_info` | 300 | 14.98 | frame=camera_color_optical_frame size=424x240 |
| OK | rtabmap info output | `/rtabmap/info` | 37 | 1.87 | frame=map ref_id=66 loop=0 wm=1 stats=106 |
| OK | rtabmap map data output | `/rtabmap/mapData` | 37 | 1.87 | frame=map nodes=1 poses=2 links=65 |
| OK | rtabmap cloud map output | `/rtabmap/cloud_map` | 1 | n/a | frame=map size=1328x1 points=1328 |
| OBS | rtabmap map graph output | `/rtabmap/mapGraph` | 1 | n/a | frame=map poses=2 links=29 |
| OBS | rtabmap path output | `/rtabmap/mapPath` | 37 | 1.87 | frame=map poses=2 |
| OBS | rtabmap occupancy map output | `/rtabmap/map` | 1 | n/a | frame=map size=105x156 resolution=0.050 |
| OBS | tf | `/tf` | 1700 | 84.95 | transforms=1 first=map->odom |

## RTAB-Map Info

- ref_id: `66`
- loop_closure_id: `0`
- proximity_detection_id: `0`
- working_memory_size: `1`
- local_path_size: `0`
- odom_cache_poses: `0`
- stats_count: `106`

## Selected Stats

| key | value |
| --- | ---: |
| `Keypoint/Index_memory_usage/KB` | 0 |
| `Loop/Accepted_hypothesis_id/` | 0 |
| `Loop/Angular_variance/` | 0 |
| `Loop/Distance_since_last_loc/m` | 0 |
| `Loop/Highest_hypothesis_id/` | 0 |
| `Loop/Highest_hypothesis_value/` | 0 |
| `Loop/Hypothesis_ratio/` | 0 |
| `Loop/Hypothesis_reactivated/` | 0 |
| `Loop/Id/` | 0 |
| `Loop/Landmark_detected/` | 0 |
| `Loop/Landmark_detected_node_ref/` | 0 |
| `Loop/Last_id/` | 0 |
| `Loop/Linear_variance/` | 0 |
| `Loop/MapToBase_lin_std/m` | 0.01 |
| `Loop/MapToBase_lin_var/m2` | 0.0001 |
| `Loop/MapToBase_pitch/deg` | 0 |
| `Loop/MapToBase_roll/deg` | 0 |
| `Loop/MapToBase_x/m` | -1.01419e-05 |
| `Loop/MapToBase_y/m` | -0.010007 |
| `Loop/MapToBase_yaw/deg` | -0.12351 |
