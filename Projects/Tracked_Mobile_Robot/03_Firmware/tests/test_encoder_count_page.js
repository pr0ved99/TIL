const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {harness,stmStatus} = require('./test_wifi_control_main_page.js');
const h = harness();
const vectors = JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const valid = value => vm.runInContext('validStatus('+JSON.stringify(value)+')',h.context);
let passed=0;
function test(name,run){run();++passed;console.log('PASS encoder PAGE '+name);}
test('accepts actual native formatter outputs, including initial/stale/false flags',()=>{
    for(const value of vectors)assert.equal(valid(value),true);
});
test('keeps counts beyond 2^53 as exact strings',()=>{
    assert.equal(vectors[1].left_count,'9007199254740993');
    assert.equal(vectors[1].right_count,'-9007199254740993');
    assert.equal(JSON.parse(JSON.stringify(vectors[1])).left_count,'9007199254740993');
});
test('accepts both signed int64 endpoints',()=>{
    assert.equal(valid({...stmStatus(),left_count:'-9223372036854775808',right_count:'9223372036854775807'}),true);
});
test('rejects lossy numbers and malformed/out-of-range count strings',()=>{
    for(const value of [1,null,'9223372036854775808','-9223372036854775809','01','-0','+1','1.0','1e2','','1 ',' 1'])
        assert.equal(valid({...stmStatus(),left_count:value}),false,JSON.stringify(value));
});
test('rejects invalid flags, sample ticks and ARM sequences',()=>{
    for(const [key,value] of [['encoder_valid',1],['encoder_arm_valid',null],['encoder_t_ms',-1],['encoder_arm_seq',4294967296]])
        assert.equal(valid({...stmStatus(),[key]:value}),false,key);
});
test('does not use false measurement flags as malformed transport data',()=>{
    assert.equal(valid({...stmStatus(),encoder_valid:false,encoder_arm_valid:false,encoder_arm_seq:0}),true);
});
test('renders actual count strings without changing commands',()=>{
    const page=harness(),ws=page.sockets[0];ws.open();
    ws.receive(vectors[1]);
    assert.equal(ws.closeCount,0);
    assert.equal(JSON.parse(page.elements.data.textContent).left_count,'9007199254740993');
    assert.deepEqual(ws.sent,['HELLO']);
});
test('read-only observer preserves raw strings and the original stop path',()=>{
    const listeners={};let originalCalls=0;
    const context={window:{addEventListener(){}},document:{hidden:false},
        performance:{now:()=>100},console:{log(){}},setInterval:()=>1,clearInterval(){},
        socket:{addEventListener(name,run){listeners[name]=run;},send(){throw Error('observer must not send');}},
        stopLocal:()=>{++originalCalls;return 'original';},
        intent:false,offer:{phase:'IDLE'},motion:null,pending:null,
        latestTel:vectors[1],latestTelAt:90,offerAt:90,
        focused:()=>true,motionReady:()=>false};
    vm.createContext(context);
    vm.runInContext(fs.readFileSync(process.argv[4],'utf8'),context);
    assert.equal(originalCalls,0);
    listeners.message({data:JSON.stringify(vectors[1])});
    assert.equal(context.stopLocal(false),'original');
    const report=JSON.parse(context.window.g6StopObserve.report());
    assert.equal(report.version,5);
    assert.equal(report.telemetry[0].left_count,'9007199254740993');
    assert.equal(report.telemetry[0].encoder_arm_seq,0);
    assert.equal(originalCalls,1);
});
console.log(passed+' encoder PAGE cases PASS');
