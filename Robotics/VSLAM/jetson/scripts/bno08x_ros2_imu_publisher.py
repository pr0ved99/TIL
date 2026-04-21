#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from typing import Optional


def _parse_int(value: str) -> int:
    return int(value, 0)


def _print_sensor_dependency_help(exc: Exception) -> None:
    print(f"missing sensor dependency: {exc}")
    print()
    print("install steps:")
    print("  sudo apt update")
    print("  sudo apt install -y python3-pip python3-venv python3-smbus i2c-tools")
    print("  python3 -m venv ~/venvs/bno08x")
    print("  source ~/venvs/bno08x/bin/activate")
    print(
        "  pip install adafruit-blinka "
        "adafruit-circuitpython-bno08x "
        "adafruit-extended-bus "
        "pyserial smbus2"
    )


def _print_ros_dependency_help(exc: Exception) -> None:
    print(f"missing ROS dependency: {exc}")
    print()
    print("run this first:")
    print("  source /opt/ros/humble/setup.bash")
    print("  source ~/venvs/bno08x/bin/activate")


def _make_bno_i2c(bus: int, address: int):
    try:
        from adafruit_extended_bus import ExtendedI2C
        from adafruit_bno08x.i2c import BNO08X_I2C
    except ModuleNotFoundError as exc:
        _print_sensor_dependency_help(exc)
        raise SystemExit(1) from exc

    i2c = ExtendedI2C(bus)
    return BNO08X_I2C(i2c, address=address)


def _make_bno_uart(port: str, baud: int):
    try:
        import serial
        from adafruit_bno08x.uart import BNO08X_UART
    except ModuleNotFoundError as exc:
        _print_sensor_dependency_help(exc)
        raise SystemExit(1) from exc

    uart = serial.Serial(port, baudrate=baud, timeout=1)
    return BNO08X_UART(uart)


