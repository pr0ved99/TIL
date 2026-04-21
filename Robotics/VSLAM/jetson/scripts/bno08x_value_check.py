#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
import time


def _parse_int(value: str) -> int:
    return int(value, 0)


def _format_vec(name: str, value) -> str:
    if value is None:
        return f"{name}=None"
    return f"{name}=({value[0]: .4f}, {value[1]: .4f}, {value[2]: .4f})"


def _format_quat(value) -> str:
    if value is None:
        return "quat=None"
    return (
        "quat=("
        f"{value[0]: .4f}, {value[1]: .4f}, {value[2]: .4f}, {value[3]: .4f}"
        ")"
    )


def _print_missing_dependency(exc: Exception) -> None:
    print(f"missing dependency: {exc}")
    print()
    print("install steps:")
    print("  sudo apt update")
    print("  sudo apt install -y python3-pip python3-venv python3-smbus2 i2c-tools")
    print("  python3 -m venv ~/venvs/bno08x")
    print("  source ~/venvs/bno08x/bin/activate")
    print(
        "  pip install adafruit-blinka "
        "adafruit-circuitpython-bno08x "
        "adafruit-extended-bus "
        "pyserial smbus2"
    )


def _make_bno_i2c(bus: int, address: int):
    try:
        from adafruit_extended_bus import ExtendedI2C
        from adafruit_bno08x.i2c import BNO08X_I2C
    except ModuleNotFoundError as exc:
        _print_missing_dependency(exc)
        raise SystemExit(1) from exc

    i2c = ExtendedI2C(bus)
    return BNO08X_I2C(i2c, address=address)


def _make_bno_uart(port: str, baud: int):
    try:
        import serial
        from adafruit_bno08x.uart import BNO08X_UART
    except ModuleNotFoundError as exc:
        _print_missing_dependency(exc)
        raise SystemExit(1) from exc

    uart = serial.Serial(port, baudrate=baud, timeout=1)
    return BNO08X_UART(uart)


def main() -> int:
    parser = argparse.ArgumentParser(description="Read live values from a BNO08x sensor.")
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
    parser.add_argument(
        "--rate",
        type=float,
        default=5.0,
        help="Print rate in Hz",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=0,
        help="Number of samples to print, 0 means infinite",
    )
    args = parser.parse_args()

    try:
        from adafruit_bno08x import (
            BNO_REPORT_ACCELEROMETER,
            BNO_REPORT_GYROSCOPE,
            BNO_REPORT_MAGNETOMETER,
            BNO_REPORT_ROTATION_VECTOR,
        )
    except ModuleNotFoundError as exc:
        _print_missing_dependency(exc)
        return 1

    if args.interface == "i2c":
        bno = _make_bno_i2c(args.bus, args.address)
        print(f"opened BNO08x over I2C bus={args.bus} address={hex(args.address)}")
    else:
        bno = _make_bno_uart(args.uart_port, args.baud)
        print(f"opened BNO08x over UART port={args.uart_port} baud={args.baud}")

    bno.enable_feature(BNO_REPORT_ACCELEROMETER)
    bno.enable_feature(BNO_REPORT_GYROSCOPE)
    bno.enable_feature(BNO_REPORT_MAGNETOMETER)
    bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

    interval = 1.0 / max(args.rate, 0.1)
    count = 0

    try:
        while True:
            accel = bno.acceleration
            gyro = bno.gyro
            magnetic = bno.magnetic
            quaternion = bno.quaternion
            stamp = time.strftime("%H:%M:%S")
            print(
                f"[{stamp}] "
                f"{_format_vec('accel', accel)} "
                f"{_format_vec('gyro', gyro)} "
                f"{_format_vec('mag', magnetic)} "
                f"{_format_quat(quaternion)}"
            )
            count += 1
            if args.samples > 0 and count >= args.samples:
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        print("stopped by user")

    return 0


if __name__ == "__main__":
    sys.exit(main())
