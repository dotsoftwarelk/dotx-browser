"""Check user-initiated target-blank navigation and unsolicited popup handling."""
import os,tempfile,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
os.environ['XDG_DATA_HOME']=tempfile.mkdtemp(prefix='dotx-popup-')
from PySide6.QtCore import QTimer,QUrl,QPoint,Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from dotx.__main__ import Browser
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        b=(b'<html><body style="margin:0"><a style="display:block;width:300px;height:100px" href="/next" target="_blank">Open next page</a></body></html>' if self.path=='/' else b'<title>Next page</title>')
        self.send_response(200);self.send_header('Content-Length',str(len(b)));self.send_header('Content-Type','text/html');self.end_headers()
        try:self.wfile.write(b)
        except (BrokenPipeError,ConnectionResetError):pass
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
app=QApplication([]);app.setApplicationName('DOTX-popup-test');app.setOrganizationName('dotsoftwarelk-test')
w=Browser();w.show();result={'ok':False};url=f'http://127.0.0.1:{server.server_port}/'
def loaded(ok):
    if not ok:app.quit();return
    def click():
        if w.tabs.count() != 1:
            print('FAIL: unsolicited popup opened a tab'); app.quit(); return
        QTest.mouseClick(w.view().focusProxy() or w.view(),Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,QPoint(30,30))
        QTimer.singleShot(1200,check)
    w.view().page().runJavaScript("window.open('/unsolicited', '_blank')")
    QTimer.singleShot(500,click)
def check():
    result['ok']=w.tabs.count()==2 and w.view().url().path()=='/next'
    print('Target-blank result:',w.tabs.count(),w.view().url().path())
    app.quit()
w.view().loadFinished.connect(loaded);w.view().setUrl(QUrl(url));QTimer.singleShot(10000,app.quit);app.exec();server.shutdown()
import shiboken6
shiboken6.delete(w)
if not result['ok']:raise SystemExit('FAIL: target-blank link')
print('PASS: unsolicited JavaScript popup blocked; user-initiated target-blank opens a tab')
