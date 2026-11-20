"""Refresh reports and compare current CAD with the reviewed 2026-11-07 draft.
Run with KiCad's bundled Python. Only reports are written; CAD remains unchanged.
PCB differences remain OPEN and are never turned into a full DRC PASS.
"""
from pathlib import Path
import csv
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
import pcbnew as pcb

P = Path(__file__).resolve().parent
PROJECT = next(p for p in P.parents if p.name == 'Tracked_Mobile_Robot')
K = Path(sys.executable).resolve().parent.parent
CLI = K / 'bin/kicad-cli.exe'
REPORTS = P / 'reports'
REFERENCE = PROJECT / 'assets/logs/pcb_design/2026-11-07_cad_closeout/shield_current.xml'
SOURCES = [P / (P.name+s) for s in ('.kicad_sch', '.kicad_pcb', '.kicad_pro')]
SOURCES += [P/'TMR_Monitor.kicad_sym', P/'sym-lib-table']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def signature(path):
    tree = ET.parse(path).getroot()
    parts = {c.get('ref'): {
        'value': c.findtext('value'), 'footprint': c.findtext('footprint') or '',
        'datasheet': c.findtext('datasheet') or '',
        'uuids': [t.text for t in c.findall('tstamps/tstamp')],
    } for c in tree.findall('components/comp')}
    nets = {n.get('name'): sorted(
        (x.get('ref'), x.get('pin'), x.get('pinfunction'), x.get('pintype'))
        for x in n.findall('node')) for n in tree.findall('nets/net')}
    return parts, nets

def main():
    hashes = {f.name: sha(f) for f in SOURCES}
    commands = [
        ['sch', 'export', 'netlist', '--format', 'kicadxml', '--output', str(REPORTS/'netlist.xml'), str(SOURCES[0])],
        ['sch', 'erc', '--format', 'json', '--output', str(REPORTS/'erc.json'), str(SOURCES[0])],
        ['pcb', 'drc', '--format', 'json', '--schematic-parity', '--output', str(REPORTS/'drc_unrouted.json'), str(SOURCES[1])],
    ]
    for args in commands:
        subprocess.run([str(CLI), *args], check=True, capture_output=True, text=True, encoding='utf-8')
    assert all(sha(P/f) == h for f, h in hashes.items()), 'CAD changed during export'
    parts, nets = signature(REPORTS/'netlist.xml')
    ref_parts, ref_nets = signature(REFERENCE)
    with (P/'bom_candidates.csv').open(encoding='utf-8-sig') as f:
        bom_rows = list(csv.DictReader(f))
    bom = {r['Reference']: r for r in bom_rows}
    bom_matches = len(bom_rows) == len(bom) and set(bom) == set(parts) and all(
        bom[r]['Value'] == c['value'] and bom[r]['Footprint_candidate'] == c['footprint']
        for r, c in parts.items())
    erc = json.loads((REPORTS/'erc.json').read_text(encoding='utf-8'))
    drc = json.loads((REPORTS/'drc_unrouted.json').read_text(encoding='utf-8'))
    violations = [v for s in erc['sheets'] for v in s.get('violations', [])]
    board = pcb.LoadBoard(str(SOURCES[1]))
    template = pcb.LoadBoard(str(K/'share/kicad/template/STM32_Nucleo-64_Morpho/STM_Nucleo64_Morpho.kicad_pcb'))
    def headers(b):
        return {f'{f.GetReference()}.{pad.GetNumber()}': (pad.GetPosition().x, pad.GetPosition().y)
                for f in b.GetFootprints() if f.GetReference() in ('J1', 'J2') for pad in f.Pads()}
    header_match = headers(board) == headers(template)
    side_match = all(f.GetLayer() == pcb.B_Cu for f in board.GetFootprints() if f.GetReference() in ('J1','J2'))
    sch_matches = parts == ref_parts and nets == ref_nets
    pcb_refs = {f.GetReference() for f in board.GetFootprints()}
    active = {n: pins for n, pins in nets.items() if not n.startswith('unconnected-')}
    checks_pass = sch_matches and bom_matches and not violations and header_match and side_match
    result = {
        'status': 'SCHEMATIC_CONTRACT_PASS_PCB_REVIEW_OPEN' if checks_pass else 'REVIEW_REQUIRED',
        'date': erc['date'], 'kicad_version': erc['kicad_version'],
        'reference': str(REFERENCE.relative_to(PROJECT)).replace('\\','/'), 'reference_sha256': sha(REFERENCE),
        'source_hashes': hashes, 'sources_unchanged': True,
        'schematic_matches_reviewed_reference': sch_matches, 'bom_matches_schematic': bom_matches,
        'schematic_components': len(parts), 'active_nets_checked': len(active), 'all_nets': len(nets),
        'erc_errors': sum(v.get('severity') == 'error' for v in violations),
        'erc_warnings': sum(v.get('severity') == 'warning' for v in violations),
        'erc_violations': len(violations), 'erc_ignored_checks': erc.get('ignored_checks', []),
        'pcb_footprints': len(pcb_refs), 'missing_on_pcb': sorted(set(parts)-pcb_refs),
        'pcb_extra_references': sorted(pcb_refs-set(parts)),
        'header_pads_checked': len(headers(board)), 'header_geometry_matches_template': header_match,
        'header_side_matches_template': side_match,
        'drc_violations': len(drc['violations']), 'schematic_parity_issues': len(drc['schematic_parity']),
        'unrouted_connections': len(drc['unconnected_items']),
        'tracks': len(list(board.GetTracks())), 'zones': len(list(board.Zones())),
        'full_drc_pass': False, 'physical_fit_verified': False, 'protection_design_complete': False,
        'input_hashes': {str(f.relative_to(P)).replace('\\','/'): sha(f) for f in
                        [*SOURCES, P/'bom_candidates.csv', REPORTS/'netlist.xml', REPORTS/'erc.json', REPORTS/'drc_unrouted.json']},
        'limits': 'Reviewed draft only; PCB not synchronized with all 40 schematic components. No fabrication, ADC performance, protection or physical fit acceptance.',
    }
    (REPORTS/'design_review.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    pin_nets = {r: {} for r in parts}
    for name, pins in nets.items():
        for ref, pin, function, kind in pins:
            if ref in pin_nets:
                pin_nets[ref][pin] = {'net': name, 'function': function, 'type': kind}
    part_report = {
        'schema_version': 2, 'date': erc['date'], 'source_sha256': hashes[SOURCES[0].name],
        'scope': 'Current schematic identity and pin/net inventory; not placement coordinates or a fabrication BOM.',
        'parts': {r: {**v, 'pin_nets': pin_nets[r]} for r, v in parts.items()},
    }
    (REPORTS/'design_parts.json').write_text(json.dumps(part_report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('input_hashes','source_hashes')}, indent=2, ensure_ascii=False))
    return 0 if checks_pass else 1

if __name__ == '__main__':
    raise SystemExit(main())
