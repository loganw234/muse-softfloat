import pathlib
root = pathlib.Path(r'C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w5-site')
files = list((root / 'site').iterdir()) + [root / '.github/workflows/pages.yml',
        root / 'README.md', root / 'docs/metrics/briefs.jsonl']
for f in files:
    if f.suffix == '.wasm':
        print(f.name, 'binary', f.stat().st_size); continue
    b = f.read_bytes()
    print(f.name, 'CRLF' if b'\r\n' in b else 'LF', len(b))
try:
    import yaml
    d = yaml.safe_load((root / '.github/workflows/pages.yml').read_text())
    print('yaml ok:', d['jobs']['deploy']['steps'][-1])
except ImportError:
    print('pyyaml not installed - yaml not parsed')
