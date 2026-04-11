#!/usr/bin/env python3

import math
from typing import Optional

import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, Image, Imu


class DepthImuLocalMapper(Node):
    """
    Quick debugging mapper.

    This is not a full SLAM system.
    It creates a local top-down occupancy-like view from depth and
    optionally rotates the accumulated map using IMU yaw integration.

    Assumptions:
    - camera optical frame follows ROS optical convention
    - gyro z roughly corresponds to yaw axis for quick debugging
    - latest IMU state is close enough in time to the latest depth frame
    """

    def __init__(self) -> None:
        super().__init__("depth_imu_local_mapper")

        self.declare_parameter(
            "depth_topic", "/camera/camera/depth/image_rect_raw"
        )
        self.declare_parameter(
            "camera_info_topic", "/camera/camera/depth/camera_info"
        )
        self.declare_parameter("gyro_topic", "/camera/camera/gyro/sample")
        self.declare_parameter("accel_topic", "/camera/camera/accel/sample")
        self.declare_parameter("use_imu_yaw", True)
        self.declare_parameter("min_depth_m", 0.3)
        self.declare_parameter("max_depth_m", 4.0)
        self.declare_parameter("sample_step", 6)
        self.declare_parameter("grid_resolution_m", 0.05)
        self.declare_parameter("grid_size_px", 800)
        self.declare_parameter("camera_height_m", 0.25)
        self.declare_parameter("camera_pitch_deg_down", 0.0)
        self.declare_parameter("obstacle_min_height_m", 0.02)
        self.declare_parameter("obstacle_max_height_m", 1.5)
        self.declare_parameter("map_decay", 0.985)
        self.declare_parameter("show_depth_panel", True)
        self.declare_parameter("window_name", "Depth IMU Local Mapper")
        self.declare_parameter("processing_rate_hz", 10.0)

        self.depth_topic = self.get_parameter("depth_topic").value
        self.camera_info_topic = self.get_parameter("camera_info_topic").value
        self.gyro_topic = self.get_parameter("gyro_topic").value
        self.accel_topic = self.get_parameter("accel_topic").value
        self.use_imu_yaw = bool(self.get_parameter("use_imu_yaw").value)
        self.min_depth_m = float(self.get_parameter("min_depth_m").value)
        self.max_depth_m = float(self.get_parameter("max_depth_m").value)
        self.sample_step = int(self.get_parameter("sample_step").value)
        self.grid_resolution_m = float(
            self.get_parameter("grid_resolution_m").value
        )
        self.grid_size_px = int(self.get_parameter("grid_size_px").value)
        self.camera_height_m = float(self.get_parameter("camera_height_m").value)
        self.camera_pitch_deg_down = float(
            self.get_parameter("camera_pitch_deg_down").value
        )
        self.obstacle_min_height_m = float(
            self.get_parameter("obstacle_min_height_m").value
        )
        self.obstacle_max_height_m = float(
            self.get_parameter("obstacle_max_height_m").value
        )
        self.map_decay = float(self.get_parameter("map_decay").value)
        self.show_depth_panel = bool(self.get_parameter("show_depth_panel").value)
        self.window_name = str(self.get_parameter("window_name").value)
        self.processing_rate_hz = float(
            self.get_parameter("processing_rate_hz").value
        )

        self.bridge = CvBridge()
        self.fx: Optional[float] = None
        self.fy: Optional[float] = None
        self.cx: Optional[float] = None
        self.cy: Optional[float] = None

        self.roll_rad = 0.0
        self.pitch_rad = 0.0
        self.yaw_rad = 0.0
        self.last_gyro_time = None
        self.latest_imu_age_sec = None
        self.have_gyro = False
        self.have_accel = False

        self.map_grid = np.zeros(
            (self.grid_size_px, self.grid_size_px), dtype=np.float32
        )
        self.last_depth_preview = np.zeros((480, 640, 3), dtype=np.uint8)
        self.latest_depth_msg: Optional[Image] = None
        self.received_depth_frames = 0
        self.processed_depth_frames = 0

        self.create_subscription(
            CameraInfo,
            self.camera_info_topic,
            self.camera_info_cb,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            Image,
            self.depth_topic,
            self.depth_cb,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            Imu,
            self.gyro_topic,
            self.gyro_cb,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            Imu,
            self.accel_topic,
            self.accel_cb,
            qos_profile_sensor_data,
        )
        self.create_timer(1.0 / max(self.processing_rate_hz, 1.0), self.process_latest_depth)

        self.get_logger().info(
            "Depth IMU local mapper started. "
            f"depth={self.depth_topic}, camera_info={self.camera_info_topic}, "
            f"gyro={self.gyro_topic}, accel={self.accel_topic}, "
            f"processing_rate_hz={self.processing_rate_hz:.1f}"
        )

    def camera_info_cb(self, msg: CameraInfo) -> None:
        self.fx = float(msg.k[0])
        self.fy = float(msg.k[4])
        self.cx = float(msg.k[2])
        self.cy = float(msg.k[5])

    def gyro_cb(self, msg: Imu) -> None:
        self.have_gyro = True
        now_sec = float(msg.header.stamp.sec) + float(msg.header.stamp.nanosec) * 1e-9
        if self.last_gyro_time is not None and self.use_imu_yaw:
            dt = now_sec - self.last_gyro_time
            if 0.0 < dt < 0.1:
                self.yaw_rad += float(msg.angular_velocity.z) * dt
        self.last_gyro_time = now_sec

    def accel_cb(self, msg: Imu) -> None:
        self.have_accel = True
        ax = float(msg.linear_acceleration.x)
        ay = float(msg.linear_acceleration.y)
        az = float(msg.linear_acceleration.z)
        if not np.isfinite([ax, ay, az]).all():
            return

        # Quick tilt estimate from gravity direction.
        self.roll_rad = math.atan2(ay, az if abs(az) > 1e-6 else 1e-6)
        self.pitch_rad = math.atan2(-ax, math.sqrt(ay * ay + az * az) + 1e-6)

    def depth_cb(self, msg: Image) -> None:
        self.received_depth_frames += 1
        self.latest_depth_msg = msg

    def process_latest_depth(self) -> None:
        if None in (self.fx, self.fy, self.cx, self.cy):
            return
        if self.latest_depth_msg is None:
            return

        msg = self.latest_depth_msg
        self.latest_depth_msg = None

        try:
            if msg.encoding == "16UC1":
                depth_mm = self.bridge.imgmsg_to_cv2(
                    msg, desired_encoding="passthrough"
                )
                depth_m = depth_mm.astype(np.float32) / 1000.0
            elif msg.encoding == "32FC1":
                depth_m = self.bridge.imgmsg_to_cv2(
                    msg, desired_encoding="passthrough"
                ).astype(np.float32)
            else:
                self.get_logger().warn(
                    f"Unsupported depth encoding: {msg.encoding}"
                )
                return
        except Exception as exc:
            self.get_logger().error(f"Depth conversion failed: {exc}")
            return

        self.processed_depth_frames += 1
        self.last_depth_preview = self.make_depth_preview(depth_m)
        self.update_map_from_depth(depth_m)
        gui = self.compose_gui()
        cv2.imshow(self.window_name, gui)
        cv2.waitKey(1)

    def make_depth_preview(self, depth_m: np.ndarray) -> np.ndarray:
        valid = np.isfinite(depth_m) & (depth_m > 0.0)
        clipped = np.clip(depth_m, self.min_depth_m, self.max_depth_m)
        normalized = np.zeros_like(clipped, dtype=np.float32)

        if np.any(valid):
            normalized[valid] = (clipped[valid] - self.min_depth_m) / max(
                self.max_depth_m - self.min_depth_m, 1e-6
            )
            normalized[valid] = 1.0 - normalized[valid]

        image_8u = (normalized * 255.0).astype(np.uint8)
        preview = cv2.applyColorMap(image_8u, cv2.COLORMAP_TURBO)
        preview[~valid] = (0, 0, 0)
        return preview

    def update_map_from_depth(self, depth_m: np.ndarray) -> None:
        self.map_grid *= self.map_decay

        step = max(self.sample_step, 1)
        sampled = depth_m[::step, ::step]
        valid = np.isfinite(sampled) & (sampled >= self.min_depth_m) & (
            sampled <= self.max_depth_m
        )
        if not np.any(valid):
            return

        h, w = depth_m.shape
        uu = np.arange(0, w, step, dtype=np.float32)
        vv = np.arange(0, h, step, dtype=np.float32)
        grid_u, grid_v = np.meshgrid(uu, vv)

        z = sampled
        x = (grid_u - self.cx) * z / self.fx
        y = (grid_v - self.cy) * z / self.fy

        # Optical frame -> body-like frame.
        forward = z
        left = -x
        up = -y

        # Apply static camera pitch correction if the camera points downward.
        pitch_correction = -math.radians(self.camera_pitch_deg_down)
        c = math.cos(pitch_correction)
        s = math.sin(pitch_correction)
        forward_corr = c * forward + s * up
        up_corr = -s * forward + c * up
        left_corr = left

        # Shift points so the ground is approximately z=0 in the map frame.
        up_world = up_corr + self.camera_height_m

        obstacle_mask = (
            valid
            & (forward_corr > 0.0)
            & (up_world >= self.obstacle_min_height_m)
            & (up_world <= self.obstacle_max_height_m)
        )
        if not np.any(obstacle_mask):
            return

        fwd = forward_corr[obstacle_mask]
        lft = left_corr[obstacle_mask]

        if self.use_imu_yaw and self.have_gyro:
            cyaw = math.cos(self.yaw_rad)
            syaw = math.sin(self.yaw_rad)
            fwd_rot = cyaw * fwd - syaw * lft
            lft_rot = syaw * fwd + cyaw * lft
        else:
            fwd_rot = fwd
            lft_rot = lft

        center_x = self.grid_size_px // 2
        center_y = int(self.grid_size_px * 0.85)

        px = center_x + (lft_rot / self.grid_resolution_m).astype(np.int32)
        py = center_y - (fwd_rot / self.grid_resolution_m).astype(np.int32)

        inside = (
            (px >= 0)
            & (px < self.grid_size_px)
            & (py >= 0)
            & (py < self.grid_size_px)
        )
        self.map_grid[py[inside], px[inside]] = np.maximum(
            self.map_grid[py[inside], px[inside]], 1.0
        )

    def compose_gui(self) -> np.ndarray:
        map_img = (np.clip(self.map_grid, 0.0, 1.0) * 255.0).astype(np.uint8)
        map_img = cv2.applyColorMap(map_img, cv2.COLORMAP_TURBO)

        center_x = self.grid_size_px // 2
        center_y = int(self.grid_size_px * 0.85)
        cv2.circle(map_img, (center_x, center_y), 8, (255, 255, 255), -1)
        cv2.arrowedLine(
            map_img,
            (center_x, center_y),
            (center_x, center_y - 40),
            (255, 255, 255),
            2,
            tipLength=0.25,
        )

        self.draw_text(
            map_img,
            f"yaw={math.degrees(self.yaw_rad):.1f} deg | "
            f"roll={math.degrees(self.roll_rad):.1f} deg | "
            f"pitch={math.degrees(self.pitch_rad):.1f} deg",
            10,
            25,
        )
        self.draw_text(
            map_img,
            f"imu: gyro={'Y' if self.have_gyro else 'N'} accel={'Y' if self.have_accel else 'N'}",
            10,
            50,
        )
        self.draw_text(
            map_img,
            f"grid_res={self.grid_resolution_m:.2f}m | range={self.min_depth_m:.1f}-{self.max_depth_m:.1f}m",
            10,
            75,
        )
        self.draw_text(
            map_img,
            f"depth recv={self.received_depth_frames} proc={self.processed_depth_frames}",
            10,
            100,
        )

        if self.show_depth_panel:
            depth_panel = cv2.resize(
                self.last_depth_preview,
                (self.grid_size_px, self.grid_size_px),
                interpolation=cv2.INTER_NEAREST,
            )
            self.draw_text(depth_panel, "depth preview", 10, 25)
            self.draw_text(map_img, "top-down local map", 10, 125)
            return np.hstack([depth_panel, map_img])

        self.draw_text(map_img, "top-down local map", 10, 125)
        return map_img

    @staticmethod
    def draw_text(image: np.ndarray, text: str, x: int, y: int) -> None:
        cv2.putText(
            image,
            text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            image,
            text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )


def main() -> None:
    rclpy.init()
    node = DepthImuLocalMapper()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
