"""Validate content invariants and numerical boundary cases before publication."""
import json, math, re
from pathlib import Path
from zipfile import ZipFile
from score import score
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/indicators.json').read_text(encoding='utf-8'))
rows=data['indicators']
assert len(rows)==28 and len({r['id'] for r in rows})==28
assert score(10,10,100,'higher')==1
assert score(20,10,100,'higher')==1
assert score(20.01,10,100,'higher')==2
assert score(100,10,100,'higher')==9
assert score(10,10,100,'lower')==9
assert score(100,10,100,'lower')==1
for r in rows:
    b=r['benchmark']
    assert b and b['n']==len(b['observations'])
    assert b['min']<b['max']
    for country in ['taiwan','china']:
        c=r[country]
        assert isinstance(c['value'],(int,float)) and math.isfinite(c['value'])
        assert c['year'] is not None
        assert c['source'].startswith('https://')
        assert r['scores'][country]==score(c['value'],b['min'],b['max'],r['direction'])
with ZipFile(ROOT/'documents/taivanas-kinija-storymaps.docx') as z:
    xml=z.read('word/document.xml').decode('utf-8')
    assert '[[TABLE:' not in xml and '[[IMAGE:' not in xml
    assert len([n for n in z.namelist() if n.startswith('word/media/')])==4
    for r in rows:assert r['id'] in xml
for path in [ROOT/'README.md',ROOT/'documents/storymaps-importas.md',ROOT/'documents/pasakojimas-perziurai.md']:
    text=path.read_text(encoding='utf-8')
    for link in re.findall(r'\]\(([^)]+)\)',text):
        if link.startswith(('https://','http://','#')):continue
        target=link.split('?')[0].split('#')[0]
        assert (path.parent/target).exists(),(str(path),target)
print('PASS: 28 criteria, 56 values, 56 scores, source references, DOCX media and repository links')
