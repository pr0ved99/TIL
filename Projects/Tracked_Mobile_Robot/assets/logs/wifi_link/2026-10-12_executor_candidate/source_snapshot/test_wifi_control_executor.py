"""Native executor C with saved dependencies; physical UART/RTOS evidence excluded."""
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
    "normal", "admission", "ticket_expiry", "queue_expiry", "cancel_order",
    "connection_identity", "cancel_during_tx", "partial_tx", "response_identity",
    "ack_deadline", "output_and_copy", "zero_only_and_old_owner", "cmd_queue_expiry",
    "source_and_blocked", "ticket_reuse_and_startup", "long_tx_completion", "seq_zero",
)


class WifiControlExecutorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = (os.environ.get("WIFI_CONTROL_HOST_CC") or os.environ.get("W5_HOST_CC")
                    or shutil.which("tcc") or shutil.which("gcc") or shutil.which("clang"))
        if not compiler:
            raise unittest.SkipTest("native compiler missing; set WIFI_CONTROL_HOST_CC")
        guide = os.environ.get("WIFI_CONTROL_EXECUTOR_GUIDE")
        names = ("wifi_control_executor.h", "wifi_control_executor.c")
        if guide:
            path = Path(guide).resolve()
            cls.inputs = [(path, path.read_bytes())]
            blocks = re.findall(r"```c\n(.*?)\n```",
                                cls.inputs[0][1].decode("utf-8").replace("\r\n", "\n"), re.S)
            if len(blocks) != 2:
                raise AssertionError("executor guide must contain exactly two C blocks")
            units = [(block + "\n").encode("utf-8") for block in blocks]
            mode = "CANDIDATE EXECUTOR WITH SAVED CONTROL MODULES"
        else:
            if not all((MAIN / name).is_file() for name in names):
                raise unittest.SkipTest("user executor .h/.c not saved; no saved-module result")
            cls.inputs = [(MAIN / name, (MAIN / name).read_bytes()) for name in names]
            units = [raw for _, raw in cls.inputs]
            mode = "SAVED EXECUTOR AND CONTROL MODULES ONLY"
        dependencies = (
            "wifi_control_contract.h", "wifi_control_contract.c",
            "wifi_control_ticket.h", "wifi_control_ticket.c",
            "wifi_control_owner.h", "wifi_control_owner.c",
            "wifi_control_state.h", "wifi_control_state.c",
        )
        for name in dependencies:
            path = MAIN / name
            cls.inputs.append((path, path.read_bytes()))
        cls.work = tempfile.TemporaryDirectory(prefix="wifi-control-executor-")
        cls.addClassCleanup(cls.work.cleanup)
        work = Path(cls.work.name)
        for name, raw in zip(names, units):
            (work / name).write_bytes(raw)
        for path, raw in cls.inputs[-len(dependencies):]:
            (work / path.name).write_bytes(raw)
        cls.program = work / ("executor.exe" if os.name == "nt" else "executor")
        sources = [work / names[1]] + [work / n for n in dependencies if n.endswith(".c")]
        result = subprocess.run(
            [compiler, "-Wall", "-Werror", "-I", str(work)] + [str(p) for p in sources]
            + [str(ROOT / "wifi_control_executor_host_fixture.c"), "-o", str(cls.program)],
            capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise AssertionError("host compilation failed:\n" + result.stdout + result.stderr)
        print("Mode:", mode, flush=True)
        for path, raw in cls.inputs:
            print(path.name, "SHA256:", hashlib.sha256(raw).hexdigest(), flush=True)

    def check_case(self, case):
        result = subprocess.run([str(self.program), case], capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), "PASS " + case)
        for path, raw in self.inputs:
            self.assertEqual(path.read_bytes(), raw, "input changed during test")


def make_test(case):
    def test(self):
        self.check_case(case)
    return test


for case in CASES:
    setattr(WifiControlExecutorTest, "test_" + case, make_test(case))

if __name__ == "__main__":
    unittest.main(verbosity=2)
