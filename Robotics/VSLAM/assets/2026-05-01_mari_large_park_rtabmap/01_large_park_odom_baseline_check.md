# Mari RTAB-Map Check - large_park_odom_baseline

## Summary

- checked_at: `2026-04-30T15:55:06.330992+00:00`
- duration_sec: `20.0`
- odom_topic: `/odom`
- rtabmap_namespace: `/rtabmap`

## Topics

| status | label | topic | count | rate_hz | summary |
| --- | --- | --- | ---: | ---: | --- |
| OK | odom input | `/odom` | 1001 | 49.96 | frame=odom child=base_footprint x=1.410 y=-0.021 |
| OK | rgb image input | `/camera/camera/color/image_raw` | 300 | 14.99 | frame=camera_color_optical_frame size=424x240 encoding=rgb8 |
| OK | depth image input | `/camera/camera/aligned_depth_to_color/image_raw` | 300 | 14.99 | frame=camera_color_optical_frame size=424x240 encoding=32FC1 |
| OK | rgb camera info input | `/camera/camera/color/camera_info` | 300 | 14.99 | frame=camera_color_optical_frame size=424x240 |
| OK | rtabmap info output | `/rtabmap/info` | 53 | 2.64 | frame=map ref_id=115 loop=0 wm=13 stats=106 |
| OK | rtabmap map data output | `/rtabmap/mapData` | 53 | 2.64 | frame=map nodes=1 poses=13 links=114 |
| OK | rtabmap cloud map output | `/rtabmap/cloud_map` | 13 | 0.61 | frame=map size=5631x1 points=5631 |
| OBS | rtabmap map graph output | `/rtabmap/mapGraph` | 13 | 0.61 | frame=map poses=13 links=114 |
| OBS | rtabmap path output | `/rtabmap/mapPath` | 53 | 2.64 | frame=map poses=13 |
| OBS | rtabmap occupancy map output | `/rtabmap/map` | 13 | 0.61 | frame=map size=146x176 resolution=0.050 |
| OBS | tf | `/tf` | 1699 | 84.93 | transforms=1 first=odom->base_footprint |

## RTAB-Map Info

- ref_id: `115`
- loop_closure_id: `0`
- proximity_detection_id: `0`
- working_memory_size: `13`
- local_path_size: `0`
- odom_cache_poses: `0`
- stats_count: `106`

## Selected Stats

| key | value |
| --- | ---: |
| `Keypoint/Index_memory_usage/KB` | 63472 |
| `Loop/Accepted_hypothesis_id/` | 0 |
| `Loop/Angular_variance/` | 0 |
| `Loop/Distance_since_last_loc/m` | 5.22368 |
| `Loop/Highest_hypothesis_id/` | 1 |
| `Loop/Highest_hypothesis_value/` | 0.00852126 |
| `Loop/Hypothesis_ratio/` | 0 |
| `Loop/Hypothesis_reactivated/` | 1 |
| `Loop/Id/` | 0 |
| `Loop/Landmark_detected/` | 0 |
| `Loop/Landmark_detected_node_ref/` | 0 |
| `Loop/Last_id/` | 0 |
| `Loop/Linear_variance/` | 0 |
| `Loop/MapToBase_lin_std/m` | 0.0678233 |
| `Loop/MapToBase_lin_var/m2` | 0.0046 |
| `Loop/MapToBase_pitch/deg` | 0 |
| `Loop/MapToBase_roll/deg` | 0 |
| `Loop/MapToBase_x/m` | 1.39559 |
| `Loop/MapToBase_y/m` | -0.0213876 |
| `Loop/MapToBase_yaw/deg` | -0.131679 |
