"""Build PC lessons in a temporary directory. Never builds/flashes board firmware."""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import tempfile


def executable(explicit, names):
    if explicit:
        found = shutil.which(explicit)
        if found:
            return found
        raise SystemExit(f"Executable not found: {explicit}")
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit("Tool missing: provide --cc and --node (no lessons marked PASS)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cc", help="C compiler executable: gcc, clang or tcc")
    parser.add_argument("--node", help="Node.js executable")
    parser.add_argument("--lesson", choices=["01", "02", "03", "04", "05"],
                        help="Run one lesson only; omit to run all five")
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    project = here.parents[2]
    stm = project / "03_Firmware/stm32_uart_mvp/Core"
    esp = project / "03_Firmware/esp32_wifi_link/main"
    lessons = [
        ("01_c_and_time", []),
        ("02_stream_parser", [stm / "Src/ring_buffer.c", stm / "Src/uart_frame_parser.c"]),
        ("03_output_and_encoder", [stm / "Src/drive_command_mapper.c", stm / "Src/encoder_speed.c"]),
        ("04_control_flow", [esp / f"wifi_control_{name}.c"
                             for name in ("contract", "ticket", "owner", "state", "executor")]),
    ]
    selected = [lesson for lesson in lessons
                if args.lesson is None or lesson[0].startswith(args.lesson + "_")]
    run_js = args.lesson in (None, "05")
    cc = (executable(args.cc or os.environ.get("W5_HOST_CC"), ["gcc", "clang", "tcc", "cc"])
          if selected else None)
    node = executable(args.node, ["node"]) if run_js else None
    if selected:
        with tempfile.TemporaryDirectory(prefix="robot_textbook_") as temporary:
            for name, sources in selected:
                target = Path(temporary) / (name + (".exe" if os.name == "nt" else ""))
                print(f"\n=== {name} ===", flush=True)
                command = [cc, "-std=c11", "-Wall", "-Werror",
                           "-I", str(stm / "Inc"), "-I", str(esp),
                           str(here / f"{name}.c"), *map(str, sources), "-o", str(target)]
                subprocess.run(command, check=True)
                subprocess.run([str(target)], check=True)
    if run_js:
        subprocess.run([node, str(here / "05_browser_timing.js")], check=True)
    summary = f"PC lesson {args.lesson} passed." if args.lesson else "All 5 PC lessons passed."
    print(f"\n{summary} No board, UART or network operation performed.")


if __name__ == "__main__":
    main()
