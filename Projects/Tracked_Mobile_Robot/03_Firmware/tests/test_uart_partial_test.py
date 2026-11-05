"""PC-only UR-02 injection review; production sources remain untouched.

Use --candidate before entry, --saved after the user types the guide.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import reproduce_uart_reconnect as stm_host
import test_wifi_control_main as adapter
from uart_partial_test_candidate import MAIN, HERE, prepare


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--candidate', action='store_true')
    group.add_argument('--saved', action='store_true')
    group.add_argument('--source', type=Path, help='Review a separate C copy without changing firmware')
    parser.add_argument('--output', type=Path, help='Candidate copy only; must be outside production main/')
    args = parser.parse_args()
    cc = os.environ.get('WIFI_CONTROL_HOST_CC') or os.environ.get('W5_HOST_CC') or shutil.which('tcc')
    if not cc:
        raise SystemExit('Set WIFI_CONTROL_HOST_CC to a native C compiler')
    paths = list(adapter.MODULES.glob('wifi_control_*.[ch]')) + [MAIN]
    stm_names = ('uart_mvp_protocol','uart_frame_parser','ring_buffer','drive_command_mapper')
    paths += [stm_host.STM / folder / (name + ext) for name in stm_names
              for folder, ext in (('Inc','.h'),('Src','.c'))]
    paths += [stm_host.STM/'Inc/motor_output.h']
    before = {p:p.read_bytes() for p in paths}
    source = prepare() if args.candidate else (args.source or MAIN).read_text(encoding='utf-8')
    assert 'UART_PARTIAL_TEST_BEGIN' in source, 'Candidate has not been entered'
    assert re.search(r'^#define WIFI_UART_PARTIAL_TEST_MODE 0U$', source, re.M), 'Review/save default-off first'
    # Adapter extraction cannot verify task placement: inspect these integration points explicitly.
    task = source[source.index('static void stm_uart_rx_task('):source.index('static void wifi_event(')]
    assert task.count('wifi_uart_test_step();\n        wifi_control_step();\n        wifi_command_step();') == 2
    server = source[source.index('static void server_start('):source.index('#define STM_UART_PORT')]
    assert 'if (WIFI_UART_PARTIAL_TEST_MODE != 0U)' in server and 'HTTP_POST' in server
    assert '.handler = wifi_uart_test_post' in server
    evidence = []
    def report(line):
        evidence.append(line)
        print(line, flush=True)
    scope = 'CANDIDATE' if args.candidate else ('REVIEW COPY' if args.source else 'SAVED')
    report('MODE '+scope+' native PC only')
    report('MAIN normalized SHA256 '+hashlib.sha256(source.encode()).hexdigest())
    with tempfile.TemporaryDirectory(prefix='uart-partial-') as temp:
        work = Path(temp)
        # Compile the real C initializer, including comments and banner macros.
        # Function extraction alone cannot detect a commented-out PAGE terminator.
        page_start = source.index('static const char PAGE[] =')
        page_end = source.index('static int status_json(', page_start)
        banner_start = source.index('#if WIFI_UART_PARTIAL_TEST_MODE == 3U' if
            'wifi_watchdog_step' in source else '#if WIFI_UART_PARTIAL_TEST_MODE != 0U')
        banner_end = source.index('#endif', banner_start) + len('#endif')
        for mode in (0, 1, 2):
            page_unit = '#include <stdio.h>\n' + f'#define WIFI_UART_PARTIAL_TEST_MODE {mode}U\n'
            page_unit += source[banner_start:banner_end] + '\n' + source[page_start:page_end]
            page_unit += '\nint main(void) { return fwrite(PAGE, 1, sizeof(PAGE)-1, stdout) == sizeof(PAGE)-1 ? 0 : 1; }\n'
            page_c = work/'page.c'; page_exe = work/'page.exe'
            page_c.write_text(page_unit,encoding='utf-8')
            r = subprocess.run([cc,'-Wall','-Werror',str(page_c),'-o',str(page_exe)],
                               capture_output=True,text=True,timeout=30)
            if r.returncode:
                raise RuntimeError(f'PAGE initializer C compile failed (mode={mode}):\n'+r.stdout+r.stderr)
            r = subprocess.run([str(page_exe)],capture_output=True,timeout=10,check=True)
            html = r.stdout.decode('utf-8').replace('\r\n', '\n')
            assert html.count('<script>') == 1 and html.count('</script>') == 1
            assert html.endswith('</html>\n')
            assert ('UART 부분 명령 시험 이미지' in html) == (mode != 0)
        report('PASS real PAGE C initializer + complete HTML/script, modes 0/1/2')
        for path, raw in before.items(): (work/path.name).write_bytes(raw)
        (work/'main.h').write_text(stm_host.HAL, encoding='utf-8')
        shutil.copyfile(HERE/'stm_uart_stream_host_fixture.c',work/'stm_uart_stream_host_fixture.c')
        modules = [str(work/p.name) for p in paths if p.name.startswith('wifi_control_') and p.suffix == '.c']

        def compile_run(name, unit, deps, cases):
            c = work/(name+'.c'); exe = work/(name+'.exe')
            c.write_text(unit, encoding='utf-8')
            r = subprocess.run([cc,'-Wall','-Werror','-I'+str(work),str(c),*deps,'-o',str(exe)],
                               capture_output=True,text=True,timeout=30)
            if r.returncode: raise RuntimeError(r.stdout+r.stderr)
            for case in cases:
                r = subprocess.run([str(exe),*([case] if case else [])],capture_output=True,text=True,timeout=10)
                if r.returncode: raise AssertionError(case+'\n'+r.stdout+r.stderr)
                if not case: report(r.stdout.strip())

        base = (HERE/'wifi_w5_host_fixture.c').read_text(encoding='utf-8')
        extra = (HERE/'wifi_control_main_host_fixture.c').read_text(encoding='utf-8')
        cases = re.findall(r'^    RUN\(([a-z_]+)\)',base,re.M) + re.findall(r'\{\s*"([a-z_]+)"\s*,',extra)
        disabled = adapter.host(source).replace('int main(', 'int adapter_main(')
        disabled += '''
int main(int argc, char **argv) {
    setup(); httpd_req_t req = {0};
    CHECK(wifi_uart_test_post(&req) == ESP_OK);
    CHECK(strcmp(mock_http_status, "404 Not Found") == 0);
    wifi_uart_test_step(); CHECK(mock_write_count == 0 && s_uart_test_phase == UART_TEST_UNUSED);
    return adapter_main(argc, argv);
}
'''
        compile_run('default', disabled, modules, cases)
        report(f'PASS mode=0: disabled handler/dispatch + {len(cases)} W5/main adapter regressions')
        for mode in (1,2):
            candidate = source.replace('#define WIFI_UART_PARTIAL_TEST_MODE 0U',f'#define WIFI_UART_PARTIAL_TEST_MODE {mode}U')
            unit = adapter.host(candidate).replace('int main(', 'int adapter_main(')
            unit = unit.replace('static int uart_write_bytes(', 'static void bench_wire(const void *, size_t);\nstatic int uart_write_bytes(')
            unit = unit.replace('    ++mock_write_count;',
                                '    ++mock_write_count;\n    bench_wire(data, mock_short_write ? length-1 : length);')
            unit += '\n#define main unused_stm_diagnostic\n#include "stm_uart_stream_host_fixture.c"\n#undef main\n'
            unit += (HERE/'uart_partial_main_host_fixture.c').read_text(encoding='utf-8')
            deps = modules + [str(work/(n+'.c')) for n in stm_names[1:]]
            compile_run(f'bench{mode}', unit, deps, [''])
    assert all(p.read_bytes() == raw for p,raw in before.items()), 'Production inputs changed'
    report('Production inputs unchanged; board build/flash/LA capture remain unverified.')
    if args.output:
        target = args.output.resolve()
        assert not target.is_relative_to(adapter.MODULES.resolve()), 'Never overwrite production'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding='utf-8')
        (target.parent/'pc_results.txt').write_text('\n'.join(evidence)+'\n',encoding='utf-8')
        manifest = {
            'scope': scope+' native PC; no target build/flash/physical UART',
            'compiler': cc, 'candidate_main_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'production_unchanged': True,
            'production_inputs': {str(p.relative_to(HERE.parent)).replace('\\','/'):
                                  hashlib.sha256(raw).hexdigest() for p,raw in before.items()},
            'test_inputs': {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
                           [Path(__file__), HERE/'uart_partial_test_candidate.py',
                            HERE/'uart_partial_http_host_fixture.c', HERE/'uart_partial_main_host_fixture.c',
                            HERE/'test_wifi_control_main.py', HERE/'wifi_control_main_host_fixture.c',
                            HERE/'wifi_w5_host_fixture.c', HERE/'stm_uart_stream_host_fixture.c']}
        }
        (target.parent/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__': run()
