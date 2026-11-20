"""Select the current session scope; preserve unrelated work and evidence bytes."""
from pathlib import Path
import subprocess, json, hashlib, re
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[6]
OUT=Path(__file__).resolve().parent
P='Projects/Tracked_Mobile_Robot/'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def sha(data):return hashlib.sha256(data).hexdigest()

assert not git('diff','--cached','--name-only').strip(), 'Pre-existing staging must be reviewed separately'
changed=[x for x in git('diff','--name-only','-z').decode().split('\0') if x]
new=[x for x in git('ls-files','--others','--exclude-standard','-z').decode().split('\0') if x]
def allowed(s):
    if s=='.gitattributes':return True
    if not s.startswith(P):return False
    q=s[len(P):]
    return (q.startswith(('01_System_Architecture/','09_Electrical_Design/','docs/')) or
      q in ['AGENTS.md','PROJECT_MEMORY.md','README.md','03_Firmware/esp32_wifi_link/README.md',
            '03_Firmware/esp32_wifi_link/main/wifi_link_main.c','03_Firmware/tests/README.md','03_Firmware/tests/test_wifi_dashboard_page.js'] or
      q.startswith('assets/logs/sensor_design/2026-10-23_expansion_power_budget/') or
      any(q.startswith('assets/logs/wifi_link/'+x) for x in ['2026-10-23_home_','2026-10-23_ws_delivery_path_review/','2026-10-24_']))

selected=sorted(s for s in changed+new if allowed(s))
excluded=[s for s in changed+new if not allowed(s)]
assert selected and all((ROOT/s).stat().st_size<100_000_000 for s in selected)
unrelated={s:sha((ROOT/s).read_bytes()) for s in excluded}
# Local Markdown file targets only, excluding code spans, anchors and URLs.
broken=[]; checked=0
for s in selected:
    if not s.endswith('.md'):continue
    txt=(ROOT/s).read_text(encoding='utf-8-sig')
    txt=re.sub(r'```[\s\S]*?```','',txt)
    for target in re.findall(r'\]\(([^\s)]+)(?:\s+"[^"\n]*")?\)',txt):
        if re.match(r'^[a-zA-Z][\w+.-]*:',target) or target.startswith('#'):continue
        target=unquote(target.split('#')[0]).strip('<>')
        if not target:continue
        checked+=1
        if not ((ROOT/s).parent/target).exists():broken.append({'file':s,'target':target})
assert not broken, json.dumps(broken,ensure_ascii=False)
receipt={'selected_files':selected,'selected_count':len(selected),'unrelated_files_sha256':unrelated,
         'local_markdown_targets_checked':checked,'missing_targets':broken,
         'scope':'Current session PCB design draft, browser observation/UI, operation docs and demo edits. Build outputs, old capture/source snapshot and prior serial logs excluded.'}
(OUT/'scope_check.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
selected.append(str((OUT/'scope_check.json').relative_to(ROOT)).replace('\\','/'))
subprocess.run(['git','add','--',*selected],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
assert all(sha((ROOT/s).read_bytes())==h for s,h in unrelated.items())
preserved=[]
for s in selected:
    if '/assets/logs/' in s:
        assert git('show',':'+s)==(ROOT/s).read_bytes(),s
        preserved.append(s)
print(json.dumps({'selected':len(selected),'excluded_unchanged':len(unrelated),'links_checked':checked,'evidence_files_byte_identical_in_index':len(preserved)},ensure_ascii=False))
