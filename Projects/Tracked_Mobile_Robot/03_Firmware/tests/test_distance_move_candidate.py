"""Compile/run distance-move C on the PC; never build/flash STM or send commands."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
CORE = HERE.parent / "stm32_uart_mvp/Core"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cc", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--saved", action="store_true",
                        help="Test user-typed Core files instead of the candidate")
    args = parser.parse_args()
    paths = ([CORE / "Inc/distance_move.h", CORE / "Src/distance_move.c"]
             if args.saved else [HERE / "distance_move_candidate" / name
                                for name in ("distance_move.h", "distance_move.c")])
    fixture = HERE / "distance_move_host_fixture.c"
    inputs = {p: p.read_bytes() for p in [*paths, fixture, Path(__file__).resolve()]}
    # Verify that neither existing firmware tree is modified by this PC check.
    firmware_paths = [
        *CORE.rglob("*.c"), *CORE.rglob("*.h"),
        *(HERE.parent / "esp32_wifi_link/main").glob("*.c"),
        *(HERE.parent / "esp32_wifi_link/main").glob("*.h"),
    ]
    firmware = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in firmware_paths}
    output = args.output.resolve()
    if output in {p.resolve() for p in [*inputs, *firmware]}:
        parser.error("Output must not overwrite source/input files")
    logs = []
    with tempfile.TemporaryDirectory(prefix="distance-move-pc-") as tmp:
        temp = Path(tmp)
        for path in paths:
            (temp / path.name).write_bytes(inputs[path])
        exe = temp / "distance_move_test.exe"
        commands = [
            [str(args.cc), "-Wall", "-Werror", "-I", str(temp),
             str(fixture), str(temp / "distance_move.c"), "-o", str(exe)],
            [str(exe)],
        ]
        for cmd in commands:
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", timeout=30)
            logs.append(result.stdout + result.stderr)
            if result.returncode:
                raise RuntimeError(f"PC check failed ({result.returncode}): {logs[-1]}")
    if not all(p.read_bytes() == raw for p, raw in inputs.items()):
        raise RuntimeError("A test input changed")
    if not all(hashlib.sha256(p.read_bytes()).hexdigest() == digest
               for p, digest in firmware.items()):
        raise RuntimeError("A firmware source changed")
    report = {
        "status": "PASS", "mode": "SAVED_MODULE" if args.saved else "CANDIDATE_MODULE",
        "scope": __doc__, "compiler": str(args.cc), "checks": "".join(logs).strip(),
        "firmware_unchanged": True,
        "inputs": {str(p.relative_to(PROJECT)): hashlib.sha256(raw).hexdigest()
                   for p, raw in inputs.items()},
        "limits": [
            "Synthetic host execution, not an STM build or physical test",
            "Module not connected to sampling/UART/ESP/PWM/safety supervisor yet",
            "100ms production encoder snapshots cannot satisfy the 20ms age bound",
            "TARGET_REACHED means output cutoff criteria, not mechanical standstill",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print(report["checks"])
    print("Production firmware unchanged; no target build, flash or motion.")


if __name__ == "__main__":
    main()
