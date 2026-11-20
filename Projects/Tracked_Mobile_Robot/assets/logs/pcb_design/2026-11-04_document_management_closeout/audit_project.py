"""Read-only project inventory and Markdown local-target audit; no build/cleanup."""
from pathlib import Path
from collections import Counter, defaultdict
from urllib.parse import unquote
import hashlib
import json
import os
import re
import subprocess

ROOT = next(p for p in Path(__file__).resolve().parents if p.name == 'Tracked_Mobile_Robot')
REPO = ROOT.parents[1]
OUT = Path(__file__).resolve().parent
SKIP_DOC = {'build', 'Debug', 'Release', 'Drivers', 'Middlewares', '__pycache__', 'node_modules', '.git'}

def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args]).decode('utf-8', errors='replace')

def run():
    files = []
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d != '.git']
        for name in names:
            p = Path(base) / name
            if p.is_file():
                files.append(p)
    stats = {p: p.stat().st_size for p in files}
    groups = defaultdict(lambda: {'files': 0, 'bytes': 0})
    for p, size in stats.items():
        g = groups[p.relative_to(ROOT).parts[0]]
        g['files'] += 1
        g['bytes'] += size
    md = [p for p in files if p.suffix.lower() == '.md' and not SKIP_DOC.intersection(p.relative_to(ROOT).parts)]
    missing = []
    checked = 0
    for p in md:
        body = p.read_text(encoding='utf-8-sig', errors='replace')
        fenced = False
        for n, line in enumerate(body.splitlines(), 1):
            if line.lstrip().startswith(('```', '~~~')):
                fenced = not fenced
                continue
            if fenced:
                continue
            for m in re.finditer(r'!?\[[^\]\n]*\]\((<[^>]+>|[^\s)]+)(?:\s+"[^"]*")?\)', line):
                target = m.group(1).strip('<>')
                if re.match(r'^[a-zA-Z][\w+.-]*:', target) or target.startswith(('#', '//')):
                    continue
                local = unquote(target.split('#', 1)[0].split('?', 1)[0])
                if not local:
                    continue
                if local.startswith('/'):
                    continue  # repository-root/app absolute links need a separate resolver
                checked += 1
                resolved = (p.parent / local).resolve()
                if not resolved.exists():
                    missing.append({'file': p.relative_to(ROOT).as_posix(), 'line': n, 'target': target})
    sizes = defaultdict(list)
    for p, size in stats.items():
        if size >= 1024 * 1024 and not SKIP_DOC.intersection(p.relative_to(ROOT).parts):
            sizes[size].append(p)
    duplicates = []
    for size, paths in sizes.items():
        if len(paths) < 2:
            continue
        hashes = defaultdict(list)
        for p in paths:
            h = hashlib.sha256()
            with p.open('rb') as f:
                for block in iter(lambda: f.read(1024 * 1024), b''):
                    h.update(block)
            hashes[h.hexdigest()].append(p.relative_to(ROOT).as_posix())
        for digest, names in hashes.items():
            if len(names) > 1:
                duplicates.append({'bytes_each': size, 'sha256': digest, 'paths': names})
    tracked = git('ls-files', '-z', '--', str(ROOT.relative_to(REPO))).split('\0')
    tracked = [x for x in tracked if x]
    build_tracked = [x for x in tracked if '/build/' in x or '/Debug/' in x or '/Release/' in x]
    suspicious = [p.relative_to(ROOT).as_posix() for p in files if p.name in {'.kicad_sch', '.kicad_sch.kicad_sch'}]
    result = {
        'audit_date_kst': '2026-11-04',
        'scope': 'All physical project files enumerated. Local Markdown targets checked outside generated/vendor folders; anchors, remote URLs, absolute links and electrical/code behavior are not validated.',
        'files': len(files), 'bytes': sum(stats.values()), 'top_level': dict(sorted(groups.items())),
        'tracked_files': len(tracked), 'tracked_build_artifacts': len(build_tracked),
        'tracked_build_examples': build_tracked[:12],
        'markdown_files_checked': len(md), 'relative_targets_checked': checked,
        'missing_relative_targets': missing,
        'large_files': [{'path': p.relative_to(ROOT).as_posix(), 'bytes': stats[p]} for p in sorted(files, key=lambda x: stats[x], reverse=True)[:20]],
        'exact_duplicate_groups_at_least_1MiB': duplicates,
        'ambiguous_cad_names': suspicious,
        'git_status': git('status', '--short', '--', str(ROOT.relative_to(REPO))).splitlines(),
        'actions': 'Read-only inventory. No source, evidence, CAD, build output or duplicates deleted/moved.'
    }
    output_name = sys.argv[1] if len(sys.argv) > 1 else 'audit.json'
    if Path(output_name).name != output_name or not output_name.endswith('.json'):
        raise ValueError('Output must be a JSON filename inside this audit folder')
    (OUT / output_name).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['files', 'bytes', 'tracked_files', 'tracked_build_artifacts', 'markdown_files_checked', 'relative_targets_checked', 'missing_relative_targets', 'ambiguous_cad_names']}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    run()
