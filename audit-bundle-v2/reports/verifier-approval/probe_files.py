import subprocess
BASE = 'C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat'
for f in ['LICENSE', 'README.md', 'docs/KICKOFF.md', 'docs/RECORD.md', 'docs/studies/SF-0.md']:
    b = open(BASE + '/' + f, 'rb').read()
    print(f, 'bytes', len(b), 'CR', b.count(b'\r'), 'trailing-ws-lines',
          sum(1 for ln in b.decode('utf-8').split('\n') if ln != ln.rstrip()),
          'ends-newline', b.endswith(b'\n'))
# diff file list + word diff check for unintended content
out = subprocess.run(['git', '-c', 'safe.directory=' + BASE, 'diff', '--name-only',
                      '828b8f1..0bfa964'], capture_output=True, cwd=BASE, text=True).stdout
print('files:', out.strip().split('\n'))
st = subprocess.run(['git', '-c', 'safe.directory=' + BASE, 'status', '--short'],
                    capture_output=True, cwd=BASE, text=True).stdout
print('status-clean:', repr(st))
log = subprocess.run(['git', '-c', 'safe.directory=' + BASE, 'log', '-1',
                      '--format=%an <%ae> // %cn <%ce>'], capture_output=True, cwd=BASE, text=True).stdout
print('author/committer:', log.strip())
