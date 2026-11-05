"""Read-only socket record check and monitoring RC calculation, not assembly PASS."""
import hashlib
import json
import math
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
VRT = ROOT / "09_Electrical_Design/VeroRoute/Tracked_Mobile_Robot_Perfboard_RevC_Estop_Logic_Power_UART_Debug_ENC_Conditioning_WIP.vrt"
b = VRT.read_bytes()
digest = hashlib.sha256(b).hexdigest()
# This narrow reader applies only to this already-reviewed file format/baseline.
if digest != "09c1546d04eeaf581bc55ea9717965a56fd6dac742b565f9796924bdf8fbef78":
    raise ValueError("VRT changed; review record format and physical mapping again")


def socket_records(name):
    """Numbered labels follow node/original IDs, layer and two pin offsets.

    Component::Save in VeroRoute source serializes the 21 bytes BEFORE QString:
    int node, int orig1, int orig2, uchar layer, int row_offset, int col_offset.
    A following int=4 is label alignment, NOT the current pin's net.
    """
    start = b.index(name.encode("utf-16-be"))
    cursor = start
    result = {}
    for pin in range(1, 20):
        label = str(pin).encode("utf-16-be")
        marker = struct.pack(">I", len(label)) + label + struct.pack(">I", 4)
        pos = b.find(marker, cursor, start + 4000)
        if pos < 0:
            raise ValueError((name, pin, "pin record missing"))
        result[pin] = {"net": struct.unpack_from(">i", b, pos - 21)[0],
                       "label_offset": pos}
        cursor = pos + len(marker)
    return result


even = socket_records("H_NUC_LOW_R28")
odd = socket_records("H_NUC_LOW_R29")
# Independent dated baseline: 3V3, encoder PA0/PA1, PWM PB7.
for pin, net in [(8, 11), (14, 21), (15, 22)]:
    if even[pin]["net"] != net:
        raise ValueError(("known even pin mismatch", pin))
if odd[11]["net"] != 4:
    raise ValueError("known PB7 pin mismatch")
signals = [
    ("I_LEFT", "PC0", 38, "H_NUC_LOW_R28", 19, even, 24, 28),
    ("I_RIGHT", "PC1", 36, "H_NUC_LOW_R28", 18, even, 23, 28),
    ("T_LEFT", "PC2", 35, "H_NUC_LOW_R29", 18, odd, 23, 29),
    ("T_RIGHT", "PC3", 37, "H_NUC_LOW_R29", 19, odd, 24, 29),
]
pins = []
for signal, mcu, cn7, socket, pin, records, col, row in signals:
    record = records[pin]
    if record["net"] != 0:
        raise ValueError((signal, "existing external net assigned"))
    pins.append({"signal": signal, "mcu_candidate": mcu,
                 "cn7_pin": cn7, "socket": socket, "socket_pin": pin,
                 "component_side_col": col, "component_side_row": row,
                 **record, "physical_access": "UNCONFIRMED",
                 "bridge_check": "REQUIRED" if mcu in ("PC0", "PC1") else "N/A"})
pin_report = {"status": "DESIGN_RECORD_CHECK_ONLY", "vrt_sha256": digest,
              "source_format_reference": "https://sources.debian.org/src/veroroute/2.28-1/Src/Component.h",
              "scope": "two socket pin records, not whole netlist or physical continuity",
              "known_reference_pins_matched": 4, "candidates": pins}
(HERE / "pin_access_review.json").write_text(
    json.dumps(pin_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

r, c = 12000.0, 100e-9
tau = r * c
rc = {"status": "CALCULATED_CANDIDATE_NOT_HARDWARE_VALIDATED",
      "series_resistor_ohm": r, "cap_after_resistor_F": c,
      "series_resistor_min_1pct_ohm": r * .99,
      "sensor_datasheet_resistive_load_min_ohm": 10000,
      "sensor_direct_capacitance_max_F": 4.7e-9,
      "nominal_fc_Hz": 1 / (2 * math.pi * tau),
      "nominal_tau_ms": tau * 1000,
      "nominal_10_to_90pct_ms": math.log(9) * tau * 1000,
      "ideal_attenuation_at_19000Hz_dB": -10 * math.log10(1 + (2 * math.pi * 19000 * tau)**2),
      "full_scale_settle_half_LSB_ms_R1pct_Cmax120nF": r * 1.01 * 120e-9 * math.log(8192) * 1000,
      "two_ntc_divider_max_mA_R1pct_short": 2 * 3.3 / 9900 * 1000,
      "two_current_IC_max_mA_no_output_load": 24,
      "scope": "first-order RC math only; output stability, cable capacitance, leakage, protection and ADC schedule pending"}
(HERE / "current_rc_candidate.json").write_text(
    json.dumps(rc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"known_reference_pins_matched": 4, "candidate_net0_count": len(pins),
                  "rc_candidate": rc}, ensure_ascii=False, indent=2))
