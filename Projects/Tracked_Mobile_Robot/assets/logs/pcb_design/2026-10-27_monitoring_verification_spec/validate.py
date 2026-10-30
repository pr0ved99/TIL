"""Check this documentation package and calculation invariants, not hardware."""
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
ROOT = PROJECT.parents[1]
subprocess.run([sys.executable, str(HERE/'calculate.py')], check=True, capture_output=True)
summary = json.loads((HERE/'calculations.json').read_text(encoding='utf-8'))
assert abs(summary['current_input_equivalent_A']-.1)<1e-12
assert abs(summary['ut210e_1p65V_bound_mV']-14.55)<1e-9
assert .77<summary['temp_beta_model_max_node_error_C']<.78
assert summary['temp_reference_resistor_0p1pct_max_C']<.041
assert summary['temp_fixed_1pct_max_C']>summary['temperature_budget_C']['divider_and_drift']
assert summary['hardware_test_status']=='NOT_RUN'

docs = [
    PROJECT/'09_Electrical_Design/22_Current_Channel_Verification_Spec_2026-10-27_ko.md',
    PROJECT/'09_Electrical_Design/23_Temperature_Channel_Verification_Spec_2026-10-27_ko.md',
    PROJECT/'09_Electrical_Design/README.md',
    PROJECT/'09_Electrical_Design/15_Expansion_PCB_Requirements_2026-10-23_ko.md',
    PROJECT/'09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA/README.md',
    PROJECT/'07_Embedded_Learning_Notes/01_Concept_Notes/README.md',
    PROJECT/'docs/handoff/CURRENT_SESSION_CONTEXT.md',
    PROJECT/'docs/handoff/NEXT_SESSION_START_PROMPT.md',
    PROJECT/'docs/progress/README.md',
    PROJECT/'docs/progress/2026-10-27_progress.md',
    HERE/'README.md',
]
missing = []
link_count = 0
for doc in docs:
    text = doc.read_text(encoding='utf-8')
    assert len(re.findall(r'^```',text,re.M))%2==0, doc
    for raw in re.findall(r'\]\(([^)]+)\)',text):
        if raw.startswith(('http:','https:','#','mailto:')):
            continue
        raw = unquote(raw.split('#')[0].strip('<>'))
        link_count += 1
        if not (doc.parent/raw).resolve().exists():
            missing.append((str(doc.relative_to(ROOT)),raw))
assert not missing, missing

rows = list(csv.DictReader((HERE/'test_matrix.csv').open(encoding='utf-8')))
assert len(rows)==10
assert all(r['status']=='NOT_RUN' for r in rows)
assert all(r['readiness']=='NOT_READY' for r in rows)
template=json.loads((HERE/'run_template.json').read_text(encoding='utf-8'))
assert template['status']=='NOT_RUN'
assert template['reference_readings']==[] and template['mean_min_max_stddev'] is None

# Verify the saved netlist corresponds to the current audited CAD snapshot.
cad=PROJECT/'09_Electrical_Design/KiCAD/TMR_Monitor_Shield_RevA'
review=json.loads((cad/'reports/design_review.json').read_text(encoding='utf-8'))
hashes={}
for name in ['TMR_Monitor_Shield_RevA.kicad_sch','TMR_Monitor_Shield_RevA.kicad_pcb','reports/netlist.xml']:
    digest=hashlib.sha256((cad/name).read_bytes()).hexdigest()
    assert digest==review['input_hashes'][name], ('CAD snapshot changed',name)
    hashes[name]=digest
proc=subprocess.run(['git','diff','--check','--',*[str(p.relative_to(ROOT)) for p in docs]],
                    cwd=ROOT,capture_output=True,text=True)
assert proc.returncode==0, proc.stdout+proc.stderr

report={
    'status':'DOCUMENT_AND_CALCULATION_CHECK_PASS',
    'hardware_tests':'NOT_RUN',
    'documents_checked':len(docs),
    'local_links_checked':link_count,
    'missing_local_links':missing,
    'calculation_assertions':'RT interpolation/inversion, direction, decision boundaries, budget sum and independent-point separation passed',
    'test_matrix_rows':len(rows),
    'current_cad_matches_saved_review_hashes':hashes,
    'source_doc_sha256':{str(p.relative_to(PROJECT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in docs[:2]},
    'git_diff_check':'PASS',
    'firmware_build_flash_and_physical_changes':'NOT_PERFORMED',
}
(HERE/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
