"""Unauthenticated GitHub public repository and issue search. No tokens."""
from dataclasses import dataclass
import json
import re
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

def search_issues_url(query: str) -> str:
    query = query.strip()
    if not query or len(query) > 200:
        raise ValueError('Enter a search of 1–200 characters.')
    return 'https://api.github.com/search/issues?' + urlencode({'q': query + ' is:issue', 'per_page': 20})

@dataclass(frozen=True)
class Issue:
    title: str
    repository: str
    number: int
    state: str
    html_url: str

def response_items(raw: bytes) -> list:
    if len(raw) > 1_000_000:
        raise ValueError('GitHub returned a response that is too large.')
    try:
        doc = json.loads(raw)
    except (UnicodeDecodeError, ValueError) as e:
        raise ValueError('GitHub returned an invalid response.') from e
    if not isinstance(doc, dict) or not isinstance(doc.get('items'), list):
        raise ValueError('GitHub returned an unexpected response.')
    return doc['items'][:20]

def parse_results(raw: bytes) -> list[Repository]:
    result = []
    for item in response_items(raw):
        if not isinstance(item, dict): continue
        name, url = item.get('full_name'), item.get('html_url')
        if not isinstance(name, str) or not isinstance(url, str): continue
        try:
            parsed = urlsplit(url)
            if parsed.scheme != 'https' or parsed.hostname != 'github.com' or parsed.username is not None or parsed.password is not None or parsed.port not in (None, 443): continue
            match = re.fullmatch(r'/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)', parsed.path)
            if not match or any(part in ('.', '..') for part in match.groups()) or name != '/'.join(match.groups()) or parsed.query or parsed.fragment: continue
        except ValueError: continue
        desc = item.get('description')
        stars = item.get('stargazers_count')
        result.append(Repository(name[:300], desc[:500] if isinstance(desc, str) else '', url, stars if type(stars) is int and stars >= 0 else 0))
    return result

def parse_issues(raw: bytes) -> list[Issue]:
    result = []
    for item in response_items(raw):
        if not isinstance(item, dict) or 'pull_request' in item: continue
        title, url, number, state = item.get('title'), item.get('html_url'), item.get('number'), item.get('state')
        if not isinstance(title, str) or not isinstance(url, str) or type(number) is not int or number <= 0 or state not in ('open', 'closed'): continue
        try:
            parsed = urlsplit(url)
            if parsed.scheme != 'https' or parsed.hostname != 'github.com' or parsed.username is not None or parsed.password is not None or parsed.port not in (None, 443): continue
            match = re.fullmatch(r'/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/issues/([1-9][0-9]*)', parsed.path)
            if not match or any(part in ('.', '..') for part in match.groups()[:2]) or int(match.group(3)) != number or parsed.query or parsed.fragment: continue
        except ValueError: continue
        result.append(Issue(title[:300].replace('\n', ' '), match.group(1) + '/' + match.group(2), number, state, url))
    return result

def error_message(status: int, rate_limited: bool = False) -> str:
    if status == 429 or (status == 403 and rate_limited): return 'GitHub rate limit reached. Try again later.'
    if status in (401, 403): return 'GitHub denied this request.'
    if status == 422: return 'GitHub could not process this search. Try a different query.'
    if status >= 500: return 'GitHub is temporarily unavailable.'
    return 'The search failed. Check your network connection and try again.'
