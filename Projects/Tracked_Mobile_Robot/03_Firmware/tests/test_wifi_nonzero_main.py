"""Native C + extracted PAGE checks; production/default mode are never modified."""
from pathlib import Path
import argparse
import contextlib
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from unittest import mock
import test_wifi_control_main as baseline

HERE=Path(__file__).resolve().parent
MAIN=HERE.parent/'esp32_wifi_link/main'


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source',type=Path)
    ap.add_argument('--cc',required=True)
    ap.add_argument('--node',required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    source=args.source.read_text(encoding='utf-8')
    modules=[MAIN/('wifi_control_'+name+ext) for name in ('contract','ticket','owner','state','executor') for ext in ('.c','.h')]
    test_inputs=[HERE/n for n in ('test_wifi_nonzero_main.py','test_wifi_control_main.py',
        'test_wifi_control_main_page.js','test_wifi_nonzero_page.js','wifi_nonzero_main_host_fixture.c',
        'wifi_control_main_host_fixture.c','wifi_w5_host_fixture.c')]
    inputs={p:p.read_bytes() for p in [args.source,MAIN/'wifi_link_main.c',*modules,*test_inputs]}
    log=[]
    def run(command,env=None):
        p=subprocess.run([str(s) for s in command],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=45,env=env)
        log.append(p.stdout+p.stderr)
        if p.returncode:raise AssertionError(p.stdout+p.stderr)
        return p.stdout
    saved=args.source.resolve()==(MAIN/'wifi_link_main.c').resolve()
    report={'mode':'SAVED MAIN' if saved else 'CANDIDATE MAIN',
            'scope':'PAGE/main + saved core in both modes; legacy C baseline forced to mode 1; native mocks only, no board build/flash/runtime',
            'source':str(args.source),'compiler':args.cc,'node':args.node,
            'inputs':{str(p):hashlib.sha256(b).hexdigest() for p,b in inputs.items()},'checks':{}}
    try:
        out=run([args.node,HERE/'test_wifi_nonzero_page.js',args.source])
        report['checks']['browser']=len(re.findall(r'^PASS ',out,re.M))
        with tempfile.TemporaryDirectory(prefix='wifi-nonzero-main-') as tmp:
            work=Path(tmp)
            header=(MAIN/'wifi_control_contract.h').read_text(encoding='utf-8')
            mode_pattern=r'^#define WIFI_CONTROL_ZERO_ONLY ([01])U$'
            modes=re.findall(mode_pattern,header,re.M)
            assert len(modes)==1,'expected one valid mode definition'
            input_mode=int(modes[0]);report['input_zero_only']=input_mode
            fixture=baseline.host(source).replace('int main(', 'int baseline_main(')
            fixture+='\n'+(HERE/'wifi_nonzero_main_host_fixture.c').read_text(encoding='utf-8')
            cases=('nz_snapshot','nz_first_zero','nz_wire','nz_expired_ticket','nz_nonowner','nz_preempt')
            for mode in (1,0):
                folder=work/str(mode);folder.mkdir()
                for p in modules:(folder/p.name).write_bytes(inputs[p])
                if mode!=input_mode:
                    (folder/'wifi_control_contract.h').write_text(re.sub(mode_pattern,
                        f'#define WIFI_CONTROL_ZERO_ONLY {mode}U',header,flags=re.M),encoding='utf-8')
                # The selected mode retains every firmware input byte unchanged.
                if mode==1:
                    output=io.StringIO()
                    with mock.patch.object(baseline,'MODULES',folder), \
                         mock.patch.object(sys,'argv',[str(HERE/'test_wifi_control_main.py'),str(args.source)]), \
                         mock.patch.dict(os.environ,{'W5_HOST_CC':args.cc}), \
                         contextlib.redirect_stdout(output):
                        baseline.run()
                    out=output.getvalue();log.append(out)
                    report['checks']['baseline_mode_1_existing_c']=len(re.findall(r'^PASS ',out,re.M))
                unit=folder/'host.c';unit.write_text(fixture,encoding='utf-8')
                exe=folder/'host.exe'
                command=[args.cc,'-Wall','-Werror','-I'+str(folder),unit,*[folder/p.name for p in modules if p.suffix=='.c'],'-o',exe]
                run(command)
                for case in cases:assert run([exe,case]).strip()=='PASS '+case
                report['checks'][f'mode_{mode}_adapter']=len(cases)
            # Compile the full PAGE initializer as C, including its banner slot.
            page=re.search(r'static const char PAGE\[\] =[\s\S]*?;\n\nstatic ',source)[0][:-len('\n\nstatic ')]
            unit=work/'page.c';exe=work/'page.exe'
            unit.write_text('#include <string.h>\n#define WIFI_UART_PARTIAL_TEST_BANNER ""\n'+page+
                '\nint main(void){return strstr(PAGE,"id=\'forward\'")==0 || strstr(PAGE,"</script></body></html>")==0;}\n',encoding='utf-8')
            run([args.cc,'-Wall','-Werror',unit,'-o',exe]);run([exe])
            report['checks']['page_c_initializer']=1
            # A zero-only advertisement must not pass the mode0 adapter check.
            unit=work/'0/host.c'
            text=unit.read_text(encoding='utf-8')
            assert text.count('WIFI_CONTROL_ZERO_ONLY ? "true" : "false"')==1
            unit.write_text(text.replace('WIFI_CONTROL_ZERO_ONLY ? "true" : "false"','"true"'),encoding='utf-8')
            run(command)
            p=subprocess.run([str(work/'0/host.exe'),'nz_snapshot'],capture_output=True,timeout=5)
            assert p.returncode!=0,'Mode advertisement mutation escaped'
            # Old hardcoded zero TX must fail the pointer-to-command checks.
            mutated=work/'zero_page.c'
            needle='const vx=move?motion.vx:0,w=move?motion.w:0;'
            assert source.count(needle)==1
            mutated.write_text(source.replace(needle,'const vx=0,w=0;'),encoding='utf-8')
            p=subprocess.run([args.node,str(HERE/'test_wifi_nonzero_page.js'),str(mutated)],capture_output=True,timeout=15)
            assert p.returncode!=0,'PAGE zero-value mutation escaped'
            report['checks']['negative_controls_detected']=2
        report['status']='PASS'
    finally:
        for p,b in inputs.items():assert p.read_bytes()==b, f'Input changed: {p}'
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.with_suffix('.txt').write_text('\n'.join(log),encoding='utf-8')
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(report['mode']+' PASS '+json.dumps(report['checks']))
    print('Inputs unchanged. No ESP/STM build, flash or physical motion test.')


if __name__=='__main__':main()
