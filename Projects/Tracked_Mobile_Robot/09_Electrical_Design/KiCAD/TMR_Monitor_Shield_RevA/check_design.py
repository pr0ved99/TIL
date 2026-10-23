"""Read-only RevA.0 draft contract check; run with KiCad's bundled Python.

Refresh CLI netlist/ERC/DRC exports before running after a design edit.
This checks connectivity/geometry, not physical fit or electrical performance.
"""
from pathlib import Path
import hashlib
import json
import sys
import xml.etree.ElementTree as ET

import pcbnew as pcb

P = Path(__file__).resolve().parent
K = Path(sys.executable).resolve().parent.parent
NAME = P.name
EXPECTED = {
    '/GND': 'C1.2 C2.2 C3.2 C4.2 J1.20 J3.2 J4.2 J5.2 J6.2 TP2.1',
    '/STM_3V3': 'J1.16 J3.1 J4.1 R3.1 R5.1 TP1.1',
    '/I_LEFT_RAW': 'J3.3 R1.1',
    '/I_LEFT_ADC': 'R1.2 C1.1 J1.38 TP3.1',
    '/I_RIGHT_RAW': 'J4.3 R2.1',
    '/I_RIGHT_ADC': 'R2.2 C2.1 J1.36 TP4.1',
    '/T_LEFT_RAW': 'J5.1 R3.2 R4.1',
    '/T_LEFT_ADC': 'R4.2 C3.1 J1.35 TP5.1',
    '/T_RIGHT_RAW': 'J6.1 R5.2 R6.1',
    '/T_RIGHT_ADC': 'R6.2 C4.1 J1.37 TP6.1',
}
root = ET.parse(P/'reports/netlist.xml').getroot()
allnets = {n.get('name'): {f"{x.get('ref')}.{x.get('pin')}" for x in n.findall('node')}
           for n in root.findall('nets/net')}
active = {n: v for n, v in allnets.items() if not n.startswith('unconnected-')}
assert active == {n: set(v.split()) for n, v in EXPECTED.items()}, 'Schematic net contract changed'
board = pcb.LoadBoard(str(P/(NAME+'.kicad_pcb')))
board_pins = {f'{f.GetReference()}.{p.GetNumber()}': p.GetNetname()
              for f in board.GetFootprints() for p in f.Pads()}
sch_pins = {pin: net for net, pins in allnets.items() for pin in pins}
assert board_pins == sch_pins, 'Schematic and board pad nets differ'
template = pcb.LoadBoard(str(K/'share/kicad/template/STM32_Nucleo-64_Morpho/STM_Nucleo64_Morpho.kicad_pcb'))
def header_pads(b):
    return {f'{f.GetReference()}.{p.GetNumber()}': (p.GetPosition().x, p.GetPosition().y)
            for f in b.GetFootprints() if f.GetReference() in ('J1', 'J2') for p in f.Pads()}
assert header_pads(board) == header_pads(template), 'Template header pad position changed'
assert all(f.GetLayer() == pcb.B_Cu for f in board.GetFootprints() if f.GetReference() in ('J1','J2'))
erc = json.loads((P/'reports/erc.json').read_text(encoding='utf-8'))
drc = json.loads((P/'reports/drc_unrouted.json').read_text(encoding='utf-8'))
erc_count = sum(len(s.get('violations', [])) for s in erc.get('sheets', []))
assert erc_count == 0, 'ERC violations'
assert not drc['schematic_parity'], 'Native schematic parity check failed'
assert not drc['violations'], 'Unexpected placement DRC violation'
result = {
    'status': 'DRAFT_CONNECTIVITY_AND_TEMPLATE_GEOMETRY_CHECK_PASS',
    'active_nets_checked': len(active), 'all_pads_checked': len(board_pins),
    'header_pads_checked': len(header_pads(board)), 'erc_violations': erc_count,
    'drc_violations': len(drc['violations']), 'schematic_parity_issues': len(drc['schematic_parity']),
    'unrouted_connections': len(drc['unconnected_items']), 'tracks': len(list(board.GetTracks())),
    'full_drc_pass': False, 'physical_fit_verified': False, 'protection_design_complete': False,
    'input_hashes': {str(f.relative_to(P)).replace('\\','/'): hashlib.sha256(f.read_bytes()).hexdigest()
                     for f in [P/(NAME+'.kicad_sch'), P/(NAME+'.kicad_pcb'), P/'reports/netlist.xml',
                               P/'reports/erc.json', P/'reports/drc_unrouted.json']},
    'limits': 'Passive draft only. No ADC performance, supply margin, protection, final footprint or real fit acceptance.',
}
(P/'reports/design_review.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='input_hashes'}, indent=2))
