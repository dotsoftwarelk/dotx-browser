"""Mocked Qt network device-flow UI check. Never contacts GitHub or uses credentials."""
import json, os
from unittest.mock import patch
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtNetwork import QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import QApplication
from dotx.integrations.github_account import GitHubAccountDialog,GitHubSession,DEVICE_URL,TOKEN_URL,USER_URL
from dotx.services.github_device import DEVICE_VERIFY_URL

class Reply(QObject):
    finished=Signal()
    def __init__(self, data): super().__init__();self.data=data
    def readAll(self): return json.dumps(self.data).encode()
    def error(self): return QNetworkReply.NetworkError.NoError
    def attribute(self, name): return 200
    def abort(self): pass
class Manager(QObject):
    def __init__(self): super().__init__();self.requests=[];self.replies=[];self.poll_count=0
    def post(self, req, body):
        self.requests.append((req.url().toString(),bytes(body)))
        if req.url().toString()==DEVICE_URL:
            return self.make({'device_code':'abc123456789','user_code':'ABCD-1234','verification_uri':DEVICE_VERIFY_URL,'expires_in':900,'interval':5})
        assert req.url().toString()==TOKEN_URL
        self.poll_count += 1
        if self.poll_count == 1: return self.make({'error':'authorization_pending'})
        if self.poll_count == 2: return self.make({'error':'slow_down','interval':10})
        return self.make({'access_token':'example-test-token','token_type':'bearer'})
    def get(self, req):
        self.requests.append((req.url().toString(),bytes(req.rawHeader('Authorization'))))
        assert req.url().toString()==USER_URL
        return self.make({'login':'example-user'})
    def make(self,data):
        reply=Reply(data);self.replies.append(reply)
        QTimer.singleShot(0,reply.finished.emit)
        return reply

app=QApplication([]);manager=Manager();session=GitHubSession();result={'ok':False}
with patch.dict(os.environ,{'DOTX_GITHUB_CLIENT_ID':'ExampleClient123'}):
    d=GitHubAccountDialog(session,manager=manager)
    assert d.status.text()=='Not connected.' and d.connect_button.isEnabled()
    d.begin()
    def after_challenge():
        assert d.challenge and d.challenge.user_code=='ABCD-1234'
        assert d.timer.isActive()
        d.timer.stop();d.poll()
        QTimer.singleShot(100,after_pending)
    def after_pending():
        assert d.challenge and d.timer.isActive() and d.challenge.interval == 5
        d.timer.stop(); d.poll()
        QTimer.singleShot(100,after_slow_down)
    def after_slow_down():
        assert d.challenge and d.timer.isActive() and d.challenge.interval == 10
        d.timer.stop(); d.poll()
        QTimer.singleShot(100,after_identity)
    def after_identity():
        assert session.login=='example-user' and session.token=='example-test-token'
        assert 'Connected and verified' in d.status.text()
        assert [x[0] for x in manager.requests]==[DEVICE_URL,TOKEN_URL,TOKEN_URL,TOKEN_URL,USER_URL]
        assert b'client_secret' not in manager.requests[0][1]
        d.disconnect();assert session.token is None and session.login is None
        result['ok']=True
        d.reject();app.quit()
    QTimer.singleShot(100,after_challenge)
    QTimer.singleShot(5000,app.quit)
    app.exec()
assert result['ok'] and len(manager.requests)==5 and session.token is None
with patch.dict(os.environ, {'DOTX_GITHUB_CLIENT_ID':''}):
    unconfigured=GitHubAccountDialog(GitHubSession(),manager=manager)
    assert 'Not configured' in unconfigured.status.text() and not unconfigured.connect_button.isEnabled()
    unconfigured.begin(); assert len(manager.requests)==5
print('PASS: mocked GitHub device challenge, pending, slow down, identity and local disconnect')
