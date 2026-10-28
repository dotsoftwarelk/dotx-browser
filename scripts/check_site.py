"""Check local HTML targets and basic metadata without relying on a deployment host."""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote
root = Path(__file__).resolve().parents[1] / 'site'
class Inspect(HTMLParser):
    def __init__(self): super().__init__(); self.urls=[]; self.title=False; self.description=False; self.main=False; self.base=None
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if tag == 'base':
            self.base=d.get('href'); return
        if tag == 'title': self.title=True
        if tag == 'meta' and d.get('name') == 'description' and d.get('content'): self.description=True
        if tag == 'main': self.main=True
        for key in ('href','src'):
            if d.get(key): self.urls.append(d[key])
errors=[]
for html in root.glob('*.html'):
    p=Inspect(); p.feed(html.read_text(encoding='utf-8'))
    if not (p.title and p.description and p.main): errors.append(f'{html.name}: metadata or main missing')
    if p.base is not None and (html.name != '404.html' or not re.fullmatch(r'/(?:[A-Za-z0-9._~-]+/)*', p.base) or '..' in p.base): errors.append(f'{html.name}: unsafe base')
    for u in p.urls:
        parsed=urlsplit(u)
        if parsed.scheme or parsed.netloc or not parsed.path: continue
        if parsed.path.startswith('/'): errors.append(f'{html.name}: root-absolute path breaks project Pages: {u}'); continue
        path=(html.parent/unquote(parsed.path)).resolve()
        if not path.is_relative_to(root.resolve()) or not path.exists(): errors.append(f'{html.name}: missing/unsafe target {u}')
if errors: raise SystemExit('\n'.join(errors))
print('Checked', len(list(root.glob('*.html'))), 'HTML pages: local paths and basic metadata OK')
