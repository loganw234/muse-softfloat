import subprocess, hashlib

BASE = 'C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat'
t = open(BASE + '/LICENSE', 'rb').read()
text = t.decode('utf-8')
lines = text.split('\n')
print('bytes', len(t), 'CR', t.count(b'\r'), 'LF', t.count(b'\n'))
print('line1', repr(lines[0]))
print('line3', repr(lines[2]))

canon_body = (
"MIT License\n"
"\n"
"Copyright (c) 2026 Logan W.\n"
"\n"
'Permission is hereby granted, free of charge, to any person obtaining a copy\n'
'of this software and associated documentation files (the "Software"), to deal\n'
'in the Software without restriction, including without limitation the rights\n'
'to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n'
'copies of the Software, and to permit persons to whom the Software is\n'
'furnished to do so, subject to the following conditions:\n'
'\n'
'The above copyright notice and this permission notice shall be included in all\n'
'copies or substantial portions of the Software.\n'
'\n'
'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n'
'IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n'
'FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n'
'AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n'
'LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n'
'OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n'
'SOFTWARE.\n'
)
print('exact-canonical-plus-holder-line:', text == canon_body)
if text != canon_body:
    import difflib
    for l in difflib.unified_diff(canon_body.splitlines(), text.splitlines(), lineterm=''):
        print(l)
print('sha256', hashlib.sha256(t).hexdigest())
print('trailing-newline-single:', text.endswith('SOFTWARE.\n') and not text.endswith('\n\n'))
