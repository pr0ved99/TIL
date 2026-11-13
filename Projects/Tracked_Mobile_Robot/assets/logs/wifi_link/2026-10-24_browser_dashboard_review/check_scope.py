"""Verify PAGE-only scope against the pre-edit receipt; no build or board access."""
import hashlib
import json
import re
from pathlib import Path

out = Path(__file__).resolve().parent
root = out.parents[3]
source = root / '03_Firmware/esp32_wifi_link/main/wifi_link_main.c'
raw = source.read_bytes()
m = re.search(rb'static const char PAGE\[\] =([\s\S]*?);\r?\n\r?\nstatic ', raw)
html = ''.join(json.loads(v) for v in re.findall(r'"(?:\\.|[^"\\])*"', m[1].decode()))
script = re.search(r'<script>([\s\S]*?)</script>', html)[1]
baseline = json.loads((out / 'baseline.json').read_text(encoding='utf-8-sig'))
old = (out / 'page_before.txt').read_text(encoding='utf-8')
old_script = re.search(r'<script>([\s\S]*?)</script>', old)[1]
sha = lambda data: hashlib.sha256(data).hexdigest()
outside = sha(raw[:m.start(1)] + raw[m.end(1):])
assert outside == baseline['outside_PAGE_sha256']
clean = re.sub(r'// Read-only dashboard:.*?(?=function motionReady\(\))', '', script, flags=re.S)
clean = clean.replace(' refreshDashboard();\n', '').replace('dashboardTick();\n', '')
assert clean.strip() == old_script.strip()
groups = {'shared_control': 46, 'distance': 28, 'nonzero': 21, 'dashboard': 10}
for suite in ['distance', 'nonzero', 'dashboard']:
    log = (out / f'test_{suite}.log').read_text(encoding='utf-8-sig')
    assert not re.search(r'AssertionError|SyntaxError|TypeError', log)
    assert f'{groups[suite]} ' in log.splitlines()[-1] and 'PASS' in log.splitlines()[-1]
result = {
    'date': '2026-10-24', 'source': str(source.relative_to(root)), 'before': baseline,
    'after_main_sha256': sha(raw), 'outside_PAGE_unchanged_byte_for_byte': True,
    'control_script_unchanged_after_removing_dashboard_helpers_and_two_hooks': True,
    'decoded_PAGE_bytes_before': len(old.encode()), 'decoded_PAGE_bytes_after': len(html.encode()),
    'unique_browser_unit_cases': sum(groups.values()), 'groups': groups,
    'test_environment': 'Actual embedded PAGE; Node VM with fake DOM/clock/WebSocket. Shared 46 counted once.',
    'actual_firmware_build': False, 'actual_board_flash': False, 'actual_robot_test': False,
    'previous_board_timing_results_apply_to_this_UI': False,
}
(out / 'validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('PASS PAGE-only bytes; original control JS preserved; 105 unique PC cases; no build/flash')
