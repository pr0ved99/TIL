"""103JT divider design calculations, not board measurements (stdlib only)."""
import csv
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
# SEMITEC P9-JT-Thermistor.pdf, 103JT nominal table, converted from kohm.
RT = [(-50, 367700), (-40, 204700), (-30, 118500), (-20, 71020),
      (-10, 43670), (0, 27700), (10, 18070), (20, 12110), (25, 10000),
      (30, 8301), (40, 5811), (50, 4147), (60, 3011), (70, 2224),
      (80, 1668), (85, 1451), (90, 1267), (100, 975.3), (110, 759.7),
      (120, 598.1), (125, 533.1)]
V = 3.3
RF = 10000.0
RS = 1000.0
CF = 100e-9
ADC_LEVELS = 4096
ADC_CLK = 84e6 / 6  # Actual .ioc/main.c PCLK2=84 MHz; /6 is a proposal.


def table_temperature(resistance):
    """Log(R) interpolation; reject values outside the published table."""
    if not RT[-1][1] <= resistance <= RT[0][1]:
        return None
    for (ta, ra), (tb, rb) in zip(RT, RT[1:]):
        if rb <= resistance <= ra:
            f = math.log(resistance / ra) / math.log(rb / ra)
            return ta + f * (tb - ta)
    raise ValueError("table interval not found")


rows = []
for temp, resistance in RT:
    q = resistance / (RF + resistance)
    rth = RS + RF * resistance / (RF + resistance)
    beta_temp = 1 / (1 / 298.15 + math.log(resistance / 10000) / 3435) - 273.15
    fixed_error = [table_temperature(resistance / scale)
                   for scale in (0.999, 1.001)]
    rows.append({
        "temperature_C": temp, "ntc_ohm": resistance,
        "node_V": V * q, "ideal_code_coordinate": ADC_LEVELS * q,
        "ntc_power_mW": 1000 * V * V * resistance / (RF + resistance) ** 2,
        "source_ohm_including_series": rth,
        "filter_tau_ms": 1000 * rth * CF,
        "filter_fc_Hz": 1 / (2 * math.pi * rth * CF),
        "beta3435_error_at_table_node_C": beta_temp - temp,
        "fixed_0p1pct_only_max_abs_error_C": max(
            (abs(t - temp) for t in fixed_error if t is not None), default=None),
    })

# Tolerance design envelope: RF +/-0.1%, RS +/-1%; require effective C >=80 nF,
# and <=120 nF including tolerance/temperature/DC bias, not nominal alone.
r_ext_max = RF * 1.001 + RS * 1.01  # Open sensor, more conservative than RT range.
c_min, c_max = 80e-9, 120e-9
r_adc_max, c_adc_max = 6000.0, 7e-12  # DS10693 ADC table.
tau_max = r_ext_max * c_max
summary = {
    "kind": "calculated_design_candidate_NOT_MEASURED",
    "sources": [
        "https://www.semitec-global.com/uploads/2022/01/P9-JT-Thermistor.pdf",
        "https://www.st.com/resource/en/datasheet/stm32f446vc.pdf",
        "https://www.st.com/resource/en/application_note/an2834-how-to-get-the-best-adc-accuracy-in-stm32-microcontrollers-stmicroelectronics.pdf",
    ],
    "adc_clock_candidate_Hz": ADC_CLK,
    "sampling_cycles_candidate": 480,
    "sampling_time_us": 480 / ADC_CLK * 1e6,
    "conversion_time_12bit_us": 492 / ADC_CLK * 1e6,
    "two_temperature_channel_scan_us": 2 * 492 / ADC_CLK * 1e6,
    "source_resistance_upper_ohm": r_ext_max,
    "filter_tau_upper_ms": tau_max * 1000,
    "full_scale_RC_settle_to_half_LSB_ms": tau_max * math.log(8192) * 1000,
    "unbuffered_acquisition_quarter_LSB_us": (
        (r_ext_max + r_adc_max) * c_adc_max * math.log(16384) * 1e6
        + 0.5 / ADC_CLK * 1e6),
    "single_full_scale_charge_share_bound_LSB": ADC_LEVELS * c_adc_max / c_min,
    "ntc_power_max_mW_nominal": 1000 * V * V / (4 * RF),
    "still_air_self_heating_estimate_C": (1000 * V * V / (4 * RF)) / 0.7,
    "two_divider_current_max_mA_at_ntc_short": 2 * V / (RF * 0.999) * 1000,
    "fixed_resistor_max_power_mW_at_ntc_short": V * V / (RF * 0.999) * 1000,
    "beta_error_max_abs_0_to_100_C_at_published_nodes": max(
        abs(r["beta3435_error_at_table_node_C"]) for r in rows
        if 0 <= r["temperature_C"] <= 100),
    "limitations": [
        "No hardware/EMC/protection/thermal validation or motor temperature limit.",
        "Interpolation between manufacturer nodes has no certified error bound.",
        "Acquisition and charge-sharing bounds do not include leakage/ADC total error.",
        "100 Hz per temperature channel, >=20 ms startup settling are design proposals.",
        "Current-channel ADC schedule and RC network are separate pending work.",
    ],
}
(HERE / "calculations.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
with (HERE / "nominal_rt_divider.csv").open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(json.dumps(summary, ensure_ascii=False, indent=2))
