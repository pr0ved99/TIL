"""Execute candidate/saved state C with saved owner C; no UART/RTOS evidence."""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAIN = ROOT.parent / "esp32_wifi_link/main"
CASES = (
    "initial_arguments", "arm_gates", "arm_queue_boundary", "ack_boundary",
    "reply_identity", "cmd_before_arm_ack", "zero_ack_tel_order", "zero_telemetry_guards",
    "first_cmd_boundary", "source_deadline_not_telemetry", "tel_boundary", "cmd_binding",
    "cmd_queue_boundary", "zero_only_and_single_pending", "owner_close_and_late_ack",
    "stop_order_and_rearm", "fault_can_confirm_stop", "stop_send_boundary",
    "stop_ack_boundary", "stop_confirm_boundary", "blocked_manual_recovery",
    "active_fault_state_age", "stm_wrap_and_reset", "frozen_stm_clock",
    "clock_backward_and_startup", "err_and_tx_failure", "no_automatic_resume",
)


class WifiControlStateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = (os.environ.get("WIFI_CONTROL_HOST_CC") or os.environ.get("W5_HOST_CC")
                    or shutil.which("tcc") or shutil.which("gcc") or shutil.which("clang"))
        if not compiler:
            raise unittest.SkipTest("native C compiler missing; set WIFI_CONTROL_HOST_CC")
        guide = os.environ.get("WIFI_CONTROL_STATE_GUIDE")
        names = ("wifi_control_state.h", "wifi_control_state.c")
        if guide:
            path = Path(guide).resolve()
            cls.inputs = [(path, path.read_bytes())]
            blocks = re.findall(r"```c\n(.*?)\n```",
                                cls.inputs[0][1].decode("utf-8").replace("\r\n", "\n"), re.S)
            if len(blocks) != 2:
                raise AssertionError("state guide must contain exactly two C blocks")
            units = [block + "\n" for block in blocks]
            mode = "CANDIDATE STATE GUIDE WITH SAVED OWNER C"
        else:
            if not all((MAIN / name).is_file() for name in names):
                raise unittest.SkipTest("user state .h/.c not saved; no saved-module result")
            cls.inputs = [(MAIN / name, (MAIN / name).read_bytes()) for name in names]
            units = [raw.decode("utf-8") for _, raw in cls.inputs]
            mode = "SAVED STATE AND OWNER C ONLY"
        dependencies = ("wifi_control_contract.h", "wifi_control_owner.h", "wifi_control_owner.c")
        for name in dependencies:
            path = MAIN / name
            if not path.is_file():
                raise unittest.SkipTest("saved dependency missing: " + name)
            cls.inputs.append((path, path.read_bytes()))
        cls.work = tempfile.TemporaryDirectory(prefix="wifi-control-state-")
        cls.addClassCleanup(cls.work.cleanup)
        work = Path(cls.work.name)
        for name, unit in zip(names, units):
            (work / name).write_text(unit, encoding="utf-8")
        for path, raw in cls.inputs[-len(dependencies):]:
            (work / path.name).write_bytes(raw)
        cls.program = work / ("state.exe" if os.name == "nt" else "state")
        result = subprocess.run(
            [compiler, "-Wall", "-Werror", "-I", str(work), str(work / names[1]),
             str(work / "wifi_control_owner.c"), str(ROOT / "wifi_control_state_host_fixture.c"),
             "-o", str(cls.program)], capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise AssertionError("host compilation failed:\n" + result.stdout + result.stderr)
        print("Mode:", mode, flush=True)
        for path, raw in cls.inputs:
            print(path.name, "SHA256:", hashlib.sha256(raw).hexdigest(), flush=True)

    def check_case(self, case):
        result = subprocess.run([str(self.program), case], capture_output=True,
                                text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), "PASS " + case)
        for path, raw in self.inputs:
            self.assertEqual(path.read_bytes(), raw, "input changed during test")


def make_test(case):
    def test(self):
        self.check_case(case)
    return test


for case in CASES:
    setattr(WifiControlStateTest, "test_" + case, make_test(case))

if __name__ == "__main__":
    unittest.main(verbosity=2)
