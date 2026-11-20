"""Arithmetic and saved-file inspection only; never runs SPICE or firmware."""
from pathlib import Path
import hashlib
import itertools
import json
import math
import re

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
SIM = PROJECT / '09_Electrical_Design/KiCAD/Simulation/03_Voltage_Divider'


def ratio(r1=12000, r2=12000, r3=4700, r4=1000, r5=47000, ron=2):
    ra = r1 + r2
    return r3 * r5 / (ra * r3 + (ra + r3) * (r4 + ron + r5))


def write_json(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    gain = ratio()
    k = 1 / gain
    vadc = 16 * gain
    req = 1 / (1 / 47000 + 1 / (1000 + 2 + 24000 * 4700 / 28700))
    corners = []
    for name, resistors, reported in [
        ('max_0p1pct', [11988, 11988, 4704.7, 999, 47047], 2.37547),
        ('min_0p1pct', [12012, 12012, 4695.3, 1001, 46953], 2.36724),
    ]:
        actual = 16 * ratio(*resistors)
        corners.append(dict(condition=name, R_ohm=resistors, calculated_vadc_V=actual,
                            user_reported_vadc_V=reported,
                            reported_minus_calculated_V=reported-actual,
                            rail_error_full_precision_V=actual*k-16,
                            rail_error_from_rounded_user_V=reported*k-16))
        assert abs(actual-reported) <= 0.000005, 'OP mismatch beyond 5-decimal display rounding'
    tcr = []
    for ppm in (25, 50, 100):
        errors = []
        for signs in itertools.product((-1, 1), repeat=5):
            rs = [r*(1+s*ppm*1e-6*5) for r, s in zip((12000,12000,4700,1000,47000), signs)]
            errors.append(16*ratio(*rs)*k-16)
        tcr.append(dict(assumed_abs_TCR_ppm_per_C=ppm, delta_T_C=5,
                        min_rail_error_V=min(errors), max_rail_error_V=max(errors)))
    data = {
        'scope': 'Algebraic comparisons; no SPICE rerun, no hardware, no final safety/accuracy PASS',
        'nominal': {'A': gain, 'K': k, 'vadc_at_16V': vadc, 'vadc_at_12p6V':12.6*gain, 'req_adc_ohm': req},
        'corners': corners,
        'ron_2_to_4p5_only': {'vadc_V':16*ratio(ron=4.5),'rail_delta_V':16*ratio(ron=4.5)*k-16,
                            'limit':'2 ohm is typical, not minimum; not a full bound'},
        'on_leakage_single_50nA': {'adc_abs_delta_V':50e-9*req, 'rail_abs_delta_V':50e-9*req*k},
        'off_current_times_R5': {'10nA_V':10e-9*47000,'2uA_V':2e-6*47000,
                                'limit':'VD=0 vendor test; floating output/MCU off IV not modeled'},
        'fast_fall_assumption': {'slope_V_per_ms':25,'trip_ms':10+(3.3-3)/25,'off_ms':10+(3.3-3)/25+.030,
                                 'cross_ms':10+(3.3-vadc)/25,'sample_ms':10.04,'vdda_V':2.3,
                                 'vdda_minus_vadc_V':2.3-vadc,'user_reported_delta_V':-.0713526,
                                 'limit':'Chosen PWL, not measured Nucleo power fall'},
        'discharge_assumption': {'R5_ohm':47000,'C2_F':100e-12,'tau_s':47000*100e-12,
                                '99pct_s':math.log(100)*47000*100e-12},
        'adc_scale_3p3V_12bit': {'adc_lsb_V':3.3/4096,'rail_lsb_V':3.3/4096*k,
                                'rail_4LSB_V':4*3.3/4096*k,'rail_3LSB_V':3*3.3/4096*k},
        'vrefint_hypothetical_Ncal1500': [dict(Nref=n,estimated_vdda_V=3.3*1500/n,
                                               rail_error_at16V=16*1500/n-16) for n in (1496,1499,1501,1504)],
        'resistor_TCR_assumptions_not_kit_specs': tcr,
        'UT210E_DC20V_spec_bound': [dict(reading_V=v,resolution_V=.01,bound_V=.007*v+3*.01) for v in (12.6,16)],
    }
    write_json('calculations.json', data)
    files = sorted(SIM.glob('03_1[0-3]*.kicad_sch')) + sorted(SIM.glob('03_1[0-3]*.kicad_pro'))
    files += [SIM/'detector_delay_30us.cir', SIM/'03_Voltage_Divider.wbk']
    manifest=[]
    for f in files:
        entry={'path':f.relative_to(PROJECT).as_posix(),'bytes':f.stat().st_size,
               'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
        if f.suffix=='.kicad_sch':
            placed=[]
            for symbol in f.read_text(encoding='utf-8-sig').split('\n\t(symbol\n')[1:]:
                pairs=re.findall(r'\(property "([^"]+)" "((?:[^"\\]|\\.)*)"',symbol)
                props={key:json.loads('"'+val+'"') for key,val in pairs}
                if not props.get('Reference','').startswith('#'):
                    placed.append({key:props[key] for key in ('Reference','Value','Sim.Params') if key in props})
            entry['saved_placed_properties']=placed
            entry['delay_include_present']='detector_delay_30us.cir' in f.read_text(encoding='utf-8-sig')
        manifest.append(entry)
    workbook=json.loads((SIM/'03_Voltage_Divider.wbk').read_text(encoding='utf-8-sig'))
    write_json('source_manifest.json', {'scope':'Read saved component properties, include, workbook and SHA256; no netlist/ERC/SPICE execution',
                                       'files':manifest,'workbook_tabs':workbook['tabs']})
    print(json.dumps({'saved_files':len(files),'OP_rounding_comparisons':'PASS',
                      'K':k,'corners_rail_mV':[x['rail_error_full_precision_V']*1000 for x in corners],
                      'simulation_run':False},ensure_ascii=False))


if __name__ == '__main__':
    main()
