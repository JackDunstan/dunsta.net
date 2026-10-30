"""Additive artifact scaffolding; page frontmatter remains the editorial source."""
import re
from frontmatter import parse, replace_field

LABELS = {
    'scrapbook-page': 'Scrapbook page', 'mixed-media': 'Mixed media',
    'newspaper-clipping': 'Newspaper clipping', 'handwritten-note': 'Handwritten note',
    'photo': 'Photo', 'photograph': 'Photo', 'portrait': 'Portrait photo',
    'typed-document': 'Typed document', 'letter': 'Letter', 'telegram': 'Telegram',
    'invitation': 'Invitation', 'greeting-card': 'Greeting card',
    'certificate': 'Certificate', 'printed-material': 'Printed material',
}


def label(kind):
    return LABELS.get(kind, kind.replace('-', ' ').capitalize())


def complete(page, artifacts):
    """Fill missing fields, preserving numbers, captions, unknown metadata and IDs."""
    prefix = f"B{page['book']:02}-S{page['sequence']:03}-A"
    artifacts = [dict(a) for a in artifacts] if artifacts else [{}]
    used = {a['number'] for a in artifacts if a.get('number')}
    used_ids = {a['id'] for a in artifacts if a.get('id')}
    next_number = 1
    for artifact in artifacts:
        if not artifact.get('number'):
            while f'{prefix}{next_number:02}' in used:
                next_number += 1
            artifact['number'] = f'{prefix}{next_number:02}'
            used.add(artifact['number'])
        if not artifact.get('id'):
            candidate = artifact['number'].lower()
            while candidate in used_ids:
                candidate += '-item'
            artifact['id'] = candidate
            used_ids.add(candidate)
        artifact.setdefault('title', f"Scrapbook page — {page['label']}")
        artifact.setdefault('type', 'scrapbook-page')
        artifact.setdefault('types', [artifact['type']])
        artifact.setdefault('caption', '')
        artifact.setdefault('caption_source', '')
        artifact.setdefault('caption_status', 'unmapped')
        artifact.setdefault('scope', 'page' if 'box' not in artifact else 'region')
        artifact.setdefault('box', [0, 0, 1, 1])
        artifact.setdefault('people', [])
        artifact.setdefault('classification_status', 'needs-review')
    return artifacts


def summary(artifacts):
    lines = ['<!-- ARTIFACTS:START -->',
             'Edit the artifacts field in this note’s frontmatter to change these records. This summary is generated.']
    for artifact in artifacts:
        lines += ['', f"### {artifact['number']} — {artifact['title']}", '',
                  'Types: ' + ', '.join(label(t) for t in artifact['types']), '',
                  'Scope: ' + ('Whole scanned page; individual items can be split out during review.' if artifact['scope']=='page' else 'Individual item or region.'), '',
                  'Caption: ' + (artifact['caption'] or 'Not mapped yet.'), '',
                  'Caption source: ' + (artifact['caption_source'] or 'Not recorded yet.'), '',
                  'Caption status: ' + artifact['caption_status']]
        if artifact.get('transcription'): lines += ['', 'Transcription: ' + artifact['transcription']]
        if artifact.get('context'): lines += ['', 'Context: ' + artifact['context']]
        if artifact.get('people'): lines += ['', 'People: ' + ' · '.join(f'[[{person}]]' for person in artifact['people'])]
    return '\n'.join(lines) + '\n<!-- ARTIFACTS:END -->'


def ensure(page, path):
    raw = path.read_text()
    meta, _ = parse(raw)
    artifacts = complete(page, meta.get('artifacts', []))
    updated = replace_field(raw, 'artifacts', artifacts)
    block = summary(artifacts)
    if '<!-- ARTIFACTS:START -->' in updated:
        updated = re.sub(r'<!-- ARTIFACTS:START -->.*?<!-- ARTIFACTS:END -->', lambda _: block, updated, flags=re.S)
    else:
        section = '## Artifacts\n\n' + block + '\n\n'
        if '## Machine transcription\n' in updated:
            updated = updated.replace('## Machine transcription\n', section + '## Machine transcription\n', 1)
        else:
            updated = updated.rstrip() + '\n\n' + section
    if updated != raw:
        path.write_text(updated)
    return parse(updated)
