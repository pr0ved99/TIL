"""Extract camera-only review sheets; never infer relay timing from UI alignment."""
from pathlib import Path
import hashlib
import io
import json
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
SOURCE = ROOT / 'assets/videos/wifi_mvp/2026-10-24/raw/mvp_cam_long_01.mp4'
FF = Path(os.environ.get('FFMPEG', str(next(
    (Path(os.environ['TEMP']) / 'tmr-video-review-tools/imageio_ffmpeg/binaries').glob('ffmpeg*.exe')
))))
FONT = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 20)

def sheet(name, times):
    canvas = Image.new('RGB', (1280, ((len(times)+1)//2)*390), 'white')
    draw = ImageDraw.Draw(canvas)
    for i, t in enumerate(times):
        data = subprocess.check_output([
            str(FF), '-v', 'error', '-nostdin', '-ss', str(t), '-i', str(SOURCE),
            '-frames:v', '1', '-vf', 'scale=640:-1', '-f', 'image2pipe', '-vcodec', 'png', '-'
        ])
        frame = Image.open(io.BytesIO(data)).convert('RGB')
        frame.thumbnail((640, 360))
        x, y = (i % 2)*640, (i // 2)*390
        canvas.paste(frame, (x, y+30))
        draw.text((x+5, y+3), f'Camera original {t:.3f} s', fill='black', font=FONT)
    canvas.save(OUT/f'{name}.jpg', quality=92)

if __name__ == '__main__':
    samples = {
        'first_overview': [61, 62, 62.5, 63, 63.5, 64, 64.5, 65],
        'second_overview': [104, 105, 105.5, 106, 106.5, 107, 107.5, 108],
    }
    for name, times in samples.items():
        sheet(name, times)
    with SOURCE.open('rb') as f:
        digest = hashlib.file_digest(f, 'sha256').hexdigest()
    (OUT/'extraction.json').write_text(json.dumps({
        'source': str(SOURCE), 'source_sha256': digest,
        'camera_sample_seconds': samples, 'original_modified': False,
        'scope': 'Sparse visual screening of S0 visibility, not stop-time measurement'
    }, indent=2)+'\n', encoding='utf-8')
    print(digest)
