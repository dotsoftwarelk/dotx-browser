"""Capture the actual DOTX window with a locally staged, non-personal sample page.

Requires a working Qt display. For container testing only, see docs/DEVELOPMENT.md
for offscreen/sandbox guidance; never disable the sandbox for normal usage.
"""
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import QStandardPaths, QTimer, QUrl
from PySide6.QtWidgets import QApplication
from dotx.__main__ import Browser

root = Path(__file__).resolve().parents[1]
app = QApplication([])
app.setApplicationName('DOTX Screenshot')
app.setOrganizationName('dotsoftwarelk-test')
page = '''<!doctype html><html><head><meta charset="utf-8"><title>Local demonstration page</title><style>
body{font-family:Segoe UI,Arial,sans-serif;margin:0;background:#f2f6fb;color:#142339}.container{max-width:730px;margin:0 auto;padding:48px}.tag{color:#20749b;font-weight:700;letter-spacing:.14em;font-size:12px}h1{font-size:38px;letter-spacing:-.04em;margin:15px 0 10px}p{color:#566d83;line-height:1.6}.panel{background:white;border:1px solid #d7e3ee;border-radius:12px;margin-top:30px;padding:22px}.columns{display:flex;gap:14px}.tile{flex:1;padding:17px;background:#f4f8fc;border-radius:8px;border:1px solid #e0e9f1;color:#496379;font-size:13px}.label{font-size:11px;color:#6e8296;font-weight:700;letter-spacing:.08em}</style></head><body><div class="container"><span class="tag">LOCAL DEMONSTRATION PAGE</span><h1>Make room for better work.</h1><p>This sample page is displayed inside the actual DOTX development browser. It contains no account data.</p><div class="panel"><div class="label">YOUR BROWSER</div><h2>Explore the web, your way.</h2><div class="columns"><div class="tile">Navigate between open tabs</div><div class="tile">Keep useful pages in bookmarks</div><div class="tile">Open tools from the workspace</div></div></div></div></body></html>'''
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = page.encode('utf-8')
        self.send_response(200); self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, *args): pass
server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
with patch.object(QStandardPaths, 'writableLocation', return_value=tempfile.mkdtemp(prefix='dotx-shot-')):
    window = Browser(); window.data['appearance'] = 'dark'; window.apply_theme()
    window.resize(1180, 740); window.show()
    def loaded(ok):
        if not ok: app.exit(1); return
        def capture():
            dest = root / 'site' / 'assets' / 'browser-screenshot.png'
            if not window.grab().save(str(dest), 'PNG'): app.exit(2); return
            print('Saved actual browser window screenshot:', dest)
            app.quit()
        QTimer.singleShot(1200, capture)
    window.view().loadFinished.connect(loaded)
    window.view().setUrl(QUrl(f'http://127.0.0.1:{server.server_port}/'))
    QTimer.singleShot(15000, lambda: app.exit(3))
    raise SystemExit(app.exec())
