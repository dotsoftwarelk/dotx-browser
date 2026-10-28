"""Small, UI-independent browser helpers. No network access or secrets."""
from urllib.parse import quote_plus, urlsplit
import ipaddress
import json
import os
from pathlib import Path
import tempfile

SEARCH = {'DuckDuckGo': 'https://duckduckgo.com/?q=', 'Google': 'https://www.google.com/search?q=', 'Bing': 'https://www.bing.com/search?q='}

def normalize_input(value: str, search: str = 'DuckDuckGo') -> str:
    value = value.strip()
    if not value:
        return 'about:blank'
    if value == 'about:blank':
        return value
    if '://' in value:
        try:
            parsed = urlsplit(value)
            # Never pass arbitrary OS handlers, credentials, malformed ports, or local files to the engine.
            if parsed.scheme.lower() in ('http', 'https') and parsed.hostname and not parsed.username and not parsed.password:
                _ = parsed.port
                return value
        except ValueError:
            pass
        raise ValueError('Only valid HTTP and HTTPS addresses are supported.')
    host = value.split('/')[0].split(':')[0]
    is_host = host.lower() == 'localhost' or ('.' in host and ' ' not in value)
    try:
        ipaddress.ip_address(host)
        is_host = True
    except ValueError:
        pass
    if is_host:
        candidate = 'https://' + value
        try:
            parsed = urlsplit(candidate)
            _ = parsed.port
            if parsed.hostname:
                return candidate
        except ValueError:
            raise ValueError('Invalid address.')
    return SEARCH.get(search, SEARCH['DuckDuckGo']) + quote_plus(value)

def load_data(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(data, dict):
            return data
    except (OSError, ValueError):
        pass
    return {}

def save_data(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.dotx-', suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
