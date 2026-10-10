"""Run ARM/CMD parser C on the host, without ESP/STM or UART adapters.

Default: compile the user's saved wifi_control_contract.h/.c. Missing input or
compiler is SKIP. WIFI_CONTROL_INPUT_GUIDE explicitly selects candidate Markdown
blocks instead; candidate results never count as saved firmware validation.
"""

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
FIXTURE = ROOT / "wifi_control_parser_host_fixture.c"
OK, BAD_FORMAT, OUT_OF_RANGE = 0, 1, 2


class WifiControlParserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = (os.environ.get("WIFI_CONTROL_HOST_CC") or os.environ.get("W5_HOST_CC")
                    or shutil.which("tcc") or shutil.which("gcc") or shutil.which("clang"))
        if not compiler:
            raise unittest.SkipTest("native C compiler missing; set WIFI_CONTROL_HOST_CC")

        guide = os.environ.get("WIFI_CONTROL_INPUT_GUIDE")
        cls.input_paths: list[Path]
        if guide:
            cls.input_paths = [Path(guide).resolve()]
            cls.input_bytes = [cls.input_paths[0].read_bytes()]
            blocks = re.findall(r"```c\n(.*?)\n```", cls.input_bytes[0].decode("utf-8").replace("\r\n", "\n"), re.S)
            if len(blocks) != 2:
                raise AssertionError("candidate guide must contain exactly header and source C blocks")
            units = [block + "\n" for block in blocks]
            cls.mode = "CANDIDATE GUIDE ONLY"
        else:
            cls.input_paths = [MAIN / "wifi_control_contract.h", MAIN / "wifi_control_contract.c"]
            if not all(p.is_file() for p in cls.input_paths):
                raise unittest.SkipTest("user's ARM/CMD .h/.c input not saved; no production parser result")
            cls.input_bytes = [p.read_bytes() for p in cls.input_paths]
            units = [raw.decode("utf-8") for raw in cls.input_bytes]
            cls.mode = "SAVED PARSER C ONLY"

        cls.work = tempfile.TemporaryDirectory(prefix="wifi-control-parser-")
        cls.addClassCleanup(cls.work.cleanup)
        work = Path(cls.work.name)
        names = ["wifi_control_contract.h", "wifi_control_contract.c"]
        for name, unit in zip(names, units):
            (work / name).write_text(unit, encoding="utf-8")
        cls.program = work / ("parser.exe" if os.name == "nt" else "parser")
        result = subprocess.run(
            [compiler, "-Wall", "-Werror", "-I", str(work), str(work / names[1]),
             str(FIXTURE), "-o", str(cls.program)],
            capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise AssertionError("host C compilation failed:\n" + result.stdout + result.stderr)

        print("Mode:", cls.mode, flush=True)
        for path, raw in zip(cls.input_paths, cls.input_bytes):
            print(path.name, "SHA256:", hashlib.sha256(raw).hexdigest(), flush=True)

    @staticmethod
    def arm(**fields) -> bytes:
        values = dict(boot_id=7, request_id=1, ticket=9)
        values.update(fields)
        return ("ARM," + ",".join(f"{key}={value}" for key, value in values.items())).encode("ascii")

    @staticmethod
    def cmd(**fields) -> bytes:
        values = dict(boot_id=7, request_id=2, control_id=1, ticket=10, vx_mmps=0, w_mradps=0)
        values.update(fields)
        return ("CMD," + ",".join(f"{key}={value}" for key, value in values.items())).encode("ascii")

    def check(self, payload: bytes, status=OK, *, length=None, mode="normal", **expected):
        count = len(payload) if length is None else length
        result = subprocess.run([str(self.program), payload.hex(), str(count), mode],
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        fields = {key: int(value) for key, value in
                  (item.split("=", 1) for item in result.stdout.strip().split())}
        self.assertEqual(fields["status"], status, repr(payload))
        self.assertEqual(fields["zero_null"], 0)
        if status != OK:
            self.assertEqual(fields["unchanged"], 1, "failed parse modified output")
        else:
            self.assertEqual((fields["session"], fields["accepted"], fields["expires"]), (0, 0, 0))
            for key, value in expected.items():
                self.assertEqual(fields[key], value, (key, repr(payload)))
        for path, raw in zip(self.input_paths, self.input_bytes):
            self.assertEqual(path.read_bytes(), raw, "input changed during host test")
        return fields

    def test_arm_fields_and_absent_motion_metadata(self):
        self.check(self.arm(), type=0, boot=7, request=1, control=0, ticket=9, vx=0, w=0, zero=1)

    def test_zero_command_fields(self):
        self.check(self.cmd(), type=1, control=1, ticket=10, vx=0, w=0, zero=1)

    def test_format_ok_is_not_zero_only_permission(self):
        self.check(self.cmd(vx_mmps=50), vx=50, w=0, zero=0)
        self.check(self.cmd(w_mradps=-1), vx=0, w=-1, zero=0)

    def test_velocity_boundary_matrix(self):
        for vx in (-100, 0, 100):
            for w in (-500, 0, 500):
                with self.subTest(vx=vx, w=w):
                    self.check(self.cmd(vx_mmps=vx, w_mradps=w), vx=vx, w=w, zero=int(vx == w == 0))

    def test_velocity_outside_boundaries(self):
        for field, values in (("vx_mmps", (-101, 101)), ("w_mradps", (-501, 501))):
            for value in values:
                with self.subTest(field=field, value=value):
                    self.check(self.cmd(**{field: value}), OUT_OF_RANGE)

    def test_u32_max_and_boot_zero(self):
        self.check(self.arm(boot_id=0), boot=0)
        self.check(self.arm(boot_id=4294967295, request_id=4294967295, ticket=4294967295),
                   boot=4294967295, request=4294967295, ticket=4294967295)
        self.check(self.cmd(control_id=4294967295), control=4294967295)

    def test_zero_request_control_ticket_ids_rejected(self):
        for field in ("request_id", "ticket"):
            self.check(self.arm(**{field: 0}), BAD_FORMAT)
        for field in ("request_id", "control_id", "ticket"):
            self.check(self.cmd(**{field: 0}), BAD_FORMAT)

    def test_unsigned_overflow_and_invalid_signed_tokens(self):
        for value in ("4294967296", "99999999999999999999", "-1", "+1", "", "1.0", "1e1"):
            self.check(self.arm(ticket=value), BAD_FORMAT)
        for value in ("+1", "--1", "-", "", "1.0", "1e1", "2147483648", "-2147483649", "-4294967296"):
            self.check(self.cmd(vx_mmps=value), BAD_FORMAT)

    def test_int32_extremes_are_parsed_then_range_rejected(self):
        for value in (-2147483648, 2147483647):
            self.check(self.cmd(vx_mmps=value), OUT_OF_RANGE)

    def test_no_whitespace_control_bytes_or_non_ascii(self):
        for byte in (0, 9, 10, 13, 32, 127, 128, 255):
            raw = self.arm()
            self.check(raw[:5] + bytes([byte]) + raw[6:], BAD_FORMAT)
        self.check(self.arm() + b"\n", BAD_FORMAT)

    def test_extra_missing_reordered_and_duplicate_fields(self):
        for raw in (
            self.arm() + b",control_id=1", self.cmd() + b",timeout_ms=300",
            self.cmd() + b",ticket=11", self.cmd().replace(b",control_id=1", b""),
            self.cmd().replace(b",vx_mmps=0,w_mradps=0", b",w_mradps=0,vx_mmps=0"),
            b"ARM,request_id=1,boot_id=7,ticket=9", b"ARM,boot_id=7,request_id=1,ticket=9,",
            b"arm,boot_id=7,request_id=1,ticket=9", b"PING,boot_id=7,request_id=1,ticket=9",
            b"CMD", b"ARM", self.cmd()[:-1],
        ):
            self.check(raw, BAD_FORMAT)

    def test_actual_length_controls_input_without_terminator(self):
        raw = self.arm()
        self.check(raw + b"ignored\x00\xff", length=len(raw), type=0, ticket=9)
        self.check(raw + b"ignored\x00\xff", BAD_FORMAT)
        self.check(raw, BAD_FORMAT, length=0)

    def test_frame_size_exact_limit_and_over_limit(self):
        raw = self.arm()
        exact = raw.replace(b"boot_id=7", b"boot_id=" + b"0" * (128 - len(raw)) + b"7")
        self.assertEqual(len(exact), 128)
        self.check(exact, boot=7)
        self.check(exact + b"0", BAD_FORMAT)
        self.check(b"x" * 129, BAD_FORMAT)

    def test_null_arguments_and_empty_text(self):
        self.check(self.arm(), BAD_FORMAT, mode="null_text")
        self.check(self.arm(), BAD_FORMAT, mode="null_out")
        self.check(b"", BAD_FORMAT)

    def test_leading_zero_and_negative_zero_values(self):
        self.check(self.arm(request_id="0001", ticket="0009"), request=1, ticket=9)
        self.check(self.cmd(vx_mmps="-0", w_mradps="000"), vx=0, w=0, zero=1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
