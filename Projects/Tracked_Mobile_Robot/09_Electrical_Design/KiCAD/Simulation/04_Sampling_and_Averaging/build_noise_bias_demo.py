"""Build a reproducible educational noise/bias demo, not measured ADC data."""
import json
import math
import random
from pathlib import Path

K = 6.747204164780444
FS, N, COUNT, SEED = 2000, 200, 20000, 37402
SIGMA, BIAS, RAIL = 0.003, 0.005, 12.0


def statistics(values):
    mean = math.fsum(values) / len(values)
    sd = math.sqrt(math.fsum((x - mean) ** 2 for x in values) / len(values))
    return {"count": len(values), "mean_V": mean, "population_sd_V": sd,
            "min_V": min(values), "max_V": max(values)}


def summarize(noise, offset):
    errors = [x + offset for x in noise]
    means = [math.fsum(errors[i:i + N]) / N for i in range(0, COUNT, N)]
    return {"raw_error": statistics(errors), "block_error": statistics(means)}, means


HTML = r'''<!doctype html><html lang="ko"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>37-4 · 40-2 실습 B | 잡음과 일정한 오차</title>
<style>
:root{font-family:system-ui,"Malgun Gothic",sans-serif;color:#193048;background:#f2f5f9}
body{max-width:1120px;margin:28px auto;padding:0 18px}h1{font-size:27px}p,li{line-height:1.65}
.badge{background:#fff0d5;color:#754a09;padding:6px 10px;border-radius:6px;font-size:13px}
.card{background:white;border:1px solid #dbe3ed;border-radius:12px;padding:18px;margin:16px 0}
.controls{display:flex;flex-wrap:wrap;gap:20px}label{cursor:pointer}input{width:18px;height:18px;vertical-align:middle}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.metric b{display:block;font-size:25px;margin:10px 0}.muted,small{color:#53667c}
svg{width:100%;height:auto}table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}th,td{text-align:right;padding:10px;border-bottom:1px solid #e4ebf3}th:first-child,td:first-child{text-align:left}th{background:#edf2f8}
.note{border-left:4px solid #2b71b8;padding-left:14px}.blue{color:#2478c8}.orange{color:#bf6116}
button{font:inherit;padding:8px 12px;background:white;border:1px solid #b5c6d8;border-radius:6px;cursor:pointer}
@media(max-width:650px){.grid{grid-template-columns:1fr}h1{font-size:22px}.scroll{overflow:auto}}
</style>
<span class="badge">가상 표본 학습 모델 · 실측 / KiCad 잡음 해석 아님</span>
<h1>평균은 흔들림과 일정한 오차를 어떻게 처리할까?</h1>
<p>기준 입력은 일정한 <b>12V</b>입니다. 명목 VADC에 가상 잡음과 일정한 오차를 더한 뒤, <b>2kHz · 200개 · 100ms 블록 평균</b>을 적용합니다.</p>
<div class="card controls">
<label><input id="noise" type="checkbox" checked> 가상 잡음: ADC 쪽 표준편차 3mV</label>
<label><input id="bias" type="checkbox"> 일정한 오차: ADC 쪽 +5mV</label>
</div>
<div class="grid">
<div class="card metric">전체 평균의 기준 대비 차이<b id="mean"></b><small id="rail"></small></div>
<div class="card metric">원시 표본의 표준편차<b id="rawsd"></b><small>각 표본이 자기 평균 주위에서 퍼진 정도</small></div>
<div class="card metric">100ms 평균들의 표준편차<b id="avgsd"></b><small>100개 블록 결과가 자기 평균 주위에서 퍼진 정도</small></div>
</div>
<div class="card">
<p><span class="blue">파랑: 원시 표본</span> · <span class="orange">주황: 블록 평균</span> · 점선: 전체 평균의 기준 대비 차이</p>
<svg id="plot" viewBox="0 0 1060 350" role="img" aria-label="가상 ADC 표본과 블록 평균의 기준 대비 차이"></svg>
<p class="muted">세로축: 정상 VADC와의 차이(mV). 가로축: ms. 그래프는 처음500ms, 통계는 전체10초(20,000표본 / 100블록)입니다. 평균은100ms부터 출력됩니다.</p>
<p id="interpret" class="note"></p>
</div>
<div class="card"><h2>세 조건을 같은 가상 잡음 표본으로 비교</h2>
<div class="scroll"><table><thead><tr><th>조건</th><th>전체 평균 차이(mV)</th><th>원시 표준편차(mV)</th><th>평균 후 표준편차(mV)</th></tr></thead><tbody id="compare"></tbody></table></div>
<p>표준편차는 각 자료의 <b>자기 평균</b>을 기준으로 계산합니다. 일정한 오차가 더해져도 퍼진 정도는 그대로입니다. 전체 평균 차이와 함께 봐야 정확도를 판단할 수 있습니다.</p></div>
<div class="card"><h2>직접 확인할 순서</h2><ol>
<li>잡음만 켠 상태에서 원시 표본과 블록 평균의 흔들림을 비교합니다.</li>
<li>잡음을 유지하고 +5mV를 켭니다. 전체 평균 차이와 두 표준편차가 어떻게 달라지는지 읽습니다.</li>
<li>+5mV를 유지하고 잡음을 끕니다. 결과가 전혀 흔들리지 않아도 기준값과 차이가 남는지 확인합니다.</li>
</ol><p id="formula"></p>
<p class="muted">잡음은 고정 시드로 생성한 독립 정규분포 표본을 가정합니다. 3mV·5mV는 효과를 구분하기 위한 학습 값이며 부품 사양이나 실제 잡음 예산이 아닙니다. 외부 RC 뒤의 관측값에 더하는 추상 오차 모델로, 실제 아날로그 잡음의 발생·대역·상관성, ADC 취득·양자화는 모델링하지 않습니다. 유한 표본의 잡음 평균은 정확히0이 아닐 수 있습니다.</p>
<button id="download">현재 조건의 100개 블록 결과 CSV 저장</button>
<details><summary>재현 조건</summary><p id="meta"></p></details></div>
<script type="application/json" id="data">__DATA__</script>
<script>
"use strict";
const D=JSON.parse(document.getElementById("data").textContent),el=id=>document.getElementById(id);
let currentMeans=[];
function stats(a){const mean=a.reduce((s,x)=>s+x,0)/a.length;return {mean,sd:Math.sqrt(a.reduce((s,x)=>s+(x-mean)**2,0)/a.length)};}
function draw(){
 const noiseOn=el("noise").checked,offset=el("bias").checked?D.bias_V:0;
 const errors=D.noise_V.map(x=>(noiseOn?x:0)+offset),means=[];
 for(let i=0;i<errors.length;i+=D.N)means.push(errors.slice(i,i+D.N).reduce((s,x)=>s+x,0)/D.N);
 currentMeans=means;
 const r=stats(errors),b=stats(means),mv=x=>(x*1000).toFixed(6)+" mV";
 el("mean").textContent=mv(r.mean);el("rawsd").textContent=mv(r.sd);el("avgsd").textContent=mv(b.sd);
 el("rail").textContent="입력 환산 차이 "+mv(D.K*r.mean)+" · 평균 "+(D.rail_V+D.K*r.mean).toFixed(6)+" V";
 el("interpret").textContent=offset?(noiseOn?"잡음만 켰을 때보다 전체 평균이 +5mV 이동합니다. 원시·평균 후 표준편차는 그대로입니다.":"모든 표본과 평균이 기준보다 +5mV 높습니다. 흔들림은0이어도 입력 환산값은 약12.033736V입니다."):(noiseOn?"블록 평균의 흔들림이 원시 표본보다 작아집니다. 유한한 잡음 표본의 평균은 정확히0일 필요는 없습니다.":"잡음과 일정한 오차가 모두0인 명목 기준입니다. VADC를 환산하면12V입니다.");
 const x=t=>65+t/500*950,y=v=>290-(v+15)/35*250;
 let h='<defs><clipPath id="clip"><rect x="65" y="35" width="950" height="255"/></clipPath></defs>';
 for(let v=-15;v<=20;v+=5){h+='<line x1="65" x2="1015" y1="'+y(v)+'" y2="'+y(v)+'" stroke="'+(v===0?'#76889c':'#e0e8f1')+'"/><text x="53" y="'+(y(v)+4)+'" text-anchor="end" font-size="12">'+v+'</text>';}
 for(let t=0;t<=500;t+=100)h+='<text x="'+x(t)+'" y="315" text-anchor="middle" font-size="12">'+t+'</text>';
 h+='<text x="8" y="24" font-size="13">mV</text><text x="1008" y="340" font-size="13">ms</text><g clip-path="url(#clip)">';
 h+='<polyline fill="none" stroke="#2478c8" stroke-width="1" opacity=".7" points="'+errors.slice(0,1000).map((v,i)=>x((i+1)/D.fs_Hz*1000)+','+y(v*1000)).join(' ')+'"/>';
 h+='<line x1="65" x2="1015" y1="'+y(r.mean*1000)+'" y2="'+y(r.mean*1000)+'" stroke="#79568e" stroke-dasharray="5 4"/>';
 for(let i=0;i<5;i++){const start=(i+1)*100,end=Math.min(500,start+100),yy=y(means[i]*1000);h+='<line x1="'+x(start)+'" x2="'+x(end)+'" y1="'+yy+'" y2="'+yy+'" stroke="#bf6116" stroke-width="3"/><circle cx="'+x(start)+'" cy="'+yy+'" r="4" fill="#bf6116"/>';}
 el("plot").innerHTML=h+'</g>';
}
const names={ideal:"오차 없음",noise_only:"가상 잡음만",noise_and_bias:"같은 잡음 +5mV"};
el("compare").innerHTML=Object.entries(D.summary).map(([key,v])=>'<tr><td>'+names[key]+'</td><td>'+ (1000*v.raw_error.mean_V).toFixed(6)+'</td><td>'+(1000*v.raw_error.population_sd_V).toFixed(6)+'</td><td>'+(1000*v.block_error.population_sd_V).toFixed(6)+'</td></tr>').join('');
el("formula").textContent="명목 VADC = 12 / K = "+(D.rail_V/D.K).toFixed(9)+" V. 일정한 +5mV의 입력 환산 = K × 0.005 = "+(D.K*D.bias_V).toFixed(9)+" V.";
el("meta").textContent="고정 시드 "+D.seed+" / Python random.Random.gauss / K="+D.K+" / 2kHz, N=200, 100ms / 10초 / 표준편차의 분모는 각 자료 개수 / 가상 모델 데이터";
el("download").addEventListener("click",()=>{let csv="source,block_index,output_time_s,average_VADC_V,rail_estimate_V,error_ADC_V\n";currentMeans.forEach((e,i)=>csv+=["SYNTHETIC_MODEL",i+1,(i+1)/10,D.rail_V/D.K+e,D.rail_V+D.K*e,e].join(',')+'\n');const a=document.createElement('a'),u=URL.createObjectURL(new Blob(['\uFEFF'+csv],{type:'text/csv;charset=utf-8'}));a.href=u;a.download='04_02_SYNTHETIC_noise_'+Number(el('noise').checked)+'_bias_'+Number(el('bias').checked)+'.csv';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);});
for(const id of ["noise","bias"])el(id).addEventListener("change",draw);draw();
</script></html>'''


