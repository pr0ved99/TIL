"""Run UART recovery tests on temporary candidate copies or user-saved firmware.

python test_uart_recovery.py --candidate
python test_uart_recovery.py --saved
Only native PC compilation is performed. No MCU build, flash or serial I/O.
"""
import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import reproduce_uart_reconnect as diagnostic
import test_wifi_control_executor as executor_tests
import test_wifi_control_main as main_tests
from test_wifi_w5_uart_contract import c_function, c_type
from uart_recovery_candidate import prepare, STM, MAIN, FIRMWARE

HERE = Path(__file__).resolve().parent


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--candidate", action="store_true")
    mode.add_argument("--saved", action="store_true")
    args = parser.parse_args()
    cc = (os.environ.get("WIFI_CONTROL_HOST_CC") or os.environ.get("W5_HOST_CC")
          or shutil.which("tcc") or shutil.which("gcc") or shutil.which("clang"))
    if not cc:
        raise SystemExit("NOT RUN: set WIFI_CONTROL_HOST_CC to a native C compiler")
    stm_names = ("uart_mvp_protocol", "uart_frame_parser", "ring_buffer", "drive_command_mapper")
    esp_names = tuple("wifi_control_" + name for name in
                      ("contract", "ticket", "owner", "state", "executor"))
    paths = [diagnostic.STM / folder / (name + ext) for name in stm_names
             for folder, ext in (("Inc", ".h"), ("Src", ".c"))]
    paths += [diagnostic.STM / "Inc/motor_output.h"]
    paths += [diagnostic.ESP / (name + ext) for name in esp_names for ext in (".h", ".c")]
    paths += [FIRMWARE / MAIN]
    inputs = {p: p.read_bytes() for p in paths}
    candidate = prepare() if args.candidate else {}
    print("MODE:", "CANDIDATE / PRODUCTION UNCHANGED" if args.candidate else "USER-SAVED FIRMWARE",
          "/ NATIVE PC ONLY", flush=True)
    with tempfile.TemporaryDirectory(prefix="uart-recovery-") as temporary:
        work = Path(temporary)
        for path, raw in inputs.items():
            relative = path.relative_to(FIRMWARE).as_posix()
            text = candidate.get(relative, raw.decode("utf-8").replace("\r\n", "\n"))
            (work / path.name).write_text(text, encoding="utf-8")
            print("TESTED", relative, hashlib.sha256(text.encode()).hexdigest(), flush=True)
        (work / "main.h").write_text(diagnostic.HAL, encoding="utf-8")
        for name in ("stm_uart_stream_host_fixture.c", "uart_recovery_host_fixture.c"):
            shutil.copyfile(HERE / name, work / name)
        main_source = (work / "wifi_link_main.c").read_text(encoding="utf-8")
        constants = [re.search(r"^#define\s+" + name + r"\s+[^\n]+", main_source, re.M)[0]
                     for name in ("STM_STARTUP_SETTLE_MS", "STM_STARTUP_SYNC_WAIT_MS",
                                  "STM_STARTUP_RESPONSE_MS", "STM_STARTUP_MAX_ATTEMPTS")]
        startup = constants + [c_type(main_source, name) for name in
                               ("stm_startup_state_t", "stm_startup_t")]
        startup += ["static stm_startup_t s_stm_startup;"]
        startup += [c_function(main_source, name) for name in
                    ("stm_startup_fail", "stm_startup_send_request", "stm_startup_retry", "stm_startup_step")]
        (work / "startup_functions.h").write_text("\n".join(startup), encoding="utf-8")

        def compile_run(name, unit, dependencies, cases):
            path = work / (name + ".c")
            path.write_text(unit, encoding="utf-8")
            exe = work / (name + (".exe" if os.name == "nt" else ""))
            result = subprocess.run([cc, "-Wall", "-Werror", "-I", str(work), str(path)]
                                    + [str(work / (dep + ".c")) for dep in dependencies]
                                    + ["-o", str(exe)], capture_output=True, text=True, timeout=30)
            if result.returncode:
                raise RuntimeError(result.stdout + result.stderr)
            for case in cases:
                result = subprocess.run([str(exe)] + ([case] if case else []),
                                        capture_output=True, text=True, timeout=20)
                print(result.stdout, end="", flush=True)
                if result.returncode:
                    raise RuntimeError(f"{name} {case}: exit {result.returncode}\n" + result.stderr)

        compile_run("recovery", (work / "uart_recovery_host_fixture.c").read_text(),
                    stm_names[1:] + esp_names, [""])
        fixture = (HERE / "wifi_control_executor_host_fixture.c").read_text()
        compile_run("executor", fixture, esp_names, executor_tests.CASES)
        host = main_tests.host(main_source)
        base = (HERE / "wifi_w5_host_fixture.c").read_text()
        extra = (HERE / "wifi_control_main_host_fixture.c").read_text()
        cases = re.findall(r"^    RUN\(([a-z_]+)\)", base, re.M)
        cases += re.findall(r'\{\s*"([a-z_]+)"\s*,', extra)
        compile_run("adapter", host, esp_names, cases)
        print(f"PASS {len(executor_tests.CASES)} executor + {len(cases)} main adapter regression cases", flush=True)
    assert all(p.read_bytes() == raw for p, raw in inputs.items()), "Production input changed during tests"
    print("Production inputs unchanged. Board build, flash and physical acceptance remain separate.", flush=True)


if __name__ == "__main__":
    run()
