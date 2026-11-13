"""Reconcile documented component identities and stale annotations; preserve connectivity.

Run once against the saved before snapshots. Export candidates with copied project
settings, verify netlists/ERC, then apply only if the live source hash still matches.
"""
from pathlib import Path
import importlib.util
import json
import shutil
import sys

OUT = Path(__file__).resolve().parent
PROJECT = next(p for p in OUT.parents if p.name == 'Tracked_Mobile_Robot')
spec = importlib.util.spec_from_file_location('tmr_parser', OUT.parent / '2026-11-06_schematic_layout_review/rearrange_schematic.py')
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)

VALUES = {
    'S0': 'SF2ER-E2R2B', 'S2': 'ABW110G', 'K1': 'V23134J1052D642',
    'K2': 'TX2-12V', 'F1': 'Littelfuse_10A', 'F2': 'Littelfuse_1A',
    'U1': 'VO617A-3', 'R13': '680R', 'R14': '10k',
    'J13': 'XL4015_1_OUT', 'J17': 'K1_COIL_INTERFACE',
    'J19': 'K1_MAIN_CONTACT_INTERFACE',
}

MVP_TEXT = {
 'K1 COIL INTERFACE': 'K1 COIL INTERFACE\nPin 1: K1_COIL_P / Pin 2: GND\nTE V23134J1052D642 installed\nP6KE16CA across physical 85-86\nClamp transient / release timing remains OPEN',
 'K1 MAIN CONTACT INTERFACE': 'K1 MAIN CONTACT INTERFACE\nPin 1: VBAT_PROTECTED / Pin 2: MOTOR_VBAT_SAFE\nExternal TE V23134J1052D642 main NO contact\nHigh-current / off-perfboard\nFunctional pin IDs; terminal / wire release remains OPEN',
 'S0-B SENSE': 'S0-B SENSE\n5V/contact closed -> opto ON -> PC7 LOW\npressed/open/5V loss -> PC7 HIGH\nInstalled: VO617A-3; R13=680R; R14=10k\nConditioned path evidence: verification report 25',
 'K2 CONTROL RELAY': 'K2 CONTROL RELAY | Panasonic TX2-12V installed\nSCHEMATIC IDs -> PHYSICAL pins (bottom view)\nA1 -> 1 (+); A2 -> 12 (-)\n11 -> 9 (COM); 14 -> 8 (NO): HOLD\n21 -> 4 (COM); 24 -> 5 (NO): K1 ENABLE\nSchematic 12/22: unused NC contacts\nGeneric symbol is not a physical footprint pin map',
 'TRACKED MOBILE ROBOT |': 'TRACKED MOBILE ROBOT | MVP FUNCTIONAL WIRING | RevB - 2026-11-07',
 'Graphical reorganization:': 'Layout: 2026-11-06 | Component identities reconciled: 2026-11-07 | Original functional connections retained',
 '08  ORIGINAL CHECKPOINT STATUS': '08  CURRENT DOCUMENT STATUS',
 'HISTORICAL:': 'Recorded hardware evidence reconciled; functional diagram, not an as-built harness release.',
 'Layout review does not': 'Component labels follow recorded hardware evidence. Functional connectivity is retained.\nUse the reconciliation report and dated bench records for physical pin / harness mapping.',
 '48 physical components': '48 physical components / original references and connections retained.\nRecorded component identities updated; rating acceptance remains separate.\nF1: 10A reported, 257 marking / 287 order discrepancy OPEN; F2 exact SKU OPEN.',
 'LAYOUT REVIEW 2026': 'DOCUMENT RECONCILIATION 2026-11-07\nS0 body: SF2ER-E2R2B; ordered suffix -A not visually confirmed\nS2: IDEC ABW110G; no new hardware test\nEvidence: assets/logs/pcb_design/2026-11-07_cad_closeout',
}

