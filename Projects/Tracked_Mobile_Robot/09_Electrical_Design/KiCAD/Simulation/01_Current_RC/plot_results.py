"""Plot saved ngspice CSV results; does not run/recalculate the simulation."""
import csv
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPORTS = HERE / 'reports'
# Optional isolated plotting dependency cache; no firmware Python packages changed.
CACHE = Path(os.environ['USERPROFILE']) / '.cache/tmr-simulation-plot/python'
if CACHE.is_dir():
    sys.path.insert(0, str(CACHE))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def read(name):
    with (REPORTS/name).open(encoding='utf-8') as f:
        return [{k: float(v) for k, v in row.items()} for row in csv.DictReader(f)]


ac, step = read('ac.csv'), read('step.csv')
result = json.loads((REPORTS/'simulation.json').read_text(encoding='utf-8'))
plt.rcParams.update({'font.family': 'Malgun Gothic', 'font.size': 11, 'axes.unicode_minus': False})
fig, axes = plt.subplots(1, 2, figsize=(14, 5.3), layout='constrained')
fig.suptitle('전류 입력 RC · 12kΩ / 100nF — ngspice 실행 결과', fontsize=17, fontweight='bold')
ax = axes[0]
ax.semilogx([r['frequency_hz'] for r in ac], [r['gain_db'] for r in ac], color='#167b96', lw=2)
fc = result['ac']['fc_sim_log_interpolation_hz']
near = result['ac']['nearest_19khz_sample']
ax.plot(fc, -3.0103, 'o', color='#b55032')
ax.annotate(f'차단 주파수 약 {fc:.2f}Hz\n출력 진폭 약 70.7%', (fc, -3.0103),
            xytext=(5, -25), arrowprops={'arrowstyle': '->'}, fontsize=10)
ax.plot(near['frequency_hz'], near['gain_db'], 'o', color='#b55032')
ax.annotate(f"19.055kHz 표본: {100*near['magnitude_ratio']:.3f}%\n약 {near['gain_db']:.2f}dB",
            (near['frequency_hz'], near['gain_db']), xytext=(1200, -65),
            arrowprops={'arrowstyle': '->'}, fontsize=10)
ax.set(xlabel='주파수 (Hz, 로그 눈금)', ylabel='출력 / 입력 진폭비 (dB)',
       title='빠른 흔들림은 얼마나 줄어드는가?', xlim=(1, 1e6), ylim=(-82, 3))
ax.grid(True, which='both', alpha=.2)
ax = axes[1]
ax.plot([r['time_s']*1000 for r in step], [r['vin_v'] for r in step],
        color='#b55032', lw=1.5, label='VIN · 입력')
ax.plot([r['time_s']*1000 for r in step], [r['vadc_v'] for r in step],
        color='#167b96', lw=2, label='VADC · RC 뒤 출력')
cross = 1000*(result['step']['rise_start_s'] + result['step']['99pct_from_rise_start_sim_s'])
ax.plot(cross, 1.8656, 'o', color='#167b96')
ax.annotate('변화 시작(1ms)부터 약 5.53ms 후\n변화량의 99% 도달', (cross, 1.8656),
            xytext=(9, 1.65), arrowprops={'arrowstyle': '->'}, fontsize=10)
ax.set(xlabel='시뮬레이션 시작부터 시간 (ms)', ylabel='전압 (V)',
       title='새 입력 전압을 얼마나 빨리 따라가는가?', xlim=(0, 30), ylim=(1.4, 1.93))
ax.legend(loc='lower center')
ax.grid(True, alpha=.2)
fig.supxlabel('이상 전압원·R·C 모델 | 센서 오차·ADC 누설/샘플링·부품 공차·실물 효과 제외', fontsize=10)
for extension in ['png', 'svg']:
    fig.savefig(REPORTS/f'current_rc_results.{extension}', dpi=160)
print(REPORTS/'current_rc_results.png')
