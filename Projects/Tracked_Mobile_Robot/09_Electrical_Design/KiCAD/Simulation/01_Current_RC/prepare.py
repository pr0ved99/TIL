"""Prepare isolated KiCad RC models and validate exported connectivity.

This prepares simulations; it does not run ngspice or operate hardware.
Embedded symbols come from the locally installed KiCad symbol library.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import uuid

HERE = Path(__file__).resolve().parent
KICAD = Path(os.environ['LOCALAPPDATA']) / 'Programs/KiCad/10.0'
CLI = KICAD / 'bin/kicad-cli.exe'
LIBS = KICAD / 'share/kicad/symbols'

def uid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'tmr/current-rc/' + name))

def quote(s):
    return json.dumps(s, ensure_ascii=False)

def lib_symbol(lib, name):
    s = (LIBS / (lib + '.kicad_sym')).read_text(encoding='utf-8')
    start = s.index('(symbol "' + name + '"')
    depth, quoted, escaped = 0, False, False
    for end in range(start, len(s)):
        c = s[end]
        if quoted:
            if escaped:
                escaped = False
            elif c == '\\':
                escaped = True
            elif c == '"':
                quoted = False
        elif c == '"':
            quoted = True
        elif c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return s[start:end+1].replace('(symbol "'+name+'"', '(symbol "'+lib+':'+name+'"', 1)
    raise ValueError(name)

def build(name, source, params, directive):
    root_id = uid(name)
    out = [f'(kicad_sch (version 20250114) (generator "tmr_sim_prepare") (uuid "{root_id}") (paper "A4")',
           '(title_block (title "TMR current RC - ideal model") (date "2026-10-28") (rev "SIM-01") (comment 1 "SIMULATION ONLY - NOT A HARDWARE VALIDATION"))',
           '(lib_symbols', lib_symbol('Device', 'R'), lib_symbol('Device', 'C'),
           lib_symbol('Simulation_SPICE', source), lib_symbol('Simulation_SPICE', '0'), ')']
    def prop(k, v, x, y, hide=False, angle=0):
        return f'(property {quote(k)} {quote(v)} (at {x} {y} {angle}) '+ ('(hide yes) ' if hide else '') + '(effects (font (size 1.27 1.27)) (justify left)))'
    def symbol(lib, ref, val, x, y, angle=0, extra=None, pins=('1','2')):
        out.append(f'(symbol (lib_id "{lib}") (at {x} {y} {angle}) (unit 1) (in_bom no) (on_board no) (dnp no) (uuid "{uid(name+ref)}")')
        if angle == 90:
            out.extend([prop('Reference',ref,x-2.54,y-7.62,angle=90), prop('Value',val,x-2.54,y-5.08,angle=90)])
        elif ref.startswith('#'):
            out.extend([prop('Reference',ref,x,y,True), prop('Value',val,x,y+5.08)])
        else:
            out.extend([prop('Reference',ref,x+5.08,y-2.54,ref.startswith('#')), prop('Value',val,x+5.08,y)])
        for k,v in (extra or {}).items():
            out.append(prop(k,v,x,y,True))
        for pin in pins:
            out.append(f'(pin "{pin}" (uuid "{uid(name+ref+pin)}"))')
        out.append(f'(instances (project "{name}" (path "/{root_id}" (reference "{ref}") (unit 1)))))')
    symbol('Simulation_SPICE:'+source,'V1',source,60.96,76.2,extra={
        'Sim.Device':'V','Sim.Type':'SIN' if source=='VSIN' else 'PULSE',
        'Sim.Params':params,'Sim.Pins':'1=+ 2=-'})
    symbol('Device:R','R1','12k',91.44,71.12,90)
    symbol('Device:C','C1','100n',116.84,76.2)
    symbol('Simulation_SPICE:0','#GND01','0',60.96,96.52,pins=('1',))
    segments=[(60.96,71.12,87.63,71.12),(95.25,71.12,116.84,71.12),
              (116.84,71.12,116.84,72.39),(116.84,80.01,116.84,96.52),
              (60.96,81.28,60.96,96.52),(60.96,96.52,116.84,96.52)]
    for i,(x1,y1,x2,y2) in enumerate(segments):
        out.append(f'(wire (pts (xy {x1} {y1}) (xy {x2} {y2})) (stroke (width 0) (type default)) (uuid "{uid(name+str(i))}"))')
    for label,x in [('VIN',78.74),('VADC',106.68)]:
        out.append(f'(label "{label}" (at {x} 71.12 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid "{uid(name+label)}"))')
    for i,(text,y) in enumerate([(directive,110),('R1 / C1 correspond to the left current-channel draft.',120),
                                 ('Ideal source and RC only; no sensor, ADC sampling, leakage or protection model.',125)]):
        out.append(f'(text {quote(text)} (at 45 {y} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{uid(name+"text"+str(i))}"))')
    out.append(')')
    schematic=HERE/(name+'.kicad_sch')
    schematic.write_bytes(('\n'.join(out)+'\n').encode('utf-8'))
    reports=HERE/'reports';reports.mkdir(exist_ok=True)
    net=reports/(name+'.cir')
    subprocess.run([str(CLI),'sch','export','netlist','--format','spice','-o',str(net),str(schematic)],check=True,capture_output=True)
    lines=net.read_text(encoding='utf-8').splitlines()
    devices={r[0]:r for r in (line.split() for line in lines) if r and r[0] in ('R1','C1','V1')}
    assert set(devices)=={'R1','C1','V1'},devices
    assert set(devices['R1'][1:3])=={'/VIN','/VADC'},devices
    assert set(devices['C1'][1:3])=={'/VADC','0'},devices
    assert devices['V1'][1:3]==['/VIN','0'],devices
    assert devices['R1'][3]=='12k' and devices['C1'][3]=='100n',devices
    subprocess.run([str(CLI),'sch','export','svg','-o',str(reports)+os.sep,str(schematic)],check=True,capture_output=True)
    return {'schematic':schematic.name,'sha256':hashlib.sha256(schematic.read_bytes()).hexdigest(),
            'netlist':net.name,'devices':devices,'default_analysis':directive}

if __name__=='__main__':
    models=[build('Current_RC_AC','VSIN','dc=1.65 ampl=100m f=19k ac=1','.ac dec 200 1 1Meg'),
            build('Current_RC_Step','VPULSE','y1=1.43 y2=1.87 td=1m tr=1u tf=1u tw=20m per=40m','.tran 2u 30m 0 2u')]
    report={'status':'SCHEMATIC_EXPORT_AND_CONNECTIVITY_CHECK_PASS',
            'kicad_version':subprocess.check_output([str(CLI),'version'],text=True).strip(),
            'ngspice_library_available':(KICAD/'bin/ngspice.dll').is_file(),
            'simulation_run':'NOT_RUN','hardware_test':'NOT_RUN','models':models}
    (HERE/'reports/preparation.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(json.dumps(report,ensure_ascii=False,indent=2))
