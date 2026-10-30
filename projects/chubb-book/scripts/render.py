"""Small, escaped Markdown renderer for this controlled archival format.
YAML frontmatter values are JSON literals. No raw HTML is rendered.
"""
import html, json, re
from pathlib import Path
from urllib.parse import quote, urlparse
from frontmatter import parse


def render_all(root, pages):
    notes=sorted((root/'vault').rglob('*.md'))
    targets={p.stem:'notes/'+str(p.relative_to(root/'vault').with_suffix('.html')) for p in notes}
    def inline(raw):
        tokens={}
        def keep(s):
            key=f'\x00{len(tokens)}\x00';tokens[key]=s;return key
        def wiki(m):
            name,_,label=m.group(1).partition('|')
            return keep(f'<a href="../../{quote(targets.get(name,"vault/"+name+".md"))}">{html.escape(label or name)}</a>')
        raw=re.sub(r'\[\[([^\]]+)\]\]',wiki,raw)
        def link(m):
            image,label,url=m.groups()
            if urlparse(url).scheme not in ('','http','https'): return html.escape(label)
            if not url.startswith(('http:','https:')):
                if url.startswith('../../'): url='../../'+url[6:]
                else: url='../../'+url
            u=html.escape(url,quote=True);label=html.escape(label)
            return keep(f'<img loading="lazy" src="{u}" alt="{label or "Scrapbook scan"}">' if image else f'<a href="{u}">{label}</a>')
        raw=re.sub(r'(!?)\[([^\]]*)\]\(([^\)]+)\)',link,raw)
        raw=html.escape(raw)
        for key,value in tokens.items():raw=raw.replace(key,value)
        return raw
    for path in notes:
        metadata,raw=parse(path.read_text())
        lines=[]; machine=False
        for line in raw.splitlines():
            if line in ('<!-- ARTIFACTS:START -->', '<!-- ARTIFACTS:END -->'):continue
            if line=='<!-- OCR:START -->': machine=True;lines.append('<pre class="transcript">');continue
            if line=='<!-- OCR:END -->': machine=False;lines.append('</pre>');continue
            if machine:lines.append(html.escape(line));continue
            if line.startswith('#'):
                m=re.match(r'^(#{1,6}) (.*)',line)
                if m:lines.append(f'<h{len(m[1])}>{inline(m[2])}</h{len(m[1])}>');continue
            if line:lines.append('<p>'+inline(line)+'</p>')
        if metadata.get('artifacts') and '<!-- ARTIFACTS:START -->' not in raw:
            lines.append('<h2>Catalogued artifacts</h2>')
            for artifact in metadata['artifacts']:
                lines.append('<h3>'+inline(artifact.get('title','Untitled artifact'))+'</h3>')
                for key in ('type','transcription','context'):
                    if artifact.get(key):lines.append('<p>'+inline(artifact[key])+'</p>')
                links=' · '.join('[['+person+']]' for person in artifact.get('people',[]))
                if links:lines.append('<p>'+inline(links)+'</p>')
        # Relative URLs are resolved from the collection root through an explicit base.
        destination=root/'notes'/path.relative_to(root/'vault').with_suffix('.html')
        destination.parent.mkdir(parents=True,exist_ok=True)
        depth=len(destination.relative_to(root).parts)-1
        prefix='../'*depth
        rendered='\n'.join(lines).replace('href="../../','href="'+prefix).replace('src="../../','src="'+prefix)
        title=html.escape(path.stem)
        destination.write_text(f'''<!doctype html><html lang="en"><head><meta name="robots" content="noindex, nofollow"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} · Chubb Scrapbooks</title><link rel="stylesheet" href="{prefix}assets/style.css"></head><body class="document"><header class="masthead"><a class="brand" href="{prefix}index.html">The Chubb Scrapbooks<span>A FAMILY ARCHIVE</span></a><a href="{prefix}index.html#browse">Browse the collection ↗</a></header><main class="note"><a href="{prefix}vault/{quote(str(path.relative_to(root/'vault')))}" download>Download Markdown ↓</a>{rendered}</main><footer>Charles Hector McFadyen · The family scrapbooks</footer></body></html>''')
