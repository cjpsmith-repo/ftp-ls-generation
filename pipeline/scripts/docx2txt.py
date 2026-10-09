import sys, zipfile, re, os
from xml.etree import ElementTree as ET
NS = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def docx_text(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml')
    root = ET.fromstring(xml)
    paras = []
    for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        texts = [t.text or '' for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')]
        paras.append(''.join(texts))
    return '\n'.join(paras)
src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
import glob
for f in glob.glob(os.path.join(src, '**', '*.docx'), recursive=True):
    base = os.path.splitext(os.path.basename(f))[0] + '.txt'
    out = os.path.join(dst, base)
    try:
        t = docx_text(f)
        with open(out, 'w') as fh: fh.write(t)
    except Exception as e:
        print('FAIL', f, e)
print('done', src)
