"""Test candidate or saved ticket C; no UART, owner FSM or RTOS evidence."""

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
    "issue_bindings", "valid_window", "single_use", "wrong_binding",
    "live_ticket_preserved", "expired_replacement", "invalidate",
    "counter_exhaustion", "clock_rollback", "time_overflow",
    "invalid_arguments", "boot_zero",
)


class WifiControlTicketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = (os.environ.get("WIFI_CONTROL_HOST_CC") or os.environ.get("W5_HOST_CC")
                    or shutil.which("tcc") or shutil.which("gcc") or shutil.which("clang"))
        if not compiler:
            raise unittest.SkipTest("native C compiler missing; set WIFI_CONTROL_HOST_CC")
        guide = os.environ.get("WIFI_CONTROL_TICKET_GUIDE")
        names = ("wifi_control_ticket.h", "wifi_control_ticket.c")
        if guide:
            path = Path(guide).resolve()
            cls.inputs = [(path, path.read_bytes())]
            units = re.findall(r"```c\n(.*?)\n```", cls.inputs[0][1].decode("utf-8")
                               .replace("\r\n", "\n"), re.S)
            if len(units) != 2:
                raise AssertionError("ticket guide must contain exactly two C blocks")
            units = [unit + "\n" for unit in units]
            mode = "CANDIDATE TICKET GUIDE ONLY"
        else:
            if not all((MAIN / name).is_file() for name in names):
                raise unittest.SkipTest("user ticket .h/.c not saved; no saved-module result")
            cls.inputs = [(MAIN / name, (MAIN / name).read_bytes()) for name in names]
            units = [raw.decode("utf-8") for _, raw in cls.inputs]
            mode = "SAVED TICKET C ONLY"

        contract = MAIN / "wifi_control_contract.h"
        if not contract.is_file():
            raise unittest.SkipTest("saved request header missing")
        cls.inputs.append((contract, contract.read_bytes()))
        cls.work = tempfile.TemporaryDirectory(prefix="wifi-control-ticket-")
        cls.addClassCleanup(cls.work.cleanup)
        work = Path(cls.work.name)
        for name, unit in zip(names, units):
            (work / name).write_text(unit, encoding="utf-8")
        (work / contract.name).write_bytes(cls.inputs[-1][1])
        cls.program = work / ("ticket.exe" if os.name == "nt" else "ticket")
        result = subprocess.run(
            [compiler, "-Wall", "-Werror", "-I", str(work), str(work / names[1]),
             str(ROOT / "wifi_control_ticket_host_fixture.c"), "-o", str(cls.program)],
            capture_output=True, text=True, timeout=30)
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
    setattr(WifiControlTicketTest, "test_" + case, make_test(case))

if __name__ == "__main__":
    unittest.main(verbosity=2)