def main():
    generator = random.Random(SEED)
    noise = [generator.gauss(0.0, SIGMA) for _ in range(COUNT)]
    clean, clean_means = summarize([0.0] * COUNT, 0.0)
    noisy, means = summarize(noise, 0.0)
    shifted, shifted_means = summarize(noise, BIAS)
    # Fixed bias must survive averaging; global average must be preserved.
    assert all(abs(y - x - BIAS) < 1e-15 for x, y in zip(means, shifted_means))
    assert abs(noisy['raw_error']['population_sd_V'] - shifted['raw_error']['population_sd_V']) < 1e-15
    assert abs(noisy['raw_error']['mean_V'] - noisy['block_error']['mean_V']) < 1e-15
    assert clean_means == [0.0] * (COUNT // N)
    data = dict(status="SYNTHETIC_EDUCATIONAL_MODEL_NOT_USER_MEASUREMENT",
                rail_V=RAIL, K=K, fs_Hz=FS, N=N, duration_s=COUNT / FS,
                seed=SEED, assumed_iid_sigma_V=SIGMA, bias_V=BIAS,
                summary=dict(ideal=clean, noise_only=noisy, noise_and_bias=shifted), noise_V=noise)
    out = Path(__file__).resolve().parent / '04_02_noise_model'
    out.mkdir(exist_ok=True)
    serialized = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    (out / 'data.json').write_text(serialized + '\n', encoding='utf-8')
    (out / 'review.html').write_text(HTML.replace('__DATA__', serialized), encoding='utf-8')
    print(json.dumps({"validation": "PASS", "output": str(out), "summary": data['summary']}, indent=2))


if __name__ == '__main__':
    main()
