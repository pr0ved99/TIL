"""Rebuild a graphical-only RevB candidate from before.kicad_sch.

Does not overwrite the live schematic. The shared parser preserves all non-layout
data; netlist/ERC comparison and visual review precede application.
"""
from pathlib import Path
import importlib.util
import json
import shutil
import sys
import uuid

OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('tmr_layout', OUT.parent / '2026-11-06_schematic_layout_review/rearrange_schematic.py')
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)
NAME = 'Tracked_Mobile_Robot_Wiring_RevB'
CAD = m.PROJECT / '09_Electrical_Design/KiCAD' / NAME


def main():
    source = (OUT / 'before.kicad_sch').read_text(encoding='utf-8-sig')
    root = m.parse(source)
    edits = {}
    groups = {}
    refgroup = {}
    positions = {}

    def group(name, refs, box, old, new, breaks=()):
        groups[name] = (box, old, new, breaks)
        for ref in refs.split():
            refgroup[ref] = name

    group('power', 'J8 F1 SW1 #FLG03 #PWR012', (125,25,178,38), (132.08,31.75),(50.8,58.42), ((143.51,25.4),(158.75,25.4)))
    group('enc3', 'J1 R1 R2 R5 R6 #PWR01 #PWR02', (45,38,95,57), (50.8,44.45),(431.8,60.96), ((63.5,25.4),))
    group('enc5', 'J2 R3 R4 R7 R8 #PWR03 #PWR04', (45,59,95,78), (50.8,66.04),(431.8,109.22), ((63.5,25.4),))
    group('auxout', 'J3 #FLG01 #FLG02', (45,80,70,90), (50.8,82.55),(146.05,120.65))
    group('motorout', 'J4', (88,79,110,90), (92.71,82.55),(335.28,57.15))
    group('motorlogic', 'J5 R9 R10 R11 R12 #PWR05', (88,95,120,112), (92.71,104.14),(224.79,104.14), ((104.14,38.1),))
    group('mcuio', 'J6', (125,96,147,112), (142.24,104.14),(368.3,104.14))
    group('buck1in', 'J9 #PWR014', (123,53,135,61), (132.08,55.88),(62.23,91.44))
    group('buck2in', 'J10 #PWR015', (157,53,170,61), (165.1,55.88),(146.05,91.44))
    group('ctrlfuse', 'F2', (125,75,140,81), (132.08,78.74),(58.42,172.72))
    group('s0port', 'J14', (157,66,170,73), (165.1,68.58),(68.58,199.39))
    group('s0', 'S0', (196,79,210,89), (203.2,81.28),(114.3,172.72))
    group('s2', 'S2', (232,81,247,86), (240.03,83.82),(170.18,185.42))
    group('k2', 'K2 #PWR06', (175,94,195,121), (185.42,109.22),(83.82,233.68))
    group('k1', 'K1 #PWR016', (205,46,225,65), (215.9,55.88),(156.21,233.68))
    group('k1contact', 'J19', (208,29,219,37), (215.9,31.75),(167.64,278.13))
    group('motorin', 'J7 #PWR013', (253,29,263,37), (260.35,31.75),(254,57.15))
    group('s2port', 'J16', (233,97,243,104), (240.03,99.06),(167.64,199.39))
    group('k1coil', 'J17 #PWR07', (207,105,217,112), (214.63,106.68),(76.2,278.13))
    group('ledr', 'R13', (159,125,172,129), (165.1,127),(248.92,171.45))
    group('s0bport', 'J15', (157,139,170,145), (165.1,140.97),(337.82,171.45))
    group('opto', 'U1 #PWR08 #PWR010', (193,139,213,149), (203.2,143.51),(259.08,203.2))
    group('pullup', 'R14', (226,138,231,149), (228.6,143.51),(321.31,203.2))
    group('senseport', 'J18 #PWR09', (247,135,257,145), (254,139.7),(351.79,234.95))
    group('uartstm', 'J11', (88,144,102,154), (92.71,148.59),(426.72,177.8))
    group('uartesp', 'J12', (139,144,151,154), (147.32,148.59),(551.18,177.8))
    group('buck1out', 'J13 #FLG04', (88,160,115,168), (92.71,162.56),(62.23,120.65))
    for i in range(1,8):
        x,y = 264.16,66.04+(i-1)*3.81
        new = (444.5,264.16+(i-1)*15.24) if i<=4 else (533.4,264.16+(i-5)*15.24)
        group(f'tp{i}',f'TP{i}',(x-.01,y-.01,x+.01,y+.01),(x,y),new)

    def fmt(value):
        return f'{value:.6f}'.rstrip('0').rstrip('.') or '0'

    def num(atom, value):
        edits[(atom.start,atom.end)] = fmt(value)

    def replace(node, text):
        edits[(node.start,node.end)] = text

    def xygroup(x,y):
        found = [g for g,(b,*_) in groups.items() if b[0]<=x<=b[2] and b[1]<=y<=b[3]]
        assert len(found)==1,(x,y,found)
        return found[0]

    def mapped(g,x,y):
        _,old,new,breaks = groups[g]
        return (x+new[0]-old[0]+sum(dx for threshold,dx in breaks if x>=threshold-1e-6), y+new[1]-old[1])

    def translate(node, dx,dy):
        if node.kind in ('at','xy'):
            num(node.items[1],float(node.items[1].value)+dx)
            num(node.items[2],float(node.items[2].value)+dy)
        else:
            for child in node.items:
                if isinstance(child,m.Node):translate(child,dx,dy)

    def position(node,x,y):
        at=node.child('at');num(at.items[1],x);num(at.items[2],y)

    def effects(node,size,justify=''):
        replace(node.child('effects'), f'(effects (font (size {size} {size}))'+(f' (justify {justify})' if justify else '')+')')

    def fields(sym, x,y,dy=-10.16,center=None):
        # Field angles are relative to symbol rotation in KiCad's schematic model.
        for name,yy in [('Reference',y+dy),('Value',y+dy+2.54)]:
            p=m.prop(sym,name)
            position(p,x if center is None else center,yy)
            num(p.child('at').items[3],float(sym.child('at').items[3].value)%180)
            effects(p,1.27)

    moves=[]
    for n in root.items:
        if not isinstance(n,m.Node):continue
        if n.kind=='symbol':
            ref=m.prop(n,'Reference').items[2].value
            x,y=m.coords(n); nx,ny=mapped(refgroup[ref],x,y)
            translate(n,nx-x,ny-y)
            positions[ref]=(nx,ny)
            moves.append({'ref':ref,'from_mm':[x,y],'to_mm':[round(nx,6),round(ny,6)]})
            if ref.startswith('#'):
                continue
            fields(n,nx,ny)
            if ref in ('R1','R2','R3','R4','R9','R10','R11','R12'):
                # Keep the four 100-mil-spaced pull-down rows readable.
                for name,xx,yy,size in [('Reference',nx-6.35,ny-.762,1.016),('Value',nx,ny,.889)]:
                    p=m.prop(n,name);position(p,xx,yy);effects(p,size)
            if ref in ('R5','R6','R7','R8'):
                side=-1 if ref in ('R6','R8') else 1
                for name,yy in [('Reference',ny+1.27),('Value',ny+3.81)]:
                    p=m.prop(n,name);position(p,nx+side*3.81,yy);effects(p,1.016,'right' if side<0 else 'left')
            if ref=='R14':
                for name,yy in [('Reference',ny-1.27),('Value',ny+1.27)]:
                    p=m.prop(n,name);position(p,nx+3.81,yy);effects(p,1.016,'left')
            if ref=='K1':fields(n,nx,ny,-15.24)
            if ref=='K2':fields(n,nx,ny,-19.05)
            if ref=='U1':fields(n,nx,ny,-10.16)
            if ref=='J11':fields(n,nx,ny,-12.7,center=nx+19.05)
            if ref=='J12':fields(n,nx,ny,-12.7,center=nx-19.05)
            if ref=='J6':fields(n,nx,ny,-10.16,center=nx-12.7)
            if ref.startswith('TP'):
                for name,yy in [('Reference',ny-1.27),('Value',ny+1.27)]:
                    p=m.prop(n,name);position(p,nx+6.35,yy);effects(p,1.27,'left')
        elif n.kind in ('wire','junction','no_connect','label'):
            points=n.child('pts').children('xy') if n.kind=='wire' else [n.child('at')]
            gs=[xygroup(float(p.items[1].value),float(p.items[2].value)) for p in points]
            assert len(set(gs))==1,gs
            for p in points:
                nx,ny=mapped(gs[0],float(p.items[1].value),float(p.items[2].value))
                num(p.items[1],nx);num(p.items[2],ny)
            if n.kind=='label':
                size=n.child('effects').child('font').child('size')
                num(size.items[1],1.016);num(size.items[2],1.016)
        elif n.kind=='text':
            t=n.items[1].value
            dest=(25.4,290.83) if t.startswith('K1 COIL') else (110.49,290.83) if t.startswith('K1 MAIN') else (215.9,223.52) if t.startswith('S0-B') else (25.4,345.44)
            position(n,*dest);effects(n,1.016,'left top')
        elif n.kind=='text_box':
            position(n,213.36,280.67)
            size=n.child('size');num(size.items[1],167.64);num(size.items[2],83.82)
            effects(n,1.27,'left top')
    replace(root.child('paper'), '(paper "A2")')

    additions=[]
    def uid(key):return str(uuid.uuid5(uuid.NAMESPACE_URL,'tmr-mvp-layout-2026-11-06/'+key))
    def text(key,t,x,y,size=1.27):
        additions.append(f'(text {json.dumps(t)} (at {x} {y} 0) (effects (font (size {size} {size})) (justify left top)) (uuid "{uid(key)}"))')
    def frame(key,title,x1,y1,x2,y2):
        additions.append(f'(polyline (pts (xy {x1} {y1}) (xy {x2} {y1}) (xy {x2} {y2}) (xy {x1} {y2}) (xy {x1} {y1})) (stroke (width 0.254) (type default)) (fill (type none)) (uuid "{uid(key)}"))')
        text(key+'title',title,x1+5.08,y1+3.81,1.778)
    text('title','TRACKED MOBILE ROBOT | MVP WIRING | RevB-WIP',15.24,13.97,2.54)
    text('subtitle','Graphical reorganization: 2026-11-06 | Original electrical checkpoint: 2026-08-12 | Net names link functional blocks',15.24,22.86,1.27)
    frame('power','01  BATTERY & DC/DC INTERFACES',15.24,30.48,198.12,137.16)
    frame('motor','02  MDD10A & STM32 MOTOR I/O',205.74,30.48,388.62,137.16)
    frame('encoder','03  DUAL ENCODER CONDITIONING',396.24,30.48,579.12,137.16)
    frame('control','04  E-STOP CONTROL / RELAY INTERFACES',15.24,144.78,198.12,325.12)
    frame('sense','05  E-STOP SENSE / STM32 PC7',205.74,144.78,388.62,254)
    frame('uart','06  STM32 - ESP32 UART',396.24,144.78,579.12,226.06)
    frame('testpoints','07  TEST POINTS',396.24,233.68,579.12,325.12)
    frame('status','08  ORIGINAL CHECKPOINT STATUS',205.74,261.62,388.62,400.05)
    frame('notes','09  RELAY MODEL & DRAWING NOTES',15.24,332.74,198.12,400.05)
    text('historical','HISTORICAL: the status text below belongs to the original RevB-WIP checkpoint.',213.36,273.05,1.143)
    text('statusboundary','Layout review does not establish current as-built wiring or a new bench PASS.\nLater hardware changes must be reconciled before using this as an as-built drawing.',213.36,372.11,1.143)
    text('motorpull','R9-R12: original 10k reset-safe pull-downs',213.36,80.01,1.143)
    text('motorports','Functional connector pin mapping retained from RevB.',213.36,128.27,1.143)
    text('encoderinfo','TIM3 and TIM5 channel identities retained; conditioning values unchanged.',403.86,128.27,1.143)
    text('uartinfo','115200 8N1 is the original documented link setting.\nMatching net names connect TX to the opposite RX; GND is shared.',403.86,203.2,1.27)
    text('notesboundary','48 physical components / original references and connections retained.\nCandidate and TBD markings are intentionally preserved.\nNo change to firmware, PCB layout, component values, or physical hardware.',25.4,381,1.143)
    text('review','LAYOUT REVIEW 2026-11-06\nFunctional blocks / label spacing / field alignment\nVerification artifacts: assets/logs/pcb_design/\n2026-11-06_mvp_schematic_layout_review',401.32,335.28,1.143)
    edits[(root.end-1,root.end-1)]='\n\t'+'\n\t'.join(additions)+'\n'
    # Disallow overlapping edit ranges; this also catches conflicting field rewrites.
    previous_end=-1
    for (start,end),_ in sorted(edits.items()):
        assert start>=previous_end,(start,end,previous_end)
        previous_end=end
    result=source
    for (start,end),v in sorted(edits.items(),reverse=True):result=result[:start]+v+result[end:]
    candidate=OUT/'candidate';candidate.mkdir(exist_ok=True)
    target=candidate/(NAME+'.kicad_sch')
    target.write_text(result,encoding='utf-8',newline='\n')
    shutil.copyfile(CAD/(NAME+'.kicad_pro'),candidate/(NAME+'.kicad_pro'))
    (OUT/'moves.json').write_text(json.dumps(moves,indent=2),encoding='utf-8')
    commands=[m.run_cli(['sch','export','pdf','--output',str(OUT/'candidate.pdf'),str(target)]),m.run_cli(['sch','export','netlist','--format','kicadxml','--output',str(OUT/'candidate_netlist.xml'),str(target)])]
    before=m.net_signature(OUT/'before_netlist.xml');after=m.net_signature(OUT/'candidate_netlist.xml')
    assert before==after, 'Electrical netlist differs: inspect before applying'
    (OUT/'candidate_commands.json').write_text(json.dumps(commands,indent=2,ensure_ascii=False),encoding='utf-8')
    doc=m.fitz.open(OUT/'candidate.pdf');doc[0].get_pixmap(matrix=m.fitz.Matrix(1.3,1.3),alpha=False).save(OUT/'candidate.png')
    print(json.dumps({'status':'CANDIDATE_NETLIST_IDENTICAL','components':len(after[0]),'nets':len(after[1]),'symbols_moved':len(moves),'pdf':str(OUT/'candidate.pdf')},indent=2))


if __name__=='__main__':main()
