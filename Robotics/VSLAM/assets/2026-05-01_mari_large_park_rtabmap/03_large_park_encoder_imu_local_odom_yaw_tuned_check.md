# Mari RTAB-Map Check - large_park_encoder_imu_local_odom_yaw_tuned

## Summary

- checked_at: `2026-05-01T05:55:38.943221+00:00`
- duration_sec: `20.0`
- odom_topic: `/odometry/local`
- rtabmap_namespace: `/rtabmap`

## Topics

| status | label | topic | count | rate_hz | summary |
| --- | --- | --- | ---: | ---: | --- |
| OK | odom input | `/odometry/local` | 572 | 29.95 | frame=odom child=base_footprint x=1.135 y=0.042 |
| OK | rgb image input | `/camera/camera/color/image_raw` | 286 | 14.98 | frame=camera_color_optical_frame size=424x240 encoding=rgb8 |
| OK | depth image input | `/camera/camera/aligned_depth_to_color/image_raw` | 286 | 14.98 | frame=camera_color_optical_frame size=424x240 encoding=32FC1 |
| OK | rgb camera info input | `/camera/camera/color/camera_info` | 286 | 14.98 | frame=camera_color_optical_frame size=424x240 |
| OK | rtabmap info output | `/rtabmap/info` | 52 | 2.55 | frame=map ref_id=77 loop=0 wm=18 stats=106 |
| OK | rtabmap map data output | `/rtabmap/mapData` | 52 | 2.55 | frame=map nodes=1 poses=19 links=76 |
| OK | rtabmap cloud map output | `/rtabmap/cloud_map` | 18 | 0.87 | frame=map size=7314x1 points=7314 |
| OBS | rtabmap map graph output | `/rtabmap/mapGraph` | 18 | 0.87 | frame=map poses=18 links=75 |
| OBS | rtabmap path output | `/rtabmap/mapPath` | 51 | 2.55 | frame=map poses=18 |
| OBS | rtabmap occupancy map output | `/rtabmap/map` | 18 | 0.87 | frame=map size=155x205 resolution=0.050 |
| OBS | tf | `/tf` | 1652 | 82.67 | transforms=4 first=base_link->left_front_virtual_track_wheel_link |

## RTAB-Map Info

- ref_id: `77`
- loop_closure_id: `0`
- proximity_detection_id: `0`
- working_memory_size: `18`
- local_path_size: `0`
- odom_cache_poses: `0`
- stats_count: `106`

## Selected Stats

| key | value |
| --- | ---: |
| `Keypoint/Index_memory_usage/KB` | 76744 |
| `Loop/Accepted_hypothesis_id/` | 0 |
| `Loop/Angular_variance/` | 0 |
| `Loop/Distance_since_last_loc/m` | 1.9983 |
| `Loop/Highest_hypothesis_id/` | 47 |
| `Loop/Highest_hypothesis_value/` | 0.0521939 |
| `Loop/Hypothesis_ratio/` | 0 |
| `Loop/Hypothesis_reactivated/` | 1 |
| `Loop/Id/` | 0 |
| `Loop/Landmark_detected/` | 0 |
| `Loop/Landmark_detected_node_ref/` | 0 |
| `Loop/Last_id/` | 0 |
| `Loop/Linear_variance/` | 0 |
| `Loop/MapToBase_lin_std/m` | 1.25308 |
| `Loop/MapToBase_lin_var/m2` | 1.5702 |
| `Loop/MapToBase_pitch/deg` | 0 |
| `Loop/MapToBase_roll/deg` | 0 |
| `Loop/MapToBase_x/m` | 1.13448 |
| `Loop/MapToBase_y/m` | 0.0349725 |
| `Loop/MapToBase_yaw/deg` | -3.13541 |
