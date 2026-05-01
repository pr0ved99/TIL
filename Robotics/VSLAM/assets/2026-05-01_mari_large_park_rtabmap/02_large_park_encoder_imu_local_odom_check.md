# Mari RTAB-Map Check - large_park_encoder_imu_local_odom

## Summary

- checked_at: `2026-04-30T16:03:04.177298+00:00`
- duration_sec: `20.0`
- odom_topic: `/odometry/local`
- rtabmap_namespace: `/rtabmap`

## Topics

| status | label | topic | count | rate_hz | summary |
| --- | --- | --- | ---: | ---: | --- |
| OK | odom input | `/odometry/local` | 600 | 29.97 | frame=odom child=base_footprint x=1.458 y=-0.002 |
| OK | rgb image input | `/camera/camera/color/image_raw` | 281 | 14.78 | frame=camera_color_optical_frame size=424x240 encoding=rgb8 |
| OK | depth image input | `/camera/camera/aligned_depth_to_color/image_raw` | 280 | 14.73 | frame=camera_color_optical_frame size=424x240 encoding=32FC1 |
| OK | rgb camera info input | `/camera/camera/color/camera_info` | 281 | 14.78 | frame=camera_color_optical_frame size=424x240 |
| OK | rtabmap info output | `/rtabmap/info` | 52 | 2.58 | frame=map ref_id=104 loop=0 wm=13 stats=106 |
| OK | rtabmap map data output | `/rtabmap/mapData` | 52 | 2.58 | frame=map nodes=1 poses=13 links=103 |
| OK | rtabmap cloud map output | `/rtabmap/cloud_map` | 13 | 0.61 | frame=map size=5659x1 points=5659 |
| OBS | rtabmap map graph output | `/rtabmap/mapGraph` | 13 | 0.61 | frame=map poses=13 links=103 |
| OBS | rtabmap path output | `/rtabmap/mapPath` | 52 | 2.58 | frame=map poses=13 |
| OBS | rtabmap occupancy map output | `/rtabmap/map` | 13 | 0.61 | frame=map size=145x176 resolution=0.050 |
| OBS | tf | `/tf` | 1632 | 81.61 | transforms=1 first=odom->base_footprint |

## RTAB-Map Info

- ref_id: `104`
- loop_closure_id: `0`
- proximity_detection_id: `0`
- working_memory_size: `13`
- local_path_size: `0`
- odom_cache_poses: `0`
- stats_count: `106`

## Selected Stats

| key | value |
| --- | ---: |
| `Keypoint/Index_memory_usage/KB` | 65680 |
| `Loop/Accepted_hypothesis_id/` | 0 |
| `Loop/Angular_variance/` | 0 |
| `Loop/Distance_since_last_loc/m` | 4.84314 |
| `Loop/Highest_hypothesis_id/` | 1 |
| `Loop/Highest_hypothesis_value/` | 0.0910221 |
| `Loop/Hypothesis_ratio/` | 0 |
| `Loop/Hypothesis_reactivated/` | 1 |
| `Loop/Id/` | 0 |
| `Loop/Landmark_detected/` | 0 |
| `Loop/Landmark_detected_node_ref/` | 0 |
| `Loop/Last_id/` | 0 |
| `Loop/Linear_variance/` | 0 |
| `Loop/MapToBase_lin_std/m` | 1.73665 |
| `Loop/MapToBase_lin_var/m2` | 3.01596 |
| `Loop/MapToBase_pitch/deg` | 0 |
| `Loop/MapToBase_roll/deg` | 0 |
| `Loop/MapToBase_x/m` | 1.45414 |
| `Loop/MapToBase_y/m` | -0.0239036 |
| `Loop/MapToBase_yaw/deg` | -0.150777 |
