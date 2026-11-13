"""AC-S06 candidate/saved review. Native PC only, never board build/flash/I/O."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
import test_wifi_control_main as adapter
import reproduce_uart_reconnect as stm_host
from test_wifi_w5_uart_contract import c_function
from uart_watchdog_candidate import HERE, MAIN, OUT, prepare


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--candidate', action='store_true')
    group.add_argument('--saved', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    cc = os.environ.get('WIFI_CONTROL_HOST_CC') or os.environ.get('W5_HOST_CC') or shutil.which('tcc')
    if not cc:
        raise SystemExit('Set WIFI_CONTROL_HOST_CC to a native C compiler')
    paths = list(adapter.MODULES.glob('wifi_control_*.[ch]')) + [MAIN]
    stm_names = ('uart_mvp_protocol', 'uart_frame_parser', 'ring_buffer', 'drive_command_mapper')
    paths += [stm_host.STM/folder/(name+ext) for name in stm_names
              for folder, ext in (('Inc', '.h'), ('Src', '.c'))]
    paths += [stm_host.STM/'Inc/motor_output.h']
    before = {p: p.read_bytes() for p in paths}
    source = prepare() if args.candidate else MAIN.read_text(encoding='utf-8')
    assert re.search(r'^#define WIFI_UART_PARTIAL_TEST_MODE 0U$', source, re.M)
    stm = (stm_host.STM/'Src/uart_mvp_protocol.c').read_text(encoding='utf-8')
    modes = re.findall(r'^#define\s+(UART_MVP_\w*TEST_ENABLED)\s+(\d+)U', stm, re.M)
    assert modes and all(value == '0' for _, value in modes), 'Restore all STM test flags first'
    evidence = []
    def report(value):
        evidence.append(value); print(value, flush=True)
    report('AC-S06 '+('CANDIDATE' if args.candidate else 'SAVED')+' native PC, no physical I/O')
    report('MAIN normalized SHA256 '+hashlib.sha256(source.encode()).hexdigest())
    with tempfile.TemporaryDirectory(prefix='uart-watchdog-') as temp:
        work = Path(temp)
        candidate = work/'candidate.c'; candidate.write_text(source, encoding='utf-8')
        # Includes exact PAGE initializer and modes 0/1/2, HTTP and 42 regressions.
        result = subprocess.run([os.sys.executable, str(HERE/'test_uart_partial_test.py'),
            '--source', str(candidate)], capture_output=True, text=True, timeout=90)
        if result.returncode:
            raise RuntimeError(result.stdout+result.stderr)
        report(result.stdout.strip())
        for path, raw in before.items(): (work/path.name).write_bytes(raw)
        (work/'main.h').write_text(stm_host.HAL, encoding='utf-8')
        shutil.copyfile(HERE/'stm_uart_stream_host_fixture.c', work/'stm_uart_stream_host_fixture.c')
        # Compile real mode guard, banner and complete C PAGE initializer for mode 3.
        cfg = source[source.index('/* 0: normal image;'):source.index('static esp_err_t wifi_uart_test_post')]
        page = source[source.index('static const char PAGE[] ='):source.index('static int status_json(')]
        for mode in (3, 4):
            unit = (cfg+page+'\nint main(void) { return 0; }\n').replace(
                '#define WIFI_UART_PARTIAL_TEST_MODE 0U', f'#define WIFI_UART_PARTIAL_TEST_MODE {mode}U')
            (work/'page.c').write_text(unit, encoding='utf-8')
            r = subprocess.run([cc, '-Wall', '-Werror', str(work/'page.c'), '-o', str(work/'page.exe')],
                               capture_output=True, text=True, timeout=30)
            assert (r.returncode == 0) == (mode == 3), r.stdout+r.stderr
        report('PASS real mode 3 PAGE initializer; invalid mode 4 compile rejected')
        enabled = source.replace('#define WIFI_UART_PARTIAL_TEST_MODE 0U', '#define WIFI_UART_PARTIAL_TEST_MODE 3U')
        unit = adapter.host(enabled).replace('int main(', 'int adapter_main(')
        unit = unit.replace('static int uart_write_bytes(',
            'static void bench_wire(const void *, size_t);\nstatic int uart_write_bytes(')
        unit = unit.replace('    ++mock_write_count;',
            '    ++mock_write_count;\n    bench_wire(data, mock_short_write ? length-1 : length);')
        unit += '\nstatic bool stm_startup_handle_response(const char *s) { (void)s; return false; }\n'
        unit += '\n'.join(c_function(source, name) for name in
                          ['stm_parse_i32_field', 'stm_parse_tel', 'stm_uart_handle_line'])
        unit += '\n#define main unused_stm_diagnostic\n#include "stm_uart_stream_host_fixture.c"\n#undef main\n'
        unit += (HERE/'uart_watchdog_host_fixture.c').read_text(encoding='utf-8')
        (work/'bench.c').write_text(unit, encoding='utf-8')
        deps = [str(work/p.name) for p in paths if p.name.startswith('wifi_control_') and p.suffix == '.c']
        deps += [str(work/(n+'.c')) for n in stm_names[1:]]
        r = subprocess.run([cc, '-Wall', '-Werror', '-I'+str(work), str(work/'bench.c'), *deps,
                            '-o', str(work/'bench.exe')], capture_output=True, text=True, timeout=30)
        if r.returncode: raise RuntimeError(r.stdout+r.stderr)
        r = subprocess.run([str(work/'bench.exe')], capture_output=True, text=True, timeout=15)
        if r.returncode: raise AssertionError(r.stdout+r.stderr)
        report(r.stdout.strip())
    assert all(p.read_bytes() == raw for p, raw in before.items())
    report('Production inputs unchanged. Target build/flash, LA, restore/manual re-arm remain unverified.')
    if args.output:
        target = args.output.resolve()
        assert not target.is_relative_to(adapter.MODULES.resolve())
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding='utf-8')
        (target.parent/'pc_results.txt').write_text('\n'.join(evidence)+'\n', encoding='utf-8')
        manifest = {'status': 'PREPARED_PC_ONLY_PENDING_USER_ENTRY',
            'candidate_normalized_sha256': hashlib.sha256(source.encode()).hexdigest(),
            'compiler': cc, 'board_build_flash_runtime': 'NOT_RUN', 'default_mode': 0,
            'test_mode': 3, 'production_unchanged': True,
            'production_inputs': {str(p.relative_to(HERE.parent)).replace('\\', '/'):
                                  hashlib.sha256(raw).hexdigest() for p, raw in before.items()},
            'test_inputs': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                [Path(__file__), HERE/'uart_watchdog_candidate.py', HERE/'uart_watchdog_test_block.c',
                 HERE/'uart_watchdog_host_fixture.c', HERE/'test_uart_partial_test.py',
                 HERE/'test_wifi_control_main.py', HERE/'stm_uart_stream_host_fixture.c']}}
        (target.parent/'source_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    run()
