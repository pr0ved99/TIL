"""PC-only adapter tests: candidate C + saved modules, mocked RTOS/UART.

Usage: python test_wifi_control_main.py <candidate.c or guide.md>
W5_HOST_CC selects TCC/GCC. Does not build ESP or flash hardware.
"""
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from test_wifi_w5_uart_contract import c_type, c_function
from test_firmware_contract import strip_c_comments

HERE = Path(__file__).resolve().parent
MODULES = HERE.parent / 'esp32_wifi_link/main'

def host(source):
    clean = strip_c_comments(source)
    constants = ['WS_MAX_CLIENTS','WIFI_COMMAND_QUEUE_LENGTH','WIFI_COMMAND_MAX_FRAME_SIZE',
                 'WIFI_COMMAND_RESPONSE_MS','WIFI_COMMAND_MIN_INTERVAL_MS','WIFI_COMMAND_RESULT_QUEUE_LENGTH']
    types = ['wifi_command_type_t','wifi_command_request_t','wifi_command_result_t',
             'stm_startup_state_t','stm_startup_t','wifi_uart_pending_t','wifi_ws_session_t']
    definitions = ['#include "wifi_control_executor.h"']
    definitions += [re.search(r'^#define\s+'+n+r'\s+[^\n]+',clean,re.M)[0] for n in constants]
    definitions += [c_type(clean,n) for n in types]
    functions = ['wifi_command_parse_u32','wifi_command_parse','stm_find_field_value',
                 'stm_parse_u32_field','stm_parse_text_field','wifi_control_now','wifi_command_name',
                 'wifi_control_ready_locked','wifi_control_cleanup_locked','wifi_control_closed',
                 'wifi_control_transport_lost','wifi_ws_session_free','wifi_ws_session_get',
                 'wifi_command_admit_locked','wifi_control_snapshot','wifi_uart_allocate_seq',
                 'wifi_control_results_locked','wifi_control_step','wifi_control_handle_response',
                 'wifi_ws_send_notice','ws_receive','ws_command_results',
                 'wifi_command_finish','wifi_command_pending_valid','wifi_command_step','wifi_command_handle_response']
    fixture = (HERE/'wifi_w5_host_fixture.c').read_text(encoding='utf-8')
    fixture = fixture.replace('/* PRODUCTION_TYPES */','\n'.join(definitions))
    globals_start = clean.index('static uint32_t s_wifi_ws_next_session_id;')
    globals_end = clean.index('static uint64_t wifi_control_now(', globals_start)
    declarations = clean[globals_start:globals_end].replace('static uint32_t s_wifi_command_owner_session_id;','')
    declarations += '\nstatic const char *s_stm_startup_status = "READY";\n'
    declarations += 'typedef struct {void *sess_ctx; void (*free_ctx)(void *);} httpd_req_t;\n'
    fixture = fixture.replace('static uint64_t mock_now_ms;', declarations+'\nstatic unsigned mock_lock_depth;\nstatic void (*mock_write_hook)(void);\nstatic uint64_t mock_now_ms;')
    fixture = fixture.replace('(void)semaphore; (void)wait; return pdPASS;', '(void)semaphore; (void)wait; CHECK(mock_lock_depth++ == 0U); return pdPASS;')
    fixture = fixture.replace('(void)semaphore; return pdPASS;', '(void)semaphore; CHECK(mock_lock_depth-- == 1U); return pdPASS;')
    fixture = fixture.replace('    CHECK(queue == s_wifi_command_result_queue && wait == 0U);', '''    CHECK(wait == 0U);
    if (queue == s_wifi_command_queue) {
        if (mock_request_present) return 0;
        mock_request = *(const wifi_command_request_t *)item; mock_request_present = true; return pdPASS;
    }
    CHECK(queue == s_wifi_command_result_queue);''')
    fixture = fixture.replace('    CHECK(queue == s_wifi_command_queue && wait == 0U);', '''
    if(queue==s_wifi_command_result_queue){
        if(!mock_result_count)return 0;
        *(wifi_command_result_t *)item=mock_results[0]; --mock_result_count;
        memmove(mock_results,mock_results+1,mock_result_count*sizeof(mock_results[0]));return pdPASS;
    }
    CHECK(queue == s_wifi_command_queue && wait == 0U);''')
    fixture = fixture.replace('static char mock_uart_line[64];','static char mock_uart_line[128];')
    fixture = fixture.replace('    CHECK(port == STM_UART_PORT', '    CHECK(mock_lock_depth == 0U);\n    if (mock_write_hook != NULL) mock_write_hook();\n    CHECK(port == STM_UART_PORT')
    fixture = fixture.replace('/* PRODUCTION_FUNCTIONS */', '''
typedef int esp_err_t;
typedef void *httpd_handle_t;
enum {ESP_OK=0, ESP_FAIL=-1, HTTPD_WS_TYPE_TEXT=1, HTTPD_WS_TYPE_PONG=10, HTTPD_WS_CLIENT_WEBSOCKET=2};
typedef struct {int type; bool final; uint8_t *payload; size_t len;} httpd_ws_frame_t;
static const char *mock_ws_input;
static char mock_ws_output[512];
static int mock_ws_type=HTTPD_WS_TYPE_TEXT;
static bool mock_ws_final=true, mock_ws_send_fail=false;
static unsigned mock_network_count;
static esp_err_t httpd_ws_recv_frame(httpd_req_t *req,httpd_ws_frame_t *f,size_t n) {
    (void)req; CHECK(mock_lock_depth==0U);
    f->type=mock_ws_type; f->final=mock_ws_final; f->len=strlen(mock_ws_input);
    if(n>0){CHECK(f->len<=n);memcpy(f->payload,mock_ws_input,f->len);} return ESP_OK;
}
static esp_err_t httpd_ws_send_frame(httpd_req_t *req,httpd_ws_frame_t *f) {
    (void)req; CHECK(mock_lock_depth==0U && f->len<sizeof(mock_ws_output));
    memcpy(mock_ws_output,f->payload,f->len); mock_ws_output[f->len]=0; ++mock_network_count;
    return mock_ws_send_fail?ESP_FAIL:ESP_OK;
}
static esp_err_t httpd_get_client_list(httpd_handle_t h,size_t *count,int *clients) {
    (void)h;CHECK(mock_lock_depth==0U);size_t n=0;
    for(size_t i=0;i<WS_MAX_CLIENTS;++i)if(s_sessions[i]!=NULL)clients[n++]=(int)i;
    *count=n;return ESP_OK;
}
static int httpd_ws_get_fd_info(httpd_handle_t h,int fd) {(void)h;(void)fd;return HTTPD_WS_CLIENT_WEBSOCKET;}
static void *httpd_sess_get_ctx(httpd_handle_t h,int fd) {(void)h;return s_sessions[fd];}
static esp_err_t httpd_ws_send_frame_async(httpd_handle_t h,int fd,httpd_ws_frame_t *f) {
    (void)h;(void)fd;return httpd_ws_send_frame(NULL,f);
}
static esp_err_t httpd_sess_trigger_close(httpd_handle_t h,int fd) {(void)h;(void)fd;return ESP_OK;}
static BaseType_t xQueueReset(QueueHandle_t q) {
    CHECK(q == s_wifi_command_queue); mock_request_present = false; return pdPASS;
}
'''+'\n'.join(c_function(clean,n) for n in functions))
    fixture = fixture.replace('    mock_now_ms = 1000U;', '''    mock_now_ms = 1000U;
    mock_lock_depth = 0U; mock_write_hook = NULL;
    mock_ws_type=HTTPD_WS_TYPE_TEXT;mock_ws_final=true;mock_ws_send_fail=false;mock_network_count=0;
    s_stm_startup_status = "READY";
    s_manual_stop_pending = false; s_manual_stop_seq = 0U;
    memset(s_sessions,0,sizeof(s_sessions)); s_wifi_ws_next_session_id = 0U;
    wifi_control_executor_init(&s_control, s_boot_id);
    wifi_control_ticket_pool_init(&s_ticket_pool, s_boot_id);''')
    # Preserve all 21 W5 cases, execute added adapter cases through a second dispatcher.
    fixture = fixture.replace('int main(', 'int w5_main(')
    fixture += '\n'+(HERE/'wifi_control_main_host_fixture.c').read_text(encoding='utf-8')
    return fixture

