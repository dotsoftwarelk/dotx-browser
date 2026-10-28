"""Validation and state transitions for GitHub's OAuth device flow.

No token persistence, UI, network, logging, or client secret lives here.
https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
"""
from dataclasses import dataclass
import re

DEVICE_VERIFY_URL = 'https://github.com/login/device'
CLIENT_ID_RE = re.compile(r'^[A-Za-z0-9_]{8,100}$')
LOGIN_RE = re.compile(r'^[A-Za-z0-9-]{1,39}$')

@dataclass
class DeviceChallenge:
    device_code: str
    user_code: str
    interval: int
    expires_in: int


def validate_client_id(value: str) -> bool:
    return bool(CLIENT_ID_RE.fullmatch(value or ''))


def parse_challenge(doc: object) -> DeviceChallenge:
    if not isinstance(doc, dict): raise ValueError('Invalid device authorization response.')
    device, user, uri = doc.get('device_code'), doc.get('user_code'), doc.get('verification_uri')
    interval, expires = doc.get('interval', 5), doc.get('expires_in')
    if not isinstance(device, str) or not 8 <= len(device) <= 512 or any(c.isspace() for c in device):
        raise ValueError('Invalid device authorization response.')
    if not isinstance(user, str) or not re.fullmatch(r'[A-Z0-9]{4}-[A-Z0-9]{4}', user):
        raise ValueError('Invalid device authorization response.')
    if uri != DEVICE_VERIFY_URL:
        raise ValueError('Unexpected GitHub verification address.')
    if type(interval) is not int or not 1 <= interval <= 120 or type(expires) is not int or not 1 <= expires <= 3600:
        raise ValueError('Invalid device authorization timing.')
    return DeviceChallenge(device, user, max(5, interval), expires)


def parse_poll(doc: object, interval: int) -> tuple[str, int, str | None]:
    """Return state, next interval and token; errors never include provider data."""
    if not isinstance(doc, dict): return ('error', interval, None)
    token = doc.get('access_token')
    token_type = doc.get('token_type')
    if isinstance(token, str) and 8 <= len(token) <= 4096 and all(33 <= ord(c) <= 126 for c in token) and isinstance(token_type, str) and token_type.lower() == 'bearer':
        return ('authorized', interval, token)
    error = doc.get('error')
    if error == 'authorization_pending': return ('pending', interval, None)
    if error == 'slow_down':
        given = doc.get('interval')
        return ('pending', max(interval + 5, given if type(given) is int and given <= 300 else 0), None)
    if error in ('access_denied', 'expired_token'): return (error, interval, None)
    return ('error', interval, None)


def valid_login(doc: object) -> str | None:
    if not isinstance(doc, dict): return None
    login = doc.get('login')
    return login if isinstance(login, str) and LOGIN_RE.fullmatch(login) else None
