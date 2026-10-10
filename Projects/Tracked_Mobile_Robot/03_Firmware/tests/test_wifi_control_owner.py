"""Run owner C with saved ticket C; no UART, ACK, FSM or RTOS evidence."""

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
    "initial_and_binding", "single_controller", "same_session_rearm",
    "new_session_rearm", "revoke_preserves_pool", "id_sequence",
    "exhaustion", "invalid_arguments", "ticket_consumption_keeps_owner",
)


class WifiControlOwnerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = (os.environ.get("WIFI_CONTROL_HOST_CC") or os.environ.get("W5_HOST_CC")
                    or shutil.which("tcc") or shutil.which("gcc") or shutil.which("clang"))
        if not compiler:
            raise unittest.SkipTest("native C compiler missing; set WIFI_CONTROL_HOST_CC")
        guide = os.environ.get("WIFI_CONTROL_OWNER_GUIDE")
        names = ("wifi_control_owner.h", "wifi_control_owner.c")
        if guide:
            path = Path(guide).resolve()
            cls.inputs = [(path, path.read_bytes())]
            units = re.findall(r"```c\n(.*?)\n```", cls.inputs[0][1].decode("utf-8")
                               .replace("\r\n", "\n"), re.S)
            if len(units) != 2:
                raise AssertionError("owner guide must contain exactly two C blocks")
            units = [unit + "\n" for unit in units]
            mode = "CANDIDATE OWNER GUIDE WITH SAVED TICKET C"
        else:
            if not all((MAIN / name).is_file() for name in names):
                raise unittest.SkipTest("user owner .h/.c not saved; no saved-module result")
            cls.inputs = [(MAIN / name, (MAIN / name).read_bytes()) for name in names]
            units = [raw.decode("utf-8") for _, raw in cls.inputs]
            mode = "SAVED OWNER AND TICKET C ONLY"

        dependencies = ("wifi_control_contract.h", "wifi_control_ticket.h", "wifi_control_ticket.c")
        for name in dependencies:
            path = MAIN / name
            if not path.is_file():
                raise unittest.SkipTest("saved dependency missing: " + name)
            cls.inputs.append((path, path.read_bytes()))
        cls.work = tempfile.TemporaryDirectory(prefix="wifi-control-owner-")
        cls.addClassCleanup(cls.work.cleanup)
        work = Path(cls.work.name)
        for name, unit in zip(names, units):
            (work / name).write_text(unit, encoding="utf-8")
        for path, raw in cls.inputs[-len(dependencies):]:
            (work / path.name).write_bytes(raw)
        cls.program = work / ("owner.exe" if os.name == "nt" else "owner")
        result = subprocess.run(
            [compiler, "-Wall", "-Werror", "-I", str(work), str(work / names[1]),
             str(work / "wifi_control_ticket.c"), str(ROOT / "wifi_control_owner_host_fixture.c"),
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
    setattr(WifiControlOwnerTest, "test_" + case, make_test(case))

if __name__ == "__main__":
    unittest.main(verbosity=2)
