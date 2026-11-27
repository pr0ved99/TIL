"""Refresh reports and compare current CAD with the reviewed 2026-11-07 draft.
Run with Python providing pcbnew (Ubuntu: /usr/bin/python3). Only reports are written.
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
CLI = K / 'bin' / ('kicad-cli.exe' if sys.platform == 'win32' else 'kicad-cli')
REPORTS = P / 'reports'
REFERENCE = PROJECT / 'assets/logs/pcb_design/2026-11-07_cad_closeout/shield_current.xml'
SOURCES = [P / (P.name+s) for s in ('.kicad_sch', '.kicad_pcb', '.kicad_pro')]
SOURCES += [P/'TMR_Monitor.kicad_sym', P/'sym-lib-table']
PA_HEADER = 'JST_PA_B02B-PASK-1_1x02_P2.00mm_Vertical'
REVIEWED_FOOTPRINTS = {ref: 'TMR_Monitor:' + PA_HEADER for ref in ('J7', 'J8')}
FILTER_CAPS = tuple(f'C{i}' for i in range(1, 7))
CAP_FOOTPRINT = 'Capacitor_THT:C_Disc_D5.1mm_W3.2mm_P5.00mm'
CAP_DATASHEET = 'https://www.vishay.com/docs/45171/kseries.pdf'
CAP_FIELDS = {'Manufacturer': 'Vishay', 'MPN': 'K104K15X7RF53H5'}
REVIEWED_FOOTPRINTS.update(dict.fromkeys(FILTER_CAPS, CAP_FOOTPRINT))
DECOUPLING_CAPS = {'C7': ('220n', 'C0805C224K5RACTU'), 'C8': ('100n', 'C0805C104K5RACTU')}
KEMET_SPECS = 'https://search.kemet.com/component-documentation/download/specsheet/'
REVIEWED_FOOTPRINTS.update(dict.fromkeys(DECOUPLING_CAPS, 'Capacitor_SMD:C_0805_2012Metric'))
RESISTOR_DATASHEETS = {
    'Vishay': 'https://www.vishay.com/docs/28758/tnpw_e3.pdf',
    'Stackpole': 'https://www.seielect.com/Catalog/SEI-RNCF.pdf',
}
# The upstream and downstream voltage channels use the same four selections.
VOLTAGE_RESISTORS = {}
for refs, manufacturer, mpn, footprint in (
    (('R7', 'R8', 'R12', 'R13'), 'Vishay', 'TNPW080512K0BEEA', 'Resistor_SMD:R_0805_2012Metric'),
    (('R9', 'R14'), 'Vishay', 'TNPW12064K70BEEA', 'Resistor_SMD:R_1206_3216Metric'),
    (('R10', 'R15'), 'Stackpole', 'RNCF2512BKE1K00', 'Resistor_SMD:R_2512_6332Metric'),
    (('R11', 'R16'), 'Vishay', 'TNPW080547K0BEEA', 'Resistor_SMD:R_0805_2012Metric'),
):
    VOLTAGE_RESISTORS.update(dict.fromkeys(refs, (manufacturer, mpn)))
    REVIEWED_FOOTPRINTS.update(dict.fromkeys(refs, footprint))
SOURCES += [P/'fp-lib-table', P/'TMR_Monitor.pretty'/(PA_HEADER + '.kicad_mod')]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def signature(path):
    tree = ET.parse(path).getroot()
    parts = {c.get('ref'): {
        'value': c.findtext('value'), 'footprint': c.findtext('footprint') or '',
        'datasheet': c.findtext('datasheet') or '',
        'uuids': (c.findtext('tstamps') or '').split(),
    } for c in tree.findall('components/comp')}
    nets = {n.get('name'): sorted(
        (x.get('ref'), x.get('pin'), x.get('pinfunction'), x.get('pintype'))
        for x in n.findall('node')) for n in tree.findall('nets/net')}
    return parts, nets

def main():
    hashes = {f.relative_to(P).as_posix(): sha(f) for f in SOURCES}
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
    # Compare against the reviewed parts while preserving the original electrical contract.
    expected_parts = {ref: dict(part) for ref, part in ref_parts.items()}
    for ref, footprint in REVIEWED_FOOTPRINTS.items():
        expected_parts[ref]['footprint'] = footprint
    for ref in FILTER_CAPS:
        expected_parts[ref]['datasheet'] = CAP_DATASHEET
    for ref, (manufacturer, _) in VOLTAGE_RESISTORS.items():
        expected_parts[ref]['datasheet'] = RESISTOR_DATASHEETS[manufacturer]
    for ref, (value, mpn) in DECOUPLING_CAPS.items():
        expected_parts[ref].update(value=value, datasheet=KEMET_SPECS + mpn)
    reviewed_matches = parts == expected_parts and nets == ref_nets
    pcb_refs = {f.GetReference() for f in board.GetFootprints()}
    active = {n: pins for n, pins in nets.items() if not n.startswith('unconnected-')}
    footprints = {f.GetReference(): f for f in board.GetFootprints()}
    components = {c.get('ref'): c for c in ET.parse(REPORTS/'netlist.xml').findall('components/comp')}
    sense_header_pads = {}
    for ref, pin, net in [('J1', '32', '/V_UP_ADC'), ('J1', '34', '/V_DOWN_ADC'), ('J2', '7', '/STM_AVDD')]:
        pad = footprints[ref].FindPadByNumber(pin) if ref in footprints else None
        sense_header_pads[f'{ref}.{pin}'] = {
            'net': net,
            'matches': bool(pad and pad.GetNetname() == net and
                            any(node[:2] == (ref, pin) for node in nets.get(net, []))),
        }
    placements = {}
    common_refs = ('U1', 'U2', 'C7', 'C8')
    for ref in (*common_refs, *VOLTAGE_RESISTORS):
        fp = footprints.get(ref)
        part = parts[ref]
        expected_pads = {pin: name for name, nodes in nets.items() for r, pin, _, _ in nodes if r == ref}
        placements[ref] = {
            'position_mm': [pcb.ToMM(fp.GetX()), pcb.ToMM(fp.GetY())] if fp else None,
            'rotation_deg': fp.GetOrientationDegrees() if fp else None,
            'matches': bool(fp and fp.GetLayer() == pcb.F_Cu and fp.GetValue() == part['value']
                            and fp.GetFPIDAsString() == part['footprint']
                            and fp.GetField(pcb.FIELD_T_DATASHEET).GetText() == part['datasheet']
                            and fp.GetPath().AsString().split('/')[-1] in part['uuids']
                            and {pad.GetNumber(): pad.GetNetname() for pad in fp.Pads()} == expected_pads
                            and all(fp.GetFieldText(field.get('name')) == field.text for field in
                                    components[ref].findall('fields/field') if field.get('name') in ('Manufacturer', 'MPN'))
                            and bom.get(ref, {}).get('PCB 배치') == '배치됨'),
        }
    def matches_selection(ref, manufacturer, mpn):
        comp = components.get(ref)
        return (
            comp is not None and comp.findtext("fields/field[@name='Manufacturer']") == manufacturer
            and comp.findtext("fields/field[@name='MPN']") == mpn
            and comp.findtext('footprint') == REVIEWED_FOOTPRINTS[ref]
            and comp.findtext('value') == expected_parts[ref]['value']
            and comp.findtext('datasheet') == expected_parts[ref]['datasheet']
            and bom.get(ref, {}).get('부품 후보') == f'{manufacturer} {mpn}'
        )
    resistor_matches = {ref: matches_selection(ref, *selection) for ref, selection in VOLTAGE_RESISTORS.items()}
    decoupling_matches = {ref: matches_selection(ref, 'KEMET', mpn) for ref, (_, mpn) in DECOUPLING_CAPS.items()}
    cap_matches = {}
    for ref in FILTER_CAPS:
        fp = footprints.get(ref)
        expected_pads = {pin: name for name, pins in nets.items() for r, pin, _, _ in pins if r == ref}
        cap_matches[ref] = (
            ref in components and fp is not None and fp.GetFPIDAsString() == CAP_FOOTPRINT
            and {pad.GetNumber(): pad.GetNetname() for pad in fp.Pads()} == expected_pads
            and all(components[ref].findtext(f"fields/field[@name='{k}']") == fp.GetFieldText(k) == v
                    for k, v in CAP_FIELDS.items())
        )
    mounting_holes = {}
    for hole in template.GetFootprints():
        ref = hole.GetReference()
        if ref not in ('H1', 'H2', 'H3'):
            continue
        fp = footprints.get(ref)
        pads = list(fp.Pads()) if fp else []
        drill = pads[0].GetDrillSize() if len(pads) == 1 else None
        mounting_holes[ref] = {
            'position_mm': [pcb.ToMM(fp.GetX()), pcb.ToMM(fp.GetY())] if fp else None,
            'drill_mm': pcb.ToMM(drill.x) if drill else None,
            'matches': bool(fp and fp.GetPosition() == hole.GetPosition()
                            and fp.GetFPIDAsString() == hole.GetFPIDAsString()
                            and fp.GetAttributes() & pcb.FP_BOARD_ONLY
                            and fp.GetAttributes() & pcb.FP_EXCLUDE_FROM_BOM
                            and drill and drill.x == drill.y == pcb.FromMM(3.2)
                            and pads[0].GetAttribute() == pcb.PAD_ATTRIB_NPTH),
        }
    electrical_footprints_match = pcb_refs - set(mounting_holes) == set(parts)
    pad_spans = {}
    for a, pin_a, b, pin_b in (
        ('C4', '1', 'J1', '37'), ('R8', '2', 'C5', '1'), ('R9', '1', 'C5', '1'),
        ('R13', '2', 'C6', '1'), ('R14', '1', 'C6', '1'),
        ('R10', '2', 'U2', '2'), ('R15', '2', 'U2', '5'),
    ):
        first = footprints[a].FindPadByNumber(pin_a) if a in footprints else None
        last = footprints[b].FindPadByNumber(pin_b) if b in footprints else None
        span = None
        if first and last and first.GetNetname() == last.GetNetname():
            span = round((first.GetPosition() - last.GetPosition()).EuclideanNorm() / 1_000_000, 2)
        pad_spans[f'{a}.{pin_a} - {b}.{pin_b}'] = span
    # Check physical copper islands. Matching net names alone can also describe unrouted pads.
    board.BuildConnectivity()
    connectivity = board.GetConnectivity()
    named_pads = {f'{ref}.{pad.GetNumber()}': pad for ref, fp in footprints.items() for pad in fp.Pads()
                  if pad.GetNumber()}
    routed_groups = {}
    voltage_nets = [net for net in active if net.startswith(('/V', '/MOTOR_VBAT'))
                    or net in ('/GND', '/STM_AVDD')]
    current_nets = [net for net in active if net.startswith('/I_') or net == '/STM_3V3']
    temperature_nets = [net for net in active if net.startswith('/T_')]
    for net, pins in active.items():
        required = [f'{ref}.{number}' for ref, number, _, _ in pins]
        anchor = named_pads.get(required[0])
        island = {item.m_Uuid.AsString() for item in connectivity.GetConnectedItems(anchor)} if anchor else set()
        missing = [pin for pin in required if pin not in named_pads or named_pads[pin].GetNetname() != net
                   or named_pads[pin].m_Uuid.AsString() not in island]
        routed_groups[net] = {'required_pads': required, 'missing_or_disconnected': missing}
    copper = list(board.GetTracks())
    segments = [item for item in copper if item.GetClass() == 'PCB_TRACK']
    vias = [item for item in copper if item.GetClass() == 'PCB_VIA']
    for net, group in routed_groups.items():
        group['net_segment_length_mm_by_layer'] = {
            board.GetLayerName(layer): round(sum(segment.GetLength() for segment in segments
                if segment.GetNetname() == net and segment.GetLayer() == layer) / 1_000_000, 2)
            for layer in (pcb.F_Cu, pcb.B_Cu)
        }
        group['net_vias'] = sum(via.GetNetname() == net for via in vias)
    drc_pass = not any(drc[key] for key in ('violations', 'unconnected_items', 'schematic_parity'))
    routing_complete = not drc['unconnected_items'] and all(
        not group['missing_or_disconnected'] for group in routed_groups.values())
    checks_pass = (reviewed_matches and bom_matches and all(cap_matches.values()) and all(resistor_matches.values())
                   and all(decoupling_matches.values()) and not violations and header_match and side_match
                   and all(pad['matches'] for pad in sense_header_pads.values())
                   and all(placement['matches'] for placement in placements.values())
                   and set(mounting_holes) == {'H1', 'H2', 'H3'}
                   and all(hole['matches'] for hole in mounting_holes.values())
                   and electrical_footprints_match and None not in pad_spans.values()
                   and routing_complete and drc_pass)
    result = {
        'status': 'SCHEMATIC_CONTRACT_PASS_PCB_REVIEW_OPEN' if checks_pass else 'REVIEW_REQUIRED',
        'date': erc['date'], 'kicad_version': erc['kicad_version'],
        'reference': str(REFERENCE.relative_to(PROJECT)).replace('\\','/'), 'reference_sha256': sha(REFERENCE),
        'source_hashes': hashes, 'sources_unchanged': True,
        'schematic_matches_reviewed_reference': sch_matches, 'bom_matches_schematic': bom_matches,
        'reviewed_footprint_assignments_2026_11_27': REVIEWED_FOOTPRINTS,
        'filter_capacitors': {**CAP_FIELDS, 'schematic_fields_board_fields_footprint_and_pad_nets_match': cap_matches},
        'voltage_resistor_selection_matches_schematic_and_bom': resistor_matches,
        'decoupling_capacitor_selection_matches_schematic_and_bom': decoupling_matches,
        'voltage_header_pads': sense_header_pads,
        'voltage_common_placements': {r: placements[r] for r in common_refs},
        'voltage_resistor_placements': {r: placements[r] for r in VOLTAGE_RESISTORS},
        'board_only_mounting_holes': mounting_holes,
        'placed_electrical_components': len(pcb_refs & set(parts)),
        'same_net_pad_center_straight_line_mm': pad_spans,
        'reviewed_value_changes_from_reference': {'C7': {'before': ref_parts['C7']['value'], 'after': parts['C7']['value']}},
        'schematic_matches_reference_with_reviewed_assignments': reviewed_matches,
        'footprints_unassigned': sorted(ref for ref, part in parts.items() if not part['footprint']),
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
        'routing_complete': routing_complete,
        'active_net_pads_checked': sum(len(pins) for pins in active.values()),
        'voltage_routed_groups': {net: routed_groups[net] for net in voltage_nets},
        'current_routed_groups': {net: routed_groups[net] for net in current_nets},
        'temperature_routed_groups': {net: routed_groups[net] for net in temperature_nets},
        'tracks': len(copper), 'track_segments': len(segments), 'vias': len(vias), 'zones': sum(not zone.GetIsRuleArea() for zone in board.Zones()),
        'rule_areas': sum(zone.GetIsRuleArea() for zone in board.Zones()),
        'full_drc_pass': drc_pass, 'physical_fit_verified': False, 'protection_design_complete': False,
        'input_hashes': {str(f.relative_to(P)).replace('\\','/'): sha(f) for f in
                        [*SOURCES, P/'bom_candidates.csv', REPORTS/'netlist.xml', REPORTS/'erc.json', REPORTS/'drc_unrouted.json']},
        'limits': 'Copper continuity is checked against the schematic pad list for every active net. DRC reports enabled rule checks, unrouted items and schematic parity. Fabrication review, power and protection behavior, ADC performance and assembled mechanical fit remain open.',
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
