"""Run exported RC circuits with KiCad's ngspice DLL; save numerical evidence.

No MCU operations. The model excludes sensor errors and ADC acquisition/leakage.
Shared-library API: https://ngspice.sourceforge.io/docs/ngspice-manual.pdf
"""
import csv
import ctypes as ct
import hashlib
import json
import math
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPORTS = HERE / 'reports'
BIN = Path(os.environ['LOCALAPPDATA']) / 'Programs/KiCad/10.0/bin'


class Complex(ct.Structure):
    _fields_ = [('real', ct.c_double), ('imag', ct.c_double)]


class Vector(ct.Structure):
    _fields_ = [('name', ct.c_char_p), ('type', ct.c_int), ('flags', ct.c_short),
                ('real', ct.POINTER(ct.c_double)), ('complex', ct.POINTER(Complex)),
                ('length', ct.c_int)]


def save_json(name, obj):
    (REPORTS / name).write_bytes((json.dumps(obj, indent=2, ensure_ascii=False) + '\n').encode())


def save_csv(name, headers, rows):
    with (REPORTS / name).open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def main():
    logs, exits = [], []
    @ct.CFUNCTYPE(ct.c_int, ct.c_char_p, ct.c_int, ct.c_void_p)
    def output(message, ident, user):
        logs.append(message.decode('utf-8', errors='replace'))
        return 0

    @ct.CFUNCTYPE(ct.c_int, ct.c_int, ct.c_bool, ct.c_bool, ct.c_int, ct.c_void_p)
    def controlled_exit(status, immediate, quit_requested, ident, user):
        exits.append({'status': status, 'quit_requested': quit_requested})
        return 0

    # Keep directory handle and callbacks alive for the whole DLL lifetime.
    directory = os.add_dll_directory(str(BIN))
    dll = ct.CDLL(str(BIN / 'ngspice.dll'))
    dll.ngSpice_Init.argtypes = [ct.c_void_p] * 7
    dll.ngSpice_Init.restype = ct.c_int
    dll.ngSpice_Command.argtypes = [ct.c_char_p]
    dll.ngSpice_Command.restype = ct.c_int
    dll.ngSpice_Circ.argtypes = [ct.POINTER(ct.c_char_p)]
    dll.ngSpice_Circ.restype = ct.c_int
    dll.ngGet_Vec_Info.argtypes = [ct.c_char_p]
    dll.ngGet_Vec_Info.restype = ct.POINTER(Vector)
    assert dll.ngSpice_Init(output, None, controlled_exit, None, None, None, None) == 0

    def command(s):
        status = dll.ngSpice_Command(s.encode())
        if status or exits:
            raise RuntimeError((s, status, exits, logs[-12:]))

    def vector(name):
        p = dll.ngGet_Vec_Info(name.encode())
        if not p:
            raise RuntimeError(('missing vector', name, logs[-12:]))
        v = p.contents
        assert v.length > 0
        # Copy into Python before ngspice replaces/destroys a plot.
        if v.complex:
            return [complex(v.complex[i].real, v.complex[i].imag) for i in range(v.length)]
        return [v.real[i] for i in range(v.length)]

    command('version')
    models = {}
    try:
        for name, scale in [('Current_RC_AC', 'frequency'), ('Current_RC_Step', 'time')]:
            path = REPORTS / (name + '.cir')
            raw = path.read_bytes()
            lines = [line.encode() for line in raw.decode().splitlines()]
            circuit = (ct.c_char_p * (len(lines) + 1))(*lines, None)
            assert dll.ngSpice_Circ(circuit) == 0, logs[-12:]
            command('run')
            models[name] = {'sha256': hashlib.sha256(raw).hexdigest(),
                            'x': vector(scale), 'vin': vector('v(/vin)'),
                            'vadc': vector('v(/vadc)')}

        tau = 12_000 * 100e-9
        ac = models['Current_RC_AC']
        frequencies = [x.real if isinstance(x, complex) else x for x in ac['x']]
        ratios = [b / a for a, b in zip(ac['vin'], ac['vadc'])]
        calculated = [1 / complex(1, 2 * math.pi * f * tau) for f in frequencies]
        max_ac_error = max(abs(s - t) for s, t in zip(ratios, calculated))
        save_csv('ac.csv', ['frequency_hz', 'vin_real_v', 'vin_imag_v', 'vadc_real_v',
                           'vadc_imag_v', 'magnitude_ratio', 'gain_db', 'phase_deg'],
                 ([f, a.real, a.imag, b.real, b.imag, abs(h), 20*math.log10(abs(h)),
                   math.degrees(math.atan2(h.imag, h.real))]
                  for f, a, b, h in zip(frequencies, ac['vin'], ac['vadc'], ratios)))
        # Interpolate crossing in log-frequency for -3.0103 dB point.
        db = [20 * math.log10(abs(h)) for h in ratios]
        target_db = 20 * math.log10(1 / math.sqrt(2))
        i = next(i for i in range(1, len(db)) if db[i] <= target_db)
        frac = (target_db - db[i-1]) / (db[i] - db[i-1])
        fc_sim = math.exp(math.log(frequencies[i-1]) + frac*math.log(frequencies[i]/frequencies[i-1]))
        j = min(range(len(frequencies)), key=lambda k: abs(frequencies[k] - 19000))

        step = models['Current_RC_Step']
        t, vin, vadc = step['x'], step['vin'], step['vadc']
        save_csv('step.csv', ['time_s', 'vin_v', 'vadc_v'], zip(t, vin, vadc))
        # Compare the rising segment against a finite 1us linear ramp, not an ideal step.
        td, tr, low, delta = .001, .000001, 1.43, .44
        def theory(now):
            u = now - td
            if u <= 0:
                return low
            if u < tr:
                return low + delta/tr*(u + tau*math.expm1(-u/tau))
            return low + delta*(1 - tau/tr*(-math.expm1(-tr/tau))*math.exp(-(u-tr)/tau))
        max_step_error = max(abs(v-theory(now)) for now, v in zip(t, vadc) if now < .02)
        threshold = low + .99 * delta
        k = next(k for k in range(1, len(t)) if t[k] >= td and vadc[k] >= threshold)
        t_cross = t[k-1] + (threshold-vadc[k-1])/(vadc[k]-vadc[k-1])*(t[k]-t[k-1])
        expected_t_cross = td + tr + tau*math.log((tau/tr*(-math.expm1(-tr/tau)))/.01)
        checks = {
            'ac_complex_gain_max_absolute_error_below_1e-10': max_ac_error < 1e-10,
            'step_rising_max_absolute_error_below_10uV': max_step_error < 10e-6,
            'step_99pct_crossing_error_below_2us': abs(t_cross-expected_t_cross) < 2e-6,
            'no_controlled_exit': not exits,
        }
        result = {
            'status': 'PASS_IDEAL_RC_MODEL' if all(checks.values()) else 'FAIL',
            'run_method': 'KiCad-exported SPICE netlists executed directly with bundled ngspice.dll',
            'gui_run': 'NOT_RUN', 'hardware_test': 'NOT_RUN',
            'dll_sha256': hashlib.sha256((BIN/'ngspice.dll').read_bytes()).hexdigest(),
            'model_netlist_sha256': {name: m['sha256'] for name, m in models.items()},
            'checks': checks, 'tau_s': tau,
            'ac': {'points': len(frequencies), 'fc_theory_hz': 1/(2*math.pi*tau),
                   'fc_sim_log_interpolation_hz': fc_sim,
                   'max_complex_gain_absolute_error': max_ac_error,
                   'nearest_19khz_sample': {'frequency_hz': frequencies[j],
                       'magnitude_ratio': abs(ratios[j]), 'gain_db': db[j]},
                   'exact_19khz_theory_ratio': abs(1/complex(1, 2*math.pi*19000*tau))},
            'step': {'points': len(t), 'max_rising_error_vs_finite_ramp_v': max_step_error,
                     'rise_start_s': td, 'rise_duration_s': tr,
                     '99pct_from_rise_start_sim_s': t_cross-td,
                     '99pct_from_rise_start_finite_ramp_theory_s': expected_t_cross-td},
            'limits': 'Ideal R/C and ideal source only; excludes sensor/ADC/leakage/protection/tolerances/EMI',
        }
        save_json('simulation.json', result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        assert all(checks.values()), checks
    finally:
        (REPORTS/'ngspice.log').write_bytes(('\n'.join(logs)+'\n').encode())


if __name__ == '__main__':
    main()
