"""Review candidate/saved PAGE and actual WS-to-UART main adapter on a native PC."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from unittest import mock

import test_wifi_control_main as adapter
import test_wifi_nonzero_main as baseline
from wifi_distance_page_candidate import HERE,MAIN,prepare,page_range

EXTRA_TEST_INPUTS=()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--saved',action='store_true')
    ap.add_argument('--cc',required=True)
    ap.add_argument('--node',required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--guide',type=Path)
    args=ap.parse_args()
    if args.saved:
        source=MAIN.read_text(encoding='utf-8');a,z,_=page_range(source);page=source[a:z]
    else:
        source,page=prepare()
    assert not(args.saved and args.guide)
    units=[MAIN.parent/('wifi_control_'+stem+ext) for stem in ('contract','owner','ticket','state','executor') for ext in ('.h','.c')]
    files=[MAIN,*units]
    original={p:p.read_bytes() for p in files}
    test_files=[HERE/name for name in ('wifi_distance_page_candidate.py','wifi_distance_page.js',
        'test_wifi_distance_page.js','wifi_distance_main_host_fixture.c',
        'test_wifi_distance_page_candidate.py','test_wifi_nonzero_main.py','test_wifi_control_main.py',
        'test_wifi_control_main_page.js','test_wifi_nonzero_page.js','wifi_distance_page_guide_intro_ko.md')]
    test_files+=list(EXTRA_TEST_INPUTS)
    report={'mode':'SAVED' if args.saved else 'CANDIDATE','scope':__doc__,
        'compiler':args.cc,'node':args.node,'input_sha256':{str(p):hashlib.sha256(b).hexdigest() for p,b in original.items()},
        'candidate_main_sha256':hashlib.sha256(source.encode('utf-8')).hexdigest(),
        'test_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in test_files},
        'checks':{},'limitations':['Native C mocks and extracted PAGE DOM/clock/WebSocket only; no MCU build/flash',
        'TEL cutoff/final observations are not physical stop-time or distance-accuracy acceptance',
        'Browser baseline is a pre-command TEL observation, not the internal STM start timestamp']}
    transcript=[]
    def run(command):
        r=subprocess.run([str(x) for x in command],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=45)
        transcript.append(r.stdout+r.stderr)
        assert r.returncode==0,r.stdout+r.stderr
        return r.stdout
    args.output.parent.mkdir(parents=True,exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix='wifi-distance-page-') as tmp:
            work=Path(tmp);candidate=MAIN if args.saved else work/'candidate.c'
            if not args.saved:candidate.write_text(source,encoding='utf-8')
            regression=work/'regression.json'
            with mock.patch.object(sys,'argv',[baseline.__file__,str(candidate),'--cc',args.cc,
                '--node',args.node,'--output',str(regression)]):baseline.main()
            report['baseline']=json.loads(regression.read_text(encoding='utf-8'))
            transcript.append(regression.with_suffix('.txt').read_text(encoding='utf-8'))
            out=run([args.node,HERE/'test_wifi_distance_page.js',candidate])
            report['checks']['distance_browser']=len(re.findall(r'^PASS distance:',out,re.M))
            host=adapter.host(source).replace('int main(', 'int adapter_baseline_main(')
            host+='\n'+(HERE/'wifi_distance_main_host_fixture.c').read_text(encoding='utf-8')
            for mode in (0,1):
                folder=work/str(mode);folder.mkdir()
                for p in units:(folder/p.name).write_bytes(original[p])
                header=folder/'wifi_control_contract.h';text=header.read_text(encoding='utf-8')
                header.write_text(re.sub(r'^#define WIFI_CONTROL_ZERO_ONLY [01]U$',
                    f'#define WIFI_CONTROL_ZERO_ONLY {mode}U',text,flags=re.M),encoding='utf-8')
                unit=folder/'host.c';unit.write_text(host,encoding='utf-8');exe=folder/'host.exe'
                run([args.cc,'-Wall','-Werror','-I',folder,unit,*[folder/p.name for p in units if p.suffix=='.c'],'-o',exe])
                cases=('distance_wire','distance_first_zero','distance_other_owner','distance_preempt','distance_frame_limit')
                for case in cases:assert run([exe,case]).strip()=='PASS '+case
                report['checks'][f'mode_{mode}_main_distance']=len(cases)
            mutations={
                'drop_goal_suffix':('if(p.distance_mm>0)text+=','if(false)text+='),
                'accept_duplicate_generations':('if(old===null||generation!==0){','if(true){'),
            }
            for name,(old,new) in mutations.items():
                assert source.count(old)==1
                mutated=work/(name+'.c');mutated.write_text(source.replace(old,new),encoding='utf-8')
                r=subprocess.run([args.node,str(HERE/'test_wifi_distance_page.js'),str(mutated)],capture_output=True,timeout=15)
                assert r.returncode!=0,name+' escaped the tests'
            report['checks']['negative_controls_detected']=len(mutations)
        report['status']='PASS'
        if args.guide:
            intro=(HERE/'wifi_distance_page_guide_intro_ko.md').read_text(encoding='utf-8')
            args.guide.parent.mkdir(parents=True,exist_ok=True)
            args.guide.write_text(intro+'\n```c\n'+page+'\n```\n',encoding='utf-8')
            (args.guide.parent/'wifi_link_main_candidate.c').write_text(source,encoding='utf-8')
    except Exception as exc:
        report.update(status='FAIL',error=str(exc));raise
    finally:
        for p,b in original.items():assert p.read_bytes()==b,'Production file changed: '+str(p)
        args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        args.output.with_suffix('.txt').write_text('\n'.join(transcript),encoding='utf-8')
    print(report['mode']+' PASS '+json.dumps(report['checks']))
    print('Production unchanged. Actual board builds, timing and link-distance measurements remain pending.')


if __name__=='__main__':main()
