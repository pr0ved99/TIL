"""Validate this documentation closeout; never operate firmware or hardware."""
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
baseline = json.loads((HERE / 'baseline.json').read_text(encoding='utf-8'))
protected = baseline['unrelated_sha256']
for name, expected in protected.items():
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name

spec = HERE.parent / '2026-10-27_monitoring_verification_spec'
subprocess.run([sys.executable, str(spec / 'validate.py')], check=True, capture_output=True)
spec_result = json.loads((spec / 'validation.json').read_text(encoding='utf-8'))

# Include the session's original scope plus the closeout entrypoints, so this
# check is reproducible after the content commit has made the worktree clean.
paths = set()
for name in baseline['initial_scope']:
    f = ROOT / name
    paths.update(f.rglob('*') if f.is_dir() else [f])
paths.update(HERE.rglob('*'))
for name in ['README.md', 'PROJECT_MEMORY.md', 'docs/handoff/README.md',
             'docs/progress/2026-10-28_progress.md']:
    paths.add(PROJECT / name)
files = sorted(f for f in paths if f.is_file() and '__pycache__' not in f.parts)
docs = [f for f in files if f.suffix == '.md']
missing = []
link_count = 0
for f in docs:
    content = f.read_text(encoding='utf-8')
    assert len(re.findall(r'^```', content, re.M)) % 2 == 0, f
    for raw in re.findall(r'\]\(([^)]+)\)', content):
        if raw.startswith(('http:', 'https:', '#', 'mailto:')):
            continue
        path = unquote(raw.split('#')[0].strip('<>'))
        link_count += 1
        target = (f.parent / path).resolve()
        # This report is created only after the checks pass on the first run.
        if not target.exists() and target != HERE / 'validation.json':
            missing.append([str(f.relative_to(ROOT)), path])
assert not missing, missing
scoped = [str(f.relative_to(ROOT)).replace('\\', '/') for f in files]
assert not set(scoped).intersection(protected)
assert not any('/03_Firmware/' in name or name.endswith(('.kicad_sch', '.kicad_pcb'))
               for name in scoped)
assert all(f.stat().st_size < 100 * 1024 * 1024 for f in files)
subprocess.run(['git', 'diff', '--check', '--', *scoped], cwd=ROOT, check=True)
subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ROOT, check=True)

report = {
    'status': 'DOCUMENT_AND_CALCULATION_CHECK_PASS',
    'scope': '10/27 work and 10/28 documentation closeout',
    'documents_checked': len(docs),
    'local_links_checked': link_count,
    'missing_local_links': missing,
    'unrelated_dirty_files_preserved': len(protected),
    'current_cad_matches_saved_review_hashes': spec_result['current_cad_matches_saved_review_hashes'],
    'calculation_check': spec_result['status'],
    'test_matrix_rows': spec_result['test_matrix_rows'],
    'hardware_tests': 'NOT_RUN',
    'firmware_build_flash_and_physical_changes': 'NOT_PERFORMED',
    'git_diff_check': 'PASS',
    'documents': [str(f.relative_to(PROJECT)).replace('\\', '/') for f in docs],
}
(HERE / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
assert (HERE / 'validation.json').is_file()
print(json.dumps({k: v for k, v in report.items() if k != 'documents'}, ensure_ascii=False, indent=2))
