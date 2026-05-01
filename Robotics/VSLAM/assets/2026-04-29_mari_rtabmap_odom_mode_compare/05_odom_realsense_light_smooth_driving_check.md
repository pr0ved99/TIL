# Mari RTAB-Map Check - odom_realsense_light_smooth_driving

## Summary

- checked_at: `2026-04-30T05:20:59.367756+00:00`
- duration_sec: `20.0`
- odom_topic: `/odom`
- rtabmap_namespace: `/rtabmap`

## Topics

| status | label | topic | count | rate_hz | summary |
| --- | --- | --- | ---: | ---: | --- |
| OK | odom input | `/odom` | 1000 | 49.95 | frame=odom child=base_footprint x=1.541 y=0.092 |
| OK | rgb image input | `/camera/camera/color/image_raw` | 300 | 14.99 | frame=camera_color_optical_frame size=424x240 encoding=rgb8 |
| OK | depth image input | `/camera/camera/aligned_depth_to_color/image_raw` | 300 | 14.99 | frame=camera_color_optical_frame size=424x240 encoding=32FC1 |
| OK | rgb camera info input | `/camera/camera/color/camera_info` | 300 | 14.98 | frame=camera_color_optical_frame size=424x240 |
| OK | rtabmap info output | `/rtabmap/info` | 53 | 2.63 | frame=map ref_id=110 loop=0 wm=20 stats=106 |
| OK | rtabmap map data output | `/rtabmap/mapData` | 53 | 2.63 | frame=map nodes=1 poses=21 links=109 |
| OK | rtabmap cloud map output | `/rtabmap/cloud_map` | 19 | 0.95 | frame=map size=4006x1 points=4006 |
| OBS | rtabmap map graph output | `/rtabmap/mapGraph` | 19 | 0.95 | frame=map poses=20 links=107 |
| OBS | rtabmap path output | `/rtabmap/mapPath` | 53 | 2.63 | frame=map poses=21 |
| OBS | rtabmap occupancy map output | `/rtabmap/map` | 19 | 0.95 | frame=map size=124x211 resolution=0.050 |
| OBS | tf | `/tf` | 1698 | 84.95 | transforms=1 first=odom->base_footprint |

## RTAB-Map Info

- ref_id: `110`
- loop_closure_id: `0`
- proximity_detection_id: `0`
- working_memory_size: `20`
- local_path_size: `0`
- odom_cache_poses: `0`
- stats_count: `106`

## Selected Stats

| key | value |
| --- | ---: |
| `Keypoint/Index_memory_usage/KB` | 50936 |
| `Loop/Accepted_hypothesis_id/` | 0 |
| `Loop/Angular_variance/` | 0 |
| `Loop/Distance_since_last_loc/m` | 3.70294 |
| `Loop/Highest_hypothesis_id/` | 81 |
| `Loop/Highest_hypothesis_value/` | 0.0620525 |
| `Loop/Hypothesis_ratio/` | 0 |
| `Loop/Hypothesis_reactivated/` | 1 |
| `Loop/Id/` | 0 |
| `Loop/Landmark_detected/` | 0 |
| `Loop/Landmark_detected_node_ref/` | 0 |
| `Loop/Last_id/` | 0 |
| `Loop/Linear_variance/` | 0 |
| `Loop/MapToBase_lin_std/m` | 0.06245 |
| `Loop/MapToBase_lin_var/m2` | 0.0039 |
| `Loop/MapToBase_pitch/deg` | -0 |
| `Loop/MapToBase_roll/deg` | 0 |
| `Loop/MapToBase_x/m` | 1.53888 |
| `Loop/MapToBase_y/m` | 0.0902046 |
| `Loop/MapToBase_yaw/deg` | 41.0666 |
