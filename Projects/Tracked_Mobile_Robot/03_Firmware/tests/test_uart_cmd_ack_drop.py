"""Native PC test of proposed/saved STM single-CMD-ACK omission, never board build."""
import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import reproduce_uart_reconnect as base
from uart_cmd_ack_drop_candidate import MODE, STM, prepare

HERE = Path(__file__).resolve().parent


def define(text, name, value):
    changed, count = re.subn(r"(?m)^(#define\s+" + name + r"\s+)\d+U$",
                             lambda m: m[1] + str(value) + "U", text)
    if count != 1:
        raise ValueError("Missing/ambiguous numeric setting: " + name)
    return changed


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--candidate", action="store_true")
    modes.add_argument("--saved", action="store_true")
    args = parser.parse_args()
    cc = (os.environ.get("WIFI_CONTROL_HOST_CC") or os.environ.get("W5_HOST_CC")
          or shutil.which("tcc") or shutil.which("gcc") or shutil.which("clang"))
    if not cc:
        raise SystemExit("NOT RUN: set WIFI_CONTROL_HOST_CC to a native compiler")
    stm_names = ("uart_mvp_protocol", "uart_frame_parser", "ring_buffer", "drive_command_mapper")
    esp_names = tuple("wifi_control_" + n for n in ("contract", "ticket", "owner", "state", "executor"))
    paths = [base.STM / d / (n + ext) for n in stm_names for d, ext in (("Inc", ".h"), ("Src", ".c"))]
    paths += [base.STM / "Inc/motor_output.h"]
    paths += [base.ESP / (n + ext) for n in esp_names for ext in (".h", ".c")]
    paths += [base.ESP / "wifi_link_main.c"]
    originals = {p: p.read_bytes() for p in paths}
    source = prepare() if args.candidate else STM.read_text(encoding="utf-8")
    print("MODE:", "CANDIDATE" if args.candidate else "SAVED", "/ NATIVE PC ONLY", flush=True)
    print("COMPILER:", cc, flush=True)
    print("STM tested text SHA256:", hashlib.sha256(source.encode()).hexdigest(), flush=True)
    with tempfile.TemporaryDirectory(prefix="uart-cmd-ack-drop-") as tmp:
        work = Path(tmp)
        for path, raw in originals.items():
            (work / path.name).write_bytes(raw)
        (work / "main.h").write_text(base.HAL, encoding="utf-8")
        for name in ("stm_uart_stream_host_fixture.c", "uart_cmd_ack_drop_host_fixture.c"):
            shutil.copyfile(HERE / name, work / name)

        def compile_source(text):
            (work / STM.name).write_text(text, encoding="utf-8")
            exe = work / ("ack_drop.exe" if os.name == "nt" else "ack_drop")
            command = [cc, "-Wall", "-Werror", "-I", str(work), str(work / "uart_cmd_ack_drop_host_fixture.c")]
            command += [str(work / (n + ".c")) for n in stm_names[1:] + esp_names]
            result = subprocess.run(command + ["-o", str(exe)], capture_output=True, text=True, timeout=30)
            return result, exe

        try:
            # Only test the intended omission mode; other production flags must be off.
            flags = re.findall(r"(?m)^#define\s+(UART_MVP_\w*TEST_ENABLED)\s+(\d+)U$", source)
            assert any(name == MODE for name, _ in flags)
            assert all(value == "0" for name, value in flags if name != MODE), flags
            for value in (0, 1):
                result, exe = compile_source(define(source, MODE, value))
                if result.returncode:
                    raise RuntimeError(result.stdout + result.stderr)
                result = subprocess.run([str(exe)], capture_output=True, text=True, timeout=20)
                print(result.stdout, end="", flush=True)
                if result.returncode:
                    raise RuntimeError(f"mode {value}: exit {result.returncode}\n" + result.stderr)
            result, _ = compile_source(define(source, MODE, 2))
            assert result.returncode and "mode must be 0 or 1" in result.stderr
            print("PASS invalid mode rejected", flush=True)
            others = [name for name, _ in flags if name != MODE]
            assert len(others) == 13, others
            for name in others:
                result, _ = compile_source(define(define(source, MODE, 1), name, 1))
                assert result.returncode and "Do not combine CMD ACK drop" in result.stderr, name
            print(f"PASS all {len(others)} combined fault/output modes rejected", flush=True)
        finally:
            assert all(p.read_bytes() == raw for p, raw in originals.items()), "Production changed during test"
    print("Production unchanged. MCU build/flash and physical acceptance are separate.", flush=True)


if __name__ == "__main__":
    run()
