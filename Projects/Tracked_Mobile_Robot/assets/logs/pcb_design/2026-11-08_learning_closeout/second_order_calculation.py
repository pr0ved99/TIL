"""Reproduce the educational two-node RC calculation; never runs KiCad/hardware."""
from fractions import Fraction as F
from math import exp, expm1, sqrt, log
from pathlib import Path
import json


def parallel(*values):
    return 1 / sum(1 / x for x in values)


def calculate():
    r12, r3, rs, rl = map(F, (24000, 4700, 1002, 47000))
    c1, c2 = F("100e-9"), F("100e-12")
    rt = parallel(r12, r3)
    total = rt + rs + rl
    a = (rt * (rs + rl) * c1 + rl * (rt + rs) * c2) / total
    b = rt * rs * rl * c1 * c2 / total

    # Independent determinant form of the two nodal admittance equations.
    gt, gs, gl = 1 / rt, 1 / rs, 1 / rl
    d0 = gt * gs + gt * gl + gs * gl
    assert a == (c1 * (gs + gl) + c2 * (gt + gs)) / d0
    assert b == c1 * c2 / d0
    tau_c1 = parallel(rt, rs + rl) * c1
    assert rt * (rs + rl) * c1 / total == tau_c1  # C2 -> 0

    af, bf = float(a), float(b)
    slow = (af + sqrt(af * af - 4 * bf)) / 2
    fast = 2 * bf / (af + sqrt(af * af - 4 * bf))
    vthev = F(16) * r3 / (r12 + r3)
    vfinal = vthev * rl / total
    k = F(16) / vfinal
    rise = 1e-6

    def residual_step(t):
        return (slow * exp(-t / slow) - fast * exp(-t / fast)) / (slow - fast)

    def residual_ramp(t):
        # Average the ideal-step residual over the 1 us rise, for t >= rise.
        def avg(tau):
            return exp(-(t - rise) / tau) * tau / rise * (-expm1(-rise / tau))
        return (slow * avg(slow) - fast * avg(fast)) / (slow - fast)

    def crossing(fn):
        lo, hi = rise, 0.006
        for _ in range(90):
            mid = (lo + hi) / 2
            if 16 * fn(mid) > 0.010:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    vf, kf = float(vfinal), float(k)
    cursor1, cursor2_rounded = 2.36985654, 2.36990
    t_ramp = crossing(residual_ramp)
    return {
        "source": "03_14 saved nominal model; manual KCL and analytic step/ramp response",
        "verification": {
            "nodal_determinant_coefficients_exactly_equal": True,
            "C2_zero_limit_equals_C1_approximation": True,
            "ramp_crossing_within_user_bracket": 0.002680 < t_ramp < 0.002690,
            "new_simulator_or_hardware_execution": False,
        },
        "R_T_ohm": float(rt), "R_S_ohm": float(rs), "R_L_ohm": float(rl),
        "R_eq_C1_ohm": float(tau_c1 / c1),
        "V_thevenin_V": float(vthev), "VADC_final_V": vf,
        "VDIV_final_V": vf * float((rs + rl) / rl), "K": kf,
        "a_s": af, "b_s2": bf,
        "tau_C1_s": float(tau_c1), "tau_slow_s": slow, "tau_fast_s": fast,
        "slow_difference_percent": (slow / float(tau_c1) - 1) * 100,
        "one_tau_VADC_approx_V": vf * (1 - exp(-1)),
        "one_tau_user_cursor_observed": False,
        "input_settling_budget_V": 0.010,
        "ADC_settling_budget_V": 0.010 / kf,
        "ADC_rising_threshold_V": vf - 0.010 / kf,
        "settling_C1_ideal_step_s": float(tau_c1) * log(1600),
        "settling_two_cap_ideal_step_s": crossing(residual_step),
        "settling_two_cap_1us_ramp_from_start_s": t_ramp,
        "graph_time_ramp_crossing_s": 0.001 + t_ramp,
        "user_cursor1_residual_input_V": (vf - cursor1) * kf,
        "user_cursor2_residual_input_approx_V": (vf - cursor2_rounded) * kf,
        "ADC_3V3_range_usage_percent": vf / 3.3 * 100,
        "nominal_12bit_3V3_input_LSB_V": 3.3 / 4096 * kf,
        "assumptions": [
            "R1+R2=24k, R3=4.7k, R4+Ron=1002, R5=47k",
            "C1=100nF, C2=100pF learning assumption; switch stays ON",
            "Zero initial voltages; input 0->16V from 1.000 to 1.001ms",
            "No component tolerance, actual ADC sampling/noise/protection model",
            "Cursor2 is rounded; no fabricated additional measured precision",
        ],
    }


if __name__ == "__main__":
    result = calculate()
    assert result["verification"]["ramp_crossing_within_user_bracket"]
    target = Path(__file__).with_suffix(".json")
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("verification", "tau_slow_s", "tau_fast_s",
          "settling_two_cap_1us_ramp_from_start_s")}, ensure_ascii=False, indent=2))
