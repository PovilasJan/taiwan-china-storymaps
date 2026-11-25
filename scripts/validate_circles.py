"""Check that the interactive/static addition preserves the audited score data."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
source = json.loads((ROOT/'data/indicators.json').read_text(encoding='utf-8'))
javascript = (ROOT/'docs/indicators.js').read_text(encoding='utf-8')
bundle = json.loads(javascript.split('window.CIRCLE_DATA = ', 1)[1].strip().removesuffix(';'))
assert len(bundle['palette']) == 9
assert len(bundle['indicators']) == 28
assert Counter(row['domain'] for row in bundle['indicators']) == Counter({name: 7 for name in bundle['domains']})
for original, rendered in zip(source['indicators'], bundle['indicators']):
    assert original['id'] == rendered['id']
    assert original['scores'] == rendered['scores']
    for country in ['taiwan', 'china']:
        for key, value in rendered[country].items():
            assert original[country][key] == value, (original['id'], country, key)
    for key, value in rendered['benchmark'].items():
        assert original['benchmark'][key] == value
for country, name in [('taiwan', 'taivano-profile-circle.png'), ('china', 'kinijos-profile-circle.png')]:
    with Image.open(ROOT/'assets'/name) as picture:
        assert picture.width >= 2000 and picture.height >= 2000
        assert json.loads(picture.info['Scores']) == {row['id']: row['scores'][country] for row in source['indicators']}
        assert picture.info['SourceDataSHA256'] == hashlib.sha256((ROOT/'data/indicators.json').read_bytes()).hexdigest()
        picture.verify()
for file in ['docs/index.html', 'docs/app.js', 'docs/style.css']:
    assert (ROOT/file).stat().st_size > 100
for file in ['README.md', 'documents/profile-circles.md', 'documents/storymaps-importas.md']:
    path = ROOT/file
    for link in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
        if link.startswith(('https://', 'http://', '#')):
            continue
        assert (path.parent/link.split('?')[0].split('#')[0]).exists(), link
print('PASS: 28 browser criteria, all 56 unchanged scores, references, images and local links')
