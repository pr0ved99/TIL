"""Execute the saved Wi-Fi application's C command functions on the host.

Set W5_HOST_CC to a native tcc/gcc/clang executable. A missing host compiler is
reported as SKIP, never as a matching PASS. Only the extracted C functions are
compiled: this is not an ESP build, UART injection, or RTOS concurrency test.
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

from test_firmware_contract import extract_function, strip_c_comments


TEST_ROOT = Path(__file__).resolve().parent
SOURCE = TEST_ROOT.parent / "esp32_wifi_link/main/wifi_link_main.c"
FIXTURE = TEST_ROOT / "wifi_w5_host_fixture.c"


def c_type(source: str, name: str) -> str:
    match = re.search(rf"typedef\s+(?:enum|struct)\s*\{{[^{{}}]*\}}\s*{name}\s*;", source)
    if not match:
        raise AssertionError(f"production type missing: {name}")
    return match.group()


def c_function(source: str, name: str) -> str:
    matches = list(re.finditer(rf"^static[^\n]*\b{name}\s*\([^;{{}}]*\)\s*\{{", source, re.M))
    if len(matches) != 1:
        raise AssertionError(f"expected one production definition: {name}")
    header = source[matches[0].start():matches[0].end() - 1]
    return header + "{\n" + extract_function(source, name) + "\n}\n"


def host_source(source: str) -> str:
    clean = strip_c_comments(source)
    definitions = []
    for name in ("WS_MAX_CLIENTS", "WIFI_COMMAND_QUEUE_LENGTH", "WIFI_COMMAND_MAX_FRAME_SIZE",
                 "WIFI_COMMAND_RESPONSE_MS", "WIFI_COMMAND_RESULT_QUEUE_LENGTH"):
        match = re.search(rf"^#define\s+{name}\s+([^\n]+)", clean, re.M)
        if not match:
            raise AssertionError(f"production constant missing: {name}")
        definitions.append(f"#define {name} {match.group(1).strip()}")
    for name in ("wifi_command_type_t", "wifi_command_request_t", "wifi_command_result_t",
                 "stm_startup_state_t", "stm_startup_t", "wifi_uart_pending_t"):
        definitions.append(c_type(clean, name))
    functions = []
    for name in ("wifi_command_parse_u32", "wifi_command_parse", "stm_find_field_value",
                 "stm_parse_u32_field", "stm_parse_text_field", "wifi_command_finish",
                 "wifi_command_pending_valid", "wifi_command_step", "wifi_command_handle_response"):
        functions.append(c_function(clean, name))
    fixture = FIXTURE.read_text(encoding="utf-8")
    assert fixture.count("/* PRODUCTION_TYPES */") == fixture.count("/* PRODUCTION_FUNCTIONS */") == 1
    return fixture.replace("/* PRODUCTION_TYPES */", "\n".join(definitions)).replace(
        "/* PRODUCTION_FUNCTIONS */", "\n".join(functions))


class WifiW5UartHostTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compiler = os.environ.get("W5_HOST_CC") or shutil.which("tcc") or shutil.which("gcc")
        if not compiler:
            raise unittest.SkipTest("set W5_HOST_CC to a native C compiler to execute production C")
        cls.source_bytes = SOURCE.read_bytes()
        cls.workspace = tempfile.TemporaryDirectory(prefix="w5-host-")
        cls.addClassCleanup(cls.workspace.cleanup)
        work = Path(cls.workspace.name)
        unit = work / "w5_host.c"
        cls.program = work / ("w5_host.exe" if os.name == "nt" else "w5_host")
        unit.write_text(host_source(cls.source_bytes.decode("utf-8")), encoding="utf-8")
        result = subprocess.run([compiler, "-Wall", "-Werror", str(unit), "-o", str(cls.program)],
                                capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise AssertionError("host test compilation failed:\n" + result.stdout + result.stderr)
        print("Production C SHA256:", hashlib.sha256(cls.source_bytes).hexdigest(), flush=True)

    def check_case(self, case: str) -> None:
        result = subprocess.run([str(self.program), case], capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), "PASS " + case)
        self.assertEqual(SOURCE.read_bytes(), self.source_bytes, "firmware source changed during host tests")

    def test_ping_before_deadline(self): self.check_case("ping_before_deadline")
    def test_disarm_ack_before_deadline(self): self.check_case("disarm_ack_before_deadline")
    def test_wrong_and_startup_sequences(self): self.check_case("wrong_and_startup_sequences")
    def test_wrong_response_kind_and_ack_type(self): self.check_case("wrong_response_kind_and_ack_type")
    def test_matching_stm_error_is_failure(self): self.check_case("matching_stm_error_is_failure")
    def test_nonmatching_error_is_ignored(self): self.check_case("nonmatching_error_is_ignored")
    def test_malformed_response_vectors(self): self.check_case("malformed_response_vectors")
    def test_no_pending_and_duplicate_responses(self): self.check_case("no_pending_and_duplicate_responses")
    def test_telemetry_is_not_a_command_response(self): self.check_case("telemetry_is_not_a_command_response")
    def test_response_at_and_after_deadline(self): self.check_case("response_at_and_after_deadline")
    def test_late_response_cannot_complete_next_request(self): self.check_case("late_response_cannot_complete_next_request")
    def test_closed_connection_has_no_result_delivery(self): self.check_case("closed_connection_has_no_result_delivery")
    def test_old_cleanup_preserves_new_owner(self): self.check_case("old_cleanup_preserves_new_owner")
    def test_orphaned_queued_request_is_not_transmitted(self): self.check_case("orphaned_queued_request_is_not_transmitted")
    def test_expired_queue_request_is_not_transmitted(self): self.check_case("expired_queue_request_is_not_transmitted")
    def test_startup_gate_and_failed_diagnostics(self): self.check_case("startup_gate_and_failed_diagnostics")
    def test_sequence_exhaustion_never_wraps(self): self.check_case("sequence_exhaustion_never_wraps")
    def test_full_result_queue_releases_request(self): self.check_case("full_result_queue_releases_request")
    def test_short_uart_write_has_no_retry(self): self.check_case("short_uart_write_has_no_retry")
    def test_wrong_boot_and_unsupported_command(self): self.check_case("wrong_boot_and_unsupported_command")
    def test_websocket_request_parser_vectors(self): self.check_case("websocket_request_parser_vectors")


if __name__ == "__main__":
    unittest.main(verbosity=2)
