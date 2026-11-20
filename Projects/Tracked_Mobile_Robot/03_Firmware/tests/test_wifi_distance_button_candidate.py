"""Stationary-button correction + complete PAGE/main regression; no board build."""
import argparse
import json
from pathlib import Path
import sys
from unittest import mock

from wifi_distance_button_candidate import prepare
from wifi_distance_page_candidate import HERE
import test_wifi_distance_page_candidate as runner


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--saved',action='store_true')
    ap.add_argument('--cc',required=True)
    ap.add_argument('--node',required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--guide',type=Path)
    args=ap.parse_args();assert not(args.saved and args.guide)
    source,page,changes=(None,None,[]) if args.saved else prepare()
    extra=(Path(__file__).resolve(),HERE/'wifi_distance_button_candidate.py',HERE/'wifi_distance_button_guide_intro_ko.md')
    argv=[runner.__file__,'--cc',args.cc,'--node',args.node,'--output',str(args.output)]
    if args.saved:argv.append('--saved')
    with mock.patch.object(runner,'prepare',lambda:(source,page)),mock.patch.object(runner,'EXTRA_TEST_INPUTS',extra),mock.patch.object(sys,'argv',argv):
        runner.main()
    report=json.loads(args.output.read_text(encoding='utf-8'))
    report['scope']=__doc__
    report['correction']='Separate stationary readiness from ACK/ticket availability; bound unsent held request to200ms, cancel on release/stale/movement'
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if args.guide:
        text=(HERE/'wifi_distance_button_guide_intro_ko.md').read_text(encoding='utf-8')
        for i,(name,block) in enumerate(changes,1):
            text+=f'\n## {i}. `{name}()` 전체 교체\n\n'
            text+='PAGE 문자열에서 `"function '+name+'(`로 시작하는 줄부터 해당 함수 끝의 `"}\\n"` 줄까지 교체한다. 다음 함수는 유지한다.\n'
            if name=='distanceReady':text+='새 `distanceStartExpired()`는 이 블록에 포함되어 있으므로 따로 중복 추가하지 않는다.\n'
            text+='\n```c\n'+block+'\n```\n'
        args.guide.parent.mkdir(parents=True,exist_ok=True)
        args.guide.write_text(text,encoding='utf-8')
        (args.guide.parent/'wifi_link_main_candidate.c').write_text(source,encoding='utf-8')


if __name__=='__main__':main()
