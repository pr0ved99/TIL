"""Analytic boxcar response and synthetic alias examples; no hardware/ADC run."""
import cmath
import json
import math
from pathlib import Path

def fold_hz(frequency, sample_rate):
    return abs((frequency + sample_rate / 2) % sample_rate - sample_rate / 2)

def gain(frequency, sample_rate, count):
    folded = fold_hz(frequency, sample_rate)
    if folded == 0:
        return 1.0
    value = abs(math.sin(math.pi * count * folded / sample_rate)
                / (count * math.sin(math.pi * folded / sample_rate)))
    return 0.0 if value < 1e-14 else value

def direct_gain(frequency, sample_rate, count):
    return abs(sum(cmath.exp(2j * math.pi * frequency * n / sample_rate)
                   for n in range(count)) / count)

def row(frequency, sample_rate, count):
    g = gain(frequency, sample_rate, count)
    return {
        "input_Hz": frequency, "sample_rate_Hz": sample_rate, "N": count,
        "raw_alias_Hz": fold_hz(frequency, sample_rate),
        "boxcar_gain": g, "boxcar_dB": None if g == 0 else 20 * math.log10(g),
        "output_rate_Hz": sample_rate / count,
        "output_alias_Hz": fold_hz(frequency, sample_rate / count),
    }

def calculate():
    low = [row(f, 2000, 200) for f in [0, 1, 2, 3, 5, 9, 10, 15, 20, 25]]
    compare = [row(f, fs, n) for f in [1, 5, 9, 19000, 19001, 38001]
               for fs, n in [(100, 10), (1000, 100), (2000, 200)]]
    deviations = [abs(r["boxcar_gain"] - direct_gain(r["input_Hz"],
                  r["sample_rate_Hz"], r["N"])) for r in low + compare]
    assert max(deviations) < 1e-10
    # 9 Hz, 100 mV peak at the input to digital processing.
    # Twenty fixed nonoverlapping blocks give two seconds at 10 Hz output.
    outputs = [sum(.100 * math.cos(2 * math.pi * 9 * n / 2000)
                   for n in range(m * 200, (m + 1) * 200)) / 200 for m in range(20)]
    output_1hz_peak = abs(2 / 20 * sum(y * cmath.exp(-2j * math.pi * 1 * m / 10)
                                     for m, y in enumerate(outputs)))
    expected = .100 * gain(9, 2000, 200)
    assert abs(output_1hz_peak - expected) < 1e-12
    lo, hi = 0.0, 10.0
    for _ in range(70):
        mid = (lo + hi) / 2
        if gain(mid, 2000, 200) > 1 / math.sqrt(2):
            lo = mid
        else:
            hi = mid
    return {
        "date": "2026-11-08",
        "evidence": "analytic frequency response and synthetic sequence arithmetic",
        "assumptions": [
            "Equally spaced valid samples, fixed linear conversion, equal weights",
            "N-point averaging followed by retaining every Nth result (fixed block phase)",
            "Steady-state tones; no startup or block-reset transient",
            "All listed amplitudes are relative to input of digital processing",
            "Analog RC attenuation, ADC acquisition, clock jitter, tolerances and real noise excluded",
            "19000/19001/38001 Hz are illustrative residual tones, not observed PWM spectra",
            "Exact zeros require exact tone/rate relation; dB null means ideal zero",
            "At aliases 0 or output Nyquist, observed real-sinusoid amplitude depends on phase",
        ],
        "low_frequency_2k_200": low,
        "candidate_comparison": compare,
        "minus_3dB_frequency_Hz": (lo + hi) / 2,
        "synthetic_9Hz_100mV_peak": {
            "output_1Hz_peak_V": output_1hz_peak, "expected_peak_V": expected,
            "output_samples_V": outputs,
        },
        "checks": {
            "max_complex_sum_gain_difference": max(deviations),
            "synthetic_block_mean_1Hz_component_matches_gain": True,
            "hardware_or_spice_run": False,
        },
    }

if __name__ == "__main__":
    result = calculate()
    Path(__file__).with_suffix(".json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "low_frequency": result["low_frequency_2k_200"],
        "19001Hz": [r for r in result["candidate_comparison"] if r["input_Hz"] == 19001],
        "38001Hz_2k": [r for r in result["candidate_comparison"] if r["input_Hz"] == 38001 and r["sample_rate_Hz"] == 2000],
        "minus_3dB_Hz": result["minus_3dB_frequency_Hz"],
        "checks": result["checks"],
    }, indent=2))