SHIELD_TEXT = {
 'MOTOR SUPPLY SIDE': 'MOTOR SUPPLY SIDE  |  J8 / R12-R16 / C6',
 'BATTERY SIDE': 'BATTERY SIDE  |  J7 / R7-R11 / C5',
 '04  VOLTAGE INPUTS': '04  VOLTAGE INPUTS - TWO CHANNELS',
 'Layout space only.': 'Two voltage channels connected to PA4 / PB0. Connection contract 27; ERC checked 2026-11-07.',
 'CN7: 16=3V3': 'CN7: 16=3V3, 20=GND; 32=PA4, 34=PB0\n35=PC2, 37=PC3; 36=PC1/PB9*, 38=PC0/PB8*\n* Verify solder bridges; preserve IMU PB8/PB9.\nCN10: 7=AVDD (TPS / TMUX supply). Other pins unused here.\nNC marks do not alter the NUCLEO wiring.',
 'OPEN ELECTRICAL ITEMS': 'OPEN ELECTRICAL ITEMS\n- Port ESD / misconnection / transient protection remains to be designed.\n- TPS / TMUX connected; power-down backfeed behavior remains unverified.\n- Supply margin, sensor cable capacitance, ADC leakage and sampling / filtering remain open.\n- No automatic motor stop threshold is defined by this sheet.',
}

def export(sch, folder, prefix):
    for kind, args in [('xml', ['export','netlist','--format','kicadxml']),
                       ('pdf', ['export','pdf']), ('erc.json', ['erc','--format','json'])]:
        m.run_cli(['sch', *args, '--output', str(folder / f'{prefix}.{kind}'), str(sch)])

