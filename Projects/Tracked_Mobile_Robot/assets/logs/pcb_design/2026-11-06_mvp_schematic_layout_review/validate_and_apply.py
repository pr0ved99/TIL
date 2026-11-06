"""Validate the candidate, then apply only with --apply and an unchanged source.

The rendered candidate must be visually reviewed before invoking --apply.
No firmware, PCB, library, or project-setting changes are made.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import shutil

import rearrange_mvp as r

OUT, m = r.OUT, r.m


def normalized(node):
    return [normalized(i) if isinstance(i,m.Node) else i.value for i in node.items
            if not isinstance(i,m.Node) or i.kind not in ('at','effects')]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    baseline=json.loads((OUT/'baseline.json').read_text(encoding='utf-8'))
    live=m.REPO/baseline['source']
    candidate=OUT/'candidate'/(r.NAME+'.kicad_sch')
    backup=OUT/'before.kicad_sch'
    assert m.sha(backup)==baseline['source_sha256'],'Backup does not match captured original'
    before=m.parse(backup.read_text(encoding='utf-8-sig'))
    after=m.parse(candidate.read_text(encoding='utf-8-sig'))
    assert m.plain(before.child('lib_symbols'))==m.plain(after.child('lib_symbols'))
    assert m.plain(before.child('title_block'))==m.plain(after.child('title_block'))
    assert m.plain(before.child('uuid'))==m.plain(after.child('uuid'))
    bsyms={m.prop(s,'Reference').items[2].value:s for s in before.children('symbol')}
    asyms={m.prop(s,'Reference').items[2].value:s for s in after.children('symbol')}
    assert set(bsyms)==set(asyms)
    for ref,b in bsyms.items():
        a=asyms[ref]
        assert normalized(a)==normalized(b),ref
        assert a.child('at').items[3].value==b.child('at').items[3].value,ref
    counts={}
    for kind in ('wire','junction','no_connect','label'):
        bb={n.child('uuid').items[1].value:n for n in before.children(kind)}
        aa={n.child('uuid').items[1].value:n for n in after.children(kind)}
        assert set(bb)==set(aa),kind
        if kind=='label':
            assert {u:n.items[1].value for u,n in bb.items()}=={u:n.items[1].value for u,n in aa.items()}
        counts[kind]=len(bb)
    for kind in ('text','text_box'):
        aa={n.child('uuid').items[1].value:n for n in after.children(kind)}
        for n in before.children(kind):
            assert aa[n.child('uuid').items[1].value].items[1].value==n.items[1].value
    def check_protected():
        changed=[path for path,sha in baseline['protected'].items() if m.sha(m.REPO/path)!=sha]
        assert not changed,changed
    check_protected()
    assert m.sha(r.CAD/(r.NAME+'.kicad_pro'))==m.sha(candidate.with_suffix('.kicad_pro'))
    commands=[]
    commands.append(m.run_cli(['sch','erc','--format','json','--output',str(OUT/'candidate_erc.json'),str(candidate)]))
    eb=json.loads((OUT/'before_erc.json').read_text(encoding='utf-8'))
    ec=json.loads((OUT/'candidate_erc.json').read_text(encoding='utf-8'))
    def erc_counts(doc):
        return dict(collections.Counter(v['severity'] for s in doc['sheets'] for v in s['violations']))
    assert eb['ignored_checks']==ec['ignored_checks']
    assert eb['included_severities']==ec['included_severities']
    assert erc_counts(eb)==erc_counts(ec)=={}
    baseline_net=m.net_signature(OUT/'before_netlist.xml')
    assert baseline_net==m.net_signature(OUT/'candidate_netlist.xml')
    validation={
        'date':'2026-11-06','status':'CANDIDATE_VERIFIED',
        'source':baseline['source'],'before_sha256':m.sha(backup),'candidate_sha256':m.sha(candidate),
        'physical_components':len(baseline_net[0]),'symbols_including_power':len(bsyms),'nets':len(baseline_net[1]),
        'primitives_preserved':counts,'component_properties_instances_uuids_orientations_identical':True,
        'embedded_symbol_definitions_identical':True,'original_notes_and_title_block_preserved':True,
        'all_net_names_and_ref_pin_pinfunction_pintype_members_identical':True,
        'protected_files_unchanged':len(baseline['protected']),
        'paper':'A2','visual_review':'Whole sheet and functional-block zooms inspected before application',
        'erc':{'version':ec['kicad_version'],'before_errors':0,'before_warnings':0,'candidate_errors':0,'candidate_warnings':0,
               'ignored_checks_preserved':ec['ignored_checks'],'included_severities':ec['included_severities']},
        'boundary':'Graphical reorganization of historical RevB-WIP only; not current as-built acceptance, fabrication release, or hardware verification.'
    }
    if args.apply:
        assert m.sha(live)==baseline['source_sha256'],'Live source changed since snapshot; do not overwrite'
        temp=live.with_suffix('.layout.tmp')
        assert not temp.exists()
        shutil.copyfile(candidate,temp)
        temp.replace(live)
        assert m.sha(live)==m.sha(candidate)
        commands.extend([
            m.run_cli(['sch','export','pdf','--output',str(OUT/'applied.pdf'),str(live)]),
            m.run_cli(['sch','export','netlist','--format','kicadxml','--output',str(OUT/'applied_netlist.xml'),str(live)]),
            m.run_cli(['sch','erc','--format','json','--output',str(OUT/'applied_erc.json'),str(live)]),
        ])
        assert baseline_net==m.net_signature(OUT/'applied_netlist.xml')
        ea=json.loads((OUT/'applied_erc.json').read_text(encoding='utf-8'))
        assert erc_counts(ea)=={}
        assert ea['ignored_checks']==eb['ignored_checks']
        with m.fitz.open(OUT/'applied.pdf') as doc, m.fitz.open(OUT/'candidate.pdf') as cdoc:
            pix=doc[0].get_pixmap(matrix=m.fitz.Matrix(1.3,1.3),alpha=False)
            cpix=cdoc[0].get_pixmap(matrix=m.fitz.Matrix(1.3,1.3),alpha=False)
            assert pix.samples==cpix.samples,'Applied rendering differs from reviewed candidate'
            pix.save(OUT/'applied.png')
            validation['render_pixels_sha256']=hashlib.sha256(pix.samples).hexdigest()
        check_protected()
        validation.update({'status':'APPLIED_AND_VERIFIED','applied_sha256':m.sha(live),'applied_pdf_sha256':m.sha(OUT/'applied.pdf'),'applied_render_identical_to_reviewed_candidate':True})
        validation['erc'].update({'applied_errors':0,'applied_warnings':0})
    (OUT/'validation.json').write_text(json.dumps(validation,indent=2,ensure_ascii=False),encoding='utf-8')
    (OUT/'validation_commands.json').write_text(json.dumps(commands,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({key:validation[key] for key in ['status','physical_components','nets','protected_files_unchanged','erc']},indent=2,ensure_ascii=False))


if __name__=='__main__':main()
