"""Fix stationary-button flicker in memory; never modify the firmware source."""
import json
import re
from wifi_distance_page_candidate import HERE,MAIN,page_range


def js_function(script,name):
    matches=list(re.finditer(r'function '+name+r'\([^\n]*\)\{[\s\S]*?\n\}',script))
    assert len(matches)==1,(name,len(matches))
    return matches[0].group(0)


def prepare():
    source=MAIN.read_text(encoding='utf-8')
    a,z,literals=page_range(source)
    html=''.join(json.loads(m[0]) for m in re.finditer(r'"(?:\\.|[^"\\])*"',literals))
    prefix,script=html.split('<script>\n',1);script,suffix=script.split('</script>',1)
    helper=(HERE/'wifi_distance_page.js').read_text(encoding='utf-8')
    assert 'function distanceStartExpired()' not in script,'Already corrected; use --saved'
    changes=[]
    for name in ('distanceReady','distanceStart','distanceObserve','sendCommand','controlTick'):
        old=js_function(script,name)
        if name=='distanceReady':
            new=js_function(helper,name)+'\n'+js_function(helper,'distanceStartExpired')
        elif name in ('distanceStart','distanceObserve'):
            new=js_function(helper,name)
        elif name=='sendCommand':
            new=old.replace(" if(cmd==='CMD'&&(!connected()", " if(cmd==='CMD'&&distanceStartExpired()){distanceInterrupt('START_WAIT_TIMEOUT');stopLocal(true);return;}\n if(cmd==='CMD'&&(!connected()",1)
            needle=" try{ws.send(text);}catch(error){disconnect(ws,'명령 송신 실패');return;}"
            assert new.count(needle)==1
            new=new.replace(needle,needle+"\n if(p.distance_mm>0&&distanceTrial!==null&&distanceTrial.first_goal_sent_ms===null)\n  distanceTrial.first_goal_sent_ms=performance.now();",1)
        else:
            needle=' if(!intent)return;'
            assert old.count(needle)==1
            new=old.replace(needle,needle+"\n if(distanceStartExpired()){distanceInterrupt('START_WAIT_TIMEOUT');stopLocal(true);return;}",1)
        assert new!=old,name
        script=script.replace(old,new,1)
        c_block='\n'.join('    '+json.dumps(line,ensure_ascii=False) for line in (new+'\n').splitlines(keepends=True))
        changes.append((name,c_block))
    html=prefix+'<script>\n'+script+'</script>'+suffix
    head,rest=html.split('</h1>',1);head+='</h1>'
    # Keep the compile-time test-image banner in its original position.
    def c_lines(text):
        return '\n'.join('    '+json.dumps(line,ensure_ascii=False) for line in text.splitlines(keepends=True))
    before,js=rest.split('<script>\n',1)
    page='static const char PAGE[] =\n'+c_lines(head)+'\n    WIFI_UART_PARTIAL_TEST_BANNER\n'
    page+='\n'.join(c_lines(part) for part in re.split(r'(?=<[A-Za-z/!])',before) if part)
    page+='\n'+c_lines('<script>\n'+js)+';'
    return source[:a]+page+source[z:],page,changes
