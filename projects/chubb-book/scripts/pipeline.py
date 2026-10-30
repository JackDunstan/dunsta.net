#!/usr/bin/env python3
"""Inventory → offline OCR → editable Obsidian notes → static search catalogue.
Python 3.9+, standard library only. Run with --help for individual stages.
"""
import argparse, concurrent.futures, hashlib, json, re, shutil, subprocess, sys
from pathlib import Path
from frontmatter import parse, field
from artifacts import ensure, complete, label

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
VAULT = ROOT / 'vault'

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def inventory():
    pages = []
    for book in (1, 2):
        for thumb in sorted((ROOT / f'images/book-{book}/thumbs').glob('*.jpg')):
            number = int(thumb.stem.split('-')[-1])
            medium = ROOT / f'images/book-{book}/medium/{thumb.name}'
            # Full-size exports have a separate, one-based numbering scheme.
            large = ROOT / f'images/book-{book}/large/JPEG/BOOK{book} - {number+1:03}.jpg'
            image = medium if medium.exists() else thumb
            pages.append(dict(id=thumb.stem, book=book, sequence=number,
                              label=f'Book {book} · scan {number:03}',
                              thumbnail=str(thumb.relative_to(ROOT)), image=str(image.relative_to(ROOT)),
                              original=str((large if large.exists() else image).relative_to(ROOT)),
                              resolution='full' if medium.exists() else 'thumbnail-only'))
    dump(DATA / 'inventory.json', pages)
    return pages

