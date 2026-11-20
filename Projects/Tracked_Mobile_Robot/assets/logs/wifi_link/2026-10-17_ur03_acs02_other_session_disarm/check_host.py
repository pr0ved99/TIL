"""Focused native-PC adapter cases; no ESP build, flashing or board connection."""
from pathlib import Path
import hashlib
import os
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
sys.path.insert(0, str(PROJECT / '03_Firmware/tests'))
from test_wifi_control_main import host

MODULES = PROJECT / '03_Firmware/esp32_wifi_link/main'
main = MODULES / 'wifi_link_main.c'
inputs = [main] + [MODULES / ('wifi_control_' + name + ext)
    for name in ('contract', 'ticket', 'owner', 'state', 'executor') for ext in ('.c', '.h')]
before = {p: p.read_bytes() for p in inputs}
source = main.read_text(encoding='utf-8')
unit = host(source).replace('int main(', 'int prior_adapter_main(')
unit += '\n' + (HERE / 'host_cases.c').read_text(encoding='utf-8')
cc = os.environ.get('WIFI_CONTROL_HOST_CC') or os.environ['W5_HOST_CC']
with tempfile.TemporaryDirectory(prefix='other-session-stop-') as folder:
    folder = Path(folder)
    cfile, exe = folder / 'host.c', folder / 'host.exe'
    cfile.write_text(unit, encoding='utf-8')
    r = subprocess.run([cc, '-Wall', '-Werror', '-I' + str(MODULES), str(cfile),
        *[str(p) for p in inputs[1:] if p.suffix == '.c'], '-o', str(exe)],
        capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stdout + r.stderr)
    r = subprocess.run([str(exe)], capture_output=True, text=True, timeout=10)
    print(r.stdout, end='')
    if r.returncode:
        raise RuntimeError(r.stderr or str(r.returncode))
assert all(p.read_bytes() == value for p, value in before.items())
print('Saved main normalized SHA256:', hashlib.sha256(source.encode()).hexdigest())
print('Production inputs unchanged; native PC simulation only.')