class BNO08XImuPublisher:
    def __init__(self, args) -> None:
        try:
            import rclpy
            from rclpy.node import Node
            from sensor_msgs.msg import Imu, MagneticField
        except ModuleNotFoundError as exc:
            _print_ros_dependency_help(exc)
            raise SystemExit(1) from exc

        try:
            from adafruit_bno08x import (
                BNO_REPORT_ACCELEROMETER,
                BNO_REPORT_GYROSCOPE,
                BNO_REPORT_MAGNETOMETER,
                BNO_REPORT_ROTATION_VECTOR,
            )
        except ModuleNotFoundError as exc:
            _print_sensor_dependency_help(exc)
            raise SystemExit(1) from exc

        self._rclpy = rclpy
        self._Imu = Imu
        self._MagneticField = MagneticField
        self._args = args
        self._last_error: Optional[str] = None
        self._sample_count = 0

        if args.interface == "i2c":
            self._bno = _make_bno_i2c(args.bus, args.address)
            self._source_label = f"I2C bus={args.bus} address={hex(args.address)}"
        else:
            self._bno = _make_bno_uart(args.uart_port, args.baud)
            self._source_label = f"UART port={args.uart_port} baud={args.baud}"

        self._bno.enable_feature(BNO_REPORT_ACCELEROMETER)
        self._bno.enable_feature(BNO_REPORT_GYROSCOPE)
        self._bno.enable_feature(BNO_REPORT_MAGNETOMETER)
        self._bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

        class _NodeImpl(Node):
            pass

        self.node = _NodeImpl("bno08x_imu_publisher")
        self._imu_pub = self.node.create_publisher(self._Imu, args.topic, 10)
        self._mag_pub = None
        if args.mag_topic:
            self._mag_pub = self.node.create_publisher(self._MagneticField, args.mag_topic, 10)

        period = 1.0 / max(args.rate, 0.1)
        self._timer = self.node.create_timer(period, self._publish_once)

        self.node.get_logger().info(f"opened BNO08x over {self._source_label}")
        self.node.get_logger().info(
            f"publishing IMU on {args.topic} frame_id={args.frame_id} rate={args.rate:.1f}Hz"
        )
        if args.mag_topic:
            self.node.get_logger().info(f"publishing magnetic field on {args.mag_topic}")

    def _publish_once(self) -> None:
        try:
            accel = self._bno.acceleration
            gyro = self._bno.gyro
            magnetic = self._bno.magnetic
            quaternion = self._bno.quaternion
        except Exception as exc:  # noqa: BLE001
            error_text = f"{type(exc).__name__}: {exc}"
            if error_text != self._last_error:
                self.node.get_logger().warning(f"sensor read failed: {error_text}")
                self._last_error = error_text
            return

        self._last_error = None
        now = self.node.get_clock().now().to_msg()

        imu_msg = self._Imu()
        imu_msg.header.stamp = now
        imu_msg.header.frame_id = self._args.frame_id
        imu_msg.orientation_covariance = [0.01, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.01]
        imu_msg.angular_velocity_covariance = [0.001, 0.0, 0.0, 0.0, 0.001, 0.0, 0.0, 0.0, 0.001]
        imu_msg.linear_acceleration_covariance = [0.01, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.01]

        if quaternion is not None:
            imu_msg.orientation.x = float(quaternion[0])
            imu_msg.orientation.y = float(quaternion[1])
            imu_msg.orientation.z = float(quaternion[2])
            imu_msg.orientation.w = float(quaternion[3])
        else:
            imu_msg.orientation_covariance[0] = -1.0

        if gyro is not None:
            imu_msg.angular_velocity.x = float(gyro[0])
            imu_msg.angular_velocity.y = float(gyro[1])
            imu_msg.angular_velocity.z = float(gyro[2])

        if accel is not None:
            imu_msg.linear_acceleration.x = float(accel[0])
            imu_msg.linear_acceleration.y = float(accel[1])
            imu_msg.linear_acceleration.z = float(accel[2])

        self._imu_pub.publish(imu_msg)

        if self._mag_pub is not None and magnetic is not None:
            mag_msg = self._MagneticField()
            mag_msg.header.stamp = now
            mag_msg.header.frame_id = self._args.frame_id
            mag_msg.magnetic_field.x = float(magnetic[0]) * 1e-6
            mag_msg.magnetic_field.y = float(magnetic[1]) * 1e-6
            mag_msg.magnetic_field.z = float(magnetic[2]) * 1e-6
            mag_msg.magnetic_field_covariance = [0.0] * 9
            self._mag_pub.publish(mag_msg)

        self._sample_count += 1
        if self._sample_count == 1:
            self.node.get_logger().info(
                "first sample: "
                f"accel={accel} gyro={gyro} mag={magnetic} quat={quaternion}"
            )

    def spin(self) -> int:
        try:
            self._rclpy.spin(self.node)
        except KeyboardInterrupt:
            self.node.get_logger().info("stopped by user")
        except Exception as exc:  # noqa: BLE001
            if exc.__class__.__name__ != "ExternalShutdownException":
                raise
        finally:
            self.node.destroy_node()
            if self._rclpy.ok():
                self._rclpy.shutdown()
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read BNO08x and publish sensor_msgs/Imu on ROS 2."
    )
    parser.add_argument("--interface", choices=("i2c", "uart"), required=True)
    parser.add_argument("--bus", type=int, default=1, help="I2C bus number for I2C mode")
    parser.add_argument(
        "--address",
        type=_parse_int,
        default=0x4B,
        help="I2C address for I2C mode, e.g. 0x4A or 0x4B",
    )
    parser.add_argument(
        "--uart-port",
        default="/dev/ttyTHS1",
        help="UART port for UART mode, e.g. /dev/ttyTHS1",
    )
    parser.add_argument(
        "--baud",
        type=int,
        default=3000000,
        help="UART baud rate for UART mode",
    )
    parser.add_argument("--topic", default="/imu/data", help="ROS 2 IMU topic name")
    parser.add_argument(
        "--mag-topic",
        default="/imu/mag",
        help="ROS 2 magnetic field topic name, empty string disables publishing",
    )
    parser.add_argument("--frame-id", default="imu_link", help="frame_id to put in outgoing messages")
    parser.add_argument("--rate", type=float, default=50.0, help="Publish rate in Hz")
    args = parser.parse_args()

    try:
        import rclpy
    except ModuleNotFoundError as exc:
        _print_ros_dependency_help(exc)
        return 1

    rclpy.init(args=None)
    publisher = BNO08XImuPublisher(args)
    return publisher.spin()


if __name__ == "__main__":
    sys.exit(main())
