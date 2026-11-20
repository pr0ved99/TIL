"""Actual ESP parser/formatter and PAGE on PC; no target build or hardware I/O."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
from encoder_count_esp_candidate import ESP,prepare,c_function,c_type

HERE=Path(__file__).resolve().parent


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=Path)
    ap.add_argument('--cc',required=True)
    ap.add_argument('--node',required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--observer',type=Path,default=HERE.parent.parent/'assets/logs/wifi_link/2026-10-20_encoder_count_saved_review/console_encoder_observe.js')
    args=ap.parse_args()
    original=ESP.read_bytes()
    source=args.source.read_text(encoding='utf-8') if args.source else prepare()
    functions=['stm_find_field_value','stm_parse_u32_field','stm_parse_i32_field',
        'stm_parse_i64_field','stm_parse_text_field','stm_parse_tel','status_json']
    preamble='''#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#define WIFI_LINK_MODE_NAME "STA"
#define portMAX_DELAY 0
static int s_stm_lock;
static uint64_t mock_us = 1000000U;
static int xSemaphoreTake(int lock, int delay) {(void)lock;(void)delay;return 1;}
static int xSemaphoreGive(int lock) {(void)lock;return 1;}
static int64_t esp_timer_get_time(void) {return (int64_t)mock_us;}
static uint32_t esp_get_free_heap_size(void) {return UINT32_MAX;}
static const char *s_stm_startup_status = "READY";
static uint32_t s_stm_tel_count;
static uint32_t s_boot_id = 123U;
'''
    for name in ['STATUS_JSON_SIZE','STM_TEL_STALE_MS','STM_UART_LINE_SIZE']:
        preamble+=re.search(r'^#define\s+'+name+r'\s+[^\n]+',source,re.M)[0]+'\n'
    assert '#define STM_UART_LINE_SIZE 512U' in preamble
    fixture=preamble+c_type(source,'stm_telemetry_t')+'\nstatic stm_telemetry_t s_stm_telemetry;\n'
    fixture+='\n'.join(c_function(source,n) for n in functions)
    fixture+=(HERE/'encoder_esp_host_fixture.c').read_text(encoding='utf-8')
    logs=[]
    def run(command):
        result=subprocess.run([str(x) for x in command],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60)
        logs.append(result.stdout+result.stderr)
        assert result.returncode==0,logs[-1]
        return result.stdout
    with tempfile.TemporaryDirectory(prefix='encoder-esp-pc-') as tmp:
        work=Path(tmp)
        src=work/'candidate.c';src.write_text(source,encoding='utf-8')
        c=work/'fixture.c';c.write_text(fixture,encoding='utf-8')
        exe=work/'fixture.exe'
        run([args.cc,'-Wall','-Werror',c,'-o',exe])
        out=run([exe])
        vectors=[json.loads(x[5:]) for x in out.splitlines() if x.startswith('JSON ')]
        vector_file=work/'vectors.json';vector_file.write_text(json.dumps(vectors),encoding='utf-8')
        page=run([args.node,HERE/'test_encoder_count_page.js',src,vector_file,args.observer])
        assert len(vectors)==5 and isinstance(vectors[1]['left_count'],str)
        report={'status':'PASS','scope':__doc__, 'mode':'SOURCE' if args.source else 'CANDIDATE',
            'native_checks':len(re.findall(r'^PASS ',out,re.M)),
            'page_checks':len(re.findall(r'^PASS encoder PAGE ',page,re.M)),
            'page_baseline_checks':len(re.findall(r'^PASS (?!encoder PAGE)',page,re.M)),
            'max_json_bytes':int(re.search(r'MAX_JSON_BYTES (\d+)',out)[1]),
            'actual_json_vectors':vectors,'source_sha256':hashlib.sha256(source.encode('utf-8')).hexdigest(),
            'saved_esp_sha256':hashlib.sha256(original).hexdigest(),'firmware_unchanged':ESP.read_bytes()==original,
            'checks':[x for text in (out,page) for x in text.splitlines() if x.startswith('PASS ')]}
        assert report['firmware_unchanged']
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('PASS ESP native:',report['native_checks'],'PAGE:',report['page_checks'],'baseline:',report['page_baseline_checks'],'JSON max:',report['max_json_bytes'])


if __name__=='__main__':main()
