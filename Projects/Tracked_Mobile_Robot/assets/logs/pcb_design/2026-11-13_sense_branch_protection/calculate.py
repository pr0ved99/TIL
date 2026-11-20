"""Nominal DC design comparison; no SPICE, hardware, or selected-part rating."""
from pathlib import Path
import hashlib
import json
from math import isclose

def parallel(*rs):
    return 1 / sum(1 / r for r in rs)

VIN = 16.0
RTOP = 24000.0
RBOT = 4700.0
RSW = 1000.0 + 2.0  # RON is an explanatory assumption, not worst-case.
RLOAD = 47000.0
C1 = 100e-9
LOWER = parallel(RBOT, RSW + RLOAD)
K0 = (RTOP + LOWER) / LOWER * (RSW + RLOAD) / RLOAD

def normal(rp):
    top = RTOP + rp
    i = VIN / (top + LOWER)
    vdiv = i * LOWER
    vadc = vdiv * RLOAD / (RSW + RLOAD)
    # Independent DC KCL solve at VDIV and VADC.
    g11 = 1/top + 1/RBOT + 1/RSW
    g22 = 1/RSW + 1/RLOAD
    det = g11*g22 - (1/RSW)**2
    adc_kcl = (VIN/top) / RSW / det
    div_kcl = (VIN/top) * g22 / det
    assert isclose(vadc, adc_kcl, rel_tol=1e-12)
    assert isclose(vdiv, div_kcl, rel_tol=1e-12)
    return dict(source_resistance_ohm=rp, input_current_A=i,
        source_drop_V=i*rp, source_power_W=i*i*rp,
        vdiv_V=vdiv, vadc_V=vadc, rail_conversion_K=VIN/vadc,
        estimate_using_old_K_V=K0*vadc,
        c1_dominant_tau_s=parallel(top, RBOT, RSW+RLOAD)*C1,
        input_referred_ideal_12bit_lsb_V=3.3/4096*(VIN/vadc))

rows=[]
for rp in (0.0,100.0,1000.0,2200.0):
    row=normal(rp)
    row.update(fault_current_A=VIN/rp if rp else None,
               fault_resistor_power_W=VIN*VIN/rp if rp else None)
    rows.append(row)
candidate=2200.0
knom=normal(candidate)['rail_conversion_K']
tolerance=[]
for delta in (-0.01,0.01):
    actual=candidate*(1+delta)
    v=normal(actual)['vadc_V']
    tolerance.append(dict(resistance_ohm=actual,
        old_nominal_new_K_error_V=knom*v-VIN,
        fault_current_A=VIN/actual, fault_power_W=VIN*VIN/actual))
root=Path(__file__).resolve().parents[4]
cad=root/'09_Electrical_Design/KiCAD'
source_paths=[
    cad/'TMR_Monitor_Shield_RevA/TMR_Monitor_Shield_RevA.kicad_sch',
    cad/'TMR_Monitor_Shield_RevA/reports/netlist.xml',
    cad/'Tracked_Mobile_Robot_Wiring_RevB/Tracked_Mobile_Robot_Wiring_RevB.kicad_sch',
]
result=dict(status='CALCULATED_DESIGN_COMPARISON_NOT_IMPLEMENTED',
    assumptions=dict(input_V=VIN, source_and_wire_impedance_ohm=0,
        mode='DC steady state; TMUX ON; common GND; nominal resistors; RON=2ohm',
        fault='short to GND AFTER Rp and BEFORE PCB 24k; intact Rp',
        exclusions=['transients/stored energy','component failure','external overvoltage/reverse polarity',
                    'temperature/tolerance except isolated Rp +/-1% case','measured protection performance'],
        c1_tau='C1-dominant approximation, not exact two-pole or whole-system response',
        resistance_range_is_not_part_selection=True),
    lower_equivalent_ohm=LOWER,baseline_conversion_K=K0,rows=rows,
    isolated_2k2_tolerance=tolerance,
    source_sha256={str(p.relative_to(root)).replace(chr(92),'/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths})
dest=Path(__file__).with_name('comparison.json')
dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(output=str(dest),rows=len(rows),independent_KCL_checks=8,
    candidate_K=knom,candidate_vadc_V=normal(candidate)['vadc_V'],
    isolated_max_abs_tolerance_error_V=max(abs(r['old_nominal_new_K_error_V']) for r in tolerance)),ensure_ascii=False))
