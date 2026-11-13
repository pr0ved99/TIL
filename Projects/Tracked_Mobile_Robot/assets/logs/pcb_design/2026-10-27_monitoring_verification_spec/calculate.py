"""Reproduce current/NTC verification planning numbers; NO hardware results.

Run from any directory with Python 3 (stdlib only). Published RT data are read
from the existing source CSV, never by importing its file-writing generator.
"""
import csv
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
RT_SOURCE = PROJECT / 'assets/logs/sensor_design/2026-10-22_ntc_input_design/nominal_rt_divider.csv'
with RT_SOURCE.open(encoding='utf-8', newline='') as f:
    RT = [(float(r['temperature_C']), float(r['ntc_ohm'])) for r in csv.DictReader(f)]
VREF = 3.3
RF = 10000.0
RS = 1000.0
LSB = VREF / 4096


def temperature(r):
    if not RT[-1][1] <= r <= RT[0][1]:
        raise ValueError('Outside published RT table')
    for (ta, ra), (tb, rb) in zip(RT, RT[1:]):
        if rb <= r <= ra:
            return ta + (tb-ta)*math.log(r/ra)/math.log(rb/ra)
    raise AssertionError('Unreachable')


def resistance(t):
    for (ta, ra), (tb, rb) in zip(RT, RT[1:]):
        if ta <= t <= tb:
            return ra*math.exp((t-ta)/(tb-ta)*math.log(rb/ra))
    raise ValueError('Outside published RT table')


def temp_from_q(q, rf=RF):
    if not 0 < q < 1:
        raise ValueError('Invalid divider ratio')
    return temperature(rf*q/(1-q))


def classify(error, guard, tolerance):
    """Bound-based guard, not a coverage-factor/statistical uncertainty claim."""
    if guard < 0 or tolerance <= 0:
        raise ValueError('Invalid bound')
    if abs(error)+guard <= tolerance:
        return 'PASS'
    if abs(error)-guard > tolerance:
        return 'FAIL'
    return 'INCONCLUSIVE'


def write_csv(name, rows):
    with (HERE/name).open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


current = []
for amps in [-30, -10, -7.5, -5, -2, -1, 0, 1, 2, 5, 7.5, 10, 30]:
    voltage = 1.65 + .044*amps
    current.append(dict(nominal_equivalent_A=amps, target_V=round(voltage, 6),
        role='calibration' if amps in [-10, 10] else 'validation' if abs(amps)<10 else 'range_only',
        tolerance_input_mV=4.4 if abs(amps)<=10 else '',
        maximum_comparison_guard_mV=1.1 if abs(amps)<=10 else '',
        status='NOT_RUN'))

ntc = []
for t,r in RT:
    if not 0 <= t <= 100:
        continue
    q = r/(RF+r)
    rth = RS+RF*r/(RF+r)
    def max_dt(qs):
        return max(abs(temp_from_q(x)-t) for x in qs)
    ntc.append(dict(target_C=t, nominal_ohm=r, ratio=q, voltage_V=VREF*q,
        ideal_code=4096*q, source_ohm=rth,
        ref_resistor_0p1pct_max_C=max(abs(temperature(r*s)-t) for s in [.999,1.001]),
        fixed_resistor_1pct_max_C=max(abs(temperature(r/s)-t) for s in [.99,1.01]),
        leakage_1uA_max_C=max_dt([q-rth*1e-6/VREF,q+rth*1e-6/VREF]),
        adc_4LSB_screen_max_C=max_dt([q-4/4096,q+4/4096]),
        excitation_ratio_0p1pct_max_C=max_dt([q*.999,q*1.001]),
        ntc_power_mW=1000*VREF**2*r/(RF+r)**2,
        beta3435_minus_table_C=1/(1/298.15+math.log(r/10000)/3435)-273.15-t,
        status='NOT_RUN'))

