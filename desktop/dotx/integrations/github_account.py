"""Experimental GitHub device authorization, session-only and no client secret.

The application must be explicitly configured with an OAuth app's public client ID.
Tokens remain in memory, are never logged and are dropped on local disconnect/exit.
"""
import json
import os
import time
from dataclasses import dataclass
from urllib.parse import urlencode
from PySide6.QtCore import QTimer, QUrl, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import QApplication, QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from ..services.github_device import DEVICE_VERIFY_URL, parse_challenge, parse_poll, validate_client_id, valid_login

DEVICE_URL = 'https://github.com/login/device/code'
TOKEN_URL = 'https://github.com/login/oauth/access_token'
USER_URL = 'https://api.github.com/user'
REVOKE_URL = 'https://github.com/settings/connections/applications'

@dataclass(repr=False)
class GitHubSession:
    # Deliberately session-only: no settings, file, crash-report, cloud or log storage.
    token: str | None = None
    login: str | None = None

    def clear(self):
        self.token = None
        self.login = None

class GitHubAccountDialog(QDialog):
    def __init__(self, session: GitHubSession, parent=None, manager=None):
        super().__init__(parent)
        self.setWindowTitle('GitHub account — experimental')
        self.resize(560, 340)
        self.session = session
        self.client_id = os.environ.get('DOTX_GITHUB_CLIENT_ID', '').strip()
        self.manager = manager or QNetworkAccessManager(self)
        self.timer = QTimer(self); self.timer.setSingleShot(True); self.timer.timeout.connect(self.poll)
        self.reply = None
        self.challenge = None
        self.deadline = 0.0
        self.pending_token = None
        self.closed = False
        layout = QVBoxLayout(self)
        description = QLabel('Optional GitHub device authorization. Requests read:user only. Tokens stay in memory and are lost on exit. This experimental flow requires an owner-registered OAuth app with device flow enabled.')
        description.setWordWrap(True); layout.addWidget(description)
        self.status = QLabel(); self.status.setWordWrap(True); layout.addWidget(self.status)
        self.code = QLabel(''); self.code.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse); layout.addWidget(self.code)
        row = QHBoxLayout()
        self.connect_button = QPushButton('Connect'); self.connect_button.clicked.connect(self.begin); row.addWidget(self.connect_button)
        self.open_button = QPushButton('Open GitHub verification'); self.open_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(DEVICE_VERIFY_URL))); row.addWidget(self.open_button)
        self.copy_button = QPushButton('Copy code'); self.copy_button.clicked.connect(lambda: QApplication.clipboard().setText(self.challenge.user_code) if self.challenge else None); row.addWidget(self.copy_button)
        layout.addLayout(row)
        row2 = QHBoxLayout()
        self.test_button = QPushButton('Test connection'); self.test_button.clicked.connect(self.test_connection); row2.addWidget(self.test_button)
        self.disconnect_button = QPushButton('Disconnect locally'); self.disconnect_button.clicked.connect(self.disconnect); row2.addWidget(self.disconnect_button)
        self.revoke_button = QPushButton('Manage GitHub authorizations'); self.revoke_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(REVOKE_URL))); row2.addWidget(self.revoke_button)
        layout.addLayout(row2)
        note = QLabel('Disconnect removes the local session only. To revoke the grant, use GitHub authorization settings. No account data is synchronized.')
        note.setWordWrap(True); layout.addWidget(note)
        self.finished.connect(self.cancel_pending)
        self.refresh()

    def refresh(self, message=None):
        configured = validate_client_id(self.client_id)
        busy = self.reply is not None or self.challenge is not None
        if message: self.status.setText(message)
        elif self.session.token and self.session.login: self.status.setText(f'Previously verified: {self.session.login}. Test connection to recheck access.')
        elif not configured: self.status.setText('Not configured: set DOTX_GITHUB_CLIENT_ID to a registered OAuth app client ID and enable device flow in GitHub.')
        else: self.status.setText('Not connected.')
        self.connect_button.setEnabled(configured and not busy and not self.session.token)
        self.open_button.setEnabled(self.challenge is not None)
        self.copy_button.setEnabled(self.challenge is not None)
        self.test_button.setEnabled(bool(self.session.token) and not busy)
        self.disconnect_button.setEnabled(bool(self.session.token) and not busy)

    def send(self, url, fields, callback, token=None):
        # All endpoints are constants; never forward an Authorization header via redirects.
        if self.reply is not None: return
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader(b'Accept', b'application/json')
        request.setRawHeader(b'User-Agent', b'DOTX-Browser-development')
        request.setTransferTimeout(15000)
        request.setAttribute(QNetworkRequest.Attribute.RedirectPolicyAttribute, QNetworkRequest.RedirectPolicy.ManualRedirectPolicy)
        if token:
            if url != USER_URL: raise ValueError('Token endpoint mismatch')
            request.setRawHeader(b'Authorization', ('Bearer ' + token).encode('ascii'))
            request.setRawHeader(b'X-GitHub-Api-Version', b'2022-11-28')
            reply = self.manager.get(request)
        else:
            request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, 'application/x-www-form-urlencoded')
            reply = self.manager.post(request, urlencode(fields).encode('ascii'))
        self.reply = reply
        def done():
            if self.closed: reply.deleteLater(); return
            self.reply = None
            status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute) or 0
            network_error = reply.error() != QNetworkReply.NetworkError.NoError
            raw = bytes(reply.readAll())
            reply.deleteLater()
            if len(raw) > 256_000:
                callback(None, int(status), True); return
            try: data = json.loads(raw)
            except (ValueError, UnicodeDecodeError): data = None
            callback(data, int(status), network_error)
        reply.finished.connect(done)

    def begin(self):
        if not validate_client_id(self.client_id) or self.reply or self.session.token: return
        self.status.setText('Requesting GitHub device authorization…')
        self.send(DEVICE_URL, {'client_id':self.client_id, 'scope':'read:user'}, self.on_challenge)
        self.refresh('Requesting GitHub device authorization…')

    def on_challenge(self, data, status, network_error):
        if network_error or status != 200:
            self.refresh('GitHub authorization unavailable or configuration invalid. Check your app registration and network.'); return
        try: self.challenge = parse_challenge(data)
        except ValueError as e: self.refresh(str(e)); return
        self.deadline = time.monotonic() + self.challenge.expires_in
        self.code.setText('Verification code: ' + self.challenge.user_code)
        self.refresh('Awaiting authorization. Open GitHub verification and enter the code; the request expires automatically.')
        self.timer.start(self.challenge.interval * 1000)

    def poll(self):
        if not self.challenge or self.reply: return
        if time.monotonic() >= self.deadline:
            self.challenge = None; self.code.clear(); self.refresh('Authorization expired. Connect again.'); return
        fields={'client_id':self.client_id,'device_code':self.challenge.device_code,'grant_type':'urn:ietf:params:oauth:grant-type:device_code'}
        self.send(TOKEN_URL, fields, self.on_poll)

    def on_poll(self, data, status, network_error):
        if not self.challenge: return
        if network_error or status != 200:
            self.challenge = None; self.code.clear(); self.refresh('Authorization failed or service unavailable. Connect again.'); return
        state, interval, token = parse_poll(data, self.challenge.interval)
        if state == 'pending':
            self.challenge.interval = interval
            if time.monotonic() + interval >= self.deadline:
                self.challenge = None; self.code.clear(); self.refresh('Authorization expired. Connect again.')
            else: self.timer.start(interval * 1000)
        elif state == 'authorized':
            self.challenge = None; self.code.clear(); self.pending_token = token
            self.refresh('Authorization received; verifying account…')
            self.send(USER_URL, None, self.on_identity, token=token)
            self.refresh('Authorization received; verifying account…')
        else:
            self.challenge = None; self.code.clear()
            self.refresh({'access_denied':'Permission denied by user.', 'expired_token':'Authorization expired. Connect again.'}.get(state, 'Authorization failed. Connect again.'))

    def on_identity(self, data, status, network_error):
        login = valid_login(data) if status == 200 and not network_error else None
        if login and self.pending_token:
            self.session.token = self.pending_token; self.session.login = login
            self.pending_token = None; self.refresh('Connected and verified: ' + login)
        else:
            self.pending_token = None; self.refresh('Authorization received but account verification failed. Connect again.')

    def test_connection(self):
        if not self.session.token or self.reply: return
        self.status.setText('Checking connection…')
        def finished(data, status, network_error):
            login = valid_login(data) if status == 200 and not network_error else None
            if login:
                self.session.login = login; self.refresh('Connected and verified: ' + login)
            elif status == 401:
                self.session.clear(); self.refresh('Reauthorization required: GitHub rejected the token.')
            elif status == 403 or status == 429: self.refresh('Permission denied or rate limited by GitHub; try again later.')
            else: self.refresh('GitHub unavailable or network error. Connection not verified.')
        self.send(USER_URL, None, finished, token=self.session.token)
        self.refresh('Checking connection…')

    def disconnect(self):
        self.timer.stop(); self.challenge = None; self.pending_token = None; self.session.clear(); self.code.clear()
        self.refresh('Disconnected locally. Revoke the grant in GitHub settings if desired.')

    def cancel_pending(self, *args):
        self.closed = True; self.timer.stop(); self.challenge = None; self.pending_token = None
        if self.reply is not None: self.reply.abort()

    def closeEvent(self, event):
        self.cancel_pending()
        super().closeEvent(event)
