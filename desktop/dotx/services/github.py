"""Unauthenticated GitHub public-repository search. No account connection or tokens."""
from dataclasses import dataclass
import json
from urllib.parse import urlencode, urlsplit

@dataclass(frozen=True)
class Repository:
    full_name: str
    description: str
    html_url: str
    stars: int

def search_url(query: str) -> str:
    query = query.strip()
    if not query or len(query) > 200:
        raise ValueError('Enter a search of 1–200 characters.')
    return 'https://api.github.com/search/repositories?' + urlencode({'q': query, 'per_page': 20})

def parse_results(raw: bytes) -> list[Repository]:
    if len(raw) > 1_000_000:
        raise ValueError('GitHub returned a response that is too large.')
    try:
        doc = json.loads(raw)
    except (UnicodeDecodeError, ValueError) as e:
        raise ValueError('GitHub returned an invalid response.') from e
    if not isinstance(doc, dict) or not isinstance(doc.get('items'), list):
        raise ValueError('GitHub returned an unexpected response.')
    result = []
    for item in doc['items'][:20]:
        if not isinstance(item, dict): continue
        name, url = item.get('full_name'), item.get('html_url')
        if not isinstance(name, str) or not isinstance(url, str): continue
        try:
            parsed = urlsplit(url)
            if parsed.scheme != 'https' or parsed.hostname != 'github.com' or parsed.username or parsed.password or parsed.port not in (None, 443): continue
        except ValueError: continue
        desc = item.get('description')
        stars = item.get('stargazers_count')
        result.append(Repository(name[:300], desc[:500] if isinstance(desc, str) else '', url, stars if isinstance(stars, int) and stars >= 0 else 0))
    return result

def error_message(status: int, rate_limited: bool = False) -> str:
    if status == 429 or (status == 403 and rate_limited): return 'GitHub rate limit reached. Try again later.'
    if status in (401, 403): return 'GitHub denied this request.'
    if status == 422: return 'GitHub could not process this search. Try a different query.'
    if status >= 500: return 'GitHub is temporarily unavailable.'
    return 'The search failed. Check your network connection and try again.'
