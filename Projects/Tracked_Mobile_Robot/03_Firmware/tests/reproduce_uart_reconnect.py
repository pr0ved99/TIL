"""Diagnostic reproduction, not an acceptance PASS or an MCU firmware build.

Run from any working directory; compiler discovery follows the Wi-Fi host tests.
The exact saved STM protocol/stream/parser/ring/mapper and ESP control modules run
on the PC. Only HAL, motor hardware and IRQ primitives are replaced by adapters.
No serial port is opened and no command is sent to a board.
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
STM = ROOT.parent / "stm32_uart_mvp/Core"
ESP = ROOT.parent / "esp32_wifi_link/main"
HAL = """#ifndef HOST_MAIN_H
#define HOST_MAIN_H
#include <stdint.h>
#include <stddef.h>
typedef struct { int unused; } UART_HandleTypeDef;
typedef struct { int unused; } TIM_HandleTypeDef;
typedef enum { HAL_OK, HAL_ERROR } HAL_StatusTypeDef;
typedef enum { GPIO_PIN_RESET, GPIO_PIN_SET } GPIO_PinState;
#define ESTOP_SENSE_GPIO_Port ((void *)0)
#define ESTOP_SENSE_Pin 7
uint32_t HAL_GetTick(void);
GPIO_PinState HAL_GPIO_ReadPin(void *, uint16_t);
HAL_StatusTypeDef HAL_UART_Receive_IT(UART_HandleTypeDef *, uint8_t *, uint16_t);
HAL_StatusTypeDef HAL_UART_Transmit(UART_HandleTypeDef *, uint8_t *, uint16_t, uint32_t);
static inline uint32_t __get_PRIMASK(void) { return 0; }
static inline void __disable_irq(void) { }
static inline void __set_PRIMASK(uint32_t mask) { (void)mask; }
#endif
"""


def main() -> int:
    compiler = (os.environ.get("WIFI_CONTROL_HOST_CC") or os.environ.get("W5_HOST_CC")
                or shutil.which("tcc") or shutil.which("gcc") or shutil.which("clang"))
    if not compiler:
        raise SystemExit("NOT RUN: set WIFI_CONTROL_HOST_CC to a native C compiler")
    stm_names = ("uart_mvp_protocol", "uart_frame_parser", "ring_buffer", "drive_command_mapper")
    esp_names = ("wifi_control_contract", "wifi_control_ticket", "wifi_control_owner",
                 "wifi_control_state", "wifi_control_executor")
    paths = [STM / directory / (name + extension) for name in stm_names
             for directory, extension in (("Inc", ".h"), ("Src", ".c"))]
    paths += [STM / "Inc/motor_output.h"]
    paths += [ESP / (name + extension) for name in esp_names for extension in (".h", ".c")]
    paths += [ROOT / "stm_uart_stream_host_fixture.c"]
    inputs = {path: path.read_bytes() for path in paths}
    print("MODE: SAVED C DIAGNOSTIC / HAL-MOTOR MOCK / NO BOARD IO", flush=True)
    with tempfile.TemporaryDirectory(prefix="stm-uart-reconnect-") as temporary:
        work = Path(temporary)
        for path, raw in inputs.items():
            (work / path.name).write_bytes(raw)
            print(path.name, "SHA256", hashlib.sha256(raw).hexdigest(), flush=True)
        (work / "main.h").write_text(HAL, encoding="utf-8")
        program = work / ("reproduce.exe" if os.name == "nt" else "reproduce")
        # protocol.c is included in the fixture to observe its internal state.
        sources = [work / (name + ".c") for name in stm_names[1:] + esp_names]
        sources += [work / "stm_uart_stream_host_fixture.c"]
        result = subprocess.run([compiler, "-Wall", "-Werror", "-I", str(work)]
                                + [str(p) for p in sources] + ["-o", str(program)],
                                capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise SystemExit(result.stdout + result.stderr)
        result = subprocess.run([str(program)], capture_output=True, text=True, timeout=10)
        print(result.stdout, end="", flush=True)
        print(result.stderr, end="", flush=True)
        for path, raw in inputs.items():
            if path.read_bytes() != raw:
                raise SystemExit("Source changed during diagnostic: " + str(path))
        return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