dc_meter = []
for amps in [0, .25, .5, 1, 1.5, 1.8, 3, 5, 7.5, 10]:
    resolution = .001 if amps <= 1.8 else .01
    digits = 8 if resolution == .001 else 3
    spec = .02*amps+digits*resolution
    dc_meter.append(dict(reference_A=amps, range_A=2 if resolution==.001 else 20,
        meter_spec_bound_A=spec,
        target_at_equal_DUT_reading_A=max(.2,.05*amps),
        remaining_discrepancy_before_setup_bound_A=max(.2,.05*amps)-spec,
        note='steady DC; specification bound only; NOT calibration uncertainty'))

summary = {
    'kind':'DESIGN_AND_TEST_BASELINE_v0.1_NOT_MEASURED',
    'date':'2026-10-27',
    'rt_source_sha256':hashlib.sha256(RT_SOURCE.read_bytes()).hexdigest(),
    'current_input_tolerance_mV':4.4,
    'current_input_equivalent_A':4.4/44,
    'current_sensor_reserve_A':.2-4.4/44,
    'comparison_guard_input_max_mV':1.1,
    'current_12k_1uA_mV':12.0,
    'current_12k_1uA_A':.012/.044,
    'current_12k_10Mohm_probe_drop_at_1p65V_mV':1000*1.65*12000/(1e7+12000),
    'adc_LSB_mV':LSB*1000,
    'adc_4LSB_screen_mV':4*LSB*1000,
    'ut210e_1p65V_bound_mV':1000*(.007*1.65+.003),
    'ut210e_2p09V_20V_range_bound_mV':1000*(.007*2.09+.03),
    'temp_reference_resistor_0p1pct_max_C':max(x['ref_resistor_0p1pct_max_C'] for x in ntc),
    'temp_fixed_1pct_max_C':max(x['fixed_resistor_1pct_max_C'] for x in ntc),
    'temp_leakage_1uA_max_C':max(x['leakage_1uA_max_C'] for x in ntc),
    'temp_adc_4LSB_screen_max_C':max(x['adc_4LSB_screen_max_C'] for x in ntc),
    'temp_g_0p1pct_max_C':max(x['excitation_ratio_0p1pct_max_C'] for x in ntc),
    'temp_beta_model_max_node_error_C':max(abs(x['beta3435_minus_table_C']) for x in ntc),
    'temp_still_air_self_heating_max_C':(1000*VREF**2/(4*RF))/.7,
    'temperature_guard_max_C':.25,
    'temperature_tolerance_C':1.0,
    'temperature_budget_C':{'divider_and_drift':.25,'adc_leakage_and_noise':.55,
                            'excitation_reference_ratio':.15,'numerical_conversion':.05},
    'hardware_test_status':'NOT_RUN',
    'limitations':[
        '4.4 mV is an engineering allocation, not a manufacturer guarantee.',
        '18 MHz ADC 4 LSB table is a screening comparison, not a 14 MHz guarantee.',
        'Do not sum ADC TUE, INL and quantization as independent worst cases.',
        'RT interpolation models the published nominal curve; no between-node physical accuracy claim.',
        'Meter bounds are not calibrated expanded uncertainties.',
        'Specified test voltages do not authorize motor current or physical connection.'
    ]
}

# Useful independent invariants: interpolation nodes/inversion and decision edges.
for t,r in RT:
    assert abs(temperature(r)-t)<1e-10
for t in [0,15,25,45,75,95,100]:
    assert abs(temperature(resistance(t))-t)<1e-10
assert abs(temp_from_q(.5)-25)<1e-10
assert temperature(11000)<25<temperature(9000)
assert classify(3,1,4)=='PASS'
assert classify(5,1,4)=='INCONCLUSIVE'
assert classify(5.01,1,4)=='FAIL'
assert classify(-5.01,1,4)=='FAIL'
assert abs(sum(summary['temperature_budget_C'].values())-1)<1e-12
assert [r['nominal_equivalent_A'] for r in current if r['role']=='calibration']==[-10,10]
assert all(r['nominal_equivalent_A'] not in [-10,10] for r in current if r['role']=='validation')

write_csv('current_voltage_points.csv',current)
write_csv('temperature_resistance_points.csv',ntc)
write_csv('ut210e_dc_feasibility.csv',dc_meter)
(HERE/'calculations.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
