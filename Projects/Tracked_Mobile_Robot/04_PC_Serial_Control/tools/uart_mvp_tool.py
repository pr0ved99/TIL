#!/usr/bin/env python3
"""PC-side UART MVP tool for the Tracked Mobile Robot project.

The tool builds line-based UART frames, sends them to STM32, monitors responses,
and records both raw and parsed logs. pyserial is imported only when a real
serial operation is requested so frame-building tests can run without hardware.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import pathlib
import queue
import sys
import threading
import time
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple


BAUDRATE_DEFAULT = 115200
CMD_TIMEOUT_MS_DEFAULT = 300
CMD_RATE_HZ_DEFAULT = 20.0
TEL_RATE_HZ_DEFAULT = 10.0
MAX_FRAME_LEN_DEFAULT = 128

CMD_VX_MIN = -100
CMD_VX_MAX = 100
CMD_W_MIN = -500
CMD_W_MAX = 500
TIMEOUT_MIN_MS = 50
TIMEOUT_MAX_MS = 500


@dataclass(frozen=True)
class ParsedFrame:
    frame_type: str
    fields: Dict[str, str]
    raw: str

    @property
    def seq(self) -> str:
        return self.fields.get("seq", "")


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="milliseconds")


def make_frame(frame_type: str, **fields: object) -> str:
    """Build a protocol frame with a trailing LF."""
    frame_type = frame_type.strip().upper()
    if not frame_type:
        raise ValueError("frame_type is required")
    if frame_type == "RAW":
        raw = str(fields.get("raw", ""))
        return raw if raw.endswith("\n") else raw + "\n"

    parts = [frame_type]
    for key, value in fields.items():
        if value is None:
            continue
        if key == "raw":
            continue
        parts.append(f"{key}={value}")
    return ",".join(parts) + "\n"


def parse_frame(line: str) -> ParsedFrame:
    """Parse a received line into a frame type and key/value fields."""
    raw = line.rstrip("\r\n")
    if not raw:
        raise ValueError("empty frame")
    tokens = raw.split(",")
    frame_type = tokens[0].strip().upper()
    if not frame_type:
        raise ValueError("missing frame type")
    fields: Dict[str, str] = {}
    for token in tokens[1:]:
        if not token:
            continue
        if "=" not in token:
            fields[token.strip()] = ""
            continue
        key, value = token.split("=", 1)
        fields[key.strip()] = value.strip()
    return ParsedFrame(frame_type=frame_type, fields=fields, raw=raw)


def classify_frame(frame: ParsedFrame) -> str:
    if frame.frame_type == "ACK":
        return "accepted"
    if frame.frame_type == "ERR":
        return "rejected"
    if frame.frame_type == "TEL":
        return "telemetry"
    if frame.frame_type == "PONG":
        return "pong"
    if frame.frame_type in {"STATE", "FAULT"}:
        return frame.frame_type.lower()
    return "other"


def validate_cmd_values(vx_mmps: int, w_mradps: int, timeout_ms: int) -> None:
    if not (CMD_VX_MIN <= vx_mmps <= CMD_VX_MAX):
        raise ValueError(f"vx_mmps out of MVP range: {vx_mmps}")
    if not (CMD_W_MIN <= w_mradps <= CMD_W_MAX):
        raise ValueError(f"w_mradps out of MVP range: {w_mradps}")
    if not (TIMEOUT_MIN_MS <= timeout_ms <= TIMEOUT_MAX_MS):
        raise ValueError(f"timeout_ms out of MVP range: {timeout_ms}")


def frame_from_args(args: argparse.Namespace, seq: int) -> str:
    frame = args.frame.upper()
    if frame == "PING":
        return make_frame("PING", seq=args.seq if args.seq is not None else seq)
    if frame == "ARM":
        return make_frame("ARM", seq=args.seq if args.seq is not None else seq)
    if frame == "DISARM":
        return make_frame("DISARM", seq=args.seq if args.seq is not None else seq)
    if frame == "CMD":
        validate_cmd_values(args.vx_mmps, args.w_mradps, args.timeout_ms)
        return make_frame(
            "CMD",
            seq=args.seq if args.seq is not None else seq,
            vx_mmps=args.vx_mmps,
            w_mradps=args.w_mradps,
            timeout_ms=args.timeout_ms,
        )
    if frame == "RAW":
        return make_frame("RAW", raw=args.raw)
    raise ValueError(f"unsupported frame type: {args.frame}")


class UartLogger:
    def __init__(self, log_dir: pathlib.Path, enabled: bool = True) -> None:
        self.enabled = enabled
        self.log_dir = log_dir
        self.raw_file = None
        self.csv_file = None
        self.csv_writer: Optional[csv.writer] = None
        if enabled:
            log_dir.mkdir(parents=True, exist_ok=True)
            stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.raw_path = log_dir / f"uart_mvp_{stamp}_raw.log"
            self.csv_path = log_dir / f"uart_mvp_{stamp}_parsed.csv"
            self.raw_file = self.raw_path.open("a", encoding="utf-8", newline="")
            self.csv_file = self.csv_path.open("a", encoding="utf-8", newline="")
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(
                [
                    "timestamp",
                    "direction",
                    "frame_type",
                    "seq",
                    "state",
                    "code",
                    "category",
                    "raw",
                ]
            )

    def close(self) -> None:
        if self.raw_file:
            self.raw_file.close()
        if self.csv_file:
            self.csv_file.close()

    def log_line(self, direction: str, line: str) -> None:
        timestamp = now_iso()
        stripped = line.rstrip("\r\n")
        print(f"{timestamp} {direction:<2} {stripped}")
        if self.raw_file:
            self.raw_file.write(f"{timestamp} {direction} {stripped}\n")
            self.raw_file.flush()
        if self.csv_writer:
            try:
                frame = parse_frame(stripped)
                self.csv_writer.writerow(
                    [
                        timestamp,
                        direction,
                        frame.frame_type,
                        frame.fields.get("seq", ""),
                        frame.fields.get("state", ""),
                        frame.fields.get("code", ""),
                        classify_frame(frame),
                        frame.raw,
                    ]
                )
            except ValueError:
                self.csv_writer.writerow(
                    [timestamp, direction, "", "", "", "", "unparsed", stripped]
                )
            assert self.csv_file is not None
            self.csv_file.flush()


class SerialSession:
    def __init__(
        self,
        port: str,
        baudrate: int,
        logger: UartLogger,
        read_timeout_s: float = 0.05,
    ) -> None:
        try:
            import serial  # type: ignore
        except ImportError as exc:
            raise SystemExit(
                "pyserial is required for real serial I/O. Run: python -m pip install -r requirements.txt"
            ) from exc
        self.serial_mod = serial
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=read_timeout_s)
        self.logger = logger
        self.rx_queue: "queue.Queue[str]" = queue.Queue()
        self.stop_event = threading.Event()
        self.rx_thread = threading.Thread(target=self._rx_loop, daemon=True)

    def __enter__(self) -> "SerialSession":
        self.rx_thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.stop_event.set()
        self.rx_thread.join(timeout=1.0)
        self.ser.close()

    def _rx_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                data = self.ser.readline()
            except Exception as exc:  # pragma: no cover - hardware path
                self.logger.log_line("RX", f"SERIAL_READ_ERROR,{exc}")
                time.sleep(0.2)
                continue
            if not data:
                continue
            text = data.decode("utf-8", errors="replace")
            self.logger.log_line("RX", text)
            self.rx_queue.put(text)

    def send(self, frame: str) -> None:
        self.ser.write(frame.encode("ascii"))
        self.ser.flush()
        self.logger.log_line("TX", frame)

    def wait_for_response(self, seconds: float) -> None:
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            time.sleep(0.05)


def list_ports() -> int:
    try:
        from serial.tools import list_ports as serial_list_ports  # type: ignore
    except ImportError:
        print("pyserial is required. Run: python -m pip install -r requirements.txt")
        return 2
    ports = list(serial_list_ports.comports())
    if not ports:
        print("No serial ports found.")
        return 1
    for port in ports:
        print(f"{port.device}\t{port.description}\t{port.hwid}")
    return 0


def command_build(args: argparse.Namespace) -> int:
    frame = frame_from_args(args, args.seq if args.seq is not None else 1)
    print(frame, end="")
    return 0


def command_send(args: argparse.Namespace) -> int:
    log_dir = pathlib.Path(args.log_dir)
    frame = frame_from_args(args, args.seq if args.seq is not None else 1)
    if args.dry_run:
        print(frame, end="")
        return 0
    logger = UartLogger(log_dir=log_dir, enabled=not args.no_log)
    try:
        with SerialSession(args.port, args.baudrate, logger) as session:
            session.send(frame)
            session.wait_for_response(args.wait_s)
    finally:
        logger.close()
    return 0


def command_monitor(args: argparse.Namespace) -> int:
    logger = UartLogger(pathlib.Path(args.log_dir), enabled=not args.no_log)
    try:
        with SerialSession(args.port, args.baudrate, logger):
            print("Monitoring. Press Ctrl+C to stop.")
            while True:
                time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        logger.close()
    return 0


def scripted_frames() -> Iterable[Tuple[str, float]]:
    yield make_frame("PING", seq=1), 0.5
    yield make_frame("CMD", seq=2, vx_mmps=80, w_mradps=0, timeout_ms=300), 0.5
    yield make_frame("ARM", seq=3), 0.5
    yield make_frame("CMD", seq=4, vx_mmps=80, w_mradps=0, timeout_ms=300), 0.5
    yield make_frame("RAW", raw="CMD,seq=5,vx_mmps=80,timeout_ms=300"), 0.5
    yield make_frame("RAW", raw="CMD,seq=6,vx_mmps=9999,w_mradps=0,timeout_ms=300"), 0.5
    yield make_frame("CMD", seq=7, vx_mmps=0, w_mradps=0, timeout_ms=300), 1.0
    yield make_frame("DISARM", seq=8), 0.5


def command_scripted_test(args: argparse.Namespace) -> int:
    log_dir = pathlib.Path(args.log_dir)
    logger = UartLogger(log_dir=log_dir, enabled=not args.no_log)
    try:
        if args.dry_run:
            for frame, delay_s in scripted_frames():
                print(frame, end="")
                print(f"# wait {delay_s:.1f}s")
            return 0
        with SerialSession(args.port, args.baudrate, logger) as session:
            for frame, delay_s in scripted_frames():
                session.send(frame)
                session.wait_for_response(delay_s)
    finally:
        logger.close()
    return 0


def prompt_int(label: str, default: int) -> int:
    text = input(f"{label} [{default}]: ").strip()
    return default if not text else int(text)


def command_interactive(args: argparse.Namespace) -> int:
    logger = UartLogger(pathlib.Path(args.log_dir), enabled=not args.no_log)
    seq = args.start_seq
    try:
        with SerialSession(args.port, args.baudrate, logger) as session:
            print("Interactive UART MVP console. Motor power should stay disconnected.")
            while True:
                print()
                print("1) PING")
                print("2) ARM")
                print("3) DISARM")
                print("4) CMD custom")
                print("5) CMD zero once")
                print("6) zero-CMD keepalive")
                print("7) raw frame")
                print("8) out-of-range CMD")
                print("9) monitor wait")
                print("q) quit")
                choice = input("> ").strip().lower()
                if choice == "q":
                    break
                if choice == "1":
                    frame = make_frame("PING", seq=seq)
                    seq += 1
                elif choice == "2":
                    frame = make_frame("ARM", seq=seq)
                    seq += 1
                elif choice == "3":
                    frame = make_frame("DISARM", seq=seq)
                    seq += 1
                elif choice == "4":
                    vx = prompt_int("vx_mmps", 0)
                    w = prompt_int("w_mradps", 0)
                    timeout_ms = prompt_int("timeout_ms", CMD_TIMEOUT_MS_DEFAULT)
                    frame = make_frame(
                        "CMD",
                        seq=seq,
                        vx_mmps=vx,
                        w_mradps=w,
                        timeout_ms=timeout_ms,
                    )
                    seq += 1
                elif choice == "5":
                    frame = make_frame(
                        "CMD",
                        seq=seq,
                        vx_mmps=0,
                        w_mradps=0,
                        timeout_ms=CMD_TIMEOUT_MS_DEFAULT,
                    )
                    seq += 1
                elif choice == "6":
                    duration_s = float(input("duration_s [3.0]: ").strip() or "3.0")
                    period_s = 1.0 / CMD_RATE_HZ_DEFAULT
                    deadline = time.monotonic() + duration_s
                    while time.monotonic() < deadline:
                        frame = make_frame(
                            "CMD",
                            seq=seq,
                            vx_mmps=0,
                            w_mradps=0,
                            timeout_ms=CMD_TIMEOUT_MS_DEFAULT,
                        )
                        session.send(frame)
                        seq += 1
                        time.sleep(period_s)
                    continue
                elif choice == "7":
                    raw = input("raw frame without trailing LF: ")
                    frame = make_frame("RAW", raw=raw)
                elif choice == "8":
                    frame = make_frame(
                        "RAW",
                        raw=f"CMD,seq={seq},vx_mmps=9999,w_mradps=0,timeout_ms=300",
                    )
                    seq += 1
                elif choice == "9":
                    wait_s = float(input("wait_s [2.0]: ").strip() or "2.0")
                    session.wait_for_response(wait_s)
                    continue
                else:
                    print("Unknown menu option.")
                    continue
                session.send(frame)
                session.wait_for_response(args.wait_s)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        logger.close()
    return 0


def add_common_serial_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--port", help="Serial port, for example COM5")
    parser.add_argument("--baudrate", type=int, default=BAUDRATE_DEFAULT)
    parser.add_argument("--log-dir", default="logs")
    parser.add_argument("--no-log", action="store_true")


def add_frame_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("frame", choices=["PING", "ARM", "DISARM", "CMD", "RAW"])
    parser.add_argument("--seq", type=int)
    parser.add_argument("--vx-mmps", type=int, default=0)
    parser.add_argument("--w-mradps", type=int, default=0)
    parser.add_argument("--timeout-ms", type=int, default=CMD_TIMEOUT_MS_DEFAULT)
    parser.add_argument("--raw", default="")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="UART MVP PC-side test tool")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-ports", help="List available serial ports")

    build = sub.add_parser("build", help="Build one MVP frame without serial I/O")
    add_frame_args(build)
    build.set_defaults(func=command_build)

    send = sub.add_parser("send", help="Send one frame and monitor briefly")
    add_common_serial_args(send)
    add_frame_args(send)
    send.add_argument("--wait-s", type=float, default=1.0)
    send.add_argument("--dry-run", action="store_true")
    send.set_defaults(func=command_send)

    monitor = sub.add_parser("monitor", help="Monitor RX lines and write logs")
    add_common_serial_args(monitor)
    monitor.set_defaults(func=command_monitor)

    scripted = sub.add_parser("scripted-test", help="Run the UART MVP smoke sequence")
    add_common_serial_args(scripted)
    scripted.add_argument("--dry-run", action="store_true")
    scripted.set_defaults(func=command_scripted_test)

    interactive = sub.add_parser("interactive", help="Interactive UART MVP console")
    add_common_serial_args(interactive)
    interactive.add_argument("--start-seq", type=int, default=1)
    interactive.add_argument("--wait-s", type=float, default=0.3)
    interactive.set_defaults(func=command_interactive)

    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if args.command == "list-ports":
        return list_ports()
    if hasattr(args, "port") and not args.port and not getattr(args, "dry_run", False):
        parser.error("--port is required unless --dry-run is used")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
