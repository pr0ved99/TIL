"""Nominal arithmetic model for TMR 40-3; no KiCad/ADC/hardware execution."""
from pathlib import Path
import json
import math

FS = 2000
VREF = 3.3
R_FIXED = 10000.0
R_SERIES = 1000.0
C = 100e-9
TABLE = [(0,27700),(10,18070),(20,12110),(25,10000),(30,8301),
         (40,5811),(50,4147),(60,3011),(70,2224),(80,1668),
         (85,1451),(90,1267),(100,975.3)]
R_AT = dict(TABLE)
BAND_C = 0.75  # illustrative |d| <= 1.0 - G_ref(0.25); other errors omitted

def q_of_r(r):
    return r / (R_FIXED + r)

def temperature(q):
    r = R_FIXED*q/(1.0-q)
    for (ta,ra),(tb,rb) in zip(TABLE,TABLE[1:]):
        if rb-1e-8 <= r <= ra+1e-8:
            return ta+(tb-ta)*math.log(r/ra)/math.log(rb/ra)
    raise ValueError(f"Resistance outside table: {r}")

def q_mean(t_out,t_change,old_c,new_c,n):
    """Samples end at t_out, uniformly spaced; exact exponential finite sum."""
    q0=q_of_r(R_AT[old_c])
    q1=q_of_r(R_AT[new_c])
    tau=(R_SERIES+R_FIXED*R_AT[new_c]/(R_FIXED+R_AT[new_c]))*C
    first=t_out-(n-1)/FS
    old_count=min(n,max(0,math.ceil((t_change-first)*FS)))
    post=n-old_count
    if not post:
        return q0
    first_post=first+old_count/FS
    tail=math.exp(-(first_post-t_change)/tau)
    tail *= -math.expm1(-post/(FS*tau)) / -math.expm1(-1/(FS*tau))
    return (old_count*q0+post*q1+(q0-q1)*tail)/n

def direct_q_mean(t_out,t_change,old_c,new_c,n):
    q0=q_of_r(R_AT[old_c]);q1=q_of_r(R_AT[new_c])
    tau=(R_SERIES+R_FIXED*R_AT[new_c]/(R_FIXED+R_AT[new_c]))*C
    values=[]
    for i in range(n):
        t=t_out-(n-1-i)/FS
        values.append(q0 if t<t_change else q1+(q0-q1)*math.exp(-(t-t_change)/tau))
    return math.fsum(values)/n

def gain(f,n):
    if f == 0:
        return 1.0
    g=abs(math.sin(math.pi*n*f/FS)/(n*math.sin(math.pi*f/FS)))
    return 0.0 if g<1e-14 else g

def critical_phase(old_c,new_c,n):
    # First output at 1 s passes for sufficiently early changes. Locate boundary.
    lo,hi=0.0,1.0
    for _ in range(75):
        mid=(lo+hi)/2
        error=abs(temperature(q_mean(1.0,mid,old_c,new_c,n))-new_c)
        if error<=BAND_C:
            lo=mid
        else:
            hi=mid
    return (lo+hi)/2

checks=[]
conditions=[]
for n in (2000,1000):
    directions=[]
    for old_c,new_c in ((25,50),(50,25)):
        phase=critical_phase(old_c,new_c,n)
        sweep=[]
        second_max_error=0.0
        for j in range(10000):
            change=(j+0.5)/10000
            t_out=1.0 if abs(temperature(q_mean(1,change,old_c,new_c,n))-new_c)<=BAND_C else 2.0
            sweep.append(t_out-change)
            second_max_error=max(second_max_error,abs(temperature(q_mean(2,change,old_c,new_c,n))-new_c))
        example={}
        for out in (1.0,2.0,3.0):
            analytic=q_mean(out,0.25025,old_c,new_c,n)
            direct=direct_q_mean(out,0.25025,old_c,new_c,n)
            checks.append(abs(analytic-direct))
            example[str(out)]={"voltage_V":VREF*analytic,"temperature_C":temperature(analytic)}
        directions.append({
            "step_C":[old_c,new_c],
            "external_tau_ms":(R_SERIES+R_FIXED*R_AT[new_c]/(R_FIXED+R_AT[new_c]))*C*1000,
            "first_output_pass_latest_change_s":phase,
            "latency_supremum_s":2.0-phase,
            "margin_to_2s_ms":phase*1000,
            "swept_max_latency_s":max(sweep),
            "phase_sweep_resolution_s":0.0001,
            "second_output_max_error_C":second_max_error,
            "example_step_at_s":0.25025,
            "example_outputs":example})
    conditions.append({
        "N":n,"window_s":n/FS,"output_rate_Hz":1,
        "raw_interval_ms":1000/FS,
        "mean_age_ms":(n-1)/(2*FS)*1000,
        "gain_at_Hz":{str(f):gain(f,n) for f in (0,0.1,0.5,0.9,1.0)},
        "directions":directions})
result={
    "purpose":"40-3 nominal comparison of 1 s / recent 0.5 s averages with 1 Hz output",
    "source":"09_Electrical_Design/23_Temperature_Channel_Verification_Spec_2026-10-27_ko.md sections 3,5,7",
    "assumptions":{
        "fs_Hz":FS,"VEXC_V":VREF,"VREF_V":VREF,"R_fixed_ohm":R_FIXED,
        "R_series_ohm":R_SERIES,"C_F":C,"t_output_s":"integer seconds",
        "model":"instant ideal resistor substitution at t_change; capacitor then settles with final Thevenin R",
        "conversion":"average ideal ADC q -> R -> existing log(R)-linear temperature LUT",
        "band_C":BAND_C,"basis":"1.0 C allowance minus illustrative reference bound 0.25 C; zero other DUT errors",
        "half_second_window":"latest 1000 samples ending each integer second; earlier half second excluded from published mean",
        "omitted":["ADC quantization and errors","VEXC/VREF drift","noise","component tolerance",
                   "trigger/processing/output jitter","switch bounce","NTC thermal lag"],
        "hardware_or_spice_run":False,
        "interpretation":"Model timing only, not hardware PASS or finalized acquisition settings"},
    "conditions":conditions,
    "validation":{"direct_sample_mean_max_abs_error_q":max(checks),
                  "phase_sweep":"10000 phases per direction and window",
                  "boundary":"bisection of first-output acceptance; 2 s result within band throughout sweep"}}
assert max(checks)<1e-12
for condition in conditions:
    for direction in condition["directions"]:
        assert direction["second_output_max_error_C"]<BAND_C
        assert abs(direction["latency_supremum_s"]-direction["swept_max_latency_s"])<0.00011
path=Path(__file__).with_suffix(".json")
path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2))
