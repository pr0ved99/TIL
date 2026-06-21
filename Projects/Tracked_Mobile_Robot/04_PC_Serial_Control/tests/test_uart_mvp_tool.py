import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import uart_mvp_tool as tool  # noqa: E402


def test_make_cmd_frame():
    frame = tool.make_frame(
        "CMD", seq=4, vx_mmps=80, w_mradps=0, timeout_ms=300
    )
    assert frame == "CMD,seq=4,vx_mmps=80,w_mradps=0,timeout_ms=300\n"


def test_make_raw_frame_adds_newline():
    assert tool.make_frame("RAW", raw="BAD") == "BAD\n"


def test_parse_ack_frame():
    parsed = tool.parse_frame("ACK,seq=4,type=CMD\n")
    assert parsed.frame_type == "ACK"
    assert parsed.fields["seq"] == "4"
    assert parsed.fields["type"] == "CMD"
    assert tool.classify_frame(parsed) == "accepted"


def test_parse_tel_frame_state():
    parsed = tool.parse_frame(
        "TEL,t_ms=123,state=ARMED,batt_mv=0,left_cps=0,right_cps=0,left_pwm=0,right_pwm=0,fault=0\n"
    )
    assert parsed.frame_type == "TEL"
    assert parsed.fields["state"] == "ARMED"
    assert tool.classify_frame(parsed) == "telemetry"


def test_validate_cmd_values_rejects_out_of_range():
    try:
        tool.validate_cmd_values(9999, 0, 300)
    except ValueError as exc:
        assert "vx_mmps" in str(exc)
    else:
        raise AssertionError("expected ValueError")