def verify():
    manifest = json.loads((DATA / 'original-images.json').read_text())
    failures = [p for p,h in manifest.items() if not (ROOT/p).exists() or hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    if failures: raise RuntimeError('Original scans changed: ' + ', '.join(failures))
    print(f'Preserved: all {len(manifest)} original JPG files match their SHA-256 hashes.')

def recognize(pages, args):
    pending = [p for p in pages if p['resolution']=='full' and (args.force or not (DATA/'ocr'/f"{p['id']}.json").exists())]
    if args.limit: pending=pending[:args.limit]
    if not pending: return
    engine = args.engine
    binary = Path('/tmp/chubb-recognize')
    if engine=='vision':
        if sys.platform!='darwin': raise RuntimeError('Vision requires macOS. Use --engine tesseract for printed text on other systems.')
        source=ROOT/'scripts/recognize.swift'
        if not binary.exists() or binary.stat().st_mtime < source.stat().st_mtime:
            subprocess.run(['swiftc','-module-cache-path','/tmp/chubb-swift-cache',str(source),'-o',str(binary)],check=True)
    def one(p):
        if engine=='vision':
            raw = subprocess.check_output([str(binary), str(ROOT/p['image'])], text=True)
            result=json.loads(raw)
            result['file']=p['image']
        else:
            text=subprocess.check_output(['tesseract',str(ROOT/p['image']),'stdout','-l','eng','--psm','3'],text=True)
            result=dict(file=p['image'],engine='Tesseract (printed text only)',text=text,lines=[],candidate_names=[],face_candidates=[])
        result['source_sha256']=hashlib.sha256((ROOT/p['image']).read_bytes()).hexdigest()
        result['status']='machine-draft'
        dump(DATA/'ocr'/f"{p['id']}.json",result)
        return p['id']
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for i, name in enumerate(pool.map(one,pending),1): print(f'OCR {i}/{len(pending)} {name}',flush=True)

def note(path, meta, body):
    path.parent.mkdir(parents=True,exist_ok=True)
    front='---\n'+'\n'.join(field(k, v) for k,v in meta.items())+'\n---\n\n'
    path.write_text(front+body+'\n')

def read_note(path):
    meta,body=parse(path.read_text())
    return meta,body.strip()

def section(body,title):
    match=re.search(r'^## '+re.escape(title)+r'\n(.*?)(?=^## |\Z)',body,re.M|re.S)
    return match.group(1).strip() if match else ''

def notes(pages):
    for p in pages:
        path=VAULT/'Pages'/f"{p['id']}.md"
        ocrpath=DATA/'ocr'/f"{p['id']}.json"
        ocr=json.loads(ocrpath.read_text()) if ocrpath.exists() else {}
        if not path.exists():
            meta=dict(id=p['id'],title=p['label'],book=p['book'],sequence=p['sequence'],
                      status='needs-review',people=[],topics=[],date='',artifacts=[],tags=['scrapbook','needs-review'])
            note(path,meta,f"# {p['label']}\n\n[Original scan](../../{p['original'].replace(' ', '%20')})\n\n"
                 f"![](../../{p['image']})\n\n## Description\n\n## Transcription\n\n"
                 "## Context\n\n## Review notes\n\nCompare the machine draft with the scan. Handwriting and names need human review.\n\n"
                 "## Machine transcription\n\n<!-- OCR:START -->\n<!-- OCR:END -->")
        # Only the machine block changes; all editorial work remains untouched.
        raw=path.read_text()
        draft=ocr.get('text','') or ('Only a thumbnail survives in this checkout; transcription deferred.' if p['resolution']=='thumbnail-only' else 'Recognition pending.')
        raw=re.sub(r'<!-- OCR:START -->.*?<!-- OCR:END -->',lambda m:'<!-- OCR:START -->\n'+draft+'\n<!-- OCR:END -->',raw,flags=re.S)
        path.write_text(raw)
    build(pages)

def build(pages):
    people=json.loads((DATA/'people.json').read_text())
    topic_defs=json.loads((DATA/'topics.json').read_text())
    catalogue=[]; candidates={}; reviews=[]
    for p in pages:
        meta,body=ensure(p, VAULT/'Pages'/f"{p['id']}.md")
        op=DATA/'ocr'/f"{p['id']}.json"
        ocr=json.loads(op.read_text()) if op.exists() else {}
        text=section(body,'Transcription') or ocr.get('text','')
        suggested=[t['id'] for t in topic_defs if any(re.search(r'\b'+re.escape(k)+r'\b',text,re.I) for k in t['keywords'])]
        names=[]; mentions=[]
        for name in ocr.get('candidate_names',[]):
            clean=' '.join(name.split()).strip('.,:;')
            if len(clean)<4 or len(clean)>70 or not re.search('[a-zA-Z]',clean): continue
            cid=slug(clean)
            if not cid: continue
            entry=candidates.setdefault(cid,dict(id=cid,name=clean,pages=[],occurrences=[],status='unverified-name'))
            if p['id'] not in entry['pages']: entry['pages'].append(p['id'])
            names.append(clean)
            lines=text.splitlines()
            evidence=next((line for line in lines if clean.casefold() in line.casefold()), '')
            entry['occurrences'].append(dict(page=p['id'],evidence=evidence[:1000]))
            mentions.append(dict(name=clean,evidence=evidence[:1000],note=f'notes/Candidates/candidate-{cid}.html'))
        faces=ocr.get('face_candidates',[])
        artifacts=meta.get('artifacts',[])
        for i,box in enumerate(faces,1):
            # A detector supplies regions to inspect, never identities.
            if any(a.get('face_index')==i and a.get('identity_status') in ('identified','not-a-person') for a in artifacts): continue
            reviews.append(dict(id=f"{p['id']}-face-{i}",page=p['id'],kind='unidentified-person',label=f"Possible person {i} · {p['label']}",box=box,status='needs-review'))
        if meta['status']!='reviewed': reviews.append(dict(id=p['id']+'-transcription',page=p['id'],kind='transcription',label=p['label'],status='needs-review'))
        catalogue.append(dict(**p,title=meta['title'],status=meta['status'],date=meta.get('date',''),
                              description=section(body,'Description'),context=section(body,'Context'),
                              transcription=text,transcription_status='reviewed' if meta['status']=='reviewed' and section(body,'Transcription') else 'machine-draft',
                              people=meta.get('people',[]),topics=meta.get('topics',[]),suggested_topics=suggested,
                              candidate_names=names,mentions=mentions,faces=faces,artifacts=artifacts,markdown=f"vault/Pages/{p['id']}.md"))
    all_artifacts=[dict(a,page=p['id']) for p in catalogue for a in p['artifacts']]
    dump(DATA/'catalogue.json',dict(artifacts=all_artifacts,pages=catalogue,people=people,topics=topic_defs,candidates=list(candidates.values()),reviews=reviews))
    for person in people:
        related=[p for p in catalogue if person['id'] in p['people']]
        body=f"# {person['name']}\n\n{person['context']}\n\n## Sources\n\n"+'\n'.join(f"- [{s['title']}]({s['url']})" for s in person['sources'])+'\n\n## Mentioned in\n\n'+'\n'.join(f"- [[{p['id']}|{p['title']}]]" for p in related)
        note(VAULT/'People'/f"{person['id']}.md",dict(type='person',id=person['id'],status='sourced-context'),body)
    for c in candidates.values():
        body=f"# {c['name']}\n\nUnverified machine-extracted name. This may be a partial name, a misreading, or text that is not a person.\n\n## Evidence in the scrapbook\n\n"+'\n\n'.join(f"[[{o['page']}]] — machine reading: {o['evidence']}" for o in c['occurrences'])
        body+='\n\n## Research task\n\nCompare the name and surrounding artifact with the scan. Establish a full name, dates and a matching authority source before adding a biography. Check the page’s printed or handwritten attribution; do not assume this is a person pictured in the photograph.'
        note(VAULT/'Candidates'/f"candidate-{c['id']}.md",dict(type='name-candidate',status='unverified-name',pages=c['pages']),body)
    for t in topic_defs:
        related=[p for p in catalogue if t['id'] in p['topics'] or t['id'] in p['suggested_topics']]
        note(VAULT/'Topics'/f"{t['id']}.md",dict(type='topic',status='mixed-reviewed-and-suggested'),f"# {t['name']}\n\nKeyword suggestions require review; they do not establish historical facts.\n\n"+'\n'.join(f"- [[{p['id']}|{p['title']}]] — {'curated' if t['id'] in p['topics'] else 'suggested'}" for p in related))
    note(VAULT/'Indexes/Artifacts.md',dict(type='index'), '# Artifacts\n\nNumbers identify book, scan and item: B01-S000-A01 is Book 1, scan 000, artifact 01. Whole-page records can be split during review. Edit captions and metadata in the corresponding page note’s artifacts field.\n\n'+'\n'.join(f"- [[{a['page']}|{a['number']} — {a['title']}]] · {', '.join(label(t) for t in a['types'])} · Caption: {a['caption'] or 'not mapped'}" for a in all_artifacts))
    note(VAULT/'Indexes/People.md',dict(type='index'),'# People\n\n## Sourced people\n\n'+'\n'.join(f"- [[{p['id']}|{p['name']}]]" for p in people)+'\n\n## Machine name candidates\n\nThese spellings and identities are unverified.\n\n'+'\n'.join(f"- [[candidate-{c['id']}|{c['name']}]]: "+', '.join(f'[[{p}]]' for p in c['pages']) for c in sorted(candidates.values(),key=lambda c:c['name'].lower())))
    note(VAULT/'Indexes/Unidentified people.md',dict(type='index'),'# Unidentified people\n\nFace detection candidates, not asserted identities. Review the region on the original page. Undetected people may also appear elsewhere.\n\n'+'\n'.join(f"- [ ] [[{r['page']}|{r['label']}]] · region {json.dumps(r['box'])}" for r in reviews if r['kind']=='unidentified-person'))
    note(VAULT/'Indexes/Topics.md',dict(type='index'),'# Topics\n\n'+'\n'.join(f"- [[{t['id']}|{t['name']}]]" for t in topic_defs))
    note(VAULT/'Indexes/Review queue.md',dict(type='index'),'# Review queue\n\n'+'\n'.join(f"- [ ] [[{r['page']}|{r['label']}]] — {r['kind']}" for r in reviews))
    note(VAULT/'Home.md',dict(type='collection',title='The Chubb Scrapbooks'),'# The Chubb Scrapbooks\n\nCharles Hector McFadyen’s family scrapbooks. Book 1 contains 163 scans; Book 2 has thumbnails only. Scan numbers preserve the digital filenames and are not claimed as original folio numbers.\n\n[[Artifacts]] · [[People]] · [[Topics]] · [[Unidentified people]] · [[Review queue]] · [[Provenance]]\n\n## Pages\n\n'+'\n'.join(f"- [[{p['id']}|{p['title']}]]" for p in catalogue))
    # Every Markdown note also gets a readable static HTML page, including without JS.
    from render import render_all
    render_all(ROOT,catalogue)
    print(f'Built {len(catalogue)} pages, {len(candidates)} name candidates, {len(reviews)} review tasks.')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=['inventory','ocr','notes','build','all','verify'])
    parser.add_argument('--engine',choices=['vision','tesseract'],default='vision')
    parser.add_argument('--jobs',type=int,default=2)
    parser.add_argument('--limit',type=int)
    parser.add_argument('--force',action='store_true',help='Re-run OCR; editorial notes are still preserved')
    args=parser.parse_args()
    if args.stage=='verify': verify(); return
    pages=inventory()
    if args.stage in ('ocr','all'): recognize(pages,args)
    if args.stage in ('notes','all'): notes(pages)
    elif args.stage=='build': build(pages)

if __name__=='__main__': main()