def main():
    previous = json.loads((OUT/'validation.json').read_text(encoding='utf-8')) if (OUT/'validation.json').exists() else {}
    results = {}
    for short, name in [('mvp','Tracked_Mobile_Robot_Wiring_RevB'), ('shield','TMR_Monitor_Shield_RevA')]:
        cad = PROJECT / '09_Electrical_Design/KiCAD' / name
        live = cad / f'{name}.kicad_sch'
        before = OUT / f'{short}_before.kicad_sch'
        live_hash = m.sha(live)
        assert live_hash in [m.sha(before),previous.get(short,{}).get('applied_sha256')], f'{short}: source changed; inspect before proceeding'
        source = before.read_text(encoding='utf-8')
        root = m.parse(source)
        edits, changes = [], []
        if short == 'mvp':
            for sym in root.children('symbol'):
                ref = m.prop(sym,'Reference').items[2].value
                if ref in VALUES:
                    atom = m.prop(sym,'Value').items[2]
                    edits.append((atom.start,atom.end,json.dumps(VALUES[ref])))
                    changes.append({'ref':ref,'before':atom.value,'after':VALUES[ref]})
        texts = MVP_TEXT if short == 'mvp' else SHIELD_TEXT
        tb=root.child('title_block')
        for kind,value in [('date','2026-11-07'),('rev','RevB-DOC1' if short=='mvp' else 'RevA.1-DRAFT')]:
            a=tb.child(kind).items[1]
            edits.append((a.start,a.end,json.dumps(value)))
        if short=='mvp':
            for n in tb.children('comment'):
                value = 'Component identities reconciled; functional pin IDs retained' if n.items[1].value=='1' else 'Existing hardware evidence only; rating / as-built release remains open'
                a=n.items[2];edits.append((a.start,a.end,json.dumps(value)))
            for n in root.children('label'):
                if n.items[1].value=='XL4015_1_5V_OUT_CANDIDATE':
                    a=n.items[1];edits.append((a.start,a.end,json.dumps('XL4015_1_5V_OUT')))
            for n in root.children('text_box'):
                if n.items[1].value.startswith('DESIGN STATUS'):
                    value='DOCUMENT STATE - 2026-11-07\n\nUPDATED FROM RECORDED HARDWARE\n- S0: Autonics SF2ER-E2R2B; S2: IDEC ABW110G\n- K1: TE V23134J1052D642; K2: Panasonic TX2-12V\n- F1: Littelfuse 10A; F2: Littelfuse 1A (reported)\n- VO617A-3 / 680R / 10k conditioned sense path\n- K2 generic-to-physical pin mapping shown below\n\nEVIDENCE BOUNDARIES\n- Reports 18 / 19: incoming identification and screens\n- Reports 24 / 25 / 30: scoped assembly / bench evidence\n- No new physical measurement or firmware change\n- F1 series / F2 exact SKU / rating coordination OPEN\n- Original functional connector / encoder topology retained\n- Overall MVP: PARTIAL / OPEN; T007 BLOCKED'
                    a=n.items[1];edits.append((a.start,a.end,json.dumps(value)))
        for n in root.children('text'):
            for prefix, replacement in texts.items():
                if replacement is not None and n.items[1].value.startswith(prefix):
                    a = n.items[1]
                    edits.append((a.start,a.end,json.dumps(replacement)))
                    break
        for start,end,new in sorted(edits,reverse=True):
            source = source[:start]+new+source[end:]
        candidate_dir = OUT / 'candidates' / name
        candidate_dir.mkdir(parents=True,exist_ok=True)
        candidate = candidate_dir / live.name
        candidate.write_text(source,encoding='utf-8',newline='\n')
        for filename in [f'{name}.kicad_pro','sym-lib-table','TMR_Monitor.kicad_sym']:
            if (cad/filename).exists():shutil.copy2(cad/filename,candidate_dir/filename)
        if live_hash==m.sha(before):export(live,OUT,f'{short}_before')
        export(candidate,OUT,f'{short}_candidate')
        bc,bn = m.net_signature(OUT/f'{short}_before.xml')
        cc,cn = m.net_signature(OUT/f'{short}_candidate.xml')
        net_renames={'/XL4015_1_5V_OUT_CANDIDATE':'/XL4015_1_5V_OUT'} if short=='mvp' else {}
        expected_nets={net_renames.get(k,k):v for k,v in bn.items()}
        assert expected_nets == cn, f'{short}: connections or pin types changed'
        expected = {k:dict(v) for k,v in bc.items()}
        if short == 'mvp':
            for ref,value in VALUES.items():expected[ref]['value']=value
        assert cc == expected, f'{short}: unexpected component metadata change'
        erc = json.loads((OUT/f'{short}_candidate.erc.json').read_text(encoding='utf-8'))
        assert not [v for sheet in erc['sheets'] for v in sheet['violations']], erc
        newroot = m.parse(source)
        for kind in ['wire','junction','no_connect','lib_symbols']:
            assert [m.plain(n) for n in root.children(kind)] == [m.plain(n) for n in newroot.children(kind)], kind
        assert m.sha(live) == live_hash, 'Live source changed during review'
        live.write_bytes(candidate.read_bytes())
        export(live,OUT,short+'_current')
        ac,an = m.net_signature(OUT/f'{short}_current.xml')
        assert (ac,an)==(cc,cn)
        applied_erc=json.loads((OUT/f'{short}_current.erc.json').read_text(encoding='utf-8'))
        assert not [v for sh in applied_erc['sheets'] for v in sh['violations']]
        doc=m.fitz.open(OUT/f'{short}_current.pdf')
        doc[0].get_pixmap(matrix=m.fitz.Matrix(1.1,1.1)).save(OUT/f'{short}_current.png')
        results[short]={'before_sha256':m.sha(before),'applied_sha256':m.sha(live),
            'physical_components':len(ac),'total_nets':len(an),'active_nets':sum(not k.startswith('unconnected-') for k in an),
            'net_name_updates':net_renames,
            'connections_and_pin_types_preserved':True,'library_symbols_preserved':True,
            'erc_errors':0,'erc_warnings':0,'ignored_checks':[x['key'] for x in applied_erc['ignored_checks']],
            'value_updates':changes,'annotation_updates':len(edits)-len(changes)}
    (OUT/'validation.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(results,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
