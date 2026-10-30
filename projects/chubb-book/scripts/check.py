#!/usr/bin/env python3
"""Validate preservation, data contracts, generated links and editorial retention."""
import hashlib, json, re, tempfile, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pipeline
from artifacts import complete, ensure
from frontmatter import field, parse

root=pipeline.ROOT
pipeline.verify()
catalogue=json.loads((root/'data/catalogue.json').read_text())
pages=catalogue['pages']
assert len(pages)==277 and len({p['id'] for p in pages})==277
assert len([p for p in pages if p['resolution']=='full'])==163
assert all(p['book']==2 for p in pages if p['resolution']=='thumbnail-only')
people={p['id'] for p in catalogue['people']};topics={t['id'] for t in catalogue['topics']}
for p in pages:
    for key in ('image','thumbnail','original','markdown'):assert (root/p[key]).is_file(),(p['id'],key)
    assert set(p['people']) <= people and set(p['topics']) <= topics
    meta,body=pipeline.read_note(root/p['markdown'])
    assert meta['id']==p['id'] and '<!-- OCR:START -->' in body
    assert p['artifacts'], p['id']
    assert meta['artifacts']==p['artifacts']
    assert '<!-- ARTIFACTS:START -->' in body
    assert len({a['id'] for a in p['artifacts']})==len(p['artifacts'])
    for artifact in p['artifacts']:
        for key in ('number','id','title','type','caption','caption_source','caption_status','scope','classification_status'):
            assert isinstance(artifact[key],str),(p['id'],key)
        assert artifact['number'] and artifact['title'] and artifact['types']
        assert set(artifact['people']) <= people
        assert artifact['number'] in body
    if p['resolution']=='full':
        ocr=json.loads((root/'data/ocr'/f"{p['id']}.json").read_text())
        assert ocr['source_sha256']==hashlib.sha256((root/p['image']).read_bytes()).hexdigest()
        assert ocr['status']=='machine-draft'
    for box in p['faces']:
        assert len(box)==4 and all(0<=n<=1 for n in box)
artifact_numbers=[a['number'] for p in pages for a in p['artifacts']]
assert len(set(artifact_numbers))==len(artifact_numbers)
assert len(catalogue['artifacts'])==len(artifact_numbers)
for r in catalogue['reviews']:

    assert r['page'] in {p['id'] for p in pages}

class Links(HTMLParser):
    def __init__(self):super().__init__();self.urls=[]
    def handle_starttag(self,tag,attrs):
        self.urls.extend(v for k,v in attrs if k in ('src','href') and v)

broken=[]
for path in [root/'index.html',root/'book2.html',*sorted((root/'notes').rglob('*.html'))]:
    parser=Links();parser.feed(path.read_text())
    for url in parser.urls:
        parts=urlsplit(url)
        if parts.scheme or parts.netloc or not parts.path:continue
        target=(path.parent/unquote(parts.path)).resolve()
        if not target.is_file():broken.append((str(path.relative_to(root)),url))
assert not broken,broken[:20]
# Re-running note generation must preserve a human correction and frontmatter.
with tempfile.TemporaryDirectory() as tmp:
    vault=Path(tmp)/'vault';data=Path(tmp)/'data';(data/'ocr').mkdir(parents=True)
    page=pages[0];path=vault/'Pages'/f"{page['id']}.md"
    pipeline.note(path,{'id':page['id'],'title':'Human title','status':'reviewed'},'# Human title\n\n## Transcription\n\nMy verified correction.\n\n<!-- OCR:START -->old<!-- OCR:END -->')
    (data/'ocr'/f"{page['id']}.json").write_text(json.dumps({'text':'new machine reading'}))
    with patch.object(pipeline,'VAULT',vault),patch.object(pipeline,'DATA',data),patch.object(pipeline,'build'):
        pipeline.notes([page])
    result=path.read_text()
    assert 'My verified correction.' in result and 'Human title' in result and 'new machine reading' in result
    assert 'old<!-- OCR:END -->' not in result
# Captions, custom fields and assigned numbers survive rebuilds and insertion.
with tempfile.TemporaryDirectory() as tmp:
    path=Path(tmp)/'page.md'
    page=pages[0]
    original=complete(page,[{'id':'existing','number':'B01-S000-A07','title':'My artifact','type':'photo',
                             'caption':'A caption with "quotes", a newline\nand [[links]].',
                             'caption_source':'Family context','caption_status':'mapped',
                             'custom_field':{'keep':True}}])[0]
    pipeline.note(path,{'id':page['id'],'artifacts':[original]},'# Human description\n\nDo not change this paragraph.')
    ensure(page,path)
    meta,body=pipeline.read_note(path)
    assert meta['artifacts'][0]==original
    assert original['caption'] in body and 'Do not change this paragraph.' in body
    first=path.read_bytes();ensure(page,path);assert path.read_bytes()==first
    enriched=complete(page,[{},original])
    assert enriched[1]==original and enriched[0]['number']=='B01-S000-A01'
    assert complete(page,list(reversed(enriched)))==list(reversed(enriched))
    assert parse('---\n'+field('artifacts',enriched)+'\n---\nBody')[0]['artifacts']==enriched
print(f'Validated {len(pages)} pages, {len(artifact_numbers)} numbered artifacts, {len(catalogue["candidates"])} name candidates and all static HTML links. Editorial/caption retention and stable numbering passed.')
