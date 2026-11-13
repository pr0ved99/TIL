"""Signal-only alignment aid; does not transcribe or publish input audio."""
from pathlib import Path
import wave, array, math, json

BASE = Path(__file__).resolve().parent
def envelope(stem):
    with wave.open(str(BASE / (stem + '_sync.wav')), 'rb') as w:
        assert w.getnchannels() == 1 and w.getsampwidth() == 2 and w.getframerate() == 8000
        values = array.array('h', w.readframes(w.getnframes()))
    return [math.sqrt(sum(v*v for v in values[i:i+80])/80) for i in range(0, len(values)-79, 80)]

camera, screen = envelope('mvp_cam_01'), envelope('mvp_01')
def score(start, end, lag):
    # Positive lag means screen source time = camera source time + lag/100.
    a = camera[start:end]
    b = screen[start+lag:end+lag]
    if len(a) != len(b): return -1
    ma, mb = sum(a)/len(a), sum(b)/len(b)
    va = sum((x-ma)**2 for x in a)
    vb = sum((x-mb)**2 for x in b)
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(va*vb) if va*vb else 0

out = {'method':'10 ms RMS envelope Pearson correlation; not a latency measurement',
       'rms_ranges':{'camera':[min(camera),max(camera)],'screen':[min(screen),max(screen)]}, 'windows':[]}
usable = max(camera) > 0 and max(screen) > 0
out['usable'] = usable
out['reason'] = None if usable else 'At least one decoded audio stream is entirely silent; no audio offset estimate.'
for start,end in ([(500,6800),(500,2500),(2500,4500),(4500,6800)] if usable else []):
    scored = sorted([(score(start,end,lag),lag/100) for lag in range(-400,401)],reverse=True)
    out['windows'].append({'camera_seconds':[start/100,end/100], 'top_candidates':scored[:5]})
(BASE / 'audio_alignment_candidates.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8')
print(json.dumps(out,indent=2))
