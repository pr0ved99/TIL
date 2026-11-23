"""Record the ADC bench stream and PC receipt freshness on Ubuntu (Python 3.12+)."""

import argparse
import csv
import fcntl
import os
import re
import select
import termios
import time
import tty
from contextlib import ExitStack
from pathlib import Path


FRAME = re.compile(rb"ADC,seq=(\d+),ms=(\d+),raw=(-?\d+),valid=([01])")
STALE_S = 1.5


def open_receiver(path, stack):
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOCTTY)
    stack.callback(os.close, fd)
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    original = termios.tcgetattr(fd)
    settings = termios.tcgetattr(fd)
    tty.cfmakeraw(settings)
    settings[2] &= ~(termios.CSTOPB | termios.CRTSCTS)
    settings[2] |= termios.CLOCAL | termios.CREAD
    settings[4] = settings[5] = termios.B115200
    termios.tcsetattr(fd, termios.TCSANOW, settings)

    def restore():
        try:
            termios.tcsetattr(fd, termios.TCSANOW, original)
        except termios.error:
            pass  # A physically disconnected port has no settings to restore.

    stack.callback(restore)
    termios.tcflush(fd, termios.TCIFLUSH)
    return fd


def record(args, writer):
    start = time.monotonic()
    fd = None
    retry_at = 0.0
    last_sample = None
    state = "WAITING"
    paused = False
    samples = 0

    def event(at, name):
        writer.writerow((f"{at:.6f}", name, "", "", "", ""))
        print(f"{at:8.3f} s  {name}", flush=True)

    event(0, state)
    with ExitStack() as port:
        while True:
            now = time.monotonic() - start
            if now >= args.seconds:
                break
            if state == "FRESH" and now - last_sample >= STALE_S:
                state = "STALE"
                event(now, state)
            in_pause = (args.pause_at is not None and
                        args.pause_at <= now < args.pause_at + args.pause_for)
            if in_pause:
                if not paused:
                    port.close()
                    fd = None
                    paused = True
                    event(now, "RX_PAUSED")
                time.sleep(0.025)
                continue
            paused = False
            if fd is None:
                if now < retry_at:
                    time.sleep(0.025)
                    continue
                try:
                    fd = open_receiver(args.port, port)
                except (OSError, termios.error):
                    port.close()
                    retry_at = now + 0.25
                    continue
                event(now, "RX_OPEN")
                # Drain the ST-LINK backlog before accepting fresh records.
                accept_after = now + 1.0
                pending = b""
            try:
                if not select.select([fd], [], [], 0.025)[0]:
                    continue
                data = os.read(fd, 4096)
                if not data:
                    raise OSError("serial port disconnected")
            except BlockingIOError:
                continue
            except OSError:
                port.close()
                fd = None
                retry_at = now + 0.25
                event(time.monotonic() - start, "RX_LOST")
                continue
            received = time.monotonic() - start
            *lines, pending = (pending + data).split(b"\n")
            if received < accept_after:
                continue
            for line in lines:
                match = FRAME.fullmatch(line.rstrip(b"\r"))
                if not match:
                    event(received, "MALFORMED")
                    continue
                seq, board_ms, raw, valid = map(int, match.groups())
                if state != "FRESH":
                    state = "FRESH"
                    event(received, state)
                last_sample = received
                writer.writerow((f"{received:.6f}", "SAMPLE", seq, board_ms, raw, valid))
                samples += 1
    event(time.monotonic() - start, "END")
    return samples


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("port", type=Path, help="ST-LINK device in /dev/serial/by-id/")
    parser.add_argument("output", type=Path, help="new CSV file")
    parser.add_argument("--seconds", type=float, default=80)
    parser.add_argument("--pause-at", type=float, help="close the PC port at this elapsed time")
    parser.add_argument("--pause-for", type=float, default=4)
    args = parser.parse_args()
    if args.seconds <= 0 or (args.pause_at is not None and
            not (0 < args.pause_at < args.pause_at + args.pause_for < args.seconds)):
        parser.error("use a positive duration and fit the optional pause inside it")
    with args.output.open("x", encoding="utf-8", newline="", buffering=1) as output:
        writer = csv.writer(output)
        writer.writerow(("host_s", "event", "seq", "board_ms", "raw", "valid"))
        samples = record(args, writer)
    if not samples:
        parser.exit(1, f"No ADC samples received from {args.port}\n")


if __name__ == "__main__":
    main()