def run():
    source_path = Path(sys.argv[1]); raw = source_path.read_bytes(); source = raw.decode('utf-8')
    if source_path.suffix == '.md': source = re.search(r'```c\n([\s\S]*?)\n```',source)[1]
    cc = os.environ['W5_HOST_CC']
    suite = (HERE/'wifi_w5_host_fixture.c').read_text(encoding='utf-8')
    w5_cases = re.findall(r'^    RUN\(([a-z_]+)\)',suite,re.M)
    adapter = (HERE/'wifi_control_main_host_fixture.c').read_text(encoding='utf-8')
    cases = w5_cases + re.findall(r'\{\s*"([a-z_]+)"\s*,',adapter)
    assert len(w5_cases)==21, w5_cases
    inputs = [MODULES/('wifi_control_'+name+ext) for name in ('contract','ticket','owner','state','executor') for ext in ('.c','.h')]
    before = {p:p.read_bytes() for p in inputs}
    print('Candidate SHA256',hashlib.sha256(source.encode()).hexdigest(),flush=True)
    with tempfile.TemporaryDirectory(prefix='wifi-main-') as work:
        work = Path(work); unit=work/'host.c'; exe=work/'host.exe'
        unit.write_text(host(source),encoding='utf-8')
        compiled=subprocess.run([cc,'-Wall','-Werror','-I'+str(MODULES),str(unit),*[str(p) for p in inputs if p.suffix=='.c'],'-o',str(exe)],capture_output=True,text=True)
        if compiled.returncode: raise RuntimeError(compiled.stdout+compiled.stderr)
        for case in cases:
            r=subprocess.run([str(exe),case],capture_output=True,text=True,timeout=5)
            if r.returncode: raise AssertionError(case+'\n'+r.stdout+r.stderr)
            print(r.stdout.strip(),flush=True)
    assert all(p.read_bytes()==b for p,b in before.items()) and source_path.read_bytes()==raw
    print(f'{len(w5_cases)} W5 + {len(cases)-len(w5_cases)} adapter cases PASS; no ESP build / real UART / RTOS concurrency evidence')

if __name__=='__main__':run()
