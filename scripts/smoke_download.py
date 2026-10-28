"""Exercise a real local Qt WebEngine download without external network or GUI dialogs."""
import os
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
os.environ['XDG_DATA_HOME'] = tempfile.mkdtemp(prefix='dotx-download-')
from PySide6.QtCore import QTimer, QUrl
from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest
from dotx.__main__ import Browser
DATA = b'DOTX download smoke test\n'
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type','application/octet-stream')
        self.send_header('Content-Disposition','attachment; filename="sample.txt"')
        self.send_header('Content-Length',str(len(DATA)))
        self.end_headers()
        try: self.wfile.write(DATA)
        except (BrokenPipeError, ConnectionResetError): pass
    def log_message(self,*args): pass
server = ThreadingHTTPServer(('127.0.0.1',0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
app=QApplication([]); app.setApplicationName('DOTX-download-test'); app.setOrganizationName('dotsoftwarelk-test')
w=Browser(); dest=Path(os.environ['XDG_DATA_HOME'])/'sample.txt'; result={'ok':False}
def requested(req):
    def finish():
        if not req.isFinished(): return
        result['ok'] = req.state() == QWebEngineDownloadRequest.DownloadState.DownloadCompleted and dest.exists() and dest.read_bytes() == DATA
        app.quit()
    req.isFinishedChanged.connect(finish)
w.profile.downloadRequested.connect(requested)
with patch.object(QFileDialog,'getSaveFileName',return_value=(str(dest),'')):
    w.view().page().download(QUrl(f'http://127.0.0.1:{server.server_port}/sample.txt'))
    QTimer.singleShot(15000,app.quit)
    app.exec()
server.shutdown()
import shiboken6
shiboken6.delete(w)
if not result['ok']: raise SystemExit('FAIL: local download')
print('PASS: local download request, destination, state and file contents')
