"""Executable contract vectors for the STM32 UART text-frame grammar.

The Python parser below is an independent contract model.  It checks the
accepted language and boundary values, while ``test_firmware_contract.py``
checks that the C source keeps the same exact-field structure.  Target-runtime
UART injection remains a separate hardware verification gate.
"""

from __future__ import annotations

import re
import unittest
from dataclasses import dataclass


U32_MAX = 4_294_967_295
I32_MIN = -2_147_483_648
I32_MAX = 2_147_483_647

SIMPLE_FRAME = re.compile(r"(PING|ARM|DISARM),seq=([0-9]+)", re.ASCII)
CMD_FRAME = re.compile(
    r"CMD,seq=([0-9]+),vx_mmps=(-?[0-9]+),"
    r"w_mradps=(-?[0-9]+),timeout_ms=([0-9]+)",
    re.ASCII,
)


@dataclass(frozen=True)
class ParsedFrame:
    frame_type: str
    seq: int
    vx_mmps: int = 0
    w_mradps: int = 0
    timeout_ms: int = 0


def parse_contract_frame(raw: bytes) -> ParsedFrame | None:
    """Return a frame only when ``raw`` exactly matches the accepted grammar."""
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError:
        return None

    simple = SIMPLE_FRAME.fullmatch(text)
    if simple is not None:
        seq = int(simple.group(2), 10)
        if seq > U32_MAX:
            return None
        return ParsedFrame(simple.group(1), seq)

    command = CMD_FRAME.fullmatch(text)
    if command is None:
        return None

    seq = int(command.group(1), 10)
    vx_mmps = int(command.group(2), 10)
    w_mradps = int(command.group(3), 10)
    timeout_ms = int(command.group(4), 10)
    if seq > U32_MAX or timeout_ms > U32_MAX:
        return None
    if not (I32_MIN <= vx_mmps <= I32_MAX):
        return None
    if not (I32_MIN <= w_mradps <= I32_MAX):
        return None

    return ParsedFrame("CMD", seq, vx_mmps, w_mradps, timeout_ms)


class UartFrameContractTest(unittest.TestCase):
    def test_valid_exact_frames_and_integer_boundaries(self) -> None:
        vectors = {
            b"PING,seq=0": ParsedFrame("PING", 0),
            b"ARM,seq=4294967295": ParsedFrame("ARM", U32_MAX),
            b"DISARM,seq=1": ParsedFrame("DISARM", 1),
            (
                b"CMD,seq=20,vx_mmps=50,w_mradps=0,timeout_ms=500"
            ): ParsedFrame("CMD", 20, 50, 0, 500),
            (
                b"CMD,seq=4294967295,vx_mmps=-2147483648,"
                b"w_mradps=2147483647,timeout_ms=4294967295"
            ): ParsedFrame("CMD", U32_MAX, I32_MIN, I32_MAX, U32_MAX),
        }

        for raw, expected in vectors.items():
            with self.subTest(raw=raw):
                self.assertEqual(parse_contract_frame(raw), expected)

    def test_malformed_frames_are_rejected(self) -> None:
        malformed = (
            b"",
            b"PING",
            b"PING,seq=",
            b"PING,seq=-1",
            b"PING,seq=+1",
            b"PING,seq=4294967296",
            b"PING,seq=1junk",
            b"PING,seq=1,extra=2",
            b"ARMORED,seq=1",
            b"CMDX,seq=1,vx_mmps=0,w_mradps=0,timeout_ms=300",
            b"CMD,seq=1",
            b"CMD,seq=1,w_mradps=0,vx_mmps=0,timeout_ms=300",
            b"CMD,seq=1,vx_mmps=0,vx_mmps=0,w_mradps=0,timeout_ms=300",
            b"CMD,seq=1, vx_mmps=0,w_mradps=0,timeout_ms=300",
            b"CMD,seq=1,vx_mmps=+1,w_mradps=0,timeout_ms=300",
            b"CMD,seq=1,vx_mmps=1junk,w_mradps=0,timeout_ms=300",
            b"CMD,seq=1,vx_mmps=2147483648,w_mradps=0,timeout_ms=300",
            b"CMD,seq=1,vx_mmps=-2147483649,w_mradps=0,timeout_ms=300",
            b"CMD,seq=1,vx_mmps=0,w_mradps=2147483648,timeout_ms=300",
            b"CMD,seq=1,vx_mmps=0,w_mradps=0,timeout_ms=4294967296",
            b"CMD,seq=1,vx_mmps=0,w_mradps=0,timeout_ms=300,extra=1",
            b"CMD,seq=1,vx_mmps=0,w_mradps=0,timeout_ms=300\x00hidden",
            b"CMD,seq=1,vx_mmps=0,w_mradps=0,timeout_ms=300\rhidden",
            "PING,seq=１".encode("utf-8"),
        )

        for raw in malformed:
            with self.subTest(raw=raw):
                self.assertIsNone(parse_contract_frame(raw))


if __name__ == "__main__":
    unittest.main()
