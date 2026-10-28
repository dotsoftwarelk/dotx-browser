"""Headless Linux development smoke test. Not Windows release verification.
Run with QT_QPA_PLATFORM=offscreen; a sandbox exception may be required in containers.
"""
import os
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
os.environ['XDG_DATA_HOME'] = tempfile.mkdtemp(prefix='dotx-smoke-')
from PySide6.QtCore import QTimer, QUrl
from PySide6.QtWidgets import QApplication
from dotx.__main__ import Browser
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b'<html><head><title>Local smoke</title></head><body>DOTX test</body></html>'
        self.send_response(200); self.send_header('Content-Type', 'text/html'); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, *args): pass
server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
app = QApplication([]); app.setOrganizationName('dotsoftwarelk-test'); app.setApplicationName('DOTX-test')
w = Browser(); assert w.tabs.count() == 1
w.new_tab(); assert w.tabs.count() == 2
w.close_tab(1); assert w.tabs.count() == 1
w.zoom(0.1); assert abs(w.view().zoomFactor() - 1.1) < 0.01
w.reset_zoom(); assert abs(w.view().zoomFactor() - 1.0) < 0.01
w.duplicate_tab(); assert w.tabs.count() == 2
w.close_tab(1); assert w.tabs.count() == 1
url = f'http://127.0.0.1:{server.server_port}/'
result = {'ok': False}
def finished(ok):
    if not ok: app.exit(1); return
    w.bookmark()
    assert any(x['url'] == url for x in w.data['bookmarks'])
    assert any(x['url'] == url for x in w.data['history'])
    assert w.path.is_file()
    w.close_tab(0)
    assert w.closed_tabs[-1] == url
    w.reopen_closed()
    assert w.view().url().toString() == url
    print('PASS: window, tabs, duplication, reopen, zoom, local navigation, history, bookmark and state file')
    result['ok'] = True; app.quit()
w.view().loadFinished.connect(finished)
w.view().setUrl(QUrl(url))
QTimer.singleShot(15000, app.quit)
app.exec(); server.shutdown()
# Tear down pages before the shared application profile.
import shiboken6
shiboken6.delete(w)
if not result['ok']: raise SystemExit('FAIL: navigation did not complete')
